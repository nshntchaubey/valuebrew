"""Builds the final in-memory Style/Beer/Sku/Benchmark graph — Catalog
Builder Implementation Design Part 7 — from `cross_reference_validate.py`'s
own output. Everything upstream (join, business rules, cross-reference
validation) has already decided which SKUs are eligible; this module's
only remaining job is arithmetic and shape: compute
`cost_per_litre`/`cost_per_ml_alcohol` (Milestone 1's `value_metrics.py`),
compute Style Benchmarks (`benchmarks.py`), compute
`value_score`/`value_verdict` (`value_score.py`), and emit the exact
Catalog Contract 1.0 Parts 2-6 structure.

Not literally the two-pass sequence Catalog Builder Implementation
Design Part 2's table describes ("once early... once at the end") —
`value_metrics.py`/`benchmarks.py`/`value_score.py` were built in
Milestone 1 as pure functions over raw values, not needing a Beer/Style
object graph to exist first, so this module reaches the same result in
one coherent pass. A more granular expression of the same sequence, per
that design document's own Part 10 framing, not a different one.

By the time a `ValidatedSku` reaches this module, `business_rules.py`
has already guaranteed `resolved_abv` and `resolved_calories_per_100ml`
are real values, and `cross_reference_validate.py` has already
guaranteed the Beer's `style` resolves to a real `StyleDef` — so every
lookup below is expected to succeed; a failure would mean an upstream
invariant broke, and raises loudly rather than guessing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from .benchmarks import compute_benchmarks
from .cross_reference_validate import ValidatedSku
from .models import AttributionBlock, Beer, Benchmark, Catalog, Sku, Style, StyleDef, ValueVerdict
from .value_metrics import cost_per_litre as compute_cost_per_litre
from .value_metrics import cost_per_ml_alcohol as compute_cost_per_ml_alcohol
from .value_score import compute_value_score, compute_value_verdict

PRICE_SOURCE = "karnataka_excise_mrp_2026"


class AssembleError(Exception):
    """A structural invariant this module trusts an earlier layer to
    have already guaranteed was violated — the caller treats this as an
    abort; it should never actually happen given every module upstream
    of this one is already implemented and tested."""


def resolve_calories(resolved_calories_per_100ml_block: AttributionBlock, pack_size_ml: int) -> int:
    """`AttributionBlock.value` here is a concentration — kcal per
    100ml, exactly as manufacturers publish it (`EnrichmentBeer`'s own
    docstring) — while `Sku.calories` is the per-pack total the app
    actually shows. Scaled by this SKU's own `size_ml` and rounded to
    the nearest whole calorie, once, here, so no founder ever has to do
    this arithmetic by hand or repeat it inconsistently per pack size."""
    return int(round(resolved_calories_per_100ml_block.value * pack_size_ml / 100))


def assemble_catalog(
    valid_skus: List[ValidatedSku],
    style_defs: List[StyleDef],
    catalog_version: int,
    generated_at: datetime,
) -> Catalog:
    """Pure function — no I/O. `valid_skus` is
    `cross_reference_validate.validate_cross_references`'s own `.valid`
    list; `style_defs` is `enrichment_reader.load_styles`'s output.
    Output lists are each sorted by their own id for deterministic,
    byte-identical builds from identical inputs."""
    style_by_key: Dict[str, StyleDef] = {s.style_key: s for s in style_defs}

    # Step 1: per-SKU raw value metrics.
    cost_per_ml_alcohol_by_id: Dict[str, float] = {}
    for validated in valid_skus:
        row = validated.admitted.joined.beer_master_row
        abv_value = validated.admitted.resolved_abv.value
        cost_per_ml_alcohol_by_id[row.canonical_product_id] = compute_cost_per_ml_alcohol(
            price=float(row.mrp), size_ml=row.pack_size_ml, abv=abv_value
        )

    # Step 2: group by style, compute Benchmarks.
    grouped_by_style: Dict[str, List[float]] = {}
    for validated in valid_skus:
        row = validated.admitted.joined.beer_master_row
        beer = validated.admitted.joined.enrichment_beer
        if beer.style is None:
            raise AssembleError(
                f"canonical_product_id {row.canonical_product_id!r} reached assemble.py with no "
                f"resolved style — business_rules.py's own missing_style rule should have excluded it"
            )
        grouped_by_style.setdefault(beer.style, []).append(cost_per_ml_alcohol_by_id[row.canonical_product_id])

    computed_benchmarks = compute_benchmarks(grouped_by_style)
    benchmark_by_style_id: Dict[str, Benchmark] = {b.style_id: b for b in computed_benchmarks}

    # Step 3: assemble Sku records.
    skus: List[Sku] = []
    beer_ids_included: set = set()
    style_ids_included: set = set()

    for validated in valid_skus:
        row = validated.admitted.joined.beer_master_row
        beer = validated.admitted.joined.enrichment_beer
        style_key = beer.style
        assert style_key is not None  # guaranteed above

        benchmark = benchmark_by_style_id.get(style_key)
        if benchmark is None:
            raise AssembleError(
                f"style {style_key!r} has admitted SKUs but no computed Benchmark — "
                f"benchmarks.py should always produce one for any style with >=1 admitted Sku"
            )

        cost_per_ml_alcohol_value = cost_per_ml_alcohol_by_id[row.canonical_product_id]
        value_score = compute_value_score(cost_per_ml_alcohol_value, benchmark)
        value_verdict = compute_value_verdict(value_score)

        skus.append(
            Sku(
                id=row.canonical_product_id,
                beer_id=beer.beer_key,
                size_ml=row.pack_size_ml,
                package_type=validated.package_type,
                abv=validated.admitted.resolved_abv.value,
                calories=resolve_calories(validated.admitted.resolved_calories_per_100ml, row.pack_size_ml),
                price=float(row.mrp),
                price_last_checked=row.effective_date,
                price_source=PRICE_SOURCE,
                cost_per_litre=compute_cost_per_litre(price=float(row.mrp), size_ml=row.pack_size_ml),
                cost_per_ml_alcohol=cost_per_ml_alcohol_value,
                value_score=value_score,
                value_verdict=value_verdict,
            )
        )
        beer_ids_included.add(beer.beer_key)
        style_ids_included.add(style_key)

    # Step 4: assemble Beer records — one per distinct beer_key with
    # >=1 included Sku.
    beer_by_key: Dict[str, Beer] = {}
    for validated in valid_skus:
        beer = validated.admitted.joined.enrichment_beer
        if beer.beer_key in beer_by_key:
            continue
        beer_by_key[beer.beer_key] = Beer(
            id=beer.beer_key,
            name=beer.name,
            brewery=beer.brewery,
            style_id=beer.style,  # type: ignore[arg-type]  # non-None, guaranteed above
            is_craft=beer.is_craft,
        )
    beers = sorted(beer_by_key.values(), key=lambda b: b.id)

    # Step 5: assemble Style records — one per distinct style_id
    # actually referenced by an included Beer.
    styles: List[Style] = []
    for style_key in sorted(style_ids_included):
        style_def = style_by_key.get(style_key)
        if style_def is None:
            raise AssembleError(
                f"style_key {style_key!r} is referenced by an included Beer but not found in styles.yaml — "
                f"cross_reference_validate.py's own dangling_style_reference check should have excluded it"
            )
        styles.append(Style(id=style_def.style_key, name=style_def.name, description=style_def.description))

    return Catalog(
        catalog_version=catalog_version,
        generated_at=generated_at,
        styles=styles,
        beers=beers,
        skus=sorted(skus, key=lambda s: s.id),
        benchmarks=sorted(computed_benchmarks, key=lambda b: b.style_id),
    )
