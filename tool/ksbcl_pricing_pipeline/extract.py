"""Stage 1: Extraction (architecture §2, §4.1).

``pdfplumber extract_tables()``, page-by-page, sequential. Tracks
current-supplier context across pages. Classifies every row as
header / supplier-header / filler / product. Strips the
whitespace-tokenization artifact from every numeric cell. Validates each
product row; failures are logged and dropped, never silently kept or
crash the run.

Split into two layers on purpose (testability): ``process_page_rows``
operates on already-extracted table rows and has no PDF/file I/O at all,
so it is unit-testable with plain lists standing in for pdfplumber output.
``extract_structured_rows`` is the thin layer that actually opens the PDF
and drives the page loop.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber

from .models import ProductRow, RejectedRow, RowKind, RunSummary, SupplierContext
from .parsing import classify_row, find_header_index_map
from .validate import PipelineValidationError, find_duplicate_item_codes, validate_product_row


@dataclass(frozen=True)
class PageResult:
    accepted: List[ProductRow]
    rejected: List[RejectedRow]
    supplier_context: Optional[SupplierContext]
    header_rows_seen: int = 0
    supplier_header_rows_seen: int = 0
    filler_rows_seen: int = 0
    product_rows_seen: int = 0


def process_page_rows(
    table_rows: List[List[Optional[str]]],
    page_number: int,
    run_month: str,
    supplier_context: Optional[SupplierContext],
    mrp_min: Optional[Decimal],
    mrp_max: Optional[Decimal],
    logger: logging.Logger,
) -> PageResult:
    """Process one page's already-extracted table rows.

    Raises PipelineValidationError for structural problems (missing/
    mismatched header, no rows at all) — these abort the whole run
    per architecture §8.2. Row-level problems never raise; they produce
    a RejectedRow instead (§8.1).
    """
    if not table_rows:
        raise PipelineValidationError(f"page {page_number}: no rows extracted (unexpected zero-row page)")

    header_index_map = find_header_index_map(table_rows[0])
    if header_index_map is None:
        raise PipelineValidationError(
            f"page {page_number}: header row does not match the expected column schema "
            f"(architecture §1/§9 — checked by name, not position): {table_rows[0]!r}"
        )

    accepted: List[ProductRow] = []
    rejected: List[RejectedRow] = []
    header_rows_seen = 1  # table_rows[0], already confirmed above
    supplier_header_rows_seen = 0
    filler_rows_seen = 0
    product_rows_seen = 0

    for row in table_rows[1:]:
        kind, maybe_supplier = classify_row(row, header_index_map)

        if kind == RowKind.HEADER:
            header_rows_seen += 1
            logger.debug("page %s: repeated header row, skipped", page_number)
            continue

        if kind == RowKind.SUPPLIER:
            supplier_context = maybe_supplier
            supplier_header_rows_seen += 1
            logger.debug(
                "page %s: entered supplier section %r (%s)",
                page_number,
                maybe_supplier.name,
                maybe_supplier.code,
            )
            continue

        if kind == RowKind.FILLER:
            filler_rows_seen += 1
            logger.debug("page %s: filler/marker row, skipped", page_number)
            continue

        # RowKind.PRODUCT
        product_rows_seen += 1
        product_row, rejected_row = validate_product_row(
            row=row,
            header_index_map=header_index_map,
            supplier_context=supplier_context,
            source_page=page_number,
            run_month=run_month,
            mrp_min=mrp_min,
            mrp_max=mrp_max,
        )
        if product_row is not None:
            accepted.append(product_row)
        else:
            rejected.append(rejected_row)
            logger.warning(
                "page %s: rejected row [%s: %s]: %s",
                page_number,
                rejected_row.reason_code,
                rejected_row.reason_detail,
                row,
            )

    return PageResult(
        accepted=accepted,
        rejected=rejected,
        supplier_context=supplier_context,
        header_rows_seen=header_rows_seen,
        supplier_header_rows_seen=supplier_header_rows_seen,
        filler_rows_seen=filler_rows_seen,
        product_rows_seen=product_rows_seen,
    )


def extract_structured_rows(
    pdf_path: Path,
    run_month: str,
    logger: logging.Logger,
    mrp_min: Optional[Decimal] = None,
    mrp_max: Optional[Decimal] = None,
    rejected_row_abort_pct: float = 2.0,
    row_count_min: Optional[int] = None,
    row_count_max: Optional[int] = None,
) -> Tuple[List[ProductRow], List[RejectedRow], RunSummary]:
    """Run Stage 1 end to end against one PDF. Raises
    PipelineValidationError on any structural/aggregate failure — the
    caller is expected to treat that as an aborted run and write no
    structured_rows.csv / rejected_rows.csv (architecture §8.5:
    idempotent, all-or-nothing output).

    Whatever RunSummary state accumulated before an abort is attached to
    the raised exception as ``partial_summary``, so the caller can still
    report accurate page/row counts for a run that failed on, say, page
    421 of 750 — not just "it failed, and that's all we know."
    """
    started_at = datetime.now(timezone.utc).isoformat()
    summary = RunSummary(
        run_month=run_month,
        source_pdf_reference=str(pdf_path),
        started_at=started_at,
        rejected_row_abort_pct_used=rejected_row_abort_pct,
        mrp_min_used=str(mrp_min) if mrp_min is not None else None,
        mrp_max_used=str(mrp_max) if mrp_max is not None else None,
        row_count_min_used=row_count_min,
        row_count_max_used=row_count_max,
    )

    accepted_rows: List[ProductRow] = []
    rejected_rows: List[RejectedRow] = []
    supplier_context: Optional[SupplierContext] = None
    seen_supplier_codes = set()

    def _sync_summary_counts() -> None:
        """Bring summary's aggregate fields up to date with whatever has
        actually been accumulated so far — called both on the normal
        success path and right before any abort, so a partial summary is
        never stale relative to accepted_rows/rejected_rows.
        """
        summary.product_rows_accepted = len(accepted_rows)
        summary.product_rows_rejected = len(rejected_rows)
        summary.distinct_supplier_sections_seen = len(seen_supplier_codes)
        reason_counts: Dict[str, int] = {}
        for rejected_row in rejected_rows:
            reason_counts[rejected_row.reason_code] = reason_counts.get(rejected_row.reason_code, 0) + 1
        summary.rejected_rows_by_reason = reason_counts

    try:
        with pdfplumber.open(pdf_path) as pdf:
            summary.total_pages = len(pdf.pages)
            logger.info("opened %s (%s pages)", pdf_path, summary.total_pages)

            if summary.total_pages == 0:
                raise PipelineValidationError(f"{pdf_path}: PDF has no pages")

            for page_index, page in enumerate(pdf.pages):
                page_number = page_index + 1
                tables = page.extract_tables()

                if len(tables) == 0:
                    raise PipelineValidationError(f"page {page_number}: no table extracted")
                if len(tables) > 1:
                    raise PipelineValidationError(
                        f"page {page_number}: expected exactly one table, found {len(tables)} "
                        "(not accounted for by the architecture — refusing to guess which is authoritative)"
                    )

                result = process_page_rows(
                    table_rows=tables[0],
                    page_number=page_number,
                    run_month=run_month,
                    supplier_context=supplier_context,
                    mrp_min=mrp_min,
                    mrp_max=mrp_max,
                    logger=logger,
                )
                supplier_context = result.supplier_context
                accepted_rows.extend(result.accepted)
                rejected_rows.extend(result.rejected)
                summary.header_rows_seen += result.header_rows_seen
                summary.supplier_header_rows_seen += result.supplier_header_rows_seen
                summary.filler_rows_seen += result.filler_rows_seen
                summary.product_rows_seen += result.product_rows_seen
                if result.supplier_context is not None:
                    seen_supplier_codes.add(result.supplier_context.code)

                if page_number % 100 == 0:
                    logger.info("processed %s/%s pages", page_number, summary.total_pages)

        _sync_summary_counts()
        logger.info(
            "extraction complete: %s pages, %s product rows seen, %s accepted, %s rejected, "
            "%s supplier sections",
            summary.total_pages,
            summary.product_rows_seen,
            summary.product_rows_accepted,
            summary.product_rows_rejected,
            summary.distinct_supplier_sections_seen,
        )

        # ---- Aggregate / structural checks (§8.3, §9) ----------------------

        if summary.product_rows_accepted == 0:
            # Not a tunable/optional bound (row_count_min is that, and stays
            # operator-configured per §12.4) — a real KSBCL snapshot has
            # never legitimately produced zero accepted rows, and silently
            # reporting "success" for an empty/degenerate extraction would
            # be worse than any of the row-level rejections this stage
            # otherwise guards against.
            raise PipelineValidationError("zero product rows accepted — refusing to report success")

        duplicates = find_duplicate_item_codes(accepted_rows)
        if duplicates:
            raise PipelineValidationError(
                "duplicate item_code(s) within one run — this is Case (a) from architecture "
                f"§4.4/§8.3, an extraction bug, not a real-world data condition: {duplicates}"
            )

        if summary.product_rows_seen > 0:
            rejected_pct = 100.0 * summary.product_rows_rejected / summary.product_rows_seen
        else:
            rejected_pct = 0.0
        if rejected_pct > rejected_row_abort_pct:
            raise PipelineValidationError(
                f"rejected-row rate {rejected_pct:.2f}% exceeds the configured abort threshold "
                f"{rejected_row_abort_pct:.2f}% (architecture §12.4 — this threshold has no "
                "architecture-specified value; it is operator-configured, default follows the "
                "architecture's own suggested starting point)"
            )

        if row_count_min is not None and summary.product_rows_accepted < row_count_min:
            raise PipelineValidationError(
                f"accepted row count {summary.product_rows_accepted} is below the configured "
                f"minimum {row_count_min}"
            )
        if row_count_max is not None and summary.product_rows_accepted > row_count_max:
            raise PipelineValidationError(
                f"accepted row count {summary.product_rows_accepted} is above the configured "
                f"maximum {row_count_max}"
            )

    except PipelineValidationError as exc:
        _sync_summary_counts()
        exc.partial_summary = summary
        raise

    summary.status = "success"
    summary.finished_at = datetime.now(timezone.utc).isoformat()
    return accepted_rows, rejected_rows, summary
