import csv
import json
from datetime import date
from decimal import Decimal

from tool.ksbcl_pricing_pipeline.canonical_models import CANONICAL_MAP_FIELDS, CanonicalMapRow
from tool.ksbcl_pricing_pipeline.classification_models import CLASSIFICATION_AUDIT_FIELDS, ClassificationAuditRow
from tool.ksbcl_pricing_pipeline.io_writers import write_csv, write_json
from tool.ksbcl_pricing_pipeline.models import PRODUCT_ROW_FIELDS, ProductRow
from tool.ksbcl_pricing_pipeline.normalize_models import NORMALIZED_ROW_FIELDS, NormalizedRow
from tool.ksbcl_pricing_pipeline.run_stage5 import run
from tool.ksbcl_pricing_pipeline.stage5_config import Stage5Config

RUN_MONTH = "2026-06"
SOURCE_PDF = "pricing_data/raw_pdfs/2026-06/x.pdf"


def _product_row(item_code, effective_date=date(2026, 6, 1)):
    return ProductRow(
        item_code=item_code,
        item_name_raw="Kingfisher Strong Beer 650ML",
        supplier_name="United Breweries",
        supplier_code="0210",
        effective_date_raw=effective_date.isoformat(),
        effective_date=effective_date,
        declared_price_raw="100.00",
        declared_price=Decimal("100.00"),
        landed_cost_raw="100.00",
        landed_cost=Decimal("100.00"),
        ksbcl_selling_price_raw="100.00",
        ksbcl_selling_price=Decimal("100.00"),
        mrp_raw="100.00",
        mrp=Decimal("100.00"),
        source_page=1,
        run_month=RUN_MONTH,
    )


def _normalized_row(item_code):
    return NormalizedRow(
        run_month=RUN_MONTH,
        item_code=item_code,
        display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        normalization_rule_version="v1",
    )


def _audit_row(item_code):
    return ClassificationAuditRow(
        run_month=RUN_MONTH,
        item_code=item_code,
        confidence_tier="high",
        included=True,
        matched_signal_type="style_keyword",
        matched_term="beer",
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=False,
        classification_config_version="abc123",
    )


def _map_row(item_code, cid):
    return CanonicalMapRow(
        ksbcl_item_code=item_code,
        canonical_product_id=cid,
        supplier_name="United Breweries",
        supplier_code="0210",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        match_confidence="unreviewed",
        matched_rule="new_canonical",
        item_status="LIVE",
        first_seen_run_month=RUN_MONTH,
        last_seen_run_month=RUN_MONTH,
    )


def _write_inputs(output_root, run_month, product_rows, audit_rows, normalized_rows, canonical_map_rows):
    runs_dir = output_root / "runs" / run_month
    write_csv(runs_dir / "structured_rows.csv", PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in product_rows))
    write_csv(runs_dir / "classification_audit.csv", CLASSIFICATION_AUDIT_FIELDS, (r.to_csv_row() for r in audit_rows))
    write_csv(runs_dir / "normalized_rows.csv", NORMALIZED_ROW_FIELDS, (r.to_csv_row() for r in normalized_rows))
    write_json(runs_dir / "run_summary.json", {"source_pdf_reference": SOURCE_PDF})
    write_csv(output_root / "item_code_canonical_map.csv", CANONICAL_MAP_FIELDS, (r.to_csv_row() for r in canonical_map_rows))


def _config(tmp_path, run_month=RUN_MONTH):
    return Stage5Config(run_month=run_month, output_root=tmp_path / "pricing_data", log_level="INFO")


def test_full_bootstrap_run_writes_master_and_history(tmp_path):
    config = _config(tmp_path)
    _write_inputs(
        config.output_root, config.run_month,
        [_product_row("1001")], [_audit_row("1001")], [_normalized_row("1001")],
        [_map_row("1001", "CP0000001")],
    )

    assert run(config) == 0

    master_path = config.output_root / "beer_master.csv"
    history_path = config.output_root / "beer_price_history.csv"
    assert master_path.exists()
    assert history_path.exists()

    with master_path.open(newline="", encoding="utf-8") as f:
        master_rows = list(csv.DictReader(f))
    assert len(master_rows) == 1
    assert master_rows[0]["canonical_product_id"] == "CP0000001"
    assert master_rows[0]["status"] == "LIVE"

    with history_path.open(newline="", encoding="utf-8") as f:
        history_rows = list(csv.DictReader(f))
    assert len(history_rows) == 1
    assert history_rows[0]["event_type"] == "INITIAL_BACKFILL"

    archive_path = config.output_root / "archive" / f"beer_master_{RUN_MONTH}.csv"
    assert archive_path.exists()

    summary = json.loads((config.output_root / "runs" / RUN_MONTH / "master_history_run_summary.json").read_text())
    assert summary["status"] == "success"


