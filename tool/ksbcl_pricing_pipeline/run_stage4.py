"""Stage 4 (Canonical Identity Resolution) entrypoint.

A separate, independently-runnable command, mirroring Stage 3's
``run_stage3.py`` pattern exactly. Reads a ``run_month``'s already-
persisted ``structured_rows.csv`` and ``normalized_rows.csv`` (both must
exist — no standalone "arbitrary CSV" mode, mirroring Stage 3's own
§2.3/§2.4 posture) plus the prior, permanent ``item_code_canonical_map.csv``
(absent on a first-ever run — bootstrap, §8), and produces an updated
``item_code_canonical_map.csv``, this run's ``canonical_resolution_review.csv``,
and a run summary (architecture §2.2, §7).

Usage:
    python -m tool.ksbcl_pricing_pipeline.run_stage4 --run-month 2026-06
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .canonical_map_io import CanonicalMapCorruptionError, canonical_map_rows_sorted, load_canonical_map
from .canonical_models import CANONICAL_MAP_FIELDS, REVIEW_ROW_FIELDS, Stage4RunSummary
from .canonical_resolve import Stage4ValidationError, run_stage4_resolution
from .io_writers import write_csv, write_json
from .normalized_rows_reader import read_normalized_rows
from .stage1_reader import read_structured_rows
from .stage4_config import Stage4Config, parse_config


def _setup_logging(log_level: str, log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ksbcl_pricing_pipeline.stage4")
    logger.setLevel(log_level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # A Stage-4-specific log file, not appended to earlier stages' own
    # logs — the same reasoning Stage 2/3's entrypoints already give.
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run(config: Stage4Config) -> int:
    runs_dir = config.output_root / "runs" / config.run_month
    log_path = runs_dir / "canonical_pipeline.log"
    logger = _setup_logging(config.log_level, log_path)

    structured_rows_path = runs_dir / "structured_rows.csv"
    normalized_rows_path = runs_dir / "normalized_rows.csv"
    canonical_map_path = config.output_root / "item_code_canonical_map.csv"
    review_path = runs_dir / "canonical_resolution_review.csv"
    run_summary_path = runs_dir / "canonical_run_summary.json"

    started_at = datetime.now(timezone.utc).isoformat()

    if not structured_rows_path.exists():
        logger.error(
            "no structured_rows.csv at %s — Stage 4 requires a successful Stage 1 run first",
            structured_rows_path,
        )
        return 1
    if not normalized_rows_path.exists():
        logger.error(
            "no normalized_rows.csv at %s — Stage 4 requires a successful Stage 3 run first",
            normalized_rows_path,
        )
        return 1

    logger.info("Stage 4 (Canonical Identity Resolution) starting: run_month=%s", config.run_month)

    try:
        prior_map = load_canonical_map(canonical_map_path)
    except CanonicalMapCorruptionError as exc:
        logger.error("Stage 4 aborted: %s", exc)
        failed_summary = Stage4RunSummary(
            run_month=config.run_month,
            started_at=started_at,
            status="failed",
            abort_reason=str(exc),
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1

    try:
        product_rows = read_structured_rows(structured_rows_path)
        normalized_rows = read_normalized_rows(normalized_rows_path)

        result = run_stage4_resolution(
            product_rows=product_rows,
            normalized_rows=normalized_rows,
            prior_map=prior_map,
            run_month=config.run_month,
            started_at=started_at,
        )

        # All-or-nothing: only reachable on full success (§8's own
        # idempotency guarantee), applied the same way earlier stages
        # already apply it to themselves.
        result.summary.status = "success"
        result.summary.finished_at = datetime.now(timezone.utc).isoformat()

        write_csv(
            canonical_map_path,
            CANONICAL_MAP_FIELDS,
            (row.to_csv_row() for row in canonical_map_rows_sorted(result.canonical_map)),
        )
        write_csv(
            review_path,
            REVIEW_ROW_FIELDS,
            (row.to_csv_row() for row in result.review_rows),
        )
        write_json(run_summary_path, result.summary.to_json_dict())

        logger.info(
            "Stage 4 complete: %s new canonical products, %s cross-supplier attachments, "
            "%s same-supplier attachments, %s review rows",
            result.summary.new_canonical_products_created,
            result.summary.attached_cross_supplier,
            result.summary.attached_same_supplier,
            result.summary.review_rows_written,
        )
        return 0

    except Stage4ValidationError as exc:
        logger.error("Stage 4 aborted: %s", exc)
        failed_summary = exc.partial_summary
        if failed_summary is None:
            failed_summary = Stage4RunSummary(run_month=config.run_month, started_at=started_at)
        failed_summary.status = "failed"
        failed_summary.abort_reason = str(exc)
        failed_summary.finished_at = datetime.now(timezone.utc).isoformat()
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1

    except Exception:  # noqa: BLE001 - top-level entrypoint: log, don't crash silently
        logger.exception("Stage 4 aborted due to an unexpected error")
        failed_summary = Stage4RunSummary(
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
