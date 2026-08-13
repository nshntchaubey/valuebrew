"""End-to-end orchestration: `beer_master.csv` + `enrichment/` ->
`catalog/catalog.json` + `catalog_build_manifest.json` — Catalog Builder
Implementation Design Part 8's own role for this module ("the direct
analogue of `run_pipeline.py`'s role for the KSBCL pipeline"). Calls
every layer exactly once, in the exact order Part 2 of that document
specifies — the same sequence `tests/test_end_to_end_catalog_build.py`
already proved correct. No new rule, no new decision, nothing hidden:
every step below is one existing, already-tested function call.

**Defaults to a dry run.** Given how much this file matters — it is the
one asset `pubspec.yaml` bundles into the real Flutter app — running
`build_catalog.py` prints the validation report and record counts but
writes nothing unless `--write` is passed explicitly. This is the
one-command "would this build actually produce anything" check a real
founder dry run found missing; it should be safe to run constantly,
including with nothing enriched yet.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .assemble import assemble_catalog
from .beer_master_reader import read_beer_master_csv
from .build_manifest import build_manifest, write_manifest
from .business_rules import apply_business_rules
from .catalog_writer import catalog_to_json_bytes, write_catalog
from .contamination_filter import filter_contamination, load_default_exclusion_terms
from .cross_reference_validate import validate_cross_references
from .enrichment_reader import load_beers, load_styles
from .join import JoinError, join
from .validate_beer import compute_invalid_beer_keys
from .validation_report import build_validation_report
from .version import next_catalog_version


class BuildCatalogError(Exception):
    """A structural failure anywhere in the pipeline — the caller
    treats this as an abort, matching every other module's own
    convention."""


def _most_common_run_month(admitted_rows) -> str:
    if not admitted_rows:
        return "unknown"
    return Counter(row.last_updated_run_month for row in admitted_rows).most_common(1)[0][0]


def run_build(
    *,
    beer_master_path: Path,
    enrichment_dir: Path,
    catalog_path: Path,
):
    """Runs every layer exactly once, in order. Returns
    `(catalog, report, catalog_json_bytes, manifest)` — writes nothing;
    `main()` decides whether to write, based on `--write`."""
    accepted, _ = read_beer_master_csv(beer_master_path)
    exclusion_terms = load_default_exclusion_terms()
    admitted, contaminated_rows = filter_contamination(accepted, exclusion_terms)
    contaminated_ids = {r.canonical_product_id for r in contaminated_rows}

    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {s.style_key for s in styles}
    beers, rejected_beer_files = load_beers(enrichment_dir / "beers", style_keys)
    invalid_beer_keys = compute_invalid_beer_keys(enrichment_dir / "beers", enrichment_dir / "styles.yaml")

    try:
        join_result = join(admitted, contaminated_row_ids=contaminated_ids, beers=beers)
    except JoinError as exc:
        raise BuildCatalogError(f"join failed: {exc}") from exc

    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)

    report = build_validation_report(
        beers, join_result, business_result, cross_ref_result, rejected_beer_files=rejected_beer_files
    )

    catalog_version = next_catalog_version(catalog_path)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    catalog = assemble_catalog(cross_ref_result.valid, styles, catalog_version, generated_at)
    catalog_json_bytes = catalog_to_json_bytes(catalog)

    manifest = build_manifest(
        build_timestamp=generated_at,
        source_run_month=_most_common_run_month(admitted),
        enrichment_dir=enrichment_dir,
        catalog_version=catalog_version,
        record_counts={
            "styles": len(catalog.styles),
            "beers": len(catalog.beers),
            "skus": len(catalog.skus),
            "benchmarks": len(catalog.benchmarks),
        },
        catalog_json_bytes=catalog_json_bytes,
    )

    return catalog, report, catalog_json_bytes, manifest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description="Build catalog.json from beer_master.csv + enrichment/. Dry run by default."
    )
    parser.add_argument("--beer-master-path", type=Path, default=repo_root / "pricing_data" / "beer_master.csv")
    parser.add_argument("--enrichment-dir", type=Path, default=repo_root / "enrichment")
    parser.add_argument("--catalog-path", type=Path, default=repo_root / "catalog" / "catalog.json")
    parser.add_argument("--write", action="store_true", help="actually write catalog.json + the build manifest")
    args = parser.parse_args()

    try:
        catalog, report, catalog_json_bytes, manifest = run_build(
            beer_master_path=args.beer_master_path,
            enrichment_dir=args.enrichment_dir,
            catalog_path=args.catalog_path,
        )
    except BuildCatalogError as exc:
        raise SystemExit(f"Build failed: {exc}") from exc

    print(f"catalog_version:  {catalog.catalog_version}")
    print(f"generated_at:     {catalog.generated_at.isoformat()}")
    print(f"styles:           {len(catalog.styles)}")
    print(f"beers included:   {report.beers_included}")
    print(f"beers rejected:   {report.beers_rejected}")
    print(f"skus included:    {report.skus_included}")
    print(f"skus rejected:    {report.skus_rejected}")
    print(f"skus unenriched:  {report.skus_unenriched}")
    if report.rejection_reasons:
        print("rejection reasons:")
        for reason, count in report.rejection_reasons.items():
            print(f"  {reason}: {count}")

    if not args.write:
        print("\nDry run — nothing written. Pass --write to actually write catalog.json and the build manifest.")
        return

    written_bytes = write_catalog(catalog, args.catalog_path)
    manifest_path = write_manifest(manifest, args.catalog_path.parent)
    print(f"\nWrote {args.catalog_path} ({len(written_bytes)} bytes)")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
