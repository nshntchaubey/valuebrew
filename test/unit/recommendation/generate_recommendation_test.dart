import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/features/recommendation/domain/generate_recommendation.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';

Beer _beer(String id, String name) {
  return Beer(id: id, name: name, brewery: 'Test Brewery', styleId: 'lager', isCraft: false);
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

Catalog _catalog({required List<Beer> beers, required List<Sku> skus}) {
  return Catalog(
    catalogVersion: 1,
    generatedAt: DateTime(2026, 1, 1),
    styles: const [],
    beers: beers,
    skus: skus,
    benchmarks: const [],
  );
}

void main() {
  group('generateRecommendation', () {
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

      final result = generateRecommendation(catalog, budget: 200);

      expect(result, isNotNull);
      expect(result!.sku.id, 'mid_sku');
      expect(result.beer.id, 'mid_beer');
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

      final result = generateRecommendation(catalog, budget: 200);

      expect(result, isNotNull);
      expect(result!.sku.id, 'budget_sku');
    });

    test('returns null when no SKU is at or under the budget', () {
      final beer = _beer('premium_beer', 'Premium Beer');
      final catalog = _catalog(
        beers: [beer],
        skus: [_sku(id: 'premium_sku', beerId: 'premium_beer', price: 500, valueScore: 99)],
      );

      final result = generateRecommendation(catalog, budget: 200);

      expect(result, isNull);
    });

    test('a SKU priced exactly at the budget is a valid candidate', () {
      final beer = _beer('exact_beer', 'Exact Beer');
      final catalog = _catalog(
        beers: [beer],
        skus: [_sku(id: 'exact_sku', beerId: 'exact_beer', price: 200, valueScore: 50)],
      );

      final result = generateRecommendation(catalog, budget: 200);

      expect(result, isNotNull);
      expect(result!.sku.id, 'exact_sku');
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

      final result = generateRecommendation(catalog, budget: 200);

      expect(result!.sku.id, 'first_sku');
    });

    test('the explanation names the beer and states the budget and Value Score reasoning', () {
      final beer = _beer('kf_premium', 'Kingfisher Premium');
      final catalog = _catalog(
        beers: [beer],
        skus: [_sku(id: 'kf_premium_650', beerId: 'kf_premium', price: 110, valueScore: 78, sizeMl: 650)],
      );

      final result = generateRecommendation(catalog, budget: 150);

      expect(result!.explanation, contains('Kingfisher Premium'));
      expect(result.explanation, contains('₹150'));
      expect(result.explanation, contains('650 mL'));
      expect(result.explanation, contains('78'));
    });
  });
}
