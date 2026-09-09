from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class EntityBase(BaseModel):
    type: str
    canonical_name: str
    display_name: str
    aliases: Optional[List[str]] = []
    confidence: Optional[float] = 1.0
    risk_score: Optional[float] = 0.0
    risk_level: Optional[str] = "LOW"
    degree_centrality: Optional[float] = 0.0
    betweenness_centrality: Optional[float] = 0.0
    pagerank_score: Optional[float] = 0.0
    community_id: Optional[int] = 0
    source_references: Optional[List[Any]] = []
    risk_factors: Optional[List[Any]] = []
    meta_info: Optional[Dict[str, Any]] = {}

class EntityCreate(EntityBase):
    case_id: str

class EntityUpdate(BaseModel):
    display_name: Optional[str] = None
    aliases: Optional[List[str]] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None

class EntityResponse(EntityBase):
    id: str
    case_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EntityMetrics(BaseModel):
    degree: float
    betweenness: float
    pagerank: float
    community_id: int
    connections_count: int

class EntityProfile(BaseModel):
    entity: EntityResponse
    metrics: EntityMetrics
    risk_reasons: List[str]
    associated_entities: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    transactions: List[Dict[str, Any]]
    communications: List[Dict[str, Any]]
