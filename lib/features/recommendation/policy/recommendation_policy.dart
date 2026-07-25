import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';

/// The recommendation *rules* [RecommendationEngine] executes: how
/// candidates are scored, and the thresholds that decide whether a
/// candidate qualifies at all.
///
/// [RecommendationEngine] never contains a weight or a threshold itself —
/// it only asks a [RecommendationPolicy] for them. This is what lets a
/// future recommendation profile (Budget Drinker, Craft Explorer, Strong
/// Beer Lover, Premium Only, Low Alcohol, Session Beers, ...) exist as a
/// new [RecommendationPolicy] implementation with its own weights and
/// thresholds, without changing [RecommendationEngine] or either of its
/// methods at all.
abstract class RecommendationPolicy {
  /// Combines individual [SimilarityStrategy] scores into the single
  /// score `similarBeers` ranks by.
  WeightedScorer get similarityScorer;

  /// The minimum [similarityScorer] score a SKU must reach to appear in
  /// `similarBeers`'s results at all.
  double get minSimilarityScore;

  /// How close two SKUs' ABV must be, in percentage points, to count as
  /// "a similar alcohol level" for `betterValueAlternatives`'s filtering.
  ///
  /// Distinct from [AbvClosenessStrategy]'s smooth `[0.0, 1.0]` scoring
  /// (used for *ranking* in `similarBeers`) — this is a hard yes/no gate
  /// (used for *filtering* candidates in `betterValueAlternatives`),
  /// because "better value" needs a comparable-or-not decision, not a
  /// degree of similarity to rank by.
  double get comparableAbvTolerance;

  /// How many `valueScore` points higher than the reference SKU's a
  /// candidate must be to count as a genuinely "better value" alternative
  /// in `betterValueAlternatives`.
  int get minValueScoreImprovement;
}

/// The production-ready default [RecommendationPolicy].
///
/// Every value here reproduces ValueBrew's original, pre-policy
/// recommendation behaviour exactly:
/// - [similarityScorer]'s weights are the same style/ABV/price/package/
///   brewery weighting the engine used to hardcode.
/// - [minSimilarityScore] is `0.0` — every [similarityScorer] score is
///   already `>= 0.0`, so this never filters anything out, matching
///   `similarBeers`' original "rank everyone, exclude no one" behaviour.
/// - [comparableAbvTolerance] is the same `1.5` the engine used to
///   hardcode.
/// - [minValueScoreImprovement] is `1` — the smallest possible
///   improvement for an integer `valueScore` — reproducing the engine's
///   original strict `candidate.valueScore > beer.valueScore` check
///   exactly.
///
/// Individual values can be overridden without writing a whole new
/// policy class — useful for tests, and for simple variations that don't
/// warrant their own named profile.
class DefaultRecommendationPolicy implements RecommendationPolicy {
  const DefaultRecommendationPolicy({
    this.similarityScorer = _defaultSimilarityScorer,
    this.minSimilarityScore = 0.0,
    this.comparableAbvTolerance = 1.5,
    this.minValueScoreImprovement = 1,
  });

  @override
  final WeightedScorer similarityScorer;

  @override
  final double minSimilarityScore;

  @override
  final double comparableAbvTolerance;

  @override
  final int minValueScoreImprovement;

  static const WeightedScorer _defaultSimilarityScorer = WeightedScorer({
    StyleMatchStrategy(): 3.0,
    AbvClosenessStrategy(): 2.0,
    PriceClosenessStrategy(): 1.5,
    PackageTypeMatchStrategy(): 1.0,
    BreweryMatchStrategy(): 0.5,
  });
}
