"""Data types for Stage 2 (Beer Identification) outputs.

Field names and shapes mirror the architecture exactly:
``ClassificationAuditRow`` -> §3.1, ``NewEntityRow`` -> §3.2,
``ClassificationRunSummary`` -> §3.3, ``KnownTermRow`` -> §3.4,
``ReviewQueueEntry`` -> §3.5/§10. Boolean CSV columns are written as the
lowercase strings "true"/"false", matching the architecture's own
lowercase rendering of tier/status values throughout (`high`/`low`,
`pending`, etc.) rather than Python's default `True`/`False`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional


def _bool_csv(value: bool) -> str:
    return "true" if value else "false"


# --------------------------------------------------------------------------
# §3.1 classification_audit.csv
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassificationAuditRow:
    run_month: str
    item_code: str
    confidence_tier: str  # "high" | "medium" | "low"
    included: bool
    matched_signal_type: str  # "style_keyword" | "brand_name" | "supplier_corroboration_only"
    matched_term: Optional[str]
    exclusion_term_matched: Optional[str]
    supplier_known_beer_seller: bool
    is_duty_free: bool
    classification_config_version: str

    def to_csv_row(self) -> dict:
        d = asdict(self)
        d["included"] = _bool_csv(self.included)
        d["supplier_known_beer_seller"] = _bool_csv(self.supplier_known_beer_seller)
        d["is_duty_free"] = _bool_csv(self.is_duty_free)
        return d


CLASSIFICATION_AUDIT_FIELDS = [
    "run_month",
    "item_code",
    "confidence_tier",
    "included",
    "matched_signal_type",
    "matched_term",
    "exclusion_term_matched",
    "supplier_known_beer_seller",
    "is_duty_free",
    "classification_config_version",
]


# --------------------------------------------------------------------------
# §3.2 classification_new_entities.csv
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class NewEntityRow:
    entity_type: str  # "style_keyword" | "brand_name" | "supplier_code"
    value: str
    sample_item_code: str
    sample_item_name_raw: str

    def to_csv_row(self) -> dict:
        return asdict(self)


NEW_ENTITY_FIELDS = ["entity_type", "value", "sample_item_code", "sample_item_name_raw"]


# --------------------------------------------------------------------------
# §3.3 classification_run_summary.json
# --------------------------------------------------------------------------


@dataclass
class ClassificationRunSummary:
    run_month: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "running"
    abort_reason: Optional[str] = None
    classification_config_version: Optional[str] = None
    is_bootstrap_run: bool = False
    total_candidate_rows: int = 0
    counts_by_tier: Dict[str, int] = field(default_factory=lambda: {"high": 0, "medium": 0, "low": 0})
    matched_signal_type_counts: Dict[str, int] = field(
        default_factory=lambda: {"style_keyword": 0, "brand_name": 0, "supplier_corroboration_only": 0}
    )
    exclusion_guard_fire_count: int = 0
    unfamiliar_supplier_demotion_count: int = 0
    none_to_low_escalation_count: int = 0
    is_duty_free_count: int = 0
    is_duty_free_ratio: float = 0.0

    def to_json_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------
# §3.4 classification_known_terms.csv (persistent, cross-run)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class KnownTermRow:
    entity_type: str  # "style_keyword" | "brand_name" | "supplier_code"
    value: str
    first_seen_run_month: str
    last_seen_run_month: str
    times_seen: int

    def to_csv_row(self) -> dict:
        return asdict(self)


KNOWN_TERM_FIELDS = ["entity_type", "value", "first_seen_run_month", "last_seen_run_month", "times_seen"]


# --------------------------------------------------------------------------
# §3.5 / §10 classification_review_queue.csv (persistent, cross-run)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ReviewQueueEntry:
    item_code: str
    item_name_raw: str
    confidence_tier: str
    matched_signal_type: str
    matched_term: Optional[str]
    first_flagged_run_month: str
    last_seen_run_month: str
    times_seen_unreviewed: int
    review_status: str  # "pending" | "confirmed_beer" | "confirmed_not_beer" | "stale_ignored" | "auto_resolved_config_change"
    reviewed_by: Optional[str]
    reviewed_at: Optional[str]
    decision_note: Optional[str]
    classification_config_version: str

    def to_csv_row(self) -> dict:
        return asdict(self)


REVIEW_QUEUE_FIELDS = [
    "item_code",
    "item_name_raw",
    "confidence_tier",
    "matched_signal_type",
    "matched_term",
    "first_flagged_run_month",
    "last_seen_run_month",
    "times_seen_unreviewed",
    "review_status",
    "reviewed_by",
    "reviewed_at",
    "decision_note",
    "classification_config_version",
]
