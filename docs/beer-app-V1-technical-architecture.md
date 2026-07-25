# ValueBrew V1 — Technical Architecture

Scope: exactly the V1 feature set (Search, Beer Detail, Value Score, Similar/Alternatives, "flag wrong price"). No backend server, no accounts, no submission pipeline.

---

## 1. Flutter Project Structure

Feature-first architecture — scales cleanly into V2 without a rewrite, avoids the over-abstraction that a layer-first structure invites at this size.

```
lib/
  main.dart
  app.dart                          # MaterialApp + router shell

  core/
    theme/
      app_theme.dart
    constants/
      app_constants.dart            # CDN catalog URL, cache keys, thresholds
    utils/
      value_score_calculator.dart   # pure functions, mirrors build script
      fuzzy_match.dart
      levenshtein.dart
    analytics/
      analytics_service.dart

  data/
    models/
      style.dart
      beer.dart
      sku.dart
      benchmark.dart
      catalog.dart
    services/
      catalog_local_cache_service.dart
      catalog_remote_service.dart
    repositories/
      catalog_repository.dart

  features/
    search/
      providers/
        search_providers.dart
      screens/
        search_screen.dart
      widgets/
        search_result_tile.dart
        empty_results_state.dart
        catalog_loading_state.dart
        catalog_error_state.dart

    beer_detail/
      providers/
        beer_detail_providers.dart
      screens/
        beer_detail_screen.dart
      widgets/
        value_score_badge.dart
        provenance_strip.dart
        sku_facts_row.dart
        similar_beers_list.dart
        flag_price_button.dart

    shared/
      providers/
        catalog_provider.dart       # app-wide catalog FutureProvider
      widgets/
        loading_indicator.dart

  routing/
    app_router.dart

test/
  unit/
    value_score_calculator_test.dart
    fuzzy_match_test.dart
    levenshtein_test.dart
    catalog_repository_test.dart
  widget/
    search_screen_test.dart
    beer_detail_screen_test.dart

scripts/
  build_catalog.py                  # seed data -> computed catalog.json
  validate_catalog.py               # schema validation
  README.md

catalog/
  seed/                             # raw research notes, not shipped
  catalog.schema.json
  catalog.json                      # published, precomputed output

.github/
  workflows/
    ci.yml
    catalog-publish.yml

docs/
  (PRD phase files already produced)
```

---

## 2. JSON Catalog Schema

Single file, precomputed at build time — the app never computes benchmarks on-device.

```json
{
  "catalog_version": 7,
  "generated_at": "2026-07-25T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false }
  ],
  "skus": [
    {
      "id": "kf_premium_650",
      "beer_id": "kf_premium",
      "size_ml": 650,
      "package_type": "bottle",
      "abv": 4.8,
      "calories": 260,
      "price": 110,
      "price_last_checked": "2026-07-20",
      "price_source": "karnataka_excise_mrp_2026",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 3.52,
      "value_score": 78,
      "value_verdict": "great_value"
    }
  ],
  "benchmarks": [
    {
      "style_id": "lager",
      "avg_cost_per_ml_alcohol": 4.10,
      "p25": 3.40,
      "p50": 3.95,
      "p75": 4.60,
      "sample_size": 42
    }
  ]
}
```

`package_type` enum: `bottle | can | pint`. `value_verdict` enum: `great_value | fair_value | overpriced` (thresholds below). `price_source` is a free-text provenance tag — this is what the ProvenanceStrip widget renders, so it must always be human-readable, not an internal code.

---

## 3. Value Score Algorithm

Computed once, at catalog build time, in `scripts/build_catalog.py`. Mirrored as pure Dart functions in `core/utils/value_score_calculator.dart` only for any future on-device recompute (e.g. group/budget mode in V2) — V1's app never calls these on the shipped catalog, it just reads precomputed fields.

```python
def cost_per_litre(price, size_ml):
    return price / (size_ml / 1000.0)

def pure_alcohol_ml(size_ml, abv_percent):
    return size_ml * (abv_percent / 100.0)

def cost_per_ml_alcohol(price, size_ml, abv_percent):
    return price / pure_alcohol_ml(size_ml, abv_percent)
```

