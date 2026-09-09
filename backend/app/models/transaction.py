import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sender_id = Column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    receiver_id = Column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    
    sender_account = Column(String(100), nullable=False)
    receiver_account = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Anomaly indicator
    is_anomalous = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    anomaly_reason = Column(Text, nullable=True)
    
    meta_info = Column(JSON, default=dict)

    case = relationship("Case", back_populates="transactions")
    sender_entity = relationship("Entity", foreign_keys=[sender_id])
    receiver_entity = relationship("Entity", foreign_keys=[receiver_id])
