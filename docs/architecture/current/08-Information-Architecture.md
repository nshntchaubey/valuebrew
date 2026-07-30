# ValueBrew — Information Architecture
### The canonical IA. Derived entirely from the seven frozen documents. Not UI design, not wireframes, not a PRD. Answers one question: how is the product organized from the user's perspective?

---

## 1. Information Architecture Principles

1. Every screen corresponds to exactly one Experience, per the Feature Inventory's layer taxonomy. Features attach to their owning Experience's screen; they never receive independent screens of their own.

2. Users should never need to understand the Decision Engine, the Recommendation Framework, or any internal reasoning mechanism to use the product.

3. Explanations appear in the context of the answer they explain, never requiring separate navigation to reach.

4. Navigation reflects the User Intent Map, not the product's internal architecture — a person moves through the product by what they want, never by what module happens to own it.

5. A screen's content must structurally separate high-confidence facts from low-confidence inferences, never blend them undifferentiated.

6. Every journey terminates at a genuine Decision Complete state. No journey is structured to require further navigation once resolved.

7. No screen exists behind a login or account boundary, consistent with the Product Definition Document's explicit rejection of accounts.

8. Recommendations are presented as outcomes reached through an interaction, never as a destination someone browses to independent of their own inputs.

9. Every screen transition is traceable to a specific user action. No screen advances a person automatically.

10. Comparison and confirmation are architecturally distinct from open discovery — a person comparing named candidates is doing something structurally different from a person still deciding what they want, and the IA does not conflate them.

11. Screens loop backward as cleanly as they move forward, mirroring the User Interaction Model's requirement that refining a constraint returns to Narrowing rather than restarting.

12. No screen, section, or piece of content may exist without tracing back to a Module, Experience, or cross-cutting Feature already named in the Feature Inventory.

13. Mechanisms — search, browse, a future scan — are entry actions into a screen, never separate destinations with their own independent purpose.

14. Price Verification is always reachable without first passing through a full recommendation flow. These are architecturally independent entry points, not sequential steps.

15. Occasion and other lower-confidence, deferred inputs never occupy the same architectural prominence as budget and core preference inputs, mirroring their different MVP tiers in the Feature Inventory.

---

## 2. Screen Inventory

**Home**
Purpose: capture an initial, unresolved intent and route it toward the right Experience.
Primary user intent: any of the seven from the User Interaction Model's Intent Map, not yet disambiguated.
Primary content: a way to search, browse, or state a direct intent (verify a price, get a recommendation, plan ahead).
Primary actions: initiate a search or browse, or select a direct intent.
Possible exits: Search/Browse Results, Recommendation, Price Verification.

**Search/Browse Results**
Purpose: present candidate SKUs matching a query or browse selection, and let a person move to a specific one.
Primary user intent: "I want to find a specific beer" (recall or recognition, per the earlier evidence base).
Primary content: a lightweight list of matching candidates — identity only, not full detail.
Primary actions: select one candidate, or select multiple to enter Comparison directly.
Possible exits: Beer Detail, Comparison.

**Beer Detail**
Purpose: present everything known about one identified SKU.
Primary user intent: "I'm holding this / I already have one in mind" (I2), or arriving from a search result.
Primary content: identity, legal price, alcohol content, size, and computed value standing (once the Style Benchmark exists); the Confirm-as-Is Feature's output when a person arrived with an anchor already in mind.
Primary actions: request price verification for this specific SKU, request a comparison against another, accept the confirmation as-is.
Possible exits: Price Verification, Comparison, Decision Complete.

**Recommendation**
Purpose: collect necessary preference inputs progressively and present the synthesized recommendation.
Primary user intent: "I haven't chosen a beer yet" (I1), "within a budget" (I6), "planning ahead" (I5), or "buying for someone else" (I7) — the latter two engage the Planning Mode and Proxy-Buying Mode Features as modes of this same screen, not separate screens.
Primary content: progressively surfaced questions, then the Full Recommendation output with its explanation attached.
Primary actions: answer a question, accept the recommendation, ask "why," move into a comparison if a genuine trade-off or tie is surfaced.
Possible exits: Beer Detail, Comparison, Decision Complete.

**Price Verification**
Purpose: check a specific SKU and a specific charged price against the legal reference.
Primary user intent: "I want to verify a price" (I4).
Primary content: the verification delta — fair, or above the legal price, and by how much.
Primary actions: enter or confirm the charged price, view the result.
Possible exits: Beer Detail, Decision Complete.

**Comparison**
Purpose: present side-by-side reasoning across two or more named candidates.
Primary user intent: "I want to compare beers" (I3), or a trade-off/tie surfaced from Recommendation or Beer Detail.
Primary content: the Trade-off Explanation or Tie Disclosure across the named candidates.
Primary actions: select a winner, ask "why," adjust a constraint and return to Recommendation.
Possible exits: Beer Detail, Recommendation, Decision Complete.

