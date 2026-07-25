# ValueBrew V1 — Implementation Task Breakdown

134 tasks, grouped by milestone, ordered by dependency within and across groups. Each task is a single, independently completable unit — hand these to Claude Code/Cursor incrementally, one at a time or in small batches within a milestone.

---

## M0 — Repo & Environment Setup
- [ ] 1. Create GitHub repo (monorepo: app + catalog + scripts + docs)
- [ ] 2. Run `flutter create` targeting Android first (iOS structure retained, deprioritized)
- [ ] 3. Add standard Flutter/Dart `.gitignore`
- [ ] 4. Add dependencies to `pubspec.yaml`: `flutter_riverpod`, `http`, `shared_preferences`, `path_provider`
- [ ] 5. Configure `analysis_options.yaml` with recommended lint rules
- [ ] 6. Create folder structure: `core/`, `data/`, `features/`, `routing/`, `test/`
- [ ] 7. Write `README.md` with project overview and setup steps
- [ ] 8. Build `app.dart` with `MaterialApp` shell and placeholder home screen

## M1 — Data Models
- [ ] 9. Define `Style` model (id, name, description)
- [ ] 10. Define `Beer` model (id, name, brewery, styleId, isCraft)
- [ ] 11. Define `Sku` model (id, beerId, sizeMl, packageType enum, abv, calories, price, priceLastChecked, priceSource, costPerLitre, costPerMlAlcohol, valueScore, valueVerdict)
- [ ] 12. Define `Benchmark` model (styleId, avgCostPerMlAlcohol, p25, p50, p75, sampleSize)
- [ ] 13. Define `Catalog` model (styles, beers, skus, benchmarks, catalogVersion, generatedAt)
- [ ] 14. Implement `fromJson`/`toJson` for `Style`
- [ ] 15. Implement `fromJson`/`toJson` for `Beer`
- [ ] 16. Implement `fromJson`/`toJson` for `Sku`
- [ ] 17. Implement `fromJson`/`toJson` for `Benchmark`
- [ ] 18. Implement `fromJson`/`toJson` for `Catalog` (top-level parser)

## M2 — Catalog Schema & Seed Data
- [ ] 19. Write `catalog.schema.json` describing the full catalog shape
- [ ] 20. Create `/catalog/seed/` directory for raw research notes
- [ ] 21. Compile first ~30 SKUs (mass-market lagers) from the Karnataka excise MRP list
- [ ] 22. Compile next ~30 SKUs (strong beers / premium licensed imports)
- [ ] 23. Compile next ~30 SKUs (craft / independent import segment)
- [ ] 24. Compile remaining SKUs to reach ~120–150 total
- [ ] 25. Cross-check compiled prices against magicpin / Livcheers / city-guide sources
- [ ] 26. Assign `style_id` to every beer entry
- [ ] 27. Validate raw seed data against `catalog.schema.json`
- [ ] 28. Fix schema validation errors in seed data

## M3 — Benchmark & Value Score Build Script
- [ ] 29. Write `build_catalog.py`: read seed data, compute `cost_per_litre` per SKU
- [ ] 30. Extend script: compute `pure_alcohol_ml` and `cost_per_ml_alcohol` per SKU
- [ ] 31. Extend script: group SKUs by `style_id`, compute benchmark distributions
- [ ] 32. Implement percentile-rank calculation for value score within each style group
- [ ] 33. Implement verdict bucketing (great_value / fair_value / overpriced)
- [ ] 34. Write final computed `catalog.json` as script output
- [ ] 35. Add `build-catalog` as a single documented command (Makefile or npm script)
- [ ] 36. Write tests for the build script's value score math
- [ ] 37. Add post-build validation: re-validate output `catalog.json` against schema
- [ ] 38. Document build script usage in `/scripts/README.md`

## M4 — Core Utilities (In-App Dart)
- [ ] 39. Implement `costPerLitre` in `core/utils/value_score_calculator.dart`
- [ ] 40. Implement `costPerMlAlcohol` in the same file
- [x] 41. Implement `scoreMatch` fuzzy search function in `core/utils/fuzzy_match.dart`
- [x] 42. Implement `levenshtein` distance helper
- [ ] 43. Unit test `costPerLitre`
- [ ] 44. Unit test `costPerMlAlcohol`
- [x] 45. Unit test `scoreMatch`
- [x] 46. Unit test `levenshtein`

