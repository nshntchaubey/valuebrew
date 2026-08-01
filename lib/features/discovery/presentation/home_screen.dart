import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/navigation/value_brew_navigator.dart';

/// The canonical Home screen — the product's sole entry point.
///
/// This is the first implemented portion of the Home Screen Contract, not
/// a partial or provisional version of it: the full three-path, five-state
/// contract remains the authoritative target, and the remaining paths
/// (Search/Browse Results, Price Verification) and states (Clarifying,
/// Out-of-Scope, Recovering) arrive incrementally, the same way this one
/// did — when a real need pulls them in.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('ValueBrew')),
      body: Center(
        child: ElevatedButton(
          onPressed: () => ref.read(valueBrewNavigatorProvider).homeToRecommendation(),
          child: const Text('Get a recommendation'),
        ),
      ),
    );
  }
}
