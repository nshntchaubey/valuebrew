"""Structural validation for what's actually buildable at this stage of
the repository: `enrichment/candidates/*.yaml` (Milestone 3's own new
artifact type) and `enrichment/` itself (`styles.yaml` + `beers/`, reusing
Milestone 2's readers rather than re-validating their shape a second
time).

This is a narrower scope than Catalog Contract 1.0 §8's full
`schema_validate.py` (which validates an *assembled* Style/Beer/Sku/
Benchmark graph, including `package_type`'s closed-enum check) — that
graph doesn't exist yet, since `join.py` and `assemble.py` aren't built
(explicitly out of scope for this milestone: no merging candidates into
Beer entities, no catalog.json). This module validates every real
artifact that exists *today*; once `join.py` exists, the app-facing
enum/cross-reference rules extend this module (or a sibling), not
replace it.

Two-tier error handling, reused exactly from every other reader in this
package: a malformed individual file is row-level (excluded, reported,
the rest of the batch continues); a repository-wide integrity problem —
today, exactly one: a `canonical_product_id` claimed by two different
`beer_key`s — is structural (raises `SchemaValidationError`, matching
Catalog Builder Implementation Design Part 4's own framing of that
specific case as "an ambiguous, contradictory identity claim").
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .enrichment_reader import load_beers, load_styles
from .models import Candidate, EnrichmentBeer, RejectedCandidateFile, RejectedEnrichmentFile, StyleDef

_CANDIDATE_REQUIRED_KEYS = {"canonical_product_id", "item_name_raw", "display_name"}
_CANDIDATE_CURATED_KEYS = {"suggested_beer_key", "name", "brewery", "style", "abv", "is_craft", "images"}
_CANDIDATE_ALLOWED_KEYS = _CANDIDATE_REQUIRED_KEYS | _CANDIDATE_CURATED_KEYS


class SchemaValidationError(Exception):
    """A structural/aggregate failure — the caller treats this as an
    abort, matching every other structural exception in this package."""


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------


def validate_candidate_entry(
    raw: Any,
    *,
    filename_canonical_product_id: str,
) -> Tuple[Optional[Candidate], Optional[str], Optional[str]]:
    """Validates one already-`yaml.safe_load`ed candidate file's
    contents. Returns `(Candidate, None, None)` on success or
    `(None, reason_code, detail)` on failure — never raises."""

    def reject(reason_code: str, detail: str = "") -> Tuple[None, str, str]:
        return None, reason_code, detail

    if not isinstance(raw, dict):
        return reject("not_a_mapping", f"got {type(raw).__name__}")

    extra_keys = set(raw.keys()) - _CANDIDATE_ALLOWED_KEYS
    if extra_keys:
        return reject("unsupported_keys", str(sorted(extra_keys)))
    missing_keys = _CANDIDATE_REQUIRED_KEYS - set(raw.keys())
    if missing_keys:
        return reject("missing_required_keys", str(sorted(missing_keys)))

    canonical_product_id = raw["canonical_product_id"]
    if not isinstance(canonical_product_id, str) or not canonical_product_id.strip():
        return reject("invalid_canonical_product_id", "must be a non-empty string")
    if canonical_product_id != filename_canonical_product_id:
        return reject(
            "canonical_product_id_does_not_match_filename",
            f"canonical_product_id={canonical_product_id!r} but filename implies "
            f"{filename_canonical_product_id!r}",
        )

    item_name_raw = raw["item_name_raw"]
    if not isinstance(item_name_raw, str) or not item_name_raw.strip():
        return reject("invalid_item_name_raw", "must be a non-empty string")

    display_name = raw["display_name"]
    if not isinstance(display_name, str) or not display_name.strip():
        return reject("invalid_display_name", "must be a non-empty string")

    def optional_string(key: str) -> Tuple[bool, Optional[str]]:
        value = raw.get(key)
        if value is None:
            return True, None
        if isinstance(value, str) and value.strip():
            return True, value
        return False, None

    ok, suggested_beer_key = optional_string("suggested_beer_key")
    if not ok:
        return reject("invalid_suggested_beer_key", "must be null or a non-empty string")
    ok, name = optional_string("name")
    if not ok:
        return reject("invalid_name", "must be null or a non-empty string")
    ok, brewery = optional_string("brewery")
    if not ok:
        return reject("invalid_brewery", "must be null or a non-empty string")
    ok, style = optional_string("style")
    if not ok:
        return reject("invalid_style", "must be null or a non-empty string")

    abv_raw = raw.get("abv")
    if abv_raw is None:
        abv: Optional[float] = None
    elif isinstance(abv_raw, (int, float)) and not isinstance(abv_raw, bool):
        abv = float(abv_raw)
    else:
        return reject("invalid_abv", "must be null or a number")

    is_craft_raw = raw.get("is_craft")
    if is_craft_raw is None:
        is_craft: Optional[bool] = None
    elif isinstance(is_craft_raw, bool):
        is_craft = is_craft_raw
    else:
        return reject("invalid_is_craft", "must be null or a boolean")

    images = raw.get("images", [])
    if not isinstance(images, list) or not all(isinstance(item, str) for item in images):
        return reject("invalid_images", "must be a list of strings")

    return (
        Candidate(
            canonical_product_id=canonical_product_id,
            item_name_raw=item_name_raw,
            display_name=display_name,
            suggested_beer_key=suggested_beer_key,
            name=name,
            brewery=brewery,
            style=style,
            abv=abv,
            is_craft=is_craft,
            images=list(images),
        ),
        None,
        None,
    )


def validate_candidates_directory(
    candidates_dir: Path,
) -> Tuple[List[Candidate], List[RejectedCandidateFile]]:
    """Reads and validates every `enrichment/candidates/*.yaml` file.
    Never writes anything — this module only ever reads candidate files,
    matching Catalog Contract 1.0's own "generated artifacts are never
    hand-mutated by a validator" discipline one layer down."""
    if not candidates_dir.exists() or not candidates_dir.is_dir():
        raise SchemaValidationError(f"candidates directory not found at {candidates_dir}")

    accepted: List[Candidate] = []
    rejected: List[RejectedCandidateFile] = []

    for path in sorted(candidates_dir.glob("*.yaml")):
        filename_id = path.stem
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            rejected.append(
                RejectedCandidateFile(filename=path.name, reason_code="unparseable_yaml", reason_detail=str(exc))
            )
            continue

        candidate, reason_code, detail = validate_candidate_entry(raw, filename_canonical_product_id=filename_id)
        if candidate is not None:
            accepted.append(candidate)
        else:
            assert reason_code is not None
            rejected.append(
                RejectedCandidateFile(filename=path.name, reason_code=reason_code, reason_detail=detail or "")
            )

    return accepted, rejected


