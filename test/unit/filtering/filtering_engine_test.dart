import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/filtering/models/abv_range.dart';
import 'package:valuebrew/features/filtering/models/filter_state.dart';
import 'package:valuebrew/features/filtering/models/price_range.dart';
import 'package:valuebrew/features/filtering/services/filtering_engine.dart';

Sku _sku({
  required String id,
  required String beerId,
  double abv = 5.0,
  double price = 100.0,
  PackageType packageType = PackageType.bottle,
  int valueScore = 50,
}) {
  return Sku(
    id: id,
    beerId: beerId,
    sizeMl: 650,
    packageType: packageType,
    abv: abv,
    calories: 250,
    price: price,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: 150,
    costPerMlAlcohol: 4.0,
    valueScore: valueScore,
    valueVerdict: ValueVerdict.fairValue,
  );
}

void main() {
  const engine = FilteringEngine();

  // A fixture built so each filter dimension is independently
  // distinguishable:
  // - kf (lager, United Breweries): two SKUs — a cheap, low-ABV bottle
  //   (78 value score) and an expensive, high-ABV can (40 value score).
  //   No single SKU is both low-ABV *and* cheap *and* a can — used to
  //   prove filters must be satisfied by the same SKU, not mixed across
  //   a beer's SKUs.
  // - toit (stout, Toit Brewpub): one mid-range can.
  // - simba (lager, Kals Brewing): one high-ABV, high-value can.
  // - ghost (lager, United Breweries): no SKUs at all.
  const kf = Beer(id: 'kf', name: 'Kingfisher Premium', brewery: 'United Breweries', styleId: 'lager', isCraft: false);
  const toit = Beer(id: 'toit', name: 'Toit Porter', brewery: 'Toit Brewpub', styleId: 'stout', isCraft: true);
  const simba = Beer(id: 'simba', name: 'Simba Strong', brewery: 'Kals Brewing', styleId: 'lager', isCraft: false);
  const ghost = Beer(id: 'ghost', name: 'Ghost Lager', brewery: 'United Breweries', styleId: 'lager', isCraft: false);

  final beers = [kf, toit, simba, ghost];

  final kfBottle = _sku(id: 'kf_bottle', beerId: 'kf', abv: 4.8, price: 110, packageType: PackageType.bottle, valueScore: 78);
  final kfCan = _sku(id: 'kf_can', beerId: 'kf', abv: 8.0, price: 250, packageType: PackageType.can, valueScore: 40);
  final toitCan = _sku(id: 'toit_can', beerId: 'toit', abv: 6.5, price: 250, packageType: PackageType.can, valueScore: 55);
  final simbaCan = _sku(id: 'simba_can', beerId: 'simba', abv: 8.0, price: 150, packageType: PackageType.can, valueScore: 82);

  final skus = [kfBottle, kfCan, toitCan, simbaCan];

  group('no filters active', () {
    test('returns the beer list unchanged', () {
      expect(engine.apply(beers, FilterState.none, skus), same(beers));
    });
  });

  group('style filter', () {
    test('matches only beers of that style, including one with no SKUs', () {
      final result = engine.apply(beers, FilterState.none.withStyle('lager'), skus);
      expect(result, [kf, simba, ghost]);
    });

    test('excludes every beer when no beer has that style', () {
      final result = engine.apply(beers, FilterState.none.withStyle('ipa'), skus);
      expect(result, isEmpty);
    });
  });

  group('brewery filter', () {
    test('matches only beers from that brewery, including one with no SKUs', () {
      final result = engine.apply(beers, FilterState.none.withBrewery('United Breweries'), skus);
      expect(result, [kf, ghost]);
    });
  });

  group('ABV range filter', () {
    test('matches a beer with at least one SKU inside the range', () {
      final result = engine.apply(
        beers,
        FilterState.none.withAbvRange(AbvRange(min: 4.0, max: 5.0)),
        skus,
      );
      // Only kf_bottle (4.8) falls in [4.0, 5.0].
      expect(result, [kf]);
    });

    test('is inclusive at the exact boundary', () {
      final result = engine.apply(
        beers,
        FilterState.none.withAbvRange(AbvRange(min: 4.8, max: 4.8)),
        skus,
      );
      expect(result, [kf]);
    });

    test('excludes a beer whose SKUs are all just outside the range', () {
      final result = engine.apply(
        beers,
        FilterState.none.withAbvRange(AbvRange(min: 4.9, max: 7.9)),
        skus,
      );
      // kf_bottle is 4.8 (just below 4.9), kf_can is 8.0 (just above 7.9).
      expect(result, isNot(contains(kf)));
    });

    test('excludes a beer with no SKUs at all', () {
      final result = engine.apply(
        beers,
        FilterState.none.withAbvRange(AbvRange(min: 0.0, max: 20.0)),
        skus,
      );
      expect(result, isNot(contains(ghost)));
    });
  });

  group('price range filter', () {
    test('matches a beer with at least one SKU inside the range', () {
      final result = engine.apply(
        beers,
        FilterState.none.withPriceRange(PriceRange(min: 100.0, max: 180.0)),
        skus,
      );
      // kf_bottle (110) and simba_can (150) qualify; toit_can (250) and
      // kf_can (250) do not.
      expect(result, [kf, simba]);
    });

    test('is inclusive at the exact boundary', () {
      final result = engine.apply(
        beers,
        FilterState.none.withPriceRange(PriceRange(min: 110.0, max: 110.0)),
        skus,
      );
      expect(result, [kf]);
    });
  });

  group('package type filter', () {
    test('matches beers with at least one SKU of that package type', () {
      final result = engine.apply(
        beers,
        FilterState.none.withPackageType(PackageType.bottle),
        skus,
      );
      // Only kf_bottle is a bottle.
      expect(result, [kf]);
    });

    test('excludes a beer whose only SKUs are a different package type', () {
      final result = engine.apply(
        beers,
        FilterState.none.withPackageType(PackageType.pint),
        skus,
      );
      expect(result, isEmpty);
    });
  });

  group('minimum value score filter', () {
    test('matches a beer with at least one SKU at or above the threshold', () {
      final result = engine.apply(
        beers,
        FilterState.none.withMinValueScore(75),
        skus,
      );
      // kf_bottle (78) and simba_can (82) qualify; kf_can (40) and
      // toit_can (55) do not.
      expect(result, [kf, simba]);
    });

    test('is inclusive at the exact boundary', () {
      final result = engine.apply(beers, FilterState.none.withMinValueScore(78), skus);
      expect(result, contains(kf));
    });

    test('excludes at one point above the boundary', () {
      final result = engine.apply(beers, FilterState.none.withMinValueScore(79), skus);
      expect(result, isNot(contains(kf)));
    });
  });

  group('multiple filters combine with AND', () {
    test('a beer matching every individual filter, but via different SKUs, does not match', () {
      // kf_bottle satisfies ABV [4,5] but not price [200,300];
      // kf_can satisfies price [200,300] but not ABV [4,5].
      // No single kf SKU satisfies both at once.
      final filters = FilterState.none
          .withAbvRange(AbvRange(min: 4.0, max: 5.0))
          .withPriceRange(PriceRange(min: 200.0, max: 300.0));

      final result = engine.apply(beers, filters, skus);

      expect(result, isNot(contains(kf)));
    });

    test('a beer with one SKU satisfying every active filter together does match', () {
      // simba_can: abv 8.0, price 150, package can, valueScore 82 —
      // satisfies all four SKU-level filters at once.
      final filters = FilterState.none
          .withAbvRange(AbvRange(min: 7.0, max: 9.0))
          .withPriceRange(PriceRange(min: 100.0, max: 200.0))
          .withPackageType(PackageType.can)
          .withMinValueScore(80);

      final result = engine.apply(beers, filters, skus);

      expect(result, [simba]);
    });

    test('beer-level and SKU-level filters combine together', () {
      final filters = FilterState.none.withStyle('lager').withMinValueScore(75);

      final result = engine.apply(beers, filters, skus);

      // kf (lager, 78) and simba (lager, 82) qualify; toit is the wrong
      // style; ghost has no SKUs to satisfy the value-score filter.
      expect(result, [kf, simba]);
    });
  });

  group('edge cases', () {
    test('no beers match when the filters are mutually exclusive', () {
      final filters = FilterState.none.withStyle('stout').withBrewery('United Breweries');
      final result = engine.apply(beers, filters, skus);
      expect(result, isEmpty);
    });

    test('every beer matches when the active filter excludes none of them', () {
      final filters = FilterState.none.withPriceRange(PriceRange(min: 0.0, max: 1000.0));
      final result = engine.apply(beers, filters, skus);
      // Every SKU-bearing beer has a SKU in [0, 1000]; ghost has no SKUs
      // so it's still excluded — a SKU-level filter can never be
      // satisfied by a beer with no SKUs.
      expect(result, [kf, toit, simba]);
    });

    test('a beer with no SKUs still matches when only beer-level filters are active', () {
      final filters = FilterState.none.withStyle('lager').withBrewery('United Breweries');
      final result = engine.apply(beers, filters, skus);
      expect(result, contains(ghost));
    });

    test('preserves the original beer order', () {
      final result = engine.apply(beers, FilterState.none.withStyle('lager'), skus);
      expect(result, [kf, simba, ghost]);
    });
  });
}
