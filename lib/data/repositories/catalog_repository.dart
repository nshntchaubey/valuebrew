import 'dart:convert';

import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/sources/catalog_local_cache.dart';
import 'package:valuebrew/data/sources/catalog_remote_source.dart';

/// Loads and parses the catalog from, in order: a. the bundled asset,
/// b. a local cache (if present and newer), c. a remote source (if it
/// reports something newer).
///
/// [loadAsset] and [assetKey] are both supplied by the caller rather than
/// hardcoded here. The V1 catalog build pipeline (which produces the real
/// `catalog.json`) and the Flutter `pubspec.yaml` asset declaration it will
/// be bundled under don't exist yet, so this repository doesn't guess at
/// either — the real asset key belongs in `core/constants` once it's known,
/// and the real loader (`rootBundle.loadString`) belongs to whatever wires
/// this repository into the app (a future provider). This also keeps
/// [CatalogRepository] free of any Flutter SDK import, so it can be unit
/// tested without a widget test binding.
///
/// [localCache] and [remoteSource] default to no-op implementations
/// ([NoopCatalogLocalCache], [StubCatalogRemoteSource]) — supplying
/// neither reproduces exactly the bundled-asset-only behaviour this
/// repository had before those steps existed, which is what keeps every
/// existing call site (and every existing test) working unchanged.
class CatalogRepository {
  /// Loads the raw contents of the asset at the given key, e.g.
  /// `rootBundle.loadString` in production, or a fake in tests.
  final Future<String> Function(String key) loadAsset;

  /// The asset key [loadAsset] is called with, e.g. `"assets/catalog.json"`.
  final String assetKey;

  /// Where a previously-fetched remote catalog is cached, if any.
  final CatalogLocalCache localCache;

  /// Where a newer catalog than what's already loaded would come from.
  final CatalogRemoteSource remoteSource;

  /// Creates a [CatalogRepository].
  const CatalogRepository({
    required this.loadAsset,
    required this.assetKey,
    this.localCache = const NoopCatalogLocalCache(),
    this.remoteSource = const StubCatalogRemoteSource(),
  });

  /// Loads the catalog and parses it into a [Catalog].
  ///
  /// This is the repository's single public entry point. It performs no
  /// indexing, searching, or filtering — just loading and parsing, plus
  /// preferring a newer cached or remote catalog over the bundled one when
  /// one is available.
  ///
  /// Throws [CatalogAssetLoadException] if the bundled asset at [assetKey]
  /// cannot be loaded (e.g. missing or unreadable) — this is the only
  /// failure that actually stops loading; a failure reading the cache or
  /// checking the remote source is caught and silently ignored, per the
  /// V1 technical architecture's documented fallback behaviour. Throws
  /// [CatalogParseException] if the bundled asset loads successfully but
  /// its contents are not valid JSON, or do not match the catalog schema
  /// expected by [Catalog.fromJson].
  Future<Catalog> loadCatalog() async {
    // a. Bundled asset — the guaranteed-available baseline. A failure here
    // is the only one that actually stops loading.
    final String bundledRaw;
    try {
      bundledRaw = await loadAsset(assetKey);
    } catch (error) {
      throw CatalogAssetLoadException(
        'Failed to load catalog asset "$assetKey": $error',
      );
    }
    var catalog = _parseCatalog(bundledRaw, source: 'Catalog asset "$assetKey"');

    // b. Local cache, if present and newer than what we already have.
    // Any failure here is treated the same as "no cache" — the cache is a
    // best-effort layer, never a reason to fail loading.
    try {
      final cached = await localCache.read();
      if (cached != null && cached.catalogVersion > catalog.catalogVersion) {
        catalog = _parseCatalog(cached.rawJson, source: 'Cached catalog');
      }
    } catch (_) {
      // Ignored — fall through with whatever we already have.
    }

    // c. Remote source, if it reports something newer. Same fallback
    // philosophy as the cache: any failure here is ignored.
    try {
      final remoteCheck = await remoteSource.checkForUpdate(catalog.catalogVersion);
      if (remoteCheck.hasUpdate) {
        final remoteRaw = remoteCheck.rawJson!;
        catalog = _parseCatalog(remoteRaw, source: 'Remote catalog');
        await localCache.write(remoteRaw, catalog.catalogVersion);
      }
    } catch (_) {
      // Ignored — fall through with whatever we already have.
    }

    return catalog;
  }

  /// Parses [raw] into a [Catalog]. The single place JSON decoding and
  /// schema validation happen, regardless of which of the three sources
  /// [raw] came from.
  Catalog _parseCatalog(String raw, {required String source}) {
    final Object? decoded;
    try {
      decoded = jsonDecode(raw);
    } on FormatException catch (error) {
      throw CatalogParseException('$source is not valid JSON: $error');
    }

    if (decoded is! Map<String, dynamic>) {
      throw CatalogParseException('$source did not decode to a JSON object.');
    }

    try {
      return Catalog.fromJson(decoded);
    } catch (error) {
      throw CatalogParseException(
        '$source does not match the expected catalog schema: $error',
      );
    }
  }
}

/// Thrown by [CatalogRepository.loadCatalog] when the bundled catalog asset
/// itself cannot be loaded, as distinct from being loaded but unparseable —
/// see [CatalogParseException].
class CatalogAssetLoadException implements Exception {
  /// Human-readable description of the failure.
  final String message;

  /// Creates a [CatalogAssetLoadException].
  const CatalogAssetLoadException(this.message);

  @override
  String toString() => 'CatalogAssetLoadException: $message';
}

/// Thrown by [CatalogRepository.loadCatalog] when a source (bundled asset,
/// cache, or remote) was read successfully but its contents are not valid
/// JSON, or do not match the catalog schema (missing/invalid fields, an
/// unrecognized enum value, etc.).
class CatalogParseException implements Exception {
  /// Human-readable description of the failure.
  final String message;

  /// Creates a [CatalogParseException].
  const CatalogParseException(this.message);

  @override
  String toString() => 'CatalogParseException: $message';
}
