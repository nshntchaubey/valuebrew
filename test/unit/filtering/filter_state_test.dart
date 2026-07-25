import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/filtering/models/abv_range.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/models/price_range.dart';

void main() {
  group('FilterState.none', () {
    test('has every field null', () {
      const filters = FilterState.none;
      expect(filters.styleId, isNull);
      expect(filters.brewery, isNull);
      expect(filters.abvRange, isNull);
      expect(filters.priceRange, isNull);
      expect(filters.packageType, isNull);
      expect(filters.minValueScore, isNull);
    });

    test('is not active and has zero active filters', () {
      expect(FilterState.none.isActive, isFalse);
      expect(FilterState.none.activeFilterCount, 0);
      expect(FilterState.none.hasSkuLevelFilters, isFalse);
    });
  });

  group('activeFilterCount / isActive', () {
    test('counts exactly the fields that are set', () {
      final filters = FilterState.none.withStyle('lager').withBrewery('Toit Brewpub');
      expect(filters.activeFilterCount, 2);
      expect(filters.isActive, isTrue);
    });

    test('counts all six fields when every filter is active', () {
      final filters = FilterState.none
          .withStyle('lager')
          .withBrewery('Toit Brewpub')
          .withAbvRange(AbvRange(min: 4.0, max: 6.0))
          .withPriceRange(PriceRange(min: 100.0, max: 200.0))
          .withPackageType(PackageType.can)
          .withMinValueScore(50);
      expect(filters.activeFilterCount, 6);
    });
  });

  group('hasSkuLevelFilters', () {
    test('is false when only beer-level filters (style, brewery) are active', () {
      final filters = FilterState.none.withStyle('lager').withBrewery('Toit Brewpub');
      expect(filters.hasSkuLevelFilters, isFalse);
    });

    test('is true when any single SKU-level filter is active', () {
      expect(FilterState.none.withAbvRange(AbvRange(min: 4.0, max: 6.0)).hasSkuLevelFilters, isTrue);
      expect(
        FilterState.none.withPriceRange(PriceRange(min: 0.0, max: 100.0)).hasSkuLevelFilters,
        isTrue,
      );
      expect(FilterState.none.withPackageType(PackageType.can).hasSkuLevelFilters, isTrue);
      expect(FilterState.none.withMinValueScore(50).hasSkuLevelFilters, isTrue);
    });
  });

  group('withX methods', () {
    test('withStyle sets only styleId, leaving every other field untouched', () {
      final base = FilterState.none.withBrewery('Toit Brewpub').withMinValueScore(50);
      final updated = base.withStyle('lager');

      expect(updated.styleId, 'lager');
      expect(updated.brewery, 'Toit Brewpub');
      expect(updated.minValueScore, 50);
    });

    test('withStyle(null) clears styleId without touching other fields', () {
      final base = FilterState.none.withStyle('lager').withBrewery('Toit Brewpub');
      final updated = base.withStyle(null);

      expect(updated.styleId, isNull);
      expect(updated.brewery, 'Toit Brewpub');
    });

    test('withBrewery, withPackageType, and withMinValueScore each set only their own field', () {
      final base = FilterState.none.withStyle('lager');

      expect(base.withBrewery('Toit Brewpub').brewery, 'Toit Brewpub');
      expect(base.withPackageType(PackageType.can).packageType, PackageType.can);
      expect(base.withMinValueScore(80).minValueScore, 80);

      // Each still carries the base's styleId forward.
      expect(base.withBrewery('Toit Brewpub').styleId, 'lager');
    });

    test('withAbvRange and withPriceRange set only their own field', () {
      final base = FilterState.none.withStyle('lager');
      final abvRange = AbvRange(min: 4.0, max: 6.0);
      final priceRange = PriceRange(min: 100.0, max: 200.0);

      expect(base.withAbvRange(abvRange).abvRange, abvRange);
      expect(base.withPriceRange(priceRange).priceRange, priceRange);
      expect(base.withAbvRange(abvRange).styleId, 'lager');
    });
  });

  group('clear', () {
    test('returns a FilterState equal to FilterState.none regardless of what was active', () {
      final filters = FilterState.none
          .withStyle('lager')
          .withBrewery('Toit Brewpub')
          .withMinValueScore(50);

      expect(filters.clear(), FilterState.none);
    });
  });

  group('equality', () {
    test('two FilterStates with identical fields are equal', () {
      final a = FilterState.none.withStyle('lager').withMinValueScore(50);
      final b = FilterState.none.withStyle('lager').withMinValueScore(50);
      expect(a, b);
      expect(a.hashCode, b.hashCode);
    });

    test('FilterStates differing by any single field are not equal', () {
      final base = FilterState.none.withStyle('lager');
      expect(base, isNot(base.withBrewery('Toit Brewpub')));
      expect(base, isNot(FilterState.none.withStyle('ipa')));
    });
  });
}
