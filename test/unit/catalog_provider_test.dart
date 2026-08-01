import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/core/constants/app_constants.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// A fake [CatalogRepository.loadAsset] that returns [contents] for any key.
Future<String> Function(String key) fixedLoader(String contents) {
  return (key) async => contents;
}

const _validCatalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false }
  ],
  "skus": [
    {
      "id": "kf_premium_650",
      "beer_id": "kf_premium",
      "size_ml": 650,
      "package_type": "bottle",
      "abv": 4.8,
      "calories": 260,
      "price": 110,
      "price_last_checked": "2026-07-20",
      "price_source": "test",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 3.52,
      "value_score": 78,
      "value_verdict": "great_value"
    }
  ],
  "benchmarks": [
    { "style_id": "lager", "avg_cost_per_ml_alcohol": 4.10, "p25": 3.40, "p50": 3.95, "p75": 4.60, "sample_size": 1 }
  ]
}
''';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('catalogRepositoryProvider', () {
    test('constructs a CatalogRepository configured with AppConstants.catalogAssetKey', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final repository = container.read(catalogRepositoryProvider);

      expect(repository.assetKey, AppConstants.catalogAssetKey);
    });

    test('the default repository successfully loads the real bundled asset', () async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final repository = container.read(catalogRepositoryProvider);
      final catalog = await repository.loadCatalog();

      expect(catalog.styles, isNotEmpty);
      expect(catalog.beers, isNotEmpty);
      expect(catalog.skus, isNotEmpty);
      expect(catalog.benchmarks, isNotEmpty);
    });

    test('can be overridden with a fake repository', () {
      final fakeRepository = CatalogRepository(
        loadAsset: fixedLoader(_validCatalogJson),
        assetKey: 'fake_key',
      );
      final container = ProviderContainer(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
      );
      addTearDown(container.dispose);

      expect(container.read(catalogRepositoryProvider), same(fakeRepository));
    });
  });

  group('catalogProvider', () {
    test('resolves to the Catalog produced by the overridden repository', () async {
      final fakeRepository = CatalogRepository(
        loadAsset: fixedLoader(_validCatalogJson),
        assetKey: 'fake_key',
      );
      final container = ProviderContainer(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
      );
      addTearDown(container.dispose);

      final catalog = await container.read(catalogProvider.future);

      expect(catalog, isA<Catalog>());
      expect(catalog.catalogVersion, 1);
      expect(catalog.beers.single.name, 'Kingfisher Premium');
    });

    test('surfaces a repository parse failure as a thrown CatalogParseException', () async {
      final fakeRepository = CatalogRepository(
        loadAsset: fixedLoader('not valid json'),
        assetKey: 'fake_key',
      );
      final container = ProviderContainer(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
      );
      addTearDown(container.dispose);

      await expectLater(
        container.read(catalogProvider.future),
        throwsA(isA<CatalogParseException>()),
      );
    });

    test('does not duplicate loading logic: two reads share one repository call', () async {
      var callCount = 0;
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async {
          callCount++;
          return _validCatalogJson;
        },
        assetKey: 'fake_key',
      );
      final container = ProviderContainer(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
      );
      addTearDown(container.dispose);

      await container.read(catalogProvider.future);
      await container.read(catalogProvider.future);

      expect(callCount, 1);
    });

    test('against the real bundled asset, resolves without any override', () async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final catalog = await container.read(catalogProvider.future);

      expect(catalog.styles, isNotEmpty);
      expect(catalog.beers, isNotEmpty);
      expect(catalog.skus, isNotEmpty);
      expect(catalog.benchmarks, isNotEmpty);
    });
  });
}
