# ValueBrew — Repository Synchronization Patch

**Trigger:** the Price Verification Engineering Screen Specification, previously absent, now exists and is part of the frozen Engineering documentation.
**Scope:** every place in the Flutter Implementation Architecture and the Implementation Bootstrap Plan that assumed "Price Verification has no Engineering Specification."
**Nature of this patch:** wording synchronization only. No new architecture, no new implementation decisions, no milestone renumbering. One dependency addition is included (Change 6) because it is a direct, necessary consequence of presentation work now being in scope for that milestone — not a new decision, just the existing shared-widget dependency rule applied to a milestone it previously didn't reach.

---

## Document 1: Flutter Implementation Architecture

### Change 1

**Section:** 0. Framing

**Existing wording:**
> Where the canon leaves something open (the two carried-forward ambiguities, the Beer Detail → Recommendation navigation inconsistency, the unwritten Price Verification specification), this document does not resolve it either.

**Replacement wording:**
> Where the canon leaves something open (the two carried-forward ambiguities, the Beer Detail → Recommendation navigation inconsistency), this document does not resolve it either.

**Reason:** the Price Verification specification is no longer unwritten, so it no longer belongs in this document's list of open items it must hold without resolving. The two carried-forward ambiguities and the navigation inconsistency remain genuinely open in the canon and are untouched.

---

### Change 2

**Section:** 20. Mapping: Engineering Specifications → Flutter Modules (table row)

**Existing wording:**
> \| Price Verification \| **Engineering Spec not yet written** \| `features/verification` \| Do not build ahead of the specification. Screen Contract alone (Section 15 doc) is sufficient to scaffold the module's domain layer (Section 6), but presentation work should wait for the spec per the project's own "no invention at the implementation layer" discipline. \|

**Replacement wording:**
> \| Price Verification \| Engineering Spec complete \| `features/verification` \| Domain and presentation layers may both be built directly from the specification, following the same pattern as Home, Beer Detail, Recommendation, and Comparison. The specification's own flagged gap — how an imprecise or approximate charged price should be handled — remains open per the canon's citation-only discipline, and must be represented as an explicit Recovery State (Section 11), never resolved by inference. \|

**Reason:** the specification's existence removes the sole reason presentation work was withheld. Price Verification now follows the same domain-and-presentation pattern as every other fully specified screen. The one thing carried forward deliberately is the still-unresolved imprecise-charged-price gap — a specification fills in implementation-facing detail by citation, it doesn't invent resolutions to gaps the canon never closed, so this gap is expected to still be flagged, not resolved, inside the new specification itself.

---

### Change 3

**Section:** Implementation Risks

**Existing wording:**
> - **Price Verification has a Screen Contract but no Engineering Specification.** Building its presentation layer now would mean the implementation, not the specification process, resolving unstated details — exactly the invention the project's own governance model exists to prevent.

**Replacement wording:**
> - **Price Verification's Engineering Specification exists but still flags an open item.** The specification does not resolve how an imprecise or approximate charged price should be handled — this remains an explicit, undecided gap in the canon. Building input-handling logic that silently picks a resolution (rounding, requiring exact figures, accepting any input) would be the implementation, not the specification process, closing a gap it was never authorized to close.

**Reason:** the original risk — presentation work outrunning a nonexistent specification — no longer applies and would be inaccurate to leave standing. But removing the entry outright would understate what's still genuinely unresolved: the specification, consistent with the Screen Specification Template's own citation-only rule, would have flagged the imprecise-price gap rather than closing it. The risk is updated to reflect its current, narrower shape rather than deleted.

---

### Change 4

**Section:** Recommended Build Order (item 4)

**Existing wording:**
> 4. **Verification Module**: Price Verification, scaffolded at the domain layer only until its Engineering Specification exists; presentation deferred (see Risks).

**Replacement wording:**
> 4. **Verification Module**: Price Verification, domain and presentation layers built together directly from its now-complete Engineering Specification — the same domain-then-tests-then-presentation sequence already used for every other screen, not a split milestone.

**Reason (why this changes scope but not sequencing):** the domain-only split existed for exactly one reason — the specification didn't exist, so presentation work would have meant inventing unstated detail. That reason is gone. Nothing else about this item changes: it still sits at position 4, still depends on the catalog repository, and still precedes Recommendation and Comparison. Only what's *included* in the milestone changes — from domain-only to the full screen — not *where* it falls in the sequence.

---

## Document 2: Implementation Bootstrap Plan

### Change 5

**Section:** M6 (title, Objective, Definition of Done)

**Existing wording:**
> ### M6 — Price Verification (Domain Layer Only)
> **Objective:** the domain logic for verification is real and tested; presentation is deliberately deferred.
> **Deliverables:** `VerifyPrice` use case; `VerificationDelta`/`VerificationResult` entities; the three-way confidence distinction (Section 6 of the Price Verification Screen Contract) implemented and tested.
> **Definition of Done:** domain-level tests pass; **no Price Verification screen/widget is built**, since its Engineering Specification doesn't exist yet — this milestone stops deliberately short of presentation.

