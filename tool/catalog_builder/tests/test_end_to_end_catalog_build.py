"""The end-to-end test: `beer_master.csv` + Beer YAMLs -> `catalog.json`
-> Flutter `Catalog` models, round-tripping successfully. Every stage is
the real, production module — nothing here bypasses a layer to make the
test easier. Also writes a golden fixture file
(`tests/fixtures/golden_catalog.json`) that a companion Dart test
(`test/unit/catalog_builder_golden_round_trip_test.dart`) parses via the
real `Catalog.fromJson`, proving the artifact this package produces is
actually consumable by the app, not merely shaped like it should be.
"""

import csv
from datetime import datetime
from pathlib import Path

import yaml

from tool.catalog_builder.assemble import assemble_catalog
from tool.catalog_builder.beer_master_reader import EXPECTED_COLUMNS, read_beer_master_csv
from tool.catalog_builder.build_manifest import build_manifest, write_manifest
from tool.catalog_builder.catalog_writer import write_catalog
from tool.catalog_builder.contamination_filter import filter_contamination, load_default_exclusion_terms
from tool.catalog_builder.cross_reference_validate import validate_cross_references
from tool.catalog_builder.business_rules import apply_business_rules
from tool.catalog_builder.enrichment_reader import load_beers, load_styles
from tool.catalog_builder.join import join
from tool.catalog_builder.models import PackageType, ValueVerdict
from tool.catalog_builder.validate_beer import compute_invalid_beer_keys
from tool.catalog_builder.version import next_catalog_version

_FIXTURES_DIR = Path(__file__).parent / "fixtures"

_ROWS = [
    {
        "canonical_product_id": "CP0000001",
        "representative_item_code": "1390101301",
        "item_name_raw": "Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls(0139)",
        "display_name": "Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls",
        "normalized_name_key": "budweiser magnum double barrel blended american whiskey 750mlx12btls",
        "pack_size_ml": "750",
        "pack_count": "12",
        "container_type": "bottle",
        "declared_price": "7408.53",
        "landed_cost": "25948.53",
        "ksbcl_selling_price": "26078.27",
        "mrp": "2395.00",
        "effective_date": "2026-06-01",
        "status": "LIVE",
        "delisted_run_month": "",
        "classification_confidence": "medium",
        "classification_matched_on": "brand_name:Budweiser",
        "gtin": "",
        "gtin_confidence": "",
        "source_pdf_reference": "x.pdf",
        "first_seen_run_month": "2026-06",
        "last_updated_run_month": "2026-06",
    },
    {
        "canonical_product_id": "CP0000002",
        "representative_item_code": "2020900211",
        "item_name_raw": "Kingfisher Premium Lager Beer-CAN 330ML(0202)",
        "display_name": "Kingfisher Premium Lager Beer-CAN 330ML",
        "normalized_name_key": "kingfisher premium lager beer-can 330ml",
        "pack_size_ml": "330",
        "pack_count": "",
        "container_type": "can",
        "declared_price": "66.90",
        "landed_cost": "95.74",
        "ksbcl_selling_price": "98.22",
        "mrp": "100.00",
        "effective_date": "2026-06-01",
        "status": "LIVE",
        "delisted_run_month": "",
        "classification_confidence": "high",
        "classification_matched_on": "style_keyword:beer",
        "gtin": "",
        "gtin_confidence": "",
        "source_pdf_reference": "x.pdf",
        "first_seen_run_month": "2026-06",
        "last_updated_run_month": "2026-06",
    },
    {
        "canonical_product_id": "CP0000003",
        "representative_item_code": "2020900212",
        "item_name_raw": "Kingfisher Premium Lager Beer-Bottle 650ML(0202)",
        "display_name": "Kingfisher Premium Lager Beer-Bottle 650ML",
        "normalized_name_key": "kingfisher premium lager beer-bottle 650ml",
        "pack_size_ml": "650",
        "pack_count": "",
        "container_type": "bottle",
        "declared_price": "120.00",
        "landed_cost": "170.00",
        "ksbcl_selling_price": "175.00",
        "mrp": "180.00",
        "effective_date": "2026-06-01",
        "status": "LIVE",
        "delisted_run_month": "",
        "classification_confidence": "high",
        "classification_matched_on": "style_keyword:beer",
        "gtin": "",
        "gtin_confidence": "",
        "source_pdf_reference": "x.pdf",
        "first_seen_run_month": "2026-06",
        "last_updated_run_month": "2026-06",
    },
    {
        "canonical_product_id": "CP0000010",
        "representative_item_code": "2030900110",
        "item_name_raw": "Tuborg Strong Beer-CAN 500ML(0203)",
        "display_name": "Tuborg Strong Beer-CAN 500ML",
        "normalized_name_key": "tuborg strong beer-can 500ml",
        "pack_size_ml": "500",
        "pack_count": "",
        "container_type": "can",
        "declared_price": "96.90",
        "landed_cost": "138.74",
        "ksbcl_selling_price": "142.22",
        "mrp": "145.00",
        "effective_date": "2026-06-01",
        "status": "LIVE",
        "delisted_run_month": "",
        "classification_confidence": "high",
        "classification_matched_on": "style_keyword:beer",
        "gtin": "",
        "gtin_confidence": "",
        "source_pdf_reference": "x.pdf",
        "first_seen_run_month": "2026-06",
        "last_updated_run_month": "2026-06",
    },
    {
        "canonical_product_id": "CP0000099",
        "representative_item_code": "2040900199",
        "item_name_raw": "Some Unenriched Beer-CAN 330ML(0204)",
        "display_name": "Some Unenriched Beer-CAN 330ML",
        "normalized_name_key": "some unenriched beer-can 330ml",
        "pack_size_ml": "330",
        "pack_count": "",
        "container_type": "can",
        "declared_price": "60.00",
        "landed_cost": "85.00",
        "ksbcl_selling_price": "88.00",
        "mrp": "90.00",
        "effective_date": "2026-06-01",
        "status": "LIVE",
        "delisted_run_month": "",
        "classification_confidence": "high",
        "classification_matched_on": "style_keyword:beer",
        "gtin": "",
        "gtin_confidence": "",
        "source_pdf_reference": "x.pdf",
        "first_seen_run_month": "2026-06",
        "last_updated_run_month": "2026-06",
    },
]

