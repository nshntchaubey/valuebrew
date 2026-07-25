/// A closed ABV range, in percentage points: `[min, max]`, both inclusive.
///
/// A small value object rather than two loose `double`s passed around
/// separately — it's the one place "is this a valid range" and "does this
/// ABV fall inside it" are defined, so every caller (the filtering engine,
/// the filter bottom sheet) shares the same rule instead of re-deriving it.
class AbvRange {
  /// Creates an [AbvRange] from [min] to [max], inclusive.
  ///
  /// Throws [ArgumentError] if [min] is negative or [max] is less than
  /// [min] — an ABV range that doesn't describe a real interval is a
  /// programming error, not a value worth silently tolerating.
  AbvRange({required this.min, required this.max}) {
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

  /// Whether [abv] falls within this range, inclusive of both ends.
  bool contains(double abv) => abv >= min && abv <= max;

  @override
  bool operator ==(Object other) {
    return identical(this, other) || (other is AbvRange && other.min == min && other.max == max);
  }

  @override
  int get hashCode => Object.hash(min, max);

  @override
  String toString() => 'AbvRange(min: $min, max: $max)';
}
