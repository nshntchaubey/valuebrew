import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// The current search query, as typed by the user. Empty by default.
final searchQueryProvider = StateProvider<String>((ref) => '');

/// The beers to display: every beer in [catalogProvider] whose name or
/// brewery contains [searchQueryProvider], case-insensitively, or every
/// beer if the query is empty (after trimming).
///
/// Wraps [catalogProvider]'s [AsyncValue] via [AsyncValue.whenData] so
/// loading/error states pass through unchanged — this provider only ever
/// adds filtering on top of an already-resolved catalog, it never loads or
/// parses anything itself.
final searchResultsProvider = Provider<AsyncValue<List<Beer>>>((ref) {
  final catalogAsync = ref.watch(catalogProvider);
  final query = ref.watch(searchQueryProvider);
  return catalogAsync.whenData((catalog) => _filterBeers(catalog.beers, query));
});

/// Filters [beers] to those whose name or brewery contains [query],
/// case-insensitively, after trimming [query]'s leading/trailing
/// whitespace. Returns [beers] unchanged if [query] is empty after
/// trimming.
List<Beer> _filterBeers(List<Beer> beers, String query) {
  final normalizedQuery = query.trim().toLowerCase();
  if (normalizedQuery.isEmpty) {
    return beers;
  }
  return beers.where((beer) {
    final name = beer.name.toLowerCase();
    final brewery = beer.brewery.toLowerCase();
    return name.contains(normalizedQuery) || brewery.contains(normalizedQuery);
  }).toList();
}
