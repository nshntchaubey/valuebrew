"""The founder's fieldwork queue — every Beer still blocked on
`missing_abv`/`missing_calories`, ranked by how many real SKUs a
physical label photo could unlock. Exists because remote manufacturer
research (Catalog Enrichment Playbook Part 4, steps 1-5) has now been
exhausted for the beers that remain: this module doesn't replace that
research, it picks up exactly where it stopped — the moment the only
credible next source is a physical can, bottle, or a legible photo of
one (Playbook Part 4 item 1 / 1a).

**Reuses the real pipeline, invents no new rule.** `join.py` ->
`business_rules.py` -> `cross_reference_validate.py`, run exactly once,
the same sequence `build_catalog.py` already runs — this module never
re-decides what counts as `missing_abv` or `missing_calories`; it reads
`validation_report.py`'s own per-SKU `rejected_details` and groups them
by `beer_key`. If that pipeline's rules ever change, this queue's counts
change with it automatically, not by editing this file.

**`grouped_sku_count` vs. `fixable_sku_count` — two different numbers,
shown separately, deliberately.** `grouped_sku_count` is simply
`len(beer.canonical_product_ids)` — every SKU a founder has already
identified as belonging to this beer. `fixable_sku_count` is narrower
and more honest: only the SKUs whose *sole* remaining rejection reason
is `missing_abv` or `missing_calories` — a SKU also blocked by
`unsupported_package_type` (the real, separate container-type gap) or
`product_unavailable` (delisted) would not become publishable from a
photo alone, so it is not counted here. Ranking uses
`fixable_sku_count`, since that is the number a photo can actually move.

**`publication_potential` is a simple, documented tier, not a claim of
precision.** High (>=10 fixable SKUs), Medium (3-9), Low (1-2) — picked
as round, legible thresholds over this repository's real current
distribution, not a formula derived from anything external. If the
distribution shifts a lot as more evidence lands, revisit the numbers,
not the concept.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .beer_master_reader import read_beer_master_csv
from .business_rules import apply_business_rules
from .contamination_filter import filter_contamination, load_default_exclusion_terms
from .cross_reference_validate import validate_cross_references
from .enrichment_reader import load_beers, load_styles
from .join import JoinError, join
from .models import EnrichmentBeer
from .validate_beer import compute_invalid_beer_keys
from .validation_report import ValidationReport, build_validation_report

_FIXABLE_REASON_CODES = {"missing_abv", "missing_calories"}

_HIGH_THRESHOLD = 10
_MEDIUM_THRESHOLD = 3


class PhotoQueueError(Exception):
    """A structural failure anywhere in the pipeline this module reuses
    — the caller treats this as an abort, matching every other module's
    own convention."""


@dataclass(frozen=True)
class PhotoQueueEntry:
    beer_key: str
    brewery: str
    grouped_sku_count: int
    fixable_sku_count: int
    missing_fields: List[str]
    publication_potential: str


def _publication_potential(fixable_sku_count: int) -> str:
    if fixable_sku_count >= _HIGH_THRESHOLD:
        return "High"
    if fixable_sku_count >= _MEDIUM_THRESHOLD:
        return "Medium"
    return "Low"


def build_photo_queue(beers: List[EnrichmentBeer], report: ValidationReport) -> List[PhotoQueueEntry]:
    """Pure function — no I/O. `beers` is `enrichment_reader.load_beers`'s
    own output; `report` is `validation_report.build_validation_report`'s
    own output over the same beers, run through the real pipeline by the
    caller (see `_load_photo_queue_inputs` below for the real wiring).
    Only beers with `abv is None` or `calories_per_100ml is None` and at
    least one real fixable SKU appear here — a beer already fully
    evidenced, or blocked only by something a photo can't fix, doesn't
    belong on a fieldwork queue.
    """
    fixable_counts: dict[str, int] = {}
    for detail in report.rejected_details:
        if detail.reason_code in _FIXABLE_REASON_CODES:
            fixable_counts[detail.beer_key] = fixable_counts.get(detail.beer_key, 0) + 1

    entries: List[PhotoQueueEntry] = []
    for beer in beers:
        missing_fields: List[str] = []
        if beer.abv is None:
            missing_fields.append("abv")
        if beer.calories_per_100ml is None:
            missing_fields.append("calories")
        if not missing_fields:
            continue

        fixable = fixable_counts.get(beer.beer_key, 0)
        if fixable == 0:
            # Every SKU is blocked by something a photo can't fix
            # (unsupported_package_type, product_unavailable, an
            # invalid Beer entity) — real work, but not fieldwork.
            continue

        entries.append(
            PhotoQueueEntry(
                beer_key=beer.beer_key,
                brewery=beer.brewery,
                grouped_sku_count=len(beer.canonical_product_ids),
                fixable_sku_count=fixable,
                missing_fields=missing_fields,
                publication_potential=_publication_potential(fixable),
            )
        )

    entries.sort(key=lambda e: (-e.fixable_sku_count, e.beer_key))
    return entries


def _load_photo_queue_inputs(repo_root: Path) -> tuple[List[EnrichmentBeer], ValidationReport]:
    enrichment_dir = repo_root / "enrichment"
    beer_master_path = repo_root / "pricing_data" / "beer_master.csv"

    accepted, _ = read_beer_master_csv(beer_master_path)
    exclusion_terms = load_default_exclusion_terms()
    admitted, contaminated_rows = filter_contamination(accepted, exclusion_terms)
    contaminated_ids = {r.canonical_product_id for r in contaminated_rows}

    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {s.style_key for s in styles}
    beers, rejected_beer_files = load_beers(enrichment_dir / "beers", style_keys)
    invalid_beer_keys = compute_invalid_beer_keys(enrichment_dir / "beers", enrichment_dir / "styles.yaml")

    try:
        join_result = join(admitted, contaminated_row_ids=contaminated_ids, beers=beers)
    except JoinError as exc:
        raise PhotoQueueError(f"join failed: {exc}") from exc

    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)
    report = build_validation_report(
        beers, join_result, business_result, cross_ref_result, rejected_beer_files=rejected_beer_files
    )
    return beers, report


def main() -> None:
    parser = argparse.ArgumentParser(description="The founder's fieldwork queue — beers needing a physical label photo.")
    parser.add_argument("--top", type=int, default=None, help="show only the top N entries")
    parser.add_argument("--brewery", type=str, default=None, help="filter to breweries whose name contains TEXT")
    parser.add_argument("--missing-abv", action="store_true", help="show only beers missing abv")
    parser.add_argument("--missing-calories", action="store_true", help="show only beers missing calories_per_100ml")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    try:
        beers, report = _load_photo_queue_inputs(repo_root)
    except PhotoQueueError as exc:
        raise SystemExit(f"photo_queue failed: {exc}") from exc

    entries = build_photo_queue(beers, report)

    if args.brewery:
        needle = args.brewery.lower()
        entries = [e for e in entries if needle in e.brewery.lower()]
    if args.missing_abv:
        entries = [e for e in entries if "abv" in e.missing_fields]
    if args.missing_calories:
        entries = [e for e in entries if "calories" in e.missing_fields]
    if args.top is not None:
        entries = entries[: args.top]

    total_fixable = sum(e.fixable_sku_count for e in entries)
    print(f"Photo queue — {len(entries)} beer(s), {total_fixable} SKU(s) fixable with a real label photo")
    print("=" * 78)
    for e in entries:
        fields = "+".join(e.missing_fields)
        print(
            f"  {e.beer_key:<40} {e.brewery:<22} skus={e.grouped_sku_count:<3} "
            f"fixable={e.fixable_sku_count:<3} missing={fields:<16} potential={e.publication_potential}"
        )


if __name__ == "__main__":
    main()
