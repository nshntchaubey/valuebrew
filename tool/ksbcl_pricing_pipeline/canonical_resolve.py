"""Stage 4 orchestration (architecture §2, §6, §7, §8).

Operates on already-loaded, plain in-memory data — no file I/O of its
own, mirroring Stage 2/3's core-logic/CLI-shell split.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from .canonical_key import MatchingKey, matching_key
from .canonical_models import CanonicalMapRow, ReviewRow, Stage4RunSummary
from .models import ProductRow
from .normalize_models import NormalizedRow


class Stage4ValidationError(Exception):
    """A structural failure that aborts the run (§10): zero rows in
    ``normalized_rows.csv``, or a join-integrity mismatch against
    ``structured_rows.csv``. Mirrors Stage 2/3's own ValidationError."""

    partial_summary: Optional[Stage4RunSummary] = None


@dataclass(frozen=True)
class Stage4Result:
    canonical_map: Dict[str, CanonicalMapRow]
    review_rows: List[ReviewRow]
    summary: Stage4RunSummary


# (item_code, canonical_product_id, supplier_code) — one entry per
# already-mapped, currently-visible item_code sharing a given key.
_KeyCandidate = Tuple[str, str, str]


def _next_canonical_id(prior_map: Dict[str, CanonicalMapRow]) -> "_CanonicalIdAllocator":
    max_seen = 0
    for row in prior_map.values():
        cid = row.canonical_product_id
        if cid.startswith("CP") and cid[2:].isdigit():
            max_seen = max(max_seen, int(cid[2:]))
    return _CanonicalIdAllocator(max_seen)


class _CanonicalIdAllocator:
    """Sequential, deterministic ``canonical_product_id`` generation
    (§3.1: "opaque, permanent... generation format is an implementation-
    time choice... the only architecture-level requirement is that it be
    stable and never collide"). Sequential IDs seeded from the highest
    existing numeric suffix satisfy both, given this run's fixed,
    deterministic processing order (§8) — never random (a UUID would
    break §8's rerun-determinism guarantee)."""

    def __init__(self, start_at: int):
        self._counter = start_at

    def next(self) -> str:
        self._counter += 1
        return f"CP{self._counter:07d}"


