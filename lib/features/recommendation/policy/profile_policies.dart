import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';

/// The three non-default named [RecommendationPolicy] implementations —
/// one per [RecommendationProfile] besides `balanced`, which stays exactly
/// [DefaultRecommendationPolicy] (see `recommendation_profile.dart`).
///
/// Every class here only varies [similarityScorer] — the weight map
/// `similarBeers` ranks and explains by. [minSimilarityScore],
/// [comparableAbvTolerance], and [minValueScoreImprovement] are identical
/// across every policy, including [DefaultRecommendationPolicy]: this
/// milestone's brief is about configuring *scoring*, and
/// `betterValueAlternatives` (the only method those three thresholds
/// affect) doesn't use [similarityScorer] at all — it's a separate,
/// hand-rolled gate. Deliberately, `betterValueAlternatives`' output is
/// therefore identical regardless of the active profile; only
/// `similarBeers`' ranking and explanations change. If a future profile
/// ever needs to change value-alternative behaviour too, that's a
/// straightforward addition to these same classes — nothing about this
/// shape prevents it.
///
/// Repeating those three fields across four classes, instead of sharing
/// them through a base class or mixin, is intentional: each class reads
/// as a complete, standalone [RecommendationPolicy] on its own, and three
/// identical lines is a smaller cost than an inheritance relationship
/// that would otherwise carry no real shared behaviour.

/// Surfaces bargains: heavily weights [ValueScoreStrategy] and
/// [CheaperPriceStrategy], while keeping enough [StyleMatchStrategy]/
/// [AbvClosenessStrategy] weight that a suggestion is still a reasonable
/// stand-in for the beer being viewed ("acceptable similarity" — this
/// profile finds bargains, not just *any* cheap beer). Brewery and
/// package type don't matter to a bargain hunter, so neither strategy is
/// included at all.
class BestValuePolicy implements RecommendationPolicy {
  const BestValuePolicy();

  @override
  WeightedScorer get similarityScorer => const WeightedScorer({
        ValueScoreStrategy(): 4.0,
        CheaperPriceStrategy(): 3.0,
        StyleMatchStrategy(): 1.5,
        AbvClosenessStrategy(): 1.0,
        PackageTypeMatchStrategy(): 0.5,
      });

  @override
  double get minSimilarityScore => 0.0;

  @override
  double get comparableAbvTolerance => 1.5;

  @override
  int get minValueScoreImprovement => 1;
}

/// Surfaces the closest match to the beer being viewed: heavily weights
/// [StyleMatchStrategy], [AbvClosenessStrategy], and
/// [BreweryMatchStrategy] — the closest proxies this catalog schema has
/// for "flavor" (see `similarity_strategy.dart`'s own note on deferred
/// flavour attributes like IBU and bitterness, which don't exist in the
/// data yet). [PriceClosenessStrategy] is included only lightly, per
/// "price should matter less" — not zero, since a wildly different price
/// point is still worth a small penalty, but far below every other
/// dimension.
class SimilarTastePolicy implements RecommendationPolicy {
  const SimilarTastePolicy();

  @override
  WeightedScorer get similarityScorer => const WeightedScorer({
        StyleMatchStrategy(): 4.0,
        AbvClosenessStrategy(): 3.0,
        BreweryMatchStrategy(): 2.0,
        PriceClosenessStrategy(): 0.5,
      });

  @override
  double get minSimilarityScore => 0.0;

  @override
  double get comparableAbvTolerance => 1.5;

  @override
  int get minValueScoreImprovement => 1;
}

/// Surfaces something new: good value from a different brewery and a
/// different style, rather than a close match.
///
/// "Penalty for same brewery/style" is expressed as *rewarding
/// difference* ([BreweryDiversityStrategy], [StyleDiversityStrategy])
/// rather than subtracting from a score — [WeightedScorer] only ever
/// combines non-negative [SimilarityStrategy] scores, so there is no
/// subtraction concept to extend; rewarding the opposite condition
/// achieves the same practical effect without changing how scores
/// combine. A light [AbvClosenessStrategy] weight keeps suggestions in a
/// roughly similar strength range, so "exploration" still means "a
/// different beer worth trying," not "anything at all."
class DiscoveryPolicy implements RecommendationPolicy {
  const DiscoveryPolicy();

  @override
  WeightedScorer get similarityScorer => const WeightedScorer({
        ValueScoreStrategy(): 3.0,
        BreweryDiversityStrategy(): 2.5,
        StyleDiversityStrategy(): 2.0,
        AbvClosenessStrategy(): 1.0,
      });

  @override
  double get minSimilarityScore => 0.0;

  @override
  double get comparableAbvTolerance => 1.5;

  @override
  int get minValueScoreImprovement => 1;
}
