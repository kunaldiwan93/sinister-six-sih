from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from app.core.database import get_db
from app.models.analysis_run import AnalysisRun
from app.schemas.analysis import AnalysisRunResponse, DocumentUploadResponse
from app.schemas.common import ApiResponse
from app.ingestion.ingestion_service import ingestion_service
from app.graph.graph_metrics import graph_metrics_calculator
from app.graph.community_detection import community_detector
from app.graph.graph_builder import graph_repository
from app.services.alert_engine import alert_engine
from app.services.risk_scoring import risk_scoring_service

router = APIRouter(prefix="", tags=["Analysis & Ingestion"])

@router.get("/analysis-runs", response_model=ApiResponse[List[AnalysisRunResponse]])
def list_analysis_runs(case_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AnalysisRun)
    if case_id:
        query = query.filter(AnalysisRun.case_id == case_id)
    runs = query.order_by(AnalysisRun.started_at.desc()).limit(50).all()
    return ApiResponse(success=True, data=[AnalysisRunResponse.model_validate(r) for r in runs])

@router.get("/analysis-runs/{run_id}", response_model=ApiResponse[AnalysisRunResponse])
def get_analysis_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return ApiResponse(success=True, data=AnalysisRunResponse.model_validate(run))

@router.post("/cases/{case_id}/documents", response_model=ApiResponse[DocumentUploadResponse])
async def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    doc_type: Optional[str] = Form("FIR"),
    db: Session = Depends(get_db)
):
    content_bytes = await file.read()
    doc_title = title or file.filename or "Uploaded Document"
    
    try:
        res = ingestion_service.process_document(
            db=db,
            case_id=case_id,
            title=doc_title,
            doc_type=doc_type or "FIR",
            filename=file.filename or "report.txt",
            content_bytes=content_bytes
        )
        return ApiResponse(success=True, data=DocumentUploadResponse(**res))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Document processing failed: {str(e)}")

@router.post("/cases/{case_id}/cdr")
async def upload_cdr(
    case_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content_bytes = await file.read()
    text = content_bytes.decode("utf-8", errors="ignore")
    res = ingestion_service.process_cdr_file(db, case_id, file.filename or "cdr.csv", text)
    return ApiResponse(success=True, data=res)

@router.post("/cases/{case_id}/transactions")
async def upload_transactions(
    case_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content_bytes = await file.read()
    text = content_bytes.decode("utf-8", errors="ignore")
    res = ingestion_service.process_transaction_file(db, case_id, file.filename or "transactions.csv", text)
    return ApiResponse(success=True, data=res)

@router.post("/cases/{case_id}/analyze")
def trigger_analysis(case_id: str, db: Session = Depends(get_db)):
    graph_repository.build_graph_for_case(db, case_id)
    metrics = graph_metrics_calculator.calculate_and_save_metrics(db, case_id)
    communities = community_detector.detect_and_save_communities(db, case_id)
    alerts = alert_engine.generate_case_alerts(db, case_id)
    risk_scoring_service.calculate_entity_risk_scores(db, case_id)

    return ApiResponse(success=True, data={
        "status": "COMPLETED",
        "message": "Analysis pipeline executed successfully.",
        "metrics": metrics,
        "communities_count": len(communities),
        "alerts_count": len(alerts)
    })
