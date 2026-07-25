import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:valuebrew/core/constants/app_constants.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/data/sources/catalog_local_cache.dart';

/// Exposes the app's production [CatalogRepository].
///
/// Construction happens here, in the provider layer, not inside
/// [CatalogRepository] itself — the repository's dependency-injected
/// constructor (`loadAsset`, `assetKey`, `localCache`, `remoteSource`)
/// stays generic and testable in isolation. This is the one place that
/// wires it to the real bundled asset ([rootBundle.loadString] and
/// [AppConstants.catalogAssetKey]) and a real local cache
/// ([SharedPreferencesCatalogLocalCache]). `remoteSource` is left at its
/// default ([StubCatalogRemoteSource]) — this milestone builds only the
/// infrastructure a real remote source will plug into later.
///
/// Override this provider in tests to substitute a fake repository without
/// touching the real Flutter asset bundle or shared preferences.
final catalogRepositoryProvider = Provider<CatalogRepository>((ref) {
  return CatalogRepository(
    loadAsset: rootBundle.loadString,
    assetKey: AppConstants.catalogAssetKey,
    localCache: const SharedPreferencesCatalogLocalCache(),
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
