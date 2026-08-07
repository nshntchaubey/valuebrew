# ValueBrew — Engineering

**Repository path:** `docs/engineering/README.md`
**Sits below:** the Canonical Architecture (`architecture/`, frozen)
**Status:** Active — engineering work in progress

---

## Purpose

This folder is where the frozen Canonical Architecture becomes buildable software. It holds every document produced *after* product behavior was fixed and *before* a single line of Flutter code is written: how engineering work is planned and sequenced, how the canon gets translated into a software architecture, how that architecture gets operationalized into a concrete build, and how each screen's canonical Screen Contract gets restated in an implementation-ready form.

Nothing in this folder defines or redefines product behavior. Every document here either plans engineering work around an already-frozen decision, or restates one in a form suited to implementation — the same citation-only discipline the Canonical Screen Specification Template already established at the architecture layer continues here.

---

## Relationship to the Canonical Architecture

The Canonical Architecture (`architecture/`) remains the single source of product truth — behavior-first, platform-independent, frozen pending its own versioned changes. This folder never reinterprets it. Every document under `engineering/` either cites the canon directly (an Engineering Specification citing its Screen Contract) or organizes work around what the canon already established (the Flutter Implementation Architecture's screen-to-module mapping, the Bootstrap Plan's milestones). If a gap is ever found here that the canon doesn't already resolve, the correct response is to raise it against the canon, never to resolve it locally.

## Relationship to the Flutter Implementation Architecture

`implementation/Flutter-Implementation-Architecture.md` is the first document in this folder that makes a technology decision. It answers *how* ValueBrew gets built in Flutter — state management, navigation, project structure, domain/data/presentation layering, error handling, testing strategy — without touching *what* gets built. It is the software architecture every other implementation document in this folder builds on.

## Relationship to the Implementation Bootstrap Plan

`implementation/Implementation-Bootstrap-Plan.md` takes the Flutter Implementation Architecture as settled and turns it into a concrete starting point: specific packages with justification, the initial project scaffold, and a milestone-by-milestone build roadmap. It doesn't revisit any architectural decision — it operationalizes the ones already made.

## Relationship to Engineering Specifications

`specifications/` holds the Engineering Screen Specifications — each screen's canonical Screen Contract restated, field by field, by direct citation, using the Canonical Screen Specification Template. These are the concrete artifact the Flutter Implementation Architecture's screen-to-module mapping and the Bootstrap Plan's per-screen milestones are built against. A screen's presentation layer is never implemented ahead of its own specification existing here — this rule has already governed a real sequencing decision in this folder's history (see the Repository Synchronization Patch, on Price Verification).

## Relationship to Future Flutter Implementation

The Flutter application itself is a separate codebase, not part of this documentation tree. Everything in this folder exists to be built from, in the order below, and to be checked against once building starts — a specification-complete screen, an architectural decision, or a milestone's Definition of Done should all be directly traceable back to a document here.

---

## Engineering Folder Structure

```
engineering/
├── README.md
├── INDEX.md
├── CHANGELOG.md
├── Engineering-Planning-Roadmap.md
├── KSBCL-*.md                    — independent pricing-pipeline workstream, see INDEX.md
├── implementation/
│   ├── Flutter-Implementation-Architecture.md
│   ├── Implementation-Bootstrap-Plan.md
│   └── Repository-Sync-Patch-Price-Verification.md
├── specifications/
└── standards/
```

- **`Engineering-Planning-Roadmap.md`** — sequences and prioritizes engineering work across the whole project; the starting point for everything else in this folder.
- **`KSBCL-*.md`** — the KSBCL pricing pipeline: a separate, non-Flutter data-engineering workstream with its own architecture, product decisions, and governance model, indexed under "KSBCL Pricing Pipeline" in `INDEX.md`. Does not follow the Engineering Documentation Flow below, which describes the Flutter product engineering path only.
- **`implementation/`** — the software architecture and build-planning documents: how the canon gets built, not what gets built.
- **`specifications/`** — the Engineering Screen Specifications, one per screen, each a citation-only restatement of its canonical Screen Contract.
- **`standards/`** — reserved for future engineering-wide standards (accessibility, telemetry, coding conventions) once ratified at the canonical layer; currently empty, consistent with the canon's own explicit deferral of these (Canonical Screen Specification Template, Sections 11–12).

---

## Recommended Reading Order

Engineering Planning Roadmap
↓
Flutter Implementation Architecture
↓
Implementation Bootstrap Plan
↓
Engineering Screen Specifications
↓
Flutter Implementation
