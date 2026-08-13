from datetime import date
from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.create_beer import CreateBeerError, _parse_attribution, create_beer, render_beer_yaml
from tool.catalog_builder.enrichment_schema import validate_beer_entry
from tool.catalog_builder.models import AttributionBlock

_ABV = AttributionBlock(
    value=4.8,
    source_type="manufacturer",
    source_name="United Breweries official product page",
    observed_at=date(2026, 8, 13),
    observed_by="founder",
)


def _write_candidate(path: Path, canonical_product_id: str, item_name_raw: str = "X") -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "canonical_product_id": canonical_product_id,
                "item_name_raw": item_name_raw,
                "display_name": item_name_raw,
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


# ---------------------------------------------------------------------------
# render_beer_yaml
# ---------------------------------------------------------------------------


def test_rendered_yaml_round_trips_through_validate_beer_entry():
    content = render_beer_yaml(
        beer_key="kingfisher_premium",
        canonical_product_ids=["CP0000002"],
        name="Kingfisher Premium",
        brewery="United Breweries",
        style="lager",
        abv=_ABV,
        calories_per_100ml=_ABV,
        is_craft=False,
        images=[],
    )
    raw = yaml.safe_load(content)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="kingfisher_premium", style_keys={"lager"})
    assert reason_code is None
    assert beer.canonical_product_ids == ["CP0000002"]
    assert beer.abv.value == 4.8
    assert beer.calories_per_100ml.value == 4.8


def test_unknown_style_abv_and_calories_render_as_literal_unknown():
    content = render_beer_yaml(
        beer_key="mystery_beer",
        canonical_product_ids=["CP0000099"],
        name="Mystery Beer",
        brewery="Some Brewery",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )
    raw = yaml.safe_load(content)
    assert raw["style"] == "unknown"
    assert raw["abv"] == "unknown"
    assert raw["calories_per_100ml"] == "unknown"
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="mystery_beer", style_keys=set())
    assert reason_code is None
    assert beer.style is None
    assert beer.abv is None
    assert beer.calories_per_100ml is None


def test_special_characters_in_name_round_trip():
    content = render_beer_yaml(
        beer_key="special_beer",
        canonical_product_ids=["CP0000001"],
        name='Beer "Special": Edition #2',
        brewery="Brewery & Co.",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )
    raw = yaml.safe_load(content)
    assert raw["name"] == 'Beer "Special": Edition #2'
    assert raw["brewery"] == "Brewery & Co."


# ---------------------------------------------------------------------------
# Non-ASCII Unicode round-trip (regression: json.dumps's default
# ensure_ascii=True escaped non-BMP characters as UTF-16 surrogate pairs
# PyYAML never recombined, corrupting the string and later crashing
# catalog_to_json_bytes on UTF-8 encode)
# ---------------------------------------------------------------------------

_KANNADA_NAME = "ಕಿಂಗ್ ಫಿಶರ್ ಪ್ರೀಮಿಯಂ"  # real non-Latin script
_EMOJI_BREWERY = "United Breweries 🍺"  # real non-BMP character
_EMOJI_SOURCE_NAME = "official brand page 🍺, checked 2026-08-13"


def test_non_ascii_name_renders_as_real_utf8_not_surrogate_escapes():
    content = render_beer_yaml(
        beer_key="unicode_beer",
        canonical_product_ids=["CP0000001"],
        name=_KANNADA_NAME,
        brewery=_EMOJI_BREWERY,
        style=None,
        abv=None,
        calories_per_100ml=None,
    )
    # The real characters must appear directly in the file text -- not a
    # \uXXXX (or, worse, an unpaired \uD83C surrogate) escape sequence.
    assert _KANNADA_NAME in content
    assert _EMOJI_BREWERY in content
    assert "\\u" not in content


def test_non_ascii_name_and_brewery_round_trip_through_validate_beer_entry():
    content = render_beer_yaml(
        beer_key="unicode_beer",
        canonical_product_ids=["CP0000001"],
        name=_KANNADA_NAME,
        brewery=_EMOJI_BREWERY,
        style=None,
        abv=None,
        calories_per_100ml=None,
    )
    raw = yaml.safe_load(content)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="unicode_beer", style_keys=set())
    assert reason_code is None
    assert beer.name == _KANNADA_NAME
    assert beer.brewery == _EMOJI_BREWERY
    # A corrupted (lone-surrogate) string cannot be encoded to UTF-8 at
    # all -- this is the exact crash the fix prevents.
    beer.name.encode("utf-8")
    beer.brewery.encode("utf-8")


def test_non_ascii_source_name_in_attribution_block_round_trips():
    abv_with_unicode_source = AttributionBlock(
        value=4.8,
        source_type="manufacturer",
        source_name=_EMOJI_SOURCE_NAME,
        observed_at=date(2026, 8, 13),
        observed_by="founder",
    )
    content = render_beer_yaml(
        beer_key="unicode_source_beer",
        canonical_product_ids=["CP0000001"],
        name="X",
        brewery="Y",
        style=None,
        abv=abv_with_unicode_source,
        calories_per_100ml=None,
    )
    raw = yaml.safe_load(content)
    beer, reason_code, _ = validate_beer_entry(raw, filename_beer_key="unicode_source_beer", style_keys=set())
    assert reason_code is None
    assert beer.abv.source_name == _EMOJI_SOURCE_NAME
    beer.abv.source_name.encode("utf-8")


