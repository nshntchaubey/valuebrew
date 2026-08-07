"""Monthly entrypoint — currently wires up Stage 1 (Extraction) only.

Later stages (§2: Beer Identification, Normalization, Canonical Identity
Resolution, Master + History) are not implemented yet and are not
invoked here. This is deliberate — see the implementation brief this
module was built against.

Usage:
    python -m tool.ksbcl_pricing_pipeline.run_pipeline \\
        --input-pdf /path/to/ksbcl_price_list.pdf \\
        --run-month 2026-06
"""

from __future__ import annotations

import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .config import PipelineConfig, parse_config
from .extract import extract_structured_rows
from .io_writers import write_csv, write_json
from .models import PRODUCT_ROW_FIELDS, REJECTED_ROW_FIELDS, RunSummary
from .validate import PipelineValidationError


def _setup_logging(log_level: str, log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ksbcl_pricing_pipeline")
    logger.setLevel(log_level)
    logger.handlers.clear()  # avoid duplicate handlers if run() is called more than once in-process

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def _copy_raw_pdf(input_pdf: Path, output_root: Path, run_month: str, logger: logging.Logger) -> Path:
    """Places the source PDF at pricing_data/raw_pdfs/<run_month>/ per the
    architecture §3 folder structure. Idempotent: copying the same source
    to the same destination twice yields the same file. Done unconditionally
    before extraction runs, on purpose — even a PDF that goes on to fail
    extraction is worth archiving, so an operator debugging a failure has
    the exact input file at hand without needing to track it down again.
    """
    dest_dir = output_root / "raw_pdfs" / run_month
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / input_pdf.name
    shutil.copy2(input_pdf, dest_path)
    logger.info("archived source PDF to %s", dest_path)
    return dest_path


def run(config: PipelineConfig) -> int:
    runs_dir = config.output_root / "runs" / config.run_month
    log_path = runs_dir / "pipeline.log"
    logger = _setup_logging(config.log_level, log_path)

    if not config.input_pdf.exists():
        logger.error("input PDF does not exist: %s", config.input_pdf)
        return 1
    if not config.input_pdf.is_file():
        logger.error("input PDF path is not a file: %s", config.input_pdf)
        return 1

    logger.info("Stage 1 (Extraction) starting: run_month=%s input=%s", config.run_month, config.input_pdf)

    structured_rows_path = runs_dir / "structured_rows.csv"
    rejected_rows_path = runs_dir / "rejected_rows.csv"
    run_summary_path = runs_dir / "run_summary.json"
    started_at = datetime.now(timezone.utc).isoformat()

    # Everything from here on (archiving the PDF, extraction, writing
    # outputs) is covered by one failure boundary: any exception, expected
    # or not, must still leave a clean, informative run_summary.json behind
    # rather than an uncaught traceback and no artifact at all.
    try:
        archived_pdf_path = _copy_raw_pdf(config.input_pdf, config.output_root, config.run_month, logger)

        accepted_rows, rejected_rows, summary = extract_structured_rows(
            pdf_path=config.input_pdf,
            run_month=config.run_month,
            logger=logger,
            mrp_min=config.mrp_min,
            mrp_max=config.mrp_max,
            rejected_row_abort_pct=config.rejected_row_abort_pct,
            row_count_min=config.row_count_min,
            row_count_max=config.row_count_max,
        )

        # All-or-nothing: only reachable on full success (§8.5).
        summary.source_pdf_reference = str(archived_pdf_path)
        write_csv(
            structured_rows_path,
            PRODUCT_ROW_FIELDS,
            (row.to_csv_row() for row in accepted_rows),
        )
        write_csv(
            rejected_rows_path,
            REJECTED_ROW_FIELDS,
            (row.to_csv_row() for row in rejected_rows),
        )
        write_json(run_summary_path, summary.to_json_dict())

        logger.info(
            "Stage 1 complete: %s -> %s (accepted=%s, rejected=%s)",
            config.input_pdf,
            structured_rows_path,
            summary.product_rows_accepted,
            summary.product_rows_rejected,
        )
        return 0

    except PipelineValidationError as exc:
        logger.error("Stage 1 aborted: %s", exc)
        failed_summary = _build_failed_summary(exc.partial_summary, config, started_at, str(exc))
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1

    except Exception:  # noqa: BLE001 - top-level entrypoint: log, don't crash silently
        logger.exception("Stage 1 aborted due to an unexpected error")
        failed_summary = _build_failed_summary(None, config, started_at, "unexpected_error")
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1


def _build_failed_summary(
    partial_summary: Optional[RunSummary],
    config: PipelineConfig,
    started_at: str,
    abort_reason: str,
) -> RunSummary:
    """Build the RunSummary written on failure. Prefers whatever partial
    progress extract_structured_rows had accumulated (page/row counts,
    rejection breakdown) over a blank-slate summary, so a run that fails
    on page 421 of 750 says so, instead of looking identical to a run
    that failed immediately.
    """
    summary = partial_summary if partial_summary is not None else RunSummary(
        run_month=config.run_month,
        source_pdf_reference=str(config.input_pdf),
        started_at=started_at,
    )
    summary.status = "failed"
    summary.abort_reason = abort_reason
    summary.finished_at = datetime.now(timezone.utc).isoformat()
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    config = parse_config(argv)
    return run(config)


if __name__ == "__main__":
    sys.exit(main())
