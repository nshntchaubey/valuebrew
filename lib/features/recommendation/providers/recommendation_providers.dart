import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile_repository.dart';
import 'package:valuebrew/features/recommendation/services/recommendation_engine.dart';

/// Exposes the app's [RecommendationProfileRepository].
///
/// Construction happens here, not inside [RecommendationProfileNotifier] —
/// the same separation `favoritesRepositoryProvider` uses for
/// `FavoritesRepository`. Override this in tests to substitute a fake
/// without touching real [SharedPreferences].
final recommendationProfileRepositoryProvider = Provider<RecommendationProfileRepository>((ref) {
  return const SharedPreferencesRecommendationProfileRepository();
});

/// Holds the currently active [RecommendationProfile] in memory, backed by
/// [RecommendationProfileRepository] for persistence.
///
/// Starts at [RecommendationProfile.balanced] and loads the real persisted
/// value once, asynchronously, at construction — the same pattern
/// `FavoritesNotifier` uses for the same reason: a screen watching this
/// provider should never need to know whether the value it's reading came
/// from disk yet.
class RecommendationProfileNotifier extends StateNotifier<RecommendationProfile> {
  RecommendationProfileNotifier(this._repository) : super(RecommendationProfile.balanced) {
    _loadInitial();
  }

  final RecommendationProfileRepository _repository;

  Future<void> _loadInitial() async {
    state = await _repository.load();
  }

  /// Selects [profile] as the active recommendation profile.
  ///
  /// Updates [state] immediately, so every screen watching it — and, in
  /// turn, [recommendationEngineProvider] — reflects the change on the
  /// very next frame; persisting via [RecommendationProfileRepository]
  /// happens after, not before, since nothing in the UI needs to wait on
  /// it. A no-op if [profile] is already the active one.
  Future<void> select(RecommendationProfile profile) async {
    if (state == profile) return;
    state = profile;
    await _repository.save(profile);
  }
}

/// The currently active [RecommendationProfile].
///
/// This is what a profile selector reads and writes, and what
/// [recommendationPolicyProvider] watches to decide which policy to hand
/// [RecommendationEngine]. Changing it never rebuilds `catalogProvider`,
/// `favoriteBeerIdsProvider`, `filterStateProvider`, or anything else
/// unrelated — only this provider and the two below it recompute.
final recommendationProfileProvider =
    StateNotifierProvider<RecommendationProfileNotifier, RecommendationProfile>((ref) {
  return RecommendationProfileNotifier(ref.watch(recommendationProfileRepositoryProvider));
});

/// Exposes the app's [RecommendationPolicy]: whatever
/// [recommendationProfileProvider]'s active profile maps to.
///
/// This is the one place a profile selection turns into an actual
/// [RecommendationPolicy] — [RecommendationEngine] and
/// [recommendationEngineProvider] below have no idea profiles exist at
/// all, and never need to.
final recommendationPolicyProvider = Provider<RecommendationPolicy>((ref) {
  final profile = ref.watch(recommendationProfileProvider);
  return profile.policy;
});

/// Exposes the app's [RecommendationEngine], configured with whatever
/// [recommendationPolicyProvider] currently provides.
///
/// A screen reads this and calls
/// `ref.read(recommendationEngineProvider).similarBeers(sku, catalog)` (or
/// `.betterValueAlternatives(...)`) directly.
final recommendationEngineProvider = Provider<RecommendationEngine>((ref) {
  final policy = ref.watch(recommendationPolicyProvider);
  return RecommendationEngine(policy: policy);
});
