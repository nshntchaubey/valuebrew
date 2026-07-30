# ValueBrew — Screen Contract: HOME
### The canonical, implementation-independent contract for the Home screen. Derived entirely from the ten frozen documents. Not UI, not wireframes, not a PRD. Written to verify future wireframes, not to produce them.

---

## 1. Screen Identity

**Screen Name:** Home.

**Purpose:** capture an initial, unresolved intent and route it toward the correct Experience, without resolving any Experience-level reasoning itself.

**Owning Module and Owning Experience — a deliberate exception, stated plainly rather than forced:** Home does not belong to a single owning Module or Experience. The Feature Inventory lists Home as an entry point for three distinct Experiences — Beer/SKU Identification, Full Recommendation, and Price Verification — spanning the Discovery, Recommendation, and Verification Modules. This is not an oversight or a violation of the Information Architecture's rule that every screen corresponds to one Experience; it is the documented, necessary exception that makes that rule possible for every other screen. Home exists structurally *before* Experience selection happens — every other screen already knows which Experience it belongs to, and Home is the one place where that hasn't been decided yet.

**Canonical Role:** the single, universal entry point into the product. Home captures an intent and hands it off; it never performs the reasoning that intent leads to.

**Why this screen exists independently:** every other screen requires something specific to already be known — Beer Detail requires an identified SKU, Recommendation requires at least a first preference input, Price Verification requires a SKU and a charged price, Comparison requires named candidates. Home is the only point in the product where none of that yet exists. Merging Home into any one destination screen would force a premature commitment to one Experience before the person has expressed which one they actually want — a direct violation of the Information Architecture's rule that navigation reflects intent, not architecture.

---

## 2. Screen Contract

**MUST:**
- Offer a path toward each of the three Experiences it serves as an entry point for, with no precondition, from its Initial state.
- Route to exactly one of Search/Browse Results, Recommendation, or Price Verification, based on the intent expressed.
- Present "no beer identified" Recovery Information if arriving as a bounce-back from a failed identification attempt.
- Preserve any Preference Summary already established before a bounce-back, and make it available to whichever path is chosen next.
- Detect when an expressed intent falls outside ValueBrew's supported capabilities, and respond by explaining the product's scope and inviting a pivot to a supported path, rather than forcing a match.
- Ask exactly one clarifying question when an intent is ambiguous but potentially maps to a supported capability, before resolving it either to a supported path or to an out-of-scope response.

**MAY:**
- Offer additional framing to help a person recognize which of the three paths applies to what they want.
- Serve as the destination when a person explicitly abandons an active flow to state a genuinely new, unrelated intent.

**MUST NEVER:**
- Perform Full Recommendation reasoning.
- Perform Price Verification computation.
- Perform Comparison reasoning.
- Display Beer Identity, Legal Price, or any other catalog-specific content — nothing has been identified at this point, so none of it can legitimately appear.
- Be the destination of a backward navigation from Beer Detail, Recommendation, Price Verification, or Comparison.
- Gate any of its three paths behind login or an account.
- Retain Preference Summary or Decision Status across separate sessions.
- Transition directly to Comparison or Beer Detail — both are reachable only via Search/Browse Results.

---

## 3. Inputs

**Known Information:** none, by default — Home is the one screen in the product where nothing is known yet. Exception: on a recovery bounce-back, any Preference Summary already established before the failed attempt is known and carried.

**Referenced Information:** none. Home references no catalog data, since nothing has been identified.

**Interaction State:** Decision Status at its initial, uninitialized value. On a bounce-back, Decision Status instead reflects "returned from a failed identification attempt, prior Preference Summary intact."

**Cross-cutting Behaviors:** none of Recommendation Explanation, Confidence Communication, or Learning ("Why") apply here — none has anything to attach to yet. Only Recovery applies, and only conditionally.

**Recovery State:** two distinct recovery states apply to Home. "No beer identified" arrives from elsewhere — a failed Beer/SKU Identification attempt on Search/Browse Results. "Intent outside product scope" and "ambiguous intent" originate at Home itself, the moment an expressed intent is detected as unsupported or unclear, rather than being received from a downstream failure.

---

## 4. Outputs

**Transition** — to Search/Browse Results, when a search or browse action is taken; to Recommendation, when a budget, preference, or general no-anchor intent is stated, including when Planning Mode or Proxy-Buying Mode is engaged as a flagged variant of the same transition; to Price Verification, when an explicit verification intent is stated. Occurs the moment an intent-expressing action is taken.

