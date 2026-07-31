# ValueBrew — Engineering Screen Specification: HOME

**Document type:** Engineering Screen Specification (not a Screen Contract).
**Implements:** Home Screen Contract (11), in full.
**Built under:** the Canonical Screen Specification Template's (18) citation discipline — every field is filled by citation or explicitly marked unspecified; nothing is invented at this layer.
**Consumers:** UI/UX design (wireframe production), Flutter engineering (build reference), QA engineering (verification reference).
**Version:** 1.0 — first instantiation of the Template against this screen.
**Status:** Draft, pending engineering review.

---

## 1. Screen Purpose

Home captures an initial, unresolved intent and routes it toward the correct downstream Experience, without performing any of the reasoning that intent leads to.

*Citation: Home Screen Contract (11), §1 — "capture an initial, unresolved intent and route it toward the correct Experience, without resolving any Experience-level reasoning itself."*

---

## 2. User Goals

A person arrives at Home holding one of the intents already named in the User Interaction Model's Intent Map, undisambiguated. Home does not need to know which one in advance:

- "I haven't chosen a beer yet."
- "I'm holding a beer" / "I already have one in mind."
- "I want to compare beers."
- "I want to verify a price."
- "I'm planning before going shopping."
- "I want recommendations within a budget."
- "I'm buying this for someone else."

*Citation: User Interaction Model (06), §1; Home Screen Contract (11), §1 — "Primary user intent: any of the seven from the User Interaction Model's Intent Map, not yet disambiguated."*

**A precision worth stating for engineering:** these seven intents resolve to exactly three routing destinations, not seven. "I'm planning" and "I'm buying for someone else" both resolve into Recommendation as flagged variants; "I want to compare beers" resolves into Search/Browse Results, per the approved clarification below. See Section 4.

---

## 3. Entry Conditions

Home is the sole entry point into the product as a whole — there is no other first screen.

*Citation: Navigation Contract (16), §4 — "Entry into the product as a whole is always Home, per the Information Architecture — there is no other first screen."*

Two distinct arrival conditions apply:

| Condition | Known state on arrival |
|---|---|
| **Fresh entry** (opening the product, or an explicit restart following a genuinely new intent) | Nothing is known. No Preference Summary, no Decision Status beyond its initial value. |
| **Recovery bounce-back** (a failed identification attempt on Search/Browse Results) | Any Preference Summary already established before the failed attempt is known and must be carried forward. |

*Citation: Home Screen Contract (11), §3 ("Known Information: none, by default... Exception: on a recovery bounce-back, any Preference Summary already established before the failed attempt is known and carried") and §8 (Initial state entry conditions).*

**Home is never entered as a backward-navigation destination** from Beer Detail, Recommendation, Price Verification, or Comparison, under any condition.

*Citation: Home Screen Contract (11), §2 MUST NEVER; Navigation Contract (16), §9 and §10.*

---

## 4. Exit Conditions

Home routes to exactly one of three screens, based on the intent expressed:

| Expressed intent | Destination |
|---|---|
| A query or browse selection, **including a query naming two or more specific beers at once** | Search/Browse Results |
| A budget, preference, or general no-anchor intent — including Planning or Proxy-Buying, flagged as a variant of this same transition | Recommendation |
| An explicit verification intent | Price Verification |

*Citation: Home Screen Contract (11), §4 (Outputs — Transition) and §7 (Interaction Contract).*

**On the comparison-intent routing clarification (Resolution Report, Finding C1, approved):** a person expressing a wish to compare named beers is not a fourth destination. It is classified under the same trigger that governs any search or browse action, resolving through Search/Browse Results' own multi-select mechanism into Comparison. This is not new behavior — it assembles three already-existing, independently-cited rules (Home's own broad "a query... is expressed" trigger; Information Architecture's "select multiple to enter Comparison directly"; Feature Inventory's naming of "Search results" as a Beer Comparison entry point) into one stated path.

*Citation: Search/Browse Results Screen Contract, §2 MUST ("Treat a query naming two or more specific beers at once as a valid, ordinary basis for presenting multiple candidates eligible for that same multi-select path into Comparison"); Information Architecture (08), §2; Feature Inventory (07), §4.*

**Home never itself reaches Decision Complete.** It is exclusively a routing screen.

