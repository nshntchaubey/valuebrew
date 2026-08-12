# Beer Detail Experience Specification

*A build specification for the Beer Detail experience, produced the same way the Recommendation Experience Specification was: grounded directly in the actual Flutter implementation (`lib/features/beer_detail/presentation/beer_detail_screen.dart`, confirmed as the real, reachable screen via `ValueBrewNavigator`), the canonical Beer Detail Screen Contract (`docs/architecture/current/13-Beer-Detail-Screen-Contract.md`), the existing Engineering Screen Specification for this screen (`docs/engineering/specifications/Beer-Detail-Screen-Specification.md`), the Canonical Screen Specification Template, The ValueBrew Experience's own Step 4/5 narrative, and Generation 1's equivalent screen, read directly and cited where it changes anything. This document does not redesign the experience — it documents what exists, resolves what the canon already permits resolving, and classifies every remaining gap as a **Product**, **Design**, or **Engineering** Decision Required, exactly as instructed.*

---

## 0. Ground Truth Statement

Two files named `beer_detail_screen.dart` exist in this codebase, and only one of them is real:

- **`presentation/beer_detail_screen.dart`** is the actual, reachable screen. Both legal entry points — `ValueBrewNavigator.recommendationToBeerDetail(skuId)` and `.priceVerificationToBeerDetail(skuId)` — push exactly this class, constructed with a single `skuId` string. This matches the canonical Screen Contract's stated precondition exactly: *"the identified SKU. This is a precondition for the screen loading at all."*
- **`screens/beer_detail_screen.dart`** is Generation 1 code, unreachable from `ValueBrewNavigator` and therefore never shown to a real user, despite still having a test (`test/widget/beer_detail_screen_test.dart`) exercising it in isolation. It takes a whole `Beer` object (not a `Sku`), and renders a favorite toggle, a "This looks wrong" report action, a recommendation-profile picker, and two inline "Similar beers" / "Better value picks" lists — none of which have any basis anywhere in the current 20-document canon. This was independently confirmed here by grepping the entire `docs/architecture/current/` set, the Product Definition Document, the Domain Model, and the Catalog Specification for "Favorites" and for any reporting/flagging feature: **zero matches**. These are not deferred canonical features; they were never specified in the current architecture at all, and the "Similar/Better value" lists actively contradict the Screen Contract's own MUST NEVER clause ("push an alternative or a comparison unprompted, however much better an alternative might be").

**This specification describes only the real, canon-shaped screen.** Nothing from the dead file is treated as a target state, a recoverable feature, or a hint about intended scope.

---

## 1. Complete User Journey

Per the Navigation Contract and confirmed directly in `ValueBrewNavigator`, Beer Detail has exactly two legal entry paths and no others:

