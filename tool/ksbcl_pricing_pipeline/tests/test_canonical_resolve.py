from datetime import date
from decimal import Decimal

import pytest

from tool.ksbcl_pricing_pipeline.canonical_models import CanonicalMapRow
from tool.ksbcl_pricing_pipeline.canonical_resolve import Stage4ValidationError, run_stage4_resolution
from tool.ksbcl_pricing_pipeline.models import ProductRow
from tool.ksbcl_pricing_pipeline.normalize_models import NormalizedRow

RUN_MONTH = "2026-06"


def _product_row(
    item_code,
    supplier_code="0210",
    supplier_name="United Breweries",
    declared_price="100.00",
    mrp=None,
    effective_date=date(2026, 6, 1),
):
    if mrp is None:
        mrp = declared_price
    return ProductRow(
        item_code=item_code,
        item_name_raw="Kingfisher Strong Beer 650ML",
        supplier_name=supplier_name,
        supplier_code=supplier_code,
        effective_date_raw=effective_date.isoformat(),
        effective_date=effective_date,
        declared_price_raw=declared_price,
        declared_price=Decimal(declared_price),
        landed_cost_raw=declared_price,
        landed_cost=Decimal(declared_price),
        ksbcl_selling_price_raw=declared_price,
        ksbcl_selling_price=Decimal(declared_price),
        mrp_raw=mrp,
        mrp=Decimal(mrp),
        source_page=1,
        run_month=RUN_MONTH,
    )


def _normalized_row(
    item_code,
    normalized_name_key="kingfisher strong beer 650ml",
    pack_size_ml=Decimal("650"),
    container_type="bottle",
    pack_count=None,
):
    return NormalizedRow(
        run_month=RUN_MONTH,
        item_code=item_code,
        display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key=normalized_name_key,
        pack_size_ml=pack_size_ml,
        pack_count=pack_count,
        container_type=container_type,
        normalization_rule_version="v1",
    )


def _mapped(item_code, canonical_product_id, supplier_code="0210", item_status="LIVE", last_seen="2026-05"):
    return CanonicalMapRow(
        ksbcl_item_code=item_code,
        canonical_product_id=canonical_product_id,
        supplier_name="United Breweries",
        supplier_code=supplier_code,
        match_confidence="unreviewed",
        matched_rule="new_canonical",
        item_status=item_status,
        first_seen_run_month="2026-05",
        last_seen_run_month=last_seen,
    )


def test_bootstrap_first_sighting_creates_new_canonical_product():
    result = run_stage4_resolution(
        product_rows=[_product_row("1001")],
        normalized_rows=[_normalized_row("1001")],
        prior_map={},
        run_month=RUN_MONTH,
        started_at="2026-06-01T00:00:00Z",
    )

    assert len(result.canonical_map) == 1
    row = result.canonical_map["1001"]
    assert row.matched_rule == "new_canonical"
    assert row.match_confidence == "unreviewed"
    assert row.item_status == "LIVE"
    assert row.first_seen_run_month == RUN_MONTH
    assert result.summary.new_canonical_products_created == 1


