import json
from datetime import date, datetime
from pathlib import Path

from tool.catalog_builder.catalog_writer import catalog_to_dict, catalog_to_json_bytes, write_catalog
from tool.catalog_builder.models import Beer, Benchmark, Catalog, PackageType, Sku, Style, ValueVerdict

_STYLE = Style(id="lager", name="Lager", description="Crisp, mild bitterness")
_BEER = Beer(id="kf_premium", name="Kingfisher Premium", brewery="United Breweries", style_id="lager", is_craft=False)
_SKU = Sku(
    id="kf_premium_650",
    beer_id="kf_premium",
    size_ml=650,
    package_type=PackageType.BOTTLE,
    abv=4.8,
    calories=260,
    price=110.0,
    price_last_checked=date(2026, 7, 20),
    price_source="karnataka_excise_mrp_2026",
    cost_per_litre=169.2,
    cost_per_ml_alcohol=3.52,
    value_score=78,
    value_verdict=ValueVerdict.GREAT_VALUE,
)
_BENCHMARK = Benchmark(
    style_id="lager", avg_cost_per_ml_alcohol=4.10, p25=3.40, p50=3.95, p75=4.60, sample_size=1
)
_CATALOG = Catalog(
    catalog_version=7,
    generated_at=datetime(2026, 7, 25, 0, 0, 0),
    styles=[_STYLE],
    beers=[_BEER],
    skus=[_SKU],
    benchmarks=[_BENCHMARK],
)


def test_top_level_shape_has_exactly_six_keys():
    data = catalog_to_dict(_CATALOG)
    assert set(data.keys()) == {"catalog_version", "generated_at", "styles", "beers", "skus", "benchmarks"}


def test_catalog_version_and_generated_at_format():
    data = catalog_to_dict(_CATALOG)
    assert data["catalog_version"] == 7
    assert data["generated_at"] == "2026-07-25T00:00:00Z"


def test_style_shape_matches_contract():
    data = catalog_to_dict(_CATALOG)
    assert data["styles"] == [{"id": "lager", "name": "Lager", "description": "Crisp, mild bitterness"}]


def test_beer_shape_matches_contract():
    data = catalog_to_dict(_CATALOG)
    assert data["beers"] == [
        {"id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": False}
    ]


def test_sku_shape_matches_contract_field_names_and_types():
    data = catalog_to_dict(_CATALOG)
    sku = data["skus"][0]
    assert sku == {
        "id": "kf_premium_650",
        "beer_id": "kf_premium",
        "size_ml": 650,
        "package_type": "bottle",
        "abv": 4.8,
        "calories": 260,
        "price": 110.0,
        "price_last_checked": "2026-07-20",
        "price_source": "karnataka_excise_mrp_2026",
        "cost_per_litre": 169.2,
        "cost_per_ml_alcohol": 3.52,
        "value_score": 78,
        "value_verdict": "great_value",
    }


def test_benchmark_shape_matches_contract():
    data = catalog_to_dict(_CATALOG)
    assert data["benchmarks"] == [
        {
            "style_id": "lager",
            "avg_cost_per_ml_alcohol": 4.10,
            "p25": 3.40,
            "p50": 3.95,
            "p75": 4.60,
            "sample_size": 1,
        }
    ]


def test_price_last_checked_is_bare_date_no_time():
    data = catalog_to_dict(_CATALOG)
    assert data["skus"][0]["price_last_checked"] == "2026-07-20"
    assert "T" not in data["skus"][0]["price_last_checked"]


def test_output_is_valid_json():
    content = catalog_to_json_bytes(_CATALOG)
    parsed = json.loads(content)
    assert parsed["catalog_version"] == 7


def test_output_is_deterministic_byte_for_byte():
    first = catalog_to_json_bytes(_CATALOG)
    second = catalog_to_json_bytes(_CATALOG)
    assert first == second


def test_write_catalog_creates_file_and_returns_matching_bytes(tmp_path: Path):
    path = tmp_path / "catalog" / "catalog.json"
    written = write_catalog(_CATALOG, path)

    assert path.exists()
    assert path.read_bytes() == written
    assert json.loads(path.read_text())["catalog_version"] == 7


def test_empty_catalog_serializes_with_empty_arrays():
    empty = Catalog(
        catalog_version=1, generated_at=datetime(2026, 1, 1), styles=[], beers=[], skus=[], benchmarks=[]
    )
    data = catalog_to_dict(empty)
    assert data["styles"] == []
    assert data["beers"] == []
    assert data["skus"] == []
    assert data["benchmarks"] == []
