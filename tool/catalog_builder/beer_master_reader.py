"""Loads `pricing_data/beer_master.csv` — Catalog Builder Implementation
Design Part 3. Read-only; never writes back to `pricing_data/`, and never
filters by `status` or classification confidence — that's downstream
business logic (contamination/validation layers, not yet built), and
this module's own responsibility per Part 1 is shape and parseability
only, never business meaning.

Two-tier error handling, reused exactly from the real pipeline's
`validate.py` convention: a missing/renamed column header is structural
(raises `BeerMasterReaderError`, aborts the whole load); an individual
row with an unparseable price, date, or missing required field is
row-level (returned as a `RejectedBeerMasterRow`, excluded from the
accepted list, never raised).
"""

from __future__ import annotations

import csv
from dataclasses import fields
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import BeerMasterRow, RejectedBeerMasterRow

# Confirmed directly against the real file's header — every column
# BeerMasterRow expects. Matched by name (csv.DictReader), not position,
# so column reordering or an added column never breaks this reader; only
# a missing/renamed expected column does.
EXPECTED_COLUMNS: Tuple[str, ...] = tuple(f.name for f in fields(BeerMasterRow))

_REQUIRED_STRING_FIELDS: Tuple[str, ...] = (
    "canonical_product_id",
    "representative_item_code",
    "item_name_raw",
    "display_name",
    "normalized_name_key",
    "container_type",
    "status",
    "classification_confidence",
    "classification_matched_on",
    "source_pdf_reference",
    "first_seen_run_month",
    "last_updated_run_month",
)
_OPTIONAL_STRING_FIELDS: Tuple[str, ...] = ("delisted_run_month", "gtin", "gtin_confidence")
_DECIMAL_FIELDS: Tuple[str, ...] = ("declared_price", "landed_cost", "ksbcl_selling_price", "mrp")


class BeerMasterReaderError(Exception):
    """A structural failure — the caller treats this as an abort, per
    `tool/ksbcl_pricing_pipeline/validate.py`'s own
    `PipelineValidationError` convention, one layer up."""


def _blank_to_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def read_beer_master_csv(path: Path) -> Tuple[List[BeerMasterRow], List[RejectedBeerMasterRow]]:
    """Reads every row of `path` (expected: `pricing_data/beer_master.csv`,
    never `beer_master_duty_free.csv`) into `BeerMasterRow` instances.

    Returns `(accepted_rows, rejected_rows)` — never raises for a
    row-level problem, only for a structural one (missing file, missing
    expected column).
    """
    if not path.exists() or not path.is_file():
        raise BeerMasterReaderError(f"beer_master.csv not found at {path}")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = set(EXPECTED_COLUMNS) - fieldnames
        if missing_columns:
            raise BeerMasterReaderError(
                f"beer_master.csv at {path} is missing expected column(s) "
                f"{sorted(missing_columns)} — a structural failure, not a row-level one"
            )

        accepted: List[BeerMasterRow] = []
        rejected: List[RejectedBeerMasterRow] = []

        for raw_row in reader:
            row, rejection = _validate_row(raw_row)
            if row is not None:
                accepted.append(row)
            else:
                assert rejection is not None
                rejected.append(rejection)

    return accepted, rejected


def _validate_row(
    raw_row: Dict[str, str],
) -> Tuple[Optional[BeerMasterRow], Optional[RejectedBeerMasterRow]]:
    canonical_product_id = _blank_to_none(raw_row.get("canonical_product_id"))

    def reject(reason_code: str, detail: str = "") -> Tuple[None, RejectedBeerMasterRow]:
        return None, RejectedBeerMasterRow(
            canonical_product_id=canonical_product_id,
            raw_row=dict(raw_row),
            reason_code=reason_code,
            reason_detail=detail,
        )

    values: Dict[str, object] = {}

    for field_name in _REQUIRED_STRING_FIELDS:
        value = _blank_to_none(raw_row.get(field_name))
        if value is None:
            return reject(f"missing_{field_name}")
        values[field_name] = value

    for field_name in _OPTIONAL_STRING_FIELDS:
        values[field_name] = _blank_to_none(raw_row.get(field_name))

    pack_size_raw = _blank_to_none(raw_row.get("pack_size_ml"))
    if pack_size_raw is None:
        return reject("missing_pack_size_ml")
    try:
        values["pack_size_ml"] = int(pack_size_raw)
    except ValueError:
        return reject("unparseable_pack_size_ml", pack_size_raw)

    pack_count_raw = _blank_to_none(raw_row.get("pack_count"))
    if pack_count_raw is None:
        values["pack_count"] = None
    else:
        try:
            values["pack_count"] = int(pack_count_raw)
        except ValueError:
            return reject("unparseable_pack_count", pack_count_raw)

    for field_name in _DECIMAL_FIELDS:
        raw_value = _blank_to_none(raw_row.get(field_name))
        if raw_value is None:
            return reject(f"missing_{field_name}")
        try:
            parsed = Decimal(raw_value)
        except InvalidOperation:
            return reject(f"unparseable_{field_name}", raw_value)
        if parsed <= Decimal("0"):
            return reject(f"{field_name}_not_positive", str(parsed))
        values[field_name] = parsed

    effective_date_raw = _blank_to_none(raw_row.get("effective_date"))
    if effective_date_raw is None:
        return reject("missing_effective_date")
    try:
        values["effective_date"] = date.fromisoformat(effective_date_raw)
    except ValueError:
        return reject("unparseable_effective_date", effective_date_raw)

    return (
        BeerMasterRow(
            canonical_product_id=values["canonical_product_id"],
            representative_item_code=values["representative_item_code"],
            item_name_raw=values["item_name_raw"],
            display_name=values["display_name"],
            normalized_name_key=values["normalized_name_key"],
            pack_size_ml=values["pack_size_ml"],
            pack_count=values["pack_count"],
            container_type=values["container_type"],
            declared_price=values["declared_price"],
            landed_cost=values["landed_cost"],
            ksbcl_selling_price=values["ksbcl_selling_price"],
            mrp=values["mrp"],
            effective_date=values["effective_date"],
            status=values["status"],
            delisted_run_month=values["delisted_run_month"],
            classification_confidence=values["classification_confidence"],
            classification_matched_on=values["classification_matched_on"],
            gtin=values["gtin"],
            gtin_confidence=values["gtin_confidence"],
            source_pdf_reference=values["source_pdf_reference"],
            first_seen_run_month=values["first_seen_run_month"],
            last_updated_run_month=values["last_updated_run_month"],
        ),
        None,
    )
