import logging

import pytest

from tool.ksbcl_pricing_pipeline import extract as extract_module
from tool.ksbcl_pricing_pipeline.extract import extract_structured_rows, process_page_rows
from tool.ksbcl_pricing_pipeline.validate import PipelineValidationError

HEADER_ROW = [
    "SR NO",
    "ITEM NAME",
    "ITEM CODE",
    "EFFECTIVE\nDATE",
    "DECLARED\nPRICE",
    "LANDED COST",
    "KSBCL SELLING\nPRICE",
    "MRP",
]


def _supplier_row(name, code):
    return [None, f"Supplier : {name} ({code})", "-", "-", "-", "-", "-", "-"]


def _product_row(sr, item_code, date_str="10-Jul-20", mrp="100.00"):
    return [sr, f"Product {sr}", item_code, date_str, "50.00", "90.00", "95.00", mrp]


def _filler_row():
    return ["1", "-", "-", "-", "(values in Rs.)", None, None, None]


@pytest.fixture
def logger():
    log = logging.getLogger("test")
    log.addHandler(logging.NullHandler())
    return log


# --- process_page_rows -------------------------------------------------------


def test_process_page_rows_accepts_valid_page(logger):
    table_rows = [
        HEADER_ROW,
        _supplier_row("Khoday R C A Industries", "0001"),
        _product_row("3", "10300901"),
        _product_row("4", "10300902"),
        _filler_row(),
    ]
    result = process_page_rows(
        table_rows, page_number=1, run_month="2026-06", supplier_context=None,
        mrp_min=None, mrp_max=None, logger=logger,
    )
    assert len(result.accepted) == 2
    assert len(result.rejected) == 0
    assert result.supplier_context.code == "0001"
    assert result.header_rows_seen == 1
    assert result.supplier_header_rows_seen == 1
    assert result.filler_rows_seen == 1
    assert result.product_rows_seen == 2


def test_process_page_rows_raises_on_missing_header(logger):
    table_rows = [_product_row("3", "10300901")]  # no header at all
    with pytest.raises(PipelineValidationError):
        process_page_rows(
            table_rows, page_number=1, run_month="2026-06", supplier_context=None,
            mrp_min=None, mrp_max=None, logger=logger,
        )


def test_process_page_rows_raises_on_empty_table(logger):
    with pytest.raises(PipelineValidationError):
        process_page_rows(
            [], page_number=1, run_month="2026-06", supplier_context=None,
            mrp_min=None, mrp_max=None, logger=logger,
        )


def test_process_page_rows_carries_supplier_context_into_next_page(logger):
    page_1 = [HEADER_ROW, _supplier_row("Khoday R C A Industries", "0001"), _product_row("3", "10300901")]
    page_2 = [HEADER_ROW, _product_row("50", "10300950")]  # no new supplier row on page 2

    result_1 = process_page_rows(
        page_1, page_number=1, run_month="2026-06", supplier_context=None,
        mrp_min=None, mrp_max=None, logger=logger,
    )
    result_2 = process_page_rows(
        page_2, page_number=2, run_month="2026-06", supplier_context=result_1.supplier_context,
        mrp_min=None, mrp_max=None, logger=logger,
    )
    assert len(result_2.accepted) == 1
    assert result_2.accepted[0].supplier_code == "0001"


def test_process_page_rows_rejects_product_row_before_any_supplier_seen(logger):
    table_rows = [HEADER_ROW, _product_row("3", "10300901")]
    result = process_page_rows(
        table_rows, page_number=1, run_month="2026-06", supplier_context=None,
        mrp_min=None, mrp_max=None, logger=logger,
    )
    assert len(result.accepted) == 0
    assert len(result.rejected) == 1
    assert result.rejected[0].reason_code == "no_active_supplier_context"


# --- extract_structured_rows (fake pdfplumber) --------------------------------


class _FakePage:
    def __init__(self, table_rows):
        self._table_rows = table_rows

    def extract_tables(self):
        return [self._table_rows]


class _FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def _patch_pdfplumber_open(monkeypatch, pages):
    monkeypatch.setattr(extract_module.pdfplumber, "open", lambda _path: _FakePDF(pages))


def test_extract_structured_rows_success(monkeypatch, logger):
    pages = [
        _FakePage([
            HEADER_ROW,
            _supplier_row("Khoday R C A Industries", "0001"),
            _product_row("3", "10300901"),
            _product_row("4", "10300902"),
        ]),
        _FakePage([
            HEADER_ROW,
            _product_row("5", "10300903"),
        ]),
    ]
    _patch_pdfplumber_open(monkeypatch, pages)

    accepted, rejected, summary = extract_structured_rows(
        pdf_path="fake.pdf", run_month="2026-06", logger=logger,
    )
    assert len(accepted) == 3
    assert len(rejected) == 0
    assert summary.status == "success"
    assert summary.total_pages == 2
    assert summary.product_rows_accepted == 3
    assert summary.distinct_supplier_sections_seen == 1


