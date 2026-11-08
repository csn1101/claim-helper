"""Tests for the claim letter extractor.

Run from the project root with:   pytest
"""
import json
from pathlib import Path

import pytest

from app.extract import extract_fields, parse_inr_amount

LETTERS_DIR = Path(__file__).resolve().parent.parent / "sample_letters"
ANSWER_KEY = json.loads((LETTERS_DIR / "answer_key.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Rs. 2,45,000/-", 245000),
        ("INR 38,500", 38500),
        ("₹72,000/-", 72000),
        ("Rs. 0", 0),
        ("Rs.1,11,550", 111550),
        ("no amount in this sentence", None),
    ],
)
def test_parse_inr_amount(text, expected):
    assert parse_inr_amount(text) == expected


@pytest.mark.parametrize("entry", ANSWER_KEY, ids=[e["file"] for e in ANSWER_KEY])
def test_claim_and_policy_numbers(entry):
    text = (LETTERS_DIR / entry["file"]).read_text(encoding="utf-8")
    result = extract_fields(text)
    assert result["claim_number"] == entry["claim_number"]
    assert result["policy_number"] == entry["policy_number"]