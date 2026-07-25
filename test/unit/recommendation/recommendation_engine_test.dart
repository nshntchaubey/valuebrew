import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/benchmark.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/models/style.dart';
import 'package:valuebrew/features/recommendation/models/recommendation.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';
import 'package:valuebrew/features/recommendation/services/recommendation_engine.dart';

/// A from-scratch [RecommendationPolicy] — deliberately not built on
/// [DefaultRecommendationPolicy] — used to prove that [RecommendationEngine]
/// works with any policy implementation, not just the default one.
class _BreweryOnlyPolicy implements RecommendationPolicy {
  const _BreweryOnlyPolicy();

  @override
  WeightedScorer get similarityScorer => const WeightedScorer({BreweryMatchStrategy(): 1.0});

  @override
  double get minSimilarityScore => 0.0;

  @override
  double get comparableAbvTolerance => 1.5;

  @override
  int get minValueScoreImprovement => 1;
}

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

/// Fixture shared by the "similarBeers" ranking test and the explanation
/// tests below: a reference SKU plus three candidates engineered so their
/// [WeightedScorer.explain] output is hand-verifiable —
/// - `best_sku`: identical style/ABV/price/package, same brewery — matches
///   every dimension.
/// - `mid_sku`: same style, ABV and price close enough to mention (scores
///   0.75 and ~0.667, both over the 0.5 explain threshold), different
///   package and brewery.
/// - `worst_sku`: different style, ABV and price far enough apart to score
///   0.0 on both, different package and brewery — matches nothing at all.
Catalog _similarityFixtureCatalog() {
  return Catalog(
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
      _sku(id: 'best_sku', beerId: 'best', abv: 5.0, costPerMlAlcohol: 4.0, packageType: PackageType.bottle),
      _sku(id: 'mid_sku', beerId: 'mid', abv: 6.0, costPerMlAlcohol: 5.0, packageType: PackageType.can),
      _sku(id: 'worst_sku', beerId: 'worst', abv: 10.0, costPerMlAlcohol: 20.0, packageType: PackageType.pint),
    ],
    benchmarks: const <Benchmark>[],
  );
}

