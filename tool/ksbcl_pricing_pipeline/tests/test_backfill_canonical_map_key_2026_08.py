import csv
from decimal import Decimal

from tool.ksbcl_pricing_pipeline.io_writers import write_csv
from tool.ksbcl_pricing_pipeline.migrations.backfill_canonical_map_key_2026_08 import (
    NEW_KEY_FIELDS,
    OLD_SCHEMA_FIELDS,
    backfill,
)
from tool.ksbcl_pricing_pipeline.normalize_models import NORMALIZED_ROW_FIELDS, NormalizedRow

RUN_MONTH = "2026-06"


def _old_schema_row(item_code, canonical_product_id="CP0000001"):
    return {
        "ksbcl_item_code": item_code,
        "canonical_product_id": canonical_product_id,
        "supplier_name": "United Breweries",
        "supplier_code": "0210",
        "match_confidence": "unreviewed",
        "matched_rule": "new_canonical",
        "item_status": "LIVE",
        "first_seen_run_month": RUN_MONTH,
        "last_seen_run_month": RUN_MONTH,
    }


def _normalized_row(item_code):
    return NormalizedRow(
        run_month=RUN_MONTH,
        item_code=item_code,
        display_name="Kingfisher Strong Beer 650ml",
        normalized_name_key="kingfisher strong beer 650ml",
        pack_size_ml=Decimal("650"),
        pack_count=None,
        container_type="bottle",
        normalization_rule_version="v1",
    )


def _read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _setup(tmp_path, item_codes=("1001", "1002")):
    output_root = tmp_path / "pricing_data"
    canonical_map_path = output_root / "item_code_canonical_map.csv"
    normalized_rows_path = output_root / "runs" / RUN_MONTH / "normalized_rows.csv"

    write_csv(canonical_map_path, OLD_SCHEMA_FIELDS, [_old_schema_row(code) for code in item_codes])
    write_csv(
        normalized_rows_path, NORMALIZED_ROW_FIELDS, (r.to_csv_row() for r in [_normalized_row(c) for c in item_codes])
    )
    return output_root, canonical_map_path, normalized_rows_path


def test_first_execution_migrates_and_creates_correct_backup(tmp_path):
    output_root, canonical_map_path, _ = _setup(tmp_path)
    pre_migration_bytes = canonical_map_path.read_bytes()

    assert backfill(output_root=output_root, source_run_month=RUN_MONTH) == 0

    migrated_rows = _read_csv(canonical_map_path)
    assert len(migrated_rows) == 2
    for field in NEW_KEY_FIELDS:
        assert field in migrated_rows[0]
    assert migrated_rows[0]["normalized_name_key"] == "kingfisher strong beer 650ml"
    assert migrated_rows[0]["pack_size_ml"] == "650"

    backup_path = canonical_map_path.with_name(canonical_map_path.name + ".pre-migration-backup")
    assert backup_path.exists()
    # The backup must be the true pre-migration (old-schema) snapshot,
    # byte-for-byte -- not a copy of the migrated output.
    assert backup_path.read_bytes() == pre_migration_bytes
    with backup_path.open(newline="", encoding="utf-8") as f:
        backup_header = next(csv.reader(f))
    assert backup_header == OLD_SCHEMA_FIELDS
    assert not any(field in backup_header for field in NEW_KEY_FIELDS)


def test_second_execution_is_inert_and_does_not_disturb_the_backup(tmp_path):
    output_root, canonical_map_path, _ = _setup(tmp_path)
    backup_path = canonical_map_path.with_name(canonical_map_path.name + ".pre-migration-backup")

    assert backfill(output_root=output_root, source_run_month=RUN_MONTH) == 0
    backup_after_first_run = backup_path.read_bytes()
    migrated_after_first_run = canonical_map_path.read_bytes()

    # The precise regression this test exists for: an earlier version of
    # this script backed up unconditionally *before* checking whether a
    # migration was even needed, so a second run copied the
    # already-migrated (13-column) file over the backup, destroying the
    # true pre-migration snapshot. That must not happen anymore.
    assert backfill(output_root=output_root, source_run_month=RUN_MONTH) == 0

    assert backup_path.read_bytes() == backup_after_first_run
    with backup_path.open(newline="", encoding="utf-8") as f:
        backup_header = next(csv.reader(f))
    assert backup_header == OLD_SCHEMA_FIELDS  # still the old schema, not overwritten
    assert canonical_map_path.read_bytes() == migrated_after_first_run  # main output also unchanged


def test_backup_artifact_preserves_true_pre_migration_state_across_repeated_runs(tmp_path):
    """A sharper version of the above: run three times, and check the
    backup's actual row data (not just its header) never drifts from the
    original pre-migration values."""
    output_root, canonical_map_path, _ = _setup(tmp_path)
    backup_path = canonical_map_path.with_name(canonical_map_path.name + ".pre-migration-backup")

    for _ in range(3):
        assert backfill(output_root=output_root, source_run_month=RUN_MONTH) == 0

    backup_rows = _read_csv(backup_path)
    assert len(backup_rows) == 2
    for row in backup_rows:
        assert set(row.keys()) == set(OLD_SCHEMA_FIELDS)  # no key fields ever leaked in
        assert row["match_confidence"] == "unreviewed"
        assert row["item_status"] == "LIVE"


def test_migrated_output_fields_are_preserved_exactly_across_repeated_runs(tmp_path):
    output_root, canonical_map_path, _ = _setup(tmp_path)

    assert backfill(output_root=output_root, source_run_month=RUN_MONTH) == 0
    first_rows = {r["ksbcl_item_code"]: r for r in _read_csv(canonical_map_path)}

    assert backfill(output_root=output_root, source_run_month=RUN_MONTH) == 0
    second_rows = {r["ksbcl_item_code"]: r for r in _read_csv(canonical_map_path)}

    assert first_rows == second_rows
    for item_code in ("1001", "1002"):
        assert second_rows[item_code]["canonical_product_id"] == "CP0000001"
        assert second_rows[item_code]["normalized_name_key"] == "kingfisher strong beer 650ml"
        assert second_rows[item_code]["pack_size_ml"] == "650"
        assert second_rows[item_code]["container_type"] == "bottle"