def test_second_run_appends_history_and_updates_master_in_place(tmp_path):
    # Same effective_date both months -> genuinely unchanged (§5.2); a
    # different effective_date each month would itself be a PRICE_CHANGE
    # event even with identical prices, per master's own literal rule.
    same_date = date(2026, 6, 1)
    config = _config(tmp_path, run_month="2026-06")
    _write_inputs(
        config.output_root, "2026-06",
        [_product_row("1001", effective_date=same_date)], [_audit_row("1001")],
        [_normalized_row("1001")], [_map_row("1001", "CP0000001")],
    )
    assert run(config) == 0

    config_next = _config(tmp_path, run_month="2026-07")
    _write_inputs(
        config.output_root, "2026-07",
        [_product_row("1001", effective_date=same_date)], [_audit_row("1001")],
        [_normalized_row("1001")], [_map_row("1001", "CP0000001")],
    )
    assert run(config_next) == 0

    with (config.output_root / "beer_master.csv").open(newline="", encoding="utf-8") as f:
        master_rows = list(csv.DictReader(f))
    assert len(master_rows) == 1  # updated in place, never duplicated
    assert master_rows[0]["last_updated_run_month"] == "2026-07"
    assert master_rows[0]["first_seen_run_month"] == "2026-06"

    with (config.output_root / "beer_price_history.csv").open(newline="", encoding="utf-8") as f:
        history_rows = list(csv.DictReader(f))
    assert len(history_rows) == 1  # unchanged price and date both months -> only the INITIAL_BACKFILL


def test_rerun_same_month_is_byte_identical_determinism(tmp_path):
    config = _config(tmp_path)
    _write_inputs(
        config.output_root, config.run_month,
        [_product_row("1001")], [_audit_row("1001")], [_normalized_row("1001")],
        [_map_row("1001", "CP0000001")],
    )

    assert run(config) == 0
    master_content_1 = (config.output_root / "beer_master.csv").read_text()
    history_content_1 = (config.output_root / "beer_price_history.csv").read_text()

    assert run(config) == 0
    master_content_2 = (config.output_root / "beer_master.csv").read_text()
    history_content_2 = (config.output_root / "beer_price_history.csv").read_text()

    assert master_content_1 == master_content_2
    assert history_content_1 == history_content_2


def test_missing_canonical_map_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    runs_dir = config.output_root / "runs" / config.run_month
    write_csv(runs_dir / "structured_rows.csv", PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in [_product_row("1001")]))
    write_csv(runs_dir / "classification_audit.csv", CLASSIFICATION_AUDIT_FIELDS, (r.to_csv_row() for r in [_audit_row("1001")]))
    write_csv(runs_dir / "normalized_rows.csv", NORMALIZED_ROW_FIELDS, (r.to_csv_row() for r in [_normalized_row("1001")]))
    write_json(runs_dir / "run_summary.json", {"source_pdf_reference": SOURCE_PDF})
    # no item_code_canonical_map.csv written at all

    assert run(config) == 1


def test_missing_structured_rows_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    runs_dir = config.output_root / "runs" / config.run_month
    write_csv(runs_dir / "classification_audit.csv", CLASSIFICATION_AUDIT_FIELDS, (r.to_csv_row() for r in [_audit_row("1")]))
    write_csv(runs_dir / "normalized_rows.csv", NORMALIZED_ROW_FIELDS, (r.to_csv_row() for r in [_normalized_row("1")]))
    write_json(runs_dir / "run_summary.json", {"source_pdf_reference": SOURCE_PDF})
    assert run(config) == 1
