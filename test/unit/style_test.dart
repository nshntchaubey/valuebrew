import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/catalog/domain/style.dart';

void main() {
  group('Style', () {
    const style = Style(
      id: 'lager',
      name: 'Lager',
      description: 'Crisp, mild bitterness',
    );

    test('constructor assigns all fields', () {
      expect(style.id, 'lager');
      expect(style.name, 'Lager');
      expect(style.description, 'Crisp, mild bitterness');
    });

    test('fromJson parses a valid JSON map', () {
      final json = {
        'id': 'stout',
        'name': 'Stout',
        'description': 'Dark, roasted malt character',
      };

      final result = Style.fromJson(json);

      expect(result.id, 'stout');
      expect(result.name, 'Stout');
      expect(result.description, 'Dark, roasted malt character');
    });

    test('toJson produces the expected JSON map', () {
      expect(style.toJson(), {
        'id': 'lager',
        'name': 'Lager',
        'description': 'Crisp, mild bitterness',
      });
    });

    test('fromJson -> toJson round-trips to an equivalent map', () {
      final json = {
        'id': 'ipa',
        'name': 'IPA',
        'description': 'Hop-forward, bitter',
      };

      expect(Style.fromJson(json).toJson(), json);
    });

    test('two instances with identical field values are equal', () {
      const other = Style(
        id: 'lager',
        name: 'Lager',
        description: 'Crisp, mild bitterness',
      );

      expect(style, equals(other));
      expect(style.hashCode, equals(other.hashCode));
    });

    test('instances differing by id are not equal', () {
      const other = Style(
        id: 'wheat',
        name: 'Lager',
        description: 'Crisp, mild bitterness',
      );

      expect(style, isNot(equals(other)));
    });

    test('instances differing by name are not equal', () {
      const other = Style(
        id: 'lager',
        name: 'Pilsner',
        description: 'Crisp, mild bitterness',
      );

      expect(style, isNot(equals(other)));
    });

    test('instances differing by description are not equal', () {
      const other = Style(
        id: 'lager',
        name: 'Lager',
        description: 'Something else entirely',
      );

      expect(style, isNot(equals(other)));
    });

    test('copyWith with no arguments returns an equal instance', () {
      final copy = style.copyWith();

      expect(copy, equals(style));
      expect(identical(copy, style), isFalse);
    });

    test('copyWith overrides only the given fields', () {
      final copy = style.copyWith(name: 'Session Lager');

      expect(copy.id, style.id);
      expect(copy.name, 'Session Lager');
      expect(copy.description, style.description);
    });

    test('copyWith can override every field', () {
      final copy = style.copyWith(
        id: 'sour',
        name: 'Sour',
        description: 'Tart, acidic',
      );

      expect(copy.id, 'sour');
      expect(copy.name, 'Sour');
      expect(copy.description, 'Tart, acidic');
    });
  });
}
