import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/sources/catalog_remote_source.dart';

void main() {
  group('RemoteCatalogCheck', () {
    test('noUpdate has hasUpdate false and no rawJson', () {
      const result = RemoteCatalogCheck.noUpdate();

      expect(result.hasUpdate, isFalse);
      expect(result.rawJson, isNull);
    });

    test('updateAvailable has hasUpdate true and carries the raw JSON', () {
      const result = RemoteCatalogCheck.updateAvailable('{"catalog_version": 2}');

      expect(result.hasUpdate, isTrue);
      expect(result.rawJson, '{"catalog_version": 2}');
    });
  });

  group('StubCatalogRemoteSource', () {
    test('always reports no update, regardless of the current version', () async {
      const source = StubCatalogRemoteSource();

      final resultAtZero = await source.checkForUpdate(0);
      final resultAtLarge = await source.checkForUpdate(999);

      expect(resultAtZero.hasUpdate, isFalse);
      expect(resultAtLarge.hasUpdate, isFalse);
    });
  });
}
