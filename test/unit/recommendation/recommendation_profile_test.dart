import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/features/recommendation/policy/profile_policies.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile.dart';

void main() {
  group('RecommendationProfile', () {
    test('every profile has a non-empty displayName and description', () {
      for (final profile in RecommendationProfile.values) {
        expect(profile.displayName, isNotEmpty, reason: '$profile');
        expect(profile.description, isNotEmpty, reason: '$profile');
      }
    });

    test('every profile has a distinct displayName', () {
      final names = RecommendationProfile.values.map((p) => p.displayName).toSet();
      expect(names.length, RecommendationProfile.values.length);
    });

    test('balanced maps to DefaultRecommendationPolicy', () {
      expect(RecommendationProfile.balanced.policy, isA<DefaultRecommendationPolicy>());
    });

    test('bestValue maps to BestValuePolicy', () {
      expect(RecommendationProfile.bestValue.policy, isA<BestValuePolicy>());
    });

    test('similarTaste maps to SimilarTastePolicy', () {
      expect(RecommendationProfile.similarTaste.policy, isA<SimilarTastePolicy>());
    });

    test('discovery maps to DiscoveryPolicy', () {
      expect(RecommendationProfile.discovery.policy, isA<DiscoveryPolicy>());
    });

    test('every profile\'s policy uses the same betterValueAlternatives thresholds', () {
      // Deliberate: profiles only vary similarityScorer (see
      // profile_policies.dart's own note on why betterValueAlternatives
      // is profile-independent).
      for (final profile in RecommendationProfile.values) {
        final policy = profile.policy;
        expect(policy.minSimilarityScore, 0.0, reason: '$profile');
        expect(policy.comparableAbvTolerance, 1.5, reason: '$profile');
        expect(policy.minValueScoreImprovement, 1, reason: '$profile');
      }
    });
  });
}
