from decimal import Decimal

from tool.ksbcl_pricing_pipeline.normalize import NORMALIZATION_RULE_VERSION, normalize_row
from tool.ksbcl_pricing_pipeline.normalize_models import NormalizeRunSummary


def test_normalize_row_confirmed_real_example():
    row, malformed = normalize_row("2026-06", "2600950111", "Original Bira 91 White Beer 650ML(0260)", "0260")
    assert row.run_month == "2026-06"
    assert row.item_code == "2600950111"
    assert row.display_name == "Original Bira 91 White Beer 650ML"
    assert row.normalized_name_key == "original bira 91 white beer 650ml"
    assert row.pack_size_ml == Decimal("650")
    assert row.pack_count is None
    assert row.container_type == "unknown"
    assert row.normalization_rule_version == NORMALIZATION_RULE_VERSION
    assert malformed is False


def test_normalize_row_to_csv_row_serializes_decimal_as_string():
    row, _ = normalize_row("2026-06", "1", "Haywards 5000 Premium Strong Beer 650ML×12Btls", "0217")
    d = row.to_csv_row()
    assert d["pack_size_ml"] == "650"
    assert d["pack_count"] == 12
    assert d["container_type"] == "bottle"


def test_normalize_row_null_pack_size_serializes_as_none():
    row, _ = normalize_row("2026-06", "1", "Some totally unrecognized product name", "0000")
    d = row.to_csv_row()
    assert d["pack_size_ml"] is None


def test_normalize_row_reports_malformed_suffix():
    row, malformed = normalize_row("2026-06", "1", "Some Beer 650ML0364)", "0364")
    assert malformed is True
    assert row.display_name == "Some Beer 650ML"


def test_run_summary_defaults():
    summary = NormalizeRunSummary(run_month="2026-06", started_at="2026-06-01T00:00:00+00:00")
    d = summary.to_json_dict()
    assert d["status"] == "running"
    assert d["total_normalized_rows"] == 0
