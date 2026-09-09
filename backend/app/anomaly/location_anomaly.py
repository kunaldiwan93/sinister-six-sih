from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.entity import Entity

class LocationAnomalyDetector:
    @staticmethod
    def detect_anomalies(db: Session, case_id: str) -> List[Dict[str, Any]]:
        events = db.query(Event).filter(Event.case_id == case_id, Event.location_name != None).all()
        entities = {e.id: e for e in db.query(Entity).filter(Entity.case_id == case_id).all()}
        
        anomalies = []
        for ev in events:
            # Check if entities from different communities are co-located
            involved = ev.involved_entity_ids or []
            if len(involved) >= 2:
                comm_ids = set()
                names = []
                for ent_id in involved:
                    ent = entities.get(ent_id)
                    if ent:
                        names.append(ent.display_name)
                        if ent.community_id > 0:
                            comm_ids.add(ent.community_id)

                if len(comm_ids) > 1:
                    anomalies.append({
                        "event_id": ev.id,
                        "title": ev.title,
                        "location": ev.location_name,
                        "involved_entities": names,
                        "communities": list(comm_ids),
                        "reason": f"Cross-community rendezvous detected between clusters {list(comm_ids)} at {ev.location_name}",
                        "evidence": [
                            f"Location: {ev.location_name}",
                            f"Time: {ev.timestamp.strftime('%Y-%m-%d %H:%M') if ev.timestamp else 'N/A'}",
                            f"Participants: {', '.join(names)}",
                            f"Cross-community interaction between clusters {list(comm_ids)}"
                        ]
                    })
        return anomalies

location_anomaly_detector = LocationAnomalyDetector()
