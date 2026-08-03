# ValueBrew — Engineering Index

**Repository path:** `docs/engineering/INDEX.md`

---

## Engineering Planning

- **Engineering-Planning-Roadmap.md** — sequences and prioritizes engineering work across the project. Read first.

---

## Implementation Planning

### Flutter Implementation Architecture
- **Purpose:** defines the software architecture for building ValueBrew in Flutter — state management, navigation, project structure, domain/data/presentation layering, error handling, and testing strategy — and maps the Engineering Specifications to Flutter modules.
- **Inputs:** the Canonical Architecture (frozen), the Engineering Screen Specifications available at the time of writing, the Navigation Contract.
- **Outputs:** twenty architectural decisions, a Recommended Build Order, an Implementation Risks and Assumptions list.
- **Dependencies:** Canonical Architecture; presumes each screen's Engineering Specification either exists or is explicitly flagged as pending.

### Implementation Bootstrap Plan
- **Purpose:** operationalizes the Flutter Implementation Architecture into a concrete, buildable starting point.
- **Inputs:** Flutter Implementation Architecture (approved), Engineering Screen Specifications, the Feature Inventory's Core V1 classification, the Navigation Contract.
- **Outputs:** a justified SDK and package inventory, the initial folder and `pubspec.yaml` structure, a nine-milestone roadmap (M0–M9), a recommended first screen.
- **Dependencies:** Flutter Implementation Architecture.

### Repository Synchronization Patch
- **Purpose:** reconciles the Flutter Implementation Architecture and Implementation Bootstrap Plan with a repository change — the arrival of the Price Verification Engineering Specification — without introducing new architecture or new implementation decisions.
- **Inputs:** the Price Verification Engineering Screen Specification, the Flutter Implementation Architecture and Implementation Bootstrap Plan as they stood before the patch.
- **Outputs:** eight itemized wording changes across the two documents.
- **Dependencies:** Flutter Implementation Architecture, Implementation Bootstrap Plan, Price Verification Engineering Screen Specification.

---

## Version 1 Architecture Reference

- **Version-1-Architecture-Reference.md** — the permanent, as-built engineering reference for Version 1: navigation graph, screen and domain ownership, shared infrastructure, repository conventions, and every intentionally deferred capability with its concrete blocker. Distinct from the Implementation Planning documents above, which describe original intent against a larger eventual scope — this document describes only what was actually built. Authoritative for Version 1's real behavior; frozen until repository behavior, the canon, the Product Definition, or a new Screen Contract changes.

---

## Engineering Retrospective

- **Engineering-Retrospective.md** — the closed engineering record for the canonical rebuild: architectural evolution, engineering principles demonstrated, decisions that proved correct or changed, mistakes the review process caught, review methodology, repository maturity, and guidance for future contributors. Distinct from the Architecture Reference above, which describes *what was built* — this document describes *how it was built*. Read once, kept as history; never updated to track new work.

---

## Engineering Specifications

Held in `specifications/`. Each is a citation-only restatement of its canonical Screen Contract, produced via the Canonical Screen Specification Template. Status as of this index: Home, Recommendation, Beer Detail, Comparison, and Price Verification each have a completed specification tied directly to their own canonical Screen Contract. Search/Browse Results also has a completed specification, produced to close the Navigation Contract's flagged structural gap, ahead of that screen having a dedicated canonical Screen Contract of its own.

---

## Engineering Standards

Held in `standards/`. Currently empty — reserved for accessibility, telemetry, and coding-convention standards once ratified at the canonical layer.

---

## Engineering Documentation Flow

Engineering Planning
↓
Implementation Architecture
↓
Implementation Bootstrap
↓
Engineering Specifications
↓
Flutter Implementation
↓
Testing
↓
Release
