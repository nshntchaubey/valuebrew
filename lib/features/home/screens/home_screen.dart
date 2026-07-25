import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// The app's entry-point screen: a plain list of every beer in the loaded
/// catalog. Tapping a beer navigates to its [BeerDetailScreen].
///
/// Deliberately minimal — this screen exists to prove the data flow from
/// [catalogProvider] through to the UI. No search, filters, or custom
/// beer-card presentation belongs here yet; those are later milestones.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalogAsync = ref.watch(catalogProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ValueBrew'),
        centerTitle: true,
      ),
      body: catalogAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Text('Failed to load catalog: $error'),
        ),
        data: (catalog) {
          final beers = catalog.beers;
          return ListView.builder(
            itemCount: beers.length,
            itemBuilder: (context, index) {
              final beer = beers[index];
              return ListTile(
                title: Text(beer.name),
                subtitle: Text(beer.brewery),
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
    );
  }
}
