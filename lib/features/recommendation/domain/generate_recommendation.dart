import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_outcome.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_result.dart';
import 'package:valuebrew/features/recommendation/domain/tied_candidate.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';

/// Recommends one SKU from [catalog] within [budget], optionally narrowed
/// by [styleId].
///
/// This is the smallest complete Recommendation Vertical Slice's entire
/// reasoning, following the canonical constraint hierarchy exactly:
/// [budget] (a Hard Constraint) filters the full catalog first; [styleId]
/// (a Strong Preference), if given, narrows only within whatever survives
/// that. Among the final candidates, the one with the best Value Score
/// wins — the highest-confidence remaining differentiator, per the
/// Recommendation Framework's tie-breaker rule (Section 2) — unless
/// multiple candidates share that exact best score, in which case a
/// [RecommendationTie] is returned instead of an arbitrary pick, per the
/// Recommendation Framework's own rule for a genuine tie (Section 5).
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
/// leave candidates too close together; Proxy-Buying Mode's conservative
/// default; a general unmet-preferences outcome model once a second
/// Strong Preference exists (this milestone's [NoRecommendationMatchingStyle]
/// is deliberately specific to style alone, not yet generalized);
/// Trade-off Explanation, which requires two conflicting Strong
/// Preferences to exist simultaneously — not reachable with today's
/// single optional style preference, and mechanically distinct from the
/// tie handling implemented here.
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
          final beer = resolveBeer(catalog, sku.beerId) ??
              (throw StateError('No beer found for id: ${sku.beerId}'));
          return beer.styleId == styleId;
        }).toList();

  if (candidates.isEmpty) {
    return const NoRecommendationMatchingStyle();
  }

  var tied = [candidates.first];
  for (final candidate in candidates.skip(1)) {
    if (candidate.valueScore > tied.first.valueScore) {
      tied = [candidate];
    } else if (candidate.valueScore == tied.first.valueScore) {
      tied.add(candidate);
    }
  }

  var styleClause = '';
  if (styleId != null) {
    final style = resolveStyle(catalog, styleId) ??
        (throw StateError('No style found for id: $styleId'));
    styleClause = ' and matching your preferred ${style.name} style';
  }

  if (tied.length == 1) {
    final best = tied.single;
    final beer = resolveBeer(catalog, best.beerId) ??
        (throw StateError('No beer found for id: ${best.beerId}'));

    final explanation =
        'Within your ${budget.currencyLabel} budget$styleClause, ${beer.name} '
        '(${best.sizeMl.volumeLabel}) is the best value available — '
        'a Value Score of ${best.valueScore}.';

    return RecommendationFound(
      RecommendationResult(sku: best, beer: beer, explanation: explanation),
    );
  }

  final tiedCandidates = tied.map((sku) {
    final beer = resolveBeer(catalog, sku.beerId) ??
        (throw StateError('No beer found for id: ${sku.beerId}'));
    return TiedCandidate(sku: sku, beer: beer);
  }).toList();

  final explanation =
      'Within your ${budget.currencyLabel} budget$styleClause, '
      '${tied.length} beers are equally good, each with a Value Score of '
      "${tied.first.valueScore} — these are equivalent on everything "
      "you've told me matters.";

  return RecommendationTie(tiedCandidates, explanation);
}
