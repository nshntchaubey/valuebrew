from datetime import date
from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.models import AttributionBlock, EnrichmentBeer
from tool.catalog_builder.photo_checklist import PhotoChecklistError, build_checklist, load_beer

_ABV = AttributionBlock(
    value=4.6, source_type="manufacturer", source_name="X", observed_at=date(2026, 8, 13), observed_by="founder"
)


def _beer(abv=None, calories_per_100ml=None) -> EnrichmentBeer:
    return EnrichmentBeer(
        beer_key="x",
        canonical_product_ids=["CP0000002"],
        name="X",
        brewery="Y",
        style="lager",
        abv=abv,
        calories_per_100ml=calories_per_100ml,
    )


def _labels(checklist):
    return {item.label: item.applicable for item in checklist.items}


def test_nothing_known_every_item_applicable():
    checklist = build_checklist(_beer())
    labels = _labels(checklist)

    assert labels["Front label"] is True
    assert labels["Back label"] is True
    assert labels["Nutrition panel"] is True
    assert labels["ABV declaration"] is True
    assert labels["Barcode (optional)"] is True
    assert labels["Notes"] is True


def test_abv_already_known_skips_abv_declaration_only():
    checklist = build_checklist(_beer(abv=_ABV))
    labels = _labels(checklist)

    assert labels["ABV declaration"] is False
    assert labels["Nutrition panel"] is True
    assert labels["Back label"] is True  # still needed for calories


def test_calories_already_known_skips_nutrition_panel_only():
    checklist = build_checklist(_beer(calories_per_100ml=_ABV))
    labels = _labels(checklist)

    assert labels["Nutrition panel"] is False
    assert labels["ABV declaration"] is True


def test_both_known_skips_back_label_too():
    checklist = build_checklist(_beer(abv=_ABV, calories_per_100ml=_ABV))
    labels = _labels(checklist)

    assert labels["Back label"] is False
    assert labels["Nutrition panel"] is False
    assert labels["ABV declaration"] is False
    # Front label, barcode, and notes are always applicable.
    assert labels["Front label"] is True
    assert labels["Barcode (optional)"] is True
    assert labels["Notes"] is True


def test_checklist_carries_real_identity_fields():
    checklist = build_checklist(_beer())
    assert checklist.beer_key == "x"
    assert checklist.name == "X"
    assert checklist.brewery == "Y"
    assert checklist.canonical_product_ids == ["CP0000002"]


def test_load_beer_missing_file_raises(tmp_path: Path):
    with pytest.raises(PhotoChecklistError):
        load_beer("does_not_exist", tmp_path)


def test_load_beer_parses_a_real_file(tmp_path: Path):
    (tmp_path / "x.yaml").write_text(
        yaml.safe_dump(
            {
                "beer_key": "x",
                "canonical_product_ids": ["CP0000002"],
                "name": "X",
                "brewery": "Y",
                "style": "unknown",
                "abv": "unknown",
                "calories_per_100ml": "unknown",
            }
        ),
        encoding="utf-8",
    )

    beer = load_beer("x", tmp_path)

    assert beer.beer_key == "x"
    assert beer.abv is None
    assert beer.calories_per_100ml is None
