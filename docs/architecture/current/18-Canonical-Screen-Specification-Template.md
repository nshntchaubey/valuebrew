# ValueBrew — Canonical Screen Specification Template
### The master template every future screen specification is written into. This document is the template itself — it contains no instantiated content for any real screen. Every future specification is produced by copying this structure and filling each field by direct citation to an already-frozen canonical document, never by invention.

---

## How to Use This Template

A screen specification is not a design document — it is the point where a frozen Screen Contract gets restated in a form an implementer can build directly from, with every field traceable back to something already decided. Filling in a field means citing the exact section of the exact canonical document that already established it. If a field cannot be filled by citation alone, the specification stops there and the gap is raised against the Screen Contract or Navigation Contract — it is never filled by invention at the specification layer. This template introduces no new authority of its own; it only organizes what the canon already contains into a form suited to implementation.

---

## 1. Screen Metadata

| Field | Instruction |
|---|---|
| Screen Name | Must exactly match the name used in the Canonical Interaction Lexicon and the corresponding Screen Contract — no informal variant. |
| Module | Copied verbatim from the Feature Inventory's Module taxonomy. Never inferred or renamed. |
| Experience | Copied verbatim from the Feature Inventory's Experience taxonomy. |
| Screen Contract Reference | A direct citation to the specific frozen Screen Contract this specification implements, including which section(s) each part of this document draws from. |
| Navigation Contract Reference | A direct citation to the specific Transition Contract entries in the Navigation Contract that involve this screen. |
| Version | The version number of this specification document itself — distinct from the version of the canon it implements. |
| Status | Draft / In Review / Approved / Deprecated — a lifecycle marker for this specification document, not a statement about the screen's product status. |

---

## 2. Purpose

*One paragraph only.*

Template sentence structure: "[Screen Name] exists to [restate the Purpose stated verbatim, or as a direct non-expansive paraphrase, from that screen's own Screen Contract, Section 1]. This specification implements that purpose as already defined; it introduces no new purpose and redefines none of the reasoning behind it."

This paragraph must never add a justification, a nuance, or a scope note the Screen Contract doesn't already contain. If the Purpose as written in the Screen Contract seems insufficient for implementation planning, that is a signal to revisit the Screen Contract itself, not to expand on it here.

---

## 3. Responsibilities

**Owns** — restated directly from the screen's own Screen Contract, Section 2 (the MUST list) and Section 1 (Canonical Role). List only what that document already establishes as owned.

**Does Not Own** — restated directly from the screen's own Screen Contract, Sections 2 (MUST NEVER) and 10 (Constraints).

**Delegates To** — the specific other screens this screen hands off to, each one citing the exact Transition Contract entry in the Navigation Contract that governs that hand-off, including its trigger and required context.

No item may appear in any of these three lists without a direct citation. A responsibility with no citation does not belong in the specification.

---

## 4. Required Context

Everything the screen requires before rendering, drawn directly from its own Screen Contract, Section 3 (Inputs).

| Category | Instruction |
|---|---|
| Required | Known Information listed as a precondition in the Screen Contract. Rendering cannot proceed without it. |
| Optional | Referenced Information the screen may draw on but doesn't strictly require to function. |
| Derived | Computed Facts or Platform-Service-sourced content, per the Beer Knowledge Model's classification — never independently entered, always calculated from Required or Optional context. |
| Transient | Context scoped to a single interaction only, per the Beer Knowledge Model's lifetime classification for the relevant Information Objects. |
| Persistent | Context surviving beyond a single interaction. **This category should be empty in nearly every specification.** Populating it requires first confirming against the Product Definition Document's rejection of accounts and persistent preference storage — a specification cannot introduce persistence on its own authority. |

---

## 5. Screen Composition

For every section of displayed content, drawn directly from the Content Architecture's composition entry for this screen:

| Field | Instruction |
|---|---|
| Information Source | The specific Information Object from the Content Architecture this content represents. |
| Owner | The Module or screen that owns this information, per the Information Architecture's ownership rules — cited exactly, never re-derived. |
| Required / Optional | Whether this content must always be present or may be gracefully omitted, per the owning Screen Contract's own MUST/MAY distinctions. |
| Visibility Rules | When this content appears or is withheld, citing the Content Architecture's Progressive Disclosure section. |
| Confidence Rules | Which confidence tier — Verified Fact, Computed Fact, or Human Judgment — this content carries, per the Beer Knowledge Model, and how Confidence Communication applies to it per the Recommendation Framework. |
| Recovery Rules | What replaces or supplements this content when a Failure Condition from the screen's own Section 11 is active. |

Repeat this table once per distinct information section the Content Architecture assigns to this screen. No section may be added that isn't already named there.

---

## 6. User Actions

For every action, drawn directly from the screen's own Screen Contract, Section 7 (Interaction Contract):

