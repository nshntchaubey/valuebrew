from datetime import date, datetime
from decimal import Decimal

import pytest

from tool.catalog_builder.assemble import AssembleError, assemble_catalog
from tool.catalog_builder.business_rules import AdmittedSku
from tool.catalog_builder.cross_reference_validate import ValidatedSku
from tool.catalog_builder.join import JoinedSku
from tool.catalog_builder.models import AttributionBlock, BeerMasterRow, EnrichmentBeer, PackageType, StyleDef, ValueVerdict
from tool.catalog_builder.value_metrics import cost_per_litre, cost_per_ml_alcohol

_LAGER = StyleDef(style_key="lager", name="Lager", description="Crisp, mild bitterness")
_STOUT = StyleDef(style_key="stout", name="Stout", description="Dark, roasted")

_ABV = AttributionBlock(
    value=4.8, source_type="manufacturer", source_name="X", observed_at=date(2026, 8, 13), observed_by="founder"
)
_CALORIES = AttributionBlock(
    # kcal per 100ml, exactly as a manufacturer would publish it -- 50
    # kcal/100ml x the default 330ml test row / 100 = 165, the same
    # expected Sku.calories total this test suite used before the
    # per-100ml rename, so the assertions below stay unchanged.
    value=50,
    source_type="manufacturer",
    source_name="X",
    observed_at=date(2026, 8, 13),
    observed_by="founder",
)


def _row(canonical_product_id: str, **overrides) -> BeerMasterRow:
    defaults = dict(
        canonical_product_id=canonical_product_id,
        representative_item_code="2020900211",
        item_name_raw="Kingfisher Premium Lager Beer-CAN 330ML(0202)",
        display_name="Kingfisher Premium Lager Beer-CAN 330ML",
        normalized_name_key="kingfisher premium lager beer-can 330ml",
        pack_size_ml=330,
        pack_count=None,
        container_type="can",
        declared_price=Decimal("100.00"),
        landed_cost=Decimal("200.00"),
        ksbcl_selling_price=Decimal("210.00"),
        mrp=Decimal("100.00"),
        effective_date=date(2026, 6, 1),
        status="LIVE",
        delisted_run_month=None,
        classification_confidence="high",
        classification_matched_on="style_keyword:beer",
        gtin=None,
        gtin_confidence=None,
        source_pdf_reference="x.pdf",
        first_seen_run_month="2026-06",
        last_updated_run_month="2026-06",
    )
    defaults.update(overrides)
    return BeerMasterRow(**defaults)


def _beer(beer_key: str, canonical_product_ids, **overrides) -> EnrichmentBeer:
    defaults = dict(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name="Kingfisher Premium",
        brewery="United Breweries",
        style="lager",
        abv=_ABV,
        calories_per_100ml=_CALORIES,
    )
    defaults.update(overrides)
    return EnrichmentBeer(**defaults)


def _validated(
    row: BeerMasterRow, beer: EnrichmentBeer, package_type=PackageType.CAN, resolved_calories_per_100ml=_CALORIES
) -> ValidatedSku:
    admitted = AdmittedSku(
        joined=JoinedSku(row, beer), resolved_abv=_ABV, resolved_calories_per_100ml=resolved_calories_per_100ml
    )
    return ValidatedSku(admitted=admitted, package_type=package_type)


_GENERATED_AT = datetime(2026, 8, 13, 10, 0, 0)


def test_single_sku_beer_assembles_correctly():
    row = _row("CP0000002", mrp=Decimal("100.00"), pack_size_ml=330)
    beer = _beer("kingfisher_premium", ["CP0000002"])
    catalog = assemble_catalog([_validated(row, beer)], [_LAGER], catalog_version=1, generated_at=_GENERATED_AT)

    assert catalog.catalog_version == 1
    assert catalog.generated_at == _GENERATED_AT
    assert len(catalog.styles) == 1
    assert catalog.styles[0].id == "lager"
    assert catalog.styles[0].name == "Lager"
    assert len(catalog.beers) == 1
    assert catalog.beers[0].id == "kingfisher_premium"
    assert catalog.beers[0].style_id == "lager"
    assert len(catalog.skus) == 1
    sku = catalog.skus[0]
    assert sku.id == "CP0000002"
    assert sku.beer_id == "kingfisher_premium"
    assert sku.size_ml == 330
    assert sku.package_type == PackageType.CAN
    assert sku.abv == 4.8
    assert sku.calories == 165
    assert sku.price == 100.0
    assert sku.price_last_checked == date(2026, 6, 1)
    assert sku.cost_per_litre == cost_per_litre(price=100.0, size_ml=330)
    assert sku.cost_per_ml_alcohol == cost_per_ml_alcohol(price=100.0, size_ml=330, abv=4.8)
    assert len(catalog.benchmarks) == 1
    assert catalog.benchmarks[0].style_id == "lager"
    assert catalog.benchmarks[0].sample_size == 1


def test_multi_sku_beer_produces_multiple_skus_one_beer():
    rows = [_row("CP0000002", pack_size_ml=330), _row("CP0000003", pack_size_ml=650)]
    beer = _beer("kingfisher_premium", ["CP0000002", "CP0000003"])
    catalog = assemble_catalog(
        [_validated(r, beer) for r in rows], [_LAGER], catalog_version=1, generated_at=_GENERATED_AT
    )

    assert len(catalog.beers) == 1
    assert len(catalog.skus) == 2
    assert {s.id for s in catalog.skus} == {"CP0000002", "CP0000003"}
    assert all(s.beer_id == "kingfisher_premium" for s in catalog.skus)


