"""The independent, catalog-build-layer contamination gate — Catalog
Builder Architecture Part 7, Catalog Builder Implementation Design
Part 6. Rejects any row whose `item_name_raw` matches a spirit-family
exclusion term, **regardless of `classification_confidence`** — this is
the fix for exactly the two confirmed-live contaminants (`CP0000001`,
`CP0000955`) that fooled Stage 2's own classifier, one at `medium`
confidence via a brand-only match, the other at `high` confidence via a
style-keyword match (`style_keyword:ipa`) despite being a real whisky.
Stage 2's own exclusion guard only ever vetoes a brand-only match, never
a style-keyword match (KSBCL pipeline architecture §6.1) — this gate
checks the raw name directly, independent of *how* Stage 2 classified
the row, so a misleading beer-related keyword in a non-beer product's own
name can no longer slip through.

**Vocabulary source — Implementation Blocker #3 (Implementation Roadmap),
resolved here rather than left open.** Imports
`tool.ksbcl_pricing_pipeline.classification_config.load_classification_config`
and reuses its `exclusion_terms` directly, instead of maintaining an
independent copy. Why: the concrete, named risk of an independent copy
(Catalog Builder Architecture Part 7) is silent vocabulary drift between
this gate and Stage 2's own; importing the live config makes drift
structurally impossible, and this gate automatically inherits the
whiskey-exclusion-terms fix already committed to `beer_classification.yaml`
without duplicating it. This creates one real, deliberate cross-package
dependency (`tool/catalog_builder` -> `tool/ksbcl_pricing_pipeline`) —
intended as the permanent choice, not a stand-in for a decision made
later; if a future need ever requires these two vocabularies to diverge,
that would be a fresh, explicit decision, not an accident this design
protects against for free today.

**Matching — reused, not reimplemented.** `fold`/`word_boundary_match`
are imported directly from `tool.ksbcl_pricing_pipeline.matching`, the
exact primitives Stage 2 itself uses, per the explicit instruction not to
build a new classifier. This is a deterministic, boundary-anchored
substring check — nothing probabilistic, nothing learned.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from tool.ksbcl_pricing_pipeline.classification_config import load_classification_config
from tool.ksbcl_pricing_pipeline.matching import fold, word_boundary_match

from .models import BeerMasterRow, RejectedBeerMasterRow

_DEFAULT_CLASSIFICATION_CONFIG_PATH = (
    Path(__file__).resolve().parents[1] / "ksbcl_pricing_pipeline" / "beer_classification.yaml"
)


def load_default_exclusion_terms(config_path: Path = _DEFAULT_CLASSIFICATION_CONFIG_PATH) -> List[str]:
    """The KSBCL pipeline's own live `exclusion_terms` vocabulary —
    see this module's own docstring for why this gate reuses it directly
    rather than maintaining an independent copy."""
    return load_classification_config(config_path).exclusion_terms


def find_matching_exclusion_term(item_name_raw: str, exclusion_terms: List[str]) -> Optional[str]:
    """The one piece of matching logic this whole gate is built on,
    factored out so any other tool that needs "would this name be
    contamination-flagged" (e.g. `enrichment_queue.py`, which only ever
    has a name string, never a full `BeerMasterRow`) calls this instead
    of re-implementing the fold/word-boundary check a second time.
    Returns the matched term, or `None`."""
    folded_name = fold(item_name_raw)
    for term in exclusion_terms:
        if word_boundary_match(fold(term), folded_name):
            return term
    return None


def filter_contamination(
    rows: List[BeerMasterRow],
    exclusion_terms: List[str],
) -> Tuple[List[BeerMasterRow], List[RejectedBeerMasterRow]]:
    """Row-level only — a matched row is excluded and reported, never
    raised; this gate never aborts a whole batch over one contaminated
    row, matching the two-tier convention every reader in this package
    already follows.

    Returns `(admitted_rows, rejected_rows)`, in the input's own order.
    """
    admitted: List[BeerMasterRow] = []
    rejected: List[RejectedBeerMasterRow] = []

    for row in rows:
        matched_term = find_matching_exclusion_term(row.item_name_raw, exclusion_terms)
        if matched_term is None:
            admitted.append(row)
            continue
        rejected.append(
            RejectedBeerMasterRow(
                canonical_product_id=row.canonical_product_id,
                raw_row={
                    "item_name_raw": row.item_name_raw,
                    "classification_confidence": row.classification_confidence,
                    "classification_matched_on": row.classification_matched_on,
                },
                reason_code="contamination_gate_matched_exclusion_term",
                reason_detail=(
                    f"matched exclusion term {matched_term!r} in item_name_raw, independent of "
                    f"classification_confidence={row.classification_confidence!r} / "
                    f"classification_matched_on={row.classification_matched_on!r}"
                ),
            )
        )

    return admitted, rejected
