# ValueBrew — Flutter Implementation Architecture

**Document Type:** Software Architecture (Implementation Layer) — **not** Product Architecture
**Status:** Draft
**Version:** 0.1
**Sits below:** Canonical Architecture (pending freeze as v1.0), all Engineering Screen Specifications, the Engineering Planning Roadmap
**Author role:** Lead Flutter Engineer

---

## 0. Framing

Everything in this document is a decision about *how* ValueBrew gets built, never *what* it does. Where this document names a class, a layer, or a pattern, it is naming a container for behavior that a canonical document has already defined — never inventing new behavior of its own. Where the canon leaves something open (the two carried-forward ambiguities, the Beer Detail → Recommendation navigation inconsistency), this document does not resolve it either. It says, explicitly, how the implementation should *hold* that gap without silently closing it — because an engineer under deadline pressure is exactly the person most likely to close it by accident, and that failure mode is cheaper to design out now than to catch in review later.

This document assumes Dart/Flutter as the client platform (already fixed by the "Lead Flutter Engineer" framing) but stays agnostic on everything the canon hasn't decided — backend technology, hosting, and the eventual catalog data source are out of scope here and should be a separate decision.

---

## 1. Overall Implementation Philosophy

Three commitments, carried down directly from the canon's own architectural principles:

- **Traceability survives the handoff from documents to code.** Every domain type should be able to answer "which canonical section made me necessary" the same way every field in the Screen Specification Template already does. This is enforced lightly (doc-comments citing source documents), not heavily (no custom tooling to verify it at MVP stage).
- **The implementation may be simpler than the canon in *engineering* terms, never in *behavioral* terms.** A solo founder can choose a lean state-management approach, skip a formal DI framework, and defer test coverage on low-risk code paths. A solo founder may not skip a Recovery State, collapse a Confidence tier, or let a screen quietly perform reasoning it doesn't own.
- **Open items are represented as open items in code, not resolved in code.** Where the canon says "flagged, not resolved," the implementation encodes that as an explicit, visible state — a `TODO` linked to the relevant ADR entry, a UI treatment that degrades honestly, or a guard clause that fails loudly — rather than a silent default that happens to compile.

Architecturally, this points to a **pragmatic Clean Architecture**: enough separation between domain, data, and presentation to keep the Screen Contracts' ownership boundaries intact in code, without the ceremony (abstract factories, elaborate DI graphs, premature microservice-shaped modularity) that a one-person team doesn't yet need and would only slow down.

---

## 2. Recommended Flutter Architecture

Three layers per feature, deliberately thin at MVP scale:

- **Domain** — pure Dart. Entities, value objects, and use cases that mirror the Canonical Interaction Lexicon and Beer Knowledge Model exactly. No Flutter import ever appears here. This layer is the actual carrier of canonical meaning; everything else is plumbing around it.
- **Data** — repository implementations, remote/local data sources, DTOs and their mapping to domain entities. This is the only layer allowed to know that a catalog API or a local cache exists.
- **Presentation** — screens, widgets, and per-screen state controllers. This layer is only allowed to *display* domain state and *call* domain use cases — it never computes a Recommendation, a Verification Delta, or a Trade-off itself.

This is deliberately **feature-first**, not layer-first, at the top level (Section 5), because the canon's own Module boundaries (Discovery, Verification, Recommendation, Comparison) are the more durable seam — they're the seam a future team would actually split along — while domain/data/presentation is the seam *within* each feature.

---

## 3. State Management Strategy

**Recommendation: Riverpod** (code-generation flavor, `riverpod_generator` + `AsyncNotifier`/`Notifier`).

Reasoning against the canon's own shape, not against generic Flutter taste:

