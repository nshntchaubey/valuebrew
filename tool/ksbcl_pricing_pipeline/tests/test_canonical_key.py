from decimal import Decimal

from tool.ksbcl_pricing_pipeline.canonical_key import MatchingKey, matching_key
from tool.ksbcl_pricing_pipeline.normalize_models import NormalizedRow


def _normalized(pack_size_ml, pack_count=None, container_type="bottle", normalized_name_key="kingfisher 650"):
    return NormalizedRow(
        run_month="2026-06",
        item_code="1",
        display_name="Kingfisher 650ml",
        normalized_name_key=normalized_name_key,
        pack_size_ml=pack_size_ml,
        pack_count=pack_count,
        container_type=container_type,
        normalization_rule_version="v1",
    )


def test_matching_key_returns_none_for_null_pack_size_ml():
    assert matching_key(_normalized(pack_size_ml=None)) is None


def test_matching_key_returns_all_four_components():
    key = matching_key(_normalized(pack_size_ml=Decimal("650"), pack_count=12, container_type="bottle"))
    assert key == MatchingKey(
        normalized_name_key="kingfisher 650",
        pack_size_ml=Decimal("650"),
        container_type="bottle",
        pack_count=12,
    )


def test_matching_key_ignores_supplier_code_entirely():
    # supplier_code isn't even a NormalizedRow field — this test documents
    # the Identity Decision's exclusion at the type level, not just behaviorally.
    assert not hasattr(_normalized(Decimal("650")), "supplier_code")


def test_matching_key_treats_null_pack_count_and_unknown_container_as_ordinary_values():
    key = matching_key(_normalized(pack_size_ml=Decimal("650"), pack_count=None, container_type="unknown"))
    assert key.pack_count is None
    assert key.container_type == "unknown"


def test_matching_key_decimal_equality_ignores_representation():
    key_a = matching_key(_normalized(pack_size_ml=Decimal("650")))
    key_b = matching_key(_normalized(pack_size_ml=Decimal("650.00")))
    assert key_a == key_b
    assert hash(key_a) == hash(key_b)
