"""Pure, unit-testable parsing helpers for Stage 1.

Every function here is a pure function over plain values (strings, lists)
with no I/O — deliberately, so they can be unit tested without opening a
PDF. Behaviour is grounded directly in architecture §1 (ground truth) and
§5.1/§5.4 (the parts of the normalization narrative that define what a
parsed value on ``structured_rows.csv`` actually is, per §4.1's schema).
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple

from .models import RowKind, SupplierContext

# --------------------------------------------------------------------------
# Header handling — "match by name, not position" (architecture §9).
# --------------------------------------------------------------------------

# The 8 columns from architecture §1, normalized (whitespace-collapsed,
# upper-cased) for comparison. pdfplumber renders some of these as
# multi-line cells (e.g. "EFFECTIVE\nDATE"), hence the normalization.
EXPECTED_HEADERS: List[str] = [
    "SR NO",
    "ITEM NAME",
    "ITEM CODE",
    "EFFECTIVE DATE",
    "DECLARED PRICE",
    "LANDED COST",
    "KSBCL SELLING PRICE",
    "MRP",
]

_HEADER_TEXT_TO_FIELD: Dict[str, str] = {
    "SR NO": "sr_no",
    "ITEM NAME": "item_name",
    "ITEM CODE": "item_code",
    "EFFECTIVE DATE": "effective_date",
    "DECLARED PRICE": "declared_price",
    "LANDED COST": "landed_cost",
    "KSBCL SELLING PRICE": "ksbcl_selling_price",
    "MRP": "mrp",
}


def normalize_header_text(text: Optional[str]) -> str:
    """Collapse whitespace/newlines and case, for header comparison only."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip().upper()


def find_header_index_map(row: Optional[List[Optional[str]]]) -> Optional[Dict[str, int]]:
    """Return {logical_field: column_index} if every expected header is
    present in ``row`` (in any position), else None.

    Binding columns by *name* rather than a fixed position is what makes
    this resilient to KSBCL reordering columns in a future release
    (architecture §9's highest-ranked schema-drift risk).
    """
    if not row:
        return None
    normalized = [normalize_header_text(cell) for cell in row]
    index_map: Dict[str, int] = {}
    for expected in EXPECTED_HEADERS:
        if expected not in normalized:
            return None
        index_map[_HEADER_TEXT_TO_FIELD[expected]] = normalized.index(expected)
    return index_map


# --------------------------------------------------------------------------
# Row classification — header / supplier / filler / product (architecture §1).
# --------------------------------------------------------------------------

# "Supplier : <Full Legal Name> (<4-digit code>)" — architecture §1.
# Not anchored at the end: a full 750-page run surfaced real supplier rows
# with trailing location text after the code, e.g.
# "Supplier : Vinspri Distributors Pvt Ltd (0386)-Mumbai" and
# "Supplier : Aloka Breweries Pvt Ltd (0956) New Delhi" — the architecture's
# own example ("Supplier : B9 Beverages Pvt Ltd Sub-Lessee of Regent Beers
# and Wines Ltd (0260)") didn't show this, but §1's stated behaviour ("every
# row after one, until the next, belongs to that supplier") is unambiguous
# about what a supplier row *is*; requiring nothing after the code was an
# unstated over-restriction, not something the architecture specified.
_SUPPLIER_PATTERN = re.compile(r"^\s*Supplier\s*:\s*(.+?)\s*\((\d{4})\)", re.IGNORECASE)


def parse_supplier_header(item_name_cell: Optional[str]) -> Optional[SupplierContext]:
    """Parse a supplier section-header row's item-name cell, if it is one."""
    if not item_name_cell:
        return None
    match = _SUPPLIER_PATTERN.match(item_name_cell)
    if not match:
        return None
    name, code = match.groups()
    return SupplierContext(name=name.strip(), code=code)


def get_cell(
    row: List[Optional[str]], header_index_map: Dict[str, int], field: str
) -> Optional[str]:
    """Safely read a named column out of an already-classified row.

    The single place that does "look up this logical field's column index,
    then bounds-check against the row" — previously reimplemented in three
    different spots (row classification here, and again as a closure in
    validate.py), which is exactly the kind of duplication a staff-engineer
    review calls out.
    """
    index = header_index_map[field]
    return row[index] if index < len(row) else None


def _is_blank_cell(value: Optional[str]) -> bool:
    return value is None or value.strip() in ("", "-")


