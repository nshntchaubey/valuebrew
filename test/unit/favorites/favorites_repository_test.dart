import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:valuebrew/features/favorites/favorites_repository.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('SharedPreferencesFavoritesRepository', () {
    test('load returns an empty set when nothing has been saved yet', () async {
      const repository = SharedPreferencesFavoritesRepository();

      expect(await repository.load(), isEmpty);
    });

    test('save then load round-trips the favorited beer IDs', () async {
      const repository = SharedPreferencesFavoritesRepository();

      await repository.save({'kf_premium', 'toit_porter'});

      expect(await repository.load(), {'kf_premium', 'toit_porter'});
    });

    test('a second save replaces the first entirely', () async {
      const repository = SharedPreferencesFavoritesRepository();

      await repository.save({'kf_premium'});
      await repository.save({'toit_porter'});

      expect(await repository.load(), {'toit_porter'});
    });

    test('add persists a new favorite alongside existing ones', () async {
      const repository = SharedPreferencesFavoritesRepository();
      await repository.save({'kf_premium'});

      await repository.add('toit_porter');

      expect(await repository.load(), {'kf_premium', 'toit_porter'});
    });

    test('adding an already-favorited beer is a no-op, not a duplicate', () async {
      const repository = SharedPreferencesFavoritesRepository();
      await repository.save({'kf_premium'});

      await repository.add('kf_premium');

      expect(await repository.load(), {'kf_premium'});
    });

    test('remove deletes a favorite while leaving the others untouched', () async {
      const repository = SharedPreferencesFavoritesRepository();
      await repository.save({'kf_premium', 'toit_porter'});

      await repository.remove('kf_premium');

      expect(await repository.load(), {'toit_porter'});
    });

    test('removing a beer that was never favorited is a no-op, not an error', () async {
      const repository = SharedPreferencesFavoritesRepository();
      await repository.save({'kf_premium'});

      await repository.remove('no_such_beer');

      expect(await repository.load(), {'kf_premium'});
    });

    test('isFavorite reflects the current persisted set', () async {
      const repository = SharedPreferencesFavoritesRepository();
      await repository.save({'kf_premium'});

      expect(await repository.isFavorite('kf_premium'), isTrue);
      expect(await repository.isFavorite('toit_porter'), isFalse);
    });

    test('persists across repository recreation — surviving an app restart', () async {
      const firstInstance = SharedPreferencesFavoritesRepository();
      await firstInstance.add('kf_premium');

      // A brand-new repository instance, backed by the same underlying
      // SharedPreferences storage — simulating a fresh app launch reading
      // whatever was persisted in a previous one.
      const secondInstance = SharedPreferencesFavoritesRepository();

      expect(await secondInstance.load(), {'kf_premium'});
    });
  });
}
