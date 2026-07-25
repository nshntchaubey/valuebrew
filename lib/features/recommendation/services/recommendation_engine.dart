import 'package:valuebrew/data/models/catalog.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/recommendation/scoring/similarity_strategy.dart';
import 'package:valuebrew/features/recommendation/scoring/weighted_scorer.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';

/// V1 of ValueBrew's recommendation engine: ranks SKUs by similarity to a
/// reference SKU, and finds "better value" alternatives among comparable
/// SKUs.
///
/// This is pure business logic — no Flutter or Riverpod dependency in
/// this file (see `providers/recommendation_providers.dart` for how a
/// future screen would obtain an instance). It reads
/// [Sku.valueScore]/[Sku.costPerMlAlcohol] as the catalog's existing
/// precomputed fields; it never recomputes a price or value metric from
/// scratch — the on-device Value Engine that would do that remains a
/// separate, already deferred milestone.
///
/// ### Complexity
/// Both [similarBeers] and [betterValueAlternatives] score every other
/// SKU in [catalog] exactly once against the reference SKU (O(n)), then
/// sort the results (O(n log n)). Neither method compares candidates
/// against each other, so this stays O(n log n) overall regardless of
/// catalog size — at 5,000+ SKUs this is still a single-digit-millisecond
/// operation. If catalog size ever grows enough that even this becomes a
/// real cost (e.g. called on every frame of a scrolling list rather than
/// once per screen), the natural next step is pre-grouping SKUs by
/// `styleId` once and only scoring within the reference SKU's style
/// group — a change to how candidates are gathered, not to the scoring
/// model itself.
class RecommendationEngine {
  /// Creates a [RecommendationEngine].
  ///
  /// [similarityScorer] defaults to a V1 weighting across style, ABV,
  /// price, package type, and brewery (see [_defaultSimilarityScorer]) —
  /// reasonable starting weights, not empirically tuned. Inject a
  /// different [WeightedScorer] (different strategies, different
  /// weights) without needing any other change to this class or its
  /// callers.
  RecommendationEngine({WeightedScorer? similarityScorer})
      : similarityScorer = similarityScorer ?? _defaultSimilarityScorer;

  /// Combines individual [SimilarityStrategy] scores into the single
  /// score [similarBeers] ranks by.
  final WeightedScorer similarityScorer;

  static final WeightedScorer _defaultSimilarityScorer = WeightedScorer({
    const StyleMatchStrategy(): 3.0,
    const AbvClosenessStrategy(): 2.0,
    const PriceClosenessStrategy(): 1.5,
    const PackageTypeMatchStrategy(): 1.0,
    const BreweryMatchStrategy(): 0.5,
  });

  /// How close two SKUs' ABV must be, in percentage points, to count as
  /// "a similar alcohol level" for [betterValueAlternatives]'s filtering.
  ///
  /// Distinct from [AbvClosenessStrategy]'s smooth `[0.0, 1.0]` scoring
  /// (used for *ranking* in [similarBeers]) — this is a hard yes/no gate
  /// (used for *filtering* candidates in [betterValueAlternatives]),
  /// because "better value" needs a comparable-or-not decision, not a
  /// degree of similarity to rank by.
  static const double comparableAbvTolerance = 1.5;

  /// Returns every other SKU in [catalog], ranked by similarity to
  /// [beer], most similar first.
  ///
  /// "Similarity" is whatever [similarityScorer] computes. [beer] itself
  /// is excluded from the result. Ties are broken by [catalog]'s SKU
  /// order, for deterministic results.
  List<Sku> similarBeers(Sku beer, Catalog catalog) {
    final candidates = catalog.skus.where((sku) => sku.id != beer.id).toList();
    return _rankedDescending(
      candidates,
      (candidate) => similarityScorer.score(beer, candidate, catalog),
    );
  }

  /// Returns every SKU in [catalog] that represents a genuinely better
  /// deal than [beer]: the same style, a comparable ABV (within
  /// [comparableAbvTolerance] of [beer]'s), and a higher `valueScore`
  /// than [beer]'s own — ranked by `valueScore` descending (best value
  /// first).
  ///
  /// This is deliberately not "cheapest first": a SKU of a different
  /// style, or with a meaningfully different ABV, isn't a comparable
  /// drinking experience, so it's excluded regardless of price.
  List<Sku> betterValueAlternatives(Sku beer, Catalog catalog) {
    final referenceBeer = resolveBeer(catalog, beer.beerId);
    if (referenceBeer == null) return const [];

    final candidates = catalog.skus.where((candidate) {
      if (candidate.id == beer.id) return false;
      if (candidate.valueScore <= beer.valueScore) return false;
      if ((candidate.abv - beer.abv).abs() > comparableAbvTolerance) return false;

      final candidateBeer = resolveBeer(catalog, candidate.beerId);
      return candidateBeer != null && candidateBeer.styleId == referenceBeer.styleId;
    }).toList();

    return _rankedDescending(candidates, (candidate) => candidate.valueScore.toDouble());
  }

  /// Sorts [candidates] by [scoreOf], descending, with ties broken by
  /// [candidates]' original order — the same `(score, originalIndex)`
  /// pattern already used by `HomeScreen`'s and `BeerDetailScreen`'s
  /// sorting, and for the same reason: [List.sort] alone doesn't
  /// guarantee stability.
  List<Sku> _rankedDescending(List<Sku> candidates, double Function(Sku) scoreOf) {
    final indexed = candidates.asMap().entries.toList()
      ..sort((a, b) {
        final scoreComparison = scoreOf(b.value).compareTo(scoreOf(a.value));
        if (scoreComparison != 0) return scoreComparison;
        return a.key.compareTo(b.key);
      });
    return [for (final entry in indexed) entry.value];
  }
}
