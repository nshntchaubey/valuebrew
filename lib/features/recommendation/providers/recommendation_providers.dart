import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/services/recommendation_engine.dart';

/// Exposes the app's [RecommendationPolicy].
///
/// Defaults to [DefaultRecommendationPolicy]. A future recommendation
/// profile (Budget Drinker, Craft Explorer, ...) would override this
/// provider with a different [RecommendationPolicy] implementation —
/// every recommendation [recommendationEngineProvider] produces changes
/// automatically, without touching [recommendationEngineProvider] itself
/// or [RecommendationEngine].
final recommendationPolicyProvider = Provider<RecommendationPolicy>((ref) {
  return const DefaultRecommendationPolicy();
});

/// Exposes the app's [RecommendationEngine], configured with whatever
/// [recommendationPolicyProvider] currently provides.
///
/// A future screen would read this and call
/// `ref.read(recommendationEngineProvider).similarBeers(sku, catalog)` (or
/// `.betterValueAlternatives(...)`) directly. This milestone builds the
/// engine and this provider only — wiring it into any actual screen (for
/// example, replacing `BeerDetailScreen`'s existing, simpler Beer-level
/// "Similar & Better Value" section, which is untouched by this
/// milestone) is explicitly out of scope here; see the milestone report.
final recommendationEngineProvider = Provider<RecommendationEngine>((ref) {
  final policy = ref.watch(recommendationPolicyProvider);
  return RecommendationEngine(policy: policy);
});
