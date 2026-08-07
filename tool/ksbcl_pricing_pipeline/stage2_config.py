"""Stage 2 CLI configuration — a new, Stage-2-owned module (Stage 1's
``config.py`` is untouched). Mirrors its conventions: everything an
operator might need to vary is a flag, nothing hardcoded, sensible
defaults where the architecture doesn't force a choice.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import RUN_MONTH_PATTERN

_DEFAULT_CLASSIFICATION_CONFIG = Path(__file__).parent / "beer_classification.yaml"


@dataclass(frozen=True)
class Stage2Config:
    run_month: str
    output_root: Path
    classification_config_path: Path
    log_level: str


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ksbcl-stage2",
        description="Stage 2 (Beer Identification) of the KSBCL beer pricing pipeline.",
    )
    parser.add_argument(
        "--run-month",
        required=True,
        help="Period to classify, as YYYY-MM (e.g. 2026-06). Must have a successful Stage 1 "
        "run already at <output-root>/runs/<run-month>/structured_rows.csv (§2.4: there is no "
        "standalone entry point that accepts arbitrary CSV input).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("pricing_data"),
        help="Root directory for pipeline outputs — must match the value Stage 1 was run with "
        "for this run_month. Default: ./pricing_data relative to the current working directory.",
    )
    parser.add_argument(
        "--classification-config",
        type=Path,
        default=_DEFAULT_CLASSIFICATION_CONFIG,
        help="Path to beer_classification.yaml (§2.2). Default: the copy shipped alongside "
        "this package.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity. Default: INFO.",
    )
    return parser


def parse_config(argv: Optional[List[str]] = None) -> Stage2Config:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not RUN_MONTH_PATTERN.match(args.run_month):
        parser.error(f"--run-month must be YYYY-MM, got {args.run_month!r}")

    return Stage2Config(
        run_month=args.run_month,
        output_root=args.output_root,
        classification_config_path=args.classification_config,
        log_level=args.log_level,
    )
