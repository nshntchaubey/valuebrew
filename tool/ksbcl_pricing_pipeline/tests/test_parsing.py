from datetime import date
from decimal import Decimal

from tool.ksbcl_pricing_pipeline.models import RowKind
from tool.ksbcl_pricing_pipeline.parsing import (
    ERROR_INVALID_CALENDAR_DATE,
    ERROR_MISSING,
    ERROR_UNPARSEABLE,
    classify_row,
    clean_numeric_cell,
    find_header_index_map,
    is_filler_row,
    parse_effective_date,
    parse_supplier_header,
)

REAL_HEADER_ROW = [
    "SR NO",
    "ITEM NAME",
    "ITEM CODE",
    "EFFECTIVE\nDATE",
    "DECLARED\nPRICE",
    "LANDED COST",
    "KSBCL SELLING\nPRICE",
    "MRP",
]

REAL_SUPPLIER_ROW = [
    "2",
    "Supplier : Khoday R C A Industries (0001)",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
]

REAL_FILLER_ROW = ["1", "-", "-", "-", "(values in Rs.)", None, None, None]

REAL_PRODUCT_ROW = [
    "3",
    "Khodays XXX Rum 750MLx12Btls(0001)",
    "10300901",
    "10-Jul-20",
    "699.00",
    "6,162.00",
    "6,199.00",
    "5 68.24",  # the confirmed whitespace-tokenization artifact
]


# --- clean_numeric_cell ----------------------------------------------------


def test_clean_numeric_cell_strips_tokenization_artifact():
    value, error_code, error_detail = clean_numeric_cell("1 40.00")
    assert error_code is None
    assert value == Decimal("140.00")


def test_clean_numeric_cell_strips_multiple_internal_spaces():
    value, error_code, error_detail = clean_numeric_cell("5 68.24")
    assert error_code is None
    assert error_detail is None
    assert value == Decimal("568.24")


def test_clean_numeric_cell_parses_indian_thousands_comma():
    value, error_code, error_detail = clean_numeric_cell("6,199.00")
    assert error_code is None
    assert value == Decimal("6199.00")


def test_clean_numeric_cell_parses_indian_lakh_grouping():
    # e.g. "1,20,166.05" seen in the real PDF (Glenfiddich 15 YO row).
    value, error_code, error_detail = clean_numeric_cell("1,20,166.05")
    assert error_code is None
    assert value == Decimal("120166.05")


def test_clean_numeric_cell_handles_clean_value_with_no_artifact():
    value, error_code, error_detail = clean_numeric_cell("70.27")
    assert error_code is None
    assert value == Decimal("70.27")


def test_clean_numeric_cell_rejects_none():
    value, error_code, error_detail = clean_numeric_cell(None)
    assert value is None
    assert error_code == ERROR_MISSING
    assert error_detail is None


def test_clean_numeric_cell_rejects_non_numeric_text():
    value, error_code, error_detail = clean_numeric_cell("abc")
    assert value is None
    assert error_code == ERROR_UNPARSEABLE
    assert error_detail == "abc"


def test_clean_numeric_cell_rejects_negative_value():
    value, error_code, error_detail = clean_numeric_cell("-5.00")
    assert value is None
    assert error_code == ERROR_UNPARSEABLE


def test_clean_numeric_cell_rejects_wrong_decimal_places():
    value, error_code, error_detail = clean_numeric_cell("12.5")
    assert value is None
    assert error_code == ERROR_UNPARSEABLE


# --- parse_effective_date ---------------------------------------------------


def test_parse_effective_date_valid():
    result, error_code, error_detail = parse_effective_date("10-Jul-20")
    assert error_code is None
    assert error_detail is None
    assert result == date(2020, 7, 10)


def test_parse_effective_date_two_digit_year_always_2000s():
    # Architecture §5.4: 00-99 -> 20xx, never a 19xx branch.
    result, error_code, error_detail = parse_effective_date("13-May-26")
    assert error_code is None
    assert result == date(2026, 5, 13)

    result, error_code, error_detail = parse_effective_date("01-Jan-99")
    assert error_code is None
    assert result == date(2099, 1, 1)


def test_parse_effective_date_rejects_wrong_format():
    result, error_code, error_detail = parse_effective_date("2020-07-10")
    assert result is None
    assert error_code == ERROR_UNPARSEABLE


def test_parse_effective_date_rejects_bad_month_abbreviation():
    result, error_code, error_detail = parse_effective_date("10-Xyz-20")
    assert result is None
    assert error_code == ERROR_UNPARSEABLE


