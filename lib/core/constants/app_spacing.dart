/// Shared spacing values, so padding and gaps are consistent across
/// screens instead of each one picking its own numbers.
///
/// Not every existing spacing value in the app has been migrated to these
/// constants — this milestone is a polish pass, not a mechanical
/// find-and-replace — but every widget touched by it uses these instead of
/// a new magic number.
class AppSpacing {
  const AppSpacing._();

  /// Tight spacing — between closely related inline elements.
  static const double xs = 4;

  /// The default gap between distinct pieces of text within one block.
  static const double sm = 8;

  /// The standard screen/section padding used throughout the app.
  static const double md = 16;

  /// Spacing between major sections of a screen.
  static const double lg = 24;

  /// Spacing around a large, standalone element (e.g. an empty-state
  /// icon).
  static const double xl = 32;
}
