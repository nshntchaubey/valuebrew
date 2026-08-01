import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/sorting/models/sort_option.dart';

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
  const beer = Beer(
    id: 'kf',
    name: 'Kingfisher Premium',
    brewery: 'United Breweries',
    styleId: 'lager',
    isCraft: false,
  );

  group('displayLabel', () {
    test('every option has a non-empty, distinct displayLabel', () {
      final labels = SortOption.values.map((o) => o.displayLabel).toSet();
      expect(labels.length, SortOption.values.length);
      for (final option in SortOption.values) {
        expect(option.displayLabel, isNotEmpty, reason: '$option');
      }
    });
  });

  group('preservesIncomingOrder', () {
    test('is true only for relevance', () {
      for (final option in SortOption.values) {
        expect(option.preservesIncomingOrder, option == SortOption.relevance, reason: '$option');
      }
    });
  });

  group('descending', () {
    test('bestValue, priceHighToLow, and abvHighToLow sort highest first', () {
      expect(SortOption.bestValue.descending, isTrue);
      expect(SortOption.priceHighToLow.descending, isTrue);
      expect(SortOption.abvHighToLow.descending, isTrue);
    });

    test('priceLowToHigh, abvLowToHigh, nameAToZ, and breweryAToZ sort lowest/first first', () {
      expect(SortOption.priceLowToHigh.descending, isFalse);
      expect(SortOption.abvLowToHigh.descending, isFalse);
      expect(SortOption.nameAToZ.descending, isFalse);
      expect(SortOption.breweryAToZ.descending, isFalse);
    });
  });

  group('sortKey', () {
    final sku = _sku(id: 'kf_650', beerId: 'kf', abv: 4.8, price: 110, valueScore: 78);
    final bestSkuByBeerId = {'kf': sku};
    final cheapestSkuByBeerId = {'kf': sku};

    test('bestValue reads the best-value SKU\'s valueScore', () {
      expect(
        SortOption.bestValue.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        78,
      );
    });

    test('priceLowToHigh and priceHighToLow both read the cheapest SKU\'s price', () {
      expect(
        SortOption.priceLowToHigh.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        110.0,
      );
      expect(
        SortOption.priceHighToLow.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        110.0,
      );
    });

    test('abvLowToHigh and abvHighToLow both read the best-value SKU\'s abv', () {
      expect(
        SortOption.abvLowToHigh.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        4.8,
      );
      expect(
        SortOption.abvHighToLow.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        4.8,
      );
    });

    test('nameAToZ and breweryAToZ read the beer\'s own fields, lower-cased', () {
      expect(
        SortOption.nameAToZ.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        'kingfisher premium',
      );
      expect(
        SortOption.breweryAToZ.sortKey(beer, bestSkuByBeerId, cheapestSkuByBeerId),
        'united breweries',
      );
    });

    test('SKU-dependent options return null when the beer has no SKU data', () {
      expect(SortOption.bestValue.sortKey(beer, {}, {}), isNull);
      expect(SortOption.priceLowToHigh.sortKey(beer, {}, {}), isNull);
      expect(SortOption.abvLowToHigh.sortKey(beer, {}, {}), isNull);
    });

    test('nameAToZ and breweryAToZ never return null, regardless of SKU data', () {
      expect(SortOption.nameAToZ.sortKey(beer, {}, {}), isNotNull);
      expect(SortOption.breweryAToZ.sortKey(beer, {}, {}), isNotNull);
    });
  });
}
