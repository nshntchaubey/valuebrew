# ValueBrew — Engineering Planning Roadmap

**Prepared by:** Founding Product Manager
**Status:** Bridges Canonical Architecture v1.0 (post-Resolution Report) to the start of engineering work.
**Governing rule throughout:** no item below may be resolved by invention. Every decision item produces a new, explicit entry in the Architectural Decisions Record, exactly as the canon already does for its existing decisions (ADR §3) — never a silent assumption buried in a specification.

---

## A. Remaining Work Inventory

| # | Item | Type | Canonical Basis | MVP-blocking? |
|---|---|---|---|---|
| 0.1–0.5 | Apply the five Resolution Report edits (C1, M1, M2, M3-citation, M4) | Documentation closure | Resolution Report §2 | Yes — gates everything below |
| 1.1 | Write Search/Browse Results Screen Contract | New canonical document | IA §2; ADR §7 ("the single most structurally significant open item"); Navigation Contract §1 | **Yes** |
| 1.2 | Decide the Anchor Situation determination rule | ADR decision | Beer Detail Screen Contract §11; ADR §7 | Yes |
| 1.3 | Decide ambiguous preference-type handling | ADR decision | Recommendation Screen Contract §11; ADR §7 | Yes |
| 1.4 | Decide imprecise/approximate charged-price handling | ADR decision | Price Verification Screen Contract §11; ADR §7 | Yes |
| 1.5 | Decide 3+ candidate comparison logic (scoped to both Comparison and Recommendation, per Resolution Report M3) | ADR decision | Comparison Screen Contract §11; Recommendation Screen Contract §11 (post-M3 edit); ADR §7 | Yes |
| 1.6 | Amend Navigation Contract's two SBR-dependent edges once 1.1 is decided | Documentation closure | Navigation Contract §1, §14 | Yes, for Beer Detail and Comparison Specifications only |
| 2.1–2.6 | Write six Screen Specifications (Home, Recommendation, Beer Detail, Price Verification, Search/Browse Results, Comparison) | New canonical-adjacent documents | Canonical Screen Specification Template (18); ADR §6 | 2.1–2.4 yes; 2.5 yes (SBR is a Home destination); 2.6 no — see Section E |

Nothing else is missing at the architecture layer. Accessibility (Template §11) and Telemetry (Template §12) remain deliberately unfilled placeholders — the canon defers both pending standards that don't exist yet (Review Guide §9), and filling them now would be invention, not completion. They stay open, correctly, past MVP.

---

## B. Dependency Graph

```
Phase 0 — Close Resolution Report (0.1–0.5)
        │
        ├──────────────┬──────────────┬──────────────┐
        ▼               ▼              ▼              ▼
  1.1 SBR Contract   1.2 Anchor     1.3 Ambiguous   1.4 Imprecise
  (large, novel,     rule           preference       price rule
  highest priority)  (Beer Detail)  (Recommendation) (Price Verif.)
        │                                                  
        ▼                                            1.5 3+ candidate
  1.6 Navigation Contract                             logic (Compar. +
  amendment (2 SBR edges)                              Recommendation)
        │
        ├───────────────┬────────────────┐
        ▼                ▼                ▼
  2.5 SBR Spec      2.3 Beer Detail   2.6 Comparison
  (needs 1.1)        Spec (needs      Spec (needs
                      1.2 + 1.6)       1.5 + 1.6)

  2.1 Home Spec ─────── needs only Phase 0 (C1 already closed there)
  2.2 Recommendation Spec ─── needs Phase 0 + 1.3 + 1.5
  2.4 Price Verification Spec ─── needs Phase 0 + 1.4
```

**Read plainly:** Phase 0 gates everything. Item 1.1 (Search/Browse Results Contract) is the long pole — it's the only Phase 1 item that is itself a full 14-section document rather than a single rule decision, and it's the sole blocker for two of the six Specifications plus the Navigation Contract amendment. Everything else in Phase 1 is independently decidable in parallel.

---

## C. Parallelization Plan

**Can start immediately after Phase 0 closes, in parallel, with no cross-dependency:**
- 1.1 (Search/Browse Results Contract) — assign first; largest scope.
- 1.2 (Anchor rule)
- 1.3 (Ambiguous preference-type rule)
- 1.4 (Imprecise price rule)
- 1.5 (3+ candidate logic)

These five are owned by the same decision-making process (PM + relevant stakeholders, recorded as new ADR entries) but touch disjoint parts of the canon and don't require sequencing relative to each other.

**Can start immediately after Phase 0 closes, in parallel with all of Phase 1:**
- 2.1 Home Specification — its only open dependency (C1) closed in Phase 0.

**Can start once their single respective Phase 1 item closes, without waiting on the others:**
- 2.2 Recommendation Specification — needs 1.3 and 1.5 specifically, not 1.1, 1.2, or 1.4.
- 2.4 Price Verification Specification — needs 1.4 specifically, not the rest.

