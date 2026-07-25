import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:valuebrew/features/beer_detail/wrong_report.dart';

void main() {
  group('WrongReport', () {
    test('round-trips through JSON', () {
      final report = WrongReport(
        beerId: 'kf_premium',
        skuId: 'kf_premium_650',
        timestamp: DateTime.utc(2026, 7, 25, 10, 30),
      );

      final restored = WrongReport.fromJson(report.toJson());

      expect(restored.beerId, report.beerId);
      expect(restored.skuId, report.skuId);
      expect(restored.timestamp, report.timestamp);
    });
  });

  group('wrongReportKey', () {
    test('combines beerId and skuId into a distinct key', () {
      expect(
        wrongReportKey('kf_premium', 'kf_premium_650'),
        'kf_premium::kf_premium_650',
      );
    });

    test('does not collide across different id splits', () {
      // "a" + "bc" must not produce the same key as "ab" + "c".
      expect(
        wrongReportKey('a', 'bc'),
        isNot(equals(wrongReportKey('ab', 'c'))),
      );
    });
  });

  group('WrongReportStore', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('submit persists a retrievable report', () async {
      const store = WrongReportStore();

      await store.submit(
        WrongReport(
          beerId: 'kf_premium',
          skuId: 'kf_premium_650',
          timestamp: DateTime.utc(2026, 7, 25),
        ),
      );

      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getStringList('wrong_reports'), hasLength(1));
    });

    test('submit appends to existing reports rather than overwriting them', () async {
      const store = WrongReportStore();

      await store.submit(
        WrongReport(
          beerId: 'kf_premium',
          skuId: 'kf_premium_650',
          timestamp: DateTime.utc(2026, 7, 25),
        ),
      );
      await store.submit(
        WrongReport(
          beerId: 'toit_porter',
          skuId: 'toit_porter_330',
          timestamp: DateTime.utc(2026, 7, 25),
        ),
      );

      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getStringList('wrong_reports'), hasLength(2));
    });
  });
}
