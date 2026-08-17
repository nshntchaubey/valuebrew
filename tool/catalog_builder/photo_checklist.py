"""Generates one founder-facing checklist for one beer's fieldwork
visit — the direct operational form of the photograph-based
`manual_observation` policy (Catalog Enrichment Playbook Part 4, item
1a; Beer Knowledge Base Architecture Part 5). Reading a checklist and
taking the right photos is the easy part; this module exists because
the two conditions that policy actually requires (personally verify
product identity, cite the specific photo) are easy to forget in the
moment of standing in front of a shelf, so this prints them as
non-skippable steps, not as a footnote.

**[RC7.3 note]:** the founder has since ruled physical fieldwork out
entirely for this project (the RC3 restart) — `manual_observation` as
a source type still exists in the schema and remains valid if a real
photo is ever taken, but manufacturer-sourced remote research, not
fieldwork, is the project's actual current evidence path. This
checklist's own content is left unchanged here — it is still correct
for the case it describes, and rewriting or removing it would be a
tooling redesign, out of scope for a documentation-only cleanup.

Reuses `enrichment_schema.validate_beer_entry` to load the target beer
— the exact same parser `create_beer.py`/`update_beer.py` already use —
rather than re-reading the YAML shape a second way.

Only asks for what is actually still missing: a beer that already has
a real, cited ABV (e.g. `tuborg_strong_premium`, ABV known, calories
still unknown) gets a checklist that says so and skips straight to the
nutrition-panel step, rather than asking a founder to re-photograph a
fact already on file.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

from .enrichment_schema import validate_beer_entry
from .models import AttributionBlock, EnrichmentBeer


class PhotoChecklistError(Exception):
    """Raised when the requested beer can't be loaded — this module
    never guesses at a beer it can't actually find and parse."""


@dataclass(frozen=True)
class ChecklistItem:
    label: str
    instruction: str
    applicable: bool
    skip_reason: Optional[str] = None


@dataclass(frozen=True)
class PhotoChecklist:
    beer_key: str
    name: str
    brewery: str
    style: Optional[str]
    canonical_product_ids: List[str]
    abv_known: Optional[AttributionBlock]
    calories_known: Optional[AttributionBlock]
    items: List[ChecklistItem]


def build_checklist(beer: EnrichmentBeer) -> PhotoChecklist:
    """Pure function — no I/O. Every item is always present in
    `items`, in a fixed order, so the checklist's shape never changes
    beer to beer — only `applicable`/`skip_reason` do."""
    abv_missing = beer.abv is None
    calories_missing = beer.calories_per_100ml is None

    items = [
        ChecklistItem(
            label="Front label",
            instruction="Photograph the full front label, straight-on, legible brand/variant name and pack size.",
            applicable=True,
        ),
        ChecklistItem(
            label="Back label",
            instruction="Photograph the full back label — this is usually where ABV and the nutrition panel live.",
            applicable=abv_missing or calories_missing,
            skip_reason=None if (abv_missing or calories_missing) else "abv and calories_per_100ml already known",
        ),
        ChecklistItem(
            label="Nutrition panel",
            instruction="Photograph the nutrition panel close enough to read every number, especially Energy/Calories per 100ml.",
            applicable=calories_missing,
            skip_reason=None if calories_missing else "calories_per_100ml already known",
        ),
        ChecklistItem(
            label="ABV declaration",
            instruction="Photograph the printed ABV/alcohol-by-volume percentage specifically, even if it also appears elsewhere on the label.",
            applicable=abv_missing,
            skip_reason=None if abv_missing else "abv already known",
        ),
        ChecklistItem(
            label="Barcode (optional)",
            instruction="Photograph the barcode/GTIN if visible — useful for cross-checking against Open Food Facts later, never required.",
            applicable=True,
        ),
        ChecklistItem(
            label="Notes",
            instruction="Write down: exact store/date observed, and anything about the label that felt ambiguous or hard to read.",
            applicable=True,
        ),
    ]

    return PhotoChecklist(
        beer_key=beer.beer_key,
        name=beer.name,
        brewery=beer.brewery,
        style=beer.style,
        canonical_product_ids=list(beer.canonical_product_ids),
        abv_known=beer.abv,
        calories_known=beer.calories_per_100ml,
        items=items,
    )


def load_beer(beer_key: str, beers_dir: Path) -> EnrichmentBeer:
    target_path = beers_dir / f"{beer_key}.yaml"
    if not target_path.exists():
        raise PhotoChecklistError(f"{target_path} does not exist")

    try:
        raw = yaml.safe_load(target_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PhotoChecklistError(f"{target_path.name} is not valid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise PhotoChecklistError(f"{target_path} is not a Beer YAML mapping")

    style_value = raw.get("style")
    style_keys = {style_value} if isinstance(style_value, str) and style_value != "unknown" else set()
    beer, reason_code, detail = validate_beer_entry(raw, filename_beer_key=beer_key, style_keys=style_keys)
    if beer is None:
        raise PhotoChecklistError(f"{target_path} is not currently structurally valid: {reason_code} {detail}")
    return beer


def _print_checklist(checklist: PhotoChecklist) -> None:
    print(f"Fieldwork checklist — {checklist.beer_key}")
    print("=" * 78)
    print(f"Name:      {checklist.name}")
    print(f"Brewery:   {checklist.brewery}")
    print(f"Style:     {checklist.style or 'unknown'}")
    print(f"SKUs:      {', '.join(checklist.canonical_product_ids)}")
    print()
    print("Currently known:")
    print(f"  abv:                {checklist.abv_known.value if checklist.abv_known else 'unknown'}")
    print(f"  calories_per_100ml: {checklist.calories_known.value if checklist.calories_known else 'unknown'}")
    print()
    print("Checklist:")
    for item in checklist.items:
        if item.applicable:
            print(f"  [ ] {item.label} — {item.instruction}")
        else:
            print(f"  [x] {item.label} — SKIP ({item.skip_reason})")

    print()
    print("Before recording anything from a photo, per the adopted evidence policy:")
    print("  1. Personally confirm the photo matches THIS exact beer and pack size —")
    print("     never trust a hosting page's own title or category alone.")
    print("  2. Cite the specific photo in source_name, never the general site")
    print("     (e.g. 'product label photo, checked at <store>, <date>' or the exact")
    print("     Open Food Facts barcode URL) — never just 'Open Food Facts' alone.")
    print()

    missing = []
    if checklist.abv_known is None:
        missing.append("--abv <value> --abv-source-type manual_observation --abv-source-name '<citation>'")
    if checklist.calories_known is None:
        missing.append(
            "--calories-per-100ml <value> --calories-per-100ml-source-type manual_observation "
            "--calories-per-100ml-source-name '<citation>'"
        )
    if missing:
        print("Once photographed, record it with:")
        print(f"  python3 -m tool.catalog_builder.update_beer --beer-key {checklist.beer_key} \\")
        for i, part in enumerate(missing):
            suffix = " \\" if i < len(missing) - 1 else ""
            print(f"    {part}{suffix}")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Generate a fieldwork photo checklist for one beer.")
    parser.add_argument("--beer-key", required=True)
    parser.add_argument("--beers-dir", type=Path, default=repo_root / "enrichment" / "beers")
    args = parser.parse_args()

    try:
        beer = load_beer(args.beer_key, args.beers_dir)
    except PhotoChecklistError as exc:
        raise SystemExit(f"photo_checklist failed: {exc}") from exc

    checklist = build_checklist(beer)
    _print_checklist(checklist)


if __name__ == "__main__":
    main()
