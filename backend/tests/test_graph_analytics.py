import pytest
import networkx as nx
from app.graph.graph_metrics import GraphMetricsCalculator
from app.graph.community_detection import CommunityDetector

def test_graph_metrics_calculation():
    G = nx.Graph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.add_edge("B", "D")
    G.add_edge("D", "E")

    degree_dict = nx.degree_centrality(G)
    betweenness_dict = nx.betweenness_centrality(G)

    # Node B and D are key intermediary bridges
    assert betweenness_dict["B"] > 0
    assert degree_dict["B"] == max(degree_dict.values())
