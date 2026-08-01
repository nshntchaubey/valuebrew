import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';

/// Combines multiple [SimilarityStrategy]s into a single similarity score
/// via a weighted average.
///
/// Each strategy already returns a score in `[0.0, 1.0]`; normalizing by
/// the sum of weights (rather than assuming weights sum to `1.0`) means
/// callers can pass any positive weights — relative magnitude between
/// them is all that matters, not an exact total.
///
/// This is the one place individual strategy scores are combined. Adding,
/// removing, or reweighting a scoring dimension only ever means changing
/// the weight map passed to a [WeightedScorer] — never touching any
/// strategy's own code.
class WeightedScorer {
  /// Creates a [WeightedScorer] combining [weights] — a strategy mapped
  /// to how much it should count relative to the others.
  const WeightedScorer(this.weights);

  /// Which strategies contribute to this scorer's score, and by how much
  /// relative to each other.
  final Map<SimilarityStrategy, double> weights;

  /// Returns the combined, weighted-average similarity score between [a]
  /// and [b], in `[0.0, 1.0]`. Returns `0.0` if [weights] is empty or all
  /// weights are zero.
  double score(Sku a, Sku b, Catalog catalog) {
    var weightedSum = 0.0;
    var totalWeight = 0.0;
    for (final entry in weights.entries) {
      weightedSum += entry.key.score(a, b, catalog) * entry.value;
      totalWeight += entry.value;
    }

    if (totalWeight <= 0) return 0.0;
    return weightedSum / totalWeight;
  }

  /// Returns every [RecommendationReason] contributed by [weights]'
  /// strategies for [a] vs [b], in the order they appear in [weights].
  ///
  /// This is a natural by-product of the same comparisons [score] makes —
  /// each strategy's `explain` reuses the exact comparison its own `score`
  /// uses (see `similarity_strategy.dart`) — not a separate set of rules
  /// layered on top. Can be empty if no strategy found [a] and [b] similar
  /// enough on its dimension to be worth mentioning.
  List<RecommendationReason> explain(Sku a, Sku b, Catalog catalog) {
    return [
      for (final strategy in weights.keys) ?strategy.explain(a, b, catalog),
    ];
  }
}
