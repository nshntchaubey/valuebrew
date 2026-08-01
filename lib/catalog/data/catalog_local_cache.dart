import 'package:shared_preferences/shared_preferences.dart';

/// A cached copy of the catalog, as last written by
/// [CatalogLocalCache.write].
class CachedCatalog {
  /// The raw catalog JSON, exactly as it will be parsed by
  /// `Catalog.fromJson`.
  final String rawJson;

  /// The `catalog_version` of [rawJson], used to decide whether this cache
  /// entry is newer than whatever else has been loaded.
  final int catalogVersion;

  /// Creates an immutable [CachedCatalog].
  const CachedCatalog({required this.rawJson, required this.catalogVersion});
}

/// Reads and writes a locally cached copy of the catalog.
///
/// This is the "b. cached catalog" step in `CatalogRepository`'s bundled
/// → cache → remote loading order — a previously-fetched remote catalog
/// is kept here so it doesn't need to be re-fetched on every launch.
abstract class CatalogLocalCache {
  /// Returns the currently cached catalog, or `null` if none is cached.
  Future<CachedCatalog?> read();

  /// Persists [rawJson] (at [catalogVersion]) as the current cache,
  /// replacing whatever was cached before.
  Future<void> write(String rawJson, int catalogVersion);
}

/// A [CatalogLocalCache] that never has anything cached, and discards
/// every write.
///
/// This is `CatalogRepository`'s default when no cache is supplied — it
/// keeps the repository's default behaviour identical to not having a
/// cache layer at all, which is what lets every existing call site (and
/// every existing test) keep working unchanged.
class NoopCatalogLocalCache implements CatalogLocalCache {
  const NoopCatalogLocalCache();

  @override
  Future<CachedCatalog?> read() async => null;

  @override
  Future<void> write(String rawJson, int catalogVersion) async {}
}

/// A [CatalogLocalCache] backed by [SharedPreferences], using the storage
/// keys the V1 technical architecture names for this purpose
/// (`catalog_json`, `catalog_version`).
class SharedPreferencesCatalogLocalCache implements CatalogLocalCache {
  const SharedPreferencesCatalogLocalCache();

  static const _jsonKey = 'catalog_json';
  static const _versionKey = 'catalog_version';

  @override
  Future<CachedCatalog?> read() async {
    final prefs = await SharedPreferences.getInstance();
    final rawJson = prefs.getString(_jsonKey);
    final version = prefs.getInt(_versionKey);
    if (rawJson == null || version == null) {
      return null;
    }
    return CachedCatalog(rawJson: rawJson, catalogVersion: version);
  }

  @override
  Future<void> write(String rawJson, int catalogVersion) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_jsonKey, rawJson);
    await prefs.setInt(_versionKey, catalogVersion);
  }
}