_STYLES = [
    {"style_key": "lager", "name": "Lager", "description": "Crisp, mild bitterness"},
    {"style_key": "strong_lager", "name": "Strong Lager", "description": "Higher-ABV lager, typically 7-8%"},
]

_KINGFISHER_ABV = {
    "value": 4.8,
    "source_type": "manufacturer",
    "source_name": "United Breweries official product page",
    "observed_at": "2026-08-13",
    "observed_by": "founder",
}
# kcal per 100ml, exactly as a manufacturer would publish it -- Sku.calories
# (the per-pack total, asserted below) is computed from this at build time.
_KINGFISHER_CALORIES = dict(_KINGFISHER_ABV, value=50)  # -> 165 kcal for CP0000002's 330ml

_TUBORG_ABV = dict(_KINGFISHER_ABV, value=8.0, source_name="Carlsberg India official product page")
_TUBORG_CALORIES = dict(_TUBORG_ABV, value=62)  # -> 310 kcal for CP0000010's 500ml

_KINGFISHER_BEER = {
    "beer_key": "kingfisher_premium",
    "canonical_product_ids": ["CP0000002", "CP0000003"],
    "name": "Kingfisher Premium",
    "brewery": "United Breweries",
    "style": "lager",
    "abv": _KINGFISHER_ABV,
    "calories_per_100ml": _KINGFISHER_CALORIES,
}
_TUBORG_BEER = {
    "beer_key": "tuborg_strong",
    "canonical_product_ids": ["CP0000010"],
    "name": "Tuborg Strong",
    "brewery": "Carlsberg India",
    "style": "strong_lager",
    "abv": _TUBORG_ABV,
    "calories_per_100ml": _TUBORG_CALORIES,
}


