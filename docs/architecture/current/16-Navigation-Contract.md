# ValueBrew — Canonical Navigation Contract
### The implementation-independent navigation contract for the ValueBrew application. Derived entirely from the ten frozen documents and the five frozen Screen Contracts. Not a wireframe, not a user flow, not an implementation guide. Wherever a behavior already belongs to a Screen Contract, it is referenced here, never restated.

---

## 1. Purpose

This document defines every legal and illegal transition between the five screens with canonical Screen Contracts — Home, Recommendation, Beer Detail, Comparison, Price Verification — along with each transition's trigger, precondition, and the context it carries or discards. It exists so that navigation itself is governed by contract, the same way each screen's internal behavior already is.

**A scope limitation stated up front, not buried:** the Information Architecture defines six screens, not five. Search/Browse Results has no Screen Contract of its own, and Home's own contract explicitly requires passing through it to reach Beer Detail or Comparison. This document can specify every transition *directly among the five contracted screens* completely. It cannot fully specify the two paths that pass through Search/Browse Results, because the screen governing that middle hop has no behavioral contract yet. Both paths are documented here as far as this document's authority extends, and the gap is flagged formally in Section 10 and Section 14.

---

## 2. Navigation Philosophy

Navigation is never a decision-making act. A transition carries context between screens that reason; it never reasons itself.

Every transition preserves context by default. Discarding context is the exception, and every instance of it must be justified against a specific screen's own contract, never assumed.

No transition occurs without a triggering action — user-initiated or a defined system completion — matching the discipline already established in the User Interaction Model and every individual Screen Contract.

Backward movement is never a blind return to a fixed default. It returns to wherever the person actually came from, per Beer Detail's own explicit rule, generalized here to the whole product.

A hand-off is not a restart. The receiving screen inherits whatever context the sending screen already carried; it never begins from nothing.

Ownership of a transition belongs to the screen initiating it, never to the destination — the same ownership discipline the Information Architecture applies to information now applies to movement between screens.

---

## 3. Screen Graph

**In canonical scope:** Home (H), Recommendation (R), Beer Detail (BD), Comparison (C), Price Verification (PV).

**Referenced but out of scope, with no Screen Contract:** Search/Browse Results (SBR).

**Direct edges, in-scope to in-scope:**

H → R · H → PV
R → BD · R → C · C → R
BD → PV · BD → C · PV → BD · C → BD
C → PV · PV → C is **not** a direct edge — see Section 10.

**Indirect edges, passing through the out-of-scope screen:**

H → SBR → BD
H → SBR → C

**Forbidden edges, stated here and detailed in Section 10:**

BD → H, R → H, C → H, PV → H (in every case). H → BD directly. H → C directly. PV → R. PV → C directly, as a system-initiated escalation.

---

## 4. Entry Points

**Entry into the product as a whole** is always Home, per the Information Architecture — there is no other first screen.

**Entry into a specific screen**, once inside an interaction, varies: Recommendation is entered from Home or from Comparison (a constraint refinement). Beer Detail is entered from Search/Browse Results, from Recommendation, from Comparison, or from Price Verification. Comparison is entered from Search/Browse Results, from Recommendation, or from Beer Detail. Price Verification is entered from Home, from Beer Detail, or from Comparison.

---

## 5. Exit Points

**Screens capable of reaching Decision Complete:** Recommendation, Beer Detail, Comparison, Price Verification — each independently, per their own contracts.

**Home never reaches Decision Complete.** It is exclusively a routing screen, per its own contract and the Content Architecture's explicit statement to that effect.

---

## 6. Transition Contracts

**Home → Recommendation.** Trigger: a budget, preference, planning, or proxy-buying intent is expressed. Required context: none. Context carried forward: any Preference Summary preserved through a prior Home-level recovery. Context discarded: none. Ownership: Home, per its own contract's Interaction Contract Section 7.

**Home → Price Verification.** Trigger: an explicit verification intent. Required context: none. Context carried forward: none beyond the intent itself — the SKU and charged price are gathered on Price Verification, not before. Context discarded: none. Ownership: Home.

**Recommendation → Beer Detail.** Trigger: an explicit request for fuller context on the recommended SKU. Required context: a recommendation must already exist, per Recommendation's own Section 6 threshold. Context carried forward: the recommended SKU's identity. Context discarded: the rest of the Preference Summary is not required by Beer Detail and is not carried in, consistent with Beer Detail's exclusive focus on one SKU's own facts. Ownership: Recommendation.

