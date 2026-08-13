"""Serializes the final assembled `Catalog` to `catalog/catalog.json` —
Catalog Builder Implementation Design Part 7. The one place
`json.dump`-equivalent output happens in the whole package. Trusts that
every prior layer (join, business rules, cross-reference validation,
assembly) already ran and produced a structurally valid graph; performs
no validation of its own.

Field names and shapes match Catalog Contract 1.0 Parts 2-6 exactly, and
`generated_at`/`price_last_checked` are formatted to match the real
Dart parsing/serialization conventions confirmed directly against
`lib/catalog/domain/catalog.dart` (`DateTime.parse`) and
`lib/shared_domain/sku.dart` (`Sku._formatDate`, bare `yyyy-MM-dd`).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict

from .models import Beer, Benchmark, Catalog, Sku, Style


def _format_generated_at(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _format_date(value: date) -> str:
    return value.isoformat()


def _style_to_dict(style: Style) -> Dict[str, Any]:
    return {"id": style.id, "name": style.name, "description": style.description}


def _beer_to_dict(beer: Beer) -> Dict[str, Any]:
    return {
        "id": beer.id,
        "name": beer.name,
        "brewery": beer.brewery,
        "style_id": beer.style_id,
        "is_craft": beer.is_craft,
    }


def _sku_to_dict(sku: Sku) -> Dict[str, Any]:
    return {
        "id": sku.id,
        "beer_id": sku.beer_id,
        "size_ml": sku.size_ml,
        "package_type": sku.package_type.value,
        "abv": sku.abv,
        "calories": sku.calories,
        "price": sku.price,
        "price_last_checked": _format_date(sku.price_last_checked),
        "price_source": sku.price_source,
        "cost_per_litre": sku.cost_per_litre,
        "cost_per_ml_alcohol": sku.cost_per_ml_alcohol,
        "value_score": sku.value_score,
        "value_verdict": sku.value_verdict.value,
    }


def _benchmark_to_dict(benchmark: Benchmark) -> Dict[str, Any]:
    return {
        "style_id": benchmark.style_id,
        "avg_cost_per_ml_alcohol": benchmark.avg_cost_per_ml_alcohol,
        "p25": benchmark.p25,
        "p50": benchmark.p50,
        "p75": benchmark.p75,
        "sample_size": benchmark.sample_size,
    }


def catalog_to_dict(catalog: Catalog) -> Dict[str, Any]:
    """Pure function — the exact six-root-key shape Catalog Contract 1.0
    Part 2 defines, no more, no fewer."""
    return {
        "catalog_version": catalog.catalog_version,
        "generated_at": _format_generated_at(catalog.generated_at),
        "styles": [_style_to_dict(s) for s in catalog.styles],
        "beers": [_beer_to_dict(b) for b in catalog.beers],
        "skus": [_sku_to_dict(s) for s in catalog.skus],
        "benchmarks": [_benchmark_to_dict(b) for b in catalog.benchmarks],
    }


def catalog_to_json_bytes(catalog: Catalog) -> bytes:
    """The exact bytes `write_catalog` would write, without touching
    disk — used by `build_manifest.py` to hash precisely what got
    written, never a separately-reserialized copy that could drift."""
    text = json.dumps(catalog_to_dict(catalog), indent=2, ensure_ascii=False) + "\n"
    return text.encode("utf-8")


def write_catalog(catalog: Catalog, path: Path) -> bytes:
    """Writes `path` (expected: `catalog/catalog.json`) and returns the
    exact bytes written."""
    content = catalog_to_json_bytes(catalog)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return content
