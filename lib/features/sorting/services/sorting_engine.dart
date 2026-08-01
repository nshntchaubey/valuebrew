import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/sorting/models/sort_option.dart';

/// Orders a list of [Beer]s by a [SortOption].
///
/// Pure Dart — no Flutter or Riverpod dependency — so it's testable with
/// plain in-memory lists and deterministic: the same [beers], [option],
/// and [skus] always produce the same result. Mirrors `FilteringEngine`'s
/// design exactly: a small, stateless executor that asks its argument
/// (here, [SortOption]; there, `FilterState`) what to do, rather than
/// containing sort-specific business rules itself.
///
/// ### Where this fits in the pipeline
/// This engine always runs on an already-filtered list — see
/// `sorting_providers.dart`, where `sortedHomeBeersProvider` and
/// `sortedFavoriteBeersProvider` both consume their corresponding
/// `filtered...BeersProvider` rather than a raw catalog or search result.
/// The pipeline is Search → Filtering → Sorting → UI, and this class has
/// no way to reverse that order — it only ever receives a list, never
/// fetches or filters one itself.
///
/// ### Complexity
/// [apply] builds two `Map<String, Sku?>` indices (`beerId` → best-value
/// SKU, `beerId` → cheapest SKU) once, in O(m) for `m` SKUs, then sorts
/// [beers] using those precomputed lookups — O(n log n) for `n` beers,
/// never O(n × m). Building both indices unconditionally, even though a
/// given [option] only ever reads one of them (or neither, for
/// [SortOption.nameAToZ]/[SortOption.breweryAToZ]), is a deliberate,
/// bounded tradeoff: it keeps this method simple and keeps [SortOption]
/// unaware of which map it needs, at the cost of one extra O(n) pass in
/// the cases that don't need it — negligible next to the O(n log n) sort
/// itself. If [option] preserves incoming order ([SortOption.relevance]),
/// [apply] returns [beers] unchanged without building anything at all.
class SortingEngine {
  const SortingEngine();

  /// Returns [beers] ordered by [option]. Returns [beers] unchanged if
  /// [option] preserves incoming order. Ties (including "no SKU data,
  /// sorts last" ties) are broken by [beers]' original order.
  List<Beer> apply(List<Beer> beers, SortOption option, List<Sku> skus) {
    if (option.preservesIncomingOrder) return beers;

    final bestSkuByBeerId = <String, Sku?>{
      for (final beer in beers) beer.id: bestSkuForBeer(skus, beer.id),
    };
    final cheapestSkuByBeerId = <String, Sku?>{
      for (final beer in beers) beer.id: cheapestSkuForBeer(skus, beer.id),
    };
    final keyByBeerId = <String, Comparable?>{
      for (final beer in beers) beer.id: option.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
    };

    final indexed = beers.asMap().entries.toList()
      ..sort((a, b) {
        final keyA = keyByBeerId[a.value.id];
        final keyB = keyByBeerId[b.value.id];
        if (keyA == null && keyB == null) return a.key.compareTo(b.key);
        if (keyA == null) return 1;
        if (keyB == null) return -1;
        final comparison = option.descending ? keyB.compareTo(keyA) : keyA.compareTo(keyB);
        if (comparison != 0) return comparison;
        return a.key.compareTo(b.key);
      });

    return [for (final entry in indexed) entry.value];
  }
}
