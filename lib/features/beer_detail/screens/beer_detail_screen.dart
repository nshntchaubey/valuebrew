import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Returns every beer in [catalog] sharing [beer]'s style (excluding
/// [beer] itself) that has at least one SKU, ranked by that beer's best
/// `valueScore` descending. Ties are broken by [catalog.beers]' original
/// order.
///
/// Beers with no SKUs are excluded entirely — there is no value score to
/// rank or display for them, so they aren't a meaningful "better value"
/// suggestion. This intentionally differs from [HomeScreen]'s sort, which
/// keeps no-SKU beers (placed last) since Home lists every beer
/// regardless of value data; this section only ever suggests beers that
/// actually have a value comparison to offer, so the two aren't the same
/// operation despite the visual similarity — see the Design Decisions
/// note on why this wasn't merged with Home's sorting logic.
///
/// Sorting on `(score, originalIndex)` pairs, rather than relying on
/// [List.sort]'s own stability, is what guarantees the tie-breaking
/// behaviour regardless of the underlying sort algorithm.
List<Beer> _similarBeers(Catalog catalog, Beer beer) {
  final candidates = catalog.beers
      .where((candidate) => candidate.styleId == beer.styleId && candidate.id != beer.id)
      .toList();

  final bestScoreByBeerId = <String, int?>{
    for (final candidate in candidates)
      candidate.id: bestSkuForBeer(catalog.skus, candidate.id)?.valueScore,
  };

  final withSkus = candidates.where((c) => bestScoreByBeerId[c.id] != null).toList();

  final indexed = withSkus.asMap().entries.toList()
    ..sort((a, b) {
      final scoreComparison =
          bestScoreByBeerId[b.value.id]!.compareTo(bestScoreByBeerId[a.value.id]!);
      if (scoreComparison != 0) return scoreComparison;
      return a.key.compareTo(b.key);
    });

  return [for (final entry in indexed) entry.value];
}

/// Shows details for a single [Beer]: its name, brewery, style, every
/// [Sku] (pack size) it comes in, and a ranked "Similar & Better Value"
/// list of other beers in the same style.
///
/// Deliberately minimal — no SKU selection belongs here yet, every SKU is
/// simply listed. `valueScore`/`valueVerdict` are read directly from the
/// catalog's precomputed fields; there is no on-device recomputation (see
/// the Value Engine milestone notes). [beer] is passed in directly by the
/// caller (see [catalogProvider] usage below for how its [Style], [Sku]s,
/// and similar beers are resolved).
class BeerDetailScreen extends ConsumerWidget {
  const BeerDetailScreen({required this.beer, super.key});

  /// The beer this screen displays.
  final Beer beer;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalogAsync = ref.watch(catalogProvider);

    return Scaffold(
      appBar: AppBar(title: Text(beer.name)),
      body: catalogAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Text('Failed to load catalog: $error'),
        ),
        data: (catalog) {
          final style = resolveStyle(catalog, beer.styleId);
          final skus = resolveSkus(catalog, beer.id);
          final similarBeers = _similarBeers(catalog, beer);
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  beer.name,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(beer.brewery),
                const SizedBox(height: 8),
                Text(style?.name ?? 'Unknown style'),
                const SizedBox(height: 16),
                if (skus.isEmpty)
                  const Text('No SKUs available for this beer.')
                else
                  ...skus.expand(
                    (sku) => [
                      Text(
                        '${sku.packageType.displayLabel} · '
                        '${sku.sizeMl.volumeLabel}',
                      ),
                      Text('MRP: ${sku.price.currencyLabel}'),
                      Text(
                        'Value score: ${sku.valueScore} '
                        '(${sku.valueVerdict.displayLabel})',
                      ),
                      const Divider(),
                    ],
                  ),
                const SizedBox(height: 16),
                Text(
                  'Similar & Better Value',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                if (similarBeers.isEmpty)
                  const Text('No similar beers available.')
                else
                  ...similarBeers.map((candidate) {
                    final candidateSku = bestSkuForBeer(catalog.skus, candidate.id)!;
                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(candidate.name),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(candidate.brewery),
                          Text(
                            'Value score: ${candidateSku.valueScore} '
                            '(${candidateSku.valueVerdict.displayLabel})',
                          ),
                        ],
                      ),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => BeerDetailScreen(beer: candidate),
                          ),
                        );
                      },
                    );
                  }),
              ],
            ),
          );
        },
      ),
    );
  }
}
