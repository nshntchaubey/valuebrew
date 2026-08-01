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
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
    { "id": "stout", "name": "Stout", "description": "Dark, roasted malt character" },
    { "id": "wheat", "name": "Wheat", "description": "Cloudy, banana and clove notes" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "stout", "is_craft": true }
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
      "price": 120,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 363.6,
      "cost_per_ml_alcohol": 5.6,
      "value_score": 60,
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

  Future<void> enterBudgetAndSubmit(WidgetTester tester, String budget) async {
    await tester.enterText(find.byType(TextField), budget);
    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();
  }

  Future<void> openRefinementAndSelect(WidgetTester tester, String styleLabel) async {
    await tester.tap(find.text('Refine recommendation'));
    await tester.pumpAndSettle();
    await tester.tap(find.text(styleLabel));
    await tester.pumpAndSettle();
  }

  group('Milestone 1 regression', () {
    testWidgets('entering a budget and submitting shows the correct recommended beer and its explanation', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('₹150'), findsOneWidget);
      expect(find.textContaining('650 mL'), findsOneWidget);
      expect(find.textContaining('78'), findsOneWidget);
    });

    testWidgets('a budget too low for anything in the catalog shows an honest no-fit message', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '10');

      expect(find.text('No beer in the catalog fits that budget.'), findsOneWidget);
    });

    testWidgets('an unparseable budget shows a validation error and no result', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, 'not a number');

      expect(find.text('Enter a valid budget.'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);
      expect(find.text('No beer in the catalog fits that budget.'), findsNothing);
    });

    testWidgets('leaving Style untouched produces output identical to Milestone 1, even with multiple styles in the catalog', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('matching your preferred'), findsNothing);
    });
  });

  group('refinement visibility', () {
    testWidgets('refinement is hidden before a recommendation exists', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);

      expect(find.text('Refine recommendation'), findsNothing);
    });

    testWidgets('refinement is visible after RecommendationFound', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Refine recommendation'), findsOneWidget);
    });

    testWidgets('refinement is hidden after NoRecommendationWithinBudget', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '10');

      expect(find.text('Refine recommendation'), findsNothing);
      expect(find.text('No preference'), findsNothing);
    });

    testWidgets('refinement remains available after a style conflict', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Wheat');

      expect(find.text('No preference'), findsOneWidget);
      expect(find.text('Lager'), findsOneWidget);
      expect(find.text('Stout'), findsOneWidget);
    });

    testWidgets('refinement remains available after a successful refinement', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('No preference'), findsOneWidget);
      expect(find.text('Lager'), findsOneWidget);
    });
  });

  group('style selection', () {
    testWidgets('selecting a Style updates the recommendation to the best match within that style', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Kingfisher Premium'), findsOneWidget);

      await openRefinementAndSelect(tester, 'Stout');

      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);
    });

    testWidgets('selecting a conflicting Style shows an honest conflict message', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Wheat');

      expect(find.text('No beer within your budget matches that style.'), findsOneWidget);
    });

    testWidgets('selecting a different Style after a conflict succeeds', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Wheat');

      await tester.tap(find.text('Stout'));
      await tester.pumpAndSettle();

      expect(find.text('Toit Porter'), findsOneWidget);
    });
  });

  group('clearing Style', () {
    testWidgets('clearing a selected Style restores the original budget-only recommendation', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      expect(find.text('Toit Porter'), findsOneWidget);

      await tester.tap(find.text('No preference'));
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text('Toit Porter'), findsNothing);
    });

    testWidgets('clearing Style produces output identical to never selecting Style in the first place', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      await tester.tap(find.text('No preference'));
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('₹150'), findsOneWidget);
      expect(find.textContaining('matching your preferred'), findsNothing);
    });
  });

  group('preference persistence', () {
    testWidgets('editing the budget after selecting a Style preserves that Style in the new recommendation', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      expect(find.text('Toit Porter'), findsOneWidget);

      // Narrowing the budget below Toit Porter's price (120) but still
      // above Kingfisher's (110) proves the Style filter, not chance,
      // determines the result: if Style had been discarded, this budget
      // alone would resolve to Kingfisher Premium instead.
      await enterBudgetAndSubmit(tester, '115');

      expect(find.text('No beer within your budget matches that style.'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);
    });

    testWidgets('resubmitting the budget regenerates using the currently selected Style, not the unfiltered best value', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      // Widening the budget proves the same thing from the other
      // direction: Kingfisher Premium has the higher Value Score and
      // would win an unfiltered search, so its absence here proves the
      // Style preference survived the budget change.
      await enterBudgetAndSubmit(tester, '300');

      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);
    });

    testWidgets('invalid budget input does not clear a previously selected Style', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      await enterBudgetAndSubmit(tester, 'not a number');

      expect(find.text('Enter a valid budget.'), findsOneWidget);

      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Toit Porter'), findsOneWidget);
    });
  });
}
