"""Data types for Stage 3 (Normalization) outputs.

``NormalizedRow`` -> §3.1, ``NormalizeRunSummary`` -> §7's tracked
aggregate metrics. Mirrors Stage 1/2's dataclass + `to_csv_row`/
`to_json_dict` conventions exactly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NormalizedRow:
    run_month: str
    item_code: str
    display_name: str
    normalized_name_key: str
    pack_size_ml: Optional[Decimal]
    pack_count: Optional[int]
    container_type: str  # "bottle" | "can" | "pet_bottle" | "tetra_pack" | "unknown"
    normalization_rule_version: str

    def to_csv_row(self) -> dict:
        d = asdict(self)
        d["pack_size_ml"] = str(self.pack_size_ml) if self.pack_size_ml is not None else None
        return d


NORMALIZED_ROW_FIELDS = [
    "run_month",
    "item_code",
    "display_name",
    "normalized_name_key",
    "pack_size_ml",
    "pack_count",
    "container_type",
    "normalization_rule_version",
]


@dataclass
class NormalizeRunSummary:
    run_month: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "running"
    abort_reason: Optional[str] = None
    normalization_rule_version: Optional[str] = None
    total_normalized_rows: int = 0
    pack_size_ml_null_count: int = 0
    pack_size_ml_null_rate: float = 0.0
    suffix_malformed_count: int = 0
    suffix_malformed_rate: float = 0.0
    container_type_unknown_count: int = 0
    container_type_unknown_rate: float = 0.0

    def to_json_dict(self) -> dict:
        return asdict(self)
