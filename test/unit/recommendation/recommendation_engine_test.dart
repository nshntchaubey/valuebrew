import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/benchmark.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/models/style.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';
import 'package:valuebrew/features/recommendation/services/recommendation_engine.dart';

Sku _sku({
  required String id,
  required String beerId,
  PackageType packageType = PackageType.bottle,
  double abv = 5.0,
  double costPerMlAlcohol = 4.0,
  int valueScore = 50,
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
    valueScore: valueScore,
    valueVerdict: ValueVerdict.fairValue,
  );
}

void main() {
  final engine = RecommendationEngine();

  group('similarBeers', () {
    test('excludes the reference SKU and ranks the rest by similarity, most similar first', () {
      final catalog = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime(2026, 1, 1),
        styles: const [
          Style(id: 'lager', name: 'Lager', description: ''),
          Style(id: 'ipa', name: 'IPA', description: ''),
        ],
        beers: const [
          Beer(id: 'ref', name: 'Reference', brewery: 'Brewery A', styleId: 'lager', isCraft: false),
          Beer(id: 'best', name: 'Best Match', brewery: 'Brewery A', styleId: 'lager', isCraft: false),
          Beer(id: 'mid', name: 'Middle Match', brewery: 'Brewery B', styleId: 'lager', isCraft: false),
          Beer(id: 'worst', name: 'Worst Match', brewery: 'Brewery C', styleId: 'ipa', isCraft: true),
        ],
        skus: [
          _sku(id: 'ref_sku', beerId: 'ref', abv: 5.0, costPerMlAlcohol: 4.0, packageType: PackageType.bottle),
          // Identical on every dimension the default scorer weighs.
          _sku(id: 'best_sku', beerId: 'best', abv: 5.0, costPerMlAlcohol: 4.0, packageType: PackageType.bottle),
          // Same style, somewhat close ABV/price, different package/brewery.
          _sku(id: 'mid_sku', beerId: 'mid', abv: 6.0, costPerMlAlcohol: 5.0, packageType: PackageType.can),
          // Different style, far ABV/price, different package/brewery.
          _sku(id: 'worst_sku', beerId: 'worst', abv: 10.0, costPerMlAlcohol: 20.0, packageType: PackageType.pint),
        ],
        benchmarks: const <Benchmark>[],
      );

      final reference = catalog.skus.firstWhere((s) => s.id == 'ref_sku');
      final result = engine.similarBeers(reference, catalog);

      expect(result.map((s) => s.id), ['best_sku', 'mid_sku', 'worst_sku']);
    });

    test('returns an empty list when the catalog has no other SKUs', () {
      final catalog = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime(2026, 1, 1),
        styles: const [Style(id: 'lager', name: 'Lager', description: '')],
        beers: const [Beer(id: 'ref', name: 'Reference', brewery: 'Brewery A', styleId: 'lager', isCraft: false)],
        skus: [_sku(id: 'only_sku', beerId: 'ref')],
        benchmarks: const <Benchmark>[],
      );

      final reference = catalog.skus.single;
      expect(engine.similarBeers(reference, catalog), isEmpty);
    });

    test('does not exclude other SKUs of the same beer, only the exact reference SKU', () {
      final catalog = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime(2026, 1, 1),
        styles: const [Style(id: 'lager', name: 'Lager', description: '')],
        beers: const [Beer(id: 'ref', name: 'Reference', brewery: 'Brewery A', styleId: 'lager', isCraft: false)],
        skus: [
          _sku(id: 'ref_650', beerId: 'ref', packageType: PackageType.bottle),
          _sku(id: 'ref_330', beerId: 'ref', packageType: PackageType.can),
        ],
        benchmarks: const <Benchmark>[],
      );

      final reference = catalog.skus.firstWhere((s) => s.id == 'ref_650');
      final result = engine.similarBeers(reference, catalog);

      expect(result.map((s) => s.id), ['ref_330']);
    });
  });

  group('betterValueAlternatives', () {
    late Catalog catalog;
    late Sku reference;

    setUp(() {
      catalog = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime(2026, 1, 1),
        styles: const [
          Style(id: 'lager', name: 'Lager', description: ''),
          Style(id: 'ipa', name: 'IPA', description: ''),
        ],
        beers: const [
          Beer(id: 'kf', name: 'Kingfisher Premium', brewery: 'United Breweries', styleId: 'lager', isCraft: false),
          Beer(id: 'simba', name: 'Simba Strong', brewery: 'Kals Brewing', styleId: 'lager', isCraft: false),
          Beer(id: 'budweiser', name: 'Budweiser', brewery: 'AB InBev', styleId: 'lager', isCraft: false),
          Beer(id: 'fosters', name: "Foster's", brewery: 'CUB', styleId: 'lager', isCraft: false),
          Beer(id: 'arbor', name: 'Arbor IPA', brewery: 'Arbor Brewing', styleId: 'ipa', isCraft: true),
        ],
        skus: [
          // Reference: valueScore 78, ABV 4.8, style lager.
          _sku(id: 'kf_650', beerId: 'kf', abv: 4.8, valueScore: 78),
          // Same beer, lower value — must never appear as a "better" alternative.
          _sku(id: 'kf_330', beerId: 'kf', abv: 4.8, valueScore: 60),
          // Higher value, same style, but ABV too far apart (diff 3.2 > 1.5 tolerance).
          _sku(id: 'simba_500', beerId: 'simba', abv: 8.0, valueScore: 82),
          // Higher value, same style, comparable ABV (diff 0.2) — qualifies.
          _sku(id: 'budweiser_650', beerId: 'budweiser', abv: 5.0, valueScore: 85),
          // Highest value of all, same style, comparable ABV (diff 0.3) — qualifies, ranks first.
          _sku(id: 'fosters_650', beerId: 'fosters', abv: 5.1, valueScore: 90),
          // Higher value, comparable ABV, but a different style — excluded.
          _sku(id: 'arbor_330', beerId: 'arbor', abv: 5.0, valueScore: 95),
        ],
        benchmarks: const <Benchmark>[],
      );
      reference = catalog.skus.firstWhere((s) => s.id == 'kf_650');
    });

    test(
      'only includes SKUs that are the same style, a comparable ABV, and a higher valueScore',
      () {
        final result = engine.betterValueAlternatives(reference, catalog);

        expect(result.map((s) => s.id), ['fosters_650', 'budweiser_650']);
      },
    );

    test('excludes a same-style, comparable-ABV SKU that is not actually better value', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.map((s) => s.id), isNot(contains('kf_330')));
    });

    test('excludes a higher-value SKU whose ABV is too different to be comparable', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.map((s) => s.id), isNot(contains('simba_500')));
    });

    test('excludes a higher-value, comparable-ABV SKU of a different style', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.map((s) => s.id), isNot(contains('arbor_330')));
    });

    test('ranks qualifying alternatives by valueScore descending', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.first.id, 'fosters_650');
      expect(result.first.valueScore, greaterThan(result.last.valueScore));
    });

    test('does not simply sort by cheapest — a same-style, comparable-ABV SKU with a lower '
        'valueScore never appears, regardless of its raw price', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      // kf_330 shares style and a comparable ABV with the reference, but its
      // valueScore (60) is lower — a naive "cheapest first" sort would need
      // to actively exclude it, which this assertion confirms happens.
      expect(result.any((s) => s.id == 'kf_330'), isFalse);
    });

    test('returns an empty list when the reference SKU\'s beer cannot be resolved', () {
      final orphanSku = _sku(id: 'orphan', beerId: 'no_such_beer', valueScore: 1);
      expect(engine.betterValueAlternatives(orphanSku, catalog), isEmpty);
    });

    test('returns an empty list when nothing qualifies', () {
      final catalogWithOnlyReference = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime(2026, 1, 1),
        styles: const [Style(id: 'lager', name: 'Lager', description: '')],
        beers: const [Beer(id: 'kf', name: 'Kingfisher Premium', brewery: 'United Breweries', styleId: 'lager', isCraft: false)],
        skus: [_sku(id: 'kf_650', beerId: 'kf', valueScore: 78)],
        benchmarks: const <Benchmark>[],
      );
      final onlyReference = catalogWithOnlyReference.skus.single;

      expect(
        engine.betterValueAlternatives(onlyReference, catalogWithOnlyReference),
        isEmpty,
      );
    });
  });

  group('dependency injection', () {
    test(
      'a custom similarityScorer actually changes ranking — proven by flipping the '
      'order relative to the default engine',
      () {
        final catalog = Catalog(
          catalogVersion: 1,
          generatedAt: DateTime(2026, 1, 1),
          styles: const [
            Style(id: 'lager', name: 'Lager', description: ''),
            Style(id: 'ipa', name: 'IPA', description: ''),
          ],
          beers: const [
            Beer(id: 'ref', name: 'Reference', brewery: 'Brewery A', styleId: 'lager', isCraft: false),
            // Matches the reference on brewery only — everything else differs.
            Beer(id: 'brewery_match', name: 'Brewery Match', brewery: 'Brewery A', styleId: 'ipa', isCraft: true),
            // Matches the reference on everything except brewery.
            Beer(id: 'everything_else_match', name: 'Everything Else', brewery: 'Brewery B', styleId: 'lager', isCraft: false),
          ],
          skus: [
            _sku(id: 'ref_sku', beerId: 'ref', abv: 5.0, costPerMlAlcohol: 4.0, packageType: PackageType.bottle),
            _sku(id: 'brewery_match_sku', beerId: 'brewery_match', abv: 10.0, costPerMlAlcohol: 20.0, packageType: PackageType.pint),
            _sku(id: 'everything_else_match_sku', beerId: 'everything_else_match', abv: 5.0, costPerMlAlcohol: 4.0, packageType: PackageType.bottle),
          ],
          benchmarks: const <Benchmark>[],
        );
        final reference = catalog.skus.firstWhere((s) => s.id == 'ref_sku');

        final defaultEngine = RecommendationEngine();
        final breweryOnlyEngine = RecommendationEngine(
          similarityScorer: WeightedScorer({const BreweryMatchStrategy(): 1.0}),
        );

        final defaultRanking = defaultEngine.similarBeers(reference, catalog).map((s) => s.id);
        final breweryOnlyRanking =
            breweryOnlyEngine.similarBeers(reference, catalog).map((s) => s.id);

        expect(defaultRanking, ['everything_else_match_sku', 'brewery_match_sku']);
        expect(breweryOnlyRanking, ['brewery_match_sku', 'everything_else_match_sku']);
      },
    );
  });
}
