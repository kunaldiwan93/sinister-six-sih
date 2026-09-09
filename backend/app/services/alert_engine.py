from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.anomaly.transaction_anomaly import transaction_anomaly_detector
from app.anomaly.communication_anomaly import communication_anomaly_detector
from app.anomaly.location_anomaly import location_anomaly_detector
from app.graph.community_detection import community_detector

class AlertEngine:
    @staticmethod
    def generate_case_alerts(db: Session, case_id: str) -> List[Alert]:
        """
        Runs all anomaly detectors and network graph analyzers to generate comprehensive, explainable alerts.
        """
        # 1. Transaction Anomalies
        tx_anomalies = transaction_anomaly_detector.detect_anomalies(db, case_id)
        
        # 2. Communication Anomalies
        comm_anomalies = communication_anomaly_detector.detect_anomalies(db, case_id)
        
        # 3. Location Anomalies
        loc_anomalies = location_anomaly_detector.detect_anomalies(db, case_id)
        
        # 4. Bridge Nodes
        bridge_nodes = community_detector.identify_bridge_nodes(db, case_id)
        
        # 5. Shared Identifiers (e.g. shared phones, vehicles, bank accounts)
        shared_rels = db.query(Relationship).filter(
            Relationship.case_id == case_id,
            Relationship.relationship_type.in_(["SHARED_PHONE", "SHARED_VEHICLE", "SHARED_ACCOUNT", "SHARED_LOCATION"])
        ).all()

        entities = {e.id: e for e in db.query(Entity).filter(Entity.case_id == case_id).all()}
        
        created_alerts: List[Alert] = []

        # Process Transaction Alerts
        for tx in tx_anomalies:
            sender = entities.get(tx.get("sender_id"))
            receiver = entities.get(tx.get("receiver_id"))
            s_name = sender.display_name if sender else tx.get("sender_account")
            r_name = receiver.display_name if receiver else tx.get("receiver_account")
            
            title = f"Suspicious High-Value Transfer: ₹{tx['amount']:,.2f} ({s_name} → {r_name})"
            alert = Alert(
                case_id=case_id,
                entity_id=tx.get("sender_id") or tx.get("receiver_id"),
                title=title,
                category="TRANSACTION_ANOMALY",
                severity="HIGH" if tx["amount"] > 300000 else "MEDIUM",
                status="NEW",
                explanation=f"Transaction amount of ₹{tx['amount']:,.2f} between {s_name} and {r_name} triggered statistical anomaly detection: {tx['reason']}",
                evidence=tx["evidence"],
                confidence=0.92,
                timestamp=datetime.utcnow(),
                meta_info={"transaction_id": tx["transaction_id"], "amount": tx["amount"]}
            )
            db.add(alert)
            created_alerts.append(alert)

        # Process Communication Alerts
        for ca in comm_anomalies:
            caller = entities.get(ca.get("caller_id"))
            receiver = entities.get(ca.get("receiver_id"))
            c_name = caller.display_name if caller else ca["caller_phone"]
            r_name = receiver.display_name if receiver else ca["receiver_phone"]

            title = f"Unusual Communication Activity: {c_name} ↔ {r_name}"
            alert = Alert(
                case_id=case_id,
                entity_id=ca.get("caller_id") or ca.get("receiver_id"),
                title=title,
                category="COMMUNICATION_ANOMALY",
                severity="HIGH" if "burst" in ca["reason"].lower() else "MEDIUM",
                status="NEW",
                explanation=f"Communication pattern anomaly detected between {c_name} and {r_name}: {ca['reason']}",
                evidence=ca["evidence"],
                confidence=0.88,
                timestamp=datetime.utcnow(),
                meta_info={"communication_id": ca["communication_id"]}
            )
            db.add(alert)
            created_alerts.append(alert)

        # Process Bridge Node Alerts
        for bn in bridge_nodes:
            title = f"Potential Intermediary Node: {bn['name']}"
            alert = Alert(
                case_id=case_id,
                entity_id=bn["id"],
                title=title,
                category="BRIDGE_NODE",
                severity="CRITICAL" if bn["betweenness"] > 0.25 else "HIGH",
                status="NEW",
                explanation=f"{bn['name']} acts as a key structural bridge between distinct network clusters (Betweenness Centrality: {bn['betweenness']:.3f}).",
                evidence=[
                    f"Entity: {bn['name']} ({bn['type']})",
                    f"Betweenness Centrality: {bn['betweenness']:.3f}",
                    f"Primary Cluster: {bn['primary_community']}",
                    f"Connected Clusters: {bn['connected_communities']}",
                    bn['reason']
                ],
                confidence=0.95,
                timestamp=datetime.utcnow(),
                meta_info={"betweenness": bn["betweenness"], "communities": bn["connected_communities"]}
            )
            db.add(alert)
            created_alerts.append(alert)

        # Process Shared Identifier Alerts
        for sr in shared_rels:
            s_ent = entities.get(sr.source_id)
            t_ent = entities.get(sr.target_id)
            if s_ent and t_ent:
                title = f"Shared Infrastructure Detected: {sr.relationship_type.replace('_', ' ').title()}"
                alert = Alert(
                    case_id=case_id,
                    entity_id=s_ent.id,
                    title=title,
                    category="SHARED_IDENTIFIER",
                    severity="HIGH",
                    status="NEW",
                    explanation=f"{s_ent.display_name} and {t_ent.display_name} share common operational infrastructure ({sr.relationship_type}).",
                    evidence=[
                        f"Source Entity: {s_ent.display_name} ({s_ent.type})",
                        f"Target Entity: {t_ent.display_name} ({t_ent.type})",
                        f"Shared Type: {sr.relationship_type}",
                        f"Confidence: {sr.confidence}",
                        f"Source Document: {sr.source_document or 'Intelligence Data'}"
                    ],
                    confidence=float(sr.confidence or 0.9),
                    timestamp=datetime.utcnow(),
                    meta_info={"source_id": s_ent.id, "target_id": t_ent.id, "type": sr.relationship_type}
                )
                db.add(alert)
                created_alerts.append(alert)

        # Process Location Alerts
        for la in loc_anomalies:
            title = f"Cross-Network Rendezvous: {la['location']}"
            alert = Alert(
                case_id=case_id,
                entity_id=None,
                title=title,
                category="UNUSUAL_LOCATION_ACTIVITY",
                severity="HIGH",
                status="NEW",
                explanation=la["reason"],
                evidence=la["evidence"],
                confidence=0.86,
                timestamp=datetime.utcnow(),
                meta_info={"location": la["location"], "event_id": la["event_id"]}
            )
            db.add(alert)
            created_alerts.append(alert)

        db.commit()
        return created_alerts

alert_engine = AlertEngine()
