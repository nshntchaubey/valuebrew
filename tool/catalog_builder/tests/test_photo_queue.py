from datetime import date

from tool.catalog_builder.models import AttributionBlock, EnrichmentBeer
from tool.catalog_builder.photo_queue import build_photo_queue
from tool.catalog_builder.validation_report import RejectionDetail, ValidationReport

_ABV = AttributionBlock(
    value=5.0, source_type="manufacturer", source_name="X", observed_at=date(2026, 8, 13), observed_by="founder"
)


def _beer(beer_key: str, canonical_product_ids, brewery="Brewery X", abv=None, calories_per_100ml=None) -> EnrichmentBeer:
    return EnrichmentBeer(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name=beer_key,
        brewery=brewery,
        style="lager",
        abv=abv,
        calories_per_100ml=calories_per_100ml,
    )


def _report(rejected: list) -> ValidationReport:
    return ValidationReport(
        skus_joined=0,
        skus_unenriched=0,
        skus_included=0,
        skus_rejected=0,
        missing_candidate_references=0,
        orphan_sku_references=0,
        beers_included=0,
        beers_rejected=0,
        rejection_reasons={},
        included_canonical_product_ids=[],
        rejected_details=rejected,
    )


def _detail(beer_key: str, cpid: str, reason_code: str) -> RejectionDetail:
    return RejectionDetail(
        canonical_product_id=cpid, beer_key=beer_key, stage="business_rules", reason_code=reason_code, reason_detail=""
    )


def test_beer_missing_both_fields_appears_with_both_missing():
    beers = [_beer("a", ["CP1", "CP2"])]
    report = _report([_detail("a", "CP1", "missing_abv"), _detail("a", "CP2", "missing_abv")])

    entries = build_photo_queue(beers, report)

    assert len(entries) == 1
    assert entries[0].beer_key == "a"
    assert entries[0].missing_fields == ["abv", "calories"]
    assert entries[0].fixable_sku_count == 2
    assert entries[0].grouped_sku_count == 2


def test_beer_missing_only_calories_when_abv_already_known():
    beers = [_beer("a", ["CP1"], abv=_ABV)]
    report = _report([_detail("a", "CP1", "missing_calories")])

    entries = build_photo_queue(beers, report)

    assert entries[0].missing_fields == ["calories"]


def test_fully_evidenced_beer_is_excluded():
    beers = [_beer("a", ["CP1"], abv=_ABV, calories_per_100ml=_ABV)]
    report = _report([])

    entries = build_photo_queue(beers, report)

    assert entries == []


def test_beer_blocked_only_by_unrelated_reason_is_excluded():
    # abv/calories missing, but no rejected_details entry with a fixable
    # reason -- e.g. every SKU already failed earlier (product_unavailable)
    # before the abv check ever ran. A photo would fix nothing here.
    beers = [_beer("a", ["CP1"])]
    report = _report([_detail("a", "CP1", "product_unavailable")])

    entries = build_photo_queue(beers, report)

    assert entries == []


def test_fixable_sku_count_excludes_structural_rejections():
    # 3 real candidates: 2 fixable via missing_abv, 1 blocked by a
    # container-type gap no photo can touch.
    beers = [_beer("a", ["CP1", "CP2", "CP3"])]
    report = _report(
        [
            _detail("a", "CP1", "missing_abv"),
            _detail("a", "CP2", "missing_abv"),
            _detail("a", "CP3", "unsupported_package_type"),
        ]
    )

    entries = build_photo_queue(beers, report)

    assert entries[0].fixable_sku_count == 2
    assert entries[0].grouped_sku_count == 3


def test_sorted_by_fixable_sku_count_descending():
    beers = [_beer("small", ["CP1"]), _beer("big", ["CP2", "CP3", "CP4"])]
    report = _report(
        [
            _detail("small", "CP1", "missing_abv"),
            _detail("big", "CP2", "missing_abv"),
            _detail("big", "CP3", "missing_abv"),
            _detail("big", "CP4", "missing_abv"),
        ]
    )

    entries = build_photo_queue(beers, report)

    assert [e.beer_key for e in entries] == ["big", "small"]


def test_publication_potential_tiers():
    beers = [_beer("high", [f"CP{i}" for i in range(10)]), _beer("medium", ["CPa", "CPb", "CPc"]), _beer("low", ["CPz"])]
    report = _report(
        [_detail("high", f"CP{i}", "missing_abv") for i in range(10)]
        + [_detail("medium", cid, "missing_abv") for cid in ("CPa", "CPb", "CPc")]
        + [_detail("low", "CPz", "missing_abv")]
    )

    entries = build_photo_queue(beers, report)
    potential_by_key = {e.beer_key: e.publication_potential for e in entries}

    assert potential_by_key["high"] == "High"
    assert potential_by_key["medium"] == "Medium"
    assert potential_by_key["low"] == "Low"


def test_real_repository_smoke_test():
    from pathlib import Path

    from tool.catalog_builder.photo_queue import _load_photo_queue_inputs

    repo_root = Path(__file__).resolve().parents[3]
    if not (repo_root / "pricing_data" / "beer_master.csv").exists():
        import pytest

        pytest.skip("real repository data not present in this environment")

    beers, report = _load_photo_queue_inputs(repo_root)
    entries = build_photo_queue(beers, report)

    # Every entry must correspond to a real beer that actually has a
    # missing field -- a basic sanity invariant, not a fixed count.
    beer_by_key = {b.beer_key: b for b in beers}
    for entry in entries:
        beer = beer_by_key[entry.beer_key]
        assert beer.abv is None or beer.calories_per_100ml is None
        assert entry.fixable_sku_count > 0
