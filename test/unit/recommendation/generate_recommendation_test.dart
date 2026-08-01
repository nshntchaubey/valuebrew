import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/catalog/domain/style.dart';
import 'package:valuebrew/features/recommendation/domain/generate_recommendation.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_outcome.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_result.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';

Beer _beer(String id, String name, {String styleId = 'lager'}) {
  return Beer(id: id, name: name, brewery: 'Test Brewery', styleId: styleId, isCraft: false);
}

Sku _sku({
  required String id,
  required String beerId,
  required double price,
  required int valueScore,
  int sizeMl = 500,
}) {
  return Sku(
    id: id,
    beerId: beerId,
    sizeMl: sizeMl,
    packageType: PackageType.bottle,
    abv: 5.0,
    calories: 150,
    price: price,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: price / sizeMl * 1000,
    costPerMlAlcohol: 2.0,
    valueScore: valueScore,
    valueVerdict: ValueVerdict.fairValue,
  );
}

Catalog _catalog({
  required List<Beer> beers,
  required List<Sku> skus,
  List<Style> styles = const [],
}) {
  return Catalog(
    catalogVersion: 1,
    generatedAt: DateTime(2026, 1, 1),
    styles: styles,
    beers: beers,
    skus: skus,
    benchmarks: const [],
  );
}

