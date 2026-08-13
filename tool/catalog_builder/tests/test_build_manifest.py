import json
from datetime import datetime
from pathlib import Path

from tool.catalog_builder.build_manifest import (
    build_manifest,
    compute_content_hash,
    compute_enrichment_snapshot_version,
    manifest_to_dict,
    write_manifest,
)

_GENERATED_AT = datetime(2026, 8, 13, 10, 0, 0)


def _setup_enrichment(tmp_path: Path) -> Path:
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    (enrichment_dir / "styles.yaml").write_text("- style_key: lager\n  name: Lager\n  description: Crisp\n")
    (beers_dir / "kingfisher_premium.yaml").write_text("beer_key: kingfisher_premium\n")
    return enrichment_dir


# ---------------------------------------------------------------------------
# compute_enrichment_snapshot_version
# ---------------------------------------------------------------------------


def test_snapshot_version_is_deterministic(tmp_path: Path):
    enrichment_dir = _setup_enrichment(tmp_path)
    first = compute_enrichment_snapshot_version(enrichment_dir)
    second = compute_enrichment_snapshot_version(enrichment_dir)
    assert first == second
    assert len(first) == 12


def test_snapshot_version_changes_when_a_beer_file_changes(tmp_path: Path):
    enrichment_dir = _setup_enrichment(tmp_path)
    before = compute_enrichment_snapshot_version(enrichment_dir)

    (enrichment_dir / "beers" / "kingfisher_premium.yaml").write_text("beer_key: kingfisher_premium_edited\n")
    after = compute_enrichment_snapshot_version(enrichment_dir)

    assert before != after


def test_snapshot_version_changes_when_styles_change(tmp_path: Path):
    enrichment_dir = _setup_enrichment(tmp_path)
    before = compute_enrichment_snapshot_version(enrichment_dir)

    (enrichment_dir / "styles.yaml").write_text("- style_key: stout\n  name: Stout\n  description: Dark\n")
    after = compute_enrichment_snapshot_version(enrichment_dir)

    assert before != after


def test_snapshot_version_handles_empty_beers_directory(tmp_path: Path):
    enrichment_dir = tmp_path / "enrichment"
    (enrichment_dir / "beers").mkdir(parents=True)
    (enrichment_dir / "styles.yaml").write_text("[]\n")
    version = compute_enrichment_snapshot_version(enrichment_dir)
    assert len(version) == 12


# ---------------------------------------------------------------------------
# compute_content_hash
# ---------------------------------------------------------------------------


def test_content_hash_deterministic_for_same_bytes():
    assert compute_content_hash(b"hello") == compute_content_hash(b"hello")


def test_content_hash_differs_for_different_bytes():
    assert compute_content_hash(b"hello") != compute_content_hash(b"world")


# ---------------------------------------------------------------------------
# build_manifest / manifest_to_dict / write_manifest
# ---------------------------------------------------------------------------


def test_build_manifest_populates_every_field(tmp_path: Path):
    enrichment_dir = _setup_enrichment(tmp_path)
    manifest = build_manifest(
        build_timestamp=_GENERATED_AT,
        source_run_month="2026-06",
        enrichment_dir=enrichment_dir,
        catalog_version=3,
        record_counts={"styles": 1, "beers": 1, "skus": 1, "benchmarks": 1},
        catalog_json_bytes=b'{"catalog_version": 3}',
    )

    assert manifest.build_timestamp == _GENERATED_AT
    assert manifest.source_run_month == "2026-06"
    assert len(manifest.enrichment_snapshot_version) == 12
    assert manifest.catalog_version == 3
    assert manifest.record_counts == {"styles": 1, "beers": 1, "skus": 1, "benchmarks": 1}
    assert len(manifest.content_hash) == 12


def test_manifest_to_dict_shape(tmp_path: Path):
    enrichment_dir = _setup_enrichment(tmp_path)
    manifest = build_manifest(
        build_timestamp=_GENERATED_AT,
        source_run_month="2026-06",
        enrichment_dir=enrichment_dir,
        catalog_version=3,
        record_counts={"styles": 1},
        catalog_json_bytes=b"{}",
    )
    data = manifest_to_dict(manifest)
    assert set(data.keys()) == {
        "build_timestamp",
        "source_run_month",
        "enrichment_snapshot_version",
        "catalog_version",
        "record_counts",
        "content_hash",
    }
    assert data["build_timestamp"] == "2026-08-13T10:00:00Z"


def test_write_manifest_creates_real_json_file(tmp_path: Path):
    enrichment_dir = _setup_enrichment(tmp_path)
    manifest = build_manifest(
        build_timestamp=_GENERATED_AT,
        source_run_month="2026-06",
        enrichment_dir=enrichment_dir,
        catalog_version=3,
        record_counts={"styles": 1},
        catalog_json_bytes=b"{}",
    )
    catalog_dir = tmp_path / "catalog"
    path = write_manifest(manifest, catalog_dir)

    assert path == catalog_dir / "catalog_build_manifest.json"
    written = json.loads(path.read_text())
    assert written["catalog_version"] == 3


def test_manifest_location_is_never_bundled_by_pubspec():
    # Confirmed directly: pubspec.yaml's assets: section lists the
    # specific file catalog/catalog.json, not the whole catalog/
    # directory -- a sibling manifest file is never bundled.
    pubspec = Path("pubspec.yaml").read_text()
    assert "catalog/catalog.json" in pubspec
    assert "catalog/catalog_build_manifest.json" not in pubspec
