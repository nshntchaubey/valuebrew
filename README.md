# ValueBrew

**Get an honest beer recommendation, budgeted to what you actually want.**
ValueBrew recommends the beer with the best real value for your budget —
cost measured per unit of alcohol, not just the price on the shelf — and
explains why, every time.

No account. No ads. No tracking.

<!--
Screenshots: capture per the checklist in store_listing.md, then replace
this block with actual images.
-->
📱 *Screenshots coming soon — see [`store_listing.md`](store_listing.md) for the capture checklist.*

---

## Features

- **Budget-based recommendation** — state a budget, get one specific
  beer with the best real value within it, and a plain-language
  explanation of why.
- **Style refinement** — optionally narrow a recommendation by style,
  requested only after a budget-only recommendation already exists, and
  reversible at any time.
- **Tie Disclosure** — when multiple beers are genuinely, exactly tied
  for the best value, ValueBrew says so honestly and shows every one of
  them, rather than picking one arbitrarily.
- **Beer Detail** — the complete picture of any recommended beer: price,
  size, package, ABV, value score and verdict, and how recently the
  price was checked.
- **Price Verification** — check whether a price you were charged for a
  specific beer matches the legal reference price, classified as at,
  below, or above.
- **Planning Mode** — an alternate entry point for a future purchase,
  carrying a standing reminder throughout that prices and availability
  may have changed by the time you actually buy.

## Technology Stack

