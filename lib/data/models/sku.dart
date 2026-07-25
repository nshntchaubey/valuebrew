import 'package:valuebrew/data/models/beer.dart';

/// The physical container type of a [Sku], as sold at retail.
enum PackageType {
  /// A glass or plastic bottle.
  bottle,

  /// A metal can.
  can,

  /// A draught pint.
  pint;

  /// Parses a [PackageType] from its catalog JSON string value
  /// (`"bottle"`, `"can"`, or `"pint"`).
  static PackageType fromJson(String value) {
    return PackageType.values.firstWhere(
      (type) => type.name == value,
      orElse: () => throw ArgumentError('Unknown package_type: "$value"'),
    );
  }

  /// Converts this [PackageType] to its catalog JSON string value.
  String toJson() => name;
}

/// The plain-language Value Score verdict shown alongside a [Sku]'s price.
enum ValueVerdict {
  /// Among the cheapest cost-per-ml-of-alcohol within its style.
  greatValue,

  /// Reasonably priced relative to its style.
  fairValue,

  /// Expensive relative to its style, for its ABV.
  overpriced;

  /// Parses a [ValueVerdict] from its catalog JSON string value
  /// (`"great_value"`, `"fair_value"`, or `"overpriced"`).
  static ValueVerdict fromJson(String value) {
    switch (value) {
      case 'great_value':
        return ValueVerdict.greatValue;
      case 'fair_value':
        return ValueVerdict.fairValue;
      case 'overpriced':
        return ValueVerdict.overpriced;
      default:
        throw ArgumentError('Unknown value_verdict: "$value"');
    }
  }

  /// Converts this [ValueVerdict] to its catalog JSON string value.
  String toJson() {
    switch (this) {
      case ValueVerdict.greatValue:
        return 'great_value';
      case ValueVerdict.fairValue:
        return 'fair_value';
      case ValueVerdict.overpriced:
        return 'overpriced';
    }
  }
}

/// A purchasable pack size of a [Beer] — one specific size, package type,
/// ABV, and price combination.
///
/// A [Beer] has one or more [Sku]s. The price, Value Score, and provenance
/// shown on the Beer Detail screen are all attributes of a [Sku], not of the
/// [Beer] itself, since a single beer can have multiple sizes with different
/// per-unit value.
///
/// Deserialized from the `skus` array of the published catalog:
/// ```json
/// {
///   "id": "kf_premium_650",
///   "beer_id": "kf_premium",
///   "size_ml": 650,
///   "package_type": "bottle",
///   "abv": 4.8,
///   "calories": 260,
///   "price": 110,
///   "price_last_checked": "2026-07-20",
///   "price_source": "karnataka_excise_mrp_2026",
///   "cost_per_litre": 169.2,
///   "cost_per_ml_alcohol": 3.52,
///   "value_score": 78,
///   "value_verdict": "great_value"
/// }
/// ```
///
/// `price`, `calories`, and `value_score` are parsed via [num] coercion
/// (`.toDouble()` / `.toInt()`) rather than a strict cast, since the catalog
/// build script may emit them as either a JSON integer or a JSON decimal.
class Sku {
  /// Unique, stable identifier for this SKU, e.g. `"kf_premium_650"`.
  final String id;

  /// Identifier of the [Beer] this SKU belongs to, matching [Beer.id].
  ///
  /// Stored as a reference rather than an embedded [Beer] to match the
  /// catalog's normalized JSON shape — the `beers` array is the single
  /// source of truth for beer-level fields, so those are never duplicated
  /// here.
  final String beerId;

  /// Pack size in millilitres, e.g. `650`.
  final int sizeMl;

  /// The physical container type: bottle, can, or pint.
  final PackageType packageType;

  /// Alcohol by volume, as a percentage, e.g. `4.8` for 4.8%.
  final double abv;

  /// Calorie count for this SKU.
  final int calories;

  /// Price in rupees.
  final double price;

  /// Date this [price] was last confirmed.
  final DateTime priceLastChecked;

  /// Human-readable provenance of [price], e.g.
  /// `"karnataka_excise_mrp_2026"`.
  ///
  /// Rendered directly by the ProvenanceStrip widget, so this must always be
  /// human-readable, not an internal code.
  final String priceSource;

  /// Cost per litre, derived from [price] and [sizeMl].
  final double costPerLitre;

  /// Cost per millilitre of pure alcohol, derived from [price], [sizeMl],
  /// and [abv]. The primary axis the Value Score is computed from.
  final double costPerMlAlcohol;

  /// Value Score (0-100): an inverted percentile of [costPerMlAlcohol]
  /// within this SKU's style benchmark. Higher is better value.
  final int valueScore;

  /// Plain-language verdict derived from [valueScore].
  final ValueVerdict valueVerdict;

