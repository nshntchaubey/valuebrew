"""Stage 3 (Normalization) entrypoint.

A separate, independently-runnable command, mirroring Stage 2's
``run_stage2.py`` pattern exactly. Reads a ``run_month``'s already-
persisted ``structured_rows.csv`` and ``classification_audit.csv`` (both
must exist — no standalone "arbitrary CSV" mode, §2.3/§2.4) and produces
``normalized_rows.csv`` plus a run summary (architecture §3, §7).

Usage:
    python -m tool.ksbcl_pricing_pipeline.run_stage3 --run-month 2026-06
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .classification_audit_reader import read_included_item_codes
from .io_writers import write_csv, write_json
from .normalize_models import NORMALIZED_ROW_FIELDS, NormalizeRunSummary
from .normalize_stage import Stage3ValidationError, run_stage3_normalization
from .stage1_reader import read_structured_rows
from .stage3_config import Stage3Config, parse_config


def _setup_logging(log_level: str, log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ksbcl_pricing_pipeline.stage3")
    logger.setLevel(log_level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # A Stage-3-specific log file, not appended to Stage 1's or Stage 2's
    # own logs — the same reasoning Stage 2's run_stage2.py already gives.
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run(config: Stage3Config) -> int:
    runs_dir = config.output_root / "runs" / config.run_month
    log_path = runs_dir / "normalize_pipeline.log"
    logger = _setup_logging(config.log_level, log_path)

    structured_rows_path = runs_dir / "structured_rows.csv"
    classification_audit_path = runs_dir / "classification_audit.csv"
    normalized_rows_path = runs_dir / "normalized_rows.csv"
    run_summary_path = runs_dir / "normalized_run_summary.json"

    started_at = datetime.now(timezone.utc).isoformat()

    if not structured_rows_path.exists():
        logger.error(
            "no structured_rows.csv at %s — Stage 3 requires a successful Stage 1 run first (§2.3)",
            structured_rows_path,
        )
        return 1
    if not classification_audit_path.exists():
        logger.error(
            "no classification_audit.csv at %s — Stage 3 requires a successful Stage 2 run first (§2.3)",
            classification_audit_path,
        )
        return 1

    logger.info("Stage 3 (Normalization) starting: run_month=%s", config.run_month)

    try:
        product_rows = read_structured_rows(structured_rows_path)
        included_item_codes = read_included_item_codes(classification_audit_path)

        result = run_stage3_normalization(
            product_rows=product_rows,
            included_item_codes=included_item_codes,
            run_month=config.run_month,
            started_at=started_at,
        )

        # All-or-nothing: only reachable on full success (§8.5, applied
        # the same way Stage 1/2 already apply it to themselves).
        result.summary.status = "success"
        result.summary.finished_at = datetime.now(timezone.utc).isoformat()

        write_csv(
            normalized_rows_path,
            NORMALIZED_ROW_FIELDS,
            (row.to_csv_row() for row in result.normalized_rows),
        )
        write_json(run_summary_path, result.summary.to_json_dict())

        logger.info(
            "Stage 3 complete: %s normalized rows (pack_size_ml null=%s, suffix_malformed=%s, "
            "container_type unknown=%s)",
            result.summary.total_normalized_rows,
            result.summary.pack_size_ml_null_count,
            result.summary.suffix_malformed_count,
            result.summary.container_type_unknown_count,
        )
        return 0

    except Stage3ValidationError as exc:
        logger.error("Stage 3 aborted: %s", exc)
        failed_summary = exc.partial_summary
        if failed_summary is None:
            failed_summary = NormalizeRunSummary(run_month=config.run_month, started_at=started_at)
        failed_summary.status = "failed"
        failed_summary.abort_reason = str(exc)
        failed_summary.finished_at = datetime.now(timezone.utc).isoformat()
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1

    except Exception:  # noqa: BLE001 - top-level entrypoint: log, don't crash silently
        logger.exception("Stage 3 aborted due to an unexpected error")
        failed_summary = NormalizeRunSummary(
            run_month=config.run_month,
            started_at=started_at,
            status="failed",
            abort_reason="unexpected_error",
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    config = parse_config(argv)
    return run(config)


if __name__ == "__main__":
    sys.exit(main())
