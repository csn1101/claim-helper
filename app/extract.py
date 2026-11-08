"""Rule-based extraction of basic fields from an insurer's claim letter.

This is the simple baseline: plain Python and regular expressions, no AI.
Later, an AI model will handle the harder fields, and the same tests will
measure whether it does better or worse than this baseline.
"""
import re

# An identifier is letters, digits, slashes and hyphens, e.g. MSH/CL/2026/004871
_ID = r"([A-Z0-9][A-Z0-9/\-]+)"

# Patterns are tried in order; the first one that matches wins.
# They are case-sensitive on purpose, so "Claim not admissible" is never read as "Claim No".
_CLAIM_PATTERNS = [
    rf"Claim\s*(?:Reference\s*)?(?:No\.?|Number)[ \t]*:?[ \t]*{_ID}",
    rf"Our\s+Ref[ \t]*:?[ \t]*{_ID}",
]
_POLICY_PATTERNS = [
    rf"Policy\s*(?:No\.?|Number)[ \t]*:?[ \t]*{_ID}",
]


def _first_match(patterns: list[str], text: str) -> str | None:
    """Return the first captured group found by any of the patterns, else None."""
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def parse_inr_amount(text: str) -> int | None:
    """Turn text like 'Rs. 2,45,000/-', 'INR 38,500' or '₹72,000/-' into whole rupees.

    Returns None if no amount is found. Paise (decimals) are ignored for now.
    """
    match = re.search(r"(?:Rs\.?|INR|₹)\s*([\d,]+)", text)
    if not match:
        return None
    digits = match.group(1).replace(",", "")
    return int(digits) if digits else None


def extract_fields(text: str) -> dict:
    """Extract the fields we can find with simple rules from the letter text."""
    return {
        "claim_number": _first_match(_CLAIM_PATTERNS, text),
        "policy_number": _first_match(_POLICY_PATTERNS, text),
    }