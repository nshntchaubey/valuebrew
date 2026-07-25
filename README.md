# ValueBrew

## Project Overview

ValueBrew is a Flutter application that helps users find the best beer,
one pint at a time. The project is in early development: the application
shell exists, the core dependencies are in place, and the codebase is
organized around a feature-first architecture ready for implementation.

## MVP Goal

Deliver a mobile-first app that lets a user browse a curated catalogue of
beers and view details for each one, without requiring a backend service.
The V1 catalogue is sourced from a local JSON file bundled with the app.

## Tech Stack

- **Flutter** 3.44.8 (stable channel) / **Dart** 3.12.2
- **flutter_riverpod** — state management
- **http** — networking (future backend integration)
- **shared_preferences** — local key-value persistence
- **path_provider** — filesystem path access
- **flutter_lints** — static analysis and recommended lint rules

## Folder Structure

The codebase follows a feature-first architecture:

```
lib/
  core/
    constants/     # App-wide constant values
    theme/          # App theming (colors, text styles, etc.)
    utils/          # Shared utility functions
  data/
    models/         # Immutable data models
    repositories/   # Repository pattern implementations
    sources/        # Data sources (e.g. local JSON catalogue)
  features/
    home/           # Home feature
    search/         # Search feature
    beer_detail/    # Beer detail feature
  routing/          # App navigation and routing
  main.dart         # App entry point
```

## Setup Instructions

1. Install [Flutter](https://docs.flutter.dev/get-started/install) (stable channel).
2. Clone the repository and install dependencies:

   ```bash
   flutter pub get
   ```

3. Run the app on a connected device or simulator:

   ```bash
   flutter run
   ```

## Running Tests

```bash
flutter test
```

Run static analysis before submitting changes:

```bash
flutter analyze
```

## Current Project Status

- Application shell in place ([lib/main.dart](lib/main.dart)) with a basic
  home screen.
- Core dependencies added (Riverpod, http, shared_preferences, path_provider),
  not yet wired into the app.
- Feature-first folder structure scaffolded under `lib/`; no feature logic
  has been implemented yet.
- A single widget test verifies the home screen renders correctly.
- No backend integration; the V1 catalogue will be a local JSON file.
