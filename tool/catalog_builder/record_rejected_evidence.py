"""Appends one entry to `enrichment/rejected_evidence.yaml` — the one
place a founder records that a piece of researched evidence was found
and specifically rejected, so a future research pass doesn't waste time
rediscovering the same dead end (Catalog Enrichment Playbook's
rejected-evidence workflow, approved RC7.6, this CLI built RC7.7).

Mirrors `create_beer.py`/`update_beer.py`'s philosophy exactly: every
curated field is a required, explicit CLI argument (nothing inferred or
read off disk beyond what's needed to cross-reference-validate);
refuses loudly on any unsafe condition rather than working around it;
round-trip validates whatever's about to be written before persisting
it.

Append-only, enforced by re-validating the *whole* file (existing
entries plus the new one) via `validate_rejected_evidence_yaml` before
writing — duplicate detection therefore falls out of that same
validation pass rather than needing its own separate check here (see
`enrichment_schema.py`'s `_rejected_evidence_identity` for what
"duplicate" means).

Does not modify `update_beer.py` or `create_beer.py`. Cross-reference
sets (`beer_keys`, `brewery_names`) are built here via
`enrichment_reader.py`'s existing `load_enrichment_directory`, reused
rather than reimplemented — this module owns no beer-loading logic of
its own.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import List, Optional

import yaml

from .enrichment_reader import EnrichmentReaderError, load_enrichment_directory
from .enrichment_schema import EnrichmentSchemaError, validate_rejected_evidence_entry, validate_rejected_evidence_yaml
from .models import RejectedEvidenceEntry

_FILE_HEADER = (
    "# enrichment/rejected_evidence.yaml — durable record of researched\n"
    "# evidence found and deliberately not curated onto a Beer/SKU field.\n"
    "# One flat list. Append-only: use\n"
    "# tool/catalog_builder/record_rejected_evidence.py to add an entry —\n"
    "# never hand-edit an existing one. Full workflow and reason taxonomy:\n"
    "# docs/CATALOG-ENRICHMENT-PLAYBOOK.md.\n"
)


class RecordRejectedEvidenceError(Exception):
    """Raised for any condition that would make recording the requested
    rejected-evidence entry unsafe — this module never works around one
    silently."""


def _yaml_string(value: str) -> str:
    # Same ensure_ascii=False discipline create_beer.py's own
    # _yaml_string uses, and for the same reason: json.dumps's default
    # escapes non-BMP characters as UTF-16 surrogate pairs PyYAML doesn't
    # recombine on load.
    return json.dumps(value, ensure_ascii=False)


def _render_entry_lines(entry: RejectedEvidenceEntry) -> List[str]:
    lines = [
        f"- subject_type: {_yaml_string(entry.subject_type)}",
        f"  subject_key: {_yaml_string(entry.subject_key)}",
        f"  field: {_yaml_string(entry.field)}",
    ]
    # Omitted, not written as null, when absent (access_blocked only,
    # RC7.11) -- matches how recheck_after is already handled below.
    if entry.value_found is not None:
        lines.append(f"  value_found: {_yaml_string(entry.value_found)}")
    lines.extend(
        [
            f"  source_type: {_yaml_string(entry.source_type)}",
            f"  source_name: {_yaml_string(entry.source_name)}",
            f"  reason_type: {_yaml_string(entry.reason_type)}",
            f"  reason_detail: {_yaml_string(entry.reason_detail)}",
            f"  observed_at: {entry.observed_at.isoformat()}",
            f"  observed_by: {_yaml_string(entry.observed_by)}",
        ]
    )
    if entry.recheck_after is not None:
        lines.append(f"  recheck_after: {entry.recheck_after.isoformat()}")
    return lines


def render_rejected_evidence_yaml(entries: List[RejectedEvidenceEntry]) -> str:
    """Pure function — renders the *entire* `rejected_evidence.yaml`
    contents (header comment plus every entry) from exactly the given
    list. Always rewrites the whole file rather than textually
    appending, the same way `render_beer_yaml` renders a whole Beer file
    fresh each time — simpler and safer than trying to patch existing
    file bytes in place."""
    if not entries:
        return _FILE_HEADER + "\n[]\n"

    lines: List[str] = []
    for entry in entries:
        lines.extend(_render_entry_lines(entry))
    return _FILE_HEADER + "\n" + "\n".join(lines) + "\n"


def record_rejected_evidence(
    *,
    subject_type: str,
    subject_key: str,
    field: str,
    value_found: Optional[str],
    source_type: str,
    source_name: str,
    reason_type: str,
    reason_detail: str,
    observed_at: str,
    observed_by: str,
    recheck_after: Optional[str],
    rejected_evidence_path: Path,
    enrichment_dir: Path,
) -> Path:
    """Validates and appends one new rejected-evidence entry to
    `rejected_evidence_path`, refusing rather than writing anything if
    the result wouldn't be valid. Returns the written path.

    Date arguments are plain ISO strings, not pre-parsed `date` objects —
    `validate_rejected_evidence_entry` already parses them the same way
    it would if this entry had come from disk, so parsing isn't
    duplicated here.
    """
    try:
        load_result = load_enrichment_directory(enrichment_dir)
    except EnrichmentReaderError as exc:
        raise RecordRejectedEvidenceError(
            f"failed to load {enrichment_dir} for beer_key/brewery cross-reference validation: {exc}"
        ) from exc

    beer_keys = {beer.beer_key for beer in load_result.beers}
    brewery_names = {beer.brewery for beer in load_result.beers}

    if rejected_evidence_path.exists():
        try:
            existing_raw = yaml.safe_load(rejected_evidence_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise RecordRejectedEvidenceError(f"{rejected_evidence_path} is not valid YAML: {exc}") from exc
        if existing_raw is None:
            existing_raw = []
        try:
            existing_entries = validate_rejected_evidence_yaml(
                existing_raw, beer_keys=beer_keys, brewery_names=brewery_names
            )
        except EnrichmentSchemaError as exc:
            raise RecordRejectedEvidenceError(
                f"{rejected_evidence_path} is not currently structurally valid: {exc}"
            ) from exc
    else:
        existing_entries = []

    new_entry_raw = {
        "subject_type": subject_type,
        "subject_key": subject_key,
        "field": field,
        "source_type": source_type,
        "source_name": source_name,
        "reason_type": reason_type,
        "reason_detail": reason_detail,
        "observed_at": observed_at,
        "observed_by": observed_by,
    }
    # Omitted, not passed as None, when not given -- validate_rejected_
    # evidence_entry treats a missing key and an explicit None the same
    # way for this field, but omitting it keeps new_entry_raw's shape
    # identical to what a real YAML file would actually contain.
    if value_found is not None:
        new_entry_raw["value_found"] = value_found
    if recheck_after is not None:
        new_entry_raw["recheck_after"] = recheck_after

    try:
        new_entry = validate_rejected_evidence_entry(
            new_entry_raw, beer_keys=beer_keys, brewery_names=brewery_names
        )
    except EnrichmentSchemaError as exc:
        raise RecordRejectedEvidenceError(f"new entry failed validation: {exc}") from exc

    candidate_entries = existing_entries + [new_entry]
    content = render_rejected_evidence_yaml(candidate_entries)

    # Fail loudly rather than writing a file this package's own
    # structural validator would immediately reject — same discipline
    # create_beer.py/update_beer.py already apply at write time. This
    # second pass is also where append-only duplicate detection actually
    # happens: if new_entry duplicates an existing one,
    # validate_rejected_evidence_yaml raises here, before anything is
    # written.
    parsed_back = yaml.safe_load(content)
    try:
        validate_rejected_evidence_yaml(parsed_back, beer_keys=beer_keys, brewery_names=brewery_names)
    except EnrichmentSchemaError as exc:
        raise RecordRejectedEvidenceError(f"amended rejected_evidence.yaml failed structural validation: {exc}") from exc

    rejected_evidence_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_evidence_path.write_text(content, encoding="utf-8")
    return rejected_evidence_path


def main() -> None:
    """Thin CLI wrapper around `record_rejected_evidence()` — every
    argument maps directly to that function's own parameters; no
    decision made here that the function doesn't already make itself."""
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description="Record one rejected-evidence entry in enrichment/rejected_evidence.yaml."
    )
    parser.add_argument("--subject-type", required=True, choices=["beer", "brewery"])
    parser.add_argument("--subject-key", required=True)
    parser.add_argument("--field", required=True, help='the Beer/SKU field the evidence was about, e.g. "abv"')
    parser.add_argument(
        "--value-found",
        default=None,
        help="the value that was found and rejected; required unless --reason-type access_blocked",
    )
    parser.add_argument("--source-type", required=True, choices=["manufacturer", "manual_observation"])
    parser.add_argument("--source-name", required=True)
    parser.add_argument(
        "--reason-type",
        required=True,
        choices=[
            "wrong_variant",
            "wrong_product_line",
            "access_blocked",
            "imprecise_value",
            "incompatible_unit",
            "conflicting_source_subordinate",
        ],
    )
    parser.add_argument("--reason-detail", required=True)
    parser.add_argument("--observed-at", default=date.today().isoformat(), help="default: today")
    parser.add_argument("--observed-by", default="founder")
    parser.add_argument("--recheck-after", default=None, help="omit if this rejection never needs a recheck")

    parser.add_argument("--enrichment-dir", type=Path, default=repo_root / "enrichment")
    parser.add_argument(
        "--rejected-evidence-path",
        type=Path,
        default=repo_root / "enrichment" / "rejected_evidence.yaml",
    )

    args = parser.parse_args()

    try:
        written = record_rejected_evidence(
            subject_type=args.subject_type,
            subject_key=args.subject_key,
            field=args.field,
            value_found=args.value_found,
            source_type=args.source_type,
            source_name=args.source_name,
            reason_type=args.reason_type,
            reason_detail=args.reason_detail,
            observed_at=args.observed_at,
            observed_by=args.observed_by,
            recheck_after=args.recheck_after,
            rejected_evidence_path=args.rejected_evidence_path,
            enrichment_dir=args.enrichment_dir,
        )
    except RecordRejectedEvidenceError as exc:
        raise SystemExit(f"record_rejected_evidence failed: {exc}") from exc

    print(f"Recorded rejected evidence in {written}")


if __name__ == "__main__":
    main()