**Why cost-per-ml-of-alcohol is the primary axis, not cost-per-litre:** this is the mechanism identified earlier as structurally unique to beer — ABV variance (4–9%+) is what makes this math discriminating at all. cost_per_litre is still shown as a secondary fact, not the scoring basis.

**Value score (0–100), inverted percentile within style:**

```python
def value_score(sku_cost_per_ml, style_distribution):
    # style_distribution = sorted list of cost_per_ml_alcohol for all SKUs in the same style
    n_worse_or_equal = sum(1 for x in style_distribution if x >= sku_cost_per_ml)
    percentile = n_worse_or_equal / len(style_distribution)
    return round(percentile * 100)
```

Lower cost-per-ml-alcohol → higher percentile → higher score. A SKU cheaper than every peer in its style scores 100.

**Verdict thresholds** (placeholders — tune once real usage exists, per the V1 validation plan):
- `score >= 75` → "Great value"
- `45 <= score < 75` → "Fair value"
- `score < 45` → "Overpriced for this ABV"

---

## 4. Search Implementation

No search engine, no index — at ~150 items, in-memory scoring on every keystroke (debounced) is faster than any network round-trip would be.

```dart
int scoreMatch(String query, String candidate) {
  final q = query.toLowerCase().trim();
  final c = candidate.toLowerCase();
  if (q.isEmpty) return 0;
  if (c == q) return 100;
  if (c.startsWith(q)) return 90;
  if (c.contains(q)) return 70;
  final window = c.substring(0, min(c.length, q.length + 2));
  final distance = levenshtein(q, window);
  return distance <= 2 ? max(0, 50 - distance * 10) : 0;
}
```

Matched against `beer.name` and `beer.brewery` per SKU, scores combined by max. Results sorted descending, filtered to score > 0, capped at 20. Search field debounced 250ms before recomputing — this is a UI-thread debounce, not a network debounce; there's no request to save, it's purely to avoid recomputing on every single keystroke.

---

## 5. State Management: Riverpod

**Choice: `flutter_riverpod`.**

Rationale: no BuildContext-threading required (matters once Beer Detail needs data independent of its navigation origin), compile-time-safe provider access, and providers are directly unit-testable via `ProviderContainer` overrides without pumping a widget tree — which matters given the testing priority is the value score and search logic, not UI rendering. It's also one of the most heavily-represented Flutter state patterns in current tooling, meaning higher-fidelity AI-generated code with fewer hallucinated APIs than a less common choice. It scales cleanly into V2 (accounts, submission state) without an architecture rewrite — the alternative of reaching for BLoC now would be premature ceremony for a four-screen app.

Core providers:
- `catalogProvider` — `FutureProvider<Catalog>`, wraps `CatalogRepository.load()`
- `searchQueryProvider` — `StateProvider<String>`
- `searchResultsProvider` — derived `Provider`, combines catalog + query + `scoreMatch`
- `selectedSkuProvider` — set on navigation to Beer Detail
- `similarBeersProvider` — derived from `selectedSkuProvider` + catalog, filtered by style, sorted by `value_score`

---

## 6. Local Storage Strategy

`shared_preferences` only — no SQLite, no Hive. At ~150 SKUs the entire catalog JSON is a few hundred KB; storing it as a raw string and parsing into Dart model objects on load is simpler than a database layer and fast enough that indexing would be solving a problem that doesn't exist yet.

Stored keys:
- `catalog_json` — raw string, last successfully fetched/validated catalog
- `catalog_version` — int, for update comparison
- `last_fetch_at` — ISO timestamp
- `has_seen_onboarding` — bool

**Reconsider this when:** V2 introduces the submission pipeline or accounts — at that point structured local storage (Hive) becomes worth the added complexity. Not before.

---

## 7. Remote Catalog Update Mechanism

Host `catalog.json` in the same GitHub repo, served through jsDelivr's CDN mirror of the repo (`cdn.jsdelivr.net/gh/{user}/{repo}@main/catalog/catalog.json`) — free, versioned by git history, CDN-cached, zero server to maintain or pay for.

