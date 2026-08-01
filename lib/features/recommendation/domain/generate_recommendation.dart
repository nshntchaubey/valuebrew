import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_outcome.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_result.dart';

/// Recommends one SKU from [catalog] within [budget], optionally narrowed
/// by [styleId].
///
/// This is the smallest complete Recommendation Vertical Slice's entire
/// reasoning, following the canonical constraint hierarchy exactly:
/// [budget] (a Hard Constraint) filters the full catalog first; [styleId]
/// (a Strong Preference), if given, narrows only within whatever survives
/// that. Among the final candidates, the one with the best Value Score
/// wins — the highest-confidence remaining differentiator, per the
/// Recommendation Framework's tie-breaker rule (Section 2).
///
/// Returns [NoRecommendationWithinBudget] if no SKU is at or under
/// [budget] at all, or [NoRecommendationMatchingStyle] if SKUs exist
/// within budget but none match [styleId] — both real, honest outcomes,
/// not errors. See [RecommendationOutcome.canBeRefinedFurther] for the
/// invariant governing when further refinement remains meaningful.
///
/// Deterministic, side-effect free, and completely independent of Flutter
/// UI — pure Dart over plain data, so every rule here remains fully unit
/// testable without a widget. A single flow throughout: the style filter
/// and the style clause in the explanation are each applied conditionally
/// within this one path, never as a separate, duplicated implementation —
/// this is what makes the [styleId] omitted case mechanically identical
/// to this vertical slice's original budget-only behaviour, not merely
/// tested to match it.
///
/// **Extension seams, deliberately not built here:** further Progressive
/// Question-Asking (strength, size, brand) once budget and style alone
/// leave candidates too close together; a genuine Tie Disclosure once
/// ties need real handling — see the tie-break note below; the optional
/// hand-off to Beer Detail; Planning Mode's confidence ceiling;
/// Proxy-Buying Mode's conservative default; a general unmet-preferences
/// outcome model once a second Strong Preference exists (this milestone's
/// [NoRecommendationMatchingStyle] is deliberately specific to style
/// alone, not yet generalized).
///
/// **Tie-break, explicitly temporary:** when multiple SKUs share the
/// highest Value Score among the final candidates, the first one
/// encountered in [Catalog.skus]'s own order wins. This is a
/// deterministic implementation choice for this vertical slice only, not
/// the long-term recommendation policy — the Recommendation Framework's
/// actual rule for a genuine tie ("presented as a tie... a complete,
/// honest recommendation") is a real extension seam, not yet implemented.
RecommendationOutcome generateRecommendation(
  Catalog catalog, {
  required double budget,
  String? styleId,
}) {
  final withinBudget = catalog.skus.where((sku) => sku.price <= budget).toList();
  if (withinBudget.isEmpty) {
    return const NoRecommendationWithinBudget();
  }

  final candidates = styleId == null
      ? withinBudget
      : withinBudget.where((sku) {
          final beer = catalog.beers.firstWhere((b) => b.id == sku.beerId);
          return beer.styleId == styleId;
        }).toList();

  if (candidates.isEmpty) {
    return const NoRecommendationMatchingStyle();
  }

  var best = candidates.first;
  for (final candidate in candidates.skip(1)) {
    if (candidate.valueScore > best.valueScore) {
      best = candidate;
    }
  }

  final beer = catalog.beers.firstWhere((b) => b.id == best.beerId);

  final styleClause = styleId == null
      ? ''
      : ' and matching your preferred '
          '${catalog.styles.firstWhere((s) => s.id == styleId).name} style';

  final explanation =
      'Within your ${budget.currencyLabel} budget$styleClause, ${beer.name} '
      '(${best.sizeMl.volumeLabel}) is the best value available — '
      'a Value Score of ${best.valueScore}.';

  return RecommendationFound(
    RecommendationResult(sku: best, beer: beer, explanation: explanation),
  );
}
