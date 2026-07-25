import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/beer_detail/wrong_report.dart';
import 'package:valuebrew/features/recommendation/providers/recommendation_providers.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// Runs [compute] and returns its result, or an empty list if it throws.
///
/// [RecommendationEngine] is trusted, tested business logic, but a screen
/// should never let a recommendation failure take down the whole page —
/// the rest of [BeerDetailScreen] (name, SKUs, "This looks wrong") is
/// useful on its own even if recommendations can't be produced.
List<Sku> _safeRecommendations(List<Sku> Function() compute) {
  try {
    return compute();
  } catch (_) {
    return const [];
  }
}

/// Builds the row for a single recommended [sku] (its resolved beer's name
/// and brewery, plus [sku]'s own value score), or `null` if [sku]'s beer
/// can't be resolved in [catalog] — which shouldn't happen for a
/// consistent catalog, but isn't worth crashing over if it ever does.
///
/// [sectionKey] distinguishes which of the two recommendation sections
/// this tile belongs to (e.g. `'similar'` vs `'better_value'`). The same
/// SKU can legitimately qualify for both sections at once, so this is
/// purely a testability hook — it has no visual effect — letting tests
/// target a specific section's tile for a given SKU unambiguously.
///
/// Tapping the row pushes a new [BeerDetailScreen] for that beer, same as
/// the rest of this screen's navigation.
Widget? _recommendationTile(BuildContext context, Catalog catalog, Sku sku, String sectionKey) {
  final candidateBeer = resolveBeer(catalog, sku.beerId);
  if (candidateBeer == null) return null;

  return ListTile(
    key: ValueKey('$sectionKey:${sku.id}'),
    contentPadding: EdgeInsets.zero,
    title: Text(candidateBeer.name),
    subtitle: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(candidateBeer.brewery),
        Text('Value score: ${sku.valueScore} (${sku.valueVerdict.displayLabel})'),
      ],
    ),
    onTap: () {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => BeerDetailScreen(beer: candidateBeer)),
      );
    },
  );
}

/// A small "This looks wrong" action for a single (beer, SKU) pair.
///
/// Shows a confirmation dialog on tap, submits a [WrongReport] via
/// [wrongReportStoreProvider] if confirmed, then shows a success
/// acknowledgement. Once submitted, replaces itself with a "Reported"
/// label for the rest of the app session (see [reportedItemsProvider]),
/// preventing duplicate submissions for the same SKU.
///
/// Used once per SKU shown on [BeerDetailScreen] — a beer with multiple
/// SKUs has multiple independent instances of this widget, which is
/// exactly why it's a small dedicated widget rather than inlined.
class _WrongReportAction extends ConsumerWidget {
  const _WrongReportAction({required this.beerId, required this.skuId});

  final String beerId;
  final String skuId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = wrongReportKey(beerId, skuId);
    final alreadyReported = ref.watch(reportedItemsProvider).contains(key);

    if (alreadyReported) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 4),
        child: Text(
          'Reported',
          style: TextStyle(fontStyle: FontStyle.italic),
        ),
      );
    }

    return TextButton.icon(
      style: TextButton.styleFrom(
        padding: EdgeInsets.zero,
        alignment: Alignment.centerLeft,
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
      icon: const Icon(Icons.flag_outlined, size: 16),
      label: const Text('This looks wrong'),
      onPressed: () => _handleTap(context, ref, key),
    );
  }

  Future<void> _handleTap(BuildContext context, WidgetRef ref, String key) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Report this listing?'),
        content: const Text(
          'Reporting incorrect info helps us improve catalog accuracy.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Report'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    await ref.read(wrongReportStoreProvider).submit(
          WrongReport(beerId: beerId, skuId: skuId, timestamp: DateTime.now()),
        );

    ref.read(reportedItemsProvider.notifier).update((state) => {...state, key});

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Thanks — this has been reported.'),
        ),
      );
    }
  }
}

