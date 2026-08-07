"""Data types for Stage 4 (Canonical Identity Resolution) outputs.

``CanonicalMapRow`` -> §3.1 (``item_code_canonical_map.csv``),
``ReviewRow`` -> §3.2 (``canonical_resolution_review.csv``),
``Stage4RunSummary`` -> this run's aggregate counts. Mirrors Stage 1/2/3's
dataclass + `to_csv_row`/`to_json_dict` conventions exactly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class CanonicalMapRow:
    ksbcl_item_code: str
    canonical_product_id: str
    supplier_name: str
    supplier_code: str
    match_confidence: str  # "deterministic_high" | "manual_confirmed" | "unreviewed"
    matched_rule: str  # "exact_key_match" | "manual_review" | "new_canonical"
    item_status: str  # "LIVE" | "DELISTED"
    first_seen_run_month: str
    last_seen_run_month: str

    def to_csv_row(self) -> dict:
        return asdict(self)


CANONICAL_MAP_FIELDS = [
    "ksbcl_item_code",
    "canonical_product_id",
    "supplier_name",
    "supplier_code",
    "match_confidence",
    "matched_rule",
    "item_status",
    "first_seen_run_month",
    "last_seen_run_month",
]


@dataclass(frozen=True)
class ReviewRow:
    run_month: str
    item_code: str
    canonical_product_id: str
    reason: str  # "possible_supersession" | "ambiguous_key_multiple_candidates"
    matched_item_code: str

    def to_csv_row(self) -> dict:
        return asdict(self)


REVIEW_ROW_FIELDS = [
    "run_month",
    "item_code",
    "canonical_product_id",
    "reason",
    "matched_item_code",
]


@dataclass
class Stage4RunSummary:
    run_month: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "running"
    abort_reason: Optional[str] = None
    total_item_codes_processed: int = 0
    new_canonical_products_created: int = 0
    attached_cross_supplier: int = 0
    attached_same_supplier: int = 0
    review_rows_written: int = 0
    review_rows_by_reason: Dict[str, int] = field(default_factory=dict)
    already_mapped_updated: int = 0
    item_status_live_count: int = 0
    item_status_delisted_count: int = 0

    def to_json_dict(self) -> dict:
        return asdict(self)