def test_already_mapped_item_code_updates_status_and_last_seen_only():
    prior = {"1001": _mapped("1001", "CP0000001", last_seen="2026-05")}
    result = run_stage4_resolution(
        product_rows=[_product_row("1001")],
        normalized_rows=[_normalized_row("1001")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    row = result.canonical_map["1001"]
    assert row.canonical_product_id == "CP0000001"
    assert row.item_status == "LIVE"
    assert row.last_seen_run_month == RUN_MONTH
    assert result.summary.new_canonical_products_created == 0
    assert result.summary.already_mapped_updated == 1


def test_2a_single_cross_supplier_candidate_attaches_unconditionally_even_at_different_price():
    prior = {"1001": _mapped("1001", "CP0000001", supplier_code="0210")}
    result = run_stage4_resolution(
        product_rows=[
            _product_row("1001", supplier_code="0210", declared_price="80.00"),
            _product_row("1002", supplier_code="0217", declared_price="190.00"),
        ],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    new_row = result.canonical_map["1002"]
    assert new_row.canonical_product_id == "CP0000001"
    assert new_row.match_confidence == "deterministic_high"
    assert new_row.matched_rule == "exact_key_match"
    assert result.summary.attached_cross_supplier == 1
    assert result.review_rows == []


def test_2a_multiple_candidates_defers_and_writes_one_review_row_per_candidate():
    prior = {
        "1001": _mapped("1001", "CP0000001", supplier_code="0210"),
        "1002": _mapped("1002", "CP0000002", supplier_code="0300"),
    }
    result = run_stage4_resolution(
        product_rows=[
            _product_row("1001", supplier_code="0210"),
            _product_row("1002", supplier_code="0300"),
            _product_row("1003", supplier_code="0217"),
        ],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002"), _normalized_row("1003")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    new_row = result.canonical_map["1003"]
    assert new_row.matched_rule == "new_canonical"
    assert len(result.review_rows) == 2
    reasons = {r.reason for r in result.review_rows}
    assert reasons == {"ambiguous_key_multiple_candidates"}
    cited_cids = {r.matched_item_code for r in result.review_rows}
    assert cited_cids == {"1001", "1002"}
    assert all(r.canonical_product_id == new_row.canonical_product_id for r in result.review_rows)


def test_2b_same_supplier_price_mismatch_creates_new_and_flags_possible_supersession():
    prior = {"1001": _mapped("1001", "CP0000001", supplier_code="0217")}
    result = run_stage4_resolution(
        product_rows=[
            _product_row("1001", supplier_code="0217", declared_price="155.00", effective_date=date(2025, 8, 25)),
            _product_row("1002", supplier_code="0217", declared_price="140.00", effective_date=date(2026, 5, 12)),
        ],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    new_row = result.canonical_map["1002"]
    assert new_row.matched_rule == "new_canonical"
    assert len(result.review_rows) == 1
    review = result.review_rows[0]
    assert review.reason == "possible_supersession"
    assert review.matched_item_code == "1001"
    assert review.canonical_product_id == new_row.canonical_product_id


def test_2b_same_supplier_matching_price_and_date_attaches():
    same_date = date(2026, 5, 1)
    prior = {"1001": _mapped("1001", "CP0000001", supplier_code="0210")}
    result = run_stage4_resolution(
        product_rows=[
            _product_row("1001", supplier_code="0210", declared_price="155.00", effective_date=same_date),
            _product_row("1002", supplier_code="0210", declared_price="155.00", effective_date=same_date),
        ],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    new_row = result.canonical_map["1002"]
    assert new_row.canonical_product_id == "CP0000001"
    assert new_row.matched_rule == "exact_key_match"
    assert new_row.match_confidence == "deterministic_high"
    assert result.summary.attached_same_supplier == 1
    assert result.review_rows == []


def test_null_pack_size_ml_always_creates_new_canonical_never_matches():
    result = run_stage4_resolution(
        product_rows=[_product_row("1001"), _product_row("1002")],
        normalized_rows=[
            _normalized_row("1001", pack_size_ml=None),
            _normalized_row("1002", pack_size_ml=None),
        ],
        prior_map={},
        run_month=RUN_MONTH,
        started_at="t",
    )

    assert result.canonical_map["1001"].canonical_product_id != result.canonical_map["1002"].canonical_product_id
    assert result.summary.new_canonical_products_created == 2


def test_within_run_bootstrap_second_sighting_attaches_to_first():
    result = run_stage4_resolution(
        product_rows=[_product_row("1001", supplier_code="0210"), _product_row("1002", supplier_code="0217")],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002")],
        prior_map={},
        run_month=RUN_MONTH,
        started_at="t",
    )

    assert result.canonical_map["1001"].canonical_product_id == result.canonical_map["1002"].canonical_product_id
    assert result.summary.new_canonical_products_created == 1
    assert result.summary.attached_cross_supplier == 1


def test_item_status_maintenance_for_already_mapped_item_code_outside_normalized_rows_still_live():
    prior = {"9999": _mapped("9999", "CP0000005", last_seen="2026-04")}
    result = run_stage4_resolution(
        product_rows=[_product_row("1001"), _product_row("9999")],  # 9999 still in structured_rows.csv
        normalized_rows=[_normalized_row("1001")],  # but excluded from normalized_rows.csv this run
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    row = result.canonical_map["9999"]
    assert row.item_status == "LIVE"
    assert row.last_seen_run_month == "2026-04"  # untouched, per §6 step 1's note


def test_item_status_maintenance_delisted_when_absent_from_structured_rows_too():
    prior = {"9999": _mapped("9999", "CP0000005", last_seen="2026-04")}
    result = run_stage4_resolution(
        product_rows=[_product_row("1001")],  # 9999 absent entirely
        normalized_rows=[_normalized_row("1001")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    row = result.canonical_map["9999"]
    assert row.item_status == "DELISTED"
    assert row.last_seen_run_month == "2026-04"


def test_zero_normalized_rows_raises_validation_error():
    with pytest.raises(Stage4ValidationError):
        run_stage4_resolution(
            product_rows=[_product_row("1001")],
            normalized_rows=[],
            prior_map={},
            run_month=RUN_MONTH,
            started_at="t",
        )


def test_join_integrity_failure_raises_when_normalized_item_code_missing_from_structured():
    with pytest.raises(Stage4ValidationError):
        run_stage4_resolution(
            product_rows=[],
            normalized_rows=[_normalized_row("1001")],
            prior_map={},
            run_month=RUN_MONTH,
            started_at="t",
        )


def test_canonical_id_allocation_continues_from_prior_map_max():
    prior = {"1001": _mapped("1001", "CP0000042")}
    result = run_stage4_resolution(
        product_rows=[_product_row("1001"), _product_row("2001", supplier_code="0999")],
        normalized_rows=[_normalized_row("1001"), _normalized_row("2001", normalized_name_key="different beer")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    assert result.canonical_map["2001"].canonical_product_id == "CP0000043"


def test_rerun_with_unchanged_input_is_deterministic():
    product_rows = [_product_row("1001", supplier_code="0210"), _product_row("1002", supplier_code="0217")]
    normalized_rows = [_normalized_row("1001"), _normalized_row("1002")]

    first = run_stage4_resolution(
        product_rows=product_rows,
        normalized_rows=normalized_rows,
        prior_map={},
        run_month=RUN_MONTH,
        started_at="t",
    )
    second = run_stage4_resolution(
        product_rows=product_rows,
        normalized_rows=normalized_rows,
        prior_map=first.canonical_map,
        run_month=RUN_MONTH,
        started_at="t",
    )

    assert second.canonical_map == first.canonical_map
    assert second.review_rows == []
    # A same-month rerun recomputes this run_month's own resolution from
    # scratch (its entries' first_seen_run_month == run_month, so they're
    # excluded from "true prior state") and reproduces the same counts —
    # it does not report zero activity just because the map already
    # reflects an earlier attempt's result.
    assert second.summary.new_canonical_products_created == first.summary.new_canonical_products_created


def test_rerun_of_same_month_reproduces_review_rows_instead_of_losing_them():
    # Same-supplier, mismatched mrp -> a real possible_supersession event.
    product_rows = [
        _product_row("1001", supplier_code="0217", mrp="155.00", effective_date=date(2025, 8, 25)),
        _product_row("1002", supplier_code="0217", mrp="140.00", effective_date=date(2026, 5, 12)),
    ]
    normalized_rows = [_normalized_row("1001"), _normalized_row("1002")]

    first = run_stage4_resolution(
        product_rows=product_rows,
        normalized_rows=normalized_rows,
        prior_map={},
        run_month=RUN_MONTH,
        started_at="t",
    )
    assert len(first.review_rows) == 1  # sanity: the event actually happened

    # Rerun the *same* run_month against the first run's own output, as
    # run_stage4.py would on a deliberate rerun or a retry after a crash.
    second = run_stage4_resolution(
        product_rows=product_rows,
        normalized_rows=normalized_rows,
        prior_map=first.canonical_map,
        run_month=RUN_MONTH,
        started_at="t",
    )

    assert second.canonical_map == first.canonical_map
    assert second.review_rows == first.review_rows  # not silently dropped to []


def test_price_gate_compares_mrp_not_declared_price():
    same_date = date(2026, 5, 1)
    prior = {"1001": _mapped("1001", "CP0000001", supplier_code="0210")}
    result = run_stage4_resolution(
        product_rows=[
            _product_row("1001", supplier_code="0210", declared_price="1050.18", mrp="155.00", effective_date=same_date),
            _product_row("1002", supplier_code="0210", declared_price="999.99", mrp="155.00", effective_date=same_date),
        ],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    # declared_price differs (1050.18 vs 999.99) but mrp matches (155.00) -> attaches.
    assert result.canonical_map["1002"].canonical_product_id == "CP0000001"
    assert result.canonical_map["1002"].matched_rule == "exact_key_match"
    assert result.review_rows == []


def test_price_gate_rejects_on_mrp_mismatch_even_when_declared_price_matches():
    same_date = date(2026, 5, 1)
    prior = {"1001": _mapped("1001", "CP0000001", supplier_code="0210")}
    result = run_stage4_resolution(
        product_rows=[
            _product_row("1001", supplier_code="0210", declared_price="100.00", mrp="155.00", effective_date=same_date),
            _product_row("1002", supplier_code="0210", declared_price="100.00", mrp="140.00", effective_date=same_date),
        ],
        normalized_rows=[_normalized_row("1001"), _normalized_row("1002")],
        prior_map=prior,
        run_month=RUN_MONTH,
        started_at="t",
    )

    # declared_price matches (100.00) but mrp differs (155.00 vs 140.00) -> does not attach.
    new_row = result.canonical_map["1002"]
    assert new_row.matched_rule == "new_canonical"
    assert len(result.review_rows) == 1
    assert result.review_rows[0].reason == "possible_supersession"
