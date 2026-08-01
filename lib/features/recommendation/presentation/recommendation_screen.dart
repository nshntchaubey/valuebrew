import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/features/recommendation/domain/generate_recommendation.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_outcome.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

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
class RecommendationScreen extends ConsumerStatefulWidget {
  const RecommendationScreen({super.key});

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
                _RecommendationOutcomeView(outcome: outcome),
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
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Could not load the catalog: $error')),
      ),
    );
  }
}

/// Renders [outcome]'s content. Inspecting the concrete outcome type here
/// is legitimate — this is a rendering decision, not a refinability
/// decision (which belongs exclusively to
/// [RecommendationOutcome.canBeRefinedFurther]).
class _RecommendationOutcomeView extends StatelessWidget {
  const _RecommendationOutcomeView({required this.outcome});

  final RecommendationOutcome outcome;

  @override
  Widget build(BuildContext context) {
    return switch (outcome) {
      RecommendationFound(:final result) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(result.beer.name, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(result.explanation),
          ],
        ),
      NoRecommendationWithinBudget() => const Text('No beer in the catalog fits that budget.'),
      NoRecommendationMatchingStyle() =>
        const Text('No beer within your budget matches that style.'),
    };
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
