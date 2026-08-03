# ValueBrew — Version Status

**Version:** 1.0.0
**Architecture status:** Frozen.
**Canon status:** Fully compliant for everything implemented. No
contradiction, omission, over-implementation, or under-implementation
found against `docs/architecture/current/` for any shipped capability.
**Repository status:** Internally consistent. `flutter analyze` clean;
no stale documentation, dead code, or unresolved inconsistency remains
as of this version.
**Testing status:** 562 tests passing, unit and widget, covering every
domain function and every screen independently.
**Documentation status:** Complete for what's implemented —
`docs/engineering/Version-1-Architecture-Reference.md` is the permanent,
as-built engineering reference; `README.md`, `RELEASE_NOTES.md`,
`CHANGELOG.md`, `privacy_policy.md`, and `store_listing.md` all describe
the application exactly as it exists today.

## What Version 1 is

Home → Recommendation (budget, Style refinement, Tie Disclosure,
Planning Mode) → Beer Detail → Price Verification. See the Architecture
Reference for full detail on ownership, navigation, and design
principles; see `CHANGELOG.md` for what shipped, milestone by milestone.

## What Version 1 intentionally excludes

Search/Browse, Comparison, Trade-off Explanation, Confirm-as-Is,
preferences beyond budget and style, Proxy-Buying Mode, and any account
or persistence layer — each with its specific blocker (a missing
canonical Screen Contract, a missing second simultaneous preference
input, or an explicit Product Definition deferral) recorded in the
Architecture Reference's "Intentionally Deferred Capabilities" section.

## Version 2 trigger

Version 2 work begins only when one of the following actually changes:

- **Repository behavior** — a new, self-documented gap or defect is
  discovered in what's already built.
- **Canon** — an existing canonical document is revised.
- **New Product Definition** — the Product Definition Document is
  revised or superseded.
- **New Screen Contract** — a canonical Screen Contract is authored for
  a capability that currently has none.

Absent one of these four, no further architecture review, milestone
planning, or implementation work should be undertaken against this
repository. This file, together with the Architecture Reference, is the
authoritative statement of Version 1's status until one of them occurs.
