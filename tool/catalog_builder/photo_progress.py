"""The repository-wide evidence-progress dashboard — where every
enriched Beer currently sits, one bucket each, no beer counted twice.
**[RC7.3 note]:** this module and its siblings (`photo_queue.py`,
`photo_checklist.py`) were originally framed around manual-observation
fieldwork — the founder has since ruled physical fieldwork out
entirely for this project. The bucket logic below is unaffected and
remains accurate; only that original framing was stale. Companion to
`photo_queue.py` (which ranks the *work still to do*) and
`enrichment_queue.py` (which tracks *candidates not yet grouped into any
Beer at all*) — this module answers a different question: of the Beers
that already exist, how close is each one to actually publishing.

**Four buckets, not three, and here is why.** The obvious three —
fully publishable, awaiting photos, awaiting identity resolution — miss
a real, currently-populated case: a beer with both `abv` and
`calories_per_100ml` already known, where some of its SKUs are still
blocked by `unsupported_package_type` (a structural container-type gap
no photo or research can fix — Catalog Contract 1.0 Part 5's own flagged
incompatibility). Silently folding those into "awaiting photos" would
be wrong (a photo would accomplish nothing there); silently dropping
them would be worse. They get their own bucket:
`structurally_blocked_only`.

**"Awaiting identity resolution" is a documented proxy, not a stored
fact.** Nothing in the frozen schema records *why* a beer's identity is
still open — that judgment lives in a founder's own research notes, not
in the YAML. This module uses `style: unknown` as the closest available
signal already present in real data: a beer with no resolved style is,
at minimum, not yet fully classified. This will occasionally also catch
a beer that's fully identified but just has no matching entry in
`styles.yaml` yet (a different, smaller problem) — a known, accepted
imprecision, not a claim of certainty. If a future milestone adds a
real identity-status field, this proxy should be replaced then, not
before.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .photo_queue import PhotoQueueError, _load_photo_queue_inputs
from .models import EnrichmentBeer
from .validation_report import ValidationReport

_STRUCTURAL_ONLY_REASON_CODES = {"unsupported_package_type", "product_unavailable", "invalid_beer_entity"}


@dataclass(frozen=True)
class ProgressReport:
    total_beers: int
    fully_publishable_beers: List[str]
    awaiting_identity_resolution_beers: List[str]
    awaiting_photos_beers: List[str]
    structurally_blocked_only_beers: List[str]
    total_admitted_skus: int
    grouped_skus: int
    publishable_skus: int
    blocked_skus: int
    unenriched_skus: int


def build_progress_report(beers: List[EnrichmentBeer], report: ValidationReport) -> ProgressReport:
    """Pure function — no I/O. `beers`/`report` are the same real
    pipeline inputs `photo_queue.py` uses (see
    `photo_queue._load_photo_queue_inputs`), reused here rather than
    re-run a second way."""
    included_ids = set(report.included_canonical_product_ids)

    fully_publishable: List[str] = []
    awaiting_identity: List[str] = []
    awaiting_photos: List[str] = []
    structurally_blocked_only: List[str] = []

    for beer in beers:
        all_ids = set(beer.canonical_product_ids)
        if all_ids and all_ids <= included_ids:
            fully_publishable.append(beer.beer_key)
        elif beer.style is None:
            awaiting_identity.append(beer.beer_key)
        elif beer.abv is None or beer.calories_per_100ml is None:
            awaiting_photos.append(beer.beer_key)
        else:
            structurally_blocked_only.append(beer.beer_key)

    return ProgressReport(
        total_beers=len(beers),
        fully_publishable_beers=sorted(fully_publishable),
        awaiting_identity_resolution_beers=sorted(awaiting_identity),
        awaiting_photos_beers=sorted(awaiting_photos),
        structurally_blocked_only_beers=sorted(structurally_blocked_only),
        total_admitted_skus=report.skus_joined + report.skus_unenriched,
        grouped_skus=report.skus_joined,
        publishable_skus=report.skus_included,
        blocked_skus=report.skus_rejected,
        unenriched_skus=report.skus_unenriched,
    )


def _pct(numerator: int, denominator: int) -> float:
    return (100.0 * numerator / denominator) if denominator else 0.0


def _print_report(p: ProgressReport) -> None:
    print("Evidence Workflow — Repository Progress")
    print("=" * 78)
    print(f"Beers total:                      {p.total_beers}")
    print(
        f"  Fully publishable:               {len(p.fully_publishable_beers)} "
        f"({_pct(len(p.fully_publishable_beers), p.total_beers):.1f}%)"
    )
    print(f"  Awaiting photos:                  {len(p.awaiting_photos_beers)}")
    print(f"  Awaiting identity resolution:     {len(p.awaiting_identity_resolution_beers)}")
    print(f"  Structurally blocked only:        {len(p.structurally_blocked_only_beers)}")
    print()
    print(f"SKUs admitted (real, live rows):  {p.total_admitted_skus}")
    print(f"  Grouped into a Beer:              {p.grouped_skus} ({_pct(p.grouped_skus, p.total_admitted_skus):.1f}%)")
    print(f"  Publishable:                      {p.publishable_skus} ({_pct(p.publishable_skus, p.total_admitted_skus):.1f}% of admitted, "
          f"{_pct(p.publishable_skus, p.grouped_skus):.1f}% of grouped)")
    print(f"  Blocked (grouped, not yet ready): {p.blocked_skus}")
    print(f"  Unenriched (not yet grouped):     {p.unenriched_skus}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Repository-wide fieldwork progress dashboard.")
    parser.add_argument("--list", action="store_true", help="also print each beer_key in every bucket")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    try:
        beers, report = _load_photo_queue_inputs(repo_root)
    except PhotoQueueError as exc:
        raise SystemExit(f"photo_progress failed: {exc}") from exc

    progress = build_progress_report(beers, report)
    _print_report(progress)

    if args.list:
        print()
        for label, keys in [
            ("Fully publishable", progress.fully_publishable_beers),
            ("Awaiting photos", progress.awaiting_photos_beers),
            ("Awaiting identity resolution", progress.awaiting_identity_resolution_beers),
            ("Structurally blocked only", progress.structurally_blocked_only_beers),
        ]:
            print(f"{label} ({len(keys)}):")
            for key in keys:
                print(f"  - {key}")


if __name__ == "__main__":
    main()
