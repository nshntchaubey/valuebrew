import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/providers/recommendation_providers.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';
import 'package:valuebrew/features/recommendation/services/recommendation_engine.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [],
  "skus": [],
  "benchmarks": []
}
''';

const _oneSkuJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [],
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
      "price_source": "test",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 3.52,
      "value_score": 78,
      "value_verdict": "great_value"
    }
  ],
  "benchmarks": []
}
''';

const _multipleSkusJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [],
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
      "price_source": "test",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 3.52,
      "value_score": 78,
      "value_verdict": "great_value"
    },
    {
      "id": "kf_premium_330",
      "beer_id": "kf_premium",
      "size_ml": 330,
      "package_type": "can",
      "abv": 4.8,
      "calories": 130,
      "price": 60,
      "price_last_checked": "2026-07-20",
      "price_source": "test",
      "cost_per_litre": 181.8,
      "cost_per_ml_alcohol": 3.79,
      "value_score": 55,
      "value_verdict": "fair_value"
    },
    {
      "id": "other_beer_sku",
      "beer_id": "other_beer",
      "size_ml": 500,
      "package_type": "can",
      "abv": 6.5,
      "calories": 220,
      "price": 250,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 500.0,
      "cost_per_ml_alcohol": 7.69,
      "value_score": 20,
      "value_verdict": "overpriced"
    }
  ],
  "benchmarks": []
}
''';

/// Built so the two recommendation sections have distinct, hand-verifiable
/// expected contents:
///
/// - `fosters_650`: same style, identical ABV/cost/package as the
///   reference, different brewery, and a higher valueScore. Qualifies for
///   both "Similar beers" (highest similarity: matches everything but
///   brewery) and "Better value picks" (comparable ABV, genuinely better
///   value).
/// - `weak_lager_650`: same style, but ABV far enough apart (diff 4.1) to
///   fail `betterValueAlternatives`' ABV-comparability gate — appears only
///   in "Similar beers" (ranked below fosters: same price/style, but a
///   zero ABV-closeness score and a different package type).
/// - `craft_ipa_330`: a different style entirely, with a higher raw
///   valueScore than the reference — proves `betterValueAlternatives`
///   correctly excludes it (style gate) even though a naive "just sort by
///   valueScore" approach would have included it. Appears in "Similar
///   beers" too, ranked last (only ABV and cost happen to match).
/// - `no_sku_lager`: a same-style beer with no SKU at all — must never
///   appear in either section.
const _recommendationsJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
    { "id": "ipa", "name": "IPA", "description": "Hop-forward, bitter" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "fosters", "name": "Foster's", "brewery": "CUB", "style_id": "lager", "is_craft": false },
    { "id": "weak_lager", "name": "Weak Lager", "brewery": "Some Brewery", "style_id": "lager", "is_craft": false },
    { "id": "craft_ipa", "name": "Craft IPA", "brewery": "Arbor Brewing", "style_id": "ipa", "is_craft": true },
    { "id": "no_sku_lager", "name": "No Sku Lager", "brewery": "Ghost Brewery", "style_id": "lager", "is_craft": false }
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
      "price_source": "test",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 4.0,
      "value_score": 50,
      "value_verdict": "fair_value"
    },
    {
      "id": "fosters_650",
      "beer_id": "fosters",
      "size_ml": 650,
      "package_type": "bottle",
      "abv": 4.8,
      "calories": 260,
      "price": 130,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 200.0,
      "cost_per_ml_alcohol": 4.0,
      "value_score": 90,
      "value_verdict": "great_value"
    },
    {
      "id": "weak_lager_650",
      "beer_id": "weak_lager",
      "size_ml": 650,
      "package_type": "can",
      "abv": 8.9,
      "calories": 260,
      "price": 140,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 215.4,
      "cost_per_ml_alcohol": 4.0,
      "value_score": 20,
      "value_verdict": "overpriced"
    },
    {
      "id": "craft_ipa_330",
      "beer_id": "craft_ipa",
      "size_ml": 330,
      "package_type": "can",
      "abv": 4.8,
      "calories": 210,
      "price": 300,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 909.1,
      "cost_per_ml_alcohol": 4.0,
      "value_score": 95,
      "value_verdict": "great_value"
    }
  ],
  "benchmarks": []
}
''';

const _kfPremium = Beer(
  id: 'kf_premium',
  name: 'Kingfisher Premium',
  brewery: 'United Breweries',
  styleId: 'lager',
  isCraft: false,
);

/// A [RecommendationEngine] whose methods always throw — used to prove
/// that a recommendation failure can't crash [BeerDetailScreen].
class _ThrowingRecommendationEngine extends RecommendationEngine {
  @override
  List<Sku> similarBeers(Sku beer, Catalog catalog) => throw StateError('boom');

  @override
  List<Sku> betterValueAlternatives(Sku beer, Catalog catalog) => throw StateError('boom');
}

