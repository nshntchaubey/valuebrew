import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/sku.dart';

/// A catalog sort order, strongly typed rather than a string, an integer
/// ID, or a scattered `switch` in every screen that needs to sort.
///
/// Each value encapsulates both its user-facing [displayLabel] and its own
/// [sortKey]/[descending] — what a beer should be sorted by, and in which
/// direction. `SortingEngine` (see `services/sorting_engine.dart`) is the
/// only thing that ever calls into these; it holds no sort-specific
/// business rules of its own, the same relationship `RecommendationEngine`
/// has with `RecommendationPolicy`.
enum SortOption {
  /// The order the list already arrived in — search's own relevance
  /// ranking, or catalog order if there's no search query. The default.
  relevance,

  /// Descending by each beer's best-value SKU's `valueScore` (see
  /// [bestSkuForBeer]) — the same "best matching SKU" concept
  /// `RecommendationEngine` and `FilteringEngine` already use, not a new
  /// definition of "value."
  bestValue,

  /// Ascending by each beer's cheapest SKU's `price` (see
  /// [cheapestSkuForBeer]).
  priceLowToHigh,

  /// Descending by each beer's cheapest SKU's `price`.
  priceHighToLow,

  /// Ascending by each beer's representative SKU's `abv` — the same
  /// best-value SKU [bestValue] uses, for consistency (see
  /// [bestSkuForBeer]).
  abvLowToHigh,

  /// Descending by each beer's representative SKU's `abv`.
  abvHighToLow,

  /// Ascending, alphabetically, by [Beer.name] (case-insensitive).
  nameAToZ,

  /// Ascending, alphabetically, by [Beer.brewery] (case-insensitive).
  breweryAToZ;

  /// Short, user-facing label for a sort selector.
  String get displayLabel {
    switch (this) {
      case SortOption.relevance:
        return 'Relevance';
      case SortOption.bestValue:
        return 'Best Value';
      case SortOption.priceLowToHigh:
        return 'Price (Low to High)';
      case SortOption.priceHighToLow:
        return 'Price (High to Low)';
      case SortOption.abvLowToHigh:
        return 'ABV (Low to High)';
      case SortOption.abvHighToLow:
        return 'ABV (High to Low)';
      case SortOption.nameAToZ:
        return 'Name (A to Z)';
      case SortOption.breweryAToZ:
        return 'Brewery (A to Z)';
    }
  }

  /// Whether this option preserves whatever order the list already
  /// arrived in. Only [relevance] — `SortingEngine` short-circuits on
  /// this rather than computing a sort key for every beer, so [sortKey]
  /// and [descending] are never actually called for it.
  bool get preservesIncomingOrder => this == SortOption.relevance;

  /// Whether this option sorts highest/most-expensive first. Ignored for
  /// [relevance].
  bool get descending {
    switch (this) {
      case SortOption.bestValue:
      case SortOption.priceHighToLow:
      case SortOption.abvHighToLow:
        return true;
      case SortOption.relevance:
      case SortOption.priceLowToHigh:
      case SortOption.abvLowToHigh:
      case SortOption.nameAToZ:
      case SortOption.breweryAToZ:
        return false;
    }
  }

  /// The value [beer] should be sorted by under this option, or `null` if
  /// [beer] has no SKU data this option can sort by (e.g. no SKUs at
  /// all) — `SortingEngine` always sorts a `null` key last, regardless of
  /// [descending].
  ///
  /// [bestSkuByBeerId] and [cheapestSkuByBeerId] are precomputed once by
  /// `SortingEngine` for the whole list being sorted, not recomputed per
  /// comparison.
  Comparable? sortKey(
    Beer beer,
    Map<String, Sku?> bestSkuByBeerId,
    Map<String, Sku?> cheapestSkuByBeerId,
  ) {
    switch (this) {
      case SortOption.relevance:
        return null; // Unreachable — see preservesIncomingOrder.
      case SortOption.bestValue:
        return bestSkuByBeerId[beer.id]?.valueScore;
      case SortOption.priceLowToHigh:
      case SortOption.priceHighToLow:
        return cheapestSkuByBeerId[beer.id]?.price;
      case SortOption.abvLowToHigh:
      case SortOption.abvHighToLow:
        return bestSkuByBeerId[beer.id]?.abv;
      case SortOption.nameAToZ:
        return beer.name.toLowerCase();
      case SortOption.breweryAToZ:
        return beer.brewery.toLowerCase();
    }
  }
}
