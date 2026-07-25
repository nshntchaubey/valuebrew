import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/favorites/favorites_repository.dart';

/// Exposes the app's [FavoritesRepository].
///
/// Construction happens here, not inside [FavoritesNotifier] — the same
/// separation `catalogRepositoryProvider` uses for `CatalogRepository`.
/// Override this in tests to substitute a fake without touching real
/// [SharedPreferences].
final favoritesRepositoryProvider = Provider<FavoritesRepository>((ref) {
  return const SharedPreferencesFavoritesRepository();
});

/// Holds every currently favorited beer ID in memory, backed by
/// [FavoritesRepository] for persistence.
///
/// Keeping the full [Set] in memory (rather than asking the repository
/// "is this beer a favorite?" on every widget build) is what makes
/// favorite-status lookups an O(1) [Set.contains] check regardless of how
/// many beers a screen renders — see `favoriteBeerIdsProvider`'s own doc
/// comment for why that matters.
class FavoritesNotifier extends StateNotifier<Set<String>> {
  FavoritesNotifier(this._repository) : super(const <String>{}) {
    _loadInitial();
  }

  final FavoritesRepository _repository;

  Future<void> _loadInitial() async {
    state = await _repository.load();
  }

  /// Whether [beerId] is currently favorited.
  bool isFavorite(String beerId) => state.contains(beerId);

  /// Favorites [beerId] if it isn't already one, otherwise un-favorites
  /// it.
  Future<void> toggle(String beerId) {
    return state.contains(beerId) ? remove(beerId) : add(beerId);
  }

  /// Favorites [beerId]. A no-op if it already is one.
  ///
  /// Updates [state] immediately, so every screen watching it reflects the
  /// change on the very next frame — persisting via [FavoritesRepository]
  /// happens after, not before, since nothing in the UI needs to wait on
  /// it.
  Future<void> add(String beerId) async {
    if (state.contains(beerId)) return;
    state = {...state, beerId};
    await _repository.add(beerId);
  }

  /// Un-favorites [beerId]. A no-op if it wasn't one.
  ///
  /// See [add] for why [state] updates before persistence completes.
  Future<void> remove(String beerId) async {
    if (!state.contains(beerId)) return;
    state = {...state}..remove(beerId);
    await _repository.remove(beerId);
  }
}

/// The set of every currently favorited beer ID.
///
/// This is what every screen should watch to check or change favorite
/// status — never [favoritesRepositoryProvider] directly, and never
/// [SharedPreferences]. Reading this provider's `Set<String>` and calling
/// `.contains(beerId)` is an O(1) average-case lookup, so rendering a long
/// beer list (e.g. `HomeScreen`, `FavoritesScreen`) never scans anything
/// proportional to the number of favorites or beers.
final favoriteBeerIdsProvider = StateNotifierProvider<FavoritesNotifier, Set<String>>((ref) {
  return FavoritesNotifier(ref.watch(favoritesRepositoryProvider));
});
