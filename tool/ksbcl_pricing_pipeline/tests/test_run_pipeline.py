import json
from pathlib import Path

from tool.ksbcl_pricing_pipeline import run_pipeline as run_pipeline_module
from tool.ksbcl_pricing_pipeline.config import PipelineConfig
from tool.ksbcl_pricing_pipeline.models import RunSummary
from tool.ksbcl_pricing_pipeline.run_pipeline import _build_failed_summary, _setup_logging, run
from tool.ksbcl_pricing_pipeline.validate import PipelineValidationError


# --- _setup_logging: state-leak check -----------------------------------


def test_setup_logging_does_not_duplicate_handlers_across_calls(tmp_path):
    log_file = tmp_path / "pipeline.log"
    logger_1 = _setup_logging("INFO", log_file)
    handler_count_after_first_call = len(logger_1.handlers)

    logger_2 = _setup_logging("INFO", log_file)
    handler_count_after_second_call = len(logger_2.handlers)

    assert logger_1 is logger_2  # logging.getLogger(name) is a singleton
    assert handler_count_after_first_call == handler_count_after_second_call
    assert handler_count_after_second_call == 2  # one console, one file


# --- _build_failed_summary -------------------------------------------------


def _make_config(tmp_path: Path, input_pdf: Path) -> PipelineConfig:
    return PipelineConfig(
        input_pdf=input_pdf,
        run_month="2026-06",
        output_root=tmp_path / "pricing_data",
        rejected_row_abort_pct=2.0,
        mrp_min=None,
        mrp_max=None,
        row_count_min=None,
        row_count_max=None,
        log_level="INFO",
    )


def test_build_failed_summary_reuses_partial_summary_when_available(tmp_path):
    partial = RunSummary(
        run_month="2026-06",
        source_pdf_reference="whatever.pdf",
        started_at="2026-01-01T00:00:00+00:00",
        total_pages=750,
        product_rows_accepted=420,
    )
    config = _make_config(tmp_path, tmp_path / "input.pdf")

    result = _build_failed_summary(partial, config, "2026-01-01T00:00:00+00:00", "boom")

    assert result is partial  # same object, not a fresh blank one
    assert result.status == "failed"
    assert result.abort_reason == "boom"
    assert result.finished_at is not None
    # Progress accumulated before the abort must survive.
    assert result.total_pages == 750
    assert result.product_rows_accepted == 420


def test_build_failed_summary_builds_fresh_summary_when_none_available(tmp_path):
    config = _make_config(tmp_path, tmp_path / "input.pdf")

    result = _build_failed_summary(None, config, "2026-01-01T00:00:00+00:00", "boom")

    assert result.status == "failed"
    assert result.abort_reason == "boom"
    assert result.run_month == "2026-06"
    assert result.total_pages == 0


# --- run(): end-to-end wiring, extraction itself mocked out ----------------


def _write_dummy_pdf(path: Path) -> Path:
    path.write_bytes(b"%PDF-1.4 not a real pdf, just a placeholder for path plumbing\n")
    return path


def test_run_writes_outputs_on_success(tmp_path, monkeypatch):
    from tool.ksbcl_pricing_pipeline.models import ProductRow
    from datetime import date
    from decimal import Decimal

    input_pdf = _write_dummy_pdf(tmp_path / "input.pdf")
    config = _make_config(tmp_path, input_pdf)

    fake_row = ProductRow(
        item_code="10300901",
        item_name_raw="x",
        supplier_name="s",
        supplier_code="0001",
        effective_date_raw="10-Jul-20",
        effective_date=date(2020, 7, 10),
        declared_price_raw="1.00",
        declared_price=Decimal("1.00"),
        landed_cost_raw="1.00",
        landed_cost=Decimal("1.00"),
        ksbcl_selling_price_raw="1.00",
        ksbcl_selling_price=Decimal("1.00"),
        mrp_raw="1.00",
        mrp=Decimal("1.00"),
        source_page=1,
        run_month="2026-06",
    )
    fake_summary = RunSummary(
        run_month="2026-06", source_pdf_reference=str(input_pdf), started_at="x",
        product_rows_accepted=1, status="success",
    )

    monkeypatch.setattr(
        run_pipeline_module,
        "extract_structured_rows",
        lambda **kwargs: ([fake_row], [], fake_summary),
    )

    exit_code = run(config)

    assert exit_code == 0
    runs_dir = config.output_root / "runs" / "2026-06"
    assert (runs_dir / "structured_rows.csv").exists()
    assert (runs_dir / "rejected_rows.csv").exists()
    summary_data = json.loads((runs_dir / "run_summary.json").read_text())
    assert summary_data["status"] == "success"
    # Archived PDF must land where the architecture's folder structure says.
    assert (config.output_root / "raw_pdfs" / "2026-06" / "input.pdf").exists()


def test_run_writes_only_summary_on_validation_failure(tmp_path, monkeypatch):
    input_pdf = _write_dummy_pdf(tmp_path / "input.pdf")
    config = _make_config(tmp_path, input_pdf)

    def _raise(**kwargs):
        exc = PipelineValidationError("page 42: something structurally broke")
        exc.partial_summary = RunSummary(
            run_month="2026-06", source_pdf_reference=str(input_pdf), started_at="x",
            total_pages=100, product_rows_accepted=41,
        )
        raise exc

    monkeypatch.setattr(run_pipeline_module, "extract_structured_rows", _raise)

    exit_code = run(config)

    assert exit_code == 1
    runs_dir = config.output_root / "runs" / "2026-06"
    assert not (runs_dir / "structured_rows.csv").exists()
    assert not (runs_dir / "rejected_rows.csv").exists()
    summary_data = json.loads((runs_dir / "run_summary.json").read_text())
    assert summary_data["status"] == "failed"
    assert "page 42" in summary_data["abort_reason"]
    assert summary_data["total_pages"] == 100
    assert summary_data["product_rows_accepted"] == 41


def test_run_handles_unexpected_exception_without_crashing(tmp_path, monkeypatch):
    input_pdf = _write_dummy_pdf(tmp_path / "input.pdf")
    config = _make_config(tmp_path, input_pdf)

    def _raise(**kwargs):
        raise RuntimeError("totally unexpected")

    monkeypatch.setattr(run_pipeline_module, "extract_structured_rows", _raise)

    exit_code = run(config)

    assert exit_code == 1
    runs_dir = config.output_root / "runs" / "2026-06"
    summary_data = json.loads((runs_dir / "run_summary.json").read_text())
    assert summary_data["status"] == "failed"
    assert summary_data["abort_reason"] == "unexpected_error"


def test_run_returns_error_when_input_pdf_missing(tmp_path):
    config = _make_config(tmp_path, tmp_path / "does_not_exist.pdf")
    assert run(config) == 1
