# Recommendation Widget Specification

*A Flutter implementation blueprint translating the (now frozen) Recommendation Experience Specification into concrete widget-tree terms. Grounded in the actual, current source at `lib/features/recommendation/` and `lib/navigation/value_brew_navigator.dart` — read directly for this document, not reconstructed from memory. Every recommendation below either reuses what's already shipped, or names a small, explicit delta against it. No new architecture, no new shared-widget system, no UI redesign.*

---

## 0. Ground Truth Warning — Read This First

`lib/features/recommendation/` contains files from **two different lineages**, and this is easy to get wrong without checking directly, so it's stated plainly here:

- **The real, reachable implementation** is `domain/generate_recommendation.dart` (a pure function), `domain/recommendation_outcome.dart`, `domain/recommendation_result.dart`, `domain/tied_candidate.dart`, and `presentation/recommendation_screen.dart`. This is what `app.dart` → `home_screen.dart` actually routes to.
- **`providers/recommendation_providers.dart` is a trap.** It sits in a folder name that looks canonical, but it wires up `RecommendationProfileRepository`, `RecommendationProfile`, `RecommendationEngine`, and `RecommendationPolicy` — all from the **unreachable Generation 1 lineage** (`policy/`, `services/`, `models/`, `scoring/`, `widgets/`). The actual `RecommendationScreen` does **not** import this file at all. It calls `generateRecommendation()` directly from local widget state, and reads only `catalogProvider` via Riverpod.

**This spec builds exclusively on the real path.** Do not wire `RecommendationScreen` to `recommendationProfileProvider`, `recommendationEngineProvider`, or `recommendationPolicyProvider` — doing so would silently resurrect dead code and contradict the shipped, tested behavior this document is extending.

---

## 1. Widget Tree (Current, Verified)

```
RecommendationScreen (ConsumerStatefulWidget)
└─ _RecommendationScreenState
   └─ Scaffold
      ├─ AppBar(title: "Recommendation")
      └─ body: catalogAsync.when(...)
         ├─ loading → _recommendationSkeleton()            [function, not a class]
         │   └─ Padding → Column
         │      ├─ SkeletonBox(height: 56)
         │      └─ SkeletonBox(height: 40)
         ├─ error → ErrorStateView(message, onRetry)         [shared widget]
         └─ data(catalog) → Padding → Column
            ├─ TextField (budget input)
            ├─ ElevatedButton ("Get a recommendation")
            ├─ if (outcome != null):
            │  ├─ if (isPlanning): _PlanningModeBanner       [private]
            │  ├─ _RecommendationOutcomeView(outcome, onSeeFullDetails)  [private]
            │  └─ if (outcome.canBeRefinedFurther):
            │     ├─ if (_refining): _StylePicker             [private]
            │     └─ else: TextButton ("Refine recommendation")
```

`_RecommendationOutcomeView` switches on the sealed `RecommendationOutcome` and renders one of four branches internally (Found / NoRecommendationWithinBudget / NoRecommendationMatchingStyle / Tie) — it is not four separate widgets.

---

## 2. Screen Hierarchy / File Map

| File | Role |
|---|---|
| `presentation/recommendation_screen.dart` | The screen, its local state, and every private widget below it |
| `domain/generate_recommendation.dart` | Pure reasoning function — no Flutter import |
| `domain/recommendation_outcome.dart` | Sealed outcome type + `canBeRefinedFurther` |
| `domain/recommendation_result.dart` | `RecommendationResult` (sku + beer + explanation) |
| `domain/tied_candidate.dart` | `TiedCandidate` (sku + beer, no explanation) |
| `features/shared/providers/catalog_provider.dart` | `catalogProvider` — the only Riverpod dependency this screen reads |
| `features/shared/widgets/error_state_view.dart`, `skeleton_box.dart` | Shared, already-used loading/error widgets |
| `navigation/value_brew_navigator.dart` | `homeToRecommendation`, `recommendationToBeerDetail` |
| `core/constants/app_spacing.dart` | `AppSpacing` tokens |
| `core/utils/display_formatting.dart` | `currencyLabel`, `volumeLabel`, `displayLabel` extensions |

---

## 3. Reusable Widgets (Already Shared — Reuse, Don't Reinvent)

- **`ErrorStateView`** — used exactly once here, for a failed catalog load. Do not build a Recommendation-specific error widget.
- **`SkeletonBox`** — composed, screen-specific, into `_recommendationSkeleton()`, matching the Beer Detail / Price Verification precedent. **[Resolved]** no shared "Recommendation skeleton" component needed or wanted — this is a one-consumer composition, consistent with the codebase's own extraction discipline.

