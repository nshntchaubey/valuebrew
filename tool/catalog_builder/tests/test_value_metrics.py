from tool.catalog_builder.value_metrics import cost_per_litre, cost_per_ml_alcohol


def test_cost_per_litre_matches_hand_computed_value():
    # 110 rupees / 0.65 litres — the real placeholder catalog.json fixture
    # (kf_premium_650), hand-verified: 110 / 0.65 = 169.2307...
    assert round(cost_per_litre(price=110, size_ml=650), 2) == 169.23


def test_cost_per_litre_scales_linearly_with_size():
    assert cost_per_litre(price=200, size_ml=1000) == 200.0


def test_cost_per_ml_alcohol_matches_hand_computed_value():
    # 110 / (650 * 0.048) = 110 / 31.2 = 3.525641... rounds to 3.53.
    # (The placeholder catalog.json's own value, 3.52, is a hand-authored
    # illustrative figure, not a golden value this function is required
    # to reproduce exactly — Catalog Contract 1.0 Part 1 is explicit that
    # the placeholder predates any real Catalog Builder output.)
    assert round(cost_per_ml_alcohol(price=110, size_ml=650, abv=4.8), 2) == 3.53


def test_cost_per_ml_alcohol_is_cheaper_for_higher_abv_at_same_price_and_size():
    lower_abv = cost_per_ml_alcohol(price=150, size_ml=650, abv=5.0)
    higher_abv = cost_per_ml_alcohol(price=150, size_ml=650, abv=8.0)
    assert higher_abv < lower_abv


def test_cost_per_ml_alcohol_third_fixture_matches_hand_computed_value():
    # 145 / (500 * 0.05) = 145 / 25 = 5.8
    assert cost_per_ml_alcohol(price=145, size_ml=500, abv=5.0) == 5.8
