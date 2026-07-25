/// App-wide constant values — asset keys, cache keys, thresholds, and
/// similar configuration that shouldn't be hardcoded inline at call sites.
class AppConstants {
  const AppConstants._();

  /// Asset key of the bundled catalog JSON, as declared under
  /// `flutter: assets:` in `pubspec.yaml`.
  static const String catalogAssetKey = 'catalog/catalog.json';

  /// Where the remote catalog JSON is fetched from — a jsDelivr CDN mirror
  /// of this repo's own `catalog/catalog.json`, per the V1 technical
  /// architecture's Remote Catalog Update Mechanism (section 7). Assumes
  /// the GitHub repo is public; jsDelivr's `/gh/` CDN only mirrors public
  /// repos.
  static const String remoteCatalogUrl =
      'https://cdn.jsdelivr.net/gh/nshntchaubey/valuebrew@main/catalog/catalog.json';

  /// How long a remote catalog fetch is allowed to take before it's treated
  /// as a failure and the app falls back to whatever it already has. 4s per
  /// the "short timeout" the technical architecture calls for.
  static const Duration remoteFetchTimeout = Duration(seconds: 4);
}
