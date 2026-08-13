"""Resolves each real `beer_master.csv` row's `beer_key`, via every
loaded `EnrichmentBeer`'s own `canonical_product_ids` list — Catalog
Builder Implementation Design Part 4. Joining never validates business
meaning, only resolves identity (Part 1's own module-boundary rule,
restated here): the rules that decide whether a *successfully joined*
SKU is actually allowed to publish live in `business_rules.py`, not here.

Four distinct outcomes per `canonical_product_id`, all typed, matching
the request's own four detection categories:

- **Joined** — a real, admitted row matched to a real Beer. The normal
  case; a Beer's multiple `canonical_product_ids` each produce their own
  `JoinedSku`, all sharing the same `EnrichmentBeer`, so a multi-SKU beer
  keeps every one of its SKUs (never collapsed to one).
- **Unenriched** (`missing beer`) — a real, admitted row with no Beer
  claiming it yet. Row-level, never an abort; the direct successor to
  Catalog Implementation Architecture Part 3 Step 4's `unenriched_skus.csv`.
- **Missing candidate** — a Beer's `canonical_product_ids` entry that
  doesn't correspond to *any* real row at all (never existed, or a
  typo'd/stale reference).
- **Orphan SKU** — a Beer's `canonical_product_ids` entry that *does*
  correspond to a real row, but one the contamination gate rejected — a
  founder enriched something that should never have been treated as a
  beer. Tracked separately from "missing candidate" because the
  remediation is different, and more serious: this isn't a typo, it's
  evidence someone (or something) mis-identified a real product.

**Duplicate ownership** (a `canonical_product_id` claimed by two
different `beer_key`s) is structural — reuses
`schema_validate.check_no_duplicate_canonical_product_id_across_beers`
directly rather than a second implementation, and aborts the whole join
via `JoinError` before any of the above is computed, per Catalog Builder
Implementation Design Part 4's own framing of that specific case as "an
ambiguous, contradictory identity claim."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from .models import BeerMasterRow, EnrichmentBeer
from .schema_validate import SchemaValidationError, check_no_duplicate_canonical_product_id_across_beers


class JoinError(Exception):
    """A structural failure — the caller treats this as an abort."""


@dataclass(frozen=True)
class JoinedSku:
    beer_master_row: BeerMasterRow
    enrichment_beer: EnrichmentBeer


@dataclass(frozen=True)
class UnenrichedSku:
    canonical_product_id: str
    item_name_raw: str
    display_name: str


@dataclass(frozen=True)
class MissingCandidateReference:
    beer_key: str
    canonical_product_id: str


@dataclass(frozen=True)
class OrphanSkuReference:
    beer_key: str
    canonical_product_id: str


@dataclass(frozen=True)
class JoinResult:
    joined: List[JoinedSku]
    unenriched: List[UnenrichedSku]
    missing_candidates: List[MissingCandidateReference]
    orphan_skus: List[OrphanSkuReference]


def join(
    admitted_rows: List[BeerMasterRow],
    contaminated_row_ids: Set[str],
    beers: List[EnrichmentBeer],
) -> JoinResult:
    """`admitted_rows` must already be post-contamination-filter (this
    module never runs that gate itself). `contaminated_row_ids` is the
    set of `canonical_product_id`s the contamination gate rejected —
    used only to distinguish an orphan-SKU reference from a genuinely
    missing-candidate one; this module trusts that classification
    without re-deriving it.
    """
    try:
        check_no_duplicate_canonical_product_id_across_beers(beers)
    except SchemaValidationError as exc:
        raise JoinError(str(exc)) from exc

    admitted_by_id: Dict[str, BeerMasterRow] = {row.canonical_product_id: row for row in admitted_rows}
    claimed_ids: Set[str] = set()

    joined: List[JoinedSku] = []
    missing_candidates: List[MissingCandidateReference] = []
    orphan_skus: List[OrphanSkuReference] = []

    for beer in sorted(beers, key=lambda b: b.beer_key):
        for canonical_product_id in beer.canonical_product_ids:
            claimed_ids.add(canonical_product_id)
            row = admitted_by_id.get(canonical_product_id)
            if row is not None:
                joined.append(JoinedSku(beer_master_row=row, enrichment_beer=beer))
            elif canonical_product_id in contaminated_row_ids:
                orphan_skus.append(
                    OrphanSkuReference(beer_key=beer.beer_key, canonical_product_id=canonical_product_id)
                )
            else:
                missing_candidates.append(
                    MissingCandidateReference(beer_key=beer.beer_key, canonical_product_id=canonical_product_id)
                )

    unenriched = sorted(
        (
            UnenrichedSku(
                canonical_product_id=row.canonical_product_id,
                item_name_raw=row.item_name_raw,
                display_name=row.display_name,
            )
            for row in admitted_rows
            if row.canonical_product_id not in claimed_ids
        ),
        key=lambda entry: entry.canonical_product_id,
    )

    return JoinResult(
        joined=sorted(joined, key=lambda j: j.beer_master_row.canonical_product_id),
        unenriched=unenriched,
        missing_candidates=sorted(missing_candidates, key=lambda m: (m.beer_key, m.canonical_product_id)),
        orphan_skus=sorted(orphan_skus, key=lambda o: (o.beer_key, o.canonical_product_id)),
    )
