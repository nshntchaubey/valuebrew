/// App-wide constant values — asset keys, cache keys, thresholds, and
/// similar configuration that shouldn't be hardcoded inline at call sites.
///
/// Only [catalogAssetKey] is defined so far. Other constants named in the
/// V1 technical architecture for this file (the CDN catalog URL, cache
/// keys) belong here too, once the milestones that need them are built.
class AppConstants {
  const AppConstants._();

  /// Asset key of the bundled catalog JSON, as declared under
  /// `flutter: assets:` in `pubspec.yaml`.
  static const String catalogAssetKey = 'catalog/catalog.json';
}