def test_full_chain_create_beer_to_enrichment_reader_to_catalog_writer(tmp_path: Path):
    """The exact chain the fix is meant to prove: create_beer() writes a
    real file to disk, enrichment_reader.load_beers() reads it back from
    disk (not just yaml.safe_load in memory), and the resulting name
    survives being written into a real catalog.json via
    catalog_writer.catalog_to_json_bytes() -- the one place this whole
    package encodes to UTF-8 and previously crashed."""
    from datetime import datetime

    from tool.catalog_builder.catalog_writer import catalog_to_json_bytes
    from tool.catalog_builder.enrichment_reader import load_beers
    from tool.catalog_builder.models import Beer, Benchmark, Catalog, PackageType, Sku, Style, ValueVerdict

    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    beers_dir = tmp_path / "beers"
    candidate = _write_candidate(candidates_dir / "CP0000001.yaml", "CP0000001")

    written = create_beer(
        beer_key="unicode_beer",
        candidate_paths=[candidate],
        beers_dir=beers_dir,
        name=_KANNADA_NAME,
        brewery=_EMOJI_BREWERY,
        style=None,
        abv=None,
        calories_per_100ml=None,
    )
    assert written == beers_dir / "unicode_beer.yaml"

    # Real disk read, through the real reader -- not yaml.safe_load
    # called directly by the test.
    beers, rejected = load_beers(beers_dir, style_keys=set())
    assert rejected == []
    assert len(beers) == 1
    loaded = beers[0]
    assert loaded.name == _KANNADA_NAME
    assert loaded.brewery == _EMOJI_BREWERY

    # Assemble a minimal but real Catalog carrying the loaded name/brewery
    # straight through, and prove the one real UTF-8 encode step in the
    # whole package (catalog_writer.py) no longer crashes.
    style = Style(id="lager", name="Lager", description="Crisp")
    beer = Beer(id=loaded.beer_key, name=loaded.name, brewery=loaded.brewery, style_id="lager", is_craft=False)
    sku = Sku(
        id="CP0000001",
        beer_id=loaded.beer_key,
        size_ml=330,
        package_type=PackageType.CAN,
        abv=4.8,
        calories=165,
        price=100.0,
        price_last_checked=date(2026, 8, 13),
        price_source="karnataka_excise_mrp_2026",
        cost_per_litre=303.0,
        cost_per_ml_alcohol=6.3,
        value_score=50,
        value_verdict=ValueVerdict.FAIR_VALUE,
    )
    benchmark = Benchmark(style_id="lager", avg_cost_per_ml_alcohol=6.3, p25=6.0, p50=6.3, p75=6.6, sample_size=1)
    catalog = Catalog(
        catalog_version=1,
        generated_at=datetime(2026, 8, 13, 12, 0, 0),
        styles=[style],
        beers=[beer],
        skus=[sku],
        benchmarks=[benchmark],
    )

    catalog_bytes = catalog_to_json_bytes(catalog)  # must not raise UnicodeEncodeError
    decoded = catalog_bytes.decode("utf-8")
    assert loaded.name in decoded
    assert loaded.brewery in decoded
    assert "\\ud8" not in decoded  # no lone surrogate escapes leaked into the JSON either


# ---------------------------------------------------------------------------
# create_beer — single-SKU
# ---------------------------------------------------------------------------


