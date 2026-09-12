from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.entity import Entity
from app.models.transaction import Transaction
from app.models.communication import Communication
from app.models.relationship import Relationship
from app.models.event import Event

class RiskScoringService:
    @staticmethod
    def calculate_entity_risk_scores(db: Session, case_id: str) -> None:
        """
        Calculates transparent, weighted investigative risk indicator scores (0-100)
        based on measurable network, communication, transaction, and behavioral signals.
        """
        entities = db.query(Entity).filter(Entity.case_id == case_id).all()
        if not entities:
            return

        # Pre-fetch relations
        transactions = db.query(Transaction).filter(Transaction.case_id == case_id).all()
        communications = db.query(Communication).filter(Communication.case_id == case_id).all()
        relationships = db.query(Relationship).filter(Relationship.case_id == case_id).all()
        events = db.query(Event).filter(Event.case_id == case_id).all()

        # Build lookup tables
        tx_by_entity: Dict[str, List[Transaction]] = {}
        for t in transactions:
            if t.sender_id:
                tx_by_entity.setdefault(t.sender_id, []).append(t)
            if t.receiver_id:
                tx_by_entity.setdefault(t.receiver_id, []).append(t)

        comm_by_entity: Dict[str, List[Communication]] = {}
        for c in communications:
            if c.caller_id:
                comm_by_entity.setdefault(c.caller_id, []).append(c)
            if c.receiver_id:
                comm_by_entity.setdefault(c.receiver_id, []).append(c)

        rel_by_entity: Dict[str, List[Relationship]] = {}
        for r in relationships:
            rel_by_entity.setdefault(r.source_id, []).append(r)
            rel_by_entity.setdefault(r.target_id, []).append(r)

        events_by_entity: Dict[str, List[Event]] = {}
        for ev in events:
            for ent_id in (ev.involved_entity_ids or []):
                events_by_entity.setdefault(ent_id, []).append(ev)

        for e in entities:
            risk_factors = []

            # 1. Communication Anomaly (0-100)
            e_comms = comm_by_entity.get(e.id, [])
            anom_comms = [c for c in e_comms if c.is_anomalous]
            comm_score = min(len(anom_comms) * 35.0 + len(e_comms) * 2.5, 100.0)
            if anom_comms:
                risk_factors.append(f"{len(anom_comms)} anomalous communication pattern(s) / call burst(s) detected")
            elif len(e_comms) >= 8:
                risk_factors.append(f"High communication volume ({len(e_comms)} records)")

            # 2. Transaction Anomaly (0-100)
            e_tx = tx_by_entity.get(e.id, [])
            anom_tx = [t for t in e_tx if t.is_anomalous]
            large_tx = [t for t in e_tx if t.amount > 200000]
            tx_score = min(len(anom_tx) * 45.0 + len(large_tx) * 25.0, 100.0)
            if anom_tx:
                total_anom_val = sum(t.amount for t in anom_tx)
                risk_factors.append(f"Involved in {len(anom_tx)} suspicious financial transfer(s) totaling ₹{total_anom_val:,.2f}")

            # 3. Network Centrality (0-100)
            # Degree centrality is 0-1, scale to 0-100
            centrality_score = min((e.degree_centrality or 0.0) * 250.0 + (e.pagerank_score or 0.0) * 400.0, 100.0)
            if (e.degree_centrality or 0.0) > 0.15:
                risk_factors.append(f"High network centrality (Degree: {e.degree_centrality:.2f}, PageRank: {e.pagerank_score:.3f})")

            # 4. Intermediary / Bridge Score (0-100)
            # Betweenness centrality is key for bridge nodes
            betweenness = e.betweenness_centrality or 0.0
            intermediary_score = min(betweenness * 350.0, 100.0)
            if betweenness > 0.10:
                risk_factors.append(f"Critical network intermediary / bridge node (Betweenness: {betweenness:.2f})")

            # 5. Association Score (0-100)
            # Connections to other high degree / flagged nodes
            e_rels = rel_by_entity.get(e.id, [])
            shared_resources = [r for r in e_rels if "SHARED" in (r.relationship_type or "") or (r.relationship_type or "") in ("USES", "OPERATES")]
            assoc_score = min(len(e_rels) * 8.0 + len(shared_resources) * 20.0, 100.0)
            if shared_resources:
                types = list(set(r.relationship_type for r in shared_resources))
                risk_factors.append(f"Shared identifiers/resources: {', '.join(types)}")

            # 6. Location Anomaly (0-100)
            e_ev = events_by_entity.get(e.id, [])
            severe_events = [ev for ev in e_ev if ev.severity in ("WARNING", "CRITICAL")]
            loc_score = min(len(severe_events) * 40.0 + len(e_ev) * 10.0, 100.0)
            if severe_events:
                risk_factors.append(f"Present at {len(severe_events)} flagged intelligence event(s) / locations")

            # Weighted Formula:
            # 0.20 * comm + 0.20 * tx + 0.20 * centrality + 0.15 * intermediary + 0.15 * assoc + 0.10 * loc
            raw_score = (
                0.20 * comm_score +
                0.20 * tx_score +
                0.20 * centrality_score +
                0.15 * intermediary_score +
                0.15 * assoc_score +
                0.10 * loc_score
            )

            # Cap between 0 and 100
            final_score = round(max(0.0, min(100.0, raw_score)), 1)
            
            # Map score to risk level
            if final_score >= 80.0:
                risk_level = "CRITICAL"
            elif final_score >= 60.0:
                risk_level = "HIGH"
            elif final_score >= 30.0:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW"

            if not risk_factors:
                risk_factors.append("Standard network baseline activity; no elevated indicators flagged.")

            e.risk_score = final_score
            e.risk_level = risk_level
            e.risk_factors = risk_factors

        db.commit()

risk_scoring_service = RiskScoringService()
