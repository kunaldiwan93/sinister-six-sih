from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.graph import GraphResponse, ShortestPathRequest, ShortestPathResponse, GraphFilterRequest
from app.schemas.common import ApiResponse
from app.graph.graph_queries import graph_query_service
from app.graph.graph_metrics import graph_metrics_calculator
from app.graph.community_detection import community_detector

router = APIRouter(prefix="", tags=["Graph"])

@router.get("/cases/{case_id}/graph", response_model=ApiResponse[GraphResponse])
def get_case_graph(case_id: str, limit: int = 300, db: Session = Depends(get_db)):
    graph = graph_query_service.get_full_graph(db, case_id, limit=limit)
    return ApiResponse(success=True, data=graph)

@router.post("/graph/shortest-path", response_model=ApiResponse[ShortestPathResponse])
def calculate_shortest_path(req: ShortestPathRequest, db: Session = Depends(get_db)):
    result = graph_query_service.find_shortest_path(db, req.case_id, req.source_id, req.target_id)
    return ApiResponse(success=True, data=result)

@router.post("/graph/filter", response_model=ApiResponse[GraphResponse])
def filter_case_graph(req: GraphFilterRequest, db: Session = Depends(get_db)):
    result = graph_query_service.filter_graph(db, req.case_id, req)
    return ApiResponse(success=True, data=result)

@router.get("/communities")
def list_communities(case_id: str, db: Session = Depends(get_db)):
    communities = community_detector.detect_and_save_communities(db, case_id)
    bridges = community_detector.identify_bridge_nodes(db, case_id)
    return ApiResponse(success=True, data={
        "communities": communities,
        "bridge_nodes": bridges,
        "count": len(communities)
    })

@router.get("/cases/{case_id}/metrics")
def get_graph_metrics(case_id: str, db: Session = Depends(get_db)):
    metrics = graph_metrics_calculator.calculate_and_save_metrics(db, case_id)
    return ApiResponse(success=True, data=metrics)
