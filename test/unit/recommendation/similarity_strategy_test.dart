import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/benchmark.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/models/style.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';

Sku _sku({
  required String id,
  required String beerId,
  PackageType packageType = PackageType.bottle,
  double abv = 5.0,
  double costPerMlAlcohol = 4.0,
}) {
  return Sku(
    id: id,
    beerId: beerId,
    sizeMl: 650,
    packageType: packageType,
    abv: abv,
    calories: 250,
    price: 100,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: 150,
    costPerMlAlcohol: costPerMlAlcohol,
    valueScore: 50,
    valueVerdict: ValueVerdict.fairValue,
  );
}

void main() {
  final catalog = Catalog(
    catalogVersion: 1,
    generatedAt: DateTime(2026, 1, 1),
    styles: const [
      Style(id: 'lager', name: 'Lager', description: ''),
      Style(id: 'ipa', name: 'IPA', description: ''),
    ],
    beers: const [
      Beer(
        id: 'kf',
        name: 'Kingfisher',
        brewery: 'United Breweries',
        styleId: 'lager',
        isCraft: false,
      ),
      Beer(
        id: 'simba',
        name: 'Simba',
        brewery: 'United Breweries',
        styleId: 'lager',
        isCraft: false,
      ),
      Beer(
        id: 'arbor',
        name: 'Arbor IPA',
        brewery: 'Arbor Brewing',
        styleId: 'ipa',
        isCraft: true,
      ),
    ],
    skus: const [],
    benchmarks: const <Benchmark>[],
  );

  group('StyleMatchStrategy', () {
    const strategy = StyleMatchStrategy();

    test('scores 1.0 when both SKUs\' beers share a style', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'simba');
      expect(strategy.score(a, b, catalog), 1.0);
    });

    test('scores 0.0 when the beers have different styles', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'arbor');
      expect(strategy.score(a, b, catalog), 0.0);
    });

    test('scores 0.0 when a beer cannot be resolved', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'nonexistent_beer');
      expect(strategy.score(a, b, catalog), 0.0);
    });

    test('explains sameStyle when both SKUs\' beers share a style', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'simba');
      expect(strategy.explain(a, b, catalog), RecommendationReason.sameStyle);
    });

    test('explains null when the beers have different styles', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'arbor');
      expect(strategy.explain(a, b, catalog), isNull);
    });
  });

  group('AbvClosenessStrategy', () {
    const strategy = AbvClosenessStrategy(maxDifference: 4.0);

    test('scores 1.0 for identical ABV', () {
      final a = _sku(id: 'a', beerId: 'kf', abv: 5.0);
      final b = _sku(id: 'b', beerId: 'simba', abv: 5.0);
      expect(strategy.score(a, b, catalog), 1.0);
    });

    test('scores partway between 0.0 and 1.0 for a partial difference', () {
      final a = _sku(id: 'a', beerId: 'kf', abv: 5.0);
      final b = _sku(id: 'b', beerId: 'simba', abv: 7.0);
      // Difference of 2.0 out of a max of 4.0 → 0.5.
      expect(strategy.score(a, b, catalog), closeTo(0.5, 1e-9));
    });

    test('scores 0.0 at or beyond the max difference', () {
      final a = _sku(id: 'a', beerId: 'kf', abv: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', abv: 9.0);
      expect(strategy.score(a, b, catalog), 0.0);
    });

    test('explains similarAbv at exactly the 0.5 explain threshold', () {
      final a = _sku(id: 'a', beerId: 'kf', abv: 5.0);
      final b = _sku(id: 'b', beerId: 'simba', abv: 7.0);
      // Difference of 2.0 out of a max of 4.0 → score 0.5, at the threshold.
      expect(strategy.explain(a, b, catalog), RecommendationReason.similarAbv);
    });

    test('explains null when the score is below the 0.5 explain threshold', () {
      final a = _sku(id: 'a', beerId: 'kf', abv: 5.0);
      final b = _sku(id: 'b', beerId: 'simba', abv: 8.0);
      // Difference of 3.0 out of a max of 4.0 → score 0.25, below threshold.
      expect(strategy.explain(a, b, catalog), isNull);
    });

    test('explains null at or beyond the max difference', () {
      final a = _sku(id: 'a', beerId: 'kf', abv: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', abv: 9.0);
      expect(strategy.explain(a, b, catalog), isNull);
    });
  });

  group('PriceClosenessStrategy', () {
    const strategy = PriceClosenessStrategy(maxRelativeDifference: 0.75);

    test('scores 1.0 for identical cost per ml of alcohol', () {
      final a = _sku(id: 'a', beerId: 'kf', costPerMlAlcohol: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', costPerMlAlcohol: 4.0);
      expect(strategy.score(a, b, catalog), 1.0);
    });

    test('scores lower as the relative difference grows', () {
      final a = _sku(id: 'a', beerId: 'kf', costPerMlAlcohol: 4.0);
      final closeB = _sku(id: 'b', beerId: 'simba', costPerMlAlcohol: 4.4);
      final farB = _sku(id: 'c', beerId: 'simba', costPerMlAlcohol: 6.0);

      final closeScore = strategy.score(a, closeB, catalog);
      final farScore = strategy.score(a, farB, catalog);

      expect(closeScore, greaterThan(farScore));
    });

    test('scores 0.0 at or beyond the max relative difference', () {
      final a = _sku(id: 'a', beerId: 'kf', costPerMlAlcohol: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', costPerMlAlcohol: 20.0);
      expect(strategy.score(a, b, catalog), 0.0);
    });

    test('explains similarPrice when the score is above the 0.5 explain threshold', () {
      final a = _sku(id: 'a', beerId: 'kf', costPerMlAlcohol: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', costPerMlAlcohol: 4.4);
      // relativeDifference = 0.1, score = 1 - 0.1/0.75 ≈ 0.867.
      expect(strategy.explain(a, b, catalog), RecommendationReason.similarPrice);
    });

    test('explains null when the score is below the 0.5 explain threshold', () {
      final a = _sku(id: 'a', beerId: 'kf', costPerMlAlcohol: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', costPerMlAlcohol: 6.0);
      // relativeDifference = 0.5, score = 1 - 0.5/0.75 ≈ 0.333.
      expect(strategy.explain(a, b, catalog), isNull);
    });

    test('explains null at or beyond the max relative difference', () {
      final a = _sku(id: 'a', beerId: 'kf', costPerMlAlcohol: 4.0);
      final b = _sku(id: 'b', beerId: 'simba', costPerMlAlcohol: 20.0);
      expect(strategy.explain(a, b, catalog), isNull);
    });
  });

  group('PackageTypeMatchStrategy', () {
    const strategy = PackageTypeMatchStrategy();

    test('scores 1.0 for the same package type', () {
      final a = _sku(id: 'a', beerId: 'kf', packageType: PackageType.can);
      final b = _sku(id: 'b', beerId: 'simba', packageType: PackageType.can);
      expect(strategy.score(a, b, catalog), 1.0);
    });

    test('scores 0.0 for different package types', () {
      final a = _sku(id: 'a', beerId: 'kf', packageType: PackageType.can);
      final b = _sku(id: 'b', beerId: 'simba', packageType: PackageType.bottle);
      expect(strategy.score(a, b, catalog), 0.0);
    });

    test('explains samePackage for the same package type', () {
      final a = _sku(id: 'a', beerId: 'kf', packageType: PackageType.can);
      final b = _sku(id: 'b', beerId: 'simba', packageType: PackageType.can);
      expect(strategy.explain(a, b, catalog), RecommendationReason.samePackage);
    });

    test('explains null for different package types', () {
      final a = _sku(id: 'a', beerId: 'kf', packageType: PackageType.can);
      final b = _sku(id: 'b', beerId: 'simba', packageType: PackageType.bottle);
      expect(strategy.explain(a, b, catalog), isNull);
    });
  });

  group('BreweryMatchStrategy', () {
    const strategy = BreweryMatchStrategy();

    test('scores 1.0 when both SKUs\' beers share a brewery', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'simba');
      expect(strategy.score(a, b, catalog), 1.0);
    });

    test('scores 0.0 for different breweries', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'arbor');
      expect(strategy.score(a, b, catalog), 0.0);
    });

    test('explains sameBrewery when both SKUs\' beers share a brewery', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'simba');
      expect(strategy.explain(a, b, catalog), RecommendationReason.sameBrewery);
    });

    test('explains null for different breweries', () {
      final a = _sku(id: 'a', beerId: 'kf');
      final b = _sku(id: 'b', beerId: 'arbor');
      expect(strategy.explain(a, b, catalog), isNull);
    });
  });
}
