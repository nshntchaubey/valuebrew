import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile_repository.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('SharedPreferencesRecommendationProfileRepository', () {
    test('load returns balanced when nothing has been saved yet', () async {
      const repository = SharedPreferencesRecommendationProfileRepository();

      expect(await repository.load(), RecommendationProfile.balanced);
    });

    test('save then load round-trips every profile', () async {
      const repository = SharedPreferencesRecommendationProfileRepository();

      for (final profile in RecommendationProfile.values) {
        await repository.save(profile);
        expect(await repository.load(), profile);
      }
    });

    test('a second save replaces the first', () async {
      const repository = SharedPreferencesRecommendationProfileRepository();

      await repository.save(RecommendationProfile.discovery);
      await repository.save(RecommendationProfile.similarTaste);

      expect(await repository.load(), RecommendationProfile.similarTaste);
    });

    test('falls back to balanced when the stored value is unrecognized', () async {
      SharedPreferences.setMockInitialValues({
        'recommendation_profile': 'some_profile_removed_in_a_later_version',
      });
      const repository = SharedPreferencesRecommendationProfileRepository();

      expect(await repository.load(), RecommendationProfile.balanced);
    });

    test('persists across repository recreation — surviving an app restart', () async {
      const firstInstance = SharedPreferencesRecommendationProfileRepository();
      await firstInstance.save(RecommendationProfile.bestValue);

      const secondInstance = SharedPreferencesRecommendationProfileRepository();

      expect(await secondInstance.load(), RecommendationProfile.bestValue);
    });
  });
}
