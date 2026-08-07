from tool.ksbcl_pricing_pipeline.matching import fold, is_duty_free, word_boundary_match


def test_fold_case_folds():
    assert fold("BEER") == "beer"


def test_fold_unifies_multiplier_symbol():
    assert fold("330ml×24") == fold("330mlx24") == fold("330MLX24")


def test_fold_collapses_whitespace():
    assert fold("Strong   Beer\t") == "strong beer"


def test_word_boundary_match_simple_word():
    assert word_boundary_match(fold("beer"), fold("Kingfisher Strong Beer 650ML"))


def test_word_boundary_match_rejects_substring_inside_longer_word():
    # "ale" must not match inside "sale" — the exact risk §4.1 cites.
    assert not word_boundary_match(fold("ale"), fold("Grand Sale Offer"))


def test_word_boundary_match_rejects_gin_inside_engine():
    assert not word_boundary_match(fold("gin"), fold("Engine Oil Additive"))


def test_word_boundary_match_accepts_gin_as_own_word():
    assert word_boundary_match(fold("gin"), fold("Bombay Sapphire Gin 750ML"))


def test_word_boundary_match_letter_digit_transition_is_a_boundary():
    # §4.1's closed definition: a letter->digit transition is always a
    # boundary, exactly like whitespace/hyphen already is.
    assert word_boundary_match(fold("df"), fold("Brewdog Lost Lager-DF330ML"))


def test_word_boundary_match_rejects_fused_no_boundary_token():
    # Confirmed real gap, disclosed in §4.8: "Chateau Latourdf" has no
    # boundary before "df" at all (letter immediately followed by letter).
    assert not word_boundary_match(fold("df"), fold("Chateau Latourdf 750ml"))


def test_word_boundary_match_multi_word_entry_exact_canonical_form():
    assert word_boundary_match(fold("strong beer"), fold("Simba Roar Wild Strong Beer 650ML"))


def test_word_boundary_match_multi_word_entry_requires_canonical_separator():
    # Strict reading (§17 Product Decision Required): a hyphen is not
    # treated as equivalent to the declared space separator.
    assert not word_boundary_match(fold("strong beer"), fold("Simba Strong-Beer 650ML"))


def test_is_duty_free_must_match_examples_from_architecture_section_4_8():
    must_match = [
        "Corona Extra Beer -Df 330ml",
        "Brewdog Lost Lager DF 330ML X 24Btls.",
        "Antinori-DF-750MLx6Btls.",
        "Absolut Vodka Df- 750 Ml",
        "Wincarnis Original Tonic Wine-DF - F/W 750MLx12Btls",
    ]
    for name in must_match:
        assert is_duty_free(name), name


def test_is_duty_free_must_not_match_illustrative_example():
    assert not is_duty_free("Sandford Reserve 750ML")


def test_is_duty_free_disclosed_fused_token_gap_is_not_caught():
    # §4.8's own disclosed, deliberately unmitigated limitation.
    for name in ("Chateau Latourdf 750ml", "Pouilly Fuissedf 750ml", "Sparkling Winedf 750 Ml"):
        assert not is_duty_free(name), name


def test_is_duty_free_not_anchored_to_end_of_string():
    # DF preceding a parenthetical supplier-code fragment, not the volume.
    assert is_duty_free("Ichiko Shochu -Df (0336) 720 Ml")


def test_is_duty_free_false_for_ordinary_row():
    assert not is_duty_free("Kingfisher Strong Beer 650ML(0210)")
