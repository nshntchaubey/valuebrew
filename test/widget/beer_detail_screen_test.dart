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

      expect(find.text('bottle · 650ml'), findsOneWidget);
      expect(find.text('MRP: ₹110.0'), findsOneWidget);
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
    expect(find.text('bottle · 650ml'), findsOneWidget);
    expect(find.text('MRP: ₹110.0'), findsOneWidget);
    expect(find.text('Value score: 78 (Great value)'), findsOneWidget);

    expect(find.text('can · 330ml'), findsOneWidget);
    expect(find.text('MRP: ₹60.0'), findsOneWidget);
    expect(find.text('Value score: 55 (Fair value)'), findsOneWidget);

    // The other beer's SKU must not appear on this screen.
    expect(find.text('can · 500ml'), findsNothing);
    expect(find.text('MRP: ₹250.0'), findsNothing);
    expect(find.text('Value score: 20 (Overpriced for this ABV)'), findsNothing);
  });
}
