/// The three-way classification of a verification delta, per the Beer
/// Knowledge Model: whether an observed/charged price sits at, above, or
/// below the legal reference price.
enum PriceVerificationVerdict { atLegalPrice, belowLegalPrice, aboveLegalPrice }

/// The result of [verifyPrice]: the classification, the two prices it was
/// computed from, and a plain-language explanation.
class PriceVerificationResult {
  const PriceVerificationResult({
    required this.verdict,
    required this.chargedPrice,
    required this.legalPrice,
    required this.explanation,
  });

  final PriceVerificationVerdict verdict;
  final double chargedPrice;
  final double legalPrice;
  final String explanation;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is PriceVerificationResult &&
            other.verdict == verdict &&
            other.chargedPrice == chargedPrice &&
            other.legalPrice == legalPrice &&
            other.explanation == explanation);
  }

  @override
  int get hashCode => Object.hash(verdict, chargedPrice, legalPrice, explanation);

  @override
  String toString() =>
      'PriceVerificationResult(verdict: $verdict, chargedPrice: $chargedPrice, '
      'legalPrice: $legalPrice, explanation: $explanation)';
}