**Deliberately not given their own screens, and worth stating explicitly rather than leaving implicit:** Planning Mode and Proxy-Buying Mode are Features attached to the Recommendation screen, per the Feature Inventory's own layer taxonomy — they are modes, not destinations. "Why"/Learning Query Handling and Recommendation Explanation are cross-cutting Features with no fixed screen of their own — they appear wherever their attached content appears. Decision Complete is not a screen at all; it is a state that Beer Detail, Recommendation, Price Verification, and Comparison can each independently reach.

---

## 3. Screen Responsibilities

**Home** owns: capturing initial intent and routing it. Does not own: any recommendation, verification, or comparison logic.

**Search/Browse Results** owns: presenting lightweight candidate identity and enabling selection. Does not own: full detail on any single SKU — that belongs to Beer Detail.

**Beer Detail** owns: the complete picture of one identified SKU, and the Confirm-as-Is outcome. Does not own: the verification delta computation itself (Price Verification's job, even though Beer Detail links into it), and does not own multi-candidate comparison logic (Comparison's job, even though Beer Detail can launch it).

**Recommendation** owns: preference input collection and the Full Recommendation synthesis, including its Planning and Proxy-Buying modes. Does not own: detailed single-SKU facts beyond what justifies the recommendation itself, and does not own charged-price verification.

**Price Verification** owns: the verification delta for one specific SKU and one specific charged price. Does not own: any broader recommendation or comparison logic — a person asking "is there something better" here is routed onward as a distinct next step, not answered inline.

**Comparison** owns: side-by-side reasoning across specific, already-identified candidates. Does not own: open-ended discovery — Comparison assumes candidates already exist, it does not generate them.

**Recommendation Explanation and Confidence Communication are deliberately not owned by any single screen.** They are cross-screen behaviors, covered in Section 6, and every screen above inherits them uniformly rather than implementing its own version. The rule they follow belongs to the Recommendation Framework; screens only ever apply it, never own it.

---

## 4. Navigation Model

**Destinations** — screens a person can rest on and reach Decision Complete from: Beer Detail, Recommendation, Price Verification, Comparison.

**Transient screens** — passed through, never rested on: Home (always routes onward), Search/Browse Results (always routes into Beer Detail or Comparison).

**Screens that launch other Experiences:** Home launches all four destinations. Beer Detail can launch Price Verification and Comparison. Recommendation can launch Comparison, when a genuine trade-off or tie is surfaced, and Beer Detail, when a person wants more context on the recommended SKU.

**Screens that terminate journeys:** any of the four destination screens, once each independently reaches its own Decision Complete state — there is no single, shared "end screen" the product funnels everyone through.

**Backward movement:** adjusting a constraint from Comparison returns to Recommendation, re-entering at the point where inputs are still being weighed, never restarting the interaction from Home. Backing out of Beer Detail returns to whichever screen led there — Search/Browse Results, Recommendation, or Comparison — never defaulting to Home regardless of origin.

---

## 5. Entry Points

**Opening the product.** Intent: unresolved. First screen: Home. Expected next: any of Search/Browse Results, Recommendation, or Price Verification, depending on what's chosen. Expected completion: any Decision Complete.

**Searching.** Intent: "I know roughly what I'm looking for" (I2/I4-adjacent). First screen: Home, with a query entered. Expected next: Search/Browse Results, then Beer Detail. Expected completion: Decision Complete via Beer Detail, or via Price Verification if launched from there.

**Browsing.** Intent: "I don't have an anchor" (I1/I3-adjacent). First screen: Home. Expected next: Search/Browse Results, then Beer Detail or directly into Comparison if multiple candidates are selected. Expected completion: Decision Complete via Beer Detail or Comparison.

**Planning.** Intent: I5. First screen: Home, with the planning intent selected. Expected next: Recommendation, with Planning Mode engaged from the start. Expected completion: Decision Complete, explicitly carrying the standing lower-confidence caveat throughout.

**Price verification.** Intent: I4. First screen: Home, with verification intent selected, or Price Verification directly if arriving via Beer Detail. Expected next: the verification delta result. Expected completion: Decision Complete.

**Recommendation.** Intent: I1/I6. First screen: Home, with recommendation intent selected, or Recommendation directly. Expected next: progressive questions, then the recommendation itself. Expected completion: Decision Complete, possibly via an intermediate Beer Detail or Comparison stop.

**Comparison.** Intent: I3, naming specific candidates. First screen: Home → Search/Browse Results, selecting multiple candidates. Expected next: Comparison directly. Expected completion: Decision Complete.

---

## 6. Cross-Screen Behaviors

**Recommendation Explanation** appears wherever a Recommendation, Verification, or Comparison result is shown, in-context, immediately alongside the answer — never requiring separate navigation to reach.

**Confidence Communication** applies to every screen presenting computed or inferred content: high-confidence facts and low-confidence inferences remain structurally separated everywhere they appear, with no screen-specific exceptions.

**Decision Complete** behaves identically regardless of which screen reaches it — Beer Detail, Recommendation, Price Verification, and Comparison all terminate the same way: nothing further is required, and nothing is artificially extended to keep the person engaged.

**Learning ("Why?")** is available as an in-context expansion wherever Recommendation Explanation appears. It never has a screen of its own, and it is never presented as if it were a new recommendation request.

