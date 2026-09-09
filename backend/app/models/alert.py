import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # TRANSACTION_ANOMALY, COMMUNICATION_ANOMALY, BRIDGE_NODE, etc.
    severity = Column(String(50), nullable=False, default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), nullable=False, default="NEW", index=True)  # NEW, REVIEWED, DISMISSED
    
    explanation = Column(Text, nullable=False)
    evidence = Column(JSON, default=list)  # structured evidence list
    confidence = Column(Float, default=0.85)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    meta_info = Column(JSON, default=dict)

    case = relationship("Case", back_populates="alerts")
    entity = relationship("Entity", back_populates="alerts")
