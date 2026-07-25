// Fuzzy string matching for search: levenshtein (edit distance) and
// scoreMatch (the matching + ranking score built on top of it, used by
// searchResultsProvider to rank and filter beers).

/// Returns the Levenshtein edit distance between [a] and [b]: the minimum
/// number of single-character insertions, deletions, or substitutions
/// needed to turn [a] into [b].
///
/// Case-sensitive — callers that want case-insensitive matching (e.g.
/// [scoreMatch]) normalize case themselves before calling this.
int levenshtein(String a, String b) {
  if (a == b) return 0;
  if (a.isEmpty) return b.length;
  if (b.isEmpty) return a.length;

  // Classic two-row dynamic-programming edit distance: `previousRow`
  // holds the distances for the row above the one currently being
  // computed, so each cell only ever needs its immediate neighbors.
  var previousRow = List<int>.generate(b.length + 1, (i) => i);
  var currentRow = List<int>.filled(b.length + 1, 0);

  for (var i = 0; i < a.length; i++) {
    currentRow[0] = i + 1;
    for (var j = 0; j < b.length; j++) {
      final deletionCost = previousRow[j + 1] + 1;
      final insertionCost = currentRow[j] + 1;
      final substitutionCost = previousRow[j] + (a[i] == b[j] ? 0 : 1);
      currentRow[j + 1] = <int>[deletionCost, insertionCost, substitutionCost]
          .reduce((value, element) => value < element ? value : element);
    }
    final swap = previousRow;
    previousRow = currentRow;
    currentRow = swap;
  }

  return previousRow[b.length];
}

/// How many characters of edit distance [scoreMatch] tolerates before
/// treating a comparison as "not a match at all", relative to [target]'s
/// length.
///
/// One typo per 4 characters (rounded up, minimum 1) is a deliberately
/// simple, fixed heuristic — there's no user research yet on what typo
/// tolerance actually feels right in this app. This is a placeholder
/// threshold, not a tuned constant: if search feels too loose or too
/// strict once there's real usage, adjusting this divisor (or replacing
/// it with something else entirely) is a self-contained change confined
/// to this function.
int _typoTolerance(String target) {
  final tolerance = (target.length / 4).ceil();
  return tolerance < 1 ? 1 : tolerance;
}

/// Scores how well [query] matches [target] for search ranking. Higher is
/// a better match; `0` means "not a match at all".
///
/// Matching, in order of preference (each tier strictly outscores every
/// lower one, so exact/prefix/substring matches always rank above fuzzy
/// ones):
/// - [target] equals [query], case-insensitively: best.
/// - [target] starts with [query]: next best.
/// - [target] contains [query] anywhere: next.
/// - otherwise, fuzzy: matches if the [levenshtein] distance between
///   [query] and [target] — or between [query] and any single word of
///   [target] — is within [_typoTolerance] of whichever string it's being
///   compared to, scored so a smaller distance ranks higher (but always
///   below every tier above).
///
/// The fuzzy tier also checks [target]'s individual words (not just
/// [target] as a whole) because most beer/brewery names here are two or
/// three words, and a single mistyped word (e.g. "Kingfsiher" for
/// "Kingfisher Premium") has a small edit distance from the one word
/// it's actually a typo of, but a large one from the multi-word string as
/// a whole — comparing only against the whole string would make typo
/// tolerance effectively never trigger on any multi-word name.
///
/// An empty (or all-whitespace) [query] always matches, with the lowest
/// score — callers that want "empty query returns everything, unranked"
/// (as `searchResultsProvider` does) check for that case themselves
/// rather than relying on this score, since "matches, but ranks lowest"
/// and "don't rank at all" are different behaviours.
///
/// This still doesn't split [query] itself into words — a multi-word
/// query is only ever compared as one string. If matching a multi-word
/// query against [target]'s words independently (e.g. "toit ipa" against
/// "IPA Toit" in either order) becomes a real need, that's the next place
/// to extend this function; it isn't needed yet since V1 search queries
/// are expected to be short, single-term lookups.
int scoreMatch(String query, String target) {
  final normalizedQuery = query.trim().toLowerCase();
  final normalizedTarget = target.trim().toLowerCase();

  if (normalizedQuery.isEmpty) return 1;
  if (normalizedTarget == normalizedQuery) return 1000;
  if (normalizedTarget.startsWith(normalizedQuery)) return 800;
  if (normalizedTarget.contains(normalizedQuery)) return 600;

  final candidates = <String>{normalizedTarget, ...normalizedTarget.split(' ')}
    ..removeWhere((candidate) => candidate.isEmpty);

  var bestFuzzyScore = 0;
  for (final candidate in candidates) {
    final distance = levenshtein(normalizedQuery, candidate);
    if (distance <= _typoTolerance(candidate)) {
      final score = 400 - distance;
      if (score > bestFuzzyScore) bestFuzzyScore = score;
    }
  }
  return bestFuzzyScore;
}
