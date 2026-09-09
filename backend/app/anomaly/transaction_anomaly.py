import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.alert import Alert

class TransactionAnomalyDetector:
    @staticmethod
    def detect_anomalies(db: Session, case_id: str) -> List[Dict[str, Any]]:
        transactions = db.query(Transaction).filter(Transaction.case_id == case_id).all()
        if len(transactions) < 3:
            return []

        # Convert to DataFrame
        data = []
        for t in transactions:
            data.append({
                "id": t.id,
                "amount": float(t.amount),
                "sender_account": t.sender_account,
                "receiver_account": t.receiver_account,
                "sender_id": t.sender_id,
                "receiver_id": t.receiver_id,
                "timestamp": t.timestamp,
                "hour": t.timestamp.hour if t.timestamp else 12
            })
        df = pd.DataFrame(data)

        # Statistical Thresholds
        mean_amt = df["amount"].mean()
        std_amt = df["amount"].std() if len(df) > 1 else 1.0
        p95 = df["amount"].quantile(0.95)

        # Isolation Forest on amount and time features
        features = df[["amount", "hour"]].values
        try:
            iso = IsolationForest(contamination=0.15, random_state=42)
            preds = iso.fit_predict(features)
            scores = -iso.score_samples(features)
        except Exception:
            # Fallback to pure statistical z-score
            z_scores = np.abs((df["amount"] - mean_amt) / (std_amt + 1e-6))
            preds = np.where(z_scores > 2.0, -1, 1)
            scores = z_scores / 3.0

        anomalies = []
        tx_dict = {t.id: t for t in transactions}

        for idx, row in df.iterrows():
            is_anomaly = (preds[idx] == -1) or (row["amount"] >= p95 and row["amount"] > 200000)
            score = float(scores[idx])

            t = tx_dict[row["id"]]
            t.is_anomalous = bool(is_anomaly)
            t.anomaly_score = round(score, 3)

            if is_anomaly:
                reasons = []
                if row["amount"] >= p95:
                    reasons.append(f"Amount ₹{row['amount']:,.2f} exceeds 95th percentile threshold (₹{p95:,.2f})")
                if row["amount"] > mean_amt + (1.5 * std_amt):
                    reasons.append(f"Statistically unusual transfer value (Z-score > 1.5)")
                if row["hour"] < 6 or row["hour"] > 22:
                    reasons.append(f"Transaction occurred during unusual hours ({row['hour']:02d}:00)")
                
                reason_text = "; ".join(reasons) if reasons else "High anomaly score detected by Isolation Forest"
                t.anomaly_reason = reason_text

                anomalies.append({
                    "transaction_id": t.id,
                    "sender_account": t.sender_account,
                    "receiver_account": t.receiver_account,
                    "sender_id": t.sender_id,
                    "receiver_id": t.receiver_id,
                    "amount": t.amount,
                    "anomaly_score": t.anomaly_score,
                    "reason": reason_text,
                    "evidence": [
                        f"Amount: ₹{t.amount:,.2f}",
                        f"Sender Account: {t.sender_account}",
                        f"Receiver Account: {t.receiver_account}",
                        f"Deviation: {(t.amount / (mean_amt + 1e-6)):.1f}x higher than average transaction size"
                    ]
                })

        db.commit()
        return anomalies

transaction_anomaly_detector = TransactionAnomalyDetector()
