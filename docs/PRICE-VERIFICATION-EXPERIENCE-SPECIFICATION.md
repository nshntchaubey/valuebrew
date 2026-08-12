# Price Verification Experience Specification

*A build specification for the Price Verification experience, produced by the same methodology as Beer Detail: the real Flutter implementation (`lib/features/price_verification/`) inspected directly, the canonical Price Verification Screen Contract (`docs/architecture/current/15-Price-Verification-Screen-Contract.md`) read in full, the Navigation Contract (`docs/architecture/current/16-Navigation-Contract.md`) read in full, Generation 1 searched for an equivalent (none exists), and the referenced Engineering Screen Specification searched for directly — with a materially important result reported in §0. This document documents the implementation as it exists. Where the implementation already satisfies canon, that is stated plainly rather than treated as an opportunity to propose a change.*

---

## 0. Ground Truth Statement

**No Price Verification Engineering Screen Specification exists in this repository, despite a frozen document claiming otherwise.** `docs/engineering/implementation/22-Repository-Sync-Patch-Price-Verification.md` is written entirely around the premise that "the Price Verification Engineering Screen Specification, previously absent, now exists and is part of the frozen Engineering documentation," and it amends the Flutter Implementation Architecture and Implementation Bootstrap Plan on that basis — removing Price Verification's "domain-only, presentation deferred" restriction, folding presentation into M6, and adding an M5 dependency for two shared widgets the specification supposedly requires. A direct search of `docs/engineering/specifications/` — which does contain Home, Beer Detail, Recommendation, Comparison, and even the unbuilt Search/Browse's specifications — turns up **no Price Verification file at all**. This is a real, confirmed inconsistency in the frozen documentation set, not a gap in this search: the patch's own premise is false against the repository as it exists today.

This has a second, compounding consequence. The patch's Change 6 asserts M6 now depends on M5 for two shared widgets, `ExplanationPanel` and `ConfidenceBadge`, "reused rather than reimplemented per screen." A direct grep of `lib/` for both names returns **zero matches** — neither widget was ever built, anywhere in the app, for any screen. This is consistent with what the Recommendation Widget Specification and Beer Detail Experience Specification already found independently for their own screens: every screen in the real codebase renders its explanation and confidence content as plain `Text`, not through a shared component. The patch's stated dependency was never real to begin with.

**This specification treats the actual, shipped `price_verification_screen.dart` as ground truth**, cites the Screen Contract directly rather than the missing specification, and flags the documentation inconsistency itself in §18 rather than either inventing the missing file's contents or silently trusting its claims.

**Generation 1 has no equivalent screen.** A direct search of the archived Generation 1 documents and code for any price-verification concept — "verify," "charged price," "legal price," "MRP check" — returns nothing beyond incidental, unrelated mentions of the word "price." Price Verification is a capability introduced entirely in the canonical rebuild, with no prior generation's design to recover from or contrast against. Unlike Recommendation and Beer Detail, this section of the methodology has nothing to report.

---

## 1. Complete User Journey

Per the Navigation Contract (§3, §4, §6), Price Verification has three canonically legal entry points: **Home → Price Verification**, **Beer Detail → Price Verification**, and **Comparison → Price Verification**. Checking each against what's actually reachable in the running app:

- **Beer Detail → Price Verification** — the only one that exists. Confirmed directly in `ValueBrewNavigator.beerDetailToPriceVerification(skuId)`, wired to the real, shipped `BeerDetailScreen`'s "Verify price" button.
- **Home → Price Verification** — canonically specified (Navigation Contract §6: "Trigger: an explicit verification intent... Ownership: Home"), but **not implemented**. The real `HomeScreen` (`lib/features/discovery/presentation/home_screen.dart`) has exactly two buttons, both routing to Recommendation. Its own doc comment states this plainly and without ambiguity: *"the remaining paths (Search/Browse Results, Price Verification) and states... arrive incrementally... when a real need pulls them in."* This is not a contradiction the way the Beer Detail → Recommendation gap was — it's an honestly self-labeled, deliberate incompleteness already acknowledged in the code itself. Carried forward here as fact, not re-litigated as a new discovery.
- **Comparison → Price Verification** — canonically specified, but Comparison itself is not built anywhere in the app. Not reachable for the same already-documented reason it wasn't reachable from Beer Detail.

