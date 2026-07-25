import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/recommendation/models/recommendation.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';

/// V1 of ValueBrew's recommendation engine: ranks SKUs by similarity to a
/// reference SKU, and finds "better value" alternatives among comparable
/// SKUs — explaining, for each one, why it was recommended.
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
/// ### Explanations
/// Both methods return [Recommendation]s, not bare [Sku]s — each one
/// carries the score it was ranked by and the [RecommendationReason]s a
/// user would recognize (e.g. "Same style • Similar ABV"). For
/// [similarBeers], those reasons come from [WeightedScorer.explain] — the
/// exact same comparisons [WeightedScorer.score] used to rank it, not a
/// separately maintained set of rules. For [betterValueAlternatives],
/// there's no scoring dimension for "better value" in [WeightedScorer] at
/// all — that method's own style/ABV/value-improvement gate *is* the
/// explanation, so its reasons are attached directly, not derived from a
/// strategy. See `models/recommendation.dart` and
/// `models/recommendation_reason.dart` for the full model.
///
/// ### Complexity
/// Both [similarBeers] and [betterValueAlternatives] score (and, for
/// [similarBeers], explain) every other SKU in [catalog] exactly once
/// against the reference SKU (O(n)), then sort the results (O(n log n)).
/// Neither method compares candidates against each other, so this stays
/// O(n log n) overall regardless of catalog size — at 5,000+ SKUs this is
/// still a single-digit-millisecond operation. If catalog size ever grows
/// enough that even this becomes a real cost (e.g. called on every frame
/// of a scrolling list rather than once per screen), the natural next
/// step is pre-grouping SKUs by `styleId` once and only scoring within the
/// reference SKU's style group — a change to how candidates are gathered,
/// not to the scoring model itself.
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
  List<Recommendation> similarBeers(Sku beer, Catalog catalog) {
    final scorer = policy.similarityScorer;

    // Score and explanation computed together, once per candidate, then
    // looked up during filtering/sorting/wrapping below — never
    // recomputed, and never derived separately from one another.
    final scoredCandidates = <String, ({double score, List<RecommendationReason> reasons})>{
      for (final candidate in catalog.skus)
        if (candidate.id != beer.id)
          candidate.id: (
            score: scorer.score(beer, candidate, catalog),
            reasons: scorer.explain(beer, candidate, catalog),
          ),
    };

    final candidates = catalog.skus
        .where((sku) =>
            sku.id != beer.id && scoredCandidates[sku.id]!.score >= policy.minSimilarityScore)
        .toList();

    final ranked = _rankedDescending(candidates, (sku) => scoredCandidates[sku.id]!.score);

    return [
      for (final sku in ranked)
        Recommendation(
          sku: sku,
          overallScore: scoredCandidates[sku.id]!.score,
          matchedReasons: scoredCandidates[sku.id]!.reasons,
          type: RecommendationType.similar,
        ),
    ];
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
  List<Recommendation> betterValueAlternatives(Sku beer, Catalog catalog) {
    final referenceBeer = resolveBeer(catalog, beer.beerId);
    if (referenceBeer == null) return const [];

    final candidates = catalog.skus.where((candidate) {
      if (candidate.id == beer.id) return false;
      if (candidate.valueScore < beer.valueScore + policy.minValueScoreImprovement) return false;
      if ((candidate.abv - beer.abv).abs() > policy.comparableAbvTolerance) return false;

      final candidateBeer = resolveBeer(catalog, candidate.beerId);
      return candidateBeer != null && candidateBeer.styleId == referenceBeer.styleId;
    }).toList();

    final ranked = _rankedDescending(candidates, (candidate) => candidate.valueScore.toDouble());

    return [
      for (final sku in ranked)
        Recommendation(
          sku: sku,
          overallScore: sku.valueScore.toDouble(),
          matchedReasons: _betterValueReasons,
          type: RecommendationType.betterValue,
        ),
    ];
  }

  /// Every candidate [betterValueAlternatives] returns already satisfies
  /// all three of these conditions by construction (its own filter above)
  /// — a fixed, shared list rather than something recomputed per
  /// candidate, since there's nothing left to check.
  static const List<RecommendationReason> _betterValueReasons = [
    RecommendationReason.sameStyle,
    RecommendationReason.similarAbv,
    RecommendationReason.betterValue,
  ];

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
