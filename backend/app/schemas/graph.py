from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # PERSON, PHONE, VEHICLE, etc.
    risk_score: float
    risk_level: str
    community_id: int
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: str
    confidence: float
    weight: float
    timestamp: Optional[str] = None
    source_document: Optional[str] = None
    metadata: Dict[str, Any]

class GraphMetadata(BaseModel):
    node_count: int
    edge_count: int
    community_count: int
    density: float
    diameter: Optional[int] = None
    communities: List[Dict[str, Any]] = []

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: GraphMetadata

class ShortestPathRequest(BaseModel):
    source_id: str
    target_id: str
    case_id: str

class ShortestPathStep(BaseModel):
    node_id: str
    node_label: str
    node_type: str
    relationship_to_next: Optional[str] = None
    edge_id: Optional[str] = None
    evidence: Optional[str] = None

class ShortestPathResponse(BaseModel):
    found: bool
    path_length: int
    path_nodes: List[str]
    path_edges: List[str]
    steps: List[ShortestPathStep]
    explanation: str

class GraphFilterRequest(BaseModel):
    case_id: str
    entity_types: Optional[List[str]] = None
    relationship_types: Optional[List[str]] = None
    min_risk_score: Optional[float] = None
    community_id: Optional[int] = None
    search_query: Optional[str] = None
    limit: Optional[int] = 300
