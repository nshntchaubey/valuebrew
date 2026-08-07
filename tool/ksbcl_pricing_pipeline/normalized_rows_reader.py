"""Reads Stage 3's already-persisted ``normalized_rows.csv`` back into
``NormalizedRow`` objects.

A new, Stage-4-owned module, mirroring Stage 3's own
``classification_audit_reader.py`` pattern — no existing reader for this
file exists, and Stage 3's own files are not modified to add one.
Round-trips ``NormalizedRow.to_csv_row()`` exactly: ``pack_size_ml`` read
back as ``Decimal`` or ``None``, ``pack_count`` as ``int`` or ``None``.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from .normalize_models import NormalizedRow


def _optional_decimal(value: str) -> Optional[Decimal]:
    return Decimal(value) if value else None


def _optional_int(value: str) -> Optional[int]:
    return int(value) if value else None


def read_normalized_rows(path: Path) -> List[NormalizedRow]:
    rows: List[NormalizedRow] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                NormalizedRow(
                    run_month=row["run_month"],
                    item_code=row["item_code"],
                    display_name=row["display_name"],
                    normalized_name_key=row["normalized_name_key"],
                    pack_size_ml=_optional_decimal(row["pack_size_ml"]),
                    pack_count=_optional_int(row["pack_count"]),
                    container_type=row["container_type"],
                    normalization_rule_version=row["normalization_rule_version"],
                )
            )
    return rows
