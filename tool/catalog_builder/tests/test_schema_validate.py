from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.models import EnrichmentBeer
from tool.catalog_builder.schema_validate import (
    SchemaValidationError,
    check_no_duplicate_canonical_product_id_across_beers,
    validate_candidate_entry,
    validate_candidates_directory,
    validate_enrichment_repository,
)

_VALID_CANDIDATE = {
    "canonical_product_id": "CP0000002",
    "item_name_raw": "Kingfisher Premium Lager Beer-CAN 330ML(0202)",
    "display_name": "Kingfisher Premium Lager Beer-CAN 330ML",
    "suggested_beer_key": None,
    "name": None,
    "brewery": None,
    "style": None,
    "abv": None,
    "is_craft": None,
    "images": [],
}


def _write_yaml(path: Path, data) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# validate_candidate_entry
# ---------------------------------------------------------------------------


def test_valid_untouched_candidate_passes():
    candidate, reason_code, _ = validate_candidate_entry(_VALID_CANDIDATE, filename_canonical_product_id="CP0000002")
    assert reason_code is None
    assert candidate.canonical_product_id == "CP0000002"
    assert candidate.name is None
    assert candidate.images == []


def test_candidate_with_filled_curated_fields_passes():
    raw = dict(
        _VALID_CANDIDATE,
        suggested_beer_key="kingfisher_premium",
        name="Kingfisher Premium",
        brewery="United Breweries",
        style="lager",
        abv=4.8,
        is_craft=False,
        images=["photo.jpg"],
    )
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert reason_code is None
    assert candidate.abv == 4.8
    assert candidate.is_craft is False
    assert candidate.images == ["photo.jpg"]


def test_missing_required_key_is_rejected():
    raw = {k: v for k, v in _VALID_CANDIDATE.items() if k != "display_name"}
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "missing_required_keys"


def test_unsupported_extra_key_is_rejected():
    raw = dict(_VALID_CANDIDATE, extra_field="oops")
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "unsupported_keys"


def test_canonical_product_id_filename_mismatch_is_rejected():
    candidate, reason_code, _ = validate_candidate_entry(_VALID_CANDIDATE, filename_canonical_product_id="CP0000099")
    assert candidate is None
    assert reason_code == "canonical_product_id_does_not_match_filename"


def test_invalid_abv_type_is_rejected():
    raw = dict(_VALID_CANDIDATE, abv="strong")
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "invalid_abv"


def test_invalid_is_craft_type_is_rejected():
    raw = dict(_VALID_CANDIDATE, is_craft="yes")
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "invalid_is_craft"


def test_invalid_images_type_is_rejected():
    raw = dict(_VALID_CANDIDATE, images="not-a-list")
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "invalid_images"


