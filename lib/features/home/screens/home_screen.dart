import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Returns the [Sku] with the highest `valueScore` among those belonging
/// to the beer with [beerId], or `null` if it has no SKUs.
///
/// [Sku.beerId] is a plain reference, not an embedded beer object — this
/// is the lookup that resolves it, scoped to this screen's single call
/// site.
Sku? _bestSkuForBeer(List<Sku> skus, String beerId) {
  Sku? best;
  for (final sku in skus) {
    if (sku.beerId != beerId) continue;
    if (best == null || sku.valueScore > best.valueScore) {
      best = sku;
    }
  }
  return best;
}

/// Plain-language label for a [ValueVerdict], matching the wording in the
/// V1 technical architecture's Value Score algorithm.
String _verdictLabel(ValueVerdict verdict) {
  switch (verdict) {
    case ValueVerdict.greatValue:
      return 'Great value';
    case ValueVerdict.fairValue:
      return 'Fair value';
    case ValueVerdict.overpriced:
      return 'Overpriced for this ABV';
  }
}

/// How [HomeScreen] orders the beer list.
enum SortMode {
  /// Unmodified order, as it appears in the loaded catalog.
  catalogOrder,

  /// Descending by each beer's highest `valueScore`, beers with no SKUs
  /// last, ties broken by catalog order.
  bestValue,
}

/// Sorts [beers] by [SortMode.bestValue]: descending by each beer's
/// highest `valueScore` (via [_bestSkuForBeer]), beers with no SKUs always
/// last, and ties (including "no SKUs" ties) broken by [beers]' original
/// order.
///
/// Sorting on `(score, originalIndex)` pairs, rather than relying on
/// [List.sort]'s own stability, is what guarantees the tie-breaking
/// behaviour regardless of the underlying sort algorithm.
List<Beer> _sortedByValue(List<Beer> beers, List<Sku> skus) {
  final bestScoreByBeerId = <String, int?>{
    for (final beer in beers) beer.id: _bestSkuForBeer(skus, beer.id)?.valueScore,
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

/// The app's entry-point screen: a search field, a sort control, and a
/// list of matching beers from the loaded catalog, each showing its best
/// available value. Tapping a beer navigates to its [BeerDetailScreen].
///
/// Deliberately minimal — this screen exists to prove the data flow from
/// [searchResultsProvider] through to the UI. No filters beyond name/
/// brewery search, sort modes beyond [SortMode], or custom beer-card
/// presentation, belong here yet; those are later milestones.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  SortMode _sortMode = SortMode.catalogOrder;

  @override
  Widget build(BuildContext context) {
    final resultsAsync = ref.watch(searchResultsProvider);
    final skus = ref.watch(catalogProvider).valueOrNull?.skus ?? const <Sku>[];

    return Scaffold(
      appBar: AppBar(
        title: const Text('ValueBrew'),
        centerTitle: true,
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
                return ListView.builder(
                  itemCount: orderedBeers.length,
                  itemBuilder: (context, index) {
                    final beer = orderedBeers[index];
                    final bestSku = _bestSkuForBeer(skus, beer.id);
                    return ListTile(
                      title: Text(beer.name),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(beer.brewery),
                          Text(
                            bestSku == null
                                ? 'No SKUs available'
                                : 'Value score: ${bestSku.valueScore} '
                                    '(${_verdictLabel(bestSku.valueVerdict)})',
                          ),
                        ],
                      ),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => BeerDetailScreen(beer: beer),
                          ),
                        );
                      },
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
