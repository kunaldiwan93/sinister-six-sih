import re
from typing import List, Dict, Any, Tuple
from app.ai.entity_extractor import entity_extractor

class RelationshipExtractor:
    def extract_relationships(self, text: str, extracted_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts semantic relationships between recognized entities based on NLP dependency patterns and sentence contexts.
        """
        if not text or len(extracted_entities) < 2:
            return []

        relationships: List[Dict[str, Any]] = []
        seen_edges = set()

        # Split into sentences for localized relationship extraction
        sentences = [s.strip() for s in re.split(r'[\.\n\r]+', text) if len(s.strip()) > 5]

        # Entity index by canonical name and display name
        ent_by_name = {}
        for e in extracted_entities:
            ent_by_name[e["display_name"].lower()] = e
            ent_by_name[e["canonical_name"].lower()] = e

        def add_rel(source_name: str, target_name: str, rel_type: str, conf: float, excerpt: str):
            s_ent = ent_by_name.get(source_name.lower())
            t_ent = ent_by_name.get(target_name.lower())
            if s_ent and t_ent and s_ent["canonical_name"] != t_ent["canonical_name"]:
                edge_key = (s_ent["canonical_name"], t_ent["canonical_name"], rel_type)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    relationships.append({
                        "source_canonical": s_ent["canonical_name"],
                        "source_display": s_ent["display_name"],
                        "source_type": s_ent["type"],
                        "target_canonical": t_ent["canonical_name"],
                        "target_display": t_ent["display_name"],
                        "target_type": t_ent["type"],
                        "relationship_type": rel_type,
                        "confidence": conf,
                        "evidence_text": excerpt[:250],
                        "meta_info": {"pattern_match": rel_type}
                    })

        for sentence in sentences:
            s_lower = sentence.lower()

            # Find all entities present in this sentence
            present_entities = []
            for e in extracted_entities:
                if e["display_name"].lower() in s_lower or e["canonical_name"].lower() in s_lower:
                    present_entities.append(e)

            persons = [e for e in present_entities if e["type"] == "PERSON"]
            phones = [e for e in present_entities if e["type"] == "PHONE"]
            vehicles = [e for e in present_entities if e["type"] == "VEHICLE"]
            locations = [e for e in present_entities if e["type"] == "LOCATION"]
            orgs = [e for e in present_entities if e["type"] == "ORGANIZATION"]
            accounts = [e for e in present_entities if e["type"] == "BANK_ACCOUNT"]

            # Pattern 1: Meeting ("met", "meeting", "spotted with", "seen together")
            if any(k in s_lower for k in ["met", "meeting", "spotted with", "seen together", "rendezvous", "gathered"]):
                if len(persons) >= 2:
                    for i in range(len(persons)):
                        for j in range(i + 1, len(persons)):
                            add_rel(persons[i]["display_name"], persons[j]["display_name"], "MET", 0.95, sentence)
                
                # Person met at location
                for p in persons:
                    for loc in locations:
                        add_rel(p["display_name"], loc["display_name"], "VISITED", 0.94, sentence)

            # Pattern 2: Communication ("called", "contacted", "dialed", "spoke with", "messaged")
            if any(k in s_lower for k in ["called", "contacted", "dialed", "spoke to", "spoke with", "messaged", "phone call"]):
                if len(persons) >= 2:
                    add_rel(persons[0]["display_name"], persons[1]["display_name"], "CALLED", 0.94, sentence)
                for p in persons:
                    for ph in phones:
                        add_rel(p["display_name"], ph["display_name"], "USES", 0.96, sentence)

            # Pattern 3: Vehicle Usage / Ownership & Co-Travel
            if any(k in s_lower for k in ["owns", "driver", "driving", "travelled in", "vehicle", "car", "suv", "co-travelling", "shared vehicle"]):
                for p in persons:
                    for v in vehicles:
                        rel = "OWNS" if "owns" in s_lower else "USES"
                        add_rel(p["display_name"], v["display_name"], rel, 0.93, sentence)

                # Direct Person-to-Person co-travel edge when multiple persons are mentioned in vehicular context
                if len(persons) >= 2 and any(k in s_lower for k in ["co-travelling", "together", "along with", "with", "shared vehicle", "travelling"]):
                    for i in range(len(persons)):
                        for j in range(i + 1, len(persons)):
                            add_rel(persons[i]["display_name"], persons[j]["display_name"], "SHARED_VEHICLE", 0.94, sentence)

            # Pattern 4: Financial ("transferred", "paid", "received ₹", "sent money", "hawala", "wire")
            if any(k in s_lower for k in ["transfer", "paid", "sent", "received", "deposited", "withdrew", "account"]):
                if len(persons) >= 2:
                    add_rel(persons[0]["display_name"], persons[1]["display_name"], "TRANSFERRED_MONEY", 0.92, sentence)
                for p in persons:
                    for acc in accounts:
                        add_rel(p["display_name"], acc["display_name"], "USES", 0.95, sentence)

            # Pattern 5: Organization Membership ("director", "member of", "works at", "associated with", "partner in")
            if any(k in s_lower for k in ["director", "member", "works at", "associated with", "partner", "firm", "employee"]):
                for p in persons:
                    for org in orgs:
                        add_rel(p["display_name"], org["display_name"], "MEMBER_OF", 0.94, sentence)

            # Pattern 6: General co-occurrence association if in same sentence
            if len(persons) >= 2 and not any(k in s_lower for k in ["met", "called", "transferred"]):
                for i in range(len(persons)):
                    for j in range(i + 1, len(persons)):
                        add_rel(persons[i]["display_name"], persons[j]["display_name"], "ASSOCIATED_WITH", 0.85, sentence)

            for p in persons:
                for loc in locations:
                    if not any(k in s_lower for k in ["met"]):
                        add_rel(p["display_name"], loc["display_name"], "VISITED", 0.88, sentence)

        return relationships

relationship_extractor = RelationshipExtractor()
