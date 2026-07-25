import 'package:valuebrew/data/models/style.dart';

/// The reference cost-per-ml-of-alcohol distribution for a single [Style],
/// computed once at catalog build time from every SKU in that style.
///
/// A SKU's Value Score is an inverted percentile of its
/// `cost_per_ml_alcohol` within this distribution — [Benchmark] is the
/// reference the score is computed against, not a value shown directly to
/// the user.
///
/// Deserialized from the `benchmarks` array of the published catalog:
/// ```json
/// {
///   "style_id": "lager",
///   "avg_cost_per_ml_alcohol": 4.10,
///   "p25": 3.40,
///   "p50": 3.95,
///   "p75": 4.60,
///   "sample_size": 42
/// }
/// ```
class Benchmark {
  /// Identifier of the [Style] this benchmark describes, matching
  /// [Style.id].
  ///
  /// V1 is a single-city (Bangalore) catalog, so [styleId] alone uniquely
  /// identifies a benchmark entry — there is no separate `id` or `city_id`
  /// field in the V1 catalog schema.
  final String styleId;

  /// Average cost per millilitre of pure alcohol across every SKU in this
  /// style.
  final double avgCostPerMlAlcohol;

  /// 25th percentile of cost per millilitre of pure alcohol within this
  /// style.
  final double p25;

  /// 50th percentile (median) of cost per millilitre of pure alcohol
  /// within this style.
  final double p50;

  /// 75th percentile of cost per millilitre of pure alcohol within this
  /// style.
  final double p75;

  /// Number of SKUs this benchmark was computed from.
  final int sampleSize;

  /// Creates an immutable [Benchmark].
  const Benchmark({
    required this.styleId,
    required this.avgCostPerMlAlcohol,
    required this.p25,
    required this.p50,
    required this.p75,
    required this.sampleSize,
  });

  /// Creates a [Benchmark] from its decoded JSON map.
  ///
  /// Numeric fields are parsed via [num] coercion (`.toDouble()` /
  /// `.toInt()`) rather than a strict cast, consistent with `Sku`, since
  /// the catalog build script may emit a whole-number statistic as either
  /// a JSON integer or a JSON decimal.
  factory Benchmark.fromJson(Map<String, dynamic> json) {
    return Benchmark(
      styleId: json['style_id'] as String,
      avgCostPerMlAlcohol:
          (json['avg_cost_per_ml_alcohol'] as num).toDouble(),
      p25: (json['p25'] as num).toDouble(),
      p50: (json['p50'] as num).toDouble(),
      p75: (json['p75'] as num).toDouble(),
      sampleSize: (json['sample_size'] as num).toInt(),
    );
  }

  /// Converts this [Benchmark] to a JSON-encodable map.
  Map<String, dynamic> toJson() {
    return {
      'style_id': styleId,
      'avg_cost_per_ml_alcohol': avgCostPerMlAlcohol,
      'p25': p25,
      'p50': p50,
      'p75': p75,
      'sample_size': sampleSize,
    };
  }

  /// Returns a copy of this [Benchmark] with the given fields replaced.
  Benchmark copyWith({
    String? styleId,
    double? avgCostPerMlAlcohol,
    double? p25,
    double? p50,
    double? p75,
    int? sampleSize,
  }) {
    return Benchmark(
      styleId: styleId ?? this.styleId,
      avgCostPerMlAlcohol: avgCostPerMlAlcohol ?? this.avgCostPerMlAlcohol,
      p25: p25 ?? this.p25,
      p50: p50 ?? this.p50,
      p75: p75 ?? this.p75,
      sampleSize: sampleSize ?? this.sampleSize,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is Benchmark &&
            other.styleId == styleId &&
            other.avgCostPerMlAlcohol == avgCostPerMlAlcohol &&
            other.p25 == p25 &&
            other.p50 == p50 &&
            other.p75 == p75 &&
            other.sampleSize == sampleSize);
  }

  @override
  int get hashCode =>
      Object.hash(styleId, avgCostPerMlAlcohol, p25, p50, p75, sampleSize);

  @override
  String toString() =>
      'Benchmark(styleId: $styleId, '
      'avgCostPerMlAlcohol: $avgCostPerMlAlcohol, p25: $p25, p50: $p50, '
      'p75: $p75, sampleSize: $sampleSize)';
}
