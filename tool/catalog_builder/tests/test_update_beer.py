from datetime import date
from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.create_beer import create_beer
from tool.catalog_builder.models import AttributionBlock
from tool.catalog_builder.update_beer import UpdateBeerError, update_beer

_ABV = AttributionBlock(
    value=4.6,
    source_type="manufacturer",
    source_name="Tuborg official brand site",
    observed_at=date(2026, 8, 13),
    observed_by="founder",
)
_CALORIES = AttributionBlock(
    value=37,
    source_type="manufacturer",
    source_name="Tuborg official brand site",
    observed_at=date(2026, 8, 13),
    observed_by="founder",
)


def _write_candidate(path: Path, canonical_product_id: str) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "canonical_product_id": canonical_product_id,
                "item_name_raw": "X",
                "display_name": "X",
                "suggested_beer_key": None,
                "name": None,
                "brewery": None,
                "style": None,
                "abv": None,
                "is_craft": None,
                "images": [],
            }
        ),
        encoding="utf-8",
    )
    return path


def _create(tmp_path: Path, beer_key: str = "tuborg_green") -> Path:
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir(exist_ok=True)
    beers_dir = tmp_path / "beers"
    candidate = _write_candidate(candidates_dir / "CP0000059.yaml", "CP0000059")
    create_beer(
        beer_key=beer_key,
        candidate_paths=[candidate],
        beers_dir=beers_dir,
        name="Tuborg Green Beer",
        brewery="Carlsberg India",
        style="lager",
        abv=_ABV,
        calories_per_100ml=None,
    )
    return beers_dir


def test_update_adds_calories_leaving_everything_else_unchanged(tmp_path: Path):
    beers_dir = _create(tmp_path)
    written = update_beer(beer_key="tuborg_green", beers_dir=beers_dir, calories_per_100ml=_CALORIES)

    raw = yaml.safe_load(written.read_text())
    assert raw["calories_per_100ml"]["value"] == 37
    assert raw["abv"]["value"] == 4.6  # untouched
    assert raw["name"] == "Tuborg Green Beer"
    assert raw["canonical_product_ids"] == ["CP0000059"]


def test_update_missing_file_is_rejected(tmp_path: Path):
    with pytest.raises(UpdateBeerError):
        update_beer(beer_key="does_not_exist", beers_dir=tmp_path / "beers", calories_per_100ml=_CALORIES)


def test_update_with_no_fields_is_rejected(tmp_path: Path):
    beers_dir = _create(tmp_path)
    with pytest.raises(UpdateBeerError):
        update_beer(beer_key="tuborg_green", beers_dir=beers_dir)


def test_update_preserves_unknown_field_it_did_not_touch(tmp_path: Path):
    beers_dir = _create(tmp_path)
    written = update_beer(beer_key="tuborg_green", beers_dir=beers_dir, abv=_ABV)
    raw = yaml.safe_load(written.read_text())
    assert raw["abv"]["value"] == 4.6
    assert raw["calories_per_100ml"] == "unknown"  # left untouched, still unknown


def test_update_can_add_a_new_sibling_candidate(tmp_path: Path):
    beers_dir = _create(tmp_path)
    candidates_dir = tmp_path / "candidates"
    sibling = _write_candidate(candidates_dir / "CP0000732.yaml", "CP0000732")

    written = update_beer(beer_key="tuborg_green", beers_dir=beers_dir, add_candidate_paths=[sibling])

    raw = yaml.safe_load(written.read_text())
    assert raw["canonical_product_ids"] == ["CP0000059", "CP0000732"]


def test_update_refuses_a_candidate_already_claimed_by_another_beer(tmp_path: Path):
    beers_dir = _create(tmp_path)
    candidates_dir = tmp_path / "candidates"
    c2 = _write_candidate(candidates_dir / "CP0000060.yaml", "CP0000060")
    create_beer(
        beer_key="other_beer",
        candidate_paths=[c2],
        beers_dir=beers_dir,
        name="Other",
        brewery="Y",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )

    with pytest.raises(UpdateBeerError):
        update_beer(beer_key="tuborg_green", beers_dir=beers_dir, add_candidate_paths=[c2])


def test_update_refuses_a_candidate_already_on_this_beer(tmp_path: Path):
    beers_dir = _create(tmp_path)
    candidates_dir = tmp_path / "candidates"
    same = _write_candidate(candidates_dir / "CP0000059.yaml", "CP0000059")

    with pytest.raises(UpdateBeerError):
        update_beer(beer_key="tuborg_green", beers_dir=beers_dir, add_candidate_paths=[same])


def test_update_refuses_when_existing_file_has_sku_overrides(tmp_path: Path):
    beers_dir = _create(tmp_path)
    beer_path = beers_dir / "tuborg_green.yaml"
    raw = yaml.safe_load(beer_path.read_text())
    raw["skus"] = {
        "CP0000059": {
            "value": 5.0,
            "source_type": "manufacturer",
            "source_name": "X",
            "observed_at": "2026-08-13",
            "observed_by": "founder",
        }
    }
    beer_path.write_text(yaml.safe_dump(raw), encoding="utf-8")

    with pytest.raises(UpdateBeerError):
        update_beer(beer_key="tuborg_green", beers_dir=beers_dir, calories_per_100ml=_CALORIES)


# ---------------------------------------------------------------------------
# CLI -- --observed-at validation
# (regression: a malformed date used to raise a raw, uncaught ValueError;
# update_beer.py's main() already wrapped this correctly, this locks it in)
# ---------------------------------------------------------------------------


def test_update_beer_cli_reports_clean_error_for_malformed_observed_at(tmp_path: Path, monkeypatch):
    import sys

    from tool.catalog_builder import update_beer as update_beer_module

    beers_dir = _create(tmp_path)

    argv = [
        "update_beer.py",
        "--beer-key",
        "tuborg_green",
        "--calories-per-100ml",
        "37",
        "--calories-per-100ml-source-type",
        "manufacturer",
        "--calories-per-100ml-source-name",
        "X",
        "--observed-at",
        "2026-02-30",
        "--beers-dir",
        str(beers_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as exc_info:
        update_beer_module.main()

    assert "YYYY-MM-DD" in str(exc_info.value)
    # The existing file must be untouched -- calories still unknown.
    raw = yaml.safe_load((beers_dir / "tuborg_green.yaml").read_text())
    assert raw["calories_per_100ml"] == "unknown"
