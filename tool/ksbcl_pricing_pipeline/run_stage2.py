"""Stage 2 (Beer Identification) entrypoint.

A separate, independently-runnable command from Stage 1's
``run_pipeline.py`` — deliberately not chained into that module, so
neither stage's own file is touched by the other's implementation.
Reads a ``run_month``'s already-persisted ``structured_rows.csv`` (must
exist — no standalone "arbitrary CSV" mode, §2.4) and produces the five
artifacts described in architecture §3.

Usage:
    python -m tool.ksbcl_pricing_pipeline.run_stage2 --run-month 2026-06
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .classification_config import ClassificationConfigError, load_classification_config
from .classification_models import (
    CLASSIFICATION_AUDIT_FIELDS,
    KNOWN_TERM_FIELDS,
    NEW_ENTITY_FIELDS,
    REVIEW_QUEUE_FIELDS,
    ClassificationRunSummary,
)
from .classify_stage import Stage2ValidationError, run_stage2_classification
from .io_writers import write_csv, write_json
from .ledger import known_terms_rows_sorted, load_known_terms
from .review_queue import load_review_queue
from .stage1_reader import read_structured_rows
from .stage2_config import Stage2Config, parse_config


def _setup_logging(log_level: str, log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ksbcl_pricing_pipeline.stage2")
    logger.setLevel(log_level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # A Stage-2-specific log file, not appended to Stage 1's
    # pipeline.log — the same "no shared writer on an already-finalized,
    # different-stage artifact" reasoning §3's run_summary.json section
    # gives, applied here since the architecture leaves this specific
    # choice as an unstated implementation detail (§10).
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run(config: Stage2Config) -> int:
    runs_dir = config.output_root / "runs" / config.run_month
    log_path = runs_dir / "classification_pipeline.log"
    logger = _setup_logging(config.log_level, log_path)

    structured_rows_path = runs_dir / "structured_rows.csv"
    audit_path = runs_dir / "classification_audit.csv"
    new_entities_path = runs_dir / "classification_new_entities.csv"
    run_summary_path = runs_dir / "classification_run_summary.json"
    known_terms_path = config.output_root / "classification_known_terms.csv"
    review_queue_path = config.output_root / "classification_review_queue.csv"

    started_at = datetime.now(timezone.utc).isoformat()

    if not structured_rows_path.exists():
        logger.error(
            "no structured_rows.csv at %s — Stage 2 requires a successful Stage 1 run for "
            "this run_month first (§2.3, §2.4)",
            structured_rows_path,
        )
        return 1

    try:
        config_obj = load_classification_config(config.classification_config_path)
    except ClassificationConfigError as exc:
        logger.error("Stage 2 aborted: %s", exc)
        failed_summary = ClassificationRunSummary(
            run_month=config.run_month,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            status="failed",
            abort_reason=str(exc),
        )
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1

    logger.info(
        "Stage 2 (Beer Identification) starting: run_month=%s config_version=%s",
        config.run_month,
        config_obj.config_version,
    )

    try:
        product_rows = read_structured_rows(structured_rows_path)
        known_terms = load_known_terms(known_terms_path)
        review_queue = load_review_queue(review_queue_path)

        result = run_stage2_classification(
            product_rows=product_rows,
            config=config_obj,
            known_terms=known_terms,
            review_queue=review_queue,
            run_month=config.run_month,
            started_at=started_at,
        )

        # All-or-nothing: only reachable on full success (§8.5, applied
        # to Stage 2 the same way Stage 1 already applies it to itself).
        result.summary.status = "success"
        result.summary.finished_at = datetime.now(timezone.utc).isoformat()

        # classification_run_summary.json is written last, deliberately —
        # mirroring Stage 1's own write order (summary last). A crash
        # between two of these writes must never leave a summary already
        # claiming "success" while a later artifact (in particular either
        # persistent ledger) never actually landed.
        write_csv(audit_path, CLASSIFICATION_AUDIT_FIELDS, (row.to_csv_row() for row in result.audit_rows))
        write_csv(new_entities_path, NEW_ENTITY_FIELDS, (row.to_csv_row() for row in result.new_entity_rows))
        write_csv(
            known_terms_path,
            KNOWN_TERM_FIELDS,
            (row.to_csv_row() for row in known_terms_rows_sorted(result.updated_known_terms)),
        )
        write_csv(
            review_queue_path,
            REVIEW_QUEUE_FIELDS,
            (row.to_csv_row() for row in result.updated_review_queue),
        )
        write_json(run_summary_path, result.summary.to_json_dict())

        logger.info(
            "Stage 2 complete: %s candidate rows (high=%s medium=%s low=%s), %s new entities, "
            "%s queue entries",
            result.summary.total_candidate_rows,
            result.summary.counts_by_tier["high"],
            result.summary.counts_by_tier["medium"],
            result.summary.counts_by_tier["low"],
            len(result.new_entity_rows),
            len(result.updated_review_queue),
        )
        return 0

    except Stage2ValidationError as exc:
        logger.error("Stage 2 aborted: %s", exc)
        failed_summary = exc.partial_summary
        if failed_summary is None:
            failed_summary = ClassificationRunSummary(
                run_month=config.run_month,
                started_at=started_at,
                classification_config_version=config_obj.config_version,
            )
        failed_summary.status = "failed"
        failed_summary.abort_reason = str(exc)
        failed_summary.finished_at = datetime.now(timezone.utc).isoformat()
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1

    except Exception:  # noqa: BLE001 - top-level entrypoint: log, don't crash silently
        logger.exception("Stage 2 aborted due to an unexpected error")
        failed_summary = ClassificationRunSummary(
            run_month=config.run_month,
            started_at=started_at,
            status="failed",
            abort_reason="unexpected_error",
            finished_at=datetime.now(timezone.utc).isoformat(),
            classification_config_version=config_obj.config_version,
        )
        write_json(run_summary_path, failed_summary.to_json_dict())
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    config = parse_config(argv)
    return run(config)


if __name__ == "__main__":
    sys.exit(main())
