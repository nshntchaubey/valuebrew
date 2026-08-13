from tool.catalog_builder.benchmarks import compute_benchmarks


def test_avg_p25_p50_p75_match_hand_computed_values():
    # A clean, evenly-spaced fixture population for "lager":
    # [2.0, 2.5, 3.0, 3.5, 4.0] — five values, hand-computable exactly
    # under linear interpolation.
    result = compute_benchmarks({"lager": [2.0, 2.5, 3.0, 3.5, 4.0]})
    assert len(result) == 1
    benchmark = result[0]
    assert benchmark.style_id == "lager"
    assert benchmark.sample_size == 5
    assert benchmark.avg_cost_per_ml_alcohol == 3.0
    assert benchmark.p25 == 2.5
    assert benchmark.p50 == 3.0
    assert benchmark.p75 == 3.5


def test_single_sample_style_has_all_percentiles_equal_to_the_one_value():
    result = compute_benchmarks({"stout": [4.2]})
    assert len(result) == 1
    benchmark = result[0]
    assert benchmark.sample_size == 1
    assert benchmark.avg_cost_per_ml_alcohol == 4.2
    assert benchmark.p25 == benchmark.p50 == benchmark.p75 == 4.2


def test_style_with_no_admitted_skus_produces_no_benchmark_entry():
    # Catalog Contract 1.0 Part 6: omission, not a zero-filled row.
    result = compute_benchmarks({"lager": [2.0, 3.0], "wheat": []})
    style_ids = [b.style_id for b in result]
    assert style_ids == ["lager"]


def test_output_sorted_by_style_id_for_deterministic_build_output():
    result = compute_benchmarks({"wheat": [3.0], "lager": [2.0], "ipa": [4.0]})
    assert [b.style_id for b in result] == ["ipa", "lager", "wheat"]


def test_input_dict_with_no_styles_returns_empty_list():
    assert compute_benchmarks({}) == []
