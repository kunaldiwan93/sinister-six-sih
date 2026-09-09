import pandas as pd
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.communication import Communication

class CommunicationAnomalyDetector:
    @staticmethod
    def detect_anomalies(db: Session, case_id: str) -> List[Dict[str, Any]]:
        comms = db.query(Communication).filter(Communication.case_id == case_id).all()
        if len(comms) < 5:
            return []

        data = []
        for c in comms:
            data.append({
                "id": c.id,
                "caller_phone": c.caller_phone,
                "receiver_phone": c.receiver_phone,
                "caller_id": c.caller_id,
                "receiver_id": c.receiver_id,
                "timestamp": c.timestamp,
                "duration": c.duration_seconds or 0,
                "date": c.timestamp.date() if c.timestamp else None,
                "hour": c.timestamp.hour if c.timestamp else 12
            })
        df = pd.DataFrame(data)

        # 1. Frequency per pair per day
        pair_counts = df.groupby(["caller_phone", "receiver_phone", "date"]).size().reset_index(name="daily_call_count")
        burst_pairs = set()
        for _, row in pair_counts[pair_counts["daily_call_count"] >= 5].iterrows():
            burst_pairs.add((row["caller_phone"], row["receiver_phone"], row["date"]))

        # 2. Total calls per caller
        caller_counts = df.groupby("caller_phone").size().to_dict()
        avg_calls = df.shape[0] / max(len(caller_counts), 1)

        anomalies = []
        comm_dict = {c.id: c for c in comms}

        for idx, row in df.iterrows():
            c = comm_dict[row["id"]]
            is_burst = (row["caller_phone"], row["receiver_phone"], row["date"]) in burst_pairs
            is_night = row["hour"] >= 23 or row["hour"] <= 4
            is_extreme_duration = row["duration"] > 1800  # > 30 minutes

            is_anomalous = is_burst or (is_night and row["duration"] > 300)
            
            reasons = []
            if is_burst:
                reasons.append("High-frequency communication burst (>5 calls/day between pair)")
            if is_night:
                reasons.append(f"Unusual late-night communication ({row['hour']:02d}:00)")
            if is_extreme_duration:
                reasons.append(f"Extended call duration ({row['duration'] // 60} minutes)")

            score = 0.85 if is_burst else (0.65 if is_night else 0.0)

            c.is_anomalous = is_anomalous
            c.anomaly_score = score
            c.anomaly_reason = "; ".join(reasons) if reasons else None

            if is_anomalous:
                anomalies.append({
                    "communication_id": c.id,
                    "caller_phone": c.caller_phone,
                    "receiver_phone": c.receiver_phone,
                    "caller_id": c.caller_id,
                    "receiver_id": c.receiver_id,
                    "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                    "anomaly_score": score,
                    "reason": c.anomaly_reason,
                    "evidence": [
                        f"Caller: {c.caller_phone}",
                        f"Receiver: {c.receiver_phone}",
                        f"Duration: {c.duration_seconds} seconds",
                        f"Anomaly trigger: {c.anomaly_reason}"
                    ]
                })

        db.commit()
        return anomalies

communication_anomaly_detector = CommunicationAnomalyDetector()
