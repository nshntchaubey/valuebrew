from datetime import date
from decimal import Decimal

import pytest

from tool.ksbcl_pricing_pipeline.canonical_models import CanonicalMapRow
from tool.ksbcl_pricing_pipeline.classification_models import ClassificationAuditRow
from tool.ksbcl_pricing_pipeline.history_models import MasterRow, PriceHistoryRow
from tool.ksbcl_pricing_pipeline.models import ProductRow
from tool.ksbcl_pricing_pipeline.normalize_models import NormalizedRow
from tool.ksbcl_pricing_pipeline.stage5_resolve import Stage5ValidationError, run_stage5

RUN_MONTH = "2026-06"
OBSERVED_AT = "2026-08-07T00:00:00Z"
SOURCE_PDF = "pricing_data/raw_pdfs/2026-06/x.pdf"


def _product_row(item_code, mrp="100.00", declared_price="100.00", effective_date=date(2026, 6, 1)):
    return ProductRow(
        item_code=item_code,
        item_name_raw="Kingfisher Strong Beer 650ML",
        supplier_name="United Breweries",
        supplier_code="0210",
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


def _normalized_row(item_code):
    return NormalizedRow(
        run_month=RUN_MONTH,
        item_code=item_code,
        display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        normalization_rule_version="v1",
    )


def _audit_row(item_code, is_duty_free=False, confidence_tier="high"):
    return ClassificationAuditRow(
        run_month=RUN_MONTH,
        item_code=item_code,
        confidence_tier=confidence_tier,
        included=True,
        matched_signal_type="style_keyword",
        matched_term="beer",
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=is_duty_free,
        classification_config_version="abc123",
    )


def _map_row(item_code, cid, status="LIVE", first_seen="2026-06", last_seen="2026-06"):
    return CanonicalMapRow(
        ksbcl_item_code=item_code,
        canonical_product_id=cid,
        supplier_name="United Breweries",
        supplier_code="0210",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        match_confidence="unreviewed",
        matched_rule="new_canonical",
        item_status=status,
        first_seen_run_month=first_seen,
        last_seen_run_month=last_seen,
    )


def _run(product_rows, canonical_map, classification_audit=None, normalized_rows=None,
         prior_history_rows=None, prior_master_retail=None, prior_master_duty_free=None):
    # `is None` throughout, deliberately not `or` — an explicitly-passed empty
    # dict (e.g. testing "no normalized_rows this run") must not be silently
    # replaced by the auto-generated default, which `{} or default` would do.
    if classification_audit is None:
        classification_audit = {p.item_code: _audit_row(p.item_code) for p in product_rows}
    if normalized_rows is None:
        normalized_rows = {p.item_code: _normalized_row(p.item_code) for p in product_rows}
    return run_stage5(
        product_rows=product_rows,
        canonical_map=canonical_map,
        classification_audit=classification_audit,
        normalized_rows=normalized_rows,
        prior_history_rows=prior_history_rows if prior_history_rows is not None else [],
        prior_master_retail=prior_master_retail if prior_master_retail is not None else {},
        prior_master_duty_free=prior_master_duty_free if prior_master_duty_free is not None else {},
        run_month=RUN_MONTH,
        started_at="t",
        observed_at=OBSERVED_AT,
        source_pdf_reference=SOURCE_PDF,
    )


def test_bootstrap_first_sighting_creates_initial_backfill_and_live_master_row():
    product_rows = [_product_row("1001")]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}

    result = _run(product_rows, canonical_map)

    assert len(result.new_history_rows) == 1
    assert result.new_history_rows[0].event_type == "INITIAL_BACKFILL"
    assert result.new_history_rows[0].previous_mrp is None

    master_row = result.master_retail["CP0000001"]
    assert master_row.status == "LIVE"
    assert master_row.representative_item_code == "1001"
    assert master_row.first_seen_run_month == RUN_MONTH


