/// The result of checking a [CatalogRemoteSource] for a newer catalog.
class RemoteCatalogCheck {
  /// Whether a newer catalog than the one checked against is available.
  final bool hasUpdate;

  /// The newer catalog's raw JSON, if [hasUpdate] is `true`; otherwise
  /// `null`.
  final String? rawJson;

  /// No newer catalog is available.
  const RemoteCatalogCheck.noUpdate() : hasUpdate = false, rawJson = null;

  /// A newer catalog, [rawJson], is available.
  const RemoteCatalogCheck.updateAvailable(this.rawJson) : hasUpdate = true;
}

/// Checks for a catalog newer than [currentVersion].
///
/// This is the "c. remote catalog" step in `CatalogRepository`'s bundled
/// → cache → remote loading order — see the V1 technical architecture's
/// remote catalog update mechanism for the documented design this
/// prepares for (a background fetch from a CDN-hosted `catalog.json`,
/// compared by `catalog_version`).
abstract class CatalogRemoteSource {
  /// Returns whether a catalog newer than [currentVersion] is available,
  /// and its contents if so.
  Future<RemoteCatalogCheck> checkForUpdate(int currentVersion);
}

/// A [CatalogRemoteSource] that never reports an update.
///
/// This milestone builds only the interface real remote checking will
/// plug into later — there is no HTTP, no CDN integration, and no
/// networking of any kind here, all explicitly out of scope for this
/// milestone. See the Future Remote Updates notes in this milestone's
/// report for what a real implementation would add.
class StubCatalogRemoteSource implements CatalogRemoteSource {
  const StubCatalogRemoteSource();

  @override
  Future<RemoteCatalogCheck> checkForUpdate(int currentVersion) async {
    return const RemoteCatalogCheck.noUpdate();
  }
}