| Layer | Choice |
|---|---|
| Framework | Flutter 3.44.8 / Dart 3.12.2 |
| State management | [flutter_riverpod](https://pub.dev/packages/flutter_riverpod) 2.6.1 |
| Networking | [http](https://pub.dev/packages/http) 1.2.2 (remote catalog fetch) |
| Local persistence | [shared_preferences](https://pub.dev/packages/shared_preferences) 2.3.3 (cached catalog only) |
| Static analysis | [flutter_lints](https://pub.dev/packages/flutter_lints) 6.0.0 |

No backend. The catalog is a local JSON file, optionally refreshed from a
static CDN-hosted copy of the same file — see [Remote Catalog](#remote-catalog)
below. Full license text for every declared dependency:
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  UI (Consumer/ConsumerStatefulWidget screens)             │
│  Home · Recommendation · Beer Detail · Price Verification │
└───────────────────────────┬───────────────────────────────┘
                             │ ref.watch / ref.read
                             ▼
┌─────────────────────────────────────────────────────────┐
│  Riverpod Providers                                       │
│  catalogProvider · catalogRepositoryProvider ·             │
│  valueBrewNavigatorProvider                                │
└───────────┬─────────────────────────────┬─────────────────┘
            │                             │
            ▼                             ▼
┌───────────────────────┐     ┌───────────────────────────┐
│  CatalogRepository       │     │  Domain functions            │
│  bundled asset ·          │     │  generateRecommendation ·     │
│  local cache · remote     │     │  verifyPrice — pure Dart,      │
│  fetch, in that order     │     │  no Flutter dependency         │
└───────────┬───────────┘     └──────────────┬──────────────┘
            │                                │ (reads, as plain data)
            ▼                                ▼
┌─────────────────────────────────────────────────────────┐
│  Catalog (Beer, Sku, Style, Benchmark — value objects)     │
└─────────────────────────────────────────────────────────┘
```

Feature-first, repository-pattern, every dependency wired via Riverpod
provider — nothing constructed inside a widget's `build()`, no global
singletons. `ValueBrewNavigator` is the only class permitted to trigger
a screen transition; its public API is exactly the set of legal
transitions, one method each, added only once a real screen needed it.

The full reasoning behind ownership, navigation, and every design
principle actually exercised in this codebase is written up in
[`docs/engineering/Version-1-Architecture-Reference.md`](docs/engineering/Version-1-Architecture-Reference.md)
— the permanent, as-built engineering reference for this version. The
product-level canon it's built against lives in
[`docs/architecture/current/`](docs/architecture/current/).

### Recommendation, briefly

`generateRecommendation` is pure Dart with zero Flutter dependency,
which is why it's the most heavily unit-tested part of the codebase. It
filters the catalog by budget (a hard limit), optionally narrows by
style, and ranks the remainder by Value Score — detecting an exact tie
rather than picking arbitrarily between equally-good options. The
result is a `RecommendationOutcome`: a sealed type with one case per
real outcome (found, tied, no match within budget, no match for the
stated style), built so a future outcome variant cannot be added
without the compiler forcing every renderer to handle it explicitly.

### Remote Catalog

On launch, `CatalogRepository` tries, in order: the bundled JSON asset
(the only failure that actually stops loading), a locally-cached
catalog if it's newer, then a remote fetch if *that* reports something
newer still. Any failure reading the cache or the network — offline,
timeout, a non-200 response, malformed JSON — is silently ignored; the
app just keeps whatever it already has. Configure the remote URL and
timeout in one place: [`lib/core/constants/app_constants.dart`](lib/core/constants/app_constants.dart).

## Project Structure

```
lib/
  navigation/                     — ValueBrewNavigator, the sole owner of screen transitions
  catalog/
    domain/                        — Style, Benchmark, Catalog
    data/                          — CatalogRepository, local cache, remote source
  shared_domain/                  — Beer, Sku
  core/
    constants/                     — AppSpacing, AppConstants
    utils/                          — display_formatting
  features/
    discovery/presentation/        — Home screen
    recommendation/
      domain/                       — generateRecommendation, RecommendationOutcome,
                                       RecommendationResult, RecommendationTie, TiedCandidate
      presentation/                  — RecommendationScreen
    beer_detail/presentation/       — BeerDetailScreen
    price_verification/
      domain/                        — verifyPrice, PriceVerificationResult
      presentation/                   — PriceVerificationScreen
    shared/
      catalog_lookups.dart            — resolveBeer / resolveStyle / resolveSku / …
      providers/                       — catalogProvider
      widgets/                          — ErrorStateView, SkeletonBox
  app.dart, main.dart
```

## Testing Strategy

**562 tests**, all passing, `flutter analyze` clean — both a hard gate
in this project's workflow; a milestone isn't complete until both pass.

- **Unit tests** — every domain function tested directly and
  independently of any widget: `generateRecommendation` (including tie
  detection), `verifyPrice`, and every `catalog_lookups` function.
- **Widget tests** — every screen, pumped with `ProviderScope` overrides
  injecting a fake `CatalogRepository` rather than touching real
  assets, storage, or network. Coverage includes rendering, navigation
  to the correct destination, state preservation across back
  navigation, and recovery/failure states.

Run everything:

```bash
flutter analyze
flutter test
```

## Setup Instructions

1. Install [Flutter](https://docs.flutter.dev/get-started/install) 3.44.8
   or later (stable channel).
2. Clone the repository and install dependencies:

   ```bash
   flutter pub get
   ```

3. Run the app on a connected device or simulator:

   ```bash
   flutter run
   ```

4. Run the test suite and static analysis:

   ```bash
   flutter test
   flutter analyze
   ```

### Regenerating brand assets

The launcher icon (adaptive, monochrome, and legacy) and splash-screen
foreground are generated from one vector mark defined in code, not
hand-exported PNGs:

```bash
flutter test tool/generate_brand_assets.dart
```

Edit the mark in `tool/generate_brand_assets.dart` and re-run this to
regenerate every density.

## Release Instructions

Full release process: [`release_checklist.md`](release_checklist.md).

Short version:

```bash
flutter build appbundle --release   # Play Store upload format
flutter build apk --release         # a signed APK
```

Without `android/key.properties` present, release builds fall back to
debug signing (so the commands above always succeed locally).

## What's not built yet

Search/Browse, Comparison, Trade-off Explanation, Confirm-as-Is,
preferences beyond budget and style, and Proxy-Buying Mode are all
intentionally deferred, each for a specific, documented reason — see
["Intentionally Deferred Capabilities"](docs/engineering/Version-1-Architecture-Reference.md#9-intentionally-deferred-capabilities)
in the Architecture Reference. This is not a roadmap — nothing here is
scheduled; each item is blocked on either a missing canonical
specification or a missing precondition this repository can't resolve
on its own.

## Privacy

ValueBrew collects no personal data, runs no analytics, shows no ads,
and requires no account. Full policy: [`privacy_policy.md`](privacy_policy.md).

## License

No open-source license has been selected for this repository yet — all
rights reserved by default until one is chosen. Third-party dependency
licenses (all permissive: BSD-3-Clause / MIT) are documented in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
