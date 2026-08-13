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

from .models import AttributionBlock, EnrichmentBeer, StyleDef

_STYLE_REQUIRED_KEYS = {"style_key", "name", "description"}
_STYLE_ALLOWED_KEYS = _STYLE_REQUIRED_KEYS

_BEER_REQUIRED_KEYS = {"beer_key", "canonical_product_ids", "name", "brewery", "style", "abv", "calories_per_100ml"}
_BEER_OPTIONAL_KEYS = {"is_craft", "images", "skus"}
_BEER_ALLOWED_KEYS = _BEER_REQUIRED_KEYS | _BEER_OPTIONAL_KEYS

_ATTRIBUTION_REQUIRED_KEYS = {"value", "source_type", "source_name", "observed_at", "observed_by"}
_VALID_SOURCE_TYPES = {"manufacturer", "manual_observation"}

_UNKNOWN_MARKER = "unknown"


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
