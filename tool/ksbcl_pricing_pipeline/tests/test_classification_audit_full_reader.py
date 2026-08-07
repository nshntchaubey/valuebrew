from tool.ksbcl_pricing_pipeline.classification_audit_full_reader import read_classification_audit
from tool.ksbcl_pricing_pipeline.classification_models import CLASSIFICATION_AUDIT_FIELDS, ClassificationAuditRow
from tool.ksbcl_pricing_pipeline.io_writers import write_csv


def _row(item_code, is_duty_free=False, confidence_tier="high", matched_term="beer"):
    return ClassificationAuditRow(
        run_month="2026-06",
        item_code=item_code,
        confidence_tier=confidence_tier,
        included=True,
        matched_signal_type="style_keyword",
        matched_term=matched_term,
        exclusion_term_matched=None,
        supplier_known_beer_seller=False,
        is_duty_free=is_duty_free,
        classification_config_version="abc123",
    )


def test_round_trips_full_row(tmp_path):
    path = tmp_path / "classification_audit.csv"
    write_csv(path, CLASSIFICATION_AUDIT_FIELDS, [_row("1001").to_csv_row(), _row("1002", is_duty_free=True).to_csv_row()])

    result = read_classification_audit(path)

    assert set(result.keys()) == {"1001", "1002"}
    assert result["1001"].is_duty_free is False
    assert result["1002"].is_duty_free is True
    assert result["1001"].confidence_tier == "high"
    assert result["1001"].matched_term == "beer"


def test_handles_null_matched_term(tmp_path):
    path = tmp_path / "classification_audit.csv"
    write_csv(path, CLASSIFICATION_AUDIT_FIELDS, [_row("1001", matched_term=None).to_csv_row()])

    result = read_classification_audit(path)

    assert result["1001"].matched_term is None
