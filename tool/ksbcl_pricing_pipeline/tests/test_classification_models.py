from tool.ksbcl_pricing_pipeline.classification_models import (
    ClassificationAuditRow,
    ClassificationRunSummary,
    KnownTermRow,
    NewEntityRow,
    ReviewQueueEntry,
)


def test_audit_row_csv_booleans_are_lowercase_strings():
    row = ClassificationAuditRow(
        run_month="2026-06",
        item_code="10300901",
        confidence_tier="high",
        included=True,
        matched_signal_type="style_keyword",
        matched_term="beer",
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=False,
        classification_config_version="abc123def456",
    )
    d = row.to_csv_row()
    assert d["included"] == "true"
    assert d["supplier_known_beer_seller"] == "false"
    assert d["is_duty_free"] == "false"
    assert d["matched_term"] == "beer"
    assert d["exclusion_term_matched"] is None


def test_new_entity_row_csv():
    row = NewEntityRow(
        entity_type="brand_name", value="Kingfisher", sample_item_code="123", sample_item_name_raw="Kingfisher Beer"
    )
    assert row.to_csv_row() == {
        "entity_type": "brand_name",
        "value": "Kingfisher",
        "sample_item_code": "123",
        "sample_item_name_raw": "Kingfisher Beer",
    }


def test_known_term_row_csv():
    row = KnownTermRow(
        entity_type="supplier_code", value="0210", first_seen_run_month="2026-06", last_seen_run_month="2026-06", times_seen=1
    )
    assert row.to_csv_row()["times_seen"] == 1


def test_review_queue_entry_defaults_none_fields():
    row = ReviewQueueEntry(
        item_code="123",
        item_name_raw="Some Whisky",
        confidence_tier="low",
        matched_signal_type="brand_name",
        matched_term="Budweiser",
        first_flagged_run_month="2026-06",
        last_seen_run_month="2026-06",
        times_seen_unreviewed=1,
        review_status="pending",
        reviewed_by=None,
        reviewed_at=None,
        decision_note=None,
        classification_config_version="abc123def456",
    )
    d = row.to_csv_row()
    assert d["reviewed_by"] is None
    assert d["review_status"] == "pending"


def test_run_summary_defaults_and_json():
    summary = ClassificationRunSummary(run_month="2026-06", started_at="2026-06-01T00:00:00+00:00")
    d = summary.to_json_dict()
    assert d["status"] == "running"
    assert d["counts_by_tier"] == {"high": 0, "medium": 0, "low": 0}
    assert d["matched_signal_type_counts"] == {
        "style_keyword": 0,
        "brand_name": 0,
        "supplier_corroboration_only": 0,
    }
    assert d["is_bootstrap_run"] is False
