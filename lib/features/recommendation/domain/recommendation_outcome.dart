import 'package:valuebrew/features/recommendation/domain/recommendation_result.dart';
import 'package:valuebrew/features/recommendation/domain/tied_candidate.dart';

/// The outcome of [generateRecommendation]: one of four real, honest
/// results — a recommendation was found, no SKU satisfies the stated
/// budget at all, SKUs exist within budget but none match the stated
/// style, or multiple SKUs are genuinely tied for the best value.
sealed class RecommendationOutcome {
  const RecommendationOutcome();

  /// Whether refinement remains meaningful from this outcome.
  ///
  /// The architectural invariant: refinement remains available whenever
  /// at least one SKU satisfies every currently stated Hard Constraint
  /// (today: budget alone) — independent of whether any currently stated
  /// Strong Preference (today: style) is currently satisfied. Narrowing
  /// by a Strong Preference can only ever shrink or preserve the
  /// Hard-Constraint-satisfying set, never grow it, so this check is the
  /// complete implementation of "could additional preference information
  /// still change the recommendation," not an approximation of it.
  ///
  /// A single exhaustive switch, not per-subclass overrides, so a future
  /// outcome variant cannot be added without the compiler forcing an
  /// explicit decision about its refinability here.
  bool get canBeRefinedFurther => switch (this) {
        NoRecommendationWithinBudget() => false,
        RecommendationFound() || NoRecommendationMatchingStyle() || RecommendationTie() =>
          true,
      };
}

/// A recommendation was found: [result] is the selected SKU, its beer,
/// and the explanation of why it was chosen.
class RecommendationFound extends RecommendationOutcome {
  const RecommendationFound(this.result);

  /// The recommendation itself.
  final RecommendationResult result;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is RecommendationFound && other.result == result);
  }

  @override
  int get hashCode => result.hashCode;

  @override
  String toString() => 'RecommendationFound(result: $result)';
}

/// No SKU in the catalog is at or under the stated budget.
class NoRecommendationWithinBudget extends RecommendationOutcome {
  const NoRecommendationWithinBudget();

  @override
  bool operator ==(Object other) => other is NoRecommendationWithinBudget;

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() => 'NoRecommendationWithinBudget()';
}

/// SKUs exist within the stated budget, but none match the stated style.
class NoRecommendationMatchingStyle extends RecommendationOutcome {
  const NoRecommendationMatchingStyle();

  @override
  bool operator ==(Object other) => other is NoRecommendationMatchingStyle;

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() => 'NoRecommendationMatchingStyle()';
}

/// Multiple SKUs are equally the best value within the stated budget and
/// style — a genuine, honest recommendation in its own right per the
/// Recommendation Framework ("these are equivalent on everything you've
/// told me matters"), never an arbitrary pick among them.
class RecommendationTie extends RecommendationOutcome {
  const RecommendationTie(this.candidates, this.explanation);

  /// Every SKU sharing the best Value Score among the final candidates.
  final List<TiedCandidate> candidates;

  /// Plain-language statement of the tie, per the Recommendation
  /// Framework's explanation rules.
  final String explanation;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is RecommendationTie &&
            _listEquals(other.candidates, candidates) &&
            other.explanation == explanation);
  }

  /// Element-wise list equality, since [List]'s default `==` is identity,
  /// not content, comparison — the same pattern [Catalog] already uses,
  /// specialized here to [TiedCandidate] since this is the only list this
  /// class has.
  static bool _listEquals(List<TiedCandidate> a, List<TiedCandidate> b) {
    if (identical(a, b)) return true;
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }

  @override
  int get hashCode => Object.hash(Object.hashAll(candidates), explanation);

  @override
  String toString() =>
      'RecommendationTie(candidates: '
      '${candidates.map((c) => c.sku.id).join(', ')}, '
      'explanation: $explanation)';
}
