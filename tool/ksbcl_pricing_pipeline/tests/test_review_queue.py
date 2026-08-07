from datetime import date
from decimal import Decimal

import pytest

from tool.ksbcl_pricing_pipeline.classification_models import ClassificationAuditRow, ReviewQueueEntry
from tool.ksbcl_pricing_pipeline.models import ProductRow
from tool.ksbcl_pricing_pipeline.review_queue import ReviewQueueError, _pending_by_item_code, update_review_queue


def _product_row(item_code, item_name_raw="Some Whisky Brand 750ML"):
    return ProductRow(
        item_code=item_code,
        item_name_raw=item_name_raw,
        supplier_name="Supplier",
        supplier_code="0210",
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


def _audit_row(item_code, tier, matched_signal_type="brand_name", matched_term="Budweiser"):
    return ClassificationAuditRow(
        run_month="2026-06",
        item_code=item_code,
        confidence_tier=tier,
        included=tier != "low",
        matched_signal_type=matched_signal_type,
        matched_term=matched_term,
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=False,
        classification_config_version="abc123def456",
    )


def _queue_entry(item_code, status="pending", first_flagged="2026-05", last_seen="2026-05", times_seen=1, config_version="v1"):
    return ReviewQueueEntry(
        item_code=item_code,
        item_name_raw="Original Snapshot Name",
        confidence_tier="low",
        matched_signal_type="brand_name",
        matched_term="Budweiser",
        first_flagged_run_month=first_flagged,
        last_seen_run_month=last_seen,
        times_seen_unreviewed=times_seen,
        review_status=status,
        reviewed_by=None,
        reviewed_at=None,
        decision_note=None,
        classification_config_version=config_version,
    )


def test_fresh_row_branch_creates_new_pending_episode():
    pairs = [(_product_row("1"), _audit_row("1", "low"))]
    result = update_review_queue([], pairs, "2026-06", "abc123def456")
    assert len(result) == 1
    entry = result[0]
    assert entry.review_status == "pending"
    assert entry.first_flagged_run_month == "2026-06"
    assert entry.last_seen_run_month == "2026-06"
    assert entry.times_seen_unreviewed == 1
    assert entry.item_name_raw == "Some Whisky Brand 750ML"


def test_refresh_branch_preserves_item_name_raw_snapshot_and_first_flagged():
    existing = [_queue_entry("1", first_flagged="2026-01", last_seen="2026-05", times_seen=2)]
    pairs = [(_product_row("1", item_name_raw="Renamed In A Later Run"), _audit_row("1", "low"))]
    result = update_review_queue(existing, pairs, "2026-06", "abc123def456")
    entry = result[0]
    assert entry.item_name_raw == "Original Snapshot Name"  # never refreshed
    assert entry.first_flagged_run_month == "2026-01"  # never touched by refresh
    assert entry.last_seen_run_month == "2026-06"
    assert entry.times_seen_unreviewed == 3
    assert entry.classification_config_version == "v1"  # ruleset when first flagged, unchanged


def test_refresh_branch_updates_matched_term_content_field():
    existing = [_queue_entry("1")]
    pairs = [(_product_row("1"), _audit_row("1", "low", matched_signal_type="supplier_corroboration_only", matched_term=None))]
    result = update_review_queue(existing, pairs, "2026-06", "abc123def456")
    entry = result[0]
    assert entry.matched_signal_type == "supplier_corroboration_only"
    assert entry.matched_term is None


def test_refresh_branch_same_month_rerun_is_a_true_no_op_on_temporal_fields():
    existing = [_queue_entry("1", first_flagged="2026-05", last_seen="2026-06", times_seen=2)]
    pairs = [(_product_row("1"), _audit_row("1", "low"))]
    result = update_review_queue(existing, pairs, "2026-06", "abc123def456")
    entry = result[0]
    assert entry.last_seen_run_month == "2026-06"
    assert entry.times_seen_unreviewed == 2  # unchanged


def test_refresh_branch_older_month_never_regresses_last_seen():
    existing = [_queue_entry("1", first_flagged="2026-05", last_seen="2026-07", times_seen=3)]
    pairs = [(_product_row("1"), _audit_row("1", "low"))]
    result = update_review_queue(existing, pairs, "2026-06", "abc123def456")
    entry = result[0]
    assert entry.last_seen_run_month == "2026-07"  # unchanged
    assert entry.times_seen_unreviewed == 4  # still incremented


def test_reconciliation_closes_pending_entry_now_high_or_medium():
    existing = [_queue_entry("1")]
    pairs = [(_product_row("1"), _audit_row("1", "medium"))]
    result = update_review_queue(existing, pairs, "2026-06", "abc123def456")
    assert len(result) == 1
    entry = result[0]
    assert entry.review_status == "auto_resolved_config_change"
    assert entry.reviewed_by is None
    assert entry.reviewed_at is None


def test_rule_3_pending_entry_absent_from_this_run_stays_untouched():
    existing = [_queue_entry("1", last_seen="2026-05", times_seen=1)]
    pairs = [(_product_row("2"), _audit_row("2", "low"))]  # a different item_code entirely
    result = update_review_queue(existing, pairs, "2026-06", "abc123def456")
    original = next(e for e in result if e.item_code == "1")
    assert original.last_seen_run_month == "2026-05"
    assert original.times_seen_unreviewed == 1


def test_reopened_episode_never_reads_prior_closed_episode_fields():
    # Prior episode: flagged 2026-01, resolved confirmed_beer in 2026-02.
    closed = ReviewQueueEntry(
        item_code="1",
        item_name_raw="Old Name",
        confidence_tier="low",
        matched_signal_type="brand_name",
        matched_term="Budweiser",
        first_flagged_run_month="2026-01",
        last_seen_run_month="2026-02",
        times_seen_unreviewed=5,
        review_status="confirmed_beer",
        reviewed_by="alice",
        reviewed_at="2026-02-01T00:00:00Z",
        decision_note="yes it's beer",
        classification_config_version="old-version",
    )
    pairs = [(_product_row("1", item_name_raw="New Name This Run"), _audit_row("1", "low"))]
    result = update_review_queue([closed], pairs, "2026-06", "new-version")

    # The closed episode is carried forward completely unchanged.
    old_episode = next(e for e in result if e.review_status == "confirmed_beer")
    assert old_episode == closed

    # The new episode is a full reset, independent of the old one.
    new_episode = next(e for e in result if e.review_status == "pending")
    assert new_episode.first_flagged_run_month == "2026-06"
    assert new_episode.last_seen_run_month == "2026-06"
    assert new_episode.times_seen_unreviewed == 1
    assert new_episode.item_name_raw == "New Name This Run"
    assert new_episode.classification_config_version == "new-version"


def test_duplicate_pending_entries_for_same_item_code_raise():
    duplicate_pending = [_queue_entry("1"), _queue_entry("1")]
    with pytest.raises(ReviewQueueError):
        _pending_by_item_code(duplicate_pending)
