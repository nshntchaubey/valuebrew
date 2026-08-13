from datetime import date

import pytest

from tool.catalog_builder.create_beer import CreateBeerError, _parse_attribution


def test_none_value_yields_none():
    assert _parse_attribution(None, None, None, "2026-08-13", "founder", field_name="abv") is None


def test_value_with_source_yields_attribution_block():
    block = _parse_attribution(4.8, "manufacturer", "Official page", "2026-08-13", "founder", field_name="abv")
    assert block.value == 4.8
    assert block.source_type == "manufacturer"
    assert block.source_name == "Official page"
    assert block.observed_at == date(2026, 8, 13)
    assert block.observed_by == "founder"


def test_value_without_source_type_raises():
    with pytest.raises(CreateBeerError):
        _parse_attribution(4.8, None, "Official page", "2026-08-13", "founder", field_name="abv")


def test_value_without_source_name_raises():
    with pytest.raises(CreateBeerError):
        _parse_attribution(4.8, "manufacturer", None, "2026-08-13", "founder", field_name="abv")