def test_unchanged_price_writes_no_history_row_but_updates_master():
    product_rows = [_product_row("1001", mrp="100.00")]
    canonical_map = {"1001": _map_row("1001", "CP0000001", first_seen="2026-05", last_seen="2026-06")}
    prior_history = [
        PriceHistoryRow(
            history_id="H00000001", ksbcl_item_code="1001", event_type="INITIAL_BACKFILL",
            effective_date="2026-06-01", effective_date_raw="01-Jun-26",
            declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
            ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
            previous_declared_price=None, previous_landed_cost=None,
            previous_ksbcl_selling_price=None, previous_mrp=None, previous_effective_date=None,
            observed_run_month="2026-05", observed_at=OBSERVED_AT, source_pdf_reference=SOURCE_PDF,
        )
    ]
    prior_master = {"CP0000001": MasterRow(
        canonical_product_id="CP0000001", representative_item_code="1001",
        item_name_raw="Kingfisher Strong Beer 650ML", display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key="kingfisher strong beer 650ml", pack_size_ml=Decimal("650"), pack_count=None,
        container_type="bottle", declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"), effective_date="2026-06-01",
        status="LIVE", delisted_run_month=None, classification_confidence="high",
        classification_matched_on="style_keyword:beer", gtin=None, gtin_confidence=None,
        source_pdf_reference=SOURCE_PDF, first_seen_run_month="2026-05", last_updated_run_month="2026-05",
    )}

    result = _run(product_rows, canonical_map, prior_history_rows=prior_history, prior_master_retail=prior_master)

    assert result.new_history_rows == []
    assert result.master_retail["CP0000001"].last_updated_run_month == RUN_MONTH
    assert result.master_retail["CP0000001"].first_seen_run_month == "2026-05"


def test_later_effective_date_is_price_change():
    product_rows = [_product_row("1001", mrp="200.00", effective_date=date(2026, 6, 15))]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}
    prior_history = [PriceHistoryRow(
        history_id="H00000001", ksbcl_item_code="1001", event_type="INITIAL_BACKFILL",
        effective_date="2026-05-01", effective_date_raw="01-May-26",
        declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
        previous_declared_price=None, previous_landed_cost=None,
        previous_ksbcl_selling_price=None, previous_mrp=None, previous_effective_date=None,
        observed_run_month="2026-05", observed_at=OBSERVED_AT, source_pdf_reference=SOURCE_PDF,
    )]

    result = _run(product_rows, canonical_map, prior_history_rows=prior_history)

    assert len(result.new_history_rows) == 1
    row = result.new_history_rows[0]
    assert row.event_type == "PRICE_CHANGE"
    assert row.previous_mrp == Decimal("100.00")
    assert row.mrp == Decimal("200.00")


def test_same_effective_date_price_differs_is_correction():
    product_rows = [_product_row("1001", mrp="200.00", effective_date=date(2026, 5, 1))]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}
    prior_history = [PriceHistoryRow(
        history_id="H00000001", ksbcl_item_code="1001", event_type="INITIAL_BACKFILL",
        effective_date="2026-05-01", effective_date_raw="01-May-26",
        declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
        previous_declared_price=None, previous_landed_cost=None,
        previous_ksbcl_selling_price=None, previous_mrp=None, previous_effective_date=None,
        observed_run_month="2026-05", observed_at=OBSERVED_AT, source_pdf_reference=SOURCE_PDF,
    )]

    result = _run(product_rows, canonical_map, prior_history_rows=prior_history)

    assert result.new_history_rows[0].event_type == "CORRECTION"


def test_earlier_effective_date_is_correction_regardless_of_price():
    product_rows = [_product_row("1001", mrp="100.00", effective_date=date(2026, 4, 1))]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}
    prior_history = [PriceHistoryRow(
        history_id="H00000001", ksbcl_item_code="1001", event_type="INITIAL_BACKFILL",
        effective_date="2026-05-01", effective_date_raw="01-May-26",
        declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
        previous_declared_price=None, previous_landed_cost=None,
        previous_ksbcl_selling_price=None, previous_mrp=None, previous_effective_date=None,
        observed_run_month="2026-05", observed_at=OBSERVED_AT, source_pdf_reference=SOURCE_PDF,
    )]

    result = _run(product_rows, canonical_map, prior_history_rows=prior_history)

    assert result.new_history_rows[0].event_type == "CORRECTION"


