import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/search/providers/search_providers.dart';

/// The app's entry-point screen: a search field and a list of matching
/// beers from the loaded catalog. Tapping a beer navigates to its
/// [BeerDetailScreen].
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
          ),
        ],
      ),
    );
  }
}
