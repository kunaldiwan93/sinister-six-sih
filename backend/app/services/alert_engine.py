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

        # 5. Shared Identifiers & Temporal Asset Sharing Analysis
        # A. Direct SHARED_* edges between Person entities
        direct_shared_rels = db.query(Relationship).filter(
            Relationship.case_id == case_id,
            Relationship.relationship_type.in_(["SHARED_PHONE", "SHARED_VEHICLE", "SHARED_ACCOUNT", "SHARED_LOCATION"])
        ).all()

        for sr in direct_shared_rels:
            s_ent = entities.get(sr.source_id)
            t_ent = entities.get(sr.target_id)
            if s_ent and t_ent:
                # Ensure we only generate Person-to-Person alerts for direct SHARED_* relationships
                if s_ent.type == "PERSON" and t_ent.type == "PERSON":
                    rel_label = sr.relationship_type.replace('_', ' ').title()
                    if sr.relationship_type == "SHARED_VEHICLE":
                        title = f"Concurrent Co-Travel Detected: {s_ent.display_name} ↔ {t_ent.display_name}"
                        explanation = f"{s_ent.display_name} and {t_ent.display_name} were observed traveling together in a shared vehicle."
                    else:
                        title = f"Shared Infrastructure Detected: {rel_label}"
                        explanation = f"{s_ent.display_name} and {t_ent.display_name} share common operational infrastructure ({sr.relationship_type})."

                    alert = Alert(
                        case_id=case_id,
                        entity_id=s_ent.id,
                        title=title,
                        category="SHARED_IDENTIFIER",
                        severity="HIGH",
                        status="NEW",
                        explanation=explanation,
                        evidence=[
                            f"Person 1: {s_ent.display_name}",
                            f"Person 2: {t_ent.display_name}",
                            f"Shared Type: {sr.relationship_type}",
                            f"Confidence: {sr.confidence}",
                            f"Evidence: {sr.evidence_text or sr.source_document or 'Intelligence Data'}"
                        ],
                        confidence=float(sr.confidence or 0.9),
                        timestamp=sr.timestamp or datetime.utcnow(),
                        meta_info={"source_id": s_ent.id, "target_id": t_ent.id, "type": sr.relationship_type}
                    )
                    db.add(alert)
                    created_alerts.append(alert)

        # B. Derived Shared Asset Analysis (Vehicles, Phones, Bank Accounts)
        asset_entities = [e for e in entities.values() if e.type in ("VEHICLE", "PHONE", "BANK_ACCOUNT")]
        for asset in asset_entities:
            # Find all usage relationships pointing to this asset entity
            usage_rels = db.query(Relationship).filter(
                Relationship.case_id == case_id,
                Relationship.target_id == asset.id,
                Relationship.relationship_type.in_(["USES", "OPERATES", "OWNS", "TRAVELED_IN", "SHARED_VEHICLE"])
            ).all()

            # Group usage by person entity
            person_usages: Dict[str, List[Relationship]] = {}
            for r in usage_rels:
                src = entities.get(r.source_id)
                if src and src.type == "PERSON":
                    if src.id not in person_usages:
                        person_usages[src.id] = []
                    person_usages[src.id].append(r)

            if len(person_usages) >= 2:
                user_ids = list(person_usages.keys())
                # Pairwise comparison of users sharing this asset
                for i in range(len(user_ids)):
                    for j in range(i + 1, len(user_ids)):
                        p1 = entities[user_ids[i]]
                        p2 = entities[user_ids[j]]
                        rels1 = person_usages[user_ids[i]]
                        rels2 = person_usages[user_ids[j]]

                        # Check for temporal concurrency
                        is_concurrent = False
                        concurrent_time = None
                        for r1 in rels1:
                            for r2 in rels2:
                                t1 = r1.timestamp
                                t2 = r2.timestamp
                                # If timestamps are both set and within 2 hours, or if same evidence document
                                if t1 and t2:
                                    time_diff = abs((t1 - t2).total_seconds())
                                    if time_diff <= 7200:
                                        is_concurrent = True
                                        concurrent_time = t1.strftime('%Y-%m-%d %H:%M')
                                        break
                                elif r1.source_document and r1.source_document == r2.source_document:
                                    is_concurrent = True
                                    break
                            if is_concurrent:
                                break

                        if asset.type == "VEHICLE":
                            if is_concurrent:
                                title = f"Concurrent Vehicle Co-Travel: {p1.display_name} & {p2.display_name}"
                                severity = "CRITICAL"
                                exp_time = f" at {concurrent_time}" if concurrent_time else ""
                                explanation = f"{p1.display_name} and {p2.display_name} were detected traveling concurrently in Vehicle {asset.display_name}{exp_time}."
                            else:
                                title = f"Sequential Shared Vehicle Usage: Vehicle {asset.display_name}"
                                severity = "MEDIUM"
                                explanation = f"{p1.display_name} and {p2.display_name} operated the same vehicle ({asset.display_name}) at different times."
                        else:
                            title = f"Shared Asset Infrastructure: {asset.type.title()} {asset.display_name}"
                            severity = "HIGH"
                            explanation = f"{p1.display_name} and {p2.display_name} share common operational asset {asset.display_name} ({asset.type})."

                        alert = Alert(
                            case_id=case_id,
                            entity_id=asset.id,
                            title=title,
                            category="SHARED_IDENTIFIER",
                            severity=severity,
                            status="NEW",
                            explanation=explanation,
                            evidence=[
                                f"Asset: {asset.display_name} ({asset.type})",
                                f"Person 1: {p1.display_name}",
                                f"Person 2: {p2.display_name}",
                                f"Concurrency: {'Concurrent Co-Travel' if is_concurrent else 'Sequential Sharing'}",
                                f"Timestamp: {concurrent_time or 'Observed Intelligence Event'}"
                            ],
                            confidence=0.93,
                            timestamp=datetime.utcnow(),
                            meta_info={"asset_id": asset.id, "person1_id": p1.id, "person2_id": p2.id, "is_concurrent": is_concurrent, "timestamp": concurrent_time}
                        )
                        db.add(alert)
                        created_alerts.append(alert)

        # C. Single-Suspect Vehicle & Driver Threat Analysis
        vehicles = [e for e in entities.values() if e.type == "VEHICLE"]
        for v in vehicles:
            v_meta = v.meta_info or {}
            v_category = v_meta.get("vehicle_category", "PERSONAL_VEHICLE")
            owner_name = v_meta.get("registered_owner")
            driver_name = v_meta.get("primary_driver")

            # Query all relationships connected to this vehicle
            v_rels = db.query(Relationship).filter(
                Relationship.case_id == case_id,
                Relationship.target_id == v.id,
                Relationship.relationship_type.in_(["DRIVES", "OWNS", "TRAVELED_IN", "OPERATES", "USES"])
            ).all()

            drivers = [r for r in v_rels if r.relationship_type in ("DRIVES", "OPERATES")]
            passengers = [r for r in v_rels if r.relationship_type in ("TRAVELED_IN", "USES")]

            for pass_rel in passengers:
                p_ent = entities.get(pass_rel.source_id)
                if not p_ent or p_ent.type != "PERSON":
                    continue

                ts_str = pass_rel.timestamp.strftime('%Y-%m-%d %H:%M') if pass_rel.timestamp else "Observed Movement"

                # Check if driver is distinct from passenger
                for drv_rel in drivers:
                    d_ent = entities.get(drv_rel.source_id)
                    if d_ent and d_ent.id != p_ent.id:
                        drv_ts = drv_rel.timestamp.strftime('%Y-%m-%d %H:%M') if drv_rel.timestamp else ts_str
                        
                        if v_category == "COMMERCIAL_CAB":
                            title = f"Commercial Cab Transit: {p_ent.display_name} ({v.display_name})"
                            severity = "LOW"
                            category = "COMMERCIAL_CAB_TRANSIT"
                            explanation = f"{p_ent.display_name} traveled via commercial cab {v.display_name} operated by driver {d_ent.display_name} at {drv_ts}."
                        else:
                            title = f"Suspicious Escorted Transit: {p_ent.display_name} (Driver: {d_ent.display_name})"
                            severity = "CRITICAL" if p_ent.risk_score > 60 or d_ent.risk_score > 60 else "HIGH"
                            category = "SUSPICIOUS_DRIVER_ESCORT"
                            explanation = f"{p_ent.display_name} was transported in syndicate asset {v.display_name} driven by operative {d_ent.display_name} at {drv_ts}."

                        alert = Alert(
                            case_id=case_id,
                            entity_id=v.id,
                            title=title,
                            category=category,
                            severity=severity,
                            status="NEW",
                            explanation=explanation,
                            evidence=[
                                f"Passenger: {p_ent.display_name} (Risk: {p_ent.risk_score:.0f})",
                                f"Driver: {d_ent.display_name} (Risk: {d_ent.risk_score:.0f})",
                                f"Vehicle: {v.display_name} ({v_category})",
                                f"Event Timestamp: {drv_ts}"
                            ],
                            confidence=0.92,
                            timestamp=drv_rel.timestamp or datetime.utcnow(),
                            meta_info={"vehicle_id": v.id, "passenger_id": p_ent.id, "driver_id": d_ent.id, "vehicle_category": v_category, "timestamp": drv_ts}
                        )
                        db.add(alert)
                        created_alerts.append(alert)

                # Check for Self-Driven Transit by Registered Owner
                if owner_name and p_ent.display_name.lower() == owner_name.lower():
                    title = f"Owner Self-Driven Transit: {p_ent.display_name} ({v.display_name})"
                    alert = Alert(
                        case_id=case_id,
                        entity_id=v.id,
                        title=title,
                        category="SELF_DRIVEN_TRANSIT",
                        severity="MEDIUM",
                        status="NEW",
                        explanation=f"{p_ent.display_name} self-drove personal vehicle {v.display_name} across operational movement points at {ts_str}.",
                        evidence=[
                            f"Owner/Driver: {p_ent.display_name}",
                            f"Vehicle: {v.display_name} ({v_category})",
                            f"Event Timestamp: {ts_str}"
                        ],
                        confidence=0.95,
                        timestamp=pass_rel.timestamp or datetime.utcnow(),
                        meta_info={"vehicle_id": v.id, "owner_id": p_ent.id, "vehicle_category": v_category, "timestamp": ts_str}
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
