import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';

/// A small, subtle "N filters active" row with a "Clear" action —
/// deliberately not a chip or a redesign of whatever screen it sits in.
/// Renders nothing at all when no filter is active.
///
/// Shared by [HomeScreen] and [FavoritesScreen] (and any future screen
/// showing a filtered beer list) since [filterStateProvider] is a single,
/// app-wide value — a filter set from one screen is already active on the
/// other, so both need the same "filters are on, here's how many, here's
/// how to clear them" affordance.
class ActiveFiltersIndicator extends ConsumerWidget {
  const ActiveFiltersIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final filters = ref.watch(filterStateProvider);

    if (!filters.isActive) return const SizedBox.shrink();

    final count = filters.activeFilterCount;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: Text(
              count == 1 ? '1 filter active' : '$count filters active',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          TextButton(
            onPressed: () => ref.read(filterStateProvider.notifier).state = FilterState.none,
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
}