def _build_fixture_repository(tmp_path: Path):
    beer_master_path = tmp_path / "beer_master.csv"
    with beer_master_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        for row in _ROWS:
            writer.writerow(row)

    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    (enrichment_dir / "styles.yaml").write_text(yaml.safe_dump(_STYLES), encoding="utf-8")
    (beers_dir / "kingfisher_premium.yaml").write_text(yaml.safe_dump(_KINGFISHER_BEER), encoding="utf-8")
    (beers_dir / "tuborg_strong.yaml").write_text(yaml.safe_dump(_TUBORG_BEER), encoding="utf-8")

    return beer_master_path, enrichment_dir


def _run_full_build(tmp_path: Path):
    beer_master_path, enrichment_dir = _build_fixture_repository(tmp_path)

    accepted, _ = read_beer_master_csv(beer_master_path)
    exclusion_terms = load_default_exclusion_terms()
    admitted_rows, contaminated_rows = filter_contamination(accepted, exclusion_terms)
    contaminated_ids = {r.canonical_product_id for r in contaminated_rows}

    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {s.style_key for s in styles}
    beers, rejected_beer_files = load_beers(enrichment_dir / "beers", style_keys)
    invalid_beer_keys = compute_invalid_beer_keys(enrichment_dir / "beers", enrichment_dir / "styles.yaml")

    join_result = join(admitted_rows, contaminated_row_ids=contaminated_ids, beers=beers)
    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)

    catalog_version = 1  # first build, no prior catalog.json in this fixture
    generated_at = datetime(2026, 8, 13, 12, 0, 0)
    catalog = assemble_catalog(cross_ref_result.valid, styles, catalog_version, generated_at)

    return catalog, join_result, contaminated_ids, enrichment_dir


# ---------------------------------------------------------------------------
# Full pipeline correctness
# ---------------------------------------------------------------------------


def test_contamination_excluded_end_to_end(tmp_path: Path):
    catalog, join_result, contaminated_ids, _ = _run_full_build(tmp_path)
    assert "CP0000001" in contaminated_ids
    assert all(sku.id != "CP0000001" for sku in catalog.skus)


def test_unenriched_row_never_appears_in_output(tmp_path: Path):
    catalog, join_result, _, _ = _run_full_build(tmp_path)
    assert any(u.canonical_product_id == "CP0000099" for u in join_result.unenriched)
    assert all(sku.id != "CP0000099" for sku in catalog.skus)


def test_multi_sku_beer_and_single_sku_beer_both_present(tmp_path: Path):
    catalog, _, _, _ = _run_full_build(tmp_path)
    assert {b.id for b in catalog.beers} == {"kingfisher_premium", "tuborg_strong"}
    kingfisher_skus = [s for s in catalog.skus if s.beer_id == "kingfisher_premium"]
    tuborg_skus = [s for s in catalog.skus if s.beer_id == "tuborg_strong"]
    assert {s.id for s in kingfisher_skus} == {"CP0000002", "CP0000003"}
    assert {s.id for s in tuborg_skus} == {"CP0000010"}


def test_both_styles_present_with_benchmarks(tmp_path: Path):
    catalog, _, _, _ = _run_full_build(tmp_path)
    assert {s.id for s in catalog.styles} == {"lager", "strong_lager"}
    benchmark_by_style = {b.style_id: b for b in catalog.benchmarks}
    assert benchmark_by_style["lager"].sample_size == 2
    assert benchmark_by_style["strong_lager"].sample_size == 1


def test_abv_calories_and_package_type_match_enriched_values(tmp_path: Path):
    catalog, _, _, _ = _run_full_build(tmp_path)
    sku_by_id = {s.id: s for s in catalog.skus}

    assert sku_by_id["CP0000002"].abv == 4.8
    assert sku_by_id["CP0000002"].calories == 165
    assert sku_by_id["CP0000002"].package_type == PackageType.CAN
    assert sku_by_id["CP0000002"].size_ml == 330
    assert sku_by_id["CP0000002"].price == 100.0

    assert sku_by_id["CP0000003"].package_type == PackageType.BOTTLE
    assert sku_by_id["CP0000003"].size_ml == 650
    assert sku_by_id["CP0000003"].price == 180.0

    assert sku_by_id["CP0000010"].abv == 8.0
    assert sku_by_id["CP0000010"].calories == 310
    assert sku_by_id["CP0000010"].price == 145.0


