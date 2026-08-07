"""Data types shared across Stage 1 (extraction).

Field names and the set of columns on ``ProductRow`` mirror §4.1
("Stage 1 output — structured_rows") of
docs/engineering/KSBCL-Beer-Pricing-Pipeline-Architecture.md exactly.
Nothing here anticipates later stages (no beer-classification, no
normalization, no canonical-identity fields).
"""

from __future__ import annotations

import enum
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional


class RowKind(enum.Enum):
    """Which of the four row shapes described in §1 a raw table row is."""

    HEADER = "header"
    SUPPLIER = "supplier"
    FILLER = "filler"
    PRODUCT = "product"


@dataclass(frozen=True)
class SupplierContext:
    """The active supplier section, per §1: carries across page breaks."""

    name: str
    code: str


@dataclass(frozen=True)
class ProductRow:
    """One accepted row of ``structured_rows.csv`` (architecture §4.1).

    Note for downstream consumers (Stage 2+): ``item_code`` must always be
    read back as a string, never auto-inferred as a numeric column (e.g.
    plain ``pandas.read_csv`` without ``dtype={"item_code": str}``) — the
    architecture requires Item Code preserved exactly, and a numeric-typed
    read would silently drop any leading zero. No leading-zero item code
    exists in the real file this pipeline has been run against so far, but
    nothing in the source guarantees that stays true for every future
    month, so this is a standing contract, not a today-only observation.
    """

    item_code: str
    item_name_raw: str
    supplier_name: str
    supplier_code: str
    effective_date_raw: str
    effective_date: date
    declared_price_raw: str
    declared_price: Decimal
    landed_cost_raw: str
    landed_cost: Decimal
    ksbcl_selling_price_raw: str
    ksbcl_selling_price: Decimal
    mrp_raw: str
    mrp: Decimal
    source_page: int
    run_month: str

    def to_csv_row(self) -> dict:
        d = asdict(self)
        d["effective_date"] = self.effective_date.isoformat()
        for money_field in (
            "declared_price",
            "landed_cost",
            "ksbcl_selling_price",
            "mrp",
        ):
            d[money_field] = str(d[money_field])
        return d


# Column order for structured_rows.csv, matching §4.1's listed field order.
PRODUCT_ROW_FIELDS = [
    "item_code",
    "item_name_raw",
    "supplier_name",
    "supplier_code",
    "effective_date_raw",
    "effective_date",
    "declared_price_raw",
    "declared_price",
    "landed_cost_raw",
    "landed_cost",
    "ksbcl_selling_price_raw",
    "ksbcl_selling_price",
    "mrp_raw",
    "mrp",
    "source_page",
    "run_month",
]


@dataclass(frozen=True)
class RejectedRow:
    """A product-row candidate that failed validation (architecture §8.1).

    §8.1: "written to rejected_rows.csv with its raw cells, page number,
    and the specific rule it failed" — no exact column schema is given
    beyond that. ``reason_code`` is drawn from a small, closed vocabulary
    (see the reject() call sites in validate.py) rather than an ad-hoc
    colon-joined string, specifically so this file is safely machine-
    parseable once Stage 2+ starts depending on it — grouping/counting by
    rejection cause should never require string-splitting a free-text
    message.
    """

    run_month: str
    source_page: int
    raw_row: List[Optional[str]]
    reason_code: str
    reason_detail: str

    def to_csv_row(self) -> dict:
        return {
            "run_month": self.run_month,
            "source_page": self.source_page,
            # JSON, not repr(): valid, portable, parseable by any tool —
            # not just Python — and unambiguous about quoting/None-vs-null.
            "raw_row": json.dumps(self.raw_row),
            "reason_code": self.reason_code,
            "reason_detail": self.reason_detail,
        }


REJECTED_ROW_FIELDS = ["run_month", "source_page", "raw_row", "reason_code", "reason_detail"]


@dataclass
class RunSummary:
    """Aggregate counts for one Stage 1 run.

    Not schema'd exactly by the architecture (only named as an output
    file in §3); content is the "row-type classification counts" and
    aggregate figures §9's Structural checks ask for, plus the
    ``*_used`` threshold fields — recorded so that a run investigated
    months later is self-explaining ("was this run using a 2% or 5%
    reject threshold?") without needing to know what the CLI defaults
    happened to be on the day it ran.
    """

    run_month: str
    source_pdf_reference: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "running"
    abort_reason: Optional[str] = None
    total_pages: int = 0
    header_rows_seen: int = 0
    supplier_header_rows_seen: int = 0
    filler_rows_seen: int = 0
    product_rows_seen: int = 0
    product_rows_accepted: int = 0
    product_rows_rejected: int = 0
    rejected_rows_by_reason: Dict[str, int] = field(default_factory=dict)
    distinct_supplier_sections_seen: int = 0
    rejected_row_abort_pct_used: Optional[float] = None
    mrp_min_used: Optional[str] = None
    mrp_max_used: Optional[str] = None
    row_count_min_used: Optional[int] = None
    row_count_max_used: Optional[int] = None

    def to_json_dict(self) -> dict:
        return asdict(self)
