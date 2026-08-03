# ValueBrew — Version 1 Architecture Reference

**Repository path:** `docs/engineering/Version-1-Architecture-Reference.md`
**Status:** Frozen — describes the repository exactly as implemented at Version 1.
**Relationship to the rest of this folder:** `implementation/20-23` are pre-implementation planning documents — they describe what was *intended* to be built, in what order, against a larger eventual scope (including Comparison and Search/Browse Results). This document is different in kind: it describes what was *actually* built, and only what was actually built. Where the two differ, this document is authoritative for Version 1's real behavior; the planning documents remain historically accurate as a record of original intent.
**Relationship to the Canonical Architecture:** every claim below traces to a citation in `docs/architecture/current/`. This document restates canon in implementation-facing terms; it never reinterprets it. Where V1 implements a deliberate subset of a canonical capability, that is stated explicitly, not silently narrowed.

---

## 1. Product Overview

ValueBrew is a decision engine that helps a beer buyer in Karnataka choose the best beer for their own budget and preferences (Product Definition Document §1). Version 1 implements a real, working slice of that engine: a person states a budget, optionally narrows by style, and receives an honest, explained recommendation — including an honest disclosure when multiple beers are genuinely tied, never an arbitrary pick. From there, they can view full details on any recommended beer, and independently check whether the price they were charged for a specific beer matches the legal reference price.

**What Version 1 solves:** the two highest-confidence capabilities the Product Definition Document names as Essential — Legal Price Verification and Alcohol-Adjusted Value Comparison — plus simple, explicit budget/style preference handling and an honest recommendation output, including the canonically-required tie-handling behavior.

**What Version 1 intentionally does not do:** it does not let a person search or browse the catalog directly (no Screen Contract exists for this in the canon); it does not compare multiple named beers side by side; it does not resolve a conflict between two simultaneously-stated preferences (Trade-off Explanation); it does not independently re-affirm an already-known beer (Confirm-as-Is); it does not accept preferences beyond budget and style; it does not build any account, login, or cross-session persistence, consistent with the Product Definition Document's explicit rejection of accounts. Each exclusion is grounded in repository or canon evidence in Section 9.

---

## 2. Navigation Graph

```
Home ──homeToRecommendation({isPlanning})──> Recommendation
Recommendation ──recommendationToBeerDetail(skuId)──> Beer Detail
Beer Detail ──beerDetailToPriceVerification(skuId)──> Price Verification
```

**Every screen:** Home, Recommendation, Beer Detail, Price Verification.

**Every edge, with its parameter:**
- `Home → Recommendation` — `homeToRecommendation({bool isPlanning = false})`. One edge, not two: Planning is a flagged variant of the same transition, per the Home Screen Contract's own language — "not a fourth distinct destination." Home offers this edge from two actions ("Get a recommendation," "I'm planning ahead"); both call the identical method, differing only in the flag.
- `Recommendation → Beer Detail` — `recommendationToBeerDetail(String skuId)`. Reachable from a `RecommendationFound` outcome's own SKU, or from any one candidate of a `RecommendationTie` — the same method, called once per tied candidate's own button.
- `Beer Detail → Price Verification` — `beerDetailToPriceVerification(String skuId)`. Invitation-only: a plain button, never automatic, consistent with Segment-Appropriate Restraint as Beer Detail's own contract cites it.

**Navigation ownership:** `ValueBrewNavigator` is the only class permitted to trigger a screen transition. Every edge above is one method, added only once a real screen needed it — there is no route table, because no edge yet has more than one caller or more than one destination to justify one.

**Why IDs cross navigation boundaries, never computed values:** every edge above takes a `String` id (or, for Planning, a `bool` flag) — never a `Sku`, `Beer`, or `RecommendationResult`. Two independent reasons converge on this: it matches the "prefer IDs over embedded objects" convention followed throughout; and it matches Information Architecture's ownership rule that a fact is *referenced*, never *re-hosted*, across a screen boundary (§7: "Legal price... Beer Detail is the canonical display home; Price Verification references it rather than re-hosting it"). Every destination screen independently re-resolves its own data from the one `Catalog` in scope, via `catalog_lookups`, rather than trusting a copy handed across navigation — so no screen can ever display a stale fact its origin screen already had a fresher version of.

