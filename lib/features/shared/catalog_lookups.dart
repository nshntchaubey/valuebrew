import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/models/style.dart';

/// Resolves [styleId] to its [Style] within [catalog], or `null` if no
/// style with that id exists.
///
/// A beer's `styleId` is a plain reference, not an embedded [Style] — this
/// is the lookup that resolves it. Shared across [catalog]-derived screens
/// (Beer Detail, Compare) rather than duplicated per file.
Style? resolveStyle(Catalog catalog, String styleId) {
  for (final style in catalog.styles) {
    if (style.id == styleId) {
      return style;
    }
  }
  return null;
}

/// Returns every [Sku] in [catalog] belonging to the beer with [beerId].
///
/// A SKU's `beerId` is a plain reference, not an embedded beer object —
/// this is the lookup that resolves it. Shared across [catalog]-derived
/// screens (Beer Detail, Compare) rather than duplicated per file.
List<Sku> resolveSkus(Catalog catalog, String beerId) {
  return catalog.skus.where((sku) => sku.beerId == beerId).toList();
}

/// Returns the [Sku] with the highest `valueScore` among [skus] belonging
/// to the beer with [beerId], or `null` if it has none.
Sku? bestSkuForBeer(List<Sku> skus, String beerId) {
  Sku? best;
  for (final sku in skus) {
    if (sku.beerId != beerId) continue;
    if (best == null || sku.valueScore > best.valueScore) {
      best = sku;
    }
  }
  return best;
}
