import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:valuebrew/core/constants/app_constants.dart';
import 'package:valuebrew/catalog/data/catalog_remote_source.dart';

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

  group('HttpCatalogRemoteSource', () {
    test('defaults catalogUrl and timeout to AppConstants', () {
      final source = HttpCatalogRemoteSource();

      expect(source.catalogUrl, Uri.parse(AppConstants.remoteCatalogUrl));
      expect(source.timeout, AppConstants.remoteFetchTimeout);
    });

    test('a custom catalogUrl and timeout override the defaults', () {
      final customUrl = Uri.parse('https://example.com/custom-catalog.json');
      final source = HttpCatalogRemoteSource(
        catalogUrl: customUrl,
        timeout: const Duration(seconds: 1),
      );

      expect(source.catalogUrl, customUrl);
      expect(source.timeout, const Duration(seconds: 1));
    });

    test(
      'successful fetch: reports an update when the remote version is newer',
      () async {
        final source = HttpCatalogRemoteSource(
          httpGet: (url) async => http.Response('{"catalog_version": 5}', 200),
        );

        final result = await source.checkForUpdate(1);

        expect(result.hasUpdate, isTrue);
        expect(result.rawJson, '{"catalog_version": 5}');
      },
    );

    test(
      'successful fetch: calls httpGet with the configured catalogUrl',
      () async {
        Uri? receivedUrl;
        final configuredUrl = Uri.parse('https://example.com/catalog.json');
        final source = HttpCatalogRemoteSource(
          catalogUrl: configuredUrl,
          httpGet: (url) async {
            receivedUrl = url;
            return http.Response('{"catalog_version": 2}', 200);
          },
        );

        await source.checkForUpdate(1);

        expect(receivedUrl, configuredUrl);
      },
    );

    test(
      'successful fetch: reports no update when the remote version is not newer',
      () async {
        final source = HttpCatalogRemoteSource(
          httpGet: (url) async => http.Response('{"catalog_version": 3}', 200),
        );

        final result = await source.checkForUpdate(3);

        expect(result.hasUpdate, isFalse);
      },
    );

    test('timeout: falls back to no update instead of throwing', () async {
      final source = HttpCatalogRemoteSource(
        timeout: const Duration(milliseconds: 10),
        httpGet: (url) async {
          await Future.delayed(const Duration(milliseconds: 100));
          return http.Response('{"catalog_version": 5}', 200);
        },
      );

      final result = await source.checkForUpdate(1);

      expect(result.hasUpdate, isFalse);
    });

    test('non-200 response: falls back to no update instead of throwing', () async {
      final source = HttpCatalogRemoteSource(
        httpGet: (url) async => http.Response('Not Found', 404),
      );

      final result = await source.checkForUpdate(1);

      expect(result.hasUpdate, isFalse);
    });

    test(
      'network failure: falls back to no update instead of throwing',
      () async {
        final source = HttpCatalogRemoteSource(
          httpGet: (url) async => throw Exception('Network unreachable'),
        );

        final result = await source.checkForUpdate(1);

        expect(result.hasUpdate, isFalse);
      },
    );

    test('malformed JSON body: falls back to no update instead of throwing', () async {
      final source = HttpCatalogRemoteSource(
        httpGet: (url) async => http.Response('{ this is not valid json', 200),
      );

      final result = await source.checkForUpdate(1);

      expect(result.hasUpdate, isFalse);
    });

    test(
      'JSON missing an integer catalog_version: falls back to no update',
      () async {
        final source = HttpCatalogRemoteSource(
          httpGet: (url) async => http.Response('{"beers": []}', 200),
        );

        final result = await source.checkForUpdate(1);

        expect(result.hasUpdate, isFalse);
      },
    );
  });
}
