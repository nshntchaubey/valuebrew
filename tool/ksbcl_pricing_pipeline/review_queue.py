"""``pricing_data/classification_review_queue.csv`` — the persistent,
episode-based review queue (architecture §3.5, §10).

Mirrors ``ledger.py``'s "pure core, thin I/O shell" split. The
episode-independence rule (§10, and its §17 close-out) is the load-
bearing invariant here: a closed episode's row is carried forward
unchanged and is never read to compute a later, distinct episode's
fields.
"""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Tuple

from .classification_models import ClassificationAuditRow, ReviewQueueEntry
from .models import ProductRow


class ReviewQueueError(Exception):
    """Raised if the persisted queue violates its own construction
    invariant: at most one ``pending`` entry per item_code, ever
    (§10 rule 1)."""


def _pending_by_item_code(entries: List[ReviewQueueEntry]) -> Dict[str, ReviewQueueEntry]:
    pending: Dict[str, ReviewQueueEntry] = {}
    for entry in entries:
        if entry.review_status != "pending":
            continue
        if entry.item_code in pending:
            raise ReviewQueueError(
                f"classification_review_queue.csv violates its own invariant: more than one "
                f"pending entry exists for item_code {entry.item_code!r}"
            )
        pending[entry.item_code] = entry
    return pending


def _advance_temporal_fields(
    current_last_seen: str, current_times_seen: int, run_month: str
) -> Tuple[str, int]:
    """§3.4 cases 2/3/4, applied to an already-open episode's own
    (last_seen_run_month, times_seen) pair — case 1 never applies here,
    since the refresh branch only runs when the row already exists."""
    if run_month == current_last_seen:
        return current_last_seen, current_times_seen  # case 2: no-op
    if run_month > current_last_seen:
        return run_month, current_times_seen + 1  # case 3: newer-month run
    return current_last_seen, current_times_seen + 1  # case 4: older-month rerun


def update_review_queue(
    existing: List[ReviewQueueEntry],
    pairs: List[Tuple[ProductRow, ClassificationAuditRow]],
    run_month: str,
    config_version: str,
) -> List[ReviewQueueEntry]:
    """Applies §10's three rules for one run and returns the full new
    state to write back — historical closed episodes untouched, open
    episodes refreshed/closed/created as this run's audit dictates.
    """
    closed_entries: List[ReviewQueueEntry] = [e for e in existing if e.review_status != "pending"]
    pending = dict(_pending_by_item_code(existing))

    audit_by_item_code = {audit_row.item_code: audit_row for _, audit_row in pairs}
    product_by_item_code = {product_row.item_code: product_row for product_row, _ in pairs}

    # Rule 2: reconciliation — close any currently-pending entry whose
    # item_code is now high/medium in this run's audit.
    for item_code in list(pending.keys()):
        audit_row = audit_by_item_code.get(item_code)
        if audit_row is not None and audit_row.confidence_tier in ("high", "medium"):
            closed_entries.append(replace(pending.pop(item_code), review_status="auto_resolved_config_change"))

    # Rule 1: every item_code that is low-tier in this run's audit.
    for item_code, audit_row in audit_by_item_code.items():
        if audit_row.confidence_tier != "low":
            continue
        current = pending.get(item_code)
        if current is not None:
            # Refresh branch: content fields refreshed, item_name_raw and
            # first_flagged_run_month and classification_config_version
            # untouched (§10's field table: item_name_raw is "snapshot at
            # first flag"; classification_config_version is "the ruleset
            # in effect when first flagged").
            new_last_seen, new_times_seen = _advance_temporal_fields(
                current.last_seen_run_month, current.times_seen_unreviewed, run_month
            )
            pending[item_code] = replace(
                current,
                matched_signal_type=audit_row.matched_signal_type,
                matched_term=audit_row.matched_term,
                last_seen_run_month=new_last_seen,
                times_seen_unreviewed=new_times_seen,
            )
        else:
            # Fresh-row branch: unconditionally a new episode, full
            # reset. A prior closed row for this item_code (if any) is
            # never read.
            product_row = product_by_item_code[item_code]
            pending[item_code] = ReviewQueueEntry(
                item_code=item_code,
                item_name_raw=product_row.item_name_raw,
                confidence_tier="low",
                matched_signal_type=audit_row.matched_signal_type,
                matched_term=audit_row.matched_term,
                first_flagged_run_month=run_month,
                last_seen_run_month=run_month,
                times_seen_unreviewed=1,
                review_status="pending",
                reviewed_by=None,
                reviewed_at=None,
                decision_note=None,
                classification_config_version=config_version,
            )

    # Rule 3 (item_codes pending but absent from this run's audit
    # entirely) requires no action: they were never touched above, so
    # they remain in `pending` exactly as loaded.

    result = closed_entries + list(pending.values())
    result.sort(key=lambda e: (e.item_code, e.first_flagged_run_month))
    return result


# --------------------------------------------------------------------------
# Thin CSV I/O shell
# --------------------------------------------------------------------------


def load_review_queue(path: Path) -> List[ReviewQueueEntry]:
    if not path.exists():
        return []
    entries: List[ReviewQueueEntry] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            entries.append(
                ReviewQueueEntry(
                    item_code=row["item_code"],
                    item_name_raw=row["item_name_raw"],
                    confidence_tier=row["confidence_tier"],
                    matched_signal_type=row["matched_signal_type"],
                    matched_term=row["matched_term"] or None,
                    first_flagged_run_month=row["first_flagged_run_month"],
                    last_seen_run_month=row["last_seen_run_month"],
                    times_seen_unreviewed=int(row["times_seen_unreviewed"]),
                    review_status=row["review_status"],
                    reviewed_by=row["reviewed_by"] or None,
                    reviewed_at=row["reviewed_at"] or None,
                    decision_note=row["decision_note"] or None,
                    classification_config_version=row["classification_config_version"],
                )
            )
    # Validate the persisted invariant on load too, not just on update.
    _pending_by_item_code(entries)
    return entries
