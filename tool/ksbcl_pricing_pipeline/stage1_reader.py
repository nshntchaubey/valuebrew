"""Reads Stage 1's already-persisted ``structured_rows.csv`` back into
``ProductRow`` objects.

Deliberately a new, Stage-2-owned module rather than an addition to
Stage 1's ``models.py`` — Stage 1 ships no CSV reader of its own (it
only ever writes), and this pipeline has no independent "Stage 2
standalone" entry point that accepts arbitrary CSV (§2.4): Stage 2 only
ever reads a ``structured_rows.csv`` that a real, successful Stage 1 run
already produced, at the exact path Stage 1's own architecture puts it.
Round-trips ``ProductRow.to_csv_row()`` exactly (Stage 1
``io_writers.py``): ISO dates, string-formatted decimals, item_code
read back as a plain string, never coerced to a numeric type.
"""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import List

from .models import ProductRow


def read_structured_rows(path: Path) -> List[ProductRow]:
    rows: List[ProductRow] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                ProductRow(
                    item_code=row["item_code"],
                    item_name_raw=row["item_name_raw"],
                    supplier_name=row["supplier_name"],
                    supplier_code=row["supplier_code"],
                    effective_date_raw=row["effective_date_raw"],
                    effective_date=date.fromisoformat(row["effective_date"]),
                    declared_price_raw=row["declared_price_raw"],
                    declared_price=Decimal(row["declared_price"]),
                    landed_cost_raw=row["landed_cost_raw"],
                    landed_cost=Decimal(row["landed_cost"]),
                    ksbcl_selling_price_raw=row["ksbcl_selling_price_raw"],
                    ksbcl_selling_price=Decimal(row["ksbcl_selling_price"]),
                    mrp_raw=row["mrp_raw"],
                    mrp=Decimal(row["mrp"]),
                    source_page=int(row["source_page"]),
                    run_month=row["run_month"],
                )
            )
    return rows
