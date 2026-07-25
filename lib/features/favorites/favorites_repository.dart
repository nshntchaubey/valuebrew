import 'package:shared_preferences/shared_preferences.dart';

/// Reads and writes the user's favorited beers, persisted locally.
///
/// Only [Beer.id] strings are persisted, never whole `Beer` objects — the
/// catalog already has every other field, so storing more than the ID
/// would just be duplicated, staleness-prone data. [FavoritesNotifier] (see
/// `providers/favorites_providers.dart`) is what the rest of the app
/// actually reads favorite state from; this repository exists purely as
/// the persistence boundary underneath it, so no widget ever talks to
/// [SharedPreferences] directly.
abstract class FavoritesRepository {
  /// Returns every currently favorited beer ID.
  Future<Set<String>> load();

  /// Replaces the entire set of favorited beer IDs with [beerIds].
  Future<void> save(Set<String> beerIds);

  /// Marks [beerId] as a favorite. A no-op if it already is one.
  Future<void> add(String beerId);

  /// Un-marks [beerId] as a favorite. A no-op if it wasn't one.
  Future<void> remove(String beerId);

  /// Returns whether [beerId] is currently favorited.
  Future<bool> isFavorite(String beerId);
}

/// A [FavoritesRepository] backed by [SharedPreferences].
///
/// [add]/[remove]/[isFavorite] are built on [load]/[save] rather than
/// maintaining any state of their own — this class holds nothing in
/// memory, so there's only one place ([load]) that ever has to agree with
/// what's on disk. Callers that need fast, repeated "is this favorited?"
/// checks (e.g. rendering a beer list) should read from
/// `favoriteBeerIdsProvider` instead, which keeps its own in-memory copy
/// for exactly that reason — this repository is not meant to be queried
/// once per list row.
class SharedPreferencesFavoritesRepository implements FavoritesRepository {
  const SharedPreferencesFavoritesRepository();

  static const _prefsKey = 'favorite_beer_ids';

  @override
  Future<Set<String>> load() async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_prefsKey) ?? const <String>[]).toSet();
  }

  @override
  Future<void> save(Set<String> beerIds) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_prefsKey, beerIds.toList());
  }

  @override
  Future<void> add(String beerId) async {
    final current = await load();
    if (current.contains(beerId)) return;
    await save({...current, beerId});
  }

  @override
  Future<void> remove(String beerId) async {
    final current = await load();
    if (!current.contains(beerId)) return;
    await save({...current}..remove(beerId));
  }

  @override
  Future<bool> isFavorite(String beerId) async {
    final current = await load();
    return current.contains(beerId);
  }
}
