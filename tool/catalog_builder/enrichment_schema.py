"""Structural (Layer 1) validation for `enrichment/`'s YAML shape —
Catalog Builder Implementation Design Part 3, Beer Knowledge Base
Architecture Part 3/4/7. Pure functions over already-`yaml.safe_load`ed
Python objects — no file I/O here; `enrichment_reader.py` owns opening
files and calling into this module.

Two-tier error handling, deliberately asymmetric between the two file
kinds this module validates, per their different roles:

- `styles.yaml` is one small, shared file every beer references — the
  exact same role `beer_classification.yaml` plays for the pipeline's
  own Stage 2, which the real `classification_config.py` treats as an
  abort-worthy structural failure if malformed. `validate_styles_yaml`
  reuses that same posture: raises `EnrichmentSchemaError`.
- One beer's YAML file is exactly analogous to one CSV row: malformed,
  it should exclude only itself, never abort the whole enrichment load —
  Catalog Builder Implementation Design Part 3's own explicit
  recommendation. `validate_beer_entry` returns a tri-state result
  (`EnrichmentBeer`, reason_code, detail) and never raises.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import AttributionBlock, EnrichmentBeer, RejectedEvidenceEntry, StyleDef

_STYLE_REQUIRED_KEYS = {"style_key", "name", "description"}
_STYLE_ALLOWED_KEYS = _STYLE_REQUIRED_KEYS

_BEER_REQUIRED_KEYS = {"beer_key", "canonical_product_ids", "name", "brewery", "style", "abv", "calories_per_100ml"}
_BEER_OPTIONAL_KEYS = {"is_craft", "images", "skus"}
_BEER_ALLOWED_KEYS = _BEER_REQUIRED_KEYS | _BEER_OPTIONAL_KEYS

_ATTRIBUTION_REQUIRED_KEYS = {"value", "source_type", "source_name", "observed_at", "observed_by"}
_VALID_SOURCE_TYPES = {"manufacturer", "manual_observation"}

_UNKNOWN_MARKER = "unknown"

_REJECTED_EVIDENCE_REQUIRED_KEYS = {
    "subject_type",
    "subject_key",
    "field",
    "source_type",
    "source_name",
    "reason_type",
    "reason_detail",
    "observed_at",
    "observed_by",
}
# value_found is required for every reason_type except access_blocked (RC7.10/
# RC7.11) -- present in _OPTIONAL_KEYS structurally (it may be absent from the
# raw mapping at all), with validate_rejected_evidence_entry enforcing the
# actual reason_type-dependent rule once reason_type itself is known.
_REJECTED_EVIDENCE_OPTIONAL_KEYS = {"recheck_after", "value_found"}
_REJECTED_EVIDENCE_ALLOWED_KEYS = _REJECTED_EVIDENCE_REQUIRED_KEYS | _REJECTED_EVIDENCE_OPTIONAL_KEYS

# The one reason_type where value_found has no natural answer -- access
# failed before any value was ever read, so there is nothing to record
# (RC7.10's evidence review: docs/PROJECT-BRAIN.md's Bira 91/B9 Beverages
# case). Every other reason_type describes rejecting a value that was
# actually found, so value_found stays required for all of them.
_REASON_TYPE_WITHOUT_VALUE_FOUND = "access_blocked"

_VALID_SUBJECT_TYPES = {"beer", "brewery"}

# Approved RC7.6 — the closed reason-type vocabulary for why a piece of
# found evidence was rejected rather than curated.
_REJECTED_EVIDENCE_REASON_TYPES = {
    "wrong_variant",
    "wrong_product_line",
    "access_blocked",
    "imprecise_value",
    "incompatible_unit",
    "conflicting_source_subordinate",
}


class EnrichmentSchemaError(Exception):
    """A structural failure in `styles.yaml` — the caller treats this as
    an abort, matching `classification_config.py`'s own
    `ClassificationConfigError` convention for a shared config file."""


# ---------------------------------------------------------------------------
# styles.yaml
# ---------------------------------------------------------------------------


def validate_styles_yaml(raw: Any) -> List[StyleDef]:
    """`raw` is the object `yaml.safe_load` produced for the whole
    `styles.yaml` file — expected to be a flat list of mappings (Beer
    Knowledge Base Architecture Part 4). Raises `EnrichmentSchemaError`
    on any problem: wrong top-level shape, a malformed entry, or a
    duplicate `style_key` (Catalog Contract 1.0 Part 3's own uniqueness
    rule, enforced here since this is the one place every style is seen
    together)."""
    if not isinstance(raw, list):
        raise EnrichmentSchemaError(
            f"styles.yaml must be a flat list of style entries, got {type(raw).__name__}"
        )

    styles: List[StyleDef] = []
    seen_keys: Set[str] = set()
    for index, entry in enumerate(raw):
        style = _validate_style_entry(entry, index)
        if style.style_key in seen_keys:
            raise EnrichmentSchemaError(f"styles.yaml has a duplicate style_key: {style.style_key!r}")
        seen_keys.add(style.style_key)
        styles.append(style)
    return styles


def _validate_style_entry(entry: Any, index: int) -> StyleDef:
    if not isinstance(entry, dict):
        raise EnrichmentSchemaError(f"styles.yaml entry #{index} must be a mapping, got {type(entry).__name__}")

    extra_keys = set(entry.keys()) - _STYLE_ALLOWED_KEYS
    if extra_keys:
        raise EnrichmentSchemaError(
            f"styles.yaml entry #{index} has unsupported key(s) {sorted(extra_keys)} — "
            f"exactly {sorted(_STYLE_REQUIRED_KEYS)} are allowed"
        )
    missing_keys = _STYLE_REQUIRED_KEYS - set(entry.keys())
    if missing_keys:
        raise EnrichmentSchemaError(f"styles.yaml entry #{index} is missing required key(s) {sorted(missing_keys)}")

    for key in _STYLE_REQUIRED_KEYS:
        if not isinstance(entry[key], str) or not entry[key].strip():
            raise EnrichmentSchemaError(f"styles.yaml entry #{index}: {key!r} must be a non-empty string")

    return StyleDef(style_key=entry["style_key"], name=entry["name"], description=entry["description"])


# ---------------------------------------------------------------------------
# enrichment/beers/<beer_key>.yaml
# ---------------------------------------------------------------------------


def validate_beer_entry(
    raw: Any,
    *,
    filename_beer_key: str,
    style_keys: Set[str],
) -> Tuple[Optional[EnrichmentBeer], Optional[str], Optional[str]]:
    """Validates one already-parsed beer YAML file's contents.

    Returns exactly one of `(EnrichmentBeer, None, None)` on success or
    `(None, reason_code, detail)` on failure — never raises; the caller
    (`enrichment_reader.py`) is responsible for excluding a failing file
    and continuing the rest of the load.
    """

    def reject(reason_code: str, detail: str = "") -> Tuple[None, str, str]:
        return None, reason_code, detail

    if not isinstance(raw, dict):
        return reject("not_a_mapping", f"got {type(raw).__name__}")

    extra_keys = set(raw.keys()) - _BEER_ALLOWED_KEYS
    if extra_keys:
        return reject("unsupported_keys", str(sorted(extra_keys)))
    missing_keys = _BEER_REQUIRED_KEYS - set(raw.keys())
    if missing_keys:
        return reject("missing_required_keys", str(sorted(missing_keys)))

    beer_key = raw["beer_key"]
    if not isinstance(beer_key, str) or not beer_key.strip():
        return reject("invalid_beer_key", "beer_key must be a non-empty string")
    if beer_key != filename_beer_key:
        return reject(
            "beer_key_does_not_match_filename",
            f"beer_key={beer_key!r} but filename implies {filename_beer_key!r}",
        )

    canonical_product_ids = raw["canonical_product_ids"]
    if (
        not isinstance(canonical_product_ids, list)
        or not canonical_product_ids
        or not all(isinstance(item, str) and item.strip() for item in canonical_product_ids)
    ):
        return reject(
            "invalid_canonical_product_ids",
            "must be a non-empty list of non-empty strings",
        )

    name = raw["name"]
    if not isinstance(name, str) or not name.strip():
        return reject("invalid_name", "name must be a non-empty string")

    brewery = raw["brewery"]
    if not isinstance(brewery, str) or not brewery.strip():
        return reject("invalid_brewery", "brewery must be a non-empty string")

    style_value = raw["style"]
    if style_value == _UNKNOWN_MARKER:
        style: Optional[str] = None
    elif isinstance(style_value, str) and style_value.strip():
        if style_value not in style_keys:
            return reject("unresolved_style_reference", f"style={style_value!r} not found in styles.yaml")
        style = style_value
    else:
        return reject("invalid_style", "style must be a style_key string or the literal 'unknown'")

    abv_value = raw["abv"]
    if abv_value == _UNKNOWN_MARKER:
        abv: Optional[AttributionBlock] = None
    elif isinstance(abv_value, dict):
        block, reason_code, detail = _validate_attribution_block(abv_value)
        if block is None:
            return reject(f"invalid_abv_{reason_code}", detail or "")
        abv = block
    else:
        return reject("invalid_abv", "abv must be an attribution block mapping or the literal 'unknown'")

    calories_per_100ml_value = raw["calories_per_100ml"]
    if calories_per_100ml_value == _UNKNOWN_MARKER:
        calories_per_100ml: Optional[AttributionBlock] = None
    elif isinstance(calories_per_100ml_value, dict):
        block, reason_code, detail = _validate_attribution_block(calories_per_100ml_value)
        if block is None:
            return reject(f"invalid_calories_per_100ml_{reason_code}", detail or "")
        calories_per_100ml = block
    else:
        return reject(
            "invalid_calories_per_100ml",
            "calories_per_100ml must be an attribution block mapping or the literal 'unknown'",
        )

    is_craft = raw.get("is_craft", False)
    if not isinstance(is_craft, bool):
        return reject("invalid_is_craft", "is_craft must be a boolean")

    images = raw.get("images", [])
    if not isinstance(images, list) or not all(isinstance(item, str) for item in images):
        return reject("invalid_images", "images must be a list of strings")

    skus_raw = raw.get("skus", {})
    if not isinstance(skus_raw, dict):
        return reject("invalid_skus", "skus must be a mapping keyed by canonical_product_id")
    skus: Dict[str, AttributionBlock] = {}
    for sku_id, override_raw in skus_raw.items():
        if not isinstance(override_raw, dict):
            return reject("invalid_sku_override", f"{sku_id!r}: must be an attribution block mapping")
        block, reason_code, detail = _validate_attribution_block(override_raw)
        if block is None:
            return reject(f"invalid_sku_override_{reason_code}", f"{sku_id!r}: {detail or ''}")
        skus[sku_id] = block

    return (
        EnrichmentBeer(
            beer_key=beer_key,
            canonical_product_ids=list(canonical_product_ids),
            name=name,
            brewery=brewery,
            style=style,
            abv=abv,
            calories_per_100ml=calories_per_100ml,
            is_craft=is_craft,
            images=list(images),
            skus=skus,
        ),
        None,
        None,
    )


def _validate_attribution_block(raw: Dict[Any, Any]) -> Tuple[Optional[AttributionBlock], Optional[str], Optional[str]]:
    """Beer Knowledge Base Architecture Part 5's attribution unit — all
    five fields required whenever the block isn't the bare `unknown`
    marker (handled one level up by the caller)."""
    extra_keys = set(raw.keys()) - _ATTRIBUTION_REQUIRED_KEYS
    if extra_keys:
        return None, "unsupported_keys", str(sorted(extra_keys))
    missing_keys = _ATTRIBUTION_REQUIRED_KEYS - set(raw.keys())
    if missing_keys:
        return None, "missing_keys", str(sorted(missing_keys))

    value = raw["value"]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None, "value_not_numeric", str(value)

    source_type = raw["source_type"]
    if source_type not in _VALID_SOURCE_TYPES:
        return None, "invalid_source_type", f"{source_type!r} not in {sorted(_VALID_SOURCE_TYPES)}"

    source_name = raw["source_name"]
    if not isinstance(source_name, str) or not source_name.strip():
        return None, "invalid_source_name", "source_name must be a non-empty string"

    observed_at_raw = raw["observed_at"]
    if isinstance(observed_at_raw, date):
        observed_at = observed_at_raw
    elif isinstance(observed_at_raw, str):
        try:
            observed_at = date.fromisoformat(observed_at_raw)
        except ValueError:
            return None, "unparseable_observed_at", observed_at_raw
    else:
        return None, "invalid_observed_at", str(observed_at_raw)

    observed_by = raw["observed_by"]
    if not isinstance(observed_by, str) or not observed_by.strip():
        return None, "invalid_observed_by", "observed_by must be a non-empty string"

    return (
        AttributionBlock(
            value=float(value),
            source_type=source_type,
            source_name=source_name,
            observed_at=observed_at,
            observed_by=observed_by,
        ),
        None,
        None,
    )


# ---------------------------------------------------------------------------
# enrichment/rejected_evidence.yaml
# ---------------------------------------------------------------------------


def _parse_date(value: Any, *, field_name: str) -> date:
    """Shared date-parsing for `observed_at`/`recheck_after` — same
    accepted shapes (a real `date`, or an ISO string) `_validate_attribution_block`
    already uses for `observed_at`, factored out here since this module
    now needs it in two places instead of one."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise EnrichmentSchemaError(f"{field_name} is not a valid ISO date: {value!r}") from exc
    raise EnrichmentSchemaError(f"{field_name} must be a date or an ISO date string, got {type(value).__name__}")


