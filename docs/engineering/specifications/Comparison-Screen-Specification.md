# ValueBrew — Engineering Screen Specification: COMPARISON

**Document type:** Engineering Screen Specification (not a Screen Contract).
**Implements:** Comparison Screen Contract (14), in full.
**Built under:** the Canonical Screen Specification Template's citation discipline — every field filled by citation or explicitly marked unspecified.
**Consumers:** UI/UX design, Flutter engineering, QA engineering.
**Version:** 1.0.
**Status:** Draft, pending engineering review. Contains one significant open architectural gap (beyond-two-candidate logic) that blocks a specific subset of behavior — see §10 and §13.

---

## 1. Screen Purpose

Comparison evaluates two or more already-identified beers relative to one another, producing a winner within the named set, a Trade-off Explanation, or a Tie Disclosure. It is the sole screen that reasons about *relationships* between named candidates — never about what exists elsewhere in the catalog, and never about a single beer in isolation.

*Citation: Comparison Screen Contract (14), §1.*

---

## 2. User Goals

- "I want to compare beers" — arriving with specific, already-known candidates, wanting a direct answer between them rather than a funneled recommendation from scratch.
- Wanting richer, multi-candidate treatment of a trade-off or tie already surfaced elsewhere in the product.

*Citation: User Interaction Model (06), §1.*

---

## 3. Entry Conditions

| Source | What arrives |
|---|---|
| **Search/Browse Results**, two or more candidates selected | The named candidate set; any Preference Summary carried from Home |
| **Recommendation**, a genuine trade-off or tie surfaced and richer treatment invited | The candidate set involved in that trade-off/tie, and the full Preference Summary |
| **Beer Detail**, an explicit signal of openness to alternatives or a direct comparison request | The current SKU, as one candidate in the new comparison set |

*Citation: Comparison Screen Contract (14), §3; Navigation Contract (16), §4, §6.*

**Precondition, absolute:** at least two already-identified, resolvable candidates. This screen never searches the catalog to produce its own candidates — it only ever reasons about candidates it was explicitly handed.

*Citation: Comparison Screen Contract (14), §2 MUST, MUST NEVER.*

---

## 4. Exit Conditions

| Trigger | Destination |
|---|---|
| Explicit request for deeper context on one named candidate | Beer Detail — carrying that one candidate's SKU identity only |
| Explicit refinement of a previously stated constraint | Recommendation — a hand-back, carrying the current candidate set and Preference Summary forward, never a restart |
| Explicit request to check one candidate's charged price | Price Verification — carrying that one candidate's SKU identity only |
| Explicit selection of a winner, or explicit acceptance of a tie | Decision Complete — no screen change |

*Citation: Comparison Screen Contract (14), §4, §7; Navigation Contract (16), §3, §4, §6.*

These edges were checked against Information Architecture's own navigation statement and found fully consistent — no discrepancy of the kind found on Beer Detail's specification exists here.

*Citation: Information Architecture (08), §4.*

---

## 5. Information Hierarchy

Directly citing Content Architecture §3's Comparison entry, without redesign:

- **Primary:** the Comparison Result — a clear winner, or a Trade-off/Tie.
- **Supporting:** Beer Identity and Alcohol-Adjusted Value for every candidate, shown together — comparison only means something with all candidates present at once.
- **Contextual:** Preference Summary, so the person can see what was actually weighed.
- **Progressive:** at most one clarifying question.
- **Explanation:** attached to the Comparison Result, especially load-bearing whenever a Trade-off is involved.
- **Confidence:** attached per candidate and to the overall result — **two distinct layers, never merged.**
- **Recovery:** for a tie, an unresolved trade-off, or insufficient differentiation.
- **Completion:** reached once a winner is chosen or a tie/trade-off is accepted as the answer.

*Citation: Content Architecture (10), §3; Comparison Screen Contract (14), §5.*

**The dual confidence layer, stated with the precision the canon itself insists on:** per-candidate confidence reflects each SKU's own Verified and Computed Facts, uniformly high, exactly as on Beer Detail. Result-level confidence reflects the Comparison Result itself, carrying the same unusual property the Trade-off object has everywhere in the canon: the underlying facts are high-confidence even when the judgment of which side to prefer is low-confidence, whenever the differentiator is a Soft Preference rather than a Hard or Strong one. These two layers must never be collapsed into one figure.

