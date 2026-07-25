import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:valuebrew/features/recommendation/services/recommendation_engine.dart';

/// Exposes the app's [RecommendationEngine].
///
/// A future screen would read this and call
/// `ref.read(recommendationEngineProvider).similarBeers(sku, catalog)` (or
/// `.betterValueAlternatives(...)`) directly. This milestone builds the
/// engine and this provider only — wiring it into any actual screen (for
/// example, replacing `BeerDetailScreen`'s existing, simpler Beer-level
/// "Similar & Better Value" section, which is untouched by this
/// milestone) is explicitly out of scope here; see the milestone report.
final recommendationEngineProvider = Provider<RecommendationEngine>((ref) {
  return RecommendationEngine();
});
