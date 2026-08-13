"""Reads the previously-published `catalog_version` and returns exactly
that value plus one — Catalog Contract 1.0 Part 2's own "monotonically
incremented by exactly one" rule, Catalog Builder Implementation Design
Part 7. No other versioning logic belongs here.
"""

from __future__ import annotations

import json
from pathlib import Path


class VersionError(Exception):
    """A structural failure reading the existing catalog's version — the
    caller treats this as an abort."""


def next_catalog_version(current_catalog_path: Path) -> int:
    """Falls back to `0` (then `+1` = `1`) if `current_catalog_path`
    doesn't exist — the very first build."""
    if not current_catalog_path.exists():
        return 1

    try:
        data = json.loads(current_catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise VersionError(f"{current_catalog_path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict) or "catalog_version" not in data:
        raise VersionError(f"{current_catalog_path} has no catalog_version field")

    current_version = data["catalog_version"]
    if not isinstance(current_version, int) or isinstance(current_version, bool):
        raise VersionError(f"{current_catalog_path}'s catalog_version is not an integer: {current_version!r}")

    return current_version + 1
