from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.enrichment_reader import (
    EnrichmentReaderError,
    load_beers,
    load_enrichment_directory,
    load_styles,
)

_STYLES_YAML = [
    {"style_key": "lager", "name": "Lager", "description": "Crisp, mild bitterness"},
]

_VALID_BEER_YAML = {
    "beer_key": "kingfisher_premium",
    "canonical_product_ids": ["CP0000002"],
    "name": "Kingfisher Premium",
    "brewery": "United Breweries",
    "style": "lager",
    "abv": {
        "value": 4.8,
        "source_type": "manufacturer",
        "source_name": "United Breweries official product page",
        "observed_at": "2026-08-10",
        "observed_by": "founder",
    },
    "calories_per_100ml": {
        "value": 165,
        "source_type": "manufacturer",
        "source_name": "United Breweries official product page",
        "observed_at": "2026-08-10",
        "observed_by": "founder",
    },
}


def _write_yaml(path: Path, data) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# load_styles
# ---------------------------------------------------------------------------


def test_load_styles_parses_a_real_file(tmp_path: Path):
    styles_path = tmp_path / "styles.yaml"
    _write_yaml(styles_path, _STYLES_YAML)

    styles = load_styles(styles_path)

    assert len(styles) == 1
    assert styles[0].style_key == "lager"


def test_load_styles_missing_file_raises(tmp_path: Path):
    with pytest.raises(EnrichmentReaderError):
        load_styles(tmp_path / "does_not_exist.yaml")


def test_load_styles_malformed_yaml_raises(tmp_path: Path):
    styles_path = tmp_path / "styles.yaml"
    styles_path.write_text("style_key: [unterminated", encoding="utf-8")

    with pytest.raises(EnrichmentReaderError):
        load_styles(styles_path)


def test_load_styles_schema_violation_raises(tmp_path: Path):
    styles_path = tmp_path / "styles.yaml"
    _write_yaml(styles_path, [{"style_key": "lager", "name": "Lager"}])  # missing description

    with pytest.raises(EnrichmentReaderError):
        load_styles(styles_path)


# ---------------------------------------------------------------------------
# load_beers
# ---------------------------------------------------------------------------


def test_load_beers_parses_a_real_file(tmp_path: Path):
    beers_dir = tmp_path / "beers"
    beers_dir.mkdir()
    _write_yaml(beers_dir / "kingfisher_premium.yaml", _VALID_BEER_YAML)

    beers, rejected = load_beers(beers_dir, style_keys={"lager"})

    assert rejected == []
    assert len(beers) == 1
    assert beers[0].beer_key == "kingfisher_premium"


def test_load_beers_missing_directory_raises(tmp_path: Path):
    with pytest.raises(EnrichmentReaderError):
        load_beers(tmp_path / "beers", style_keys={"lager"})


def test_load_beers_empty_directory_returns_empty_lists(tmp_path: Path):
    beers_dir = tmp_path / "beers"
    beers_dir.mkdir()

    beers, rejected = load_beers(beers_dir, style_keys={"lager"})

    assert beers == []
    assert rejected == []


def test_one_malformed_file_does_not_block_the_others(tmp_path: Path):
    beers_dir = tmp_path / "beers"
    beers_dir.mkdir()
    _write_yaml(beers_dir / "kingfisher_premium.yaml", _VALID_BEER_YAML)
    (beers_dir / "broken.yaml").write_text("beer_key: [unterminated", encoding="utf-8")

    beers, rejected = load_beers(beers_dir, style_keys={"lager"})

    assert len(beers) == 1
    assert beers[0].beer_key == "kingfisher_premium"
    assert len(rejected) == 1
    assert rejected[0].filename == "broken.yaml"
    assert rejected[0].reason_code == "unparseable_yaml"


def test_one_schema_invalid_file_does_not_block_the_others(tmp_path: Path):
    beers_dir = tmp_path / "beers"
    beers_dir.mkdir()
    _write_yaml(beers_dir / "kingfisher_premium.yaml", _VALID_BEER_YAML)
    bad_beer = dict(_VALID_BEER_YAML, beer_key="tuborg_strong", style="not_a_real_style")
    _write_yaml(beers_dir / "tuborg_strong.yaml", bad_beer)

    beers, rejected = load_beers(beers_dir, style_keys={"lager"})

    assert len(beers) == 1
    assert beers[0].beer_key == "kingfisher_premium"
    assert len(rejected) == 1
    assert rejected[0].filename == "tuborg_strong.yaml"
    assert rejected[0].reason_code == "unresolved_style_reference"


# ---------------------------------------------------------------------------
# load_enrichment_directory
# ---------------------------------------------------------------------------


def test_load_enrichment_directory_happy_path(tmp_path: Path):
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    _write_yaml(enrichment_dir / "styles.yaml", _STYLES_YAML)
    _write_yaml(beers_dir / "kingfisher_premium.yaml", _VALID_BEER_YAML)

    result = load_enrichment_directory(enrichment_dir)

    assert len(result.styles) == 1
    assert len(result.beers) == 1
    assert result.rejected_beer_files == []


def test_load_enrichment_directory_beer_referencing_a_real_style(tmp_path: Path):
    # A beer file that references a style defined in this same load's
    # styles.yaml must resolve — confirms load_enrichment_directory wires
    # the two loads together correctly, not just independently.
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    _write_yaml(enrichment_dir / "styles.yaml", [{"style_key": "stout", "name": "Stout", "description": "Dark"}])
    stout_beer = dict(_VALID_BEER_YAML, style="stout")
    _write_yaml(beers_dir / "kingfisher_premium.yaml", stout_beer)

    result = load_enrichment_directory(enrichment_dir)

    assert result.rejected_beer_files == []
    assert result.beers[0].style == "stout"
