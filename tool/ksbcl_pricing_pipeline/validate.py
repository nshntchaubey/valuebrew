"""Stage 1 validation: row-level checks (§8.1) and the structural /
aggregate checks that are Stage 1's responsibility per §9 ("Structural"
and the Stage-1-relevant parts of "Field-level" and "Relational").

Row-level failures return a RejectedRow and never raise (§8.1: "Row-level
failures never abort the run; they're logged and dropped"). Structural /
aggregate failures raise PipelineValidationError, which the caller
(extract.py / run_pipeline.py) treats as an abort (§8.2, §8.3).
"""

from __future__ import annotations

import calendar
import re
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .models import ProductRow, RejectedRow, SupplierContext
from .parsing import ERROR_MISSING, ERROR_UNPARSEABLE, clean_numeric_cell, get_cell, parse_effective_date

ITEM_CODE_PATTERN = re.compile(r"^\d{8,11}$")

# The four price columns, in the order they appear on structured_rows.csv
# (architecture §4.1) — used to drive the DRY validation loop below instead
# of four near-identical hand-written blocks.
PRICE_FIELDS: Tuple[str, ...] = (
    "declared_price",
    "landed_cost",
    "ksbcl_selling_price",
    "mrp",
)


class PipelineValidationError(Exception):
    """A structural/aggregate failure that aborts the run (§8.2, §8.3).

    ``partial_summary``, if set by the raiser, carries whatever RunSummary
    state had accumulated before the abort — so a failed run's
    run_summary.json isn't just "status: failed" with no other content.
    Not declared as a constructor parameter (kept as a plain attribute,
    set after construction) so raising a PipelineValidationError stays a
    one-line ``raise PipelineValidationError("...")`` everywhere except
    the single place (extract_structured_rows) that attaches it.
    """

    partial_summary: Optional[object] = None


def _run_month_end(run_month: str) -> date:
    year_str, month_str = run_month.split("-")
    year, month = int(year_str), int(month_str)
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


def validate_product_row(
    row: List[Optional[str]],
    header_index_map: Dict[str, int],
    supplier_context: Optional[SupplierContext],
    source_page: int,
    run_month: str,
    mrp_min: Optional[Decimal] = None,
    mrp_max: Optional[Decimal] = None,
) -> Tuple[Optional[ProductRow], Optional[RejectedRow]]:
    """Validate one candidate product row.

    Returns exactly one of (ProductRow, None) on success or
    (None, RejectedRow) on failure — never both, never neither.
    """

    def reject(reason_code: str, detail: str = "") -> Tuple[None, RejectedRow]:
        return None, RejectedRow(
            run_month=run_month,
            source_page=source_page,
            raw_row=list(row),
            reason_code=reason_code,
            reason_detail=detail,
        )

    # §8.1: "supplier context present" — a product row must belong to an
    # active supplier section (architecture §1: every product row lives
    # inside a supplier section).
    if supplier_context is None:
        return reject("no_active_supplier_context")

    item_name_raw = get_cell(row, header_index_map, "item_name")
    if item_name_raw is None or not item_name_raw.strip():
        return reject("missing_item_name")

    item_code_raw = get_cell(row, header_index_map, "item_code")
    item_code = (item_code_raw or "").strip()
    if not ITEM_CODE_PATTERN.match(item_code):
        return reject("invalid_item_code_format", str(item_code_raw))

    effective_date_raw = get_cell(row, header_index_map, "effective_date")
    effective_date, date_error_code, date_error_detail = parse_effective_date(effective_date_raw)
    if date_error_code == ERROR_MISSING:
        return reject("missing_effective_date")
    if date_error_code == ERROR_UNPARSEABLE:
        return reject("unparseable_effective_date", date_error_detail or "")
    if date_error_code is not None:  # invalid_calendar_date
        return reject(date_error_code, date_error_detail or "")

    if effective_date > _run_month_end(run_month):
        return reject(
            "effective_date_after_run_month",
            f"{effective_date.isoformat()} > end of run_month {run_month}",
        )

    # §8.1: "all four prices parse to a positive decimal post-cleanup" —
    # every price column, not just MRP. Parsed via one loop rather than
    # four copy-pasted blocks (each field only differs by name).
    prices: Dict[str, Decimal] = {}
    price_raws: Dict[str, Optional[str]] = {}
    for field in PRICE_FIELDS:
        raw_value = get_cell(row, header_index_map, field)
        value, error_code, error_detail = clean_numeric_cell(raw_value)
        if error_code == ERROR_MISSING:
            return reject(f"missing_{field}")
        if error_code is not None:  # unparseable
            return reject(f"unparseable_{field}", error_detail or "")
        prices[field] = value
        price_raws[field] = raw_value

    for field in PRICE_FIELDS:
        if prices[field] <= Decimal("0"):
            return reject(f"{field}_not_positive", str(prices[field]))

    # §9 Field-level: "MRP within a plausible absolute range (tunable)".
    # No default is given anywhere in the architecture, so this check is
    # inert (skipped) unless the operator explicitly configures a bound —
    # never an invented threshold. See config.py --mrp-min/--mrp-max.
    mrp = prices["mrp"]
    if mrp_min is not None and mrp < mrp_min:
        return reject("mrp_below_configured_min", f"{mrp} < {mrp_min}")
    if mrp_max is not None and mrp > mrp_max:
        return reject("mrp_above_configured_max", f"{mrp} > {mrp_max}")

    product_row = ProductRow(
        item_code=item_code,
        item_name_raw=item_name_raw,
        supplier_name=supplier_context.name,
        supplier_code=supplier_context.code,
        effective_date_raw=effective_date_raw,
        effective_date=effective_date,
        declared_price_raw=price_raws["declared_price"],
        declared_price=prices["declared_price"],
        landed_cost_raw=price_raws["landed_cost"],
        landed_cost=prices["landed_cost"],
        ksbcl_selling_price_raw=price_raws["ksbcl_selling_price"],
        ksbcl_selling_price=prices["ksbcl_selling_price"],
        mrp_raw=price_raws["mrp"],
        mrp=mrp,
        source_page=source_page,
        run_month=run_month,
    )
    return product_row, None


def find_duplicate_item_codes(rows: List[ProductRow]) -> Dict[str, List[int]]:
    """Item Code is unique per row within one snapshot (architecture §1).
    A repeat among *accepted* rows is Case (a) from §4.4/§8.3 — an
    extraction bug, not a real-world data condition — and the caller
    treats a non-empty result as abort-worthy.
    """
    pages_by_code: Dict[str, List[int]] = {}
    for product_row in rows:
        pages_by_code.setdefault(product_row.item_code, []).append(product_row.source_page)
    return {code: pages for code, pages in pages_by_code.items() if len(pages) > 1}
