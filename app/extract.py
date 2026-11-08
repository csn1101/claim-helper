"""Rule-based extraction of basic fields from an insurer's claim letter.

This is the simple baseline: plain Python and regular expressions, no AI.
Later, an AI model will handle the harder fields, and the same tests will
measure whether it does better or worse than this baseline.
"""
import re
from datetime import date

# ---------- claim and policy numbers ----------

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

# ---------- claim amount ----------

# A currency marker followed by a number, captured together, e.g. "Rs. 2,45,000".
_AMOUNT = r"((?:Rs\.?|INR|₹)\s*[\d,]+)"

# The first amount in a letter is often something else (for example the sum insured),
# so we only accept an amount that sits right next to words that mean "the amount claimed".
# Tried in order; the first match wins. (?i) makes the words case-insensitive.
_CLAIM_AMOUNT_PATTERNS = [
    rf"(?i)total claimed amount (?:of )?{_AMOUNT}",
    rf"(?i)amount claimed(?: is|:)?\s*{_AMOUNT}",
    rf"(?i)claimed amount (?:is )?{_AMOUNT}",
    rf"(?i)total bill (?:amount )?(?:is|submitted:?)\s*{_AMOUNT}",
    rf"(?i)claim (?:of|for) {_AMOUNT}",
]

# ---------- dates ----------

_MONTHS = {
    name: number
    for number, name in enumerate(
        ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
        start=1,
    )
}

# 02/04/2026, 24.04.2026, 18-07-2026 (day first, as written in India)
_NUMERIC_DATE = re.compile(r"\b(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})\b")
# 20 February 2026, 28th May 2026, 14-Aug-2026, 02 Feb 2026
_TEXT_DATE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?[ \-]([A-Za-z]{3,9})\.?,?[ \-](\d{4})\b")


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


def parse_date(text: str) -> str | None:
    """Return the first real date found in the text, as 'YYYY-MM-DD', else None."""
    found: list[tuple[int, date]] = []

    for match in _NUMERIC_DATE.finditer(text):
        day, month, year = (int(g) for g in match.groups())
        try:
            found.append((match.start(), date(year, month, day)))
        except ValueError:  # e.g. 31/02/2026 is not a real date
            continue

    for match in _TEXT_DATE.finditer(text):
        day, month_name, year = match.groups()
        month = _MONTHS.get(month_name[:3].lower())
        if month is None:  # the word was not a month, so this was not a date
            continue
        try:
            found.append((match.start(), date(int(year), month, int(day))))
        except ValueError:
            continue

    if not found:
        return None
    return min(found, key=lambda item: item[0])[1].isoformat()  # earliest in the text


def _letter_date(text: str) -> str | None:
    """Use a line labelled 'Date:' if there is one, otherwise the first date in the letter."""
    labelled = re.search(r"^[ \t]*Date[ \t]*:[ \t]*(.+)$", text, re.MULTILINE)
    if labelled:
        found = parse_date(labelled.group(1))
        if found:
            return found
    return parse_date(text)


def _claim_amount(text: str) -> int | None:
    captured = _first_match(_CLAIM_AMOUNT_PATTERNS, text)
    return parse_inr_amount(captured) if captured else None


def extract_fields(text: str) -> dict:
    """Extract the fields we can find with simple rules from the letter text."""
    return {
        "claim_number": _first_match(_CLAIM_PATTERNS, text),
        "policy_number": _first_match(_POLICY_PATTERNS, text),
        "letter_date": _letter_date(text),
        "claim_amount_inr": _claim_amount(text),
    }