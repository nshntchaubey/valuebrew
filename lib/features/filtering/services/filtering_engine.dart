import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';

/// Narrows a list of [Beer]s down to those matching every active filter in
/// a [FilterState].
///
/// Pure Dart — no Flutter or Riverpod dependency, so it's testable with
/// plain in-memory lists and deterministic: the same [beers], [filters],
/// and [skus] always produce the same result.
///
/// ### Why [apply] also takes [skus]
/// [FilterState.styleId] and [FilterState.brewery] describe a [Beer]
/// directly, but [FilterState.abvRange], [FilterState.priceRange],
/// [FilterState.packageType], and [FilterState.minValueScore] all describe
/// a [Sku] — ABV, price, package type, and value score are pack-size-level
/// attributes, not beer-level ones (the same beer can have a 650ml bottle
/// and a 330ml can at different prices and value scores). A beer-only
/// `apply(List<Beer>, FilterState)` signature can't express those filters
/// at all, so this engine takes the catalog's SKUs alongside its beers.
///
/// ### How a beer is matched against SKU-level filters
/// A beer matches the active SKU-level filters if **at least one of its
/// own SKUs** satisfies all of them *together* — not if different SKUs
/// each satisfy a different filter. A user filtering "ABV ≤ 6% AND Price ≤
/// ₹180" is asking for one purchasable option meeting both conditions, not
/// for a beer that merely has some cheap SKU and some low-ABV SKU. A beer
/// with no SKUs at all can never satisfy an active SKU-level filter, since
/// there is no SKU to check.
///
/// ### Complexity
/// [apply] indexes [skus] by `beerId` once (O(m) for `m` SKUs), then
/// checks each beer against that index (O(n) for `n` beers, each SKU-level
/// check itself bounded by that beer's own SKU count) — O(n + m) overall,
/// not O(n × m). If [filters] has nothing active, [apply] returns [beers]
/// unchanged without touching [skus] or allocating anything.
class FilteringEngine {
  const FilteringEngine();

  /// Returns every beer in [beers] that matches every active filter in
  /// [filters], preserving [beers]' original order. Returns [beers]
  /// unchanged if [filters] has nothing active.
  List<Beer> apply(List<Beer> beers, FilterState filters, List<Sku> skus) {
    if (!filters.isActive) return beers;

    final skusByBeerId = <String, List<Sku>>{};
    for (final sku in skus) {
      skusByBeerId.putIfAbsent(sku.beerId, () => []).add(sku);
    }

    return beers.where((beer) {
      return _matchesBeer(beer, filters) &&
          _matchesSkuLevelFilters(skusByBeerId[beer.id] ?? const [], filters);
    }).toList();
  }

  /// Checks [filters]' beer-level conditions ([FilterState.styleId],
  /// [FilterState.brewery]) against [beer] — checked first, and cheaply,
  /// so a beer that fails on style or brewery never needs its SKUs looked
  /// up at all.
  bool _matchesBeer(Beer beer, FilterState filters) {
    if (filters.styleId != null && beer.styleId != filters.styleId) return false;
    if (filters.brewery != null && beer.brewery != filters.brewery) return false;
    return true;
  }

  /// Checks whether any SKU in [beerSkus] satisfies every active SKU-level
  /// filter in [filters] at once. Always `true` if no SKU-level filter is
  /// active, regardless of [beerSkus] — including when it's empty.
  bool _matchesSkuLevelFilters(List<Sku> beerSkus, FilterState filters) {
    if (!filters.hasSkuLevelFilters) return true;
    return beerSkus.any((sku) => _matchesSku(sku, filters));
  }

  bool _matchesSku(Sku sku, FilterState filters) {
    if (filters.abvRange != null && !filters.abvRange!.contains(sku.abv)) return false;
    if (filters.priceRange != null && !filters.priceRange!.contains(sku.price)) return false;
    if (filters.packageType != null && sku.packageType != filters.packageType) return false;
    if (filters.minValueScore != null && sku.valueScore < filters.minValueScore!) return false;
    return true;
  }
}
