import networkx as nx
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.entity import Entity
from app.graph.graph_builder import graph_repository

class CommunityDetector:
    @staticmethod
    def detect_and_save_communities(db: Session, case_id: str) -> List[Dict[str, Any]]:
        """
        Detects graph communities and updates entity records. Identifies bridge nodes connecting clusters.
        """
        G = graph_repository.get_graph(db, case_id, force_rebuild=False)
        
        if G.number_of_nodes() < 2:
            return []

        # Find communities using Louvain or greedy modularity
        try:
            communities_generator = nx.community.louvain_communities(G, seed=42)
            communities = list(communities_generator)
        except Exception:
            try:
                communities = list(nx.community.greedy_modularity_communities(G))
            except Exception:
                # Connected components fallback
                communities = list(nx.connected_components(G))

        entity_community_map = {}
        for idx, comm in enumerate(communities, start=1):
            for node_id in comm:
                entity_community_map[node_id] = idx

        # Update in database
        entities = db.query(Entity).filter(Entity.case_id == case_id).all()
        for e in entities:
            c_id = entity_community_map.get(e.id, 0)
            e.community_id = c_id
            if G.has_node(e.id):
                G.nodes[e.id]["community_id"] = c_id

        db.commit()

        # Build community summary statistics
        community_summaries = []
        for idx, comm in enumerate(communities, start=1):
            member_entities = [e for e in entities if e.id in comm]
            type_counts = {}
            for me in member_entities:
                type_counts[me.type] = type_counts.get(me.type, 0) + 1
            
            # Sort top entities by pagerank or betweenness
            top_members = sorted(member_entities, key=lambda x: (x.pagerank_score or 0.0), reverse=True)[:4]

            community_summaries.append({
                "community_id": idx,
                "member_count": len(comm),
                "dominant_types": type_counts,
                "top_entities": [{"id": tm.id, "name": tm.display_name, "type": tm.type, "risk_score": tm.risk_score} for tm in top_members],
                "description": f"Cluster {idx} ({len(comm)} entities - primary type: {max(type_counts, key=type_counts.get) if type_counts else 'MIXED'})"
            })

        return community_summaries

    @staticmethod
    def identify_bridge_nodes(db: Session, case_id: str) -> List[Dict[str, Any]]:
        """
        Identifies nodes that connect 2 or more distinct communities.
        """
        G = graph_repository.get_graph(db, case_id)
        bridge_nodes = []
        
        entities = {e.id: e for e in db.query(Entity).filter(Entity.case_id == case_id).all()}

        for node_id in G.nodes():
            current_entity = entities.get(node_id)
            if not current_entity:
                continue
            
            my_community = current_entity.community_id
            neighbor_communities = set()
            for neighbor_id in G.neighbors(node_id):
                n_entity = entities.get(neighbor_id)
                if n_entity and n_entity.community_id != my_community and n_entity.community_id > 0:
                    neighbor_communities.add(n_entity.community_id)

            if len(neighbor_communities) >= 1 and current_entity.betweenness_centrality > 0.05:
                bridge_nodes.append({
                    "id": current_entity.id,
                    "name": current_entity.display_name,
                    "type": current_entity.type,
                    "betweenness": current_entity.betweenness_centrality,
                    "primary_community": my_community,
                    "connected_communities": list(neighbor_communities),
                    "reason": f"Connects Community {my_community} to Community {list(neighbor_communities)}"
                })

        return sorted(bridge_nodes, key=lambda x: x["betweenness"], reverse=True)

community_detector = CommunityDetector()