**Decision:** none. Home makes no decisions of its own.

**Recommendation:** none. Not Home's to produce.

**Recovery:** two distinct cases, not one. Home *receives and displays* the "no beer identified" recovery condition generated elsewhere, on Search/Browse Results. Home *originates* its own recovery response — restating product scope, or asking one clarifying question — the moment it detects an expressed intent that doesn't map to a supported capability. The earlier version of this contract stated Home never originates a recovery condition; that was incomplete, and is corrected here.

**State Change:** Decision Status moves from "uninitialized" to "intent expressed, routing" the moment a path is selected.

**Worth stating precisely, to avoid conflating this with a different canonical mechanism:** Home's intent-capture invitation is not a Progressive Question in the sense the Decision Engine Model defines — Progressive Question-Asking only begins once an Experience like Recommendation is already underway and gathering specific preference values. Home's invitation is a single, prior step: which Experience applies at all, not which value a known Experience should use.

---

## 5. Information Composition

Directly citing Content Architecture Section 3's Home entry, not redesigning it.

**Primary:** none of the sixteen canonical Information Objects apply here — Home's "primary information" is the intent-capture invitation itself, which is procedural, not one of the catalog- or reasoning-derived objects that populate every other screen.

**Supporting:** none.

**Contextual:** none, except on a recovery bounce-back, where the prior Preference Summary serves as contextual information carried forward.

**Progressive:** none. Home does not ask progressive preference questions itself.

**Recovery:** the Recovery Information object, present either when arriving as a bounce-back from a failed identification attempt, or when Home itself detects an out-of-scope or ambiguous intent.

**Explanation:** none. Nothing exists yet to explain.

**Confidence:** none. Nothing has been computed or inferred yet.

**Completion:** not applicable. Per Content Architecture's own explicit statement, Home never itself reaches Decision Complete.

---

## 6. Behavioral Rules

Recovery preserves progress: a "no beer identified" bounce-back keeps any established Preference Summary intact and available to whichever path is chosen next.

Home asks no preference or progressive questions of its own — its one implicit ask ("which of these three paths") is asked once, never repeated.

No screen requires understanding the Decision Engine to use it: Home's function is fully legible without knowledge of any downstream reasoning.

No automatic transitions: Home only moves forward on an explicit action, never on its own.

No persistent information across visits: consistent with the canon's rejection of accounts, nothing carries over between separate sessions.

An ambiguous intent is met with exactly one clarifying question, never a chain of them — this mirrors the Decision Engine Model's discipline against asking more than necessary, applied here to intent recognition rather than preference gathering.

An out-of-scope intent is always named as such, never silently forced into one of the three recognized paths.

---

## 7. Interaction Contract

**Initiate Search or Browse.** Trigger: a query or browse selection is expressed. Precondition: none — available in both Initial and Recovering states. System Response: transitions to Search/Browse Results, carrying forward the query or selection and any existing Preference Summary. Possible Outcomes: candidates are found, or none are. Recovery: "no beer identified," returning to Home's Recovering state. Completion: not applicable at Home — completion belongs to whichever downstream Experience is entered.

**State a Recommendation Intent.** Trigger: a budget, a preference, or a general no-anchor intent is expressed. Precondition: none. System Response: transitions to Recommendation, carrying forward whatever was stated as the first known input. Possible Outcomes: proceeds into Recommendation's own progressive gathering. Recovery: not applicable at Home — any recovery from insufficient information occurs within Recommendation itself. Completion: not applicable at Home.

**State a Verification Intent.** Trigger: a wish to check a specific charged price is expressed. Precondition: none. System Response: transitions to Price Verification. Possible Outcomes: proceeds into Price Verification's own flow, which gathers the SKU and charged price there, not here. Recovery: not applicable at Home. Completion: not applicable at Home.

**State a Planning or Proxy-Buying Intent.** Trigger: the decision is indicated to be for a future occasion, or on someone else's behalf. Precondition: none. System Response: transitions to Recommendation, with Planning Mode or Proxy-Buying Mode flagged from the outset — this is a variant of the Recommendation transition above, not a fourth distinct destination, since both modes are Features attached to Recommendation per the Feature Inventory, not separate Experiences. Possible Outcomes: proceeds into Recommendation's flow, carrying the mode flag. Recovery: not applicable at Home. Completion: not applicable at Home.

