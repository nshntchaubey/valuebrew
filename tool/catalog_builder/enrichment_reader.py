"""Loads `enrichment/` from disk — Catalog Builder Implementation Design
Part 3. Owns all file I/O for this layer; delegates every shape/type
decision to `enrichment_schema.py`'s pure validation functions, per that
module's own docstring split.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Tuple

import yaml

from .enrichment_schema import EnrichmentSchemaError, validate_beer_entry, validate_styles_yaml
from .models import EnrichmentBeer, RejectedEnrichmentFile, StyleDef


class EnrichmentReaderError(Exception):
    """A structural failure loading `enrichment/` itself — a missing
    `styles.yaml`, or a `styles.yaml` that fails `enrichment_schema.py`'s
    own validation (wrapped here, not re-raised directly, so every
    caller of this module only ever needs to catch one exception type)."""


@dataclass(frozen=True)
class EnrichmentLoadResult:
    """Everything a directory load of `enrichment/` produced."""

    styles: List[StyleDef]
    beers: List[EnrichmentBeer]
    rejected_beer_files: List[RejectedEnrichmentFile]


def load_styles(styles_path: Path) -> List[StyleDef]:
    """Reads and validates `enrichment/styles.yaml`. Raises
    `EnrichmentReaderError` on any problem — a missing or malformed
    shared config file is always a structural failure here, never a
    row-level one (see `enrichment_schema.py`'s own module docstring for
    why this file is treated differently from an individual beer file)."""
    if not styles_path.exists() or not styles_path.is_file():
        raise EnrichmentReaderError(f"styles.yaml not found at {styles_path}")

    try:
        raw = yaml.safe_load(styles_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise EnrichmentReaderError(f"styles.yaml at {styles_path} is not valid YAML: {exc}") from exc

    try:
        return validate_styles_yaml(raw)
    except EnrichmentSchemaError as exc:
        raise EnrichmentReaderError(str(exc)) from exc


def load_beers(
    beers_dir: Path,
    style_keys: Set[str],
) -> Tuple[List[EnrichmentBeer], List[RejectedEnrichmentFile]]:
    """Reads and validates every `enrichment/beers/*.yaml` file.

    Returns `(accepted_beers, rejected_files)` — a malformed individual
    file is row-level (excluded, recorded, the rest of the load
    continues); a missing `beers_dir` itself is structural (raises
    `EnrichmentReaderError`), since an enrichment load with nowhere to
    read beers from at all is not a partial result, it's a setup error.
    """
    if not beers_dir.exists() or not beers_dir.is_dir():
        raise EnrichmentReaderError(f"enrichment beers directory not found at {beers_dir}")

    accepted: List[EnrichmentBeer] = []
    rejected: List[RejectedEnrichmentFile] = []

    for path in sorted(beers_dir.glob("*.yaml")):
        filename_beer_key = path.stem

        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            rejected.append(
                RejectedEnrichmentFile(filename=path.name, reason_code="unparseable_yaml", reason_detail=str(exc))
            )
            continue

        beer, reason_code, detail = validate_beer_entry(
            raw, filename_beer_key=filename_beer_key, style_keys=style_keys
        )
        if beer is not None:
            accepted.append(beer)
        else:
            assert reason_code is not None
            rejected.append(
                RejectedEnrichmentFile(filename=path.name, reason_code=reason_code, reason_detail=detail or "")
            )

    return accepted, rejected


def load_enrichment_directory(enrichment_dir: Path) -> EnrichmentLoadResult:
    """Convenience wrapper: loads `<enrichment_dir>/styles.yaml` then
    `<enrichment_dir>/beers/*.yaml` against it. Loading only — this does
    not join against `pricing_data/` (that's `join.py`, not yet built)."""
    styles = load_styles(enrichment_dir / "styles.yaml")
    style_keys = {style.style_key for style in styles}
    beers, rejected_beer_files = load_beers(enrichment_dir / "beers", style_keys)
    return EnrichmentLoadResult(styles=styles, beers=beers, rejected_beer_files=rejected_beer_files)
