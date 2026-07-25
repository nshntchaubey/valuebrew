import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';

/// A single, composable dimension of similarity between two SKUs.
///
/// Each strategy scores independently in `[0.0, 1.0]` — `0.0` meaning
/// maximally different on this one dimension, `1.0` meaning identical —
/// and knows nothing about any other dimension. [WeightedScorer] (see
/// `weighted_scorer.dart`) combines multiple strategies into one overall
/// score. This is what keeps adding a new scoring dimension a matter of
/// writing one new class and adding it to a weight map — never touching
/// an existing strategy, and never a giant switch statement.
///
/// Each strategy also [explain]s itself: whether the same comparison
/// [score] made is strong enough to be worth telling a user about, as a
/// [RecommendationReason]. This reuses each strategy's own comparison (via
/// a private helper shared with [score]) rather than re-deriving it — the
/// explanation is a by-product of scoring, not a second, separately
/// maintained set of rules.
///
/// V1 has no data source for beer-flavour attributes like IBU, bitterness,
/// sweetness, or body — none of those fields exist anywhere in the
/// catalog schema yet. This interface is deliberately shaped so that once
/// they do, a `BitternessClosenessStrategy` (etc.) is exactly as simple to
/// add as any strategy already below — no engine or scorer changes
/// required. See the milestone report for why these were designed for,
/// not implemented, this time.
abstract class SimilarityStrategy {
  /// A short, stable identifier for this strategy — used as the key in a
  /// `WeightedScorer`'s weight map, and useful when debugging why two
  /// SKUs scored the way they did.
  String get name;

  /// Returns a similarity score in `[0.0, 1.0]` between [a] and [b].
  /// [catalog] is available for any cross-referencing a strategy needs
  /// (e.g. resolving each SKU's beer to compare styles).
  double score(Sku a, Sku b, Catalog catalog);

  /// Returns the [RecommendationReason] this strategy contributes when [a]
  /// and [b] are similar enough on this dimension to be worth explaining
  /// to a user, or `null` if not.
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog);
}

/// Scores `1.0` if [a] and [b]'s beers share the same style, `0.0`
/// otherwise (including if either beer can't be resolved).
class StyleMatchStrategy implements SimilarityStrategy {
  const StyleMatchStrategy();

  @override
  String get name => 'style_match';

  @override
  double score(Sku a, Sku b, Catalog catalog) => _stylesMatch(a, b, catalog) ? 1.0 : 0.0;

  @override
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog) =>
      _stylesMatch(a, b, catalog) ? RecommendationReason.sameStyle : null;

  bool _stylesMatch(Sku a, Sku b, Catalog catalog) {
    final beerA = resolveBeer(catalog, a.beerId);
    final beerB = resolveBeer(catalog, b.beerId);
    if (beerA == null || beerB == null) return false;
    return beerA.styleId == beerB.styleId;
  }
}

/// Scores how close [a] and [b]'s ABV is: `1.0` at identical ABV,
/// decreasing linearly to `0.0` at [maxDifference] percentage points
/// apart or further.
class AbvClosenessStrategy implements SimilarityStrategy {
  const AbvClosenessStrategy({this.maxDifference = 4.0});

  /// The ABV difference, in percentage points, beyond which two SKUs are
  /// considered to have no similarity on this dimension at all.
  final double maxDifference;

  /// The minimum [score] for two SKUs' ABV to be considered "similar
  /// enough" to mention to a user — half of [maxDifference]'s worth of
  /// closeness, a simple, self-consistent bar rather than a separately
  /// configurable threshold.
  static const double _explainThreshold = 0.5;

  @override
  String get name => 'abv_closeness';

  @override
  double score(Sku a, Sku b, Catalog catalog) => _closeness(a, b);

  @override
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog) =>
      _closeness(a, b) >= _explainThreshold ? RecommendationReason.similarAbv : null;

  double _closeness(Sku a, Sku b) {
    final difference = (a.abv - b.abv).abs();
    if (difference >= maxDifference) return 0.0;
    return 1.0 - (difference / maxDifference);
  }
}

/// Scores how close [a] and [b]'s cost per ml of alcohol is: `1.0` at
/// identical cost, decreasing linearly to `0.0` at
/// [maxRelativeDifference] proportional difference or further.
///
/// Reads [Sku.costPerMlAlcohol] as the catalog's existing precomputed
/// field — this never recomputes a price/value metric from scratch. The
/// on-device Value Engine that would do that remains a separate, already
/// deferred milestone (see this milestone's report).
class PriceClosenessStrategy implements SimilarityStrategy {
  const PriceClosenessStrategy({this.maxRelativeDifference = 0.75});

  /// The proportional difference in cost-per-ml-alcohol, relative to the
  /// cheaper of the two, beyond which two SKUs are considered to have no
  /// similarity on this dimension at all.
  final double maxRelativeDifference;

  /// The minimum [score] for two SKUs' cost to be considered "similar
  /// enough" to mention to a user — see
  /// [AbvClosenessStrategy._explainThreshold] for why this is a fixed
  /// proportion rather than a separately configurable threshold.
  static const double _explainThreshold = 0.5;

  @override
  String get name => 'price_closeness';

  @override
  double score(Sku a, Sku b, Catalog catalog) => _closeness(a, b);

  @override
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog) =>
      _closeness(a, b) >= _explainThreshold ? RecommendationReason.similarPrice : null;

  double _closeness(Sku a, Sku b) {
    final lower = a.costPerMlAlcohol < b.costPerMlAlcohol
        ? a.costPerMlAlcohol
        : b.costPerMlAlcohol;
    final higher = a.costPerMlAlcohol < b.costPerMlAlcohol
        ? b.costPerMlAlcohol
        : a.costPerMlAlcohol;
    if (lower <= 0) return 0.0;
    final relativeDifference = (higher - lower) / lower;
    if (relativeDifference >= maxRelativeDifference) return 0.0;
    return 1.0 - (relativeDifference / maxRelativeDifference);
  }
}

/// Scores `1.0` if [a] and [b] are the same [PackageType] (bottle/can/
/// pint), `0.0` otherwise.
class PackageTypeMatchStrategy implements SimilarityStrategy {
  const PackageTypeMatchStrategy();

  @override
  String get name => 'package_type_match';

  @override
  double score(Sku a, Sku b, Catalog catalog) => _packagesMatch(a, b) ? 1.0 : 0.0;

  @override
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog) =>
      _packagesMatch(a, b) ? RecommendationReason.samePackage : null;

  bool _packagesMatch(Sku a, Sku b) => a.packageType == b.packageType;
}

/// Scores `1.0` if [a] and [b]'s beers share the same brewery, `0.0`
/// otherwise (including if either beer can't be resolved).
class BreweryMatchStrategy implements SimilarityStrategy {
  const BreweryMatchStrategy();

  @override
  String get name => 'brewery_match';

  @override
  double score(Sku a, Sku b, Catalog catalog) => _breweriesMatch(a, b, catalog) ? 1.0 : 0.0;

  @override
  RecommendationReason? explain(Sku a, Sku b, Catalog catalog) =>
      _breweriesMatch(a, b, catalog) ? RecommendationReason.sameBrewery : null;

  bool _breweriesMatch(Sku a, Sku b, Catalog catalog) {
    final beerA = resolveBeer(catalog, a.beerId);
    final beerB = resolveBeer(catalog, b.beerId);
    if (beerA == null || beerB == null) return false;
    return beerA.brewery == beerB.brewery;
  }
}
