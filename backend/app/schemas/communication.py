from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class CommunicationBase(BaseModel):
    caller_phone: str
    receiver_phone: str
    timestamp: datetime
    duration_seconds: Optional[int] = 0
    communication_type: Optional[str] = "VOICE_CALL"
    caller_id: Optional[str] = None
    receiver_id: Optional[str] = None
    is_anomalous: Optional[bool] = False
    anomaly_score: Optional[float] = 0.0
    anomaly_reason: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = {}

class CommunicationCreate(CommunicationBase):
    case_id: str

class CommunicationResponse(CommunicationBase):
    id: str
    case_id: str
    caller_name: Optional[str] = None
    receiver_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