void main() {
  final engine = RecommendationEngine();

  group('similarBeers', () {
    test('excludes the reference SKU and ranks the rest by similarity, most similar first', () {
      final catalog = _similarityFixtureCatalog();

      final reference = catalog.skus.firstWhere((s) => s.id == 'ref_sku');
      final result = engine.similarBeers(reference, catalog);

      expect(result.map((r) => r.sku.id), ['best_sku', 'mid_sku', 'worst_sku']);
      expect(result.every((r) => r.type == RecommendationType.similar), isTrue);
    });

    test(
      'matchedReasons reflects exactly which strategies found each candidate similar enough '
      'to mention — proving explanations match scoring, not a separate set of rules',
      () {
        final catalog = _similarityFixtureCatalog();
        final reference = catalog.skus.firstWhere((s) => s.id == 'ref_sku');
        final result = engine.similarBeers(reference, catalog);

        final reasonsById = {for (final r in result) r.sku.id: r.matchedReasons};

        // Matches every dimension: style, ABV, price, package, and brewery.
        expect(
          reasonsById['best_sku'],
          [
            RecommendationReason.sameStyle,
            RecommendationReason.similarAbv,
            RecommendationReason.similarPrice,
            RecommendationReason.samePackage,
            RecommendationReason.sameBrewery,
          ],
        );

        // Same style, ABV/price close enough to mention, but a different
        // package and brewery.
        expect(
          reasonsById['mid_sku'],
          [
            RecommendationReason.sameStyle,
            RecommendationReason.similarAbv,
            RecommendationReason.similarPrice,
          ],
        );

        // Matches nothing — a valid, if unexplained, recommendation.
        expect(reasonsById['worst_sku'], isEmpty);
      },
    );

    test('overallScore equals the policy\'s WeightedScorer score for that candidate', () {
      final catalog = _similarityFixtureCatalog();
      final reference = catalog.skus.firstWhere((s) => s.id == 'ref_sku');
      final result = engine.similarBeers(reference, catalog);

      final bestSku = catalog.skus.firstWhere((s) => s.id == 'best_sku');
      final expectedScore =
          const DefaultRecommendationPolicy().similarityScorer.score(reference, bestSku, catalog);

      final bestRecommendation = result.firstWhere((r) => r.sku.id == 'best_sku');
      expect(bestRecommendation.overallScore, expectedScore);
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

      expect(result.map((r) => r.sku.id), ['ref_330']);
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

        expect(result.map((r) => r.sku.id), ['fosters_650', 'budweiser_650']);
      },
    );

    test('excludes a same-style, comparable-ABV SKU that is not actually better value', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.map((r) => r.sku.id), isNot(contains('kf_330')));
    });

    test('excludes a higher-value SKU whose ABV is too different to be comparable', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.map((r) => r.sku.id), isNot(contains('simba_500')));
    });

    test('excludes a higher-value, comparable-ABV SKU of a different style', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.map((r) => r.sku.id), isNot(contains('arbor_330')));
    });

    test('ranks qualifying alternatives by valueScore descending', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      expect(result.first.sku.id, 'fosters_650');
      expect(result.first.sku.valueScore, greaterThan(result.last.sku.valueScore));
    });

    test(
      'every result is tagged betterValue type, with a fixed matchedReasons set and '
      'overallScore equal to its own valueScore — reflecting the gate that already '
      'guaranteed same style, comparable ABV, and better value, not a separate re-check',
      () {
        final result = engine.betterValueAlternatives(reference, catalog);

        expect(result, isNotEmpty);
        for (final recommendation in result) {
          expect(recommendation.type, RecommendationType.betterValue);
          expect(
            recommendation.matchedReasons,
            [
              RecommendationReason.sameStyle,
              RecommendationReason.similarAbv,
              RecommendationReason.betterValue,
            ],
          );
          expect(recommendation.overallScore, recommendation.sku.valueScore.toDouble());
        }
      },
    );

    test('does not simply sort by cheapest — a same-style, comparable-ABV SKU with a lower '
        'valueScore never appears, regardless of its raw price', () {
      final result = engine.betterValueAlternatives(reference, catalog);

      // kf_330 shares style and a comparable ABV with the reference, but its
      // valueScore (60) is lower — a naive "cheapest first" sort would need
      // to actively exclude it, which this assertion confirms happens.
      expect(result.any((r) => r.sku.id == 'kf_330'), isFalse);
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
      'a custom policy actually changes ranking — proven by flipping the order '
      'relative to the default engine',
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
        // A whole new RecommendationPolicy implementation — not a
        // DefaultRecommendationPolicy override — accepted by the exact
        // same, unmodified RecommendationEngine.
        final breweryOnlyEngine = RecommendationEngine(policy: const _BreweryOnlyPolicy());

        final defaultRanking = defaultEngine.similarBeers(reference, catalog).map((r) => r.sku.id);
        final breweryOnlyRanking =
            breweryOnlyEngine.similarBeers(reference, catalog).map((r) => r.sku.id);

        expect(defaultRanking, ['everything_else_match_sku', 'brewery_match_sku']);
        expect(breweryOnlyRanking, ['brewery_match_sku', 'everything_else_match_sku']);
      },
    );

    test('a stricter minValueScoreImprovement policy excludes a candidate the default policy includes', () {
      final catalog = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime(2026, 1, 1),
        styles: const [Style(id: 'lager', name: 'Lager', description: '')],
        beers: const [
          Beer(id: 'kf', name: 'Kingfisher', brewery: 'United Breweries', styleId: 'lager', isCraft: false),
          Beer(id: 'simba', name: 'Simba', brewery: 'Kals Brewing', styleId: 'lager', isCraft: false),
        ],
        skus: [
          _sku(id: 'kf_650', beerId: 'kf', abv: 5.0, valueScore: 78),
          // Only 2 points better — qualifies under the default policy
          // (minValueScoreImprovement: 1) but not under a policy that
          // requires at least 10.
          _sku(id: 'simba_650', beerId: 'simba', abv: 5.0, valueScore: 80),
        ],
        benchmarks: const <Benchmark>[],
      );
      final reference = catalog.skus.firstWhere((s) => s.id == 'kf_650');

      final defaultEngine = RecommendationEngine();
      final strictEngine = RecommendationEngine(
        policy: const DefaultRecommendationPolicy(minValueScoreImprovement: 10),
      );

      expect(
        defaultEngine.betterValueAlternatives(reference, catalog).map((r) => r.sku.id),
        ['simba_650'],
      );
      expect(strictEngine.betterValueAlternatives(reference, catalog), isEmpty);
    });
  });

  group('DefaultRecommendationPolicy preserves original engine behaviour', () {
    test('minSimilarityScore of 0.0 never filters out a candidate, matching the original '
        'unfiltered similarBeers behaviour', () {
      const policy = DefaultRecommendationPolicy();
      expect(policy.minSimilarityScore, 0.0);
    });

    test('minValueScoreImprovement of 1 reproduces the original strict > comparison', () {
      const policy = DefaultRecommendationPolicy();
      expect(policy.minValueScoreImprovement, 1);
    });

    test('comparableAbvTolerance matches the value the engine used to hardcode', () {
      const policy = DefaultRecommendationPolicy();
      expect(policy.comparableAbvTolerance, 1.5);
    });
  });
}
