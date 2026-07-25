/// A typed, user-facing reason a SKU was recommended.
///
/// This exists so [RecommendationEngine] never hands the UI a raw string —
/// each value here is produced by a specific [SimilarityStrategy] (or, for
/// [betterValue], by [RecommendationEngine.betterValueAlternatives]'s own
/// value-improvement gate) recognizing that its own dimension is a strong
/// enough match to be worth telling the user about. See
/// `recommendation.dart` for how these are collected into a
/// [Recommendation].
///
/// Adding a new reason (e.g. once a `BitternessClosenessStrategy` exists —
/// see `similarity_strategy.dart`'s own note on deferred flavour
/// dimensions) means adding one value here and one `explain` case in the
/// strategy that produces it — nothing else needs to change.
enum RecommendationReason {
  /// Contributed by [StyleMatchStrategy] when both SKUs' beers share a
  /// style.
  sameStyle,

  /// Contributed by [BreweryMatchStrategy] when both SKUs' beers share a
  /// brewery.
  sameBrewery,

  /// Contributed by [AbvClosenessStrategy] when two SKUs' ABV is close
  /// enough to be worth mentioning (not merely "closer than the absolute
  /// maximum" — see that strategy's own explain threshold).
  similarAbv,

  /// Contributed by [PriceClosenessStrategy] when two SKUs' cost per ml of
  /// alcohol is close enough to be worth mentioning.
  similarPrice,

  /// Contributed by [PackageTypeMatchStrategy] when both SKUs are the same
  /// package type.
  samePackage,

  /// Contributed directly by [RecommendationEngine.betterValueAlternatives]
  /// — not by any [SimilarityStrategy] — when a candidate meets its
  /// value-improvement gate. There is no "value closeness" scoring
  /// dimension in [WeightedScorer]; this reason reflects that method's own
  /// business rule instead.
  betterValue,
}

/// User-facing display text for a [RecommendationReason], used to build a
/// recommendation's subtitle (e.g. "Same style • Similar ABV").
extension RecommendationReasonFormatting on RecommendationReason {
  String get displayLabel => switch (this) {
        RecommendationReason.sameStyle => 'Same style',
        RecommendationReason.sameBrewery => 'Same brewery',
        RecommendationReason.similarAbv => 'Similar ABV',
        RecommendationReason.similarPrice => 'Similar price',
        RecommendationReason.samePackage => 'Same package',
        RecommendationReason.betterValue => 'Better value',
      };
}
