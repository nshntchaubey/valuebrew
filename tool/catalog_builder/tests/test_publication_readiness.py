import csv
from pathlib import Path

import pytest
import yaml

from tool.catalog_builder.beer_master_reader import EXPECTED_COLUMNS
from tool.catalog_builder.join import JoinError
from tool.catalog_builder.validate_beer import check_publication_readiness

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


def test_publication_ready_beer_reports_ready_and_not_yet_in_catalog(tmp_path: Path):
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
    result = check_publication_readiness(
        "kingfisher_premium",
        beer_master_path=beer_master_path,
        enrichment_dir=enrichment_dir,
        catalog_path=tmp_path / "catalog" / "catalog.json",
    )
    assert result.structurally_valid is True
    assert len(result.skus) == 1
    assert result.skus[0].publication_ready is True
    assert result.skus[0].included_in_catalog is False
    assert result.skus[0].reason is None


def test_missing_abv_reports_not_ready_with_reason(tmp_path: Path):
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
                "abv": "unknown",
                "calories_per_100ml": "unknown",
            }
        },
    )
    result = check_publication_readiness(
        "kingfisher_premium",
        beer_master_path=beer_master_path,
        enrichment_dir=enrichment_dir,
        catalog_path=tmp_path / "catalog" / "catalog.json",
    )
    assert result.skus[0].publication_ready is False
    assert "missing_abv" in result.skus[0].reason


def test_unmappable_container_type_reports_not_ready(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(
        tmp_path,
        rows=[{"canonical_product_id": "CP0000002", "container_type": "unknown"}],
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
    result = check_publication_readiness(
        "kingfisher_premium",
        beer_master_path=beer_master_path,
        enrichment_dir=enrichment_dir,
        catalog_path=tmp_path / "catalog" / "catalog.json",
    )
    assert result.skus[0].publication_ready is False
    assert "unsupported_package_type" in result.skus[0].reason


def test_missing_candidate_reference_reports_not_ready(tmp_path: Path):
    beer_master_path, enrichment_dir = _setup(
        tmp_path,
        rows=[{"canonical_product_id": "CP0000002"}],
        beer_files={
            "kingfisher_premium.yaml": {
                "beer_key": "kingfisher_premium",
                "canonical_product_ids": ["CP0000002", "CP0000999"],
                "name": "Kingfisher Premium",
                "brewery": "United Breweries",
                "style": "lager",
                "abv": _ABV_BLOCK,
                "calories_per_100ml": _ABV_BLOCK,
            }
        },
    )
    result = check_publication_readiness(
        "kingfisher_premium",
        beer_master_path=beer_master_path,
        enrichment_dir=enrichment_dir,
        catalog_path=tmp_path / "catalog" / "catalog.json",
    )
    by_id = {s.canonical_product_id: s for s in result.skus}
    assert by_id["CP0000002"].publication_ready is True
    assert by_id["CP0000999"].publication_ready is False
    assert "missing_candidate" in by_id["CP0000999"].reason


def test_included_in_catalog_reads_the_real_file(tmp_path: Path):
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
    catalog_path = tmp_path / "catalog" / "catalog.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text('{"skus": [{"id": "CP0000002"}, {"id": "CP0000003"}]}', encoding="utf-8")

    result = check_publication_readiness(
        "kingfisher_premium", beer_master_path=beer_master_path, enrichment_dir=enrichment_dir, catalog_path=catalog_path
    )
    assert result.skus[0].included_in_catalog is True


def test_duplicate_canonical_product_id_across_beers_raises_join_error(tmp_path: Path):
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
    with pytest.raises(JoinError):
        check_publication_readiness(
            "beer_a",
            beer_master_path=beer_master_path,
            enrichment_dir=enrichment_dir,
            catalog_path=tmp_path / "catalog" / "catalog.json",
        )
