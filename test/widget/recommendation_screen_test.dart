import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/recommendation/presentation/recommendation_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "lager", "is_craft": true }
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
      "value_score": 55,
      "value_verdict": "fair_value"
    }
  ],
  "benchmarks": []
}
''';

void main() {
  Future<void> pumpRecommendationScreen(WidgetTester tester, {String json = _catalogJson}) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => json,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: const MaterialApp(home: RecommendationScreen()),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('entering a budget and submitting shows the correct recommended beer and its explanation', (
    WidgetTester tester,
  ) async {
    await pumpRecommendationScreen(tester);

    await tester.enterText(find.byType(TextField), '150');
    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.textContaining('₹150'), findsOneWidget);
    expect(find.textContaining('650 mL'), findsOneWidget);
    expect(find.textContaining('78'), findsOneWidget);
    expect(find.text('Toit Porter'), findsNothing);
  });

  testWidgets('a budget too low for anything in the catalog shows an honest no-fit message', (
    WidgetTester tester,
  ) async {
    await pumpRecommendationScreen(tester);

    await tester.enterText(find.byType(TextField), '10');
    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();

    expect(find.text('No beer in the catalog fits that budget.'), findsOneWidget);
  });

  testWidgets('an unparseable budget shows a validation error and no result', (
    WidgetTester tester,
  ) async {
    await pumpRecommendationScreen(tester);

    await tester.enterText(find.byType(TextField), 'not a number');
    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();

    expect(find.text('Enter a valid budget.'), findsOneWidget);
    expect(find.text('Kingfisher Premium'), findsNothing);
    expect(find.text('No beer in the catalog fits that budget.'), findsNothing);
  });
}
