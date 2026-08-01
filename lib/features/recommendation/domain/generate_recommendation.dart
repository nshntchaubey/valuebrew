import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_result.dart';

/// Recommends one SKU from [catalog] within [budget].
///
/// This is the smallest complete Recommendation Vertical Slice's entire
/// reasoning: filter to SKUs at or under [budget], then pick the one with
/// the best Value Score — the highest-confidence remaining differentiator,
/// per the Recommendation Framework's tie-breaker rule (Section 2).
///
/// Returns `null` if no SKU in [catalog] is at or under [budget] — a real,
/// honest outcome, not an error.
///
/// Deterministic, side-effect free, and completely independent of Flutter
/// UI — pure Dart over plain data, so every rule here remains fully unit
/// testable without a widget.
///
/// **Extension seams, deliberately not built here:** further Progressive
/// Question-Asking (style, strength, size, brand) once budget alone leaves
/// candidates too close together; a genuine Tie Disclosure once ties need
/// real handling — see the tie-break note below; the optional hand-off to
/// Beer Detail; Planning Mode's confidence ceiling; Proxy-Buying Mode's
/// conservative default.
///
/// **Tie-break, explicitly temporary:** when multiple SKUs share the
/// highest Value Score within budget, the first one encountered in
/// [Catalog.skus]'s own order wins. This is a deterministic implementation
/// choice for this vertical slice only, not the long-term recommendation
/// policy — the Recommendation Framework's actual rule for a genuine tie
/// ("presented as a tie... a complete, honest recommendation") is a real
/// extension seam, not yet implemented.
RecommendationResult? generateRecommendation(
  Catalog catalog, {
  required double budget,
}) {
  final candidates = catalog.skus.where((sku) => sku.price <= budget).toList();
  if (candidates.isEmpty) return null;

  var best = candidates.first;
  for (final candidate in candidates.skip(1)) {
    if (candidate.valueScore > best.valueScore) {
      best = candidate;
    }
  }

  final beer = catalog.beers.firstWhere((b) => b.id == best.beerId);

  final explanation =
      'Within your ${budget.currencyLabel} budget, ${beer.name} '
      '(${best.sizeMl.volumeLabel}) is the best value available — '
      'a Value Score of ${best.valueScore}.';

  return RecommendationResult(sku: best, beer: beer, explanation: explanation);
}
