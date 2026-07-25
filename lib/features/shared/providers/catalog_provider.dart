import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:valuebrew/core/constants/app_constants.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/data/sources/catalog_local_cache.dart';
import 'package:valuebrew/data/sources/catalog_remote_source.dart';

/// Exposes the app's production [CatalogRepository].
///
/// Construction happens here, in the provider layer, not inside
/// [CatalogRepository] itself — the repository's dependency-injected
/// constructor (`loadAsset`, `assetKey`, `localCache`, `remoteSource`)
/// stays generic and testable in isolation. This is the one place that
/// wires it to the real bundled asset ([rootBundle.loadString] and
/// [AppConstants.catalogAssetKey]), a real local cache
/// ([SharedPreferencesCatalogLocalCache]), and the real remote source
/// ([HttpCatalogRemoteSource], fetching [AppConstants.remoteCatalogUrl]).
///
/// Override this provider in tests to substitute a fake repository without
/// touching the real Flutter asset bundle, shared preferences, or network.
final catalogRepositoryProvider = Provider<CatalogRepository>((ref) {
  return CatalogRepository(
    loadAsset: rootBundle.loadString,
    assetKey: AppConstants.catalogAssetKey,
    localCache: const SharedPreferencesCatalogLocalCache(),
    remoteSource: HttpCatalogRemoteSource(),
  );
});

/// Asynchronously loads the app-wide [Catalog].
///
/// This is the single source of truth for the parsed catalog the rest of
/// the app reads from. It composes [catalogRepositoryProvider] — it does
/// not duplicate or reimplement any loading or parsing logic itself.
final catalogProvider = FutureProvider<Catalog>((ref) {
  final repository = ref.watch(catalogRepositoryProvider);
  return repository.loadCatalog();
});
