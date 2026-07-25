import 'dart:convert';

import 'package:valuebrew/data/models/catalog.dart';

/// Loads and parses a bundled catalog asset into a [Catalog].
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
class CatalogRepository {
  /// Loads the raw contents of the asset at the given key, e.g.
  /// `rootBundle.loadString` in production, or a fake in tests.
  final Future<String> Function(String key) loadAsset;

  /// The asset key [loadAsset] is called with, e.g. `"assets/catalog.json"`.
  final String assetKey;

  /// Creates a [CatalogRepository].
  const CatalogRepository({required this.loadAsset, required this.assetKey});

  /// Loads the bundled catalog asset and parses it into a [Catalog].
  ///
  /// This is the repository's single public entry point. It performs no
  /// caching, indexing, searching, or filtering — just loading and parsing.
  ///
  /// Throws [CatalogAssetLoadException] if the asset at [assetKey] cannot
  /// be loaded (e.g. missing or unreadable). Throws [CatalogParseException]
  /// if the asset loads successfully but its contents are not valid JSON,
  /// or do not match the catalog schema expected by [Catalog.fromJson].
  Future<Catalog> loadCatalog() async {
    final String raw;
    try {
      raw = await loadAsset(assetKey);
    } catch (error) {
      throw CatalogAssetLoadException(
        'Failed to load catalog asset "$assetKey": $error',
      );
    }

    final Object? decoded;
    try {
      decoded = jsonDecode(raw);
    } on FormatException catch (error) {
      throw CatalogParseException(
        'Catalog asset "$assetKey" is not valid JSON: $error',
      );
    }

    if (decoded is! Map<String, dynamic>) {
      throw CatalogParseException(
        'Catalog asset "$assetKey" did not decode to a JSON object.',
      );
    }

    try {
      return Catalog.fromJson(decoded);
    } catch (error) {
      throw CatalogParseException(
        'Catalog asset "$assetKey" does not match the expected catalog '
        'schema: $error',
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

/// Thrown by [CatalogRepository.loadCatalog] when the bundled catalog asset
/// was loaded successfully but its contents are not valid JSON, or do not
/// match the catalog schema (missing/invalid fields, an unrecognized enum
/// value, etc.).
class CatalogParseException implements Exception {
  /// Human-readable description of the failure.
  final String message;

  /// Creates a [CatalogParseException].
  const CatalogParseException(this.message);

  @override
  String toString() => 'CatalogParseException: $message';
}
