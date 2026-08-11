from decimal import Decimal

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
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
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


def test_matching_key_fields_round_trip_including_null_pack_size(tmp_path):
    path = tmp_path / "item_code_canonical_map.csv"
    null_key_row = CanonicalMapRow(
        ksbcl_item_code="9999",
        canonical_product_id="CP0000009",
        supplier_name="X",
        supplier_code="0999",
        normalized_name_key="some unresolved beer",
        pack_size_ml=None,
        pack_count=None,
        container_type="unknown",
        match_confidence="unreviewed",
        matched_rule="new_canonical",
        item_status="LIVE",
        first_seen_run_month="2026-06",
        last_seen_run_month="2026-06",
    )
    write_csv(path, CANONICAL_MAP_FIELDS, [_row("1001").to_csv_row(), null_key_row.to_csv_row()])

    loaded = load_canonical_map(path)

    assert loaded["1001"].normalized_name_key == "kingfisher strong beer 650ml"
    assert loaded["1001"].pack_size_ml == Decimal("650")
    assert loaded["1001"].pack_count is None
    assert loaded["1001"].container_type == "bottle"
    assert loaded["9999"].pack_size_ml is None  # null round-trips as null, not "0" or ""


def test_load_canonical_map_raises_on_pre_migration_schema(tmp_path):
    path = tmp_path / "item_code_canonical_map.csv"
    # The old, 9-column schema, missing the four matching-key fields —
    # simulates a file that predates the backfill migration.
    old_fields = [
        "ksbcl_item_code", "canonical_product_id", "supplier_name", "supplier_code",
        "match_confidence", "matched_rule", "item_status",
        "first_seen_run_month", "last_seen_run_month",
    ]
    write_csv(path, old_fields, [{
        "ksbcl_item_code": "1001", "canonical_product_id": "CP0000001",
        "supplier_name": "United Breweries", "supplier_code": "0210",
        "match_confidence": "unreviewed", "matched_rule": "new_canonical",
        "item_status": "LIVE", "first_seen_run_month": "2026-06", "last_seen_run_month": "2026-06",
    }])

    with pytest.raises(CanonicalMapCorruptionError, match="pre-migration"):
        load_canonical_map(path)
