"""Stage 2's per-row classification mechanism (architecture §4.2, §4.5,
§4.8, §5).

``classify_row`` is a pure function — no I/O, no ledger mutation — over
one already-extracted ``ProductRow`` and a frozen snapshot of which
supplier codes are already known to carry beer. This mirrors Stage 1's
``validate_product_row``: given the same inputs, it always returns the
same result, which is what makes Phase 1's "classify against a frozen
snapshot" guarantee (§3.4) actually hold.
"""

from __future__ import annotations

from typing import FrozenSet, List, Optional

from .classification_config import ClassificationConfig
from .classification_models import ClassificationAuditRow
from .matching import fold, is_duty_free, word_boundary_match
from .models import ProductRow


def _find_earliest_declared_match(vocabulary: List[str], folded_name: str) -> Optional[str]:
    """§5: the term recorded is whichever matching entry appears
    earliest in the vocabulary's own declaration order — never
    leftmost-in-string-position, never longest-match. The architecture
    states this rule explicitly for ``style_keywords`` and
    ``brand_names`` ("the same rule applies identically to
    brand_names"); it does not separately restate it for
    ``exclusion_terms``. Reusing the identical, already-specified rule
    here — rather than inventing a different one — is the only way to
    keep ``exclusion_term_matched`` deterministic when a row's name
    happens to contain more than one spirit-family term, consistent
    with §9's determinism being the primary correctness criterion. See
    the completion report's Assumptions section.
    """
    for term in vocabulary:
        if word_boundary_match(fold(term), folded_name):
            return term
    return None


def classify_row(
    row: ProductRow,
    config: ClassificationConfig,
    known_supplier_codes: FrozenSet[str],
    run_month: str,
) -> Optional[ClassificationAuditRow]:
    """Classify one row per §4.2's four-layer mechanism.

    ``known_supplier_codes`` must be the frozen, run-start snapshot of
    confirmed beer-carrying supplier codes (§3.4's two-phase execution
    model) — never anything mutated during this same run.

    Returns ``None`` for a row matching nothing at all (§4.6) — no
    ``classification_audit.csv`` row is ever written for that case, by
    design.
    """
    folded_name = fold(row.item_name_raw)
    duty_free = is_duty_free(row.item_name_raw)
    supplier_familiar = row.supplier_code in known_supplier_codes

    # Rule 1: style-keyword allowlist (primary) — never vetoed by anything
    # below, without exception (§4.2 rule 1).
    matched_style = _find_earliest_declared_match(config.style_keywords, folded_name)
    if matched_style is not None:
        return ClassificationAuditRow(
            run_month=run_month,
            item_code=row.item_code,
            confidence_tier="high",
            included=True,
            matched_signal_type="style_keyword",
            matched_term=matched_style,
            exclusion_term_matched=None,
            supplier_known_beer_seller=supplier_familiar,
            is_duty_free=duty_free,
            classification_config_version=config.config_version,
        )

    # Rule 2: brand-name allowlist (secondary) — only reached when no
    # style keyword matched.
    matched_brand = _find_earliest_declared_match(config.brand_names, folded_name)
    if matched_brand is not None:
        # Rule 3: exclusion / demotion guard — demotes to Low if either
        # condition holds (§4.2 rule 3, master architecture §6.2).
        matched_exclusion = _find_earliest_declared_match(config.exclusion_terms, folded_name)
        if matched_exclusion is not None or not supplier_familiar:
            return ClassificationAuditRow(
                run_month=run_month,
                item_code=row.item_code,
                confidence_tier="low",
                included=False,
                matched_signal_type="brand_name",
                matched_term=matched_brand,
                exclusion_term_matched=matched_exclusion,
                supplier_known_beer_seller=supplier_familiar,
                is_duty_free=duty_free,
                classification_config_version=config.config_version,
            )
        return ClassificationAuditRow(
            run_month=run_month,
            item_code=row.item_code,
            confidence_tier="medium",
            included=True,
            matched_signal_type="brand_name",
            matched_term=matched_brand,
            exclusion_term_matched=None,
            supplier_known_beer_seller=supplier_familiar,
            is_duty_free=duty_free,
            classification_config_version=config.config_version,
        )

    # Rule 4: supplier corroboration — escalates a no-match row from
    # silent none to a visible, reviewable Low (§4.5). Never grants High
    # or Medium on its own.
    if supplier_familiar:
        return ClassificationAuditRow(
            run_month=run_month,
            item_code=row.item_code,
            confidence_tier="low",
            included=False,
            matched_signal_type="supplier_corroboration_only",
            matched_term=None,
            exclusion_term_matched=None,
            supplier_known_beer_seller=True,
            is_duty_free=duty_free,
            classification_config_version=config.config_version,
        )

    # No match at all -> none tier, no row emitted (§4.6).
    return None
