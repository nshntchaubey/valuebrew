import pytest

from tool.catalog_builder.enrichment_schema import (
    EnrichmentSchemaError,
    validate_beer_entry,
    validate_styles_yaml,
)

_VALID_ABV = {
    "value": 4.8,
    "source_type": "manufacturer",
    "source_name": "United Breweries official product page",
    "observed_at": "2026-08-10",
    "observed_by": "founder",
}

_VALID_BEER = {
    "beer_key": "kingfisher_premium",
    "canonical_product_ids": ["CP0000002", "CP0000003"],
    "name": "Kingfisher Premium",
    "brewery": "United Breweries",
    "style": "lager",
    "abv": _VALID_ABV,
    "calories_per_100ml": _VALID_ABV,
}


# ---------------------------------------------------------------------------
# validate_styles_yaml
# ---------------------------------------------------------------------------


def test_valid_styles_list_parses():
    raw = [
        {"style_key": "lager", "name": "Lager", "description": "Crisp, mild bitterness"},
        {"style_key": "stout", "name": "Stout", "description": "Dark, roasted"},
    ]
    styles = validate_styles_yaml(raw)
    assert [s.style_key for s in styles] == ["lager", "stout"]
    assert styles[0].name == "Lager"


def test_styles_yaml_must_be_a_list():
    with pytest.raises(EnrichmentSchemaError):
        validate_styles_yaml({"lager": "Lager"})


def test_style_entry_missing_required_key_raises():
    with pytest.raises(EnrichmentSchemaError):
        validate_styles_yaml([{"style_key": "lager", "name": "Lager"}])


def test_style_entry_with_typical_abv_range_raises():
    # Beer Entity Specification 1.0 proposed typical_abv_range; Beer
    # Knowledge Base Architecture Part 4 explicitly declined to adopt it
    # into the frozen v1 contract. A stray extra key must be rejected,
    # not silently accepted.
    with pytest.raises(EnrichmentSchemaError):
        validate_styles_yaml(
            [
                {
                    "style_key": "lager",
                    "name": "Lager",
                    "description": "Crisp",
                    "typical_abv_range": [4.0, 5.5],
                }
            ]
        )


def test_duplicate_style_key_raises():
    with pytest.raises(EnrichmentSchemaError):
        validate_styles_yaml(
            [
                {"style_key": "lager", "name": "Lager", "description": "A"},
                {"style_key": "lager", "name": "Lager 2", "description": "B"},
            ]
        )


def test_style_entry_with_empty_string_field_raises():
    with pytest.raises(EnrichmentSchemaError):
        validate_styles_yaml([{"style_key": "lager", "name": "", "description": "Crisp"}])


def test_style_entry_not_a_mapping_raises():
    with pytest.raises(EnrichmentSchemaError):
        validate_styles_yaml(["lager"])


# ---------------------------------------------------------------------------
# validate_beer_entry
# ---------------------------------------------------------------------------


def test_valid_beer_entry_parses():
    beer, reason_code, detail = validate_beer_entry(
        _VALID_BEER, filename_beer_key="kingfisher_premium", style_keys={"lager"}
    )
    assert reason_code is None and detail is None
    assert beer is not None
    assert beer.beer_key == "kingfisher_premium"
    assert beer.canonical_product_ids == ["CP0000002", "CP0000003"]
    assert beer.style == "lager"
    assert beer.abv is not None
    assert beer.abv.value == 4.8
    assert beer.abv.source_type == "manufacturer"
    assert beer.is_craft is False
    assert beer.images == []
    assert beer.skus == {}


def test_unknown_style_marker_yields_none():
    raw = dict(_VALID_BEER, style="unknown")
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert reason_code is None
    assert beer.style is None


def test_unknown_abv_marker_yields_none():
    raw = dict(_VALID_BEER, abv="unknown")
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert reason_code is None
    assert beer.abv is None


def test_unknown_calories_marker_yields_none():
    raw = dict(_VALID_BEER, calories_per_100ml="unknown")
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert reason_code is None
    assert beer.calories_per_100ml is None


def test_calories_block_missing_a_required_key_is_rejected():
    bad_calories = {k: v for k, v in _VALID_ABV.items() if k != "source_name"}
    raw = dict(_VALID_BEER, calories_per_100ml=bad_calories)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_calories_per_100ml_missing_keys"


def test_calories_not_a_block_or_unknown_is_rejected():
    raw = dict(_VALID_BEER, calories_per_100ml=165)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_calories_per_100ml"


def test_beer_key_mismatch_with_filename_is_rejected():
    beer, reason_code, _ = validate_beer_entry(
        _VALID_BEER, filename_beer_key="wrong_filename", style_keys={"lager"}
    )
    assert beer is None
    assert reason_code == "beer_key_does_not_match_filename"


def test_missing_required_key_is_rejected():
    raw = {k: v for k, v in _VALID_BEER.items() if k != "brewery"}
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "missing_required_keys"


def test_unsupported_extra_key_is_rejected():
    raw = dict(_VALID_BEER, gtin="8905002180007")
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "unsupported_keys"


def test_empty_canonical_product_ids_is_rejected():
    raw = dict(_VALID_BEER, canonical_product_ids=[])
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_canonical_product_ids"


def test_unresolved_style_reference_is_rejected():
    raw = dict(_VALID_BEER, style="nonexistent_style")
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "unresolved_style_reference"


def test_abv_block_missing_a_required_key_is_rejected():
    bad_abv = {k: v for k, v in _VALID_ABV.items() if k != "source_name"}
    raw = dict(_VALID_BEER, abv=bad_abv)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_abv_missing_keys"


def test_abv_block_with_invalid_source_type_is_rejected():
    bad_abv = dict(_VALID_ABV, source_type="retailer_listing")
    raw = dict(_VALID_BEER, abv=bad_abv)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_abv_invalid_source_type"


def test_abv_block_with_unparseable_observed_at_is_rejected():
    bad_abv = dict(_VALID_ABV, observed_at="10 Aug 2026")
    raw = dict(_VALID_BEER, abv=bad_abv)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_abv_unparseable_observed_at"


def test_is_craft_defaults_false_when_omitted():
    beer, _, _ = validate_beer_entry(_VALID_BEER, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer.is_craft is False


def test_is_craft_true_when_set():
    raw = dict(_VALID_BEER, is_craft=True)
    beer, _, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer.is_craft is True


def test_valid_sku_override_is_captured():
    raw = dict(_VALID_BEER, skus={"CP0000003": _VALID_ABV})
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert reason_code is None
    assert "CP0000003" in beer.skus
    assert beer.skus["CP0000003"].value == 4.8


def test_invalid_sku_override_is_rejected():
    raw = dict(_VALID_BEER, skus={"CP0000003": {"value": 5.0}})
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert beer is None
    assert reason_code == "invalid_sku_override_missing_keys"


def test_not_a_mapping_is_rejected():
    beer, reason_code, _ = validate_beer_entry(
        ["not", "a", "dict"], filename_beer_key="kingfisher_premium", style_keys={"lager"}
    )
    assert beer is None
    assert reason_code == "not_a_mapping"
