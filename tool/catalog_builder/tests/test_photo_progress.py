from datetime import date

from tool.catalog_builder.models import AttributionBlock, EnrichmentBeer
from tool.catalog_builder.photo_progress import build_progress_report
from tool.catalog_builder.validation_report import ValidationReport

_ABV = AttributionBlock(
    value=5.0, source_type="manufacturer", source_name="X", observed_at=date(2026, 8, 13), observed_by="founder"
)


def _beer(beer_key, canonical_product_ids, *, style="lager", abv=None, calories_per_100ml=None) -> EnrichmentBeer:
    return EnrichmentBeer(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name=beer_key,
        brewery="Y",
        style=style,
        abv=abv,
        calories_per_100ml=calories_per_100ml,
    )


def _report(*, included, skus_joined, skus_unenriched, skus_rejected) -> ValidationReport:
    return ValidationReport(
        skus_joined=skus_joined,
        skus_unenriched=skus_unenriched,
        skus_included=len(included),
        skus_rejected=skus_rejected,
        missing_candidate_references=0,
        orphan_sku_references=0,
        beers_included=0,
        beers_rejected=0,
        rejection_reasons={},
        included_canonical_product_ids=included,
    )


def test_beer_with_all_skus_included_is_fully_publishable():
    beers = [_beer("a", ["CP1", "CP2"])]
    report = _report(included=["CP1", "CP2"], skus_joined=2, skus_unenriched=0, skus_rejected=0)

    progress = build_progress_report(beers, report)

    assert progress.fully_publishable_beers == ["a"]
    assert progress.awaiting_photos_beers == []
    assert progress.awaiting_identity_resolution_beers == []
    assert progress.structurally_blocked_only_beers == []


def test_beer_with_unknown_style_is_awaiting_identity_resolution():
    beers = [_beer("a", ["CP1"], style=None)]
    report = _report(included=[], skus_joined=1, skus_unenriched=0, skus_rejected=1)

    progress = build_progress_report(beers, report)

    assert progress.awaiting_identity_resolution_beers == ["a"]
    assert progress.awaiting_photos_beers == []


def test_beer_missing_abv_with_known_style_is_awaiting_photos():
    beers = [_beer("a", ["CP1"], style="lager", abv=None)]
    report = _report(included=[], skus_joined=1, skus_unenriched=0, skus_rejected=1)

    progress = build_progress_report(beers, report)

    assert progress.awaiting_photos_beers == ["a"]
    assert progress.awaiting_identity_resolution_beers == []


def test_beer_fully_evidenced_but_partially_included_is_structurally_blocked_only():
    # abv and calories both known, style known, but not every SKU made
    # it into included_canonical_product_ids -- e.g. blocked by
    # unsupported_package_type, which no photo or identity work fixes.
    beers = [_beer("a", ["CP1", "CP2"], abv=_ABV, calories_per_100ml=_ABV)]
    report = _report(included=["CP1"], skus_joined=2, skus_unenriched=0, skus_rejected=1)

    progress = build_progress_report(beers, report)

    assert progress.structurally_blocked_only_beers == ["a"]
    assert progress.fully_publishable_beers == []
    assert progress.awaiting_photos_beers == []


def test_every_beer_counted_exactly_once():
    beers = [
        _beer("full", ["CP1"]),
        _beer("identity", ["CP2"], style=None),
        _beer("photos", ["CP3"], abv=None),
        _beer("structural", ["CP4"], abv=_ABV, calories_per_100ml=_ABV),
    ]
    report = _report(included=["CP1"], skus_joined=4, skus_unenriched=0, skus_rejected=3)

    progress = build_progress_report(beers, report)

    all_bucketed = (
        progress.fully_publishable_beers
        + progress.awaiting_identity_resolution_beers
        + progress.awaiting_photos_beers
        + progress.structurally_blocked_only_beers
    )
    assert sorted(all_bucketed) == ["full", "identity", "photos", "structural"]
    assert progress.total_beers == 4


def test_sku_counts_pass_through_from_report():
    beers = [_beer("a", ["CP1"])]
    report = _report(included=[], skus_joined=10, skus_unenriched=5, skus_rejected=10)

    progress = build_progress_report(beers, report)

    assert progress.grouped_skus == 10
    assert progress.unenriched_skus == 5
    assert progress.blocked_skus == 10
    assert progress.total_admitted_skus == 15


def test_real_repository_smoke_test():
    from pathlib import Path

    from tool.catalog_builder.photo_queue import _load_photo_queue_inputs

    repo_root = Path(__file__).resolve().parents[3]
    if not (repo_root / "pricing_data" / "beer_master.csv").exists():
        import pytest

        pytest.skip("real repository data not present in this environment")

    beers, report = _load_photo_queue_inputs(repo_root)
    progress = build_progress_report(beers, report)

    assert progress.total_beers == len(beers)
    bucketed_count = (
        len(progress.fully_publishable_beers)
        + len(progress.awaiting_identity_resolution_beers)
        + len(progress.awaiting_photos_beers)
        + len(progress.structurally_blocked_only_beers)
    )
    assert bucketed_count == progress.total_beers
