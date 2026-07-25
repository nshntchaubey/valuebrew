import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/features/recommendation/policy/profile_policies.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_policy.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile.dart';
import 'package:valuebrew/features/recommendation/policy/recommendation_profile_repository.dart';
import 'package:valuebrew/features/recommendation/providers/recommendation_providers.dart';

class _FakeRecommendationProfileRepository implements RecommendationProfileRepository {
  _FakeRecommendationProfileRepository([this._stored = RecommendationProfile.balanced]);

  RecommendationProfile _stored;
  int saveCallCount = 0;

  @override
  Future<RecommendationProfile> load() async => _stored;

  @override
  Future<void> save(RecommendationProfile profile) async {
    saveCallCount++;
    _stored = profile;
  }
}

/// Builds a [ProviderContainer] wired to [repository], primes
/// [recommendationProfileProvider] to trigger its (lazy) construction, and
/// awaits its async initial load resolving.
Future<ProviderContainer> _readyContainer(_FakeRecommendationProfileRepository repository) async {
  final container = ProviderContainer(
    overrides: [recommendationProfileRepositoryProvider.overrideWithValue(repository)],
  );
  container.read(recommendationProfileProvider);
  await Future<void>.delayed(Duration.zero);
  return container;
}

void main() {
  group('recommendationProfileProvider', () {
    test('loads its initial state from the repository', () async {
      final repository = _FakeRecommendationProfileRepository(RecommendationProfile.discovery);
      final container = await _readyContainer(repository);
      addTearDown(container.dispose);

      expect(container.read(recommendationProfileProvider), RecommendationProfile.discovery);
    });

    test('defaults to balanced when the repository has nothing saved', () async {
      final container = await _readyContainer(_FakeRecommendationProfileRepository());
      addTearDown(container.dispose);

      expect(container.read(recommendationProfileProvider), RecommendationProfile.balanced);
    });

    test('select updates state immediately and persists via the repository', () async {
      final repository = _FakeRecommendationProfileRepository();
      final container = await _readyContainer(repository);
      addTearDown(container.dispose);

      final future = container
          .read(recommendationProfileProvider.notifier)
          .select(RecommendationProfile.bestValue);

      // State reflects the change before persistence even completes.
      expect(container.read(recommendationProfileProvider), RecommendationProfile.bestValue);

      await future;
      expect(repository.saveCallCount, 1);
      expect(await repository.load(), RecommendationProfile.bestValue);
    });

    test('selecting the already-active profile does not call the repository again', () async {
      final repository = _FakeRecommendationProfileRepository(RecommendationProfile.similarTaste);
      final container = await _readyContainer(repository);
      addTearDown(container.dispose);

      await container
          .read(recommendationProfileProvider.notifier)
          .select(RecommendationProfile.similarTaste);

      expect(repository.saveCallCount, 0);
    });
  });

  group('recommendationPolicyProvider', () {
    test('returns the policy matching the active profile', () async {
      final container = await _readyContainer(
        _FakeRecommendationProfileRepository(RecommendationProfile.discovery),
      );
      addTearDown(container.dispose);

      expect(container.read(recommendationPolicyProvider), isA<DiscoveryPolicy>());
    });

    test('recomputes when the profile changes', () async {
      final container = await _readyContainer(_FakeRecommendationProfileRepository());
      addTearDown(container.dispose);

      expect(container.read(recommendationPolicyProvider), isA<DefaultRecommendationPolicy>());

      await container
          .read(recommendationProfileProvider.notifier)
          .select(RecommendationProfile.similarTaste);

      expect(container.read(recommendationPolicyProvider), isA<SimilarTastePolicy>());
    });
  });

  group('recommendationEngineProvider', () {
    test('is configured with the policy matching the active profile', () async {
      final container = await _readyContainer(
        _FakeRecommendationProfileRepository(RecommendationProfile.bestValue),
      );
      addTearDown(container.dispose);

      final engine = container.read(recommendationEngineProvider);
      expect(engine.policy, isA<BestValuePolicy>());
    });

    test('recomputes when the profile changes, without needing any change of its own', () async {
      final container = await _readyContainer(_FakeRecommendationProfileRepository());
      addTearDown(container.dispose);

      expect(container.read(recommendationEngineProvider).policy, isA<DefaultRecommendationPolicy>());

      await container
          .read(recommendationProfileProvider.notifier)
          .select(RecommendationProfile.discovery);

      expect(container.read(recommendationEngineProvider).policy, isA<DiscoveryPolicy>());
    });
  });
}
