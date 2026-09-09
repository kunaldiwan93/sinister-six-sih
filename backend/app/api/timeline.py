from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.event import Event
from app.models.entity import Entity
from app.schemas.event import EventResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.get("", response_model=ApiResponse[List[EventResponse]])
def get_timeline(
    case_id: str,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.case_id == case_id)
    if event_type:
        query = query.filter(Event.event_type == event_type.upper())
    if severity:
        query = query.filter(Event.severity == severity.upper())

    events = query.order_by(Event.timestamp.asc()).limit(limit).all()
    entities = {e.id: e for e in db.query(Entity).filter(Entity.case_id == case_id).all()}

    results = []
    for ev in events:
        involved_ents = []
        for ent_id in (ev.involved_entity_ids or []):
            if ent_id in entities:
                ent = entities[ent_id]
                involved_ents.append({
                    "id": ent.id,
                    "name": ent.display_name,
                    "type": ent.type,
                    "risk_score": ent.risk_score
                })

        if entity_id and entity_id not in (ev.involved_entity_ids or []):
            continue

        results.append(EventResponse(
            id=ev.id,
            case_id=ev.case_id,
            title=ev.title,
            description=ev.description,
            event_type=ev.event_type,
            timestamp=ev.timestamp,
            location_name=ev.location_name,
            involved_entity_ids=ev.involved_entity_ids or [],
            involved_entities=involved_ents,
            source_reference=ev.source_reference,
            severity=ev.severity,
            meta_info=ev.meta_info or {},
            created_at=ev.created_at
        ))
    return ApiResponse(success=True, data=results)
