from datetime import date
from decimal import Decimal

import pytest

from tool.catalog_builder.join import JoinError, join
from tool.catalog_builder.models import BeerMasterRow, EnrichmentBeer


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
        declared_price=Decimal("666.90"),
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
        style=None,
        abv=None,
        calories_per_100ml=None,
    )
    defaults.update(overrides)
    return EnrichmentBeer(**defaults)


# ---------------------------------------------------------------------------
# Successful join
# ---------------------------------------------------------------------------


def test_single_sku_beer_joins_successfully():
    rows = [_row("CP0000002")]
    beers = [_beer("kingfisher_premium", ["CP0000002"])]

    result = join(rows, contaminated_row_ids=set(), beers=beers)

    assert len(result.joined) == 1
    assert result.joined[0].beer_master_row.canonical_product_id == "CP0000002"
    assert result.joined[0].enrichment_beer.beer_key == "kingfisher_premium"
    assert result.unenriched == []
    assert result.missing_candidates == []
    assert result.orphan_skus == []


def test_multi_sku_beer_preserves_every_sku():
    rows = [_row("CP0000002"), _row("CP0000003"), _row("CP0000004")]
    beers = [_beer("kingfisher_premium", ["CP0000002", "CP0000003", "CP0000004"])]

    result = join(rows, contaminated_row_ids=set(), beers=beers)

    joined_ids = {j.beer_master_row.canonical_product_id for j in result.joined}
    assert joined_ids == {"CP0000002", "CP0000003", "CP0000004"}
    assert all(j.enrichment_beer.beer_key == "kingfisher_premium" for j in result.joined)


# ---------------------------------------------------------------------------
# Missing beer (unenriched)
# ---------------------------------------------------------------------------


def test_row_with_no_enriching_beer_is_unenriched():
    rows = [_row("CP0000002"), _row("CP0000099")]
    beers = [_beer("kingfisher_premium", ["CP0000002"])]

    result = join(rows, contaminated_row_ids=set(), beers=beers)

    assert len(result.joined) == 1
    assert len(result.unenriched) == 1
    assert result.unenriched[0].canonical_product_id == "CP0000099"


# ---------------------------------------------------------------------------
# Missing candidate
# ---------------------------------------------------------------------------


def test_beer_referencing_nonexistent_row_is_missing_candidate():
    rows = [_row("CP0000002")]
    beers = [_beer("kingfisher_premium", ["CP0000002", "CP0000999"])]

    result = join(rows, contaminated_row_ids=set(), beers=beers)

    assert len(result.joined) == 1
    assert len(result.missing_candidates) == 1
    assert result.missing_candidates[0].canonical_product_id == "CP0000999"
    assert result.missing_candidates[0].beer_key == "kingfisher_premium"


# ---------------------------------------------------------------------------
# Orphan SKU
# ---------------------------------------------------------------------------


def test_beer_referencing_a_contaminated_row_is_orphan_sku():
    # CP0000001 exists in raw data (was once a real row) but was
    # rejected by the contamination gate before join.py ever saw it —
    # distinct from "never existed at all".
    rows = [_row("CP0000002")]
    beers = [_beer("mistakenly_enriched", ["CP0000002", "CP0000001"])]

    result = join(rows, contaminated_row_ids={"CP0000001"}, beers=beers)

    assert len(result.joined) == 1
    assert len(result.orphan_skus) == 1
    assert result.orphan_skus[0].canonical_product_id == "CP0000001"
    assert result.missing_candidates == []


# ---------------------------------------------------------------------------
# Duplicate ownership
# ---------------------------------------------------------------------------


def test_duplicate_ownership_raises_join_error():
    rows = [_row("CP0000002")]
    beers = [
        _beer("beer_a", ["CP0000002"]),
        _beer("beer_b", ["CP0000002"]),
    ]

    with pytest.raises(JoinError):
        join(rows, contaminated_row_ids=set(), beers=beers)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_output_is_deterministic_across_calls():
    rows = [_row("CP0000099"), _row("CP0000002"), _row("CP0000050")]
    beers = [_beer("beer_a", ["CP0000099"]), _beer("beer_b", ["CP0000002"])]

    first = join(rows, contaminated_row_ids=set(), beers=beers)
    second = join(rows, contaminated_row_ids=set(), beers=beers)
    assert first == second


def test_joined_output_is_sorted_by_canonical_product_id():
    rows = [_row("CP0000099"), _row("CP0000002")]
    beers = [_beer("beer_a", ["CP0000099"]), _beer("beer_b", ["CP0000002"])]

    result = join(rows, contaminated_row_ids=set(), beers=beers)

    assert [j.beer_master_row.canonical_product_id for j in result.joined] == ["CP0000002", "CP0000099"]