**Express an Unsupported or Ambiguous Intent.** Trigger: the expressed intent doesn't map to search/browse, a recommendation-style intent, or a verification intent. Precondition: none. System Response: if the intent is clearly outside ValueBrew's domain, Home states the boundary plainly, restates the four supported capabilities — identify a beer, recommend a beer, verify a price, compare beers — and invites a pivot; if the intent is ambiguous but potentially maps to one of these, Home asks exactly one clarifying question before resolving it. Possible Outcomes: the person pivots to a supported path and routes normally, or the intent is confirmed unsupported and the person remains at Home with the boundary restated. Recovery: any previously established Preference Summary is preserved and remains available if the person pivots to a supported intent. Completion: not applicable at Home.

**Precisely stated: Home supports four recognized intent expressions but only three actual transition destinations,** since the fourth (Planning/Proxy) is a flagged variant of the second (Recommendation), not an independent path. The out-of-scope and clarifying interactions above add no new destination either — they only ever resolve back into one of the same three, or end without a transition at all.

---

## 8. State Machine

**Initial.** Entry: first arrival — opening the product, or a genuinely new intent following an explicit restart. Exit: an intent-expressing action is taken. Permitted transitions: to Routing, to Clarifying, to Out-of-Scope. Forbidden: directly to any destination screen without an action; directly to Recovering, since that state only arrives via a real failed attempt on Search/Browse Results, never spontaneously from Initial.

**Routing.** Entry: an intent-expressing action has just been taken, and it maps clearly to a supported capability. Exit: successful hand-off to a destination screen. Permitted transitions: to exactly one of Search/Browse Results, Recommendation, or Price Verification. Forbidden: to Comparison or Beer Detail directly, in either case.

**Clarifying.** Entry: an ambiguous, potentially-supported intent has been expressed. Exit: the single permitted clarifying question is answered. Permitted transitions: to Routing, if the answer resolves to a supported path; to Out-of-Scope, if the answer confirms the intent isn't supported after all. Forbidden: asking a second clarifying question; returning to Initial without resolving the question first.

**Out-of-Scope.** Entry: an intent has been confirmed — directly, or after clarification — to fall outside ValueBrew's supported capabilities. Exit: the person pivots to one of the four stated supported paths, or the interaction ends here without a transition. Permitted transitions: to Routing, if a pivot is made. Forbidden: silently discarding any preserved Preference Summary; forcing the original unsupported intent into one of the three recognized paths instead of naming it as out of scope.

**Recovering.** Entry: a "no beer identified" condition returned from a failed Search/Browse Results attempt. Exit: a new search/browse attempt is made, or the person pivots to a different intent entirely. Permitted transitions: to Routing, to Recommendation, to Price Verification, carrying forward any preserved Preference Summary in every case. Forbidden: silently discarding that preserved Preference Summary — doing so would violate the recovery-preserves-progress rule.

**Not relevant to this screen, and worth stating why:** Waiting, Gathering, Evaluating, and Completed do not apply to Home. Gathering and Evaluating belong to Experiences already underway, which Home by definition is not. Completed does not apply because Home never reaches Decision Complete, per Content Architecture's explicit statement.

---

## 9. Dependencies

**Decision Engine Model** — indirectly. Home performs no Decision Engine reasoning itself, but its three routing destinations are the literal entry points into that document's own journeys.

**Beer Knowledge Model** — not directly. Home displays no catalog information at all.

**Recommendation Framework** — not directly. No recommendation reasoning occurs at Home.

**Information Architecture** — directly. Home's existence, its screen inventory entry, its exact possible exits, and its status as an entry-only, never-a-back-destination screen are all defined there.

**Experience Flows** — directly. Every one of the seven canonical flows begins at Home, and Home's Recovering state is drawn directly from the "no beer identified" recovery flow.

**Content Architecture** — directly. Home's composition in Section 5 above is a direct citation of that document's own Home entry.

**Feature Inventory** — directly. Home is listed there as an entry point for exactly three Experiences — the authoritative source for Home's three, and only three, routing destinations.

---

## 10. Constraints

Cannot perform Recommendation reasoning. Cannot perform Price Verification computation. Cannot perform Comparison reasoning. Cannot display Beer Identity, Legal Price, or any other catalog content. Cannot be a backward-navigation destination from any of the four destination screens. Cannot gate any path behind login or an account. Cannot retain Preference Summary or Decision Status across separate sessions. Cannot transition directly to Comparison or Beer Detail. Cannot ask more than one clarifying question before resolving an ambiguous intent to either a supported path or an out-of-scope response. Cannot force an unsupported intent into one of the three recognized paths — it must be named as out of scope, never silently misrouted.

