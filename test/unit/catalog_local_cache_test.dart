import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:valuebrew/catalog/data/catalog_local_cache.dart';

void main() {
  group('NoopCatalogLocalCache', () {
    test('read always returns null', () async {
      const cache = NoopCatalogLocalCache();

      expect(await cache.read(), isNull);
    });

    test('write is a no-op — a subsequent read still returns null', () async {
      const cache = NoopCatalogLocalCache();

      await cache.write('{"catalog_version": 1}', 1);

      expect(await cache.read(), isNull);
    });
  });

  group('SharedPreferencesCatalogLocalCache', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('read returns null when nothing has been cached yet', () async {
      const cache = SharedPreferencesCatalogLocalCache();

      expect(await cache.read(), isNull);
    });

    test('write then read round-trips the cached catalog', () async {
      const cache = SharedPreferencesCatalogLocalCache();

      await cache.write('{"catalog_version": 4}', 4);
      final result = await cache.read();

      expect(result, isNotNull);
      expect(result!.rawJson, '{"catalog_version": 4}');
      expect(result.catalogVersion, 4);
    });

    test('a second write replaces the first', () async {
      const cache = SharedPreferencesCatalogLocalCache();

      await cache.write('{"catalog_version": 1}', 1);
      await cache.write('{"catalog_version": 2}', 2);
      final result = await cache.read();

      expect(result!.catalogVersion, 2);
    });
  });
}
