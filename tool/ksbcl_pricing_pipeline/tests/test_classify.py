from datetime import date
from decimal import Decimal

from tool.ksbcl_pricing_pipeline.classification_config import ClassificationConfig
from tool.ksbcl_pricing_pipeline.classify import classify_row
from tool.ksbcl_pricing_pipeline.models import ProductRow

CONFIG = ClassificationConfig(
    style_keywords=["beer", "lager", "strong beer", "witbier"],
    brand_names=["Kingfisher", "Budweiser", "Corona"],
    exclusion_terms=["whisky", "rum", "gin"],
    config_version="abc123def456",
)


def _row(item_name_raw, supplier_code="0210", item_code="10300901"):
    return ProductRow(
        item_code=item_code,
        item_name_raw=item_name_raw,
        supplier_name="Some Distillery",
        supplier_code=supplier_code,
        effective_date_raw="10-Jul-26",
        effective_date=date(2026, 7, 10),
        declared_price_raw="100.00",
        declared_price=Decimal("100.00"),
        landed_cost_raw="100.00",
        landed_cost=Decimal("100.00"),
        ksbcl_selling_price_raw="100.00",
        ksbcl_selling_price=Decimal("100.00"),
        mrp_raw="100.00",
        mrp=Decimal("100.00"),
        source_page=1,
        run_month="2026-06",
    )


def _classify(name, supplier_code="0210", known=frozenset({"0210"})):
    return classify_row(_row(name, supplier_code=supplier_code), CONFIG, known, "2026-06")


def test_style_keyword_match_is_high_and_included():
    result = _classify("Kingfisher Strong Beer 650ML")
    assert result.confidence_tier == "high"
    assert result.included is True
    assert result.matched_signal_type == "style_keyword"
    assert result.exclusion_term_matched is None


def test_style_keyword_never_vetoed_by_exclusion_term_present():
    # "Whisky" appears alongside a style keyword — must still be High,
    # per §4.2 rule 1's absolute, no-exception guarantee.
    result = _classify("Budweiser Whisky Barrel Aged Strong Beer 650ML")
    assert result.confidence_tier == "high"
    assert result.exclusion_term_matched is None


def test_style_keyword_tie_break_is_earliest_declaration_order():
    # Both "beer" and "strong beer" match; "beer" is declared first.
    result = _classify("Simba Roar Wild Premium Strong Beer 650ML")
    assert result.matched_term == "beer"


def test_brand_match_no_exclusion_familiar_supplier_is_medium():
    result = _classify("Corona Extra 330ml", known=frozenset({"0210"}))
    assert result.confidence_tier == "medium"
    assert result.included is True
    assert result.matched_signal_type == "brand_name"


def test_brand_match_with_exclusion_term_is_demoted_to_low():
    result = _classify("Budweiser Magnum Double Barrel Blended American Whisky 750ML")
    assert result.confidence_tier == "low"
    assert result.included is False
    assert result.exclusion_term_matched == "whisky"


def test_brand_match_unfamiliar_supplier_is_demoted_to_low():
    result = _classify("Corona Extra 330ml", supplier_code="9999", known=frozenset({"0210"}))
    assert result.confidence_tier == "low"
    assert result.included is False
    assert result.exclusion_term_matched is None
    assert result.supplier_known_beer_seller is False


def test_brand_match_exclusion_and_unfamiliar_supplier_both_independent_low():
    result = _classify("Budweiser Whisky Blend 750ML", supplier_code="9999", known=frozenset({"0210"}))
    assert result.confidence_tier == "low"
    assert result.exclusion_term_matched == "whisky"
    assert result.supplier_known_beer_seller is False


def test_no_match_familiar_supplier_escalates_to_low_supplier_corroboration():
    result = _classify("Some Unknown Import 330ml", known=frozenset({"0210"}))
    assert result.confidence_tier == "low"
    assert result.included is False
    assert result.matched_signal_type == "supplier_corroboration_only"
    assert result.matched_term is None


def test_no_match_unfamiliar_supplier_yields_no_row_at_all():
    result = _classify("Some Unknown Import 330ml", supplier_code="9999", known=frozenset({"0210"}))
    assert result is None


def test_is_duty_free_populated_independently_of_classification():
    result = _classify("Corona Extra Beer -Df 330ml")
    assert result.confidence_tier == "high"  # style keyword "beer"
    assert result.is_duty_free is True


def test_whisky_whiskey_spelling_gap_is_not_silently_fixed():
    # American spelling "Whiskey" is not in the configured exclusion_terms
    # (only "whisky" is) — this is a documented, permanent configuration
    # gap (architecture §16/§17), not something the matching mechanism
    # should paper over.
    result = _classify("Budweiser Magnum Double Barrel Blended American Whiskey 750ML")
    assert result.confidence_tier == "medium"
    assert result.exclusion_term_matched is None


def test_root_beer_style_keyword_match_is_the_documented_unmitigated_gap():
    # §8: no mechanism defends the style-keyword path against this —
    # the implementation must not invent one either.
    result = _classify("Acme Root Beer 330ml")
    assert result.confidence_tier == "high"
    assert result.included is True
    assert result.matched_term == "beer"


def test_supplier_familiarity_never_grants_high_or_medium_on_its_own():
    result = _classify("Totally Unrecognized Product Name 330ml", known=frozenset({"0210"}))
    assert result.confidence_tier == "low"
