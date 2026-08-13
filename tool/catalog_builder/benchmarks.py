"""Per-style Value Score benchmarks — Catalog Builder Implementation
Design Part 5. Depends only on `value_metrics.py`'s output (each admitted
Sku's `cost_per_ml_alcohol`, already computed) and on knowing which Skus
this build actually admits — no I/O, no join logic here.

Percentile method: linear interpolation between closest ranks (the same
method numpy's and Excel's default percentile functions use). No
canonical document specifies an exact method, so this is a documented
implementation choice, not a restatement of settled canon — see
docs/CATALOG-CONTRACT-1.0.md Part 6, which defines the *fields* but not
the computation.
"""

from __future__ import annotations

import math
from typing import Dict, List

from .models import Benchmark


def _percentile(sorted_values: List[float], pct: float) -> float:
    """`pct` in [0, 100]. `sorted_values` must be sorted ascending and
    non-empty."""
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    rank = (pct / 100) * (n - 1)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return sorted_values[int(rank)]
    weight = rank - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def compute_benchmarks(
    cost_per_ml_alcohol_by_style: Dict[str, List[float]],
) -> List[Benchmark]:
    """One `Benchmark` per style present as a key with a non-empty value
    list. A style with no admitted Skus simply isn't a key here, and
    produces no `Benchmark` entry — omission, not a zero-filled row, per
    Catalog Contract 1.0 Part 6. Output is sorted by `style_id` for
    deterministic build output (Implementation Roadmap Part 6's
    determinism requirement)."""
    benchmarks: List[Benchmark] = []
    for style_id in sorted(cost_per_ml_alcohol_by_style):
        values = cost_per_ml_alcohol_by_style[style_id]
        if not values:
            continue
        sorted_values = sorted(values)
        benchmarks.append(
            Benchmark(
                style_id=style_id,
                avg_cost_per_ml_alcohol=sum(sorted_values) / len(sorted_values),
                p25=_percentile(sorted_values, 25),
                p50=_percentile(sorted_values, 50),
                p75=_percentile(sorted_values, 75),
                sample_size=len(sorted_values),
            )
        )
    return benchmarks
