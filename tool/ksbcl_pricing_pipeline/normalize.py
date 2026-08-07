"""Stage 3 (Normalization) — the fold pipeline and structured extraction
(architecture §4.1-4.5).

Pure functions operating on plain strings, no I/O — mirroring Stage 1's
``parsing.py`` and Stage 2's ``matching.py`` testability convention.
Every rule here is a literal implementation of the frozen architecture
document; no behavior beyond what it specifies.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from .matching import fold as vocab_fold
from .matching import word_boundary_match
from .normalize_models import NormalizedRow

# §4.7: hand-maintained, bumped alongside any change to the rules in
# §4.1-§4.5. Not a content hash — there is no external file to hash.
NORMALIZATION_RULE_VERSION = "stage3-v1"

_MULTIPLIER_UNIFY = str.maketrans({"×": "x", "X": "x"})

# §4.1 step 5: unify volume-unit casing/spacing into "ml" with no internal
# space, tolerant of any casing (ML/Ml/ml) and an optional single space
# between the number and the unit. No trailing boundary requirement — the
# canonical multiplier "x" is a valid, expected continuation immediately
# after the unit (the same adjacency §4.4's pack_size_ml grammar treats
# as non-violating), so requiring one here would silently fail to unify
# e.g. "720 MLx12Btls", the same class of gap the token-boundary fix
# (§12.1) already closed for extraction itself.
_UNIT_CASING_PATTERN = re.compile(r"(\d)\s?ml", re.IGNORECASE)

# §4.4 pack_size_ml: digits (optional decimal point) immediately followed
# by the canonical unit "ml" (post step 5, always glued with zero space).
_PACK_SIZE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)ml")

# §4.4 pack_count: the canonical multiplier "x" — optionally
# whitespace-separated from the preceding volume unit, and optionally
# whitespace-separated from the count digits that follow it (both
# tolerances confirmed real, e.g. "1000ML x 12Btls").
_MULTIPLIER_COUNT_PATTERN = re.compile(r"\s?x\s?(\d+)")

# §4.4 container_type: the two priority tiers.
_SPECIFIC_CONTAINER_TERMS = {
    "can": ["can", "cans"],
    "pet_bottle": ["pet"],
    "tetra_pack": ["tetra"],
}
_BOTTLE_TERMS = ["btl", "btls", "bottle", "bottles"]

# §4.4: tokens recognized as "a container token" immediately after a
# pack_count match, for the purpose of deciding whether that match is
# valid (vs. an intervening fragment like "P." rejecting it — the
# documented, accepted P.Btls limitation, §12).
_ALL_CONTAINER_TOKENS = ["can", "cans", "pet", "tetra"] + _BOTTLE_TERMS


def _char_class(ch: str) -> str:
    if ch.isalpha():
        return "letter"
    if ch.isdigit():
        return "digit"
    return "other"


def strip_supplier_code_fragment(text: str, supplier_code: str) -> Tuple[str, bool]:
    """§4.1 step 4: strip `(supplier_code)`, wherever it appears, tolerant
    of a missing opening parenthesis. Returns (stripped_text, malformed).
    """
    pattern = re.compile(r"\(?" + re.escape(supplier_code) + r"\)")
    malformed = False
    result_parts = []
    last_end = 0
    for match in pattern.finditer(text):
        if not match.group(0).startswith("("):
            malformed = True
        result_parts.append(text[last_end:match.start()])
        last_end = match.end()
    result_parts.append(text[last_end:])
    stripped = "".join(result_parts)
    # Re-collapse whitespace left behind by the removed fragment.
    stripped = " ".join(stripped.split())
    return stripped, malformed


def fold_1_to_4(item_name_raw: str, supplier_code: str) -> Tuple[str, bool]:
    """§4.1 steps 1-4: NFKC, multiplier-unify, whitespace-collapse,
    supplier-code strip. Casing preserved — this is `display_name`'s
    exact output, and the input `normalized_name_key` continues from.
    Returns (folded_text, suffix_malformed).
    """
    text = unicodedata.normalize("NFKC", item_name_raw)
    text = text.translate(_MULTIPLIER_UNIFY)
    text = " ".join(text.split())
    text, malformed = strip_supplier_code_fragment(text, supplier_code)
    return text, malformed


def fold_5_to_6(display_folded_text: str) -> str:
    """§4.1 steps 5-6: unify volume-unit casing/spacing, then case-fold.
    Continues from `fold_1_to_4`'s output — this is `normalized_name_key`
    and the text every §4.4 extraction rule operates on."""
    text = _UNIT_CASING_PATTERN.sub(lambda m: f"{m.group(1)}ml", display_folded_text)
    return text.casefold()


@dataclass(frozen=True)
class ExtractedPackInfo:
    pack_size_ml: Optional[Decimal]
    pack_count: Optional[int]
    container_type: str


def _extract_pack_size_ml(matching_text: str) -> Optional[Tuple[Decimal, int, int]]:
    """§4.4 pack_size_ml. Returns (value, match_start, match_end) for the
    first valid match, or None. A match is valid only if its right edge
    is a standard boundary or is immediately followed by the canonical
    multiplier character "x" (a defined continuation, not a violation)."""
    for match in _PACK_SIZE_PATTERN.finditer(matching_text):
        end = match.end()
        if end >= len(matching_text):
            valid = True
        else:
            next_char = matching_text[end]
            if next_char == "x":
                valid = True
            else:
                valid = _char_class(matching_text[end - 1]) != _char_class(next_char)
        if valid:
            return Decimal(match.group(1)), match.start(), end
    return None


def _extract_pack_count(matching_text: str, search_from: int) -> Optional[int]:
    """§4.4 pack_count. The integer immediately (optionally, whitespace-
    separated) following the canonical multiplier, itself immediately
    (or whitespace-separated) preceding a recognized container token, or
    the end of the pack-info segment. If neither holds — e.g. an
    intervening fragment like "P." — this returns None (the documented,
    accepted `P.Btls` limitation, §12)."""
    match = _MULTIPLIER_COUNT_PATTERN.match(matching_text, search_from)
    if match is None:
        return None
    count = int(match.group(1))
    rest = matching_text[match.end():]
    rest_stripped = rest[1:] if rest[:1] == " " else rest

    if not rest_stripped:
        return count  # end of the pack-info segment
    for token in _ALL_CONTAINER_TOKENS:
        # Boundary-anchored, not a bare prefix check — "canss" must not
        # match "cans" any more than container_type's own search does
        # (both are the identical accepted, undocumented vocabulary gap,
        # §12; a prefix check would inconsistently "recognize" it here
        # while container_type correctly does not).
        token_len = len(token)
        if rest_stripped[:token_len] == token and (
            token_len == len(rest_stripped) or _char_class(rest_stripped[token_len]) != "letter"
        ):
            return count
    # Not a recognized container token immediately here. Still counts as
    # "the end of the segment" if only punctuation remains until the end
    # of the string (e.g. a stray trailing paren or period).
    if not any(ch.isalnum() for ch in rest_stripped):
        return count
    return None


def _extract_container_type(matching_text: str) -> str:
    """§4.4 container_type: priority order. `can`/`pet_bottle`/
    `tetra_pack` outrank `bottle`. More than one *specific* (top-tier)
    category matching is an undocumented case in the frozen architecture
    (no real row confirms it) — resolved conservatively here as
    `unknown`, consistent with the document's own "never guess" posture,
    rather than picking an arbitrary priority among equally-weighted
    specific assertions."""
    matched_specific = set()
    for category, terms in _SPECIFIC_CONTAINER_TERMS.items():
        for term in terms:
            if word_boundary_match(vocab_fold(term), matching_text):
                matched_specific.add(category)
                break
    if len(matched_specific) == 1:
        return next(iter(matched_specific))
    if len(matched_specific) > 1:
        return "unknown"
    for term in _BOTTLE_TERMS:
        if word_boundary_match(vocab_fold(term), matching_text):
            return "bottle"
    return "unknown"


def extract_pack_info(matching_text: str) -> ExtractedPackInfo:
    """§4.4 + §4.5's bundling rule: if no volume is found at all, every
    field is null/`unknown` together — never partially salvaged."""
    size_match = _extract_pack_size_ml(matching_text)
    if size_match is None:
        return ExtractedPackInfo(pack_size_ml=None, pack_count=None, container_type="unknown")

    pack_size_ml, _, size_end = size_match
    pack_count = _extract_pack_count(matching_text, size_end)
    container_type = _extract_container_type(matching_text)
    return ExtractedPackInfo(pack_size_ml=pack_size_ml, pack_count=pack_count, container_type=container_type)


def normalize_row(
    run_month: str,
    item_code: str,
    item_name_raw: str,
    supplier_code: str,
) -> Tuple[NormalizedRow, bool]:
    """Runs the complete Stage 3 mechanism (§4) for one row. Returns
    (row, suffix_malformed) — the malformation fact is not part of the
    public row (§4.5, §12) but the caller needs it for the aggregate
    run-summary metric (§7)."""
    display_folded, suffix_malformed = fold_1_to_4(item_name_raw, supplier_code)
    matching_text = fold_5_to_6(display_folded)
    pack_info = extract_pack_info(matching_text)

    row = NormalizedRow(
        run_month=run_month,
        item_code=item_code,
        display_name=display_folded,
        normalized_name_key=matching_text,
        pack_size_ml=pack_info.pack_size_ml,
        pack_count=pack_info.pack_count,
        container_type=pack_info.container_type,
        normalization_rule_version=NORMALIZATION_RULE_VERSION,
    )
    return row, suffix_malformed
