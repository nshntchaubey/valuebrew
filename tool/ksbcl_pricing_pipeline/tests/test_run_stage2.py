import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from tool.ksbcl_pricing_pipeline.io_writers import write_csv
from tool.ksbcl_pricing_pipeline.models import PRODUCT_ROW_FIELDS, ProductRow
from tool.ksbcl_pricing_pipeline.run_stage2 import run
from tool.ksbcl_pricing_pipeline.stage2_config import Stage2Config

VALID_CONFIG_YAML = """\
style_keywords:
  - beer
  - lager
brand_names:
  - Corona
exclusion_terms:
  - whisky
"""


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


def _write_structured_rows(output_root: Path, run_month: str, rows):
    path = output_root / "runs" / run_month / "structured_rows.csv"
    write_csv(path, PRODUCT_ROW_FIELDS, (r.to_csv_row() for r in rows))
    return path


def _config(tmp_path, run_month="2026-06", classification_yaml=VALID_CONFIG_YAML):
    output_root = tmp_path / "pricing_data"
    classification_config_path = tmp_path / "beer_classification.yaml"
    classification_config_path.write_text(classification_yaml, encoding="utf-8")
    return Stage2Config(
        run_month=run_month,
        output_root=output_root,
        classification_config_path=classification_config_path,
        log_level="INFO",
    )


def test_full_run_writes_all_five_artifacts(tmp_path):
    config = _config(tmp_path)
    rows = [
        _row("10000001", "Kingfisher Strong Beer 650ML"),
        _row("10000002", "Some Random Whisky 750ML"),
        # Brand-only match, but this is the bootstrap run: supplier 0210
        # is not yet in the (empty) pre-run known_terms snapshot, so the
        # "unfamiliar supplier" condition correctly demotes it to Low —
        # two-phase execution means it cannot become "familiar" from
        # within this same run (§3.4).
        _row("10000003", "Corona Extra 330ml"),
    ]
    _write_structured_rows(config.output_root, config.run_month, rows)

    exit_code = run(config)
    assert exit_code == 0

    runs_dir = config.output_root / "runs" / config.run_month
    audit_path = runs_dir / "classification_audit.csv"
    new_entities_path = runs_dir / "classification_new_entities.csv"
    summary_path = runs_dir / "classification_run_summary.json"
    known_terms_path = config.output_root / "classification_known_terms.csv"
    review_queue_path = config.output_root / "classification_review_queue.csv"

    for path in (audit_path, new_entities_path, summary_path, known_terms_path, review_queue_path):
        assert path.exists(), path

    with audit_path.open(newline="", encoding="utf-8") as f:
        audit_rows = list(csv.DictReader(f))
    assert len(audit_rows) == 2  # whisky-only row matches nothing -> no audit row
    tiers = {row["item_code"]: row["confidence_tier"] for row in audit_rows}
    assert tiers["10000001"] == "high"
    assert tiers["10000003"] == "low"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "success"
    assert summary["is_bootstrap_run"] is True
    assert summary["counts_by_tier"] == {"high": 1, "medium": 0, "low": 1}

    with known_terms_path.open(newline="", encoding="utf-8") as f:
        known_terms_rows = list(csv.DictReader(f))
    known_keys = {(r["entity_type"], r["value"]) for r in known_terms_rows}
    assert ("style_keyword", "beer") in known_keys
    assert ("brand_name", "Corona") in known_keys
    assert ("supplier_code", "0210") in known_keys


def test_missing_structured_rows_aborts_cleanly(tmp_path):
    config = _config(tmp_path)
    exit_code = run(config)
    assert exit_code == 1


def test_missing_config_writes_failed_summary(tmp_path):
    config = _config(tmp_path)
    config.classification_config_path.unlink()
    _write_structured_rows(config.output_root, config.run_month, [_row("10000001", "Kingfisher Beer 650ML")])

    exit_code = run(config)
    assert exit_code == 1
    summary_path = config.output_root / "runs" / config.run_month / "classification_run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "failed"


def test_zero_high_tier_aborts_via_structural_assert(tmp_path):
    config = _config(tmp_path)
    # Only a brand-only, familiar-supplier row -> medium, never high.
    _write_structured_rows(config.output_root, config.run_month, [_row("10000003", "Corona Extra 330ml")])

    exit_code = run(config)
    assert exit_code == 1
    summary_path = config.output_root / "runs" / config.run_month / "classification_run_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "failed"
    assert "High-tier" in summary["abort_reason"]
    # Failed-run atomicity: no classification_audit.csv left behind.
    assert not (config.output_root / "runs" / config.run_month / "classification_audit.csv").exists()


def test_rerun_same_month_is_idempotent_on_persistent_ledgers(tmp_path):
    config = _config(tmp_path)
    rows = [_row("10000001", "Kingfisher Strong Beer 650ML")]
    _write_structured_rows(config.output_root, config.run_month, rows)

    assert run(config) == 0
    known_terms_path = config.output_root / "classification_known_terms.csv"
    first_content = known_terms_path.read_text(encoding="utf-8")

    assert run(config) == 0
    second_content = known_terms_path.read_text(encoding="utf-8")

    assert first_content == second_content
