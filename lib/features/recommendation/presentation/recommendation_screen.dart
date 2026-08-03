import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/core/constants/app_spacing.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/recommendation/domain/generate_recommendation.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_outcome.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/error_state_view.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';
import 'package:valuebrew/navigation/value_brew_navigator.dart';

/// The Recommendation screen.
///
/// Collects budget, then optionally a Style preference, and shows one
/// real, explained recommendation computed by [generateRecommendation]
/// against the real catalog. See that function's own doc comment for the
/// extension seams intentionally left for later.
///
/// Refinement visibility relies exclusively on
/// [RecommendationOutcome.canBeRefinedFurther] — this screen never
/// inspects concrete outcome subclasses to decide whether refinement is
/// available. It does inspect them to decide what to render, which is a
/// different, legitimate presentation concern.
///
/// [isPlanning] is a pure presentation modifier, per the Decision Engine
/// Model's Journey 4 ("the same inputs as Journey 3... a structurally
/// lower confidence ceiling on the output"): it changes nothing about
/// [generateRecommendation] itself — same inputs, same filtering, same
/// ranking, same outcomes — only whether [_PlanningModeBanner] is shown
/// alongside whatever outcome results.
class RecommendationScreen extends ConsumerStatefulWidget {
  const RecommendationScreen({super.key, this.isPlanning = false});

  final bool isPlanning;

  @override
  ConsumerState<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends ConsumerState<RecommendationScreen> {
  final _budgetController = TextEditingController();
  RecommendationOutcome? _outcome;
  String? _selectedStyleId;
  bool _refining = false;
  String? _error;

  @override
  void dispose() {
    _budgetController.dispose();
    super.dispose();
  }

  /// The single internal regeneration path. Invoked identically by the
  /// primary budget submission and by every Style selection or clearing
  /// action, always against the complete current state — the current
  /// budget text and [styleId] — so recommendation generation can never
  /// drift into two different behaviours depending on which control
  /// triggered it.
  ///
  /// Invalid budget input clears [_outcome] (so nothing stale is shown,
  /// matching this screen's original behaviour) but never touches
  /// [_selectedStyleId] — a stated Style preference is never discarded
  /// as a side effect of a validation failure.
  void _regenerate(Catalog catalog, {required String? styleId}) {
    final budget = double.tryParse(_budgetController.text);
    setState(() {
      _selectedStyleId = styleId;
      if (budget == null) {
        _error = 'Enter a valid budget.';
        _outcome = null;
      } else {
        _error = null;
        _outcome = generateRecommendation(catalog, budget: budget, styleId: styleId);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final catalogAsync = ref.watch(catalogProvider);
    final outcome = _outcome;

    return Scaffold(
      appBar: AppBar(title: const Text('Recommendation')),
      body: catalogAsync.when(
        data: (catalog) => Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _budgetController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  labelText: 'Your budget (₹)',
                  errorText: _error,
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => _regenerate(catalog, styleId: _selectedStyleId),
                child: const Text('Get a recommendation'),
              ),
              if (outcome != null) ...[
                const SizedBox(height: 24),
                if (widget.isPlanning) ...[
                  const _PlanningModeBanner(),
                  const SizedBox(height: 16),
                ],
                _RecommendationOutcomeView(
                  outcome: outcome,
                  onSeeFullDetails: (skuId) =>
                      ref.read(valueBrewNavigatorProvider).recommendationToBeerDetail(skuId),
                ),
                if (outcome.canBeRefinedFurther) ...[
                  const SizedBox(height: 16),
                  if (_refining)
                    _StylePicker(
                      catalog: catalog,
                      selectedStyleId: _selectedStyleId,
                      onChanged: (styleId) => _regenerate(catalog, styleId: styleId),
                    )
                  else
                    TextButton(
                      onPressed: () => setState(() => _refining = true),
                      child: const Text('Refine recommendation'),
                    ),
                ],
              ],
            ],
          ),
        ),
        loading: () => _recommendationSkeleton(),
        error: (error, _) => ErrorStateView(
          message: "Couldn't load the beer catalog.",
          onRetry: () => ref.invalidate(catalogProvider),
        ),
      ),
    );
  }
}

