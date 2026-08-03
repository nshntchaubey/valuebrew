import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/constants/app_spacing.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/price_verification/domain/price_verification_result.dart';
import 'package:valuebrew/features/price_verification/domain/verify_price.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/error_state_view.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';

/// The Price Verification screen: Beer Detail → Price Verification.
///
/// Checks one specific SKU's charged price against its legal reference
/// price ([Sku.price] — the Beer Knowledge Model's own Legal Price,
/// already stored on the catalog, never re-derived here). Presentation
/// owns the charged-price input and rendering only; [verifyPrice] owns
/// the classification.
class PriceVerificationScreen extends ConsumerStatefulWidget {
  const PriceVerificationScreen({super.key, required this.skuId});

  final String skuId;

  @override
  ConsumerState<PriceVerificationScreen> createState() => _PriceVerificationScreenState();
}

class _PriceVerificationScreenState extends ConsumerState<PriceVerificationScreen> {
  final _chargedPriceController = TextEditingController();
  PriceVerificationResult? _result;
  String? _error;

  @override
  void dispose() {
    _chargedPriceController.dispose();
    super.dispose();
  }

  void _verify(double legalPrice) {
    final chargedPrice = double.tryParse(_chargedPriceController.text);
    setState(() {
      if (chargedPrice == null) {
        _error = 'Enter a valid price.';
        _result = null;
      } else {
        _error = null;
        _result = verifyPrice(chargedPrice: chargedPrice, legalPrice: legalPrice);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final catalogAsync = ref.watch(catalogProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Price Verification')),
      body: catalogAsync.when(
        loading: () => _priceVerificationSkeleton(),
        error: (error, stackTrace) => ErrorStateView(
          message: "Couldn't load the beer catalog.",
          onRetry: () => ref.invalidate(catalogProvider),
        ),
        data: (catalog) {
          final sku = resolveSku(catalog, widget.skuId);
          final beer = sku == null ? null : resolveBeer(catalog, sku.beerId);
          if (sku == null || beer == null) {
            return const ErrorStateView(message: "This beer couldn't be found.");
          }
          final result = _result;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(beer.name, style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: AppSpacing.xs),
                Text('Legal price: ${sku.price.currencyLabel}'),
                const SizedBox(height: AppSpacing.lg),
                TextField(
                  controller: _chargedPriceController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: 'What did you pay? (₹)',
                    errorText: _error,
                  ),
                ),
                const SizedBox(height: AppSpacing.md),
                ElevatedButton(
                  onPressed: () => _verify(sku.price),
                  child: const Text('Verify price'),
                ),
                if (result != null) ...[
                  const SizedBox(height: AppSpacing.lg),
                  Text(
                    result.verdict.displayLabel,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  Text(result.explanation),
                  const SizedBox(height: AppSpacing.md),
                  const Text(
                    'Beer identity and the legal price are both Verified Facts — '
                    'high confidence. This result reflects exactly what you '
                    "reported; it isn't independently checked against what you "
                    'were actually charged.',
                    style: TextStyle(fontStyle: FontStyle.italic),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}

/// A placeholder roughly matching this screen's real layout — identity,
/// legal price, and the charged-price input — shown while the catalog
/// loads, instead of a generic centered spinner. Screen-specific
/// [SkeletonBox] composition, matching the Beer Detail precedent, not a
/// shared "detail skeleton" abstraction with only one consumer.
Widget _priceVerificationSkeleton() {
  return SingleChildScrollView(
    padding: const EdgeInsets.all(AppSpacing.md),
    child: const Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SkeletonBox(width: 180, height: 24),
        SizedBox(height: AppSpacing.xs),
        SkeletonBox(width: 140),
        SizedBox(height: AppSpacing.lg),
        SkeletonBox(height: 56),
        SizedBox(height: AppSpacing.md),
        SkeletonBox(height: 40),
      ],
    ),
  );
}
