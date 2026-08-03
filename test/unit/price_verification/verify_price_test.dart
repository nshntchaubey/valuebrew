import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/features/price_verification/domain/price_verification_result.dart';
import 'package:valuebrew/features/price_verification/domain/verify_price.dart';

void main() {
  group('verifyPrice', () {
    test('a charged price exactly equal to the legal price is classified atLegalPrice', () {
      final result = verifyPrice(chargedPrice: 110, legalPrice: 110);

      expect(result.verdict, PriceVerificationVerdict.atLegalPrice);
    });

    test('a charged price below the legal price is classified belowLegalPrice', () {
      final result = verifyPrice(chargedPrice: 100, legalPrice: 110);

      expect(result.verdict, PriceVerificationVerdict.belowLegalPrice);
    });

    test('a charged price above the legal price is classified aboveLegalPrice', () {
      final result = verifyPrice(chargedPrice: 120, legalPrice: 110);

      expect(result.verdict, PriceVerificationVerdict.aboveLegalPrice);
    });

    test('the atLegalPrice explanation states the price plainly, with no discrepancy language', () {
      final result = verifyPrice(chargedPrice: 110, legalPrice: 110);

      expect(result.explanation, 'You paid ₹110, exactly the legal price.');
    });

    test('the belowLegalPrice explanation names both prices, never as a problem', () {
      final result = verifyPrice(chargedPrice: 100, legalPrice: 110);

      expect(result.explanation, 'You paid ₹100, below the legal price of ₹110.');
    });

    test('the aboveLegalPrice explanation names both prices and flags a possible overcharge', () {
      final result = verifyPrice(chargedPrice: 120, legalPrice: 110);

      expect(
        result.explanation,
        'You paid ₹120, above the legal price of ₹110. This may be an overcharge.',
      );
    });

    test('preserves the exact chargedPrice and legalPrice values used', () {
      final result = verifyPrice(chargedPrice: 100, legalPrice: 110);

      expect(result.chargedPrice, 100);
      expect(result.legalPrice, 110);
    });
  });
}
