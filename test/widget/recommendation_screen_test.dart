import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/presentation/beer_detail_screen.dart';
import 'package:valuebrew/features/recommendation/presentation/recommendation_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/navigation/value_brew_navigator.dart';

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
  Future<void> pumpRecommendationScreen(
    WidgetTester tester, {
    String json = _catalogJson,
    bool isPlanning = false,
  }) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => json,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: MaterialApp(
          navigatorKey: rootNavigatorKey,
          home: RecommendationScreen(isPlanning: isPlanning),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  const planningCaveat =
      'This is a provisional recommendation for planning ahead — prices '
      'and availability may have changed by the time you actually buy.';

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

  group('navigation to Beer Detail', () {
    testWidgets('"See full details" is shown only for RecommendationFound', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('See full details'), findsOneWidget);
    });

    testWidgets('"See full details" is hidden for NoRecommendationWithinBudget', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '10');

      expect(find.text('See full details'), findsNothing);
    });

    testWidgets('"See full details" is hidden for NoRecommendationMatchingStyle', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Wheat');

      expect(find.text('See full details'), findsNothing);
    });

    testWidgets('tapping "See full details" opens Beer Detail for the recommended SKU', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      await tester.tap(find.text('See full details'));
      await tester.pumpAndSettle();

      expect(find.byType(BeerDetailScreen), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsOneWidget);
    });

    testWidgets('navigating back from Beer Detail preserves Recommendation state', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      await tester.tap(find.text('See full details'));
      await tester.pumpAndSettle();
      expect(find.byType(BeerDetailScreen), findsOneWidget);

      await tester.pageBack();
      await tester.pumpAndSettle();

      expect(find.byType(RecommendationScreen), findsOneWidget);
      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('No preference'), findsOneWidget);
    });
  });

  group('carried-forward Recommendation behaviour', () {
    testWidgets('clearing a selected Style while in conflict restores the original budget-only recommendation', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Wheat');

      expect(find.text('No beer within your budget matches that style.'), findsOneWidget);

      await tester.tap(find.text('No preference'));
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('matching your preferred'), findsNothing);
    });

    testWidgets('a Style survives a detour through NoRecommendationWithinBudget', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Stout');

      expect(find.text('Toit Porter'), findsOneWidget);

      // Narrowing the budget below anything in the catalog makes refinement
      // temporarily unavailable — this must not discard the Style.
      await enterBudgetAndSubmit(tester, '10');

      expect(find.text('No beer in the catalog fits that budget.'), findsOneWidget);
      expect(find.text('Refine recommendation'), findsNothing);

      // Widening the budget back proves Stout survived the detour:
      // Kingfisher Premium has the higher Value Score and would win an
      // unfiltered search, so its absence here proves the Style wasn't lost.
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);
    });
  });

  group('tie disclosure', () {
    const tiedDifferentBeersJson = '''
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
          "price": 100,
          "price_last_checked": "2026-07-20",
          "price_source": "test",
          "cost_per_litre": 153.8,
          "cost_per_ml_alcohol": 3.2,
          "value_score": 70,
          "value_verdict": "fair_value"
        },
        {
          "id": "toit_porter_500",
          "beer_id": "toit_porter",
          "size_ml": 500,
          "package_type": "can",
          "abv": 6.5,
          "calories": 220,
          "price": 100,
          "price_last_checked": "2026-07-18",
          "price_source": "test",
          "cost_per_litre": 200.0,
          "cost_per_ml_alcohol": 3.08,
          "value_score": 70,
          "value_verdict": "fair_value"
        }
      ],
      "benchmarks": []
    }
    ''';

    const tiedSameBeerJson = '''
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
          "id": "kf_premium_330",
          "beer_id": "kf_premium",
          "size_ml": 330,
          "package_type": "can",
          "abv": 4.8,
          "calories": 130,
          "price": 100,
          "price_last_checked": "2026-07-20",
          "price_source": "test",
          "cost_per_litre": 303.0,
          "cost_per_ml_alcohol": 6.3,
          "value_score": 70,
          "value_verdict": "fair_value"
        },
        {
          "id": "kf_premium_650",
          "beer_id": "kf_premium",
          "size_ml": 650,
          "package_type": "bottle",
          "abv": 4.8,
          "calories": 260,
          "price": 100,
          "price_last_checked": "2026-07-20",
          "price_source": "test",
          "cost_per_litre": 153.8,
          "cost_per_ml_alcohol": 3.2,
          "value_score": 70,
          "value_verdict": "fair_value"
        }
      ],
      "benchmarks": []
    }
    ''';

    testWidgets('shows the tie explanation', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, json: tiedDifferentBeersJson);
      await enterBudgetAndSubmit(tester, '150');

      expect(
        find.text(
          "Within your ₹150 budget, 2 beers are equally good, each with a "
          "Value Score of 70 — these are equivalent on everything you've "
          "told me matters.",
        ),
        findsOneWidget,
      );
    });

    testWidgets('shows both tied candidates', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, json: tiedDifferentBeersJson);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.textContaining('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('Toit Porter'), findsOneWidget);
    });

    testWidgets('a tie between two SKUs of the same beer renders distinguishable rows', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester, json: tiedSameBeerJson);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.textContaining('330 mL'), findsOneWidget);
      expect(find.textContaining('650 mL'), findsOneWidget);
      expect(find.textContaining('Can'), findsOneWidget);
      expect(find.textContaining('Bottle'), findsOneWidget);
    });

    testWidgets('refinement remains available from a tie', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, json: tiedDifferentBeersJson);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Refine recommendation'), findsOneWidget);
    });

    // Kingfisher Premium (lager, ₹90) and Toit Porter (stout, ₹100) share
    // the same Value Score at budget 150, so both tie; narrowing the
    // budget to 95 or selecting the Lager style each independently
    // resolve the tie down to Kingfisher Premium alone.
    const tiedResolvableJson = '''
    {
      "catalog_version": 1,
      "generated_at": "2026-01-01T00:00:00Z",
      "styles": [
        { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
        { "id": "stout", "name": "Stout", "description": "Dark, roasted malt character" }
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
          "price": 90,
          "price_last_checked": "2026-07-20",
          "price_source": "test",
          "cost_per_litre": 138.5,
          "cost_per_ml_alcohol": 2.9,
          "value_score": 70,
          "value_verdict": "fair_value"
        },
        {
          "id": "toit_porter_500",
          "beer_id": "toit_porter",
          "size_ml": 500,
          "package_type": "can",
          "abv": 6.5,
          "calories": 220,
          "price": 100,
          "price_last_checked": "2026-07-18",
          "price_source": "test",
          "cost_per_litre": 200.0,
          "cost_per_ml_alcohol": 3.08,
          "value_score": 70,
          "value_verdict": "fair_value"
        }
      ],
      "benchmarks": []
    }
    ''';

    group('navigation to Beer Detail', () {
      testWidgets('tapping the first candidate\'s "See full details" opens Beer Detail for that SKU', (
        WidgetTester tester,
      ) async {
        await pumpRecommendationScreen(tester, json: tiedDifferentBeersJson);
        await enterBudgetAndSubmit(tester, '150');

        // Candidates render in catalog order — Kingfisher Premium first.
        await tester.tap(find.widgetWithText(TextButton, 'See full details').at(0));
        await tester.pumpAndSettle();

        expect(find.byType(BeerDetailScreen), findsOneWidget);
        expect(find.text('Kingfisher Premium'), findsOneWidget);
      });

      testWidgets('tapping the second candidate\'s "See full details" opens Beer Detail for that SKU', (
        WidgetTester tester,
      ) async {
        await pumpRecommendationScreen(tester, json: tiedDifferentBeersJson);
        await enterBudgetAndSubmit(tester, '150');

        await tester.tap(find.widgetWithText(TextButton, 'See full details').at(1));
        await tester.pumpAndSettle();

        expect(find.byType(BeerDetailScreen), findsOneWidget);
        expect(find.text('Toit Porter'), findsOneWidget);
      });

      testWidgets('navigating back from a tied candidate\'s Beer Detail preserves the tie', (
        WidgetTester tester,
      ) async {
        await pumpRecommendationScreen(tester, json: tiedDifferentBeersJson);
        await enterBudgetAndSubmit(tester, '150');

        await tester.tap(find.widgetWithText(TextButton, 'See full details').at(0));
        await tester.pumpAndSettle();
        expect(find.byType(BeerDetailScreen), findsOneWidget);

        await tester.pageBack();
        await tester.pumpAndSettle();

        expect(find.byType(RecommendationScreen), findsOneWidget);
        expect(find.textContaining('Kingfisher Premium'), findsOneWidget);
        expect(find.textContaining('Toit Porter'), findsOneWidget);
      });
    });

    group('interaction with existing behaviour', () {
      testWidgets('selecting a Style resolves a tie down to a single recommendation', (
        WidgetTester tester,
      ) async {
        await pumpRecommendationScreen(tester, json: tiedResolvableJson);
        await enterBudgetAndSubmit(tester, '150');
        expect(find.textContaining('Kingfisher Premium'), findsOneWidget);
        expect(find.textContaining('Toit Porter'), findsOneWidget);

        await openRefinementAndSelect(tester, 'Lager');

        expect(find.text('Kingfisher Premium'), findsOneWidget);
        expect(find.text('Toit Porter'), findsNothing);
      });

      testWidgets('narrowing the budget resolves a tie down to a single recommendation', (
        WidgetTester tester,
      ) async {
        await pumpRecommendationScreen(tester, json: tiedResolvableJson);
        await enterBudgetAndSubmit(tester, '150');
        expect(find.textContaining('Kingfisher Premium'), findsOneWidget);
        expect(find.textContaining('Toit Porter'), findsOneWidget);

        await enterBudgetAndSubmit(tester, '95');

        expect(find.text('Kingfisher Premium'), findsOneWidget);
        expect(find.text('Toit Porter'), findsNothing);
      });
    });
  });

  group('planning mode', () {
    const tiedPlanningJson = '''
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
          "price": 100,
          "price_last_checked": "2026-07-20",
          "price_source": "test",
          "cost_per_litre": 153.8,
          "cost_per_ml_alcohol": 3.2,
          "value_score": 70,
          "value_verdict": "fair_value"
        },
        {
          "id": "toit_porter_500",
          "beer_id": "toit_porter",
          "size_ml": 500,
          "package_type": "can",
          "abv": 6.5,
          "calories": 220,
          "price": 100,
          "price_last_checked": "2026-07-18",
          "price_source": "test",
          "cost_per_litre": 200.0,
          "cost_per_ml_alcohol": 3.08,
          "value_score": 70,
          "value_verdict": "fair_value"
        }
      ],
      "benchmarks": []
    }
    ''';

    testWidgets('the banner is absent when isPlanning is false', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text(planningCaveat), findsNothing);
    });

    testWidgets('the banner is present when isPlanning is true', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, isPlanning: true);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text(planningCaveat), findsOneWidget);
    });

    testWidgets('the banner persists after a budget edit', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, isPlanning: true);
      await enterBudgetAndSubmit(tester, '150');
      expect(find.text(planningCaveat), findsOneWidget);

      await enterBudgetAndSubmit(tester, '120');

      expect(find.text(planningCaveat), findsOneWidget);
    });

    testWidgets('the banner persists after Style refinement', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, isPlanning: true);
      await enterBudgetAndSubmit(tester, '150');
      expect(find.text(planningCaveat), findsOneWidget);

      await openRefinementAndSelect(tester, 'Stout');

      expect(find.text(planningCaveat), findsOneWidget);
    });

    testWidgets('the banner is shown alongside RecommendationFound', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, isPlanning: true);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text(planningCaveat), findsOneWidget);
    });

    testWidgets('the banner is shown alongside RecommendationTie', (WidgetTester tester) async {
      await pumpRecommendationScreen(tester, json: tiedPlanningJson, isPlanning: true);
      await enterBudgetAndSubmit(tester, '150');

      expect(find.textContaining('Kingfisher Premium'), findsOneWidget);
      expect(find.textContaining('Toit Porter'), findsOneWidget);
      expect(find.text(planningCaveat), findsOneWidget);
    });

    testWidgets('the banner is shown alongside NoRecommendationWithinBudget', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester, isPlanning: true);
      await enterBudgetAndSubmit(tester, '10');

      expect(find.text('No beer in the catalog fits that budget.'), findsOneWidget);
      expect(find.text(planningCaveat), findsOneWidget);
    });

    testWidgets('the banner is shown alongside NoRecommendationMatchingStyle', (
      WidgetTester tester,
    ) async {
      await pumpRecommendationScreen(tester, isPlanning: true);
      await enterBudgetAndSubmit(tester, '150');
      await openRefinementAndSelect(tester, 'Wheat');

      expect(find.text('No beer within your budget matches that style.'), findsOneWidget);
      expect(find.text(planningCaveat), findsOneWidget);
    });
  });
}