*Citation: Content Architecture (10), §3 ("this composition is transient by nature and never itself reaches Decision Complete"); Navigation Contract (16), §5.*

---

## 5. Information Hierarchy

Home carries no catalog content and none of the sixteen canonical Information Objects defined in Content Architecture apply to it. Its entire content surface reduces to two layers:

1. **Primary (always present in the Initial state):** the intent-capture invitation itself — procedural, not one of the fact-derived Information Objects every other screen displays.
2. **Recovery (conditionally present):** Recovery Information — either a "no beer identified" bounce-back, an Out-of-Scope boundary statement, or a single Clarifying Question — never more than one of these three at a time.

Nothing else may appear. No Beer Identity, Legal Price, Recommendation, or Confidence content is ever legitimate on this screen.

*Citation: Home Screen Contract (11), §5 ("none of the sixteen canonical Information Objects apply here... Home's 'primary information' is the intent-capture invitation itself, which is procedural") and §2 MUST NEVER ("Display Beer Identity, Legal Price, or any other catalog-specific content").*

---

## 6. Screen Sections

Three functional sections, defined by behavior, not layout:

**A. Intent Capture** — always present in the Initial and Routing states. Captures which of the three destinations (or the search-based comparison path) applies.

**B. Recovery / Boundary Messaging** — conditionally present. Displays exactly one of: a "no beer identified" recovery message, an Out-of-Scope boundary statement restating the four supported capabilities, or nothing (if neither condition is active).

**C. Clarifying Question** — conditionally present, and mutually exclusive with Section B's Out-of-Scope state. Displays exactly one question, never a sequence.

*Citation: Home Screen Contract (11), §8 (State Machine — Initial, Routing, Clarifying, Out-of-Scope, Recovering) and §11 (Failure Conditions).*

**How these sections are visually arranged, and whether they share a layout or separate views, is a design decision. Intentionally left unspecified by the Canonical Architecture.**

---

## 7. Every UI Element

Each element below is functional, not visual — purpose, data, and visibility are canonical; exact form (button, field, chip, or otherwise) is a design decision unless stated otherwise.

| Element | Purpose | Required Data | Optional Data | Visibility Rule |
|---|---|---|---|---|
| **General Intent Expression Mechanism** | Capture an unresolved intent, mapping to one of the three destinations or the comparison-via-search path | None | None | Always visible in Initial and Recovering states |
| **Capability Framing** (MAY) | Help a person recognize which supported path applies to what they want | The three destination concepts, in canonical terms | — | Optional; presence and form left to design, per Home §2 MAY |
| **"No Beer Identified" Recovery Message** | Communicate a failed identification bounce-back from Search/Browse Results | Recovery Information object | — | Visible only in Recovering state |
| **Out-of-Scope Boundary Message** | State plainly that the expressed intent is unsupported, and restate the four supported capabilities verbatim | The four canonical capability names: identify a beer, recommend a beer, verify a price, compare beers | — | Visible only in Out-of-Scope state |
| **Clarifying Question Prompt** | Resolve an ambiguous-but-plausibly-supported intent with exactly one further question | The question content (not canonically specified — depends on what was ambiguous) | — | Visible only in Clarifying state; never a second instance in the same cycle |
| **Clarifying Question Response Mechanism** | Capture the answer to the Clarifying Question Prompt | None | None | Visible only alongside the Clarifying Question Prompt |

*Citation: Home Screen Contract (11), §2, §3, §5, §7, §11.*

**No element beyond these six is permitted.** Adding an element not traceable to the list above would require revisiting Home's own Screen Contract first, not inventing it at this layer.

---

## 8. User Interactions

| Interaction type | Applies to Home? | Detail |
|---|---|---|
| **Tap** | Yes, functionally | Selecting a recognized path, submitting an expressed intent, or answering the Clarifying Question — the underlying action is canonical; whether it's realized as a tap, a selection, or another gesture is a design/implementation decision. |
| **Long press** | Not applicable | No canonical behavior on this screen requires a long-press interaction. |
| **Text input** | Possibly, mechanism unspecified | The canon defines *what* must be capturable (an intent, mapping to one of three destinations) but never *how* — free text, structured selection, voice, or another modality. **Intentionally left unspecified by the Canonical Architecture.** Mechanisms (Search, Browse, and by extension how an intent is typed or selected) are explicitly treated as implementation-layer choices, never canonically mandated. |
| **Scrolling** | Layout-dependent | Whether Home's content requires scrolling depends on visual layout, which is out of scope for this specification. |
| **Gestures** (swipe, etc.) | None defined | No canonical behavior on this screen involves any gesture beyond the functional "express an intent" and "answer a question" actions already named. |