*Citation: Comparison Screen Contract (14), §6.*

---

## 6. Screen Sections

Six functional sections:

**A. Candidate Set Display** — Beer Identity and Alcohol-Adjusted Value for every candidate, always shown together, never partially; present from arrival onward, before and after resolution.

**B. Comparison Result** — the winner, Trade-off, or Tie, with its Explanation and per-layer Confidence as intrinsic, non-detachable sub-parts; visible only once resolved.

**C. Preference Summary Context** — what was actually weighed, carried from wherever the comparison originated.

**D. Clarifying Question** — at most one, only when what matters most between candidates hasn't already been stated.

**E. Recovery** — an unresolvable candidate, communicated plainly, never silently dropped.

**F. Actions** — select a winner, accept a tie, ask "why," add or remove a candidate, refine a constraint, request Beer Detail or Price Verification for one named candidate.

*Citation: Comparison Screen Contract (14), §5, §7, §8.*

**How these sections are visually arranged is a design decision. Intentionally left unspecified by the Canonical Architecture.**

---

## 7. Every UI Element

| Element | Purpose | Required Data | Optional Data | Visibility Rule |
|---|---|---|---|---|
| **Candidate Set Display** | Show every candidate's identity and value together | Beer Identity + Alcohol-Adjusted Value per candidate | Style Benchmark relative standing per candidate, where available | Always visible from arrival, before and after resolution |
| **Comparison Result — Winner** | State that one candidate dominates cleanly within the named set | The winning candidate; per-candidate and result-level Confidence; Explanation | — | Only in Resolved state, when a clean winner exists |
| **Comparison Result — Trade-off Explanation** | Name the specific dimensions on which candidates differ | The named dimensions; the constituent facts, shown alongside, never separated; Explanation; both confidence layers | — | Only in Resolved state, when no clean winner exists |
| **Comparison Result — Tie Disclosure** | State plainly that candidates are equivalent on everything known to matter | The equivalence statement; Explanation; both confidence layers | — | Only in Resolved state, and only after the tie-breaker rule has already been applied and failed to differentiate |
| **Preference Summary Context Display** | Show what was actually weighed | Preference Summary as carried forward (may be minimal) | — | Always visible, contextually |
| **Clarifying Question** | Resolve genuine ambiguity about what matters most, if not already stated | The question content — not canonically specified, depends on the specific ambiguity | — | Only in Clarifying state; never a second instance in the same comparison cycle |
| **Select Winner Action** | Register explicit choice following a Trade-off Explanation or a dominant candidate | The chosen candidate | — | Only when the Comparison Result is a Winner or Trade-off — **not the mechanism for resolving a Tie** |
| **Accept Tie Action** | Register explicit acceptance of a Tie Disclosure as the answer | — | — | Only when the Comparison Result is a Tie — a distinct action from Select Winner, never conflated with it |
| **Ask "Why" Action** | Re-surface the existing Explanation | — | — | Only when a Comparison Result and its Explanation already exist |
| **Add/Remove Candidate Action** | Change the named set mid-comparison | The candidate being added or removed | — | Removal is only available when it would leave at least two candidates remaining — this is a stated precondition on the action itself, not a post-hoc correction |
| **Refine Constraint Action** | Change a previously stated preference | The input being changed | — | Always available; always hands back to Recommendation |
| **Request Beer Detail (per candidate)** | Drill into full detail for one named candidate | Which candidate | — | Always available per candidate; does not alter the comparison itself |
| **Request Price Verification (per candidate)** | Check one candidate's charged price | Which candidate | — | Always available per candidate |
| **Unresolvable Candidate Recovery Display** | Inform plainly that a named candidate can't be resolved, invite removal or replacement | Which candidate | — | Only in Recovering state; never silently drops the candidate without informing |

*Citation: Comparison Screen Contract (14), §2, §5, §6, §7.*

**No element beyond these fourteen is permitted.**

---

## 8. User Interactions

