"""The Stage 4 matching key (architecture §4): ``(normalized_name_key,
pack_size_ml, container_type, pack_count)`` — master's original
five-component key with ``supplier_code`` removed, per the recorded
Identity Decision.

A null ``pack_size_ml`` is Stage 3's sole "extraction failed entirely"
signal (§6): an item_code with a null ``pack_size_ml`` never
participates in exact-key matching in either direction — it is always
its own new canonical product, and it is never a match target for a
later item_code either, since matching on an absent value would be a
guess this pipeline never makes. ``MatchingKey`` is only ever computed
for a row whose ``pack_size_ml`` is not null; callers route null-key
rows to the "always new" branch before ever calling this.
"""

from __future__ import annotations

from decimal import Decimal
from typing import NamedTuple, Optional

from .normalize_models import NormalizedRow


class MatchingKey(NamedTuple):
    normalized_name_key: str
    pack_size_ml: Decimal
    container_type: str
    pack_count: Optional[int]


def matching_key(normalized_row: NormalizedRow) -> Optional[MatchingKey]:
    """Returns ``None`` for a null ``pack_size_ml`` row — the caller's
    signal to skip exact-key matching entirely for this row (§6)."""
    if normalized_row.pack_size_ml is None:
        return None
    return MatchingKey(
        normalized_name_key=normalized_row.normalized_name_key,
        pack_size_ml=normalized_row.pack_size_ml,
        container_type=normalized_row.container_type,
        pack_count=normalized_row.pack_count,
    )
