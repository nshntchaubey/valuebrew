import java.io.FileInputStream
import java.util.Properties

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// Release signing: reads android/key.properties if present (gitignored —
// see android/key.properties.example and docs/RELEASE_SIGNING.md), falling
// back to debug signing otherwise. This is what lets `flutter build apk`
// keep working for anyone who clones the repo without a real keystore,
// while still supporting a real release signature once one exists.
val keystorePropertiesFile = rootProject.file("key.properties")
val keystoreProperties = Properties()
val hasReleaseKeystore = keystorePropertiesFile.exists()
if (hasReleaseKeystore) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    namespace = "com.nishantchaubey.valuebrew"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        applicationId = "com.nishantchaubey.valuebrew"
        // minSdk/targetSdk are left at Flutter's own managed defaults
        // (currently minSdk 21 / targetSdk from the installed Flutter SDK)
        // rather than pinned here, so they stay current automatically on
        // every `flutter upgrade` instead of silently drifting behind.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        // versionCode/versionName are read from pubspec.yaml's `version:`
        // field (the single source of truth — see AppConstants doc note)
        // rather than duplicated here.
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (hasReleaseKeystore) {
            create("release") {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        release {
            // Signs with the real release key once android/key.properties
            // exists (see docs/RELEASE_SIGNING.md); otherwise falls back to
            // the debug key so `flutter build apk --release` still works
            // for local/CI builds that aren't being published.
            signingConfig = if (hasReleaseKeystore) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }
            // R8 shrinking + resource shrinking for release builds. Flutter
            // and flutter_riverpod are pure Dart (compiled to the Flutter
            // engine, not reflected-over Kotlin/Java), and http /
            // shared_preferences / path_provider each ship their own
            // consumer ProGuard rules inside their AARs — so no
            // project-specific keep rules have been needed so far.
            // proguard-rules.pro exists as the place to add any if a future
            // dependency needs them.
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
