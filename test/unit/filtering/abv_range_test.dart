import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/features/filtering/models/abv_range.dart';

void main() {
  group('AbvRange', () {
    test('contains returns true for a value strictly inside the range', () {
      final range = AbvRange(min: 4.0, max: 6.0);
      expect(range.contains(5.0), isTrue);
    });

    test('contains is inclusive of both the min and max boundary', () {
      final range = AbvRange(min: 4.0, max: 6.0);
      expect(range.contains(4.0), isTrue);
      expect(range.contains(6.0), isTrue);
    });

    test('contains returns false just outside either boundary', () {
      final range = AbvRange(min: 4.0, max: 6.0);
      expect(range.contains(3.9), isFalse);
      expect(range.contains(6.1), isFalse);
    });

    test('a zero-width range only contains its single value', () {
      final range = AbvRange(min: 5.0, max: 5.0);
      expect(range.contains(5.0), isTrue);
      expect(range.contains(4.9), isFalse);
      expect(range.contains(5.1), isFalse);
    });

    test('throws ArgumentError when min is negative', () {
      expect(() => AbvRange(min: -1.0, max: 5.0), throwsArgumentError);
    });

    test('throws ArgumentError when max is less than min', () {
      expect(() => AbvRange(min: 6.0, max: 4.0), throwsArgumentError);
    });

    test('two ranges with identical bounds are equal', () {
      expect(AbvRange(min: 4.0, max: 6.0), AbvRange(min: 4.0, max: 6.0));
      expect(AbvRange(min: 4.0, max: 6.0).hashCode, AbvRange(min: 4.0, max: 6.0).hashCode);
    });

    test('ranges differing by either bound are not equal', () {
      expect(AbvRange(min: 4.0, max: 6.0), isNot(AbvRange(min: 4.0, max: 7.0)));
      expect(AbvRange(min: 4.0, max: 6.0), isNot(AbvRange(min: 3.0, max: 6.0)));
    });
  });
}
