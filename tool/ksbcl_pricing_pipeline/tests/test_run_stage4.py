import csv
import json
from datetime import date
from decimal import Decimal

from tool.ksbcl_pricing_pipeline.io_writers import write_csv
from tool.ksbcl_pricing_pipeline.models import PRODUCT_ROW_FIELDS, ProductRow
from tool.ksbcl_pricing_pipeline.normalize_models import NORMALIZED_ROW_FIELDS, NormalizedRow
from tool.ksbcl_pricing_pipeline.run_stage4 import run
from tool.ksbcl_pricing_pipeline.stage4_config import Stage4Config


def _product_row(item_code, supplier_code="0210", mrp="100.00", effective_date=date(2026, 6, 1)):
    return ProductRow(
        item_code=item_code,
        item_name_raw="Kingfisher Strong Beer 650ML",
        supplier_name="United Breweries",
        supplier_code=supplier_code,
        effective_date_raw=effective_date.isoformat(),
        effective_date=effective_date,
        declared_price_raw="100.00",
        declared_price=Decimal("100.00"),
        landed_cost_raw="100.00",
        landed_cost=Decimal("100.00"),
        ksbcl_selling_price_raw="100.00",
        ksbcl_selling_price=Decimal("100.00"),
        mrp_raw=mrp,
        mrp=Decimal(mrp),
        source_page=1,
        run_month="2026-06",
    )


def _normalized_row(item_code):
    return NormalizedRow(
        run_month="2026-06",
        item_code=item_code,
        display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        normalization_rule_version="v1",
    )


def _write_inputs(output_root, run_month, product_rows, normalized_rows):
    runs_dir = output_root / "runs" / run_month
    write_csv(runs_dir / "structured_rows.csv", PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in product_rows))
    write_csv(runs_dir / "normalized_rows.csv", NORMALIZED_ROW_FIELDS, (r.to_csv_row() for r in normalized_rows))


def _config(tmp_path, run_month="2026-06"):
    return Stage4Config(run_month=run_month, output_root=tmp_path / "pricing_data", log_level="INFO")


def test_full_bootstrap_run_writes_canonical_map_and_summary(tmp_path):
    config = _config(tmp_path)
    _write_inputs(
        config.output_root,
        config.run_month,
        [_product_row("1001", "0210"), _product_row("1002", "0217")],
        [_normalized_row("1001"), _normalized_row("1002")],
    )

    assert run(config) == 0

    canonical_map_path = config.output_root / "item_code_canonical_map.csv"
    assert canonical_map_path.exists()
    with canonical_map_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    # Different suppliers, same key -> one canonical product (§6, 2a).
    assert rows[0]["canonical_product_id"] == rows[1]["canonical_product_id"]

    summary_path = config.output_root / "runs" / config.run_month / "canonical_run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "success"
    assert summary["new_canonical_products_created"] == 1
    assert summary["attached_cross_supplier"] == 1


def test_second_run_reads_prior_map_and_updates_in_place(tmp_path):
    config = _config(tmp_path)
    _write_inputs(config.output_root, "2026-06", [_product_row("1001")], [_normalized_row("1001")])
    assert run(config) == 0

    config_next = _config(tmp_path, run_month="2026-07")
    _write_inputs(config.output_root, "2026-07", [_product_row("1001")], [_normalized_row("1001")])
    assert run(config_next) == 0

    canonical_map_path = config.output_root / "item_code_canonical_map.csv"
    with canonical_map_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1  # updated in place, never appended
    assert rows[0]["last_seen_run_month"] == "2026-07"
    assert rows[0]["first_seen_run_month"] == "2026-06"


def test_missing_structured_rows_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    runs_dir = config.output_root / "runs" / config.run_month
    write_csv(runs_dir / "normalized_rows.csv", NORMALIZED_ROW_FIELDS, (r.to_csv_row() for r in [_normalized_row("1")]))
    assert run(config) == 1


def test_missing_normalized_rows_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    runs_dir = config.output_root / "runs" / config.run_month
    write_csv(runs_dir / "structured_rows.csv", PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in [_product_row("1")]))
    assert run(config) == 1


def test_rerun_same_month_is_byte_identical_determinism(tmp_path):
    config = _config(tmp_path)
    _write_inputs(
        config.output_root,
        config.run_month,
        [_product_row("1001", "0210"), _product_row("1002", "0217")],
        [_normalized_row("1001"), _normalized_row("1002")],
    )

    assert run(config) == 0
    canonical_map_path = config.output_root / "item_code_canonical_map.csv"
    first_content = canonical_map_path.read_text(encoding="utf-8")

    assert run(config) == 0
    second_content = canonical_map_path.read_text(encoding="utf-8")

    assert first_content == second_content


def test_rerun_same_month_does_not_lose_review_rows(tmp_path):
    config = _config(tmp_path)
    _write_inputs(
        config.output_root,
        config.run_month,
        [
            _product_row("1001", supplier_code="0217", mrp="155.00", effective_date=date(2025, 8, 25)),
            _product_row("1002", supplier_code="0217", mrp="140.00", effective_date=date(2026, 5, 12)),
        ],
        [_normalized_row("1001"), _normalized_row("1002")],
    )

    assert run(config) == 0
    review_path = config.output_root / "runs" / config.run_month / "canonical_resolution_review.csv"
    with review_path.open(newline="", encoding="utf-8") as f:
        first_review_rows = list(csv.DictReader(f))
    assert len(first_review_rows) == 1  # sanity: a real possible_supersession event happened

    # Rerun the exact same run_month — the scenario that previously
    # silently overwrote canonical_resolution_review.csv with an empty file.
    assert run(config) == 0
    with review_path.open(newline="", encoding="utf-8") as f:
        second_review_rows = list(csv.DictReader(f))

    assert second_review_rows == first_review_rows
