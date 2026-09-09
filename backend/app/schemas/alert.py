from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class AlertBase(BaseModel):
    title: str
    category: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    status: Optional[str] = "NEW"  # NEW, REVIEWED, DISMISSED
    explanation: str
    evidence: Optional[List[Any]] = []
    confidence: Optional[float] = 0.85
    timestamp: Optional[datetime] = None
    meta_info: Optional[Dict[str, Any]] = {}

class AlertCreate(AlertBase):
    case_id: str
    entity_id: Optional[str] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None  # NEW, REVIEWED, DISMISSED
    explanation: Optional[str] = None

class AlertResponse(AlertBase):
    id: str
    case_id: str
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