def run_stage4_resolution(
    product_rows: List[ProductRow],
    normalized_rows: List[NormalizedRow],
    prior_map: Dict[str, CanonicalMapRow],
    run_month: str,
    started_at: str,
) -> Stage4Result:
    """Resolves canonical identity for every item_code in this run's
    ``normalized_rows.csv`` (§2.1's row set), and separately maintains
    ``item_status`` for every already-mapped item_code outside that row
    set (§6, step 1's note).

    Raises ``Stage4ValidationError`` for the §10 structural failures:
    zero rows in ``normalized_rows.csv``, or an item_code present there
    but absent from ``structured_rows.csv`` — structurally should be
    impossible given both are frozen outputs of prior stages for the
    same run_month, checked anyway (the same defensive posture Stage 3
    §2.4 applies to its own equivalent check).
    """
    if not normalized_rows:
        error = Stage4ValidationError(
            "normalized_rows.csv has zero rows — a real month always has hundreds; this means "
            "an upstream failure, not a real data condition (§10)"
        )
        error.partial_summary = Stage4RunSummary(run_month=run_month, started_at=started_at)
        raise error

    structured_by_code: Dict[str, ProductRow] = {row.item_code: row for row in product_rows}
    normalized_by_code: Dict[str, NormalizedRow] = {row.item_code: row for row in normalized_rows}

    missing_in_structured = normalized_by_code.keys() - structured_by_code.keys()
    if missing_in_structured:
        error = Stage4ValidationError(
            f"{len(missing_in_structured)} item_code(s) in normalized_rows.csv are absent from "
            f"structured_rows.csv — a join-integrity failure (§10): {sorted(missing_in_structured)[:10]}"
        )
        error.partial_summary = Stage4RunSummary(run_month=run_month, started_at=started_at)
        raise error

    # Rerun-determinism (§8) requires comparing against the map state as
    # of *before* this run_month was ever processed — not whatever is
    # currently on disk, which may already include this run_month's own
    # effects from an earlier attempt (a deliberate rerun, or a retry
    # after a crash). An entry's own first_seen_run_month tells us
    # exactly which of those it is: anything first seen in this same
    # run_month was created by this run_month's own processing, so it is
    # excluded here and recomputed fresh below — reproducing the same
    # canonical_product_id (via the same deterministic allocator order)
    # and the same canonical_resolution_review.csv rows, rather than
    # silently treating it as "already mapped" and losing the review
    # trail a first attempt already recorded.
    true_prior_map: Dict[str, CanonicalMapRow] = {
        item_code: row for item_code, row in prior_map.items() if row.first_seen_run_month != run_month
    }

    working_map: Dict[str, CanonicalMapRow] = dict(true_prior_map)
    review_rows: List[ReviewRow] = []
    id_allocator = _next_canonical_id(true_prior_map)

    new_canonical_count = 0
    attached_cross_supplier = 0
    attached_same_supplier = 0
    review_by_reason: Dict[str, int] = defaultdict(int)
    already_mapped_updated = 0

    # key -> already-mapped candidates sharing that key, visible this run
    # (either from the prior map, or attached/created earlier in this
    # same run — §6's bootstrap note). Seeded only from item_codes this
    # run can actually observe a key for (§2.1's row set).
    key_index: Dict[MatchingKey, List[_KeyCandidate]] = defaultdict(list)
    for product_row in product_rows:
        item_code = product_row.item_code
        if item_code not in normalized_by_code or item_code not in true_prior_map:
            continue
        key = matching_key(normalized_by_code[item_code])
        if key is None:
            continue
        entry = true_prior_map[item_code]
        key_index[key].append((item_code, entry.canonical_product_id, entry.supplier_code))

    # Resolution, per item_code, in structured_rows.csv's original row
    # order (§8: load-bearing for determinism), restricted to this run's
    # normalized_rows.csv row set (§2.1).
    for product_row in product_rows:
        item_code = product_row.item_code
        if item_code not in normalized_by_code:
            continue
        normalized_row = normalized_by_code[item_code]

        if item_code in working_map:
            # Step 1: already mapped -> item_status/last_seen only.
            entry = working_map[item_code]
            working_map[item_code] = replace(entry, item_status="LIVE", last_seen_run_month=run_month)
            already_mapped_updated += 1
            continue

        key = matching_key(normalized_row)
        candidates = key_index.get(key, []) if key is not None else []

        different_supplier_cids = {
            cid for (_code, cid, supplier) in candidates if supplier != product_row.supplier_code
        }

        if key is None or not candidates:
            new_id = id_allocator.next()
            new_canonical_count += 1
            working_map[item_code] = CanonicalMapRow(
                ksbcl_item_code=item_code,
                canonical_product_id=new_id,
                supplier_name=product_row.supplier_name,
                supplier_code=product_row.supplier_code,
                match_confidence="unreviewed",
                matched_rule="new_canonical",
                item_status="LIVE",
                first_seen_run_month=run_month,
                last_seen_run_month=run_month,
            )

        elif different_supplier_cids:
            if len(different_supplier_cids) == 1:
                # 2a, single candidate: attach unconditionally.
                target_cid = next(iter(different_supplier_cids))
                attached_cross_supplier += 1
                working_map[item_code] = CanonicalMapRow(
                    ksbcl_item_code=item_code,
                    canonical_product_id=target_cid,
                    supplier_name=product_row.supplier_name,
                    supplier_code=product_row.supplier_code,
                    match_confidence="deterministic_high",
                    matched_rule="exact_key_match",
                    item_status="LIVE",
                    first_seen_run_month=run_month,
                    last_seen_run_month=run_month,
                )
            else:
                # 2a, multi-candidate: defer to review (Identity Decision 2).
                new_id = id_allocator.next()
                new_canonical_count += 1
                working_map[item_code] = CanonicalMapRow(
                    ksbcl_item_code=item_code,
                    canonical_product_id=new_id,
                    supplier_name=product_row.supplier_name,
                    supplier_code=product_row.supplier_code,
                    match_confidence="unreviewed",
                    matched_rule="new_canonical",
                    item_status="LIVE",
                    first_seen_run_month=run_month,
                    last_seen_run_month=run_month,
                )
                representative_by_cid: Dict[str, str] = {}
                for code, cid, _supplier in candidates:
                    if cid in different_supplier_cids and cid not in representative_by_cid:
                        representative_by_cid[cid] = code
                for cid in sorted(representative_by_cid):
                    review_rows.append(
                        ReviewRow(
                            run_month=run_month,
                            item_code=item_code,
                            canonical_product_id=new_id,
                            reason="ambiguous_key_multiple_candidates",
                            matched_item_code=representative_by_cid[cid],
                        )
                    )
                    review_by_reason["ambiguous_key_multiple_candidates"] += 1

        else:
            # 2b: only same-supplier matches exist — master's original
            # price/effective_date gate, unchanged. "Price" is `mrp`, not
            # `declared_price`: architecture §6's own worked example (the
            # Budweiser Magnum pair, item_codes 2170900611/2171700211)
            # cites ₹155.00/₹140.00, which are those item_codes' real
            # `mrp` values (₹1050.18/₹1051.00 are their `declared_price`,
            # not the cited figures) — `mrp` is also the one figure
            # master treats as directly comparable across listings without
            # a known case size (§1, §5.5, §4.6).
            same_supplier = [
                (code, cid) for (code, cid, supplier) in candidates if supplier == product_row.supplier_code
            ]
            matched_target: Optional[Tuple[str, str]] = None
            for code, cid in same_supplier:
                other = structured_by_code.get(code)
                if (
                    other is not None
                    and other.mrp == product_row.mrp
                    and other.effective_date == product_row.effective_date
                ):
                    matched_target = (code, cid)
                    break

            if matched_target is not None:
                _matched_code, target_cid = matched_target
                attached_same_supplier += 1
                working_map[item_code] = CanonicalMapRow(
                    ksbcl_item_code=item_code,
                    canonical_product_id=target_cid,
                    supplier_name=product_row.supplier_name,
                    supplier_code=product_row.supplier_code,
                    match_confidence="deterministic_high",
                    matched_rule="exact_key_match",
                    item_status="LIVE",
                    first_seen_run_month=run_month,
                    last_seen_run_month=run_month,
                )
            else:
                new_id = id_allocator.next()
                new_canonical_count += 1
                working_map[item_code] = CanonicalMapRow(
                    ksbcl_item_code=item_code,
                    canonical_product_id=new_id,
                    supplier_name=product_row.supplier_name,
                    supplier_code=product_row.supplier_code,
                    match_confidence="unreviewed",
                    matched_rule="new_canonical",
                    item_status="LIVE",
                    first_seen_run_month=run_month,
                    last_seen_run_month=run_month,
                )
                review_rows.append(
                    ReviewRow(
                        run_month=run_month,
                        item_code=item_code,
                        canonical_product_id=new_id,
                        reason="possible_supersession",
                        matched_item_code=same_supplier[0][0],
                    )
                )
                review_by_reason["possible_supersession"] += 1

        # Make this item_code visible to later item_codes processed
        # later in this same run (§6's bootstrap/within-run note).
        if key is not None:
            key_index[key].append(
                (item_code, working_map[item_code].canonical_product_id, product_row.supplier_code)
            )

    # item_status maintenance for already-mapped item_codes entirely
    # outside this run's normalized_rows.csv row set (§6, step 1's note):
    # checked against structured_rows.csv only; last_seen_run_month is
    # deliberately not touched here.
    for item_code, entry in list(working_map.items()):
        if item_code in normalized_by_code:
            continue
        new_status = "LIVE" if item_code in structured_by_code else "DELISTED"
        if entry.item_status != new_status:
            working_map[item_code] = replace(entry, item_status=new_status)

    live_count = sum(1 for row in working_map.values() if row.item_status == "LIVE")
    delisted_count = sum(1 for row in working_map.values() if row.item_status == "DELISTED")

    summary = Stage4RunSummary(
        run_month=run_month,
        started_at=started_at,
        total_item_codes_processed=len(normalized_by_code),
        new_canonical_products_created=new_canonical_count,
        attached_cross_supplier=attached_cross_supplier,
        attached_same_supplier=attached_same_supplier,
        review_rows_written=len(review_rows),
        review_rows_by_reason=dict(review_by_reason),
        already_mapped_updated=already_mapped_updated,
        item_status_live_count=live_count,
        item_status_delisted_count=delisted_count,
    )

    return Stage4Result(canonical_map=working_map, review_rows=review_rows, summary=summary)