**Recommendation → Comparison.** Trigger: a genuine trade-off or tie is surfaced, and richer treatment is invited. Required context: the trade-off or tie must already exist, per Recommendation's Section 6. Context carried forward: the candidate set involved in the trade-off or tie, and the full Preference Summary. Context discarded: none. Ownership: Recommendation.

**Comparison → Recommendation.** Trigger: an explicit refinement of a previously stated constraint. Required context: none beyond an active comparison. Context carried forward: the current candidate set and Preference Summary, per Comparison's own Section 7. Context discarded: none — this is a hand-back, not a restart. Ownership: Comparison.

**Beer Detail → Price Verification.** Trigger: an explicit request to check a charged price. Required context: an already-identified SKU. Context carried forward: the SKU identity only. Context discarded: none, though nothing beyond the SKU is required. Ownership: Beer Detail.

**Beer Detail → Comparison.** Trigger: an explicit signal of openness to alternatives, or a direct comparison request. Required context: an already-identified SKU. Context carried forward: the current SKU, as one candidate in the new comparison set. Context discarded: none. Ownership: Beer Detail.

**Price Verification → Beer Detail.** Trigger: an explicit request for broader context beyond the verification itself. Required context: an already-resolved SKU. Context carried forward: the SKU identity. Context discarded: the charged price is never carried forward — it is exclusively Price Verification's, per that contract's own Constraints, and Beer Detail explicitly excludes it. Ownership: Price Verification.

**Comparison → Beer Detail.** Trigger: an explicit request to drill into one named candidate. Required context: the candidate must already be part of the active comparison set. Context carried forward: that one candidate's SKU identity. Context discarded: the rest of the comparison set is not carried into Beer Detail, consistent with that screen's single-SKU scope. Ownership: Comparison.

**Comparison → Price Verification.** Trigger: an explicit request to check one named candidate's charged price. Required context: the candidate must already be part of the active comparison set. Context carried forward: that one candidate's SKU identity. Context discarded: the rest of the comparison set and the Preference Summary are not required by Price Verification's bounded scope. Ownership: Comparison.

**Home → Search/Browse Results → Beer Detail, and Home → Search/Browse Results → Comparison.** Trigger, required context, and context handling for the first hop cannot be fully specified here, since Search/Browse Results has no Screen Contract. What can be stated, drawn from Home's and Beer Detail's own contracts: Home never transitions directly to either destination; whatever selection happens on Search/Browse Results must resolve to one or more specific SKUs before Beer Detail or Comparison can begin; and any Preference Summary already established before the search is expected to survive the hop, per the general context-preservation philosophy in Section 2, though this expectation is not independently confirmed by a contract for the middle screen.

---

## 7. Preconditions

Home → Recommendation: none. Home → Price Verification: none. Recommendation → Beer Detail: a recommendation must exist. Recommendation → Comparison: a trade-off or tie must exist. Comparison → Recommendation: an active comparison must exist. Beer Detail → Price Verification: an identified SKU must exist. Beer Detail → Comparison: an identified SKU must exist. Price Verification → Beer Detail: a resolved SKU must exist. Comparison → Beer Detail: the target candidate must already be in the active set. Comparison → Price Verification: the target candidate must already be in the active set.

---

## 8. Postconditions

After every transition into Recommendation: Progressive Question-Asking resumes or begins from whatever Preference Summary was carried in, never from zero if something was already known. After every transition into Beer Detail: the destination SKU's facts are loaded before any Confirm-as-Is judgment is evaluated, per Beer Detail's own State Machine. After every transition into Comparison: the candidate set contains at least the SKU that triggered the hand-off, never fewer. After every transition into Price Verification: exactly one SKU is active, and the charged price is treated as unknown unless it was somehow already provided, which no current transition supplies. After every transition into Home: Decision Status resets to Initial — nothing from a prior interaction survives into a fresh entry, consistent with Home's own Constraints.

---

## 9. Navigation Invariants

Home is never reached as a backward destination, from any of the other four screens, under any condition. This holds without exception across every contract.

No screen persists Preference Summary, a candidate set, or an SKU identity beyond the session it was established in, consistent with the Product Definition Document's rejection of accounts.

Every transition traces to either an explicit user action or a defined system completion (a recommendation being reached, a comparison resolving) — never to an unexplained or automatic advance.

Price Verification never transitions directly into Recommendation or Comparison as a system-initiated escalation, regardless of the verification outcome. Any onward movement from Price Verification into broader reasoning requires the person's own explicit request, routed as a fresh entry into that screen, not as an automatic consequence of a discrepancy.

A hand-off always carries at least the minimum context the destination's own Preconditions require, per Section 7 — no transition may fail to supply what its own destination contract demands.

