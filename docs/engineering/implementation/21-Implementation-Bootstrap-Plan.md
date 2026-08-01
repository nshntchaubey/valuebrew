# ValueBrew — Implementation Bootstrap Plan

**Document Type:** Engineering Playbook (Implementation Layer) — not Product or Software Architecture
**Status:** Draft
**Sits below:** Canonical Architecture (frozen), Engineering Specifications, Flutter Implementation Architecture (v0.1, approved)
**Purpose:** prepare the repository for implementation. Nothing here writes the product — it prepares the ground it will be written on.

A note on precision before anything else, in the same spirit the canon itself insists on: package and SDK version numbers below are current as of this bootstrap, but pub.dev and the Flutter stable channel both move continuously. Where I give a specific number, treat it as "confirmed at time of writing, re-verify at `flutter create` time" — never as a number worth hand-typing into a real pubspec without checking `flutter pub outdated` or pub.dev first. Inventing false precision here would violate the same discipline the Recommendation Framework applies to its own outputs.

---

## 1. Flutter SDK Version Recommendation

**Recommendation: Flutter stable channel, currently 3.44.x** (3.44.7 as of late July 2026).

- Use **stable**, not beta or main — this is a production MVP for a solo founder, not a contribution to Flutter itself, and stable is the only channel Flutter's own team recommends for shipped apps.
- Recommend installing via **FVM (Flutter Version Management)** rather than a bare system install, and pinning the exact version in an `.fvmrc` at the repo root. This matters more for a solo founder than it looks: it means "it works on my machine" never becomes a real problem the day a second engineer, a CI runner, or a future you on a different laptop needs to build the exact same thing.
- Do **not** hand-write the Dart SDK constraint in `environment:` — let `flutter create` populate it from whatever Dart version ships with the Flutter version you actually installed, then leave it alone. Guessing this number is a common source of entirely avoidable build failures.

---

## 2. Project Creation Command

```
fvm flutter create --org com.valuebrew --platforms=android,ios --empty valuebrew_app
```

- **`--platforms=android,ios` only.** Nothing in the Product Definition Document or Behavioral Hypothesis Model evidences a web or desktop need — the product's evidence base is a person standing in front of a retail shelf. Adding platforms costs nothing to *declare* but adds real, ongoing CI and testing surface for a solo founder to carry. Add a platform later, deliberately, if evidence ever justifies it — the same discipline the Feature Inventory applies to product capabilities applies here to platform targets.
- **`--empty`** skips Flutter's default counter-app scaffold entirely, so the repository never contains throwaway sample code that has to be manually deleted before real work starts.
- **`--org com.valuebrew`** — confirm this reverse-domain identifier is actually available/intended before running; it's baked into both the Android package name and iOS bundle identifier and is painful to change later.

---

## 3. Required Packages

For every package: why it exists in this app specifically, why this one, why the alternatives were set aside. Grouped exactly as requested.

### State Management

| Package | Role |
|---|---|
| `flutter_riverpod` | Reactive state layer + DI graph (per Implementation Architecture §3, §10) |
| `riverpod_annotation` + `riverpod_generator` | Code-gen for providers, reducing hand-written boilerplate |
| `build_runner` | Generic code-gen runner, shared across Riverpod/Drift/Freezed |

**Why it exists:** every screen's canonical State Machine needs a concrete carrier in code, and Preference Summary needs a session-scoped (never-persisted) home.

**Why chosen:** Riverpod's current major line (3.x) added stronger compile-time safety and reduced boilerplate around code-generated providers — directly useful here since so much of this app's correctness rests on the compiler catching an invalid state, not a test catching it at runtime. It also removes the need for a separate DI package (Section 10 of the Implementation Architecture already committed to this).

