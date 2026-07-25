import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/features/filtering/models/price_range.dart';

void main() {
  group('PriceRange', () {
    test('contains returns true for a value strictly inside the range', () {
      final range = PriceRange(min: 100.0, max: 200.0);
      expect(range.contains(150.0), isTrue);
    });

    test('contains is inclusive of both the min and max boundary', () {
      final range = PriceRange(min: 100.0, max: 200.0);
      expect(range.contains(100.0), isTrue);
      expect(range.contains(200.0), isTrue);
    });

    test('contains returns false just outside either boundary', () {
      final range = PriceRange(min: 100.0, max: 200.0);
      expect(range.contains(99.99), isFalse);
      expect(range.contains(200.01), isFalse);
    });

    test('throws ArgumentError when min is negative', () {
      expect(() => PriceRange(min: -1.0, max: 100.0), throwsArgumentError);
    });

    test('throws ArgumentError when max is less than min', () {
      expect(() => PriceRange(min: 200.0, max: 100.0), throwsArgumentError);
    });

    test('two ranges with identical bounds are equal', () {
      expect(PriceRange(min: 100.0, max: 200.0), PriceRange(min: 100.0, max: 200.0));
      expect(
        PriceRange(min: 100.0, max: 200.0).hashCode,
        PriceRange(min: 100.0, max: 200.0).hashCode,
      );
    });

    test('ranges differing by either bound are not equal', () {
      expect(PriceRange(min: 100.0, max: 200.0), isNot(PriceRange(min: 100.0, max: 250.0)));
      expect(PriceRange(min: 100.0, max: 200.0), isNot(PriceRange(min: 50.0, max: 200.0)));
    });
  });
}
