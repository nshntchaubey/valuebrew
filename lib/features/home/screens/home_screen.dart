import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/compare/screens/compare_screen.dart';
import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/favorites/screens/favorites_screen.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/filtering/widgets/active_filters_indicator.dart';
import 'package:valuebrew/features/filtering/widgets/filter_bottom_sheet.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/beer_list_tile.dart';

/// How [HomeScreen] orders the beer list.
enum SortMode {
  /// Unmodified order, as it appears in the loaded catalog.
  catalogOrder,

  /// Descending by each beer's highest `valueScore`, beers with no SKUs
  /// last, ties broken by catalog order.
  bestValue,
}

/// Sorts [beers] by [SortMode.bestValue]: descending by each beer's
/// highest `valueScore` (via [bestSkuForBeer]), beers with no SKUs always
/// last, and ties (including "no SKUs" ties) broken by [beers]' original
/// order.
///
/// Sorting on `(score, originalIndex)` pairs, rather than relying on
/// [List.sort]'s own stability, is what guarantees the tie-breaking
/// behaviour regardless of the underlying sort algorithm.
List<Beer> _sortedByValue(List<Beer> beers, List<Sku> skus) {
  final bestScoreByBeerId = <String, int?>{
    for (final beer in beers) beer.id: bestSkuForBeer(skus, beer.id)?.valueScore,
  };

  final indexed = beers.asMap().entries.toList()
    ..sort((a, b) {
      final scoreA = bestScoreByBeerId[a.value.id];
      final scoreB = bestScoreByBeerId[b.value.id];
      if (scoreA == null && scoreB == null) return a.key.compareTo(b.key);
      if (scoreA == null) return 1;
      if (scoreB == null) return -1;
      final scoreComparison = scoreB.compareTo(scoreA);
      if (scoreComparison != 0) return scoreComparison;
      return a.key.compareTo(b.key);
    });

  return [for (final entry in indexed) entry.value];
}

/// The app's entry-point screen: a search field, a filter action, a sort
/// control, and a list of matching beers from the loaded catalog, each
/// showing its best available value. Tapping a beer navigates to its
/// [BeerDetailScreen].
///
/// The visible list is [filteredHomeBeersProvider]'s output — search text
/// and active filters (style, brewery, ABV, price, package type, minimum
/// value score, via [FilteringEngine]) both narrow it before this screen
/// ever sees it; sorting is the only ordering decision this screen still
/// makes itself. No custom beer-card presentation belongs here yet; that's
/// a later milestone.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  SortMode _sortMode = SortMode.catalogOrder;

  @override
  Widget build(BuildContext context) {
    final resultsAsync = ref.watch(filteredHomeBeersProvider);
    final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const <Sku>[];
    final favoriteIds = ref.watch(favoriteBeerIdsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ValueBrew'),
        centerTitle: true,
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
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: SegmentedButton<SortMode>(
              segments: const [
                ButtonSegment(
                  value: SortMode.catalogOrder,
                  label: Text('Catalog order'),
                ),
                ButtonSegment(
                  value: SortMode.bestValue,
                  label: Text('Best value'),
                ),
              ],
              selected: {_sortMode},
              onSelectionChanged: (selection) {
                setState(() => _sortMode = selection.first);
              },
            ),
          ),
          const ActiveFiltersIndicator(),
          const SizedBox(height: 8),
          Expanded(
            child: resultsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stackTrace) => Center(
                child: Text('Failed to load catalog: $error'),
              ),
              data: (beers) {
                final orderedBeers = _sortMode == SortMode.bestValue
                    ? _sortedByValue(beers, skus)
                    : beers;

                if (orderedBeers.isEmpty && ref.watch(filterStateProvider).isActive) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text('No beers match your filters.'),
                          const SizedBox(height: 8),
                          TextButton(
                            onPressed: () =>
                                ref.read(filterStateProvider.notifier).state = FilterState.none,
                            child: const Text('Clear filters'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return ListView.builder(
                  itemCount: orderedBeers.length,
                  itemBuilder: (context, index) {
                    final beer = orderedBeers[index];
                    return buildBeerListTile(
                      context,
                      beer,
                      skus,
                      isFavorite: favoriteIds.contains(beer.id),
                    );
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
