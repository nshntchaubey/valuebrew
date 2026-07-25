# Release Checklist

Run through this before every Play Store submission (internal testing
track or higher). Check off manually — nothing here runs itself.

## Automated checks

- [ ] `flutter analyze` passes with no issues
- [ ] `flutter test` passes, all green

## Release build

- [ ] Version bumped in `pubspec.yaml` (`version: X.Y.Z+N`) — this is the
      single source of truth for both Android `versionName`/`versionCode`
      and iOS `CFBundleShortVersionString`/`CFBundleVersion`
- [ ] `android/key.properties` present and correct (see
      `docs/RELEASE_SIGNING.md`) — confirm with:
      `apksigner verify --print-certs build/app/outputs/flutter-apk/app-release.apk`
      and check it's signed with the release key, not the debug fallback
- [ ] `flutter build appbundle --release` succeeds
- [ ] Release build installs and launches on a physical device or emulator

## Manual verification (on the release build, not `flutter run` debug)

- [ ] Remote catalog fetch works: confirm a launch actually reaches the
      configured URL (`AppConstants.remoteCatalogUrl`) — e.g. via
      `adb logcat` filtered on the `CatalogRemoteSource` log tag — and
      falls back cleanly with airplane mode on (no crash, no error shown)
- [ ] Favorites persist: favorite a beer, force-quit the app, relaunch,
      confirm it's still favorited
- [ ] Recommendations: open a beer detail screen, confirm similar-beer
      recommendations appear with reasons, and that switching
      recommendation profiles reorders them
- [ ] Filters: apply a style/ABV/price/value-score filter, confirm the
      list narrows correctly and "Clear filters" restores it
- [ ] Sorting: switch sort options on Home and Favorites, confirm order
      changes accordingly
- [ ] Accessibility: enable TalkBack (or a screen reader), confirm
      favorite-heart buttons announce their state ("Favorited" / "Not
      favorited") and primary actions are reachable
- [ ] Splash/icon: confirm the launcher icon (not the Flutter default)
      appears on the home screen and app drawer, and the splash shows the
      brand background + mark before the first frame — check on both an
      Android 12+ device (native SplashScreen API) and an older one
      (`launch_background.xml` path)

## Documentation

- [ ] `README.md` reflects the current feature set and setup steps
- [ ] `CHANGELOG.md` has an entry for this version
- [ ] `privacy_policy.md` still accurately describes what the app collects
      (re-check after any change touching networking or local storage)

## Store assets

- [ ] `store_listing.md` copy reviewed and current
- [ ] Screenshots captured per the checklist in `store_listing.md`
- [ ] Feature graphic (1024×500) ready
- [ ] 512×512 hi-res icon exported
- [ ] Play Console Data Safety form filled in, consistent with
      `privacy_policy.md` (no personal data collected, no third parties)
- [ ] Privacy policy URL set in Play Console (this file needs to be
      hosted somewhere public — e.g. a GitHub Pages page or raw GitHub
      URL — a local Markdown file isn't enough; Play Console requires a
      reachable link)
