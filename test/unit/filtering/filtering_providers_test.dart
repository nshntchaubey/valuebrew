import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/favorites/favorites_repository.dart';
import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/filtering/services/filtering_engine.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

class _FakeFavoritesRepository implements FavoritesRepository {
  _FakeFavoritesRepository([Set<String>? initial]) : _stored = {...?initial};

  Set<String> _stored;

  @override
  Future<Set<String>> load() async => {..._stored};

  @override
  Future<void> save(Set<String> beerIds) async => _stored = {...beerIds};

  @override
  Future<void> add(String beerId) async => _stored = {..._stored, beerId};

  @override
  Future<void> remove(String beerId) async {
    final updated = {..._stored};
    updated.remove(beerId);
    _stored = updated;
  }

  @override
  Future<bool> isFavorite(String beerId) async => _stored.contains(beerId);
}

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
    { "id": "stout", "name": "Stout", "description": "Dark, roasted" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "stout", "is_craft": true },
    { "id": "simba_strong", "name": "Simba Strong", "brewery": "Kals Brewing", "style_id": "lager", "is_craft": false }
  ],
  "skus": [
    {
      "id": "kf_premium_650", "beer_id": "kf_premium", "size_ml": 650, "package_type": "bottle",
      "abv": 4.8, "calories": 260, "price": 110, "price_last_checked": "2026-07-20",
      "price_source": "test", "cost_per_litre": 169.2, "cost_per_ml_alcohol": 3.52,
      "value_score": 78, "value_verdict": "great_value"
    },
    {
      "id": "toit_porter_330", "beer_id": "toit_porter", "size_ml": 330, "package_type": "can",
      "abv": 6.5, "calories": 220, "price": 250, "price_last_checked": "2026-07-18",
      "price_source": "test", "cost_per_litre": 757.6, "cost_per_ml_alcohol": 11.66,
      "value_score": 55, "value_verdict": "fair_value"
    },
    {
      "id": "simba_strong_500", "beer_id": "simba_strong", "size_ml": 500, "package_type": "can",
      "abv": 8.0, "calories": 300, "price": 150, "price_last_checked": "2026-07-18",
      "price_source": "test", "cost_per_litre": 300.0, "cost_per_ml_alcohol": 3.75,
      "value_score": 82, "value_verdict": "great_value"
    }
  ],
  "benchmarks": []
}
''';

/// Builds a [ProviderContainer] wired to an in-memory catalog and favorites
/// repository, and waits for both [catalogProvider]'s load and
/// [favoriteBeerIdsProvider]'s initial load to resolve — so every test can
/// read [filteredHomeBeersProvider]/[filteredFavoriteBeersProvider]
/// synchronously afterward via `.requireValue`.
Future<ProviderContainer> _readyContainer({Set<String>? favoriteIds}) async {
  final catalogRepository = CatalogRepository(
    loadAsset: (key) async => _catalogJson,
    assetKey: 'fake_key',
  );
  final container = ProviderContainer(
    overrides: [
      catalogRepositoryProvider.overrideWithValue(catalogRepository),
      favoritesRepositoryProvider.overrideWithValue(_FakeFavoritesRepository(favoriteIds)),
    ],
  );

  container.read(favoriteBeerIdsProvider);
  await container.read(catalogProvider.future);
  await Future<void>.delayed(Duration.zero);

  return container;
}

void main() {
  group('filterStateProvider', () {
    test('defaults to FilterState.none', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      expect(container.read(filterStateProvider), FilterState.none);
    });

    test('updating the notifier state changes what the provider reads', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('lager');

      expect(container.read(filterStateProvider).styleId, 'lager');
    });

    test('resetting to FilterState.none clears every filter', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('lager');
      container.read(filterStateProvider.notifier).state = FilterState.none;

      expect(container.read(filterStateProvider).isActive, isFalse);
    });
  });

  group('filteringEngineProvider', () {
    test('exposes a FilteringEngine', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      expect(container.read(filteringEngineProvider), isA<FilteringEngine>());
    });
  });

  group('filteredHomeBeersProvider', () {
    test('equals the unfiltered search results when no filter is active', () async {
      final container = await _readyContainer();
      addTearDown(container.dispose);

      final searchResults = container.read(searchResultsProvider).requireValue;
      final filtered = container.read(filteredHomeBeersProvider).requireValue;

      expect(filtered, searchResults);
    });

    test('narrows the search results when a filter is active', () async {
      final container = await _readyContainer();
      addTearDown(container.dispose);

      container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('lager');

      final filtered = container.read(filteredHomeBeersProvider).requireValue;

      expect(filtered.map((b) => b.id), ['kf_premium', 'simba_strong']);
    });

    test('recomputes when the filter changes', () async {
      final container = await _readyContainer();
      addTearDown(container.dispose);

      final before = container.read(filteredHomeBeersProvider).requireValue;
      expect(before, hasLength(3));

      container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('stout');
      final after = container.read(filteredHomeBeersProvider).requireValue;

      expect(after.map((b) => b.id), ['toit_porter']);
    });

    test('composes with search: a search query narrows first, filters narrow further', () async {
      final container = await _readyContainer();
      addTearDown(container.dispose);

      container.read(searchQueryProvider.notifier).state = 'kingfisher';
      container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('stout');

      final filtered = container.read(filteredHomeBeersProvider).requireValue;

      // "kingfisher" only matches Kingfisher Premium (lager); filtering to
      // stout on top of that leaves nothing.
      expect(filtered, isEmpty);
    });
  });

  group('filteredFavoriteBeersProvider', () {
    test('contains only favorited beers when no filter is active', () async {
      final container = await _readyContainer(favoriteIds: {'kf_premium', 'simba_strong'});
      addTearDown(container.dispose);

      final filtered = container.read(filteredFavoriteBeersProvider).requireValue;

      expect(filtered.map((b) => b.id).toSet(), {'kf_premium', 'simba_strong'});
    });

    test('narrows favorited beers further when a filter is active', () async {
      final container = await _readyContainer(favoriteIds: {'kf_premium', 'simba_strong'});
      addTearDown(container.dispose);

      container.read(filterStateProvider.notifier).state = FilterState.none.withMinValueScore(80);

      final filtered = container.read(filteredFavoriteBeersProvider).requireValue;

      // Of the two favorites, only simba_strong (82) clears 80; kf_premium
      // (78) does not.
      expect(filtered.map((b) => b.id), ['simba_strong']);
    });

    test('recomputes when the favorited set changes', () async {
      final container = await _readyContainer(favoriteIds: {'kf_premium'});
      addTearDown(container.dispose);

      final before = container.read(filteredFavoriteBeersProvider).requireValue;
      expect(before.map((b) => b.id), ['kf_premium']);

      await container.read(favoriteBeerIdsProvider.notifier).add('simba_strong');
      final after = container.read(filteredFavoriteBeersProvider).requireValue;

      expect(after.map((b) => b.id).toSet(), {'kf_premium', 'simba_strong'});
    });
  });

  group('shared engine verification', () {
    test(
      'filteredHomeBeersProvider and filteredFavoriteBeersProvider apply the same '
      'FilterState identically to whatever beers they are given',
      () async {
        // Every beer is favorited, so the favorites source collection is
        // the same as the full catalog search results — the only variable
        // left is which provider computed the result.
        final container = await _readyContainer(
          favoriteIds: {'kf_premium', 'toit_porter', 'simba_strong'},
        );
        addTearDown(container.dispose);

        container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('lager');

        final homeResult = container.read(filteredHomeBeersProvider).requireValue;
        final favoritesResult = container.read(filteredFavoriteBeersProvider).requireValue;

        expect(homeResult, favoritesResult);
      },
    );
  });
}
