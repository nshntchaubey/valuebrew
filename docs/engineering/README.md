# ValueBrew Engineering Documentation

## Purpose

This folder translates the frozen Canonical Architecture into build-ready specifications for ValueBrew's six screens. It exists to remove engineering ambiguity — exact states, exact validation thresholds, exact UI elements with their required and optional data — without introducing a single product decision the Canonical Architecture didn't already make.

Nothing in this folder originates product behavior. Every specification here is a translation of an existing Screen Contract, not a new design.

## Relationship to the Canonical Architecture

The Canonical Architecture (nineteen foundational documents plus six Screen Contracts, the Navigation Contract, the Canonical Interaction Lexicon, the Canonical Screen Specification Template, and the Architectural Decisions Record) is upstream of everything in this folder and remains the sole source of product-behavior authority. Every statement in every document here traces to a specific canonical section. Where the canon leaves something genuinely undecided, the corresponding specification says so explicitly rather than filling the gap by inference. This folder has no authority to resolve an open architectural question — only to state precisely where and how it remains open.

## Relationship to Engineering Planning

The Engineering Planning Roadmap is this folder's own starting point. It identified which specifications needed to be written, in what order, which could proceed in parallel, and what would constitute MVP implementation readiness. Every specification in this folder exists because the Roadmap named it as necessary.

## Relationship to Flutter Implementation

This folder is the boundary, not the destination. It defines behavior — states, validation rules, required data, acceptance criteria — completely independent of any specific technology. No Flutter widget, API, or backend design appears anywhere in this folder; that work begins after these specifications, using them as a build reference, not before them or in place of them.

## Intended Audience

- **Flutter engineers**, as the primary build reference for each screen.
- **UI/UX designers**, for wireframing against defined states, elements, and content requirements.
- **QA engineers**, for building acceptance tests directly from each specification's Acceptance Criteria and Traceability Matrix.
- **New engineering hires**, as the fastest path to understanding what to build and why, without needing to read the full twenty-document canon first.

## Reading Order

1. **Engineering Planning Roadmap** — context for why these six specifications exist and how they relate to one another.
2. **Home** — the product's sole entry point; the simplest screen, and the one every other screen is eventually reached from.
3. **Search/Browse Results** — the routing layer immediately downstream of Home; still no product reasoning, but the first screen with a real catalog dependency.
4. **Recommendation** — the product's core synthesis screen; the most complex specification, and the one most worth understanding well before the others that hand off to or from it.
5. **Beer Detail** — the single-SKU complement to Recommendation, sharing its Explanation and Confidence structures without duplicating them.
6. **Comparison** — the multi-candidate extension of Recommendation's own trade-off and tie-handling logic.
7. **Price Verification** — the narrowest, most self-contained screen; deliberately read last, since it depends on the least context from the other five.

## Repository Philosophy

Every specification in this folder follows the same discipline the Canonical Architecture itself was built under:

- **Citation over invention.** A statement that can't be traced to a canonical document doesn't belong here.
- **Explicit gaps over silent resolution.** Where the canon hasn't decided something, the specification says "Intentionally left unspecified by the Canonical Architecture" rather than guessing a plausible answer.
- **Behavior over implementation.** These documents describe what must be true, never how to build it.
- **Translation over redesign.** An Engineering Screen Specification's job is to make an already-approved Screen Contract precise enough to build from — not to improve, simplify, or reinterpret it.

## What This Folder Intentionally Does NOT Contain

- Flutter widgets, packages, or code of any kind.
- API definitions or backend/database design.
- Visual layouts, wireframes, typography, or color decisions.
- A finalized accessibility standard or telemetry/analytics event schema — both are deliberately deferred pending dedicated, cross-screen standards, consistent with the Canonical Screen Specification Template's own placeholder discipline.
- Resolved answers to the architectural questions still open across these six specifications. Each remaining gap is flagged precisely, in place, rather than answered here.
- Product strategy, market reasoning, or user research — all of that belongs to the Canonical Architecture, not this folder.

## Repository Structure

```
Engineering/
├── README.md                                          (this document)
├── INDEX.md                                            (navigation entry point)
├── CHANGELOG.md                                        (milestone record)
├── Engineering-Planning-Roadmap.md
├── Engineering-Spec-Home.md
├── Engineering-Spec-Search-Browse-Results.md
├── Engineering-Spec-Recommendation.md
├── Engineering-Spec-Beer-Detail.md
├── Engineering-Spec-Comparison.md
└── Engineering-Spec-Price-Verification.md
```

This folder sits alongside, and strictly downstream of, the Canonical Architecture folder. It does not duplicate that folder's contents; it cites them.

## Maintenance Principles

- **A specification's authority never exceeds its source.** If a Screen Contract changes, the corresponding Engineering Screen Specification must be re-validated against it before it can be trusted again — a specification built against a superseded version of its Screen Contract is not current, regardless of its own internal consistency.
- **Every specification's Traceability Matrix is load-bearing, not decorative.** It exists so that a change to any cited canonical section can be traced forward to every specification it affects.
- **New specifications follow the same Template discipline as the existing six.** No new document in this folder should introduce a structure, a section, or a citation convention inconsistent with what's already established here.
- **Open items are tracked, not buried.** A gap flagged inside one specification should also be discoverable from the architecture layer — an unresolved question that exists only inside an engineering document is a maintenance risk, not a closed matter.
- **This README is updated whenever a document is added to or removed from this folder.** A stale index is worse than no index.
