import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/features/beer_detail/domain/style_standing.dart';
import 'package:valuebrew/shared_domain/sku.dart';

Sku _sku({required double costPerMlAlcohol}) {
  return Sku(
    id: 'sku_1',
    beerId: 'beer_1',
    sizeMl: 500,
    packageType: PackageType.bottle,
    abv: 5.0,
    calories: 150,
    price: 100,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: 200,
    costPerMlAlcohol: costPerMlAlcohol,
    valueScore: 50,
    valueVerdict: ValueVerdict.fairValue,
  );
}

void main() {
  const benchmark = Benchmark(
    styleId: 'lager',
    avgCostPerMlAlcohol: 4.10,
    p25: 3.40,
    p50: 3.95,
    p75: 4.60,
    sampleSize: 42,
  );

  group('classifyStyleStanding', () {
    test('returns betterThanTypical when cost is below the style median', () {
      final sku = _sku(costPerMlAlcohol: 3.50);
      expect(classifyStyleStanding(sku, benchmark), StyleStanding.betterThanTypical);
    });

    test('returns typical when cost equals the style median exactly', () {
      final sku = _sku(costPerMlAlcohol: 3.95);
      expect(classifyStyleStanding(sku, benchmark), StyleStanding.typical);
    });

    test('returns worseThanTypical when cost is above the style median', () {
      final sku = _sku(costPerMlAlcohol: 4.20);
      expect(classifyStyleStanding(sku, benchmark), StyleStanding.worseThanTypical);
    });
  });
}
