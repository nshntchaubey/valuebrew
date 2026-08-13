from tool.catalog_builder.models import Benchmark, ValueVerdict
from tool.catalog_builder.value_score import compute_value_score, compute_value_verdict

_BENCHMARK = Benchmark(
    style_id="lager",
    avg_cost_per_ml_alcohol=3.0,
    p25=2.5,
    p50=3.0,
    p75=3.5,
    sample_size=42,
)


def test_at_median_cost_scores_fifty():
    assert compute_value_score(3.0, _BENCHMARK) == 50


def test_below_median_cost_scores_above_fifty():
    # Cheaper than the style median -> better value -> higher score.
    score = compute_value_score(2.75, _BENCHMARK)
    assert score > 50


def test_above_median_cost_scores_below_fifty():
    # Pricier than the style median -> worse value -> lower score.
    score = compute_value_score(3.25, _BENCHMARK)
    assert score < 50


def test_at_p25_scores_seventy_five():
    assert compute_value_score(2.5, _BENCHMARK) == 75


def test_at_p75_scores_twenty_five():
    assert compute_value_score(3.5, _BENCHMARK) == 25


def test_extreme_cheap_outlier_clamps_at_one_hundred():
    assert compute_value_score(0.1, _BENCHMARK) == 100


def test_extreme_expensive_outlier_clamps_at_zero():
    assert compute_value_score(50.0, _BENCHMARK) == 0


def test_thin_sample_benchmark_returns_neutral_score():
    thin_benchmark = Benchmark(
        style_id="stout", avg_cost_per_ml_alcohol=4.2, p25=4.2, p50=4.2, p75=4.2, sample_size=1
    )
    assert compute_value_score(4.2, thin_benchmark) == 50


def test_great_value_verdict_at_or_above_threshold():
    assert compute_value_verdict(67) == ValueVerdict.GREAT_VALUE
    assert compute_value_verdict(100) == ValueVerdict.GREAT_VALUE


def test_fair_value_verdict_in_middle_band():
    assert compute_value_verdict(66) == ValueVerdict.FAIR_VALUE
    assert compute_value_verdict(34) == ValueVerdict.FAIR_VALUE


def test_overpriced_verdict_below_threshold():
    assert compute_value_verdict(33) == ValueVerdict.OVERPRICED
    assert compute_value_verdict(0) == ValueVerdict.OVERPRICED


def test_below_median_fixture_end_to_end_yields_great_or_fair_value():
    # Direct chain: a SKU priced below its style's median should never
    # come out "overpriced".
    score = compute_value_score(2.75, _BENCHMARK)
    verdict = compute_value_verdict(score)
    assert verdict in (ValueVerdict.GREAT_VALUE, ValueVerdict.FAIR_VALUE)


def test_above_median_fixture_end_to_end_never_yields_great_value():
    score = compute_value_score(3.25, _BENCHMARK)
    verdict = compute_value_verdict(score)
    assert verdict != ValueVerdict.GREAT_VALUE
