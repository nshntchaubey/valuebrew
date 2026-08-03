import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/price_verification/presentation/price_verification_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';

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

const _orphanSkuCatalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [],
  "beers": [],
  "skus": [
    {
      "id": "orphan_sku",
      "beer_id": "missing_beer",
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

void main() {
  Future<void> pumpPriceVerificationScreen(
    WidgetTester tester, {
    String skuId = 'kf_premium_650',
    Future<String> Function(String key)? loadAsset,
  }) async {
    final fakeRepository = CatalogRepository(
      loadAsset: loadAsset ?? (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: MaterialApp(home: PriceVerificationScreen(skuId: skuId)),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> enterChargedPriceAndSubmit(WidgetTester tester, String price) async {
    await tester.enterText(find.byType(TextField), price);
    await tester.tap(find.text('Verify price'));
    await tester.pumpAndSettle();
  }

  testWidgets('shows the beer identity and legal price as context', (WidgetTester tester) async {
    await pumpPriceVerificationScreen(tester);

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.textContaining('₹110'), findsOneWidget);
  });

  testWidgets('a charged price exactly equal to the legal price shows atLegalPrice', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(tester);
    await enterChargedPriceAndSubmit(tester, '110');

    expect(find.text('At the legal price'), findsOneWidget);
    expect(find.text('You paid ₹110, exactly the legal price.'), findsOneWidget);
  });

  testWidgets('a charged price below the legal price shows belowLegalPrice, never as a problem', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(tester);
    await enterChargedPriceAndSubmit(tester, '100');

    expect(find.text('Below the legal price'), findsOneWidget);
    expect(find.text('You paid ₹100, below the legal price of ₹110.'), findsOneWidget);
  });

  testWidgets('a charged price above the legal price shows aboveLegalPrice, flagged plainly', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(tester);
    await enterChargedPriceAndSubmit(tester, '120');

    expect(find.text('Above the legal price'), findsOneWidget);
    expect(
      find.text('You paid ₹120, above the legal price of ₹110. This may be an overcharge.'),
      findsOneWidget,
    );
  });

  testWidgets('an unparseable charged price after a valid result clears the shown verdict', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(tester);
    await enterChargedPriceAndSubmit(tester, '120');

    expect(find.text('Above the legal price'), findsOneWidget);

    await enterChargedPriceAndSubmit(tester, 'not a number');

    expect(find.text('Enter a valid price.'), findsOneWidget);
    expect(find.text('Above the legal price'), findsNothing);
  });

  testWidgets('an unparseable charged price shows a validation error and no result', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(tester);
    await enterChargedPriceAndSubmit(tester, 'not a number');

    expect(find.text('Enter a valid price.'), findsOneWidget);
    expect(find.text('At the legal price'), findsNothing);
    expect(find.text('Below the legal price'), findsNothing);
    expect(find.text('Above the legal price'), findsNothing);
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
        child: const MaterialApp(home: PriceVerificationScreen(skuId: 'kf_premium_650')),
      ),
    );
    await tester.pump();

    expect(find.byType(SkeletonBox), findsWidgets);
    expect(find.text('Kingfisher Premium'), findsNothing);

    await tester.pumpAndSettle();
  });

  testWidgets('shows an error message and Retry when the catalog fails to load, with no raw exception text', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(
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
    await pumpPriceVerificationScreen(tester, skuId: 'nonexistent_sku');

    expect(find.text("This beer couldn't be found."), findsOneWidget);
    expect(find.text('Kingfisher Premium'), findsNothing);
  });

  testWidgets('shows a not-found message when the SKU exists but its beer cannot be resolved', (
    WidgetTester tester,
  ) async {
    await pumpPriceVerificationScreen(
      tester,
      skuId: 'orphan_sku',
      loadAsset: (key) async => _orphanSkuCatalogJson,
    );

    expect(find.text("This beer couldn't be found."), findsOneWidget);
  });
}
