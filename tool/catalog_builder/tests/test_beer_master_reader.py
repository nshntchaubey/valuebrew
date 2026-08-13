import csv
import io
from pathlib import Path
from typing import Dict, List

import pytest

from tool.catalog_builder.beer_master_reader import (
    EXPECTED_COLUMNS,
    BeerMasterReaderError,
    read_beer_master_csv,
)

_BASE_ROW: Dict[str, str] = {
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
    "source_pdf_reference": "pricing_data/raw_pdfs/2026-06/x.pdf",
    "first_seen_run_month": "2026-06",
    "last_updated_run_month": "2026-06",
}


def _write_csv(path: Path, rows: List[Dict[str, str]], header: List[str] = None) -> None:
    header = header or list(EXPECTED_COLUMNS)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_valid_row_parses_into_beer_master_row(tmp_path: Path):
    csv_path = tmp_path / "beer_master.csv"
    _write_csv(csv_path, [_BASE_ROW])

    accepted, rejected = read_beer_master_csv(csv_path)

    assert rejected == []
    assert len(accepted) == 1
    row = accepted[0]
    assert row.canonical_product_id == "CP0000002"
    assert row.pack_size_ml == 330
    assert row.pack_count is None
    assert str(row.mrp) == "100.00"
    assert row.effective_date.isoformat() == "2025-05-16"
    assert row.delisted_run_month is None
    assert row.gtin is None


def test_pack_count_parses_when_present():
    row = dict(_BASE_ROW, canonical_product_id="CP0000001", pack_count="12")
    accepted, rejected = _parse_single_row(row)
    assert rejected == []
    assert accepted[0].pack_count == 12


def test_missing_required_string_field_is_row_level_rejected():
    row = dict(_BASE_ROW, item_name_raw="")
    accepted, rejected = _parse_single_row(row)
    assert accepted == []
    assert len(rejected) == 1
    assert rejected[0].reason_code == "missing_item_name_raw"
    assert rejected[0].canonical_product_id == "CP0000002"


def test_unparseable_price_is_row_level_rejected():
    row = dict(_BASE_ROW, mrp="not-a-number")
    accepted, rejected = _parse_single_row(row)
    assert accepted == []
    assert rejected[0].reason_code == "unparseable_mrp"


def test_zero_price_is_row_level_rejected():
    row = dict(_BASE_ROW, mrp="0")
    accepted, rejected = _parse_single_row(row)
    assert accepted == []
    assert rejected[0].reason_code == "mrp_not_positive"


def test_negative_price_is_row_level_rejected():
    row = dict(_BASE_ROW, declared_price="-5.00")
    accepted, rejected = _parse_single_row(row)
    assert accepted == []
    assert rejected[0].reason_code == "declared_price_not_positive"


def test_unparseable_effective_date_is_row_level_rejected():
    row = dict(_BASE_ROW, effective_date="16-05-2025")
    accepted, rejected = _parse_single_row(row)
    assert accepted == []
    assert rejected[0].reason_code == "unparseable_effective_date"


def test_unparseable_pack_size_is_row_level_rejected():
    row = dict(_BASE_ROW, pack_size_ml="six-fifty")
    accepted, rejected = _parse_single_row(row)
    assert accepted == []
    assert rejected[0].reason_code == "unparseable_pack_size_ml"


def test_one_bad_row_does_not_exclude_a_good_row(tmp_path: Path):
    good_row = dict(_BASE_ROW, canonical_product_id="CP0000002")
    bad_row = dict(_BASE_ROW, canonical_product_id="CP0000003", mrp="garbage")
    csv_path = tmp_path / "beer_master.csv"
    _write_csv(csv_path, [good_row, bad_row])

    accepted, rejected = read_beer_master_csv(csv_path)

    assert len(accepted) == 1
    assert accepted[0].canonical_product_id == "CP0000002"
    assert len(rejected) == 1
    assert rejected[0].canonical_product_id == "CP0000003"


def test_missing_expected_column_is_structural_and_raises(tmp_path: Path):
    header = [c for c in EXPECTED_COLUMNS if c != "mrp"]
    csv_path = tmp_path / "beer_master.csv"
    _write_csv(csv_path, [{k: v for k, v in _BASE_ROW.items() if k != "mrp"}], header=header)

    with pytest.raises(BeerMasterReaderError):
        read_beer_master_csv(csv_path)


def test_missing_file_raises():
    with pytest.raises(BeerMasterReaderError):
        read_beer_master_csv(Path("/nonexistent/beer_master.csv"))


def test_real_contamination_fixture_rows_parse_cleanly(tmp_path: Path):
    # CP0000001 and CP0000955 are the two confirmed-live contamination
    # rows (Project Brain §11). This reader's job is shape/parseability
    # only — it must accept them exactly like any other row. Rejecting
    # non-beer content is the contamination filter's job (not yet
    # built), never this module's.
    budweiser_whiskey = dict(
        _BASE_ROW,
        canonical_product_id="CP0000001",
        representative_item_code="1390101301",
        item_name_raw="Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls(0139)",
        display_name="Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls",
        normalized_name_key="budweiser magnum double barrel blended american whiskey 750mlx12btls",
        pack_size_ml="750",
        pack_count="12",
        container_type="bottle",
        declared_price="7408.53",
        landed_cost="25948.53",
        ksbcl_selling_price="26078.27",
        mrp="2395.00",
        effective_date="2024-10-05",
        classification_confidence="medium",
        classification_matched_on="brand_name:Budweiser",
    )
    csv_path = tmp_path / "beer_master.csv"
    _write_csv(csv_path, [budweiser_whiskey])

    accepted, rejected = read_beer_master_csv(csv_path)

    assert rejected == []
    assert len(accepted) == 1
    assert accepted[0].canonical_product_id == "CP0000001"
    assert accepted[0].classification_matched_on == "brand_name:Budweiser"


def _parse_single_row(row: Dict[str, str]):
    handle = io.StringIO()
    writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
    writer.writeheader()
    writer.writerow(row)
    handle.seek(0)

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as tmp:
        tmp.write(handle.getvalue())
        tmp_path = Path(tmp.name)
    try:
        return read_beer_master_csv(tmp_path)
    finally:
        tmp_path.unlink()
