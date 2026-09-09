from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class RelationshipBase(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    confidence: Optional[float] = 1.0
    weight: Optional[float] = 1.0
    source_document: Optional[str] = None
    evidence_text: Optional[str] = None
    timestamp: Optional[datetime] = None
    meta_info: Optional[Dict[str, Any]] = {}

class RelationshipCreate(RelationshipBase):
    case_id: str

class RelationshipResponse(RelationshipBase):
    id: str
    case_id: str
    created_at: datetime
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    target_name: Optional[str] = None
    target_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
