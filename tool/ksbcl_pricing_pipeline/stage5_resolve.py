"""Stage 5 orchestration (architecture §2, §4, §5, §6, §8).

Operates on already-loaded, plain in-memory data — no file I/O of its
own, mirroring Stage 2-4's core-logic/CLI-shell split.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from .canonical_models import CanonicalMapRow
from .classification_models import ClassificationAuditRow
from .history_io import next_history_id, most_recent_by_item_code
from .history_models import MasterRow, PriceHistoryRow, Stage5RunSummary
from .models import ProductRow
from .normalize_models import NormalizedRow


class Stage5ValidationError(Exception):
    """A structural failure that aborts the run (§10): zero rows in
    `item_code_canonical_map.csv`, or a join-integrity mismatch against
    `structured_rows.csv`. Mirrors Stages 2-4's own ValidationError."""

    partial_summary: Optional[Stage5RunSummary] = None


@dataclass(frozen=True)
class Stage5Result:
    new_history_rows: List[PriceHistoryRow]
    master_retail: Dict[str, MasterRow]
    master_duty_free: Dict[str, MasterRow]
    summary: Stage5RunSummary


_PriceTuple = tuple  # (declared_price, landed_cost, ksbcl_selling_price, mrp, effective_date)


def _price_tuple(row: ProductRow) -> _PriceTuple:
    return (row.declared_price, row.landed_cost, row.ksbcl_selling_price, row.mrp, row.effective_date)


def _run_history_diff(
    product_rows: List[ProductRow],
    canonical_map: Dict[str, CanonicalMapRow],
    prior_history_rows: List[PriceHistoryRow],
    run_month: str,
    observed_at: str,
    source_pdf_reference: str,
) -> tuple:
    """§5: the item-code-level diff. Returns (new_rows, event_counts)."""
    prior_by_code = most_recent_by_item_code(prior_history_rows)
    is_bootstrap = len(prior_history_rows) == 0
    id_allocator = next_history_id(prior_history_rows)

    new_rows: List[PriceHistoryRow] = []
    event_counts: Dict[str, int] = defaultdict(int)

    for product_row in product_rows:
        item_code = product_row.item_code
        if item_code not in canonical_map:
            continue  # not yet resolved by Stage 4 — outside Stage 5's row set (§5.1)

        prior_row = prior_by_code.get(item_code)

        if prior_row is None:
            event_type = "INITIAL_BACKFILL" if is_bootstrap else "NEW_ITEM"
            new_rows.append(
                PriceHistoryRow(
                    history_id=id_allocator.next(),
                    ksbcl_item_code=item_code,
                    event_type=event_type,
                    effective_date=product_row.effective_date.isoformat(),
                    effective_date_raw=product_row.effective_date_raw,
                    declared_price=product_row.declared_price,
                    landed_cost=product_row.landed_cost,
                    ksbcl_selling_price=product_row.ksbcl_selling_price,
                    mrp=product_row.mrp,
                    previous_declared_price=None,
                    previous_landed_cost=None,
                    previous_ksbcl_selling_price=None,
                    previous_mrp=None,
                    previous_effective_date=None,
                    observed_run_month=run_month,
                    observed_at=observed_at,
                    source_pdf_reference=source_pdf_reference,
                )
            )
            event_counts[event_type] += 1
            continue

        prior_effective_date = date.fromisoformat(prior_row.effective_date)
        prior_tuple = (
            prior_row.declared_price,
            prior_row.landed_cost,
            prior_row.ksbcl_selling_price,
            prior_row.mrp,
            prior_effective_date,
        )
        current_tuple = _price_tuple(product_row)

        if current_tuple == prior_tuple:
            continue  # unchanged — no history row (§5.2, §5.3)

        if product_row.effective_date > prior_effective_date:
            event_type = "PRICE_CHANGE"
        else:
            # Same or earlier effective_date, but the tuple differs -> CORRECTION
            # in both sub-cases (§5.2/§7.2 of master).
            event_type = "CORRECTION"

        new_rows.append(
            PriceHistoryRow(
                history_id=id_allocator.next(),
                ksbcl_item_code=item_code,
                event_type=event_type,
                effective_date=product_row.effective_date.isoformat(),
                effective_date_raw=product_row.effective_date_raw,
                declared_price=product_row.declared_price,
                landed_cost=product_row.landed_cost,
                ksbcl_selling_price=product_row.ksbcl_selling_price,
                mrp=product_row.mrp,
                previous_declared_price=prior_row.declared_price,
                previous_landed_cost=prior_row.landed_cost,
                previous_ksbcl_selling_price=prior_row.ksbcl_selling_price,
                previous_mrp=prior_row.mrp,
                previous_effective_date=prior_row.effective_date,
                observed_run_month=run_month,
                observed_at=observed_at,
                source_pdf_reference=source_pdf_reference,
            )
        )
        event_counts[event_type] += 1

    return new_rows, dict(event_counts)


