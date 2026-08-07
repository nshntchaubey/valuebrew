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

## KSBCL Pricing Pipeline

An independent engineering workstream, not sequenced against the Engineering Documentation Flow above and not part of the Flutter app: a Python data pipeline that ingests KSBCL's monthly PDF price list, classifies which rows are beer, normalizes names and pack sizes, and resolves the result to a stable canonical product identity. Code and tests live in `tool/ksbcl_pricing_pipeline/`; real run output lives in `pricing_data/` (git-ignored — check that folder's own state before assuming its contents are on GitHub).

**Reading order:**

1. **KSBCL-Beer-Pricing-Pipeline-Architecture.md** — the master architecture: the four-stage pipeline, every artifact's field sketch, and the product decisions settled once at the top (Duty-Free exclusion, implementation language, the original auto-merge confidence bar). Read first.
2. **KSBCL-Stage-1-Extraction-Contract.md** — raw PDF → `structured_rows.csv`. Frozen, implemented, tested.
3. **KSBCL-Stage-2-Beer-Identification-Architecture.md** — beer/not-beer classification, the persistent known-terms ledger and review queue. Frozen, implemented, tested.
4. **KSBCL-Stage-3-Normalization-Architecture.md** — name folding and pack-size/container extraction. Frozen, implemented, tested.
5. **KSBCL-Stage-4-Canonical-Identity-Product-Discussion.md**, **-Settlement.md**, **-Product-Identity-Charter.md**, **-User-Mental-Model.md** — the product-design phase that preceded Stage 4's architecture, working through what "the same product" should mean before any mechanism was drafted.
6. **KSBCL-Stage-4-Identity-Decision.md** — the two Product Decisions that came out of that phase (`supplier_code` excluded from canonical identity; multi-candidate ambiguity deferred to manual review, not auto-resolved), each recorded with rationale and accepted trade-off.
7. **KSBCL-Stage-4-Canonical-Identity-Architecture.md** — Stage 4's architecture, built on the above. Revised twice; see its own status banner for what changed and why. Not yet implemented.
8. **KSBCL-Stage-4-Review-Closure-Report.md** — the historical record of the adversarial review that produced Stage 4's architecture and the Identity Decisions: what was corrected, what was investigated and rejected, and why the review concluded.
9. **KSBCL-Repository-Governance.md** — eleven conventions extracted from repeated practice across Stages 1–4, not a new policy — written for whoever drafts Stage 5.
10. **KSBCL-Engineering-Process-Retrospective.md** — the blank-page-to-frozen workflow Stages 2–4 actually followed, extracted for Stage 5's author to reuse rather than rediscover by trial.

**Status as of this index:** Stages 1–3 implemented and tested (182 tests, `tool/ksbcl_pricing_pipeline/`), run against a real June 2026 KSBCL price list. Stage 4 is architecture only, frozen in intent with two known-open freeze-review questions recorded in its own §13. Stage 5 (master catalogue construction) has not been designed.

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
