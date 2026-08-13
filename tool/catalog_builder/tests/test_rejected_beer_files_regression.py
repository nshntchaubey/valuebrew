"""Regression suite for the completeness gap the Milestone 1-6
implementation audit found: a malformed `enrichment/beers/*.yaml` file
used to disappear silently past the loading layer. Every test here
writes real files to a real temp `enrichment/` tree and runs them
through the actual production chain — `enrichment_reader.load_beers` ->
`validate_beer.compute_invalid_beer_keys` -> `join` ->
`apply_business_rules` -> `validate_cross_references` ->
`build_validation_report` — the same modules `build_catalog.py` will
eventually call, not a synthetic shortcut. Each test asserts the
rejection actually surfaces in the final report with filename, reason,
and stage.
"""

from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.business_rules import apply_business_rules
from tool.catalog_builder.cross_reference_validate import validate_cross_references
from tool.catalog_builder.enrichment_reader import load_beers, load_styles
from tool.catalog_builder.join import JoinError, join
from tool.catalog_builder.validate_beer import compute_invalid_beer_keys
from tool.catalog_builder.validation_report import build_validation_report

_STYLES = [{"style_key": "lager", "name": "Lager", "description": "Crisp"}]

_VALID_BEER = {
    "beer_key": "kingfisher_premium",
    "canonical_product_ids": ["CP0000002"],
    "name": "Kingfisher Premium",
    "brewery": "United Breweries",
    "style": "lager",
    "abv": "unknown",
    "calories_per_100ml": "unknown",
}


def _setup(tmp_path: Path):
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    styles_path = enrichment_dir / "styles.yaml"
    styles_path.write_text(yaml.safe_dump(_STYLES), encoding="utf-8")
    return enrichment_dir, beers_dir, styles_path


def _write(path: Path, data) -> None:
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(data), encoding="utf-8")


def _run_full_pipeline(enrichment_dir: Path, beers_dir: Path, styles_path: Path, rows=()):
    styles = load_styles(styles_path)
    style_keys = {s.style_key for s in styles}
    beers, rejected_beer_files = load_beers(beers_dir, style_keys)
    invalid_beer_keys = compute_invalid_beer_keys(beers_dir, styles_path)

    join_result = join(list(rows), contaminated_row_ids=set(), beers=beers)
    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)
    report = build_validation_report(
        beers, join_result, business_result, cross_ref_result, rejected_beer_files=rejected_beer_files
    )
    return report


# ---------------------------------------------------------------------------
# 1. Malformed YAML
# ---------------------------------------------------------------------------


def test_malformed_yaml_appears_in_final_report(tmp_path: Path):
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    _write(beers_dir / "broken.yaml", "beer_key: [unterminated")

    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path)

    assert len(report.rejected_beer_files) == 1
    entry = report.rejected_beer_files[0]
    assert entry.filename == "broken.yaml"
    assert entry.stage == "enrichment_schema"
    assert entry.reason_code == "unparseable_yaml"
    assert "unparseable_yaml" in report.rejection_reasons
    assert report.beers_rejected == 1


# ---------------------------------------------------------------------------
# 2. Missing required field
# ---------------------------------------------------------------------------


def test_missing_required_field_appears_in_final_report(tmp_path: Path):
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    beer = {k: v for k, v in _VALID_BEER.items() if k != "brewery"}
    _write(beers_dir / "kingfisher_premium.yaml", beer)

    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path)

    assert len(report.rejected_beer_files) == 1
    entry = report.rejected_beer_files[0]
    assert entry.filename == "kingfisher_premium.yaml"
    assert entry.reason_code == "missing_required_keys"
    assert entry.stage == "enrichment_schema"
    assert "missing_required_keys" in report.rejection_reasons


# ---------------------------------------------------------------------------
# 3. Duplicate beer_key
# ---------------------------------------------------------------------------


def test_duplicate_beer_key_appears_via_both_pathways(tmp_path: Path):
    # "kingfisher_premium.yaml" is valid on its own. "stray.yaml"
    # declares the SAME beer_key in its content but lives under a
    # different filename -- it fails its own structural check
    # (rejected_beer_files), AND its raw content still collides with
    # the real file, so compute_invalid_beer_keys correctly flags the
    # real file too (business_rules "invalid_beer_entity").
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    _write(beers_dir / "kingfisher_premium.yaml", _VALID_BEER)
    stray = dict(_VALID_BEER, canonical_product_ids=["CP0000099"])
    _write(beers_dir / "stray.yaml", stray)

    row = _real_row("CP0000002")
    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path, rows=[row])

    # stray.yaml: rejected at the loading layer (filename != its own
    # declared beer_key).
    assert any(e.filename == "stray.yaml" and e.reason_code == "beer_key_does_not_match_filename" for e in report.rejected_beer_files)

    # kingfisher_premium.yaml: structurally valid on its own, but
    # correctly caught as an invalid Beer entity because of the
    # collision -- its SKU must not silently publish.
    assert report.skus_included == 0
    assert "invalid_beer_entity" in report.rejection_reasons
    assert any(d.beer_key == "kingfisher_premium" and d.reason_code == "invalid_beer_entity" for d in report.rejected_details)