## 4. Local Widgets (Correctly Private — Do Not Promote)

`_RecommendationOutcomeView`, `_PlanningModeBanner`, `_StylePicker` are each private, single-consumer widgets. **[Resolved]** none should be promoted to `shared_presentation` or similar — the codebase's established rule is extraction only after a genuine second consumer exists, and none currently does. Leave them exactly where they are.

---

## 5. State Ownership

| State | Owner | Type |
|---|---|---|
| Budget text | `_budgetController` (TextEditingController) | Local widget state |
| Current outcome | `_outcome` | Local widget state (`RecommendationOutcome?`) |
| Selected style | `_selectedStyleId` | Local widget state (`String?`) |
| Refine-panel visibility | `_refining` | Local widget state (`bool`) |
| Validation error | `_error` | Local widget state (`String?`) |
| The Catalog | `catalogProvider` | Riverpod `FutureProvider<Catalog>` |

**[Resolved]** Recommendation's own flow state is deliberately *not* a Riverpod `StateNotifier` — it's plain `setState` inside `_RecommendationScreenState`, exactly like the rest of this screen already works. There is no dedicated ViewModel class; the private `State` object plays that role. This spec does not introduce one — doing so would be new architecture, explicitly out of scope.

## 6. "ViewModel" Responsibilities (Mapped Onto the Existing State Class)

`_RecommendationScreenState` already owns:
- Holding the current Preference Summary equivalent (`_selectedStyleId`, and the budget text).
- The single regeneration path (`_regenerate`), called identically by budget submission and every style change — **[Resolved]** this is the correct place for any future input to hook into; a new input source should call `_regenerate`, never bypass it.
- Deciding whether the refine control is visible (`outcome.canBeRefinedFurther`), delegated entirely to the domain layer's own invariant — the widget never re-derives this itself.

No changes needed here.

---

## 7. State Transitions (Experience Spec → Actual Code)

| Experience Spec state | Real code condition |
|---|---|
| Initial | `_outcome == null`, catalog loaded |
| Gathering — Budget | Always visible (the `TextField` never leaves the tree) |
| Gathering — Style | `_refining == true` |
| Evaluating | The synchronous gap inside `_regenerate` — **[Resolved]** given this is local, synchronous computation over an already-loaded Catalog, no distinct "Evaluating" visual state exists or is needed; `setState` completes before the next frame. The Experience Spec's skeleton treatment for "Evaluating" applies only to the *catalog's own* async load (`loading:` branch), not to re-running `generateRecommendation` on an already-loaded catalog. |
| Recommending — Winner | `_outcome is RecommendationFound` |
| Recommending — Tie | `_outcome is RecommendationTie` |
| Recovering — Conflicting Constraints | `_outcome is NoRecommendationWithinBudget` or `NoRecommendationMatchingStyle` — see §20 for the copy delta |
| Recovering — Low-Confidence | **Not reachable in the current build.** Confirmed directly in `generate_recommendation.dart`'s own doc comment and the V1 Architecture Reference: today's two-input surface always resolves to a definite outcome. No widget branch exists for this, and none should be added speculatively. |
| Completed | Not a distinct visual state — leaving the screen via `onSeeFullDetails` *is* completion, exactly as the Experience Spec already describes. |

---

## 8. Navigation Integration

Confirmed exact signatures, already correct, reuse as-is:
- Entry: `ValueBrewNavigator.homeToRecommendation({bool isPlanning = false})` — pushes `RecommendationScreen(isPlanning: isPlanning)` directly via `MaterialPageRoute`. **[Resolved]** no named route table — consistent with the established "not earned yet, one caller one destination" rule; do not introduce one for this work.
- Exit: `onSeeFullDetails` → `ref.read(valueBrewNavigatorProvider).recommendationToBeerDetail(skuId)`. Reachable from both the single-winner branch and every tied-candidate's own "See full details" button in `_RecommendationOutcomeView`.

---

## 9. Design Tokens / Spacing

`AppSpacing` (`xs=4, sm=8, md=16, lg=24, xl=32`) exists and is used in `_recommendationSkeleton()`, but **the main `build()` method still uses raw `EdgeInsets.all(16)` and bare `SizedBox(height: 16/24)` values** rather than the named constants. **[Implementation delta, resolvable, not a Product Decision]** migrate these specific call sites to `AppSpacing.md` (16) and `AppSpacing.lg` (24) respectively — this is exactly the kind of incremental token migration `AppSpacing`'s own doc comment already anticipates ("not every existing spacing value... has been migrated... every widget touched by it uses these instead"), and this screen is now being touched.