---

## 3. Screen Responsibilities

### Home

**Owns:** initial intent capture and routing, for the two intents actually wired — a direct recommendation request, and a planning-ahead request.

**Does not own:** any recommendation, verification, or comparison logic (Home Screen Contract, MUST NEVER); Search/Browse or Price Verification routing (not yet built — see Section 9).

**Inputs:** none.

**Outputs:** a navigation call to Recommendation, optionally flagged for Planning Mode.

**Dependencies:** `ValueBrewNavigator`.

---

### Recommendation

**Owns:** budget and style preference collection; invoking `generateRecommendation`; rendering whichever `RecommendationOutcome` results, including a genuine tie; Style refinement; the Planning Mode caveat, shown continuously alongside every outcome type when active.

**Does not own:** Beer Detail's full per-SKU facts (only enough is shown to identify a recommended or tied candidate); Price Verification's computation; Comparison's multi-candidate reasoning (not built).

**Inputs:** an optional `isPlanning` flag, carried from Home.

**Outputs:** a navigation call to Beer Detail, per the recommended SKU or per any tied candidate.

**Dependencies:** `catalogProvider`, `generateRecommendation`, `ValueBrewNavigator`, `display_formatting` (for the Planning caveat's neighboring formatted values and, since the loading/error consistency fix, for none directly — loading/error now route through `SkeletonBox`/`ErrorStateView`).

---

### Beer Detail

**Owns:** the complete presentation of one identified SKU — beer identity, price, ABV, volume, package, Value Score, verdict, and price staleness (`priceLastChecked`).

**Does not own:** the verification delta computation (Price Verification's job, even though this screen links into it); multi-candidate comparison logic; any recommendation logic.

**Inputs:** `skuId`.

**Outputs:** a navigation call to Price Verification, invitation-only.

**Dependencies:** `catalogProvider`, `catalog_lookups` (`resolveSku`, `resolveBeer`, `resolveStyle`), `display_formatting`, `ErrorStateView`, `SkeletonBox`.

---

### Price Verification

**Owns:** the verification delta for exactly one SKU and one reported charged price — classified as at, below, or above the legal reference, with the three confidence dimensions the Screen Contract names (identification, legal reference, verification outcome) stated as plain text.

**Does not own:** any broader recommendation or comparison logic; Beer Detail's fuller facts, referenced here only as context (beer name, legal price).

**Inputs:** `skuId`.

**Outputs:** none currently wired — the optional `Price Verification → Beer Detail` hand-off (a MAY in its own contract) is not built; the platform back gesture already satisfies "return to Beer Detail."

**Dependencies:** `catalogProvider`, `catalog_lookups` (`resolveSku`, `resolveBeer`), `verifyPrice`, `display_formatting`, `ErrorStateView`, `SkeletonBox`.

---

## 4. Domain Responsibilities

**`generateRecommendation`** — pure Dart, zero Flutter dependency. Filters the catalog by budget (a Hard Constraint), then optionally by style (a Strong Preference), then ranks by Value Score, detecting an exact tie via a single-pass accumulation rather than an arbitrary first-match pick. Exists as the sole implementation of the Full Recommendation synthesis the Recommendation Framework and Decision Engine Model describe, kept independent of any UI so every rule is unit-testable without a widget. Owned here, not in the presentation layer, because the Recommendation Screen Contract names Recommendation as owning "the Full Recommendation synthesis" outright — duplicating any part of this reasoning in a widget would violate that ownership.

**`verifyPrice`** — pure Dart. Computes the three-way classification (at/below/above the legal reference) the Beer Knowledge Model itself defines as the "verification delta." Owned exclusively by the Price Verification domain layer, since Observed/Charged Price is explicitly excluded from Beer Detail's own composition.

**`RecommendationOutcome`** (sealed: `RecommendationFound`, `NoRecommendationWithinBudget`, `NoRecommendationMatchingStyle`, `RecommendationTie`) — a single exhaustive switch, not per-subclass overrides, deliberately built so a future outcome variant cannot be added without the compiler forcing an explicit decision about its refinability. This is not a theoretical property: it was directly exercised when `RecommendationTie` was added, which forced both `canBeRefinedFurther`'s switch and the presentation-layer rendering switch to be updated in the same commit — exactly the discipline the design was built to enforce.

**`RecommendationResult`** — `sku` + `beer` + `explanation`. Embeds fully-resolved objects, not bare ids, because `generateRecommendation` already holds the entire `Catalog` in scope and this is its own internal return value, never a navigation boundary — the "prefer IDs" rule governs crossing screens and serialization, not a domain function's own result shape.

**`RecommendationTie`** — `candidates` (a `List<TiedCandidate>`) + `explanation`. Exists because a tie cannot be represented by `RecommendationFound`'s shape (a single winner) without reintroducing nullable, implicit state exactly where the sealed hierarchy exists to prevent it.

**`TiedCandidate`** — `sku` + `beer` only, deliberately without an `explanation` field: a tied candidate has no valid "why this one" content, since the entire point of a tie is that no candidate is individually preferred. The tie's own explanation covers the set; nothing per-candidate is missing by this field's absence.

**`PriceVerificationResult`** — `verdict` + `chargedPrice` + `legalPrice` + `explanation`, a flat class, not a sealed hierarchy. The Beer Knowledge Model defines the verification delta as a classification alone, not as three differently-shaped outcomes — there is no per-verdict data to justify branching the type.

---

## 5. Shared Infrastructure

**`catalogProvider`** — the single `FutureProvider<Catalog>` every screen reads from. Composes `catalogRepositoryProvider`; never reimplements loading or parsing.

**`catalog_lookups`** — `resolveBeer`, `resolveStyle`, `resolveSku`, `resolveSkus`, `bestSkuForBeer`, `cheapestSkuForBeer`: pure, null-returning functions, the only place any id-to-object resolution happens against a loaded `Catalog`. `generateRecommendation` was itself consolidated onto `resolveBeer`/`resolveStyle` rather than keeping its own inline lookups, once it became a second real consumer.

**`display_formatting`** — extension methods on domain types (`CurrencyFormatting`, `VolumeFormatting`, `PackageTypeFormatting`, `ValueVerdictFormatting`, `PriceVerificationVerdictFormatting`) — the only place a raw domain value becomes display text. Each new enum-to-label need was added here, never inlined, once an equivalent extension already established the pattern.

**`ValueBrewNavigator`** — described fully in Section 2. The one class allowed to trigger a transition; its public API is exactly the Navigation Contract's edge list.

**`ErrorStateView`** — the shared error state for every async screen. By its own documented contract, it never renders a raw exception or stack trace — a screen's `.when(error: ...)` callback must already have turned the error into a human-readable message before it reaches this widget.

**`SkeletonBox`** — the app's entire skeleton-loading primitive: one pulsing placeholder box, composed per-screen into a layout roughly matching that screen's real content. Deliberately not a shared "detail skeleton" — each screen's real layout differs enough that a generic skeleton would misrepresent it.

---

## 6. Design Principles

Each stated only because it was actually exercised in this repository, with the instance that demonstrates it:

- **Screens never compute another screen's logic.** Beer Detail never computes a Value Score; Price Verification never recommends an alternative.
- **IDs cross navigation boundaries, never computed objects.** Every `ValueBrewNavigator` method signature.
- **Formatting belongs in `display_formatting.dart`.** `PriceVerificationVerdictFormatting` was added there, not inlined in the Price Verification screen, mirroring `ValueVerdictFormatting`'s existing placement.
- **Lookups belong in `catalog_lookups.dart`.** `resolveSku` was added there for Beer Detail; `generate_recommendation.dart`'s own inline `firstWhere` calls were later consolidated onto `resolveBeer`/`resolveStyle` once a second real consumer existed.
- **Presentation owns only presentation.** `_RecommendationOutcomeView` knows nothing about navigation — it exposes a callback and lets its parent own the navigator call.
- **Domain owns business reasoning.** `generateRecommendation` and `verifyPrice` have zero Flutter import between them.
- **Compiler-enforced evolution is preferred over nullable state.** When Tie Disclosure was designed, a nullable "tied-with" field on `RecommendationFound` was considered and rejected in favor of a new sealed case, specifically because the nullable version wouldn't force any renderer to handle it.
- **No speculative abstractions.** `PriceVerificationResult` stayed a flat class — a sealed hierarchy was considered and rejected because the Beer Knowledge Model's own definition of the verification delta gives no per-outcome differentiated data to justify one.
- **Reuse before extraction.** Tie Disclosure's per-candidate "See full details" buttons reuse the exact callback (`onSeeFullDetails`) and navigator edge (`recommendationToBeerDetail`) `RecommendationFound` already used — no new callback, no new edge.
- **Extraction happens after a third genuine consumer, not before.** The near-identical `_listEquals` helper in `Catalog` and `RecommendationTie` was explicitly left unextracted, with the concrete trigger for extraction (a third class needing list equality) named rather than acted on speculatively.

---

## 7. Testing Philosophy

**Unit testing:** every pure domain function (`generateRecommendation`, `verifyPrice`, each `catalog_lookups` function) is tested directly, with no widget pump — deterministic, side-effect-free logic stays fully testable without Flutter.

**Widget testing:** every screen is pumped via `ProviderScope` overriding `catalogRepositoryProvider` with a fake `CatalogRepository`, inside a `MaterialApp` wired to the real `rootNavigatorKey` whenever a test needs to exercise navigation.

**Behavior vs. implementation:** every assertion targets rendered text, a widget's presence/absence, or a returned domain value — never a private `State` field or a direct call into a private method.

**Observable assertions, not proxy assertions:** a loading-state test must assert `SkeletonBox` presence directly, not merely that final content is absent — this distinction was found missing once, in Beer Detail's first loading test, and fixed; every skeleton test since has followed the corrected pattern.

**State preservation:** every navigation edge has a dedicated back-navigation test confirming the origin screen's state — a selected Style, an entered budget, a rendered tie — survives the round trip rather than being silently rebuilt from scratch.

**Navigation testing:** every edge is tested for its *correct, specific* destination content (e.g., the correct beer name on the far side of a tied candidate's button), never only that "some navigation occurred."

**Fixture strategy:** JSON catalog fixtures are deliberately duplicated per test file and per scenario rather than shared, since each screen's tests need a differently-shaped catalog. A shared Dart-object test builder was considered for two near-identical domain-test helpers and explicitly deferred, with its own trigger (a third consuming test file) named rather than acted on early.

**Duplication policy:** identical in spirit to Section 6's "extraction after the third consumer" — applied to test code exactly as it is to production code.

---

## 8. Repository Conventions

**Constructors:** `const` wherever the constructor body allows it, even for types (like `RecommendationFound` or `RecommendationTie`) that are, in practice, never actually invoked as a compile-time constant — consistency with sibling types matters more than whether any real call site benefits.

**`const` usage:** applied to every literal and constructor invocation that can be `const`, consistently across all new-architecture code.

**Equality:** hand-rolled `identical(this, other) || (other is X && ...field comparisons)` on every domain type — no `package:equatable`. List-valued equality (`Catalog`, `RecommendationTie`) uses a hand-rolled, private, non-generic `_listEquals` — no `package:collection` — specialized to each class's one actual list field rather than written generically for a genericity no second field within that class needs.

**`hashCode`:** `Object.hash`/`Object.hashAll`, always covering exactly the same fields `==` compares, never more or fewer.

**`toString`:** abbreviated identifying information (an id, a name) rather than a full nested-object dump, consistently.

**Private widgets:** leading underscore, defined in the same file as their sole consumer, promoted out of that file only once a second real consumer exists (none has yet, for any private widget in this codebase).

**File placement:** a domain "payload" type that belongs to exactly one outcome (`RecommendationResult` for `RecommendationFound`, `TiedCandidate` for `RecommendationTie`) lives in its own file, separate from the outcome/hierarchy file that references it — a repeated, deliberate convention, not a one-off.

**Extension placement:** every formatting extension lives in the one file, `display_formatting.dart`, regardless of which feature introduced it.

**Documentation style:** doc comments explain *why*, not *what* — a hidden constraint, a rejected alternative, a citation to the canonical rule being satisfied. Extension seams and deliberate simplifications are named explicitly in the doc comment of the function or class that owns them, and are corrected the moment they stop being accurate — this was caught and fixed twice in this repository's history (a stale navigator comment, a stale extension-seams list) specifically because the convention makes a false claim easy to notice.

---

## 9. Intentionally Deferred Capabilities

**Trade-off Explanation** — blocked, repository: requires two Strong Preferences stated simultaneously; only budget (Hard Constraint) and one optional style (Strong Preference) exist today. Also canon-grounded: the Recommendation Framework's own illustrative example ("style versus strength") implies the two are meant to coexist, so a scoped-down, mutually-exclusive version would misrepresent the canon rather than partially satisfy it — not attempted for that reason.

**Comparison** — blocked, repository and canon: depends on Trade-off/Tie-handling's trade-off half, which is unreachable for the same reason above; and the one entry point that *is* technically reachable today (`Recommendation → Comparison` from a genuine tie) has nothing to add, since a tie's candidates are by construction equal on every measured axis — building it would duplicate Recommendation's own tie rendering, violating Information Architecture's anti-duplication rule.

**Preference expansion (strength, size, brand)** — blocked, repository: the same missing-second-Strong-Preference dependency as Trade-off Explanation.

**Search/Browse Results** — blocked, canon: no Screen Contract exists for it among the five canonical Screen Contracts that do; the Navigation Contract states this about itself directly.

**Confirm-as-Is** — blocked, canon and repository: requires an anchor-known entry path (Search/Browse → Beer Detail) that doesn't exist; attempting it via Beer Detail reached from Recommendation would duplicate content Recommendation's own explanation already states, violating the same anti-duplication rule as Comparison above.

**Confidence Communication** (the formal Hard/Strong/Soft separation, beyond Planning Mode's own caveat) — deferred, repository, not blocked: every input Recommendation currently uses is uniformly high-confidence per the Beer Knowledge Model, so building this now would add a sentence with zero informational variance across every recommendation shown.

**Proxy-Buying Mode** — blocked, canon, explicitly: the Product Definition Document names it directly — "any accommodation for proxy buying, given the model's explicitly unknown prevalence for this behavior" — under its own "Intentionally deferred" heading, distinct from every other deferral in this list, which are architectural rather than authorial.

**Why/Learning Query Handling** — deferred, repository, not blocked: every explanation currently shown is already inline and persists across navigation; nothing exists anywhere in the app today that is hidden and would need a retrieval action.

**Low-Confidence Response** — blocked, repository: today's two-input surface (budget, one optional style) always resolves to a definite outcome; no scenario of genuine, irreducible ambiguity is reachable to build against.

---

## 10. Version 1 Boundaries

**Includes:** Home, recognizing exactly two intents (direct recommendation, planning-ahead); Recommendation, with budget and style preference handling, Tie Disclosure, and Planning Mode; Beer Detail; Price Verification. Every navigation edge, domain function, and shared infrastructure piece named in Sections 2–5.

**Excludes:** Search/Browse Results, Comparison, Trade-off Explanation, Confirm-as-Is, any preference beyond budget and style, Confidence Communication as a formal cross-cutting system, Proxy-Buying Mode, Why/Learning retrieval, Low-Confidence Response, and any account, login, or cross-session persistence mechanism.

---

## 11. Future Work Trigger

Version 2 work begins only when one of the following actually changes:

- **Repository behavior** — a new, self-documented gap or defect is discovered in what's already built.
- **Canon** — an existing canonical document is revised.
- **New Product Definition** — the Product Definition Document is revised or superseded.
- **New Screen Contract** — a canonical Screen Contract is authored for a capability that currently has none (Search/Browse Results being the standing example).

Absent one of these four, no further architecture review, milestone planning, or implementation work should be undertaken. This document remains the authoritative description of Version 1 until one of them occurs.