**In practice, today, exactly one path into this screen exists**: arriving from Beer Detail, having already seen a specific SKU's full facts, and explicitly choosing to check what was actually charged for it. The journey ends (Screen Contract §7, §8) either by acknowledging the result and leaving, or by handing back to Beer Detail for broader context — the Navigation Contract's own rule that the charged price is never carried along on that hand-off (§12) is enforced exactly: `priceVerificationToBeerDetail` passes only `sku.id`.

---

## 2. Screen States (Canonical State Machine → Real Code)

| Canonical state | Real code condition | Notes |
|---|---|---|
| **Awaiting Price** | Catalog loaded, SKU resolved, `_result == null` | The `TextField` and "Verify price" button are always visible in this state; no separate "request" affordance exists beyond the input itself. |
| **Verifying** | The synchronous instant inside `_verify()` | No distinct visual state — matches the same finding already made for Recommendation's own synchronous evaluation gap: a local, synchronous computation over already-loaded data needs no loading treatment of its own. |
| **Recovering** | `catalogAsync` is `AsyncError`, **or** `sku == null \|\| beer == null` after load, **or** `chargedPrice == null` after a parse attempt | Three real conditions map onto this one canonical state — see §7 for why the third is a meaningfully different kind of "Recovering" than the canon's own named failure condition. |
| **Completed** | Not a distinct visual state | Reached by acknowledgment (simply not re-verifying) or by the "View Beer Detail" hand-off; no special rendering marks this moment, consistent with the Screen Contract's own terminal-state rule. |

---

## 3. Visual Hierarchy & Layout

`Scaffold` → `AppBar(title: "Price Verification")` → body — the literal screen name, not the beer's name, exactly matching the pattern already established and confirmed correct for Beer Detail.

Body: `SingleChildScrollView` → `Padding(AppSpacing.md)` → `Column(crossAxisAlignment: stretch)` — note this screen uses `stretch`, not Beer Detail's `start`, so the `TextField` and `ElevatedButton` span the full width; a small, sensible, already-correct difference given this screen's primary action is data entry, not reading. In order:

1. **Identity + Legal Price** — beer name (`titleLarge`), Legal Price as plain body text.
2. **Charged-price input** — a `TextField` with a numeric decimal keyboard and an inline `errorText`.
3. **The single action** — `ElevatedButton`, "Verify price."
4. **Result block** (only once `_result != null`) — verdict (`titleMedium`), the Explanation, and a fixed, italicized confidence-disclaimer paragraph.
5. **Hand-off** — a `TextButton`, "View Beer Detail," always present regardless of whether a result exists yet.

This ordering satisfies the canon's own Information Composition (Screen Contract §5) directly: Progressive content (the price request) sits immediately after the Supporting facts it needs (Legal Price), the Primary object (the Verification Result) appears only once it exists, and its Explanation and Confidence are attached in the same breath — not on a separate screen, tab, or delayed reveal.

---

## 4. Components

**Reused:** `ErrorStateView` (twice — see §6) and `SkeletonBox` (composed into `_priceVerificationSkeleton()`), matching the identical pattern already established for Beer Detail and Recommendation.

**No dedicated widgets exist** for the verdict, the Explanation, or the confidence disclaimer — all three are plain `Text` widgets, differing only in `TextTheme` role and italics. This is consistent with the confirmed absence of `ExplanationPanel`/`ConfidenceBadge` noted in §0: this screen was never blocked by their absence, because it never needed them — the three-way confidence distinction the Screen Contract requires (§6) is achieved entirely through **plain sentence structure**, not a component. **This already satisfies canon** — the Screen Contract nowhere requires a specific visual component for confidence communication, only that the three dimensions not be collapsed into one figure. They aren't: identification and legal-reference confidence are stated together as a fixed sentence ("Beer identity and the legal price are both Verified Facts — high confidence"), and the outcome's own weaker ceiling is stated separately, immediately after, in its own sentence ("This result reflects exactly what you reported; it isn't independently checked..."). No change is proposed here.

---

## 5. Interactions, Gestures, Transitions, Animations

