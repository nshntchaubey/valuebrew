import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/benchmark.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';

class _ConstantStrategy implements SimilarityStrategy {
  const _ConstantStrategy(this.name, this.value);

  @override
  final String name;
  final double value;

  @override
  double score(Sku a, Sku b, Catalog catalog) => value;
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
}
