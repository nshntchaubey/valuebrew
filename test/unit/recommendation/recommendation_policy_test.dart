import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/benchmark.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/models/style.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';

void main() {
  final catalog = Catalog(
    catalogVersion: 1,
    generatedAt: DateTime(2026, 1, 1),
    styles: const [Style(id: 'lager', name: 'Lager', description: '')],
    beers: const [Beer(id: 'kf', name: 'Kingfisher', brewery: 'United Breweries', styleId: 'lager', isCraft: false)],
    skus: const [],
    benchmarks: const <Benchmark>[],
  );

  final sku = Sku(
    id: 'a',
    beerId: 'kf',
    sizeMl: 650,
    packageType: PackageType.bottle,
    abv: 5.0,
    calories: 250,
    price: 100,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: 150,
    costPerMlAlcohol: 4.0,
    valueScore: 50,
    valueVerdict: ValueVerdict.fairValue,
  );

  group('DefaultRecommendationPolicy', () {
    test('default values', () {
      const policy = DefaultRecommendationPolicy();

      expect(policy.minSimilarityScore, 0.0);
      expect(policy.comparableAbvTolerance, 1.5);
      expect(policy.minValueScoreImprovement, 1);
      // Same SKU scored against itself: every strategy matches itself, so
      // the default weighted scorer's weights are irrelevant here — this
      // just confirms the scorer is wired up and usable.
      expect(policy.similarityScorer.score(sku, sku, catalog), 1.0);
    });

    test('individual values can be overridden without redefining the rest', () {
      const policy = DefaultRecommendationPolicy(
        comparableAbvTolerance: 3.0,
        minValueScoreImprovement: 5,
      );

      expect(policy.comparableAbvTolerance, 3.0);
      expect(policy.minValueScoreImprovement, 5);
      // Untouched values still fall back to the production defaults.
      expect(policy.minSimilarityScore, 0.0);
    });

    test('similarityScorer can be overridden independently', () {
      const customScorer = WeightedScorer({BreweryMatchStrategy(): 1.0});
      const policy = DefaultRecommendationPolicy(similarityScorer: customScorer);

      expect(policy.similarityScorer, same(customScorer));
    });
  });

  group('RecommendationPolicy', () {
    test('a from-scratch implementation satisfies the interface', () {
      const policy = _FixedPolicy();

      expect(policy.minSimilarityScore, 0.25);
      expect(policy.comparableAbvTolerance, 2.0);
      expect(policy.minValueScoreImprovement, 3);
      expect(policy.similarityScorer.weights, isEmpty);
    });
  });
}

class _FixedPolicy implements RecommendationPolicy {
  const _FixedPolicy();

  @override
  WeightedScorer get similarityScorer => const WeightedScorer({});

  @override
  double get minSimilarityScore => 0.25;

  @override
  double get comparableAbvTolerance => 2.0;

  @override
  int get minValueScoreImprovement => 3;
}
