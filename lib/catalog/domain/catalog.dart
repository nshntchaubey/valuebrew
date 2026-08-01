import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/catalog/domain/benchmark.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/catalog/domain/style.dart';

/// The full, precomputed beer catalog published by the build pipeline.
///
/// A pure data model mirroring the catalog JSON exactly: it holds [styles],
/// [beers], [skus], and [benchmarks] as flat collections linked only by ID
/// (`Beer.styleId`, `Sku.beerId`, `Benchmark.styleId`). Resolving those
/// references, looking items up, indexing, or caching are all
/// responsibilities of a future repository, not of [Catalog] itself.
///
/// Deserialized from the top level of the published catalog:
/// ```json
/// {
///   "catalog_version": 7,
///   "generated_at": "2026-07-25T00:00:00Z",
///   "styles": [...],
///   "beers": [...],
///   "skus": [...],
///   "benchmarks": [...]
/// }
/// ```
class Catalog {
  /// Monotonically increasing version number, used to decide whether a
  /// freshly fetched remote catalog should replace the cached one.
  final int catalogVersion;

  /// Timestamp the catalog was generated at.
  final DateTime generatedAt;

  /// Every beer style/category in the catalog.
  final List<Style> styles;

  /// Every beer in the catalog.
  final List<Beer> beers;

  /// Every purchasable SKU in the catalog.
  final List<Sku> skus;

  /// Every style-level Value Score benchmark in the catalog.
  final List<Benchmark> benchmarks;

  /// Creates an immutable [Catalog].
  const Catalog({
    required this.catalogVersion,
    required this.generatedAt,
    required this.styles,
    required this.beers,
    required this.skus,
    required this.benchmarks,
  });

  /// Creates a [Catalog] from its decoded JSON map.
  ///
  /// [generatedAt] is parsed via [DateTime.parse], consistent with
  /// `Sku.priceLastChecked`. `catalog_version` is parsed via [num]
  /// coercion, consistent with the numeric handling in the other models.
  /// Each nested collection is parsed by delegating to that model's own
  /// `fromJson`.
  factory Catalog.fromJson(Map<String, dynamic> json) {
    return Catalog(
      catalogVersion: (json['catalog_version'] as num).toInt(),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      styles: (json['styles'] as List<dynamic>)
          .map((e) => Style.fromJson(e as Map<String, dynamic>))
          .toList(),
      beers: (json['beers'] as List<dynamic>)
          .map((e) => Beer.fromJson(e as Map<String, dynamic>))
          .toList(),
      skus: (json['skus'] as List<dynamic>)
          .map((e) => Sku.fromJson(e as Map<String, dynamic>))
          .toList(),
      benchmarks: (json['benchmarks'] as List<dynamic>)
          .map((e) => Benchmark.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  /// Converts this [Catalog] to a JSON-encodable map, delegating each
  /// nested collection to that model's own `toJson`.
  Map<String, dynamic> toJson() {
    return {
      'catalog_version': catalogVersion,
      'generated_at': generatedAt.toIso8601String(),
      'styles': styles.map((e) => e.toJson()).toList(),
      'beers': beers.map((e) => e.toJson()).toList(),
      'skus': skus.map((e) => e.toJson()).toList(),
      'benchmarks': benchmarks.map((e) => e.toJson()).toList(),
    };
  }

  /// Returns a copy of this [Catalog] with the given fields replaced.
  Catalog copyWith({
    int? catalogVersion,
    DateTime? generatedAt,
    List<Style>? styles,
    List<Beer>? beers,
    List<Sku>? skus,
    List<Benchmark>? benchmarks,
  }) {
    return Catalog(
      catalogVersion: catalogVersion ?? this.catalogVersion,
      generatedAt: generatedAt ?? this.generatedAt,
      styles: styles ?? this.styles,
      beers: beers ?? this.beers,
      skus: skus ?? this.skus,
      benchmarks: benchmarks ?? this.benchmarks,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other is Catalog &&
            other.catalogVersion == catalogVersion &&
            other.generatedAt == generatedAt &&
            _listEquals(other.styles, styles) &&
            _listEquals(other.beers, beers) &&
            _listEquals(other.skus, skus) &&
            _listEquals(other.benchmarks, benchmarks));
  }

  /// Element-wise list equality, since [List]'s default `==` is identity,
  /// not content, comparison. Used only to fulfil the [==] contract above.
  static bool _listEquals<T>(List<T> a, List<T> b) {
    if (identical(a, b)) return true;
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }

  @override
  int get hashCode => Object.hash(
        catalogVersion,
        generatedAt,
        Object.hashAll(styles),
        Object.hashAll(beers),
        Object.hashAll(skus),
        Object.hashAll(benchmarks),
      );

  @override
  String toString() =>
      'Catalog(catalogVersion: $catalogVersion, generatedAt: $generatedAt, '
      'styles: ${styles.length}, beers: ${beers.length}, '
      'skus: ${skus.length}, benchmarks: ${benchmarks.length})';
}