---

## 10. Typography Mapping

| Element | Current mapping |
|---|---|
| Beer name (Winner outcome) | `Theme.of(context).textTheme.titleLarge` |
| Explanation text | Default body style (no explicit `textTheme` role set) |
| Planning Mode banner | `textTheme.bodySmall` + `FontStyle.italic` |
| Tied candidate name/size line | Default body style |

**[Resolved]** the explanation and tied-candidate text should stay on the default body role — the Experience Spec's "explanation set noticeably lighter than the headline" intent is already satisfied by the contrast between `titleLarge` and the unstyled default, without needing a new, separate "explanation" text style invented for this screen.

---

## 11. Icon Mapping

**None currently used on this screen.** No icons on the budget field, the buttons, or the style chips (`ChoiceChip` uses Material's default label-only rendering). **[Resolved, consistent with the Experience Spec's own "minimal iconography" rule]** no icons should be added. The Experience Spec's mention of "a single, consistent info-style affordance for Why this one?" does not apply here as a separate icon-bearing control, because — see §20 — the current build has no distinct "Why this one?" action at all; the explanation is always inline.

---

## 12. Loading Widgets

`_recommendationSkeleton()` — exact composition already correct: two `SkeletonBox` instances (heights 56 and 40) approximating the budget field and button, inside a `Padding`/`Column`. **[Resolved]** no changes needed; do not build a generic cross-screen loading widget for this.

## 13. Error Widgets

`ErrorStateView(message: "Couldn't load the beer catalog.", onRetry: () => ref.invalidate(catalogProvider))` — exact, already correct. **[Resolved]** this is the only error path this screen has (the catalog itself failing to load); `generateRecommendation` never throws in a way the UI needs to catch — its own honest outcomes (`NoRecommendationWithinBudget`, etc.) are not errors and must never route through `ErrorStateView`, per the canon's own explicit rule against conflating technical failure with a Recovery State.

---

## 14. Accessibility Semantics

