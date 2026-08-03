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
- [ ] `android/key.properties` present and correct — confirm with:
      `apksigner verify --print-certs build/app/outputs/flutter-apk/app-release.apk`
      and check it's signed with the release key, not the debug fallback
- [ ] `flutter build appbundle --release` succeeds
- [ ] Release build installs and launches on a physical device or emulator

## Manual verification (on the release build, not `flutter run` debug)

- [ ] Remote catalog fetch works: confirm a launch actually reaches the
      configured URL (`AppConstants.remoteCatalogUrl`) and falls back
      cleanly with airplane mode on (no crash, no error shown)
- [ ] Get a recommendation: enter a budget, confirm a specific beer and
      an explanation appear
- [ ] Style refinement: refine a recommendation by style, confirm the
      result updates and can be cleared back to "No preference"
- [ ] Tie Disclosure: confirm a budget that produces a genuine tie shows
      every tied beer, each with its own path to full details, rather
      than a single arbitrary pick
- [ ] Beer Detail: from a recommendation, confirm price, size, package,
      ABV, value score, and price-checked date all display
- [ ] Price Verification: from Beer Detail, confirm entering a charged
      price returns the correct at/below/above classification
- [ ] Planning Mode: use "I'm planning ahead" from Home, confirm the
      standing caveat appears alongside the recommendation and persists
      through a budget edit or style refinement
- [ ] Accessibility: enable TalkBack (or a screen reader), confirm
      primary actions are reachable and announced correctly
- [ ] Splash/icon: confirm the launcher icon (not the Flutter default)
      appears on the home screen and app drawer

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
      hosted somewhere public — a local Markdown file isn't enough;
      Play Console requires a reachable link)
