# Changelog

All notable changes to ValueBrew are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project uses [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`,
with the Android/iOS build number as the fourth, CI-facing component).

## [1.0.0] - 2026-08-03

The canonical-architecture rebuild, built milestone-by-milestone against
the frozen Canonical Architecture (`docs/architecture/current/`). Each
bullet below is a distinct, independently-tested milestone.

### Added
- Project reorganization onto the Canonical Architecture: catalog and
  shared domain models relocated into `catalog/` and `shared_domain/`,
  the app's default launch screen switched to a new, canon-derived Home
  screen, and `ValueBrewNavigator` introduced as the sole owner of every
  screen transition — one method per legal transition, added only once a
  real screen needed it, never ahead of that need.
- Recommendation: budget-driven recommendation against the real catalog,
  with an honest explanation attached to every result.
- Style refinement: an optional Style preference, requested only after a
  budget-only recommendation exists, never gathered upfront — matching
  the canon's progressive-question discipline. Refinement is reversible
  and persists correctly across budget edits.
- Beer Detail: the complete picture of one recommended SKU (price,
  package, volume, ABV, Value Score, verdict, price staleness), reached
  from Recommendation. Presentation-only — nothing here is computed.
- Price Verification: checks one SKU's charged price against its legal
  reference price, classified as at, below, or above, with its own
  confidence framing. Reached from Beer Detail, on request.
- Tie Disclosure: when multiple beers are genuinely, exactly tied for
  the best value within budget, the app says so honestly — each tied
  beer shown individually, with its own path to full details — rather
  than silently picking one.
- Planning Mode: an alternate entry point for recommendations intended
  for a future purchase, carrying a standing caveat throughout the flow
  that prices and availability may have changed by the time of an
  actual purchase.

### Changed
- `generate_recommendation.dart`'s lookups consolidated onto the shared
  `catalog_lookups` module, removing duplicated catalog-search logic.
- Recommendation's loading and error states brought in line with the
  rest of the app — a composed skeleton placeholder while the catalog
  loads, and a retry-capable error state that never shows a raw
  exception, matching Beer Detail and Price Verification.

### Testing
- 562 tests passing, `flutter analyze` clean — both a hard gate for
  every milestone in this release. Unit tests cover every domain
  function (recommendation generation, tie detection, price
  verification, catalog lookups) independently of any widget. Widget
  tests cover every screen's rendering, navigation, state preservation
  across back-navigation, and recovery behavior, using `ProviderScope`
  overrides against a fake catalog repository rather than real assets,
  storage, or network.

### Documentation
- `docs/engineering/Version-1-Architecture-Reference.md` — the
  permanent, as-built engineering reference: navigation graph, screen
  and domain ownership, shared infrastructure, repository conventions,
  and every intentionally deferred capability with its concrete
  blocker.

### Out of scope
Search/Browse, Comparison, Trade-off Explanation, Confirm-as-Is,
preferences beyond budget and style, Proxy-Buying Mode, and any
account or persistence layer. See the Architecture Reference's
"Intentionally Deferred Capabilities" section for why each is deferred
and what would need to change to unblock it.
