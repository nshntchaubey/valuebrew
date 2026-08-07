from decimal import Decimal

from tool.ksbcl_pricing_pipeline.models import ProductRow, SupplierContext
from tool.ksbcl_pricing_pipeline.parsing import find_header_index_map
from tool.ksbcl_pricing_pipeline.validate import find_duplicate_item_codes, validate_product_row

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
HEADER_MAP = find_header_index_map(HEADER_ROW)

VALID_ROW = [
    "3",
    "Khodays XXX Rum 750MLx12Btls(0001)",
    "10300901",
    "10-Jul-20",
    "699.00",
    "6,162.00",
    "6,199.00",
    "568.24",
]

SUPPLIER = SupplierContext(name="Khoday R C A Industries", code="0001")


def _validate(row, supplier=SUPPLIER, run_month="2026-06", mrp_min=None, mrp_max=None):
    return validate_product_row(
        row=row,
        header_index_map=HEADER_MAP,
        supplier_context=supplier,
        source_page=3,
        run_month=run_month,
        mrp_min=mrp_min,
        mrp_max=mrp_max,
    )


def test_valid_row_is_accepted():
    product_row, rejected = _validate(VALID_ROW)
    assert rejected is None
    assert isinstance(product_row, ProductRow)
    assert product_row.item_code == "10300901"
    assert product_row.mrp == Decimal("568.24")
    assert product_row.supplier_name == "Khoday R C A Industries"
    assert product_row.supplier_code == "0001"
    assert product_row.run_month == "2026-06"
    assert product_row.source_page == 3


def test_no_active_supplier_is_rejected():
    product_row, rejected = _validate(VALID_ROW, supplier=None)
    assert product_row is None
    assert rejected.reason_code == "no_active_supplier_context"


def test_missing_item_name_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["item_name"]] = None
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "missing_item_name"


def test_invalid_item_code_too_short_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["item_code"]] = "123"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "invalid_item_code_format"
    assert rejected.reason_detail == "123"


def test_invalid_item_code_non_numeric_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["item_code"]] = "10300901A"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "invalid_item_code_format"


def test_unparseable_date_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["effective_date"]] = "not-a-date"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "unparseable_effective_date"
    assert rejected.reason_detail == "not-a-date"


def test_missing_date_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["effective_date"]] = None
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "missing_effective_date"


def test_invalid_calendar_date_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["effective_date"]] = "30-Feb-20"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "invalid_calendar_date"


def test_effective_date_after_run_month_is_rejected():
    row = list(VALID_ROW)
    row[HEADER_MAP["effective_date"]] = "15-Jul-26"  # after run_month=2026-06
    product_row, rejected = _validate(row, run_month="2026-06")
    assert product_row is None
    assert rejected.reason_code == "effective_date_after_run_month"


def test_effective_date_within_run_month_is_accepted():
    row = list(VALID_ROW)
    row[HEADER_MAP["effective_date"]] = "30-Jun-26"
    product_row, rejected = _validate(row, run_month="2026-06")
    assert rejected is None
    assert product_row is not None


def test_bad_declared_price_is_rejected_with_field_specific_code():
    row = list(VALID_ROW)
    row[HEADER_MAP["declared_price"]] = "garbage"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "unparseable_declared_price"
    assert rejected.reason_detail == "garbage"


def test_missing_mrp_cell_is_rejected_with_field_specific_code():
    row = list(VALID_ROW)
    row[HEADER_MAP["mrp"]] = None
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "missing_mrp"


def test_mrp_zero_is_rejected_as_not_positive():
    row = list(VALID_ROW)
    row[HEADER_MAP["mrp"]] = "0.00"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "mrp_not_positive"


def test_declared_price_zero_is_rejected_as_not_positive():
    # §8.1: "all four prices parse to a positive decimal", not just MRP.
    row = list(VALID_ROW)
    row[HEADER_MAP["declared_price"]] = "0.00"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "declared_price_not_positive"


def test_landed_cost_zero_is_rejected_as_not_positive():
    row = list(VALID_ROW)
    row[HEADER_MAP["landed_cost"]] = "0.00"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "landed_cost_not_positive"


def test_ksbcl_selling_price_zero_is_rejected_as_not_positive():
    row = list(VALID_ROW)
    row[HEADER_MAP["ksbcl_selling_price"]] = "0.00"
    product_row, rejected = _validate(row)
    assert product_row is None
    assert rejected.reason_code == "ksbcl_selling_price_not_positive"


def test_mrp_range_check_is_a_noop_when_unconfigured():
    row = list(VALID_ROW)
    row[HEADER_MAP["mrp"]] = "5.00"
    product_row, rejected = _validate(row, mrp_min=None, mrp_max=None)
    assert rejected is None
    assert product_row is not None


def test_mrp_range_check_rejects_below_configured_min():
    row = list(VALID_ROW)
    row[HEADER_MAP["mrp"]] = "5.00"
    product_row, rejected = _validate(row, mrp_min=Decimal("10"))
    assert product_row is None
    assert rejected.reason_code == "mrp_below_configured_min"


def test_mrp_range_check_rejects_above_configured_max():
    row = list(VALID_ROW)
    row[HEADER_MAP["mrp"]] = "9999.00"
    product_row, rejected = _validate(row, mrp_max=Decimal("1000"))
    assert product_row is None
    assert rejected.reason_code == "mrp_above_configured_max"


def _make_product_row(item_code: str, page: int) -> ProductRow:
    return ProductRow(
        item_code=item_code,
        item_name_raw="x",
        supplier_name="s",
        supplier_code="0001",
        effective_date_raw="10-Jul-20",
        effective_date=__import__("datetime").date(2020, 7, 10),
        declared_price_raw="1.00",
        declared_price=Decimal("1.00"),
        landed_cost_raw="1.00",
        landed_cost=Decimal("1.00"),
        ksbcl_selling_price_raw="1.00",
        ksbcl_selling_price=Decimal("1.00"),
        mrp_raw="1.00",
        mrp=Decimal("1.00"),
        source_page=page,
        run_month="2026-06",
    )


def test_find_duplicate_item_codes_detects_duplicates():
    rows = [
        _make_product_row("10300901", 3),
        _make_product_row("10300902", 4),
        _make_product_row("10300901", 5),
    ]
    duplicates = find_duplicate_item_codes(rows)
    assert duplicates == {"10300901": [3, 5]}


def test_find_duplicate_item_codes_returns_empty_when_all_unique():
    rows = [_make_product_row("10300901", 3), _make_product_row("10300902", 4)]
    assert find_duplicate_item_codes(rows) == {}