def test_parse_effective_date_rejects_invalid_calendar_date():
    result, error_code, error_detail = parse_effective_date("30-Feb-20")
    assert result is None
    assert error_code == ERROR_INVALID_CALENDAR_DATE
    assert error_detail == "30-Feb-20"


def test_parse_effective_date_rejects_none():
    result, error_code, error_detail = parse_effective_date(None)
    assert result is None
    assert error_code == ERROR_MISSING


# --- find_header_index_map --------------------------------------------------


def test_find_header_index_map_matches_real_header_row():
    index_map = find_header_index_map(REAL_HEADER_ROW)
    assert index_map is not None
    assert index_map["item_code"] == 2
    assert index_map["mrp"] == 7


def test_find_header_index_map_is_order_independent():
    # "match by name, not position" (architecture §9) — a reordered header
    # row should still resolve correctly.
    reordered = list(reversed(REAL_HEADER_ROW))
    index_map = find_header_index_map(reordered)
    assert index_map is not None
    assert reordered[index_map["mrp"]].strip().upper() == "MRP"
    assert reordered[index_map["item_code"]].strip().upper() == "ITEM CODE"


def test_find_header_index_map_rejects_missing_column():
    incomplete = REAL_HEADER_ROW[:-1]  # drop MRP
    assert find_header_index_map(incomplete) is None


def test_find_header_index_map_rejects_product_row():
    assert find_header_index_map(REAL_PRODUCT_ROW) is None


# --- parse_supplier_header ---------------------------------------------------


def test_parse_supplier_header_matches_real_row():
    context = parse_supplier_header(REAL_SUPPLIER_ROW[1])
    assert context is not None
    assert context.name == "Khoday R C A Industries"
    assert context.code == "0001"


def test_parse_supplier_header_rejects_product_name():
    assert parse_supplier_header(REAL_PRODUCT_ROW[1]) is None


def test_parse_supplier_header_tolerates_trailing_location_text():
    # Real rows found on a full 750-page run, not in the sampled ground
    # truth: trailing text after the "(code)" (a city/plant name).
    context = parse_supplier_header("Supplier : Vinspri Distributors Pvt Ltd (0386)-Mumbai")
    assert context is not None
    assert context.name == "Vinspri Distributors Pvt Ltd"
    assert context.code == "0386"

    context = parse_supplier_header(
        "Supplier : William Grant and Sons India Pvt Ltd(0725)Bottling at Modi Distillery"
    )
    assert context is not None
    assert context.name == "William Grant and Sons India Pvt Ltd"
    assert context.code == "0725"

    context = parse_supplier_header("Supplier : Aloka Breweries Pvt Ltd (0956) New Delhi")
    assert context is not None
    assert context.name == "Aloka Breweries Pvt Ltd"
    assert context.code == "0956"


def test_parse_supplier_header_rejects_none():
    assert parse_supplier_header(None) is None


# --- is_filler_row / classify_row -------------------------------------------


def test_classify_row_detects_repeated_header():
    header_map = find_header_index_map(REAL_HEADER_ROW)
    kind, supplier = classify_row(REAL_HEADER_ROW, header_map)
    assert kind == RowKind.HEADER
    assert supplier is None


def test_classify_row_detects_supplier_row():
    header_map = find_header_index_map(REAL_HEADER_ROW)
    kind, supplier = classify_row(REAL_SUPPLIER_ROW, header_map)
    assert kind == RowKind.SUPPLIER
    assert supplier.code == "0001"


def test_classify_row_detects_filler_row():
    header_map = find_header_index_map(REAL_HEADER_ROW)
    kind, supplier = classify_row(REAL_FILLER_ROW, header_map)
    assert kind == RowKind.FILLER
    assert supplier is None


def test_classify_row_detects_product_row():
    header_map = find_header_index_map(REAL_HEADER_ROW)
    kind, supplier = classify_row(REAL_PRODUCT_ROW, header_map)
    assert kind == RowKind.PRODUCT
    assert supplier is None


def test_is_filler_row_true_for_dash_cells():
    header_map = find_header_index_map(REAL_HEADER_ROW)
    assert is_filler_row(REAL_FILLER_ROW, header_map) is True


def test_is_filler_row_false_for_real_product():
    header_map = find_header_index_map(REAL_HEADER_ROW)
    assert is_filler_row(REAL_PRODUCT_ROW, header_map) is False