  /// Creates an immutable [Sku].
  const Sku({
    required this.id,
    required this.beerId,
    required this.sizeMl,
    required this.packageType,
    required this.abv,
    required this.calories,
    required this.price,
    required this.priceLastChecked,
    required this.priceSource,
    required this.costPerLitre,
    required this.costPerMlAlcohol,
    required this.valueScore,
    required this.valueVerdict,
  });

  /// Creates a [Sku] from its decoded JSON map.
  factory Sku.fromJson(Map<String, dynamic> json) {
    return Sku(
      id: json['id'] as String,
      beerId: json['beer_id'] as String,
      sizeMl: json['size_ml'] as int,
      packageType: PackageType.fromJson(json['package_type'] as String),
      abv: (json['abv'] as num).toDouble(),
      calories: (json['calories'] as num).toInt(),
      price: (json['price'] as num).toDouble(),
      priceLastChecked: DateTime.parse(json['price_last_checked'] as String),
      priceSource: json['price_source'] as String,
      costPerLitre: (json['cost_per_litre'] as num).toDouble(),
      costPerMlAlcohol: (json['cost_per_ml_alcohol'] as num).toDouble(),
      valueScore: (json['value_score'] as num).toInt(),
      valueVerdict: ValueVerdict.fromJson(json['value_verdict'] as String),
    );
  }

  /// Converts this [Sku] to a JSON-encodable map.
  ///
  /// [priceLastChecked] is written back out in the same bare `yyyy-MM-dd`
  /// form used by the catalog, discarding any time-of-day component.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'beer_id': beerId,
      'size_ml': sizeMl,
      'package_type': packageType.toJson(),
      'abv': abv,
      'calories': calories,
      'price': price,
      'price_last_checked': _formatDate(priceLastChecked),
      'price_source': priceSource,
      'cost_per_litre': costPerLitre,
      'cost_per_ml_alcohol': costPerMlAlcohol,
      'value_score': valueScore,
      'value_verdict': valueVerdict.toJson(),
    };
  }

  static String _formatDate(DateTime date) {
    final year = date.year.toString().padLeft(4, '0');
    final month = date.month.toString().padLeft(2, '0');
    final day = date.day.toString().padLeft(2, '0');
    return '$year-$month-$day';
  }

  /// Returns a copy of this [Sku] with the given fields replaced.
  Sku copyWith({
    String? id,
    String? beerId,
    int? sizeMl,
    PackageType? packageType,
    double? abv,
    int? calories,
    double? price,
    DateTime? priceLastChecked,
    String? priceSource,
    double? costPerLitre,
    double? costPerMlAlcohol,
    int? valueScore,
    ValueVerdict? valueVerdict,
  }) {
    return Sku(
      id: id ?? this.id,
      beerId: beerId ?? this.beerId,
      sizeMl: sizeMl ?? this.sizeMl,
      packageType: packageType ?? this.packageType,
      abv: abv ?? this.abv,
      calories: calories ?? this.calories,
      price: price ?? this.price,
      priceLastChecked: priceLastChecked ?? this.priceLastChecked,
      priceSource: priceSource ?? this.priceSource,
      costPerLitre: costPerLitre ?? this.costPerLitre,
      costPerMlAlcohol: costPerMlAlcohol ?? this.costPerMlAlcohol,
      valueScore: valueScore ?? this.valueScore,
      valueVerdict: valueVerdict ?? this.valueVerdict,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is Sku &&
            other.id == id &&
            other.beerId == beerId &&
            other.sizeMl == sizeMl &&
            other.packageType == packageType &&
            other.abv == abv &&
            other.calories == calories &&
            other.price == price &&
            other.priceLastChecked == priceLastChecked &&
            other.priceSource == priceSource &&
            other.costPerLitre == costPerLitre &&
            other.costPerMlAlcohol == costPerMlAlcohol &&
            other.valueScore == valueScore &&
            other.valueVerdict == valueVerdict);
  }

  @override
  int get hashCode => Object.hash(
        id,
        beerId,
        sizeMl,
        packageType,
        abv,
        calories,
        price,
        priceLastChecked,
        priceSource,
        costPerLitre,
        costPerMlAlcohol,
        Object.hash(valueScore, valueVerdict),
      );

  @override
  String toString() =>
      'Sku(id: $id, beerId: $beerId, sizeMl: $sizeMl, '
      'packageType: $packageType, abv: $abv, calories: $calories, '
      'price: $price, priceLastChecked: $priceLastChecked, '
      'priceSource: $priceSource, costPerLitre: $costPerLitre, '
      'costPerMlAlcohol: $costPerMlAlcohol, valueScore: $valueScore, '
      'valueVerdict: $valueVerdict)';
}
