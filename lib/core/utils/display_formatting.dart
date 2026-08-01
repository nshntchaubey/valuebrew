import 'package:valuebrew/shared_domain/sku.dart';

/// Formats a raw rupee amount for display.
///
/// Whole-number amounts never show a trailing `.0` (`110.0` -> `"₹110"`);
/// non-whole amounts keep their decimal portion (`110.5` -> `"₹110.5"`).
extension CurrencyFormatting on double {
  String get currencyLabel {
    final isWhole = this == roundToDouble();
    return isWhole ? '₹${toStringAsFixed(0)}' : '₹$this';
  }
}

/// Formats a size in millilitres for display, e.g. `650` -> `"650 mL"`.
extension VolumeFormatting on int {
  String get volumeLabel => '$this mL';
}

/// Plain-language label for a [PackageType], e.g. [PackageType.bottle] ->
/// `"Bottle"`.
extension PackageTypeFormatting on PackageType {
  String get displayLabel {
    switch (this) {
      case PackageType.bottle:
        return 'Bottle';
      case PackageType.can:
        return 'Can';
      case PackageType.pint:
        return 'Pint';
    }
  }
}

/// Plain-language label for a [ValueVerdict], matching the wording in the
/// V1 technical architecture's Value Score algorithm.
extension ValueVerdictFormatting on ValueVerdict {
  String get displayLabel {
    switch (this) {
      case ValueVerdict.greatValue:
        return 'Great value';
      case ValueVerdict.fairValue:
        return 'Fair value';
      case ValueVerdict.overpriced:
        return 'Overpriced for this ABV';
    }
  }
}
