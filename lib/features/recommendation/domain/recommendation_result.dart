import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';

/// The outcome of [generateRecommendation]: one specific SKU, the [Beer] it
/// belongs to, and a plain-language explanation of why it was chosen.
///
/// Deliberately minimal for this vertical slice — see
/// `generate_recommendation.dart` for what's intentionally not represented
/// here yet (a genuine tie, a trade-off, a low-confidence response).
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