*Citation: Feature Inventory (07), §1 ("Mechanism — an implementation-level method for satisfying a capability... never canonically mandated or excluded"); Review Guide (00), §2 (visual design, layout, and components explicitly out of scope for the canon).*

---

## 9. States

Mapped directly and exhaustively onto Home Screen Contract §8's own State Machine. No new state is introduced at this layer.

| Requested category | Canonical mapping | Notes |
|---|---|---|
| **Initial** | **Initial** | First arrival — opening the product, or a genuinely new intent following an explicit restart. All three recognized intent paths available with no precondition. |
| **Loading** | **No canonical state named "Loading."** The transitional moment between an intent-expressing action and a completed hand-off is covered by the **Routing** state itself. No new state is introduced here, per the Template's own rule against inventing states at this layer. |
| **Empty** | **Not applicable to Home.** Home has no content list to be empty — that condition belongs to Search/Browse Results. The nearest canonical equivalent on this screen is **Out-of-Scope**, mapped below. |
| **Recovering** | **Recovering** | Entry: a "no beer identified" condition returned from a failed Search/Browse Results attempt. Preserves any established Preference Summary. |
| **Error** | **No generic "system error" state is defined anywhere in the canon for this screen.** Home's own Failure Conditions cover only "no matching candidates," "Intent Outside Product Scope," and "Ambiguous Intent" — never a technical/system-level failure (network loss, service unavailability). **Intentionally left unspecified by the Canonical Architecture.** |
| **Unavailable** | **Same as Error, above. Intentionally left unspecified.** |
| **Clarifying** *(not requested by name, included for completeness)* | **Clarifying** | Entry: an ambiguous, potentially-supported intent has been expressed. Exit: the single permitted clarifying question is answered. |
| **Out-of-Scope** *(not requested by name, included for completeness)* | **Out-of-Scope** | Entry: an intent has been confirmed, directly or after clarification, to fall outside ValueBrew's supported capabilities. |
| **Completed (if applicable)** | **Not applicable — by design, not by omission.** Home never reaches Decision Complete. This is a deliberate architectural property, not a gap to be filled. |

*Citation: Home Screen Contract (11), §8, in full; Content Architecture (10), §3; Canonical Screen Specification Template (18), §7 ("No new states are permitted at this layer").*

---

## 10. Validation Rules

- Exactly one clarifying question may be posed per ambiguous-intent cycle. A second clarifying question is forbidden under any condition.
- An intent confirmed out of scope must never be silently forced into one of the three recognized paths.
- Any Preference Summary established before a recovery bounce-back must remain intact and available to whichever path is chosen next.
- No path may be gated behind login or an account.
- Nothing about Home's state may persist across separate sessions.
- A comparison-intent expression (naming two or more beers) must resolve through the same path as any other search or browse action — it must never be treated as unsupported, and it must never be routed as if it were a Recommendation or Price Verification intent.

*Citation: Home Screen Contract (11), §2, §6, §10, §11, §12.*

**How an expressed intent is technically classified** — as matching Search/Browse, Recommendation, Verification, ambiguous, or out-of-scope — **is not specified anywhere in the canon.** The canon defines the required outcome for each classification; the classification mechanism itself is implementation logic. **Intentionally left unspecified by the Canonical Architecture.**

---

## 11. Accessibility Considerations

**Intentionally left unspecified by the Canonical Architecture.** The Canonical Screen Specification Template reserves this section as a placeholder pending a future, dedicated accessibility standard not yet established anywhere in the canon, so that accessibility requirements are introduced consistently across all screens at once rather than invented ad hoc, one specification at a time.

*Citation: Canonical Screen Specification Template (18), §11; Architecture Review Guide (00), §9 ("a future accessibility standard" listed among deferred, not open, items).*

