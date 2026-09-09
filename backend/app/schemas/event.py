from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: Optional[str] = "INTERACTION"
    timestamp: datetime
    location_name: Optional[str] = None
    involved_entity_ids: Optional[List[str]] = []
    source_reference: Optional[str] = None
    severity: Optional[str] = "INFO"
    meta_info: Optional[Dict[str, Any]] = {}

class EventCreate(EventBase):
    case_id: str

class EventResponse(EventBase):
    id: str
    case_id: str
    created_at: datetime
    involved_entities: Optional[List[Dict[str, Any]]] = []

    model_config = ConfigDict(from_attributes=True)
