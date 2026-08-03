import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/beer_detail/presentation/beer_detail_screen.dart';
import 'package:valuebrew/features/price_verification/presentation/price_verification_screen.dart';
import 'package:valuebrew/features/recommendation/presentation/recommendation_screen.dart';

/// The [Navigator] key every screen transition in the app goes through.
///
/// Shared between [ValueBrewNavigator] (which uses it to push) and the
/// root [MaterialApp], which is wired to it as `navigatorKey`.
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
  ///
  /// [isPlanning] carries a Planning Mode intent through as a flagged
  /// variant of this same transition — per the Home Screen Contract, "not
  /// a fourth distinct destination" — rather than a separate edge.
  Future<void> homeToRecommendation({bool isPlanning = false}) {
    return _navigatorKey.currentState!.push<void>(
      MaterialPageRoute(builder: (_) => RecommendationScreen(isPlanning: isPlanning)),
    );
  }

  /// Recommendation → Beer Detail (Navigation Contract, Section 6).
  ///
  /// Reachable only from a [RecommendationFound] outcome — the caller
  /// passes the id of the SKU already chosen there. Pushes directly, same
  /// as [homeToRecommendation]: still exactly one caller and one
  /// destination per edge, so a route table isn't earned yet.
  Future<void> recommendationToBeerDetail(String skuId) {
    return _navigatorKey.currentState!.push<void>(
      MaterialPageRoute(builder: (_) => BeerDetailScreen(skuId: skuId)),
    );
  }

  /// Beer Detail → Price Verification (Navigation Contract, Section 6).
  ///
  /// Invitation-only — reachable only from an explicit request on an
  /// already-identified SKU. Pushes directly, same as the other two
  /// edges: still exactly one caller and one destination per edge, so a
  /// route table isn't earned yet.
  Future<void> beerDetailToPriceVerification(String skuId) {
    return _navigatorKey.currentState!.push<void>(
      MaterialPageRoute(builder: (_) => PriceVerificationScreen(skuId: skuId)),
    );
  }

  /// Price Verification → Beer Detail (Navigation Contract, Section 6).
  ///
  /// Invitation-only, for broader context beyond the verification itself —
  /// reachable only from an already-resolved SKU. Carries the SKU identity
  /// only; the charged price is never carried forward, per the Navigation
  /// Contract's own Section 12. Pushes directly, same as the other edges:
  /// still exactly one caller and one destination per edge, so a route
  /// table isn't earned yet.
  Future<void> priceVerificationToBeerDetail(String skuId) {
    return _navigatorKey.currentState!.push<void>(
      MaterialPageRoute(builder: (_) => BeerDetailScreen(skuId: skuId)),
    );
  }
}

/// Exposes the app's [ValueBrewNavigator].
final valueBrewNavigatorProvider = Provider<ValueBrewNavigator>((ref) {
  return ValueBrewNavigator(rootNavigatorKey);
});