# ---------------------------------------------------------------------------
# 4. Duplicate canonical_product_id
# ---------------------------------------------------------------------------


def test_duplicate_canonical_product_id_within_one_beer_appears_in_report(tmp_path: Path):
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_VALID_BEER, canonical_product_ids=["CP0000002", "CP0000002"])
    _write(beers_dir / "kingfisher_premium.yaml", beer)

    row = _real_row("CP0000002")
    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path, rows=[row])

    assert report.skus_included == 0
    assert "invalid_beer_entity" in report.rejection_reasons
    assert report.beers_rejected == 1


def test_duplicate_canonical_product_id_across_beers_aborts_the_build(tmp_path: Path):
    # Never silently disappearing also means never silently *succeeding*
    # -- this must abort loudly, not produce a report that pretends
    # everything is fine.
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    _write(beers_dir / "beer_a.yaml", dict(_VALID_BEER, beer_key="beer_a"))
    _write(beers_dir / "beer_b.yaml", dict(_VALID_BEER, beer_key="beer_b"))

    styles = load_styles(styles_path)
    style_keys = {s.style_key for s in styles}
    beers, _ = load_beers(beers_dir, style_keys)

    with pytest.raises(JoinError):
        join([], contaminated_row_ids=set(), beers=beers)


# ---------------------------------------------------------------------------
# 5. Invalid style
# ---------------------------------------------------------------------------


def test_invalid_style_appears_in_final_report(tmp_path: Path):
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_VALID_BEER, style="nonexistent_style")
    _write(beers_dir / "kingfisher_premium.yaml", beer)

    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path)

    assert len(report.rejected_beer_files) == 1
    entry = report.rejected_beer_files[0]
    assert entry.filename == "kingfisher_premium.yaml"
    assert entry.reason_code == "unresolved_style_reference"
    assert "unresolved_style_reference" in report.rejection_reasons


# ---------------------------------------------------------------------------
# 6. Invalid schema (unsupported key)
# ---------------------------------------------------------------------------


def test_unsupported_key_appears_in_final_report(tmp_path: Path):
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_VALID_BEER, gtin="8905002180007")
    _write(beers_dir / "kingfisher_premium.yaml", beer)

    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path)

    assert len(report.rejected_beer_files) == 1
    entry = report.rejected_beer_files[0]
    assert entry.reason_code == "unsupported_keys"
    assert "unsupported_keys" in report.rejection_reasons


# ---------------------------------------------------------------------------
# Mixed batch: nothing lost among several simultaneous problems
# ---------------------------------------------------------------------------


def test_multiple_simultaneous_rejections_all_appear_none_lost(tmp_path: Path):
    enrichment_dir, beers_dir, styles_path = _setup(tmp_path)
    _write(beers_dir / "broken.yaml", "beer_key: [unterminated")
    _write(beers_dir / "bad_style.yaml", dict(_VALID_BEER, beer_key="bad_style", style="nope", canonical_product_ids=["CP0000010"]))
    real_abv = {
        "value": 4.8,
        "source_type": "manufacturer",
        "source_name": "United Breweries official product page",
        "observed_at": "2026-08-13",
        "observed_by": "founder",
    }
    _write(
        beers_dir / "kingfisher_premium.yaml", dict(_VALID_BEER, abv=real_abv, calories_per_100ml=real_abv)
    )  # valid, publishable

    row = _real_row("CP0000002")
    report = _run_full_pipeline(enrichment_dir, beers_dir, styles_path, rows=[row])

    filenames = {e.filename for e in report.rejected_beer_files}
    assert filenames == {"broken.yaml", "bad_style.yaml"}
    assert report.skus_included == 1  # kingfisher_premium's SKU still publishes
    assert report.beers_rejected == 2  # broken.yaml + bad_style.yaml
    assert report.beers_included == 1


def _real_row(canonical_product_id: str):
    from datetime import date
    from decimal import Decimal

    from tool.catalog_builder.models import BeerMasterRow

    return BeerMasterRow(
        canonical_product_id=canonical_product_id,
        representative_item_code="2020900211",
        item_name_raw="Kingfisher Premium Lager Beer-CAN 330ML(0202)",
        display_name="Kingfisher Premium Lager Beer-CAN 330ML",
        normalized_name_key="kingfisher premium lager beer-can 330ml",
        pack_size_ml=330,
        pack_count=None,
        container_type="can",
        declared_price=Decimal("100.00"),
        landed_cost=Decimal("200.00"),
        ksbcl_selling_price=Decimal("210.00"),
        mrp=Decimal("100.00"),
        effective_date=date(2026, 6, 1),
        status="LIVE",
        delisted_run_month=None,
        classification_confidence="high",
        classification_matched_on="style_keyword:beer",
        gtin=None,
        gtin_confidence=None,
        source_pdf_reference="x.pdf",
        first_seen_run_month="2026-06",
        last_updated_run_month="2026-06",
    )
