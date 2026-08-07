"""``pricing_data/beer_master.csv`` / ``beer_master_duty_free.csv`` —
Stage 5's own permanent, overwritten-each-run state (architecture §2.2,
§3.1). One row per ``canonical_product_id`` per file, mirroring Stage
4's ``item_code_canonical_map.csv`` "thin CSV I/O shell" split.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

from .history_models import MasterRow


class MasterCorruptionError(Exception):
    """A duplicate ``canonical_product_id`` within a persisted master
    file itself — mirrors Stage 4's identical posture toward a
    duplicate ``ksbcl_item_code`` in its own map."""


def _optional_decimal(value: str) -> Optional[Decimal]:
    return Decimal(value) if value else None


def _optional_int(value: str) -> Optional[int]:
    return int(value) if value else None


def load_master(path: Path) -> Dict[str, MasterRow]:
    """Empty dict if the file does not exist yet (bootstrap) — never an
    error."""
    if not path.exists():
        return {}
    result: Dict[str, MasterRow] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = row["canonical_product_id"]
            if cid in result:
                raise MasterCorruptionError(
                    f"duplicate canonical_product_id {cid!r} in {path} — a corrupted prior master "
                    "state; this run cannot safely diff against it"
                )
            result[cid] = MasterRow(
                canonical_product_id=cid,
                representative_item_code=row["representative_item_code"],
                item_name_raw=row["item_name_raw"],
                display_name=row["display_name"],
                normalized_name_key=row["normalized_name_key"],
                pack_size_ml=_optional_decimal(row["pack_size_ml"]),
                pack_count=_optional_int(row["pack_count"]),
                container_type=row["container_type"],
                declared_price=Decimal(row["declared_price"]),
                landed_cost=Decimal(row["landed_cost"]),
                ksbcl_selling_price=Decimal(row["ksbcl_selling_price"]),
                mrp=Decimal(row["mrp"]),
                effective_date=row["effective_date"],
                status=row["status"],
                delisted_run_month=row["delisted_run_month"] or None,
                classification_confidence=row["classification_confidence"],
                classification_matched_on=row["classification_matched_on"],
                gtin=row["gtin"] or None,
                gtin_confidence=row["gtin_confidence"] or None,
                source_pdf_reference=row["source_pdf_reference"],
                first_seen_run_month=row["first_seen_run_month"],
                last_updated_run_month=row["last_updated_run_month"],
            )
    return result


def master_rows_sorted(master: Dict[str, MasterRow]) -> List[MasterRow]:
    """Deterministic write order — sorted by ``canonical_product_id`` so
    a rerun that changes nothing produces a byte-identical file."""
    return [master[cid] for cid in sorted(master.keys())]