/// Shows details for a single [Beer]: its name, brewery, style, every
/// [Sku] (pack size) it comes in, a "This looks wrong" report action per
/// SKU, and two [RecommendationEngine]-backed lists — "Similar beers" and
/// "Better value picks" — under a shared "Similar & Better Value" heading.
///
/// Deliberately minimal — no SKU selection belongs here yet, every SKU is
/// simply listed. `valueScore`/`valueVerdict` are read directly from the
/// catalog's precomputed fields; there is no on-device recomputation (see
/// the Value Engine milestone notes). [beer] is passed in directly by the
/// caller (see [catalogProvider] usage below for how its [Style] and
/// [Sku]s are resolved, and [recommendationEngineProvider] for how its
/// recommendations are produced).
///
/// This screen has no beer-level SKU selection, so its highest-`valueScore`
/// SKU (via [bestSkuForBeer]) stands in as the reference SKU passed to
/// [RecommendationEngine] — the same SKU this screen already used to rank
/// candidates before this milestone. If a beer has no SKUs at all, there is
/// no reference SKU and both recommendation lists are simply empty.
///
/// [RecommendationEngine] is SKU-level and only excludes the exact
/// reference SKU it was given, not every SKU belonging to the same beer
/// (see its own tests) — so this screen filters out any recommended SKU
/// whose `beerId` matches [beer]'s own, since a beer with more than one SKU
/// would otherwise be recommended to itself. This is this screen's own
/// beer-level adaptation of a SKU-level result, not a change to
/// [RecommendationEngine]'s behaviour.
class BeerDetailScreen extends ConsumerWidget {
  const BeerDetailScreen({required this.beer, super.key});

  /// The beer this screen displays.
  final Beer beer;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalogAsync = ref.watch(catalogProvider);
    final engine = ref.watch(recommendationEngineProvider);

    return Scaffold(
      appBar: AppBar(title: Text(beer.name)),
      body: catalogAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Text('Failed to load catalog: $error'),
        ),
        data: (catalog) {
          final style = resolveStyle(catalog, beer.styleId);
          final skus = resolveSkus(catalog, beer.id);
          final referenceSku = bestSkuForBeer(catalog.skus, beer.id);

          // RecommendationEngine only excludes the exact reference SKU, not
          // every SKU of its beer (it's deliberately SKU-level — see its own
          // tests). This screen is beer-level, so a beer with more than one
          // SKU would otherwise recommend itself; filtering out any result
          // sharing beer.id is this screen's own adaptation, not a change to
          // the engine's behaviour.
          final similarBeers = referenceSku == null
              ? const <Sku>[]
              : _safeRecommendations(() => engine.similarBeers(referenceSku, catalog))
                  .where((sku) => sku.beerId != beer.id)
                  .toList();
          final betterValueAlternatives = referenceSku == null
              ? const <Sku>[]
              : _safeRecommendations(() => engine.betterValueAlternatives(referenceSku, catalog))
                  .where((sku) => sku.beerId != beer.id)
                  .toList();

          return SingleChildScrollView(
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
                const SizedBox(height: 16),
                if (skus.isEmpty)
                  const Text('No SKUs available for this beer.')
                else
                  ...skus.expand(
                    (sku) => [
                      Text(
                        '${sku.packageType.displayLabel} · '
                        '${sku.sizeMl.volumeLabel}',
                      ),
                      Text('MRP: ${sku.price.currencyLabel}'),
                      Text(
                        'Value score: ${sku.valueScore} '
                        '(${sku.valueVerdict.displayLabel})',
                      ),
                      _WrongReportAction(beerId: beer.id, skuId: sku.id),
                      const Divider(),
                    ],
                  ),
                const SizedBox(height: 16),
                Text(
                  'Similar & Better Value',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Similar beers',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                if (similarBeers.isEmpty)
                  const Text('No similar beers available.')
                else
                  ...similarBeers
                      .map((sku) => _recommendationTile(context, catalog, sku, 'similar'))
                      .whereType<Widget>(),
                const SizedBox(height: 16),
                Text(
                  'Better value picks',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                if (betterValueAlternatives.isEmpty)
                  const Text('No better value alternatives available.')
                else
                  ...betterValueAlternatives
                      .map((sku) => _recommendationTile(context, catalog, sku, 'better_value'))
                      .whereType<Widget>(),
              ],
            ),
          );
        },
      ),
    );
  }
}
