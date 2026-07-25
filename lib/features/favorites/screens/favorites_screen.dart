import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/favorites/providers/favorites_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/beer_list_tile.dart';

/// Lists every beer the user has favorited, reusing the same row
/// (`buildBeerListTile`) `HomeScreen` uses — tapping one opens
/// [BeerDetailScreen], same as everywhere else in the app.
///
/// [favoriteBeerIdsProvider] only ever stores beer IDs; the actual [Beer]
/// data for each one is resolved from [catalogProvider]. If a favorited ID
/// no longer resolves to a beer in the current catalog (e.g. after a
/// catalog update removes it), it's simply skipped — this screen never
/// crashes over a favorite that's gone stale, it just shows one fewer row.
class FavoritesScreen extends ConsumerWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favoriteIds = ref.watch(favoriteBeerIdsProvider);
    final catalogAsync = ref.watch(catalogProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Favorites')),
      body: catalogAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Text('Failed to load catalog: $error'),
        ),
        data: (catalog) {
          final favoriteBeers =
              catalog.beers.where((beer) => favoriteIds.contains(beer.id)).toList();

          if (favoriteBeers.isEmpty) {
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

          return ListView.builder(
            itemCount: favoriteBeers.length,
            itemBuilder: (context, index) {
              final beer = favoriteBeers[index];
              return buildBeerListTile(context, beer, catalog.skus, isFavorite: true);
            },
          );
        },
      ),
    );
  }
}