/// A placeholder roughly matching this screen's real layout — the budget
/// input and submit button — shown while the catalog loads, instead of a
/// generic centered spinner. Screen-specific [SkeletonBox] composition,
/// matching the Beer Detail and Price Verification precedent, not a
/// shared "detail skeleton" abstraction with only one consumer.
Widget _recommendationSkeleton() {
  return Padding(
    padding: const EdgeInsets.all(AppSpacing.md),
    child: const Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SkeletonBox(height: 56),
        SizedBox(height: AppSpacing.md),
        SkeletonBox(height: 40),
      ],
    ),
  );
}

/// Renders [outcome]'s content. Inspecting the concrete outcome type here
/// is legitimate — this is a rendering decision, not a refinability
/// decision (which belongs exclusively to
/// [RecommendationOutcome.canBeRefinedFurther]).
class _RecommendationOutcomeView extends StatelessWidget {
  const _RecommendationOutcomeView({required this.outcome, required this.onSeeFullDetails});

  final RecommendationOutcome outcome;

  /// Called with the recommended SKU's id when "See full details" is
  /// tapped. Only reachable from [RecommendationFound] — the button
  /// itself only exists in that branch.
  final ValueChanged<String> onSeeFullDetails;

  @override
  Widget build(BuildContext context) {
    return switch (outcome) {
      RecommendationFound(:final result) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(result.beer.name, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(result.explanation),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => onSeeFullDetails(result.sku.id),
              child: const Text('See full details'),
            ),
          ],
        ),
      NoRecommendationWithinBudget() => const Text('No beer in the catalog fits that budget.'),
      NoRecommendationMatchingStyle() =>
        const Text('No beer within your budget matches that style.'),
      RecommendationTie(:final candidates, :final explanation) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(explanation),
            for (final candidate in candidates) ...[
              const SizedBox(height: 8),
              Text(
                '${candidate.beer.name} — ${candidate.sku.sizeMl.volumeLabel}, '
                '${candidate.sku.packageType.displayLabel}',
              ),
              TextButton(
                onPressed: () => onSeeFullDetails(candidate.sku.id),
                child: const Text('See full details'),
              ),
            ],
          ],
        ),
    };
  }
}

/// The standing caveat shown throughout a Planning-Mode-flagged
/// Recommendation flow: prices and availability may no longer hold by
/// the time an actual purchase happens. Rendered independently of
/// [RecommendationOutcome]'s concrete type — per the Decision Engine
/// Model ("explicitly caveated throughout, not only at the end") and
/// Experience Flows ("restating the caveat every time it appears, not
/// just once") — so it applies uniformly to every outcome this flow can
/// produce, recovery outcomes included, not only a successful one. Not a
/// shared widget: exactly one consumer.
class _PlanningModeBanner extends StatelessWidget {
  const _PlanningModeBanner();

  @override
  Widget build(BuildContext context) {
    return Text(
      'This is a provisional recommendation for planning ahead — prices '
      'and availability may have changed by the time you actually buy.',
      style: Theme.of(context).textTheme.bodySmall?.copyWith(fontStyle: FontStyle.italic),
    );
  }
}

/// Lets a person choose a Style preference, or clear it back to no
/// preference. Stays expanded once revealed, rather than collapsing back
/// behind the refine affordance after a selection — a deliberate,
/// architecturally-inconsequential choice (see the Commit 2 plan's own
/// implementation guidance), made here in favour of letting a person
/// change their mind about Style without repeatedly re-opening it.
class _StylePicker extends StatelessWidget {
  const _StylePicker({
    required this.catalog,
    required this.selectedStyleId,
    required this.onChanged,
  });

  final Catalog catalog;
  final String? selectedStyleId;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: [
        ChoiceChip(
          label: const Text('No preference'),
          selected: selectedStyleId == null,
          onSelected: (_) => onChanged(null),
        ),
        for (final style in catalog.styles)
          ChoiceChip(
            label: Text(style.name),
            selected: selectedStyleId == style.id,
            onSelected: (_) => onChanged(style.id),
          ),
      ],
    );
  }
}
