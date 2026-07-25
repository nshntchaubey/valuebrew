import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/core/constants/app_constants.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';

/// A fake [CatalogRepository.loadAsset] that returns [contents] for any key.
Future<String> Function(String key) fixedLoader(String contents) {
  return (key) async => contents;
}

/// A fake [CatalogRepository.loadAsset] that always throws [error].
Future<String> Function(String key) failingLoader(Object error) {
  return (key) async => throw error;
}

const _realisticCatalogJson = '''
{
  "catalog_version": 7,
  "generated_at": "2026-07-25T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
    { "id": "stout", "name": "Stout", "description": "Dark, roasted malt character" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "stout", "is_craft": true }
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
      "price_source": "karnataka_excise_mrp_2026",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 3.52,
      "value_score": 78,
      "value_verdict": "great_value"
    }
  ],
  "benchmarks": [
    { "style_id": "lager", "avg_cost_per_ml_alcohol": 4.10, "p25": 3.40, "p50": 3.95, "p75": 4.60, "sample_size": 42 }
  ]
}
''';

void main() {
  group('CatalogRepository', () {
    test('loadCatalog successfully loads and parses a valid catalog', () async {
      final json = jsonEncode({
        'catalog_version': 1,
        'generated_at': '2026-01-01T00:00:00Z',
        'styles': <dynamic>[],
        'beers': <dynamic>[],
        'skus': <dynamic>[],
        'benchmarks': <dynamic>[],
      });
      final repository = CatalogRepository(
        loadAsset: fixedLoader(json),
        assetKey: 'assets/catalog.json',
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 1);
      expect(catalog.styles, isEmpty);
    });

    test('loadCatalog parses a realistic multi-item catalog fixture', () async {
      final repository = CatalogRepository(
        loadAsset: fixedLoader(_realisticCatalogJson),
        assetKey: 'assets/catalog.json',
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 7);
      expect(catalog.styles, hasLength(2));
      expect(catalog.beers, hasLength(2));
      expect(catalog.skus, hasLength(1));
      expect(catalog.benchmarks, hasLength(1));
      expect(catalog.skus.single.id, 'kf_premium_650');
      expect(catalog.beers.first.name, 'Kingfisher Premium');
    });

    test('loadCatalog calls loadAsset with the configured assetKey', () async {
      String? receivedKey;
      final repository = CatalogRepository(
        loadAsset: (key) async {
          receivedKey = key;
          return _realisticCatalogJson;
        },
        assetKey: 'assets/catalog.json',
      );

      await repository.loadCatalog();

      expect(receivedKey, 'assets/catalog.json');
    });

    test('loadCatalog throws CatalogAssetLoadException when the asset fails to load', () async {
      final repository = CatalogRepository(
        loadAsset: failingLoader(Exception('Unable to load asset')),
        assetKey: 'assets/catalog.json',
      );

      expect(
        () => repository.loadCatalog(),
        throwsA(isA<CatalogAssetLoadException>()),
      );
    });

    test('loadCatalog throws CatalogParseException on malformed JSON', () async {
      final repository = CatalogRepository(
        loadAsset: fixedLoader('{ this is not valid json'),
        assetKey: 'assets/catalog.json',
      );

      expect(
        () => repository.loadCatalog(),
        throwsA(isA<CatalogParseException>()),
      );
    });

    test('loadCatalog throws CatalogParseException when the JSON is not an object', () async {
      final repository = CatalogRepository(
        loadAsset: fixedLoader(jsonEncode([1, 2, 3])),
        assetKey: 'assets/catalog.json',
      );

      expect(
        () => repository.loadCatalog(),
        throwsA(isA<CatalogParseException>()),
      );
    });

    test('loadCatalog throws CatalogParseException when a required field is missing', () async {
      final json = jsonEncode({
        // 'catalog_version' intentionally omitted.
        'generated_at': '2026-01-01T00:00:00Z',
        'styles': <dynamic>[],
        'beers': <dynamic>[],
        'skus': <dynamic>[],
        'benchmarks': <dynamic>[],
      });
      final repository = CatalogRepository(
        loadAsset: fixedLoader(json),
        assetKey: 'assets/catalog.json',
      );

      expect(
        () => repository.loadCatalog(),
        throwsA(isA<CatalogParseException>()),
      );
    });

    test('loadCatalog throws CatalogParseException for invalid nested model data', () async {
      final json = jsonEncode({
        'catalog_version': 1,
        'generated_at': '2026-01-01T00:00:00Z',
        'styles': [
          {'id': 'lager', 'name': 'Lager', 'description': 'Crisp'},
        ],
        'beers': <dynamic>[],
        'skus': [
          {
            'id': 'bad_sku',
            'beer_id': 'kf_premium',
            'size_ml': 650,
            // Not a recognized PackageType value.
            'package_type': 'keg',
            'abv': 4.8,
            'calories': 260,
            'price': 110,
            'price_last_checked': '2026-07-20',
            'price_source': 'test',
            'cost_per_litre': 169.2,
            'cost_per_ml_alcohol': 3.52,
            'value_score': 78,
            'value_verdict': 'great_value',
          },
        ],
        'benchmarks': <dynamic>[],
      });
      final repository = CatalogRepository(
        loadAsset: fixedLoader(json),
        assetKey: 'assets/catalog.json',
      );

      expect(
        () => repository.loadCatalog(),
        throwsA(isA<CatalogParseException>()),
      );
    });

    test('CatalogAssetLoadException and CatalogParseException messages include the asset key', () async {
      final loadFailure = CatalogRepository(
        loadAsset: failingLoader(Exception('boom')),
        assetKey: 'assets/catalog.json',
      );
      final parseFailure = CatalogRepository(
        loadAsset: fixedLoader('not json'),
        assetKey: 'assets/catalog.json',
      );

      try {
        await loadFailure.loadCatalog();
        fail('Expected a CatalogAssetLoadException');
      } on CatalogAssetLoadException catch (e) {
        expect(e.toString(), contains('assets/catalog.json'));
      }

      try {
        await parseFailure.loadCatalog();
        fail('Expected a CatalogParseException');
      } on CatalogParseException catch (e) {
        expect(e.toString(), contains('assets/catalog.json'));
      }
    });
  });

  group('CatalogRepository against the real bundled asset', () {
    TestWidgetsFlutterBinding.ensureInitialized();

    test(
      'loadCatalog loads the real catalog.json registered in pubspec.yaml, '
      'via the real AppConstants.catalogAssetKey and rootBundle.loadString',
      () async {
        final repository = CatalogRepository(
          loadAsset: rootBundle.loadString,
          assetKey: AppConstants.catalogAssetKey,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, greaterThan(0));
        expect(catalog.styles, isNotEmpty);
        expect(catalog.beers, isNotEmpty);
        expect(catalog.skus, isNotEmpty);
        expect(catalog.benchmarks, isNotEmpty);
      },
    );
  });
}
