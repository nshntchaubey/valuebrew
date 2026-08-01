import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';

class _ConstantStrategy implements SimilarityStrategy {
  const _ConstantStrategy(this.name, this.value, {this.reason});

  @override
  final String name;
  final double value;
  final RecommendationReason? reason;

  @override
  double score(Sku a, Sku b, Catalog catalog) => value;

  @override
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog) => reason;
}

void main() {
  final catalog = Catalog(
    catalogVersion: 1,
    generatedAt: DateTime(2026, 1, 1),
    styles: const [],
    beers: const [],
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

  test('a single strategy\'s weight cancels out — the score equals its own', () {
    final scorer = WeightedScorer({const _ConstantStrategy('only', 0.7): 5.0});

    expect(scorer.score(sku, sku, catalog), closeTo(0.7, 1e-9));
  });

  test('combines multiple strategies as a weighted average', () {
    final scorer = WeightedScorer({
      const _ConstantStrategy('a', 1.0): 3.0,
      const _ConstantStrategy('b', 0.0): 1.0,
    });

    // (1.0 * 3.0 + 0.0 * 1.0) / (3.0 + 1.0) = 0.75
    expect(scorer.score(sku, sku, catalog), closeTo(0.75, 1e-9));
  });

  test('equal weights average the strategies evenly', () {
    final scorer = WeightedScorer({
      const _ConstantStrategy('a', 1.0): 1.0,
      const _ConstantStrategy('b', 0.0): 1.0,
    });

    expect(scorer.score(sku, sku, catalog), closeTo(0.5, 1e-9));
  });

  test('an empty weight map scores 0.0', () {
    const scorer = WeightedScorer({});

    expect(scorer.score(sku, sku, catalog), 0.0);
  });

  test('all-zero weights score 0.0 rather than dividing by zero', () {
    final scorer = WeightedScorer({const _ConstantStrategy('a', 1.0): 0.0});

    expect(scorer.score(sku, sku, catalog), 0.0);
  });

  group('explain', () {
    test('collects every non-null reason from its strategies, in weight-map order', () {
      final scorer = WeightedScorer({
        const _ConstantStrategy('a', 1.0, reason: RecommendationReason.sameStyle): 1.0,
        const _ConstantStrategy('b', 0.0, reason: RecommendationReason.sameBrewery): 1.0,
        const _ConstantStrategy('c', 1.0, reason: RecommendationReason.samePackage): 1.0,
      });

      expect(
        scorer.explain(sku, sku, catalog),
        [
          RecommendationReason.sameStyle,
          RecommendationReason.sameBrewery,
          RecommendationReason.samePackage,
        ],
      );
    });

    test('a strategy contributing no reason is simply omitted, not a gap or an error', () {
      final scorer = WeightedScorer({
        const _ConstantStrategy('a', 1.0, reason: RecommendationReason.sameStyle): 1.0,
        const _ConstantStrategy('b', 0.0): 1.0,
      });

      expect(scorer.explain(sku, sku, catalog), [RecommendationReason.sameStyle]);
    });

    test('no strategy contributing a reason returns an empty list', () {
      final scorer = WeightedScorer({const _ConstantStrategy('a', 1.0): 1.0});

      expect(scorer.explain(sku, sku, catalog), isEmpty);
    });

    test('an empty weight map explains with an empty list', () {
      const scorer = WeightedScorer({});

      expect(scorer.explain(sku, sku, catalog), isEmpty);
    });
  });
}