def _eligible_item_codes_for_channel(
    item_codes: List[str],
    channel_is_duty_free: bool,
    canonical_map: Dict[str, CanonicalMapRow],
    normalized_rows: Dict[str, NormalizedRow],
    classification_audit: Dict[str, ClassificationAuditRow],
) -> List[str]:
    """§4: LIVE, present in this run's normalized_rows.csv (the
    sufficient condition — implies a classification_audit.csv row
    exists too, §4's corrected eligibility rule), and matching this
    channel's is_duty_free value."""
    eligible = []
    for item_code in item_codes:
        if canonical_map[item_code].item_status != "LIVE":
            continue
        if item_code not in normalized_rows:
            continue
        audit_row = classification_audit.get(item_code)
        if audit_row is None:
            continue
        if audit_row.is_duty_free != channel_is_duty_free:
            continue
        eligible.append(item_code)
    return eligible


def _select_representative(eligible: List[str], structured_by_code: Dict[str, ProductRow]) -> str:
    """§4: newest effective_date wins; lowest ksbcl_item_code breaks a tie."""
    return max(eligible, key=lambda code: (structured_by_code[code].effective_date, -int(code)))


def _build_master_row(
    canonical_product_id: str,
    representative_item_code: str,
    structured_by_code: Dict[str, ProductRow],
    normalized_rows: Dict[str, NormalizedRow],
    classification_audit: Dict[str, ClassificationAuditRow],
    existing: Optional[MasterRow],
    run_month: str,
    source_pdf_reference: str,
) -> MasterRow:
    product_row = structured_by_code[representative_item_code]
    normalized_row = normalized_rows[representative_item_code]
    audit_row = classification_audit[representative_item_code]

    matched_on = (
        f"{audit_row.matched_signal_type}:{audit_row.matched_term}"
        if audit_row.matched_term
        else audit_row.matched_signal_type
    )

    return MasterRow(
        canonical_product_id=canonical_product_id,
        representative_item_code=representative_item_code,
        item_name_raw=product_row.item_name_raw,
        display_name=normalized_row.display_name,
        normalized_name_key=normalized_row.normalized_name_key,
        pack_size_ml=normalized_row.pack_size_ml,
        pack_count=normalized_row.pack_count,
        container_type=normalized_row.container_type,
        declared_price=product_row.declared_price,
        landed_cost=product_row.landed_cost,
        ksbcl_selling_price=product_row.ksbcl_selling_price,
        mrp=product_row.mrp,
        effective_date=product_row.effective_date.isoformat(),
        status="LIVE",
        delisted_run_month=None,
        classification_confidence=audit_row.confidence_tier,
        classification_matched_on=matched_on,
        gtin=None,
        gtin_confidence=None,
        source_pdf_reference=source_pdf_reference,
        first_seen_run_month=existing.first_seen_run_month if existing is not None else run_month,
        last_updated_run_month=run_month,
    )


