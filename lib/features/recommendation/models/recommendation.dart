import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';

/// Which of [RecommendationEngine]'s two methods produced a
/// [Recommendation].
///
/// Exists so a [Recommendation] is self-describing (a caller holding one
/// doesn't need to remember which list it came from) — not to enable any
/// merged/combined recommendation list, which is out of scope here.
enum RecommendationType {
  /// Produced by [RecommendationEngine.similarBeers].
  similar,

  /// Produced by [RecommendationEngine.betterValueAlternatives].
  betterValue,
}

/// A single recommended [Sku], together with why it was recommended.
///
/// [RecommendationEngine] used to return a plain `List<Sku>` — enough to
/// display a beer, but nothing about *why* it was suggested. This is the
/// minimal wrapper that fixes that: [overallScore] is what the SKU was
/// ranked by, and [matchedReasons] is what to actually show a user (see
/// [reasonSummary]).
///
/// This is a plain, immutable value object — no `fromJson`/`toJson`, since
/// a [Recommendation] is always computed at runtime by
/// [RecommendationEngine], never read from or written to the catalog JSON.
class Recommendation {
  const Recommendation({
    required this.sku,
    required this.overallScore,
    required this.matchedReasons,
    required this.type,
  });

  /// The recommended SKU.
  final Sku sku;

  /// The score this recommendation was ranked by.
  ///
  /// For [RecommendationType.similar], this is [WeightedScorer]'s combined
  /// `[0.0, 1.0]` similarity score. For [RecommendationType.betterValue],
  /// this is the candidate's own `valueScore` — the same field
  /// `betterValueAlternatives` has always ranked by.
  final double overallScore;

  /// Why this SKU was recommended, in the order its underlying
  /// [SimilarityStrategy]s were evaluated.
  ///
  /// Can be empty — a low-scoring [RecommendationType.similar] result may
  /// cross no strategy's "worth mentioning" bar at all. That's a valid,
  /// if unexplained, recommendation, not an error.
  final List<RecommendationReason> matchedReasons;

  /// Which engine method produced this recommendation.
  final RecommendationType type;

  /// [matchedReasons] joined into one display string (e.g. "Same style •
  /// Similar ABV"), or `null` if there's nothing to show.
  String? get reasonSummary =>
      matchedReasons.isEmpty ? null : matchedReasons.map((reason) => reason.displayLabel).join(' • ');

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is Recommendation &&
            other.sku == sku &&
            other.overallScore == overallScore &&
            other.type == type &&
            _listEquals(other.matchedReasons, matchedReasons));
  }

  /// Element-wise list equality, since [List]'s default `==` is identity,
  /// not content, comparison. Used only to fulfil the [==] contract above.
  static bool _listEquals<T>(List<T> a, List<T> b) {
    if (identical(a, b)) return true;
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }

  @override
  int get hashCode => Object.hash(sku, overallScore, type, Object.hashAll(matchedReasons));

  @override
  String toString() =>
      'Recommendation(sku: ${sku.id}, overallScore: $overallScore, '
      'matchedReasons: $matchedReasons, type: $type)';
}
