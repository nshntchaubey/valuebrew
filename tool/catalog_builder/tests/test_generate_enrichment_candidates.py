import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import yaml

from tool.catalog_builder.beer_master_reader import EXPECTED_COLUMNS, read_beer_master_csv
from tool.catalog_builder.generate_enrichment_candidates import (
    render_candidate_yaml,
    write_candidates,
)
from tool.catalog_builder.models import BeerMasterRow


def _row(**overrides) -> BeerMasterRow:
    defaults = dict(
        canonical_product_id="CP0000002",
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
        effective_date=date(2025, 5, 16),
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


# ---------------------------------------------------------------------------
# render_candidate_yaml
# ---------------------------------------------------------------------------


def test_rendered_yaml_parses_and_contains_known_fields():
    text = render_candidate_yaml(_row())
    parsed = yaml.safe_load(text)

    assert parsed["canonical_product_id"] == "CP0000002"
    assert parsed["item_name_raw"] == "Kingfisher Premium Lager Beer-CAN 330ML(0202)"
    assert parsed["display_name"] == "Kingfisher Premium Lager Beer-CAN 330ML"


def test_non_ascii_item_name_renders_and_round_trips_as_real_utf8():
    # Regression: json.dumps's default ensure_ascii=True escaped non-BMP
    # characters as UTF-16 surrogate pairs PyYAML never recombined.
    unicode_name = "Kingfisher ಪ್ರೀಮಿಯಂ Lager 🍺 330ML"
    text = render_candidate_yaml(_row(item_name_raw=unicode_name, display_name=unicode_name))

    assert unicode_name in text
    assert "\\u" not in text

    parsed = yaml.safe_load(text)
    assert parsed["item_name_raw"] == unicode_name
    parsed["item_name_raw"].encode("utf-8")  # must not raise UnicodeEncodeError


def test_curated_fields_are_all_explicit_null_or_empty_never_guessed():
    text = render_candidate_yaml(_row())
    parsed = yaml.safe_load(text)

    assert parsed["suggested_beer_key"] is None
    assert parsed["name"] is None
    assert parsed["brewery"] is None
    assert parsed["style"] is None
    assert parsed["abv"] is None
    assert parsed["is_craft"] is None
    assert parsed["images"] == []


def test_no_pricing_fields_are_duplicated_into_the_candidate():
    # Beer Knowledge Base Architecture Part 2: price, size, and container
    # type must never be duplicated into enrichment/.
    text = render_candidate_yaml(_row())
    parsed = yaml.safe_load(text)

    for forbidden_key in ("price", "mrp", "size_ml", "pack_size_ml", "container_type", "declared_price"):
        assert forbidden_key not in parsed


def test_special_characters_in_item_name_round_trip_exactly():
    row = _row(
        item_name_raw='Beer "Special" Edition: 750ML(Batch #2)',
        display_name="Beer Special Edition 750ML",
    )
    text = render_candidate_yaml(row)
    parsed = yaml.safe_load(text)

    assert parsed["item_name_raw"] == 'Beer "Special" Edition: 750ML(Batch #2)'


def test_rendering_is_deterministic_across_calls():
    row = _row()
    assert render_candidate_yaml(row) == render_candidate_yaml(row)


# ---------------------------------------------------------------------------
# write_candidates
# ---------------------------------------------------------------------------


def test_writes_one_file_per_row_named_by_canonical_product_id(tmp_path: Path):
    rows = [_row(canonical_product_id="CP0000002"), _row(canonical_product_id="CP0000003")]
    candidates_dir = tmp_path / "candidates"

    written = write_candidates(rows, candidates_dir)

    assert {p.name for p in written} == {"CP0000002.yaml", "CP0000003.yaml"}
    assert (candidates_dir / "CP0000002.yaml").exists()
    assert (candidates_dir / "CP0000003.yaml").exists()


def test_creates_the_candidates_directory_if_missing(tmp_path: Path):
    candidates_dir = tmp_path / "does" / "not" / "exist" / "yet"
    write_candidates([_row()], candidates_dir)
    assert candidates_dir.is_dir()


def test_rerunning_overwrites_deterministically_without_duplicating(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    row = _row()

    write_candidates([row], candidates_dir)
    first_content = (candidates_dir / "CP0000002.yaml").read_text()

    write_candidates([row], candidates_dir)
    second_content = (candidates_dir / "CP0000002.yaml").read_text()

    assert first_content == second_content
    assert len(list(candidates_dir.glob("*.yaml"))) == 1


def test_written_files_are_sorted_for_a_deterministic_summary(tmp_path: Path):
    rows = [_row(canonical_product_id="CP0000099"), _row(canonical_product_id="CP0000002")]
    written = write_candidates(rows, tmp_path / "candidates")
    assert [p.name for p in written] == ["CP0000002.yaml", "CP0000099.yaml"]


# ---------------------------------------------------------------------------
# End-to-end with the real reader: a row-level-rejected row never gets a
# candidate file.
# ---------------------------------------------------------------------------


def test_row_rejected_by_beer_master_reader_gets_no_candidate_file(tmp_path: Path):
    good_row = {
        "canonical_product_id": "CP0000002",
        "representative_item_code": "2020900211",
        "item_name_raw": "Kingfisher Premium Lager Beer-CAN 330ML(0202)",
        "display_name": "Kingfisher Premium Lager Beer-CAN 330ML",
        "normalized_name_key": "kingfisher premium lager beer-can 330ml",
        "pack_size_ml": "330",
        "pack_count": "",
        "container_type": "can",
        "declared_price": "666.90",
        "landed_cost": "2095.74",
        "ksbcl_selling_price": "2106.22",
        "mrp": "100.00",
        "effective_date": "2025-05-16",
        "status": "LIVE",
        "delisted_run_month": "",
        "classification_confidence": "high",
        "classification_matched_on": "style_keyword:beer",
        "gtin": "",
        "gtin_confidence": "",
        "source_pdf_reference": "x.pdf",
        "first_seen_run_month": "2026-06",
        "last_updated_run_month": "2026-06",
    }
    # Real anomaly (CP0000103): a blank pack_size_ml, row-level rejected.
    bad_row = dict(good_row, canonical_product_id="CP0000103", pack_size_ml="")

    csv_path = tmp_path / "beer_master.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        writer.writerow(good_row)
        writer.writerow(bad_row)

    accepted, rejected = read_beer_master_csv(csv_path)
    written = write_candidates(accepted, tmp_path / "candidates")

    assert len(rejected) == 1 and rejected[0].canonical_product_id == "CP0000103"
    assert [p.name for p in written] == ["CP0000002.yaml"]
