from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.case import Case
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.alert import Alert
from app.models.document import Document
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.schemas.common import ApiResponse
from app.ai.investigation_assistant import investigation_assistant

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=ApiResponse[List[CaseResponse]])
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    results = []
    for c in cases:
        c_dict = {
            "id": c.id,
            "case_number": c.case_number,
            "name": c.name,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "meta_info": c.meta_info or {},
            "entity_count": db.query(Entity).filter(Entity.case_id == c.id).count(),
            "relationship_count": db.query(Relationship).filter(Relationship.case_id == c.id).count(),
            "alert_count": db.query(Alert).filter(Alert.case_id == c.id).count(),
            "document_count": db.query(Document).filter(Document.case_id == c.id).count(),
        }
        results.append(CaseResponse(**c_dict))
    return ApiResponse(success=True, data=results)

@router.post("", response_model=ApiResponse[CaseResponse])
def create_case(req: CaseCreate, db: Session = Depends(get_db)):
    existing = db.query(Case).filter(Case.case_number == req.case_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="A case with this number already exists.")
    
    new_case = Case(
        case_number=req.case_number,
        name=req.name,
        description=req.description,
        status=req.status or "ACTIVE",
        meta_info=req.meta_info or {}
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return ApiResponse(success=True, data=CaseResponse.model_validate(new_case))

@router.get("/{case_id}", response_model=ApiResponse[CaseResponse])
def get_case(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found.")
    
    c_dict = {
        "id": c.id,
        "case_number": c.case_number,
        "name": c.name,
        "description": c.description,
        "status": c.status,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "meta_info": c.meta_info or {},
        "entity_count": db.query(Entity).filter(Entity.case_id == c.id).count(),
        "relationship_count": db.query(Relationship).filter(Relationship.case_id == c.id).count(),
        "alert_count": db.query(Alert).filter(Alert.case_id == c.id).count(),
        "document_count": db.query(Document).filter(Document.case_id == c.id).count(),
    }
    return ApiResponse(success=True, data=CaseResponse(**c_dict))

@router.get("/{case_id}/summary")
def get_case_summary(case_id: str, db: Session = Depends(get_db)):
    summary = investigation_assistant.generate_investigation_summary(db, case_id)
    return ApiResponse(success=True, data=summary)
