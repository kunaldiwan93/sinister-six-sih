from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.alert import Alert
from app.models.event import Event
from app.models.transaction import Transaction
from app.models.communication import Communication
from app.schemas.entity import EntityResponse, EntityProfile, EntityMetrics
from app.schemas.common import ApiResponse
from app.graph.graph_queries import graph_query_service

router = APIRouter(prefix="/entities", tags=["Entities"])

@router.get("", response_model=ApiResponse[List[EntityResponse]])
def list_entities(
    case_id: str,
    type: Optional[str] = None,
    min_risk: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Entity).filter(Entity.case_id == case_id)
    if type:
        query = query.filter(Entity.type == type)
    if min_risk is not None:
        query = query.filter(Entity.risk_score >= min_risk)
    if search:
        s = f"%{search.lower()}%"
        query = query.filter((Entity.canonical_name.ilike(s)) | (Entity.display_name.ilike(s)))
    
    entities = query.order_by(Entity.risk_score.desc()).limit(limit).all()
    return ApiResponse(success=True, data=[EntityResponse.model_validate(e) for e in entities])

@router.get("/{entity_id}", response_model=ApiResponse[EntityResponse])
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    e = db.query(Entity).filter(Entity.id == entity_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Entity not found")
    return ApiResponse(success=True, data=EntityResponse.model_validate(e))

@router.get("/{entity_id}/profile", response_model=ApiResponse[EntityProfile])
def get_entity_profile(entity_id: str, db: Session = Depends(get_db)):
    e = db.query(Entity).filter(Entity.id == entity_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Fetch associated relationships
    rels = db.query(Relationship).filter(
        (Relationship.source_id == entity_id) | (Relationship.target_id == entity_id)
    ).all()
    
    associated = []
    for r in rels:
        is_source = (r.source_id == entity_id)
        other_id = r.target_id if is_source else r.source_id
        other_ent = db.query(Entity).filter(Entity.id == other_id).first()
        associated.append({
            "relationship_id": r.id,
            "relationship_type": r.relationship_type,
            "direction": "OUTGOING" if is_source else "INCOMING",
            "connected_entity_id": other_id,
            "connected_entity_name": other_ent.display_name if other_ent else other_id,
            "connected_entity_type": other_ent.type if other_ent else "UNKNOWN",
            "confidence": r.confidence,
            "evidence": r.evidence_text or r.source_document
        })

    # Fetch alerts
    alerts = db.query(Alert).filter(Alert.entity_id == entity_id).all()
    alerts_data = [{"id": a.id, "title": a.title, "category": a.category, "severity": a.severity, "explanation": a.explanation} for a in alerts]

    # Fetch transactions
    txs = db.query(Transaction).filter(
        (Transaction.sender_id == entity_id) | (Transaction.receiver_id == entity_id)
    ).order_by(Transaction.timestamp.desc()).limit(15).all()
    tx_data = [{"id": t.id, "amount": t.amount, "sender": t.sender_account, "receiver": t.receiver_account, "is_anomalous": t.is_anomalous, "timestamp": t.timestamp.isoformat()} for t in txs]

    # Fetch communications
    comms = db.query(Communication).filter(
        (Communication.caller_id == entity_id) | (Communication.receiver_id == entity_id)
    ).order_by(Communication.timestamp.desc()).limit(15).all()
    comm_data = [{"id": c.id, "caller": c.caller_phone, "receiver": c.receiver_phone, "duration": c.duration_seconds, "is_anomalous": c.is_anomalous, "timestamp": c.timestamp.isoformat()} for c in comms]

    # Fetch events
    events = db.query(Event).filter(Event.case_id == e.case_id).all()
    involved_events = []
    for ev in events:
        if entity_id in (ev.involved_entity_ids or []):
            involved_events.append({
                "id": ev.id,
                "title": ev.title,
                "location": ev.location_name,
                "timestamp": ev.timestamp.isoformat(),
                "severity": ev.severity
            })

    metrics = EntityMetrics(
        degree=float(e.degree_centrality or 0.0),
        betweenness=float(e.betweenness_centrality or 0.0),
        pagerank=float(e.pagerank_score or 0.0),
        community_id=int(e.community_id or 0),
        connections_count=len(associated)
    )

    profile = EntityProfile(
        entity=EntityResponse.model_validate(e),
        metrics=metrics,
        risk_reasons=e.risk_factors or ["Standard activity"],
        associated_entities=associated,
        recent_events=involved_events,
        alerts=alerts_data,
        transactions=tx_data,
        communications=comm_data
    )

    return ApiResponse(success=True, data=profile)

@router.get("/{entity_id}/neighbors")
def get_entity_neighbors(entity_id: str, hops: int = 1, db: Session = Depends(get_db)):
    e = db.query(Entity).filter(Entity.id == entity_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Entity not found")
    subgraph = graph_query_service.get_neighborhood(db, e.case_id, entity_id, hops)
    return ApiResponse(success=True, data=subgraph)