## M5 — Catalog Loading & Local Storage
- [ ] 47. Implement `CatalogLocalCacheService` (get/set raw JSON + version via `shared_preferences`)
- [ ] 48. Implement `CatalogRemoteService` (fetch `catalog.json` via `http` from CDN URL)
- [ ] 49. Add bundled-asset fallback (`catalog.json` shipped as a Flutter asset)
- [ ] 50. Implement `CatalogRepository`: bundled → cache → remote, version-compared
- [ ] 51. Add timeout handling to remote fetch (fail fast, fall back silently)
- [ ] 52. Add error handling/logging for malformed remote catalog JSON
- [ ] 53. Implement in-memory parsed `Catalog` singleton for the app session
- [ ] 54. Unit test `CatalogLocalCacheService` (mocked `shared_preferences`)
- [ ] 55. Unit test `CatalogRemoteService` (mocked HTTP client)
- [ ] 56. Unit test `CatalogRepository` version-comparison logic
- [ ] 57. Integration test: bundled asset loads with no network on fresh install
- [ ] 58. Integration test: remote catalog replaces cache when version is newer

## M6 — State Management Wiring (Riverpod)
- [ ] 59. Set up `ProviderScope` at app root
- [ ] 60. Implement `catalogProvider` (`FutureProvider<Catalog>`)
- [ ] 61. Implement `searchQueryProvider` (`StateProvider<String>`)
- [x] 62. Implement `searchResultsProvider` (derived from catalog + query + `scoreMatch`)
- [ ] 63. Implement `selectedSkuProvider`
- [ ] 64. Implement `similarBeersProvider` (derived from selected SKU + catalog, sorted by value score)
- [ ] 65. Add 250ms debounce to search query updates
- [ ] 66. Test `searchResultsProvider` and `similarBeersProvider` via `ProviderContainer` overrides

## M7 — Search Screen UI
- [ ] 67. Build `SearchScreen` scaffold (AppBar + search field)
- [ ] 68. Wire search field to `searchQueryProvider`
- [ ] 69. Build `SearchResultTile` (name, brewery, style, quick value badge)
- [ ] 70. Build results `ListView` consuming `searchResultsProvider`
- [ ] 71. Build empty-results state (fuzzy "did you mean" + "help us add this" CTA)
- [ ] 72. Build zero-query state (simple prompt, no forms)
- [ ] 73. Build catalog-loading state
- [ ] 74. Build catalog-load-error state with retry action
- [ ] 75. Wire tap-through from `SearchResultTile` to Beer Detail
- [ ] 76. Widget-test `SearchScreen` across loaded/empty/error/loading states

## M8 — Beer Detail Screen UI
- [ ] 77. Build `BeerDetailScreen` scaffold (name, brewery, style header)
- [ ] 78. Build SKU size picker for beers with multiple sizes
- [ ] 79. Build `ValueScoreBadge` (large score + plain verdict)
- [ ] 80. Build `ProvenanceStrip` ("Price checked [date]" / "Estimated — no confirmed price yet")
- [ ] 81. Build `SkuFactsRow` (ABV, calories, cost/litre, cost/ml alcohol)
- [ ] 82. Wire screen to `selectedSkuProvider` and `catalogProvider`
- [ ] 83. Handle "no price data" state per the Phase 2 empty-state spec
- [ ] 84. Widget-test `BeerDetailScreen` across populated/no-price/loading states

## M9 — Similar & Better Alternatives
- [ ] 85. Build `SimilarBeersList` widget, ranked by value score within style
- [ ] 86. Wire to `similarBeersProvider`
- [ ] 87. Wire tap-through from a similar item into its own Beer Detail screen
- [ ] 88. Handle empty state when no similar beers exist in the style
- [ ] 89. Widget-test `SimilarBeersList` populated/empty states
- [ ] 90. Add `alternative_tapped` analytics hook (see M11)

