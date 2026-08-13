"""Validates one `enrichment/beers/<beer_key>.yaml` file — the gate
between `create_beer.py` writing a file and a founder treating it as
accepted. Reuses `enrichment_schema.py`'s own `validate_beer_entry` for
everything that's already a single-file structural concern (required
fields, `brewery` always required, `style`/`abv` either real or the
literal `unknown`, malformed YAML), and adds exactly the checks that
require knowing about the rest of the repository, which a single-file
validator structurally cannot do on its own:

- **Unique `beer_key`** — no other file in `beers_dir` declares the same
  `beer_key`.
- **Duplicate `canonical_product_id`**, in two senses: listed twice
  within this beer's own file (a real, catchable copy-paste mistake), or
  claimed by a different beer_key elsewhere in `beers_dir`.
- **SKU integrity** — every key in this beer's own `skus:` override map
  is one of its own `canonical_product_ids`; an override for a SKU that
  doesn't belong to this beer at all is silently meaningless today and a
  real mistake to catch now.

**On `abv`/`style` being `unknown`:** the frozen schema explicitly allows
either as `unknown` (Beer Knowledge Base Architecture Part 3) — this
validator does not reject that. "ABV present" and "style validity" here
mean "if given, it resolves/is well-formed," never "must not be
unknown"; rejecting an honest `unknown` would silently reopen a decision
this whole session's canon repeatedly protects (Catalog Enrichment
Playbook Part 1's own "never guess, mark unknown instead").

**Three distinct states, confirmed by a real founder dry run to be
routinely confused for one another:** `validate_beer_file`'s own
`valid=True` means *structurally valid* only — a file can validate
cleanly and still publish nothing. `check_publication_readiness` (below)
answers the genuinely different question of whether each SKU would
survive the real `join` -> `business_rules` -> `cross_reference_validate`
chain *today* — it calls those exact functions against the full current
repository and reports what they decided; it makes no decision of its
own. A third, independent question — whether a SKU is actually present
in the `catalog/catalog.json` sitting on disk right now — is checked by
reading that file directly, since "ready to publish" and "already
published" are not the same fact: a beer can be fully ready and simply
not yet built.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from .beer_master_reader import read_beer_master_csv
from .business_rules import apply_business_rules
from .contamination_filter import filter_contamination, load_default_exclusion_terms
from .cross_reference_validate import validate_cross_references
from .enrichment_reader import EnrichmentReaderError, load_beers, load_styles
from .enrichment_schema import validate_beer_entry
from .join import JoinError, join
from .models import EnrichmentBeer


@dataclass(frozen=True)
class BeerValidationIssue:
    reason_code: str
    reason_detail: str


@dataclass(frozen=True)
class BeerValidationResult:
    valid: bool
    beer: Optional[EnrichmentBeer]
    issues: List[BeerValidationIssue] = field(default_factory=list)


def validate_beer_file(beer_path: Path, *, styles_path: Path, beers_dir: Path) -> BeerValidationResult:
    """Validates `beer_path` as a candidate for acceptance into
    `beers_dir` — `beer_path` is typically already inside `beers_dir`
    (the normal case: `create_beer.py` just wrote it there), but this
    works equally against a file anywhere else, checked against
    `beers_dir`'s existing contents."""
    if not beer_path.exists() or not beer_path.is_file():
        return BeerValidationResult(
            valid=False, beer=None, issues=[BeerValidationIssue("file_not_found", str(beer_path))]
        )

    try:
        styles = load_styles(styles_path)
    except EnrichmentReaderError as exc:
        return BeerValidationResult(
            valid=False, beer=None, issues=[BeerValidationIssue("styles_yaml_invalid", str(exc))]
        )
    style_keys = {style.style_key for style in styles}

    try:
        raw = yaml.safe_load(beer_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return BeerValidationResult(
            valid=False, beer=None, issues=[BeerValidationIssue("unparseable_yaml", str(exc))]
        )

    beer, reason_code, detail = validate_beer_entry(raw, filename_beer_key=beer_path.stem, style_keys=style_keys)
    if beer is None:
        assert reason_code is not None
        return BeerValidationResult(
            valid=False, beer=None, issues=[BeerValidationIssue(reason_code, detail or "")]
        )

    issues: List[BeerValidationIssue] = []

    seen_ids = set()
    for canonical_product_id in beer.canonical_product_ids:
        if canonical_product_id in seen_ids:
            issues.append(
                BeerValidationIssue("duplicate_canonical_product_id_within_beer", canonical_product_id)
            )
        seen_ids.add(canonical_product_id)

    for sku_id in beer.skus:
        if sku_id not in beer.canonical_product_ids:
            issues.append(BeerValidationIssue("sku_override_not_in_canonical_product_ids", sku_id))

    issues.extend(_check_against_repository(beer, beer_path=beer_path, beers_dir=beers_dir))

    return BeerValidationResult(valid=len(issues) == 0, beer=beer, issues=issues)


def compute_invalid_beer_keys(beers_dir: Path, styles_path: Path) -> Set[str]:
    """Returns the set of `beer_key`s (derived from filename, since an
    invalid file may not even parse into a `beer_key` of its own) that
    fail validation — the same set `validate_beer_file`, called once per
    file, would produce, but computed in one O(n) repository pass rather
    than the O(n^2) that calling it in a loop used to cost.

    **Why this used to be O(n^2), and isn't a rewrite of the rule, only
    of how it's computed.** `validate_beer_file` calls
    `_check_against_repository`, which re-reads and re-parses every
    *other* beer file to check for a duplicate `beer_key` or an
    overlapping `canonical_product_id` — a correct, necessary check for
    validating one specific file (the CLI's own use, still unchanged
    below), but doing that once per beer in a loop means every file gets
    re-scanned once for every other file: O(n) work, n times. The fix
    reads every file exactly once, builds the two repository-wide
    ownership maps `_check_against_repository` was re-deriving from
    scratch each time, and then makes the same per-file decision against
    those maps.

    **Same shape as `schema_validate.check_no_duplicate_canonical_
    product_id_across_beers`, deliberately not a call to it.** That
    function already proves the right pattern here — one pass, one
    owners-dict, O(n) — and this reuses exactly that shape. It can't be
    called directly, though: it operates only on already-validated
    `EnrichmentBeer`s and raises on any conflict (the right contract for
    `join.py`'s own hard-abort case), while this function must also
    catch a *malformed* file's raw claims conflicting with a valid one
    (the real, narrower case `_check_against_repository` exists for) and
    must never abort — it always returns a full set, one entry per
    invalid file, matching `validate_beer_file`'s own per-file semantics
    exactly.

    **Every rule `validate_beer_file` enforces is still enforced, in the
    same order of consequence, none added, none removed:** unparseable
    `styles.yaml`; unparseable beer YAML; `validate_beer_entry`'s own
    structural checks; a `canonical_product_id` repeated within one
    beer's own list; a `skus` override key not among that beer's own
    `canonical_product_ids`; a `beer_key` or `canonical_product_id`
    claimed by another real file in the directory, valid or not."""
    if not beers_dir.exists():
        return set()

    try:
        styles = load_styles(styles_path)
    except EnrichmentReaderError:
        # validate_beer_file's own behavior: a broken styles.yaml fails
        # every single beer file identically. Matched here in one pass
        # instead of re-discovering it once per file.
        return {path.stem for path in beers_dir.glob("*.yaml")}
    style_keys = {style.style_key for style in styles}

    # Read every real beer file exactly once — the single repository
    # pass that replaces every previous re-scan.
    raw_by_path: Dict[Path, Optional[Dict[str, Any]]] = {}
    for path in sorted(beers_dir.glob("*.yaml")):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            raw_by_path[path] = None
            continue
        raw_by_path[path] = raw if isinstance(raw, dict) else None

    # Repository-wide ownership maps, built once, from every real raw
    # dict (valid or not) — exactly what _check_against_repository was
    # rebuilding from scratch for every single beer.
    beer_key_owners: Dict[Any, List[Path]] = defaultdict(list)
    cpid_owners: Dict[str, List[Path]] = defaultdict(list)
    for path, raw in raw_by_path.items():
        if raw is None:
            continue
        beer_key_owners[raw.get("beer_key")].append(path)
        for cpid in raw.get("canonical_product_ids") or []:
            if isinstance(cpid, str):
                cpid_owners[cpid].append(path)

    invalid: Set[str] = set()
    for path, raw in raw_by_path.items():
        stem = path.stem

        if raw is None:
            invalid.add(stem)
            continue

        beer, _, _ = validate_beer_entry(raw, filename_beer_key=stem, style_keys=style_keys)
        if beer is None:
            invalid.add(stem)
            continue

        seen_ids: Set[str] = set()
        has_internal_duplicate = False
        for canonical_product_id in beer.canonical_product_ids:
            if canonical_product_id in seen_ids:
                has_internal_duplicate = True
                break
            seen_ids.add(canonical_product_id)
        if has_internal_duplicate:
            invalid.add(stem)
            continue

        if any(sku_id not in beer.canonical_product_ids for sku_id in beer.skus):
            invalid.add(stem)
            continue

        # beer.beer_key == stem is guaranteed by validate_beer_entry
        # above (it rejects any mismatch), so this is exactly
        # _check_against_repository's own "does another real file's raw
        # beer_key equal mine" check.
        if len(beer_key_owners.get(beer.beer_key, [])) > 1:
            invalid.add(stem)
            continue

        if any(len(cpid_owners.get(cpid, [])) > 1 for cpid in beer.canonical_product_ids):
            invalid.add(stem)
            continue

    return invalid


@dataclass(frozen=True)
class SkuPublicationStatus:
    canonical_product_id: str
    publication_ready: bool
    included_in_catalog: bool
    reason: Optional[str] = None


@dataclass(frozen=True)
class PublicationReadinessResult:
    beer_key: str
    structurally_valid: bool
    structural_issues: List[BeerValidationIssue]
    skus: List[SkuPublicationStatus]


def _load_existing_catalog_sku_ids(catalog_path: Path) -> Set[str]:
    if not catalog_path.exists():
        return set()
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    skus = data.get("skus") if isinstance(data, dict) else None
    if not isinstance(skus, list):
        return set()
    return {sku["id"] for sku in skus if isinstance(sku, dict) and "id" in sku}


def check_publication_readiness(
    beer_key: str,
    *,
    beer_master_path: Path,
    enrichment_dir: Path,
    catalog_path: Path,
) -> PublicationReadinessResult:
    """Runs the exact real `join` -> `business_rules` ->
    `cross_reference_validate` chain against the *entire* current
    repository — not a scoped-down copy of that logic — then reports
    only what those functions decided about `beer_key`'s own SKUs. No
    new rule is evaluated here; this function only calls and filters.

    Raises `JoinError` unchanged if the repository has a genuine
    structural problem (e.g. a duplicate `canonical_product_id` across
    two different beers) — that is a real, repository-wide failure, not
    specific to this beer, and this function does not hide it.
    """
    beers_dir = enrichment_dir / "beers"
    styles_path = enrichment_dir / "styles.yaml"
    beer_path = beers_dir / f"{beer_key}.yaml"

    structural = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    accepted, _ = read_beer_master_csv(beer_master_path)
    exclusion_terms = load_default_exclusion_terms()
    admitted, rejected_rows = filter_contamination(accepted, exclusion_terms)
    contaminated_ids = {r.canonical_product_id for r in rejected_rows}

    styles = load_styles(styles_path)
    style_keys = {s.style_key for s in styles}
    beers, _ = load_beers(beers_dir, style_keys)
    invalid_beer_keys = compute_invalid_beer_keys(beers_dir, styles_path)

    join_result = join(admitted, contaminated_row_ids=contaminated_ids, beers=beers)
    business_result = apply_business_rules(join_result.joined, invalid_beer_keys=invalid_beer_keys)
    cross_ref_result = validate_cross_references(business_result.admitted, style_keys=style_keys)

    included_ids = {
        v.admitted.joined.beer_master_row.canonical_product_id
        for v in cross_ref_result.valid
        if v.admitted.joined.enrichment_beer.beer_key == beer_key
    }

    reason_by_id: Dict[str, str] = {}
    for rejected in business_result.rejected:
        if rejected.joined.enrichment_beer.beer_key == beer_key:
            reason_by_id[rejected.joined.beer_master_row.canonical_product_id] = (
                f"{rejected.reason_code}: {rejected.reason_detail}"
            )
    for rejected in cross_ref_result.rejected:
        if rejected.admitted.joined.enrichment_beer.beer_key == beer_key:
            reason_by_id[rejected.admitted.joined.beer_master_row.canonical_product_id] = (
                f"{rejected.reason_code}: {rejected.reason_detail}"
            )
    for missing in join_result.missing_candidates:
        if missing.beer_key == beer_key:
            reason_by_id[missing.canonical_product_id] = "missing_candidate: no matching real row in beer_master.csv"
    for orphan in join_result.orphan_skus:
        if orphan.beer_key == beer_key:
            reason_by_id[orphan.canonical_product_id] = "orphan_sku: this row was rejected by the contamination gate"

    catalog_sku_ids = _load_existing_catalog_sku_ids(catalog_path)

    canonical_ids = structural.beer.canonical_product_ids if structural.beer is not None else []
    skus = [
        SkuPublicationStatus(
            canonical_product_id=cpid,
            publication_ready=cpid in included_ids,
            included_in_catalog=cpid in catalog_sku_ids,
            reason=None if cpid in included_ids else reason_by_id.get(cpid, "unresolved"),
        )
        for cpid in canonical_ids
    ]

    return PublicationReadinessResult(
        beer_key=beer_key,
        structurally_valid=structural.valid,
        structural_issues=structural.issues,
        skus=skus,
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description="Check a Beer YAML: structural validity, publication readiness, and catalog inclusion."
    )
    parser.add_argument("beer_key")
    parser.add_argument("--enrichment-dir", type=Path, default=repo_root / "enrichment")
    parser.add_argument("--beer-master-path", type=Path, default=repo_root / "pricing_data" / "beer_master.csv")
    parser.add_argument("--catalog-path", type=Path, default=repo_root / "catalog" / "catalog.json")
    args = parser.parse_args()

    beers_dir = args.enrichment_dir / "beers"
    styles_path = args.enrichment_dir / "styles.yaml"
    beer_path = beers_dir / f"{args.beer_key}.yaml"

    structural = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    print(f"{args.beer_key}")
    print(f"  Structurally valid:   {'YES' if structural.valid else 'NO'}")
    if not structural.valid:
        for issue in structural.issues:
            print(f"    - {issue.reason_code}: {issue.reason_detail}")
        raise SystemExit(1)
    for issue in structural.issues:
        print(f"    - {issue.reason_code}: {issue.reason_detail}")

    try:
        readiness = check_publication_readiness(
            args.beer_key,
            beer_master_path=args.beer_master_path,
            enrichment_dir=args.enrichment_dir,
            catalog_path=args.catalog_path,
        )
    except JoinError as exc:
        raise SystemExit(f"Repository-wide structural failure — cannot check readiness: {exc}") from exc

    for sku in readiness.skus:
        ready = "YES" if sku.publication_ready else "NO "
        included = "YES" if sku.included_in_catalog else "NO "
        line = f"  {sku.canonical_product_id}: Publication ready: {ready}   Included in catalog: {included}"
        if sku.reason:
            line += f"   ({sku.reason})"
        print(line)


def _check_against_repository(beer: EnrichmentBeer, *, beer_path: Path, beers_dir: Path) -> List[BeerValidationIssue]:
    issues: List[BeerValidationIssue] = []
    if not beers_dir.exists():
        return issues

    resolved_beer_path = beer_path.resolve()
    for other_path in sorted(beers_dir.glob("*.yaml")):
        if other_path.resolve() == resolved_beer_path:
            continue
        try:
            other_raw = yaml.safe_load(other_path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(other_raw, dict):
            continue

        if other_raw.get("beer_key") == beer.beer_key:
            issues.append(BeerValidationIssue("duplicate_beer_key", f"also used by {other_path.name}"))

        other_ids = set(other_raw.get("canonical_product_ids") or [])
        overlap = other_ids & set(beer.canonical_product_ids)
        if overlap:
            issues.append(
                BeerValidationIssue(
                    "canonical_product_id_claimed_by_another_beer",
                    f"{sorted(overlap)} also in {other_path.name}",
                )
            )

    return issues


if __name__ == "__main__":
    main()