| Canonical action | Detail |
|---|---|
| **View the comparison** | Presents the composition; a winner, trade-off, or tie is shown, or a clarifying question is posed first if needed. |
| **Answer the clarifying question** | Applied once; the comparison is re-evaluated a single time. |
| **Select a winner** | Requires a Comparison Result already resolved as a Winner or Trade-off. Moves Decision Status to Completed. |
| **Accept a tie as the answer** | Requires a Tie Disclosure already resolved. Moves Decision Status to Completed. |
| **Ask "why"** | Requires an existing Explanation. Re-surfaces it; generates nothing new. |
| **Add or remove a candidate** | At least two candidates must remain. Re-evaluates the set; reasoning already established for unchanged candidates is not redone from scratch. |
| **Refine a constraint** | Hands back to Recommendation, carrying the current candidate set and Preference Summary. |
| **Request Beer Detail or Price Verification for one candidate** | Requires that candidate already be part of the named set. Hands off, carrying that one SKU forward. |

*Citation: Comparison Screen Contract (14), §7.*

**Interaction modality is not specified anywhere in the canon.** Whether these are realized as taps, selections, or another mechanism is a design decision. **Intentionally left unspecified by the Canonical Architecture.**

*Citation: Feature Inventory (07), §1; Review Guide (00), §2.*

---

## 9. States

Mapped exhaustively onto Comparison Screen Contract §8's own State Machine. No new state introduced.

| Requested category | Canonical mapping | Notes |
|---|---|---|
| **Initial** | **Initial** | Entry: arrival with a named candidate set. Exit: the set is evaluated at least once. No result presented before evaluation. |
| **Populated** | **Evaluating**, refined further into **Resolved** once a result exists | Evaluating: candidate facts loaded and under evaluation, entered every time the set or its inputs change, including first arrival. Resolved: the fuller "populated" condition, with a winner, trade-off, or tie also present. |
| **Comparison unavailable** | **Recovering** — scoped to one candidate, not the whole screen | The canon defines this per-candidate ("a member of the named set... cannot be resolved"), never as a global "comparison capability unavailable" condition. No canonical state represents the entire comparison being unavailable as a distinct concept from one unresolvable candidate. |
| **Recovering (if canonically applicable)** | **Recovering** — the same single canonical state as "Comparison unavailable," above | Both requested categories collapse to one canonical state; presenting them as two would introduce a state the Screen Contract doesn't define. |
| **Completed (if applicable)** | **Completed** | Applicable, with **two distinct entry paths, preserved rather than merged**: explicit winner selection (following a Trade-off Explanation or a dominant candidate), or explicit tie acceptance (following a Tie Disclosure) — two different actions, two different result types, one terminal state. |
| **Any other canonical state** | **Clarifying** | Entry: one further question would resolve genuine ambiguity. Exit: the question is answered. Never a second instance. |

*Citation: Comparison Screen Contract (14), §8; Screen Specification Template (18), §7.*

**Stated with the emphasis the explicit instruction not to simplify tie handling requires:** a Tie Disclosure is a **Resolved**-state outcome, not a Recovering condition. The "insufficient differentiation" language in §3's Recovery State describes the condition that, once the single clarifying question and the tie-breaker rule have both been exhausted, resolves *into* the Tie Disclosure — it is never presented as a failure, and it never triggers a Recovering display of its own.

*Citation: Comparison Screen Contract (14), §3, §11.*

---

## 10. Validation Rules

- No candidate may be added that wasn't part of the original request or an explicit later addition — this screen never searches the catalog.
- Removal is only permitted when at least two candidates would remain afterward; this is a stated precondition on the action, not a state to recover from after the fact.
- The Recommendation Framework's tie-breaker rule must be applied and must fail to differentiate the candidates before a Tie Disclosure may legitimately be presented.
- **No more than one clarifying question may ever be posed, under any circumstance, in a single comparison.**
- A Trade-off must always be presented with its constituent facts alongside it — never split across separate views.
- A winner must never be manufactured to avoid presenting a genuine tie or trade-off.
- Per-candidate confidence and result-level confidence must remain two distinct, simultaneously visible layers — never merged into one figure.
- **Comparison must never claim or imply catalog-wide "Recommended" status.** Its conclusion is always bounded to the named set — "Comparison can conclude that Beer A is better than Beer B. It can never claim to have recommended the best beer in existence, because it never looked past the candidates it was handed."

*Citation: Comparison Screen Contract (14), §2, §6, §10.*

