import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "lager", "is_craft": true },
    { "id": "simba_strong", "name": "Simba Strong", "brewery": "Kals Brewing", "style_id": "lager", "is_craft": false }
  ],
  "skus": [],
  "benchmarks": []
}
''';

ProviderContainer _containerWithCatalog() {
  final repository = CatalogRepository(
    loadAsset: (key) async => _catalogJson,
    assetKey: 'fake_key',
  );
  final container = ProviderContainer(
    overrides: [catalogRepositoryProvider.overrideWithValue(repository)],
  );
  addTearDown(container.dispose);
  return container;
}

void main() {
  group('searchQueryProvider', () {
    test('defaults to an empty string', () {
      final container = _containerWithCatalog();

      expect(container.read(searchQueryProvider), '');
    });
  });

  group('searchResultsProvider', () {
    test('returns every beer when the query is empty', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      final results = container.read(searchResultsProvider);

      expect(results.value, hasLength(3));
    });

    test('returns every beer when the query is only whitespace', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      container.read(searchQueryProvider.notifier).state = '   ';

      expect(container.read(searchResultsProvider).value, hasLength(3));
    });

    test('filters by beer name, case-insensitively', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      container.read(searchQueryProvider.notifier).state = 'KING';

      final results = container.read(searchResultsProvider).value!;
      expect(results, hasLength(1));
      expect(results.single.name, 'Kingfisher Premium');
    });

    test('filters by brewery name, case-insensitively', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      container.read(searchQueryProvider.notifier).state = 'toit brewpub';

      final results = container.read(searchResultsProvider).value!;
      expect(results, hasLength(1));
      expect(results.single.name, 'Toit Porter');
    });

    test('trims leading and trailing whitespace from the query', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      container.read(searchQueryProvider.notifier).state = '  simba  ';

      final results = container.read(searchResultsProvider).value!;
      expect(results, hasLength(1));
      expect(results.single.name, 'Simba Strong');
    });

    test('returns an empty list when nothing matches', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      container.read(searchQueryProvider.notifier).state = 'nonexistent';

      expect(container.read(searchResultsProvider).value, isEmpty);
    });

    test('does not match a substring split across name and brewery', () async {
      final container = _containerWithCatalog();
      await container.read(catalogProvider.future);

      // "Premium United" spans the end of the name and start of the
      // brewery of the same beer, but is not a substring of either field.
      container.read(searchQueryProvider.notifier).state = 'Premium United';

      expect(container.read(searchResultsProvider).value, isEmpty);
    });

    test('passes through the loading state from catalogProvider', () {
      final container = _containerWithCatalog();

      final results = container.read(searchResultsProvider);

      expect(results, isA<AsyncLoading<List<dynamic>>>());
    });

    test('passes through the error state from catalogProvider', () async {
      final failingRepository = CatalogRepository(
        loadAsset: (key) async => throw Exception('boom'),
        assetKey: 'fake_key',
      );
      final container = ProviderContainer(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(failingRepository),
        ],
      );
      addTearDown(container.dispose);

      try {
        await container.read(catalogProvider.future);
      } catch (_) {
        // Expected: the fake repository always throws.
      }

      expect(container.read(searchResultsProvider).hasError, isTrue);
    });
  });
}
