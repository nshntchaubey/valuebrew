# Release Signing Setup

ValueBrew's release build signs with the debug key by default, so
`flutter build apk --release` and `flutter build appbundle` work out of the
box for anyone who clones the repo. To publish a real release (Play Store,
internal testing tracks, or a signed APK handed to someone else), generate
a real release key and point the build at it — neither the keystore nor
its passwords are ever committed to this repo.

## 1. Generate a keystore (once, ever — keep it forever)

```bash
keytool -genkey -v -keystore ~/valuebrew-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias valuebrew
```

This prompts for a store password, a key password, and identity details
(name, org, etc. — anything reasonable; the Play Store doesn't display
these). Store the resulting `.jks` file somewhere durable and backed up
**outside this repo** — Play Store app-signing lets Google re-sign your
uploads with a separate upload key even if you lose the original, but
losing your upload key still means going through key-loss recovery with
Google, so don't treat this file as disposable.

## 2. Point the build at it

Copy the template and fill in real values:

```bash
cp android/key.properties.example android/key.properties
```

Edit `android/key.properties`:

```properties
storePassword=<the store password you set above>
keyPassword=<the key password you set above>
keyAlias=valuebrew
storeFile=/absolute/path/to/valuebrew-release.jks
```

`android/key.properties` is already gitignored (`android/.gitignore`), as
are `**/*.jks` and `**/*.keystore` — this file and the keystore itself
must never be committed.

## 3. Build

```bash
flutter build appbundle --release   # Play Store upload format
flutter build apk --release         # a signed APK, e.g. for direct sharing
```

`android/app/build.gradle.kts` picks up `android/key.properties`
automatically when it exists and signs the release build type with it;
when the file is absent (e.g. a fresh clone, or CI without secrets), it
falls back to the debug key so the build still succeeds.

## Verifying which key signed a build

```bash
apksigner verify --print-certs build/app/outputs/flutter-apk/app-release.apk
```

Compare the certificate fingerprint against `keytool -list -v -keystore
~/valuebrew-release.jks` to confirm the release build was actually signed
with the release key, not a silent debug-key fallback (e.g. because
`android/key.properties` was missing or misconfigured).