---

## 10. Illegal Navigation

**Any screen → Home, as a backward destination.** Forbidden by Beer Detail's, Recommendation's, Comparison's, and Price Verification's own contracts, all independently, and restated here as a product-wide invariant.

**Home → Beer Detail, direct.** Forbidden by Home's own Constraints — Beer Detail is reachable only via Search/Browse Results.

**Home → Comparison, direct.** Forbidden by Home's own Constraints, for the same reason.

**Price Verification → Recommendation, direct, as a system-initiated transition.** Forbidden by Price Verification's own Constraints — this screen must never escalate into recommendation reasoning on its own initiative, even following an overcharge finding.

**Price Verification → Comparison, direct, as a system-initiated transition.** Forbidden for the same reason.

**Any transition that would let a screen perform another screen's owned reasoning instead of handing off.** For instance, Beer Detail computing a verification delta itself rather than transitioning to Price Verification; Comparison synthesizing a Full Recommendation from a freshly gathered preference profile rather than handing back to Recommendation. Every individual Screen Contract's own Constraints section already forbids this on its own terms; this is the cross-cutting restatement.

---

## 11. Recovery Navigation

**Home's own recovery states** — Recovering (no beer identified), Clarifying (ambiguous intent), Out-of-Scope (unsupported intent) — are internal to Home and do not constitute a screen transition in the sense this document tracks; they are documented fully in Home's own Screen Contract and referenced here only for completeness.

**Beer Detail's "SKU not found" recovery** does not transition anywhere new — the person remains on Beer Detail in its Recovering state, per that contract's own State Machine, until the reference is corrected or the interaction ends.

**Comparison's "unresolvable candidate" recovery** does not transition to a new screen either — it holds the person on Comparison until the candidate set is corrected, per that contract's own rules.

**Price Verification's "unresolvable SKU" recovery** behaves identically — no screen transition occurs; the person remains on Price Verification until resolved.

**The general pattern, worth stating once rather than five times:** recovery, across every screen with its own contract, resolves *in place*. None of the five screens' recovery conditions produce a transition to a different screen as their resolution mechanism — they hold the person where they are until the triggering condition clears. The one partial exception is Home, where a recovery condition can be followed by a pivot into a different screen entirely, but that pivot is an ordinary Home → Recommendation or Home → Price Verification transition, governed by Section 6 like any other, not a special recovery-specific transition type.

---

## 12. Cross-Screen Context Preservation

**Preference Summary** persists across Recommendation ↔ Comparison hand-offs in both directions, per both screens' own contracts, and is not required or referenced by Beer Detail or Price Verification, whose scopes don't call for it.

**SKU identity** is the one piece of context that survives every single transition in this graph — every edge in Section 3 either requires it as a precondition or produces it as a postcondition, with the sole exception of Home → Recommendation and Home → Price Verification, where it doesn't yet exist.

**Observed/Charged Price** never survives any transition at all. It is exclusive to Price Verification, per the Beer Knowledge Model's own classification, and no edge in this graph carries it anywhere, including Price Verification's own hand-off back to Beer Detail.

**Candidate sets** persist across Comparison ↔ Recommendation and Comparison → Beer Detail / Price Verification hand-offs, though only the single relevant candidate travels forward into Beer Detail or Price Verification specifically, never the full set, consistent with those screens' single-SKU scope.

---

## 13. Validation

✓ Every transition among the five contracted screens traces to a rule already stated in at least one of their individual Screen Contracts — none was invented here.
✓ No illegal transition listed in Section 10 is permitted anywhere else in this document.
✓ Every screen's own Constraints section is respected without exception across Sections 6 through 9.
✓ No new capability, screen, or behavior was introduced — this document only synthesizes what already existed across five separate contracts into one graph.
✓ The one genuine incompleteness — the two edges passing through the uncontracted Search/Browse Results screen — is named explicitly in Sections 1, 6, and 14, not silently smoothed over.

---

## 14. Future Compatibility

**Natural future evolution:** a Screen Contract for Search/Browse Results, which would complete this document's two currently-underspecified edges and let Sections 6 through 9 state their preconditions and context handling with the same precision as every other edge in the graph.

**Forbidden future evolution:** any new transition added to this graph without a corresponding rule already present in the relevant screen's own contract — a new edge here must always be traceable backward to a screen-level permission, never invented at the navigation layer directly. Any relaxation of the Home-is-never-a-backward-destination invariant, or the Price-Verification-never-escalates invariant, without first formally revisiting the individual Screen Contracts those rules originate from.