**Must wait on 1.1 and its downstream 1.6 amendment:**
- 2.5 Search/Browse Results Specification — cannot exist before its own Contract does.
- 2.3 Beer Detail Specification — needs 1.2 (its own gap) *and* 1.6 (the Navigation Contract's SBR→Beer Detail edge) for full completion.
- 2.6 Comparison Specification — needs 1.5 (its own gap) *and* 1.6 (the SBR→Comparison edge).

**Net effect:** three of the six Specifications (Home, Recommendation, Price Verification) can be fully complete well before the other three, since they don't sit downstream of the Search/Browse Results work at all.

---

## D. The Architecture → Engineering Transition Point

The transition is not a calendar date or a milestone ceremony — it's a specific, checkable state, and the canon already defines where it sits: the ADR states plainly that *"no code, framework, or technical architecture has been decided"* (ADR §7) as of the frozen canon, and that the Screen Specification Template is *"the first implementation-facing artifact"* the canon produces (ADR §6).

**The transition occurs at the moment all six Screen Specifications exist and each independently passes its own §13 Validation Checklist**, with the Navigation Contract carrying zero remaining "cannot be fully specified" caveats (Navigation Contract §1).

Before that point, any data schema, API contract, or technology choice would be implementation invented ahead of a specification that hasn't stopped to demand it — exactly what the Template's own citation discipline forbids. After that point, those same activities are correct and expected: they're Engineering's own artifacts, built downstream of and citing the Specifications, no longer part of the frozen canon. Design's visual work begins at the same point, for the same reason (Review Guide §2) — both tracks start from the same completed baseline, in parallel with each other, not with Engineering waiting on Design or vice versa.

---

## E. MVP Implementation Readiness

MVP scope is not being redefined here — it's already fixed by the Feature Inventory's Core V1 classification (Feature Inventory §5). Reading that classification against the screen-level work above gives a materially smaller bar than "all six Specifications done":

**Core V1 Experiences:** Beer/SKU Identification, Beer Detail, Price Verification, Full Recommendation (Feature Inventory §5).
**Screens that serve them:** Home, Search/Browse Results, Beer Detail, Recommendation, Price Verification — five screens, not six.

**Comparison is Important-Soon-After, not Core** (Feature Inventory §5), and Feature Inventory §3 is explicit that the *Experience* (the standalone screen) can be deferred independently of its underlying *Engine Behavior* (Trade-off/Tie-handling), which stays Core because it's used inside Recommendation. This means:

- **The Comparison Specification (2.6) is not required for MVP.**
- **Decision 1.5 (3+ candidate logic) is still required for MVP** — not because Comparison needs it, but because the Resolution Report's M3 finding showed this exact logic is reachable from Recommendation's own Core V1 threshold rule (Recommendation Screen Contract §6) the moment three close candidates remain on a Soft Preference, independent of whether the Comparison screen ships at all.

**MVP Implementation Readiness is reached when, and only when:**
1. Phase 0 (all five Resolution Report edits) is closed.
2. Decisions 1.1, 1.2, 1.3, 1.4, and 1.5 are recorded as new ADR entries — including 1.5, even though the Comparison *screen* is deferred.
3. The Navigation Contract's SBR-dependent edges (1.6) are closed.
4. Five Screen Specifications — Home, Search/Browse Results, Beer Detail, Recommendation, Price Verification — exist and each passes its own §13 Validation Checklist.
5. The Comparison Screen Contract's §11 gap remains explicitly logged as deferred-not-resolved in the ADR, exactly as the canon's own precedent already treats every other intentionally-deferred item — not silently dropped.

Comparison's Specification (2.6) becomes the first item of work in the Important-Soon-After phase that follows MVP, not a precondition for it.

---

## F. Consumers by Phase

| Phase | Primary owner | Consumed by |
|---|---|---|
| 0 — Resolution Report closure | PM / architecture maintainer | Everyone downstream; nothing else can start first |
| 1 — Gap decisions (1.1–1.6) | PM + relevant stakeholders, recorded in ADR §3 | Whoever writes the affected Screen Specification next |
| 2 — Screen Specifications | PM, against the Template (18) | Engineering (build reference), Design (behavior reference for wireframes), QA (§6–§8 as literal test-case source) |
| Post-MVP | PM | Comparison Specification (2.6), Accessibility standard, Telemetry framework — each opened as its own future decision when ready, not before |

---

## Validation

✓ Every item in Section A traces to a specific canonical section already naming it as unfinished — nothing here was invented.
✓ No product behavior is introduced; this document sequences existing gaps and existing (but unwritten) deliverables only.
✓ The MVP boundary in Section E is drawn from Feature Inventory §5's existing Core/Important classification, not a new judgment call.
✓ The transition point in Section D is drawn directly from the ADR's own stated boundary ("no code... has been decided" / "the first implementation-facing artifact"), not asserted independently.