The one constraint this specification can state with canonical authority, because it follows directly from Section 7 above rather than inventing a new standard: **no element may be introduced for accessibility purposes that isn't already named in Section 7.** Making the six named elements operable and legible via platform-standard conventions is expected engineering practice; expanding the screen's functional surface to do so is not permitted without revisiting the Screen Contract first.

---

## 12. Copy Requirements

Exact wording is a design/content deliverable, not specified by the canon. What follows are the requirements that wording must satisfy — not the wording itself.

- **The Out-of-Scope boundary message must restate all four supported capabilities verbatim, in canonical terms, never a subset:** identify a beer, recommend a beer, verify a price, compare beers.
- **No forbidden synonym may be used anywhere on this screen.** Per the Canonical Interaction Lexicon: never "Suggest" in place of "Recommend"; never "Best" unqualified; never "Score" or "Rating"; never "Match" or "Fit" standing in for an outcome; never "Verify" outside Price Verification's own scope; never "Confirm" without "-as-Is" when referring to that specific Feature; never "Personalize/Personalization" used loosely; never "Correct price" in place of "Legal Price"; never "Alternative" as an unqualified catch-all.
- **No catalog-specific content may appear in any copy on this screen** — no beer names, prices, or other catalog facts, since nothing has been identified at this point.
- **The Clarifying Question's exact wording is not canonically specified** — it depends on the specific ambiguity detected, which is itself implementation logic. Intentionally left unspecified by the Canonical Architecture.

*Citation: Home Screen Contract (11), §11, §12; Canonical Interaction Lexicon (17), §5 (Forbidden Synonyms).*

---

## 13. Edge Cases

**An intent that remains ambiguous even after the single permitted clarifying question.** Resolution is canonical, not inferred: treat as Intent Outside Product Scope, never a second question.
*Citation: Home Screen Contract (11), §7, §8.*

**A comparison intent naming only one beer.** This is not a comparison intent at all under the canon's own terms — it is an ordinary search, resolving to Search/Browse Results and, on a single match, to Beer Detail. No special handling is required beyond the existing search/browse path.
*Citation: Search/Browse Results Screen Contract, §6 (Selection Resolution Rule).*

**A person attempting to navigate backward to Home from any of the four destination screens** (via a platform-level back action, for instance). The behavioral rule — Home is never a legitimate backward-navigation destination — is canonical. **How a platform-level back gesture is intercepted or redirected to honor this rule is an implementation decision. Intentionally left unspecified by the Canonical Architecture.**
*Citation: Home Screen Contract (11), §2 MUST NEVER; Navigation Contract (16), §9, §10.*

**Two simultaneously-plausible intents expressed in a single statement** (for example, a single utterance that could be read as both a recommendation request and a verification request). **No canonical rule resolves this case. Intentionally left unspecified by the Canonical Architecture.**

**Arrival at Home mid-Recovering with a subsequently expressed intent unrelated to the original search.** The Preference Summary established before the bounce-back is preserved regardless of which new path is chosen — this is explicitly covered, not an edge case requiring new interpretation.
*Citation: Home Screen Contract (11), §7 ("Recovering" interaction; §6, "Recovery preserves progress").*

---

## 14. Analytics Events

**Intentionally left unspecified by the Canonical Architecture at the schema level.** The Canonical Screen Specification Template reserves telemetry as a placeholder pending a dedicated analytics framework not yet established anywhere in the canon. No event names, properties, or tooling are canonically defined.

*Citation: Canonical Screen Specification Template (18), §12; Architecture Review Guide (00), §9.*

What the Template does permit at this layer is naming which already-defined User Actions are *plausible future telemetry candidates*, without defining their schema. Listed here on that basis only:

- Screen viewed (Home reached, Initial state entered)
- Search/browse intent expressed
- Recommendation intent expressed (including Planning or Proxy-Buying variant flagged)
- Verification intent expressed
- Comparison-shaped query expressed (routed via the search/browse path)
- Clarifying Question presented
- Clarifying Question answered
- Out-of-Scope boundary shown
- Recovery bounce-back received
- Routing transition completed, by destination

*Citation: Canonical Screen Specification Template (18), §12 ("This section may note which of the User Actions listed in Section 6 are plausible future telemetry candidates, without naming actual event schemas, properties, or analytics tooling").*

---

## 15. Non-functional Requirements

