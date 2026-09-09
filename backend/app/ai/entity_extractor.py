import re
from typing import List, Dict, Any, Optional

# Pre-compiled Patterns for high precision extraction
PHONE_PATTERN = re.compile(r'(?:\+91[\-\s]?)?[6-9]\d{9}\b')
VEHICLE_PATTERN = re.compile(r'\b[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}\b', re.IGNORECASE)
ACCOUNT_PATTERN = re.compile(r'\b(?:AC|ACC|ACCT|ACCOUNT)[\s#:]*([A-Z0-9]{8,18})\b', re.IGNORECASE)
DATE_PATTERN = re.compile(r'\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b', re.IGNORECASE)
CASE_PATTERN = re.compile(r'\b(?:FIR[\s\-_#:]*[0-9]+/[0-9]+|CASE[\s\-_#:]*[A-Z0-9\-_]+)\b', re.IGNORECASE)

KNOWN_LOCATIONS = [
    "Connaught Place", "Karol Bagh", "Chandni Chowk", "Lajpat Nagar", "Hauz Khas", "Dwarka",
    "Sector 18 Noida", "Cyber City", "MG Road", "Bandra", "Andheri", "Indiranagar", "Koramangala",
    "South Ex", "Rohini", "Saket", "Vasant Kunj", "Mayur Vihar", "Noida Sector 62", "Gurugram Sector 29",
    "Mumbai Port", "IGI Airport", "Delhi Cantt", "Old Delhi Railway Station"
]

KNOWN_PERSONS = [
    "Rohit Sharma", "Amit Verma", "Sameer Khan", "Neha Kapoor", "Vikram Singh",
    "Karan Malhotra", "Pooja Hegde", "Suresh Raina", "Manish Sisodia", "Rajesh Gupta",
    "Sunil Mehra", "Deepak Joshi", "Rakesh Yadav", "Anil Deshmukh", "Vikas Dubey",
    "Mohammad Aslam", "Praveen Kumar", "Ajay Tyagi", "Sanjay Singhania", "Vijay Mallya",
    "Ravi Shastri", "Gaurav Taneja", "Rohan Mehra", "Priya Sharma", "Ankit Patel"
]

KNOWN_ORGS = [
    "Apex Logistics", "Delta Trading Corp", "Skyline Exports", "Kuber Enterprises",
    "Falcon Security Services", "Om Jewellers", "Nexus Holdings", "Crown Real Estate",
    "Blue Dart Express", "National Bank", "ICICI Bank", "HDFC Bank", "State Bank of India"
]

class EntityExtractor:
    def __init__(self):
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.blank("en")
        except Exception:
            pass

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts named entities from raw police reports, FIRs, and intelligence text.
        Returns a structured list of entities with canonical name, display name, type, and confidence.
        """
        if not text:
            return []

        extracted: List[Dict[str, Any]] = []
        seen_keys = set()

        def add_entity(canonical: str, display: str, e_type: str, conf: float = 0.95, meta: Optional[dict] = None):
            key = (e_type, canonical.lower().strip())
            if key not in seen_keys and len(canonical.strip()) > 1:
                seen_keys.add(key)
                extracted.append({
                    "type": e_type,
                    "canonical_name": canonical.strip(),
                    "display_name": display.strip(),
                    "confidence": conf,
                    "meta_info": meta or {}
                })

        # 1. Phone Numbers
        for match in PHONE_PATTERN.finditer(text):
            val = match.group(0).replace(" ", "").replace("-", "")
            if val.startswith("+91"):
                val = val[3:]
            add_entity(val, val, "PHONE", 0.99, {"raw_match": match.group(0)})

        # 2. Vehicles
        for match in VEHICLE_PATTERN.finditer(text):
            val = match.group(0).upper().replace(" ", "")
            add_entity(val, val, "VEHICLE", 0.98, {"registration": val})

        # 3. Bank Accounts
        for match in ACCOUNT_PATTERN.finditer(text):
            val = match.group(1).upper()
            add_entity(val, f"Account {val}", "BANK_ACCOUNT", 0.95, {"account_number": val})

        # 4. Dates
        for match in DATE_PATTERN.finditer(text):
            val = match.group(0)
            add_entity(val, val, "DATE", 0.92, {})

        # 5. Case references
        for match in CASE_PATTERN.finditer(text):
            val = match.group(0).upper()
            add_entity(val, val, "CASE", 0.99, {})

        # 6. Known Locations
        for loc in KNOWN_LOCATIONS:
            if re.search(r'\b' + re.escape(loc) + r'\b', text, re.IGNORECASE):
                add_entity(loc, loc, "LOCATION", 0.95, {})

        # 7. Known Persons
        for person in KNOWN_PERSONS:
            if re.search(r'\b' + re.escape(person) + r'\b', text, re.IGNORECASE):
                add_entity(person, person, "PERSON", 0.96, {})
            else:
                # Also check single word first name if unambiguous in text
                parts = person.split()
                if len(parts) >= 2:
                    first, last = parts[0], parts[1]
                    if re.search(r'\b' + re.escape(first) + r'\b', text) and re.search(r'\b' + re.escape(last) + r'\b', text):
                        add_entity(person, person, "PERSON", 0.90, {})

        # 8. Known Organizations
        for org in KNOWN_ORGS:
            if re.search(r'\b' + re.escape(org) + r'\b', text, re.IGNORECASE):
                add_entity(org, org, "ORGANIZATION", 0.94, {})

        # 9. Generic Regex for Capitalized Person Names (e.g. "Mr. Harish Rawat", "Sameer Khan")
        name_regex = re.compile(r'\b(?:Shri|Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b')
        for match in name_regex.finditer(text):
            name_val = match.group(1).strip()
            add_entity(name_val, name_val, "PERSON", 0.88, {})

        return extracted

entity_extractor = EntityExtractor()
