import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship_type = Column(String(100), nullable=False, index=True)  # CALLED, TRANSFERRED_MONEY, OWNS, USES, MET, etc.
    confidence = Column(Float, default=1.0)
    weight = Column(Float, default=1.0)
    
    source_document = Column(String(255), nullable=True)  # File name or FIR ID
    evidence_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=True)
    
    meta_info = Column(JSON, default=dict)  # extra attributes like call duration, amount, frequency
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="relationships")
    source_entity = relationship("Entity", foreign_keys=[source_id])
    target_entity = relationship("Entity", foreign_keys=[target_id])
