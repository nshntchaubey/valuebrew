# Changelog

All notable changes to ValueBrew are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project uses [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`,
with the Android/iOS build number as the fourth, CI-facing component).

## [Unreleased]

Production-readiness polish — no user-facing features added. See
`release_checklist.md` for what's left before publishing.

### Added
- Adaptive app icon (Android 8+), monochrome themed icon (Android 13+),
  and a matching splash screen, generated from a single vector mark.
- Release build configuration: R8/resource shrinking for release builds, a
  release-signing config that reads a local, gitignored `key.properties`
  and falls back to debug signing when none is present (see
  `docs/RELEASE_SIGNING.md`).
- `privacy_policy.md`, `THIRD_PARTY_NOTICES.md`, `store_listing.md`,
  `release_checklist.md`.
- A polished, GitHub-facing `README.md`.

### Changed
- Android `applicationId` from the template default `com.example.valuebrew`
  to `com.nishantchaubey.valuebrew` (Play Console rejects `com.example.*`).
- App display name from `valuebrew` to `ValueBrew` (Android manifest label,
  iOS `CFBundleDisplayName`/`CFBundleName`).

### Fixed
- Release builds were missing the `INTERNET` permission (only granted to
  debug/profile builds by Flutter's own tooling), which would have made
  the remote catalog fetch silently fail on every published build.

## [1.0.0] - 2026-07-25

The full V1 feature set, built milestone-by-milestone. All dated the same
day here because the project's git history was authored in one continuous
session; each bullet below represents a distinct, separately-tested
milestone, not a single day's work.

### Added
- Project scaffold: Flutter app shell, feature-first folder structure,
  core dependencies (`flutter_riverpod`, `http`, `shared_preferences`,
  `path_provider`), and initial documentation.
- Immutable catalog data models (`Style`, `Beer`, `Benchmark`, `Catalog`)
  and a repository that loads and parses the bundled JSON catalog.
- Home screen with the full catalog loaded and rendered.
- Beer detail screen and navigation from the home list.
- Search, with fuzzy matching over beer name and brewery.
- Per-SKU value information (price, cost per litre, cost per mL of
  alcohol, value score/verdict) surfaced on both the list and detail
  screens.
- Value-based sorting, later generalized into a reusable `SortingEngine` +
  `SortOption` pair shared across Home and Favorites.
- Beer-to-beer comparison screen.
- Shared display-formatting helpers, used consistently across list,
  detail, and comparison views.
- Similar-beer recommendations, later generalized into a full
  recommendation engine: a `RecommendationPolicy` abstraction, explainable
  recommendation reasons (e.g. "Similar ABV", "Better value"), and
  user-selectable recommendation profiles.
- Local "this looks wrong" reporting for incorrect catalog data — recorded
  on-device only, for later manual review (see `privacy_policy.md`).
- Persistent favorites (`shared_preferences`-backed), with a dedicated
  Favorites screen that respects the same filter/sort state as Home.
- A reusable `FilteringEngine` and advanced catalog filters (style, ABV,
  price range, minimum value score).
- `docs/architecture.md` and `docs/philosophy.md` — living documentation
  of the codebase's architecture and engineering principles.
- Remote catalog updates: the bundled catalog is checked against a
  remotely-hosted `catalog.json` (via `HttpCatalogRemoteSource`) on
  launch, preferring whichever of {bundled, cached, remote} has the
  newest `catalog_version`, with a configurable timeout and a silent,
  crash-free fallback to whatever's already loaded on any failure
  (offline, timeout, a non-200 response, or malformed JSON).
- UX polish pass: skeleton loading states, richer empty/error states with
  retry actions, an app-wide Material 3 theme, consistent spacing
  constants, and subtle built-in-widget animations for favoriting and
  profile-driven reordering.

### Testing
- Comprehensive unit, provider, and widget test coverage added
  incrementally alongside every feature above (467 tests as of this
  release) — see `README.md`'s Testing Strategy section for the approach.