1. **Recommendation → Beer Detail** — reachable only from a `RecommendationFound` outcome (a single winner) or a `RecommendationTie` candidate's own "See full details" action. The person arrives having just been told, with an Explanation, why this specific SKU was chosen.
2. **Price Verification → Beer Detail** — reachable after an explicit verification, carrying the SKU identity forward but never the charged price just entered (Navigation Contract's own rule, confirmed unbroken in the real code: `beerDetailToPriceVerification`/`priceVerificationToBeerDetail` pass only `skuId`).

There is **no direct entry from Home**, and no Search/Browse entry, because Search/Browse Results has no Screen Contract at all — a canonical gap named consistently across every prior document in this set, not reopened here. The ValueBrew Experience document's own framing is exact and is reused directly, not reworded: *"However the person arrives here (today, always by way of a Recommendation hand-off), this is the screen that has to answer everything knowable about one specific beer."*

Once here, the journey ends one of two equally legitimate ways (Screen Contract §7, §8): an explicit hand-off to Price Verification, or simply leaving, satisfied, with no further action. Both are Decision Complete. Neither is treated as more "real" than the other.

---

## 2. Screen States (Canonical State Machine → Real Code)

| Canonical state | Real code condition | Notes |
|---|---|---|
| **Loading** | `catalogAsync` is `AsyncLoading` | Renders `_beerDetailSkeleton()`. |
| **Loaded** | `catalogAsync` has data, `sku` and `beer` both resolve | Renders the full facts column. |
| **Confirming** | *(no code path — see §9)* | Confirm-as-Is is not implemented anywhere in the real screen. This is not an omission bug; it mirrors what The ValueBrew Experience itself already states plainly: *"this feature is not built... blocked on two things at once."* Carried forward here, not re-litigated. |
| **Handoff-Pending** | The moment `beerDetailToPriceVerification` is called | Transient — resolves immediately into a screen push. |
| **Recovering** | `sku == null \|\| beer == null` (data loaded, but the ID doesn't resolve), **or** `catalogAsync` is `AsyncError` | Two distinct real conditions collapse correctly onto the canon's single Recovering state — see §7. |
| **Completed** | Not a distinct visual state | Reached by either accepting a hand-off or simply leaving; the screen renders nothing different at this moment, consistent with the Screen Contract's own "no further automatic content or prompt" rule for the terminal state. |

---

## 3. Visual Hierarchy & Layout

`Scaffold` → `AppBar(title: "Beer Detail")` → body. The AppBar title is the literal screen name, not the beer's name — a small, deliberate, already-shipped choice worth stating explicitly since it's easy to assume otherwise: the beer's name is the first content element in the body instead, at `headlineSmall`, so a person scrolling back up still sees it restated at the top of the AppBar as "Beer Detail," the screen identity, not the beer identity.

Body: `SingleChildScrollView` → `Padding(AppSpacing.md)` → `Column(crossAxisAlignment: start)`, in this exact top-to-bottom order:

1. **Beer Identity block** — beer name (`headlineSmall`), brewery, style name (only if the style resolves).
2. **`Divider`** — the one and only visual section break on this screen, separating identity from economics.
3. **Economic/Composition block** — Legal Price (`titleLarge`, the single largest text on the page after the beer name), package type, size, ABV.
4. **Value block** — Value Score line, Style Standing (only if a benchmark exists for this style), price-last-checked date.
5. **Action** — a single `TextButton`, "Verify price."

This ordering matches the canonical Information Hierarchy exactly (Screen Contract §5, Engineering Spec §5): Primary facts first, Supporting/Confidence content immediately after, Action last. No card, no tabs, no expand/collapse — a single flat, linearly-read column, consistent with how Recommendation and Price Verification are also built.

---

## 4. Components

**Reused, not reinvented** (identical to the Recommendation Widget Specification's own findings for these same shared widgets):
- `ErrorStateView` — used twice on this screen, for two different failure conditions (see §7).
- `SkeletonBox` — composed into a screen-specific `_beerDetailSkeleton()`, matching this screen's real layout shape rather than a generic spinner.

**Screen-local, not shared:** `_beerDetailSkeleton()` and `_formatDate()` are private top-level functions in this file, not widgets promoted anywhere else — correctly private, single-consumer, consistent with the codebase's established extraction discipline (only promote after a second real consumer exists).

**No dedicated widgets exist for:** the Confirm-as-Is judgment, a Style Benchmark badge, or a confidence indicator of any kind. Every fact is a plain `Text` widget. This is consistent with the canon's own explicit statement that this screen carries **no confidence split at all** — "Confidence on this screen is uniformly high across everything shown" — so there is no structural need for a `ConfidenceBadge`-style component the way a naive read of Recommendation's spec might suggest. Nothing should be built here to visually distinguish confidence tiers, because the canon says none exist on this screen.

---

## 5. Interactions, Gestures, Transitions, Animations

**Interactions**, matching the canonical Interaction Contract (§7) one-to-one against what's actually tappable in the real code:

| Canonical action | Real affordance |
|---|---|
| View SKU details | Passive — happens on arrival, no gesture. |
| Request Price Verification | The single `TextButton`, "Verify price." |
| Accept Confirm-as-Is / Ask "why" | **Not present** — no such affordance exists, consistent with §2 and §9. |
| Request Comparison | **Not present** — Comparison itself is not built anywhere in the app; this is a pre-existing, already-documented scope gap (Execution Backlog), not newly discovered here. |
| Leave without acceptance | Standard back navigation — no custom handling. |

**Gestures:** none beyond standard scroll and standard back navigation (system back gesture or AppBar back arrow, both platform-default, no custom `PopScope`/`WillPopScope` logic in the file). **[Design Decision Required, low-priority]** whether "Verify price" deserves a leading icon or any other visual treatment beyond `TextButton`'s default styling is unspecified by canon and unresolved in the real code — currently plain text, matching Recommendation's equally plain "See full details"/"Refine recommendation" buttons.

**Transitions:** a standard `MaterialPageRoute` push/pop, no custom transition curve or duration — consistent with every other screen in the app; `ValueBrewNavigator` never customizes route transitions anywhere.

**Animations:** none. No `AnimatedSwitcher`, no fade between Loading and Loaded. Consistent with Recommendation's own already-resolved finding that the absence of animation here is the correct, aligned implementation of the codebase's established "no custom animation" convention, not a gap.

---

## 6. Loading, Empty, and Error States

**Loading** — `_beerDetailSkeleton()`: seven `SkeletonBox` placeholders shaped to approximate the real content column (name, brewery, style, a divider-adjacent gap, price, package/size, value line), at `AppSpacing.sm`/`.xs`/`.lg`/`.md` gaps mirroring the real content's own spacing rhythm.

**Empty** — does not apply to this screen in the ordinary sense. There is no "zero results" condition; either a SKU resolves or it doesn't (see Recovery below). Style Standing is the one genuinely optional element, and its absence is handled as graceful omission, not an empty state: the `if (styleStanding != null)` guard simply skips those two `Text`/`SizedBox` widgets entirely, with no placeholder, no "not yet available" message, no visual gap left behind. This is a direct, correct implementation of the Screen Contract's own explicit instruction: *"Style Benchmark's absence... is never treated as a missing Primary object"* and *"never treated as an error."*

**Error** — two distinct, correctly-separated conditions:
1. Catalog fails to load at all → `ErrorStateView(message: "Couldn't load the beer catalog.", onRetry: () => ref.invalidate(catalogProvider))` — a real, actionable technical failure, with a retry.
2. Catalog loads fine, but `skuId` doesn't resolve to a real SKU/beer → `ErrorStateView(message: "This beer couldn't be found.")` — **no `onRetry`**, correctly, since there's nothing to retry; the catalog is fine, the identity reference is simply stale. This is the canon's own named "SKU not found" Recovery State (Screen Contract §11), and the plain, blame-free, no-substitute-offered copy matches the Conversation Model's Recovery Communication Patterns exactly ("state the fact... never assigns blame... no invented substitute").

---

## 7. Recovery Flows

Both Recovery paths in §6 terminate the screen's usefulness entirely — there is no retry-into-content path for a stale SKU reference, matching the Screen Contract's own explicit statement: *"there is no prior context on this screen to preserve, since it depends entirely on a single, freshly-arriving identification."* The only way forward from either Recovery condition is leaving the screen. No fallback content, no "here's something similar instead," consistent with the MUST NEVER clause against pushing an unprompted alternative — including as a recovery gesture.

---

## 8. Accessibility

**Intentionally left unspecified by the Canonical Architecture**, exactly as the Engineering Screen Specification already states (§11) — no accessibility standard exists anywhere in the current canon, for this screen or any other. The real code carries no explicit `Semantics` wrapping beyond what `Text`, `TextButton`, and `Scaffold`/`AppBar` provide by default via Material. **[Engineering Decision Required, deferred, not blocking]** any accessibility work here should wait for a canonical standard to be established once, across all screens simultaneously — per the Screen Specification Template's own stated discipline — rather than being invented ad hoc for this screen alone.

One canon-grounded fact worth stating precisely for whenever that standard exists: because this screen carries no confidence split, an eventual accessible treatment does **not** need the kind of confidence-tier semantic distinction Recommendation's screen will eventually need — carrying forward the Engineering Screen Specification's own explicit warning against introducing "a false parallel to Recommendation's screen" here.

---

## 9. Explanation Behavior

Beer Detail reuses the Recommendation Framework's Explanation structure, but only for one thing: the Confirm-as-Is judgment (Screen Contract §6, §9). Since Confirm-as-Is is not built, **there is currently no Explanation content anywhere on this screen** — every fact shown is a bare, self-evident Verified or Computed Fact (a price, an ABV, a size) that needs no accompanying reasoning, unlike Recommendation's synthesized outcome. This is the single cleanest distinguishing property of this screen versus Recommendation, and the real code reflects it precisely: there is no explanation-shaped text anywhere in `presentation/beer_detail_screen.dart`.

---

## 10. Copy

Exact wording is a content deliverable, not fixed here, but three requirements from the Engineering Screen Specification's own Copy Requirements (§12) bear directly on what's already shipped:

- **"Correct price" must never replace "Legal Price."** The real code never uses this phrase — compliant.
- **"Confirm" must always pair with "-as-Is."** Not applicable today since the feature doesn't exist in the shipped copy at all — compliant by absence.
- **No forbidden Lexicon terms — "Score" or "Rating," anywhere, under any framing.** **This is violated today.** Line 74 of the real screen reads literally: `'Value score: ${sku.valueScore} (${sku.valueVerdict.displayLabel})'`. This is the single most important, concrete finding of this document — a direct, confirmed breach of the Canonical Interaction Lexicon's most heavily and repeatedly enforced rule, present in shipped, user-facing copy right now. **[Engineering Decision Required — a safe, scoped copy fix, not a Product or Design question]**: drop the bare "Value score: N" line entirely, and rely on `sku.valueVerdict.displayLabel` alone ("Great value" / "Fair value" / "Overpriced for this ABV") plus, where a benchmark exists, `styleStanding.displayLabel` ("Better value than typical for this style," etc.) — both of which are already Lexicon-compliant, plain-language phrasings that exist in the codebase today and require no new copy to be written. This mirrors exactly the "Value Score of Y" finding already flagged and resolved the same way in the Recommendation Widget Specification — the same violation exists in two places, with the same fix.

---

## 11. Typography, Spacing, Iconography

**Typography:** `headlineSmall` for the beer name (the largest, most prominent text on the page), `titleLarge` for the price (the second-most prominent — deliberately distinct treatment for "what beer" versus "what it costs"), default body style for everything else. No dedicated style exists for the Value Verdict or Style Standing lines — they read at the same visual weight as plain facts, which is exactly correct per §9: nothing here is a judgment call requiring visual emphasis or de-emphasis, since everything on this screen carries uniform confidence.

**Spacing:** this screen already fully uses `AppSpacing` tokens throughout (`.md`, `.sm`, `.xs`, `.lg`) — unlike Recommendation's screen, which the Widget Specification found only partially migrated. **No spacing delta needed here.**

**Iconography:** none used anywhere on this screen. Consistent with the Experience Specification's own established minimal-iconography stance for Recommendation; no icon should be introduced here either.

---

## 12. Information Priority & Trust Signals

Priority order matches Section 3's layout exactly: identity first (what is this), then economics (what does it cost, in what size), then value judgment (is that a good price for this ABV, relative to its style), then provenance (when was this price last checked), then the one available action. This ordering directly encodes the canon's own Content Architecture composition (Primary → Supporting → Contextual) without reinterpretation.

**The trust signal this screen leans on hardest is exactly the one already named in The ValueBrew Experience:** completeness without overreach. It answers "what is this" exhaustively and refuses to answer "should I buy it" (Confirm-as-Is, not built) or "is this a good deal right now, at this shop" (Price Verification, a deliberate hand-off, never computed here). The price-last-checked date is the screen's only provenance signal — no crowd-sourced freshness badge, no "confirmed by N people," a deliberate departure from Generation 1 already documented and explicitly not reopened here (see §14, item 3).

---

## 13. Confidence Presentation

**There is none to present, distinctly.** This is the one place this specification diverges structurally from the Recommendation Experience Specification, and it does so on canon's own explicit instruction, not by omission: *"Confidence on Beer Detail is uniformly high across everything shown here, since nothing displayed is built from a Soft Preference... there is no 'mixed confidence' case on this screen."* No hedge language, no "seems to," no certainty-then-judgment shift anywhere in this screen's copy — every fact is stated flatly, because every fact here actually is a Verified or Computed Fact.

---

## 14. Edge Cases

1. **A beer with multiple SKUs (pack sizes).** The real screen shows exactly one identified SKU, with no size-switcher affordance — and this is not a missing feature, it's an exact match to the canon's own Known Information: "the identified SKU," singular, not a beer with a list of SKUs. (Notably, this is one respect in which the *dead* Gen1 screen — built around a whole `Beer` object with a looped list of its SKUs — was never actually canon-shaped to begin with, independent of its other, already-documented problems.)
2. **Style Benchmark not yet computed for this beer's style.** Fully resolved, not a gap — gracefully omitted, confirmed in the real `if (styleStanding != null)` guard, exactly matching §6.
3. **Freshness of the Legal Price itself.** The ValueBrew Experience's own generational note already names this precisely: Generation 1 showed a visible crowd-sourced freshness signal ("confirmed 2 days ago by 3 people"); the current screen shows only a flat last-checked date with no visible signal of how stale that date is considered. **[Product Decision Required]** — whether any additional freshness signal (a warning past some age threshold, a different visual treatment for an old date, or nothing at all beyond the plain date already shown) should ever be added is, in the canon's own words, "a genuinely open question worth deciding on purpose, not by default." This document does not choose an answer, consistent with the instruction not to silently resolve what the canon leaves open.
4. **Confirm-as-Is's trigger rule (the "anchor situation").** The Screen Contract's own flagged, unresolved gap (§11), restated here rather than re-derived: no document specifies what actually determines whether an anchor situation applies — entry point, some other contextual marker, or always. **[Product Decision Required]** — this is the same class of decision already made explicitly for Home's unsupported-intent case and Recommendation's ambiguous-preference case; it deserves the same deliberate treatment, not an assumption made here or anywhere downstream of here.
5. **Backward navigation from Beer Detail toward Recommendation.** Already discovered and documented in the existing Engineering Screen Specification (§4, §13), restated here for completeness rather than re-investigated: Information Architecture states that backing out of Beer Detail should return to Recommendation when that's where the person came from, but the Navigation Contract's Screen Graph has no such edge, and `ValueBrewNavigator` confirms this directly — there is no `beerDetailToRecommendation` method anywhere in its API surface; only forward edges exist. **[Engineering Decision Required]** — this is a genuine cross-document inconsistency in the frozen canon itself (Information Architecture vs. Navigation Contract), not a deliberate deferral, and building a literal "back to Recommendation" edge is blocked on resolving which document is authoritative before any code is written — exactly as the existing specification already concluded.
6. **Arrival from Recommendation carrying an already-produced Recommendation object.** Already flagged in the existing Engineering Screen Specification (§13): the Recommendation object itself must never be recomputed here (confirmed — the real code never touches `generateRecommendation` or any Recommendation type; it resolves the SKU fresh from the catalog by ID, correctly). Whether this specific entry context alone should be sufficient to count as the "anchor situation" triggering Confirm-as-Is is explicitly *not* confirmed by canon — folded into item 4 above, not a separate decision.
7. **Comparison hand-off.** The Screen Contract permits it; the real code has no such button, because Comparison itself isn't built anywhere in the app yet. **Not a new gap** — already a known, scoped, cross-cutting deferral (Execution Backlog), restated here only so this document doesn't silently imply the affordance should exist today.

---

## 15. Offline Behavior

**Intentionally left unspecified by the Canonical Architecture**, exactly as the Engineering Screen Specification already states for non-functional requirements generally (§15) — no offline standard exists anywhere in canon. The real code's only offline-adjacent behavior is incidental: `catalogProvider`'s own loading/error handling already covers "the catalog failed to fetch," regardless of *why* it failed (offline or otherwise) — this screen adds nothing offline-specific beyond what it inherits from that shared provider.

---

## 16. Data Dependencies

`catalogProvider` (the only Riverpod dependency), resolved via the shared `catalog_lookups.dart` functions: `resolveSku`, `resolveBeer`, `resolveStyle`, `resolveBenchmark` — all pure, linear lookups by ID against the loaded `Catalog`, no caching layer beyond what `catalogProvider` itself already provides, no separate fetch for this screen specifically. `classifyStyleStanding` (pure Dart, no Flutter dependency) is the one piece of actual computation this screen performs locally, deriving `StyleStanding` from `Sku.costPerMlAlcohol` against `Benchmark.p50` — everything else displayed is read directly off already-computed catalog fields (`valueScore`, `valueVerdict`, `costPerLitre`, etc.), never recomputed on-device.

---

## 17. Analytics Events (Proposed, Not Yet Built)

Matching the names already proposed in the existing Engineering Screen Specification (§14), with concrete real-code call sites named for the first time here:
- **Screen viewed (by SKU)** — would sit at the top of `build()`, keyed on `skuId`.
- **Price Verification requested from this screen** — inside the "Verify price" `TextButton`'s `onPressed`, before the navigator call.
- **SKU-not-found recovery shown** — inside the `if (sku == null || beer == null)` branch.
- **Screen exited without explicit acceptance** — not independently instrumentable without a dedicated exit hook; would require the same kind of `initState`/dispose-based tracking Recommendation's own proposed hooks would need, not present in either screen today.

No `AnalyticsSink` calls exist anywhere in this file today — this section proposes hook locations only, exactly as the Recommendation Widget Specification did for its own screen; wiring them is out-of-scope E5 work, not invented here.

---

## 18. Implementation Notes — Deltas From Canon

**Safe to apply (Engineering, scoped copy fix, already detailed in §10):** remove the bare "Value score: N" numeric display; keep `valueVerdict.displayLabel` and `styleStanding.displayLabel` as the sole value-judgment copy. This is the one concrete change this document identifies as ready to make without further authority.

**Everything else about the current implementation is already canon-compliant** — a genuinely different outcome than the Recommendation Widget Specification found for its own screen, worth stating plainly: Beer Detail's real code has no dead-code trap wired into its live path (the Gen1 file is cleanly unreachable, not half-integrated the way `recommendation_providers.dart` was), fully uses its spacing tokens, and correctly implements graceful Style Standing omission, correct Recovery separation, and zero speculative UI for unbuilt features (no ghost "Confirm" button, no disabled "Compare" affordance sitting around waiting for a feature that doesn't exist).

---

## 19. Explicit Non-Goals

No Confirm-as-Is implementation (blocked on §14 item 4, a Product Decision). No SKU/pack-size switcher (not canonically specified; a beer with multiple SKUs is out of this screen's scope by design, per §14 item 1). No freshness badge or crowd-verification signal (§14 item 3, a Product Decision, and even if resolved toward "yes," building it is separate future work). No Comparison hand-off button (Comparison itself isn't built). No resurrection of Favorites, "This looks wrong" reporting, or inline Similar/Better-Value recommendation lists from the dead Gen1 screen — none of these have any canonical basis today, and restoring any of them would require a fresh Product Decision establishing them as in-scope, not an implementation choice made inside this document.

---

## 20. Items Requiring a Decision — Consolidated

**Product Decision Required:**
1. The exact rule determining when an "anchor situation" applies and Confirm-as-Is should surface (§14 item 4; also the sole reason Confirm-as-Is remains unbuilt).
2. Whether any price-freshness signal beyond the plain last-checked date should ever be shown, and if so, at what staleness threshold it would change presentation (§14 item 3).

**Design Decision Required:**
3. Whether the "Verify price" action deserves any visual treatment beyond plain `TextButton` styling (§5) — low priority, does not block anything else in this document.
4. The exact visual form any future freshness signal should take, once (and only if) item 2 above is resolved toward building one.

**Engineering Decision Required:**
5. Removing the Lexicon-violating "Value score: N" text at line 74 of `presentation/beer_detail_screen.dart`, replacing it with the already-available `valueVerdict.displayLabel`/`styleStanding.displayLabel` pair (§10) — scoped, safe, ready to apply.
6. Resolving the Information Architecture vs. Navigation Contract inconsistency over whether a Beer Detail → Recommendation back-edge should exist, before any such edge is built (§14 item 5) — inherited unchanged from the existing Engineering Screen Specification, not newly discovered here.
7. Deferred, non-blocking: establishing a canonical accessibility standard before any screen-specific accessibility work begins here (§8).

Everything else in this document describes an already-correct, already-shipped implementation that needs no change to satisfy the frozen canon.
