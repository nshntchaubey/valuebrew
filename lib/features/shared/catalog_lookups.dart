import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/data/models/style.dart';

/// Resolves [beerId] to its [Beer] within [catalog], or `null` if no beer
/// with that id exists.
///
/// A SKU's `beerId` is a plain reference, not an embedded [Beer] — this is
/// the lookup that resolves it.
Beer? resolveBeer(Catalog catalog, String beerId) {
  for (final beer in catalog.beers) {
    if (beer.id == beerId) {
      return beer;
    }
  }
  return null;
}

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

/// Returns the [Sku] with the lowest `price` among [skus] belonging to the
/// beer with [beerId], or `null` if it has none.
///
/// Distinct from [bestSkuForBeer] on purpose: `valueScore` and raw `price`
/// are different axes (`valueScore` is a style-relative percentile of
/// cost-per-ml-alcohol, not the sticker price) — a beer's cheapest SKU is
/// not necessarily its best-value one.
Sku? cheapestSkuForBeer(List<Sku> skus, String beerId) {
  Sku? cheapest;
  for (final sku in skus) {
    if (sku.beerId != beerId) continue;
    if (cheapest == null || sku.price < cheapest.price) {
      cheapest = sku;
    }
  }
  return cheapest;
}
