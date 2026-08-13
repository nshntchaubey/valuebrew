"""The founder's dashboard — turns `enrichment/candidates/`, the current
`enrichment/beers/` state, and `pricing_data/beer_master.csv`'s own
`container_type` field into one view of what needs attention, what
should be skipped, and what's already done. Not part of Catalog Builder
Implementation Design's own module list (it names `enrichment_report.py`
as the eventual CLI form of this same "Enrichment Queue" responsibility —
this is an earlier, candidate-file-based version of the identical
responsibility).

Five buckets, deterministic, every candidate in exactly one:

- **contamination** — the candidate's name matches the contamination
  gate's own exclusion vocabulary (reusing `contamination_filter.py`'s
  exact matching logic, never a second implementation of it). Never
  worth researching.
- **structurally_blocked** — the candidate's real `container_type`
  (read directly from `beer_master.csv`, never guessed) has no
  equivalent in the app's closed `PackageType` enum
  (`cross_reference_validate.CONTAINER_TYPE_MAP`, the exact same
  mapping the real build gate uses — read here, not re-decided).
  Confirmed directly against a real founder dry run: roughly a quarter
  of real candidates fall here, and nothing surfaced this before a
  founder had already spent research time on one.
- **enriched** — the candidate's `canonical_product_id` already appears
  in some real `enrichment/beers/*.yaml` file — a human already made
  the identity decision for it.
- **remaining** — everything else: genuinely available, waiting for a
  founder's research and a `create_beer.py` call.
- **malformed** — the candidate's own file is structurally broken
  (`schema_validate.py` rejected it) — tracked separately since it may
  not even carry a usable `canonical_product_id`.

**Display-only grouping, never an identity decision.** `remaining` is
also clustered by a best-effort strip-the-pack-size heuristic over
`normalized_name_key`, purely so pack-size siblings of one real beer
tend to sit near each other when a founder is scanning the list — never
consumed by any decision this module or any other makes, and known to
be imperfect (confirmed directly in a real dry run: "Kingfisher" vs.
"King Fisher" won't cluster; naming inconsistency in the source data is
real and this heuristic doesn't fix it). Grouping candidates remains,
as always, a founder's own judgment call.

Malformed Beer files (`rejected_beer_files`) are always surfaced,
never silently dropped — the completeness gap a prior implementation
audit found and fixed.

This module never writes anything — read-only, over already-generated,
already-validated artifacts and the real `beer_master.csv`.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .beer_master_reader import read_beer_master_csv
from .contamination_filter import find_matching_exclusion_term, load_default_exclusion_terms
from .cross_reference_validate import CONTAINER_TYPE_MAP
from .models import Candidate, EnrichmentBeer, RejectedBeerFileEntry, RejectedCandidateFile, RejectedEnrichmentFile
from .schema_validate import validate_candidates_directory, validate_enrichment_repository

_BEER_FILE_REJECTION_STAGE = "enrichment_schema"

# Execution Backlog E2 / Implementation Roadmap Part 8's own already-frozen
# number — cited for progress display, not decided here.
LAUNCH_TARGET_SKUS = 100

_TRAILING_PACK_SIZE = re.compile(
    r"[\s\-]*(can|bottle|btls?|cans?)?[\s\-]*\d+\s*ml(\s*x\s*\d+\w*)?\s*$",
    re.IGNORECASE,
)


def display_group_key(normalized_name_key: str) -> str:
    """Best-effort, display-only grouping key: strips a trailing pack-size
    chunk (e.g. `-can 330ml`, ` 650ml`, ` 330 ml`, `750mlx12btls`) so
    different pack sizes of what's probably the same beer tend to sort
    together. Never used for any decision — see this module's own
    docstring for its known limitations."""
    stripped = _TRAILING_PACK_SIZE.sub("", normalized_name_key).strip()
    return stripped or normalized_name_key


@dataclass(frozen=True)
class QueueEntry:
    canonical_product_id: str
    item_name_raw: str
    display_name: str
    container_type: Optional[str] = None
    beer_key: Optional[str] = None
    reason: Optional[str] = None


@dataclass(frozen=True)
class BeerFamilyGroup:
    """Display-only — see module docstring. Never an identity decision."""

    display_group_key: str
    entries: List[QueueEntry]


@dataclass(frozen=True)
class EnrichmentQueueReport:
    total_candidates: int
    enriched_count: int
    remaining_count: int
    contamination_count: int
    structurally_blocked_count: int
    malformed_count: int
    enriched: List[QueueEntry]
    remaining: List[QueueEntry]
    remaining_grouped: List[BeerFamilyGroup]
    contamination: List[QueueEntry]
    structurally_blocked: List[QueueEntry]
    malformed: List[QueueEntry]
    rejected_beer_files: List[RejectedBeerFileEntry]


def build_enrichment_queue(
    candidates: List[Candidate],
    rejected_candidate_files: List[RejectedCandidateFile],
    beers: List[EnrichmentBeer],
    exclusion_terms: List[str],
    *,
    rejected_beer_files: List[RejectedEnrichmentFile],
    container_type_by_id: Dict[str, str],
) -> EnrichmentQueueReport:
    """Pure function — no I/O. `candidates`/`rejected_candidate_files`
    are `schema_validate.validate_candidates_directory`'s own output;
    `beers`/`rejected_beer_files` are `enrichment_reader.load_beers`'s
    (or `schema_validate.validate_enrichment_repository`'s) output.
    `container_type_by_id` maps `canonical_product_id` -> the real
    `beer_master.csv` `container_type` string, built by the caller from
    `beer_master_reader.read_beer_master_csv`'s own output — this
    function never reads a file itself. Both keyword-only args are
    required, deliberately, so a caller can't silently omit rejected
    Beer files or the container-type lookup and quietly regress either
    one."""
    enriched_by_id: Dict[str, str] = {}
    for beer in beers:
        for canonical_product_id in beer.canonical_product_ids:
            enriched_by_id[canonical_product_id] = beer.beer_key

    enriched: List[QueueEntry] = []
    remaining: List[QueueEntry] = []
    contamination: List[QueueEntry] = []
    structurally_blocked: List[QueueEntry] = []

    for candidate in sorted(candidates, key=lambda c: c.canonical_product_id):
        cpid = candidate.canonical_product_id

        if cpid in enriched_by_id:
            enriched.append(
                QueueEntry(
                    canonical_product_id=cpid,
                    item_name_raw=candidate.item_name_raw,
                    display_name=candidate.display_name,
                    container_type=container_type_by_id.get(cpid),
                    beer_key=enriched_by_id[cpid],
                )
            )
            continue

        matched_term = find_matching_exclusion_term(candidate.item_name_raw, exclusion_terms)
        if matched_term is not None:
            contamination.append(
                QueueEntry(
                    canonical_product_id=cpid,
                    item_name_raw=candidate.item_name_raw,
                    display_name=candidate.display_name,
                    reason=f"matched exclusion term {matched_term!r}",
                )
            )
            continue

        container_type = container_type_by_id.get(cpid)
        if container_type is not None and container_type not in CONTAINER_TYPE_MAP:
            structurally_blocked.append(
                QueueEntry(
                    canonical_product_id=cpid,
                    item_name_raw=candidate.item_name_raw,
                    display_name=candidate.display_name,
                    container_type=container_type,
                    reason=f"container_type={container_type!r} has no PackageType equivalent",
                )
            )
            continue

        remaining.append(
            QueueEntry(
                canonical_product_id=cpid,
                item_name_raw=candidate.item_name_raw,
                display_name=candidate.display_name,
                container_type=container_type,
            )
        )

    malformed: List[QueueEntry] = sorted(
        (
            QueueEntry(
                canonical_product_id=Path(r.filename).stem,
                item_name_raw="",
                display_name="",
                reason=f"malformed_candidate_file: {r.reason_code}",
            )
            for r in rejected_candidate_files
        ),
        key=lambda entry: entry.canonical_product_id,
    )

    remaining_grouped = _group_for_display(remaining)

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

    total_candidates = len(candidates) + len(rejected_candidate_files)

    return EnrichmentQueueReport(
        total_candidates=total_candidates,
        enriched_count=len(enriched),
        remaining_count=len(remaining),
        contamination_count=len(contamination),
        structurally_blocked_count=len(structurally_blocked),
        malformed_count=len(malformed),
        enriched=enriched,
        remaining=remaining,
        remaining_grouped=remaining_grouped,
        contamination=contamination,
        structurally_blocked=structurally_blocked,
        malformed=malformed,
        rejected_beer_files=rejected_beer_file_entries,
    )


def _group_for_display(entries: List[QueueEntry]) -> List[BeerFamilyGroup]:
    groups: Dict[str, List[QueueEntry]] = {}
    for entry in entries:
        key = display_group_key(entry.display_name.lower())
        groups.setdefault(key, []).append(entry)

    return [
        BeerFamilyGroup(
            display_group_key=key,
            entries=sorted(groups[key], key=lambda e: e.canonical_product_id),
        )
        for key in sorted(groups)
    ]


def _matches_brand(entry: QueueEntry, brand: str) -> bool:
    return brand.lower() in entry.display_name.lower()


def _print_entries(entries: List[QueueEntry], *, brand: Optional[str], limit: Optional[int]) -> None:
    filtered = [e for e in entries if brand is None or _matches_brand(e, brand)]
    shown = filtered if limit is None else filtered[:limit]
    for entry in shown:
        extra = f" [{entry.container_type}]" if entry.container_type else ""
        beer = f" -> {entry.beer_key}" if entry.beer_key else ""
        reason = f" ({entry.reason})" if entry.reason else ""
        print(f"  - {entry.canonical_product_id}: {entry.display_name}{extra}{beer}{reason}")
    if len(filtered) > len(shown):
        print(f"  ... and {len(filtered) - len(shown)} more (use --limit to see more)")


def _build_report(repo_root: Path) -> EnrichmentQueueReport:
    enrichment_dir = repo_root / "enrichment"
    beer_master_path = repo_root / "pricing_data" / "beer_master.csv"

    candidates, rejected_candidate_files = validate_candidates_directory(enrichment_dir / "candidates")
    enrichment_report = validate_enrichment_repository(enrichment_dir)
    exclusion_terms = load_default_exclusion_terms()

    container_type_by_id: Dict[str, str] = {}
    if beer_master_path.exists():
        accepted, _ = read_beer_master_csv(beer_master_path)
        container_type_by_id = {row.canonical_product_id: row.container_type for row in accepted}

    return build_enrichment_queue(
        candidates,
        rejected_candidate_files,
        enrichment_report.beers,
        exclusion_terms,
        rejected_beer_files=enrichment_report.rejected_beer_files,
        container_type_by_id=container_type_by_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="The founder's enrichment dashboard.")
    parser.add_argument("--limit", type=int, default=20, help="max entries to print per section (default: 20)")
    parser.add_argument("--brand", type=str, default=None, help="filter to candidates whose name contains TEXT")
    parser.add_argument("--remaining", action="store_true", help="show only the remaining (workable) candidates")
    parser.add_argument("--blocked", action="store_true", help="show only structurally-blocked candidates")
    parser.add_argument("--enriched", action="store_true", help="show only already-enriched candidates")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = _build_report(repo_root)

    any_section_selected = args.remaining or args.blocked or args.enriched

    if not any_section_selected:
        pct = (100 * report.enriched_count / report.total_candidates) if report.total_candidates else 0.0
        toward_launch = min(100.0, 100 * report.enriched_count / LAUNCH_TARGET_SKUS)
        print("Founder Dashboard")
        print("=================")
        print(f"Total candidates:        {report.total_candidates}")
        print(f"Enriched:                {report.enriched_count} ({pct:.1f}%)")
        print(f"Remaining (workable):    {report.remaining_count}")
        print(f"Structurally blocked:    {report.structurally_blocked_count}")
        print(f"Contamination:           {report.contamination_count}")
        print(f"Malformed candidates:    {report.malformed_count}")
        print(f"Rejected Beer files:     {len(report.rejected_beer_files)}")
        print(f"Progress toward Version 1 target ({LAUNCH_TARGET_SKUS} SKUs): {toward_launch:.1f}%")

        if report.rejected_beer_files:
            print("\nRejected Beer files (must be fixed by hand):")
            for entry in report.rejected_beer_files:
                print(f"  - {entry.filename} [{entry.stage}]: {entry.reason_code} — {entry.reason_detail}")

        if report.contamination:
            print(f"\nContamination ({len(report.contamination)}):")
            _print_entries(report.contamination, brand=args.brand, limit=args.limit)

        print(f"\nRemaining, grouped for display only ({report.remaining_count} total):")
        groups = report.remaining_grouped
        if args.brand:
            groups = [g for g in groups if any(_matches_brand(e, args.brand) for e in g.entries)]
        for group in groups[: args.limit]:
            print(f"  {group.display_group_key} ({len(group.entries)}):")
            _print_entries(group.entries, brand=args.brand, limit=None)
        if len(groups) > args.limit:
            print(f"  ... and {len(groups) - args.limit} more groups (use --limit to see more)")
        return

    if args.remaining:
        print(f"Remaining ({report.remaining_count}):")
        _print_entries(report.remaining, brand=args.brand, limit=args.limit)
    if args.blocked:
        print(f"Structurally blocked ({report.structurally_blocked_count}):")
        _print_entries(report.structurally_blocked, brand=args.brand, limit=args.limit)
    if args.enriched:
        print(f"Enriched ({report.enriched_count}):")
        _print_entries(report.enriched, brand=args.brand, limit=args.limit)


if __name__ == "__main__":
    main()
