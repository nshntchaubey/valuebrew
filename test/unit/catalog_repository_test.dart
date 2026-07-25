import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:valuebrew/core/constants/app_constants.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/data/sources/catalog_local_cache.dart';
import 'package:valuebrew/data/sources/catalog_remote_source.dart';

/// A fake [CatalogRepository.loadAsset] that returns [contents] for any key.
Future<String> Function(String key) fixedLoader(String contents) {
  return (key) async => contents;
}

/// A fake [CatalogRepository.loadAsset] that always throws [error].
Future<String> Function(String key) failingLoader(Object error) {
  return (key) async => throw error;
}

/// A minimal, valid catalog JSON string at the given [version].
String _catalogJsonAtVersion(int version) => jsonEncode({
      'catalog_version': version,
      'generated_at': '2026-01-01T00:00:00Z',
      'styles': <dynamic>[],
      'beers': <dynamic>[],
      'skus': <dynamic>[],
      'benchmarks': <dynamic>[],
    });

/// A fake [CatalogLocalCache] with a controllable initial state and
/// write-tracking, for testing [CatalogRepository]'s cache handling
/// without touching real [SharedPreferences].
class _FakeCatalogLocalCache implements CatalogLocalCache {
  _FakeCatalogLocalCache({this.initial, this.readError});

  CachedCatalog? initial;
  Object? readError;
  bool writeWasCalled = false;
  String? writtenRawJson;
  int? writtenVersion;

  @override
  Future<CachedCatalog?> read() async {
    if (readError != null) throw readError!;
    return initial;
  }

  @override
  Future<void> write(String rawJson, int catalogVersion) async {
    writeWasCalled = true;
    writtenRawJson = rawJson;
    writtenVersion = catalogVersion;
    initial = CachedCatalog(rawJson: rawJson, catalogVersion: catalogVersion);
  }
}

/// A fake [CatalogRemoteSource] with a controllable response and
/// call-tracking, for testing [CatalogRepository]'s remote handling
/// without any real networking.
class _FakeCatalogRemoteSource implements CatalogRemoteSource {
  _FakeCatalogRemoteSource({this.result, this.checkError});

  RemoteCatalogCheck? result;
  Object? checkError;
  int? lastCheckedVersion;

  @override
  Future<RemoteCatalogCheck> checkForUpdate(int currentVersion) async {
    lastCheckedVersion = currentVersion;
    if (checkError != null) throw checkError!;
    return result ?? const RemoteCatalogCheck.noUpdate();
  }
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

  group('CatalogRepository bundled → cache → remote loading order', () {
    test(
      'bundled-only behaviour is unchanged when no cache or remote source is supplied',
      () async {
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 1);
      },
    );

    test('cache miss: falls through to the bundled asset', () async {
      final cache = _FakeCatalogLocalCache(initial: null);
      final repository = CatalogRepository(
        loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
        assetKey: 'assets/catalog.json',
        localCache: cache,
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 1);
    });

    test('cache hit: a newer cached catalog is preferred over the bundled asset', () async {
      final cache = _FakeCatalogLocalCache(
        initial: CachedCatalog(rawJson: _catalogJsonAtVersion(2), catalogVersion: 2),
      );
      final repository = CatalogRepository(
        loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
        assetKey: 'assets/catalog.json',
        localCache: cache,
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 2);
    });

    test('a cached catalog that is not newer than the bundled asset is ignored', () async {
      final cache = _FakeCatalogLocalCache(
        initial: CachedCatalog(rawJson: _catalogJsonAtVersion(1), catalogVersion: 1),
      );
      final repository = CatalogRepository(
        loadAsset: fixedLoader(_catalogJsonAtVersion(2)),
        assetKey: 'assets/catalog.json',
        localCache: cache,
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 2);
    });

    test('remote reports no update: the bundled/cache result is kept unchanged', () async {
      final remote = _FakeCatalogRemoteSource(result: const RemoteCatalogCheck.noUpdate());
      final repository = CatalogRepository(
        loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
        assetKey: 'assets/catalog.json',
        remoteSource: remote,
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 1);
      expect(remote.lastCheckedVersion, 1);
    });

    test(
      'remote reports an update: it is preferred and persisted to the cache',
      () async {
        final cache = _FakeCatalogLocalCache();
        final remote = _FakeCatalogRemoteSource(
          result: RemoteCatalogCheck.updateAvailable(_catalogJsonAtVersion(3)),
        );
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          localCache: cache,
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 3);
        expect(cache.writeWasCalled, isTrue);
        expect(cache.writtenVersion, 3);
      },
    );

