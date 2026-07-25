import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// A user-submitted "this looks wrong" report for a single SKU.
///
/// V1 has no moderation pipeline, backend, or networking (see the V1
/// scope doc and this milestone's report) — a report is recorded locally
/// only, for later manual review. See [WrongReportStore] for where it's
/// kept.
class WrongReport {
  /// The beer this report is about.
  final String beerId;

  /// The specific SKU this report is about.
  final String skuId;

  /// When the report was submitted.
  final DateTime timestamp;

  /// Creates an immutable [WrongReport].
  const WrongReport({
    required this.beerId,
    required this.skuId,
    required this.timestamp,
  });

  /// Converts this [WrongReport] to a JSON-encodable map.
  Map<String, dynamic> toJson() => {
        'beer_id': beerId,
        'sku_id': skuId,
        'timestamp': timestamp.toIso8601String(),
      };

  /// Creates a [WrongReport] from its decoded JSON map.
  factory WrongReport.fromJson(Map<String, dynamic> json) => WrongReport(
        beerId: json['beer_id'] as String,
        skuId: json['sku_id'] as String,
        timestamp: DateTime.parse(json['timestamp'] as String),
      );
}

/// Stores [WrongReport]s locally, as an append-only list of JSON strings
/// in [SharedPreferences].
///
/// This is a V1 placeholder for what the V1 scope doc describes as a flag
/// that "routes to founder" — there is no networking, webhook, or
/// moderation pipeline here to actually deliver reports off-device (all
/// explicitly excluded from this milestone). [submit] is the only method
/// the rest of the app calls; replacing local storage with a real
/// delivery mechanism later only requires changing this class's
/// internals — see the Future Migration notes in the milestone report.
class WrongReportStore {
  const WrongReportStore();

  static const _prefsKey = 'wrong_reports';

  /// Persists [report] locally.
  Future<void> submit(WrongReport report) async {
    final prefs = await SharedPreferences.getInstance();
    final existing = prefs.getStringList(_prefsKey) ?? <String>[];
    await prefs.setStringList(_prefsKey, [
      ...existing,
      jsonEncode(report.toJson()),
    ]);
  }
}

/// Exposes the app's [WrongReportStore].
final wrongReportStoreProvider = Provider<WrongReportStore>((ref) {
  return const WrongReportStore();
});

/// The set of `"beerId::skuId"` keys reported so far in this app session,
/// used to prevent duplicate reports for the same SKU within one session.
///
/// Deliberately in-memory only, not read back from [WrongReportStore] on
/// startup — the requirement is duplicate prevention "within the same app
/// session," not across app restarts, so a plain session-scoped provider
/// is the simplest thing that satisfies it.
final reportedItemsProvider = StateProvider<Set<String>>((ref) => <String>{});

/// The [reportedItemsProvider] key for a given beer/SKU pair.
String wrongReportKey(String beerId, String skuId) => '$beerId::$skuId';