def test_extract_structured_rows_aborts_on_duplicate_item_code(monkeypatch, logger):
    pages = [
        _FakePage([
            HEADER_ROW,
            _supplier_row("Khoday R C A Industries", "0001"),
            _product_row("3", "10300901"),
            _product_row("4", "10300901"),  # duplicate item_code, extraction-bug shaped
        ]),
    ]
    _patch_pdfplumber_open(monkeypatch, pages)

    with pytest.raises(PipelineValidationError, match="duplicate item_code"):
        extract_structured_rows(pdf_path="fake.pdf", run_month="2026-06", logger=logger)


def test_extract_structured_rows_aborts_when_rejected_rate_exceeds_threshold(monkeypatch, logger):
    rows = [HEADER_ROW, _supplier_row("Khoday R C A Industries", "0001")]
    # 1 valid, 3 invalid (bad item code) => 75% rejected, well above any sane threshold.
    rows.append(_product_row("3", "10300901"))
    for i in range(3):
        bad = _product_row(str(4 + i), "BADCODE")
        rows.append(bad)
    pages = [_FakePage(rows)]
    _patch_pdfplumber_open(monkeypatch, pages)

    with pytest.raises(PipelineValidationError, match="rejected-row rate"):
        extract_structured_rows(
            pdf_path="fake.pdf", run_month="2026-06", logger=logger, rejected_row_abort_pct=2.0,
        )


def test_extract_structured_rows_raises_on_multiple_tables_per_page(monkeypatch, logger):
    class _MultiTablePage:
        def extract_tables(self):
            return [[HEADER_ROW], [HEADER_ROW]]

    _patch_pdfplumber_open(monkeypatch, [_MultiTablePage()])
    with pytest.raises(PipelineValidationError, match="expected exactly one table"):
        extract_structured_rows(pdf_path="fake.pdf", run_month="2026-06", logger=logger)


def test_extract_structured_rows_aborts_on_zero_pages(monkeypatch, logger):
    _patch_pdfplumber_open(monkeypatch, [])
    with pytest.raises(PipelineValidationError, match="no pages"):
        extract_structured_rows(pdf_path="fake.pdf", run_month="2026-06", logger=logger)


def test_extract_structured_rows_aborts_when_zero_rows_accepted(monkeypatch, logger):
    # A page with only a header + a filler row: structurally valid, but
    # yields zero product rows — must not be reported as "success".
    pages = [_FakePage([HEADER_ROW, _filler_row()])]
    _patch_pdfplumber_open(monkeypatch, pages)
    with pytest.raises(PipelineValidationError, match="zero product rows accepted"):
        extract_structured_rows(pdf_path="fake.pdf", run_month="2026-06", logger=logger)


def test_extract_structured_rows_attaches_partial_summary_on_mid_run_abort(monkeypatch, logger):
    # Page 1 succeeds with 2 real accepted rows; page 2's header is broken.
    # The abort must not lose page 1's already-accumulated progress.
    pages = [
        _FakePage([
            HEADER_ROW,
            _supplier_row("Khoday R C A Industries", "0001"),
            _product_row("3", "10300901"),
            _product_row("4", "10300902"),
        ]),
        _FakePage([["not", "a", "valid", "header"]]),
    ]
    _patch_pdfplumber_open(monkeypatch, pages)

    with pytest.raises(PipelineValidationError) as exc_info:
        extract_structured_rows(pdf_path="fake.pdf", run_month="2026-06", logger=logger)

    partial = exc_info.value.partial_summary
    assert partial is not None
    assert partial.total_pages == 2
    assert partial.product_rows_accepted == 2
    assert partial.status == "running"  # caller (run_pipeline.py) marks it "failed"


def test_extract_structured_rows_attaches_partial_summary_on_aggregate_check_abort(monkeypatch, logger):
    pages = [
        _FakePage([
            HEADER_ROW,
            _supplier_row("Khoday R C A Industries", "0001"),
            _product_row("3", "10300901"),
            _product_row("4", "10300901"),  # duplicate item_code
        ]),
    ]
    _patch_pdfplumber_open(monkeypatch, pages)

    with pytest.raises(PipelineValidationError) as exc_info:
        extract_structured_rows(pdf_path="fake.pdf", run_month="2026-06", logger=logger)

    partial = exc_info.value.partial_summary
    assert partial is not None
    assert partial.product_rows_accepted == 2  # both rows individually valid, still counted


def test_extract_structured_rows_records_configured_thresholds_used(monkeypatch, logger):
    pages = [
        _FakePage([
            HEADER_ROW,
            _supplier_row("Khoday R C A Industries", "0001"),
            _product_row("3", "10300901"),
        ]),
    ]
    _patch_pdfplumber_open(monkeypatch, pages)

    _, _, summary = extract_structured_rows(
        pdf_path="fake.pdf",
        run_month="2026-06",
        logger=logger,
        rejected_row_abort_pct=5.0,
        row_count_min=1,
    )
    assert summary.rejected_row_abort_pct_used == 5.0
    assert summary.row_count_min_used == 1
    assert summary.mrp_min_used is None