def test_not_a_mapping_is_rejected():
    candidate, reason_code, _ = validate_candidate_entry(["nope"], filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "not_a_mapping"


def test_empty_string_curated_field_is_rejected_not_treated_as_unknown():
    # An empty string is not the same as an honest null — never silently
    # accepted as "no value" (Catalog Enrichment Playbook's own
    # never-guess discipline extends to "never silently launder a blank
    # into a valid absence" too).
    raw = dict(_VALID_CANDIDATE, brewery="")
    candidate, reason_code, _ = validate_candidate_entry(raw, filename_canonical_product_id="CP0000002")
    assert candidate is None
    assert reason_code == "invalid_brewery"


# ---------------------------------------------------------------------------
# validate_candidates_directory
# ---------------------------------------------------------------------------


def test_valid_directory_all_pass(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    _write_yaml(candidates_dir / "CP0000002.yaml", _VALID_CANDIDATE)

    accepted, rejected = validate_candidates_directory(candidates_dir)

    assert rejected == []
    assert len(accepted) == 1


def test_malformed_yaml_file_is_rejected_others_still_pass(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    _write_yaml(candidates_dir / "CP0000002.yaml", _VALID_CANDIDATE)
    (candidates_dir / "CP0000003.yaml").write_text("canonical_product_id: [unterminated", encoding="utf-8")

    accepted, rejected = validate_candidates_directory(candidates_dir)

    assert len(accepted) == 1
    assert len(rejected) == 1
    assert rejected[0].filename == "CP0000003.yaml"
    assert rejected[0].reason_code == "unparseable_yaml"


def test_missing_directory_raises():
    with pytest.raises(SchemaValidationError):
        validate_candidates_directory(Path("/nonexistent/candidates"))


def test_directory_validation_does_not_mutate_files(tmp_path: Path):
    candidates_dir = tmp_path / "candidates"
    candidates_dir.mkdir()
    file_path = candidates_dir / "CP0000002.yaml"
    _write_yaml(file_path, _VALID_CANDIDATE)
    before = file_path.read_text()

    validate_candidates_directory(candidates_dir)

    after = file_path.read_text()
    assert before == after


def test_real_generated_candidates_all_validate_cleanly():
    # End-to-end: the real 1,004 files this session's own generator
    # produced must all pass this validator with zero rejections.
    candidates_dir = Path("enrichment/candidates")
    if not candidates_dir.is_dir() or not any(candidates_dir.glob("*.yaml")):
        pytest.skip("enrichment/candidates/ not populated in this environment")

    accepted, rejected = validate_candidates_directory(candidates_dir)

    assert rejected == []
    assert len(accepted) >= 1000


# ---------------------------------------------------------------------------
# check_no_duplicate_canonical_product_id_across_beers
# ---------------------------------------------------------------------------


def _beer(beer_key: str, canonical_product_ids) -> EnrichmentBeer:
    return EnrichmentBeer(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name="X",
        brewery="Y",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )


def test_no_beers_is_fine():
    check_no_duplicate_canonical_product_id_across_beers([])


def test_non_conflicting_beers_is_fine():
    beers = [_beer("a", ["CP0000001"]), _beer("b", ["CP0000002", "CP0000003"])]
    check_no_duplicate_canonical_product_id_across_beers(beers)


def test_same_canonical_product_id_in_two_beers_raises():
    beers = [_beer("a", ["CP0000001"]), _beer("b", ["CP0000001"])]
    with pytest.raises(SchemaValidationError):
        check_no_duplicate_canonical_product_id_across_beers(beers)


def test_same_canonical_product_id_twice_in_the_same_beer_is_not_a_conflict():
    beers = [_beer("a", ["CP0000001", "CP0000001"])]
    check_no_duplicate_canonical_product_id_across_beers(beers)


# ---------------------------------------------------------------------------
# validate_enrichment_repository
# ---------------------------------------------------------------------------


def test_validate_enrichment_repository_on_real_scaffold():
    report = validate_enrichment_repository(Path("enrichment"))
    assert any(s.style_key == "lager" for s in report.styles)
    # enrichment/beers/ is no longer guaranteed empty -- a real founder
    # dry run created real Beer files. Only check what's still a real
    # invariant: whatever's there is structurally valid (no rejects) and
    # every beer_key is unique.
    assert report.rejected_beer_files == []
    assert len({b.beer_key for b in report.beers}) == len(report.beers)


def test_validate_enrichment_repository_detects_cross_file_conflict(tmp_path: Path):
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    _write_yaml(
        enrichment_dir / "styles.yaml",
        [{"style_key": "lager", "name": "Lager", "description": "Crisp"}],
    )
    beer_yaml = {
        "beer_key": "beer_a",
        "canonical_product_ids": ["CP0000001"],
        "name": "Beer A",
        "brewery": "Brewery A",
        "style": "lager",
        "abv": "unknown",
        "calories_per_100ml": "unknown",
    }
    _write_yaml(beers_dir / "beer_a.yaml", beer_yaml)
    conflicting = dict(beer_yaml, beer_key="beer_b")
    _write_yaml(beers_dir / "beer_b.yaml", conflicting)

    with pytest.raises(SchemaValidationError):
        validate_enrichment_repository(enrichment_dir)
