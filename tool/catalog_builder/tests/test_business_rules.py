from datetime import date
from decimal import Decimal

from tool.catalog_builder.business_rules import apply_business_rules, resolve_abv
from tool.catalog_builder.join import JoinedSku
from tool.catalog_builder.models import AttributionBlock, BeerMasterRow, EnrichmentBeer

_ABV = AttributionBlock(
    value=4.8,
    source_type="manufacturer",
    source_name="United Breweries official product page",
    observed_at=date(2026, 8, 13),
    observed_by="founder",
)
_OVERRIDE_ABV = AttributionBlock(
    value=8.0,
    source_type="manufacturer",
    source_name="United Breweries official product page",
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
        landed_cost=Decimal("2095.74"),
        ksbcl_selling_price=Decimal("2106.22"),
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
        calories_per_100ml=_ABV,
    )
    defaults.update(overrides)
    return EnrichmentBeer(**defaults)


# ---------------------------------------------------------------------------
# resolve_abv
# ---------------------------------------------------------------------------


def test_resolve_abv_uses_beer_level_default():
    joined = JoinedSku(_row("CP0000002"), _beer("x", ["CP0000002"], abv=_ABV))
    assert resolve_abv(joined) is _ABV


def test_resolve_abv_prefers_sku_level_override():
    beer = _beer("x", ["CP0000002"], abv=_ABV, skus={"CP0000002": _OVERRIDE_ABV})
    joined = JoinedSku(_row("CP0000002"), beer)
    assert resolve_abv(joined) is _OVERRIDE_ABV


def test_resolve_abv_returns_none_when_both_missing():
    joined = JoinedSku(_row("CP0000002"), _beer("x", ["CP0000002"], abv=None))
    assert resolve_abv(joined) is None


# ---------------------------------------------------------------------------
# apply_business_rules
# ---------------------------------------------------------------------------


def test_valid_sku_is_admitted():
    joined = JoinedSku(_row("CP0000002"), _beer("x", ["CP0000002"]))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert len(result.admitted) == 1
    assert result.rejected == []
    assert result.admitted[0].resolved_abv is _ABV


def test_invalid_beer_entity_is_rejected():
    joined = JoinedSku(_row("CP0000002"), _beer("bad_beer", ["CP0000002"]))
    result = apply_business_rules([joined], invalid_beer_keys={"bad_beer"})
    assert result.admitted == []
    assert result.rejected[0].reason_code == "invalid_beer_entity"


def test_delisted_product_is_rejected():
    joined = JoinedSku(_row("CP0000002", status="DELISTED"), _beer("x", ["CP0000002"]))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert result.admitted == []
    assert result.rejected[0].reason_code == "product_unavailable"


def test_missing_abv_is_rejected():
    joined = JoinedSku(_row("CP0000002"), _beer("x", ["CP0000002"], abv=None))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert result.admitted == []
    assert result.rejected[0].reason_code == "missing_abv"


def test_missing_style_is_rejected():
    joined = JoinedSku(_row("CP0000002"), _beer("x", ["CP0000002"], style=None))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert result.admitted == []
    assert result.rejected[0].reason_code == "missing_style"


def test_missing_calories_is_a_warning_not_a_rejection():
    # Product Decisions Register D22: calories is warning-only now that
    # value_metrics.py/value_score.py never use it -- unlike missing_abv
    # and missing_style, this no longer excludes the SKU.
    joined = JoinedSku(_row("CP0000002"), _beer("x", ["CP0000002"], calories_per_100ml=None))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert result.rejected == []
    assert len(result.admitted) == 1
    assert result.admitted[0].resolved_calories_per_100ml is None
    assert result.admitted[0].warnings == ["missing_calories"]


def test_missing_calories_and_stale_price_both_warn_together():
    row = _row("CP0000002", effective_date=date(2026, 1, 1), last_updated_run_month="2026-06")
    joined = JoinedSku(row, _beer("x", ["CP0000002"], calories_per_100ml=None))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert result.admitted[0].warnings == ["stale_price", "missing_calories"]


def test_stale_price_is_a_warning_not_a_rejection():
    # last_updated_run_month is 3 months after effective_date -> stale.
    row = _row("CP0000002", effective_date=date(2026, 1, 1), last_updated_run_month="2026-06")
    joined = JoinedSku(row, _beer("x", ["CP0000002"]))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert len(result.admitted) == 1
    assert result.admitted[0].warnings == ["stale_price"]


def test_fresh_price_has_no_warning():
    row = _row("CP0000002", effective_date=date(2026, 6, 1), last_updated_run_month="2026-06")
    joined = JoinedSku(row, _beer("x", ["CP0000002"]))
    result = apply_business_rules([joined], invalid_beer_keys=set())
    assert result.admitted[0].warnings == []


def test_output_is_deterministic_and_sorted():
    joined_a = JoinedSku(_row("CP0000099"), _beer("x", ["CP0000099"]))
    joined_b = JoinedSku(_row("CP0000002"), _beer("y", ["CP0000002"]))
    result = apply_business_rules([joined_a, joined_b], invalid_beer_keys=set())
    assert [a.joined.beer_master_row.canonical_product_id for a in result.admitted] == ["CP0000002", "CP0000099"]
