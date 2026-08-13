"""Writes the build manifest — Catalog Implementation Architecture Part
3 Step 11 / Part 6, Catalog Builder Implementation Design Part 7: which
`pricing_data/` run and which `enrichment/` snapshot produced this exact
`catalog_version` — the direct analogue of `beer_master.csv`'s own
`source_pdf_reference` field, one layer up.

**Implementation Blocker #2 (Implementation Roadmap), resolved here
rather than left open.** File location: `catalog/catalog_build_manifest.json`,
sibling to `catalog.json` itself. Confirmed safe before choosing this:
`pubspec.yaml`'s `assets:` section bundles the specific file
`catalog/catalog.json`, not the whole `catalog/` directory (checked
directly), so a sibling manifest file here is never bundled into the
Flutter app and adds no bundle-size cost.

`enrichment_snapshot_version` mirrors `classification_config.py`'s own
content-hash-versioning convention (first 12 hex characters of a
SHA-256 over raw file bytes) — a content hash over `styles.yaml` plus
every `enrichment/beers/*.yaml` file, sorted by path for determinism —
not a hand-maintained version number.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

MANIFEST_FILENAME = "catalog_build_manifest.json"


@dataclass(frozen=True)
class BuildManifest:
    build_timestamp: datetime
    source_run_month: str
    enrichment_snapshot_version: str
    catalog_version: int
    record_counts: Dict[str, int]
    content_hash: str


def compute_enrichment_snapshot_version(enrichment_dir: Path) -> str:
    """Content-hash of `enrichment/styles.yaml` plus every
    `enrichment/beers/*.yaml` file, sorted by filename so the hash
    itself is deterministic regardless of filesystem iteration order."""
    hasher = hashlib.sha256()
    styles_path = enrichment_dir / "styles.yaml"
    beers_dir = enrichment_dir / "beers"
    beer_paths = sorted(beers_dir.glob("*.yaml")) if beers_dir.exists() else []

    for path in [styles_path, *beer_paths]:
        if path.exists():
            hasher.update(path.name.encode("utf-8"))
            hasher.update(path.read_bytes())

    return hasher.hexdigest()[:12]


def compute_content_hash(catalog_json_bytes: bytes) -> str:
    return hashlib.sha256(catalog_json_bytes).hexdigest()[:12]


def build_manifest(
    *,
    build_timestamp: datetime,
    source_run_month: str,
    enrichment_dir: Path,
    catalog_version: int,
    record_counts: Dict[str, int],
    catalog_json_bytes: bytes,
) -> BuildManifest:
    """Pure function apart from reading `enrichment_dir`'s own content
    to hash it — no other I/O. `record_counts` and `catalog_json_bytes`
    are supplied by the caller (`assemble.py`'s output and
    `catalog_writer.write_catalog`'s own return value respectively),
    never recomputed here, so the manifest always describes exactly what
    was actually built and written."""
    return BuildManifest(
        build_timestamp=build_timestamp,
        source_run_month=source_run_month,
        enrichment_snapshot_version=compute_enrichment_snapshot_version(enrichment_dir),
        catalog_version=catalog_version,
        record_counts=dict(record_counts),
        content_hash=compute_content_hash(catalog_json_bytes),
    )


def manifest_to_dict(manifest: BuildManifest) -> dict:
    return {
        "build_timestamp": manifest.build_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_run_month": manifest.source_run_month,
        "enrichment_snapshot_version": manifest.enrichment_snapshot_version,
        "catalog_version": manifest.catalog_version,
        "record_counts": manifest.record_counts,
        "content_hash": manifest.content_hash,
    }


def write_manifest(manifest: BuildManifest, catalog_dir: Path) -> Path:
    path = catalog_dir / MANIFEST_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest_to_dict(manifest), indent=2) + "\n", encoding="utf-8")
    return path
