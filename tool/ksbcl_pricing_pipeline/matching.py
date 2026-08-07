"""Stage 2 matching primitives (architecture §4.1, §4.8).

Every function here is pure — no I/O, no config loading — so it can be
unit tested directly against plain strings, mirroring Stage 1's
``parsing.py`` testability convention.

Three things are defined, precisely, in the order the architecture states
them (§4.1):

1. ``fold`` — the minimal, local, permanent fold Stage 2 applies purely
   for matching (Unicode case-fold, whitespace-collapse, ×/x/X
   unification). Never a substitute for Stage 3's ``normalized_name_key``.
2. The token-boundary rule — a boundary exists at every transition
   between character classes (letter / digit / any other character), and
   at the start and end of the string. This is the complete, closed
   definition; nothing here varies by which vocabulary is being matched.
3. ``word_boundary_match`` — the one matching rule used everywhere in
   Stage 2: a literal, folded substring, bounded on both sides. This
   also correctly handles multi-word entries (e.g. ``"strong beer"``)
   with no special-casing, because ``fold`` already collapses internal
   whitespace to a single, canonical space that survives as literal
   substring content — matching only in that exact declared form is the
   one reading of §4.1's "complete token sequence" that requires no
   invented punctuation-normalization behavior (the choice between that
   and a looser reading is recorded as a Product Decision Required, §17,
   and is deliberately not made here).
"""

from __future__ import annotations

_MULTIPLIER_UNIFY = str.maketrans({"×": "x", "X": "x"})


def fold(text: str) -> str:
    """The minimal, local fold Stage 2 applies purely for matching
    (§4.1): Unicode case-fold, ×/x/X unification, whitespace-collapse.
    Applied identically to ``item_name_raw`` and to every config entry —
    never assumed pre-folded on either side (§4.1, §2.2).
    """
    folded = text.casefold()
    folded = folded.translate(_MULTIPLIER_UNIFY)
    return " ".join(folded.split())


def _char_class(ch: str) -> str:
    """One of "letter" / "digit" / "other" — the three classes §4.1's
    token-boundary rule is defined over."""
    if ch.isalpha():
        return "letter"
    if ch.isdigit():
        return "digit"
    return "other"


def _is_boundary(text: str, pos: int) -> bool:
    """True if a token boundary exists between text[pos-1] and
    text[pos], per §4.1: a transition between character classes, or the
    start/end of the string."""
    if pos <= 0 or pos >= len(text):
        return True
    return _char_class(text[pos - 1]) != _char_class(text[pos])


def word_boundary_match(folded_term: str, folded_text: str) -> bool:
    """True if ``folded_term`` appears in ``folded_text`` as a complete,
    boundary-anchored token (or token sequence) — never as a substring
    inside a longer run (§4.1). Both arguments must already be folded
    (via ``fold``) by the caller; this function does no folding itself,
    so it can be reused identically for both single- and multi-word
    entries and for §4.8's ``df`` check.
    """
    if not folded_term:
        return False
    start = 0
    while True:
        idx = folded_text.find(folded_term, start)
        if idx == -1:
            return False
        end = idx + len(folded_term)
        if _is_boundary(folded_text, idx) and _is_boundary(folded_text, end):
            return True
        start = idx + 1


# §4.8: the single literal token this check searches for. Not sourced
# from any config list — §2.2 defines exactly three keys, none of them
# duty-free vocabulary, and §4.8 states the token as a fixed literal,
# not "any entry in a list". Alternate spellings/forms (case, hyphens,
# the spelled-out "Duty Free") are explicitly out of scope here — see
# §16/§17 of the architecture, which classify them as configuration
# content or leave them as a disclosed, unmitigated gap, never as a
# reason to widen this specific check.
_DUTY_FREE_TOKEN = fold("df")


def is_duty_free(item_name_raw: str) -> bool:
    """§4.8: reuses ``word_boundary_match`` exactly, applied to the
    literal token "df", searched anywhere in the folded name — not
    anchored to end-of-string or to immediately preceding the volume
    field (confirmed against real data to vary)."""
    return word_boundary_match(_DUTY_FREE_TOKEN, fold(item_name_raw))
