import 'package:valuebrew/features/recommendation/policy/profile_policies.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';

/// A user-selectable recommendation profile — which [RecommendationPolicy]
/// (and therefore which weights) [RecommendationEngine] executes.
///
/// A plain enum, not a string, an integer ID, or a boolean flag: every
/// valid profile is a named, exhaustively-switchable value. There is no
/// "unknown profile" state to guard against, no risk of a typo'd string
/// silently falling through to some default, and no combination of
/// booleans that could represent an invalid or ambiguous state — exactly
/// what "clearly express recommendation intent" means here.
///
/// Persisted by [RecommendationProfileRepository] as [name] (e.g.
/// `"bestValue"`) purely as a storage key — that's serialization, the
/// same as every other enum in this codebase ([PackageType],
/// [ValueVerdict]) round-tripping through a string field, not a
/// reintroduction of the string comparisons this model is meant to avoid
/// for actual application logic.
enum RecommendationProfile {
  /// The original, no-single-dimension-dominant mix: style, ABV, price
  /// closeness, package type, and brewery. See
  /// [DefaultRecommendationPolicy]. Unchanged by this milestone.
  balanced,

  /// Surfaces bargains, even if less similar to what's being viewed. See
  /// [BestValuePolicy].
  bestValue,

  /// Surfaces the closest match to what's being viewed; price barely
  /// factors in. See [SimilarTastePolicy].
  similarTaste,

  /// Surfaces something new: good value from a different brewery and
  /// style, rather than a close match. See [DiscoveryPolicy].
  discovery;

  /// Short, user-facing name for a profile selector.
  String get displayName {
    switch (this) {
      case RecommendationProfile.balanced:
        return 'Balanced';
      case RecommendationProfile.bestValue:
        return 'Best Value';
      case RecommendationProfile.similarTaste:
        return 'Similar Taste';
      case RecommendationProfile.discovery:
        return 'Discovery';
    }
  }

  /// One-line, user-facing explanation of what this profile prioritizes.
  String get description {
    switch (this) {
      case RecommendationProfile.balanced:
        return 'A well-rounded mix of similarity and value.';
      case RecommendationProfile.bestValue:
        return "Surfaces bargains, even if less similar to what you're viewing.";
      case RecommendationProfile.similarTaste:
        return "The closest match to what you're viewing — price matters less.";
      case RecommendationProfile.discovery:
        return 'Explore something new: good value, different brewery, different style.';
    }
  }

  /// The [RecommendationPolicy] this profile configures
  /// [RecommendationEngine] with.
  RecommendationPolicy get policy {
    switch (this) {
      case RecommendationProfile.balanced:
        return const DefaultRecommendationPolicy();
      case RecommendationProfile.bestValue:
        return const BestValuePolicy();
      case RecommendationProfile.similarTaste:
        return const SimilarTastePolicy();
      case RecommendationProfile.discovery:
        return const DiscoveryPolicy();
    }
  }
}