def test_calories_scale_with_pack_size_from_one_shared_concentration():
    # One Beer-level calories_per_100ml (50 kcal/100ml) must produce a
    # different, correctly-scaled Sku.calories total for each pack size
    # -- the whole reason this field is a concentration, not a total.
    small_row = _row("CP0000002", pack_size_ml=330)
    large_row = _row("CP0000003", pack_size_ml=650)
    beer = _beer("kingfisher_premium", ["CP0000002", "CP0000003"])

    catalog = assemble_catalog(
        [_validated(small_row, beer), _validated(large_row, beer)],
        [_LAGER],
        catalog_version=1,
        generated_at=_GENERATED_AT,
    )

    by_id = {s.id: s for s in catalog.skus}
    assert by_id["CP0000002"].calories == 165  # round(50 * 330 / 100)
    assert by_id["CP0000003"].calories == 325  # round(50 * 650 / 100)


def test_unknown_calories_produces_none_not_a_crash():
    # Product Decisions Register D22: a SKU can be admitted with
    # resolved_calories_per_100ml=None (calories is warning-only now) --
    # resolve_calories must pass that through as None, not raise or guess.
    row = _row("CP0000002", pack_size_ml=330)
    beer = _beer("kingfisher_premium", ["CP0000002"], calories_per_100ml=None)
    catalog = assemble_catalog(
        [_validated(row, beer, resolved_calories_per_100ml=None)],
        [_LAGER],
        catalog_version=1,
        generated_at=_GENERATED_AT,
    )

    assert catalog.skus[0].calories is None
    # Everything else about the SKU still assembles normally -- calories
    # being unknown never touches ABV or Value Score.
    assert catalog.skus[0].abv == 4.8
    assert isinstance(catalog.skus[0].value_score, int)


def test_multiple_styles_produce_multiple_benchmarks():
    lager_row = _row("CP0000002")
    stout_row = _row("CP0000003", item_name_raw="Some Stout 330ML")
    lager_beer = _beer("kingfisher_premium", ["CP0000002"], style="lager")
    stout_beer = _beer("some_stout", ["CP0000003"], style="stout")

    catalog = assemble_catalog(
        [_validated(lager_row, lager_beer), _validated(stout_row, stout_beer)],
        [_LAGER, _STOUT],
        catalog_version=1,
        generated_at=_GENERATED_AT,
    )

    assert {b.style_id for b in catalog.benchmarks} == {"lager", "stout"}
    assert {s.id for s in catalog.styles} == {"lager", "stout"}


def test_unreferenced_style_is_excluded_from_output():
    # styles.yaml may define more styles than any admitted beer uses --
    # only referenced ones appear in the catalog.
    row = _row("CP0000002")
    beer = _beer("kingfisher_premium", ["CP0000002"], style="lager")
    catalog = assemble_catalog([_validated(row, beer)], [_LAGER, _STOUT], catalog_version=1, generated_at=_GENERATED_AT)

    assert [s.id for s in catalog.styles] == ["lager"]


def test_value_score_and_verdict_are_populated_consistently():
    # Two SKUs in the same style, one cheaper than the other -- the
    # cheaper one must score higher and never rank worse.
    cheap_row = _row("CP0000002", mrp=Decimal("80.00"))
    pricey_row = _row("CP0000003", mrp=Decimal("150.00"))
    cheap_beer = _beer("cheap_beer", ["CP0000002"])
    pricey_beer = _beer("pricey_beer", ["CP0000003"])

    catalog = assemble_catalog(
        [_validated(cheap_row, cheap_beer), _validated(pricey_row, pricey_beer)],
        [_LAGER],
        catalog_version=1,
        generated_at=_GENERATED_AT,
    )

    by_id = {s.id: s for s in catalog.skus}
    assert by_id["CP0000002"].value_score >= by_id["CP0000003"].value_score
    assert isinstance(by_id["CP0000002"].value_verdict, ValueVerdict)


def test_output_is_deterministic_and_sorted():
    rows = [_row("CP0000099"), _row("CP0000002")]
    beers = [_beer("b", ["CP0000099"]), _beer("a", ["CP0000002"])]
    validated = [_validated(rows[0], beers[0]), _validated(rows[1], beers[1])]

    first = assemble_catalog(validated, [_LAGER], catalog_version=1, generated_at=_GENERATED_AT)
    second = assemble_catalog(validated, [_LAGER], catalog_version=1, generated_at=_GENERATED_AT)

    assert first == second
    assert [s.id for s in first.skus] == ["CP0000002", "CP0000099"]
    assert [b.id for b in first.beers] == ["a", "b"]


def test_catalog_version_and_generated_at_pass_through_unchanged():
    row = _row("CP0000002")
    beer = _beer("x", ["CP0000002"])
    catalog = assemble_catalog([_validated(row, beer)], [_LAGER], catalog_version=42, generated_at=_GENERATED_AT)
    assert catalog.catalog_version == 42
    assert catalog.generated_at == _GENERATED_AT


def test_empty_input_produces_empty_catalog():
    catalog = assemble_catalog([], [_LAGER], catalog_version=1, generated_at=_GENERATED_AT)
    assert catalog.styles == []
    assert catalog.beers == []
    assert catalog.skus == []
    assert catalog.benchmarks == []
