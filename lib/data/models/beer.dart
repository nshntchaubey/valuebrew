import 'package:valuebrew/data/models/style.dart';

/// A beer brand/product, e.g. "Kingfisher Premium".
///
/// A [Beer] belongs to exactly one [Style], referenced by [styleId] rather
/// than an embedded [Style] instance, and has one or more SKUs representing
/// its purchasable pack sizes.
///
/// Deserialized from the `beers` array of the published catalog:
/// ```json
/// { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false }
/// ```
class Beer {
  /// Unique, stable identifier for this beer, e.g. `"kf_premium"`.
  final String id;

  /// Display name of the beer, e.g. `"Kingfisher Premium"`.
  final String name;

  /// Name of the brewery that produces this beer, e.g. `"United Breweries"`.
  final String brewery;

  /// Identifier of the [Style] this beer belongs to, matching [Style.id].
  ///
  /// Stored as a reference rather than an embedded [Style] to match the
  /// catalog's normalized JSON shape: the `styles` array is the single
  /// source of truth for style name/description, so those fields are never
  /// duplicated here. Resolving [styleId] to a full [Style] is the
  /// responsibility of whatever holds both collections (e.g. the catalog
  /// repository), not of [Beer] itself.
  final String styleId;

  /// Whether this beer is a craft/independent beer, as opposed to a
  /// mass-market brand.
  final bool isCraft;

  /// Creates an immutable [Beer].
  const Beer({
    required this.id,
    required this.name,
    required this.brewery,
    required this.styleId,
    required this.isCraft,
  });

  /// Creates a [Beer] from its decoded JSON map.
  factory Beer.fromJson(Map<String, dynamic> json) {
    return Beer(
      id: json['id'] as String,
      name: json['name'] as String,
      brewery: json['brewery'] as String,
      styleId: json['style_id'] as String,
      isCraft: json['is_craft'] as bool,
    );
  }

  /// Converts this [Beer] to a JSON-encodable map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'brewery': brewery,
      'style_id': styleId,
      'is_craft': isCraft,
    };
  }

  /// Returns a copy of this [Beer] with the given fields replaced.
  Beer copyWith({
    String? id,
    String? name,
    String? brewery,
    String? styleId,
    bool? isCraft,
  }) {
    return Beer(
      id: id ?? this.id,
      name: name ?? this.name,
      brewery: brewery ?? this.brewery,
      styleId: styleId ?? this.styleId,
      isCraft: isCraft ?? this.isCraft,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is Beer &&
            other.id == id &&
            other.name == name &&
            other.brewery == brewery &&
            other.styleId == styleId &&
            other.isCraft == isCraft);
  }

  @override
  int get hashCode => Object.hash(id, name, brewery, styleId, isCraft);

  @override
  String toString() =>
      'Beer(id: $id, name: $name, brewery: $brewery, styleId: $styleId, isCraft: $isCraft)';
}
