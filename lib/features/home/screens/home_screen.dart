import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/compare/screens/compare_screen.dart';
import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/favorites/screens/favorites_screen.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/filtering/widgets/active_filters_indicator.dart';
import 'package:valuebrew/features/filtering/widgets/filter_bottom_sheet.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/beer_list_tile.dart';
import 'package:valuebrew/features/shared/widgets/empty_state_view.dart';
import 'package:valuebrew/features/shared/widgets/error_state_view.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_list.dart';
import 'package:valuebrew/features/sorting/providers/sorting_providers.dart';
import 'package:valuebrew/features/sorting/widgets/active_sort_indicator.dart';
import 'package:valuebrew/features/sorting/widgets/sort_bottom_sheet.dart';

/// The app's entry-point screen: a search field, a filter action, a sort
/// action, and a list of matching beers from the loaded catalog, each
/// showing its best available value. Tapping a beer navigates to its
/// [BeerDetailScreen].
///
/// The visible list is [sortedHomeBeersProvider]'s output — search text,
/// active filters (via [FilteringEngine]), and the selected sort order
/// (via [SortingEngine]) all narrow and order it before this screen ever
/// sees it. This screen makes no filtering or sorting decision itself; it
/// only resolves and renders. No custom beer-card presentation belongs
/// here yet; that's a later milestone.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final resultsAsync = ref.watch(sortedHomeBeersProvider);
    final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const <Sku>[];
    final favoriteIds = ref.watch(favoriteBeerIdsProvider);
    final filters = ref.watch(filterStateProvider);
    final sortOption = ref.watch(sortOptionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ValueBrew'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            tooltip: 'Filter beers',
            onPressed: () {
              showModalBottomSheet(
                context: context,
                isScrollControlled: true,
                builder: (context) => const FilterBottomSheet(),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.sort),
            tooltip: 'Sort beers',
            onPressed: () {
              showModalBottomSheet(
                context: context,
                isScrollControlled: true,
                builder: (context) => const SortBottomSheet(),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.favorite),
            tooltip: 'Favorites',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const FavoritesScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.compare_arrows),
            tooltip: 'Compare beers',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CompareScreen()),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search by beer or brewery',
                prefixIcon: Icon(Icons.search),
              ),
              onChanged: (value) =>
                  ref.read(searchQueryProvider.notifier).state = value,
            ),
          ),
          const ActiveFiltersIndicator(),
          const ActiveSortIndicator(),
          const SizedBox(height: 8),
          Expanded(
            child: resultsAsync.when(
              loading: () => const BeerListSkeleton(),
              error: (error, stackTrace) => ErrorStateView(
                message: "Couldn't load the beer catalog.",
                onRetry: () => ref.invalidate(catalogProvider),
              ),
              data: (beers) {
                Widget content;

                if (beers.isEmpty && filters.isActive) {
                  content = EmptyStateView(
                    icon: Icons.filter_alt_off_outlined,
                    title: 'No beers match your filters',
                    message: 'Try adjusting or clearing your filters.',
                    action: TextButton(
                      onPressed: () =>
                          ref.read(filterStateProvider.notifier).state = FilterState.none,
                      child: const Text('Clear filters'),
                    ),
                  );
                } else if (beers.isEmpty) {
                  content = const EmptyStateView(
                    icon: Icons.search_off,
                    title: 'No beers found',
                    message: 'Try a different search term.',
                  );
                } else {
                  content = ListView.builder(
                    itemCount: beers.length,
                    itemBuilder: (context, index) {
                      final beer = beers[index];
                      return buildBeerListTile(
                        context,
                        beer,
                        skus,
                        isFavorite: favoriteIds.contains(beer.id),
                      );
                    },
                  );
                }

                // A subtle cross-fade whenever the filter or sort choice
                // changes the list, keyed on both so unrelated rebuilds
                // (e.g. a favorite toggled elsewhere) don't retrigger it.
                return AnimatedSwitcher(
                  duration: const Duration(milliseconds: 200),
                  child: KeyedSubtree(
                    key: ValueKey('${filters.hashCode}-${sortOption.name}-${beers.isEmpty}'),
                    child: content,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
