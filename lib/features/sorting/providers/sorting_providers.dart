import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/sorting/models/sort_option.dart';
import 'package:valuebrew/features/sorting/services/sorting_engine.dart';

/// The app-wide currently selected [SortOption].
///
/// A single source of truth for sorting across the app, the same way
/// `filterStateProvider` is for filtering — every screen showing a sorted
/// beer list watches this same provider (via
/// [sortedHomeBeersProvider]/[sortedFavoriteBeersProvider]), and changing
/// it from Home is reflected on Favorites too. Plain [StateProvider]:
/// there's no persistence or other side effect attached to changing the
/// sort order (unlike, say, the selected recommendation profile), so
/// there's no behavior here beyond holding and replacing a value.
final sortOptionProvider = StateProvider<SortOption>((ref) => SortOption.relevance);

/// Exposes the app's [SortingEngine].
///
/// [SortingEngine] is stateless with no dependencies of its own, but it's
/// still read through a provider — never constructed inline in a widget —
/// for the same reason every other service in this app is: consistency,
/// and so a test can override it if it ever needs to.
final sortingEngineProvider = Provider<SortingEngine>((ref) => const SortingEngine());

/// [HomeScreen]'s beer list: [filteredHomeBeersProvider]'s results,
/// ordered by [sortOptionProvider] via [sortingEngineProvider].
///
/// Consuming the already-*filtered* provider (not `searchResultsProvider`
/// or the raw catalog directly) is what keeps the pipeline in order:
/// Search → Filtering → Sorting → UI. If filtering has already narrowed
/// the list to nothing, [SortingEngine.apply] simply receives and returns
/// an empty list — sorting never changes whether any beer is shown, only
/// the order of whatever filtering already decided to show.
final sortedHomeBeersProvider = Provider<AsyncValue<List<Beer>>>((ref) {
  final filteredAsync = ref.watch(filteredHomeBeersProvider);
  final sortOption = ref.watch(sortOptionProvider);
  final engine = ref.watch(sortingEngineProvider);
  final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const <Sku>[];

  return filteredAsync.whenData((beers) => engine.apply(beers, sortOption, skus));
});

/// [FavoritesScreen]'s beer list: [filteredFavoriteBeersProvider]'s
/// results, ordered by [sortOptionProvider] via the exact same
/// [SortingEngine] [sortedHomeBeersProvider] uses. Only the source
/// collection differs (favorited-and-filtered beers here, searched-and-
/// filtered beers there); the sorting logic itself is never duplicated.
final sortedFavoriteBeersProvider = Provider<AsyncValue<List<Beer>>>((ref) {
  final filteredAsync = ref.watch(filteredFavoriteBeersProvider);
  final sortOption = ref.watch(sortOptionProvider);
  final engine = ref.watch(sortingEngineProvider);
  final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const <Sku>[];

  return filteredAsync.whenData((beers) => engine.apply(beers, sortOption, skus));
});
