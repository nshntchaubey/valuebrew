import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/presentation/beer_detail_screen.dart';
import 'package:valuebrew/features/price_verification/presentation/price_verification_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';
import 'package:valuebrew/navigation/value_brew_navigator.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
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

const _catalogJsonWithBenchmark = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
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
      "price_source": "test",
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
''';

void main() {
  Future<void> pumpBeerDetailScreen(
    WidgetTester tester, {
    String skuId = 'kf_premium_650',
    String catalogJson = _catalogJson,
    Future<String> Function(String key)? loadAsset,
  }) async {
    final fakeRepository = CatalogRepository(
      loadAsset: loadAsset ?? (key) async => catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: MaterialApp(
          navigatorKey: rootNavigatorKey,
          home: BeerDetailScreen(skuId: skuId),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('shows the beer identity: name, brewery, and style', (WidgetTester tester) async {
    await pumpBeerDetailScreen(tester);

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.text('United Breweries'), findsOneWidget);
    expect(find.text('Lager'), findsOneWidget);
  });

  testWidgets('shows the SKU information: price, package, ABV, and volume', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(tester);

    expect(find.textContaining('₹110'), findsOneWidget);
    expect(find.text('Bottle'), findsOneWidget);
    expect(find.text('650 mL'), findsOneWidget);
    expect(find.textContaining('4.8%'), findsOneWidget);
  });

  testWidgets('shows the value information: score and verdict, already computed', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(tester);

    expect(find.textContaining('78'), findsOneWidget);
    expect(find.textContaining('Great value'), findsOneWidget);
  });

  testWidgets('shows the Style Benchmark standing when a benchmark exists for the style', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(tester, catalogJson: _catalogJsonWithBenchmark);

    expect(find.text('Better value than typical for this style'), findsOneWidget);
  });

  testWidgets('omits the Style Benchmark section when no benchmark exists for the style', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(tester);

    expect(find.text('Better value than typical for this style'), findsNothing);
    expect(find.text('Typical value for this style'), findsNothing);
    expect(find.text('Worse value than typical for this style'), findsNothing);
  });

  testWidgets('shows price staleness via priceLastChecked, already existing catalog data', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(tester);

    expect(find.textContaining('2026-07-20'), findsOneWidget);
  });

  testWidgets('shows a skeleton loading state while the catalog loads', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async {
        await Future<void>.delayed(const Duration(milliseconds: 100));
        return _catalogJson;
      },
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: const MaterialApp(home: BeerDetailScreen(skuId: 'kf_premium_650')),
      ),
    );
    await tester.pump();

    expect(find.byType(SkeletonBox), findsWidgets);
    expect(find.text('Kingfisher Premium'), findsNothing);

    await tester.pumpAndSettle();
  });

  testWidgets('shows an error message and Retry when the catalog fails to load', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(
      tester,
      loadAsset: (key) async => throw Exception('boom'),
    );

    expect(find.text("Couldn't load the beer catalog."), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
    expect(find.textContaining('Exception'), findsNothing);
  });

  testWidgets('shows a not-found message when skuId matches no SKU in the catalog', (
    WidgetTester tester,
  ) async {
    await pumpBeerDetailScreen(tester, skuId: 'nonexistent_sku');

    expect(find.text("This beer couldn't be found."), findsOneWidget);
    expect(find.text('Kingfisher Premium'), findsNothing);
  });

  group('navigation to Price Verification', () {
    testWidgets('tapping "Verify price" opens Price Verification for the correct SKU', (
      WidgetTester tester,
    ) async {
      await pumpBeerDetailScreen(tester);

      await tester.tap(find.text('Verify price'));
      await tester.pumpAndSettle();

      expect(find.byType(PriceVerificationScreen), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('₹110'), findsOneWidget);
    });

    testWidgets('navigating back from Price Verification preserves Beer Detail state', (
      WidgetTester tester,
    ) async {
      await pumpBeerDetailScreen(tester);

      await tester.tap(find.text('Verify price'));
      await tester.pumpAndSettle();
      expect(find.byType(PriceVerificationScreen), findsOneWidget);

      await tester.pageBack();
      await tester.pumpAndSettle();

      expect(find.byType(BeerDetailScreen), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text('Bottle'), findsOneWidget);
    });
  });
}
