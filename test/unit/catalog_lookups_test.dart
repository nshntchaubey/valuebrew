import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/catalog/domain/style.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';

Beer _beer(String id, {String styleId = 'lager'}) {
  return Beer(id: id, name: 'Beer $id', brewery: 'Brewery', styleId: styleId, isCraft: false);
}

Sku _sku(String id, {required String beerId}) {
  return Sku(
    id: id,
    beerId: beerId,
    sizeMl: 500,
    packageType: PackageType.bottle,
    abv: 5.0,
    calories: 150,
    price: 100,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: 200,
    costPerMlAlcohol: 2.0,
    valueScore: 50,
    valueVerdict: ValueVerdict.fairValue,
  );
}

void main() {
  final lager = Style(id: 'lager', name: 'Lager', description: 'Crisp');
  final beer = _beer('beer_1');
  final sku = _sku('sku_1', beerId: 'beer_1');
  const benchmark = Benchmark(
    styleId: 'lager',
    avgCostPerMlAlcohol: 4.10,
    p25: 3.40,
    p50: 3.95,
    p75: 4.60,
    sampleSize: 42,
  );
  final catalog = Catalog(
    catalogVersion: 1,
    generatedAt: DateTime(2026, 1, 1),
    styles: [lager],
    beers: [beer],
    skus: [sku],
    benchmarks: const [benchmark],
  );

  group('resolveBeer', () {
    test('returns the beer with a matching id', () {
      expect(resolveBeer(catalog, 'beer_1'), beer);
    });

    test('returns null when no beer matches', () {
      expect(resolveBeer(catalog, 'missing'), isNull);
    });
  });

  group('resolveStyle', () {
    test('returns the style with a matching id', () {
      expect(resolveStyle(catalog, 'lager'), lager);
    });

    test('returns null when no style matches', () {
      expect(resolveStyle(catalog, 'missing'), isNull);
    });
  });

  group('resolveSku', () {
    test('returns the SKU with a matching id', () {
      expect(resolveSku(catalog, 'sku_1'), sku);
    });

    test('returns null when no SKU matches', () {
      expect(resolveSku(catalog, 'missing'), isNull);
    });
  });

  group('resolveBenchmark', () {
    test('returns the benchmark for a matching style id', () {
      expect(resolveBenchmark(catalog, 'lager'), benchmark);
    });

    test('returns null when no benchmark matches', () {
      expect(resolveBenchmark(catalog, 'missing'), isNull);
    });
  });
}