No explicit `Semantics` widgets are present in the current build — the `TextField`'s `labelText`, the `ElevatedButton`/`TextButton`'s text children, and `ChoiceChip`'s `label` already provide baseline semantic labels via Material's own defaults. **[Resolved, baseline only, per the Experience Spec's own explicit caveat that no formal accessibility standard exists yet]** no new semantic wrapping is required for this work beyond what Material widgets already provide by default; do not invent a bespoke accessibility layer here, since none is canonically specified.

## 15. Animations

None currently present — the outcome view and skeleton appear/disappear via plain `Column` child list changes (Flutter's default, no explicit transition). **[Resolved, consistent with both Generation 1's and Generation 2's established "no custom animation" convention]** do not add an `AnimatedSwitcher` or similar for the outcome transition; the current plain-rebuild behavior is the correct, already-aligned implementation of that rule, not a gap to fill.

## 16. Responsive Behavior

Single-column, `Padding` + `Column` with `crossAxisAlignment: stretch` — no breakpoints, no adaptive layout logic anywhere in the current build. **[Resolved]** this is acceptable and correct for a phone-first V1 with no stated tablet/desktop requirement anywhere in the canon; no responsive work is in scope here.

---

## 17. Dependency Injection Points

- `catalogProvider` — overridable in tests via `ProviderScope(overrides: [...])`, exactly as every other screen already does.
- `valueBrewNavigatorProvider` — overridable the same way, to inject a fake navigator and assert on calls without a real `Navigator`.
- **[Resolved]** no new injectable dependency is needed for anything in this spec — `generateRecommendation` is a pure function taking `Catalog` directly, not a service requiring its own provider.

## 18. Analytics Hook Locations (Proposed, Not Yet Built)

Matching the event names proposed in the Recommendation Experience Specification §3.11, the concrete call sites are:
- `recommendation_flow_started` — `RecommendationScreen.initState` (would need to be added; the widget is currently `ConsumerStatefulWidget` without an `initState` override).
- `budget_submitted` — inside `_regenerate`, on the branch where `budget != null`.
- `style_selected` / `style_skipped` — inside `_StylePicker.onChanged`, keyed off whether the passed `styleId` is null.
- `recommendation_outcome_shown` — inside `_RecommendationOutcomeView.build`, tagged with the outcome's runtime type.
- `recommendation_accepted` — inside `onSeeFullDetails`, before the navigator call.
- `preference_refined` — inside the `TextButton` that sets `_refining = true`.
- `planning_mode_active` — inside `_PlanningModeBanner.build`, or once per screen entry when `widget.isPlanning` is true.

**[Resolved as proposed hook locations; actual wiring is out of scope here]** this screen has no `AnalyticsSink` calls today — adding them is the same E5 work already scoped in the Execution Backlog, not new work invented by this document.

## 19. Testing Seams

Already exercised by the existing test suite's established pattern (per V1 Architecture Reference §7): `ProviderScope` overriding `catalogRepositoryProvider` with a fake, pumped inside a `MaterialApp` wired to the real `rootNavigatorKey` when navigation needs asserting. **[Resolved]** new tests for any copy or spacing changes in §20 should follow this exact existing pattern — override the catalog, assert on rendered text for each of the four outcome branches, and assert on the specific destination screen after tapping "See full details," not merely that "some navigation occurred," per the codebase's own established testing philosophy.

---

## 20. Implementation Deltas — What Actually Needs to Change

Everything above this section is either already correct or a small, resolvable adjustment. This section lists every place the current shipped screen differs from the frozen Recommendation Experience Specification, each classified as safe-to-apply or requiring a decision first.

**Safe to apply — copy alignment (no structural change):**
- `NoRecommendationWithinBudget`'s copy ("No beer in the catalog fits that budget.") and `NoRecommendationMatchingStyle`'s copy ("No beer within your budget matches that style.") do not currently restate the specific budget number or name both tension-producing inputs together, as the Experience Spec's Conflicting Constraints copy (§2.6) calls for. Recommended updated copy, consistent with existing string-literal style: *"Nothing in the catalog fits your ₹[budget] budget."* and *"Nothing fits both your ₹[budget] budget and [style] — try loosening one."* This is a pure string change inside the existing switch branches — no new widget, no new state.
- The Winner outcome's explanation is already close to the Experience Spec's certainty-then-judgment pattern (*"Within your ₹X budget... is the best value available — a Value Score of Y"*) but uses the literal phrase **"a Value Score of [number]"** — **this directly conflicts with the Lexicon's forbidden-terminology rule against numeric-scoring language and the Experience Spec's own explicit "never a bare number" requirement.** Recommended fix: replace the numeric Value Score mention with the plain-language Style Standing phrasing already specified in the Experience Spec (§2.4) — e.g., *"...is the best value available for your budget."* — omitting the raw number entirely. This is the single most important copy delta in this document.

**Requires a decision before changing (do not silently rewrite shipped, tested behavior):**
- Whether to add a distinct "Why this one?" affordance separate from the always-visible inline explanation, as the Experience Spec describes (§2.4) — **[PRODUCT/DESIGN DECISION REQUIRED]** the current build shows the full explanation inline, always, with no expand action at all. Adding a separate "Why this one?" control that re-surfaces the *same* content would be a genuine UI addition, not a copy fix — flagged here rather than added silently, since "do not redesign the UI" governs this document as much as the Experience Spec did.
- Whether the always-available "Refine recommendation" control (offered whenever `canBeRefinedFurther` is true, regardless of whether style would actually change the outcome) should instead be gated by the Decision Engine 2.0 §10 threshold logic. **[Resolved, not a gap]** — on inspection, this is not actually a conflict: the canon's threshold logic governs when the *system* should proactively ask another question; it does not forbid a person-initiated, always-available manual refine action. The shipped behavior is a legitimate implementation of the same canon, not a deviation from it.

---

## 21. Explicit Non-Goals

No new shared widget system (`ConfidenceBadge`, `ExplanationPanel`, `TradeoffCard` from the original Flutter Implementation Architecture plan were never built and are not built here — they remain planned-but-unearned, consistent with the codebase's own extraction discipline). No Riverpod `StateNotifier` introduced for Recommendation's flow state. No route table. No new animation system. No accessibility standard invented. No wiring to `recommendation_providers.dart`'s Generation 1 profile/engine/policy system, ever.

## 22. Items Requiring a Decision — Consolidated

1. **Whether to add a distinct "Why this one?" affordance** (§20) — a genuine, flagged UI question, not resolved here.
2. **The null-ABV-in-ranking gap**, inherited unchanged from the Recommendation Experience Specification — `generateRecommendation`'s candidate filter (`catalog.skus.where((sku) => sku.price <= budget)`) does not currently check ABV completeness at all, because the real launch catalog this would matter for doesn't exist yet in the loaded `Catalog`. This remains the single most important blocking dependency for shipping this screen against real, incomplete data, restated here at the exact line of code it will need to change.

Everything else in this document is either a direct restatement of the already-shipped, correct implementation, or a small, explicitly-scoped copy delta safe to apply without further authority.
