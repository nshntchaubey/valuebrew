import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/recommendation/presentation/recommendation_screen.dart';

/// The [Navigator] key every screen transition in the app goes through.
///
/// Shared between [ValueBrewNavigator] (which uses it to push) and the
/// root [MaterialApp] (which will be wired to it as `navigatorKey` once
/// the new Home screen becomes the app's default entry point).
final rootNavigatorKey = GlobalKey<NavigatorState>();

/// The only thing in the app allowed to trigger a screen transition.
///
/// Its public API is exactly the Navigation Contract's edge list: one
/// method per legal transition between canonical screens, added only once
/// a real screen genuinely needs it — never spun up ahead of that need.
/// An illegal edge simply has no corresponding method; there is nothing to
/// call for it.
class ValueBrewNavigator {
  const ValueBrewNavigator(this._navigatorKey);

  final GlobalKey<NavigatorState> _navigatorKey;

  /// Home → Recommendation (Navigation Contract, Section 6).
  ///
  /// Pushes directly to [RecommendationScreen] rather than a named route —
  /// there is exactly one caller and one destination so far, so a route
  /// table isn't earned yet.
  Future<void> homeToRecommendation() {
    return _navigatorKey.currentState!.push<void>(
      MaterialPageRoute(builder: (_) => const RecommendationScreen()),
    );
  }
}

/// Exposes the app's [ValueBrewNavigator].
final valueBrewNavigatorProvider = Provider<ValueBrewNavigator>((ref) {
  return ValueBrewNavigator(rootNavigatorKey);
});
