from decimal import Decimal

import pytest

from tool.ksbcl_pricing_pipeline.history_models import MASTER_ROW_FIELDS, MasterRow
from tool.ksbcl_pricing_pipeline.io_writers import write_csv
from tool.ksbcl_pricing_pipeline.master_io import MasterCorruptionError, load_master, master_rows_sorted


def _row(cid, item_code="1001"):
    return MasterRow(
        canonical_product_id=cid,
        representative_item_code=item_code,
        item_name_raw="Kingfisher Strong Beer 650ML",
        display_name="Kingfisher Strong Beer 650ML",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        declared_price=Decimal("100.00"),
        landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"),
        mrp=Decimal("100.00"),
        effective_date="2026-06-01",
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


def test_load_master_returns_empty_dict_when_file_absent(tmp_path):
    assert load_master(tmp_path / "does_not_exist.csv") == {}


def test_load_master_round_trips(tmp_path):
    path = tmp_path / "beer_master.csv"
    write_csv(path, MASTER_ROW_FIELDS, [_row("CP0000001").to_csv_row(), _row("CP0000002").to_csv_row()])

    result = load_master(path)

    assert set(result.keys()) == {"CP0000001", "CP0000002"}
    assert result["CP0000001"].pack_size_ml == Decimal("650")


def test_load_master_raises_on_duplicate_canonical_product_id(tmp_path):
    path = tmp_path / "beer_master.csv"
    write_csv(path, MASTER_ROW_FIELDS, [_row("CP0000001").to_csv_row(), _row("CP0000001").to_csv_row()])

    with pytest.raises(MasterCorruptionError):
        load_master(path)


def test_master_rows_sorted_is_deterministic():
    mapping = {"CP0000002": _row("CP0000002"), "CP0000001": _row("CP0000001")}
    rows = master_rows_sorted(mapping)
    assert [r.canonical_product_id for r in rows] == ["CP0000001", "CP0000002"]
