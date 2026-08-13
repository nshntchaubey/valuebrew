from datetime import date
from decimal import Decimal
from pathlib import Path

from tool.catalog_builder.beer_master_reader import read_beer_master_csv
from tool.catalog_builder.business_rules import apply_business_rules
from tool.catalog_builder.contamination_filter import filter_contamination, load_default_exclusion_terms
from tool.catalog_builder.cross_reference_validate import validate_cross_references
from tool.catalog_builder.enrichment_reader import load_beers, load_styles
from tool.catalog_builder.join import JoinedSku, join
from tool.catalog_builder.models import AttributionBlock, BeerMasterRow, EnrichmentBeer
from tool.catalog_builder.validate_beer import compute_invalid_beer_keys
from tool.catalog_builder.validation_report import build_validation_report

_ABV = AttributionBlock(
    value=4.8, source_type="manufacturer", source_name="X", observed_at=date(2026, 8, 13), observed_by="founder"
)


def _row(canonical_product_id: str, **overrides) -> BeerMasterRow:
    defaults = dict(
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
    defaults.update(overrides)
    return BeerMasterRow(**defaults)


def _beer(beer_key: str, canonical_product_ids, **overrides) -> EnrichmentBeer:
    defaults = dict(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name="Kingfisher Premium",
        brewery="United Breweries",
        style="lager",
        abv=_ABV,
        calories_per_100ml=_ABV,
    )
    defaults.update(overrides)
    return EnrichmentBeer(**defaults)


def _run_pipeline(
    rows,
    beers,
    contaminated_ids=frozenset(),
    invalid_beer_keys=frozenset(),
    style_keys=frozenset({"lager"}),
    rejected_beer_files=(),
):
    join_result = join(rows, contaminated_row_ids=set(contaminated_ids), beers=beers)
    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=set(invalid_beer_keys))
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=set(style_keys))
    report = build_validation_report(
        beers, join_result, business_result, cross_ref_result, rejected_beer_files=list(rejected_beer_files)
    )
    return report


# ---------------------------------------------------------------------------
# Fixture-based
# ---------------------------------------------------------------------------


def test_all_included_report():
    rows = [_row("CP0000002")]
    beers = [_beer("x", ["CP0000002"])]
    report = _run_pipeline(rows, beers)

    assert report.skus_included == 1
    assert report.skus_rejected == 0
    assert report.beers_included == 1
    assert report.beers_rejected == 0
    assert report.included_canonical_product_ids == ["CP0000002"]
    assert report.rejection_reasons == {}


def test_mixed_pipeline_report_counts():
    rows = [_row("CP0000002"), _row("CP0000003", status="DELISTED"), _row("CP0000004")]
    beers = [
        _beer("beer_a", ["CP0000002", "CP0000003"]),
        _beer("beer_b", ["CP0000004"], abv=None),  # will fail missing_abv
        _beer("beer_c", ["CP0000999"]),  # missing_candidate
    ]
    report = _run_pipeline(rows, beers)

    assert report.skus_included == 1  # only CP0000002
    assert report.missing_candidate_references == 1
    assert "product_unavailable" in report.rejection_reasons
    assert "missing_abv" in report.rejection_reasons
    assert "missing_candidate" in report.rejection_reasons
    assert report.beers_included == 1  # beer_a
    assert report.beers_rejected == 2  # beer_b, beer_c


def test_orphan_sku_counted_and_reasoned():
    rows = [_row("CP0000002")]
    beers = [_beer("x", ["CP0000002", "CP0000001"])]
    report = _run_pipeline(rows, beers, contaminated_ids={"CP0000001"})

    assert report.orphan_sku_references == 1
    assert "orphan_sku" in report.rejection_reasons


def test_invalid_beer_entity_reasoned():
    rows = [_row("CP0000002")]
    beers = [_beer("bad_beer", ["CP0000002"])]
    report = _run_pipeline(rows, beers, invalid_beer_keys={"bad_beer"})

    assert report.skus_included == 0
    assert report.beers_rejected == 1
    assert "invalid_beer_entity" in report.rejection_reasons


def test_report_is_deterministic_across_calls():
    rows = [_row("CP0000099"), _row("CP0000002")]
    beers = [_beer("a", ["CP0000099"]), _beer("b", ["CP0000002"])]

    first = _run_pipeline(rows, beers)
    second = _run_pipeline(rows, beers)

    assert first == second


def test_rejected_details_sorted_deterministically():
    rows = [_row("CP0000099", status="DELISTED"), _row("CP0000002", status="DELISTED")]
    beers = [_beer("a", ["CP0000099"]), _beer("b", ["CP0000002"])]
    report = _run_pipeline(rows, beers)
    assert [d.canonical_product_id for d in report.rejected_details] == ["CP0000002", "CP0000099"]


# ---------------------------------------------------------------------------
# Full real end-to-end pipeline, against the actual repository
# ---------------------------------------------------------------------------


def test_real_repository_end_to_end_pipeline_runs_cleanly():
    # Real production enrichment sessions have created real Beer files
    # in enrichment/beers/, grouped correctly, most still honestly
    # "unknown" on abv and/or calories_per_100ml (no citable evidence
    # reachable under the accepted evidence policy) -- this proves the
    # whole chain (contamination filter -> join -> business rules ->
    # cross-reference validate -> report) runs correctly end to end
    # against real data: real SKUs join correctly, and either publish
    # or correctly fail to (missing_abv / missing_calories /
    # unsupported_package_type), never an error, never a silent
    # success. A structural smoke test, not a fixed target -- real beer
    # and SKU counts change every real production session, so this
    # asserts internal consistency instead of hand-bumped numbers.
    enrichment_dir = Path("enrichment")
    beer_master_path = Path("pricing_data/beer_master.csv")
    if not beer_master_path.exists() or not (enrichment_dir / "styles.yaml").exists():
        import pytest

        pytest.skip("real repository data not present in this environment")

    accepted, _ = read_beer_master_csv(beer_master_path)
    exclusion_terms = load_default_exclusion_terms()
    admitted_rows, rejected_rows = filter_contamination(accepted, exclusion_terms)
    contaminated_ids = {r.canonical_product_id for r in rejected_rows}

    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {s.style_key for s in styles}
    beers, rejected_beer_files = load_beers(enrichment_dir / "beers", style_keys)

    invalid_beer_keys = compute_invalid_beer_keys(enrichment_dir / "beers", enrichment_dir / "styles.yaml")

    join_result = join(admitted_rows, contaminated_row_ids=contaminated_ids, beers=beers)
    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)
    report = build_validation_report(
        beers, join_result, business_result, cross_ref_result, rejected_beer_files=rejected_beer_files
    )

    assert len(beers) > 0
    assert report.rejected_beer_files == []  # no malformed real file, ever
    assert report.beers_included + report.beers_rejected == len(beers)
    assert report.skus_included <= report.skus_joined
    assert sum(report.rejection_reasons.values()) == report.skus_joined - report.skus_included
    # Every real admitted row not claimed by one of the real enriched
    # beers is still unenriched -- a structural invariant, not a count
    # that should ever need bumping by hand.
    assert report.skus_unenriched == len(admitted_rows) - report.skus_joined
