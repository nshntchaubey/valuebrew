"""The final gate before serialization (not yet built) — validates the
already-joined, already-business-rule-filtered graph against the two
remaining structural facts nothing upstream checks: whether a Beer's
`style` actually resolves in `styles.yaml`, and whether a SKU's raw
KSBCL `container_type` has a real equivalent in the app's own closed
`PackageType` enum (Catalog Contract 1.0 Part 5's already-flagged,
already-evidenced incompatibility — enforced here for the first time as
an actual build-blocking rule, not merely documented).

Two-tier, same convention as everywhere else in this package: an
individual SKU failing one of these checks is row-level (excluded,
reported, the rest of the graph continues) — one bad style reference or
one unsupported container type should never block every other real,
correct SKU. The one thing that *does* abort (raises
`CrossReferenceValidationError`) is a duplicate `canonical_product_id`
reaching this layer at all — `join.py`'s own duplicate-ownership check
already makes this structurally impossible upstream, so seeing one here
means an invariant this whole package depends on has already been
violated, not a normal data-quality problem to route around.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .business_rules import AdmittedSku
from .models import PackageType

# KSBCL's own five-value `container_type` vocabulary vs. the app's
# closed three-value `PackageType` (Catalog Contract 1.0 Part 5).
# `tetra_pack`/`unknown` have no equivalent: `tetra_pack` is a genuinely
# different container form with no PackageType analog, and `unknown` is
# KSBCL's own "the source doesn't say" marker -- mapping either would
# mean inventing a fact the source doesn't state, forbidden project-wide.
# `pet_bottle` (RC6.1) is different in kind, not degree: the app's own
# shipped `PackageType.bottle` is documented as "A glass or plastic
# bottle" (lib/shared_domain/sku.dart) -- a PET bottle already satisfies
# that definition, so mapping it here applies an existing rule, not a
# new one. `pint` exists in the app's enum with no KSBCL source, so it
# can never be produced from this mapping; only a future manual override
# could ever set it, which no code path in this package does today.
#
# Public (not `_`-prefixed): `enrichment_queue.py`'s dashboard reuses
# this exact mapping to flag structurally-blocked candidates *before*
# a founder spends research time on them — the same rule, read earlier,
# never a second copy that could drift from this one.
CONTAINER_TYPE_MAP: Dict[str, PackageType] = {
    "bottle": PackageType.BOTTLE,
    "can": PackageType.CAN,
    "pet_bottle": PackageType.BOTTLE,
}


class CrossReferenceValidationError(Exception):
    """Structural — the caller treats this as an abort."""


@dataclass(frozen=True)
class ValidatedSku:
    admitted: AdmittedSku
    package_type: PackageType


@dataclass(frozen=True)
class RejectedValidatedSku:
    admitted: AdmittedSku
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class CrossReferenceValidationResult:
    valid: List[ValidatedSku]
    rejected: List[RejectedValidatedSku]


def validate_cross_references(
    admitted_skus: List[AdmittedSku],
    style_keys: Set[str],
) -> CrossReferenceValidationResult:
    seen_ids: Set[str] = set()
    for admitted in admitted_skus:
        canonical_product_id = admitted.joined.beer_master_row.canonical_product_id
        if canonical_product_id in seen_ids:
            raise CrossReferenceValidationError(
                f"duplicate canonical_product_id reached cross-reference validation: "
                f"{canonical_product_id!r} — join.py's own duplicate-ownership check "
                f"should have made this impossible upstream"
            )
        seen_ids.add(canonical_product_id)

    valid: List[ValidatedSku] = []
    rejected: List[RejectedValidatedSku] = []

    ordered = sorted(admitted_skus, key=lambda a: a.joined.beer_master_row.canonical_product_id)

    for admitted in ordered:
        beer = admitted.joined.enrichment_beer
        row = admitted.joined.beer_master_row

        if beer.style is not None and beer.style not in style_keys:
            rejected.append(
                RejectedValidatedSku(
                    admitted=admitted,
                    reason_code="dangling_style_reference",
                    reason_detail=f"style={beer.style!r} not found in styles.yaml",
                )
            )
            continue

        package_type = CONTAINER_TYPE_MAP.get(row.container_type)
        if package_type is None:
            rejected.append(
                RejectedValidatedSku(
                    admitted=admitted,
                    reason_code="unsupported_package_type",
                    reason_detail=(
                        f"container_type={row.container_type!r} has no PackageType equivalent "
                        f"(Catalog Contract 1.0 Part 5)"
                    ),
                )
            )
            continue

        valid.append(ValidatedSku(admitted=admitted, package_type=package_type))

    return CrossReferenceValidationResult(valid=valid, rejected=rejected)
