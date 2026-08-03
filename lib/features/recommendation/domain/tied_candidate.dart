import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';

/// One SKU tied with others for the best Value Score in a
/// [RecommendationTie] — its identity only, resolved once by
/// `generateRecommendation`, the same way `RecommendationResult` already
/// embeds a resolved [Sku]/[Beer] pair rather than bare ids.
class TiedCandidate {
  const TiedCandidate({required this.sku, required this.beer});

  final Sku sku;
  final Beer beer;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is TiedCandidate && other.sku == sku && other.beer == beer);
  }

  @override
  int get hashCode => Object.hash(sku, beer);

  @override
  String toString() => 'TiedCandidate(sku: ${sku.id}, beer: ${beer.name})';
}
