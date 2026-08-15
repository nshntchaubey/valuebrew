import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/shared_domain/sku.dart';

void main() {
  group('PackageType', () {
    test('fromJson parses each known value', () {
      expect(PackageType.fromJson('bottle'), PackageType.bottle);
      expect(PackageType.fromJson('can'), PackageType.can);
      expect(PackageType.fromJson('pint'), PackageType.pint);
    });

    test('fromJson throws on an unknown value', () {
      expect(() => PackageType.fromJson('keg'), throwsArgumentError);
    });

    test('toJson round-trips each value', () {
      for (final type in PackageType.values) {
        expect(PackageType.fromJson(type.toJson()), type);
      }
    });
  });

  group('ValueVerdict', () {
    test('fromJson parses each known value', () {
      expect(ValueVerdict.fromJson('great_value'), ValueVerdict.greatValue);
      expect(ValueVerdict.fromJson('fair_value'), ValueVerdict.fairValue);
      expect(ValueVerdict.fromJson('overpriced'), ValueVerdict.overpriced);
    });

    test('fromJson throws on an unknown value', () {
      expect(() => ValueVerdict.fromJson('terrible'), throwsArgumentError);
    });

    test('toJson round-trips each value', () {
      for (final verdict in ValueVerdict.values) {
        expect(ValueVerdict.fromJson(verdict.toJson()), verdict);
      }
    });
  });

  group('Sku', () {
    final sku = Sku(
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

    final json = {
      'id': 'kf_premium_650',
      'beer_id': 'kf_premium',
      'size_ml': 650,
      'package_type': 'bottle',
      'abv': 4.8,
      'calories': 260,
      'price': 110,
      'price_last_checked': '2026-07-20',
      'price_source': 'karnataka_excise_mrp_2026',
      'cost_per_litre': 169.2,
      'cost_per_ml_alcohol': 3.52,
      'value_score': 78,
      'value_verdict': 'great_value',
    };

    test('constructor assigns all fields', () {
      expect(sku.id, 'kf_premium_650');
      expect(sku.beerId, 'kf_premium');
      expect(sku.sizeMl, 650);
      expect(sku.packageType, PackageType.bottle);
      expect(sku.abv, 4.8);
      expect(sku.calories, 260);
      expect(sku.price, 110);
      expect(sku.priceLastChecked, DateTime(2026, 7, 20));
      expect(sku.priceSource, 'karnataka_excise_mrp_2026');
      expect(sku.costPerLitre, 169.2);
      expect(sku.costPerMlAlcohol, 3.52);
      expect(sku.valueScore, 78);
      expect(sku.valueVerdict, ValueVerdict.greatValue);
    });

    test('fromJson parses a valid JSON map', () {
      final result = Sku.fromJson(json);

      expect(result, equals(sku));
    });

    test('fromJson coerces an integer-valued price to double', () {
      final result = Sku.fromJson(json);

      expect(result.price, isA<double>());
      expect(result.price, 110.0);
    });

    test('fromJson accepts a decimal price without error', () {
      final decimalJson = {...json, 'price': 110.5};

      final result = Sku.fromJson(decimalJson);

      expect(result.price, 110.5);
    });

    test('fromJson coerces calories and value_score to int', () {
      final result = Sku.fromJson(json);

      expect(result.calories, isA<int>());
      expect(result.valueScore, isA<int>());
    });

    test('toJson produces the expected JSON map', () {
      expect(sku.toJson(), json);
    });

    test('fromJson -> toJson round-trips to an equivalent map', () {
      expect(Sku.fromJson(json).toJson(), json);
    });

    test('two instances with identical field values are equal', () {
      final other = Sku(
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

      expect(sku, equals(other));
      expect(sku.hashCode, equals(other.hashCode));
    });

    test('instances differing by id are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(id: 'kf_premium_330'))));
    });

    test('instances differing by beerId are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(beerId: 'kf_ultra'))));
    });

    test('instances differing by sizeMl are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(sizeMl: 330))));
    });

    test('instances differing by packageType are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(packageType: PackageType.can))));
    });

    test('instances differing by abv are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(abv: 5.0))));
    });

    test('instances differing by calories are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(calories: 200))));
    });

    test('instances differing by price are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(price: 120))));
    });

    test('instances differing by priceLastChecked are not equal', () {
      expect(
        sku,
        isNot(equals(sku.copyWith(priceLastChecked: DateTime(2026, 7, 21)))),
      );
    });

    test('instances differing by priceSource are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(priceSource: 'store_visit'))));
    });

    test('instances differing by costPerLitre are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(costPerLitre: 200.0))));
    });

    test('instances differing by costPerMlAlcohol are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(costPerMlAlcohol: 4.0))));
    });

    test('instances differing by valueScore are not equal', () {
      expect(sku, isNot(equals(sku.copyWith(valueScore: 50))));
    });

    test('instances differing by valueVerdict are not equal', () {
      expect(
        sku,
        isNot(equals(sku.copyWith(valueVerdict: ValueVerdict.overpriced))),
      );
    });

    test('copyWith with no arguments returns an equal instance', () {
      final copy = sku.copyWith();

      expect(copy, equals(sku));
      expect(identical(copy, sku), isFalse);
    });

    test('copyWith overrides only the given fields', () {
      final copy = sku.copyWith(price: 120, valueScore: 60);

      expect(copy.price, 120);
      expect(copy.valueScore, 60);
      expect(copy.id, sku.id);
      expect(copy.beerId, sku.beerId);
      expect(copy.sizeMl, sku.sizeMl);
      expect(copy.packageType, sku.packageType);
      expect(copy.abv, sku.abv);
      expect(copy.calories, sku.calories);
      expect(copy.priceLastChecked, sku.priceLastChecked);
      expect(copy.priceSource, sku.priceSource);
      expect(copy.costPerLitre, sku.costPerLitre);
      expect(copy.costPerMlAlcohol, sku.costPerMlAlcohol);
      expect(copy.valueVerdict, sku.valueVerdict);
    });

    test('copyWith can override every field', () {
      final copy = sku.copyWith(
        id: 'toit_white_ale_500',
        beerId: 'toit_white_ale',
        sizeMl: 500,
        packageType: PackageType.can,
        abv: 5.5,
        calories: 210,
        price: 350,
        priceLastChecked: DateTime(2026, 6, 1),
        priceSource: 'store_visit',
        costPerLitre: 700.0,
        costPerMlAlcohol: 12.73,
        valueScore: 20,
        valueVerdict: ValueVerdict.overpriced,
      );

      expect(copy.id, 'toit_white_ale_500');
      expect(copy.beerId, 'toit_white_ale');
      expect(copy.sizeMl, 500);
      expect(copy.packageType, PackageType.can);
      expect(copy.abv, 5.5);
      expect(copy.calories, 210);
      expect(copy.price, 350);
      expect(copy.priceLastChecked, DateTime(2026, 6, 1));
      expect(copy.priceSource, 'store_visit');
      expect(copy.costPerLitre, 700.0);
      expect(copy.costPerMlAlcohol, 12.73);
      expect(copy.valueScore, 20);
      expect(copy.valueVerdict, ValueVerdict.overpriced);
    });

    test('toString includes all field values', () {
      final result = sku.toString();

      expect(result, contains('kf_premium_650'));
      expect(result, contains('kf_premium'));
      expect(result, contains('650'));
      expect(result, contains('PackageType.bottle'));
      expect(result, contains('4.8'));
      expect(result, contains('260'));
      expect(result, contains('110'));
      expect(result, contains('karnataka_excise_mrp_2026'));
      expect(result, contains('169.2'));
      expect(result, contains('3.52'));
      expect(result, contains('78'));
      expect(result, contains('ValueVerdict.greatValue'));
    });
  });

  group('Sku with unknown calories (Product Decisions Register D22)', () {
    // D22 downgraded missing calories from a blocking publication rule to
    // a warning, so the catalog JSON may legitimately carry a null
    // "calories" value for a published SKU -- these guard against the
    // exact crash risk that motivated this group: `Sku.fromJson`
    // previously cast `json['calories']` straight to `num`, which throws
    // a `TypeError` on `null` rather than failing gracefully.
    final jsonWithNullCalories = {
      'id': 'kf_premium_650',
      'beer_id': 'kf_premium',
      'size_ml': 650,
      'package_type': 'bottle',
      'abv': 4.8,
      'calories': null,
      'price': 110,
      'price_last_checked': '2026-07-20',
      'price_source': 'karnataka_excise_mrp_2026',
      'cost_per_litre': 169.2,
      'cost_per_ml_alcohol': 3.52,
      'value_score': 78,
      'value_verdict': 'great_value',
    };

    test('fromJson parses a null calories value without throwing', () {
      final result = Sku.fromJson(jsonWithNullCalories);

      expect(result.calories, isNull);
    });

    test('fromJson leaves every other field unaffected by null calories', () {
      final result = Sku.fromJson(jsonWithNullCalories);

      expect(result.abv, 4.8);
      expect(result.price, 110.0);
      expect(result.valueScore, 78);
    });

    test('toJson serializes a null calories value as null', () {
      final sku = Sku.fromJson(jsonWithNullCalories);

      expect(sku.toJson()['calories'], isNull);
    });

    test('fromJson -> toJson round-trips a null calories value', () {
      expect(Sku.fromJson(jsonWithNullCalories).toJson(), jsonWithNullCalories);
    });

    test('constructor allows omitting calories, defaulting to null', () {
      final sku = Sku(
        id: 'kf_premium_650',
        beerId: 'kf_premium',
        sizeMl: 650,
        packageType: PackageType.bottle,
        abv: 4.8,
        price: 110,
        priceLastChecked: DateTime(2026, 7, 20),
        priceSource: 'karnataka_excise_mrp_2026',
        costPerLitre: 169.2,
        costPerMlAlcohol: 3.52,
        valueScore: 78,
        valueVerdict: ValueVerdict.greatValue,
      );

      expect(sku.calories, isNull);
    });

    test('a null-calories Sku and a known-calories Sku are not equal', () {
      final knownCalories = Sku.fromJson(
        jsonWithNullCalories,
      ).copyWith(calories: 260);
      final nullCalories = Sku.fromJson(jsonWithNullCalories);

      expect(nullCalories, isNot(equals(knownCalories)));
    });
  });
}
