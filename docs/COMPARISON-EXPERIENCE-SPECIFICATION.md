# Comparison Experience Specification

*A build specification for the Comparison experience, produced by the same methodology as Beer Detail and Price Verification: the real Flutter tree searched directly for an implementation, the canonical Comparison Screen Contract (`docs/architecture/current/14-Comparison-Screen-Contract.md`) read in full, the existing Engineering Screen Specification (`docs/engineering/specifications/Comparison-Screen-Specification.md`) read in full, the Navigation Contract read in full, Generation 1's own Compare screen read in full, and Decision Engine 2.0 (Part 5), Interaction Model 2.0 (Part 5 and its consolidated cross-cutting sections), the Product Definition Document, the Conversation Model, the Beer Knowledge Model, and the Domain Model all searched directly for every Comparison-relevant passage. Because no real implementation exists, this document is, by necessity, the frozen canon translated directly into build terms — every requirement is cited, and every place canon is silent is named as implementation guidance rather than filled by invention.*

---

## 0. Ground Truth Statement

**No canonical Comparison implementation exists anywhere in this codebase.** `lib/features/compare/screens/compare_screen.dart` is the only file with "compare" in its name, and it is Generation 1 code, structurally incompatible with the canon in a way worth stating precisely rather than just noting its existence — see §18. It is reachable only from the *other* dead Generation 1 screen, `lib/features/home/screens/home_screen.dart` (already identified as unreachable dead code in the Beer Detail Experience Specification, §0) — never from `app.dart`, never from `ValueBrewNavigator`, never from the real, shipped `discovery/presentation/home_screen.dart`. There is no live code path to a Comparison screen of any kind in the running app today.

**The canonical documentation, by contrast, is unusually complete for an unbuilt screen.** Unlike Price Verification (§0 of that specification, where the referenced Engineering Screen Specification turned out not to exist), Comparison's Engineering Screen Specification is real, present in the repository, and its own Document Notes state its own status honestly: fourteen UI elements, six states, and every validation rule fully specified for the two-candidate case, with exactly one large, explicitly self-reported open item. Four independent canonical documents — the Screen Contract (§11), the Engineering Specification (§10, §13), Decision Engine 2.0 (Part 5's own flagged gap), and Interaction Model 2.0 (its own flagged gap) — converge on **the identical open question, described in nearly identical language each time**: none of the tie-breaker, Trade-off, or Tie Disclosure logic anywhere in canon has a defined generalization beyond exactly two candidates. This is not a discovery made here; it is the single most consistently, repeatedly, and deliberately flagged gap in the entire canonical architecture, and this document carries it forward rather than attempting to resolve it (§14, §21).

Because there is no shipped code, every section below is built from direct citation to frozen canon, marked **[Canonical Requirement]** where a MUST/MUST NEVER rule governs it, and **[Implementation Guidance]** where canon is deliberately silent and a build choice is still needed.

---

## 1. Complete User Journey **[Canonical Requirement, currently unreachable]**

