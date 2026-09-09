from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.entity import Entity
from app.schemas.transaction import TransactionResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=ApiResponse[List[TransactionResponse]])
def list_transactions(
    case_id: str,
    is_anomalous: Optional[bool] = None,
    min_amount: Optional[float] = None,
    account: Optional[str] = None,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.case_id == case_id)
    if is_anomalous is not None:
        query = query.filter(Transaction.is_anomalous == is_anomalous)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if account:
        s = f"%{account}%"
        query = query.filter((Transaction.sender_account.ilike(s)) | (Transaction.receiver_account.ilike(s)))

    txs = query.order_by(Transaction.timestamp.desc()).limit(limit).all()
    results = []
    for t in txs:
        s_ent = db.query(Entity).filter(Entity.id == t.sender_id).first() if t.sender_id else None
        r_ent = db.query(Entity).filter(Entity.id == t.receiver_id).first() if t.receiver_id else None
        
        results.append(TransactionResponse(
            id=t.id,
            case_id=t.case_id,
            sender_id=t.sender_id,
            receiver_id=t.receiver_id,
            sender_name=s_ent.display_name if s_ent else t.sender_account,
            receiver_name=r_ent.display_name if r_ent else t.receiver_account,
            sender_account=t.sender_account,
            receiver_account=t.receiver_account,
            amount=t.amount,
            currency=t.currency,
            timestamp=t.timestamp,
            is_anomalous=t.is_anomalous,
            anomaly_score=t.anomaly_score,
            anomaly_reason=t.anomaly_reason,
            meta_info=t.meta_info or {}
        ))
    return ApiResponse(success=True, data=results)