---

## 7. Information Ownership

**Beer identity** — sourced from the Beer Knowledge Base; Beer Detail is the canonical screen home for the full picture; Search/Browse Results shows an abbreviated reference, not a duplicate.

**Legal price** — same source; Beer Detail is the canonical display home; Price Verification references it rather than re-hosting it.

**Observed/charged price** — owned exclusively and transiently by the Price Verification screen. It is never persisted or shown on Beer Detail, consistent with the Beer Knowledge Model's classification of this as transaction-level, not catalog, knowledge.

**Alcohol-adjusted value** — Beer Detail is the canonical home for a single SKU's figure; Comparison and Recommendation reference it without re-hosting its computation.

**Recommendation output** — owned exclusively by the Recommendation screen; if a person drills into the recommended SKU via Beer Detail, that's a reference to the same information, not a second copy of it.

**Comparison result** — owned exclusively by the Comparison screen.

**Explanation and confidence indicators** — owned by no fixed screen; contextually attached wherever the content they explain appears, per Section 6.

**Budget and preference inputs** — owned by the Recommendation screen for the duration of one interaction only. Per the Beer Knowledge Model and the Product Definition Document's rejection of accounts, there is no persistent home for these across sessions — they exist only within the active interaction that collected them.

---

## 8. IA Validation

**Every Feature belongs somewhere:** Confirm-as-Is → Beer Detail. Low-Confidence Response → attaches wherever needed, across Recommendation, Comparison, and Price Verification. Planning Mode and Proxy-Buying Mode → Recommendation. Preference Input Handling → Recommendation. Recommendation Explanation and "Why" → cross-screen, per Section 6.

**Every Experience has a home:** Beer/SKU Identification → Home and Search/Browse Results. Beer Detail → its own screen. Price Verification → its own screen. Full Recommendation → its own screen. Beer Comparison → its own screen.

**Every Module is represented:** Discovery (Home, Search/Browse Results, Beer Detail), Verification (Price Verification), Recommendation (Recommendation), Comparison (Comparison).

**No screen exists without purpose:** confirmed against Section 3 — each of the six screens has a distinct, non-overlapping ownership statement.

**No purpose exists without a screen:** Engine Behaviors and Platform Services deliberately have no screen at all, by definition of their layer — this is correct, not a gap. Mechanisms are entry actions into Home or Search/Browse Results, not separate destinations, per Principle 13.

**Navigation supports every User Interaction journey:** all six flows from the User Interaction Model (no-anchor recommendation, anchored confirmation, explicit comparison, price verification, planning ahead, proxy buying) map cleanly onto the screens and entry points above with no gaps.

**Assumptions made explicitly, since none of the seven frozen documents named a screen structure before now:** that a single unified Home screen is the right formalization of the "Home" entry point already referenced repeatedly across the Feature Inventory. That Search and Browse, two distinct Mechanisms, can reasonably share one conceptual results screen — whether a future UI visually separates them is a UI decision, not an IA one. That charged-price entry happens within the Price Verification screen itself, since no frozen document specifies exactly where this capture occurs.

---

## 9. Information Architecture Principles — Governing Future Evolution

1. No new screen may be added unless it corresponds to a new Experience already present in the Feature Inventory, or the Feature Inventory is updated first. The IA follows product architecture; it never leads it.

2. A Feature may never be promoted to its own screen simply for convenience — that requires promoting it to Experience status in the Feature Inventory first.

3. No information may be duplicated across two screens' primary content. A screen may reference or link to information owned elsewhere, but never re-host it.

4. Every new entry point must terminate in an existing Decision-Complete-compatible screen, never a dead end requiring undocumented navigation.

5. Cross-screen behaviors must never be reimplemented per screen. A screen introducing its own variant of Explanation or Confidence Communication is a violation, not an enhancement.

6. A screen's "does not own" list is as binding as its "owns" list. Future features must respect both.

7. No screen may require understanding of the Decision Engine, Beer Knowledge Model, or Recommendation Framework's internal logic to use.

8. Backward navigation must remain as well-defined as forward navigation for any newly added flow.

9. No screen may be placed behind login or an account without first formally revisiting the Product Definition Document's boundary against accounts — the IA cannot quietly reverse a canonical decision.

10. Mechanisms may be added or changed freely without requiring any IA change, provided they still enter through an existing screen's ownership.

11. Any new Module must be represented by at least one screen with its own non-overlapping purpose. A Module without a screen, or a screen without a Module, fails the Section 8 checklist.

12. The number of screens is a cost, not a neutral choice. A new screen must justify why an existing screen's ownership couldn't reasonably be extended instead.

13. Occasion and other low-confidence, deferred inputs must never gain the same architectural prominence as budget and core preference inputs, even as new input types are added over time.

14. Every future IA change must be re-validated against the Section 8 checklist in full — passing once is not assumed to mean it still passes after a change.

15. This document must remain re-derivable from the seven frozen documents plus itself. No future screen, behavior, or ownership decision may require reinterpreting any of them.