def test_single_sku_beer_created_successfully(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    candidate = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")
    beers_dir = tmp_path / "beers"

    written = create_beer(
        beer_key="kingfisher_premium",
        candidate_paths=[candidate],
        beers_dir=beers_dir,
        name="Kingfisher Premium",
        brewery="United Breweries",
        style="lager",
        abv=_ABV,
        calories_per_100ml=_ABV,
    )

    assert written == beers_dir / "kingfisher_premium.yaml"
    raw = yaml.safe_load(written.read_text())
    assert raw["canonical_product_ids"] == ["CP0000002"]


# ---------------------------------------------------------------------------
# create_beer — multi-SKU
# ---------------------------------------------------------------------------


def test_multi_sku_beer_preserves_every_canonical_product_id(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    c1 = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")
    c2 = _write_candidate(candidates_dir / "CP0000003.yaml", "CP0000003")
    c3 = _write_candidate(candidates_dir / "CP0000004.yaml", "CP0000004")
    beers_dir = tmp_path / "beers"

    written = create_beer(
        beer_key="kingfisher_premium",
        candidate_paths=[c1, c2, c3],
        beers_dir=beers_dir,
        name="Kingfisher Premium",
        brewery="United Breweries",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )

    raw = yaml.safe_load(written.read_text())
    assert raw["canonical_product_ids"] == ["CP0000002", "CP0000003", "CP0000004"]


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


def test_duplicate_canonical_product_id_among_given_candidates_is_rejected(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    # Two different files that (erroneously) declare the same ID.
    c1 = _write_candidate(candidates_dir / "a.yaml", "CP0000002")
    c1_dup = candidates_dir / "a.yaml"
    c2_path = candidates_dir / "b.yaml"
    c2_path.write_text(c1_dup.read_text(), encoding="utf-8")  # same canonical_product_id inside

    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="x",
            candidate_paths=[c1, c2_path],
            beers_dir=tmp_path / "beers",
            name="X",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )


def test_canonical_product_id_already_claimed_by_existing_beer_is_rejected(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    beers_dir = tmp_path / "beers"
    c1 = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")

    create_beer(
        beer_key="first_beer",
        candidate_paths=[c1],
        beers_dir=beers_dir,
        name="First",
        brewery="Y",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )

    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="second_beer",
            candidate_paths=[c1],
            beers_dir=beers_dir,
            name="Second",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )


def test_duplicate_beer_key_never_overwrites_existing_file(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    beers_dir = tmp_path / "beers"
    c1 = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")
    c2 = _write_candidate(candidates_dir / "CP0000003.yaml", "CP0000003")

    create_beer(
        beer_key="shared_key",
        candidate_paths=[c1],
        beers_dir=beers_dir,
        name="A",
        brewery="Y",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )

    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="shared_key",
            candidate_paths=[c2],
            beers_dir=beers_dir,
            name="B",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )

    # The original file must be untouched.
    raw = yaml.safe_load((beers_dir / "shared_key.yaml").read_text())
    assert raw["name"] == "A"


def test_missing_candidate_file_is_rejected(tmp_path: Path):
    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="x",
            candidate_paths=[tmp_path / "does_not_exist.yaml"],
            beers_dir=tmp_path / "beers",
            name="X",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )


def test_empty_candidate_list_is_rejected(tmp_path: Path):
    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="x",
            candidate_paths=[],
            beers_dir=tmp_path / "beers",
            name="X",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )


def test_blank_beer_key_is_rejected(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    c1 = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")
    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="  ",
            candidate_paths=[c1],
            beers_dir=tmp_path / "beers",
            name="X",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )


def test_blank_name_is_rejected(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    c1 = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")
    with pytest.raises(CreateBeerError):
        create_beer(
            beer_key="x",
            candidate_paths=[c1],
            beers_dir=tmp_path / "beers",
            name="",
            brewery="Y",
            style=None,
            abv=None,
            calories_per_100ml=None,
        )


# ---------------------------------------------------------------------------
# _parse_attribution -- --observed-at validation
# (regression: a malformed date used to raise a raw, uncaught ValueError
# with a Python traceback instead of a clean, founder-facing error)
# ---------------------------------------------------------------------------


def test_parse_attribution_accepts_a_valid_date():
    block = _parse_attribution(4.8, "manufacturer", "X", "2026-08-13", "founder", field_name="abv")
    assert block.observed_at == date(2026, 8, 13)


def test_parse_attribution_rejects_dd_mm_yyyy_with_clean_error():
    with pytest.raises(CreateBeerError, match="YYYY-MM-DD"):
        _parse_attribution(4.8, "manufacturer", "X", "13-08-2026", "founder", field_name="abv")


def test_parse_attribution_rejects_a_random_string_with_clean_error():
    with pytest.raises(CreateBeerError, match="YYYY-MM-DD"):
        _parse_attribution(4.8, "manufacturer", "X", "not-a-date", "founder", field_name="abv")


def test_parse_attribution_rejects_an_impossible_date_with_clean_error():
    with pytest.raises(CreateBeerError, match="YYYY-MM-DD"):
        _parse_attribution(4.8, "manufacturer", "X", "2026-02-30", "founder", field_name="abv")


def test_parse_attribution_error_message_names_the_bad_value():
    with pytest.raises(CreateBeerError, match="13-08-2026"):
        _parse_attribution(4.8, "manufacturer", "X", "13-08-2026", "founder", field_name="abv")


def test_create_beer_cli_reports_clean_error_for_malformed_observed_at(tmp_path: Path, monkeypatch):
    """End-to-end through main() itself, not just _parse_attribution --
    proves create_beer.py's own CLI wrapper actually catches this (it
    previously did not: the _parse_attribution calls in main() sat
    outside its try/except CreateBeerError block)."""
    import sys

    from tool.catalog_builder import create_beer as create_beer_module

    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")

    argv = [
        "create_beer.py",
        "--beer-key",
        "x",
        "--candidates",
        "CP0000002",
        "--name",
        "X",
        "--brewery",
        "Y",
        "--abv",
        "4.8",
        "--abv-source-type",
        "manufacturer",
        "--abv-source-name",
        "X",
        "--observed-at",
        "13-08-2026",
        "--candidates-dir",
        str(candidates_dir),
        "--beers-dir",
        str(tmp_path / "beers"),
    ]
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as exc_info:
        create_beer_module.main()

    assert "YYYY-MM-DD" in str(exc_info.value)
    assert not (tmp_path / "beers" / "x.yaml").exists()
