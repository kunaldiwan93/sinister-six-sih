import networkx as nx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.graph.graph_builder import graph_repository
from app.schemas.graph import GraphResponse, GraphNode, GraphEdge, GraphMetadata, ShortestPathResponse, ShortestPathStep

class GraphQueryService:
    @staticmethod
    def get_full_graph(db: Session, case_id: str, limit: int = 300) -> GraphResponse:
        G = graph_repository.get_graph(db, case_id)
        
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # Get nodes
        for node_id, data in list(G.nodes(data=True))[:limit]:
            nodes.append(GraphNode(
                id=node_id,
                label=data.get("label", node_id),
                type=data.get("type", "UNKNOWN"),
                risk_score=float(data.get("risk_score", 0.0)),
                risk_level=data.get("risk_level", "LOW"),
                community_id=int(data.get("community_id", 0)),
                metrics={
                    "degree": data.get("degree_centrality", 0.0),
                    "betweenness": data.get("betweenness_centrality", 0.0),
                    "pagerank": data.get("pagerank_score", 0.0)
                },
                metadata=data.get("meta_info", {})
            ))

        node_ids_set = {n.id for n in nodes}

        # Get edges
        for u, v, data in G.edges(data=True):
            if u in node_ids_set and v in node_ids_set:
                edges.append(GraphEdge(
                    id=data.get("id", f"{u}_{v}"),
                    source=u,
                    target=v,
                    relationship=data.get("relationship", "ASSOCIATED_WITH"),
                    confidence=float(data.get("confidence", 1.0)),
                    weight=float(data.get("weight", 1.0)),
                    timestamp=data.get("timestamp"),
                    source_document=data.get("source_document"),
                    metadata=data.get("meta_info", {})
                ))

        density = nx.density(G) if G.number_of_nodes() > 0 else 0.0

        return GraphResponse(
            nodes=nodes,
            edges=edges,
            metadata=GraphMetadata(
                node_count=len(nodes),
                edge_count=len(edges),
                community_count=len(set(n.community_id for n in nodes if n.community_id > 0)),
                density=round(density, 4)
            )
        )

    @staticmethod
    def find_shortest_path(db: Session, case_id: str, source_id: str, target_id: str) -> ShortestPathResponse:
        G = graph_repository.get_graph(db, case_id)
        
        if not G.has_node(source_id) or not G.has_node(target_id):
            return ShortestPathResponse(
                found=False,
                path_length=0,
                path_nodes=[],
                path_edges=[],
                steps=[],
                explanation="One or both of the specified entities do not exist in the case graph."
            )

        try:
            path = nx.shortest_path(G, source=source_id, target=target_id)
        except nx.NetworkXNoPath:
            return ShortestPathResponse(
                found=False,
                path_length=0,
                path_nodes=[],
                path_edges=[],
                steps=[],
                explanation=f"No direct or indirect connection path found between the selected entities."
            )

        steps: List[ShortestPathStep] = []
        path_edges: List[str] = []
        explanation_parts = []

        entities = {e.id: e for e in db.query(Entity).filter(Entity.case_id == case_id).all()}

        for i in range(len(path)):
            curr_id = path[i]
            curr_entity = entities.get(curr_id)
            label = curr_entity.display_name if curr_entity else curr_id
            e_type = curr_entity.type if curr_entity else "UNKNOWN"

            rel_to_next = None
            edge_id = None
            evidence = None

            if i < len(path) - 1:
                next_id = path[i+1]
                edge_data = G.get_edge_data(curr_id, next_id) or {}
                rel_to_next = edge_data.get("relationship", "ASSOCIATED_WITH")
                edge_id = edge_data.get("id")
                if edge_id:
                    path_edges.append(edge_id)
                evidence = edge_data.get("evidence_text") or edge_data.get("source_document")

                next_entity = entities.get(next_id)
                next_label = next_entity.display_name if next_entity else next_id
                explanation_parts.append(f"{label} [{e_type}] --({rel_to_next})--> {next_label}")

            steps.append(ShortestPathStep(
                node_id=curr_id,
                node_label=label,
                node_type=e_type,
                relationship_to_next=rel_to_next,
                edge_id=edge_id,
                evidence=evidence
            ))

        full_explanation = f"Connection path identified with {len(path) - 1} intermediary hop(s):\n" + " -> ".join(explanation_parts)

        return ShortestPathResponse(
            found=True,
            path_length=len(path) - 1,
            path_nodes=path,
            path_edges=path_edges,
            steps=steps,
            explanation=full_explanation
        )

    @staticmethod
    def get_neighborhood(db: Session, case_id: str, entity_id: str, hops: int = 1) -> GraphResponse:
        G = graph_repository.get_graph(db, case_id)
        if not G.has_node(entity_id):
            return GraphResponse(
                nodes=[],
                edges=[],
                metadata=GraphMetadata(node_count=0, edge_count=0, community_count=0, density=0.0)
            )

        ego = nx.ego_graph(G, entity_id, radius=hops)
        
        nodes: List[GraphNode] = []
        for node_id, data in ego.nodes(data=True):
            nodes.append(GraphNode(
                id=node_id,
                label=data.get("label", node_id),
                type=data.get("type", "UNKNOWN"),
                risk_score=float(data.get("risk_score", 0.0)),
                risk_level=data.get("risk_level", "LOW"),
                community_id=int(data.get("community_id", 0)),
                metrics={
                    "degree": data.get("degree_centrality", 0.0),
                    "betweenness": data.get("betweenness_centrality", 0.0),
                    "pagerank": data.get("pagerank_score", 0.0)
                },
                metadata=data.get("meta_info", {})
            ))

        edges: List[GraphEdge] = []
        for u, v, data in ego.edges(data=True):
            edges.append(GraphEdge(
                id=data.get("id", f"{u}_{v}"),
                source=u,
                target=v,
                relationship=data.get("relationship", "ASSOCIATED_WITH"),
                confidence=float(data.get("confidence", 1.0)),
                weight=float(data.get("weight", 1.0)),
                timestamp=data.get("timestamp"),
                source_document=data.get("source_document"),
                metadata=data.get("meta_info", {})
            ))

        return GraphResponse(
            nodes=nodes,
            edges=edges,
            metadata=GraphMetadata(
                node_count=len(nodes),
                edge_count=len(edges),
                community_count=len(set(n.community_id for n in nodes if n.community_id > 0)),
                density=round(nx.density(ego), 4) if ego.number_of_nodes() > 0 else 0.0
            )
        )

    @staticmethod
    def filter_graph(db: Session, case_id: str, req) -> GraphResponse:
        G = graph_repository.get_graph(db, case_id)
        
        filtered_nodes = []
        for node_id, data in G.nodes(data=True):
            # Check entity type filter
            if req.entity_types and data.get("type") not in req.entity_types:
                continue
            # Check risk filter
            if req.min_risk_score is not None and data.get("risk_score", 0.0) < req.min_risk_score:
                continue
            # Check community filter
            if req.community_id is not None and data.get("community_id") != req.community_id:
                continue
            # Check search query
            if req.search_query:
                q = req.search_query.lower()
                label = data.get("label", "").lower()
                canonical = data.get("canonical_name", "").lower()
                if q not in label and q not in canonical:
                    continue

            filtered_nodes.append(GraphNode(
                id=node_id,
                label=data.get("label", node_id),
                type=data.get("type", "UNKNOWN"),
                risk_score=float(data.get("risk_score", 0.0)),
                risk_level=data.get("risk_level", "LOW"),
                community_id=int(data.get("community_id", 0)),
                metrics={
                    "degree": data.get("degree_centrality", 0.0),
                    "betweenness": data.get("betweenness_centrality", 0.0),
                    "pagerank": data.get("pagerank_score", 0.0)
                },
                metadata=data.get("meta_info", {})
            ))

        node_ids_set = {n.id for n in filtered_nodes}
        filtered_edges = []
        for u, v, data in G.edges(data=True):
            if u in node_ids_set and v in node_ids_set:
                if req.relationship_types and data.get("relationship") not in req.relationship_types:
                    continue
                filtered_edges.append(GraphEdge(
                    id=data.get("id", f"{u}_{v}"),
                    source=u,
                    target=v,
                    relationship=data.get("relationship", "ASSOCIATED_WITH"),
                    confidence=float(data.get("confidence", 1.0)),
                    weight=float(data.get("weight", 1.0)),
                    timestamp=data.get("timestamp"),
                    source_document=data.get("source_document"),
                    metadata=data.get("meta_info", {})
                ))

        return GraphResponse(
            nodes=filtered_nodes[:req.limit or 300],
            edges=filtered_edges,
            metadata=GraphMetadata(
                node_count=len(filtered_nodes),
                edge_count=len(filtered_edges),
                community_count=len(set(n.community_id for n in filtered_nodes if n.community_id > 0)),
                density=0.0
            )
        )

graph_query_service = GraphQueryService()
