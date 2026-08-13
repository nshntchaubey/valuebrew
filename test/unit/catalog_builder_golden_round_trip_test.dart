// Milestone 7's own end-to-end proof: a catalog.json produced by the
// real Python Catalog Builder pipeline (tool/catalog_builder/tests/
// test_end_to_end_catalog_build.py) must deserialize successfully
// through the real, unmodified Flutter Catalog models — not a
// hand-authored fixture shaped to make this test pass, but the actual
// output of beer_master.csv + Beer YAMLs -> catalog.json.
//
// Regenerate the fixture this test reads via:
//   python3 -m pytest tool/catalog_builder/tests/test_end_to_end_catalog_build.py::test_write_catalog_and_manifest_and_golden_fixture

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/catalog.dart';
import 'package:valuebrew/shared_domain/sku.dart';

void main() {
  group('Catalog Builder golden round-trip', () {
    late Catalog catalog;

    setUpAll(() {
      final file = File('tool/catalog_builder/tests/fixtures/golden_catalog.json');
      expect(
        file.existsSync(),
        isTrue,
        reason:
            'golden_catalog.json missing — regenerate via: python3 -m pytest '
            'tool/catalog_builder/tests/test_end_to_end_catalog_build.py::'
            'test_write_catalog_and_manifest_and_golden_fixture',
      );
      final decoded = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
      catalog = Catalog.fromJson(decoded);
    });

    test('parses without throwing, via the real, unmodified Catalog.fromJson', () {
      expect(catalog, isNotNull);
    });

    test('catalog_version and generated_at round-trip correctly', () {
      expect(catalog.catalogVersion, 1);
      expect(catalog.generatedAt, DateTime.utc(2026, 8, 13, 12, 0, 0));
    });

    test('both real styles are present', () {
      expect(catalog.styles.length, 2);
      final lager = catalog.styles.firstWhere((s) => s.id == 'lager');
      expect(lager.name, 'Lager');
      final strongLager = catalog.styles.firstWhere((s) => s.id == 'strong_lager');
      expect(strongLager.name, 'Strong Lager');
    });

    test('both real beers are present with correct style references', () {
      expect(catalog.beers.length, 2);
      final kingfisher = catalog.beers.firstWhere((b) => b.id == 'kingfisher_premium');
      expect(kingfisher.name, 'Kingfisher Premium');
      expect(kingfisher.brewery, 'United Breweries');
      expect(kingfisher.styleId, 'lager');

      final tuborg = catalog.beers.firstWhere((b) => b.id == 'tuborg_strong');
      expect(tuborg.brewery, 'Carlsberg India');
      expect(tuborg.styleId, 'strong_lager');
    });

    test('the multi-SKU beer keeps every one of its SKUs', () {
      final kingfisherSkus = catalog.skus.where((s) => s.beerId == 'kingfisher_premium').toList();
      expect(kingfisherSkus.map((s) => s.id).toSet(), {'CP0000002', 'CP0000003'});
    });

    test('SKU fields match the real enriched/pipeline-sourced values exactly', () {
      final sku = catalog.skus.firstWhere((s) => s.id == 'CP0000002');
      expect(sku.sizeMl, 330);
      expect(sku.packageType, PackageType.can);
      expect(sku.abv, 4.8);
      expect(sku.calories, 165);
      expect(sku.price, 100.0);
      expect(sku.priceLastChecked, DateTime(2026, 6, 1));
      expect(sku.priceSource, 'karnataka_excise_mrp_2026');
    });

    test('a bottle-packaged SKU parses its package_type correctly', () {
      final sku = catalog.skus.firstWhere((s) => s.id == 'CP0000003');
      expect(sku.packageType, PackageType.bottle);
      expect(sku.sizeMl, 650);
    });

    test('the confirmed contamination row never reached the catalog', () {
      expect(catalog.skus.any((s) => s.id == 'CP0000001'), isFalse);
      expect(catalog.beers.any((b) => b.name.toLowerCase().contains('budweiser')), isFalse);
    });

    test('the unenriched row never reached the catalog', () {
      expect(catalog.skus.any((s) => s.id == 'CP0000099'), isFalse);
    });

    test('every SKU has a real cross-referenceable Beer', () {
      final beerIds = catalog.beers.map((b) => b.id).toSet();
      for (final sku in catalog.skus) {
        expect(beerIds.contains(sku.beerId), isTrue, reason: 'dangling beer_id: ${sku.beerId}');
      }
    });

    test('every Beer has a real cross-referenceable Style', () {
      final styleIds = catalog.styles.map((s) => s.id).toSet();
      for (final beer in catalog.beers) {
        expect(styleIds.contains(beer.styleId), isTrue, reason: 'dangling style_id: ${beer.styleId}');
      }
    });

    test('value_score and value_verdict are real, well-formed computed fields', () {
      for (final sku in catalog.skus) {
        expect(sku.valueScore, inInclusiveRange(0, 100));
        expect(ValueVerdict.values.contains(sku.valueVerdict), isTrue);
        expect(sku.costPerLitre, greaterThan(0));
        expect(sku.costPerMlAlcohol, greaterThan(0));
      }
    });

    test('both Style Benchmarks are present with correct sample sizes', () {
      expect(catalog.benchmarks.length, 2);
      final lagerBenchmark = catalog.benchmarks.firstWhere((b) => b.styleId == 'lager');
      expect(lagerBenchmark.sampleSize, 2);
      final strongLagerBenchmark = catalog.benchmarks.firstWhere((b) => b.styleId == 'strong_lager');
      expect(strongLagerBenchmark.sampleSize, 1);
    });

    test('toJson round-trips back to an equivalent structure', () {
      final reEncoded = catalog.toJson();
      final reParsed = Catalog.fromJson(reEncoded);
      expect(reParsed, catalog);
    });
  });
}
