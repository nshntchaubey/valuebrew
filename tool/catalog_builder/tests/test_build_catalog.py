import csv
from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.beer_master_reader import EXPECTED_COLUMNS
from tool.catalog_builder.build_catalog import BuildCatalogError, run_build

_STYLES = [{"style_key": "lager", "name": "Lager", "description": "Crisp"}]

_ABV_BLOCK = {
    "value": 4.8,
    "source_type": "manufacturer",
    "source_name": "X",
    "observed_at": "2026-08-13",
    "observed_by": "founder",
}

_ROW_DEFAULTS = {
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
}


def _setup(tmp_path: Path, rows, beer_files):
    beer_master_path = tmp_path / "beer_master.csv"
    with beer_master_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(_ROW_DEFAULTS, **row))

    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    (enrichment_dir / "styles.yaml").write_text(yaml.safe_dump(_STYLES), encoding="utf-8")
    for filename, data in beer_files.items():
        (beers_dir / filename).write_text(yaml.safe_dump(data), encoding="utf-8")

    return beer_master_path, enrichment_dir


def test_run_build_produces_a_real_catalog_and_manifest(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(
        tmp_path,
        rows=[{"canonical_product_id": "CP0000002"}],
        beer_files={
            "kingfisher_premium.yaml": {
                "beer_key": "kingfisher_premium",
                "canonical_product_ids": ["CP0000002"],
                "name": "Kingfisher Premium",
                "brewery": "United Breweries",
                "style": "lager",
                "abv": _ABV_BLOCK,
                "calories_per_100ml": _ABV_BLOCK,
            }
        },
    )
    catalog, report, catalog_json_bytes, manifest = run_build(
        beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=tmp_path / "catalog.json"
    )

    assert catalog.catalog_version == 1
    assert len(catalog.skus) == 1
    assert catalog.skus[0].id == "CP0000002"
    assert report.skus_included == 1
    assert catalog_json_bytes.startswith(b"{")
    assert manifest.record_counts == {"styles": 1, "beers": 1, "skus": 1, "benchmarks": 1}
    assert manifest.source_run_month == "2026-06"


def test_run_build_does_not_write_anything(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(
        tmp_path,
        rows=[{"canonical_product_id": "CP0000002"}],
        beer_files={
            "kingfisher_premium.yaml": {
                "beer_key": "kingfisher_premium",
                "canonical_product_ids": ["CP0000002"],
                "name": "Kingfisher Premium",
                "brewery": "United Breweries",
                "style": "lager",
                "abv": _ABV_BLOCK,
                "calories_per_100ml": _ABV_BLOCK,
            }
        },
    )
    catalog_path = tmp_path / "catalog.json"
    run_build(beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=catalog_path)
    assert not catalog_path.exists()


def test_run_build_second_run_increments_version(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(
        tmp_path,
        rows=[{"canonical_product_id": "CP0000002"}],
        beer_files={
            "kingfisher_premium.yaml": {
                "beer_key": "kingfisher_premium",
                "canonical_product_ids": ["CP0000002"],
                "name": "Kingfisher Premium",
                "brewery": "United Breweries",
                "style": "lager",
                "abv": _ABV_BLOCK,
                "calories_per_100ml": _ABV_BLOCK,
            }
        },
    )
    catalog_path = tmp_path / "catalog.json"
    from tool.catalog_builder.catalog_writer import write_catalog

    catalog_1, _, _, _ = run_build(beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=catalog_path)
    write_catalog(catalog_1, catalog_path)

    catalog_2, _, _, _ = run_build(beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=catalog_path)
    assert catalog_2.catalog_version == 2


def test_run_build_with_no_enriched_beers_produces_empty_catalog(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(tmp_path, rows=[{"canonical_product_id": "CP0000002"}], beer_files={})
    catalog, report, _, manifest = run_build(
        beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=tmp_path / "catalog.json"
    )
    assert catalog.skus == []
    assert catalog.beers == []
    assert report.skus_unenriched == 1
    assert manifest.record_counts == {"styles": 0, "beers": 0, "skus": 0, "benchmarks": 0}


def test_run_build_raises_on_duplicate_canonical_product_id_across_beers(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(
        tmp_path,
        rows=[{"canonical_product_id": "CP0000002"}],
        beer_files={
            "beer_a.yaml": {
                "beer_key": "beer_a",
                "canonical_product_ids": ["CP0000002"],
                "name": "A",
                "brewery": "Y",
                "style": "lager",
                "abv": "unknown",
                "calories_per_100ml": "unknown",
            },
            "beer_b.yaml": {
                "beer_key": "beer_b",
                "canonical_product_ids": ["CP0000002"],
                "name": "B",
                "brewery": "Y",
                "style": "lager",
                "abv": "unknown",
                "calories_per_100ml": "unknown",
            },
        },
    )
    with pytest.raises(BuildCatalogError):
        run_build(beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=tmp_path / "catalog.json")


def test_real_repository_dry_run_produces_a_real_valid_catalog():
    beer_master_path = Path("pricing_data/beer_master.csv")
    enrichment_dir = Path("enrichment")
    if not beer_master_path.exists() or not (enrichment_dir / "styles.yaml").exists():
        pytest.skip("real repository data not present in this environment")

    catalog, report, catalog_json_bytes, manifest = run_build(
        beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=Path("catalog/catalog.json")
    )
    # A structural smoke test against the real repository, not a fixed
    # target -- skus_included only needs to be non-negative and
    # internally consistent; the exact real count changes every real
    # production session and is asserted precisely in
    # test_validation_report.py's own real-repository test instead.
    assert report.skus_included >= 0
    assert len(catalog.skus) == report.skus_included
    assert len(catalog_json_bytes) > 0
