"""Turns one or more `enrichment/candidates/*.yaml` files into a new,
real `enrichment/beers/<beer_key>.yaml` — the one place in this whole
package where the identity decision every frozen document insists must
stay human (Catalog Implementation Architecture Part 2, Catalog
Enrichment Playbook Part 2) is actually carried out. This module makes
that decision zero times. Every curated field (`beer_key`, `name`,
`brewery`, `style`, `abv`, `calories_per_100ml`, `is_craft`, `images`)
is a required, explicit
argument — nothing is read from a candidate file's own curated fields,
even if a founder has since hand-scribbled something into one as a
scratch note. The only thing this module reads from a candidate file is
its `canonical_product_id` — proof the SKU exists and is a valid
candidate, nothing more. This is deliberate: it keeps this module's
behaviour identical regardless of what state any candidate file happens
to be in, so there is never a question of whether a value came from the
founder's call or was silently picked up from disk.

Refuses, rather than silently working around, three unsafe conditions:
an already-existing `beer_key` file (never overwritten); a duplicate
`canonical_product_id` among the candidates given in one call; a
`canonical_product_id` already claimed by a different, existing
`beer_key` file. The existing-file scan here is intentionally a raw,
lightweight read (not a full `enrichment_reader.load_beers` call) — it
exists only to catch an identity collision before it's written, not to
re-validate every sibling file's own correctness; `validate_beer.py` is
the dedicated place for full validation, run after this module writes.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import List, Optional

import yaml

from .enrichment_schema import validate_beer_entry
from .models import AttributionBlock


class CreateBeerError(Exception):
    """Raised for any condition that would make writing the requested
    Beer file unsafe — this module never works around one silently."""


def _yaml_string(value: str) -> str:
    # ensure_ascii=False: json.dumps's default escapes non-BMP characters
    # (emoji, some rare symbols) as UTF-16 surrogate pairs, which PyYAML
    # does not recombine on load -- the resulting Python string contains
    # lone surrogates that later crash on UTF-8 encode (e.g. in
    # catalog_writer.py). Writing the real UTF-8 characters directly
    # avoids the surrogate-pair round-trip entirely and is still valid
    # inside a YAML double-quoted scalar.
    return json.dumps(value, ensure_ascii=False)


def load_candidate_canonical_product_id(candidate_path: Path) -> str:
    """Reads exactly the identity field from one candidate file — see
    this module's own docstring for why nothing else is read."""
    if not candidate_path.exists() or not candidate_path.is_file():
        raise CreateBeerError(f"candidate file not found: {candidate_path}")

    try:
        raw = yaml.safe_load(candidate_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CreateBeerError(f"{candidate_path.name} is not valid YAML: {exc}") from exc

    if not isinstance(raw, dict) or "canonical_product_id" not in raw:
        raise CreateBeerError(f"{candidate_path.name} has no canonical_product_id")

    canonical_product_id = raw["canonical_product_id"]
    if not isinstance(canonical_product_id, str) or not canonical_product_id.strip():
        raise CreateBeerError(f"{candidate_path.name}: canonical_product_id must be a non-empty string")

    return canonical_product_id


def _render_attribution_block_lines(key: str, block: Optional[AttributionBlock]) -> List[str]:
    if block is None:
        return [f"{key}: unknown"]
    return [
        f"{key}:",
        f"  value: {block.value}",
        f"  source_type: {_yaml_string(block.source_type)}",
        f"  source_name: {_yaml_string(block.source_name)}",
        f"  observed_at: {block.observed_at.isoformat()}",
        f"  observed_by: {_yaml_string(block.observed_by)}",
    ]


def render_beer_yaml(
    *,
    beer_key: str,
    canonical_product_ids: List[str],
    name: str,
    brewery: str,
    style: Optional[str],
    abv: Optional[AttributionBlock],
    calories_per_100ml: Optional[AttributionBlock],
    is_craft: bool = False,
    images: Optional[List[str]] = None,
) -> str:
    """Pure function — renders the real Beer Knowledge Base Architecture
    Part 3 YAML shape (extended with `calories_per_100ml`, Milestone 7's
    own fix) from exactly the given values. No defaults pulled from
    anywhere but the caller's own arguments."""
    lines: List[str] = []
    lines.append(f"beer_key: {_yaml_string(beer_key)}")
    lines.append("canonical_product_ids:")
    for canonical_product_id in canonical_product_ids:
        lines.append(f"  - {_yaml_string(canonical_product_id)}")
    lines.append(f"name: {_yaml_string(name)}")
    lines.append(f"brewery: {_yaml_string(brewery)}")
    lines.append(f"style: {_yaml_string(style) if style is not None else 'unknown'}")
    lines.extend(_render_attribution_block_lines("abv", abv))
    lines.extend(_render_attribution_block_lines("calories_per_100ml", calories_per_100ml))

    lines.append(f"is_craft: {'true' if is_craft else 'false'}")

    if images:
        lines.append("images:")
        for image in images:
            lines.append(f"  - {_yaml_string(image)}")
    else:
        lines.append("images: []")

    return "\n".join(lines) + "\n"


def create_beer(
    *,
    beer_key: str,
    candidate_paths: List[Path],
    beers_dir: Path,
    name: str,
    brewery: str,
    style: Optional[str],
    abv: Optional[AttributionBlock],
    calories_per_100ml: Optional[AttributionBlock],
    is_craft: bool = False,
    images: Optional[List[str]] = None,
) -> Path:
    """Writes `<beers_dir>/<beer_key>.yaml`, grouping exactly the
    `canonical_product_id`s of the candidate files the founder listed —
    no more, no fewer, and never any others. Returns the written path.
    """
    if not candidate_paths:
        raise CreateBeerError("at least one candidate file is required")
    if not beer_key or not beer_key.strip():
        raise CreateBeerError("beer_key must be a non-empty string")
    if not name or not name.strip():
        raise CreateBeerError("name must be a non-empty string")
    if not brewery or not brewery.strip():
        raise CreateBeerError("brewery must be a non-empty string")

    canonical_product_ids = [load_candidate_canonical_product_id(path) for path in candidate_paths]
    if len(set(canonical_product_ids)) != len(canonical_product_ids):
        raise CreateBeerError(
            f"duplicate canonical_product_id among the given candidate files: {canonical_product_ids}"
        )

    target_path = beers_dir / f"{beer_key}.yaml"
    if target_path.exists():
        raise CreateBeerError(
            f"{target_path} already exists — create_beer.py never overwrites an existing Beer file"
        )

    if beers_dir.exists():
        for existing_path in sorted(beers_dir.glob("*.yaml")):
            try:
                existing_raw = yaml.safe_load(existing_path.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue
            if not isinstance(existing_raw, dict):
                continue
            existing_ids = set(existing_raw.get("canonical_product_ids") or [])
            overlap = existing_ids & set(canonical_product_ids)
            if overlap:
                raise CreateBeerError(
                    f"canonical_product_id(s) {sorted(overlap)} already claimed by {existing_path.name}"
                )

    content = render_beer_yaml(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name=name,
        brewery=brewery,
        style=style,
        abv=abv,
        calories_per_100ml=calories_per_100ml,
        is_craft=is_craft,
        images=images,
    )

    # Fail loudly rather than writing a file this package's own
    # structural validator would immediately reject — a mistake here
    # should surface at creation time, not at the next validate_beer.py
    # run.
    parsed_back = yaml.safe_load(content)
    style_keys = {style} if style is not None else set()
    beer, reason_code, detail = validate_beer_entry(
        parsed_back, filename_beer_key=beer_key, style_keys=style_keys
    )
    if beer is None:
        raise CreateBeerError(f"generated Beer YAML failed structural validation: {reason_code} {detail}")

    beers_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")
    return target_path


def _parse_attribution(
    value: Optional[float],
    source_type: Optional[str],
    source_name: Optional[str],
    observed_at: str,
    observed_by: str,
    *,
    field_name: str,
) -> Optional[AttributionBlock]:
    """`None` when `value` wasn't given (the CLI's `unknown`). Requires
    `source_type`/`source_name` whenever `value` is given — the same
    "never a bare scalar" rule `enrichment_schema.py` already enforces,
    just caught earlier, at the command line, with a clearer message.

    `observed_at` is parsed here too, and rejected with the same clean
    `CreateBeerError` (never a raw `ValueError` traceback) — a malformed
    or impossible date (`13-08-2026`, `2026-02-30`) is exactly the kind
    of typo a founder makes by hand, not a structural problem worth a
    stack trace."""
    if value is None:
        return None
    if not source_type or not source_name:
        raise CreateBeerError(f"--{field_name} was given but --{field_name}-source-type/--{field_name}-source-name were not")
    try:
        parsed_observed_at = date.fromisoformat(observed_at)
    except ValueError as exc:
        raise CreateBeerError(
            f"--observed-at {observed_at!r} is not a valid date — required format is YYYY-MM-DD"
        ) from exc
    return AttributionBlock(
        value=value,
        source_type=source_type,
        source_name=source_name,
        observed_at=parsed_observed_at,
        observed_by=observed_by,
    )


def main() -> None:
    """Thin CLI wrapper around `create_beer()` — every argument maps
    directly to that function's own parameters; no decision made here
    that `create_beer()` doesn't already make itself. `--candidates`
    takes bare `canonical_product_id`s (e.g. `CP0000002`), resolved
    against `--candidates-dir` — matching how a founder actually thinks
    about a beer, from the dashboard's own output, not file paths."""
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Create a new enrichment/beers/<beer_key>.yaml from one or more candidates.")
    parser.add_argument("--beer-key", required=True)
    parser.add_argument("--candidates", required=True, nargs="+", metavar="CANONICAL_PRODUCT_ID")
    parser.add_argument("--name", required=True)
    parser.add_argument("--brewery", required=True)
    parser.add_argument("--style", default=None, help="a style_key from enrichment/styles.yaml; omit for unknown")
    parser.add_argument("--is-craft", action="store_true")
    parser.add_argument("--images", nargs="*", default=None)

    parser.add_argument("--abv", type=float, default=None, help="omit for unknown")
    parser.add_argument("--abv-source-type", choices=["manufacturer", "manual_observation"], default=None)
    parser.add_argument("--abv-source-name", default=None)

    parser.add_argument(
        "--calories-per-100ml", type=float, default=None, help="kcal per 100ml, as published; omit for unknown"
    )
    parser.add_argument("--calories-per-100ml-source-type", choices=["manufacturer", "manual_observation"], default=None)
    parser.add_argument("--calories-per-100ml-source-name", default=None)

    parser.add_argument("--observed-at", default=date.today().isoformat(), help="default: today")
    parser.add_argument("--observed-by", default="founder")

    parser.add_argument("--candidates-dir", type=Path, default=repo_root / "enrichment" / "candidates")
    parser.add_argument("--beers-dir", type=Path, default=repo_root / "enrichment" / "beers")

    args = parser.parse_args()

    try:
        abv = _parse_attribution(
            args.abv, args.abv_source_type, args.abv_source_name, args.observed_at, args.observed_by, field_name="abv"
        )
        calories_per_100ml = _parse_attribution(
            args.calories_per_100ml,
            args.calories_per_100ml_source_type,
            args.calories_per_100ml_source_name,
            args.observed_at,
            args.observed_by,
            field_name="calories-per-100ml",
        )
    except CreateBeerError as exc:
        raise SystemExit(f"create_beer failed: {exc}") from exc

    candidate_paths = [args.candidates_dir / f"{cpid}.yaml" for cpid in args.candidates]

    try:
        written = create_beer(
            beer_key=args.beer_key,
            candidate_paths=candidate_paths,
            beers_dir=args.beers_dir,
            name=args.name,
            brewery=args.brewery,
            style=args.style,
            abv=abv,
            calories_per_100ml=calories_per_100ml,
            is_craft=args.is_craft,
            images=args.images,
        )
    except CreateBeerError as exc:
        raise SystemExit(f"create_beer failed: {exc}") from exc

    print(f"Wrote {written}")
    if abv is None:
        print("  abv: unknown")
    if calories_per_100ml is None:
        print("  calories_per_100ml: unknown")
    if args.style is None:
        print("  style: unknown")
    print("Structurally valid. Run validate_beer.py to check publication readiness.")


if __name__ == "__main__":
    main()
