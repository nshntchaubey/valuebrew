from tool.ksbcl_pricing_pipeline.normalize import (
    fold_1_to_4,
    fold_5_to_6,
    strip_supplier_code_fragment,
)


def test_fold_1_to_4_confirmed_real_example():
    # §4.2's own worked example.
    text, malformed = fold_1_to_4("Original Bira 91 White Beer 650ML(0260)", "0260")
    assert text == "Original Bira 91 White Beer 650ML"
    assert malformed is False


def test_fold_5_to_6_confirmed_real_example():
    # §4.3's own worked example, continuing from §4.2's output.
    display_folded = "Original Bira 91 White Beer 650ML"
    assert fold_5_to_6(display_folded) == "original bira 91 white beer 650ml"


def test_suffix_strip_trailing_case():
    text, malformed = strip_supplier_code_fragment("Kingfisher Strong Beer 650ML(0210)", "0210")
    assert text == "Kingfisher Strong Beer 650ML"
    assert malformed is False


def test_suffix_strip_position_independent_confirmed_real_row():
    # §4.1's own cited confirmed real row: fragment precedes the volume.
    text, malformed = strip_supplier_code_fragment("Sapporo Draft Beer (Can) (0364) 350 Ml", "0364")
    assert text == "Sapporo Draft Beer (Can) 350 Ml"
    assert malformed is False


def test_suffix_strip_tolerates_missing_open_paren():
    text, malformed = strip_supplier_code_fragment("Some Beer 650ML0364)", "0364")
    assert text == "Some Beer 650ML"
    assert malformed is True


def test_suffix_strip_no_match_leaves_text_unchanged():
    text, malformed = strip_supplier_code_fragment("Kingfisher Strong Beer 650ML", "0210")
    assert text == "Kingfisher Strong Beer 650ML"
    assert malformed is False


def test_fold_step_2_unifies_multiplier_symbol_before_display_name():
    # §4.1: display_name is produced after step 4, which is after step 2 —
    # the multiplier symbol is unified even in the display-facing output.
    text, _ = fold_1_to_4("Haywards 5000 Premium Strong Beer 650ML×12Btls(0217)", "0217")
    assert text == "Haywards 5000 Premium Strong Beer 650MLx12Btls"


def test_fold_collapses_whitespace():
    text, _ = fold_1_to_4("Kingfisher   Strong   Beer  650ML", "0210")
    assert text == "Kingfisher Strong Beer 650ML"


def test_full_pipeline_end_to_end_confirmed_real_row():
    item_name_raw = "Original Bira 91 White Beer 650ML(0260)"
    display_folded, malformed = fold_1_to_4(item_name_raw, "0260")
    matching_text = fold_5_to_6(display_folded)
    assert display_folded == "Original Bira 91 White Beer 650ML"  # display_name
    assert matching_text == "original bira 91 white beer 650ml"  # normalized_name_key
    assert malformed is False
