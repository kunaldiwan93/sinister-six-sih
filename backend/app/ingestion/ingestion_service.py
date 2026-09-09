import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.document import Document
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.transaction import Transaction
from app.models.communication import Communication
from app.models.event import Event
from app.models.analysis_run import AnalysisRun
from app.ingestion.parsers import file_parser
from app.ai.entity_extractor import entity_extractor
from app.ai.relationship_extractor import relationship_extractor
from app.services.entity_resolution import entity_resolution_service
from app.services.risk_scoring import risk_scoring_service
from app.services.alert_engine import alert_engine
from app.graph.graph_metrics import graph_metrics_calculator
from app.graph.community_detection import community_detector
from app.graph.graph_builder import graph_repository

class IngestionService:
    @staticmethod
    def process_document(db: Session, case_id: str, title: str, doc_type: str, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Processes an uploaded police report / FIR / intelligence document:
        extracts text, runs NER and relationship extraction, resolves entities, updates knowledge graph.
        """
        start_time = time.time()
        
        # 1. Create Analysis Run
        analysis_run = AnalysisRun(
            case_id=case_id,
            run_type="DOCUMENT_INGESTION",
            status="PROCESSING",
            input_files=[filename]
        )
        db.add(analysis_run)
        db.commit()

        try:
            # 2. Extract raw text
            text = file_parser.extract_text_from_file(filename, content_bytes)
            
            # Save Document
            doc = Document(
                case_id=case_id,
                title=title,
                document_type=doc_type,
                raw_text=text,
                processed_status="PROCESSING"
            )
            db.add(doc)
            db.commit()

            # 3. Extract entities
            raw_entities = entity_extractor.extract_entities(text)
            
            # 4. Resolve and save entities
            entity_map: Dict[str, Entity] = {}
            new_entities_count = 0

            for raw_e in raw_entities:
                existing = entity_resolution_service.find_matching_entity(
                    db, case_id, raw_e["canonical_name"], raw_e["type"]
                )
                if existing:
                    entity_map[raw_e["canonical_name"].lower()] = existing
                    # Append source reference
                    refs = existing.source_references or []
                    refs.append({"doc_id": doc.id, "title": title, "type": "FIR_MENTION"})
                    existing.source_references = refs
                else:
                    new_ent = Entity(
                        case_id=case_id,
                        type=raw_e["type"],
                        canonical_name=raw_e["canonical_name"],
                        display_name=raw_e["display_name"],
                        confidence=raw_e.get("confidence", 0.95),
                        source_references=[{"doc_id": doc.id, "title": title, "type": "FIR_MENTION"}],
                        meta_info=raw_e.get("meta_info", {})
                    )
                    db.add(new_ent)
                    db.flush()
                    entity_map[raw_e["canonical_name"].lower()] = new_ent
                    new_entities_count += 1

            db.commit()

            # 5. Extract relationships
            raw_relationships = relationship_extractor.extract_relationships(text, raw_entities)
            new_rels_count = 0

            for raw_r in raw_relationships:
                s_ent = entity_map.get(raw_r["source_canonical"].lower())
                t_ent = entity_map.get(raw_r["target_canonical"].lower())
                
                if s_ent and t_ent and s_ent.id != t_ent.id:
                    # Check if relationship already exists
                    existing_rel = db.query(Relationship).filter(
                        Relationship.case_id == case_id,
                        Relationship.source_id == s_ent.id,
                        Relationship.target_id == t_ent.id,
                        Relationship.relationship_type == raw_r["relationship_type"]
                    ).first()

                    if not existing_rel:
                        new_rel = Relationship(
                            case_id=case_id,
                            source_id=s_ent.id,
                            target_id=t_ent.id,
                            relationship_type=raw_r["relationship_type"],
                            confidence=raw_r.get("confidence", 0.9),
                            source_document=title,
                            evidence_text=raw_r.get("evidence_text"),
                            meta_info=raw_r.get("meta_info", {})
                        )
                        db.add(new_rel)
                        new_rels_count += 1

            db.commit()

            # 6. Re-run analytics and risk scoring
            graph_repository.build_graph_for_case(db, case_id)
            graph_metrics_calculator.calculate_and_save_metrics(db, case_id)
            community_detector.detect_and_save_communities(db, case_id)
            alerts = alert_engine.generate_case_alerts(db, case_id)
            risk_scoring_service.calculate_entity_risk_scores(db, case_id)

            # Update Document and AnalysisRun status
            doc.processed_status = "PROCESSED"
            analysis_run.status = "COMPLETED"
            analysis_run.completed_at = datetime.utcnow()
            analysis_run.duration_seconds = round(time.time() - start_time, 2)
            analysis_run.entities_extracted = len(raw_entities)
            analysis_run.relationships_extracted = len(raw_relationships)
            analysis_run.alerts_generated = len(alerts)
            db.commit()

            return {
                "document_id": doc.id,
                "case_id": case_id,
                "title": title,
                "document_type": doc_type,
                "entities_extracted": len(raw_entities),
                "relationships_extracted": len(raw_relationships),
                "status": "PROCESSED",
                "message": f"Successfully processed document. Extracted {len(raw_entities)} entities and {len(raw_relationships)} relationships.",
                "extracted_entities_sample": raw_entities[:8],
                "extracted_relationships_sample": raw_relationships[:8]
            }

        except Exception as e:
            db.rollback()
            analysis_run.status = "FAILED"
            analysis_run.error_message = str(e)
            analysis_run.completed_at = datetime.utcnow()
            analysis_run.duration_seconds = round(time.time() - start_time, 2)
            db.commit()
            raise e

    @staticmethod
    def process_cdr_file(db: Session, case_id: str, filename: str, content: str) -> Dict[str, Any]:
        """
        Parses CDR CSV, creates Communication records and Phone entities, connects to knowledge graph.
        """
        start_time = time.time()
        records, errors = file_parser.parse_cdr_csv(content)
        if errors and not records:
            return {"status": "FAILED", "errors": errors, "records_processed": 0}

        analysis_run = AnalysisRun(
            case_id=case_id,
            run_type="CDR_INGESTION",
            status="PROCESSING",
            input_files=[filename]
        )
        db.add(analysis_run)
        db.commit()

        # Phone entity cache
        phone_cache: Dict[str, Entity] = {}
        for p in db.query(Entity).filter(Entity.case_id == case_id, Entity.type == "PHONE").all():
            phone_cache[p.canonical_name] = p

        added_comms = 0
        added_entities = 0

        for rec in records:
            c_phone = rec["caller_phone"]
            r_phone = rec["receiver_phone"]

            # Ensure caller phone entity exists
            if c_phone not in phone_cache:
                c_ent = Entity(
                    case_id=case_id,
                    type="PHONE",
                    canonical_name=c_phone,
                    display_name=c_phone,
                    meta_info={"phone_number": c_phone}
                )
                db.add(c_ent)
                db.flush()
                phone_cache[c_phone] = c_ent
                added_entities += 1

            # Ensure receiver phone entity exists
            if r_phone not in phone_cache:
                r_ent = Entity(
                    case_id=case_id,
                    type="PHONE",
                    canonical_name=r_phone,
                    display_name=r_phone,
                    meta_info={"phone_number": r_phone}
                )
                db.add(r_ent)
                db.flush()
                phone_cache[r_phone] = r_ent
                added_entities += 1

            # Create Communication record
            comm = Communication(
                case_id=case_id,
                caller_id=phone_cache[c_phone].id,
                receiver_id=phone_cache[r_phone].id,
                caller_phone=c_phone,
                receiver_phone=r_phone,
                timestamp=rec["timestamp"],
                duration_seconds=rec["duration_seconds"],
                communication_type=rec["communication_type"]
            )
            db.add(comm)

            # Create CALLED relationship
            rel = Relationship(
                case_id=case_id,
                source_id=phone_cache[c_phone].id,
                target_id=phone_cache[r_phone].id,
                relationship_type="CALLED",
                confidence=0.98,
                source_document=filename,
                evidence_text=f"CDR call: duration {rec['duration_seconds']}s on {rec['timestamp']}",
                timestamp=rec["timestamp"]
            )
            db.add(rel)
            added_comms += 1

        db.commit()

        # Run pipeline refresh
        graph_repository.build_graph_for_case(db, case_id)
        graph_metrics_calculator.calculate_and_save_metrics(db, case_id)
        community_detector.detect_and_save_communities(db, case_id)
        alerts = alert_engine.generate_case_alerts(db, case_id)
        risk_scoring_service.calculate_entity_risk_scores(db, case_id)

        analysis_run.status = "COMPLETED"
        analysis_run.completed_at = datetime.utcnow()
        analysis_run.duration_seconds = round(time.time() - start_time, 2)
        analysis_run.entities_extracted = added_entities
        analysis_run.relationships_extracted = added_comms
        analysis_run.alerts_generated = len(alerts)
        db.commit()

        return {
            "status": "COMPLETED",
            "records_processed": added_comms,
            "entities_created": added_entities,
            "errors": errors
        }

    @staticmethod
    def process_transaction_file(db: Session, case_id: str, filename: str, content: str) -> Dict[str, Any]:
        """
        Parses Transaction CSV, creates Transaction records and Bank Account entities.
        """
        start_time = time.time()
        records, errors = file_parser.parse_transaction_csv(content)
        if errors and not records:
            return {"status": "FAILED", "errors": errors, "records_processed": 0}

        analysis_run = AnalysisRun(
            case_id=case_id,
            run_type="TRANSACTION_INGESTION",
            status="PROCESSING",
            input_files=[filename]
        )
        db.add(analysis_run)
        db.commit()

        # Account entity cache
        account_cache: Dict[str, Entity] = {}
        for acc in db.query(Entity).filter(Entity.case_id == case_id, Entity.type == "BANK_ACCOUNT").all():
            account_cache[acc.canonical_name] = acc

        added_tx = 0
        added_entities = 0

        for rec in records:
            s_acc = rec["sender_account"]
            r_acc = rec["receiver_account"]

            if s_acc not in account_cache:
                s_ent = Entity(
                    case_id=case_id,
                    type="BANK_ACCOUNT",
                    canonical_name=s_acc,
                    display_name=f"Acc {s_acc}",
                    meta_info={"account_number": s_acc}
                )
                db.add(s_ent)
                db.flush()
                account_cache[s_acc] = s_ent
                added_entities += 1

            if r_acc not in account_cache:
                r_ent = Entity(
                    case_id=case_id,
                    type="BANK_ACCOUNT",
                    canonical_name=r_acc,
                    display_name=f"Acc {r_acc}",
                    meta_info={"account_number": r_acc}
                )
                db.add(r_ent)
                db.flush()
                account_cache[r_acc] = r_ent
                added_entities += 1

            tx = Transaction(
                case_id=case_id,
                sender_id=account_cache[s_acc].id,
                receiver_id=account_cache[r_acc].id,
                sender_account=s_acc,
                receiver_account=r_acc,
                amount=rec["amount"],
                currency=rec["currency"],
                timestamp=rec["timestamp"]
            )
            db.add(tx)

            rel = Relationship(
                case_id=case_id,
                source_id=account_cache[s_acc].id,
                target_id=account_cache[r_acc].id,
                relationship_type="TRANSFERRED_MONEY",
                confidence=0.99,
                weight=rec["amount"] / 10000.0,
                source_document=filename,
                evidence_text=f"Bank transfer: ₹{rec['amount']:,.2f} on {rec['timestamp']}",
                timestamp=rec["timestamp"]
            )
            db.add(rel)
            added_tx += 1

        db.commit()

        # Run pipeline refresh
        graph_repository.build_graph_for_case(db, case_id)
        graph_metrics_calculator.calculate_and_save_metrics(db, case_id)
        community_detector.detect_and_save_communities(db, case_id)
        alerts = alert_engine.generate_case_alerts(db, case_id)
        risk_scoring_service.calculate_entity_risk_scores(db, case_id)

        analysis_run.status = "COMPLETED"
        analysis_run.completed_at = datetime.utcnow()
        analysis_run.duration_seconds = round(time.time() - start_time, 2)
        analysis_run.entities_extracted = added_entities
        analysis_run.relationships_extracted = added_tx
        analysis_run.alerts_generated = len(alerts)
        db.commit()

        return {
            "status": "COMPLETED",
            "records_processed": added_tx,
            "entities_created": added_entities,
            "errors": errors
        }

ingestion_service = IngestionService()
