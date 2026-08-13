"""Aggregates `join.py`, `business_rules.py`, and
`cross_reference_validate.py`'s own outputs into one structured,
deterministic report — mirroring the real KSBCL pipeline's own
`RunSummary`/`run_summary.json` pattern (Catalog Builder Implementation
Design Part 6): counts and named reasons, never a bare pass/fail
boolean. Read-only — aggregates already-computed results, runs nothing
itself.

`rejected_beer_files` (a malformed `enrichment/beers/*.yaml` file that
never even became an `EnrichmentBeer`) is a required, keyword-only
parameter — deliberately, not optional — so this function can't be
called without it and silently omit those files from the report again.
This closes the completeness gap the Milestone 1-6 implementation audit
found: `beers_rejected` now counts them, and each one gets its own
`RejectedBeerFileEntry` in `rejected_beer_files`, carrying `filename`,
`stage`, and its rejection reason — the same three things every other
rejection in this report already carries.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from .business_rules import BusinessRulesResult
from .cross_reference_validate import CrossReferenceValidationResult
from .join import JoinResult
from .models import EnrichmentBeer, RejectedBeerFileEntry, RejectedEnrichmentFile

_BEER_FILE_REJECTION_STAGE = "enrichment_schema"


@dataclass(frozen=True)
class RejectionDetail:
    canonical_product_id: str
    beer_key: str
    stage: str
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class ValidationReport:
    skus_joined: int
    skus_unenriched: int
    skus_included: int
    skus_rejected: int
    missing_candidate_references: int
    orphan_sku_references: int
    beers_included: int
    beers_rejected: int
    rejection_reasons: Dict[str, int]
    included_canonical_product_ids: List[str]
    rejected_details: List[RejectionDetail] = field(default_factory=list)
    rejected_beer_files: List[RejectedBeerFileEntry] = field(default_factory=list)


def build_validation_report(
    beers: List[EnrichmentBeer],
    join_result: JoinResult,
    business_rules_result: BusinessRulesResult,
    cross_reference_result: CrossReferenceValidationResult,
    *,
    rejected_beer_files: List[RejectedEnrichmentFile],
) -> ValidationReport:
    """Every rejection this build produced, accounted for exactly once,
    at the exact stage it actually happened — `rejected_beer_files`
    (never even parsed into an `EnrichmentBeer`), `join.py`'s own
    `missing_candidates`/`orphan_skus` (never reached a real join at
    all), `business_rules.py`'s own `rejected` (joined, but excluded by
    a publication rule), and `cross_reference_validate.py`'s own
    `rejected` (passed business rules, but failed a structural check)."""
    rejected_beer_file_entries = sorted(
        (
            RejectedBeerFileEntry(
                filename=r.filename,
                stage=_BEER_FILE_REJECTION_STAGE,
                reason_code=r.reason_code,
                reason_detail=r.reason_detail,
            )
            for r in rejected_beer_files
        ),
        key=lambda entry: entry.filename,
    )

    rejected_details: List[RejectionDetail] = []

    for entry in join_result.missing_candidates:
        rejected_details.append(
            RejectionDetail(
                canonical_product_id=entry.canonical_product_id,
                beer_key=entry.beer_key,
                stage="join_missing_candidate",
                reason_code="missing_candidate",
                reason_detail="Beer references a canonical_product_id with no matching real row",
            )
        )

    for entry in join_result.orphan_skus:
        rejected_details.append(
            RejectionDetail(
                canonical_product_id=entry.canonical_product_id,
                beer_key=entry.beer_key,
                stage="join_orphan_sku",
                reason_code="orphan_sku",
                reason_detail="Beer references a real row the contamination gate rejected",
            )
        )

    for rejected in business_rules_result.rejected:
        rejected_details.append(
            RejectionDetail(
                canonical_product_id=rejected.joined.beer_master_row.canonical_product_id,
                beer_key=rejected.joined.enrichment_beer.beer_key,
                stage="business_rules",
                reason_code=rejected.reason_code,
                reason_detail=rejected.reason_detail,
            )
        )

    for rejected in cross_reference_result.rejected:
        rejected_details.append(
            RejectionDetail(
                canonical_product_id=rejected.admitted.joined.beer_master_row.canonical_product_id,
                beer_key=rejected.admitted.joined.enrichment_beer.beer_key,
                stage="cross_reference_validate",
                reason_code=rejected.reason_code,
                reason_detail=rejected.reason_detail,
            )
        )

    rejected_details.sort(key=lambda d: (d.canonical_product_id, d.stage))

    rejection_reasons = dict(
        sorted(
            Counter(
                [d.reason_code for d in rejected_details] + [e.reason_code for e in rejected_beer_file_entries]
            ).items()
        )
    )

    included_ids = sorted(
        v.admitted.joined.beer_master_row.canonical_product_id for v in cross_reference_result.valid
    )

    beer_keys_with_included_sku = {v.admitted.joined.enrichment_beer.beer_key for v in cross_reference_result.valid}
    all_beer_keys = {beer.beer_key for beer in beers}
    beers_included = len(beer_keys_with_included_sku)
    # A malformed Beer file never became an EnrichmentBeer at all, so it
    # has no beer_key to appear in all_beer_keys — counted separately
    # here, added on, rather than silently absent from this total.
    beers_rejected = len(all_beer_keys - beer_keys_with_included_sku) + len(rejected_beer_file_entries)

    return ValidationReport(
        skus_joined=len(join_result.joined),
        skus_unenriched=len(join_result.unenriched),
        skus_included=len(cross_reference_result.valid),
        skus_rejected=len(business_rules_result.rejected) + len(cross_reference_result.rejected),
        missing_candidate_references=len(join_result.missing_candidates),
        orphan_sku_references=len(join_result.orphan_skus),
        beers_included=beers_included,
        beers_rejected=beers_rejected,
        rejection_reasons=rejection_reasons,
        included_canonical_product_ids=included_ids,
        rejected_details=rejected_details,
        rejected_beer_files=rejected_beer_file_entries,
    )
