import pytest

from tool.ksbcl_pricing_pipeline.canonical_map_io import (
    CanonicalMapCorruptionError,
    canonical_map_rows_sorted,
    load_canonical_map,
)
from tool.ksbcl_pricing_pipeline.canonical_models import CANONICAL_MAP_FIELDS, CanonicalMapRow
from tool.ksbcl_pricing_pipeline.io_writers import write_csv


def _row(item_code, canonical_product_id="CP0000001"):
    return CanonicalMapRow(
        ksbcl_item_code=item_code,
        canonical_product_id=canonical_product_id,
        supplier_name="United Breweries",
        supplier_code="0210",
        match_confidence="unreviewed",
        matched_rule="new_canonical",
        item_status="LIVE",
        first_seen_run_month="2026-06",
        last_seen_run_month="2026-06",
    )


def test_load_canonical_map_returns_empty_dict_when_file_absent(tmp_path):
    assert load_canonical_map(tmp_path / "does_not_exist.csv") == {}


def test_load_canonical_map_round_trips(tmp_path):
    path = tmp_path / "item_code_canonical_map.csv"
    write_csv(path, CANONICAL_MAP_FIELDS, [_row("1001").to_csv_row(), _row("1002", "CP0000002").to_csv_row()])

    loaded = load_canonical_map(path)

    assert set(loaded.keys()) == {"1001", "1002"}
    assert loaded["1001"].canonical_product_id == "CP0000001"


def test_load_canonical_map_raises_on_duplicate_item_code(tmp_path):
    path = tmp_path / "item_code_canonical_map.csv"
    write_csv(path, CANONICAL_MAP_FIELDS, [_row("1001").to_csv_row(), _row("1001").to_csv_row()])

    with pytest.raises(CanonicalMapCorruptionError):
        load_canonical_map(path)


def test_canonical_map_rows_sorted_is_deterministic_by_item_code():
    mapping = {"1002": _row("1002"), "1001": _row("1001")}
    rows = canonical_map_rows_sorted(mapping)
    assert [r.ksbcl_item_code for r in rows] == ["1001", "1002"]
