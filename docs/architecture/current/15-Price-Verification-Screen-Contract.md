# ValueBrew — Screen Contract: PRICE VERIFICATION
### The canonical, implementation-independent contract for the Price Verification screen. Derived entirely from the ten frozen documents plus the Home, Recommendation, Beer Detail, and Comparison Screen Contracts. Not UI, not wireframes, not a PRD.

---

## 1. Screen Identity

**Screen Name:** Price Verification.

**Purpose:** answer exactly one question — was the charged price for this specific SKU the correct legal price — and nothing beyond it.

**Owning Module:** Verification Module.

**Owning Experience:** Price Verification.

**Canonical Role:** the sole screen bounded to a single computation — the verification delta — comparing one Verified Fact, the Legal Price, against one transient, user-reported fact, the Observed/Charged Price.

**Why this screen exists independently:** Beer Detail explains a beer broadly, including its value standing, but never touches a specific transaction's charged price at all — that content is explicitly excluded there. Recommendation and Comparison both reason across multiple options or full preference profiles; Price Verification reasons about exactly one SKU and exactly one reported transaction, a fundamentally narrower operation than either. Merging Price Verification into Beer Detail would violate that screen's explicit exclusion of Observed/Charged Price. Merging it into Recommendation or Comparison would import multi-candidate reasoning into what must remain a single, bounded comparison.

---

## 2. Screen Contract

**MUST:**
- Operate on exactly one identified SKU and exactly one observed/charged price.
- Request the charged price if not already provided — the one legitimate progressive step this screen performs.
- Compute the verification delta by comparing the charged price against the legal reference, without modifying either value.
- Classify the outcome as exactly one of: at the legal price, below the legal price, or above the legal price.
- Attach an Explanation stating the delta plainly, immediately alongside the result.
- Distinguish, in its confidence communication, between confidence in the beer identification, confidence in the legal reference, and confidence in the verification outcome — never collapsing the three into one figure.
- Treat the legal reference as always authoritative, never overridden by the charged price regardless of how confidently that price was reported.

**MAY:**
- Hand off to Beer Detail, if broader context on the SKU is wanted beyond the verification itself.
- Accept a corrected charged price, if the person indicates the first one given was wrong, recomputing without restarting the interaction.

**MUST NEVER:**
- Recommend an alternative beer, under any circumstance, including when an overcharge is found.
- Compare this SKU against any other.
- Perform discovery, preference reasoning, or synthesis of any kind.
- Modify, round, or reinterpret either the legal reference or the reported charged price before comparing them.
- Escalate directly into Recommendation or Comparison merely because a discrepancy was found.
- Persist the charged price beyond the single interaction it belongs to.

---

## 3. Inputs

**Known Information:** the identified SKU, a precondition for this screen to load at all; the Legal Price for that SKU, a Verified Fact drawn from the Beer Knowledge Base.

**Referenced Information:** Beer Identity, for context, never re-owned here.

**Interaction State:** whether the charged price has been provided yet.

**Cross-cutting Behaviors:** Recommendation Explanation is directly reused, applied to the verification delta. Confidence Communication applies with the three-way distinction detailed in Section 6. Decision Complete is directly reachable here.

**Recovery State:** the SKU cannot be resolved against the catalog, an equivalent condition to Beer Detail's own; and, per the open gap flagged in Section 11, a charged price that can't be reported with confidence or precision.

---

## 4. Outputs

**Transition** — to Beer Detail, if broader context is requested.

**Decision** — a system decision: the verification delta's classification, once both values are known.

**Recommendation** — none, ever, regardless of the outcome. This holds even when an overcharge is found.

**Recovery** — an unresolvable SKU.

**Information Request** — the charged price, if not yet given. **This is the screen's normal operating sequence, not a recovery condition** — the same distinction drawn in the Recommendation contract between an ordinary progressive question and genuine Low-Confidence Response applies here identically.

**State Change** — Decision Status moving from Awaiting Price to Verifying, and from there to Completed.

---

## 5. Information Composition

Directly citing Content Architecture Section 3's Price Verification entry. Primary: the Verification Result. Supporting: Legal Price and Observed Price, shown together — the result means nothing without both. Contextual: Beer Identity, referenced rather than re-owned. Progressive: the request for Observed Price, when not yet given. Explanation: states the delta plainly. Confidence: see Section 6's three-way distinction. Completion: reached once the result is acknowledged.

---

## 6. Behavioral Rules

**Verification outcome classification — exactly three, not a binary:**

*At the legal price* — the charged price exactly equals the legal reference. No discrepancy exists.

*Below the legal price* — the charged price is less than the legal reference. This is never treated as a problem, an anomaly, or something requiring explanation beyond a plain statement of the fact — it is simply a favorable, legitimate outcome.

