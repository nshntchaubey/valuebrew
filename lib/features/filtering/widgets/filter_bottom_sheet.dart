import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/filtering/models/abv_range.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/models/price_range.dart';
import 'package:valuebrew/features/filtering/providers/filtering_providers.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Returns every distinct brewery name in [beers], sorted alphabetically.
///
/// A plain, pure function — not a provider — since it's derived once per
/// bottom-sheet build directly from data already loaded by [catalogProvider],
/// with a single call site. Nothing here decides whether a beer matches a
/// filter; that's [FilteringEngine]'s job.
List<String> _distinctBreweries(List<Beer> beers) {
  return beers.map((beer) => beer.brewery).toSet().toList()..sort();
}

/// The filter-editing UI shown in a modal bottom sheet from [HomeScreen]'s
/// AppBar action. Every control writes straight to [filterStateProvider]
/// on change — there is no separate "Apply" step, matching the requirement
/// that changing a filter updates the visible list immediately.
///
/// This widget only *presents* choices already defined by [FilterState];
/// it contains no filtering decision of its own. Reusable by any future
/// screen that wants the same filter-editing UI, unchanged.
class FilterBottomSheet extends ConsumerWidget {
  const FilterBottomSheet({super.key});

  /// Upper bound of the ABV slider. A fixed, presentation-only constant —
  /// not derived from live catalog data — chosen to comfortably span
  /// realistic beer ABVs.
  static const double _maxAbv = 15.0;

  /// Upper bound of the price slider, for the same reason as [_maxAbv].
  static const double _maxPrice = 1000.0;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalogAsync = ref.watch(catalogProvider);
    final filters = ref.watch(filterStateProvider);
    final notifier = ref.read(filterStateProvider.notifier);

    return SafeArea(
      child: catalogAsync.when(
        loading: () => const SizedBox(
          height: 200,
          child: Center(child: CircularProgressIndicator()),
        ),
        error: (error, stackTrace) => SizedBox(
          height: 200,
          child: Center(child: Text('Failed to load catalog: $error')),
        ),
        data: (catalog) {
          final breweries = _distinctBreweries(catalog.beers);

          return Padding(
            padding: EdgeInsets.only(
              left: 16,
              right: 16,
              top: 16,
              bottom: MediaQuery.of(context).viewInsets.bottom + 16,
            ),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Filters', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 16),
                  const Text('Style'),
                  DropdownButton<String?>(
                    isExpanded: true,
                    value: filters.styleId,
                    hint: const Text('Any style'),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('Any style')),
                      for (final style in catalog.styles)
                        DropdownMenuItem(value: style.id, child: Text(style.name)),
                    ],
                    onChanged: (value) => notifier.state = filters.withStyle(value),
                  ),
                  const SizedBox(height: 16),
                  const Text('Brewery'),
                  DropdownButton<String?>(
                    isExpanded: true,
                    value: filters.brewery,
                    hint: const Text('Any brewery'),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('Any brewery')),
                      for (final brewery in breweries)
                        DropdownMenuItem(value: brewery, child: Text(brewery)),
                    ],
                    onChanged: (value) => notifier.state = filters.withBrewery(value),
                  ),
                  const SizedBox(height: 16),
                  const Text('Package type'),
                  DropdownButton<PackageType?>(
                    isExpanded: true,
                    value: filters.packageType,
                    hint: const Text('Any package'),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('Any package')),
                      for (final packageType in PackageType.values)
                        DropdownMenuItem(
                          value: packageType,
                          child: Text(packageType.displayLabel),
                        ),
                    ],
                    onChanged: (value) => notifier.state = filters.withPackageType(value),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'ABV: ${(filters.abvRange?.min ?? 0).toStringAsFixed(1)}% – '
                    '${(filters.abvRange?.max ?? _maxAbv).toStringAsFixed(1)}%',
                  ),
                  RangeSlider(
                    min: 0,
                    max: _maxAbv,
                    divisions: 30,
                    values: RangeValues(
                      filters.abvRange?.min ?? 0,
                      filters.abvRange?.max ?? _maxAbv,
                    ),
                    onChanged: (values) {
                      notifier.state = filters.withAbvRange(
                        AbvRange(min: values.start, max: values.end),
                      );
                    },
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Price: ${(filters.priceRange?.min ?? 0).toStringAsFixed(0)} – '
                    '${(filters.priceRange?.max ?? _maxPrice).toStringAsFixed(0)}',
                  ),
                  RangeSlider(
                    min: 0,
                    max: _maxPrice,
                    divisions: 20,
                    values: RangeValues(
                      filters.priceRange?.min ?? 0,
                      filters.priceRange?.max ?? _maxPrice,
                    ),
                    onChanged: (values) {
                      notifier.state = filters.withPriceRange(
                        PriceRange(min: values.start, max: values.end),
                      );
                    },
                  ),
                  const SizedBox(height: 8),
                  Text('Minimum value score: ${filters.minValueScore ?? 0}'),
                  Slider(
                    min: 0,
                    max: 100,
                    divisions: 20,
                    value: (filters.minValueScore ?? 0).toDouble(),
                    onChanged: (value) {
                      final rounded = value.round();
                      notifier.state = filters.withMinValueScore(rounded == 0 ? null : rounded);
                    },
                  ),
                  const SizedBox(height: 8),
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () => notifier.state = FilterState.none,
                      child: const Text('Clear filters'),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