Widget _wrap(
  Widget child, {
  required CatalogRepository repository,
  List<Override> extraOverrides = const [],
}) {
  return ProviderScope(
    overrides: [
      catalogRepositoryProvider.overrideWithValue(repository),
      ...extraOverrides,
    ],
    child: MaterialApp(home: child),
  );
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('shows a loading indicator before the catalog resolves', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('shows beer name, brewery, and the resolved style name', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsWidgets);
    expect(find.text('United Breweries'), findsOneWidget);
    expect(find.text('Lager'), findsOneWidget);
  });

  testWidgets('falls back to "Unknown style" when the styleId cannot be resolved', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );
    const orphanBeer = Beer(
      id: 'mystery_beer',
      name: 'Mystery Beer',
      brewery: 'Unknown Brewery',
      styleId: 'nonexistent_style',
      isCraft: false,
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: orphanBeer), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Unknown style'), findsOneWidget);
  });

  testWidgets('shows an error message when the catalog fails to load', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => throw Exception('boom'),
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('Failed to load catalog'), findsOneWidget);
  });

  testWidgets('shows a fallback message when the beer has no SKUs', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('No SKUs available for this beer.'), findsOneWidget);
    expect(find.textContaining('MRP:'), findsNothing);
  });

  testWidgets(
    'shows package type, volume, MRP, valueScore, and valueVerdict for a single SKU',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _oneSkuJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      expect(find.text('Bottle · 650 mL'), findsOneWidget);
      expect(find.text('MRP: ₹110'), findsOneWidget);
      expect(find.text('Value score: 78 (Great value)'), findsOneWidget);
    },
  );

  testWidgets('shows every SKU belonging to the beer, and none from other beers', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _multipleSkusJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    // This beer's two SKUs are both shown, fully rendered.
    expect(find.text('Bottle · 650 mL'), findsOneWidget);
    expect(find.text('MRP: ₹110'), findsOneWidget);
    expect(find.text('Value score: 78 (Great value)'), findsOneWidget);

    expect(find.text('Can · 330 mL'), findsOneWidget);
    expect(find.text('MRP: ₹60'), findsOneWidget);
    expect(find.text('Value score: 55 (Fair value)'), findsOneWidget);

    // The other beer's SKU must not appear on this screen.
    expect(find.text('Can · 500 mL'), findsNothing);
    expect(find.text('MRP: ₹250'), findsNothing);
    expect(find.text('Value score: 20 (Overpriced for this ABV)'), findsNothing);
  });

  testWidgets(
    'shows the empty-state message in both recommendation sections when the beer has no SKUs',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _catalogJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      expect(find.text('Similar & Better Value'), findsOneWidget);
      expect(find.text('Similar beers'), findsOneWidget);
      expect(find.text('No similar beers available.'), findsOneWidget);
      expect(find.text('Better value picks'), findsOneWidget);
      expect(find.text('No better value alternatives available.'), findsOneWidget);
    },
  );

  testWidgets(
    'shows the empty-state message in both recommendation sections when nothing else qualifies',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _oneSkuJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      expect(find.text('No similar beers available.'), findsOneWidget);
      expect(find.text('No better value alternatives available.'), findsOneWidget);
    },
  );

  testWidgets(
    'Similar beers is ranked by RecommendationEngine.similarBeers, excluding the '
    'current beer and beers with no SKUs',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _recommendationsJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      // All three other SKUs appear in Similar beers — similarBeers has no
      // style filter, just a similarity ranking. (Foster's also separately
      // qualifies for Better value picks — see the next test — so its name
      // legitimately appears twice on screen; the 'similar:' key below
      // targets only its Similar-beers tile.)
      final fostersSimilarTile = find.byKey(const ValueKey('similar:fosters_650'));
      final weakSimilarTile = find.byKey(const ValueKey('similar:weak_lager_650'));
      final craftSimilarTile = find.byKey(const ValueKey('similar:craft_ipa_330'));
      expect(fostersSimilarTile, findsOneWidget);
      expect(weakSimilarTile, findsOneWidget);
      expect(craftSimilarTile, findsOneWidget);

      // The viewed beer itself must not appear in its own similar list.
      expect(find.text('Kingfisher Premium'), findsNWidgets(2));

      // A same-style beer with no SKU must never appear.
      expect(find.text('No Sku Lager'), findsNothing);

      // fosters (score 0.9375) > weak_lager (0.5625) > craft_ipa (0.4375) —
      // see the fixture's doc comment for the full weighted-score derivation.
      final fostersY = tester.getTopLeft(fostersSimilarTile).dy;
      final weakY = tester.getTopLeft(weakSimilarTile).dy;
      final craftY = tester.getTopLeft(craftSimilarTile).dy;
      expect(fostersY, lessThan(weakY));
      expect(weakY, lessThan(craftY));
    },
  );

  testWidgets(
    'Better value picks only shows RecommendationEngine.betterValueAlternatives\' '
    'results: same style, comparable ABV, and a genuinely higher valueScore',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _recommendationsJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      // Only fosters qualifies: same style, comparable ABV, higher value.
      final betterValueSection = find.text('Better value picks');
      expect(betterValueSection, findsOneWidget);
      expect(find.byKey(const ValueKey('better_value:fosters_650')), findsOneWidget);

      // weak_lager has a comparable style but too different an ABV; craft_ipa
      // has a higher raw valueScore but a different style — a naive
      // "sort every beer by valueScore" would have wrongly included one or
      // both, which this test rules out by confirming neither has a tile in
      // the Better value picks section specifically (both legitimately do
      // have a tile in Similar beers — see the previous test).
      expect(find.byKey(const ValueKey('better_value:weak_lager_650')), findsNothing);
      expect(find.byKey(const ValueKey('better_value:craft_ipa_330')), findsNothing);
      expect(find.text('No better value alternatives available.'), findsNothing);
    },
  );

  testWidgets('tapping a recommendation pushes a new BeerDetailScreen for it', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _recommendationsJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    final fostersRow = find.byKey(const ValueKey('similar:fosters_650'));
    await tester.tap(fostersRow);
    await tester.pumpAndSettle();

    // The pushed screen's AppBar title and content uniquely identify it as
    // Foster's own BeerDetailScreen (its own brewery and value score, not
    // Kingfisher Premium's).
    expect(find.widgetWithText(AppBar, "Foster's"), findsOneWidget);
    expect(find.text('CUB'), findsOneWidget);
    expect(find.text('Value score: 90 (Great value)'), findsWidgets);
  });

  testWidgets(
    'a different RecommendationPolicy (via Riverpod) changes what Similar beers shows — '
    'proving the screen actually delegates to RecommendationEngine rather than its own logic',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _recommendationsJson,
        assetKey: 'fake_key',
      );

      // Brewery match only: none of the three candidates share Kingfisher
      // Premium's brewery, so every similarity score is 0.0 — a completely
      // different ranking outcome (all tied) from the default policy's.
      const breweryOnlyPolicy = DefaultRecommendationPolicy(
        similarityScorer: WeightedScorer({BreweryMatchStrategy(): 1.0}),
      );

      await tester.pumpWidget(
        _wrap(
          const BeerDetailScreen(beer: _kfPremium),
          repository: repository,
          extraOverrides: [
            recommendationPolicyProvider.overrideWithValue(breweryOnlyPolicy),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // All three still appear in Similar beers (no candidate shares a
      // brewery with the reference, so every score is exactly 0.0 — still
      // >= the default 0.0 threshold, so nothing is filtered out), but this
      // is driven entirely by the overridden policy's WeightedScorer, not
      // any logic inside BeerDetailScreen.
      expect(find.byKey(const ValueKey('similar:fosters_650')), findsOneWidget);
      expect(find.byKey(const ValueKey('similar:weak_lager_650')), findsOneWidget);
      expect(find.byKey(const ValueKey('similar:craft_ipa_330')), findsOneWidget);
    },
  );

  testWidgets(
    'a recommendation failure leaves the rest of the screen intact and shows empty '
    'recommendation sections instead of crashing',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _oneSkuJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(
          const BeerDetailScreen(beer: _kfPremium),
          repository: repository,
          extraOverrides: [
            recommendationEngineProvider.overrideWithValue(_ThrowingRecommendationEngine()),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // No uncaught exception reached the widget tree.
      expect(tester.takeException(), isNull);

      // The rest of the screen still renders normally.
      expect(find.text('Kingfisher Premium'), findsWidgets);
      expect(find.text('Bottle · 650 mL'), findsOneWidget);

      // Both recommendation sections gracefully fall back to empty.
      expect(find.text('No similar beers available.'), findsOneWidget);
      expect(find.text('No better value alternatives available.'), findsOneWidget);
    },
  );

  testWidgets('shows a "This looks wrong" action for each SKU', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _multipleSkusJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    // Kingfisher Premium has two of its own SKUs in this fixture.
    expect(find.text('This looks wrong'), findsNWidgets(2));
  });

  testWidgets('tapping "This looks wrong" shows a confirmation dialog', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _oneSkuJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('This looks wrong'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Report this listing?'), findsOneWidget);
    expect(find.textContaining('catalog accuracy'), findsOneWidget);
    expect(find.text('Cancel'), findsOneWidget);
    expect(find.text('Report'), findsOneWidget);
  });

  testWidgets('canceling the dialog does not submit a report', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _oneSkuJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('This looks wrong'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Cancel'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsNothing);
    expect(find.text('This looks wrong'), findsOneWidget);
    expect(find.text('Reported'), findsNothing);

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getStringList('wrong_reports'), anyOf(isNull, isEmpty));
  });

  testWidgets(
    'confirming submits the report, shows a success acknowledgement, and '
    'prevents a duplicate submission for the same SKU',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _oneSkuJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('This looks wrong'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Report'));
      await tester.pumpAndSettle();

      // Success acknowledgement.
      expect(find.text('Thanks — this has been reported.'), findsOneWidget);

      // Persisted locally.
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getStringList('wrong_reports'), hasLength(1));

      // Duplicate prevention: the action is replaced by a static
      // "Reported" label, with no tappable "This looks wrong" left for
      // this SKU.
      expect(find.text('Reported'), findsOneWidget);
      expect(find.text('This looks wrong'), findsNothing);
    },
  );
}
