import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
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

const _similarBeersJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
    { "id": "ipa", "name": "IPA", "description": "Hop-forward, bitter" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "lager", "is_craft": true },
    { "id": "simba_strong", "name": "Simba Strong", "brewery": "Kals Brewing", "style_id": "lager", "is_craft": false },
    { "id": "weak_lager", "name": "Weak Lager", "brewery": "Some Brewery", "style_id": "lager", "is_craft": false },
    { "id": "no_sku_lager", "name": "No Sku Lager", "brewery": "Ghost Brewery", "style_id": "lager", "is_craft": false },
    { "id": "craft_ipa", "name": "Craft IPA", "brewery": "Arbor Brewing", "style_id": "ipa", "is_craft": true }
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
      "cost_per_ml_alcohol": 3.52,
      "value_score": 50,
      "value_verdict": "fair_value"
    },
    {
      "id": "toit_porter_330",
      "beer_id": "toit_porter",
      "size_ml": 330,
      "package_type": "can",
      "abv": 6.5,
      "calories": 220,
      "price": 250,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 757.6,
      "cost_per_ml_alcohol": 11.66,
      "value_score": 78,
      "value_verdict": "great_value"
    },
    {
      "id": "simba_strong_500",
      "beer_id": "simba_strong",
      "size_ml": 500,
      "package_type": "can",
      "abv": 8.0,
      "calories": 300,
      "price": 150,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 300.0,
      "cost_per_ml_alcohol": 3.75,
      "value_score": 78,
      "value_verdict": "great_value"
    },
    {
      "id": "weak_lager_650",
      "beer_id": "weak_lager",
      "size_ml": 650,
      "package_type": "bottle",
      "abv": 4.5,
      "calories": 260,
      "price": 140,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 215.4,
      "cost_per_ml_alcohol": 4.78,
      "value_score": 30,
      "value_verdict": "overpriced"
    },
    {
      "id": "craft_ipa_330",
      "beer_id": "craft_ipa",
      "size_ml": 330,
      "package_type": "bottle",
      "abv": 6.0,
      "calories": 210,
      "price": 300,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 909.1,
      "cost_per_ml_alcohol": 15.15,
      "value_score": 90,
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

Widget _wrap(Widget child, {required CatalogRepository repository}) {
  return ProviderScope(
    overrides: [catalogRepositoryProvider.overrideWithValue(repository)],
    child: MaterialApp(home: child),
  );
}

void main() {
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

  testWidgets('shows the empty-state message when there are no similar beers', (
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

    expect(find.text('Similar & Better Value'), findsOneWidget);
    expect(find.text('No similar beers available.'), findsOneWidget);
  });

  testWidgets(
    'shows similar beers ranked by value score, excluding the current beer, '
    'other styles, and beers with no SKUs',
    (WidgetTester tester) async {
      final repository = CatalogRepository(
        loadAsset: (key) async => _similarBeersJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
      );
      await tester.pumpAndSettle();

      // Same-style beers with SKUs are shown, correctly ranked.
      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Toit Brewpub'), findsOneWidget);
      expect(find.text('Simba Strong'), findsOneWidget);
      expect(find.text('Kals Brewing'), findsOneWidget);
      expect(find.text('Weak Lager'), findsOneWidget);

      // The viewed beer itself must not appear in its own similar list.
      // (Its name still appears twice as-is: once in the AppBar title,
      // once as the screen's own heading — never a third time in the
      // similar-beers section below.)
      expect(find.text('Kingfisher Premium'), findsNWidgets(2));

      // A beer in a different style must not appear.
      expect(find.text('Craft IPA'), findsNothing);

      // A same-style beer with no SKUs must not appear — there is no
      // value score to display or rank it by.
      expect(find.text('No Sku Lager'), findsNothing);

      // Toit Porter and Simba Strong tie at 78; catalog order (Toit
      // Porter listed first) must be preserved. Weak Lager (30) ranks
      // last among the three.
      final toitY = tester.getTopLeft(find.text('Toit Porter')).dy;
      final simbaY = tester.getTopLeft(find.text('Simba Strong')).dy;
      final weakY = tester.getTopLeft(find.text('Weak Lager')).dy;
      expect(toitY, lessThan(simbaY));
      expect(simbaY, lessThan(weakY));
    },
  );

  testWidgets('tapping a similar beer pushes a new BeerDetailScreen for it', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _similarBeersJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    final toitRow = find.widgetWithText(ListTile, 'Toit Porter');
    await tester.tap(toitRow);
    await tester.pumpAndSettle();

    // The pushed screen's AppBar title and content uniquely identify it as
    // Toit Porter's own BeerDetailScreen (its own brewery and value score,
    // not Kingfisher Premium's).
    expect(find.widgetWithText(AppBar, 'Toit Porter'), findsOneWidget);
    expect(find.text('Toit Brewpub'), findsOneWidget);
    expect(find.text('Value score: 78 (Great value)'), findsWidgets);
  });
}