void main() {
  group('generateRecommendation', () {
    group('budget-only behaviour (Milestone 1 regression)', () {
      test('selects the affordable SKU with the highest Value Score', () {
        final cheapLowValue = _beer('cheap_beer', 'Cheap Beer');
        final midHighValue = _beer('mid_beer', 'Mid Beer');
        final catalog = _catalog(
          beers: [cheapLowValue, midHighValue],
          skus: [
            _sku(id: 'cheap_sku', beerId: 'cheap_beer', price: 80, valueScore: 40),
            _sku(id: 'mid_sku', beerId: 'mid_beer', price: 150, valueScore: 90),
          ],
        );

        final outcome = generateRecommendation(catalog, budget: 200);

        expect(outcome, isA<RecommendationFound>());
        final found = outcome as RecommendationFound;
        expect(found.result.sku.id, 'mid_sku');
        expect(found.result.beer.id, 'mid_beer');
      });

      test('never selects a SKU priced above the budget, even if it has the highest Value Score', () {
        final overBudgetBeer = _beer('premium_beer', 'Premium Beer');
        final affordableBeer = _beer('budget_beer', 'Budget Beer');
        final catalog = _catalog(
          beers: [overBudgetBeer, affordableBeer],
          skus: [
            _sku(id: 'premium_sku', beerId: 'premium_beer', price: 500, valueScore: 99),
            _sku(id: 'budget_sku', beerId: 'budget_beer', price: 120, valueScore: 60),
          ],
        );

        final outcome = generateRecommendation(catalog, budget: 200);

        expect(outcome, isA<RecommendationFound>());
        expect((outcome as RecommendationFound).result.sku.id, 'budget_sku');
      });

      test('returns NoRecommendationWithinBudget when no SKU is at or under the budget', () {
        final beer = _beer('premium_beer', 'Premium Beer');
        final catalog = _catalog(
          beers: [beer],
          skus: [_sku(id: 'premium_sku', beerId: 'premium_beer', price: 500, valueScore: 99)],
        );

        final outcome = generateRecommendation(catalog, budget: 200);

        expect(outcome, equals(const NoRecommendationWithinBudget()));
      });

      test('a SKU priced exactly at the budget is a valid candidate', () {
        final beer = _beer('exact_beer', 'Exact Beer');
        final catalog = _catalog(
          beers: [beer],
          skus: [_sku(id: 'exact_sku', beerId: 'exact_beer', price: 200, valueScore: 50)],
        );

        final outcome = generateRecommendation(catalog, budget: 200);

        expect(outcome, isA<RecommendationFound>());
        expect((outcome as RecommendationFound).result.sku.id, 'exact_sku');
      });

      test('a tie in Value Score is broken deterministically by catalog order (temporary for this slice)', () {
        final firstBeer = _beer('first_beer', 'First Beer');
        final secondBeer = _beer('second_beer', 'Second Beer');
        final catalog = _catalog(
          beers: [firstBeer, secondBeer],
          skus: [
            _sku(id: 'first_sku', beerId: 'first_beer', price: 100, valueScore: 70),
            _sku(id: 'second_sku', beerId: 'second_beer', price: 100, valueScore: 70),
          ],
        );

        final outcome = generateRecommendation(catalog, budget: 200);

        expect((outcome as RecommendationFound).result.sku.id, 'first_sku');
      });

      test('the explanation names the beer and states the budget and Value Score reasoning, with no style clause', () {
        final beer = _beer('kf_premium', 'Kingfisher Premium');
        final catalog = _catalog(
          beers: [beer],
          skus: [_sku(id: 'kf_premium_650', beerId: 'kf_premium', price: 110, valueScore: 78, sizeMl: 650)],
        );

        final outcome = generateRecommendation(catalog, budget: 150);

        final explanation = (outcome as RecommendationFound).result.explanation;
        expect(
          explanation,
          'Within your ₹150 budget, Kingfisher Premium (650 mL) is the '
          'best value available — a Value Score of 78.',
        );
      });
    });

    group('style preference', () {
      test('narrows to the best-value SKU matching the requested style, even over a higher-scoring other style', () {
        final lager = Style(id: 'lager', name: 'Lager', description: 'Crisp');
        final stout = Style(id: 'stout', name: 'Stout', description: 'Dark');
        final lagerBeer = _beer('lager_beer', 'Lager Beer', styleId: 'lager');
        final stoutBeer = _beer('stout_beer', 'Stout Beer', styleId: 'stout');
        final catalog = _catalog(
          styles: [lager, stout],
          beers: [lagerBeer, stoutBeer],
          skus: [
            _sku(id: 'lager_sku', beerId: 'lager_beer', price: 100, valueScore: 60),
            _sku(id: 'stout_sku', beerId: 'stout_beer', price: 100, valueScore: 90),
          ],
        );

        final outcome = generateRecommendation(catalog, budget: 150, styleId: 'lager');

        expect(outcome, isA<RecommendationFound>());
        expect((outcome as RecommendationFound).result.sku.id, 'lager_sku');
      });

      test('returns NoRecommendationMatchingStyle when candidates exist within budget but none match the style', () {
        final lager = Style(id: 'lager', name: 'Lager', description: 'Crisp');
        final lagerBeer = _beer('lager_beer', 'Lager Beer', styleId: 'lager');
        final catalog = _catalog(
          styles: [lager],
          beers: [lagerBeer],
          skus: [_sku(id: 'lager_sku', beerId: 'lager_beer', price: 100, valueScore: 60)],
        );

        final outcome = generateRecommendation(catalog, budget: 150, styleId: 'wheat');

        expect(outcome, equals(const NoRecommendationMatchingStyle()));
      });

      test('the explanation mentions the matched style, preserving the Milestone 1 sentence structure', () {
        final lager = Style(id: 'lager', name: 'Lager', description: 'Crisp');
        final beer = _beer('kf_premium', 'Kingfisher Premium', styleId: 'lager');
        final catalog = _catalog(
          styles: [lager],
          beers: [beer],
          skus: [_sku(id: 'kf_premium_650', beerId: 'kf_premium', price: 110, valueScore: 78, sizeMl: 650)],
        );

        final outcome = generateRecommendation(catalog, budget: 150, styleId: 'lager');

        final explanation = (outcome as RecommendationFound).result.explanation;
        expect(
          explanation,
          'Within your ₹150 budget and matching your preferred Lager style, '
          'Kingfisher Premium (650 mL) is the best value available — '
          'a Value Score of 78.',
        );
      });

      test('omitting styleId behaves exactly as Milestone 1, regardless of styles present in the catalog', () {
        final lager = Style(id: 'lager', name: 'Lager', description: 'Crisp');
        final stout = Style(id: 'stout', name: 'Stout', description: 'Dark');
        final lagerBeer = _beer('lager_beer', 'Lager Beer', styleId: 'lager');
        final stoutBeer = _beer('stout_beer', 'Stout Beer', styleId: 'stout');
        final catalog = _catalog(
          styles: [lager, stout],
          beers: [lagerBeer, stoutBeer],
          skus: [
            _sku(id: 'lager_sku', beerId: 'lager_beer', price: 100, valueScore: 60),
            _sku(id: 'stout_sku', beerId: 'stout_beer', price: 100, valueScore: 90),
          ],
        );

        final outcome = generateRecommendation(catalog, budget: 150);

        expect(outcome, isA<RecommendationFound>());
        final found = outcome as RecommendationFound;
        expect(found.result.sku.id, 'stout_sku');
        expect(found.result.explanation, isNot(contains('matching your preferred')));
      });
    });
  });

  group('RecommendationOutcome.canBeRefinedFurther', () {
    test('is true for RecommendationFound', () {
      final beer = _beer('beer', 'Beer');
      final sku = _sku(id: 'sku', beerId: 'beer', price: 100, valueScore: 50);
      final found = RecommendationFound(
        RecommendationResult(sku: sku, beer: beer, explanation: 'test'),
      );

      expect(found.canBeRefinedFurther, isTrue);
    });

    test('is true for NoRecommendationMatchingStyle', () {
      expect(const NoRecommendationMatchingStyle().canBeRefinedFurther, isTrue);
    });

    test('is false for NoRecommendationWithinBudget', () {
      expect(const NoRecommendationWithinBudget().canBeRefinedFurther, isFalse);
    });
  });
}
