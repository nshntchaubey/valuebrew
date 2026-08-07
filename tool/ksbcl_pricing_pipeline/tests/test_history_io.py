from decimal import Decimal

import pytest

from tool.ksbcl_pricing_pipeline.history_io import (
    PriceHistoryCorruptionError,
    load_price_history,
    most_recent_by_item_code,
    next_history_id,
)
from tool.ksbcl_pricing_pipeline.history_models import PRICE_HISTORY_FIELDS, PriceHistoryRow
from tool.ksbcl_pricing_pipeline.io_writers import write_csv


def _row(history_id, item_code, event_type="NEW_ITEM", observed_run_month="2026-06"):
    return PriceHistoryRow(
        history_id=history_id,
        ksbcl_item_code=item_code,
        event_type=event_type,
        effective_date="2026-06-01",
        effective_date_raw="01-Jun-26",
        declared_price=Decimal("100.00"),
        landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"),
        mrp=Decimal("100.00"),
        previous_declared_price=None,
        previous_landed_cost=None,
        previous_ksbcl_selling_price=None,
        previous_mrp=None,
        previous_effective_date=None,
        observed_run_month=observed_run_month,
        observed_at="2026-08-07T00:00:00Z",
        source_pdf_reference="x.pdf",
    )


def test_load_price_history_returns_empty_list_when_file_absent(tmp_path):
    assert load_price_history(tmp_path / "does_not_exist.csv") == []


def test_load_price_history_round_trips(tmp_path):
    path = tmp_path / "beer_price_history.csv"
    write_csv(path, PRICE_HISTORY_FIELDS, [_row("H00000001", "1001").to_csv_row(), _row("H00000002", "1002").to_csv_row()])

    rows = load_price_history(path)

    assert [r.ksbcl_item_code for r in rows] == ["1001", "1002"]


def test_load_price_history_raises_on_duplicate_history_id(tmp_path):
    path = tmp_path / "beer_price_history.csv"
    write_csv(path, PRICE_HISTORY_FIELDS, [_row("H00000001", "1001").to_csv_row(), _row("H00000001", "1002").to_csv_row()])

    with pytest.raises(PriceHistoryCorruptionError):
        load_price_history(path)


def test_most_recent_by_item_code_takes_last_occurrence():
    rows = [
        _row("H00000001", "1001", observed_run_month="2026-05"),
        _row("H00000002", "1001", observed_run_month="2026-06"),
        _row("H00000003", "1002", observed_run_month="2026-06"),
    ]

    result = most_recent_by_item_code(rows)

    assert result["1001"].history_id == "H00000002"
    assert result["1002"].history_id == "H00000003"


def test_next_history_id_continues_from_max_seen():
    rows = [_row("H00000042", "1001")]
    allocator = next_history_id(rows)
    assert allocator.next() == "H00000043"


def test_next_history_id_starts_at_one_on_bootstrap():
    allocator = next_history_id([])
    assert allocator.next() == "H00000001"
