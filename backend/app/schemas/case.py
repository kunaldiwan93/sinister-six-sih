from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class CaseBase(BaseModel):
    case_number: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    meta_info: Optional[Dict[str, Any]] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None

class CaseResponse(CaseBase):
    id: str
    created_at: datetime
    updated_at: datetime
    entity_count: Optional[int] = 0
    relationship_count: Optional[int] = 0
    alert_count: Optional[int] = 0
    document_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
