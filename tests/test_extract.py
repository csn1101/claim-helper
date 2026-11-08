"""Tests for the claim letter extractor.

Run from the project root with:   pytest
"""
import json
from pathlib import Path

import pytest

from app.extract import extract_fields, parse_date, parse_inr_amount

LETTERS_DIR = Path(__file__).resolve().parent.parent / "sample_letters"
ANSWER_KEY = json.loads((LETTERS_DIR / "answer_key.json").read_text(encoding="utf-8"))
LETTER_IDS = [e["file"] for e in ANSWER_KEY]


def read_letter(entry) -> str:
    return (LETTERS_DIR / entry["file"]).read_text(encoding="utf-8")


# ---------- small building blocks ----------


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


@pytest.mark.parametrize(
    "text, expected",
    [
        ("02/04/2026", "2026-04-02"),  # day first, as in India
        ("24.04.2026", "2026-04-24"),
        ("18-07-2026", "2026-07-18"),
        ("20 February 2026", "2026-02-20"),
        ("28th May 2026", "2026-05-28"),
        ("14-Aug-2026", "2026-08-14"),
        ("02 Feb 2026", "2026-02-02"),
        ("Date: 11 August 2026", "2026-08-11"),
        ("31/02/2026", None),  # not a real date
        ("no date here", None),
    ],
)
def test_parse_date(text, expected):
    assert parse_date(text) == expected


# ---------- whole letters, checked against the answer key ----------


@pytest.mark.parametrize("entry", ANSWER_KEY, ids=LETTER_IDS)
def test_claim_and_policy_numbers(entry):
    result = extract_fields(read_letter(entry))
    assert result["claim_number"] == entry["claim_number"]
    assert result["policy_number"] == entry["policy_number"]


@pytest.mark.parametrize("entry", ANSWER_KEY, ids=LETTER_IDS)
def test_letter_date(entry):
    result = extract_fields(read_letter(entry))
    assert result["letter_date"] == entry["letter_date"]


@pytest.mark.parametrize("entry", ANSWER_KEY, ids=LETTER_IDS)
def test_claim_amount(entry):
    result = extract_fields(read_letter(entry))
    assert result["claim_amount_inr"] == entry["claim_amount_inr"]


def test_first_amount_in_the_letter_is_not_always_the_claim_amount():
    """Letter 5 starts with the sum insured (Rs. 5,00,000) long before the claim amount."""
    entry = next(e for e in ANSWER_KEY if e["file"].startswith("letter_05"))
    text = read_letter(entry)
    assert parse_inr_amount(text) == 500000  # the naive answer is wrong
    assert extract_fields(text)["claim_amount_inr"] == 310600  # the real claim amount