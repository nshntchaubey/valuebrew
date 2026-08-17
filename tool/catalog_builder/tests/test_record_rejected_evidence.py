from datetime import date
from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.create_beer import create_beer
from tool.catalog_builder.models import AttributionBlock
from tool.catalog_builder.record_rejected_evidence import (
    RecordRejectedEvidenceError,
    record_rejected_evidence,
)

_ABV = AttributionBlock(
    value=4.8,
    source_type="manufacturer",
    source_name="United Breweries official product page",
    observed_at=date(2026, 8, 10),
    observed_by="founder",
)


def _write_candidate(path: Path, canonical_product_id: str) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "canonical_product_id": canonical_product_id,
                "item_name_raw": "X",
                "display_name": "X",
                "suggested_beer_key": None,
                "name": None,
                "brewery": None,
                "style": None,
                "abv": None,
                "is_craft": None,
                "images": [],
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_enrichment_dir(tmp_path: Path) -> Path:
    """A minimal, real enrichment/ directory — one style, one beer —
    real enough for load_enrichment_directory to load without error, so
    record_rejected_evidence's beer_key/brewery cross-reference sets are
    built from a real load, not a shortcut."""
    enrichment_dir = tmp_path / "enrichment"
    enrichment_dir.mkdir()
    (enrichment_dir / "styles.yaml").write_text(
        yaml.safe_dump([{"style_key": "lager", "name": "Lager", "description": "Crisp"}]),
        encoding="utf-8",
    )

    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    candidate = _write_candidate(candidates_dir / "CP0000002.yaml", "CP0000002")

    beers_dir = enrichment_dir / "beers"
    create_beer(
        beer_key="kingfisher_premium",
        candidate_paths=[candidate],
        beers_dir=beers_dir,
        name="Kingfisher Premium",
        brewery="United Breweries",
        style="lager",
        abv=_ABV,
        calories_per_100ml=None,
    )
    return enrichment_dir


def _record(enrichment_dir: Path, rejected_evidence_path: Path, **overrides):
    kwargs = dict(
        subject_type="beer",
        subject_key="kingfisher_premium",
        field="abv",
        value_found="5.2",
        source_type="manual_observation",
        source_name="Madhuloka product listing, 21 Aug 2026",
        reason_type="wrong_variant",
        reason_detail="Listing's ABV is for the Strong variant, not this SKU.",
        observed_at="2026-08-17",
        observed_by="founder",
        recheck_after=None,
        rejected_evidence_path=rejected_evidence_path,
        enrichment_dir=enrichment_dir,
    )
    kwargs.update(overrides)
    return record_rejected_evidence(**kwargs)


def test_first_entry_creates_the_file_with_header_and_entry(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    written = _record(enrichment_dir, target)

    assert written == target
    text = written.read_text(encoding="utf-8")
    assert text.startswith("# enrichment/rejected_evidence.yaml")

    raw = yaml.safe_load(text)
    assert len(raw) == 1
    assert raw[0]["subject_key"] == "kingfisher_premium"
    assert raw[0]["reason_type"] == "wrong_variant"
    assert "recheck_after" not in raw[0]


def test_second_entry_appends_without_losing_the_first(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    _record(enrichment_dir, target)
    _record(
        enrichment_dir,
        target,
        field="calories_per_100ml",
        value_found="55",
        source_name="A different retailer listing",
        reason_type="imprecise_value",
        reason_detail="Rounded figure, not precise enough to cite.",
    )

    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert len(raw) == 2
    assert raw[0]["field"] == "abv"
    assert raw[1]["field"] == "calories_per_100ml"


def test_recheck_after_is_written_when_given(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    _record(enrichment_dir, target, reason_type="access_blocked", recheck_after="2027-01-01")

    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert raw[0]["recheck_after"] == date(2027, 1, 1)


def test_brewery_subject_resolves_against_a_real_beer_files_brewery(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    written = _record(
        enrichment_dir,
        target,
        subject_type="brewery",
        subject_key="United Breweries",
        field="brewery",
        value_found="United Breweries Ltd.",
        reason_type="imprecise_value",
    )

    raw = yaml.safe_load(written.read_text(encoding="utf-8"))
    assert raw[0]["subject_type"] == "brewery"
    assert raw[0]["subject_key"] == "United Breweries"


def test_dangling_beer_key_is_rejected(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    with pytest.raises(RecordRejectedEvidenceError):
        _record(enrichment_dir, target, subject_key="not_a_real_beer_key")

    assert not target.exists()


def test_dangling_brewery_is_rejected(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    with pytest.raises(RecordRejectedEvidenceError):
        _record(
            enrichment_dir,
            target,
            subject_type="brewery",
            subject_key="Not A Real Brewery",
            field="brewery",
        )

    assert not target.exists()


def test_invalid_reason_type_is_rejected(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    with pytest.raises(RecordRejectedEvidenceError):
        _record(enrichment_dir, target, reason_type="not_a_real_reason")

    assert not target.exists()


def test_duplicate_entry_is_rejected_append_only(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    _record(enrichment_dir, target)

    with pytest.raises(RecordRejectedEvidenceError):
        _record(enrichment_dir, target)

    # The duplicate attempt must not have corrupted the file — still
    # exactly the one entry from the first, successful call.
    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert len(raw) == 1


def test_a_different_reason_for_the_same_subject_and_field_is_not_a_duplicate(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    _record(enrichment_dir, target)
    _record(enrichment_dir, target, source_name="A second, independent source", reason_type="imprecise_value")

    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert len(raw) == 2


def test_malformed_existing_file_is_rejected_rather_than_silently_overwritten(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"
    target.write_text("{ this is not valid yaml", encoding="utf-8")

    with pytest.raises(RecordRejectedEvidenceError):
        _record(enrichment_dir, target)


# --- access_blocked's optional value_found (RC7.10/RC7.11) ---


def test_access_blocked_omission_succeeds(tmp_path: Path):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    written = _record(enrichment_dir, target, reason_type="access_blocked", value_found=None)

    raw = yaml.safe_load(written.read_text(encoding="utf-8"))
    assert raw[0]["reason_type"] == "access_blocked"
    assert "value_found" not in raw[0]


@pytest.mark.parametrize(
    "reason_type",
    [
        "wrong_variant",
        "wrong_product_line",
        "imprecise_value",
        "incompatible_unit",
        "conflicting_source_subordinate",
    ],
)
def test_omission_fails_for_every_other_reason_type(tmp_path: Path, reason_type: str):
    enrichment_dir = _write_enrichment_dir(tmp_path)
    target = tmp_path / "rejected_evidence.yaml"

    with pytest.raises(RecordRejectedEvidenceError):
        _record(enrichment_dir, target, reason_type=reason_type, value_found=None)

    assert not target.exists()
