"""``pricing_data/beer_price_history.csv`` — Stage 5's permanent,
append-only ledger (architecture §2.2, §3.2).

Unlike ``item_code_canonical_map.csv`` (Stage 4) or ``beer_master.csv``
(this stage), this file has no per-key uniqueness — every write grows
it. ``load_price_history`` returns every row, in file order; the most
recent row per item_code is exactly the last occurrence of that
item_code in that order (Stage 5 architecture §5.3), since a pipeline
only ever runs forward in time.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

from .history_models import PriceHistoryRow


class PriceHistoryCorruptionError(Exception):
    """A duplicate ``history_id`` within the persisted ledger itself —
    ``history_id`` is a surrogate key that must be unique; a duplicate
    means the file was corrupted or hand-edited unsafely, mirroring
    Stage 4's identical posture toward a duplicate ``ksbcl_item_code``."""


def _optional_decimal(value: str) -> Optional[Decimal]:
    return Decimal(value) if value else None


def load_price_history(path: Path) -> List[PriceHistoryRow]:
    """Empty list if the file does not exist yet (bootstrap, §5.4) —
    never an error."""
    if not path.exists():
        return []
    rows: List[PriceHistoryRow] = []
    seen_ids = set()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["history_id"] in seen_ids:
                raise PriceHistoryCorruptionError(
                    f"duplicate history_id {row['history_id']!r} in {path} — a corrupted ledger; "
                    "this run cannot safely diff against it"
                )
            seen_ids.add(row["history_id"])
            rows.append(
                PriceHistoryRow(
                    history_id=row["history_id"],
                    ksbcl_item_code=row["ksbcl_item_code"],
                    event_type=row["event_type"],
                    effective_date=row["effective_date"],
                    effective_date_raw=row["effective_date_raw"],
                    declared_price=Decimal(row["declared_price"]),
                    landed_cost=Decimal(row["landed_cost"]),
                    ksbcl_selling_price=Decimal(row["ksbcl_selling_price"]),
                    mrp=Decimal(row["mrp"]),
                    previous_declared_price=_optional_decimal(row["previous_declared_price"]),
                    previous_landed_cost=_optional_decimal(row["previous_landed_cost"]),
                    previous_ksbcl_selling_price=_optional_decimal(row["previous_ksbcl_selling_price"]),
                    previous_mrp=_optional_decimal(row["previous_mrp"]),
                    previous_effective_date=row["previous_effective_date"] or None,
                    observed_run_month=row["observed_run_month"],
                    observed_at=row["observed_at"],
                    source_pdf_reference=row["source_pdf_reference"],
                )
            )
    return rows


def most_recent_by_item_code(rows: List[PriceHistoryRow]) -> Dict[str, PriceHistoryRow]:
    """The last (most recent) row per ``ksbcl_item_code``, in file order —
    Stage 5 architecture §5.3's stated basis for rerun-idempotency."""
    result: Dict[str, PriceHistoryRow] = {}
    for row in rows:
        result[row.ksbcl_item_code] = row
    return result


def next_history_id(rows: List[PriceHistoryRow]) -> "_HistoryIdAllocator":
    max_seen = 0
    for row in rows:
        if row.history_id.startswith("H") and row.history_id[1:].isdigit():
            max_seen = max(max_seen, int(row.history_id[1:]))
    return _HistoryIdAllocator(max_seen)


class _HistoryIdAllocator:
    """Sequential, deterministic ``history_id`` generation — mirrors
    Stage 4's ``canonical_product_id`` allocator exactly, for the same
    reason: a random surrogate key would break rerun-determinism."""

    def __init__(self, start_at: int):
        self._counter = start_at

    def next(self) -> str:
        self._counter += 1
        return f"H{self._counter:08d}"
