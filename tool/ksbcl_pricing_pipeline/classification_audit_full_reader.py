"""Reads Stage 2's already-persisted ``classification_audit.csv`` back in
full — Stage 5 needs every field (`is_duty_free`, `confidence_tier`,
`matched_signal_type`, `matched_term`), unlike Stage 3's own reader,
which only needs `item_code`/`included` (§2.2 of that stage).

A new, Stage-5-owned module, mirroring Stage 3's own
``classification_audit_reader.py`` pattern — no existing reader for this
fuller read exists, and Stage 2/3's own files are not modified to add
one. Not every row of ``structured_rows.csv`` has a corresponding row
here — Stage 2 only scores candidates that matched at least one signal
(Stage 5 architecture §2.1) — so callers must treat a missing item_code
as "not scored this run," never as an error.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Optional

from .classification_models import ClassificationAuditRow


def _bool(value: str) -> bool:
    return value == "true"


def _optional(value: str) -> Optional[str]:
    return value if value else None


def read_classification_audit(path: Path) -> Dict[str, ClassificationAuditRow]:
    rows: Dict[str, ClassificationAuditRow] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[row["item_code"]] = ClassificationAuditRow(
                run_month=row["run_month"],
                item_code=row["item_code"],
                confidence_tier=row["confidence_tier"],
                included=_bool(row["included"]),
                matched_signal_type=row["matched_signal_type"],
                matched_term=_optional(row["matched_term"]),
                exclusion_term_matched=_optional(row["exclusion_term_matched"]),
                supplier_known_beer_seller=_bool(row["supplier_known_beer_seller"]),
                is_duty_free=_bool(row["is_duty_free"]),
                classification_config_version=row["classification_config_version"],
            )
    return rows
