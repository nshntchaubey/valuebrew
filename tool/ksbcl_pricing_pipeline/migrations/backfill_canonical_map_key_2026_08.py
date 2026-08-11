"""One-time backfill: adds the persisted matching-key fields
(``normalized_name_key``, ``pack_size_ml``, ``pack_count``,
``container_type``) to the real, on-disk ``pricing_data/item_code_canonical_map.csv``.

This script is not meant to be reused or generalized — it exists to
migrate the one real dataset this pipeline has ever produced (the
2026-06 run) from the pre-fix 9-column schema to the persisted-key
13-column schema described in ``KSBCL-Stage-4-Canonical-Identity-Architecture.md``
§3.1. Safe to delete once run successfully in the intended environment.

Usage:
    python -m tool.ksbcl_pricing_pipeline.migrations.backfill_canonical_map_key_2026_08

Steps:
    0. Precondition check — exit inertly if already migrated, before
       touching anything else. This must run *before* the backup step:
       backing up unconditionally first would, on a second invocation,
       overwrite a correct pre-migration backup with a copy of the
       already-migrated file — destroying the one thing the backup
       exists to preserve. (This was a real defect in an earlier version
       of this script, found by an independent implementation audit and
       confirmed to have already corrupted the real backup file's
       evidentiary value, though never the real map file itself. See
       `KSBCL-Engineering-Process-Retrospective.md` §10, lesson 4.)
    1. Back up the current map file, verify the backup matches — only
       reached once step 0 has confirmed there's a genuine pre-migration
       file to back up.
    2. Read the old-schema map and the source run's normalized_rows.csv.
    3. Join every map row onto its normalized_rows.csv row by item_code;
       any miss is a hard error, never a silent skip.
    4. Write the new 13-column file atomically.
    5. Verify: row count unchanged, every pre-existing field byte-identical,
       only the four new columns added.
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path
from typing import Dict, List

from ..canonical_models import CANONICAL_MAP_FIELDS
from ..io_writers import write_csv

# Hardcoded to the one real run this pipeline has ever produced — this
# script is a one-time migration for that specific dataset, not a
# general-purpose tool.
OUTPUT_ROOT = Path("pricing_data")
SOURCE_RUN_MONTH = "2026-06"

OLD_SCHEMA_FIELDS = [
    "ksbcl_item_code",
    "canonical_product_id",
    "supplier_name",
    "supplier_code",
    "match_confidence",
    "matched_rule",
    "item_status",
    "first_seen_run_month",
    "last_seen_run_month",
]

NEW_KEY_FIELDS = ["normalized_name_key", "pack_size_ml", "pack_count", "container_type"]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def backfill(output_root: Path = OUTPUT_ROOT, source_run_month: str = SOURCE_RUN_MONTH) -> int:
    canonical_map_path = output_root / "item_code_canonical_map.csv"
    normalized_rows_path = output_root / "runs" / source_run_month / "normalized_rows.csv"
    backup_path = canonical_map_path.with_name(canonical_map_path.name + ".pre-migration-backup")

    if not canonical_map_path.exists():
        print(f"no {canonical_map_path} found — nothing to migrate", file=sys.stderr)
        return 1

    # Step 0 — precondition check, first, before anything is touched or
    # backed up. Only a confirmed, genuine pre-migration file proceeds
    # past this point.
    with canonical_map_path.open(newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    if all(field in header for field in NEW_KEY_FIELDS):
        print("already migrated (matching-key columns present) — nothing to do")
        return 0
    if header != OLD_SCHEMA_FIELDS:
        print(
            f"unexpected header — neither the known pre-migration schema nor the post-migration "
            f"schema: {header}",
            file=sys.stderr,
        )
        return 1

    # Step 1 — backup, only now that step 0 has confirmed this really is
    # a pre-migration file worth preserving.
    backup_path.write_bytes(canonical_map_path.read_bytes())
    original_rows = _read_csv_rows(canonical_map_path)
    backup_rows = _read_csv_rows(backup_path)
    if len(backup_rows) != len(original_rows) or _sha256(backup_path) != _sha256(canonical_map_path):
        print("backup verification failed — refusing to proceed", file=sys.stderr)
        return 1
    print(f"backup written and verified: {backup_path} ({len(backup_rows)} rows)")

    if not normalized_rows_path.exists():
        print(f"no {normalized_rows_path} found — cannot source the matching key", file=sys.stderr)
        return 1

    # Step 2/3 — join every map row onto normalized_rows.csv by item_code.
    normalized_by_code = {row["item_code"]: row for row in _read_csv_rows(normalized_rows_path)}

    migrated_rows: List[Dict[str, str]] = []
    for row in original_rows:
        item_code = row["ksbcl_item_code"]
        source = normalized_by_code.get(item_code)
        if source is None:
            print(
                f"item_code {item_code!r} in the canonical map has no corresponding row in "
                f"{normalized_rows_path} — cannot backfill its matching key; aborting without "
                "writing anything (the original file and its backup are untouched)",
                file=sys.stderr,
            )
            return 1
        migrated_row = dict(row)
        migrated_row["normalized_name_key"] = source["normalized_name_key"]
        migrated_row["pack_size_ml"] = source["pack_size_ml"]
        migrated_row["pack_count"] = source["pack_count"]
        migrated_row["container_type"] = source["container_type"]
        migrated_rows.append(migrated_row)

    # Step 4 — write atomically (write_csv already writes to a temp file
    # in the destination directory and os.replace()s it into place).
    write_csv(canonical_map_path, CANONICAL_MAP_FIELDS, migrated_rows)

    # Step 5 — verify.
    final_rows = _read_csv_rows(canonical_map_path)
    if len(final_rows) != len(original_rows):
        print(
            f"row count changed ({len(original_rows)} -> {len(final_rows)}) — this should be "
            "impossible; restore from the backup and investigate",
            file=sys.stderr,
        )
        return 1
    for original, final in zip(original_rows, final_rows):
        for field in OLD_SCHEMA_FIELDS:
            if original[field] != final[field]:
                print(
                    f"pre-existing field {field!r} changed for item_code {original['ksbcl_item_code']!r} "
                    "— this should be impossible; restore from the backup and investigate",
                    file=sys.stderr,
                )
                return 1

    print(f"migration complete: {len(final_rows)} rows, matching-key fields backfilled from {normalized_rows_path}")
    return 0


if __name__ == "__main__":
    sys.exit(backfill())
