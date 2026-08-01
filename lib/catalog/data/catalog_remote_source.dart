import 'dart:async';
import 'dart:convert';
import 'dart:developer' as developer;

import 'package:http/http.dart' as http;
import 'package:valuebrew/core/constants/app_constants.dart';

/// The result of checking a [CatalogRemoteSource] for a newer catalog.
class RemoteCatalogCheck {
  /// Whether a newer catalog than the one checked against is available.
  final bool hasUpdate;

  /// The newer catalog's raw JSON, if [hasUpdate] is `true`; otherwise
  /// `null`.
  final String? rawJson;

  /// No newer catalog is available.
  const RemoteCatalogCheck.noUpdate() : hasUpdate = false, rawJson = null;

  /// A newer catalog, [rawJson], is available.
  const RemoteCatalogCheck.updateAvailable(this.rawJson) : hasUpdate = true;
}

/// Checks for a catalog newer than [currentVersion].
///
/// This is the "c. remote catalog" step in `CatalogRepository`'s bundled
/// → cache → remote loading order — see the V1 technical architecture's
/// remote catalog update mechanism for the documented design this
/// prepares for (a background fetch from a CDN-hosted `catalog.json`,
/// compared by `catalog_version`).
abstract class CatalogRemoteSource {
  /// Returns whether a catalog newer than [currentVersion] is available,
  /// and its contents if so.
  Future<RemoteCatalogCheck> checkForUpdate(int currentVersion);
}

/// A [CatalogRemoteSource] that never reports an update.
///
/// This milestone builds only the interface real remote checking will
/// plug into later — there is no HTTP, no CDN integration, and no
/// networking of any kind here, all explicitly out of scope for this
/// milestone. See the Future Remote Updates notes in this milestone's
/// report for what a real implementation would add.
class StubCatalogRemoteSource implements CatalogRemoteSource {
  const StubCatalogRemoteSource();

  @override
  Future<RemoteCatalogCheck> checkForUpdate(int currentVersion) async {
    return const RemoteCatalogCheck.noUpdate();
  }
}

/// A [CatalogRemoteSource] that fetches the catalog over HTTP from
/// [catalogUrl], per the V1 technical architecture's Remote Catalog Update
/// Mechanism: fetch the whole file (no separate version-check endpoint),
/// then compare its `catalog_version` against [checkForUpdate]'s
/// `currentVersion`.
///
/// Every failure mode this is asked to handle — network unavailable,
/// timeout, a non-200 response, or a body that isn't valid/parseable JSON —
/// is caught here and turned into [RemoteCatalogCheck.noUpdate] rather than
/// thrown. [CatalogRepository] already treats a thrown remote-source error
/// as "ignore and keep whatever we have," so returning `noUpdate` directly
/// is equivalent but lets each failure path log something specific and be
/// tested in isolation, without relying on the repository's catch-all as
/// the only thing standing between a flaky network and a crash.
class HttpCatalogRemoteSource implements CatalogRemoteSource {
  /// Creates an [HttpCatalogRemoteSource].
  ///
  /// [catalogUrl] and [timeout] default to [AppConstants.remoteCatalogUrl]
  /// and [AppConstants.remoteFetchTimeout] — the single configured location
  /// for both — but can be overridden, e.g. in tests.
  ///
  /// [httpGet] is injected as a plain function, the same pattern
  /// [CatalogRepository.loadAsset] uses, rather than requiring a full
  /// [http.Client] — it lets tests substitute a fake fetch (including a
  /// deliberately slow one, to exercise the timeout) without constructing
  /// or mocking an [http.Client].
  HttpCatalogRemoteSource({
    Uri? catalogUrl,
    Duration? timeout,
    Future<http.Response> Function(Uri url)? httpGet,
  }) : catalogUrl = catalogUrl ?? Uri.parse(AppConstants.remoteCatalogUrl),
       timeout = timeout ?? AppConstants.remoteFetchTimeout,
       _httpGet = httpGet ?? http.get;

  /// Where the remote catalog JSON is fetched from.
  final Uri catalogUrl;

  /// How long a fetch may take before it's treated as a failure.
  final Duration timeout;

  final Future<http.Response> Function(Uri url) _httpGet;

  static const _logName = 'CatalogRemoteSource';

  @override
  Future<RemoteCatalogCheck> checkForUpdate(int currentVersion) async {
    final String rawJson;
    try {
      final response = await _httpGet(catalogUrl).timeout(timeout);
      if (response.statusCode != 200) {
        developer.log(
          'Remote catalog fetch returned HTTP ${response.statusCode}; '
          'falling back.',
          name: _logName,
        );
        return const RemoteCatalogCheck.noUpdate();
      }
      rawJson = response.body;
    } on TimeoutException {
      developer.log(
        'Remote catalog fetch timed out after $timeout; falling back.',
        name: _logName,
      );
      return const RemoteCatalogCheck.noUpdate();
    } catch (error) {
      developer.log(
        'Remote catalog fetch failed: $error; falling back.',
        name: _logName,
      );
      return const RemoteCatalogCheck.noUpdate();
    }

    final remoteVersion = _peekCatalogVersion(rawJson);
    if (remoteVersion == null) {
      developer.log(
        'Remote catalog response was not valid/parseable JSON; falling back.',
        name: _logName,
      );
      return const RemoteCatalogCheck.noUpdate();
    }

    if (remoteVersion <= currentVersion) {
      return const RemoteCatalogCheck.noUpdate();
    }

    developer.log(
      'Remote catalog fetch succeeded: version $remoteVersion is newer '
      'than $currentVersion.',
      name: _logName,
    );
    return RemoteCatalogCheck.updateAvailable(rawJson);
  }

  /// Reads just the `catalog_version` field out of [rawJson], without
  /// validating the rest of the catalog schema — full validation happens
  /// once, in [CatalogRepository]'s `_parseCatalog`, regardless of which
  /// source the JSON came from. Returns `null` for anything that isn't a
  /// JSON object with an integer `catalog_version`, which this class
  /// treats the same as "no update available."
  int? _peekCatalogVersion(String rawJson) {
    try {
      final decoded = jsonDecode(rawJson);
      if (decoded is Map<String, dynamic>) {
        final version = decoded['catalog_version'];
        if (version is int) return version;
      }
    } catch (_) {
      // Falls through to the `null` return below.
    }
    return null;
  }
}
