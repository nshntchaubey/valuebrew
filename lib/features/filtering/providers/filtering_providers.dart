import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/services/filtering_engine.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// The app-wide currently active [FilterState].
///
/// This is the single source of truth for filtering across the app —
/// every screen showing a filtered beer list watches this same provider
/// (via [filteredHomeBeersProvider]/[filteredFavoriteBeersProvider]), and
/// changing it from any one screen is reflected on every other. Plain
/// [StateProvider] rather than a `StateNotifierProvider`, matching this
/// codebase's convention: filters have no persistence or other side
/// effect attached to changing them, so there's no behavior here beyond
/// holding and replacing a value — see [searchQueryProvider] for the same
/// reasoning applied to search text.
final filterStateProvider = StateProvider<FilterState>((ref) => FilterState.none);

/// Exposes the app's [FilteringEngine].
///
/// [FilteringEngine] is stateless and has no dependencies of its own, but
/// it's still read through a provider — never constructed inline in a
/// widget — for the same reason every other service in this app is:
/// consistency, and so a test can override it if it ever needs to.
final filteringEngineProvider = Provider<FilteringEngine>((ref) => const FilteringEngine());

/// [HomeScreen]'s beer list: [searchResultsProvider]'s results, narrowed
/// by [filterStateProvider] via [filteringEngineProvider].
///
/// Search and filters compose — search narrows by typed text first,
/// filtering narrows what's left by style/brewery/ABV/price/package/value
/// score. Recomputes only when [searchResultsProvider], [filterStateProvider],
/// or the catalog's SKUs actually change; [HomeScreen] never filters
/// anything itself.
final filteredHomeBeersProvider = Provider<AsyncValue<List<Beer>>>((ref) {
  final resultsAsync = ref.watch(searchResultsProvider);
  final filters = ref.watch(filterStateProvider);
  final engine = ref.watch(filteringEngineProvider);
  final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const <Sku>[];

  return resultsAsync.whenData((beers) => engine.apply(beers, filters, skus));
});

/// [FavoritesScreen]'s beer list: every favorited beer, narrowed by
/// [filterStateProvider] via [filteringEngineProvider] — the exact same
/// engine [filteredHomeBeersProvider] uses. Only the source collection
/// differs (favorited beers here, search results there); the filtering
/// logic itself is never duplicated.
final filteredFavoriteBeersProvider = Provider<AsyncValue<List<Beer>>>((ref) {
  final favoriteIds = ref.watch(favoriteBeerIdsProvider);
  final catalogAsync = ref.watch(catalogProvider);
  final filters = ref.watch(filterStateProvider);
  final engine = ref.watch(filteringEngineProvider);

  return catalogAsync.whenData((catalog) {
    final favoriteBeers = catalog.beers.where((beer) => favoriteIds.contains(beer.id)).toList();
    return engine.apply(favoriteBeers, filters, catalog.skus);
  });
});
