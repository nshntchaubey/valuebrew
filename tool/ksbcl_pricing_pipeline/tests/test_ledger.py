from datetime import date
from decimal import Decimal

from tool.ksbcl_pricing_pipeline.classification_models import ClassificationAuditRow, KnownTermRow
from tool.ksbcl_pricing_pipeline.ledger import (
    build_new_entity_rows,
    compute_known_supplier_codes,
    entities_contributed_this_run,
    known_terms_rows_sorted,
    load_known_terms,
    update_known_terms,
)
from tool.ksbcl_pricing_pipeline.models import ProductRow


def _product_row(item_code, item_name_raw, supplier_code):
    return ProductRow(
        item_code=item_code,
        item_name_raw=item_name_raw,
        supplier_name="Supplier",
        supplier_code=supplier_code,
        effective_date_raw="10-Jul-26",
        effective_date=date(2026, 7, 10),
        declared_price_raw="1.00",
        declared_price=Decimal("1.00"),
        landed_cost_raw="1.00",
        landed_cost=Decimal("1.00"),
        ksbcl_selling_price_raw="1.00",
        ksbcl_selling_price=Decimal("1.00"),
        mrp_raw="1.00",
        mrp=Decimal("1.00"),
        source_page=1,
        run_month="2026-06",
    )


def _audit_row(item_code, matched_signal_type, matched_term):
    return ClassificationAuditRow(
        run_month="2026-06",
        item_code=item_code,
        confidence_tier="high",
        included=True,
        matched_signal_type=matched_signal_type,
        matched_term=matched_term,
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=False,
        classification_config_version="abc123def456",
    )


def test_entities_contributed_style_keyword_row_contributes_two_entities():
    pair = (_product_row("1", "Kingfisher Beer", "0210"), _audit_row("1", "style_keyword", "beer"))
    contributed = entities_contributed_this_run([pair])
    assert contributed == {("supplier_code", "0210"), ("style_keyword", "beer")}


def test_entities_contributed_supplier_corroboration_only_contributes_one_entity():
    pair = (_product_row("1", "Some Import", "0210"), _audit_row("1", "supplier_corroboration_only", None))
    contributed = entities_contributed_this_run([pair])
    assert contributed == {("supplier_code", "0210")}


def test_entities_contributed_dedupes_within_one_run():
    pairs = [
        (_product_row("1", "Kingfisher Beer", "0210"), _audit_row("1", "style_keyword", "beer")),
        (_product_row("2", "Kingfisher Lager", "0210"), _audit_row("2", "style_keyword", "beer")),
    ]
    contributed = entities_contributed_this_run(pairs)
    assert contributed == {("supplier_code", "0210"), ("style_keyword", "beer")}


def test_update_case_1_no_existing_row():
    updated = update_known_terms({}, {("style_keyword", "beer")}, "2026-06")
    entry = updated[("style_keyword", "beer")]
    assert entry.first_seen_run_month == "2026-06"
    assert entry.last_seen_run_month == "2026-06"
    assert entry.times_seen == 1


def test_update_case_2_same_month_rerun_is_a_true_no_op():
    existing = {
        ("style_keyword", "beer"): KnownTermRow("style_keyword", "beer", "2026-05", "2026-06", 3)
    }
    updated = update_known_terms(existing, {("style_keyword", "beer")}, "2026-06")
    assert updated[("style_keyword", "beer")] == existing[("style_keyword", "beer")]


def test_update_case_3_newer_month_advances_last_seen_and_increments():
    existing = {
        ("style_keyword", "beer"): KnownTermRow("style_keyword", "beer", "2026-05", "2026-06", 3)
    }
    updated = update_known_terms(existing, {("style_keyword", "beer")}, "2026-07")
    entry = updated[("style_keyword", "beer")]
    assert entry.first_seen_run_month == "2026-05"
    assert entry.last_seen_run_month == "2026-07"
    assert entry.times_seen == 4


def test_update_case_4_older_month_never_regresses_last_seen():
    existing = {
        ("style_keyword", "beer"): KnownTermRow("style_keyword", "beer", "2026-05", "2026-07", 3)
    }
    updated = update_known_terms(existing, {("style_keyword", "beer")}, "2026-06")
    entry = updated[("style_keyword", "beer")]
    assert entry.last_seen_run_month == "2026-07"  # unchanged
    assert entry.first_seen_run_month == "2026-05"  # unchanged (2026-06 is not earlier)
    assert entry.times_seen == 4  # still incremented


def test_update_case_4_older_month_lowers_first_seen_if_earlier():
    existing = {
        ("style_keyword", "beer"): KnownTermRow("style_keyword", "beer", "2026-05", "2026-07", 3)
    }
    updated = update_known_terms(existing, {("style_keyword", "beer")}, "2026-01")
    entry = updated[("style_keyword", "beer")]
    assert entry.first_seen_run_month == "2026-01"
    assert entry.last_seen_run_month == "2026-07"


def test_compute_known_supplier_codes_filters_by_entity_type():
    known = {
        ("supplier_code", "0210"): KnownTermRow("supplier_code", "0210", "2026-05", "2026-06", 2),
        ("style_keyword", "beer"): KnownTermRow("style_keyword", "beer", "2026-05", "2026-06", 2),
    }
    assert compute_known_supplier_codes(known) == frozenset({"0210"})


def test_build_new_entity_rows_only_includes_genuinely_new_entities():
    existing = {("supplier_code", "0210"): KnownTermRow("supplier_code", "0210", "2026-05", "2026-05", 1)}
    pairs = [
        (_product_row("1", "Kingfisher Beer", "0210"), _audit_row("1", "style_keyword", "beer")),
    ]
    rows = build_new_entity_rows(existing, pairs)
    assert len(rows) == 1
    assert rows[0].entity_type == "style_keyword"
    assert rows[0].value == "beer"
    assert rows[0].sample_item_code == "1"


def test_build_new_entity_rows_sorted_deterministically():
    pairs = [
        (_product_row("2", "Corona", "0999"), _audit_row("2", "brand_name", "Corona")),
        (_product_row("1", "Kingfisher Beer", "0210"), _audit_row("1", "style_keyword", "beer")),
    ]
    rows = build_new_entity_rows({}, pairs)
    keys = [(r.entity_type, r.value) for r in rows]
    assert keys == sorted(keys)


def test_known_terms_rows_sorted_is_deterministic():
    known = {
        ("style_keyword", "lager"): KnownTermRow("style_keyword", "lager", "2026-05", "2026-05", 1),
        ("brand_name", "Kingfisher"): KnownTermRow("brand_name", "Kingfisher", "2026-05", "2026-05", 1),
    }
    rows = known_terms_rows_sorted(known)
    assert [(r.entity_type, r.value) for r in rows] == [("brand_name", "Kingfisher"), ("style_keyword", "lager")]


def test_load_known_terms_missing_file_returns_empty_dict(tmp_path):
    assert load_known_terms(tmp_path / "does_not_exist.csv") == {}
