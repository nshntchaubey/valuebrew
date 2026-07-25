/// A closed price range, in rupees: `[min, max]`, both inclusive.
///
/// See [AbvRange] for why this is a small value object rather than two
/// loose `double`s — the same reasoning applies here.
class PriceRange {
  /// Creates a [PriceRange] from [min] to [max], inclusive.
  ///
  /// Throws [ArgumentError] if [min] is negative or [max] is less than
  /// [min].
  PriceRange({required this.min, required this.max}) {
    if (min < 0) {
      throw ArgumentError.value(min, 'min', 'must not be negative');
    }
    if (max < min) {
      throw ArgumentError.value(max, 'max', 'must not be less than min');
    }
  }

  /// The lower bound, inclusive.
  final double min;

  /// The upper bound, inclusive.
  final double max;

  /// Whether [price] falls within this range, inclusive of both ends.
  bool contains(double price) => price >= min && price <= max;

  @override
  bool operator ==(Object other) {
    return identical(this, other) || (other is PriceRange && other.min == min && other.max == max);
  }

  @override
  int get hashCode => Object.hash(min, max);

  @override
  String toString() => 'PriceRange(min: $min, max: $max)';
}
