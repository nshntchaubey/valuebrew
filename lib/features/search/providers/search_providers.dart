import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/utils/fuzzy_match.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// The current search query, as typed by the user. Empty by default.
final searchQueryProvider = StateProvider<String>((ref) => '');

/// The beers to display: every beer in [catalogProvider] whose name or
/// brewery fuzzy-matches [searchQueryProvider] (see [scoreMatch]), ranked
/// best-match-first, or every beer in catalog order if the query is empty
/// (after trimming).
///
/// Wraps [catalogProvider]'s [AsyncValue] via [AsyncValue.whenData] so
/// loading/error states pass through unchanged — this provider only ever
/// adds filtering/ranking on top of an already-resolved catalog, it never
/// loads or parses anything itself.
final searchResultsProvider = Provider<AsyncValue<List<Beer>>>((ref) {
  final catalogAsync = ref.watch(catalogProvider);
  final query = ref.watch(searchQueryProvider);
  return catalogAsync.whenData((catalog) => _filterBeers(catalog.beers, query));
});

/// Filters [beers] to those whose name or brewery fuzzy-matches [query]
/// (see [scoreMatch] — this covers exact, prefix, substring, and
/// typo-tolerant matches), ranked by whichever of the two fields scored
/// higher, descending. Returns [beers] unchanged, in catalog order, if
/// [query] is empty after trimming — an empty query isn't "ranked", it's
/// "everything, as-is".
///
/// [scoreMatch] is checked against [Beer.name] and [Beer.brewery]
/// separately, and the higher of the two is each beer's score — never
/// against the two fields concatenated. That distinction matters: a query
/// like "Premium United" might look like it spans a beer's name
/// ("Kingfisher Premium") and brewery ("United Breweries"), but since
/// neither field alone matches it, that beer is correctly excluded.
///
/// Sorting on `(score, originalIndex)` pairs, rather than relying on
/// [List.sort]'s own stability, is what guarantees deterministic
/// tie-breaking regardless of the underlying sort algorithm — the same
/// pattern used by [HomeScreen]'s and [BeerDetailScreen]'s sorting.
List<Beer> _filterBeers(List<Beer> beers, String query) {
  final normalizedQuery = query.trim().toLowerCase();
  if (normalizedQuery.isEmpty) {
    return beers;
  }

  final scoreByBeerId = <String, int>{
    for (final beer in beers)
      beer.id: [
        scoreMatch(normalizedQuery, beer.name),
        scoreMatch(normalizedQuery, beer.brewery),
      ].reduce((a, b) => a > b ? a : b),
  };

  final matches = beers.where((beer) => scoreByBeerId[beer.id]! > 0).toList();

  final indexed = matches.asMap().entries.toList()
    ..sort((a, b) {
      final scoreComparison =
          scoreByBeerId[b.value.id]!.compareTo(scoreByBeerId[a.value.id]!);
      if (scoreComparison != 0) return scoreComparison;
      return a.key.compareTo(b.key);
    });

  return [for (final entry in indexed) entry.value];
}