Flow on app launch/resume:
1. Load bundled asset copy immediately (guarantees the app is usable offline on first install, no network wait on the critical path).
2. In the background, fetch the remote file with a short timeout (e.g. 4s).
3. Compare `catalog_version`; if remote is newer, parse and persist it to `shared_preferences`, replacing the in-memory catalog for the current session.
4. On any failure (timeout, malformed JSON, offline), silently fall back to whichever of {bundled, cached} is newest. Never block the UI on this and never show a network error for what is, from the user's perspective, a background refresh.

No separate "version check" endpoint — the whole file is small enough that fetching it in full on every launch is cheaper than building and maintaining a second lightweight endpoint just to check a version number.

---

## 8. Testing Strategy

Priority order, matching where a wrong answer actually damages the product's core trust premise:

1. **Unit tests — highest priority.** `value_score_calculator.dart`, `fuzzy_match.dart`, `levenshtein.dart`, and JSON deserialization for every model. These are pure functions; a bug here is a silently wrong Value Score reaching a user, which is the single worst failure mode this product has.
2. **Widget tests — second priority.** Search screen (loaded / empty / loading / error states) and Beer Detail screen (populated / no-price-data states) — covering exactly the empty/error states specified in Phase 2, since those are where trust is actually won or lost.
3. **Golden tests — explicitly deferred.** Not worth the maintenance overhead at solo-founder scale yet.
4. **Manual QA checklist** — run against real Bangalore store visits before each soft-launch milestone in the Day 1–30 plan. This substitutes for integration/e2e test infrastructure that isn't worth building before there's a second developer.

---

## 9. Analytics / Events to Capture

Firebase Analytics + Crashlytics (FlutterFire) — a hosted SDK, not custom infrastructure, consistent with the "rent, don't build" approach to anything outside the core product.

| Event | Properties | Validates |
|---|---|---|
| `app_open` | — | Baseline usage, time-of-day distribution |
| `search_performed` | query, result_count | Search friction (assumption 4) |
| `search_result_tapped` | sku_id, position | Search relevance |
| `beer_detail_viewed` | sku_id | Core loop completion |
| `value_score_viewed` | sku_id, score, verdict | Whether the score is actually seen |
| `alternative_tapped` | from_sku_id, to_sku_id | Whether Value Score changes behavior (assumption 2) |
| `price_flagged_wrong` | sku_id | Freshness/trust assumption (assumption 3) |
| `session_start` / `session_end` | duration | Repeat-usage rate — the clearest PMF proxy available at this stage |

Every event above maps directly to one of the six assumptions from the V1 scope document — nothing is tracked "just in case."

---

## 10. GitHub Repository Structure

Single monorepo — app, catalog, scripts, and docs together. Splitting these into separate repos would be premature process for a one-person team; reconsider only if a second engineer joins.

```
/                      # Flutter app root
/catalog/               # schema + seed + published catalog.json
/scripts/               # build_catalog.py, validate_catalog.py
/docs/                  # PRD phase files, operations notes
/.github/workflows/     # ci.yml, catalog-publish.yml
```

---

## 11. CI/CD & Deployment

**CI (every push/PR):**
- `flutter analyze`
- `flutter test`
- `flutter build apk --debug` (build sanity check only)

**Catalog pipeline (on changes under `/catalog`):**
- Run `validate_catalog.py` against `catalog.schema.json`
- Run `build_catalog.py` to regenerate computed fields (value scores, benchmarks)
- Fail the workflow if validation fails — a broken catalog should never reach the CDN

**Deployment — deliberately manual for the first 30 days:** `flutter build appbundle`, upload by hand to Google Play Console's Internal Testing track. Automating store deployment (Codemagic + Fastlane) is worth doing once release cadence stabilizes past the initial daily-iteration window, not before — automating a process you're still actively changing wastes more time than it saves.

Play Store listing needs: privacy policy page (minimal, given no accounts and only anonymous analytics), and the age-rating questionnaire answered per the Section 2.5 legal findings from Phase 1 (comparison-only, no sale facilitation — a materially easier compliance lane than a delivery app).