def _run_master_diff(
    canonical_map: Dict[str, CanonicalMapRow],
    structured_by_code: Dict[str, ProductRow],
    normalized_rows: Dict[str, NormalizedRow],
    classification_audit: Dict[str, ClassificationAuditRow],
    prior_master_retail: Dict[str, MasterRow],
    prior_master_duty_free: Dict[str, MasterRow],
    run_month: str,
    source_pdf_reference: str,
) -> tuple:
    """§6: the canonical-level diff, per (canonical_product_id, channel).
    Returns (master_retail, master_duty_free, live_retail_count,
    delisted_retail_count, live_duty_free_count, delisted_duty_free_count,
    representative_ineligible_count)."""
    cid_to_item_codes: Dict[str, List[str]] = defaultdict(list)
    for item_code, row in canonical_map.items():
        cid_to_item_codes[row.canonical_product_id].append(item_code)

    working_retail = dict(prior_master_retail)
    working_duty_free = dict(prior_master_duty_free)

    live_retail = delisted_retail = live_df = delisted_df = 0
    ineligible_count = 0

    for cid, item_codes in cid_to_item_codes.items():
        for channel_is_df, target in ((False, working_retail), (True, working_duty_free)):
            eligible = _eligible_item_codes_for_channel(
                item_codes, channel_is_df, canonical_map, normalized_rows, classification_audit
            )
            existing = target.get(cid)

            if eligible:
                rep = _select_representative(eligible, structured_by_code)
                target[cid] = _build_master_row(
                    cid, rep, structured_by_code, normalized_rows, classification_audit,
                    existing, run_month, source_pdf_reference,
                )
                if channel_is_df:
                    live_df += 1
                else:
                    live_retail += 1
            elif existing is not None:
                # §4's ineligible-representative scenario is scoped to *this*
                # channel specifically — a LIVE item_code matching this
                # channel's is_duty_free that still didn't make `eligible`
                # (excluded only by the normalized_rows.csv check). Checking
                # "is anything at all LIVE" without the channel/is_duty_free
                # filter would also fire for an ordinary single-channel
                # delisting whenever the *other* channel happens to have a
                # live item_code — a real bug caught by adversarial review.
                any_live_for_this_channel = any(
                    canonical_map[code].item_status == "LIVE"
                    and classification_audit.get(code) is not None
                    and classification_audit[code].is_duty_free == channel_is_df
                    for code in item_codes
                )
                if any_live_for_this_channel:
                    ineligible_count += 1
                new_delisted_run_month = (
                    existing.delisted_run_month if existing.status == "DELISTED" else run_month
                )
                target[cid] = replace(
                    existing,
                    status="DELISTED",
                    delisted_run_month=new_delisted_run_month,
                    last_updated_run_month=run_month,
                )
                if channel_is_df:
                    delisted_df += 1
                else:
                    delisted_retail += 1
            # else: no eligible item_codes and no existing row -> nothing to do for this channel.

    return working_retail, working_duty_free, live_retail, delisted_retail, live_df, delisted_df, ineligible_count


def run_stage5(
    product_rows: List[ProductRow],
    canonical_map: Dict[str, CanonicalMapRow],
    classification_audit: Dict[str, ClassificationAuditRow],
    normalized_rows: Dict[str, NormalizedRow],
    prior_history_rows: List[PriceHistoryRow],
    prior_master_retail: Dict[str, MasterRow],
    prior_master_duty_free: Dict[str, MasterRow],
    run_month: str,
    started_at: str,
    observed_at: str,
    source_pdf_reference: str,
) -> Stage5Result:
    """Runs both Stage 5 diffs (§5, §6).

    Raises Stage5ValidationError for the §10 structural failures: zero
    rows in `item_code_canonical_map.csv`, or a `LIVE` item_code absent
    from this run's `structured_rows.csv` (should be structurally
    impossible given Stage 4's own `item_status` rule, checked anyway).
    """
    if not canonical_map:
        error = Stage5ValidationError(
            "item_code_canonical_map.csv has zero rows — Stage 5 cannot run against a pipeline "
            "that has never resolved a single item_code (§10)"
        )
        error.partial_summary = Stage5RunSummary(run_month=run_month, started_at=started_at)
        raise error

    structured_by_code: Dict[str, ProductRow] = {row.item_code: row for row in product_rows}

    live_but_missing = [
        code for code, row in canonical_map.items() if row.item_status == "LIVE" and code not in structured_by_code
    ]
    if live_but_missing:
        error = Stage5ValidationError(
            f"{len(live_but_missing)} item_code(s) marked LIVE in item_code_canonical_map.csv are "
            f"absent from structured_rows.csv — a join-integrity failure (§10): {sorted(live_but_missing)[:10]}"
        )
        error.partial_summary = Stage5RunSummary(run_month=run_month, started_at=started_at)
        raise error

    new_history_rows, event_counts = _run_history_diff(
        product_rows, canonical_map, prior_history_rows, run_month, observed_at, source_pdf_reference
    )

    (
        master_retail,
        master_duty_free,
        live_retail,
        delisted_retail,
        live_df,
        delisted_df,
        ineligible_count,
    ) = _run_master_diff(
        canonical_map,
        structured_by_code,
        normalized_rows,
        classification_audit,
        prior_master_retail,
        prior_master_duty_free,
        run_month,
        source_pdf_reference,
    )

    summary = Stage5RunSummary(
        run_month=run_month,
        started_at=started_at,
        history_rows_written=len(new_history_rows),
        history_event_counts=event_counts,
        master_retail_rows_live=live_retail,
        master_retail_rows_delisted=delisted_retail,
        master_duty_free_rows_live=live_df,
        master_duty_free_rows_delisted=delisted_df,
        representative_ineligible_channels=ineligible_count,
    )

    return Stage5Result(
        new_history_rows=new_history_rows,
        master_retail=master_retail,
        master_duty_free=master_duty_free,
        summary=summary,
    )
