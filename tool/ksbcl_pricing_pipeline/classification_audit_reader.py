"""Reads Stage 2's already-persisted ``classification_audit.csv`` back —
Stage 3 needs only ``item_code`` and ``included`` (§2.2: every other
column is opaque to Stage 3).

A new, Stage-3-owned module, mirroring Stage 2's own ``stage1_reader.py``
pattern — no existing reader for this file exists, and Stage 2's own
files are not modified to add one.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Set


def read_included_item_codes(path: Path) -> Set[str]:
    included: Set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["included"] == "true":
                included.add(row["item_code"])
    return included