def test_representative_selection_newest_effective_date_wins():
    product_rows = [
        _product_row("1001", effective_date=date(2020, 1, 1)),
        _product_row("1002", effective_date=date(2025, 1, 1)),
    ]
    canonical_map = {
        "1001": _map_row("1001", "CP0000001"),
        "1002": _map_row("1002", "CP0000001"),
    }

    result = _run(product_rows, canonical_map)

    assert result.master_retail["CP0000001"].representative_item_code == "1002"


def test_representative_selection_tie_break_lowest_item_code():
    product_rows = [
        _product_row("2002", effective_date=date(2025, 1, 1)),
        _product_row("1001", effective_date=date(2025, 1, 1)),
    ]
    canonical_map = {
        "2002": _map_row("2002", "CP0000001"),
        "1001": _map_row("1001", "CP0000001"),
    }

    result = _run(product_rows, canonical_map)

    assert result.master_retail["CP0000001"].representative_item_code == "1001"


def test_duty_free_item_routes_to_duty_free_file_only():
    product_rows = [_product_row("1001")]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}
    classification_audit = {"1001": _audit_row("1001", is_duty_free=True)}

    result = _run(product_rows, canonical_map, classification_audit=classification_audit)

    assert "CP0000001" in result.master_duty_free
    assert "CP0000001" not in result.master_retail


def test_canonical_product_with_both_channels_gets_two_rows():
    product_rows = [_product_row("1001"), _product_row("1002")]
    canonical_map = {
        "1001": _map_row("1001", "CP0000001"),
        "1002": _map_row("1002", "CP0000001"),
    }
    classification_audit = {
        "1001": _audit_row("1001", is_duty_free=False),
        "1002": _audit_row("1002", is_duty_free=True),
    }

    result = _run(product_rows, canonical_map, classification_audit=classification_audit)

    assert result.master_retail["CP0000001"].representative_item_code == "1001"
    assert result.master_duty_free["CP0000001"].representative_item_code == "1002"


def test_delisting_freezes_master_row_and_sets_delisted_run_month():
    canonical_map = {"1001": _map_row("1001", "CP0000001", status="DELISTED")}
    prior_master = {"CP0000001": MasterRow(
        canonical_product_id="CP0000001", representative_item_code="1001",
        item_name_raw="Kingfisher Strong Beer 650ML", display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key="kingfisher strong beer 650ml", pack_size_ml=Decimal("650"), pack_count=None,
        container_type="bottle", declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"), effective_date="2026-05-01",
        status="LIVE", delisted_run_month=None, classification_confidence="high",
        classification_matched_on="style_keyword:beer", gtin=None, gtin_confidence=None,
        source_pdf_reference=SOURCE_PDF, first_seen_run_month="2026-05", last_updated_run_month="2026-05",
    )}

    result = _run([], {"1001": canonical_map["1001"]}, prior_master_retail=prior_master)

    row = result.master_retail["CP0000001"]
    assert row.status == "DELISTED"
    assert row.delisted_run_month == RUN_MONTH
    assert row.mrp == Decimal("100.00")  # frozen, not blanked (recorded product decision, §6.3)
    assert row.representative_item_code == "1001"  # frozen from prior row


