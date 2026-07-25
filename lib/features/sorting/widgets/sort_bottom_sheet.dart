import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/sorting/models/sort_option.dart';
import 'package:valuebrew/features/sorting/providers/sorting_providers.dart';

/// Lets the user pick a [SortOption] — shown in a modal bottom sheet from
/// [HomeScreen]'s AppBar action.
///
/// Selecting an option writes to [sortOptionProvider] immediately and
/// closes the sheet; there is no separate "Apply" step, matching the
/// requirement that changing the sort order reorders the list right away.
/// This widget only *presents* the eight built-in sort options; it
/// contains no sorting decision of its own.
class SortBottomSheet extends ConsumerWidget {
  const SortBottomSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeOption = ref.watch(sortOptionProvider);

    return SafeArea(
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Text('Sort by', style: Theme.of(context).textTheme.titleMedium),
            ),
            for (final option in SortOption.values)
              ListTile(
                title: Text(option.displayLabel),
                trailing: option == activeOption ? const Icon(Icons.check) : null,
                onTap: () {
                  ref.read(sortOptionProvider.notifier).state = option;
                  Navigator.pop(context);
                },
              ),
          ],
        ),
      ),
    );
  }
}
