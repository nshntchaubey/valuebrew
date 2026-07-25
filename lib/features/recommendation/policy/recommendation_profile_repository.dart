import 'package:shared_preferences/shared_preferences.dart';

import 'package:valuebrew/features/recommendation/policy/recommendation_profile.dart';

/// Reads and writes the user's selected [RecommendationProfile], persisted
/// locally — the same [SharedPreferences]-backed approach already
/// established for favorites (see `favorites_repository.dart`).
abstract class RecommendationProfileRepository {
  /// Returns the currently persisted profile, or
  /// [RecommendationProfile.balanced] if none has been saved yet.
  Future<RecommendationProfile> load();

  /// Persists [profile] as the current selection.
  Future<void> save(RecommendationProfile profile);
}

/// A [RecommendationProfileRepository] backed by [SharedPreferences].
///
/// Stores [RecommendationProfile.name] (e.g. `"bestValue"`) as a plain
/// string — a storage key, not a value the rest of the app ever compares
/// against directly (see [RecommendationProfile]'s own doc comment). An
/// unrecognized or corrupted stored value falls back to
/// [RecommendationProfile.balanced] rather than throwing, the same
/// forgiving default used when nothing has been saved at all.
class SharedPreferencesRecommendationProfileRepository implements RecommendationProfileRepository {
  const SharedPreferencesRecommendationProfileRepository();

  static const _prefsKey = 'recommendation_profile';

  @override
  Future<RecommendationProfile> load() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_prefsKey);
    if (stored == null) return RecommendationProfile.balanced;

    return RecommendationProfile.values.firstWhere(
      (profile) => profile.name == stored,
      orElse: () => RecommendationProfile.balanced,
    );
  }

  @override
  Future<void> save(RecommendationProfile profile) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, profile.name);
  }
}