def test_already_delisted_keeps_original_delisted_run_month():
    canonical_map = {"1001": _map_row("1001", "CP0000001", status="DELISTED")}
    prior_master = {"CP0000001": MasterRow(
        canonical_product_id="CP0000001", representative_item_code="1001",
        item_name_raw="x", display_name="x", normalized_name_key="x", pack_size_ml=Decimal("650"),
        pack_count=None, container_type="bottle", declared_price=Decimal("100.00"),
        landed_cost=Decimal("100.00"), ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
        effective_date="2026-04-01", status="DELISTED", delisted_run_month="2026-05",
        classification_confidence="high", classification_matched_on="style_keyword:beer",
        gtin=None, gtin_confidence=None, source_pdf_reference=SOURCE_PDF,
        first_seen_run_month="2026-04", last_updated_run_month="2026-05",
    )}

    result = _run([], canonical_map, prior_master_retail=prior_master)

    assert result.master_retail["CP0000001"].delisted_run_month == "2026-05"
    assert result.master_retail["CP0000001"].last_updated_run_month == RUN_MONTH


def test_reappearance_clears_delisted_run_month_and_recomputes():
    product_rows = [_product_row("1001", mrp="199.00", effective_date=date(2026, 6, 1))]
    canonical_map = {"1001": _map_row("1001", "CP0000001", status="LIVE")}
    prior_master = {"CP0000001": MasterRow(
        canonical_product_id="CP0000001", representative_item_code="1001",
        item_name_raw="x", display_name="x", normalized_name_key="x", pack_size_ml=Decimal("650"),
        pack_count=None, container_type="bottle", declared_price=Decimal("100.00"),
        landed_cost=Decimal("100.00"), ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
        effective_date="2026-04-01", status="DELISTED", delisted_run_month="2026-05",
        classification_confidence="high", classification_matched_on="style_keyword:beer",
        gtin=None, gtin_confidence=None, source_pdf_reference=SOURCE_PDF,
        first_seen_run_month="2026-04", last_updated_run_month="2026-05",
    )}

    result = _run(product_rows, canonical_map, prior_master_retail=prior_master)

    row = result.master_retail["CP0000001"]
    assert row.status == "LIVE"
    assert row.delisted_run_month is None
    assert row.mrp == Decimal("199.00")
    assert row.first_seen_run_month == "2026-04"  # never resets


def test_live_item_not_in_normalized_rows_is_ineligible_and_freezes_existing_row():
    product_rows = [_product_row("1001")]
    canonical_map = {"1001": _map_row("1001", "CP0000001", status="LIVE")}
    prior_master = {"CP0000001": MasterRow(
        canonical_product_id="CP0000001", representative_item_code="1001",
        item_name_raw="x", display_name="x", normalized_name_key="x", pack_size_ml=Decimal("650"),
        pack_count=None, container_type="bottle", declared_price=Decimal("50.00"),
        landed_cost=Decimal("50.00"), ksbcl_selling_price=Decimal("50.00"), mrp=Decimal("50.00"),
        effective_date="2026-05-01", status="LIVE", delisted_run_month=None,
        classification_confidence="high", classification_matched_on="style_keyword:beer",
        gtin=None, gtin_confidence=None, source_pdf_reference=SOURCE_PDF,
        first_seen_run_month="2026-05", last_updated_run_month="2026-05",
    )}

    result = _run(product_rows, canonical_map, normalized_rows={}, prior_master_retail=prior_master)

    row = result.master_retail["CP0000001"]
    assert row.status == "DELISTED"
    assert row.mrp == Decimal("50.00")  # frozen at old value, never recomputed from unclassifiable data
    assert result.summary.representative_ineligible_channels == 1