*Above the legal price* — the charged price exceeds the legal reference. This is the one outcome that requires an explicit, honest flag, and per the Recommendation Framework's rule that a genuinely evidenced concern must always surface, it must never be softened or omitted.

**Confidence — three distinct dimensions, and this is a genuine refinement worth stating plainly rather than glossing over.** An earlier canonical document characterized this entire flow as carrying "uniformly high confidence." That framing is correct for two of the three dimensions below, but not automatically for the third, and this contract makes the distinction explicit rather than letting the earlier summary stand unexamined:

*Confidence in beer identification* — a Verified Fact, high, once the SKU is resolved. Identical in kind to every other screen's treatment of identity.

*Confidence in the legal reference* — a Verified Fact, high. Its authority is never in question on this screen; its freshness is a separate, ongoing operational concern belonging to the Beer Knowledge Model's data pipeline, not something this screen itself needs to reason about.

*Confidence in the verification outcome* — genuinely mixed, and this is the nuance the "uniformly high" framing was too loose to capture. The *computation itself* — comparing two numbers — is trivially, deterministically correct, and carries no uncertainty at all. But the outcome's real-world validity is only as good as the Observed/Charged Price input, which the Beer Knowledge Model itself classifies as "high confidence assuming honest reporting, not independently verifiable." The delta is exactly right *given what was reported*; whether what was reported is itself accurate is a ceiling this screen cannot remove, and must not paper over by implying more certainty than the input actually supports.

**Never escalate merely because a discrepancy exists.** An overcharge finding is stated plainly and completely, on its own. It is never accompanied by an unprompted pivot toward "would you like to see a better option" or any comparison — that decision belongs entirely to the person, initiated by their own explicit request, never volunteered by this screen.

**How incorrect SKU selection is handled:** Price Verification has no independent mechanism to detect that the wrong SKU was identified — it trusts the identification handed to it, exactly as every other screen does. If a result seems implausible to the person, the correction path is to return to identification and re-select; this is not something Price Verification computes, flags, or catches on its own.

**How Beer Detail participates:** it supplies Beer Identity for context, and is the destination if the person wants information about the SKU beyond what verification itself requires.

**How Recommendation Explanation is reused:** directly and without modification, applied here to the verification delta rather than to a recommendation — the same structure, the same discipline about stating exactly what's known and at what confidence.

---

## 7. Interaction Contract

**View verification, once the SKU is known.** Trigger: arrival with an identified SKU. Precondition: the SKU must already be resolved. System Response: presents the composition from Section 5, requesting the charged price if not yet given. Possible Outcomes: the result is computed, or the price is requested first. Recovery: an unresolvable SKU. Completion: not yet reached.

**Provide the charged price.** Trigger: the price is requested and not yet given. Precondition: the SKU must be resolved. System Response: the delta is computed and classified. Possible Outcomes: one of the three classifications in Section 6. Recovery: if the price can't be given with confidence, see the open gap in Section 11. Completion: not yet reached.

**View the result.** Trigger: the delta has been computed. Precondition: both values must be known. System Response: presents the classification with its Explanation and Confidence. Possible Outcomes: the person acknowledges it, asks "why," corrects the price, or requests Beer Detail. Recovery: not applicable. Completion: reached upon acknowledgment.

**Correct a previously given charged price.** Trigger: an explicit indication that the first value given was wrong. Precondition: a result must already exist. System Response: recomputes the delta with the corrected value, without restarting the interaction. Possible Outcomes: a new classification. Recovery: not applicable. Completion: not yet reached until the new result is acknowledged.

**Ask "why."** Trigger: an explicit request following a result. Precondition: an Explanation must already exist. System Response: the existing Explanation is re-surfaced; nothing new is generated. Possible Outcomes: the person acknowledges the result afterward. Recovery: not applicable. Completion: not changed by this interaction alone.

**Request Beer Detail.** Trigger: an explicit request for broader context. Precondition: none beyond an already-resolved SKU. System Response: hands off to Beer Detail, carrying the SKU forward. Possible Outcomes: proceeds into Beer Detail's own contract. Recovery: not applicable here. Completion: not reached at Price Verification in this case.

---

## 8. State Machine

**Awaiting Price.** Entry: arrival with a resolved SKU but no charged price yet. Exit: the charged price is given. Permitted transitions: to Verifying. Forbidden: computing a delta before the charged price is known.

**Verifying.** Entry: both the legal reference and the charged price are known. Exit: the delta is computed and classified. Permitted transitions: to Completed. Forbidden: presenting a classification without its attached Explanation and Confidence.

**Recovering.** Entry: the SKU cannot be resolved, or the charged price cannot be given with sufficient confidence per the open gap in Section 11. Exit: the SKU is corrected, or a usable charged price is provided. Permitted transitions: to Awaiting Price, once resolved. Forbidden: computing a delta from an unresolved SKU or an unusable charged price.

