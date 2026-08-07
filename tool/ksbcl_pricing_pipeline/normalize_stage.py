"""Stage 3 orchestration (architecture §2.2, §2.4, §7).

Operates on already-loaded, plain in-memory data — no file I/O of its
own, mirroring Stage 2's ``classify_stage.py`` split between core logic
(raises on structural failure) and the CLI I/O shell.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .models import ProductRow
from .normalize import normalize_row
from .normalize_models import NormalizedRow, NormalizeRunSummary


class Stage3ValidationError(Exception):
    """A structural failure that aborts the run (§2.4): zero included
    rows, or a join-integrity mismatch between the two input files.
    Mirrors Stage 2's ``Stage2ValidationError``."""

    partial_summary: Optional[NormalizeRunSummary] = None


@dataclass(frozen=True)
class Stage3Result:
    normalized_rows: List[NormalizedRow]
    summary: NormalizeRunSummary


def run_stage3_normalization(
    product_rows: List[ProductRow],
    included_item_codes: Set[str],
    run_month: str,
    started_at: str,
) -> Stage3Result:
    """Runs Stage 3 for every row Stage 2 marked included (§2.2).

    Raises Stage3ValidationError for the §2.4 structural failures: zero
    included rows, or an included item_code missing from
    structured_rows.csv (a join-integrity failure that should be
    structurally impossible given two frozen, unmodified upstream
    outputs, but is checked anyway — the same defensive posture Stage 1
    applies to its own structural invariants).
    """
    if not included_item_codes:
        error = Stage3ValidationError(
            "classification_audit.csv has zero included=true rows — a real month always has "
            "hundreds; this means an upstream failure, not a real data condition (§2.4)"
        )
        error.partial_summary = NormalizeRunSummary(run_month=run_month, started_at=started_at)
        raise error

    rows_by_item_code: Dict[str, ProductRow] = {row.item_code: row for row in product_rows}
    missing = included_item_codes - rows_by_item_code.keys()
    if missing:
        error = Stage3ValidationError(
            f"{len(missing)} item_code(s) marked included=true in classification_audit.csv are "
            f"absent from structured_rows.csv — a join-integrity failure (§2.4): {sorted(missing)[:10]}"
        )
        error.partial_summary = NormalizeRunSummary(run_month=run_month, started_at=started_at)
        raise error

    normalized_rows: List[NormalizedRow] = []
    malformed_count = 0

    # Preserve structured_rows.csv's own stable row order (§5: determinism).
    for row in product_rows:
        if row.item_code not in included_item_codes:
            continue
        normalized_row, malformed = normalize_row(
            run_month=run_month,
            item_code=row.item_code,
            item_name_raw=row.item_name_raw,
            supplier_code=row.supplier_code,
        )
        normalized_rows.append(normalized_row)
        if malformed:
            malformed_count += 1

    total = len(normalized_rows)
    pack_size_null_count = sum(1 for r in normalized_rows if r.pack_size_ml is None)
    container_unknown_count = sum(1 for r in normalized_rows if r.container_type == "unknown")

    summary = NormalizeRunSummary(
        run_month=run_month,
        started_at=started_at,
        normalization_rule_version=normalized_rows[0].normalization_rule_version if normalized_rows else None,
        total_normalized_rows=total,
        pack_size_ml_null_count=pack_size_null_count,
        pack_size_ml_null_rate=(pack_size_null_count / total) if total else 0.0,
        suffix_malformed_count=malformed_count,
        suffix_malformed_rate=(malformed_count / total) if total else 0.0,
        container_type_unknown_count=container_unknown_count,
        container_type_unknown_rate=(container_unknown_count / total) if total else 0.0,
    )

    return Stage3Result(normalized_rows=normalized_rows, summary=summary)