def validate_rejected_evidence_entry(
    raw: Any,
    *,
    beer_keys: Set[str],
    brewery_names: Set[str],
) -> RejectedEvidenceEntry:
    """Validates one already-parsed rejected-evidence entry.

    Raises `EnrichmentSchemaError` on any problem — unlike
    `validate_beer_entry`, this never returns a tri-state "excluded, keep
    going" result. `rejected_evidence.yaml` is one shared file (like
    `styles.yaml`), not a directory of independently-loaded per-entity
    files, and nothing in the Catalog Builder's publish pipeline reads it
    (RC7.7 deliberately keeps it that way) — so there is no "the rest of
    the load must survive one bad entry" requirement to protect here. A
    malformed entry should simply be fixed before whatever wrote it is
    trusted again.

    `beer_keys`/`brewery_names` are supplied by the caller, never read
    from disk here — this module owns no file I/O anywhere, per its own
    module docstring — mirroring exactly how `validate_beer_entry`
    receives `style_keys` today.
    """
    if not isinstance(raw, dict):
        raise EnrichmentSchemaError(f"rejected-evidence entry must be a mapping, got {type(raw).__name__}")

    extra_keys = set(raw.keys()) - _REJECTED_EVIDENCE_ALLOWED_KEYS
    if extra_keys:
        raise EnrichmentSchemaError(f"rejected-evidence entry has unsupported key(s) {sorted(extra_keys)}")
    missing_keys = _REJECTED_EVIDENCE_REQUIRED_KEYS - set(raw.keys())
    if missing_keys:
        raise EnrichmentSchemaError(f"rejected-evidence entry is missing required key(s) {sorted(missing_keys)}")

    subject_type = raw["subject_type"]
    if subject_type not in _VALID_SUBJECT_TYPES:
        raise EnrichmentSchemaError(
            f"rejected-evidence entry: subject_type {subject_type!r} not in {sorted(_VALID_SUBJECT_TYPES)}"
        )

    subject_key = raw["subject_key"]
    if not isinstance(subject_key, str) or not subject_key.strip():
        raise EnrichmentSchemaError("rejected-evidence entry: subject_key must be a non-empty string")
    if subject_type == "beer" and subject_key not in beer_keys:
        raise EnrichmentSchemaError(
            f"rejected-evidence entry: subject_key {subject_key!r} does not resolve to an existing beer_key"
        )
    if subject_type == "brewery" and subject_key not in brewery_names:
        raise EnrichmentSchemaError(
            f"rejected-evidence entry: subject_key {subject_key!r} does not resolve to an existing brewery"
        )

    field_name_value = raw["field"]
    if not isinstance(field_name_value, str) or not field_name_value.strip():
        raise EnrichmentSchemaError("rejected-evidence entry: field must be a non-empty string")

    # reason_type is validated here, ahead of its usual position below,
    # because value_found's own requiredness depends on it (RC7.11).
    reason_type = raw["reason_type"]
    if reason_type not in _REJECTED_EVIDENCE_REASON_TYPES:
        raise EnrichmentSchemaError(
            f"rejected-evidence entry: reason_type {reason_type!r} not in {sorted(_REJECTED_EVIDENCE_REASON_TYPES)}"
        )

    value_found_raw = raw.get("value_found")
    if reason_type == _REASON_TYPE_WITHOUT_VALUE_FOUND:
        # Optional: access failed before any value was ever read, so
        # there's nothing to require -- but a value_found that *is*
        # given must still be real, same as every other reason_type.
        if value_found_raw is not None and (not isinstance(value_found_raw, str) or not value_found_raw.strip()):
            raise EnrichmentSchemaError(
                "rejected-evidence entry: value_found, when given, must be a non-empty string"
            )
        value_found = value_found_raw if isinstance(value_found_raw, str) else None
    else:
        if not isinstance(value_found_raw, str) or not value_found_raw.strip():
            raise EnrichmentSchemaError("rejected-evidence entry: value_found must be a non-empty string")
        value_found = value_found_raw

    source_type = raw["source_type"]
    if source_type not in _VALID_SOURCE_TYPES:
        raise EnrichmentSchemaError(
            f"rejected-evidence entry: source_type {source_type!r} not in {sorted(_VALID_SOURCE_TYPES)}"
        )

    source_name = raw["source_name"]
    if not isinstance(source_name, str) or not source_name.strip():
        raise EnrichmentSchemaError("rejected-evidence entry: source_name must be a non-empty string")

    reason_detail = raw["reason_detail"]
    if not isinstance(reason_detail, str) or not reason_detail.strip():
        raise EnrichmentSchemaError("rejected-evidence entry: reason_detail must be a non-empty string")

    observed_at = _parse_date(raw["observed_at"], field_name="rejected-evidence entry: observed_at")

    observed_by = raw["observed_by"]
    if not isinstance(observed_by, str) or not observed_by.strip():
        raise EnrichmentSchemaError("rejected-evidence entry: observed_by must be a non-empty string")

    recheck_after_raw = raw.get("recheck_after")
    recheck_after = (
        _parse_date(recheck_after_raw, field_name="rejected-evidence entry: recheck_after")
        if recheck_after_raw is not None
        else None
    )

    return RejectedEvidenceEntry(
        subject_type=subject_type,
        subject_key=subject_key,
        field=field_name_value,
        value_found=value_found,
        source_type=source_type,
        source_name=source_name,
        reason_type=reason_type,
        reason_detail=reason_detail,
        observed_at=observed_at,
        observed_by=observed_by,
        recheck_after=recheck_after,
    )


