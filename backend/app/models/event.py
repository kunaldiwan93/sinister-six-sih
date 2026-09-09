import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(100), default="INTERACTION")  # MEETING, CALL, TRANSACTION, SURVEILLANCE, ARREST, MOVEMENT
    
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    location_name = Column(String(255), nullable=True)
    
    # Associated entity IDs stored as JSON list for timeline linking
    involved_entity_ids = Column(JSON, default=list)
    source_reference = Column(String(255), nullable=True)
    severity = Column(String(50), default="INFO")  # INFO, WARNING, CRITICAL
    
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="events")