def test_ordinary_single_channel_delisting_does_not_count_as_ineligible_when_other_channel_is_live():
    """Regression: a canonical product with a LIVE duty-free item_code and
    a DELISTED retail item_code is an ordinary retail-channel delisting
    (§6.1), not a §4 "representative ineligible" case — the two must not
    be conflated just because *something* on the canonical product is LIVE."""
    product_rows = [_product_row("2001")]  # only the duty-free item is live this run
    canonical_map = {
        "1001": _map_row("1001", "CP0000001", status="DELISTED"),  # retail, gone
        "2001": _map_row("2001", "CP0000001", status="LIVE"),  # duty-free, still live
    }
    classification_audit = {"2001": _audit_row("2001", is_duty_free=True)}
    normalized_rows = {"2001": _normalized_row("2001")}
    prior_master_retail = {"CP0000001": MasterRow(
        canonical_product_id="CP0000001", representative_item_code="1001",
        item_name_raw="x", display_name="x", normalized_name_key="x", pack_size_ml=Decimal("650"),
        pack_count=None, container_type="bottle", declared_price=Decimal("50.00"),
        landed_cost=Decimal("50.00"), ksbcl_selling_price=Decimal("50.00"), mrp=Decimal("50.00"),
        effective_date="2026-05-01", status="LIVE", delisted_run_month=None,
        classification_confidence="high", classification_matched_on="style_keyword:beer",
        gtin=None, gtin_confidence=None, source_pdf_reference=SOURCE_PDF,
        first_seen_run_month="2026-05", last_updated_run_month="2026-05",
    )}

    result = _run(
        product_rows, canonical_map, classification_audit=classification_audit,
        normalized_rows=normalized_rows, prior_master_retail=prior_master_retail,
    )

    assert result.master_retail["CP0000001"].status == "DELISTED"
    assert result.master_duty_free["CP0000001"].status == "LIVE"
    assert result.summary.representative_ineligible_channels == 0


def test_history_diff_ignores_item_codes_not_yet_known_to_canonical_map():
    # "9999" is a real structured row this run, but Stage 4 hasn't resolved
    # it yet (not in canonical_map) — Stage 5's row set excludes it (§5.1).
    product_rows = [_product_row("1001"), _product_row("9999")]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}

    result = _run(product_rows, canonical_map)

    assert {row.ksbcl_item_code for row in result.new_history_rows} == {"1001"}


def test_zero_rows_in_canonical_map_raises_validation_error():
    with pytest.raises(Stage5ValidationError):
        _run([_product_row("1001")], {})


def test_join_integrity_failure_when_live_item_missing_from_structured_rows():
    canonical_map = {"1001": _map_row("1001", "CP0000001", status="LIVE")}

    with pytest.raises(Stage5ValidationError):
        _run([], canonical_map)


def test_delisted_item_absent_from_structured_rows_is_not_an_error():
    canonical_map = {
        "1001": _map_row("1001", "CP0000001", status="LIVE"),
        "9999": _map_row("9999", "CP0000005", status="DELISTED"),
    }
    product_rows = [_product_row("1001")]

    result = _run(product_rows, canonical_map)

    assert "CP0000001" in result.master_retail
    assert "CP0000005" not in result.master_retail  # never had a row, nothing to freeze


def test_rerun_of_same_month_produces_zero_duplicate_history_rows():
    """The exact regression this document's rerun-determinism section
    exists to prevent: a genuine PRICE_CHANGE recorded once must not be
    recorded again on a rerun of the same month."""
    product_rows = [_product_row("1001", mrp="200.00", effective_date=date(2026, 6, 15))]
    canonical_map = {"1001": _map_row("1001", "CP0000001")}
    prior_history = [PriceHistoryRow(
        history_id="H00000001", ksbcl_item_code="1001", event_type="INITIAL_BACKFILL",
        effective_date="2026-05-01", effective_date_raw="01-May-26",
        declared_price=Decimal("100.00"), landed_cost=Decimal("100.00"),
        ksbcl_selling_price=Decimal("100.00"), mrp=Decimal("100.00"),
        previous_declared_price=None, previous_landed_cost=None,
        previous_ksbcl_selling_price=None, previous_mrp=None, previous_effective_date=None,
        observed_run_month="2026-05", observed_at=OBSERVED_AT, source_pdf_reference=SOURCE_PDF,
    )]

    first = _run(product_rows, canonical_map, prior_history_rows=prior_history)
    assert len(first.new_history_rows) == 1  # sanity: a real event happened

    # Rerun: prior_history now includes the row the first run just wrote.
    combined_history = prior_history + first.new_history_rows
    second = _run(product_rows, canonical_map, prior_history_rows=combined_history)

    assert second.new_history_rows == []
