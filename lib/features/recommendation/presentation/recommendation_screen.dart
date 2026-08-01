import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/features/recommendation/domain/generate_recommendation.dart';
import 'package:valuebrew/features/recommendation/domain/recommendation_result.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

/// The Recommendation screen — the smallest complete Recommendation
/// Vertical Slice.
///
/// Collects budget, the only user input gathered in this milestone, and
/// shows one real, explained recommendation computed by
/// [generateRecommendation] against the real catalog. See that function's
/// own doc comment for the extension seams intentionally left for later
/// (further preference gathering, real tie handling, the Beer Detail
/// hand-off, Planning Mode, Proxy-Buying Mode).
class RecommendationScreen extends ConsumerStatefulWidget {
  const RecommendationScreen({super.key});

  @override
  ConsumerState<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends ConsumerState<RecommendationScreen> {
  final _budgetController = TextEditingController();
  RecommendationResult? _result;
  bool _searched = false;
  String? _error;

  @override
  void dispose() {
    _budgetController.dispose();
    super.dispose();
  }

  void _generate(Catalog catalog) {
    final budget = double.tryParse(_budgetController.text);
    setState(() {
      if (budget == null) {
        _error = 'Enter a valid budget.';
        _searched = false;
        _result = null;
      } else {
        _error = null;
        _result = generateRecommendation(catalog, budget: budget);
        _searched = true;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final catalogAsync = ref.watch(catalogProvider);

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
                onPressed: () => _generate(catalog),
                child: const Text('Get a recommendation'),
              ),
              const SizedBox(height: 24),
              if (_searched) _RecommendationResultView(result: _result),
            ],
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Could not load the catalog: $error')),
      ),
    );
  }
}

class _RecommendationResultView extends StatelessWidget {
  const _RecommendationResultView({required this.result});

  final RecommendationResult? result;

  @override
  Widget build(BuildContext context) {
    if (result == null) {
      return const Text('No beer in the catalog fits that budget.');
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(result!.beer.name, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Text(result!.explanation),
      ],
    );
  }
}
