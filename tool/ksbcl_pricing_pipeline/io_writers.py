"""Atomic file writers.

Architecture §8.5: "Idempotent, all-or-nothing output. Each stage writes
to a new run-dated artifact (or a temp location promoted atomically on
success)." Every writer here follows the same pattern: write to a temp
file in the destination directory, then ``os.replace`` it into place —
so a crash mid-write never leaves a half-written CSV/JSON where a caller
might mistake it for a complete file, and re-running for the same
run_month deterministically overwrites rather than appends.
"""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, List, Mapping


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Mapping]) -> None:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    _atomic_write_text(path, buffer.getvalue())


def write_json(path: Path, data: dict) -> None:
    _atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")