**Completed.** Entry: an explicit acknowledgment of the result. Exit: none — terminal for this interaction. Forbidden: any further automatic verification or prompt.

---

## 9. Dependencies

**Decision Engine Model** — directly. The Price Verification recommendation type and its "used whenever a SKU and observed price are both known" framing originate there.

**Beer Knowledge Model** — directly, and most load-bearing. The Legal Price, Observed/Charged Price, and Verification Result object classifications — including the "not independently verifiable" caveat this contract makes explicit in Section 6 — are drawn directly from that document.

**Recommendation Framework** — directly, for the Explanation structure and confidence-expression rules this screen reuses without modification.

**Information Architecture** — directly. This screen's ownership, its possible exits, and its exclusive claim on Observed/Charged Price are defined there.

**Experience Flows** — directly. The Price Verification flow lives entirely on this screen.

**Content Architecture** — directly. This screen's composition in Section 5 is a direct citation.

**Feature Inventory** — directly. Price Verification is the Experience this screen embodies, named there as Core V1 and explicit Essential.

---

## 10. Constraints

Cannot recommend an alternative beer under any circumstance. Cannot compare this SKU against any other. Cannot perform discovery, preference reasoning, or synthesis of any kind. Cannot modify, round, or reinterpret either the legal reference or the reported charged price. Cannot escalate into Recommendation or Comparison unprompted, even when an overcharge is found. Cannot persist the charged price beyond the single interaction it belongs to. Cannot present a verification outcome without distinguishing the three confidence dimensions from Section 6.

---

## 11. Failure Conditions

**Unresolvable SKU.** Detection: the identified SKU can no longer be resolved against the catalog. Recovery: state plainly that the beer can't be found, without inventing a substitute. Progress Preservation: not applicable — there is no prior context on this screen to preserve.

**Open gap, flagged rather than resolved, per policy:** none of the ten frozen documents address what happens when a person cannot report the charged price with precision — an approximate figure ("around 110, not sure exactly") rather than an exact one. The Beer Knowledge Model classifies Observed/Charged Price as user-reported without specifying whether it must be exact to be usable, and the behavioral principle that "verification must never silently modify either value" governs how a *given* value is handled, but not whether an *imprecise* value should be accepted for comparison at all, or what a delta computed against an approximate figure should honestly be allowed to claim. Whether this screen should require an exact figure, accept a range, or handle uncertainty some other way is genuinely undecided, and this is worth a deliberate decision rather than an invented resolution here — consistent with how the equivalent gaps were handled for Home, Recommendation, Beer Detail, and Comparison.

---

## 12. Acceptance Criteria

✓ Price Verification never operates on more than one SKU or produces a comparison against another.
✓ Every verification result is classified as exactly one of at, below, or above the legal price.
✓ A "below" outcome is never presented as, or treated as, a problem.
✓ An "above" outcome is always stated plainly and completely, never softened or omitted.
✓ The three confidence dimensions — identification, legal reference, verification outcome — are never collapsed into a single figure.
✓ Neither the legal reference nor the charged price is ever modified, rounded, or reinterpreted before comparison.
✓ No recommendation or comparison is ever offered unprompted, regardless of the outcome.
✓ The charged price is never retained beyond the interaction that provided it.

---

## 13. Validation

✓ No Product Definition Document violated — no new capability introduced beyond what's already named.
✓ No Recommendation Framework violated — the Explanation and confidence-expression rules are applied exactly as defined.
✓ No Information Architecture ownership violated — this screen's ownership matches its IA entry exactly, including its exclusive claim on Observed/Charged Price.
✓ No Experience Flow violated — the Price Verification flow maps cleanly onto this contract.
✓ No Content Architecture violated — this screen's composition matches that document's entry directly.
✓ No new capability introduced — every behavior here traces to an already-named Experience or Feature.
✓ No hidden assumptions introduced — one genuine gap is named rather than silently resolved: how an imprecise or approximate charged price should be handled, flagged in Section 11, left open pending an explicit decision. One earlier looseness is also corrected rather than left standing: the "uniformly high confidence" characterization of this flow is sharpened in Section 6 into its three actual components, one of which carries a real, honestly stated ceiling.

---

## 14. Future Compatibility

**Natural future evolution:** a formal resolution of the Section 11 gap, defining how approximate or uncertain charged-price reporting should be handled; a possible future indication of the legal reference's own last-confirmed date, if that operational concern is ever surfaced to this screen.

**Forbidden future evolution:** this screen ever recommending an alternative or initiating a comparison on its own, regardless of how severe an overcharge is found to be. This screen ever silently adjusting a reported charged price to make a result look cleaner. This screen ever collapsing its three confidence dimensions into a single score for the sake of a simpler-looking output. This screen ever persisting a charged price across sessions, which would violate both the Beer Knowledge Model's classification of that value as transient and the Product Definition Document's boundary against retained personal data.
