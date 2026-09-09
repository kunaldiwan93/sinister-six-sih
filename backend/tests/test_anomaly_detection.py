import pytest
from app.ingestion.parsers import file_parser

def test_cdr_parser():
    sample_cdr = """caller,receiver,date,duration
9876543210,9811223344,2026-08-01 10:15:00,340
9876543210,9811223344,2026-08-01 14:22:00,520"""
    records, errors = file_parser.parse_cdr_csv(sample_cdr)
    assert len(records) == 2
    assert len(errors) == 0
    assert records[0]["caller_phone"] == "9876543210"

def test_transaction_parser():
    sample_tx = '''sender,receiver,amount,date
ACC1,ACC2,450000,2026-08-01 11:30:00
ACC2,ACC3,"₹50,000",2026-08-02 12:00:00'''
    records, errors = file_parser.parse_transaction_csv(sample_tx)
    assert len(records) == 2
    assert records[0]["amount"] == 450000.0
    assert records[1]["amount"] == 50000.0
