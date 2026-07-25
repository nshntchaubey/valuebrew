import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/sorting/providers/sorting_providers.dart';

/// A small, subtle "Sorted by: X" label — deliberately not a redesign of
/// whatever screen it sits in.
///
/// Unlike [ActiveFiltersIndicator] (which hides itself entirely when no
/// filter is active), this always renders: there's no "off" state for
/// sorting the way there is for filtering — [SortOption.relevance] is
/// still a real, meaningful choice worth naming, not an absence of one.
///
/// Shared by [HomeScreen] and [FavoritesScreen] since [sortOptionProvider]
/// is a single, app-wide value — a sort order chosen on Home is already
/// active on Favorites, so both need to show it.
class ActiveSortIndicator extends ConsumerWidget {
  const ActiveSortIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sortOption = ref.watch(sortOptionProvider);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Text(
        'Sorted by: ${sortOption.displayLabel}',
        style: Theme.of(context).textTheme.bodySmall,
      ),
    );
  }
}