**Replacement wording:**
> ### M6 — Price Verification
> **Objective:** the full Price Verification screen — domain and presentation — is implemented directly from its now-complete Engineering Specification.
> **Deliverables:** `VerifyPrice` use case; `VerificationDelta`/`VerificationResult` entities; the three-way confidence distinction (Section 6 of the Price Verification Screen Contract); the Price Verification screen itself, per its Engineering Specification, reusing the `ExplanationPanel` and `ConfidenceBadge` widgets first built in M5.
> **Definition of Done:** domain-level tests pass; every Acceptance Criterion in the Price Verification Engineering Specification has a corresponding passing test; the specification's flagged gap — handling of an imprecise or approximate charged price — is represented as an explicit Recovery State in the UI, never silently resolved by a default input rule.

**Reason (explaining why domain + presentation now belong in one milestone):** this milestone was split into "domain only" specifically because building presentation without a specification would have meant the engineering team inventing unstated UI/behavioral detail — the exact invention the project's governance model exists to prevent. That blocking condition applied to the *absence* of a specification, not to Price Verification's complexity or its place in the build order. Every other screen with a complete specification (Home, Beer Detail, Recommendation, Comparison) already gets domain and presentation built within a single milestone; Price Verification was the one exception, and it was an exception created entirely by the missing specification. Now that the specification exists, the same reasoning already applied to every other screen applies here, and keeping domain and presentation artificially split would be maintaining a distinction the underlying cause for no longer justifies.

---

### Change 6

**Section:** M6 (Dependencies, Estimated complexity)

**Existing wording:**
> **Dependencies:** M2.
> **Estimated complexity:** S (domain-only).

**Replacement wording:**
> **Dependencies:** M2, M5 (for the shared `ExplanationPanel` and `ConfidenceBadge` widgets, reused rather than rebuilt).
> **Estimated complexity:** S–M.

**Reason:** this is the one genuine planning consequence of folding presentation into M6 (Change 5) — Section 7 of the Implementation Architecture already establishes that `ExplanationPanel` and `ConfidenceBadge` are shared, built once, and reused rather than reimplemented per screen; those widgets are first built in M5. A milestone that now includes presentation work using those widgets has a real dependency on M5 that a domain-only milestone never had. This is the direct, mechanical consequence of Change 5, not a new decision — the shared-widget rule already existed; only the point at which Price Verification's milestone reaches it has changed. Complexity moves from S to S–M to reflect the added presentation scope, consistent with the S–M notation already used for the comparably-scoped M4 (Home).

---

### Change 7

**Section:** 6. Recommended First Screen: Home (justification point 2)

**Existing wording:**
> 2. **Its Engineering Specification is complete**, unlike Price Verification's. Building ahead of a written specification is exactly the invention this project's governance model exists to prevent (see M6 above); Home carries no such risk.

**Replacement wording:**
> 2. **Its Engineering Specification is complete** — as, now, are Price Verification's, Beer Detail's, Recommendation's, and Comparison's. Specification-completeness no longer distinguishes Home from the alternatives; Home remains the right starting point for the reasons in points 1, 3, and 4 below, not because it is uniquely spec-complete.

**Reason:** the original justification rested partly on a contrast — Home was spec-complete when Price Verification wasn't. That contrast is no longer true, since every canonical screen now has a complete specification. The recommendation to build Home first does not change (points 1, 3, and 4 — sole entry point, lowest complexity, unblocks downstream milestones — are untouched and remain sufficient on their own), but stating a now-false contrast as part of the justification would misrepresent why Home is still correct.

---

### Change 8

**Section:** 6. Recommended First Screen: Home ("Explicitly not recommended first")

**Existing wording:**
> **Explicitly not recommended first:** Recommendation (highest reasoning complexity — build order in Section 5 already sequences it after the foundation is proven) and Price Verification (no Engineering Specification yet — see M6).

**Replacement wording:**
> **Explicitly not recommended first:** Recommendation (highest reasoning complexity — build order in Section 5 already sequences it after the foundation is proven) and Price Verification (now fully specified, but its presentation layer depends on shared widgets not built until M5 — see M6).

**Reason:** Price Verification is no longer excluded from early implementation because its specification is missing. It is still not the *first* screen to build, but for a structural reason that was always true and is now the operative one: its presentation work depends on shared widgets (`ExplanationPanel`, `ConfidenceBadge`) that don't exist until M5, and Home remains the product's sole mandatory entry point regardless of any other screen's specification status.

---

## Summary of What Did Not Change

- Milestone numbering and overall sequence (M0–M9) are unchanged. Price Verification stays at M6, in the same position relative to Discovery (M4–M5) and Recommendation (M7).
- The recommendation that **Home** be the first screen implemented is unchanged, and rests on the same three surviving justifications (sole entry point, lowest complexity, unblocks downstream work) it always did.
- The two carried-forward canonical ambiguities and the Beer Detail → Recommendation navigation inconsistency are untouched — none of them were resolved by the Price Verification specification's arrival, and none are addressed by this patch.
- The imprecise-charged-price gap is preserved as an open item throughout — narrowed in scope (from "no spec exists" to "the spec exists and still flags this"), never closed.
