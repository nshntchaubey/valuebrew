"""Amends `abv` and/or `calories_per_100ml` on an already-existing
`enrichment/beers/<beer_key>.yaml` — a real gap production enrichment
just discovered: `create_beer.py`'s own docstring is explicit that it
"never overwrites an existing Beer file," and no other module fills the
gap that leaves. A founder who holds a fact back pending a real
decision (`tuborg_green`'s `calories_per_100ml`, held back while the
per-100ml-vs-per-pack schema question was open) has no CLI path to add
it once the file already exists, without dropping into Python — exactly
the condition production enrichment's own rules treat as a tooling
defect to fix, not work around.

Also amends `canonical_product_ids` — additively only, via
`--add-candidates` — for the one real case production enrichment has
now hit twice: a beer already exists, and a later research pass finds a
real sibling SKU that genuinely belongs to it (Tuborg's "Original
Green"/festival-edition cans, confirmed via `carlsbergindia.com`'s own
brand list and independent corroboration as limited-edition *packaging*
of Tuborg Green, not a different product). The identity judgment itself
still happens entirely in the founder's own research, exactly as
`create_beer.py`'s docstring insists — this module makes that decision
zero times, same discipline, just for an existing file instead of a new
one. Reuses `create_beer.py`'s own collision checks (duplicate within
the given candidates, or already claimed by a different beer file) so
an identity mistake fails the same way here as it would there.

Every other curated field (`name`, `brewery`, `style`, `is_craft`,
`images`) stays out of scope — no real session has yet needed to
correct one of those, so adding that path now would be inventing a need
rather than closing a demonstrated one. If that changes, extend this
module then, not now.

Refuses, rather than silently dropping data, when the existing file has
any per-SKU `skus` override — `render_beer_yaml` doesn't render that
map today (create_beer.py's own CLI has no way to set one either), and
production has never populated one, so preserving it correctly here is
unbuilt, untested surface rather than a real, demonstrated need.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import List, Optional

import yaml

from .create_beer import CreateBeerError, _parse_attribution, load_candidate_canonical_product_id, render_beer_yaml
from .enrichment_schema import validate_beer_entry
from .models import AttributionBlock


class UpdateBeerError(Exception):
    """Raised for any condition that would make amending the requested
    Beer file unsafe — this module never works around one silently."""


def update_beer(
    *,
    beer_key: str,
    beers_dir: Path,
    abv: Optional[AttributionBlock] = None,
    calories_per_100ml: Optional[AttributionBlock] = None,
    add_candidate_paths: Optional[List[Path]] = None,
) -> Path:
    """Sets `abv` and/or `calories_per_100ml` on an existing Beer file,
    and/or appends newly-identified sibling SKUs via
    `add_candidate_paths`, leaving every other field exactly as it
    already is. Pass `None` for `abv`/`calories_per_100ml` to leave that
    fact unchanged, not to clear it — there is no path here to un-set an
    already-recorded fact; that has never been a real need, and doing it
    by accident would be worse than not offering it. Returns the amended
    path.
    """
    target_path = beers_dir / f"{beer_key}.yaml"
    if not target_path.exists():
        raise UpdateBeerError(f"{target_path} does not exist — update_beer.py never creates a new file")

    try:
        raw = yaml.safe_load(target_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise UpdateBeerError(f"{target_path.name} is not valid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise UpdateBeerError(f"{target_path} is not a Beer YAML mapping")

    style_value = raw.get("style")
    style_keys = {style_value} if isinstance(style_value, str) and style_value != "unknown" else set()
    existing_beer, reason_code, detail = validate_beer_entry(raw, filename_beer_key=beer_key, style_keys=style_keys)
    if existing_beer is None:
        raise UpdateBeerError(f"{target_path} is not currently structurally valid: {reason_code} {detail}")

    if existing_beer.skus:
        raise UpdateBeerError(
            f"{target_path} has per-SKU overrides ({sorted(existing_beer.skus)}) — update_beer.py "
            "doesn't preserve those yet (out of scope, see this module's own docstring); refusing "
            "rather than silently dropping them"
        )

    if abv is None and calories_per_100ml is None and not add_candidate_paths:
        raise UpdateBeerError("nothing to update — pass --abv, --calories-per-100ml, and/or --add-candidates")

    canonical_product_ids = list(existing_beer.canonical_product_ids)
    if add_candidate_paths:
        new_ids = [load_candidate_canonical_product_id(path) for path in add_candidate_paths]
        if len(set(new_ids)) != len(new_ids):
            raise UpdateBeerError(f"duplicate canonical_product_id among the given --add-candidates: {new_ids}")
        already_here = set(new_ids) & set(canonical_product_ids)
        if already_here:
            raise UpdateBeerError(f"canonical_product_id(s) {sorted(already_here)} already belong to {target_path.name}")

        for other_path in sorted(beers_dir.glob("*.yaml")):
            if other_path == target_path:
                continue
            try:
                other_raw = yaml.safe_load(other_path.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue
            if not isinstance(other_raw, dict):
                continue
            other_ids = set(other_raw.get("canonical_product_ids") or [])
            overlap = other_ids & set(new_ids)
            if overlap:
                raise UpdateBeerError(f"canonical_product_id(s) {sorted(overlap)} already claimed by {other_path.name}")

        canonical_product_ids += new_ids

    content = render_beer_yaml(
        beer_key=existing_beer.beer_key,
        canonical_product_ids=canonical_product_ids,
        name=existing_beer.name,
        brewery=existing_beer.brewery,
        style=existing_beer.style,
        abv=abv if abv is not None else existing_beer.abv,
        calories_per_100ml=calories_per_100ml if calories_per_100ml is not None else existing_beer.calories_per_100ml,
        is_craft=existing_beer.is_craft,
        images=existing_beer.images,
    )

    # Fail loudly rather than writing a file this package's own
    # structural validator would immediately reject — same discipline
    # create_beer.py already applies at write time.
    parsed_back = yaml.safe_load(content)
    beer, reason_code, detail = validate_beer_entry(parsed_back, filename_beer_key=beer_key, style_keys=style_keys)
    if beer is None:
        raise UpdateBeerError(f"amended Beer YAML failed structural validation: {reason_code} {detail}")

    target_path.write_text(content, encoding="utf-8")
    return target_path


def main() -> None:
    """Thin CLI wrapper — mirrors `create_beer.py main()`'s own
    argument shape for `--abv`/`--calories-per-100ml` exactly, so a
    founder already familiar with that command needs nothing new here."""
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description="Amend abv/calories_per_100ml on an existing enrichment/beers/<beer_key>.yaml."
    )
    parser.add_argument("--beer-key", required=True)

    parser.add_argument("--abv", type=float, default=None, help="omit to leave unchanged")
    parser.add_argument("--abv-source-type", choices=["manufacturer", "manual_observation"], default=None)
    parser.add_argument("--abv-source-name", default=None)

    parser.add_argument(
        "--calories-per-100ml", type=float, default=None, help="kcal per 100ml, as published; omit to leave unchanged"
    )
    parser.add_argument("--calories-per-100ml-source-type", choices=["manufacturer", "manual_observation"], default=None)
    parser.add_argument("--calories-per-100ml-source-name", default=None)

    parser.add_argument("--observed-at", default=date.today().isoformat(), help="default: today")
    parser.add_argument("--observed-by", default="founder")

    parser.add_argument(
        "--add-candidates",
        nargs="*",
        default=None,
        metavar="CANONICAL_PRODUCT_ID",
        help="newly-identified sibling SKUs to append to this beer's canonical_product_ids",
    )
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
        raise SystemExit(f"update_beer failed: {exc}") from exc

    add_candidate_paths = (
        [args.candidates_dir / f"{cpid}.yaml" for cpid in args.add_candidates] if args.add_candidates else None
    )

    try:
        written = update_beer(
            beer_key=args.beer_key,
            beers_dir=args.beers_dir,
            abv=abv,
            calories_per_100ml=calories_per_100ml,
            add_candidate_paths=add_candidate_paths,
        )
    except UpdateBeerError as exc:
        raise SystemExit(f"update_beer failed: {exc}") from exc

    print(f"Updated {written}")


if __name__ == "__main__":
    main()
