"""Stage 5 CLI configuration — a new, Stage-5-owned module. Mirrors
Stage 4's ``stage4_config.py`` conventions."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import RUN_MONTH_PATTERN


@dataclass(frozen=True)
class Stage5Config:
    run_month: str
    output_root: Path
    log_level: str


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ksbcl-stage5",
        description="Stage 5 (Master + History) of the KSBCL beer pricing pipeline.",
    )
    parser.add_argument(
        "--run-month",
        required=True,
        help="Period to process, as YYYY-MM. Must have successful Stage 1-4 runs already at "
        "<output-root>/runs/<run-month>/ and a current <output-root>/item_code_canonical_map.csv.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("pricing_data"),
        help="Root directory for pipeline outputs — must match the value Stage 1-4 were run "
        "with for this run_month. Default: ./pricing_data relative to the current working directory.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity. Default: INFO.",
    )
    return parser


def parse_config(argv: Optional[List[str]] = None) -> Stage5Config:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not RUN_MONTH_PATTERN.match(args.run_month):
        parser.error(f"--run-month must be YYYY-MM, got {args.run_month!r}")

    return Stage5Config(
        run_month=args.run_month,
        output_root=args.output_root,
        log_level=args.log_level,
    )