---

## 11. Failure Conditions

**A search or browse attempt yields no matching candidates.** Detection: Search/Browse Results reports zero candidates. Recovery: return to Home's Recovering state with Recovery Information present. Progress Preservation: any established Preference Summary remains intact.

**Intent Outside Product Scope.** Detection: the expressed intent cannot be mapped to any supported ValueBrew capability, because it falls outside the product's defined domain entirely. Recovery: clearly communicate that the request is outside ValueBrew's scope, restate the four supported capabilities — identify a beer, recommend a beer, verify a price, compare beers — and invite a pivot to one of them. Progress Preservation: any previously established Preference Summary that remains relevant is preserved if the person pivots to a supported intent.

**Ambiguous Intent.** Detection: the expressed intent doesn't clearly map to a supported capability, but plausibly could with one further clarification. Recovery: ask exactly one clarifying question; route to a supported path if the answer resolves it, or treat it as Intent Outside Product Scope if it doesn't. Progress Preservation: the same as above.

**This resolves what an earlier version of this contract left as an open gap.** The distinction between the two failure conditions above — a clean boundary statement for genuinely unsupported intents, versus exactly one clarifying question for merely ambiguous ones — is a deliberate rule, not an assumption, and it closes the gap without expanding the product's scope or contradicting any other canonical document.

---

## 12. Acceptance Criteria

✓ From the Initial state, all three recognized intent paths are available with no precondition.
✓ No catalog-specific content ever appears on Home.
✓ Home never receives a backward navigation from Beer Detail, Recommendation, Price Verification, or Comparison.
✓ Every transition out of Home traces to an explicit, person-initiated action.
✓ A "no beer identified" recovery preserves any Preference Summary established before the failed attempt.
✓ No transition from Home leads anywhere other than Search/Browse Results, Recommendation, or Price Verification.
✓ Nothing about Home's state persists across separate sessions.
✓ Home never presents a Progressive question of its own — that behavior belongs exclusively to Recommendation, Comparison, and Price Verification.
✓ An intent clearly outside ValueBrew's domain always receives a boundary explanation and a restatement of the four supported capabilities, never a forced match to one of them.
✓ An ambiguous intent receives exactly one clarifying question — never zero, never more than one — before being routed or declared out of scope.
✓ A pivot from an out-of-scope or clarifying response to a supported intent preserves any Preference Summary already established.

---

## 13. Validation

✓ No Product Definition Document violated — no accounts, no new capability introduced.
✓ No Recommendation Framework violated — no recommendation reasoning performed here.
✓ No Information Architecture ownership violated — Home's ownership matches its IA Section 3 entry exactly.
✓ No Experience Flow violated — Home's role as the starting point for all seven flows matches Experience Flows Section 2.
✓ No Content Architecture violated — Home's composition matches that document's Section 3 entry exactly, including its explicit statement that Home never reaches Decision Complete.
✓ No new capability introduced — the three routing destinations are exactly the three named in the Information Architecture and Feature Inventory.
✓ No hidden assumptions introduced — one judgment call remains made visible rather than buried: that Planning/Proxy intents route to Recommendation as a flagged variant, directly derivable from the Feature Inventory's classification of both as Features, not separate Experiences. The "unrecognized intent" failure mode, originally flagged here as an open gap, has since been resolved by an explicit decision — an out-of-scope intent receives a boundary explanation, an ambiguous one receives exactly one clarifying question — and is now incorporated in Section 11 rather than left open.

---

## 14. Future Compatibility

**Natural future evolution:** additional recognized intent categories, if a new Experience is ever formally added to the Feature Inventory; richer recovery framing, if real usage surfaces failure modes beyond "no beer identified."

**Forbidden future evolution:** Home performing any Experience-level reasoning itself, which would collapse ownership boundaries the Information Architecture explicitly protects. Home becoming a backward-navigation destination, which the Navigation Model explicitly forbids. Home gaining persistent, cross-session content, which would violate the canon's rejection of accounts. Home directly launching Comparison or Beer Detail without passing through Search/Browse Results — this would require a change to the Information Architecture itself first, not a decision this screen's contract can make unilaterally.
