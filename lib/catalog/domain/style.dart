/// A beer style/category, e.g. Lager, Wheat, Stout, IPA.
///
/// Every [Sku] belongs to exactly one [Style]. A SKU's Value Score is
/// computed as a percentile within its [Style]'s benchmark distribution, so
/// [Style] defines the peer group beers are compared against.
///
/// Deserialized from the `styles` array of the published catalog:
/// ```json
/// { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
/// ```
class Style {
  /// Unique, stable identifier for this style, e.g. `"lager"`.
  final String id;

  /// Human-readable display name, e.g. `"Lager"`.
  final String name;

  /// Short, human-readable description of the style.
  final String description;

  /// Creates an immutable [Style].
  const Style({
    required this.id,
    required this.name,
    required this.description,
  });

  /// Creates a [Style] from its decoded JSON map.
  factory Style.fromJson(Map<String, dynamic> json) {
    return Style(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
    );
  }

  /// Converts this [Style] to a JSON-encodable map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
    };
  }

  /// Returns a copy of this [Style] with the given fields replaced.
  Style copyWith({
    String? id,
    String? name,
    String? description,
  }) {
    return Style(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is Style &&
            other.id == id &&
            other.name == name &&
            other.description == description);
  }

  @override
  int get hashCode => Object.hash(id, name, description);

  @override
  String toString() => 'Style(id: $id, name: $name, description: $description)';
}
