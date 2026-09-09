import re
import difflib
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.entity import Entity

class EntityResolutionService:
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalizes a string for canonical comparison.
        """
        if not name:
            return ""
        # Remove honorifics
        s = re.sub(r'^(mr\.|mrs\.|ms\.|shri|smt\.|dr\.|inspector|constable|adv\.)\s+', '', name, flags=re.IGNORECASE)
        # Remove special characters except alphanumeric and whitespace
        s = re.sub(r'[^\w\s]', '', s)
        # Collapse whitespace and lowercase
        s = " ".join(s.lower().split())
        return s

    @staticmethod
    def normalize_identifier(identifier: str) -> str:
        """
        Normalizes phone numbers, vehicle numbers, or bank account numbers.
        """
        if not identifier:
            return ""
        # Remove spaces, dashes, dots, +91
        s = re.sub(r'[\s\-\.\(\)]', '', identifier).upper()
        if s.startswith("+91"):
            s = s[3:]
        elif s.startswith("91") and len(s) == 12:
            s = s[2:]
        return s

    @classmethod
    def find_matching_entity(cls, db: Session, case_id: str, raw_name: str, entity_type: str, threshold: float = 0.88) -> Optional[Entity]:
        """
        Attempts to resolve an entity to an existing canonical record in the database using exact or high-confidence fuzzy matching.
        """
        norm_name = cls.normalize_name(raw_name) if entity_type == "PERSON" else cls.normalize_identifier(raw_name)
        
        # 1. Exact canonical match
        exact_match = db.query(Entity).filter(
            Entity.case_id == case_id,
            Entity.type == entity_type,
            Entity.canonical_name == norm_name
        ).first()
        if exact_match:
            return exact_match

        # 2. For phone / vehicle / bank account, only exact identifier matches should merge
        if entity_type in ["PHONE", "VEHICLE", "BANK_ACCOUNT"]:
            return None

        # 3. For persons, check aliases and fuzzy matches
        candidates = db.query(Entity).filter(
            Entity.case_id == case_id,
            Entity.type == entity_type
        ).all()

        for cand in candidates:
            # Check if name is in aliases
            if raw_name.lower() in [a.lower() for a in (cand.aliases or [])]:
                return cand
            
            # Fuzzy match on canonical names
            sim = difflib.SequenceMatcher(None, norm_name, cand.canonical_name).ratio()
            if sim >= threshold:
                return cand

            # Match on first name + last name initial (e.g. "Rohit Sharma" vs "Rohit S.")
            parts1 = norm_name.split()
            parts2 = cand.canonical_name.split()
            if len(parts1) >= 2 and len(parts2) >= 2:
                if parts1[0] == parts2[0] and (parts1[1][0] == parts2[1][0] and (len(parts1[1]) == 1 or len(parts2[1]) == 1)):
                    return cand

        return None

entity_resolution_service = EntityResolutionService()
