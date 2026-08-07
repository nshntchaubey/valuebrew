import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from tool.ksbcl_pricing_pipeline.classification_models import CLASSIFICATION_AUDIT_FIELDS, ClassificationAuditRow
from tool.ksbcl_pricing_pipeline.io_writers import write_csv
from tool.ksbcl_pricing_pipeline.models import PRODUCT_ROW_FIELDS, ProductRow
from tool.ksbcl_pricing_pipeline.run_stage3 import run
from tool.ksbcl_pricing_pipeline.stage3_config import Stage3Config


def _row(item_code, item_name_raw, supplier_code="0210"):
    return ProductRow(
        item_code=item_code,
        item_name_raw=item_name_raw,
        supplier_name="United Breweries",
        supplier_code=supplier_code,
        effective_date_raw="10-Jul-26",
        effective_date=date(2026, 7, 10),
        declared_price_raw="100.00",
        declared_price=Decimal("100.00"),
        landed_cost_raw="100.00",
        landed_cost=Decimal("100.00"),
        ksbcl_selling_price_raw="100.00",
        ksbcl_selling_price=Decimal("100.00"),
        mrp_raw="100.00",
        mrp=Decimal("100.00"),
        source_page=1,
        run_month="2026-06",
    )


def _audit_row(item_code, included):
    return ClassificationAuditRow(
        run_month="2026-06",
        item_code=item_code,
        confidence_tier="high" if included else "low",
        included=included,
        matched_signal_type="style_keyword",
        matched_term="beer" if included else None,
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=False,
        classification_config_version="abc123def456",
    )


def _write_inputs(output_root, run_month, structured_rows, audit_rows):
    runs_dir = output_root / "runs" / run_month
    write_csv(runs_dir / "structured_rows.csv", PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in structured_rows))
    write_csv(runs_dir / "classification_audit.csv", CLASSIFICATION_AUDIT_FIELDS, (r.to_csv_row() for r in audit_rows))


def _config(tmp_path, run_month="2026-06"):
    return Stage3Config(run_month=run_month, output_root=tmp_path / "pricing_data", log_level="INFO")


def test_full_run_writes_normalized_rows_and_summary(tmp_path):
    config = _config(tmp_path)
    structured_rows = [
        _row("10000001", "Kingfisher Strong Beer 650ML(0210)"),
        _row("10000002", "Some Excluded Whisky 750ML"),
        _row("10000003", "Haywards 5000 Premium Strong Beer 650ML×12Btls(0217)", "0217"),
    ]
    audit_rows = [_audit_row("10000001", True), _audit_row("10000002", False), _audit_row("10000003", True)]
    _write_inputs(config.output_root, config.run_month, structured_rows, audit_rows)

    exit_code = run(config)
    assert exit_code == 0

    runs_dir = config.output_root / "runs" / config.run_month
    normalized_path = runs_dir / "normalized_rows.csv"
    summary_path = runs_dir / "normalized_run_summary.json"
    assert normalized_path.exists()
    assert summary_path.exists()

    with normalized_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2  # the excluded whisky row never reaches Stage 3
    by_code = {r["item_code"]: r for r in rows}
    assert by_code["10000001"]["display_name"] == "Kingfisher Strong Beer 650ML"
    assert by_code["10000001"]["pack_size_ml"] == "650"
    assert by_code["10000003"]["pack_count"] == "12"
    assert by_code["10000003"]["container_type"] == "bottle"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "success"
    assert summary["total_normalized_rows"] == 2


def test_missing_structured_rows_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    runs_dir = config.output_root / "runs" / config.run_month
    write_csv(
        runs_dir / "classification_audit.csv",
        CLASSIFICATION_AUDIT_FIELDS,
        (r.to_csv_row() for r in [_audit_row("1", True)]),
    )
    assert run(config) == 1


def test_missing_classification_audit_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    runs_dir = config.output_root / "runs" / config.run_month
    write_csv(runs_dir / "structured_rows.csv", PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in [_row("1", "Beer 650ML")]))
    assert run(config) == 1


def test_zero_included_rows_aborts_via_structural_assert(tmp_path):
    config = _config(tmp_path)
    structured_rows = [_row("1", "Some Whisky 750ML")]
    audit_rows = [_audit_row("1", False)]
    _write_inputs(config.output_root, config.run_month, structured_rows, audit_rows)

    exit_code = run(config)
    assert exit_code == 1
    summary_path = config.output_root / "runs" / config.run_month / "normalized_run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "failed"
    assert not (config.output_root / "runs" / config.run_month / "normalized_rows.csv").exists()


def test_rerun_is_byte_identical_determinism(tmp_path):
    config = _config(tmp_path)
    structured_rows = [_row("10000001", "Kingfisher Strong Beer 650ML(0210)")]
    audit_rows = [_audit_row("10000001", True)]
    _write_inputs(config.output_root, config.run_month, structured_rows, audit_rows)

    assert run(config) == 0
    normalized_path = config.output_root / "runs" / config.run_month / "normalized_rows.csv"
    first_content = normalized_path.read_text(encoding="utf-8")

    assert run(config) == 0
    second_content = normalized_path.read_text(encoding="utf-8")

    assert first_content == second_content
