from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class AnalysisRunBase(BaseModel):
    case_id: str
    run_type: Optional[str] = "FULL_PIPELINE"
    status: Optional[str] = "QUEUED"
    input_files: Optional[List[str]] = []
    entities_extracted: Optional[int] = 0
    relationships_extracted: Optional[int] = 0
    alerts_generated: Optional[int] = 0
    summary_stats: Optional[Dict[str, Any]] = {}

class AnalysisRunCreate(AnalysisRunBase):
    pass

class AnalysisRunResponse(AnalysisRunBase):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = 0.0
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    document_id: str
    case_id: str
    title: str
    document_type: str
    entities_extracted: int
    relationships_extracted: int
    status: str
    message: str
    extracted_entities_sample: List[Dict[str, Any]] = []
    extracted_relationships_sample: List[Dict[str, Any]] = []
