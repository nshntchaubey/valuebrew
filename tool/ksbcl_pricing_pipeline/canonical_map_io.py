"""``pricing_data/item_code_canonical_map.csv`` — Stage 4's own permanent,
cross-run persistent state (architecture §2.1, §3.1).

Mirrors Stage 2's ``ledger.py`` "thin CSV I/O shell" split: everything
above the load/save functions is pure over plain data.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from .canonical_models import CanonicalMapRow


class CanonicalMapCorruptionError(Exception):
    """A duplicate ``ksbcl_item_code`` within the persisted map itself —
    the extraction-bug-shaped structural failure architecture §10 names
    distinctly from the real-world "two item_codes, same product"
    condition, which is never an error (§6)."""


def load_canonical_map(path: Path) -> Dict[str, CanonicalMapRow]:
    """Empty dict if the file does not exist yet (§8's bootstrap case:
    first-ever run) — never an error."""
    if not path.exists():
        return {}
    result: Dict[str, CanonicalMapRow] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            item_code = row["ksbcl_item_code"]
            if item_code in result:
                raise CanonicalMapCorruptionError(
                    f"duplicate ksbcl_item_code {item_code!r} in {path} — a corrupted prior map "
                    "state (§10); this run cannot safely resolve identity against it"
                )
            result[item_code] = CanonicalMapRow(
                ksbcl_item_code=item_code,
                canonical_product_id=row["canonical_product_id"],
                supplier_name=row["supplier_name"],
                supplier_code=row["supplier_code"],
                match_confidence=row["match_confidence"],
                matched_rule=row["matched_rule"],
                item_status=row["item_status"],
                first_seen_run_month=row["first_seen_run_month"],
                last_seen_run_month=row["last_seen_run_month"],
            )
    return result


def canonical_map_rows_sorted(canonical_map: Dict[str, CanonicalMapRow]) -> List[CanonicalMapRow]:
    """Deterministic write order — sorted by ``ksbcl_item_code`` so a
    rerun that changes nothing produces a byte-identical file, mirroring
    ``ledger.known_terms_rows_sorted``."""
    return [canonical_map[item_code] for item_code in sorted(canonical_map.keys())]
