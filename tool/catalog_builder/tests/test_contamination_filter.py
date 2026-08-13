from datetime import date
from decimal import Decimal
from pathlib import Path

from tool.catalog_builder.beer_master_reader import read_beer_master_csv
from tool.catalog_builder.contamination_filter import filter_contamination, load_default_exclusion_terms
from tool.catalog_builder.models import BeerMasterRow

_EXCLUSION_TERMS = ["whisky", "whiskey", "rum", "brandy", "vodka", "gin"]


def _row(**overrides) -> BeerMasterRow:
    defaults = dict(
        canonical_product_id="CP0000002",
        representative_item_code="2020900211",
        item_name_raw="Kingfisher Premium Lager Beer-CAN 330ML(0202)",
        display_name="Kingfisher Premium Lager Beer-CAN 330ML",
        normalized_name_key="kingfisher premium lager beer-can 330ml",
        pack_size_ml=330,
        pack_count=None,
        container_type="can",
        declared_price=Decimal("666.90"),
        landed_cost=Decimal("2095.74"),
        ksbcl_selling_price=Decimal("2106.22"),
        mrp=Decimal("100.00"),
        effective_date=date(2025, 5, 16),
        status="LIVE",
        delisted_run_month=None,
        classification_confidence="high",
        classification_matched_on="style_keyword:beer",
        gtin=None,
        gtin_confidence=None,
        source_pdf_reference="x.pdf",
        first_seen_run_month="2026-06",
        last_updated_run_month="2026-06",
    )
    defaults.update(overrides)
    return BeerMasterRow(**defaults)


# ---------------------------------------------------------------------------
# The two real, confirmed contamination fixtures
# ---------------------------------------------------------------------------


def test_cp0000001_budweiser_whiskey_is_rejected():
    # Real row: caught at only medium confidence via a brand-only match
    # (Budweiser sells both beer and whiskey) — Stage 2's own exclusion
    # guard never fired for it.
    row = _row(
        canonical_product_id="CP0000001",
        item_name_raw="Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls(0139)",
        display_name="Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls",
        classification_confidence="medium",
        classification_matched_on="brand_name:Budweiser",
    )
    admitted, rejected = filter_contamination([row], _EXCLUSION_TERMS)

    assert admitted == []
    assert len(rejected) == 1
    assert rejected[0].canonical_product_id == "CP0000001"
    assert rejected[0].reason_code == "contamination_gate_matched_exclusion_term"
    assert "whiskey" in rejected[0].reason_detail


def test_cp0000955_glenfiddich_ipa_experiment_whisky_is_rejected():
    # Real row: caught at HIGH confidence via style_keyword:ipa, because
    # its own product name contains "IPA" — a genuine adversarial case.
    # This is the exact scenario the request calls out: a misleading
    # beer-related keyword in a non-beer product's name.
    row = _row(
        canonical_product_id="CP0000955",
        item_name_raw=(
            "Glenfiddich Experimental Series #01 Single Malt Scotch Whisky "
            "IPA Experiment 700MLx12Btls(0380)"
        ),
        display_name="Glenfiddich Experimental Series #01 Single Malt Scotch Whisky IPA Experiment 700MLx12Btls",
        classification_confidence="high",
        classification_matched_on="style_keyword:ipa",
    )
    admitted, rejected = filter_contamination([row], _EXCLUSION_TERMS)

    assert admitted == []
    assert len(rejected) == 1
    assert rejected[0].canonical_product_id == "CP0000955"
    assert rejected[0].reason_code == "contamination_gate_matched_exclusion_term"
    assert "whisky" in rejected[0].reason_detail


def test_high_confidence_does_not_protect_a_matched_row():
    # The whole point of this gate: it ignores classification_confidence
    # entirely, unlike Stage 2's own classifier.
    row = _row(item_name_raw="Any Whisky Product 700ML", classification_confidence="high")
    admitted, rejected = filter_contamination([row], _EXCLUSION_TERMS)
    assert admitted == []
    assert len(rejected) == 1


# ---------------------------------------------------------------------------
# Real beers pass through
# ---------------------------------------------------------------------------


def test_real_beer_row_is_admitted():
    admitted, rejected = filter_contamination([_row()], _EXCLUSION_TERMS)
    assert rejected == []
    assert len(admitted) == 1
    assert admitted[0].canonical_product_id == "CP0000002"


def test_word_boundary_correctness_reused_gin_inside_engine_does_not_match():
    # Reuses matching.py's own word_boundary_match — "gin" must not
    # match inside "Engine". A regex/substring-only filter would get
    # this wrong; this one must not.
    row = _row(item_name_raw="Engine Cleaner Spray 500ML")
    admitted, rejected = filter_contamination([row], _EXCLUSION_TERMS)
    assert rejected == []
    assert len(admitted) == 1


def test_gin_as_its_own_word_is_rejected():
    row = _row(item_name_raw="Bombay Sapphire Gin 750ML")
    admitted, rejected = filter_contamination([row], _EXCLUSION_TERMS)
    assert admitted == []
    assert len(rejected) == 1


# ---------------------------------------------------------------------------
# Determinism and no mutation
# ---------------------------------------------------------------------------


def test_output_is_deterministic_across_calls():
    rows = [_row(canonical_product_id="CP0000002"), _row(canonical_product_id="CP0000001", item_name_raw="X Whiskey")]
    first = filter_contamination(rows, _EXCLUSION_TERMS)
    second = filter_contamination(rows, _EXCLUSION_TERMS)
    assert first == second


def test_input_rows_are_not_mutated():
    row = _row(item_name_raw="Some Whiskey Product")
    original = row
    filter_contamination([row], _EXCLUSION_TERMS)
    # BeerMasterRow is frozen, so mutation would raise at the type level
    # regardless — this asserts the same object/values still hold.
    assert row == original
    assert row.item_name_raw == "Some Whiskey Product"


def test_preserves_input_order_for_admitted_rows():
    rows = [_row(canonical_product_id="CP0000003"), _row(canonical_product_id="CP0000002")]
    admitted, _ = filter_contamination(rows, _EXCLUSION_TERMS)
    assert [r.canonical_product_id for r in admitted] == ["CP0000003", "CP0000002"]


# ---------------------------------------------------------------------------
# Vocabulary source
# ---------------------------------------------------------------------------


def test_load_default_exclusion_terms_reuses_the_live_pipeline_config():
    terms = load_default_exclusion_terms()
    assert "whisky" in terms
    assert "whiskey" in terms
    assert "rum" in terms


# ---------------------------------------------------------------------------
# Real end-to-end run
# ---------------------------------------------------------------------------


def test_real_beer_master_csv_rejects_exactly_the_two_known_contaminants():
    accepted, _ = read_beer_master_csv(Path("pricing_data/beer_master.csv"))
    terms = load_default_exclusion_terms()

    admitted, rejected = filter_contamination(accepted, terms)

    rejected_ids = {r.canonical_product_id for r in rejected}
    assert rejected_ids == {"CP0000001", "CP0000955"}
    assert len(admitted) == len(accepted) - 2
