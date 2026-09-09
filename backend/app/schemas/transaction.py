from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class TransactionBase(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float
    currency: Optional[str] = "INR"
    timestamp: datetime
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    is_anomalous: Optional[bool] = False
    anomaly_score: Optional[float] = 0.0
    anomaly_reason: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = {}

class TransactionCreate(TransactionBase):
    case_id: str

class TransactionResponse(TransactionBase):
    id: str
    case_id: str
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
