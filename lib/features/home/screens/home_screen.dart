import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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

/// The app's entry-point screen: a search field and a list of matching
/// beers from the loaded catalog, each showing its best available value.
/// Tapping a beer navigates to its [BeerDetailScreen].
///
/// Deliberately minimal — this screen exists to prove the data flow from
/// [searchResultsProvider] through to the UI. No filters beyond name/
/// brewery search, or custom beer-card presentation, belong here yet;
/// those are later milestones.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
          Expanded(
            child: resultsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stackTrace) => Center(
                child: Text('Failed to load catalog: $error'),
              ),
              data: (beers) {
                return ListView.builder(
                  itemCount: beers.length,
                  itemBuilder: (context, index) {
                    final beer = beers[index];
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
