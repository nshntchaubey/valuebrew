"""Every deterministic Catalog Builder Architecture §7 / Part 5
publication rule not already enforced by an earlier layer — reused, not
invented. Operates only on already-joined pairs (`join.py`'s own
`JoinedSku`); the contamination gate and the join layer's own reference
checks are deliberately not re-applied here (each layer owns exactly one
concern, per Catalog Builder Implementation Design Part 1's own
"Validation never mutates, only inspects and reports" boundary).

**Blocking rules, in the order Catalog Builder Architecture Part 7's own
ranked risk list gives them:**

1. **Invalid Beer entity** — the owning Beer failed `validate_beer.py`
   (an externally-computed `invalid_beer_keys` set, so this module stays
   pure/no I/O; nothing here re-implements Beer validation).
2. **Product unavailable** — `status != "LIVE"` (Beer Knowledge Base
   Architecture Part 6: a delisted product "simply stops being joinable
   ... naturally excludes it," restated here as the rule that actually
   enforces that).
3. **Missing ABV** — the single most consequential rule in this whole
   module (Catalog Builder Architecture Part 5: ABV is provisionally
   mandatory pending Product Decisions Register D1). Resolution order:
   a per-SKU override in the Beer's own `skus` map, if one exists for
   this exact `canonical_product_id`, else the Beer-level default — the
   exact precedence Beer Knowledge Base Architecture Part 3's own worked
   example describes, implemented here for the first time.
4. **Missing Style** — added while building `assemble.py` (Milestone 7),
   not previously enforced anywhere: `Beer.style_id` is a required,
   non-nullable field in the real schema (Catalog Contract 1.0 Part 4),
   and Part 7 names it explicitly, by field name, as the same "zero
   nullable fields" case ABV already is — "There is no ... Beer with a
   null `style_id`... either the fact is fully known and the entity is
   included, or it isn't known and the entity is excluded from that
   build entirely." A Beer enriched with `style: unknown` is a
   legitimate intermediate state during enrichment work (Beer Knowledge
   Base Architecture Part 3 explicitly allows it), but cannot be
   assembled into a valid `Beer` record until resolved — same shape as
   the ABV rule, same citation, applied to the one other field with an
   `unknown` escape valve.
5. **Missing calories** — `Sku.calories` is required and non-nullable
   in the real schema. `EnrichmentBeer` carries the manually-cited fact
   as `calories_per_100ml` (a concentration, matching what manufacturer
   sources actually publish — production enrichment found no source
   that publishes a per-pack total directly) using the same
   `AttributionBlock` pattern as ABV; `Sku.calories`, the per-pack total,
   is computed from it at build time (`assemble.py`'s
   `resolve_calories`), not entered directly. Same blocking shape as the
   ABV/style rules — a beer whose `calories_per_100ml` is still
   `unknown` blocks exactly like a beer whose `abv` is.

**Warning-only, never blocking:** a stale price — `effective_date` more
than one cycle behind the row's own `last_updated_run_month` (Catalog
Builder Architecture Part 7's own "more than one documented cycle"
language; Product Decisions Register D11 remains open on what, if
anything, this should mean for *display* — this module only flags it in
the report, never excludes on it).

**Deliberately not implemented, flagged rather than silently skipped:**
broken/unlicensed image references (Catalog Builder Architecture Part 7)
— the current, frozen `EnrichmentBeer.images` schema (Beer Knowledge
Base Architecture Part 3) stores a bare list of strings with no license
field at all, and no real Beer file has ever populated one; enforcing a
license rule against a field the schema doesn't actually carry would be
inventing data, not validating it. Listing-inconsistency (multi-supplier
price spread) is also not implemented — Catalog Builder Architecture
Part 7 itself never names a concrete threshold, and checking it would
require reading `item_code_canonical_map.csv`, a data source no module
in this package reads today; implementing either would mean guessing at
an undecided number or building unrequested infrastructure, not applying
"only the frozen architecture."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from .join import JoinedSku
from .models import AttributionBlock


@dataclass(frozen=True)
class AdmittedSku:
    joined: JoinedSku
    resolved_abv: AttributionBlock
    resolved_calories_per_100ml: AttributionBlock
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RejectedJoinedSku:
    joined: JoinedSku
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class BusinessRulesResult:
    admitted: List[AdmittedSku]
    rejected: List[RejectedJoinedSku]


def resolve_abv(joined_sku: JoinedSku) -> Optional[AttributionBlock]:
    """A per-SKU override, if one exists for this exact
    `canonical_product_id`, else the Beer-level default. `None` means
    genuinely unresolved (both are missing/unknown)."""
    beer = joined_sku.enrichment_beer
    canonical_product_id = joined_sku.beer_master_row.canonical_product_id
    return beer.skus.get(canonical_product_id, beer.abv)


def _is_price_stale(row) -> bool:
    try:
        run_year_str, run_month_str = row.last_updated_run_month.split("-")
        run_year, run_month = int(run_year_str), int(run_month_str)
    except (ValueError, AttributeError):
        return False
    run_month_index = run_year * 12 + (run_month - 1)
    effective_month_index = row.effective_date.year * 12 + (row.effective_date.month - 1)
    return (run_month_index - effective_month_index) > 1


def apply_business_rules(
    joined_skus: List[JoinedSku],
    invalid_beer_keys: Set[str],
) -> BusinessRulesResult:
    """Pure function — no I/O. `invalid_beer_keys` is computed upstream
    (e.g. `validate_beer.compute_invalid_beer_keys`), never re-derived
    here."""
    admitted: List[AdmittedSku] = []
    rejected: List[RejectedJoinedSku] = []

    ordered = sorted(joined_skus, key=lambda j: j.beer_master_row.canonical_product_id)

    for joined_sku in ordered:
        row = joined_sku.beer_master_row
        beer = joined_sku.enrichment_beer

        if beer.beer_key in invalid_beer_keys:
            rejected.append(
                RejectedJoinedSku(
                    joined=joined_sku,
                    reason_code="invalid_beer_entity",
                    reason_detail=f"beer_key {beer.beer_key!r} failed Beer validation",
                )
            )
            continue

        if row.status != "LIVE":
            rejected.append(
                RejectedJoinedSku(
                    joined=joined_sku, reason_code="product_unavailable", reason_detail=f"status={row.status!r}"
                )
            )
            continue

        resolved_abv = resolve_abv(joined_sku)
        if resolved_abv is None:
            rejected.append(
                RejectedJoinedSku(
                    joined=joined_sku,
                    reason_code="missing_abv",
                    reason_detail="no beer-level or SKU-level ABV recorded",
                )
            )
            continue

        if beer.style is None:
            rejected.append(
                RejectedJoinedSku(
                    joined=joined_sku,
                    reason_code="missing_style",
                    reason_detail="Beer.style_id is required and non-nullable (Catalog Contract 1.0 Part 7); "
                    "this beer's style is still 'unknown'",
                )
            )
            continue

        if beer.calories_per_100ml is None:
            rejected.append(
                RejectedJoinedSku(
                    joined=joined_sku,
                    reason_code="missing_calories",
                    reason_detail="Sku.calories is required and non-nullable (Catalog Contract 1.0 Part 5); "
                    "this beer's calories_per_100ml is still 'unknown'",
                )
            )
            continue

        warnings: List[str] = []
        if _is_price_stale(row):
            warnings.append("stale_price")

        admitted.append(
            AdmittedSku(
                joined=joined_sku,
                resolved_abv=resolved_abv,
                resolved_calories_per_100ml=beer.calories_per_100ml,
                warnings=warnings,
            )
        )

    return BusinessRulesResult(admitted=admitted, rejected=rejected)
