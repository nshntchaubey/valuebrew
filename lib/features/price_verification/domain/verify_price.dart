import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/features/price_verification/domain/price_verification_result.dart';

/// Computes the verification delta for [chargedPrice] against
/// [legalPrice]: whether the charged price sits at, above, or below the
/// legal reference — the Beer Knowledge Model's own definition of this
/// capability. Pure Dart, deterministic, no Flutter dependency.
PriceVerificationResult verifyPrice({
  required double chargedPrice,
  required double legalPrice,
}) {
  final PriceVerificationVerdict verdict;
  final String explanation;

  if (chargedPrice == legalPrice) {
    verdict = PriceVerificationVerdict.atLegalPrice;
    explanation = 'You paid ${chargedPrice.currencyLabel}, exactly the legal price.';
  } else if (chargedPrice < legalPrice) {
    verdict = PriceVerificationVerdict.belowLegalPrice;
    explanation =
        'You paid ${chargedPrice.currencyLabel}, below the legal price of '
        '${legalPrice.currencyLabel}.';
  } else {
    verdict = PriceVerificationVerdict.aboveLegalPrice;
    explanation =
        'You paid ${chargedPrice.currencyLabel}, above the legal price of '
        '${legalPrice.currencyLabel}. This may be an overcharge.';
  }

  return PriceVerificationResult(
    verdict: verdict,
    chargedPrice: chargedPrice,
    legalPrice: legalPrice,
    explanation: explanation,
  );
}
