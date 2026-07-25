# Project-specific ProGuard/R8 rules for the release build.
#
# Empty by design: Flutter and flutter_riverpod are pure Dart, compiled to
# the Flutter engine rather than run as reflected-over JVM bytecode, so
# they need no keep rules. http, shared_preferences, and path_provider each
# ship their own consumer ProGuard rules bundled in their AARs, applied
# automatically by R8 — nothing here needs to duplicate them.
#
# Add rules here only when a real R8/release crash points at a specific
# stripped or obfuscated class (e.g. a plugin relying on Java reflection or
# JSON (de)serialization by field name).
