import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/sorting/models/sort_option.dart';
import 'package:valuebrew/features/sorting/providers/sorting_providers.dart';
import 'package:valuebrew/features/sorting/services/sorting_engine.dart';

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
      "value_score": 50, "value_verdict": "fair_value"
    },
    {
      "id": "toit_porter_330", "beer_id": "toit_porter", "size_ml": 330, "package_type": "can",
      "abv": 6.5, "calories": 220, "price": 250, "price_last_checked": "2026-07-18",
      "price_source": "test", "cost_per_litre": 757.6, "cost_per_ml_alcohol": 11.66,
      "value_score": 90, "value_verdict": "great_value"
    },
    {
      "id": "simba_strong_500", "beer_id": "simba_strong", "size_ml": 500, "package_type": "can",
      "abv": 8.0, "calories": 300, "price": 60, "price_last_checked": "2026-07-18",
      "price_source": "test", "cost_per_litre": 300.0, "cost_per_ml_alcohol": 3.75,
      "value_score": 70, "value_verdict": "fair_value"
    }
  ],
  "benchmarks": []
}
''';

ProviderContainer _container() {
  final catalogRepository = CatalogRepository(
    loadAsset: (key) async => _catalogJson,
    assetKey: 'fake_key',
  );
  return ProviderContainer(
    overrides: [catalogRepositoryProvider.overrideWithValue(catalogRepository)],
  );
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('sortOptionProvider', () {
    test('defaults to relevance', () {
      final container = _container();
      addTearDown(container.dispose);

      expect(container.read(sortOptionProvider), SortOption.relevance);
    });

    test('updating the notifier state changes what the provider reads', () {
      final container = _container();
      addTearDown(container.dispose);

      container.read(sortOptionProvider.notifier).state = SortOption.bestValue;

      expect(container.read(sortOptionProvider), SortOption.bestValue);
    });
  });

  group('sortingEngineProvider', () {
    test('exposes a SortingEngine', () {
      final container = _container();
      addTearDown(container.dispose);

      expect(container.read(sortingEngineProvider), isA<SortingEngine>());
    });
  });

  group('sortedHomeBeersProvider', () {
    test('equals the filtered results, unordered, when relevance is selected', () async {
      final container = _container();
      addTearDown(container.dispose);
      await container.read(catalogProvider.future);

      final filtered = container.read(filteredHomeBeersProvider).requireValue;
      final sorted = container.read(sortedHomeBeersProvider).requireValue;

      expect(sorted, filtered);
    });

    test('orders by valueScore descending when bestValue is selected', () async {
      final container = _container();
      addTearDown(container.dispose);
      await container.read(catalogProvider.future);

      container.read(sortOptionProvider.notifier).state = SortOption.bestValue;

      final sorted = container.read(sortedHomeBeersProvider).requireValue;
      expect(sorted.map((b) => b.id), ['toit_porter', 'simba_strong', 'kf_premium']);
    });

    test('recomputes when the sort option changes', () async {
      final container = _container();
      addTearDown(container.dispose);
      await container.read(catalogProvider.future);

      final relevanceOrder =
          container.read(sortedHomeBeersProvider).requireValue.map((b) => b.id).toList();

      container.read(sortOptionProvider.notifier).state = SortOption.priceLowToHigh;
      final priceOrder =
          container.read(sortedHomeBeersProvider).requireValue.map((b) => b.id).toList();

      expect(priceOrder, isNot(relevanceOrder));
      expect(priceOrder, ['simba_strong', 'kf_premium', 'toit_porter']);
    });

    test('sorts within the already-filtered subset, not the whole catalog', () async {
      final container = _container();
      addTearDown(container.dispose);
      await container.read(catalogProvider.future);

      container.read(filterStateProvider.notifier).state = FilterState.none.withStyle('lager');
      container.read(sortOptionProvider.notifier).state = SortOption.bestValue;

      final sorted = container.read(sortedHomeBeersProvider).requireValue;

      // toit_porter (stout, value 90) is filtered out entirely — it must
      // never reappear just because it would otherwise rank first.
      expect(sorted.map((b) => b.id), ['simba_strong', 'kf_premium']);
    });
  });

  group('sortedFavoriteBeersProvider', () {
    test('uses the same SortingEngine and SortOption as sortedHomeBeersProvider', () async {
      // With every beer favorited, the favorites source collection equals
      // the full catalog — the only variable left is which provider
      // computed the result.
      final container = _container();
      addTearDown(container.dispose);
      await container.read(catalogProvider.future);
      container.read(favoriteBeerIdsProvider.notifier);
      await Future<void>.delayed(Duration.zero);

      for (final beerId in ['kf_premium', 'toit_porter', 'simba_strong']) {
        await container.read(favoriteBeerIdsProvider.notifier).add(beerId);
      }
      container.read(sortOptionProvider.notifier).state = SortOption.nameAToZ;

      final homeResult = container.read(sortedHomeBeersProvider).requireValue;
      final favoritesResult = container.read(sortedFavoriteBeersProvider).requireValue;

      expect(homeResult, favoritesResult);
    });
  });
}
