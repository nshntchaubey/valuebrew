"""``pricing_data/classification_known_terms.csv`` — the persistent,
cross-run ledger (architecture §3.4).

Every function here is pure over plain data (dicts, lists) except the
two thin CSV load/save wrappers at the bottom, mirroring Stage 1's
"pure core, thin I/O shell" split.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, FrozenSet, List, Set, Tuple

from .classification_models import ClassificationAuditRow, KnownTermRow, NewEntityRow
from .models import ProductRow

EntityKey = Tuple[str, str]  # (entity_type, value)


def _entity_keys_for_row(product_row: ProductRow, audit_row: ClassificationAuditRow) -> List[EntityKey]:
    """§3.4's write trigger: every candidate row contributes its own
    ``supplier_code`` entry, plus (where applicable) one
    ``style_keyword``/``brand_name`` entry for its ``matched_term``. A
    ``supplier_corroboration_only`` row contributes only the
    ``supplier_code`` entry, since no keyword/brand term matched."""
    keys: List[EntityKey] = [("supplier_code", product_row.supplier_code)]
    if audit_row.matched_signal_type in ("style_keyword", "brand_name"):
        keys.append((audit_row.matched_signal_type, audit_row.matched_term))
    return keys


def compute_known_supplier_codes(known_terms: Dict[EntityKey, KnownTermRow]) -> FrozenSet[str]:
    """§4.2 rule 3 / §4.5: the frozen set of supplier codes already
    confirmed to carry beer, as of the run-start snapshot."""
    return frozenset(value for (entity_type, value) in known_terms if entity_type == "supplier_code")


def entities_contributed_this_run(pairs: List[Tuple[ProductRow, ClassificationAuditRow]]) -> Set[EntityKey]:
    """The deduplicated set of (entity_type, value) pairs this run
    touched at least once — deduplicated because ``times_seen`` counts
    distinct *runs*, never row-occurrences within one (§3.4)."""
    contributed: Set[EntityKey] = set()
    for product_row, audit_row in pairs:
        contributed.update(_entity_keys_for_row(product_row, audit_row))
    return contributed


def build_new_entity_rows(
    existing: Dict[EntityKey, KnownTermRow],
    pairs: List[Tuple[ProductRow, ClassificationAuditRow]],
) -> List[NewEntityRow]:
    """§3.2: one row per entity that matched this run but is not yet in
    the pre-run snapshot, sampled from the first row (in input order)
    that contributed it. Output sorted by (entity_type, value) for a
    deterministic, diffable file."""
    first_sample: Dict[EntityKey, Tuple[str, str]] = {}
    for product_row, audit_row in pairs:
        for key in _entity_keys_for_row(product_row, audit_row):
            if key not in existing and key not in first_sample:
                first_sample[key] = (product_row.item_code, product_row.item_name_raw)

    rows = [
        NewEntityRow(entity_type=entity_type, value=value, sample_item_code=code, sample_item_name_raw=name)
        for (entity_type, value), (code, name) in first_sample.items()
    ]
    rows.sort(key=lambda r: (r.entity_type, r.value))
    return rows


def update_known_terms(
    existing: Dict[EntityKey, KnownTermRow],
    contributed: Set[EntityKey],
    run_month: str,
) -> Dict[EntityKey, KnownTermRow]:
    """§3.4's exact four-case update rule, applied once per contributed
    entity. ``run_month`` strings compare correctly with plain `<`/`>`
    since the format is always YYYY-MM (lexicographic order matches
    calendar order).
    """
    updated = dict(existing)
    for key in contributed:
        entity_type, value = key
        current = updated.get(key)

        if current is None:
            # Case 1: no existing row.
            updated[key] = KnownTermRow(
                entity_type=entity_type,
                value=value,
                first_seen_run_month=run_month,
                last_seen_run_month=run_month,
                times_seen=1,
            )
        elif run_month == current.last_seen_run_month:
            # Case 2: same-month rerun — true no-op.
            continue
        elif run_month > current.last_seen_run_month:
            # Case 3: newer-month run.
            updated[key] = KnownTermRow(
                entity_type=entity_type,
                value=value,
                first_seen_run_month=current.first_seen_run_month,
                last_seen_run_month=run_month,
                times_seen=current.times_seen + 1,
            )
        else:
            # Case 4: older-month rerun — last_seen_run_month never
            # regresses; first_seen_run_month is lowered only if this
            # run is chronologically earlier than what's already stored.
            updated[key] = KnownTermRow(
                entity_type=entity_type,
                value=value,
                first_seen_run_month=min(current.first_seen_run_month, run_month),
                last_seen_run_month=current.last_seen_run_month,
                times_seen=current.times_seen + 1,
            )
    return updated


# --------------------------------------------------------------------------
# Thin CSV I/O shell
# --------------------------------------------------------------------------


def load_known_terms(path: Path) -> Dict[EntityKey, KnownTermRow]:
    """Empty dict if the file does not exist yet (§3.4 first-ever run,
    §3.4's bootstrap handling) — never an error."""
    if not path.exists():
        return {}
    result: Dict[EntityKey, KnownTermRow] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["entity_type"], row["value"])
            result[key] = KnownTermRow(
                entity_type=row["entity_type"],
                value=row["value"],
                first_seen_run_month=row["first_seen_run_month"],
                last_seen_run_month=row["last_seen_run_month"],
                times_seen=int(row["times_seen"]),
            )
    return result


def known_terms_rows_sorted(known_terms: Dict[EntityKey, KnownTermRow]) -> List[KnownTermRow]:
    """Deterministic write order — sorted by (entity_type, value) so a
    rerun that changes nothing produces a byte-identical file."""
    return [known_terms[key] for key in sorted(known_terms.keys())]