Per the Navigation Contract (§3, §4, §6), Comparison has three legal entry paths: **Recommendation → Comparison** (a surfaced Trade-off or Tie, richer treatment invited), **Beer Detail → Comparison** (an explicit signal of openness to alternatives), and **Home → Search/Browse Results → Comparison** (a multi-select), the last of which the Navigation Contract itself admits it cannot fully specify since Search/Browse has no Screen Contract at all (§1, §6). All three are unreachable today for compounding reasons: Comparison itself isn't built, and two of its three entry surfaces (Recommendation's Trade-off/Tie hand-off action, and Search/Browse entirely) aren't built either. Only Beer Detail's side already has a working, canon-shaped predecessor — the "Verify price" pattern on the real Beer Detail screen shows exactly what a "Request Comparison" action would look like once added, though no such action exists there today (confirmed directly in the Beer Detail Experience Specification's own component inventory — no Comparison hand-off button exists in the real code).

Exit is symmetric and precise (Navigation Contract §6, §12): to Beer Detail for one named candidate (carrying only that SKU), to Price Verification for one named candidate (carrying only that SKU, direct edge), or back to Recommendation on a constraint refinement — explicitly a **hand-back, never a restart**, carrying the current candidate set and Preference Summary forward intact. One asymmetry is worth stating precisely because it's easy to assume otherwise: **Comparison → Price Verification is a direct edge; Price Verification → Comparison is not**, in either a system-initiated or a person-initiated form (Navigation Contract §3, §10) — a person leaving Price Verification who wants to return to a comparison must route back through Beer Detail. This is not a gap; it is the direct, correct consequence of Price Verification's own "never escalates" constraint, applied consistently at the navigation-graph level, not only at the reasoning level.

---

## 2. Screen States **[Canonical Requirement]**

Directly from the Screen Contract's own State Machine (§8), with the Engineering Specification's own state-mapping table (§9) reused rather than re-derived:

| State | Entry | Exit |
|---|---|---|
| **Initial** | Arrival with a named candidate set (≥2) | The set is evaluated at least once |
| **Evaluating** | Every time the set or its inputs change, including first arrival | The tie-breaker rule and trade-off logic are applied |
| **Clarifying** | One further question would resolve genuine ambiguity | The question is answered — never a second instance, ever |
| **Resolved** | A winner, Trade-off, or Tie has been determined | Selection, tie acceptance, "why," refinement, or hand-off |
| **Recovering** | One named candidate can't be resolved | The candidate is removed or replaced, scoped to that candidate only |
| **Completed** | Explicit selection or tie acceptance | Terminal |

**One property worth stating with the same emphasis the canon itself gives it:** a Tie Disclosure is a **Resolved**-state outcome, never a Recovering condition (Screen Contract §3, §11; Engineering Spec §9's own explicit correction against conflating the two). And per the Domain Model's own precise statement about the `Comparison Result` entity (§264–265): this screen **never has a "no result exists yet" shape** the way Recommendation's does, because Comparison is never entered without at least two already-resolved candidates to begin with — there is structurally no equivalent of Recommendation's blank Initial-before-any-input screen here.

---

## 3. Visual Hierarchy & Layout **[Implementation Guidance — canon deliberately silent]**

The Engineering Specification states this directly and is not contradicted anywhere else in canon: *"How these sections are visually arranged is a design decision. Intentionally left unspecified by the Canonical Architecture."* What canon does fix is content, not layout: the Candidate Set Display must show every candidate's identity and value together, never partially (§5), and a Trade-off must always be presented with its constituent facts alongside it, never split across separate views (§6, §10 Validation Rules). Any layout — side-by-side columns, a stacked list, a table — satisfies this as long as those adjacency requirements hold. See §18 for what Generation 1's own layout instinct offers here.

---

## 4. Components **[Canonical Requirement for content; Implementation Guidance for widget shape]**

The Engineering Specification's own Section 7 names exactly fourteen permitted UI elements, and states plainly: *"No element beyond these fourteen is permitted."* Restated here at the category level rather than duplicated in full: Candidate Set Display; three mutually-exclusive Comparison Result variants (Winner / Trade-off / Tie); Preference Summary Context Display; the single Clarifying Question; Select Winner and Accept Tie as two **distinct, never-conflated** actions; Ask "Why"; Add/Remove Candidate; Refine Constraint; per-candidate Request Beer Detail and Request Price Verification; and the Unresolvable Candidate Recovery Display.

**No dedicated `ExplanationPanel` or `ConfidenceBadge` widget should be built for this screen specifically.** Both were planned in the Flutter Implementation Architecture as shared components but were never actually built anywhere in the app — confirmed by direct grep across `lib/` in both the Recommendation Widget Specification and the Price Verification Experience Specification, with zero matches. Every real screen inspected in this series renders its Explanation and confidence content as plain, differently-styled `Text`. Comparison's two-layer confidence requirement (§13) is the one place this pattern will be pushed hardest — but the existing, working precedent (Price Verification's fixed-sentence confidence disclaimer, already confirmed to satisfy an equally strict three-way distinction without any dedicated component) suggests plain text, structured into two clearly separate sentences or blocks, is sufficient here too, not a reason to finally build the shared widgets the rest of the app has consistently done without.

---

## 5. Interactions **[Canonical Requirement]**

The eight canonical actions (Screen Contract §7; Engineering Spec §8), stated at the level a Flutter engineer needs, not re-derived: view the comparison; answer the single clarifying question, if posed; select a winner (only valid when the result is a Winner or a Trade-off — **never** the mechanism for resolving a Tie); accept a tie (a distinct action, only valid when the result is a Tie); ask "why" (re-surfaces the existing Explanation, generates nothing new); add or remove a candidate (removal is only offered when ≥2 candidates would remain afterward — a precondition on the control itself, not a post-hoc correction); refine a constraint (always hands back to Recommendation, never resolved in place); and request Beer Detail or Price Verification for one named candidate.

**Interaction modality — tap, swipe, long-press, or otherwise — is nowhere specified in canon** (Engineering Spec §8, citing Feature Inventory §1 and the Review Guide §2). **[Implementation Guidance]** ordinary Material tap targets, consistent with every other real screen in this app (plain `TextButton`/`ElevatedButton`/`ChoiceChip` — no screen anywhere in the codebase uses swipe or long-press for a primary action), are the reasonable default absent any canonical signal otherwise.

---

## 6. Loading, Empty, and Error States

**Loading [Implementation Guidance]:** no code exists to inspect, but the established pattern across every other real screen in this app — `SkeletonBox` composed into a screen-specific placeholder function, never a generic spinner — is the only precedent this codebase has, and nothing in canon suggests deviating from it. A two-column skeleton, one per candidate slot, would directly parallel Generation 1's own `_compareColumnSkeleton()` shape (§18) — this specific piece of Gen1's approach is safe to reuse precisely because it concerns only a loading placeholder's shape, not any judgment content.

**Empty [Canonical Requirement — does not apply]:** per §2, Comparison structurally cannot have a "no candidates yet" empty state — it is never entered without ≥2 already-resolved candidates. Any build that shows an in-screen "pick your beers" empty state, the way Generation 1's did, would be reintroducing a state canon does not permit this screen to have (§18).

**Error [Canonical Requirement]:** exactly one recovery condition exists, per-candidate, never whole-screen (§8, §11) — see §7.

---

## 7. Recovery Flows **[Canonical Requirement]**

**Insufficient differentiation** is not a failure state at all — it resolves directly into the Resolved-state Tie Disclosure, once the shared tie-breaker rule and the single permitted clarifying question have both been exhausted (§11; Engineering Spec §13, restated precisely to avoid the natural but incorrect assumption that a tie "feels like" a recovery). **Unresolvable candidate** is the screen's one genuine Recovering condition, and it is explicitly scoped to the one affected candidate, never presented as the whole comparison failing (§8, §11). The canon is specific about tone here in a way worth citing directly rather than paraphrasing: *"inform the person plainly and invite removal or replacement of that one candidate; never silently drop it without saying so."* The remaining resolvable candidates and any established Preference Summary stay intact throughout (§11 Progress Preservation) — matching the same "recovery resolves in place, never a screen transition" pattern the Navigation Contract states as the general rule across every screen with its own contract (§11).

---

## 8. Accessibility **[Implementation Guidance, deferred]**

**Intentionally left unspecified by the Canonical Architecture**, identical finding to every other screen in this series — no accessibility standard exists anywhere in canon. One canon-grounded constraint is worth stating precisely for whenever a standard exists (Engineering Spec §11): the requirement that per-candidate and result-level confidence remain visibly, structurally distinguishable is **a canonical content requirement, not a styling suggestion** — whatever accessible presentation is eventually built must preserve that distinction by whatever means the standard requires, not rely on visual proximity or color alone, which would not survive, e.g., a screen-reader pass.

---

## 9. Explanation Behavior **[Canonical Requirement]**

The Recommendation Framework's Explanation structure is reused directly, without modification, applied to the Comparison Result rather than a Full Recommendation (§6, §9) — same discipline, same "computed together with its conclusion, never derived afterward" guarantee Interaction Model 2.0 extends by direct, flagged inference to Comparison's Trade-off Explanation specifically (Interaction Model 2.0, Part 5 cross-reference). A Trade-off's Explanation is never separated from the constituent facts that produced it — shown together, always, never requiring the person to piece the reasoning together themselves across two views.

---

## 10. Copy **[Canonical Requirement]**

Directly from the Engineering Specification's own Copy Requirements (§12), restated at full weight since this is one of the most heavily-guarded distinctions in the entire canon:

- **"Better" and "Recommended" must never be used interchangeably.** A winner is described as better than the other named candidates, on stated grounds, *within the named set* — never "the recommended beer," never "the best beer available."
- **Trade-offs are framed against what the person actually said, never against an assumed preference.** Canonical example of correct framing, quoted directly: *"this is different from your stated style, but meaningfully better value, since you didn't set a hard style limit."* Canonical example of forbidden framing, quoted directly: *"this is objectively the smarter pick."*
- **A tie is stated plainly as a tie** — *"these are equivalent on everything you've told me matters"* — never softened, apologized for, or presented as an incomplete answer, matching the identical Plain-Tie shape the Conversation Model already establishes for Recommendation and generalizes explicitly to Comparison (Conversation Model, Part 2 "Comparison" and Part 3 "The Plain-Tie shape").
- **No invented numerical precision** in confidence statements or trade-off descriptions.
- **Forbidden Lexicon terms:** "Score" or "Rating," anywhere. "Alternative" used as an unqualified catch-all in place of the specific terms Trade-off or Comparison. "Verify," used loosely, outside Price Verification's own scope.

Directly relevant given how the Lexicon violation has recurred twice already in this series (Recommendation's "Value Score of Y," Beer Detail's "Value score: N"): **any future Comparison implementation must not display a bare `valueScore` number**, using `valueVerdict.displayLabel` and, where available, `styleStanding.displayLabel` instead — exactly the fix already applied to the other two screens, and exactly the pattern Generation 1's own Compare screen violates (§18).

---

## 11. Typography, Spacing, Iconography **[Implementation Guidance]**

Nothing to cite from a real implementation. `AppSpacing` tokens (`xs/sm/md/lg/xl`) are the only established app-wide resource and should be used from the start here, unlike Recommendation's screen, which the Widget Specification found only partially migrated — there's no legacy code on this screen to migrate away from, so there's no reason to ever introduce a raw `EdgeInsets` value in the first build. No icon usage is established anywhere else in the app's real screens beyond default Material affordances; nothing in canon calls for icons here either.

---

## 12. Information Priority & Trust Signals **[Canonical Requirement]**

The ordering in §5 of the Screen Contract is exact and load-bearing: Primary (the Comparison Result) sits above Supporting (per-candidate Identity and Alcohol-Adjusted Value, "shown together — the result means nothing without both"), which sits above Contextual (the Preference Summary, so the person can see what was actually weighed). The single most important trust signal this screen carries — repeated with near-identical wording across the Screen Contract, the Engineering Specification, and Product Definition — is the **bounded-claim discipline**: "Comparison can conclude that Beer A is better than Beer B. It can never claim to have recommended the best beer in existence, because it never looked past the candidates it was handed." This is not a copy nicety; it's named directly in Product Definition's own Fundamental Truths as a trust-preservation mechanism ("a comparison between two named beers is not a claim about every beer in existence, and pretending otherwise erodes trust the moment someone finds the exception").

---

## 13. Confidence Presentation **[Canonical Requirement — the load-bearing distinguishing property of this screen]**

Two distinct layers, never merged, stated with the same precision across every canonical source consulted: **per-candidate confidence** (uniformly high, identical in kind to Beer Detail, since each candidate's own facts are Verified/Computed) and **result-level confidence** (which "can be genuinely low even when every underlying fact is certain," whenever the differentiator between candidates is a Soft Preference rather than a Hard or Strong one). This second layer is the one place Comparison's confidence model is genuinely richer than Beer Detail's uniform-high treatment and genuinely different in shape from Recommendation's single confidence-through-explanation approach — it is its own, distinct thing, not a restatement of either. The Engineering Specification's own accessibility note (§8 above) already flags the consequence: this distinction must never collapse into visual proximity alone.

---

## 14. Edge Cases

1. **Three or more candidates, and non-transitive results.** **[Product Decision Required — see §21]** The flagship, unanimously-flagged gap: every tie-breaker, Trade-off, and Tie Disclosure rule anywhere in canon assumes exactly two candidates. Decision Engine 2.0's own framing is precise about why this can't be quietly deferred as "just a Comparison problem": the same gap is reachable from inside Recommendation's own Core reasoning the instant three candidates tie on a Soft input, independent of whether the Comparison surface is ever entered at all (Decision Engine 2.0, Part 5's flagged gap; Interaction Model 2.0's identical flagged gap).
2. **A candidate becomes unresolvable mid-comparison.** Fully resolved by canon — see §7.
3. **The clarifying question is answered and the result is still a tie.** Fully resolved, and worth restating precisely because it reads like a failure and isn't one: this is exactly the honest sequence that legitimately produces a Tie Disclosure, not a sign anything went wrong (Screen Contract §3, §6, §11).
4. **A person drills into Beer Detail for one candidate mid-comparison.** Fully resolved: does not alter comparison state; the person returns to the same, unchanged comparison, or hands off from Beer Detail elsewhere (§6).
5. **A refined constraint would have excluded a named candidate had it been known from the start.** Fully resolved as a matter of ownership: Comparison never re-filters the set against a new constraint itself — refining always hands back to Recommendation, and any re-evaluation happens there, on re-entry, not here (§7; Information Architecture §3).
6. **Removing a candidate down to exactly one.** Fully resolved: removal is only offered while ≥2 candidates would remain afterward — a precondition on the control, never a state to recover from after the fact (§7).

---

## 15. Offline Behavior **[Implementation Guidance]**

**Intentionally left unspecified by the Canonical Architecture**, identical finding to every other screen in this series.

---

## 16. Data Dependencies **[Canonical Requirement for content; Implementation Guidance for wiring]**

Beer Knowledge Base facts for every named candidate; Style Benchmark, where available, for relative standing (§3, §9). Comparison never re-derives a SKU's price, ABV, or size independently — "it consumes exactly what Beer Detail already owns" (§6). **[Implementation Guidance]** the existing `catalog_lookups.dart` functions (`resolveSku`, `resolveBeer`, `resolveStyle`, `resolveBenchmark`, already shared across Beer Detail and Price Verification) are the direct, obvious dependency for a future implementation — no new lookup layer is implied by anything in canon.

---

## 17. Analytics Events (Proposed, Not Yet Built)

Directly from the Engineering Specification's own placeholder list (§14), names only: screen viewed (by candidate-set size); clarifying question presented/answered; Comparison Result produced, split by winner/trade-off/tie; winner selected; tie accepted; explanation requested; candidate added/removed mid-comparison; constraint refined (hand-back); Beer Detail/Price Verification requested per candidate; unresolvable-candidate recovery shown. Consistent with every other screen in this series, no `AnalyticsSink` wiring is proposed as anything but a name list.

---

## 18. Generation 1 — What to Reject, What to Recover

Generation 1's `CompareScreen` (`lib/features/compare/screens/compare_screen.dart`) is real, complete, working code — 197 lines, unit-testable, not a stub — but it answers a fundamentally different, much smaller question than canonical Comparison does. It is a **read-only, side-by-side fact display for two freely-chosen beers**, with its own doc comment stating its scope honestly: *"Deliberately minimal — no new value scoring happens here, nothing is persisted, and there is no recommendation of which beer to pick."* The ValueBrew Experience document's own generational note, written earlier in this project, already reached the correct verdict independently, and this document confirms it stands: *"the clearest case in the whole product's history of a rebuilt idea actually getting better, not just getting rebuilt."*

**Reject, explicitly, and do not carry forward into any future build:**
- **The in-screen `DropdownButton<Beer>` candidate picker.** This is not a minor implementation detail — it is a direct structural violation of the Screen Contract's own MUST NEVER clause: *"Search the catalog for candidates that weren't already provided."* Canonical Comparison is entered with its candidate set already named by whatever screen sent it there; it never presents an open, full-catalog picker of its own. Any future build must receive its candidate set as constructor/route arguments, the same way Beer Detail and Price Verification receive a `skuId`, never as in-screen selection state.
- **The complete absence of a winner, Trade-off, or Tie.** Already correctly identified and rejected by The ValueBrew Experience document; restated here because it's the single largest capability gap between the two.
- **The bare `'Value score: ${sku.valueScore}'` numeric display** inside `buildBeerColumn` — the same Lexicon violation already found and fixed twice elsewhere in this series (§10). Must not be recovered even if the surrounding column layout is.
- **The "Select Beer A / Beer B to compare" empty-column hint state.** Structurally impossible under canon (§2, §6) — Comparison is never entered without ≥2 already-resolved candidates, so there is no canonical moment where an unpopulated candidate slot would ever need to be shown.
- **No Explanation, no confidence content, no hand-off actions of any kind** (no Beer Detail drill-down, no Price Verification link, no back-to-Recommendation refinement path) — the screen is a dead end with no exits besides system back. None of this is a foundation to build on; canon's entire hand-off graph (§1) has no precedent in this file at all.

**Worth recovering, narrowly, as a non-binding layout instinct only — not as settled canon:**
- **The two-column, side-by-side visual arrangement itself** (`Row` of two `Expanded` columns, one per candidate), each showing that candidate's identity and facts together. This satisfies the Screen Contract's own adjacency requirement (Beer Identity and Alcohol-Adjusted Value "shown together... never partially") about as directly as a layout can, and there's no reason to invent a different shape from scratch. This is explicitly **[Implementation Guidance]**, not canon — the Canonical Screen Specification Template states plainly that visual arrangement is a Design Decision, and nothing here elevates Generation 1's specific choice above any other layout that satisfies the same content-adjacency rule.
- **The screen-specific loading-skeleton shape** (`_compareColumnSkeleton()`, mirrored per column) — safe to reuse as a starting shape precisely because a loading placeholder carries no judgment content and can't violate any of the rules above.

Everything else about Generation 1's Compare screen — its selection model, its complete lack of synthesis, its numeric Value Score display, its dead-end navigation — should remain rejected, not revisited, consistent with how firmly The ValueBrew Experience document already closed this question.

---

## 19. Implementation Notes

No code exists to correct, so this section states build guidance rather than deltas. A future implementation should: accept its candidate set as constructor arguments (never an in-screen picker, per §18); reuse `ErrorStateView` and a screen-specific `SkeletonBox` composition, matching every other real screen's established pattern; render the Explanation and both confidence layers as structured plain `Text`, not a new shared widget (§4); use `AppSpacing` tokens from the start; and route every navigation-triggering action through new, dedicated `ValueBrewNavigator` methods (`comparisonToBeerDetail`, `comparisonToPriceVerification`, `comparisonToRecommendation`, and the not-yet-existing `recommendationToComparison`/`beerDetailToComparison` entry methods), following the exact one-method-per-edge pattern every existing `ValueBrewNavigator` method already uses — never a generic `Navigator.push` call the way Generation 1's dead screens use throughout.

---

## 20. Explicit Non-Goals

No resolution of the 3+-candidate gap invented here (§14, §21 — a Product Decision, not an implementation choice). No shared `ExplanationPanel`/`ConfidenceBadge` component introduced on this screen's account (§4). No in-screen candidate picker of any kind, at any point, ever (§18). No Search/Browse Results screen built as a side effect of unblocking one of Comparison's entry paths — that remains its own, separately-scoped, larger canonical gap, untouched by this document.

---

## 21. Items Requiring a Decision — Consolidated

**Product Decision Required:**
1. **How comparison logic generalizes beyond exactly two candidates**, including non-transitive results (§2, §14). This is the single most heavily and consistently flagged open item in the entire canonical architecture — named identically in the Screen Contract, the Engineering Specification, Decision Engine 2.0, and Interaction Model 2.0 — and it blocks not only Comparison's own 3+-candidate path but also a reachable branch of Recommendation's own Core reasoning (a 3+-way Soft-input tie), independent of whether Comparison is ever entered at all.

**Design Decision Required:**
2. The exact visual arrangement of Comparison's six sections (§3) — canon fixes content adjacency, not layout; Generation 1's side-by-side column instinct is a reasonable non-binding starting point (§18), not a settled answer.
3. Interaction modality for every action in §5 — tap, selection, or otherwise (§5).

**Engineering Decision Required:**
4. Establishing a canonical accessibility standard before any screen-specific accessibility work begins here — deferred, non-blocking, identical in nature to the same item already raised for Beer Detail and Price Verification (§8).
5. Adding the new `ValueBrewNavigator` methods this screen requires (§19) once building actually begins — mechanical, not ambiguous, but real work with no precedent to copy from since no edge into or out of Comparison exists in the navigator today.

Every other requirement in this document — the fourteen UI elements, the six states, the copy rules, the dual confidence layers, the Recovery behavior, the hand-off contracts — is already fully and unambiguously specified by the frozen canon, and a future implementation can be built directly from this document with no further interpretation needed on any of those points.
