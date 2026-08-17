"""Data types the Catalog Builder operates on.

Two families of dataclass live here, matching Catalog Builder
Implementation Design Part 1:

- **Source types** (`BeerMasterRow`, `EnrichmentBeer`, `StyleDef`,
  `AttributionBlock`) — the shapes the loading layer (not yet built)
  parses `pricing_data/beer_master.csv` and `enrichment/` into.
- **Output types** (`Style`, `Beer`, `Sku`, `Benchmark`) — mirror
  docs/CATALOG-CONTRACT-1.0.md Parts 3-6 field-for-field, and the real
  Dart classes those parts are grounded in (`lib/shared_domain/sku.dart`,
  `lib/shared_domain/beer.dart`, `lib/catalog/domain/style.dart`,
  `lib/catalog/domain/benchmark.dart`). `PackageType`/`ValueVerdict` are
  the app's own closed vocabularies, reused verbatim — not KSBCL's own
  five-value `container_type` vocabulary, which stays a plain string on
  `BeerMasterRow` until the schema-validation layer maps or rejects it
  (Catalog Contract 1.0 Part 5's flagged incompatibility).

No logic, no I/O, no validation anywhere in this module — those are the
loading, join, and validation layers' jobs respectively.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Shared enums (output-side closed vocabularies — Catalog Contract 1.0 Part 5)
# ---------------------------------------------------------------------------


class PackageType(enum.Enum):
    """The app's own closed container-type vocabulary
    (`lib/shared_domain/sku.dart`'s `PackageType`) — exactly three values,
    no fallback. Distinct from KSBCL's own `container_type` field, which
    uses a different five-value vocabulary (`bottle`, `can`, `pet_bottle`,
    `tetra_pack`, `unknown`) and is never auto-mapped here."""

    BOTTLE = "bottle"
    CAN = "can"
    PINT = "pint"


class ValueVerdict(enum.Enum):
    """The app's own closed verdict vocabulary
    (`lib/shared_domain/sku.dart`'s `ValueVerdict`)."""

    GREAT_VALUE = "great_value"
    FAIR_VALUE = "fair_value"
    OVERPRICED = "overpriced"


# ---------------------------------------------------------------------------
# Source types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RejectedBeerMasterRow:
    """One `beer_master.csv` row that failed row-level validation —
    mirrors the real pipeline's own `RejectedRow` shape
    (`tool/ksbcl_pricing_pipeline/models.py`) at one layer up. Never
    raised; returned alongside the accepted rows so the caller can report
    it the same way `rejected_rows.csv` already does."""

    canonical_product_id: Optional[str]
    raw_row: Dict[str, str]
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class RejectedEnrichmentFile:
    """One `enrichment/beers/*.yaml` file that failed row-level
    validation — Catalog Builder Implementation Design Part 3's own
    recommendation that a malformed enrichment file is row-level-shaped
    (that file excluded, the rest of the load continues), not a
    structural abort."""

    filename: str
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class RejectedBeerFileEntry:
    """One rejected `enrichment/beers/*.yaml` file, shaped specifically
    for founder-facing reporting (`enrichment_queue.py`,
    `validation_report.py`) — wraps a `RejectedEnrichmentFile` with an
    explicit `stage` label, since that type alone doesn't say which
    layer produced it. Exists so a malformed Beer file is never silently
    absent from a report: every consumer of this type carries `filename`,
    `stage`, and `reason_code`/`reason_detail` together, always."""

    filename: str
    stage: str
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class RejectedCandidateFile:
    """One `enrichment/candidates/*.yaml` file that failed
    `schema_validate.py`'s structural validation — row-level, mirroring
    `RejectedEnrichmentFile`'s own shape one artifact type over."""

    filename: str
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class Candidate:
    """A validated `enrichment/candidates/<canonical_product_id>.yaml` —
    the new, non-canonical artifact type `generate_enrichment_candidates.py`
    introduced (not part of any frozen document's schema). Curated fields
    are `Optional` since a fresh candidate always has them `None`; a
    human is not required to leave them that way (only advised to, by
    the generator's own README), so the validator accepts either state
    rather than enforcing the untouched-null shape."""

    canonical_product_id: str
    item_name_raw: str
    display_name: str
    suggested_beer_key: Optional[str]
    name: Optional[str]
    brewery: Optional[str]
    style: Optional[str]
    abv: Optional[float]
    is_craft: Optional[bool]
    images: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class BeerMasterRow:
    """One row of `pricing_data/beer_master.csv`, field-for-field —
    confirmed directly against the real CSV header, not reconstructed
    from documentation. `container_type` is left as the raw KSBCL string;
    mapping it to `PackageType` is the schema-validation layer's job.
    `pack_count` is genuinely blank for many real rows (e.g. cans), hence
    `Optional`."""

    canonical_product_id: str
    representative_item_code: str
    item_name_raw: str
    display_name: str
    normalized_name_key: str
    pack_size_ml: int
    pack_count: Optional[int]
    container_type: str
    declared_price: Decimal
    landed_cost: Decimal
    ksbcl_selling_price: Decimal
    mrp: Decimal
    effective_date: date
    status: str
    delisted_run_month: Optional[str]
    classification_confidence: str
    classification_matched_on: str
    gtin: Optional[str]
    gtin_confidence: Optional[str]
    source_pdf_reference: str
    first_seen_run_month: str
    last_updated_run_month: str


@dataclass(frozen=True)
class AttributionBlock:
    """A single Curated fact plus its citation — Beer Knowledge Base
    Architecture Part 5's attribution unit. Used today for `abv` only,
    but not named `AbvAttribution` since the shape is explicitly meant to
    extend to any future Curated field without new architecture.

    A field that is genuinely unknown is represented as `None` at this
    dataclass's own field (e.g. `EnrichmentBeer.abv: Optional[...]`), not
    as a special value here — by the time an `EnrichmentBeer` exists as a
    constructed object, the enrichment-schema validator (not yet built)
    has already distinguished "explicitly marked unknown" (valid) from
    "field never written at all" (a structural failure that never reaches
    this dataclass in the first place)."""

    value: float
    source_type: str
    source_name: str
    observed_at: date
    observed_by: str


@dataclass(frozen=True)
class RejectedEvidenceEntry:
    """One piece of researched evidence that was found but deliberately
    not curated onto a Beer/SKU field — the Catalog Enrichment
    Playbook's rejected-evidence record (approved RC7.6, infrastructure
    built RC7.7). Exists so a future research pass has a durable answer
    to "has anyone already looked at this?" instead of re-discovering
    the same dead end: what this records is not "we don't know X," it's
    "we looked, found a candidate value for X, and specifically decided
    not to use it, for this reason."

    Reuses `AttributionBlock`'s own citation fields (`source_type`,
    `source_name`, `observed_at`, `observed_by`) rather than inventing a
    second citation shape — a rejected finding is still a real, sourced
    observation, and deserves the same citation discipline as an
    accepted one. `source_type` therefore shares `AttributionBlock`'s
    closed vocabulary (`manufacturer`, `manual_observation`), enforced
    in `enrichment_schema.py`, not here (this module has no validation
    logic anywhere, per its own module docstring).

    `value_found` is a string, not a float like `AttributionBlock.value`
    — a rejected finding is not always numeric (a wrong brewery name, an
    out-of-range unit are all valid things to have found and rejected),
    so this field stays general rather than assuming every rejection is
    a rejected number.

    `value_found` is `Optional` — approved RC7.10, implemented RC7.11 —
    because one `reason_type`, `access_blocked`, is semantically
    different from the other five: `wrong_variant`, `wrong_product_line`,
    `imprecise_value`, `incompatible_unit`, and
    `conflicting_source_subordinate` all describe rejecting a value that
    was actually read; `access_blocked` describes access failing before
    any value was ever read at all. Forcing a `value_found` on that case
    would mean fabricating one — exactly the "guess dressed as a fact"
    the Catalog Enrichment Playbook's own Part 1 exists to prevent. Still
    always explicitly supplied by the caller (`None`, not a default) —
    `enrichment_schema.py` enforces the actual rule: required and
    non-empty for every `reason_type` except `access_blocked`, where it
    is optional but still rejected if given empty.

    `recheck_after` is `Optional`: not every rejection reason implies a
    future recheck is worthwhile (`wrong_product_line` likely never
    needs one; `access_blocked` often does) — the field lets a founder
    say when, without forcing every entry to have an opinion."""

    subject_type: str
    subject_key: str
    field: str
    value_found: Optional[str]
    source_type: str
    source_name: str
    reason_type: str
    reason_detail: str
    observed_at: date
    observed_by: str
    recheck_after: Optional[date]


@dataclass(frozen=True)
class StyleDef:
    """One entry of `enrichment/styles.yaml` — Beer Knowledge Base
    Architecture Part 4. Deliberately has no `typical_abv_range` field:
    that was proposed in Beer Entity Specification 1.0 but explicitly not
    adopted into the frozen contract (Catalog Contract 1.0 Part 3, Beer
    Knowledge Base Architecture Part 4) — adding it here would be
    reopening a decision this package treats as closed."""

    style_key: str
    name: str
    description: str


@dataclass(frozen=True)
class EnrichmentBeer:
    """One `enrichment/beers/<beer_key>.yaml` file — Beer Knowledge Base
    Architecture Part 3, extended with `calories_per_100ml` (Milestone
    7's own fix for a real gap: `Sku.calories` is required and
    non-nullable in the real schema, but Beer Knowledge Base Architecture
    Part 3's own field table never included a calorie field — closed
    here using the exact same `AttributionBlock` citation discipline as
    `abv`, its stated extension point).

    `calories_per_100ml` (not a per-pack total) per the production
    finding this field was renamed for: manufacturer sources publish
    calories as a concentration (kcal per 100ml), never as a per-pack
    total, so that is exactly what a founder can honestly cite here.
    `Sku.calories`, the per-pack total the app actually shows, is
    computed once at build time from this value and the SKU's own
    `size_ml` (`assemble.py`'s `resolve_calories`) — never entered
    manually, never duplicated per pack size.

    `style`/`abv`/`calories_per_100ml` are `None` when explicitly
    Unknown (see `AttributionBlock`'s own docstring for why that's safe
    here). `skus` holds only genuine per-SKU ABV overrides, keyed by
    `canonical_product_id` — `calories_per_100ml` has no per-SKU
    override, and does not need one the way `abv` sometimes does: it is
    a concentration, not a total, so one Beer-level value already scales
    correctly to every pack size via the build-time computation above."""

    beer_key: str
    canonical_product_ids: List[str]
    name: str
    brewery: str
    style: Optional[str]
    abv: Optional[AttributionBlock]
    calories_per_100ml: Optional[AttributionBlock]
    is_craft: bool = False
    images: List[str] = field(default_factory=list)
    skus: Dict[str, AttributionBlock] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Output types — Catalog Contract 1.0 Parts 3-6, field-for-field
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Style:
    """Matches `lib/catalog/domain/style.dart`'s `Style` exactly."""

    id: str
    name: str
    description: str


@dataclass(frozen=True)
class Beer:
    """Matches `lib/shared_domain/beer.dart`'s `Beer` exactly."""

    id: str
    name: str
    brewery: str
    style_id: str
    is_craft: bool


@dataclass(frozen=True)
class Sku:
    """Matches `lib/shared_domain/sku.dart`'s `Sku` exactly — thirteen
    fields, twelve non-nullable per Catalog Contract 1.0 Part 5.
    `calories` is the one exception: Product Decisions Register D22
    downgraded missing calories from a blocking publication rule to a
    warning (`business_rules.py`'s own `missing_calories` warning code),
    since `value_metrics.py`/`value_score.py` never use it — so a
    published Sku may legitimately have no known calorie value."""

    id: str
    beer_id: str
    size_ml: int
    package_type: PackageType
    abv: float
    calories: Optional[int]
    price: float
    price_last_checked: date
    price_source: str
    cost_per_litre: float
    cost_per_ml_alcohol: float
    value_score: int
    value_verdict: ValueVerdict


@dataclass(frozen=True)
class Benchmark:
    """Matches `lib/catalog/domain/benchmark.dart`'s `Benchmark` exactly."""

    style_id: str
    avg_cost_per_ml_alcohol: float
    p25: float
    p50: float
    p75: float
    sample_size: int


@dataclass(frozen=True)
class Catalog:
    """Matches `lib/catalog/domain/catalog.dart`'s `Catalog` exactly —
    six root keys, no more, no fewer (Catalog Contract 1.0 Part 2)."""

    catalog_version: int
    generated_at: datetime
    styles: List[Style]
    beers: List[Beer]
    skus: List[Sku]
    benchmarks: List[Benchmark]