**Intentionally left unspecified by the Canonical Architecture.** Responsiveness targets, performance budgets, offline behavior, and platform expectations are never addressed anywhere in the twenty-document canon — implementation, codebase, and infrastructure decisions are explicitly out of scope for the entire architecture.

*Citation: Architecture Review Guide (00), §2 ("Explicitly out of scope for this review: ...any specific implementation, codebase, or technology stack... database or infrastructure design"); ADR (19), §7 ("No implementation guidance exists yet").*

The one grounded, citable fact this specification can state: **Home references no catalog data and requires nothing from the Beer Knowledge Base to render.** Whether this implies a specific offline capability is not addressed by the canon and is not asserted here.

*Citation: Home Screen Contract (11), §3 ("Referenced Information: none. Home references no catalog data, since nothing has been identified").*

---

## 16. Acceptance Criteria

Restated directly from Home Screen Contract §12, with one addition reflecting the Search/Browse Results integration:

✓ From the Initial state, all three recognized intent paths are available with no precondition.
✓ No catalog-specific content ever appears on Home.
✓ Home never receives a backward navigation from Beer Detail, Recommendation, Price Verification, or Comparison.
✓ Every transition out of Home traces to an explicit, person-initiated action.
✓ A "no beer identified" recovery preserves any Preference Summary established before the failed attempt.
✓ No transition from Home leads anywhere other than Search/Browse Results, Recommendation, or Price Verification.
✓ Nothing about Home's state persists across separate sessions.
✓ Home never presents a progressive preference question of its own.
✓ An intent clearly outside ValueBrew's domain always receives a boundary explanation and a full, verbatim restatement of the four supported capabilities.
✓ An ambiguous intent receives exactly one clarifying question — never zero, never more than one.
✓ A pivot from an Out-of-Scope or Clarifying response to a supported intent preserves any Preference Summary already established.
✓ **A query naming two or more beers is accepted as an ordinary basis for entering Search/Browse Results, never rejected as unsupported and never routed as a Recommendation or Verification intent.**

*Citation: Home Screen Contract (11), §12; Search/Browse Results Screen Contract, §12.*

---

## 17. Traceability Matrix

| Specification Section | Canonical Source(s) |
|---|---|
| 1. Screen Purpose | Home Screen Contract §1 |
| 2. User Goals | User Interaction Model §1; Home Screen Contract §1 |
| 3. Entry Conditions | Navigation Contract §4; Home Screen Contract §3, §8 |
| 4. Exit Conditions | Home Screen Contract §4, §7; Search/Browse Results Screen Contract §2; Information Architecture §2; Feature Inventory §4; Content Architecture §3; Navigation Contract §5 |
| 5. Information Hierarchy | Home Screen Contract §5; Content Architecture §2, §3 |
| 6. Screen Sections | Home Screen Contract §8, §11 |
| 7. Every UI Element | Home Screen Contract §2, §3, §5, §7, §11 |
| 8. User Interactions | Feature Inventory §1; Review Guide §2 |
| 9. States | Home Screen Contract §8; Content Architecture §3; Screen Specification Template §7 |
| 10. Validation Rules | Home Screen Contract §2, §6, §10, §11, §12 |
| 11. Accessibility Considerations | Screen Specification Template §11; Review Guide §9 |
| 12. Copy Requirements | Home Screen Contract §11, §12; Canonical Interaction Lexicon §5 |
| 13. Edge Cases | Home Screen Contract §2, §7, §8; Search/Browse Results Screen Contract §6; Navigation Contract §9, §10 |
| 14. Analytics Events | Screen Specification Template §12 |
| 15. Non-functional Requirements | Review Guide §2; ADR §7; Home Screen Contract §3 |
| 16. Acceptance Criteria | Home Screen Contract §12; Search/Browse Results Screen Contract §12 |

---

## Document Notes

This specification introduces no product behavior beyond what Home Screen Contract (11) and Search/Browse Results Screen Contract already establish. Every item marked "Intentionally left unspecified by the Canonical Architecture" is a genuine boundary the canon itself draws — most explicitly, between behavior (in scope for the twenty-document canon) and implementation, UI mechanism, accessibility standard, and telemetry schema (all explicitly deferred or out of scope per the Architecture Review Guide and the Screen Specification Template).
