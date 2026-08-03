import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';

/// The outcome of [generateRecommendation]: one specific SKU, the [Beer] it
/// belongs to, and a plain-language explanation of why it was chosen.
///
/// Represents the single-result case only. A genuine tie is represented
/// separately, by the sibling `RecommendationTie` outcome — see
/// `generate_recommendation.dart` for what's still intentionally not
/// represented anywhere yet (a trade-off, a low-confidence response).
class RecommendationResult {
  /// The recommended SKU.
  final Sku sku;

  /// The [Beer] [sku] belongs to.
  final Beer beer;

  /// Plain-language statement of what drove this recommendation, per the
  /// Recommendation Framework's explanation rules.
  final String explanation;

  /// Creates an immutable [RecommendationResult].
  const RecommendationResult({
    required this.sku,
    required this.beer,
    required this.explanation,
  });

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is RecommendationResult &&
            other.sku == sku &&
            other.beer == beer &&
            other.explanation == explanation);
  }

  @override
  int get hashCode => Object.hash(sku, beer, explanation);

  @override
  String toString() =>
      'RecommendationResult(sku: ${sku.id}, beer: ${beer.name}, '
      'explanation: $explanation)';
}
