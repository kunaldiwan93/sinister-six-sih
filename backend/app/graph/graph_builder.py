import networkx as nx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entity import Entity
from app.models.relationship import Relationship

class NetworkXGraphRepository:
    def __init__(self):
        self.graphs: Dict[str, nx.Graph] = {}
        self.directed_graphs: Dict[str, nx.DiGraph] = {}

    def build_graph_for_case(self, db: Session, case_id: str) -> nx.Graph:
        """
        Builds and caches a NetworkX Graph from database entities and relationships for a specific case.
        """
        G = nx.Graph()
        DiG = nx.DiGraph()

        entities = db.query(Entity).filter(Entity.case_id == case_id).all()
        for e in entities:
            node_attrs = {
                "id": e.id,
                "label": e.display_name or e.canonical_name,
                "type": e.type,
                "canonical_name": e.canonical_name,
                "risk_score": float(e.risk_score or 0.0),
                "risk_level": e.risk_level or "LOW",
                "community_id": int(e.community_id or 0),
                "degree_centrality": float(e.degree_centrality or 0.0),
                "betweenness_centrality": float(e.betweenness_centrality or 0.0),
                "pagerank_score": float(e.pagerank_score or 0.0),
                "aliases": e.aliases or [],
                "meta_info": e.meta_info or {},
                "risk_factors": e.risk_factors or [],
                "source_references": e.source_references or []
            }
            G.add_node(e.id, **node_attrs)
            DiG.add_node(e.id, **node_attrs)

        relationships = db.query(Relationship).filter(Relationship.case_id == case_id).all()
        for r in relationships:
            # Check if both endpoints exist
            if G.has_node(r.source_id) and G.has_node(r.target_id):
                edge_attrs = {
                    "id": r.id,
                    "relationship": r.relationship_type,
                    "confidence": float(r.confidence or 1.0),
                    "weight": float(r.weight or 1.0),
                    "source_document": r.source_document or "",
                    "evidence_text": r.evidence_text or "",
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "meta_info": r.meta_info or {}
                }
                G.add_edge(r.source_id, r.target_id, **edge_attrs)
                DiG.add_edge(r.source_id, r.target_id, **edge_attrs)

        self.graphs[case_id] = G
        self.directed_graphs[case_id] = DiG
        return G

    def get_graph(self, db: Session, case_id: str, force_rebuild: bool = False) -> nx.Graph:
        if force_rebuild or case_id not in self.graphs:
            return self.build_graph_for_case(db, case_id)
        return self.graphs[case_id]

    def get_directed_graph(self, db: Session, case_id: str, force_rebuild: bool = False) -> nx.DiGraph:
        if force_rebuild or case_id not in self.directed_graphs:
            self.build_graph_for_case(db, case_id)
        return self.directed_graphs[case_id]

graph_repository = NetworkXGraphRepository()
