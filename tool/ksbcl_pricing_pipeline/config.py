"""Stage 1 CLI configuration.

Every path and threshold is supplied by the operator (CLI flags) —
nothing is hardcoded, per the implementation brief. Where the
architecture leaves a threshold genuinely unspecified (MRP plausible
range, row-count sanity band — §9), the corresponding flag defaults to
"unset", meaning that check is a documented no-op rather than an
invented number. Where the architecture *does* suggest a starting value
(§12.4: "abort above 1-2% rejected"), that becomes the flag's default.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Optional

RUN_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@dataclass(frozen=True)
class PipelineConfig:
    input_pdf: Path
    run_month: str
    output_root: Path
    rejected_row_abort_pct: float
    mrp_min: Optional[Decimal]
    mrp_max: Optional[Decimal]
    row_count_min: Optional[int]
    row_count_max: Optional[int]
    log_level: str


def _decimal_arg(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"not a valid decimal: {value!r}") from exc


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ksbcl-pricing-pipeline",
        description="Stage 1 (Extraction) of the KSBCL beer pricing pipeline.",
    )
    parser.add_argument(
        "--input-pdf",
        type=Path,
        required=True,
        help="Path to this month's KSBCL Supplier-wise Item-wise Price List PDF.",
    )
    parser.add_argument(
        "--run-month",
        required=True,
        help="Period this PDF represents, as YYYY-MM (e.g. 2026-06). "
        "Used as the run's directory key and as the reference point for "
        "the effective-date-not-in-the-future check.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("pricing_data"),
        help="Root directory for pipeline outputs (architecture §3). "
        "Default: ./pricing_data relative to the current working directory.",
    )
    parser.add_argument(
        "--rejected-row-abort-pct",
        type=float,
        default=2.0,
        help="Abort the run if the rejected-row rate exceeds this percentage "
        "(architecture §12.4 — open, non-blocking; suggested starting point "
        "was 1-2%%). Default: 2.0.",
    )
    parser.add_argument(
        "--mrp-min",
        type=_decimal_arg,
        default=None,
        help="Optional plausible-range floor for MRP (architecture §9, "
        "unspecified default). Unset by default: the check is a no-op "
        "until an operator supplies a value.",
    )
    parser.add_argument(
        "--mrp-max",
        type=_decimal_arg,
        default=None,
        help="Optional plausible-range ceiling for MRP. Unset by default, "
        "same reasoning as --mrp-min.",
    )
    parser.add_argument(
        "--row-count-min",
        type=int,
        default=None,
        help="Optional lower bound on total accepted product rows this run "
        "(architecture §9's 'rolling historical band', unspecified until "
        "real run history exists). Unset by default.",
    )
    parser.add_argument(
        "--row-count-max",
        type=int,
        default=None,
        help="Optional upper bound on total accepted product rows this run. "
        "Unset by default, same reasoning as --row-count-min.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity. Default: INFO.",
    )
    return parser


def parse_config(argv: Optional[List[str]] = None) -> PipelineConfig:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not RUN_MONTH_PATTERN.match(args.run_month):
        parser.error(f"--run-month must be YYYY-MM, got {args.run_month!r}")

    return PipelineConfig(
        input_pdf=args.input_pdf,
        run_month=args.run_month,
        output_root=args.output_root,
        rejected_row_abort_pct=args.rejected_row_abort_pct,
        mrp_min=args.mrp_min,
        mrp_max=args.mrp_max,
        row_count_min=args.row_count_min,
        row_count_max=args.row_count_max,
        log_level=args.log_level,
    )
