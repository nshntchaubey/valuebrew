from decimal import Decimal

from tool.ksbcl_pricing_pipeline.normalize import extract_pack_info, fold_1_to_4, fold_5_to_6


def _matching_text(item_name_raw, supplier_code="0000"):
    display_folded, _ = fold_1_to_4(item_name_raw, supplier_code)
    return fold_5_to_6(display_folded)


# --- pack_size_ml: must extract (§4.4) --------------------------------------


def test_pack_size_ml_glued_multiplier_dominant_real_pattern():
    info = extract_pack_info(_matching_text("Haywards 5000 Premium Strong Beer 650ML×12Btls", "0217"))
    assert info.pack_size_ml == Decimal("650")


def test_pack_size_ml_no_multiplier_at_all():
    info = extract_pack_info(_matching_text("Original Bira 91 White Beer 650ML(0260)", "0260"))
    assert info.pack_size_ml == Decimal("650")


def test_pack_size_ml_space_separated_multiplier():
    info = extract_pack_info(_matching_text("Batch Distilled Gin-DF 1000ML x 12Btls", "0000"))
    assert info.pack_size_ml == Decimal("1000")


# --- pack_count: must extract / must not extract (§4.4) --------------------


def test_pack_count_glued_multiplier():
    info = extract_pack_info(_matching_text("Haywards 5000 Premium Strong Beer 650ML×12Btls", "0217"))
    assert info.pack_count == 12


def test_pack_count_cans_container_word():
    info = extract_pack_info(_matching_text("Budweiser Magnum Beer-CAN 330ML×24Cans", "0000"))
    assert info.pack_count == 24


def test_pack_count_trailing_punctuation_after_container_word():
    info = extract_pack_info(_matching_text("Brewdog Lost Lager DF 330ML X 24Btls.", "0000"))
    assert info.pack_count == 24


def test_pack_count_null_when_no_multiplier():
    info = extract_pack_info(_matching_text("Original Bira 91 White Beer 650ML(0260)", "0260"))
    assert info.pack_count is None


def test_pack_count_space_separated_multiplier_edge_case():
    info = extract_pack_info(_matching_text("Batch Distilled Gin-DF 1000ML x 12Btls", "0000"))
    assert info.pack_count == 12


# --- container_type: must extract / must default unknown (§4.4) -----------


def test_container_type_bottle_default_when_only_btls_present():
    info = extract_pack_info(_matching_text("Haywards 5000 Premium Strong Beer 650ML×12Btls", "0217"))
    assert info.container_type == "bottle"


def test_container_type_can_keyword():
    info = extract_pack_info(_matching_text("Budweiser Magnum Beer-CAN 330ML×24Cans", "0000"))
    assert info.container_type == "can"


def test_container_type_can_in_standalone_parenthetical_no_multiplier():
    info = extract_pack_info(_matching_text("Sapporo Draft Beer (Can)-Df 350ml", "0000"))
    assert info.container_type == "can"
    assert info.pack_count is None


def test_container_type_standalone_qualifier_beats_count_position_btls():
    # The confirmed real collision case (§12.1) — the fix.
    info = extract_pack_info(_matching_text("Royal Challenge Strong Premium Beer-CAN 330MLx24Btls(0217)", "0217"))
    assert info.container_type == "can"
    assert info.pack_count == 24


def test_container_type_unknown_when_no_recognized_token():
    info = extract_pack_info(_matching_text("Original Bira 91 White Beer 650ML(0260)", "0260"))
    assert info.container_type == "unknown"


# --- Edge cases (§6) ---------------------------------------------------------


def test_edge_case_container_word_before_volume_kilkenny_pattern():
    info = extract_pack_info(_matching_text("Kilkenny Drught Irish Beer - Can-DF440ML", "0000"))
    assert info.container_type == "can"
    assert info.pack_size_ml == Decimal("440")


def test_edge_case_no_volume_at_all_bundles_everything_null():
    # §4.5's bundling rule: pack_size_ml not found -> pack_count and
    # container_type are null/unknown too, even if container_type's own
    # search would otherwise have matched something.
    info = extract_pack_info("acme strong can beer no volume stated")
    assert info.pack_size_ml is None
    assert info.pack_count is None
    assert info.container_type == "unknown"


# --- Accepted limitations (§12) — confirmed to behave exactly as frozen ----


def test_accepted_limitation_p_btls_intervening_fragment_yields_null_count():
    # The documented, accepted P.Btls limitation — NOT fixed, confirmed
    # to still behave exactly as the frozen architecture specifies.
    info = extract_pack_info(
        _matching_text("The Original Haywards 5000 Super Strong Beer-PET 1500MLx6P.Btls", "0265")
    )
    assert info.pack_size_ml == Decimal("1500")
    assert info.pack_count is None  # accepted limitation, not fixed
    assert info.container_type == "pet_bottle"  # unaffected — PET is standalone


def test_accepted_limitation_bcans_not_recognized_as_container_word():
    # BCans is a confirmed real, unhandled vocabulary gap (§12) — not a
    # Stage 3 architecture concern, left unrecognized as specified.
    info = extract_pack_info(_matching_text("Tuborg Classic Black Strong Beer-Can 500MLx24BCans", "0205"))
    # "Can" appears standalone earlier in the name, so container_type
    # still resolves correctly via that independent occurrence...
    assert info.container_type == "can"
    # ...but pack_count's own adjacency check requires the text right
    # after the count to itself be a recognized container token, which
    # "bcans" is not (it starts with "b", not "can"/"cans") — so this
    # accepted vocabulary gap affects pack_count too, not just
    # container_type, exactly per the frozen rule's literal wording.
    assert info.pack_count is None


def test_accepted_limitation_canss_typo_consistent_with_bcans():
    # Confirmed real (item 2800902513): "Canss" must be treated exactly
    # like "BCans" — an unrecognized vocabulary variant — for BOTH
    # container_type (already correct) and pack_count (was a real
    # implementation bug: a bare startswith check let "canss" match the
    # "cans" prefix, inconsistently "recognizing" it here while
    # container_type's own boundary-anchored search correctly does not).
    info = extract_pack_info(
        _matching_text("Biere Blanche Blanc Kronenbourg 1664 French Beer-Can 500MLx24Canss", "0280")
    )
    assert info.container_type == "can"  # via the standalone "Can" qualifier
    assert info.pack_count is None  # "canss" is not a recognized container token


def test_unit_casing_normalizes_space_separated_unit_glued_to_multiplier():
    # §4.1 step 5 must unify "720 ML" -> "720ml" even when the multiplier
    # immediately follows with no separator — a latent bug where the old
    # regex's trailing \b silently failed to match here (no boundary
    # between "l" and "x", both letters), nulling pack_size_ml entirely.
    info = extract_pack_info(_matching_text("Kaon Wine 720 MLx12Btls", "0000"))
    assert info.pack_size_ml == Decimal("720")
    assert info.pack_count == 12


def test_accepted_limitation_bare_ltr_unit_not_recognized():
    # Confirmed real gap (§12) — only "ml" is a recognized unit; "Ltr" is
    # left unhandled exactly as the frozen architecture specifies.
    info = extract_pack_info(_matching_text("Kingfisher Dra. Lager Beer 5 Ltr. Can", "0206"))
    assert info.pack_size_ml is None
    assert info.pack_count is None
    assert info.container_type == "unknown"  # bundled null per §4.5, even though "Can" is present
