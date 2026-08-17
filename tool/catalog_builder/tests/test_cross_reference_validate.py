from datetime import date
from decimal import Decimal

import pytest

from tool.catalog_builder.business_rules import AdmittedSku
from tool.catalog_builder.cross_reference_validate import (
    CrossReferenceValidationError,
    validate_cross_references,
)
from tool.catalog_builder.join import JoinedSku
from tool.catalog_builder.models import AttributionBlock, BeerMasterRow, EnrichmentBeer, PackageType

_ABV = AttributionBlock(
    value=4.8,
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
        calories_per_100ml=_ABV,
    )
    defaults.update(overrides)
    return EnrichmentBeer(**defaults)


def _admitted(row: BeerMasterRow, beer: EnrichmentBeer) -> AdmittedSku:
    return AdmittedSku(joined=JoinedSku(row, beer), resolved_abv=_ABV, resolved_calories_per_100ml=_ABV)


# ---------------------------------------------------------------------------
# Passing
# ---------------------------------------------------------------------------


def test_valid_sku_passes():
    admitted = _admitted(_row("CP0000002"), _beer("x", ["CP0000002"]))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert len(result.valid) == 1
    assert result.valid[0].package_type == PackageType.CAN
    assert result.rejected == []


def test_bottle_maps_correctly():
    admitted = _admitted(_row("CP0000002", container_type="bottle"), _beer("x", ["CP0000002"]))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert result.valid[0].package_type == PackageType.BOTTLE


def test_pet_bottle_maps_to_bottle():
    # RC6.1: PackageType.bottle's own shipped doc comment is "A glass or
    # plastic bottle" -- a PET bottle already satisfies that, unlike
    # tetra_pack or unknown, neither of which is a bottle at all.
    admitted = _admitted(_row("CP0000002", container_type="pet_bottle"), _beer("x", ["CP0000002"]))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert result.valid[0].package_type == PackageType.BOTTLE
    assert result.rejected == []


def test_style_none_is_not_a_dangling_reference():
    admitted = _admitted(_row("CP0000002"), _beer("x", ["CP0000002"], style=None))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert len(result.valid) == 1


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


def test_dangling_style_reference_is_rejected():
    admitted = _admitted(_row("CP0000002"), _beer("x", ["CP0000002"], style="nonexistent"))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert result.valid == []
    assert result.rejected[0].reason_code == "dangling_style_reference"


def test_unsupported_container_type_is_rejected():
    admitted = _admitted(_row("CP0000002", container_type="unknown"), _beer("x", ["CP0000002"]))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert result.valid == []
    assert result.rejected[0].reason_code == "unsupported_package_type"


def test_tetra_pack_container_type_is_rejected():
    admitted = _admitted(_row("CP0000002", container_type="tetra_pack"), _beer("x", ["CP0000002"]))
    result = validate_cross_references([admitted], style_keys={"lager"})
    assert result.rejected[0].reason_code == "unsupported_package_type"


# ---------------------------------------------------------------------------
# Structural (raises)
# ---------------------------------------------------------------------------


def test_duplicate_canonical_product_id_raises():
    row = _row("CP0000002")
    beer = _beer("x", ["CP0000002"])
    admitted_1 = _admitted(row, beer)
    admitted_2 = _admitted(row, beer)
    with pytest.raises(CrossReferenceValidationError):
        validate_cross_references([admitted_1, admitted_2], style_keys={"lager"})


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_output_is_deterministic_and_sorted():
    admitted_a = _admitted(_row("CP0000099"), _beer("x", ["CP0000099"]))
    admitted_b = _admitted(_row("CP0000002"), _beer("y", ["CP0000002"]))
    result = validate_cross_references([admitted_a, admitted_b], style_keys={"lager"})
    assert [v.admitted.joined.beer_master_row.canonical_product_id for v in result.valid] == [
        "CP0000002",
        "CP0000099",
    ]
