import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/features/favorites/favorites_repository.dart';
import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';

class _FakeFavoritesRepository implements FavoritesRepository {
  _FakeFavoritesRepository([Set<String>? initial]) : _stored = {...?initial};

  Set<String> _stored;
  int saveCallCount = 0;
  int addCallCount = 0;
  int removeCallCount = 0;

  @override
  Future<Set<String>> load() async => {..._stored};

  @override
  Future<void> save(Set<String> beerIds) async {
    saveCallCount++;
    _stored = {...beerIds};
  }

  @override
  Future<void> add(String beerId) async {
    addCallCount++;
    _stored = {..._stored, beerId};
  }

  @override
  Future<void> remove(String beerId) async {
    removeCallCount++;
    _stored = {..._stored}..remove(beerId);
  }

  @override
  Future<bool> isFavorite(String beerId) async => _stored.contains(beerId);
}

/// Creates a [ProviderContainer] overriding [favoritesRepositoryProvider]
/// with [repository], reads [favoriteBeerIdsProvider] once to trigger its
/// (lazy) construction, then awaits a turn of the event loop so its async
/// initial load resolves before the caller inspects its state.
Future<ProviderContainer> _containerWithLoadedFavorites(
  _FakeFavoritesRepository repository,
) async {
  final container = ProviderContainer(
    overrides: [favoritesRepositoryProvider.overrideWithValue(repository)],
  );
  addTearDown(container.dispose);

  container.read(favoriteBeerIdsProvider);
  await Future<void>.delayed(Duration.zero);

  return container;
}

void main() {
  group('favoriteBeerIdsProvider', () {
    test('loads its initial state from the repository', () async {
      final repository = _FakeFavoritesRepository({'kf_premium'});
      final container = await _containerWithLoadedFavorites(repository);

      expect(container.read(favoriteBeerIdsProvider), {'kf_premium'});
    });

    test('starts empty when the repository has nothing saved', () async {
      final repository = _FakeFavoritesRepository();
      final container = await _containerWithLoadedFavorites(repository);

      expect(container.read(favoriteBeerIdsProvider), isEmpty);
    });

    test('add updates state immediately and persists via the repository', () async {
      final repository = _FakeFavoritesRepository();
      final container = await _containerWithLoadedFavorites(repository);

      final future = container.read(favoriteBeerIdsProvider.notifier).add('kf_premium');

      // State reflects the change before persistence even completes.
      expect(container.read(favoriteBeerIdsProvider), {'kf_premium'});

      await future;
      expect(repository.addCallCount, 1);
      expect(await repository.load(), {'kf_premium'});
    });

    test('adding an already-favorited beer does not call the repository again', () async {
      final repository = _FakeFavoritesRepository({'kf_premium'});
      final container = await _containerWithLoadedFavorites(repository);

      await container.read(favoriteBeerIdsProvider.notifier).add('kf_premium');

      expect(repository.addCallCount, 0);
      expect(container.read(favoriteBeerIdsProvider), {'kf_premium'});
    });

    test('remove updates state immediately and persists via the repository', () async {
      final repository = _FakeFavoritesRepository({'kf_premium', 'toit_porter'});
      final container = await _containerWithLoadedFavorites(repository);

      final future = container.read(favoriteBeerIdsProvider.notifier).remove('kf_premium');

      expect(container.read(favoriteBeerIdsProvider), {'toit_porter'});

      await future;
      expect(repository.removeCallCount, 1);
      expect(await repository.load(), {'toit_porter'});
    });

    test('removing a beer that isn\'t favorited does not call the repository', () async {
      final repository = _FakeFavoritesRepository({'kf_premium'});
      final container = await _containerWithLoadedFavorites(repository);

      await container.read(favoriteBeerIdsProvider.notifier).remove('no_such_beer');

      expect(repository.removeCallCount, 0);
      expect(container.read(favoriteBeerIdsProvider), {'kf_premium'});
    });

    test('toggle favorites an un-favorited beer, then un-favorites it back', () async {
      final repository = _FakeFavoritesRepository();
      final container = await _containerWithLoadedFavorites(repository);
      final notifier = container.read(favoriteBeerIdsProvider.notifier);

      await notifier.toggle('kf_premium');
      expect(container.read(favoriteBeerIdsProvider), {'kf_premium'});

      await notifier.toggle('kf_premium');
      expect(container.read(favoriteBeerIdsProvider), isEmpty);
    });

    test('isFavorite reflects current state', () async {
      final repository = _FakeFavoritesRepository({'kf_premium'});
      final container = await _containerWithLoadedFavorites(repository);
      final notifier = container.read(favoriteBeerIdsProvider.notifier);

      expect(notifier.isFavorite('kf_premium'), isTrue);
      expect(notifier.isFavorite('toit_porter'), isFalse);
    });
  });
}
