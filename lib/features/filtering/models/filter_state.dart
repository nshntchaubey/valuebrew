import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/filtering/models/abv_range.dart';
import 'package:valuebrew/features/filtering/models/price_range.dart';

/// The currently active set of catalog filters — every field is optional,
/// and a `null` field means "not filtering on this dimension at all."
///
/// This is a strongly typed model rather than a `Map<String, dynamic>` or a
/// pile of loosely-related nullable variables, specifically so the set of
/// supported filters is visible in one place (this class's fields) and
/// adding a new filter is a one-field addition here, not a new string key
/// that has to be remembered and kept in sync everywhere it's read.
///
/// [styleId] and [brewery] describe a [Beer] directly. [abvRange],
/// [priceRange], [packageType], and [minValueScore] describe a [Sku] —
/// see `FilteringEngine`'s own doc comment for how a beer with several
/// SKUs is matched against those.
class FilterState {
  /// Creates a [FilterState]. Every field defaults to `null` (inactive) —
  /// [FilterState.none] is the equivalent no-args constant.
  const FilterState({
    this.styleId,
    this.brewery,
    this.abvRange,
    this.priceRange,
    this.packageType,
    this.minValueScore,
  });

  /// No filters active on any dimension.
  static const FilterState none = FilterState();

  /// Only beers whose [Beer.styleId] equals this. `null` means any style.
  final String? styleId;

  /// Only beers whose [Beer.brewery] equals this. `null` means any
  /// brewery.
  final String? brewery;

  /// Only SKUs whose ABV falls within this range. `null` means any ABV.
  final AbvRange? abvRange;

  /// Only SKUs whose price falls within this range. `null` means any
  /// price.
  final PriceRange? priceRange;

  /// Only SKUs of this [PackageType]. `null` means any package type.
  final PackageType? packageType;

  /// Only SKUs whose `valueScore` is at least this. `null` means no
  /// minimum.
  ///
  /// An `int`, matching [Sku.valueScore]'s own type and its documented
  /// `0`–`100` range — not a separate decimal scale.
  final int? minValueScore;

  /// Whether any filter is currently active.
  bool get isActive => activeFilterCount > 0;

  /// How many of the six filters are currently active — what a "3 filters
  /// active" indicator reads directly.
  int get activeFilterCount {
    return <Object?>[
      styleId,
      brewery,
      abvRange,
      priceRange,
      packageType,
      minValueScore,
    ].where((value) => value != null).length;
  }

  /// Whether any of the SKU-level filters ([abvRange], [priceRange],
  /// [packageType], [minValueScore]) is active.
  ///
  /// A beer with no SKUs at all can never satisfy any of these — see
  /// `FilteringEngine`.
  bool get hasSkuLevelFilters {
    return abvRange != null || priceRange != null || packageType != null || minValueScore != null;
  }

  /// Returns a copy with [styleId] replaced — pass `null` to clear it.
  FilterState withStyle(String? styleId) {
    return FilterState(
      styleId: styleId,
      brewery: brewery,
      abvRange: abvRange,
      priceRange: priceRange,
      packageType: packageType,
      minValueScore: minValueScore,
    );
  }

  /// Returns a copy with [brewery] replaced — pass `null` to clear it.
  FilterState withBrewery(String? brewery) {
    return FilterState(
      styleId: styleId,
      brewery: brewery,
      abvRange: abvRange,
      priceRange: priceRange,
      packageType: packageType,
      minValueScore: minValueScore,
    );
  }

  /// Returns a copy with [abvRange] replaced — pass `null` to clear it.
  FilterState withAbvRange(AbvRange? abvRange) {
    return FilterState(
      styleId: styleId,
      brewery: brewery,
      abvRange: abvRange,
      priceRange: priceRange,
      packageType: packageType,
      minValueScore: minValueScore,
    );
  }

  /// Returns a copy with [priceRange] replaced — pass `null` to clear it.
  FilterState withPriceRange(PriceRange? priceRange) {
    return FilterState(
      styleId: styleId,
      brewery: brewery,
      abvRange: abvRange,
      priceRange: priceRange,
      packageType: packageType,
      minValueScore: minValueScore,
    );
  }

  /// Returns a copy with [packageType] replaced — pass `null` to clear it.
  FilterState withPackageType(PackageType? packageType) {
    return FilterState(
      styleId: styleId,
      brewery: brewery,
      abvRange: abvRange,
      priceRange: priceRange,
      packageType: packageType,
      minValueScore: minValueScore,
    );
  }

  /// Returns a copy with [minValueScore] replaced — pass `null` to clear
  /// it.
  FilterState withMinValueScore(int? minValueScore) {
    return FilterState(
      styleId: styleId,
      brewery: brewery,
      abvRange: abvRange,
      priceRange: priceRange,
      packageType: packageType,
      minValueScore: minValueScore,
    );
  }

  /// Returns [FilterState.none] — every filter cleared at once.
  FilterState clear() => FilterState.none;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is FilterState &&
            other.styleId == styleId &&
            other.brewery == brewery &&
            other.abvRange == abvRange &&
            other.priceRange == priceRange &&
            other.packageType == packageType &&
            other.minValueScore == minValueScore);
  }

  @override
  int get hashCode {
    return Object.hash(styleId, brewery, abvRange, priceRange, packageType, minValueScore);
  }

  @override
  String toString() {
    return 'FilterState(styleId: $styleId, brewery: $brewery, '
        'abvRange: $abvRange, priceRange: $priceRange, '
        'packageType: $packageType, minValueScore: $minValueScore)';
  }
}
