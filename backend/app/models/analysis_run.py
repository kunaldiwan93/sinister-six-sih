import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    run_type = Column(String(100), default="FULL_PIPELINE")  # FULL_PIPELINE, GRAPH_ANALYTICS, ANOMALY_DETECTION, NLP_EXTRACTION
    status = Column(String(50), default="QUEUED", index=True)  # QUEUED, PROCESSING, COMPLETED, FAILED
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    
    input_files = Column(JSON, default=list)
    entities_extracted = Column(Integer, default=0)
    relationships_extracted = Column(Integer, default=0)
    alerts_generated = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    summary_stats = Column(JSON, default=dict)

    case = relationship("Case", back_populates="analysis_runs")
