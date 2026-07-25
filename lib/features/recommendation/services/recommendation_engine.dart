import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';

/// V1 of ValueBrew's recommendation engine: ranks SKUs by similarity to a
/// reference SKU, and finds "better value" alternatives among comparable
/// SKUs.
///
/// This engine is a pure *executor*: every weight and threshold it needs
/// comes from its [policy], and it contains no recommendation rule of its
/// own. This split is what lets a future recommendation profile (Budget
/// Drinker, Craft Explorer, ...) exist purely as a new
/// [RecommendationPolicy] implementation, with this class and its methods
/// entirely unchanged. See [RecommendationPolicy]'s own doc comment for
/// the full rationale, and `providers/recommendation_providers.dart` for
/// how a future screen would obtain an instance.
///
/// This is pure business logic — no Flutter or Riverpod dependency in
/// this file. It reads [Sku.valueScore]/[Sku.costPerMlAlcohol] as the
/// catalog's existing precomputed fields; it never recomputes a price or
/// value metric from scratch — the on-device Value Engine that would do
/// that remains a separate, already deferred milestone.
///
/// ### Complexity
/// Both [similarBeers] and [betterValueAlternatives] score every other
/// SKU in [catalog] exactly once against the reference SKU (O(n)), then
/// sort the results (O(n log n)). Neither method compares candidates
/// against each other, so this stays O(n log n) overall regardless of
/// catalog size — at 5,000+ SKUs this is still a single-digit-millisecond
/// operation. If catalog size ever grows enough that even this becomes a
/// real cost (e.g. called on every frame of a scrolling list rather than
/// once per screen), the natural next step is pre-grouping SKUs by
/// `styleId` once and only scoring within the reference SKU's style
/// group — a change to how candidates are gathered, not to the scoring
/// model itself.
class RecommendationEngine {
  /// Creates a [RecommendationEngine].
  ///
  /// [policy] defaults to [DefaultRecommendationPolicy]. Inject a
  /// different [RecommendationPolicy] (different weights, different
  /// thresholds — a different recommendation profile entirely) without
  /// needing any other change to this class or its callers.
  RecommendationEngine({RecommendationPolicy? policy})
      : policy = policy ?? const DefaultRecommendationPolicy();

  /// The recommendation rules this engine executes. See
  /// [RecommendationPolicy].
  final RecommendationPolicy policy;

  /// Returns every other SKU in [catalog], ranked by similarity to
  /// [beer], most similar first.
  ///
  /// "Similarity" is whatever [policy]'s `similarityScorer` computes.
  /// [beer] itself is excluded from the result, as is any candidate whose
  /// score falls below [policy]'s `minSimilarityScore`. Ties are broken
  /// by [catalog]'s SKU order, for deterministic results.
  List<Sku> similarBeers(Sku beer, Catalog catalog) {
    final scorer = policy.similarityScorer;

    // Scored once per candidate up front, then looked up during sorting,
    // rather than rescored on every comparator call.
    final scoreById = <String, double>{
      for (final candidate in catalog.skus)
        if (candidate.id != beer.id) candidate.id: scorer.score(beer, candidate, catalog),
    };

    final candidates = catalog.skus
        .where((sku) => sku.id != beer.id && scoreById[sku.id]! >= policy.minSimilarityScore)
        .toList();

    return _rankedDescending(candidates, (sku) => scoreById[sku.id]!);
  }

  /// Returns every SKU in [catalog] that represents a genuinely better
  /// deal than [beer]: the same style, a comparable ABV (within
  /// [policy]'s `comparableAbvTolerance` of [beer]'s), and a `valueScore`
  /// at least [policy]'s `minValueScoreImprovement` higher than [beer]'s
  /// own — ranked by `valueScore` descending (best value first).
  ///
  /// This is deliberately not "cheapest first": a SKU of a different
  /// style, or with a meaningfully different ABV, isn't a comparable
  /// drinking experience, so it's excluded regardless of price.
  List<Sku> betterValueAlternatives(Sku beer, Catalog catalog) {
    final referenceBeer = resolveBeer(catalog, beer.beerId);
    if (referenceBeer == null) return const [];

    final candidates = catalog.skus.where((candidate) {
      if (candidate.id == beer.id) return false;
      if (candidate.valueScore < beer.valueScore + policy.minValueScoreImprovement) return false;
      if ((candidate.abv - beer.abv).abs() > policy.comparableAbvTolerance) return false;

      final candidateBeer = resolveBeer(catalog, candidate.beerId);
      return candidateBeer != null && candidateBeer.styleId == referenceBeer.styleId;
    }).toList();

    return _rankedDescending(candidates, (candidate) => candidate.valueScore.toDouble());
  }

  /// Sorts [candidates] by [scoreOf], descending, with ties broken by
  /// [candidates]' original order — the same `(score, originalIndex)`
  /// pattern already used by `HomeScreen`'s and `BeerDetailScreen`'s
  /// sorting, and for the same reason: [List.sort] alone doesn't
  /// guarantee stability.
  List<Sku> _rankedDescending(List<Sku> candidates, double Function(Sku) scoreOf) {
    final indexed = candidates.asMap().entries.toList()
      ..sort((a, b) {
        final scoreComparison = scoreOf(b.value).compareTo(scoreOf(a.value));
        if (scoreComparison != 0) return scoreComparison;
        return a.key.compareTo(b.key);
      });
    return [for (final entry in indexed) entry.value];
  }
}
