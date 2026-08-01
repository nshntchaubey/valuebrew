import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/sorting/models/sort_option.dart';
import 'package:valuebrew/features/sorting/services/sorting_engine.dart';

Sku _sku({
  required String id,
  required String beerId,
  double abv = 5.0,
  double price = 100.0,
  int valueScore = 50,
}) {
  return Sku(
    id: id,
    beerId: beerId,
    sizeMl: 650,
    packageType: PackageType.bottle,
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
  const engine = SortingEngine();

  // A fixture with distinguishable name/brewery/value/price/ABV per beer:
  // - zebra: highest value (90), cheapest (50), lowest ABV (4.0).
  // - apple: lowest value (50), most expensive (100), highest ABV (8.0).
  // - middle: mid value (70), mid price (75), mid ABV (6.0).
  // - tie: same value as middle (70), used to prove stable tie-breaking.
  // - noSku: no SKUs at all — always sorts last on SKU-dependent options.
  const zebra = Beer(id: 'zebra', name: 'Zebra Lager', brewery: 'Zulu Brewing', styleId: 'lager', isCraft: false);
  const apple = Beer(id: 'apple', name: 'Apple Ale', brewery: 'Apple Brewing', styleId: 'ale', isCraft: false);
  const middle = Beer(id: 'middle', name: 'Middle IPA', brewery: 'Middle Brewing', styleId: 'ipa', isCraft: false);
  const tie = Beer(id: 'tie', name: 'Tie Stout', brewery: 'Tie Brewing', styleId: 'stout', isCraft: false);
  const noSku = Beer(id: 'no_sku', name: 'No Sku Beer', brewery: 'Zzz Brewing', styleId: 'lager', isCraft: false);

  final beers = [zebra, apple, middle, tie, noSku];

  final skus = [
    _sku(id: 'zebra_sku', beerId: 'zebra', abv: 4.0, price: 50, valueScore: 90),
    _sku(id: 'apple_sku', beerId: 'apple', abv: 8.0, price: 100, valueScore: 50),
    _sku(id: 'middle_sku', beerId: 'middle', abv: 6.0, price: 75, valueScore: 70),
    _sku(id: 'tie_sku', beerId: 'tie', abv: 6.0, price: 75, valueScore: 70),
  ];

  group('relevance', () {
    test('returns the beer list unchanged, without touching skus at all', () {
      expect(engine.apply(beers, SortOption.relevance, skus), same(beers));
    });
  });

  group('bestValue', () {
    test('orders descending by best-value SKU valueScore, no-SKU beers last', () {
      final result = engine.apply(beers, SortOption.bestValue, skus);
      expect(result.map((b) => b.id), ['zebra', 'middle', 'tie', 'apple', 'no_sku']);
    });

    test('ties are broken by original list order', () {
      final result = engine.apply(beers, SortOption.bestValue, skus);
      final middleIndex = result.indexOf(middle);
      final tieIndex = result.indexOf(tie);
      // middle appears before tie in `beers`, and both score 70.
      expect(middleIndex, lessThan(tieIndex));
    });
  });

  group('priceLowToHigh', () {
    test('orders ascending by cheapest SKU price, no-SKU beers last', () {
      final result = engine.apply(beers, SortOption.priceLowToHigh, skus);
      expect(result.map((b) => b.id), ['zebra', 'middle', 'tie', 'apple', 'no_sku']);
    });
  });

  group('priceHighToLow', () {
    test('orders descending by cheapest SKU price, no-SKU beers last', () {
      final result = engine.apply(beers, SortOption.priceHighToLow, skus);
      expect(result.map((b) => b.id), ['apple', 'middle', 'tie', 'zebra', 'no_sku']);
    });
  });

  group('abvLowToHigh', () {
    test('orders ascending by representative SKU ABV, no-SKU beers last', () {
      final result = engine.apply(beers, SortOption.abvLowToHigh, skus);
      expect(result.map((b) => b.id), ['zebra', 'middle', 'tie', 'apple', 'no_sku']);
    });
  });

  group('abvHighToLow', () {
    test('orders descending by representative SKU ABV, no-SKU beers last', () {
      final result = engine.apply(beers, SortOption.abvHighToLow, skus);
      expect(result.map((b) => b.id), ['apple', 'middle', 'tie', 'zebra', 'no_sku']);
    });
  });

  group('nameAToZ', () {
    test('orders alphabetically by name, case-insensitively', () {
      final result = engine.apply(beers, SortOption.nameAToZ, skus);
      expect(result.map((b) => b.id), ['apple', 'middle', 'no_sku', 'tie', 'zebra']);
    });
  });

  group('breweryAToZ', () {
    test('orders alphabetically by brewery, case-insensitively', () {
      final result = engine.apply(beers, SortOption.breweryAToZ, skus);
      expect(result.map((b) => b.id), ['apple', 'middle', 'tie', 'zebra', 'no_sku']);
    });
  });

  group('edge cases', () {
    test('an empty beer list returns an empty list for every option', () {
      for (final option in SortOption.values) {
        expect(engine.apply(const [], option, skus), isEmpty, reason: '$option');
      }
    });

    test('a single-beer list is returned as-is for every option', () {
      for (final option in SortOption.values) {
        expect(engine.apply([zebra], option, skus).map((b) => b.id), ['zebra'], reason: '$option');
      }
    });

    test('ordering is deterministic: repeated calls produce the same result', () {
      final first = engine.apply(beers, SortOption.bestValue, skus).map((b) => b.id).toList();
      final second = engine.apply(beers, SortOption.bestValue, skus).map((b) => b.id).toList();
      expect(first, second);
    });

    test('sorting does not mutate the input list', () {
      final original = List<Beer>.of(beers);
      engine.apply(beers, SortOption.bestValue, skus);
      expect(beers, original);
    });
  });
}