    test(
      'dependency injection: a custom localCache and remoteSource are used instead '
      'of the defaults',
      () async {
        final cache = _FakeCatalogLocalCache(
          initial: CachedCatalog(rawJson: _catalogJsonAtVersion(5), catalogVersion: 5),
        );
        final remote = _FakeCatalogRemoteSource();
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          localCache: cache,
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        // Proves the injected fakes were actually used, not the defaults
        // (NoopCatalogLocalCache would never have produced version 5, and
        // the fake remote's call is directly observable).
        expect(catalog.catalogVersion, 5);
        expect(remote.lastCheckedVersion, 5);
      },
    );

    test(
      'fallback order: bundled → cache → remote, each preferred only if newer',
      () async {
        final cache = _FakeCatalogLocalCache(
          initial: CachedCatalog(rawJson: _catalogJsonAtVersion(2), catalogVersion: 2),
        );
        final remote = _FakeCatalogRemoteSource(
          result: RemoteCatalogCheck.updateAvailable(_catalogJsonAtVersion(3)),
        );
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          localCache: cache,
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        // Bundled (1) is superseded by cache (2), which is in turn
        // superseded by remote (3) — the remote source was consulted
        // using the cache-resolved version, not the original bundled one.
        expect(catalog.catalogVersion, 3);
        expect(remote.lastCheckedVersion, 2);
        expect(cache.writtenVersion, 3);
      },
    );

    test('a failure reading the cache is ignored, falling back to the bundled asset', () async {
      final cache = _FakeCatalogLocalCache(readError: Exception('cache read failed'));
      final repository = CatalogRepository(
        loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
        assetKey: 'assets/catalog.json',
        localCache: cache,
      );

      final catalog = await repository.loadCatalog();

      expect(catalog.catalogVersion, 1);
    });

    test(
      'a failure checking the remote source is ignored, falling back to the bundled asset',
      () async {
        final remote = _FakeCatalogRemoteSource(checkError: Exception('remote check failed'));
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 1);
      },
    );
  });

  group('CatalogRepository with the real HttpCatalogRemoteSource', () {
    test(
      'a successful HTTP fetch with a newer version is preferred over the bundled asset',
      () async {
        final remote = HttpCatalogRemoteSource(
          httpGet: (url) async => http.Response(_catalogJsonAtVersion(9), 200),
        );
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 9);
      },
    );

    test(
      'a timed-out HTTP fetch falls back to the bundled asset, with no exception',
      () async {
        final remote = HttpCatalogRemoteSource(
          timeout: const Duration(milliseconds: 10),
          httpGet: (url) async {
            await Future.delayed(const Duration(milliseconds: 100));
            return http.Response(_catalogJsonAtVersion(9), 200);
          },
        );
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 1);
      },
    );

    test(
      'an HTTP failure response falls back to the bundled asset, with no exception',
      () async {
        final remote = HttpCatalogRemoteSource(
          httpGet: (url) async => http.Response('Service Unavailable', 503),
        );
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 1);
      },
    );

    test(
      'a malformed remote JSON body falls back to the bundled asset, with no exception',
      () async {
        final remote = HttpCatalogRemoteSource(
          httpGet: (url) async => http.Response('{ not valid json', 200),
        );
        final repository = CatalogRepository(
          loadAsset: fixedLoader(_catalogJsonAtVersion(1)),
          assetKey: 'assets/catalog.json',
          remoteSource: remote,
        );

        final catalog = await repository.loadCatalog();

        expect(catalog.catalogVersion, 1);
      },
    );
  });
}
