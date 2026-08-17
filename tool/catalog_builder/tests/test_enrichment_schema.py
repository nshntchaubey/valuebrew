import pytest

from tool.catalog_builder.enrichment_schema import (
    EnrichmentSchemaError,
    validate_beer_entry,
    validate_rejected_evidence_entry,
    validate_rejected_evidence_yaml,
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


# ---------------------------------------------------------------------------
# validate_rejected_evidence_entry / validate_rejected_evidence_yaml
# ---------------------------------------------------------------------------

_BEER_KEYS = {"kingfisher_premium"}
_BREWERY_NAMES = {"United Breweries"}

_VALID_REJECTED_EVIDENCE = {
    "subject_type": "beer",
    "subject_key": "kingfisher_premium",
    "field": "abv",
    "value_found": "5.2",
    "source_type": "manual_observation",
    "source_name": "Madhuloka product listing, 21 Aug 2026",
    "reason_type": "wrong_variant",
    "reason_detail": "Listing's ABV is for the Strong variant, not this SKU.",
    "observed_at": "2026-08-17",
    "observed_by": "founder",
}


def _rejected_evidence(**overrides):
    return dict(_VALID_REJECTED_EVIDENCE, **overrides)


def test_valid_rejected_evidence_entry_parses():
    entry = validate_rejected_evidence_entry(
        _VALID_REJECTED_EVIDENCE, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES
    )
    assert entry.subject_type == "beer"
    assert entry.subject_key == "kingfisher_premium"
    assert entry.field == "abv"
    assert entry.value_found == "5.2"
    assert entry.source_type == "manual_observation"
    assert entry.reason_type == "wrong_variant"
    assert entry.recheck_after is None


def test_recheck_after_is_captured_when_present():
    raw = _rejected_evidence(recheck_after="2027-01-01")
    entry = validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)
    from datetime import date

    assert entry.recheck_after == date(2027, 1, 1)


def test_brewery_subject_resolves_against_brewery_names():
    raw = _rejected_evidence(subject_type="brewery", subject_key="United Breweries", field="brewery")
    entry = validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)
    assert entry.subject_type == "brewery"
    assert entry.subject_key == "United Breweries"


def test_not_a_mapping_raises():
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(["not", "a", "dict"], beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_missing_required_key_raises():
    raw = {k: v for k, v in _VALID_REJECTED_EVIDENCE.items() if k != "reason_detail"}
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_unsupported_extra_key_raises():
    raw = _rejected_evidence(extra_field="not allowed")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_invalid_subject_type_raises():
    raw = _rejected_evidence(subject_type="sku")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_dangling_beer_subject_key_raises():
    raw = _rejected_evidence(subject_key="not_a_real_beer_key")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_dangling_brewery_subject_key_raises():
    raw = _rejected_evidence(subject_type="brewery", subject_key="Not A Real Brewery", field="brewery")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_invalid_source_type_raises():
    raw = _rejected_evidence(source_type="retailer_listing")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_invalid_reason_type_raises():
    raw = _rejected_evidence(reason_type="not_a_real_reason")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_every_approved_reason_type_is_accepted():
    for reason_type in (
        "wrong_variant",
        "wrong_product_line",
        "access_blocked",
        "imprecise_value",
        "incompatible_unit",
        "conflicting_source_subordinate",
    ):
        raw = _rejected_evidence(reason_type=reason_type)
        entry = validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)
        assert entry.reason_type == reason_type


# --- access_blocked's optional value_found (RC7.10/RC7.11) ---


def test_access_blocked_succeeds_without_value_found():
    raw = {k: v for k, v in _VALID_REJECTED_EVIDENCE.items() if k != "value_found"}
    raw["reason_type"] = "access_blocked"
    entry = validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)
    assert entry.reason_type == "access_blocked"
    assert entry.value_found is None


def test_access_blocked_rejects_an_explicitly_empty_value_found():
    raw = _rejected_evidence(reason_type="access_blocked", value_found="")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_access_blocked_still_accepts_a_real_value_found():
    raw = _rejected_evidence(reason_type="access_blocked", value_found="partial figure glimpsed before the page died")
    entry = validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)
    assert entry.value_found == "partial figure glimpsed before the page died"


@pytest.mark.parametrize(
    "reason_type",
    [
        "wrong_variant",
        "wrong_product_line",
        "imprecise_value",
        "incompatible_unit",
        "conflicting_source_subordinate",
    ],
)
def test_every_other_reason_type_still_requires_value_found(reason_type):
    raw = {k: v for k, v in _VALID_REJECTED_EVIDENCE.items() if k != "value_found"}
    raw["reason_type"] = reason_type
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_unparseable_observed_at_raises():
    raw = _rejected_evidence(observed_at="17 Aug 2026")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_unparseable_recheck_after_raises():
    raw = _rejected_evidence(recheck_after="not-a-date")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_empty_string_field_raises():
    raw = _rejected_evidence(reason_detail="")
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_entry(raw, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_empty_rejected_evidence_yaml_list_is_valid():
    entries = validate_rejected_evidence_yaml([], beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)
    assert entries == []


def test_rejected_evidence_yaml_must_be_a_list():
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_yaml({"not": "a list"}, beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES)


def test_valid_rejected_evidence_yaml_list_parses():
    entries = validate_rejected_evidence_yaml(
        [_VALID_REJECTED_EVIDENCE], beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES
    )
    assert len(entries) == 1
    assert entries[0].subject_key == "kingfisher_premium"


def test_duplicate_rejected_evidence_entry_raises():
    with pytest.raises(EnrichmentSchemaError):
        validate_rejected_evidence_yaml(
            [_VALID_REJECTED_EVIDENCE, dict(_VALID_REJECTED_EVIDENCE)],
            beer_keys=_BEER_KEYS,
            brewery_names=_BREWERY_NAMES,
        )


def test_same_subject_and_field_different_reason_is_not_a_duplicate():
    # A second, independent source rejected for a different reason is new
    # information, not a duplicate — see _rejected_evidence_identity's own
    # docstring for why the identity tuple is this narrow.
    second = _rejected_evidence(source_name="A different source", reason_type="imprecise_value")
    entries = validate_rejected_evidence_yaml(
        [_VALID_REJECTED_EVIDENCE, second], beer_keys=_BEER_KEYS, brewery_names=_BREWERY_NAMES
    )
    assert len(entries) == 2


def test_a_bad_entry_within_the_list_raises_with_its_index():
    with pytest.raises(EnrichmentSchemaError, match="entry #1"):
        validate_rejected_evidence_yaml(
            [_VALID_REJECTED_EVIDENCE, _rejected_evidence(reason_type="bogus")],
            beer_keys=_BEER_KEYS,
            brewery_names=_BREWERY_NAMES,
        )
