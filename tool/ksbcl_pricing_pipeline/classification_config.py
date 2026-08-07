"""Load and validate ``beer_classification.yaml`` (architecture §2.2, §2.4).

A missing, malformed, or empty config aborts the run outright (§2.4) —
this is exactly the kind of failure §9's own posture treats as a Stage 2
bug, not a data condition, so it is raised loudly here rather than
defaulted around.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

_REQUIRED_KEYS = ("style_keywords", "brand_names", "exclusion_terms")


class ClassificationConfigError(Exception):
    """Raised for any unsupported config input (§2.4) — the caller
    treats this as an abort, the same way PipelineValidationError is
    treated as an abort in Stage 1."""


@dataclass(frozen=True)
class ClassificationConfig:
    """The loaded, validated config plus its content-hash version.

    ``style_keywords`` / ``brand_names`` / ``exclusion_terms`` preserve
    YAML declaration order exactly — §5's tie-break rule ("earliest in
    that list's declaration order") depends on this.
    """

    style_keywords: List[str]
    brand_names: List[str]
    exclusion_terms: List[str]
    config_version: str


def _compute_config_version(raw_bytes: bytes) -> str:
    """§3.1: first 12 hex characters of SHA-256 over the raw file bytes,
    computed before any parsing."""
    return hashlib.sha256(raw_bytes).hexdigest()[:12]


def _validate_string_list(value: object, key: str) -> List[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ClassificationConfigError(
            f"beer_classification.yaml: {key!r} must be a flat list of plain strings, got {value!r}"
        )
    return list(value)


def load_classification_config(path: Path) -> ClassificationConfig:
    """Load, validate, and version ``beer_classification.yaml``.

    Raises ClassificationConfigError for every case §2.4 names as
    unsupported: missing file, unparseable YAML, wrong top-level shape,
    or an empty ``style_keywords`` (§2.3's stated assumption).
    """
    if not path.exists() or not path.is_file():
        raise ClassificationConfigError(f"beer_classification.yaml not found at {path}")

    raw_bytes = path.read_bytes()
    if not raw_bytes.strip():
        raise ClassificationConfigError(f"beer_classification.yaml at {path} is empty")

    config_version = _compute_config_version(raw_bytes)

    try:
        data = yaml.safe_load(raw_bytes)
    except yaml.YAMLError as exc:
        raise ClassificationConfigError(f"beer_classification.yaml at {path} is not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ClassificationConfigError(
            f"beer_classification.yaml at {path} must be a mapping with exactly the keys "
            f"{_REQUIRED_KEYS}, got {type(data).__name__}"
        )

    extra_keys = set(data.keys()) - set(_REQUIRED_KEYS)
    if extra_keys:
        raise ClassificationConfigError(
            f"beer_classification.yaml at {path} has unsupported top-level key(s) {sorted(extra_keys)} "
            f"— exactly three keys are allowed (§2.2): {_REQUIRED_KEYS}"
        )
    missing_keys = set(_REQUIRED_KEYS) - set(data.keys())
    if missing_keys:
        raise ClassificationConfigError(
            f"beer_classification.yaml at {path} is missing required key(s) {sorted(missing_keys)}"
        )

    style_keywords = _validate_string_list(data["style_keywords"], "style_keywords")
    brand_names = _validate_string_list(data["brand_names"], "brand_names")
    exclusion_terms = _validate_string_list(data["exclusion_terms"], "exclusion_terms")

    if not style_keywords:
        raise ClassificationConfigError(
            f"beer_classification.yaml at {path}: style_keywords must contain at least one entry (§2.3)"
        )

    return ClassificationConfig(
        style_keywords=style_keywords,
        brand_names=brand_names,
        exclusion_terms=exclusion_terms,
        config_version=config_version,
    )
