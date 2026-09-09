import pytest
from app.ai.entity_extractor import entity_extractor
from app.ai.relationship_extractor import relationship_extractor

def test_extract_phone_and_vehicle():
    text = "Rohit Sharma met Amit Verma near Connaught Place on 12 August. They contacted Sameer Khan using 9876543210. Vehicle DL01AB1234 was observed nearby."
    entities = entity_extractor.extract_entities(text)
    
    types = {e["type"] for e in entities}
    assert "PERSON" in types
    assert "LOCATION" in types
    assert "PHONE" in types
    assert "VEHICLE" in types

    canonical_names = {e["canonical_name"] for e in entities}
    assert "9876543210" in canonical_names
    assert "DL01AB1234" in canonical_names

def test_relationship_extraction():
    text = "Rohit Sharma met Amit Verma near Connaught Place. Rohit called Sameer Khan."
    entities = entity_extractor.extract_entities(text)
    relationships = relationship_extractor.extract_relationships(text, entities)
    
    rel_types = {r["relationship_type"] for r in relationships}
    assert "MET" in rel_types or "VISITED" in rel_types or "CALLED" in rel_types
