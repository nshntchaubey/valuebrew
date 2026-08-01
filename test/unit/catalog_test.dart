import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/catalog/domain/style.dart';

void main() {
  group('Catalog', () {
    const lager = Style(
      id: 'lager',
      name: 'Lager',
      description: 'Crisp, mild bitterness',
    );
    const stout = Style(
      id: 'stout',
      name: 'Stout',
      description: 'Dark, roasted malt character',
    );

    const kfPremium = Beer(
      id: 'kf_premium',
      name: 'Kingfisher Premium',
      brewery: 'United Breweries',
      styleId: 'lager',
      isCraft: false,
    );
    const toitPorter = Beer(
      id: 'toit_porter',
      name: 'Toit Porter',
      brewery: 'Toit Brewpub',
      styleId: 'stout',
      isCraft: true,
    );

    final kfPremium650 = Sku(
      id: 'kf_premium_650',
      beerId: 'kf_premium',
      sizeMl: 650,
      packageType: PackageType.bottle,
      abv: 4.8,
      calories: 260,
      price: 110,
      priceLastChecked: DateTime(2026, 7, 20),
      priceSource: 'karnataka_excise_mrp_2026',
      costPerLitre: 169.2,
      costPerMlAlcohol: 3.52,
      valueScore: 78,
      valueVerdict: ValueVerdict.greatValue,
    );
    final toitPorter330 = Sku(
      id: 'toit_porter_330',
      beerId: 'toit_porter',
      sizeMl: 330,
      packageType: PackageType.can,
      abv: 6.5,
      calories: 220,
      price: 250,
      priceLastChecked: DateTime(2026, 7, 18),
      priceSource: 'store_visit',
      costPerLitre: 757.6,
      costPerMlAlcohol: 11.66,
      valueScore: 22,
      valueVerdict: ValueVerdict.overpriced,
    );

    const lagerBenchmark = Benchmark(
      styleId: 'lager',
      avgCostPerMlAlcohol: 4.10,
      p25: 3.40,
      p50: 3.95,
      p75: 4.60,
      sampleSize: 42,
    );
    const stoutBenchmark = Benchmark(
      styleId: 'stout',
      avgCostPerMlAlcohol: 8.20,
      p25: 6.50,
      p50: 7.90,
      p75: 9.30,
      sampleSize: 15,
    );

    final catalog = Catalog(
      catalogVersion: 7,
      generatedAt: DateTime.utc(2026, 7, 25),
      styles: [lager, stout],
      beers: [kfPremium, toitPorter],
      skus: [kfPremium650, toitPorter330],
      benchmarks: [lagerBenchmark, stoutBenchmark],
    );

    final json = {
      'catalog_version': 7,
      'generated_at': '2026-07-25T00:00:00.000Z',
      'styles': [lager.toJson(), stout.toJson()],
      'beers': [kfPremium.toJson(), toitPorter.toJson()],
      'skus': [kfPremium650.toJson(), toitPorter330.toJson()],
      'benchmarks': [lagerBenchmark.toJson(), stoutBenchmark.toJson()],
    };

    test('constructor assigns all fields', () {
      expect(catalog.catalogVersion, 7);
      expect(catalog.generatedAt, DateTime.utc(2026, 7, 25));
      expect(catalog.styles, [lager, stout]);
      expect(catalog.beers, [kfPremium, toitPorter]);
      expect(catalog.skus, [kfPremium650, toitPorter330]);
      expect(catalog.benchmarks, [lagerBenchmark, stoutBenchmark]);
    });

    test('fromJson parses a valid JSON map', () {
      final result = Catalog.fromJson(json);

      expect(result, equals(catalog));
    });

    test('fromJson deserializes nested models correctly', () {
      final result = Catalog.fromJson(json);

      expect(result.styles.first, isA<Style>());
      expect(result.styles.first.id, 'lager');
      expect(result.beers.first, isA<Beer>());
      expect(result.beers.first.name, 'Kingfisher Premium');
      expect(result.skus.first, isA<Sku>());
      expect(result.skus.first.packageType, PackageType.bottle);
      expect(result.benchmarks.first, isA<Benchmark>());
      expect(result.benchmarks.first.sampleSize, 42);
    });

    test('toJson produces the expected JSON map', () {
      expect(catalog.toJson(), json);
    });

    test('toJson serializes nested models as JSON maps, not objects', () {
      final result = catalog.toJson();

      expect(result['styles'], isA<List<dynamic>>());
      expect((result['styles'] as List)[0], isA<Map<String, dynamic>>());
      expect(
        (result['styles'] as List)[0],
        {'id': 'lager', 'name': 'Lager', 'description': 'Crisp, mild bitterness'},
      );
    });

    test('fromJson -> toJson round-trips to an equivalent map', () {
      expect(Catalog.fromJson(json).toJson(), json);
    });

    test('two instances with identical field values are equal', () {
      final other = Catalog(
        catalogVersion: 7,
        generatedAt: DateTime.utc(2026, 7, 25),
        styles: [lager, stout],
        beers: [kfPremium, toitPorter],
        skus: [kfPremium650, toitPorter330],
        benchmarks: [lagerBenchmark, stoutBenchmark],
      );

      expect(catalog, equals(other));
      expect(catalog.hashCode, equals(other.hashCode));
    });

    test('instances differing by catalogVersion are not equal', () {
      expect(catalog, isNot(equals(catalog.copyWith(catalogVersion: 8))));
    });

    test('instances differing by generatedAt are not equal', () {
      expect(
        catalog,
        isNot(equals(catalog.copyWith(generatedAt: DateTime.utc(2026, 7, 26)))),
      );
    });

    test('instances differing by styles are not equal', () {
      expect(catalog, isNot(equals(catalog.copyWith(styles: [lager]))));
    });

    test('instances differing by beers are not equal', () {
      expect(catalog, isNot(equals(catalog.copyWith(beers: [kfPremium]))));
    });

    test('instances differing by skus are not equal', () {
      expect(catalog, isNot(equals(catalog.copyWith(skus: [kfPremium650]))));
    });

    test('instances differing by benchmarks are not equal', () {
      expect(
        catalog,
        isNot(equals(catalog.copyWith(benchmarks: [lagerBenchmark]))),
      );
    });

    test('instances with same-length but differently-ordered lists are not equal', () {
      final reordered = catalog.copyWith(styles: [stout, lager]);

      expect(catalog, isNot(equals(reordered)));
    });

    test('copyWith with no arguments returns an equal instance', () {
      final copy = catalog.copyWith();

      expect(copy, equals(catalog));
      expect(identical(copy, catalog), isFalse);
    });

    test('copyWith overrides only the given fields', () {
      final copy = catalog.copyWith(catalogVersion: 8);

      expect(copy.catalogVersion, 8);
      expect(copy.generatedAt, catalog.generatedAt);
      expect(copy.styles, catalog.styles);
      expect(copy.beers, catalog.beers);
      expect(copy.skus, catalog.skus);
      expect(copy.benchmarks, catalog.benchmarks);
    });

    test('copyWith can override every field', () {
      final copy = catalog.copyWith(
        catalogVersion: 8,
        generatedAt: DateTime.utc(2026, 8, 1),
        styles: [lager],
        beers: [kfPremium],
        skus: [kfPremium650],
        benchmarks: [lagerBenchmark],
      );

      expect(copy.catalogVersion, 8);
      expect(copy.generatedAt, DateTime.utc(2026, 8, 1));
      expect(copy.styles, [lager]);
      expect(copy.beers, [kfPremium]);
      expect(copy.skus, [kfPremium650]);
      expect(copy.benchmarks, [lagerBenchmark]);
    });

    test('toString includes version and collection sizes', () {
      final result = catalog.toString();

      expect(result, contains('7'));
      expect(result, contains('styles: 2'));
      expect(result, contains('beers: 2'));
      expect(result, contains('skus: 2'));
      expect(result, contains('benchmarks: 2'));
    });

    group('empty collections', () {
      final emptyCatalog = Catalog(
        catalogVersion: 1,
        generatedAt: DateTime.utc(2026, 1, 1),
        styles: const [],
        beers: const [],
        skus: const [],
        benchmarks: const [],
      );

      final emptyJson = {
        'catalog_version': 1,
        'generated_at': '2026-01-01T00:00:00.000Z',
        'styles': <dynamic>[],
        'beers': <dynamic>[],
        'skus': <dynamic>[],
        'benchmarks': <dynamic>[],
      };

      test('constructor accepts empty collections', () {
        expect(emptyCatalog.styles, isEmpty);
        expect(emptyCatalog.beers, isEmpty);
        expect(emptyCatalog.skus, isEmpty);
        expect(emptyCatalog.benchmarks, isEmpty);
      });

      test('fromJson parses empty collections', () {
        final result = Catalog.fromJson(emptyJson);

        expect(result.styles, isEmpty);
        expect(result.beers, isEmpty);
        expect(result.skus, isEmpty);
        expect(result.benchmarks, isEmpty);
      });

      test('toJson serializes empty collections as empty lists', () {
        expect(emptyCatalog.toJson(), emptyJson);
      });

      test('fromJson -> toJson round-trips an empty catalog', () {
        expect(Catalog.fromJson(emptyJson).toJson(), emptyJson);
      });

      test('two empty catalogs with identical scalar fields are equal', () {
        final other = Catalog(
          catalogVersion: 1,
          generatedAt: DateTime.utc(2026, 1, 1),
          styles: const [],
          beers: const [],
          skus: const [],
          benchmarks: const [],
        );

        expect(emptyCatalog, equals(other));
        expect(emptyCatalog.hashCode, equals(other.hashCode));
      });

      test('an empty catalog is not equal to a populated one', () {
        expect(emptyCatalog, isNot(equals(catalog)));
      });
    });
  });
}