| Canonical action (§7) | Real affordance |
|---|---|
| View verification, once the SKU is known | Passive, on arrival. |
| Provide the charged price | `TextField` + "Verify price" `ElevatedButton`. |
| Correct a previously given charged price | **The same `TextField` and the same button** — editing the text and pressing "Verify price" again re-runs `_verify()` with the new value, replacing `_result`. This directly satisfies the canon's MAY clause ("recomputing without restarting the interaction") **without any dedicated "correct" affordance being necessary** — already resolved, not a gap. |
| Ask "why" | **Not present as a separate action** — the Explanation is always shown inline alongside the verdict the instant it exists, so there is nothing to separately request. This is a stricter, simpler satisfaction of the underlying rule (an Explanation always accompanies its result) than a re-surfacing "why" button would be, not a missing feature. |
| Request Beer Detail | The "View Beer Detail" `TextButton`. |

**Gestures:** none beyond standard scroll and back navigation, identical finding to Beer Detail.

**Transitions/Animations:** none beyond the standard `MaterialPageRoute` push/pop; no `AnimatedSwitcher` around the result block's appearance. Consistent with the already-established, correct "no custom animation" convention.

---

## 6. Loading, Empty, and Error States

**Loading** — `_priceVerificationSkeleton()`: identity/price placeholders, then a tall block (56) and a shorter block (40) approximating the input field and button — matching the real layout's shape, per the same discipline already used for Beer Detail and Recommendation.

**Empty** — does not apply as a distinct state; "no result yet" is simply the ordinary Awaiting Price state, not an empty-state placeholder.

**Error** — three real conditions, not two:
1. Catalog fails to load → `ErrorStateView` with retry — a genuine technical failure.
2. SKU doesn't resolve → `ErrorStateView("This beer couldn't be found.")`, no retry — the canon's named "Unresolvable SKU" Recovery State (§11), implemented identically to Beer Detail's own equivalent.
3. The charged price fails to parse → **not** an `ErrorStateView` at all, but an inline `TextField errorText: "Enter a valid price."` This is the right family of treatment (in-place, not a full-screen interruption) for a condition the canon itself calls "the same distinction drawn in the Recommendation contract between an ordinary progressive question and genuine Low-Confidence Response" — i.e., needing the price is normal operation, not failure. But see §7 for what this condition does *not* yet address.

---

## 7. Recovery Flows

The Unresolvable-SKU recovery (condition 2 above) matches Beer Detail's own pattern exactly and needs no further comment — no retry offered, nothing to preserve, consistent with the Screen Contract's own "no prior context on this screen to preserve" language.

**The charged-price parse failure is where this screen's one genuine, substantive gap lives.** The Screen Contract's own Section 11 names an explicitly open canonical question: whether an *imprecise* charged price ("around 110, not sure exactly") should be accepted at all, and if so, how. The real code does not represent this as a distinct condition — `double.tryParse()` either succeeds on an exact numeric string or fails, and every failure (a typo, empty input, or a deliberately approximate answer like "around 110") produces the identical generic message, "Enter a valid price." **This is a live implementation of a default the canon never actually authorized**: by requiring an exactly-parseable number to proceed at all, the code has silently chosen "require an exact figure" — one of the three options the Screen Contract itself lists as undecided ("require an exact figure, accept a range, or handle uncertainty some other way") — without that choice ever having been made as a deliberate decision. This is exactly the kind of implementation-layer invention the project's own Repository Sync Patch warned against in its own words: *"the specification's flagged gap... remains open per the canon's citation-only discipline, and must be represented as an explicit Recovery State... never resolved by inference."* The current code resolves it by inference. **See §18, Product Decision Required.**

---

## 8. Accessibility

**Intentionally left unspecified by the Canonical Architecture**, identical finding to Beer Detail and Recommendation — no accessibility standard exists anywhere in canon, and no explicit `Semantics` wrapping exists beyond Material's own defaults on `TextField`, `ElevatedButton`, and `TextButton`. No new work proposed here for the same reason already given for Beer Detail: a canonical standard should land once, across every screen, not be invented per-screen.

---

## 9. Explanation Behavior

Fully compliant, and worth stating as such rather than proposed as a change: the Screen Contract requires the Recommendation Framework's Explanation structure be reused "directly and without modification, applied here to the verification delta" (§6), always attached in the same breath as the result (§2 MUST, §8 Verifying-state Forbidden clause). `verifyPrice()` constructs the `explanation` string in the exact same computation that produces the `verdict` — the two can never exist independently of each other in the domain model, which is a stronger, more mechanically-enforced guarantee than the canon's own prose requires. No gap here.

---

## 10. Copy

