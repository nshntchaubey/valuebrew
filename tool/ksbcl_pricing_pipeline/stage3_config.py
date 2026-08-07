"""Stage 3 CLI configuration — a new, Stage-3-owned module. Mirrors
Stage 2's ``stage2_config.py`` conventions."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import RUN_MONTH_PATTERN


@dataclass(frozen=True)
class Stage3Config:
    run_month: str
    output_root: Path
    log_level: str


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ksbcl-stage3",
        description="Stage 3 (Normalization) of the KSBCL beer pricing pipeline.",
    )
    parser.add_argument(
        "--run-month",
        required=True,
        help="Period to normalize, as YYYY-MM. Must have successful Stage 1 and Stage 2 runs "
        "already at <output-root>/runs/<run-month>/ (§2.3, §2.4).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("pricing_data"),
        help="Root directory for pipeline outputs — must match the value Stage 1/2 were run "
        "with for this run_month. Default: ./pricing_data relative to the current working directory.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity. Default: INFO.",
    )
    return parser


def parse_config(argv: Optional[List[str]] = None) -> Stage3Config:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not RUN_MONTH_PATTERN.match(args.run_month):
        parser.error(f"--run-month must be YYYY-MM, got {args.run_month!r}")

    return Stage3Config(
        run_month=args.run_month,
        output_root=args.output_root,
        log_level=args.log_level,
    )
