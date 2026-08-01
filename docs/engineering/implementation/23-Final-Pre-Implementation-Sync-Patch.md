# ValueBrew — Repository Synchronization Patch (Final, Pre-Implementation)

**Source of truth:** Engineering Readiness Review
**Scope:** three items only — Navigation Contract enforcement ordering, App Store compliance ownership, Backend/Beer Knowledge Base ownership.
**Nature of this patch:** wording synchronization and risk-tracking only. No new architecture, no new documents, no redesign. Repository policy: fix genuine inconsistencies, don't inflate tracked risks into blockers.

All changes below have been applied directly to `Flutter-Implementation-Architecture.md` and `Implementation-Bootstrap-Plan.md`, along with the previously-agreed Price Verification patch (written up in the prior synchronization but not yet applied to the files at that time — it is now).

---

## 1. Navigation Contract Enforcement Ordering

**Document:** Flutter Implementation Architecture
**Section:** Recommended Build Order

**Existing wording:**
> 1. Domain layer + canonical-rule unit tests first...
> 2. Catalog repository + local cache...
> 3. Discovery Module: Home → Search/Browse Results → Beer Detail...
> 4. Verification Module: Price Verification...
> 5. Recommendation Module...
> 6. Comparison Module...
> **7. Navigation Contract enforcement wiring across all screens, plus the illegal-navigation tests.**
> 8. Cross-cutting presentation...
> 9. Offline hardening, build flavors, CI...

**Replacement wording:**
> 1. Domain layer + canonical-rule unit tests first...
> 2. Catalog repository + local cache...
> **3. Navigation Contract enforcement wiring across all screens, plus the illegal-navigation tests — built before any screen, since Home cannot legally navigate anywhere without this layer already in place.**
> 4. Discovery Module: Home → Search/Browse Results → Beer Detail...
> 5. Verification Module: Price Verification...
> 6. Recommendation Module...
> 7. Comparison Module...
> 8. Cross-cutting presentation...
> 9. Offline hardening, build flavors, CI...

**Rationale:** the Bootstrap Plan's M3 (navigation, before any screen) is authoritative per repository policy, since Home structurally depends on the navigator to route at all. The Architecture document's prose list is reordered to match — same nine items, no content removed or added beyond the one clause explaining *why* navigation now comes third, which prevents the same ambiguity recurring for the next reader.

---

## 2. App Store Compliance

**Document:** Flutter Implementation Architecture
**Section:** Implementation Risks

**Existing wording:** no entry existed for this risk.

**Replacement wording (new bullet, appended):**
> "App store compliance for alcohol-related content is untracked. ValueBrew recommends, compares, and prices alcoholic beverages; both major app stores impose category-specific requirements (age-gating/verification, content-rating declarations, a published privacy policy) that nothing in this document currently assigns an owner to. Tracked here as a release-readiness risk, owned by Milestone 9 in the Implementation Bootstrap Plan — not a reason to change anything the app does."

**Document:** Implementation Bootstrap Plan
**Section:** M9 — Offline Hardening, Release Configuration, Polish

**Existing wording:**
> **Deliverables:** ...app icons, splash, and store metadata.
> **Definition of Done:** ...a release build succeeds for both platforms.

**Replacement wording:**
> **Deliverables:** ...app icons, splash, and store metadata; app store compliance for alcohol-related content (age-gating/verification, content-rating declarations, published privacy policy) confirmed against current Google Play and Apple App Store requirements.
> **Definition of Done:** ...a release build succeeds for both platforms; app store compliance items are confirmed complete, not merely reviewed.

**Rationale:** the smallest available move — one Risk bullet naming it, one milestone deliverable giving it a home and an owner (M9). No release checklist document, no new architecture.

---

## 3. Backend / Beer Knowledge Base Ownership

**Document:** Flutter Implementation Architecture
**Section:** Implementation Risks

**Existing wording:** no entry existed; the fact lived only in Implementation Assumptions.

**Replacement wording (new bullet, appended):**
> "No committed decision or owner yet exists for the Beer Knowledge Base's backend/data source. Milestone 2 (Catalog Platform Service) can proceed against a stubbed or mocked remote source without this being resolved, so it does not block implementation start. It is tracked here, explicitly, as an open external dependency this document takes no position on — see Implementation Assumptions below — and should be assigned an owner and a target decision point before the milestones that depend on real catalog data (M6 onward) are reached."

**Document:** Flutter Implementation Architecture
**Section:** Implementation Assumptions

**Existing wording:**
> "The Beer Knowledge Base's backend/data source is not yet decided; this document assumes a network API exists or will exist, fronted entirely by `BeerCatalogRepository`, and takes no position on its technology."

**Replacement wording:**
> "...takes no position on its technology. Tracked as an owned, milestone-linked risk under Implementation Risks above, not left as a background assumption alone."

**Rationale:** elevates an existing statement from passive assumption to tracked risk without choosing a backend, without inflating it into a blocker (M2 explicitly still proceeds on a stub), and without touching the Bootstrap Plan, since M2 already handles this operationally.

---

## Final Assessment

**READY FOR IMPLEMENTATION**

All three items from the Engineering Readiness Review are resolved at the documentation level: the ordering conflict is reconciled, and both remaining risks are named, owned, and tied to a specific milestone rather than left as untracked assumptions. Nothing here required new architecture, a new document, or a redesign — each was a wording change to something already in the repository. M0 can begin.
