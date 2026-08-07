"""Stage 2 orchestration: the two-phase run (architecture §3.4).

Operates on already-loaded, plain in-memory data (a list of
``ProductRow``, a loaded config, a loaded known-terms snapshot, a loaded
review queue) — no file I/O of its own, mirroring the split between
Stage 1's ``extract.py`` (core logic, raises on structural failure) and
``run_pipeline.py`` (the I/O shell that reads input and writes output).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .classification_config import ClassificationConfig
from .classification_models import (
    ClassificationAuditRow,
    ClassificationRunSummary,
    KnownTermRow,
    NewEntityRow,
    ReviewQueueEntry,
)
from .classify import classify_row
from .ledger import EntityKey, build_new_entity_rows, compute_known_supplier_codes, entities_contributed_this_run, update_known_terms
from .models import ProductRow
from .review_queue import update_review_queue


class Stage2ValidationError(Exception):
    """A structural failure that aborts the run (§9's hard structural
    assert: High-tier count must be non-zero). ``partial_summary``, if
    set by the raiser, carries whatever counts had accumulated —
    mirroring Stage 1's ``PipelineValidationError``."""

    partial_summary: Optional[ClassificationRunSummary] = None


@dataclass(frozen=True)
class Stage2Result:
    audit_rows: List[ClassificationAuditRow]
    new_entity_rows: List[NewEntityRow]
    updated_known_terms: Dict[EntityKey, KnownTermRow]
    updated_review_queue: List[ReviewQueueEntry]
    summary: ClassificationRunSummary


def run_stage2_classification(
    product_rows: List[ProductRow],
    config: ClassificationConfig,
    known_terms: Dict[EntityKey, KnownTermRow],
    review_queue: List[ReviewQueueEntry],
    run_month: str,
    started_at: str,
) -> Stage2Result:
    """Runs the complete two-phase classification for one run.

    Raises Stage2ValidationError if the §9 hard structural assert
    fails (zero High-tier rows) — the caller is expected to treat that
    as an aborted run, matching §8.5's idempotent, all-or-nothing
    output guarantee: no artifact from a failed Stage 2 run is written
    except a "failed" summary.
    """
    is_bootstrap_run = len(known_terms) == 0
    known_supplier_codes = compute_known_supplier_codes(known_terms)

    # Phase 1 (classify): every row against the frozen, run-start
    # snapshot passed in — never anything mutated during this function.
    pairs: List[Tuple[ProductRow, ClassificationAuditRow]] = []
    for row in product_rows:
        result = classify_row(row, config, known_supplier_codes, run_month)
        if result is not None:
            pairs.append((row, result))
    audit_rows = [audit for _, audit in pairs]

    # Phase 2 (record): only after Phase 1 has completed for every row.
    new_entity_rows = build_new_entity_rows(known_terms, pairs)
    updated_known_terms = update_known_terms(known_terms, entities_contributed_this_run(pairs), run_month)
    updated_review_queue = update_review_queue(review_queue, pairs, run_month, config.config_version)

    summary = ClassificationRunSummary(
        run_month=run_month,
        started_at=started_at,
        classification_config_version=config.config_version,
        is_bootstrap_run=is_bootstrap_run,
    )
    summary.total_candidate_rows = len(audit_rows)
    for audit in audit_rows:
        summary.counts_by_tier[audit.confidence_tier] += 1
        summary.matched_signal_type_counts[audit.matched_signal_type] += 1
        if audit.matched_signal_type == "brand_name" and audit.confidence_tier == "low":
            if audit.exclusion_term_matched is not None:
                summary.exclusion_guard_fire_count += 1
            if not audit.supplier_known_beer_seller:
                summary.unfamiliar_supplier_demotion_count += 1
        if audit.matched_signal_type == "supplier_corroboration_only":
            summary.none_to_low_escalation_count += 1
        if audit.is_duty_free:
            summary.is_duty_free_count += 1
    summary.is_duty_free_ratio = (
        summary.is_duty_free_count / summary.total_candidate_rows if summary.total_candidate_rows else 0.0
    )

    if summary.counts_by_tier["high"] == 0:
        error = Stage2ValidationError(
            "zero High-tier rows accepted — a real month always contains hundreds of plain "
            "'X Beer' rows; this means the config failed to load correctly or the style-keyword "
            "allowlist is empty, a Stage 2 bug, not a real data condition (§9 hard structural assert)"
        )
        error.partial_summary = summary
        raise error

    return Stage2Result(
        audit_rows=audit_rows,
        new_entity_rows=new_entity_rows,
        updated_known_terms=updated_known_terms,
        updated_review_queue=updated_review_queue,
        summary=summary,
    )