**This screen has no confirmed Lexicon violation** — a materially different finding from both Recommendation and Beer Detail, each of which had one bare-number "Score" violation. Checked directly against the Canonical Interaction Lexicon's forbidden terms (Screen Contract's own citation trail, §9, §13):
- "Legal price" is used correctly and consistently; "correct price" never appears.
- No "Score" or "Rating" language appears anywhere on this screen — there is no value-scoring content here at all, only the three-way verdict.
- "Verify"/"Verification" is used exactly within its own scope, which is this screen's entire purpose — not a loose or borrowed usage the Lexicon would object to.
- The verdict labels themselves ("At the legal price," "Below the legal price," "Above the legal price") are plain, factual, and match the Screen Contract's own three-way classification names directly (§6), with no informal substitute.

**One phrase is worth naming without treating it as a violation:** "This may be an overcharge" (the above-legal-price explanation). The Screen Contract itself uses "overcharge" as ordinary vocabulary throughout ("even when an overcharge is found," §6, §10, §14), so this is canon-sanctioned language, not an invented dramatization — no change proposed.

---

## 11. Typography, Spacing, Iconography

**Typography:** beer name at `titleLarge` (this screen's largest text); Legal Price and the charged-price input share plain body-level presentation; the verdict, once it exists, steps up to `titleMedium` — a deliberate, sensible escalation matching the moment the Primary object actually appears. The confidence disclaimer is set in italics with no other distinguishing treatment — the one hedge-like visual cue this screen uses, and it's applied uniformly to the same fixed sentence regardless of verdict, which is correct: per §6, the *outcome's* confidence ceiling is the same regardless of which of the three verdicts was reached, so a uniform treatment is the right one, not a gap.

**Spacing:** fully `AppSpacing`-token-based throughout (`.md`, `.xs`, `.lg`), matching Beer Detail's already-fully-migrated state, not Recommendation's partially-migrated one. No delta needed.

**Iconography:** none. Consistent with the established minimal-iconography pattern across every real screen in the app.

---

## 12. Information Priority & Trust Signals

This is, by the canon's own account, "the single highest-trust capability in the entire product" (The ValueBrew Experience, Step 6), and the layout matches that weight: the Legal Price is shown before the person is even asked for their own number, so the comparison always has a stated, visible reference point rather than asking someone to report a price against something invisible. The confidence disclaimer is the screen's single most important trust-signal sentence, and it is shown unconditionally alongside every result, every time, regardless of verdict — not only when the news is bad. This directly satisfies the canon's own repeated insistence that a "below" outcome never be dressed up as more certain than an "above" one, or vice versa.

---

## 13. Confidence Presentation

**Fully compliant with the Screen Contract's three-way distinction (§6), and this is worth stating explicitly since the Contract itself flags the *earlier* canonical summary of this screen as too loose.** The real code's fixed disclaimer sentence does exactly what §6 demands: states identification and legal-reference confidence as uniformly high ("Verified Facts — high confidence"), then separately and honestly states the outcome's own weaker ceiling, sourced to the fact that the charged price is self-reported and "isn't independently checked." No blending, no single figure, no visual score. This is one of the more precisely-matched implementations across every screen inspected in this document series so far — **no change proposed.**

---

## 14. Edge Cases

1. **Home → Price Verification, the missing direct entry point.** Already covered in §1: canonically specified, not built, and honestly self-labeled as such in the real Home screen's own doc comment. Not a contradiction to resolve — a scoped, acknowledged future build item.
2. **Comparison → Price Verification.** Not reachable because Comparison itself doesn't exist yet — a pre-existing, already-documented cross-cutting gap, not new here.
3. **The imprecise/approximate charged price.** The screen's one genuine open gap, detailed fully in §7 — the canon leaves the underlying question open, and the real code has silently defaulted to the strictest of the three named options without that default ever being a deliberate decision.
4. **A person edits the charged price after seeing a result, without re-pressing "Verify price."** The stale `_result` remains visible, unchanged, until the button is pressed again — there is no live-recompute-on-keystroke behavior. This is a reasonable, unremarkable implementation choice (verification is an explicit, deliberate act, not a live calculator) and nothing in canon suggests otherwise — **not treated as a gap.**
5. **A person taps "View Beer Detail" before ever entering a charged price.** Permitted by the real code (the button is unconditional) and permitted by canon — the MAY clause for this hand-off has no precondition beyond an already-identified SKU, which this screen always has by the time it's rendering content at all. **Already resolved, not a gap.**

---

## 15. Offline Behavior

**Intentionally left unspecified by the Canonical Architecture**, identical finding to both prior specifications in this series — no offline standard exists anywhere in canon; this screen's only offline-adjacent behavior is inherited unchanged from `catalogProvider`'s own error handling.

---

## 16. Data Dependencies

`catalogProvider`, resolved via the same shared `resolveSku`/`resolveBeer` lookups used by Beer Detail — no separate fetch, no separate repository. `verifyPrice()` (pure Dart, no Flutter dependency) is the screen's only local computation, taking the already-loaded `sku.price` as the Legal Price and the freshly-entered charged price as its two inputs — nothing else from the catalog is read.

---

## 17. Analytics Events (Proposed, Not Yet Built)

No `AnalyticsSink` calls exist anywhere in this file, consistent with every other screen inspected so far. Proposed hook locations, following the same naming discipline already used in the Beer Detail and Recommendation specifications:
- **Screen viewed (by SKU)** — top of `build()`.
- **Charged price submitted** — inside `_verify()`, on a successful parse.
- **Verification result shown, by verdict** — immediately after `_result` is set.
- **Invalid price entry** — inside `_verify()`'s `chargedPrice == null` branch; this is also exactly where a future resolution of the imprecise-price gap (§7) would need its own distinct event, once that gap is actually decided.
- **Beer Detail requested from this screen** — inside the "View Beer Detail" `TextButton`'s `onPressed`.

---

## 18. Implementation Notes

**No code change is proposed by this document for the screen itself**, beyond what's already named as an open Product Decision in §7 — everything else inspected here already satisfies the canon as written, a genuinely different outcome than either prior specification in this series found for its own screen (each of which found one concrete, safe copy fix). The one substantive action this document does recommend is **documentary, not code**: `docs/engineering/implementation/22-Repository-Sync-Patch-Price-Verification.md` should either be corrected to no longer claim a Price Verification Engineering Screen Specification exists, or that specification should actually be written (matching the pattern of the other four files in `docs/engineering/specifications/`) so the patch's premise becomes true. Until one of those happens, any future engineering work that trusts the patch's stated M5→M6 widget dependency will be planning against components (`ExplanationPanel`, `ConfidenceBadge`) that don't exist and that this screen's own real implementation proves were never actually needed to build it.

---

## 19. Explicit Non-Goals

No shared `ExplanationPanel`/`ConfidenceBadge` widgets introduced here or elsewhere on the strength of the patch document's claim — confirmed unnecessary by this screen's own working implementation. No resolution invented for the imprecise-charged-price gap (§7) — that remains a Product Decision, not something this document or a future engineering pass should default into silently, a second time. No Home → Price Verification or Comparison → Price Verification entry point built here — both are real, scoped, future work blocked on other screens/features, not on anything this document identifies.

---

## 20. Items Requiring a Decision — Consolidated

**Product Decision Required:**
1. Whether an imprecise/approximate charged price should ever be accepted, and if so, how it should be represented and what confidence ceiling a delta computed from it should honestly be allowed to claim (§7). The current code's "silently require an exact number" behavior is a de facto default, not a decision, and should not be read as canon's intended answer.

**Design Decision Required:**
2. Whether the "above legal price" verdict deserves any visual distinction beyond its existing plain-text `titleMedium` treatment and explanatory sentence — the canon requires the finding be stated plainly and never softened, which the current text already satisfies; whether a stronger visual signal (color, icon) would help or would risk exactly the "celebratory/alarmed" tone the Conversation Model explicitly forbids is an open, low-priority styling question, not a compliance gap.

**Engineering Decision Required:**
3. Reconciling `docs/engineering/implementation/22-Repository-Sync-Patch-Price-Verification.md` with the actual repository state — either write the Price Verification Engineering Screen Specification it claims already exists, or correct the patch to stop asserting that it does, and correspondingly re-examine its M5→M6 shared-widget dependency claim, which does not hold against the real, working implementation (§0, §18).

Every other aspect of this screen inspected in this document — the three-way confidence distinction, the Explanation-always-attached rule, the correction-without-restart behavior, the Lexicon compliance, the non-persistence of the charged price, the hand-off context rules — already satisfies the frozen canon exactly as written, and no change is proposed for any of it.
