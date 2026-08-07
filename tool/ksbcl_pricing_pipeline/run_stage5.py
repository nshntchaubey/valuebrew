"""Stage 5 (Master + History) entrypoint.

A separate, independently-runnable command, mirroring Stage 4's
``run_stage4.py`` pattern exactly. Reads a ``run_month``'s already-
persisted ``structured_rows.csv``, ``classification_audit.csv``,
``normalized_rows.csv``, ``run_summary.json`` (all must exist) plus the
permanent, current ``item_code_canonical_map.csv`` and Stage 5's own
prior permanent state (``beer_price_history.csv``,
``beer_master.csv``/``beer_master_duty_free.csv``, absent on a
first-ever run — bootstrap, architecture §5.4), and produces the
updated versions of all three plus dated archive snapshots and a run
summary (architecture §2.2, §9).

Usage:
    python -m tool.ksbcl_pricing_pipeline.run_stage5 --run-month 2026-06
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .canonical_map_io import load_canonical_map
from .classification_audit_full_reader import read_classification_audit
from .history_io import (
    PriceHistoryCorruptionError,
    load_price_history,
)
from .history_models import MASTER_ROW_FIELDS, PRICE_HISTORY_FIELDS, Stage5RunSummary
from .io_writers import write_csv, write_json
from .master_io import MasterCorruptionError, load_master, master_rows_sorted
from .normalized_rows_reader import read_normalized_rows
from .run_summary_reader import read_source_pdf_reference
from .stage1_reader import read_structured_rows
from .stage5_config import Stage5Config, parse_config
from .stage5_resolve import Stage5ValidationError, run_stage5


def _setup_logging(log_level: str, log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ksbcl_pricing_pipeline.stage5")
    logger.setLevel(log_level)
    logger.handlers.clear()

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


def run(config: Stage5Config) -> int:
    runs_dir = config.output_root / "runs" / config.run_month
    log_path = runs_dir / "master_history_pipeline.log"
    logger = _setup_logging(config.log_level, log_path)

    structured_rows_path = runs_dir / "structured_rows.csv"
    classification_audit_path = runs_dir / "classification_audit.csv"
    normalized_rows_path = runs_dir / "normalized_rows.csv"
    run_summary_path = runs_dir / "run_summary.json"
    canonical_map_path = config.output_root / "item_code_canonical_map.csv"
    price_history_path = config.output_root / "beer_price_history.csv"
    master_retail_path = config.output_root / "beer_master.csv"
    master_duty_free_path = config.output_root / "beer_master_duty_free.csv"
    archive_retail_path = config.output_root / "archive" / f"beer_master_{config.run_month}.csv"
    archive_duty_free_path = config.output_root / "archive" / f"beer_master_duty_free_{config.run_month}.csv"
    stage5_summary_path = runs_dir / "master_history_run_summary.json"

    started_at = datetime.now(timezone.utc).isoformat()

    for label, path in (
        ("structured_rows.csv", structured_rows_path),
        ("classification_audit.csv", classification_audit_path),
        ("normalized_rows.csv", normalized_rows_path),
        ("run_summary.json", run_summary_path),
    ):
        if not path.exists():
            logger.error("no %s at %s — Stage 5 requires a successful Stage 1-3 run first", label, path)
            return 1

    logger.info("Stage 5 (Master + History) starting: run_month=%s", config.run_month)

    try:
        canonical_map = load_canonical_map(canonical_map_path)
        prior_history_rows = load_price_history(price_history_path)
        prior_master_retail = load_master(master_retail_path)
        prior_master_duty_free = load_master(master_duty_free_path)
    except (PriceHistoryCorruptionError, MasterCorruptionError) as exc:
        logger.error("Stage 5 aborted: %s", exc)
        failed_summary = Stage5RunSummary(
            run_month=config.run_month,
            started_at=started_at,
            status="failed",
            abort_reason=str(exc),
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        write_json(stage5_summary_path, failed_summary.to_json_dict())
        return 1

    try:
        product_rows = read_structured_rows(structured_rows_path)
        classification_audit = read_classification_audit(classification_audit_path)
        normalized_rows_list = read_normalized_rows(normalized_rows_path)
        normalized_rows = {row.item_code: row for row in normalized_rows_list}
        source_pdf_reference = read_source_pdf_reference(run_summary_path)
        observed_at = datetime.now(timezone.utc).isoformat()

        result = run_stage5(
            product_rows=product_rows,
            canonical_map=canonical_map,
            classification_audit=classification_audit,
            normalized_rows=normalized_rows,
            prior_history_rows=prior_history_rows,
            prior_master_retail=prior_master_retail,
            prior_master_duty_free=prior_master_duty_free,
            run_month=config.run_month,
            started_at=started_at,
            observed_at=observed_at,
            source_pdf_reference=source_pdf_reference,
        )

        result.summary.status = "success"
        result.summary.finished_at = datetime.now(timezone.utc).isoformat()

        all_history_rows = prior_history_rows + result.new_history_rows
        write_csv(price_history_path, PRICE_HISTORY_FIELDS, (row.to_csv_row() for row in all_history_rows))

        retail_rows = list(master_rows_sorted(result.master_retail))
        duty_free_rows = list(master_rows_sorted(result.master_duty_free))
        write_csv(master_retail_path, MASTER_ROW_FIELDS, (row.to_csv_row() for row in retail_rows))
        write_csv(master_duty_free_path, MASTER_ROW_FIELDS, (row.to_csv_row() for row in duty_free_rows))
        write_csv(archive_retail_path, MASTER_ROW_FIELDS, (row.to_csv_row() for row in retail_rows))
        write_csv(archive_duty_free_path, MASTER_ROW_FIELDS, (row.to_csv_row() for row in duty_free_rows))

        write_json(stage5_summary_path, result.summary.to_json_dict())

        logger.info(
            "Stage 5 complete: %s new history rows (%s), retail master %s live/%s delisted, "
            "duty-free master %s live/%s delisted",
            result.summary.history_rows_written,
            result.summary.history_event_counts,
            result.summary.master_retail_rows_live,
            result.summary.master_retail_rows_delisted,
            result.summary.master_duty_free_rows_live,
            result.summary.master_duty_free_rows_delisted,
        )
        return 0

    except Stage5ValidationError as exc:
        logger.error("Stage 5 aborted: %s", exc)
        failed_summary = exc.partial_summary
        if failed_summary is None:
            failed_summary = Stage5RunSummary(run_month=config.run_month, started_at=started_at)
        failed_summary.status = "failed"
        failed_summary.abort_reason = str(exc)
        failed_summary.finished_at = datetime.now(timezone.utc).isoformat()
        write_json(stage5_summary_path, failed_summary.to_json_dict())
        return 1

    except Exception:  # noqa: BLE001 - top-level entrypoint: log, don't crash silently
        logger.exception("Stage 5 aborted due to an unexpected error")
        failed_summary = Stage5RunSummary(
            run_month=config.run_month,
            started_at=started_at,
            status="failed",
            abort_reason="unexpected_error",
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        write_json(stage5_summary_path, failed_summary.to_json_dict())
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    config = parse_config(argv)
    return run(config)


if __name__ == "__main__":
    sys.exit(main())