**Genuinely unresolved by the frozen canon — must not be filled by inference at this layer:** the logic for three or more candidates, particularly non-transitive results (Candidate A beating Candidate B, B tied with Candidate C, but A beating C outright). Every worked example of tie-breaking and trade-off reasoning across the entire canon assumes exactly two candidates. Whether a 3+ comparison should present one combined result, several pairwise sub-comparisons, or resolve some other way is genuinely undecided. **Intentionally left unspecified by the Canonical Architecture; pending ADR resolution (Engineering Planning Roadmap, item 1.5).** This gap was also found reachable inside Recommendation's own Core V1 flow, independent of whether this screen is entered at all, per the Resolution Report's Finding M3 — it is not confined to this screen alone.

*Citation: Comparison Screen Contract (14), §11; Resolution Report, Finding M3.*

---

## 11. Accessibility Considerations

**Intentionally left unspecified by the Canonical Architecture**, per the Screen Specification Template's placeholder discipline.

*Citation: Screen Specification Template (18), §11.*

The one constraint statable with canonical authority: no element may be introduced beyond the fourteen named in §7. Worth flagging specifically for this screen: the requirement that per-candidate and result-level confidence remain **visibly, structurally distinguishable, never merged**, is a canonical content requirement, not a styling suggestion — whatever accessible presentation is eventually built must preserve that distinction by whatever means the eventual standard requires, not rely on visual proximity alone.

*Citation: Comparison Screen Contract (14), §6, §10.*

---

## 12. Copy Requirements

Exact wording remains a design/content deliverable. What follows are the requirements that wording must satisfy.

- **"Better" and "Recommended" must never be used interchangeably.** A Comparison winner is described as better than the other named candidates, on stated grounds, within the named set — never described as "the recommended beer" or "the best beer available."
- **Trade-offs must be framed against what the person actually said, never against what the engine assumes they'd prefer** — the same discipline the Recommendation Framework establishes generally, reused here without modification. Canonical example of correct framing: *"this is different from your stated style, but meaningfully better value, since you didn't set a hard style limit."* Canonical example of forbidden framing: *"this is objectively the smarter pick."*
- **A tie must be stated plainly as a tie** — "these are equivalent on everything you've told me matters" — never softened, never apologized for, never presented as an incomplete answer.
- **No invented numerical precision** in confidence statements or trade-off descriptions.
- **Forbidden terms, per the Canonical Interaction Lexicon:** "Score" or "Rating," anywhere. "Alternative," used as an unqualified catch-all, in place of the specific canonical terms Trade-off or Comparison. "Verify," used loosely, outside Price Verification's own scope.

*Citation: Comparison Screen Contract (14), §6; Recommendation Framework (04), §4, §6; Canonical Interaction Lexicon (17), §3, §4, §5.*

---

## 13. Edge Cases

**Three or more candidates in the named set.** This is the flagship open item on this screen. The tie-breaker and trade-off logic this screen's own §6 and §2 depend on is worked out only for exactly two candidates anywhere in the canon; non-transitive results are entirely unaddressed. **Intentionally left unspecified by the Canonical Architecture; pending ADR resolution.**
*Citation: Comparison Screen Contract (14), §11; Resolution Report, Finding M3.*

**Attempting to remove a candidate when only two remain.** Fully resolved, not a gap: the Add/Remove action's own precondition requires at least two candidates to remain, so the removal is simply unavailable rather than needing to be handled after the fact.
*Citation: Comparison Screen Contract (14), §7.*

**A candidate becomes unresolvable mid-comparison** (for instance, a stale reference discovered after arrival). Fully resolved: enters Recovering, informs plainly, invites removal or replacement, never silently drops the candidate.
*Citation: Comparison Screen Contract (14), §11.*

**The clarifying question is answered and the result is still a tie.** Fully resolved, and worth stating precisely because it looks like a failure and isn't one: this is exactly the sequence that legitimately produces a Tie Disclosure — the clarifying question and the tie-breaker rule have both been exhausted, and the honest resolution is the tie itself, not a sign that something went wrong.
*Citation: Comparison Screen Contract (14), §3, §6, §11.*

**A person drills into Beer Detail for one candidate mid-comparison.** Fully resolved: does not alter the comparison state; the person returns to the same comparison, unchanged, or explicitly hands off from Beer Detail elsewhere.
*Citation: Comparison Screen Contract (14), §6.*

**A refined constraint would have excluded one of the named candidates had it been known from the start.** Fully resolved as a matter of ownership, though worth stating precisely: refining a constraint always hands back to Recommendation; Comparison itself never re-filters or re-validates the candidate set against the new constraint — that re-evaluation is Recommendation's responsibility once re-entered, not this screen's.
*Citation: Comparison Screen Contract (14), §7; Information Architecture (08), §3.*

