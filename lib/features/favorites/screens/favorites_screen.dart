import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/filtering/widgets/active_filters_indicator.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/beer_list_tile.dart';
import 'package:valuebrew/features/sorting/providers/sorting_providers.dart';
import 'package:valuebrew/features/sorting/widgets/active_sort_indicator.dart';

/// Lists every beer the user has favorited, reusing the same row
/// (`buildBeerListTile`) `HomeScreen` uses — tapping one opens
/// [BeerDetailScreen], same as everywhere else in the app.
///
/// [favoriteBeerIdsProvider] only ever stores beer IDs; the actual [Beer]
/// data for each one is resolved from [catalogProvider]. If a favorited ID
/// no longer resolves to a beer in the current catalog (e.g. after a
/// catalog update removes it), it's simply skipped — this screen never
/// crashes over a favorite that's gone stale, it just shows one fewer row.
///
/// The visible list is [sortedFavoriteBeersProvider]'s output — the same
/// app-wide [filterStateProvider]/[FilteringEngine] and
/// [sortOptionProvider]/[SortingEngine] [HomeScreen] uses, applied to
/// favorited beers instead of search results. This screen has no
/// filter-editing or sort-editing UI of its own (only `HomeScreen` does);
/// it simply reflects whatever filter and sort are currently active,
/// since both are single, app-wide sources of truth, not per-screen
/// settings.
class FavoritesScreen extends ConsumerWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favoriteIds = ref.watch(favoriteBeerIdsProvider);
    final sortedAsync = ref.watch(sortedFavoriteBeersProvider);
    final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const [];

    return Scaffold(
      appBar: AppBar(title: const Text('Favorites')),
      body: Column(
        children: [
          const ActiveFiltersIndicator(),
          const ActiveSortIndicator(),
          Expanded(
            child: sortedAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stackTrace) => Center(
                child: Text('Failed to load catalog: $error'),
              ),
              data: (favoriteBeers) {
                if (favoriteIds.isEmpty) {
                  return const Center(
                    child: Padding(
                      padding: EdgeInsets.all(24),
                      child: Text(
                        'No favorite beers yet.\n\n'
                        'Tap the heart on any beer to save it.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  );
                }

                if (favoriteBeers.isEmpty) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text('No beers match your filters.'),
                          const SizedBox(height: 8),
                          TextButton(
                            onPressed: () => ref.read(filterStateProvider.notifier).state =
                                FilterState.none,
                            child: const Text('Clear filters'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return ListView.builder(
                  itemCount: favoriteBeers.length,
                  itemBuilder: (context, index) {
                    final beer = favoriteBeers[index];
                    return buildBeerListTile(context, beer, skus, isFavorite: true);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
