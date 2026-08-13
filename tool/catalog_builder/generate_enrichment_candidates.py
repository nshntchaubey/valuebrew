"""Bootstraps `enrichment/candidates/` from the real `beer_master.csv`.

Not part of Catalog Builder Implementation Design's own module list — a
one-time, explicitly out-of-band tool introduced this session, kept
separate from the frozen Part 1 module set on purpose. It exists to solve
a narrower problem than any frozen document specifies a tool for: turning
1,000+ real SKU rows into a real starting point for enrichment, without
performing the one identity act every frozen document insists must stay
human (Catalog Implementation Architecture Part 2, Catalog Enrichment
Playbook Part 2, Catalog Builder Architecture Part 1): deciding which
`canonical_product_id`s are the same real Beer.

**What a candidate file is, and is not.** One `enrichment/candidates/
<canonical_product_id>.yaml` per admitted `beer_master.csv` row —
SKU-grain, not Beer-grain. It is a scratch draft, never read by
`enrichment_reader.py`/`enrichment_schema.py`, never joined into a
catalog build, and never itself a source of truth. Turning a candidate
into a real Beer is a human act: pick one or more candidates that are
genuinely the same beer, assign one real `beer_key`, and hand-write (or
adapt) a real `enrichment/beers/<beer_key>.yaml` from them. This module
does not perform, suggest, or shortcut that step.

**What's populated vs. left for a human.** Only `canonical_product_id`,
`item_name_raw`, and `display_name` — Government/pipeline-sourced,
objectively known today, not owned by `enrichment/` in the sense Beer
Knowledge Base Architecture Part 2 forbids (that prohibition names price,
size, and container type specifically — the identity/naming fields here
are the same evidence Catalog Builder Architecture Part 3 already
classifies as a human's starting research material, not a fact this
repository would ever assert on its own authority). Every curated field
(`suggested_beer_key`, `name`, `brewery`, `style`, `abv`, `is_craft`,
`images`) is written as an explicit `null`/TODO placeholder — never a
guess, per the Catalog Enrichment Playbook's own "never guess" rule.

**Determinism.** Same input rows always produce byte-identical output —
no timestamps, no non-deterministic ordering, matching the same
discipline the real Catalog Builder itself will need (Implementation
Roadmap Part 6).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .beer_master_reader import read_beer_master_csv
from .models import BeerMasterRow


def _yaml_string(value: str) -> str:
    """A safely-quoted YAML scalar for `value`. JSON string escaping
    (backslashes, quotes) is valid YAML double-quoted-scalar syntax, so
    this avoids depending on a full YAML dumper just to escape one
    string, while staying trivially correct for the real data's own
    special characters (parentheses, hyphens, quotes). `ensure_ascii=False`
    so non-BMP characters (emoji, rare symbols) round-trip as real UTF-8
    rather than as UTF-16 surrogate pairs PyYAML doesn't recombine."""
    return json.dumps(value, ensure_ascii=False)


def render_candidate_yaml(row: BeerMasterRow) -> str:
    """Pure function: one `BeerMasterRow` -> the exact text of its
    candidate YAML file. No I/O."""
    return (
        f"# Enrichment candidate — a raw draft, not a canonical Beer entity.\n"
        f"# Generated from pricing_data/beer_master.csv by\n"
        f"# generate_enrichment_candidates.py. Do not hand-edit the fields\n"
        f"# above the divider; they are objectively known, pipeline-sourced\n"
        f"# facts and will be overwritten the next time this generator runs.\n"
        f"\n"
        f"canonical_product_id: {_yaml_string(row.canonical_product_id)}\n"
        f"item_name_raw: {_yaml_string(row.item_name_raw)}\n"
        f"display_name: {_yaml_string(row.display_name)}\n"
        f"\n"
        f"# --- Curated fields below are not known from pricing_data/ and must\n"
        f"# --- be researched by hand (Catalog Enrichment Playbook Part 4).\n"
        f"# --- Leave any field you cannot cite a real source for as null —\n"
        f"# --- never guess (Catalog Enrichment Playbook Part 1/10).\n"
        f"\n"
        f"suggested_beer_key: null  # TODO — assign once you decide which real\n"
        f"  # Beer this SKU belongs to (Catalog Enrichment Playbook Part 2, step\n"
        f"  # 3). This generator never decides that for you — it may be the\n"
        f"  # same beer_key as another candidate file at a different pack size.\n"
        f"name: null      # TODO — cleaned display name\n"
        f"brewery: null   # TODO\n"
        f"style: null     # TODO — a style_key from enrichment/styles.yaml, or leave null\n"
        f"abv: null       # TODO — {{value, source_type, source_name, observed_at, observed_by}}\n"
        f"is_craft: null  # TODO\n"
        f"images: []      # TODO\n"
    )


def write_candidates(rows: List[BeerMasterRow], candidates_dir: Path) -> List[Path]:
    """Writes one candidate file per row into `candidates_dir` (created
    if missing), named deterministically by the row's own
    `canonical_product_id` — already a stable, pipeline-assigned
    identity; this module invents no new ID. Returns the written paths,
    sorted, for a deterministic summary."""
    candidates_dir.mkdir(parents=True, exist_ok=True)

    written: List[Path] = []
    for row in rows:
        path = candidates_dir / f"{row.canonical_product_id}.yaml"
        path.write_text(render_candidate_yaml(row), encoding="utf-8")
        written.append(path)

    return sorted(written)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    beer_master_path = repo_root / "pricing_data" / "beer_master.csv"
    candidates_dir = repo_root / "enrichment" / "candidates"

    accepted, rejected = read_beer_master_csv(beer_master_path)
    written = write_candidates(accepted, candidates_dir)

    print(f"Read {beer_master_path}")
    print(f"  accepted rows (candidates generated): {len(accepted)}")
    print(f"  rejected rows (no candidate generated): {len(rejected)}")
    for row in rejected:
        print(f"    - {row.canonical_product_id}: {row.reason_code} {row.reason_detail}")
    print(f"Wrote {len(written)} candidate file(s) to {candidates_dir}")


if __name__ == "__main__":
    main()
