import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/shared_domain/sku.dart';

/// How a [Sku]'s cost per millilitre of alcohol compares to its style's
/// median, per the Beer Knowledge Model's "relative standing within
/// style." No richer classification than this three-way comparison is
/// canonically specified.
enum StyleStanding {
  /// Below the style's median cost per millilitre of alcohol.
  betterThanTypical,

  /// Exactly at the style's median cost per millilitre of alcohol.
  typical,

  /// Above the style's median cost per millilitre of alcohol.
  worseThanTypical,
}

/// Classifies [sku]'s standing within its style, using only
/// [Benchmark.p50] — the canon specifies the comparison concept alone, not
/// a number of bands, so this is the smallest classification that
/// faithfully represents it. Pure Dart, deterministic, no Flutter
/// dependency.
StyleStanding classifyStyleStanding(Sku sku, Benchmark benchmark) {
  if (sku.costPerMlAlcohol < benchmark.p50) {
    return StyleStanding.betterThanTypical;
  }
  if (sku.costPerMlAlcohol > benchmark.p50) {
    return StyleStanding.worseThanTypical;
  }
  return StyleStanding.typical;
}
