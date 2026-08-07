"""Reads Stage 1's already-persisted ``run_summary.json`` back — Stage 5
needs only ``source_pdf_reference`` (Stage 5 architecture §2.1), which
exists nowhere else: it is not a field on ``structured_rows.csv`` itself
(``models.py``'s ``ProductRow``/``PRODUCT_ROW_FIELDS``).

A new, Stage-5-owned module, mirroring the project's established
per-consumer-reader convention (``classification_audit_reader.py``,
``stage1_reader.py``) — no existing reader for this file exists, and
Stage 1's own files are not modified to add one.
"""

from __future__ import annotations

import json
from pathlib import Path


def read_source_pdf_reference(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["source_pdf_reference"]
