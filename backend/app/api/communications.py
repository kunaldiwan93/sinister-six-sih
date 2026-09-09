from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.communication import Communication
from app.models.entity import Entity
from app.schemas.communication import CommunicationResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/communications", tags=["Communications"])

@router.get("", response_model=ApiResponse[List[CommunicationResponse]])
def list_communications(
    case_id: str,
    is_anomalous: Optional[bool] = None,
    phone: Optional[str] = None,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    query = db.query(Communication).filter(Communication.case_id == case_id)
    if is_anomalous is not None:
        query = query.filter(Communication.is_anomalous == is_anomalous)
    if phone:
        s = f"%{phone}%"
        query = query.filter((Communication.caller_phone.ilike(s)) | (Communication.receiver_phone.ilike(s)))

    comms = query.order_by(Communication.timestamp.desc()).limit(limit).all()
    results = []
    for c in comms:
        caller_ent = db.query(Entity).filter(Entity.id == c.caller_id).first() if c.caller_id else None
        recv_ent = db.query(Entity).filter(Entity.id == c.receiver_id).first() if c.receiver_id else None
        
        results.append(CommunicationResponse(
            id=c.id,
            case_id=c.case_id,
            caller_id=c.caller_id,
            receiver_id=c.receiver_id,
            caller_name=caller_ent.display_name if caller_ent else c.caller_phone,
            receiver_name=recv_ent.display_name if recv_ent else c.receiver_phone,
            caller_phone=c.caller_phone,
            receiver_phone=c.receiver_phone,
            timestamp=c.timestamp,
            duration_seconds=c.duration_seconds,
            communication_type=c.communication_type,
            is_anomalous=c.is_anomalous,
            anomaly_score=c.anomaly_score,
            anomaly_reason=c.anomaly_reason,
            meta_info=c.meta_info or {}
        ))
    return ApiResponse(success=True, data=results)
