from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.alert import Alert
from app.models.entity import Entity
from app.schemas.alert import AlertResponse, AlertUpdate
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=ApiResponse[List[AlertResponse]])
def list_alerts(
    case_id: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert).filter(Alert.case_id == case_id)
    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if category:
        query = query.filter(Alert.category == category.upper())
    if status:
        query = query.filter(Alert.status == status.upper())

    alerts = query.order_by(Alert.timestamp.desc()).all()
    results = []
    for a in alerts:
        ent = db.query(Entity).filter(Entity.id == a.entity_id).first() if a.entity_id else None
        results.append(AlertResponse(
            id=a.id,
            case_id=a.case_id,
            entity_id=a.entity_id,
            entity_name=ent.display_name if ent else None,
            entity_type=ent.type if ent else None,
            title=a.title,
            category=a.category,
            severity=a.severity,
            status=a.status,
            explanation=a.explanation,
            evidence=a.evidence or [],
            confidence=float(a.confidence or 0.85),
            timestamp=a.timestamp,
            meta_info=a.meta_info or {}
        ))
    return ApiResponse(success=True, data=results)

@router.patch("/{alert_id}", response_model=ApiResponse[AlertResponse])
def update_alert(alert_id: str, req: AlertUpdate, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")

    if req.status:
        a.status = req.status.upper()
    if req.explanation:
        a.explanation = req.explanation

    db.commit()
    db.refresh(a)

    ent = db.query(Entity).filter(Entity.id == a.entity_id).first() if a.entity_id else None
    return ApiResponse(success=True, data=AlertResponse(
        id=a.id,
        case_id=a.case_id,
        entity_id=a.entity_id,
        entity_name=ent.display_name if ent else None,
        entity_type=ent.type if ent else None,
        title=a.title,
        category=a.category,
        severity=a.severity,
        status=a.status,
        explanation=a.explanation,
        evidence=a.evidence or [],
        confidence=float(a.confidence or 0.85),
        timestamp=a.timestamp,
        meta_info=a.meta_info or {}
    ))
