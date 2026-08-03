import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/constants/app_spacing.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/error_state_view.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';
import 'package:valuebrew/navigation/value_brew_navigator.dart';

/// The Beer Detail screen: Recommendation → Beer Detail.
///
/// Purely presentational. Every value shown — price, package, ABV, volume,
/// Value Score, verdict, price staleness — already exists on [Sku]/[Beer]/
/// [Style]; nothing here is computed. Recommendation remains the only
/// place a beer is chosen; this screen only explains one already-chosen
/// SKU, identified by [skuId] rather than an embedded model, consistent
/// with the rest of the new architecture.
class BeerDetailScreen extends ConsumerWidget {
  const BeerDetailScreen({super.key, required this.skuId});

  final String skuId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalogAsync = ref.watch(catalogProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Beer Detail')),
      body: catalogAsync.when(
        loading: () => _beerDetailSkeleton(),
        error: (error, stackTrace) => ErrorStateView(
          message: "Couldn't load the beer catalog.",
          onRetry: () => ref.invalidate(catalogProvider),
        ),
        data: (catalog) {
          final sku = resolveSku(catalog, skuId);
          final beer = sku == null ? null : resolveBeer(catalog, sku.beerId);
          if (sku == null || beer == null) {
            return const ErrorStateView(message: "This beer couldn't be found.");
          }
          final style = resolveStyle(catalog, beer.styleId);

          return SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(beer.name, style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: AppSpacing.sm),
                Text(beer.brewery),
                if (style != null) ...[
                  const SizedBox(height: AppSpacing.xs),
                  Text(style.name),
                ],
                const SizedBox(height: AppSpacing.lg),
                const Divider(),
                const SizedBox(height: AppSpacing.md),
                Text(sku.price.currencyLabel, style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: AppSpacing.xs),
                Text(sku.packageType.displayLabel),
                const SizedBox(height: AppSpacing.xs),
                Text(sku.sizeMl.volumeLabel),
                const SizedBox(height: AppSpacing.xs),
                Text('${sku.abv}% ABV'),
                const SizedBox(height: AppSpacing.md),
                Text('Value score: ${sku.valueScore} (${sku.valueVerdict.displayLabel})'),
                const SizedBox(height: AppSpacing.xs),
                Text('Price last checked: ${_formatDate(sku.priceLastChecked)}'),
                const SizedBox(height: AppSpacing.lg),
                TextButton(
                  onPressed: () =>
                      ref.read(valueBrewNavigatorProvider).beerDetailToPriceVerification(sku.id),
                  child: const Text('Verify price'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// A placeholder roughly matching this screen's real layout — name,
/// brewery, style, and the price/value block — shown while the catalog
/// loads, instead of a generic centered spinner. Composed the same way as
/// the legacy Beer Detail screen's own loading state: screen-specific
/// [SkeletonBox] composition, not a shared "detail skeleton" abstraction
/// with only one consumer.
Widget _beerDetailSkeleton() {
  return SingleChildScrollView(
    padding: const EdgeInsets.all(AppSpacing.md),
    child: const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SkeletonBox(width: 200, height: 24),
        SizedBox(height: AppSpacing.sm),
        SkeletonBox(width: 140),
        SizedBox(height: AppSpacing.xs),
        SkeletonBox(width: 100),
        SizedBox(height: AppSpacing.lg),
        SkeletonBox(width: 100, height: 20),
        SizedBox(height: AppSpacing.xs),
        SkeletonBox(width: 220),
        SizedBox(height: AppSpacing.md),
        SkeletonBox(width: 160),
        SizedBox(height: AppSpacing.xs),
        SkeletonBox(width: 180),
      ],
    ),
  );
}

String _formatDate(DateTime date) {
  final year = date.year.toString().padLeft(4, '0');
  final month = date.month.toString().padLeft(2, '0');
  final day = date.day.toString().padLeft(2, '0');
  return '$year-$month-$day';
}
