import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/shared_domain/sku.dart';

void main() {
  group('CurrencyFormatting', () {
    test('formats a whole-number amount without a trailing .0', () {
      expect(110.0.currencyLabel, '₹110');
    });

    test('formats a non-whole amount with its decimal portion', () {
      expect(110.5.currencyLabel, '₹110.5');
    });

    test('formats zero as a whole number', () {
      expect(0.0.currencyLabel, '₹0');
    });
  });

  group('VolumeFormatting', () {
    test('formats a millilitre size with a space and mL unit', () {
      expect(650.volumeLabel, '650 mL');
      expect(500.volumeLabel, '500 mL');
    });
  });

  group('PackageTypeFormatting', () {
    test('capitalizes each package type', () {
      expect(PackageType.bottle.displayLabel, 'Bottle');
      expect(PackageType.can.displayLabel, 'Can');
      expect(PackageType.pint.displayLabel, 'Pint');
    });
  });

  group('ValueVerdictFormatting', () {
    test('matches the existing verdict wording exactly', () {
      expect(ValueVerdict.greatValue.displayLabel, 'Great value');
      expect(ValueVerdict.fairValue.displayLabel, 'Fair value');
      expect(ValueVerdict.overpriced.displayLabel, 'Overpriced for this ABV');
    });
  });
}
