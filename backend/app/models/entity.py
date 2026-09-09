import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Entity core attributes
    type = Column(String(50), nullable=False, index=True)  # PERSON, PHONE, VEHICLE, LOCATION, ORGANIZATION, BANK_ACCOUNT, etc.
    canonical_name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    aliases = Column(JSON, default=list)
    
    # Risk and Graph analytics scores
    confidence = Column(Float, default=1.0)
    risk_score = Column(Float, default=0.0)  # 0 to 100
    risk_level = Column(String(50), default="LOW")  # LOW, MODERATE, HIGH, CRITICAL
    
    # Graph metrics cache
    degree_centrality = Column(Float, default=0.0)
    betweenness_centrality = Column(Float, default=0.0)
    pagerank_score = Column(Float, default=0.0)
    community_id = Column(Integer, default=0)
    
    # Traceability and explainability
    source_references = Column(JSON, default=list)  # list of doc_ids, text excerpts
    risk_factors = Column(JSON, default=list)       # detailed reasons for the risk score
    meta_info = Column(JSON, default=dict)          # additional attributes (e.g. phone model, vehicle registration, address)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    case = relationship("Case", back_populates="entities")
    alerts = relationship("Alert", back_populates="entity", cascade="all, delete-orphan")