def test_unknown_calories_still_publishes_end_to_end(tmp_path: Path):
    # Product Decisions Register D22: a beer with known ABV and style but
    # unknown calories now publishes with calories=None, not excluded --
    # a standalone one-beer fixture so this doesn't touch the shared
    # _ROWS/_STYLES fixture every other test in this file also depends on.
    beer_master_path = tmp_path / "beer_master.csv"
    with beer_master_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        writer.writerow(_ROWS[1])  # CP0000002, kingfisher, 330ml

    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    (enrichment_dir / "styles.yaml").write_text(yaml.safe_dump([_STYLES[0]]), encoding="utf-8")
    (beers_dir / "kingfisher_premium.yaml").write_text(
        yaml.safe_dump(dict(_KINGFISHER_BEER, canonical_product_ids=["CP0000002"], calories_per_100ml="unknown")),
        encoding="utf-8",
    )

    accepted, _ = read_beer_master_csv(beer_master_path)
    admitted_rows, contaminated_rows = filter_contamination(accepted, load_default_exclusion_terms())
    contaminated_ids = {r.canonical_product_id for r in contaminated_rows}
    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {s.style_key for s in styles}
    beers, rejected_beer_files = load_beers(beers_dir, style_keys)
    invalid_beer_keys = compute_invalid_beer_keys(beers_dir, enrichment_dir / "styles.yaml")

    join_result = join(admitted_rows, contaminated_row_ids=contaminated_ids, beers=beers)
    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    assert business_result.rejected == []
    assert business_result.admitted[0].warnings == ["missing_calories"]

    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)
    catalog = assemble_catalog(cross_ref_result.valid, styles, catalog_version=1, generated_at=datetime(2026, 8, 13, 12, 0, 0))

    assert len(catalog.skus) == 1
    assert catalog.skus[0].id == "CP0000002"
    assert catalog.skus[0].calories is None
    assert catalog.skus[0].abv == 4.8


def test_value_scores_and_verdicts_are_well_formed(tmp_path: Path):
    catalog, _, _, _ = _run_full_build(tmp_path)
    for sku in catalog.skus:
        assert 0 <= sku.value_score <= 100
        assert isinstance(sku.value_verdict, ValueVerdict)
        assert sku.cost_per_litre > 0
        assert sku.cost_per_ml_alcohol > 0


def test_build_is_deterministic(tmp_path_factory):
    tmp_path_1 = tmp_path_factory.mktemp("build1")
    tmp_path_2 = tmp_path_factory.mktemp("build2")
    catalog_1, _, _, _ = _run_full_build(tmp_path_1)
    catalog_2, _, _, _ = _run_full_build(tmp_path_2)
    assert catalog_1 == catalog_2


# ---------------------------------------------------------------------------
# Full write + manifest + golden fixture for the Dart round-trip test
# ---------------------------------------------------------------------------


def test_write_catalog_and_manifest_and_golden_fixture(tmp_path: Path):
    catalog, _, _, enrichment_dir = _run_full_build(tmp_path)

    catalog_path = tmp_path / "catalog" / "catalog.json"
    catalog_bytes = write_catalog(catalog, catalog_path)
    assert catalog_path.exists()

    next_version = next_catalog_version(catalog_path.parent / "does_not_exist_yet.json")
    assert next_version == 1  # no prior catalog in this isolated fixture

    manifest = build_manifest(
        build_timestamp=catalog.generated_at,
        source_run_month="2026-06",
        enrichment_dir=enrichment_dir,
        catalog_version=catalog.catalog_version,
        record_counts={
            "styles": len(catalog.styles),
            "beers": len(catalog.beers),
            "skus": len(catalog.skus),
            "benchmarks": len(catalog.benchmarks),
        },
        catalog_json_bytes=catalog_bytes,
    )
    manifest_path = write_manifest(manifest, catalog_path.parent)
    assert manifest_path.exists()
    assert manifest.record_counts == {"styles": 2, "beers": 2, "skus": 3, "benchmarks": 2}

    # Also write the golden fixture the companion Dart test reads.
    _FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    golden_path = _FIXTURES_DIR / "golden_catalog.json"
    golden_path.write_bytes(catalog_bytes)