**Why alternatives rejected:** `Bloc`/`flutter_bloc` is a legitimate, more ceremony-heavy alternative — event classes plus state classes plus a mapping function per screen is more boilerplate than a solo founder needs to carry for the number of screens in scope. `Provider` (the plain package, Riverpod's predecessor) lacks Riverpod's compile-time safety and is effectively in maintenance mode in favor of Riverpod itself. `GetX` was rejected outright — its service-locator style state/DI/navigation bundling actively works against the Navigation Contract enforcement pattern in Section 4 below, which depends on navigation being a distinct, narrow surface, not something bundled into a general-purpose "God object" utility.

### Routing

| Package | Role |
|---|---|
| `go_router` | Declarative routing, wrapped by `ValueBrewNavigator` |

**Why it exists:** the Navigation Contract is a closed, named graph of legal transitions; something has to actually move the user between screens.

**Why chosen:** it's the Flutter team's own recommended declarative router, has first-class support for typed route parameters and `extra` payloads (used to carry SKU identity and candidate sets per Section 4 of the Implementation Architecture), and its redirect/guard hooks are a natural place to enforce entry-point rules like "Home is never a backward destination" at the framework level, not just by convention in the wrapper.

**Why alternatives rejected:** `auto_route` adds its own code-gen layer on top of routing for marginal benefit here, given the screen count is small and fixed (six screens, a closed graph) rather than large and dynamic. Hand-rolled `Navigator 2.0` was rejected as strictly more boilerplate for the same outcome, with no compensating benefit given `go_router` already provides everything the `ValueBrewNavigator` wrapper needs.

### Local Database

| Package | Role |
|---|---|
| `drift` + `drift_flutter` | Type-safe local cache for the Beer Knowledge Base/Catalog |
| `sqlite3_flutter_libs` | Native SQLite binaries drift needs on mobile |

**Why it exists:** Section 9 of the Implementation Architecture calls for an offline-readable catalog cache (Beer → Sku → Style → Style Benchmark) — this is genuinely relational data, not a flat key-value store.

**Why chosen:** drift generates type-safe queries and reactive streams from Dart table definitions, and its relational model matches the Beer Knowledge Model's own domain shape (a Beer groups Skus; a Style anchors a Benchmark) far better than a document/key-value store would. It's also the most actively maintained SQLite layer in the current Flutter ecosystem.

**Why alternatives rejected:** `Hive` is lighter-weight but fundamentally a key-value store — expressing "all SKUs within a Style, ranked by value" would mean hand-rolling in-memory joins Drift gets natively. `Isar` had a period of maintainer uncertainty industry-wide; given this app's catalog-refresh and query needs don't require Isar's specific performance profile, the extra risk isn't worth taking for an MVP. Raw `sqflite` was rejected because it offers no compile-time query safety — exactly the "illegal states unrepresentable" discipline this project has committed to elsewhere would be absent at the one layer touching real persisted data.

### Code Generation

| Package | Role |
|---|---|
| `freezed` + `freezed_annotation` | Immutable domain entities, sealed unions for constraint tiers and recommendation outcomes |
| `drift_dev` | Drift's generator (dev-only) |
| (Riverpod/build_runner already listed above) |

**Why it exists:** Section 19 of the Implementation Architecture commits to "illegal states unrepresentable wherever Dart's type system allows it" — sealed unions for things like `HardConstraint | StrongPreference | SoftPreference` or a Recommendation outcome of `Winner | TradeoffExplanation | TieDisclosure`.

**Why chosen:** `freezed` adds generated `copyWith`, deep equality, and exhaustive `when`/`map` pattern matching on top of a union — genuinely useful for data-carrying variants (a `TradeoffExplanation` carries fields; equality matters for tests).

**Why alternatives rejected:** Dart 3's **native `sealed class`** keyword is not rejected — it's used directly, without `freezed`, for simple state-machine enums that carry no data of their own (e.g., a screen's plain lifecycle state where no `copyWith` is ever needed). `freezed` is reserved for the cases where its generated equality/copying genuinely earns its build-time cost, rather than applied uniformly out of habit.

### Testing

| Package | Role |
|---|---|
| `flutter_test` (bundled) | Unit and widget tests |
| `mocktail` | Mocking repositories/use cases in isolation |
| `integration_test` (bundled) | End-to-end journey tests |

**Why it exists:** Section 14 of the Implementation Architecture treats every Screen Contract Acceptance Criterion and every Recommendation Principle as a literal test to write.

**Why chosen:** `mocktail` gives null-safe, code-gen-free mocking — for a solo founder, one fewer generator in the `build_runner` pipeline to wait on is a real, if small, velocity win.

**Why alternatives rejected:** `mockito` requires either code generation or manual mock classes for null-safe Dart; `mocktail` gets the same capability without adding a fourth thing to `build_runner`'s job list (alongside Riverpod, Drift, and Freezed).

### Logging

| Package | Role |
|---|---|
| `logging` | Backing implementation for the abstract `Logger` interface (Implementation Architecture §12) |

**Why it exists:** diagnosing *why* the Decision Engine reasoned the way it did, during development, without creating a shadow persistence layer for anything session-scoped.

**Why chosen:** it's the Dart team's own minimal logging package — hierarchical loggers, log levels, no runtime dependencies beyond `dart:core`. That minimalism matters here specifically: Section 12 is explicit that logging must never become an accidental account-shaped store, so the smallest capable tool is the right tool, not the most feature-rich one.

**Why alternatives rejected:** third-party loggers like `logger` or `talker` add colorized console output and richer formatting that's genuinely nice, but is pure UI-of-the-logs polish this project doesn't need yet — easy to swap in later behind the same abstract interface if it ever earns its place.

### Linting

| Package | Role |
|---|---|
| `very_good_analysis` | Strict base lint set |
| `riverpod_lint` + `custom_lint` | Riverpod-specific static analysis (catches provider misuse at analyze-time) |

**Why it exists:** a lint set is the cheapest possible enforcement of "illegal states unrepresentable" and "no silent gap-filling" — catching a whole class of mistakes before a human reviewer ever has to.

**Why chosen:** `very_good_analysis` is meaningfully stricter than Flutter's own default `flutter_lints`, which matters given how much of this architecture's safety comes from the type system actually being used rigorously rather than loosely. `riverpod_lint` catches Riverpod-specific footguns (like an unused `ref`, or a provider that should be `autoDispose` but isn't) that a generic lint set can't see.

**Why alternatives rejected:** the default `flutter_lints` package (what `flutter create` ships with) was rejected as a *floor*, not a target — it's a reasonable baseline for any Flutter app, but this project's own stated discipline calls for stricter enforcement than the default.

### Utilities

| Package | Role |
|---|---|
| `intl` | Currency (₹) and number formatting for prices and alcohol-adjusted value figures |
| `collection` | Advanced collection operations (e.g., computing Style Benchmark percentiles) |
| `envied` + `envied_generator` | Type-safe, compile-time environment configuration |
| `connectivity_plus` | Network-state detection, to trigger the offline/staleness treatment in Implementation Architecture §15 |

**Why chosen (envied specifically):** it generates a typed config class from a `.env` file at build time rather than parsing one at runtime — meaning a missing or malformed key is a build failure, not a runtime crash discovered by a real user, and the `.env` file itself never has to be bundled as a Flutter asset (a common source of accidentally-shipped secrets).

**Why alternatives rejected (envied specifically):** `flutter_dotenv` was rejected because it parses the `.env` file at runtime, from an asset bundled into the app binary — which is both a minor security surface and gives no compile-time guarantee that a required variable actually exists.

---

## 4. Initial Folder Structure

```
valuebrew_app/
├── lib/
│   ├── main.dart
│   ├── app/
│   ├── core/
│   │   ├── result/
│   │   ├── confidence/
│   │   ├── logging/
│   │   └── analytics/
│   ├── navigation/
│   ├── features/
│   │   ├── discovery/
│   │   │   ├── domain/
│   │   │   ├── data/
│   │   │   └── presentation/
│   │   ├── verification/
│   │   ├── recommendation/
│   │   └── comparison/
│   ├── shared_domain/
│   ├── shared_presentation/
│   └── catalog/
│       ├── domain/
│       └── data/
├── test/
│   ├── domain/              # one subfolder per feature, mirroring lib/features
│   ├── widget/
│   └── integration/
├── assets/
│   ├── images/
│   └── icons/
├── l10n/
│   └── app_en.arb
├── analysis_options.yaml
└── pubspec.yaml
```

Notes on the pieces the request specifically called out:

- **`assets/`** — kept intentionally thin at bootstrap (images/icons only). No sample data or placeholder content committed here; the catalog is a live data concern (Section 3/8 of the Implementation Architecture), not a bundled asset.
- **`l10n/`** — scaffolded from day one even though V1 almost certainly ships English-only. Routing every displayed string through Flutter's ARB-based localization, rather than hard-coding strings in widgets, is a cheap structural bet with a direct payoff already established by the canon: the Canonical Interaction Lexicon requires exact, consistent terminology everywhere a term appears, and a single ARB file is a natural, greppable place to keep that consistent — independent of whether a second locale ever ships.
- **`analysis_options.yaml`** — lives at the repo root (not inside `lib/`), includes `very_good_analysis` and enables `custom_lint`/`riverpod_lint`, per Section 3 above.
- **`pubspec.yaml`** — described here by section, not written as a literal file:
  - **`name` / `description`** — `valuebrew_app`, one line restating the product's purpose without redefining it.
  - **`environment`** — populated by `flutter create`, per Section 1; never hand-edited.
  - **`dependencies`** — the runtime packages from Section 3 (Riverpod, go_router, drift + drift_flutter, intl, collection, connectivity_plus, logging), plus `flutter: sdk: flutter`.
  - **`dev_dependencies`** — the build-time-only packages (build_runner, riverpod_generator, riverpod_annotation stays a runtime dep since annotations are referenced at compile time — drift_dev, freezed + freezed_annotation, envied_generator, very_good_analysis, mocktail, custom_lint + riverpod_lint).
  - **`flutter:`** block — `uses-material-design: true`, `generate: true` (required for ARB-based localization), and an `assets:` list pointing at `assets/images/` and `assets/icons/`.

---

## 5. Implementation Roadmap

Milestones, not sprints — no calendar estimate is attached to any of these, deliberately. This project's own Recommendation Framework refuses to invent false-precision numbers (a fake match percentage, an unevidenced confidence score); estimating "M3 will take 6 days" would be exactly that kind of invented precision from an assistant with no actual visibility into your available hours. Complexity is given as a relative signal instead — useful for sequencing and risk conversations, not for a calendar.

### M0 — Repository & Tooling Bootstrap
**Objective:** a running, empty, correctly-configured Flutter project that builds on a real device/simulator, with CI passing on an empty test suite.
**Deliverables:** project created per Section 2; all Section 3 packages added; folder structure per Section 4; `analysis_options.yaml` configured and passing with zero violations; a minimal GitHub Actions workflow running `flutter analyze` and `flutter test`.
**Definition of Done:** `flutter run` launches a blank app on both Android and iOS; `flutter analyze` is clean; CI is green on a trivial commit.
**Dependencies:** none — this is the starting point.
**Estimated complexity:** S.

### M1 — Domain Foundations & Canonical Rule Tests
**Objective:** the shared domain vocabulary exists in code, and the Recommendation Principles / Acceptance Criteria exist as executable tests before any screen does.
**Deliverables:** `shared_domain` entities (`Sku`, `Beer`, `PreferenceSummary` and its `Constraint` sealed hierarchy, `KnowledgeTier`); `core/result` sealed `Result` type; a first batch of domain-level unit tests encoding rules like "a recommendation must never violate a Hard Constraint" against stub logic.
**Definition of Done:** every entity's doc-comment cites its canonical source section; the rule-tests exist and currently fail (red, since no real logic exists yet) or are marked pending — not skipped silently.
**Dependencies:** M0.
**Estimated complexity:** M.

### M2 — Catalog Platform Service
**Objective:** `BeerCatalogRepository` is real, backed by Drift locally and a (possibly stubbed/mocked) remote source, with staleness tracking wired in.
**Deliverables:** Drift schema for Beer/Sku/Style/StyleBenchmark; `BeerCatalogRepository` interface + implementation; `lastRefreshedAt` staleness exposed per Implementation Architecture §8; seed/test data for local development.
**Definition of Done:** the repository can be queried offline against seeded local data with correct joins (a Sku's Style Benchmark resolves correctly); staleness is asserted in a test.
**Dependencies:** M1.
**Estimated complexity:** M.

### M3 — Navigation Contract Enforcement Layer
**Objective:** `ValueBrewNavigator` exists with one method per legal Transition Contract entry, and illegal navigation is structurally absent, not just untested.
**Deliverables:** `go_router` route table for all six screens (five contracted + Search/Browse Results); `ValueBrewNavigator` wrapper; a test asserting the navigator's public API surface matches the Navigation Contract's legal-edge list exactly.
**Definition of Done:** the illegal-edge test passes; every screen (even as placeholder scaffolds) is reachable via its correct entry point only.
**Dependencies:** M0 (M1/M2 not strictly required, but typically ready by now).
**Estimated complexity:** M.

### M4 — Home
**Objective:** the product's sole entry point is real.
**Deliverables:** Home screen per its Engineering Specification; routing to Recommendation and Price Verification (and, indirectly, Search/Browse Results) via `ValueBrewNavigator`; Home's own (thin) state handling — it never reaches Decision Complete, per its contract.
**Definition of Done:** every Acceptance Criterion in Home's Engineering Specification has a corresponding passing test; Home is reachable as the app's actual launch route.
**Dependencies:** M2, M3.
**Estimated complexity:** S–M.

### M5 — Search/Browse Results & Beer Detail
**Objective:** a person can find a real beer and see its full detail, including Confirm-as-Is.
**Deliverables:** Search/Browse Results scaffold (kept conservative, flagged per its missing Screen Contract); Beer Detail screen per its Engineering Specification; `ExplanationPanel` and `ConfidenceBadge` shared widgets built here for the first time, since Beer Detail is their first real consumer.
**Definition of Done:** Beer Detail's Acceptance Criteria are all covered by tests; the two shared widgets are used by at least this one screen and are themselves unit/golden-tested in isolation.
**Dependencies:** M4.
**Estimated complexity:** M.

### M6 — Price Verification (Domain Layer Only)
### M6 — Price Verification
**Objective:** the full Price Verification screen — domain and presentation — is implemented directly from its now-complete Engineering Specification.
**Deliverables:** `VerifyPrice` use case; `VerificationDelta`/`VerificationResult` entities; the three-way confidence distinction (Section 6 of the Price Verification Screen Contract); the Price Verification screen itself, per its Engineering Specification, reusing the `ExplanationPanel` and `ConfidenceBadge` widgets first built in M5.
**Definition of Done:** domain-level tests pass; every Acceptance Criterion in the Price Verification Engineering Specification has a corresponding passing test; the specification's flagged gap — handling of an imprecise or approximate charged price — is represented as an explicit Recovery State in the UI, never silently resolved by a default input rule.
**Dependencies:** M2, M5 (for the shared `ExplanationPanel` and `ConfidenceBadge` widgets, reused rather than rebuilt).
**Estimated complexity:** S–M.

### M7 — Recommendation
**Objective:** the product's core reasoning surface is implemented.
**Deliverables:** `GenerateRecommendation` use case implementing Progressive Question-Asking, the Hard/Strong/Soft constraint engine, Trade-off and Tie detection; Recommendation screen per its Engineering Specification; `TradeoffCard`/`TieCard` shared widgets.
**Definition of Done:** every Recommendation Principle and Acceptance Criterion has a passing test; all five Feature Inventory journeys (No-anchor, Anchor-known, Planning, Proxy-buying, Explicit price check where relevant) are covered by integration tests.
**Dependencies:** M2, M5 (for hand-off to Beer Detail).
**Estimated complexity:** L — this is explicitly the most complex reasoning surface in the product.

### M8 — Comparison
**Objective:** dedicated multi-candidate comparison is implemented, deliberately bounded.
**Deliverables:** Comparison screen per its Engineering Specification; reuse of Recommendation's Trade-off/Tie machinery; a **structural limit to exactly two candidates**, since beyond-two-candidate logic is an unresolved open item — the UI should make a third candidate unreachable, not silently degrade.
**Definition of Done:** Comparison's Acceptance Criteria pass; a test explicitly asserts a third candidate cannot be added, tied to the open-item comment from Section 20 of the Implementation Architecture.
**Dependencies:** M7.
**Estimated complexity:** M.

### M9 — Offline Hardening, Release Configuration, Polish
**Objective:** the app is genuinely usable offline per Implementation Architecture §15, and is buildable for a real release.
**Deliverables:** `connectivity_plus`-driven staleness/offline UI treatments; build flavors (dev/staging/prod) with `envied`-backed config; app icons, splash, and store metadata; app store compliance for alcohol-related content (age-gating/verification, content-rating declarations, published privacy policy) confirmed against current Google Play and Apple App Store requirements.
**Definition of Done:** the app functions (Beer Detail, cached-catalog Recommendation) with connectivity disabled in a manual test; a release build succeeds for both platforms; app store compliance items are confirmed complete, not merely reviewed..
**Dependencies:** M4–M8 substantially complete.
**Estimated complexity:** M.

---

## 6. Recommended First Screen: **Home**

**Recommendation:** build **Home** first (Milestone 4 above), immediately after the M0–M3 foundation work.

**Justification, from the Engineering Specifications and Navigation Contract directly, not from general engineering intuition:**

1. **It is the only possible entry point.** The Navigation Contract states plainly that entry into the product as a whole is always Home — "there is no other first screen." Building anything else first means testing it against a mocked or hard-coded entry condition rather than the real one it will actually receive in production.
2. **Its Engineering Specification is complete** — as, now, are Price Verification's, Beer Detail's, Recommendation's, and Comparison's. Specification-completeness no longer distinguishes Home from the alternatives; Home remains the right starting point for the reasons in points 1, 3, and 4 below, not because it is uniquely spec-complete.
3. **It is the lowest-complexity screen in the canon**, by its own contract's own description — Home is "exclusively a routing screen" that never itself reaches Decision Complete. That makes it the ideal first real screen to validate the *scaffold* (the M3 navigation wrapper, Riverpod wiring, the shared widget conventions) against, before spending that validation effort on a screen that also carries real reasoning risk.
4. **It unblocks everything downstream.** Recommendation and Price Verification are both entered directly from Home; Search/Browse Results (and therefore Beer Detail and Comparison) is entered from Home indirectly. Every other milestone's "reachable via its correct entry point" Definition of Done depends on Home existing first.

**Second choice, if you want the first screen with real domain reasoning rather than pure routing:** Beer Detail. It's also fully specified and comparatively low in behavioral complexity (it never recommends, never computes a delta — Section 19 of the Architectural Decisions Record is explicit that "Beer Detail never recommends"), making it a reasonable follow-on once Home exists to route into it for real, rather than via a hard-coded test SKU.

**Explicitly not recommended first:** Recommendation (highest reasoning complexity — build order in Section 5 already sequences it after the foundation is proven) and Price Verification (now fully specified, but its presentation layer depends on shared widgets not built until M5 — see M6).