- Every screen with a canonical Screen Contract already has an explicit **State Machine** section (Home, Recommendation, Beer Detail, Comparison, Price Verification each define their own named states — e.g., Price Verification's `Awaiting Price → Verifying → Recovering → Completed`). A `Notifier` per screen, holding a **sealed state class** whose variants are exactly the states that screen's contract names, turns "no new states are permitted at this layer" from a documentation rule into a compile-time guarantee: an engineer literally cannot add a state the switch statement doesn't know about without the compiler stopping them.
- **Preference Summary** and any in-progress candidate set are explicitly session-only, never persisted (Product Definition Document's rejection of accounts; Beer Knowledge Model's classification of the Constraint Set as existing "only for the duration of one interaction"). A provider scoped to app-session lifetime, holding plain in-memory state, expresses this directly — there's no persistence code to accidentally add, because the provider is never wired to a storage layer at all.
- Riverpod's provider graph doubles as dependency injection (Section 10), which matters for a one-person team: one library instead of two.

State management is **not** used to smuggle in behavior. A `Notifier`'s job is to hold state and call a use case; the use case (domain layer) is where a Hard Constraint gets checked, a tie gets detected, a delta gets computed. This separation is what keeps "Recommendation Principle 1: a recommendation must never violate a Hard Constraint" testable in isolation from any widget.

---

## 4. Navigation Strategy

**Recommendation: `go_router`**, wrapped behind a single **`ValueBrewNavigator`** service that is the *only* thing allowed to trigger a screen transition.

The reason for the wrapper, specifically: the Navigation Contract is a closed, enumerated graph — six named transitions in scope, an explicit **Illegal Navigation** list (Home is never a backward destination; Price Verification never escalates to Recommendation or Comparison as a system-initiated transition; a screen may never perform another screen's owned reasoning instead of handing off). A generic `context.go('/recommendation')` call anywhere in the codebase makes every one of those invariants an unenforced convention. Instead:

- `ValueBrewNavigator` exposes **named methods that mirror the Navigation Contract's own Transition Contract entries** — one method per legal edge (`homeToRecommendation()`, `beerDetailToPriceVerification(skuId)`, `comparisonToBeerDetail(skuId)`, and so on) — and nothing else. There is structurally no method to call for an illegal edge, so illegal navigation isn't caught by a test after the fact — it's absent from the API surface.
- Each method's signature carries exactly the context the Navigation Contract says survives that edge — SKU identity, a candidate set, a Preference Summary reference — and nothing the contract says is discarded (Observed/Charged Price, notably, never appears as a parameter on *any* method, anywhere, because no edge in the graph carries it).
- The two edges that pass through the uncontracted **Search/Browse Results** screen are implemented, but their navigator methods carry a code comment pointing at Navigation Contract Section 14's flagged gap, so a future engineer tightening that screen's contract knows exactly where the implementation currently improvises.

Route parameters stay off the URL for anything session-scoped or privacy-sensitive (SKU identity is fine in a path segment for potential future deep-linking; Preference Summary and Observed Price are passed via the navigator's typed payload, never serialized into a URL).

---

## 5. Project Folder Structure

```
lib/
├── main.dart
├── app/                          # App shell, theming, root routing table
├── core/
│   ├── result/                   # Sealed Result/Either type for domain-level outcomes
│   ├── confidence/                # Shared Confidence tier types & display rules
│   ├── logging/                  # Abstract Logger
│   └── analytics/                 # Abstract AnalyticsSink (no-op default)
├── navigation/
│   └── value_brew_navigator.dart # Enforces Navigation Contract edges only
├── features/
│   ├── discovery/                # Beer/SKU Identification, Beer Detail, Search/Browse Results
│   │   ├── domain/
│   │   ├── data/
│   │   └── presentation/
│   ├── verification/             # Price Verification
│   ├── recommendation/           # Full Recommendation (Confirm-as-Is, Planning/Proxy modes)
│   └── comparison/                # Beer Comparison
├── shared_domain/                # Cross-cutting entities: Sku, Beer, PreferenceSummary,
│                                  # Recommendation, ComparisonResult, VerificationResult
├── shared_presentation/          # ExplanationPanel, ConfidenceBadge, TradeoffCard, TieCard —
│                                  # cross-cutting per Feature Inventory's own "Cross-cutting
│                                  # Feature" classification of Explanation & Confidence
└── catalog/                      # Beer Knowledge Base/Catalog Platform Service
    ├── domain/
    └── data/
```

`shared_domain` and `shared_presentation` exist because the canon itself names cross-cutting concerns (Recommendation Explanation, Confidence Communication, the Beer Knowledge Base) that no single Module owns — folding them into one feature folder would misrepresent their actual scope.

---

## 6. Domain Layer Structure

Entities are named to match the Canonical Interaction Lexicon term-for-term, so a code review can be checked against the Lexicon directly:

**Catalog entities:** `Beer`, `Brand`, `BeerStyle`, `Sku` (carrying `LegalPrice`, `AbvPercent`, `SizeMl`, `PackageFormat`), `DerivedValueProfile` (alcohol-adjusted value, cost/litre, value percentile), `StyleBenchmark`.

**Interaction entities:** `PreferenceSummary` (a collection of `Constraint`s, each tagged `HardConstraint` / `StrongPreference` / `SoftPreference` — implemented as a sealed class hierarchy, not a boolean flag, so the tier is structurally impossible to blur), `ObservedPrice` (deliberately has **no** repository or storage adapter anywhere in the app — see Section 9), `VerificationDelta`, `VerificationResult`, `Recommendation`, `ComparisonResult`, `TradeoffExplanation`, `TieDisclosure`.

**Confidence & knowledge tiers:** a shared `KnowledgeTier` enum — `verifiedFact` / `computedFact` / `humanJudgment` — attached to any content that carries it, matching the Beer Knowledge Model's three-way classification exactly. This is deliberately a single shared type used everywhere (Section 3's confidence widgets depend on it) rather than a per-feature reimplementation, because the canon treats it as one consistent rule across the whole product.

**Use cases (one per canonical Experience, not per screen):** `IdentifyBeerSku`, `GetBeerDetail`, `VerifyPrice`, `GenerateRecommendation`, `CompareCandidates`, `ExplainPreviousResult` ("Why"/Learning Query Handling). Each use case is where a Screen Contract's **Behavioral Rules** and **Recommendation Principles** sections become executable logic — e.g., `GenerateRecommendation` is the one place in the codebase that may decide "a recommendation exists," matching the Recommendation Screen Contract's own threshold definition.

**Repository interfaces** (implemented in the data layer): `BeerCatalogRepository`, `StyleBenchmarkRepository`. Deliberately **no** `PreferenceSummaryRepository` or `ObservedPriceRepository` exist at all — their absence from the interface layer is the architectural enforcement of "never persisted," stronger than a comment saying so.

---

## 7. Presentation Layer Structure

Per screen: a `Screen` widget (routing target, thin), a `Notifier`/state controller (owns the State Machine, Section 3), and a `ViewModel` mapping used to turn domain output into display-ready content organized by the **same categories the Content Architecture already uses** — Primary, Supporting, Contextual, Progressive, Explanation, Confidence, Recovery, Completion. Keeping that exact vocabulary in the view-model (rather than inventing UI-specific groupings) means a screen's presentation code can be checked directly against its Content Architecture composition table.

**Shared widgets, because the canon says these concerns are cross-cutting, not per-screen:**
- `ConfidenceBadge` — renders a `KnowledgeTier`, with the visual vocabulary fixed once and reused everywhere Confidence Communication applies (Recommendation, Comparison, Price Verification's three-way distinction).
- `ExplanationPanel` — renders Recommendation Explanation content; used identically for a Recommendation, a Verification Result, and a Comparison Result, per the canon's explicit instruction that Price Verification "reuses [Explanation] directly and without modification."
- `TradeoffCard` / `TieCard` — render `TradeoffExplanation` / `TieDisclosure`, shared between Recommendation and Comparison since both draw on the same underlying Trade-off/Tie-handling Engine Behavior.
- `RecoveryBanner` — a generic renderer for any Recovery State, parameterized by the specific condition (Low-Confidence, Conflicting Constraints, SKU Not Found, Unresolvable Candidate), so recovery UI doesn't get reinvented five times.

Screens never import another screen's `Notifier`. A hand-off is always: current screen calls `ValueBrewNavigator`, which carries a typed payload, which the destination screen's own `Notifier` consumes on init — this is the code-level shape of "navigation carries context between screens that reason; it never reasons itself."

---

## 8. Repository Layer

The repository layer's sole job is to make the **Beer Knowledge Base/Catalog Platform Service** available to every Module without any Module owning it. `BeerCatalogRepository` fronts two data sources — a remote catalog API (source TBD, outside this document's scope) and a local cache (Section 9) — and returns domain entities only, never DTOs, so nothing above the data layer ever sees a wire format.

Two rules enforced structurally, not just by convention:

- **Regulatory volatility is a first-class repository concern.** Legal Price is explicitly "dynamic, not static" per the Beer Knowledge Model, with a documented history of excise changes. `BeerCatalogRepository` exposes a `lastRefreshedAt` alongside every price, and callers (specifically the Price Verification and Beer Detail view-models) are required to surface staleness rather than silently trusting a cached number — this is the direct implementation of the canon's own instruction not to imply more certainty than the input supports.
- **Nothing session-only ever reaches this layer.** `PreferenceSummary` and `ObservedPrice` are constructed, used, and discarded entirely within the presentation/domain layers of a single interaction. They are never passed to any repository method — there is no method signature that would accept them.

---

## 9. Local Storage Strategy

Local storage exists for exactly one purpose: an **offline-readable cache of catalog knowledge** (Beer, Sku, LegalPrice, StyleBenchmark) — not for session state.

- **Recommendation:** `drift` (SQLite) for the catalog cache, since it's genuinely relational (Beer → Sku → Style, Style → Benchmark) and benefits from queryable indexes for search.
- **Refresh cadence** tied to the data's own volatility classification from the Beer Knowledge Model: Regulatory (price) refreshed on a short, explicit cycle; Physical (ABV, size) refreshed less often but still periodically, since the canon flags SKU facts as "point-in-time, not eternal" given reformulation risk.
- **What is explicitly *not* stored locally, ever:** Preference Summary, candidate comparison sets, in-progress SKU selection, Observed/Charged Price, anything resembling a user profile. This isn't an oversight to fill in later — it's the direct implementation of the ADR's "No accounts exist" decision. If a future engineer proposes adding any of these to local storage, that proposal is itself a canonical change and belongs in the ADR before it belongs in code.

---

## 10. Dependency Injection

Riverpod's provider graph serves as DI directly — no separate `get_it`/`injectable` layer at MVP scale. Repositories and use cases are exposed as providers; `Notifier`s declare their dependencies via `ref.read`/`ref.watch`. This keeps the dependency graph declarative and testable (providers are trivially overridable in tests) without adding a second framework a one-person team would have to maintain in parallel with Riverpod's own object lifecycle.

Revisit if the team grows past ~2–3 engineers working on independent Modules concurrently — at that point a more explicit module-boundary DI convention earns its cost (Section 18).

---

## 11. Error Handling Philosophy

Two categories, deliberately kept separate in code because the canon treats them as conceptually different things:

- **Canonical Recovery States** (Low-Confidence Response, Conflicting Constraints, SKU Not Found, Unresolvable Candidate, and Price Verification's flagged-but-unresolved "imprecise charged price" gap) are **domain-level states, not exceptions.** They're represented as variants of each screen's sealed state class, returned from a use case as a normal, expected outcome — never thrown, never caught. This matches the canon's own framing: a Recovery State is "a complete, honest answer," not a failure.
- **Technical/infrastructure errors** (no network, malformed API response, cache corruption) are a separate, generic layer — a `Result<T, AppFailure>` type returned from repository calls, handled with ordinary retry/offline-fallback UI. These are never mapped onto a canonical Recovery State, because doing so would misrepresent a plumbing problem as a product-level honesty mechanism, diluting exactly the distinction the canon draws.

A `Notifier` that receives a technical failure while, say, generating a recommendation shows a generic "couldn't reach the catalog, try again" state — it does not relabel this as Low-Confidence Response, which has a specific, different meaning and a specific, different resolution path.

---

## 12. Logging Strategy

An abstract `Logger` interface, local-only (`debugPrint`/file-backed) at MVP stage, with no remote log aggregation wired in yet. Two constraints, both derived from the canon rather than generic best practice:

- Logs must never become a shadow persistence layer for Preference Summary or Observed Price — logging "user stated budget ₹250" across sessions would quietly recreate the account-shaped profile the ADR explicitly rejected. Logging is scoped to diagnosing *engine reasoning* (which Hard/Strong/Soft inputs a given Recommendation run actually used), not to reconstructing a person's history.
- Reasoning logs should be structured enough to answer "why did the engine ask this question" or "why was this a Trade-off and not a winner" during development, directly supporting the Recommendation Principles' explainability requirement — for the engineer's own debugging, not just the end user's.

---

## 13. Analytics Integration Philosophy

The canon's own Screen Specification Template marks **Telemetry Hooks as an explicit placeholder** ("no events are defined at this layer... until a dedicated analytics framework is established"). The implementation honors that literally: an abstract `AnalyticsSink` with a no-op default implementation is threaded through the app from day one, so the *call sites* exist (a `Notifier` can call `analytics.track(...)`) without any concrete event schema being hard-coded into screen or widget code. When a dedicated analytics standard is eventually ratified at the canonical layer, only the `AnalyticsSink` implementation changes — no screen code needs to be touched or re-reviewed.

---

## 14. Testing Strategy

The single highest-leverage testing idea in this document: **every Screen Contract's Acceptance Criteria and every Recommendation Principle is already written as a testable assertion.** Treat them as a literal test-writing source.

- **Domain/unit tests** — one test (or small group) per Acceptance Criteria bullet and per Recommendation Principle, e.g. "a recommendation must never violate a Hard Constraint," "no more than one question is ever active at a time," "confidence is never expressed as a single blended figure." These tests exist independent of any UI and should be written *before* the corresponding use case, not after — this is the canon's own "governance first" pattern carried into code.
- **State machine tests** — for each screen's sealed state type, assert every permitted transition succeeds and every forbidden transition is structurally unrepresentable (a compile-time check where possible, a unit test where not).
- **Navigation tests** — assert every method on `ValueBrewNavigator` corresponds to a legal Transition Contract entry, and assert (via static analysis or a simple reflection-based test) that no other navigation path exists in the codebase.
- **Widget/golden tests** — for the shared cross-cutting widgets (`ConfidenceBadge`, `ExplanationPanel`, `TradeoffCard`) specifically, since a visual regression there silently affects every screen at once.
- **Integration tests** — end-to-end journeys matching the Feature Inventory's own named compositions (No-anchor budget-led, Anchor already known, Explicit price check, Explicit comparison, Planning ahead).

---

## 15. Offline-First Considerations

The canon's own data model draws a sharp line between what's cacheable and what isn't, and the offline strategy follows that line exactly:

- **Cacheable, offline-safe:** Beer identity, Legal Price, ABV, size, Style Benchmark — all Verified or Computed Facts, all catalog-scoped, all safe to read from local storage with a visible "last updated" marker.
- **Never offline-relevant, by definition:** Preference Summary and Observed Price are session-only regardless of connectivity — there's nothing to sync, because there's nothing stored.
- **Degraded-but-honest behavior when offline:** Beer Detail and Price Verification should remain usable against the last cached Legal Price, with the staleness surfaced through the same Confidence Communication mechanism used everywhere else — not a generic "offline" banner that's disconnected from the product's own honesty discipline. Full Recommendation and Comparison, which reason across the whole catalog, should degrade to "cached catalog as of [date]" rather than failing outright, since a slightly stale catalog is a confidence problem the product already has a vocabulary for, not a new failure mode to invent.

---

## 16. Build Configuration

- **Flavors:** `dev`, `staging`, `prod` via native Flutter flavors, each pointing at a distinct catalog API base URL (`--dart-define=API_BASE_URL=...`).
- **CI (solo-founder-appropriate):** a single GitHub Actions workflow running domain-layer tests (Section 14) on every push, widget tests on PRs, and a release build only on tag — no elaborate multi-stage pipeline until there's a second engineer to justify the maintenance cost.
- **Static analysis:** `very_good_analysis` or an equivalent strict lint set, with null-safety and sealed-class exhaustiveness checks doing real work here given how much of this architecture leans on "illegal states unrepresentable."

---

## 17. Environment Management

- Secrets and endpoints via `--dart-define` / `.env`-style config, never committed; a `dev`-flavor default pointing at a local or mocked catalog so the app is runnable without live credentials.
- **Feature flags**, not for A/B testing infrastructure, but specifically to let engineering build ahead of a Feature Inventory tier without shipping it live — e.g., Beer Comparison as a standalone destination or "Why"/Learning Query Handling can be built and merged behind a flag, then turned on once the founder is ready to treat it as promoted, matching the canon's own rule that promotion "requires real usage evidence, never internal enthusiasm alone." The flag is the implementation-side seam for a decision the canon already says belongs to product judgment, not to engineering.

---

## 18. Scalability Considerations

- **Module boundaries in `features/` are deliberately the same boundaries the canon already drew** (Discovery, Verification, Recommendation, Comparison), because that's the seam most likely to become a team boundary later — each Module's `domain/data/presentation` triplet can become an independently owned package (`melos` monorepo) without restructuring, if and when a team forms.
- **Mechanisms are cheap to add by design.** Because the canon treats Search, Browse, Barcode Scan, and Image Recognition as implementation-free "Mechanisms" serving one Experience (Beer/SKU Identification), the domain layer should expose `IdentifyBeerSku` as a single use case accepting a `SkuIdentificationQuery` (a sealed type with `TextQuery`/`BarcodeQuery`/`ImageQuery` variants), so a new mechanism is a new variant and a new data-source adapter — never a change to Recommendation, Comparison, or any other Module.
- **The repository layer is the seam for a future backend.** Nothing in the domain or presentation layers should ever assume a specific API shape; if the catalog source changes (a different backend, a different regulatory data pipeline), only `BeerCatalogRepository`'s implementation changes.
- **Accounts remain structurally absent, not just unbuilt**, per Section 9 — this is a scalability decision as much as a privacy one: it keeps the entire app session-shaped, which is dramatically simpler to reason about and test than a persisted-state app would be, for as long as the canon holds that line.

---

## 19. Coding Principles

- **Single Responsibility, applied at the class level the same way the canon applies "Owns/Does Not Own" at the screen level.** A `Notifier` never computes a Recommendation; a repository never applies a Hard Constraint; a widget never calls another screen's use case directly.
- **Every non-trivial domain type carries a doc-comment citation** to its first canonical source (e.g., `/// See Beer Knowledge Model, Section 1.` on `Sku`), continuing the traceability discipline the canon already applies to every document field.
- **Illegal states are made unrepresentable wherever Dart's type system allows it** — sealed classes for constraint tiers, screen states, and recommendation outcomes (winner / Trade-off / Tie), rather than enums-plus-nullable-fields that can be constructed in invalid combinations.
- **No silent gap-filling in code, mirroring the canon's own rule for documents.** Where an engineer hits one of the two open items (Section "Implementation Risks" below) or the navigation inconsistency, the correct response is a visible `// TODO(ADR-open-item): ...` referencing the specific open item, plus a deliberately conservative, clearly-labeled placeholder behavior — never a confident-looking implementation that happens to guess the eventual resolution correctly.
- **No feature ships because it's easy, only because a Feature Inventory tier justifies it** — the engineering-side restatement of the Feature Inventory's own Principle 3.

---

## 20. Mapping: Engineering Specifications → Flutter Modules

| Canonical Screen / Concern | Spec Status | Flutter Module | Notes |
|---|---|---|---|
| Home | Engineering Spec complete | `features/discovery` (entry) | Routes to Recommendation, Price Verification, or Search/Browse Results only, per Navigation Contract §10. |
| Search/Browse Results | No canonical Screen Contract (flagged gap) | `features/discovery` | Build conservatively; keep logic minimal since the contract it implements against doesn't yet exist. Flag in code per Navigation Contract §14. |
| Recommendation | Engineering Spec complete | `features/recommendation` | Owns Confirm-as-Is, Planning Mode, Proxy-Buying Mode as attached behaviors, not separate screens. |
| Beer Detail | Engineering Spec complete | `features/discovery` | Never computes a Verification Delta or a Recommendation itself — hands off. Flag the Recommendation-return-edge inconsistency (see Risks) at the navigator method level. |
| Comparison | Engineering Spec complete | `features/comparison` | Beyond-two-candidate behavior is an open item — see Risks; implement for exactly two until resolved, with the UI structurally preventing a third candidate rather than silently degrading. |
| Price Verification \| Engineering Spec complete \| `features/verification` \| Domain and presentation layers may both be built directly from the specification, following the same pattern as Home, Beer Detail, Recommendation, and Comparison. The specification's own flagged gap — how an imprecise or approximate charged price should be handled — remains open per the canon's citation-only discipline, and must be represented as an explicit Recovery State (Section 11), never resolved by inference. \|
| Navigation Contract | Complete | `navigation/value_brew_navigator.dart` | One method per Transition Contract entry, per Section 4 above. |
| Recommendation Explanation, Confidence Communication | Cross-cutting Features | `shared_presentation`, `core/confidence` | Never re-implemented per-screen. |
| Beer Knowledge Base/Catalog, Style Benchmark | Platform Services | `catalog/` | Owned by no Module, depended on by all. |

---

## Implementation Risks

- **Price Verification's Engineering Specification exists but still flags an open item.** The specification does not resolve how an imprecise or approximate charged price should be handled — this remains an explicit, undecided gap in the canon. Building input-handling logic that silently picks a resolution (rounding, requiring exact figures, accepting any input) would be the implementation, not the specification process, closing a gap it was never authorized to close.
- **The two carried-forward open items — beyond-two-candidate Comparison logic and occasion-input scope — are reachable from real user flows.** If not enforced architecturally (structurally limiting Comparison to two candidates; keeping occasion entirely out of `PreferenceInputHandling`'s Core-tier code path), an engineer will resolve them ad hoc under deadline pressure, and that resolution will look like a design decision to everyone downstream.
- **The Beer Detail → Recommendation navigation inconsistency is unresolved between two frozen documents.** Coding *either* direction as if it were settled bakes in a guess. The navigator method for this specific edge should be either omitted entirely or explicitly gated behind a comment pending formal resolution — not implemented on inference.
- **Regulatory price staleness is an operational risk, not just a technical one.** If the legal price refresh pipeline lags, the product's single highest-confidence capability silently degrades without anyone noticing unless staleness is surfaced deliberately (Section 15).
- **Scope creep via Flutter idiom.** Flutter makes certain nice-to-haves (animations, micro-interactions, "just one more field") cheap to add; none of them are licensed by a Feature Inventory tier. The Core V1 boundary is a product decision this document does not get to loosen.
- **App store compliance for alcohol-related content is untracked.** ValueBrew recommends, compares, and prices alcoholic beverages; both major app stores impose category-specific requirements (age-gating/verification, content-rating declarations, a published privacy policy) that nothing in this document currently assigns an owner to. Tracked here as a release-readiness risk, owned by Milestone 9 in the Implementation Bootstrap Plan — not a reason to change anything the app does.
- **No committed decision or owner yet exists for the Beer Knowledge Base's backend/data source.** Milestone 2 (Catalog Platform Service) can proceed against a stubbed or mocked remote source without this being resolved, so it does not block implementation start. It is tracked here, explicitly, as an open external dependency this document takes no position on — see Implementation Assumptions below — and should be assigned an owner and a target decision point before the milestones that depend on real catalog data (M6 onward) are reached.
---

## Implementation Assumptions

- The Beer Knowledge Base's backend/data source is not yet decided; this document assumes a network API exists or will exist, fronted entirely by `BeerCatalogRepository`, and takes no position on its technology.Tracked as an owned, milestone-linked risk under Implementation Risks above, not left as a background assumption alone.
- Riverpod is recommended in the absence of an existing founder preference; if one exists, it should be confirmed before Section 3 is treated as settled.
- No accounts, ever, per the ADR — this document assumes that decision holds for the entire MVP and does not scaffold anything account-shaped "just in case."
- Single-market regulatory scope (the canon's own evidence base is Karnataka-specific); this document assumes no near-term multi-jurisdiction requirement, which would otherwise complicate the Legal Price refresh model in Section 8.

---

## Recommended Build Order

1. **Domain layer + canonical-rule unit tests first** — encode the Acceptance Criteria and Recommendation Principles as executable tests before any UI exists, continuing the project's own "governance before construction" sequencing into engineering.
2. **Catalog repository + local cache** (Section 8–9) — nothing else can be demonstrated without it.
3. **Navigation Contract enforcement wiring across all screens, plus the illegal-navigation tests** — built before any screen, since Home cannot legally navigate anywhere without this layer already in place.
4. **Discovery Module**: Home → Search/Browse Results → Beer Detail — the foundation every other flow enters through.
5. **Verification Module**: Price Verification, scaffolded at the domain layer only until its Engineering Specification exists; presentation deferred (see Risks).
6. **Recommendation Module** — the most complex reasoning surface; build once Discovery and the catalog are stable.
7. **Comparison Module** — depends on Recommendation's Trade-off/Tie machinery; build after it.
8. **Cross-cutting presentation**: `ExplanationPanel`, `ConfidenceBadge`, `TradeoffCard`, `RecoveryBanner` — extract these the moment a second screen needs one, not before.
9. **Offline hardening, build flavors, CI** — last, once the behavioral surface is stable enough that polishing it is worth the time.

---

## Repository Structure

```
valuebrew/
├── architecture/                 # Existing canonical + engineering docs (unchanged)
│   ├── current/
│   └── archive/
├── app/                           # This is the new Flutter application repository
│   ├── lib/                       # Per Section 5 above
│   ├── test/
│   │   ├── domain/                # Canonical-rule tests, mirrored to Screen Contracts
│   │   ├── widget/
│   │   └── integration/
│   ├── docs/
│   │   └── 20-Flutter-Implementation-Architecture.md   # This document
│   ├── pubspec.yaml
│   └── analysis_options.yaml
```

Keeping `architecture/` and `app/` as siblings (rather than nesting one inside the other) preserves the canon's own stated intent — that the architecture is "platform independent" and shouldn't live inside, or be perceived as owned by, any one implementation.

---

## Future Refactoring Opportunities

- **Package-per-Module**, via a `melos` monorepo, once a second engineer joins and needs to own a Module (Recommendation, say) without merge contention against Comparison.
- **A dedicated rules layer for the constraint engine**, if Hard/Strong/Soft evaluation logic grows past what a handful of use case methods can hold cleanly — a small internal rules/DSL abstraction, not a rewrite, once the Decision Engine Model's actual complexity is known from real usage.
- **A real sync engine** for the catalog cache, if the backend ever supports push-based updates, replacing the pull-based TTL refresh in Section 9.
- **Accessibility and Telemetry layers**, the moment the canon itself graduates those from placeholders (Screen Specification Template §11–12) to defined standards — the `AnalyticsSink` seam (Section 13) and semantic-widget hygiene should make this additive, not a rewrite.
- **Formal state persistence**, only if and when the ADR's "No accounts exist" decision is itself revisited at the canonical layer — never before, and never as an engineering-led decision.
