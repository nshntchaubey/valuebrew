import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/catalog/domain/style.dart';

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

/// Resolves [skuId] to its [Sku] within [catalog], or `null` if no SKU
/// with that id exists.
Sku? resolveSku(Catalog catalog, String skuId) {
  for (final sku in catalog.skus) {
    if (sku.id == skuId) {
      return sku;
    }
  }
  return null;
}

/// Resolves [styleId] to its [Benchmark] within [catalog], or `null` if no
/// benchmark for that style exists.
///
/// A style's benchmark is Important-Soon-After, not Core V1 — its absence
/// is expected, not an error.
Benchmark? resolveBenchmark(Catalog catalog, String styleId) {
  for (final benchmark in catalog.benchmarks) {
    if (benchmark.styleId == styleId) {
      return benchmark;
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
