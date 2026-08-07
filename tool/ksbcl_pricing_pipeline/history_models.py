"""Data types for Stage 5 (Master + History) outputs.

``PriceHistoryRow`` -> Stage 5 architecture §3.2 (`beer_price_history.csv`),
``MasterRow`` -> §3.1 (`beer_master.csv` / `beer_master_duty_free.csv`,
same schema, two files), ``Stage5RunSummary`` -> this run's aggregate
counts. Mirrors Stage 1-4's dataclass + `to_csv_row`/`to_json_dict`
conventions exactly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Dict, Optional


@dataclass(frozen=True)
class PriceHistoryRow:
    history_id: str
    ksbcl_item_code: str
    event_type: str  # "INITIAL_BACKFILL" | "NEW_ITEM" | "PRICE_CHANGE" | "CORRECTION"
    effective_date: str
    effective_date_raw: str
    declared_price: Decimal
    landed_cost: Decimal
    ksbcl_selling_price: Decimal
    mrp: Decimal
    previous_declared_price: Optional[Decimal]
    previous_landed_cost: Optional[Decimal]
    previous_ksbcl_selling_price: Optional[Decimal]
    previous_mrp: Optional[Decimal]
    previous_effective_date: Optional[str]
    observed_run_month: str
    observed_at: str
    source_pdf_reference: str

    def to_csv_row(self) -> dict:
        d = asdict(self)
        for money_field in (
            "declared_price",
            "landed_cost",
            "ksbcl_selling_price",
            "mrp",
            "previous_declared_price",
            "previous_landed_cost",
            "previous_ksbcl_selling_price",
            "previous_mrp",
        ):
            value = d[money_field]
            d[money_field] = str(value) if value is not None else None
        return d


PRICE_HISTORY_FIELDS = [
    "history_id",
    "ksbcl_item_code",
    "event_type",
    "effective_date",
    "effective_date_raw",
    "declared_price",
    "landed_cost",
    "ksbcl_selling_price",
    "mrp",
    "previous_declared_price",
    "previous_landed_cost",
    "previous_ksbcl_selling_price",
    "previous_mrp",
    "previous_effective_date",
    "observed_run_month",
    "observed_at",
    "source_pdf_reference",
]


@dataclass(frozen=True)
class MasterRow:
    canonical_product_id: str
    representative_item_code: str
    item_name_raw: str
    display_name: str
    normalized_name_key: str
    pack_size_ml: Optional[Decimal]
    pack_count: Optional[int]
    container_type: str
    declared_price: Decimal
    landed_cost: Decimal
    ksbcl_selling_price: Decimal
    mrp: Decimal
    effective_date: str
    status: str  # "LIVE" | "DELISTED"
    delisted_run_month: Optional[str]
    classification_confidence: str
    classification_matched_on: str
    gtin: Optional[str]
    gtin_confidence: Optional[str]
    source_pdf_reference: str
    first_seen_run_month: str
    last_updated_run_month: str

    def to_csv_row(self) -> dict:
        d = asdict(self)
        d["pack_size_ml"] = str(self.pack_size_ml) if self.pack_size_ml is not None else None
        for money_field in ("declared_price", "landed_cost", "ksbcl_selling_price", "mrp"):
            d[money_field] = str(d[money_field])
        return d


MASTER_ROW_FIELDS = [
    "canonical_product_id",
    "representative_item_code",
    "item_name_raw",
    "display_name",
    "normalized_name_key",
    "pack_size_ml",
    "pack_count",
    "container_type",
    "declared_price",
    "landed_cost",
    "ksbcl_selling_price",
    "mrp",
    "effective_date",
    "status",
    "delisted_run_month",
    "classification_confidence",
    "classification_matched_on",
    "gtin",
    "gtin_confidence",
    "source_pdf_reference",
    "first_seen_run_month",
    "last_updated_run_month",
]


@dataclass
class Stage5RunSummary:
    run_month: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "running"
    abort_reason: Optional[str] = None
    history_rows_written: int = 0
    history_event_counts: Dict[str, int] = field(default_factory=dict)
    master_retail_rows_live: int = 0
    master_retail_rows_delisted: int = 0
    master_duty_free_rows_live: int = 0
    master_duty_free_rows_delisted: int = 0
    representative_ineligible_channels: int = 0

    def to_json_dict(self) -> dict:
        return asdict(self)