| Field | Instruction |
|---|---|
| Trigger | Restated exactly from the Interaction Contract entry for this action. |
| Preconditions | Restated exactly from the same entry. |
| System Response | Restated exactly, with no elaboration beyond what the Screen Contract already specifies. |
| State Changes | Cited against the screen's own State Machine, Section 8 — the specific state transition this action produces. |
| Navigation | Cited against the Navigation Contract's Transition Contract entry, if this action results in a screen change; otherwise marked "none — resolves within this screen." |
| Completion Impact | Whether this action moves Decision Status toward, into, or away from Completed, per the screen's own State Machine. |

Repeat once per action already enumerated in the Screen Contract. No action may be added that isn't already there.

---

## 7. State Mapping

A direct, exhaustive mapping of every visible condition the eventual interface will need to represent, onto the States already defined in this screen's own Screen Contract, Section 8.

**No new states are permitted at this layer.** If an implementer believes a additional visible condition is needed beyond what the State Machine already names, that is evidence the Screen Contract itself is incomplete — the correct action is to revisit that frozen document, not to add a state here. A purely visual treatment (for instance, how a transition between two already-named states is rendered) is not a new state and does not require an entry of its own in this section; only conditions with distinct behavioral meaning require mapping.

| UI-Visible Condition | Maps to Canonical State | Citation |
|---|---|---|
| [to be filled per screen] | [must be one of the States already named in that screen's Section 8] | [Screen Contract, Section 8] |

---

## 8. Error Mapping

Every visible error, mapped directly to the screen's own Screen Contract, Section 11 (Failure Conditions).

| Visible Error | Failure Condition (cited) | Recovery (cited) | Progress Preservation (cited) |
|---|---|---|---|
| [to be filled per screen] | [exact Failure Condition name from Section 11] | [exact Recovery behavior from the same entry] | [exact Progress Preservation statement from the same entry] |

No error may be represented here that doesn't already correspond to a named Failure Condition. An error state without a canonical citation is not yet specifiable — it must be raised against the Screen Contract first.

---

## 9. Content Rules

Every displayed element, mapped across four dimensions:

| Field | Instruction |
|---|---|
| Content Architecture | Which Information Object and which composition category (Primary, Supporting, Contextual, Progressive, Explanation, Confidence, Recovery, Completion) this element belongs to. |
| Lexicon | The exact canonical term, capitalized and phrased per the Canonical Interaction Lexicon's Naming Rules, that this element must use — no informal substitute, no forbidden synonym from the Lexicon's Section 5. |
| Confidence Communication | Whether and how this element must visibly distinguish certain from inferred content, per the Recommendation Framework. |
| Explanation | Whether this element requires an attached Explanation, and if so, which parent object it belongs to. |

---

## 10. Navigation

This section contains only citations to the Navigation Contract — never a restatement or reinterpretation of any transition's logic. List every Transition Contract entry from the Navigation Contract, Section 6, that involves this screen, either as origin or destination, with a one-line pointer to where its full definition lives. No new transition, precondition, or context-handling rule may be introduced here under any circumstance.

---

## 11. Accessibility Notes

*Placeholder only. No implementation guidance is defined at this layer.*

This section is reserved for a future, dedicated accessibility standard, not yet established anywhere in the canon. Every screen specification carries this placeholder unfilled until that standard exists, so that accessibility requirements are introduced consistently across all screens at once, rather than invented ad hoc, one specification at a time.

---

## 12. Telemetry Hooks

*Placeholder only. No events are defined at this layer.*

This section may note which of the User Actions listed in Section 6 are plausible future telemetry candidates, without naming actual event schemas, properties, or analytics tooling — all of which remain undefined until a dedicated analytics framework is established across the canon.

---

## 13. Validation Checklist

Every completed screen specification must be checked against this list before being considered final:

✓ No behavior stated here differs from what the corresponding Screen Contract already defines.
✓ No transition, precondition, or context rule differs from what the Navigation Contract already defines.
✓ Every item in Section 3 (Responsibilities) has exactly one owner, with no overlap or duplication against another screen's specification.
✓ Every term used matches the Canonical Interaction Lexicon exactly, with no forbidden synonym present.
✓ Every state in Section 7 and every error in Section 8 traces to an entry already named in the Screen Contract — nothing was added at this layer.
✓ Sections 11 and 12 remain placeholders, not filled with invented implementation detail.

---

## 14. Future Extensions

A screen specification may gain new fields over time — for instance, once Sections 11 or 12 are ready to be filled, following a dedicated accessibility or analytics standard established at the canonical layer first, never invented locally within one specification. Adding a field to this template itself requires the same rigor as any other canonical change: it must be justified, applied uniformly across every future specification, and never alter the meaning of an existing field. A specification's Version field increments whenever its content changes; any such change must be re-validated against Section 13 in full, not assumed to still pass. This template itself may only be revised by amending this document directly — no individual screen specification may silently diverge from it.