# ---------------------------------------------------------------------------
# enrichment/ repository integrity
# ---------------------------------------------------------------------------


def check_no_duplicate_canonical_product_id_across_beers(beers: List[EnrichmentBeer]) -> None:
    """Catalog Builder Implementation Design Part 4: a `canonical_product_id`
    claimed by two different `beer_key`s is an ambiguous, contradictory
    identity claim — a structural failure, not a row-level one. (Within
    one file this can't happen; `canonical_product_ids` is a plain list
    on one `EnrichmentBeer`. This checks *across* files.)"""
    owners: Dict[str, List[str]] = defaultdict(list)
    for beer in beers:
        for canonical_product_id in beer.canonical_product_ids:
            owners[canonical_product_id].append(beer.beer_key)

    conflicts = {cpid: beer_keys for cpid, beer_keys in owners.items() if len(set(beer_keys)) > 1}
    if conflicts:
        detail = ", ".join(f"{cpid!r} claimed by {sorted(set(bks))}" for cpid, bks in sorted(conflicts.items()))
        raise SchemaValidationError(f"duplicate canonical_product_id claimed by multiple beer_keys: {detail}")


@dataclass(frozen=True)
class EnrichmentValidationReport:
    styles: List[StyleDef]
    beers: List[EnrichmentBeer]
    rejected_beer_files: List[RejectedEnrichmentFile]


def validate_enrichment_repository(enrichment_dir: Path) -> EnrichmentValidationReport:
    """Orchestrates Milestone 2's own `load_styles`/`load_beers`
    (reused unchanged, not re-validated a second time) plus the one
    cross-file integrity check `enrichment_reader.py` has no way to
    perform on its own (it validates one file, or one directory in
    isolation, never the whole tree's identity claims against each
    other)."""
    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {style.style_key for style in styles}
    beers, rejected_beer_files = load_beers(enrichment_dir / "beers", style_keys)

    check_no_duplicate_canonical_product_id_across_beers(beers)

    return EnrichmentValidationReport(styles=styles, beers=beers, rejected_beer_files=rejected_beer_files)