def is_filler_row(row: List[Optional[str]], header_index_map: Dict[str, int]) -> bool:
    """Filler/marker rows (architecture §1): e.g.
    ``1 | - | - | - | (values in Rs.)`` — both item name and item code
    are blank/"-".
    """
    item_name = get_cell(row, header_index_map, "item_name")
    item_code = get_cell(row, header_index_map, "item_code")
    return _is_blank_cell(item_name) and _is_blank_cell(item_code)


def classify_row(
    row: List[Optional[str]], header_index_map: Dict[str, int]
) -> Tuple[RowKind, Optional[SupplierContext]]:
    """Classify one already-extracted table row.

    ``header_index_map`` must come from this page's own header row
    (architecture §1: the header repeats on every page).
    """
    if find_header_index_map(row) is not None:
        return RowKind.HEADER, None

    supplier = parse_supplier_header(get_cell(row, header_index_map, "item_name"))
    if supplier is not None:
        return RowKind.SUPPLIER, supplier

    if is_filler_row(row, header_index_map):
        return RowKind.FILLER, None

    return RowKind.PRODUCT, None


# --------------------------------------------------------------------------
# Numeric cleanup — defeats the whitespace-tokenization artifact (§1, §5.4).
# --------------------------------------------------------------------------

_CLEAN_NUMBER_PATTERN = re.compile(r"^\d+\.\d{2}$")

# Error codes returned by clean_numeric_cell / parse_effective_date below.
# A small, closed, stable vocabulary — deliberately NOT free-form strings —
# so a caller (validate.py, and eventually Stage 2+) can build a clean,
# machine-parseable rejection reason without string-splitting an ad-hoc
# colon-joined message. See RejectedRow.reason_code/reason_detail.
ERROR_MISSING = "missing"
ERROR_UNPARSEABLE = "unparseable"
ERROR_INVALID_CALENDAR_DATE = "invalid_calendar_date"


def clean_numeric_cell(raw: Optional[str]) -> Tuple[Optional[Decimal], Optional[str], Optional[str]]:
    """Parse a price cell into a Decimal, defeating both known distortions:
    the PDF's internal-whitespace tokenization artifact ("1 40.00") and
    Indian comma-grouping ("6,199.00", "1,20,166.05").

    Returns (value, error_code, error_detail). On success, both error
    fields are None. On failure, value is None, error_code is one of the
    ERROR_* constants above, and error_detail carries the offending raw
    text (None when there was no raw text to show, i.e. a missing cell).
    """
    if raw is None:
        return None, ERROR_MISSING, None
    # Strip ALL whitespace, not just leading/trailing (architecture §1, §5.4)
    cleaned = re.sub(r"\s+", "", raw)
    cleaned = cleaned.replace(",", "")
    if not _CLEAN_NUMBER_PATTERN.match(cleaned):
        return None, ERROR_UNPARSEABLE, raw
    try:
        return Decimal(cleaned), None, None
    except InvalidOperation:
        return None, ERROR_UNPARSEABLE, raw


# --------------------------------------------------------------------------
# Date parsing — DD-Mon-YY, explicit 20xx pivot (architecture §5.4).
# --------------------------------------------------------------------------

_MONTH_ABBREVIATIONS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

_DATE_PATTERN = re.compile(r"^(\d{1,2})-([A-Za-z]{3})-(\d{2})$")


def parse_effective_date(raw: Optional[str]) -> Tuple[Optional[date], Optional[str], Optional[str]]:
    """Parse "DD-Mon-YY" (e.g. "13-May-26") into a date.

    Two-digit year is always resolved as 20xx per architecture §5.4:
    "an explicit, documented two-digit-year pivot rule (00-99 -> 20xx),
    since no row predates 2000" — not a locale/library default.

    Returns (value, error_code, error_detail), same convention as
    clean_numeric_cell above.
    """
    if raw is None:
        return None, ERROR_MISSING, None
    match = _DATE_PATTERN.match(raw.strip())
    if not match:
        return None, ERROR_UNPARSEABLE, raw
    day_str, month_str, year_str = match.groups()
    month = _MONTH_ABBREVIATIONS.get(month_str.lower())
    if month is None:
        return None, ERROR_UNPARSEABLE, raw
    year = 2000 + int(year_str)
    try:
        return date(year, month, int(day_str)), None, None
    except ValueError:
        return None, ERROR_INVALID_CALENDAR_DATE, raw
