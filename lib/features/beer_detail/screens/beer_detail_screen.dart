import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/style.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Resolves [styleId] to its [Style] within [catalog], or `null` if no
/// style with that id exists.
///
/// [Beer.styleId] is a plain reference, not an embedded [Style] — this is
/// the lookup that resolves it, scoped to this screen's single call site.
Style? _resolveStyle(Catalog catalog, String styleId) {
  for (final style in catalog.styles) {
    if (style.id == styleId) {
      return style;
    }
  }
  return null;
}

/// Shows details for a single [Beer]: its name, brewery, and style.
///
/// Deliberately minimal — no SKU selection, pricing, or Value Score belong
/// here yet; those are later milestones. [beer] is passed in directly by
/// the caller (see [catalogProvider] usage below for how its [Style] is
/// resolved).
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
          final style = _resolveStyle(catalog, beer.styleId);
          return Padding(
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
              ],
            ),
          );
        },
      ),
    );
  }
}