---

## 14. Analytics Candidates

Names only, no schema, properties, or tooling defined, per the Screen Specification Template's placeholder discipline.

*Citation: Screen Specification Template (18), §12.*

- Screen viewed (Comparison reached, by candidate set size)
- Clarifying question presented
- Clarifying question answered
- Comparison Result produced — winner
- Comparison Result produced — trade-off
- Comparison Result produced — tie
- Winner selected (Decision Complete)
- Tie accepted (Decision Complete)
- Explanation requested ("why")
- Candidate added mid-comparison
- Candidate removed mid-comparison
- Constraint refined (hand-back to Recommendation)
- Beer Detail requested, per candidate
- Price Verification requested, per candidate
- Unresolvable candidate recovery shown

*Citation: Screen Specification Template (18), §12.*

---

## 15. Non-functional Requirements

**Intentionally left unspecified by the Canonical Architecture** for responsiveness, performance budgets, offline behavior, and platform expectations.

*Citation: Review Guide (00), §2; ADR (19), §7.*

The one grounded, citable fact: this screen's Referenced Information requires Beer Knowledge Base facts for every named candidate, and the Style Benchmark computation where available. Style Benchmark is an Important-Soon-After Platform Service, not Core V1 — this screen must degrade gracefully in its absence.

*Citation: Comparison Screen Contract (14), §3; Feature Inventory (07), §5.*

---

## 16. Acceptance Criteria

Restated directly from Comparison Screen Contract §12:

✓ Comparison never includes a candidate that wasn't part of the original request.
✓ A Comparison Result is never presented without the Recommendation Framework's tie-breaker rule having been applied first.
✓ A Tie Disclosure is never replaced with an arbitrary pick.
✓ A Trade-off is never presented without its constituent facts alongside it.
✓ No more than one clarifying question is ever posed in a single comparison.
✓ Per-candidate confidence and result-level confidence are always kept visibly distinct, never merged.
✓ Comparison never states or implies that its conclusion reflects a search of the whole catalog.
✓ Refining a constraint always hands back to Recommendation rather than being resolved on this screen.

*Citation: Comparison Screen Contract (14), §12.*

---

## 17. Traceability Matrix

| Specification Section | Canonical Source(s) |
|---|---|
| 1. Screen Purpose | Comparison Screen Contract §1 |
| 2. User Goals | User Interaction Model §1 |
| 3. Entry Conditions | Comparison Screen Contract §2, §3; Navigation Contract §4, §6 |
| 4. Exit Conditions | Comparison Screen Contract §4, §7; Navigation Contract §3, §4, §6; Information Architecture §4 |
| 5. Information Hierarchy | Content Architecture §3; Comparison Screen Contract §5, §6 |
| 6. Screen Sections | Comparison Screen Contract §5, §7, §8 |
| 7. Every UI Element | Comparison Screen Contract §2, §5, §6, §7 |
| 8. User Interactions | Comparison Screen Contract §7; Feature Inventory §1; Review Guide §2 |
| 9. States | Comparison Screen Contract §3, §8, §11; Screen Specification Template §7 |
| 10. Validation Rules | Comparison Screen Contract §2, §6, §10, §11; Resolution Report M3 |
| 11. Accessibility Considerations | Screen Specification Template §11; Comparison Screen Contract §6, §10 |
| 12. Copy Requirements | Comparison Screen Contract §6; Recommendation Framework §4, §6; Canonical Interaction Lexicon §3, §4, §5 |
| 13. Edge Cases | Comparison Screen Contract §3, §6, §7, §11; Resolution Report M3; Information Architecture §3 |
| 14. Analytics Candidates | Screen Specification Template §12 |
| 15. Non-functional Requirements | Review Guide §2; ADR §7; Comparison Screen Contract §3; Feature Inventory §5 |
| 16. Acceptance Criteria | Comparison Screen Contract §12 |

---

## Document Notes

This screen carries the most consequential open architectural question of the four specified so far. Everything involving exactly two candidates — the large majority of realistic comparisons — is fully specified and buildable. The three-or-more-candidate path is not, and this document does not guess at a resolution anywhere in its fourteen elements, six states, or validation rules.
