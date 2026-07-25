import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/core/utils/fuzzy_match.dart';

void main() {
  group('levenshtein', () {
    test('is zero for identical strings', () {
      expect(levenshtein('kingfisher', 'kingfisher'), 0);
    });

    test('is the length of the other string when one is empty', () {
      expect(levenshtein('', 'kingfisher'), 10);
      expect(levenshtein('kingfisher', ''), 10);
    });

    test('counts a single substitution as distance 1', () {
      expect(levenshtein('toit', 'tout'), 1);
    });

    test('counts a single insertion as distance 1', () {
      expect(levenshtein('simba', 'simbaa'), 1);
    });

    test('counts a single deletion as distance 1', () {
      expect(levenshtein('simba', 'simb'), 1);
    });

    test('is case-sensitive', () {
      expect(levenshtein('Toit', 'toit'), 1);
    });
  });

  group('scoreMatch', () {
    test('matches (with the lowest score) when the query is empty', () {
      expect(scoreMatch('', 'Kingfisher Premium'), greaterThan(0));
      expect(scoreMatch('   ', 'Kingfisher Premium'), greaterThan(0));
    });

    test('scores an exact, case-insensitive match highest', () {
      final exact = scoreMatch('kingfisher premium', 'Kingfisher Premium');
      final prefix = scoreMatch('kingfisher', 'Kingfisher Premium');
      expect(exact, greaterThan(prefix));
    });

    test('scores a prefix match above a plain substring match', () {
      final prefix = scoreMatch('king', 'Kingfisher Premium');
      final substring = scoreMatch('fisher', 'Kingfisher Premium');
      expect(prefix, greaterThan(substring));
    });

    test('scores a substring match above a fuzzy (typo) match', () {
      final substring = scoreMatch('fisher', 'Kingfisher Premium');
      final fuzzy = scoreMatch('kingfsiher premium', 'Kingfisher Premium');
      expect(substring, greaterThan(fuzzy));
      expect(fuzzy, greaterThan(0));
    });

    test('tolerates a small typo', () {
      // One transposed pair in "kingfisher" — well within tolerance.
      expect(scoreMatch('kingfsiher', 'Kingfisher Premium'), greaterThan(0));
    });

    test('does not match a query unrelated to the target', () {
      expect(scoreMatch('nonexistent', 'Kingfisher Premium'), 0);
    });

    test('does not match a query spanning two separate fields', () {
      // "Premium United" is not a substring or close typo of either the
      // beer name or the brewery alone.
      expect(scoreMatch('Premium United', 'Kingfisher Premium'), 0);
      expect(scoreMatch('Premium United', 'United Breweries'), 0);
    });
  });
}
