import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';

void main() {
  group('Benchmark', () {
    const benchmark = Benchmark(
      styleId: 'lager',
      avgCostPerMlAlcohol: 4.10,
      p25: 3.40,
      p50: 3.95,
      p75: 4.60,
      sampleSize: 42,
    );

    final json = {
      'style_id': 'lager',
      'avg_cost_per_ml_alcohol': 4.10,
      'p25': 3.40,
      'p50': 3.95,
      'p75': 4.60,
      'sample_size': 42,
    };

    test('constructor assigns all fields', () {
      expect(benchmark.styleId, 'lager');
      expect(benchmark.avgCostPerMlAlcohol, 4.10);
      expect(benchmark.p25, 3.40);
      expect(benchmark.p50, 3.95);
      expect(benchmark.p75, 4.60);
      expect(benchmark.sampleSize, 42);
    });

    test('fromJson parses a valid JSON map', () {
      final result = Benchmark.fromJson(json);

      expect(result, equals(benchmark));
    });

    test('fromJson coerces an integer-valued statistic to double', () {
      final integerJson = {...json, 'avg_cost_per_ml_alcohol': 4};

      final result = Benchmark.fromJson(integerJson);

      expect(result.avgCostPerMlAlcohol, isA<double>());
      expect(result.avgCostPerMlAlcohol, 4.0);
    });

    test('fromJson coerces sample_size to int', () {
      final result = Benchmark.fromJson(json);

      expect(result.sampleSize, isA<int>());
    });

    test('toJson produces the expected JSON map', () {
      expect(benchmark.toJson(), json);
    });

    test('fromJson -> toJson round-trips to an equivalent map', () {
      expect(Benchmark.fromJson(json).toJson(), json);
    });

    test('two instances with identical field values are equal', () {
      const other = Benchmark(
        styleId: 'lager',
        avgCostPerMlAlcohol: 4.10,
        p25: 3.40,
        p50: 3.95,
        p75: 4.60,
        sampleSize: 42,
      );

      expect(benchmark, equals(other));
      expect(benchmark.hashCode, equals(other.hashCode));
    });

    test('instances differing by styleId are not equal', () {
      expect(benchmark, isNot(equals(benchmark.copyWith(styleId: 'stout'))));
    });

    test('instances differing by avgCostPerMlAlcohol are not equal', () {
      expect(
        benchmark,
        isNot(equals(benchmark.copyWith(avgCostPerMlAlcohol: 5.0))),
      );
    });

    test('instances differing by p25 are not equal', () {
      expect(benchmark, isNot(equals(benchmark.copyWith(p25: 3.0))));
    });

    test('instances differing by p50 are not equal', () {
      expect(benchmark, isNot(equals(benchmark.copyWith(p50: 4.0))));
    });

    test('instances differing by p75 are not equal', () {
      expect(benchmark, isNot(equals(benchmark.copyWith(p75: 5.0))));
    });

    test('instances differing by sampleSize are not equal', () {
      expect(benchmark, isNot(equals(benchmark.copyWith(sampleSize: 10))));
    });

    test('copyWith with no arguments returns an equal instance', () {
      final copy = benchmark.copyWith();

      expect(copy, equals(benchmark));
      expect(identical(copy, benchmark), isFalse);
    });

    test('copyWith overrides only the given fields', () {
      final copy = benchmark.copyWith(sampleSize: 50);

      expect(copy.sampleSize, 50);
      expect(copy.styleId, benchmark.styleId);
      expect(copy.avgCostPerMlAlcohol, benchmark.avgCostPerMlAlcohol);
      expect(copy.p25, benchmark.p25);
      expect(copy.p50, benchmark.p50);
      expect(copy.p75, benchmark.p75);
    });

    test('copyWith can override every field', () {
      final copy = benchmark.copyWith(
        styleId: 'ipa',
        avgCostPerMlAlcohol: 6.2,
        p25: 5.0,
        p50: 6.0,
        p75: 7.5,
        sampleSize: 15,
      );

      expect(copy.styleId, 'ipa');
      expect(copy.avgCostPerMlAlcohol, 6.2);
      expect(copy.p25, 5.0);
      expect(copy.p50, 6.0);
      expect(copy.p75, 7.5);
      expect(copy.sampleSize, 15);
    });

    test('toString includes all field values', () {
      final result = benchmark.toString();

      expect(result, contains('lager'));
      expect(result, contains('4.1'));
      expect(result, contains('3.4'));
      expect(result, contains('3.95'));
      expect(result, contains('4.6'));
      expect(result, contains('42'));
    });
  });
}
