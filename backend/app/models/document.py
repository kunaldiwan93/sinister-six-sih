import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), default="FIR")  # FIR, SURVEILLANCE, INTELLIGENCE, CDR_CSV, TRANS_CSV
    file_path = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=True)
    processed_status = Column(String(50), default="PENDING")  # PENDING, PROCESSED, FAILED
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="documents")