## M10 — "This Looks Wrong" Feedback Flow
- [ ] 91. Build `FlagPriceButton` on Beer Detail screen
- [ ] 92. Implement flag-submission action (webhook or lightweight endpoint — no custom backend)
- [ ] 93. Set up a minimal receiver for flags (free-tier serverless function, or a Google Form/Sheet)
- [ ] 94. Show confirmation snackbar after a flag is submitted
- [ ] 95. Widget-test `FlagPriceButton` submission flow
- [ ] 96. Document the manual flag-review process in `/docs/operations.md`

## M11 — Analytics / Events
- [ ] 97. Create Firebase project, configure FlutterFire
- [ ] 98. Add `firebase_analytics`, initialize in `app.dart`
- [ ] 99. Implement `AnalyticsService` wrapper (`core/analytics/analytics_service.dart`)
- [ ] 100. Log `app_open`
- [ ] 101. Log `search_performed` (query, result_count)
- [ ] 102. Log `search_result_tapped` (sku_id, position)
- [ ] 103. Log `beer_detail_viewed` and `value_score_viewed`
- [ ] 104. Log `alternative_tapped`
- [ ] 105. Log `price_flagged_wrong`
- [ ] 106. Add Crashlytics alongside Analytics

## M12 — Testing Hardening
- [ ] 107. Add `mocktail` (or `mockito`) to dev dependencies
- [ ] 108. Confirm unit test coverage on all `core/utils` functions
- [ ] 109. Confirm widget test coverage on Search and Beer Detail happy paths
- [ ] 110. (Optional, low priority) Golden test for `ValueScoreBadge`
- [ ] 111. Set up `lcov` coverage reporting
- [ ] 112. Write a manual QA checklist for dogfooding rounds
- [ ] 113. Run manual QA pass #1 against a real Bangalore store visit
- [ ] 114. Fix bugs found in manual QA pass #1

## M13 — CI/CD & Deployment
- [ ] 115. Write `.github/workflows/ci.yml` (`flutter analyze` + `flutter test` on push/PR)
- [ ] 116. Write `.github/workflows/catalog-publish.yml` (validate + rebuild catalog on `/catalog` changes)
- [ ] 117. Enable branch protection requiring CI pass before merge to `main`
- [ ] 118. Set up Android signing config (keystore + GitHub Actions secrets)
- [ ] 119. Build the first `flutter build appbundle` release manually
- [ ] 120. Create Google Play Console account and app listing (Internal Testing track)
- [ ] 121. Upload first build to Internal Testing
- [ ] 122. Add 10–20 internal testers for soft-launch
- [ ] 123. Document the release process in `/docs/release-process.md`
- [ ] 124. (Deferred) Evaluate Codemagic/Fastlane automation once release cadence stabilizes

## M14 — Launch Readiness & Polish
- [ ] 125. Add app icon and splash screen
- [ ] 126. Add a minimal, skippable one-time onboarding screen (no forms, per product principles)
- [ ] 127. Verify offline behavior end-to-end (airplane mode test)
- [ ] 128. Verify catalog update flow end-to-end (bump version, confirm app picks it up)
- [ ] 129. Accessibility pass (text scaling, contrast on `ValueScoreBadge`)
- [ ] 130. Performance check: cold start time, search responsiveness at full catalog size
- [ ] 131. Write a minimal privacy policy page for the Play Store listing
- [ ] 132. Complete Play Store listing (description, screenshots, age-rating questionnaire per Phase 1 legal findings)
- [ ] 133. Final smoke test against the Day 14–18 soft-launch plan
- [ ] 134. Tag `v1.0.0` release in GitHub

---

**Dependency notes for whoever (or whichever AI agent) executes this:**
- M0 blocks everything.
- M1 (models) blocks M2 validation, M4 utilities, and all of M5–M9.
- M2 + M3 (catalog data + build script) can run in parallel with M4 (in-app utilities) once M1 is done — they don't depend on each other.
- M5 (catalog loading) requires M1 + a valid `catalog.json` from M2/M3.
- M6 (state management) requires M5.
- M7, M8, M9, M10 (UI) each require M6, but are independent of each other and can be built in any order or in parallel.
- M11 (analytics) can be threaded through M7–M10 as those screens are built, or added afterward — listed last only for clarity, not because it must be last.
- M12–M14 are correctly last: nothing in them is buildable before the features they test/ship exist.
