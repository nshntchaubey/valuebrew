import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/beer.dart';

void main() {
  group('Beer', () {
    const beer = Beer(
      id: 'kf_premium',
      name: 'Kingfisher Premium',
      brewery: 'United Breweries',
      styleId: 'lager',
      isCraft: false,
    );

    test('constructor assigns all fields', () {
      expect(beer.id, 'kf_premium');
      expect(beer.name, 'Kingfisher Premium');
      expect(beer.brewery, 'United Breweries');
      expect(beer.styleId, 'lager');
      expect(beer.isCraft, isFalse);
    });

    test('fromJson parses a valid JSON map', () {
      final json = {
        'id': 'toit_white_ale',
        'name': 'Toit White Ale',
        'brewery': 'Toit Brewpub',
        'style_id': 'wheat',
        'is_craft': true,
      };

      final result = Beer.fromJson(json);

      expect(result.id, 'toit_white_ale');
      expect(result.name, 'Toit White Ale');
      expect(result.brewery, 'Toit Brewpub');
      expect(result.styleId, 'wheat');
      expect(result.isCraft, isTrue);
    });

    test('toJson produces the expected JSON map', () {
      expect(beer.toJson(), {
        'id': 'kf_premium',
        'name': 'Kingfisher Premium',
        'brewery': 'United Breweries',
        'style_id': 'lager',
        'is_craft': false,
      });
    });

    test('fromJson -> toJson round-trips to an equivalent map', () {
      final json = {
        'id': 'simba_strong',
        'name': 'Simba Strong',
        'brewery': 'Kals Brewing',
        'style_id': 'strong_lager',
        'is_craft': false,
      };

      expect(Beer.fromJson(json).toJson(), json);
    });

    test('two instances with identical field values are equal', () {
      const other = Beer(
        id: 'kf_premium',
        name: 'Kingfisher Premium',
        brewery: 'United Breweries',
        styleId: 'lager',
        isCraft: false,
      );

      expect(beer, equals(other));
      expect(beer.hashCode, equals(other.hashCode));
    });

    test('instances differing by id are not equal', () {
      const other = Beer(
        id: 'kf_ultra',
        name: 'Kingfisher Premium',
        brewery: 'United Breweries',
        styleId: 'lager',
        isCraft: false,
      );

      expect(beer, isNot(equals(other)));
    });

    test('instances differing by name are not equal', () {
      const other = Beer(
        id: 'kf_premium',
        name: 'Kingfisher Ultra',
        brewery: 'United Breweries',
        styleId: 'lager',
        isCraft: false,
      );

      expect(beer, isNot(equals(other)));
    });

    test('instances differing by brewery are not equal', () {
      const other = Beer(
        id: 'kf_premium',
        name: 'Kingfisher Premium',
        brewery: 'Some Other Brewery',
        styleId: 'lager',
        isCraft: false,
      );

      expect(beer, isNot(equals(other)));
    });

    test('instances differing by styleId are not equal', () {
      const other = Beer(
        id: 'kf_premium',
        name: 'Kingfisher Premium',
        brewery: 'United Breweries',
        styleId: 'strong_lager',
        isCraft: false,
      );

      expect(beer, isNot(equals(other)));
    });

    test('instances differing by isCraft are not equal', () {
      const other = Beer(
        id: 'kf_premium',
        name: 'Kingfisher Premium',
        brewery: 'United Breweries',
        styleId: 'lager',
        isCraft: true,
      );

      expect(beer, isNot(equals(other)));
    });

    test('copyWith with no arguments returns an equal instance', () {
      final copy = beer.copyWith();

      expect(copy, equals(beer));
      expect(identical(copy, beer), isFalse);
    });

    test('copyWith overrides only the given fields', () {
      final copy = beer.copyWith(name: 'Kingfisher Premium Lager');

      expect(copy.id, beer.id);
      expect(copy.name, 'Kingfisher Premium Lager');
      expect(copy.brewery, beer.brewery);
      expect(copy.styleId, beer.styleId);
      expect(copy.isCraft, beer.isCraft);
    });

    test('copyWith can override every field', () {
      final copy = beer.copyWith(
        id: 'arbor_ipa',
        name: 'Arbor IPA',
        brewery: 'Arbor Brewing Company',
        styleId: 'ipa',
        isCraft: true,
      );

      expect(copy.id, 'arbor_ipa');
      expect(copy.name, 'Arbor IPA');
      expect(copy.brewery, 'Arbor Brewing Company');
      expect(copy.styleId, 'ipa');
      expect(copy.isCraft, isTrue);
    });

    test('toString includes all field values', () {
      final result = beer.toString();

      expect(result, contains('kf_premium'));
      expect(result, contains('Kingfisher Premium'));
      expect(result, contains('United Breweries'));
      expect(result, contains('lager'));
      expect(result, contains('false'));
    });
  });
}
