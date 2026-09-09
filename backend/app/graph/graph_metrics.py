import networkx as nx
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.entity import Entity
from app.graph.graph_builder import graph_repository

class GraphMetricsCalculator:
    @staticmethod
    def calculate_and_save_metrics(db: Session, case_id: str) -> Dict[str, Any]:
        """
        Calculates network metrics for a case and updates the Entity records in the database.
        """
        G = graph_repository.get_graph(db, case_id, force_rebuild=True)
        DiG = graph_repository.get_directed_graph(db, case_id)
        
        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()
        
        if node_count == 0:
            return {
                "node_count": 0,
                "edge_count": 0,
                "density": 0.0,
                "top_influential": [],
                "top_intermediaries": []
            }

        # 1. Degree Centrality
        degree_dict = nx.degree_centrality(G)
        
        # 2. Betweenness Centrality
        betweenness_dict = nx.betweenness_centrality(G, normalized=True)
        
        # 3. PageRank
        try:
            pagerank_dict = nx.pagerank(DiG, alpha=0.85, max_iter=200)
        except Exception:
            # Fallback for undirected or disconnected components
            try:
                pagerank_dict = nx.pagerank(G, alpha=0.85, max_iter=200)
            except Exception:
                pagerank_dict = {node: 1.0 / max(node_count, 1) for node in G.nodes()}

        # 4. Density
        density = nx.density(G)

        # Update database entities
        entities = db.query(Entity).filter(Entity.case_id == case_id).all()
        for e in entities:
            e.degree_centrality = round(degree_dict.get(e.id, 0.0), 4)
            e.betweenness_centrality = round(betweenness_dict.get(e.id, 0.0), 4)
            e.pagerank_score = round(pagerank_dict.get(e.id, 0.0), 4)
            
            # Update node attribute cache in memory
            if G.has_node(e.id):
                G.nodes[e.id]["degree_centrality"] = e.degree_centrality
                G.nodes[e.id]["betweenness_centrality"] = e.betweenness_centrality
                G.nodes[e.id]["pagerank_score"] = e.pagerank_score

        db.commit()

        # Top influential (PageRank / Degree)
        top_influential = sorted(
            [{"id": e.id, "name": e.display_name, "type": e.type, "pagerank": e.pagerank_score, "degree": e.degree_centrality} for e in entities],
            key=lambda x: x["pagerank"],
            reverse=True
        )[:5]

        # Top intermediaries (Betweenness)
        top_intermediaries = sorted(
            [{"id": e.id, "name": e.display_name, "type": e.type, "betweenness": e.betweenness_centrality} for e in entities],
            key=lambda x: x["betweenness"],
            reverse=True
        )[:5]

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "density": round(density, 4),
            "top_influential": top_influential,
            "top_intermediaries": top_intermediaries
        }

graph_metrics_calculator = GraphMetricsCalculator()
