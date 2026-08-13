"""Value Score and Value Verdict — Catalog Builder Implementation Design
Part 5. Depends directly on `benchmarks.py`'s output (a `Benchmark`), not
on the raw per-style population — matching the implementation design's
own framing of a strict `value_metrics` -> `benchmarks` -> `value_score`
dependency chain.

`value_score`: an inverted percentile of a Sku's `cost_per_ml_alcohol`
within its Style's Benchmark (`Sku.valueScore`'s own doc comment,
`lib/shared_domain/sku.dart`: "Higher is better value"). No canonical
document specifies the exact interpolation method or the score->verdict
thresholds — both are documented, tested implementation choices below,
not a restatement of settled canon. The method: piecewise-linear
interpolation through three control points derived from the Benchmark
(p25 -> score 75, p50 -> score 50, p75 -> score 25), extrapolated beyond
either end using the boundary segment's own slope, clamped to [0, 100].
This matches the qualitative rule every canonical document already states
("below median -> better value") without inventing a fourth, undocumented
data point.

`value_verdict`: a fixed tertile mapping of `value_score`
(>=67 -> great_value, 34-66 -> fair_value, <34 -> overpriced) — matching
`ValueVerdict`'s three real values (`lib/shared_domain/sku.dart`).
"""

from __future__ import annotations

from typing import List, Tuple

from .models import Benchmark, ValueVerdict

_GREAT_VALUE_THRESHOLD = 67
_FAIR_VALUE_THRESHOLD = 34


def _interpolate(x: float, points: List[Tuple[float, float]]) -> float:
    """Piecewise-linear interpolation/extrapolation through `points`
    (sorted ascending by x-value). Degenerate segments (equal x on both
    ends) fall back to the midpoint of their y-values rather than
    dividing by zero."""
    if x <= points[0][0]:
        (x0, y0), (x1, y1) = points[0], points[1]
    elif x >= points[-1][0]:
        (x0, y0), (x1, y1) = points[-2], points[-1]
    else:
        x0 = y0 = x1 = y1 = None
        for i in range(len(points) - 1):
            if points[i][0] <= x <= points[i + 1][0]:
                x0, y0 = points[i]
                x1, y1 = points[i + 1]
                break
    if x1 == x0:
        return (y0 + y1) / 2
    weight = (x - x0) / (x1 - x0)
    return y0 + weight * (y1 - y0)


def compute_value_score(cost_per_ml_alcohol: float, benchmark: Benchmark) -> int:
    """A `Benchmark` with `sample_size < 2` can't support a meaningful
    peer comparison, so it returns a neutral 50 rather than an
    artificially precise-looking score."""
    if benchmark.sample_size < 2:
        return 50
    points = [(benchmark.p25, 75.0), (benchmark.p50, 50.0), (benchmark.p75, 25.0)]
    raw_score = _interpolate(cost_per_ml_alcohol, points)
    return max(0, min(100, round(raw_score)))


def compute_value_verdict(value_score: int) -> ValueVerdict:
    if value_score >= _GREAT_VALUE_THRESHOLD:
        return ValueVerdict.GREAT_VALUE
    if value_score >= _FAIR_VALUE_THRESHOLD:
        return ValueVerdict.FAIR_VALUE
    return ValueVerdict.OVERPRICED
