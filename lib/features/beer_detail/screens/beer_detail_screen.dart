import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Shows details for a single [Beer]: its name, brewery, style, and every
/// [Sku] (pack size) it comes in.
///
/// Deliberately minimal — no SKU selection belongs here yet, every SKU is
/// simply listed. `valueScore`/`valueVerdict` are read directly from the
/// catalog's precomputed fields; there is no on-device recomputation (see
/// the Value Engine milestone notes). [beer] is passed in directly by the
/// caller (see [catalogProvider] usage below for how its [Style] and
/// [Sku]s are resolved).
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
                      Text('${sku.packageType.name} · ${sku.sizeMl}ml'),
                      Text('MRP: ₹${sku.price}'),
                      Text(
                        'Value score: ${sku.valueScore} '
                        '(${verdictLabel(sku.valueVerdict)})',
                      ),
                      const Divider(),
                    ],
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
