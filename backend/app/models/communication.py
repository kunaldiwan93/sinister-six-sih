import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Communication(Base):
    __tablename__ = "communications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    caller_id = Column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    receiver_id = Column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    
    caller_phone = Column(String(50), nullable=False)
    receiver_phone = Column(String(50), nullable=False)
    
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration_seconds = Column(Integer, default=0)
    communication_type = Column(String(50), default="VOICE_CALL")  # VOICE_CALL, SMS, VOIP, ENCRYPTED
    
    # Anomaly indicator
    is_anomalous = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    anomaly_reason = Column(Text, nullable=True)
    
    meta_info = Column(JSON, default=dict)

    case = relationship("Case", back_populates="communications")
    caller_entity = relationship("Entity", foreign_keys=[caller_id])
    receiver_entity = relationship("Entity", foreign_keys=[receiver_id])