def _rejected_evidence_identity(entry: RejectedEvidenceEntry) -> Tuple[str, str, str, str, str, str]:
    """What makes two rejected-evidence entries "the same finding" for
    duplicate-detection purposes: the same subject, field, source, found
    value, and rejection reason. Deliberately narrower than "same subject
    and field" alone — a second, independent source corroborating the
    same rejected value (or a different value rejected for a different
    reason) is new information worth its own entry, not a duplicate."""
    return (
        entry.subject_type,
        entry.subject_key,
        entry.field,
        entry.source_name,
        entry.value_found,
        entry.reason_type,
    )


def validate_rejected_evidence_yaml(
    raw: Any,
    *,
    beer_keys: Set[str],
    brewery_names: Set[str],
) -> List[RejectedEvidenceEntry]:
    """`raw` is the object `yaml.safe_load` produced for the whole
    `rejected_evidence.yaml` file — a flat list of entries, the same
    top-level shape `styles.yaml` uses. Raises `EnrichmentSchemaError` on
    any problem, including a duplicate entry (see `_rejected_evidence_identity`
    for what "duplicate" means here) — the same shared-file,
    abort-on-any-problem posture `validate_styles_yaml` uses, and for the
    same reason: this file is seen and validated all at once, never
    loaded piecemeal."""
    if not isinstance(raw, list):
        raise EnrichmentSchemaError(
            f"rejected_evidence.yaml must be a flat list of entries, got {type(raw).__name__}"
        )

    entries: List[RejectedEvidenceEntry] = []
    seen_identities: Set[Tuple[str, str, str, str, str, str]] = set()
    for index, raw_entry in enumerate(raw):
        try:
            entry = validate_rejected_evidence_entry(raw_entry, beer_keys=beer_keys, brewery_names=brewery_names)
        except EnrichmentSchemaError as exc:
            raise EnrichmentSchemaError(f"rejected_evidence.yaml entry #{index}: {exc}") from exc

        identity = _rejected_evidence_identity(entry)
        if identity in seen_identities:
            raise EnrichmentSchemaError(
                f"rejected_evidence.yaml entry #{index} duplicates an existing entry: "
                f"subject_type={entry.subject_type!r} subject_key={entry.subject_key!r} "
                f"field={entry.field!r} source_name={entry.source_name!r} "
                f"value_found={entry.value_found!r} reason_type={entry.reason_type!r}"
            )
        seen_identities.add(identity)
        entries.append(entry)

    return entries
