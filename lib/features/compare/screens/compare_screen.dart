import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Renders one side of the comparison: [beer]'s brewery, style, and every
/// SKU it comes in, read from [catalog].
///
/// A plain function rather than a widget class, matching this codebase's
/// convention for small, single-purpose builders (see [HomeScreen] and
/// [BeerDetailScreen]) — used twice in [CompareScreen], for Beer A and
/// Beer B, which is exactly the "more than one call site" bar for sharing
/// this rather than inlining it.
Widget buildBeerColumn(BuildContext context, Catalog catalog, Beer beer) {
  final style = resolveStyle(catalog, beer.styleId);
  final skus = resolveSkus(catalog, beer.id);

  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(beer.name, style: Theme.of(context).textTheme.titleMedium),
      const SizedBox(height: 4),
      Text(beer.brewery),
      Text(style?.name ?? 'Unknown style'),
      const SizedBox(height: 8),
      if (skus.isEmpty)
        const Text('No SKUs available for this beer.')
      else
        ...skus.expand(
          (sku) => [
            Text(
              '${sku.packageType.displayLabel} · ${sku.sizeMl.volumeLabel}',
            ),
            Text('MRP: ${sku.price.currencyLabel}'),
            Text(
              'Value score: ${sku.valueScore} '
              '(${sku.valueVerdict.displayLabel})',
            ),
            const Divider(),
          ],
        ),
    ],
  );
}

/// Lets the user pick two beers and see their facts side by side: brewery,
/// style, and every SKU (package type, volume, MRP, value score, value
/// verdict).
///
/// Deliberately minimal — no new value scoring happens here, nothing is
/// persisted, and there is no recommendation of which beer to pick. Every
/// value shown is read directly from the catalog's precomputed fields, the
/// same as [BeerDetailScreen].
class CompareScreen extends ConsumerStatefulWidget {
  const CompareScreen({super.key});

  @override
  ConsumerState<CompareScreen> createState() => _CompareScreenState();
}

class _CompareScreenState extends ConsumerState<CompareScreen> {
  Beer? _beerA;
  Beer? _beerB;

  @override
  Widget build(BuildContext context) {
    final catalogAsync = ref.watch(catalogProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Compare Beers')),
      body: catalogAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Text('Failed to load catalog: $error'),
        ),
        data: (catalog) {
          final beers = catalog.beers;
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: DropdownButton<Beer>(
                        isExpanded: true,
                        hint: const Text('Choose Beer A'),
                        value: _beerA,
                        items: [
                          for (final beer in beers)
                            DropdownMenuItem(value: beer, child: Text(beer.name)),
                        ],
                        onChanged: (beer) => setState(() => _beerA = beer),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: DropdownButton<Beer>(
                        isExpanded: true,
                        hint: const Text('Choose Beer B'),
                        value: _beerB,
                        items: [
                          for (final beer in beers)
                            DropdownMenuItem(value: beer, child: Text(beer.name)),
                        ],
                        onChanged: (beer) => setState(() => _beerB = beer),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: SingleChildScrollView(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: _beerA == null
                              ? const Text('Select Beer A to compare.')
                              : buildBeerColumn(context, catalog, _beerA!),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _beerB == null
                              ? const Text('Select Beer B to compare.')
                              : buildBeerColumn(context, catalog, _beerB!),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
