# ValueBrew — Screen Contract: COMPARISON
### The canonical, implementation-independent contract for the Comparison screen. Derived entirely from the ten frozen documents plus the Home, Recommendation, and Beer Detail Screen Contracts. Not UI, not wireframes, not a PRD.

---

## 1. Screen Identity

**Screen Name:** Comparison.

**Purpose:** evaluate two or more already-identified beers relative to one another, producing a winner within the named set, a Trade-off Explanation, or a Tie Disclosure.

**Owning Module:** Comparison Module.

**Owning Experience:** Beer Comparison.

**Canonical Role:** the sole screen that reasons about *relationships* between named candidates — never about what exists elsewhere in the catalog, and never about a single beer in isolation.

**Why this screen exists independently:** Recommendation searches the entire catalog from preference inputs to arrive at an answer; Comparison never searches anything at all — it only ever reasons about candidates it was explicitly handed. Beer Detail explains exactly one beer in isolation; Comparison exists specifically because a single-beer view has no way to express a relationship between two or more. Price Verification checks a charged price against a legal reference; Comparison never touches transaction-level pricing. Merging Comparison into any of these would either force it to start searching the catalog, in direct violation of its bounded nature, or would strip out the explicitly relational content — Trade-off, Tie — that has no home anywhere else in the product.

---

## 2. Screen Contract

**MUST:**
- Operate only on candidates already explicitly named or selected before arrival — never add a candidate the person didn't provide.
- Apply the Recommendation Framework's tie-breaker rule — the highest-confidence remaining differentiator — before concluding that a genuine tie exists.
- Produce a Comparison Result reflecting the actual relationship among the named candidates: a winner within that set, a Trade-off Explanation, or a Tie Disclosure.
- Present a Tie Disclosure honestly when candidates are genuinely equivalent on every known input, never forcing an arbitrary pick.
- Present a Trade-off Explanation whenever no clean winner exists, naming the specific dimensions on which candidates differ.
- Attach Recommendation Explanation and Confidence Communication to every Comparison Result, using the exact same structure used everywhere else in the product.
- Reference each candidate's per-SKU facts directly from the Beer Knowledge Model, never recomputing them independently.

**MAY:**
- Ask at most one clarifying question, if what matters most between the candidates hasn't already been stated.
- Hand back to Recommendation, if a constraint is refined.
- Hand off to Beer Detail, for deeper context on any one candidate.
- Hand off to Price Verification, if the person wants to check one candidate's charged price.
- Accept an added or removed candidate mid-comparison, re-evaluating the set without discarding reasoning already established about the unchanged candidates.

**MUST NEVER:**
- Search the catalog for candidates that weren't already provided.
- Synthesize a Full Recommendation from a preference profile gathered from scratch — that operation belongs exclusively to Recommendation.
- Perform the verification delta computation.
- Explain a single beer in isolation, without reference to at least one other candidate — that is Beer Detail's job.
- Push the person toward a beer that was never part of the original comparison request.
- Manufacture a winner simply to avoid presenting a tie or a trade-off.
- Ask more than one clarifying question.

---

## 3. Inputs

**Known Information:** the named candidate set — two or more already-identified SKUs; any Preference Summary carried forward from wherever the comparison originated.

**Referenced Information:** Beer Knowledge Base facts for every named candidate; Style Benchmark, where available, for relative-standing context.

**Interaction State:** whether the named set has resolved to a winner, a trade-off, or a tie yet.

**Cross-cutting Behaviors:** Recommendation Explanation, Confidence Communication, and Learning ("Why") all directly apply. Decision Complete is reachable here.

**Recovery State:** insufficient differentiation among candidates, requiring the single permitted clarifying question; or a member of the named set that can no longer be resolved against the catalog, analogous to Beer Detail's "SKU not found," scoped to one candidate within the set.

---

## 4. Outputs

**Transition** — to Beer Detail, for deeper context on one candidate; to Recommendation, if a constraint is refined; to Price Verification, if a specific candidate's charged price is to be checked.

**Decision** — a system decision: whether the named set resolves to a winner, a trade-off, or a tie.

**Recommendation** — none, in the Full Recommendation sense. Only ever a bounded, dimension-scoped "better" conclusion among the named candidates. See Section 6 for the precise distinction this contract depends on.

**Recovery** — insufficient differentiation, or an unresolvable candidate.

**Information Request** — the single permitted clarifying question, when genuinely needed.

**State Change** — Decision Status moving toward a resolved Comparison Result, and from there into Completed.

---

## 5. Information Composition

Directly citing Content Architecture Section 3's Comparison entry. Primary: the Comparison Result. Supporting: Beer Identity and Alcohol-Adjusted Value for every candidate, shown together. Contextual: Preference Summary, so the person can see what was actually weighed. Progressive: at most one clarifying question. Explanation: attached to the Comparison Result, especially load-bearing whenever a Trade-off is involved. Confidence: attached per candidate and to the overall result. Recovery: for a tie, an unresolved trade-off, or insufficient differentiation. Completion: reached once a winner is chosen or a tie/trade-off is accepted as the answer.

---

## 6. Behavioral Rules

**How "better" differs from "recommended" — the load-bearing distinction this entire contract depends on.** Recommendation answers "what should I choose," by searching the whole catalog and synthesizing an answer from a fully gathered preference profile. Comparison answers "how do these known beers differ," and never searches anything — it only ever describes relationships among candidates it was explicitly given. "Better," on this screen, is always relative and dimension-bound: one candidate outperforms another on a specific, named axis (alcohol-adjusted value, say), or dominates cleanly across every currently-known criterion *for this bounded set specifically*. "Recommended" is what Full Recommendation alone can produce, because only Recommendation looked beyond a pre-named set to begin with. **Comparison can conclude that Beer A is better than Beer B. It can never claim to have recommended the best beer in existence, because it never looked past the candidates it was handed.** This distinction must never blur, even when Comparison's tie-breaker logic clearly favors one candidate over the others — that conclusion is still bounded to the named set, not a claim about the whole catalog.

**How trade-offs are communicated:** by naming the specific dimensions on which candidates genuinely differ — never as a vague "these are different" statement. A Trade-off is presented alongside its constituent facts, never separated from them, per the Content Architecture's information relationships.

**How ties are represented:** only after the Recommendation Framework's tie-breaker rule has already been applied and failed to differentiate the candidates. A genuine tie is stated plainly — "these are equivalent on everything you've told me matters" — never forced into an arbitrary pick, and never treated as a lesser or incomplete outcome than a clean winner.

**How Confidence Communication behaves here, distinct from both Recommendation and Beer Detail:** two separate confidence layers apply simultaneously, and they must never be merged. Per-candidate confidence reflects each SKU's own Verified and Computed Facts, uniformly high, exactly as on Beer Detail. Result-level confidence reflects the Comparison Result itself, and carries the same unusual property the Trade-off object has everywhere else in the canon — the underlying facts are high-confidence even when the judgment of which side to prefer is low-confidence, whenever the differentiator is a Soft Preference rather than a Hard or Strong one.

**How Recommendation Explanation is reused:** directly, without modification, applied here to the Comparison Result rather than to a Full Recommendation — the same structure, the same rules about separating certain from inferred content.

**How Beer Detail participates:** it is the source of every per-candidate fact Comparison references. Comparison never re-derives a SKU's price, ABV, or size independently — it consumes exactly what Beer Detail already owns. A person may also drill into a full Beer Detail view for any one candidate directly from this screen, without that drill-down altering the comparison itself.

**How Recommendation participates:** it may be the origin of a comparison request, when a trade-off or tie surfaced there and richer treatment was invited; it is always the destination when a constraint is refined mid-comparison; and it may supply an existing Preference Summary that Comparison inherits as context, without re-gathering it from scratch.

---

## 7. Interaction Contract

**View the comparison.** Trigger: arrival with a named candidate set. Precondition: at least two resolvable candidates. System Response: presents the composition from Section 5. Possible Outcomes: a winner, trade-off, or tie is shown; or a clarifying question is posed first, if needed. Recovery: an unresolvable candidate, if one exists in the set. Completion: not yet reached.

**Answer the clarifying question.** Trigger: the single permitted question has been posed. Precondition: the question must be currently active. System Response: the answer is applied and the comparison is re-evaluated once. Possible Outcomes: a winner, trade-off, or tie now resolves. Recovery: not applicable. Completion: not yet reached.

**Select a winner.** Trigger: an explicit choice, following a Trade-off Explanation or a dominant candidate. Precondition: a Comparison Result must already exist. System Response: Decision Status moves to Completed. Possible Outcomes: Decision Complete. Recovery: not applicable. Completion: reached.

**Accept a tie as the answer.** Trigger: an explicit acceptance, following a Tie Disclosure. Precondition: a Tie Disclosure must already exist. System Response: Decision Status moves to Completed. Possible Outcomes: Decision Complete. Recovery: not applicable. Completion: reached.

**Ask "why."** Trigger: an explicit request, following any Comparison Result. Precondition: an Explanation must already exist to retrieve. System Response: the existing Explanation is re-surfaced; nothing new is generated. Possible Outcomes: the person selects a winner, accepts a tie, or refines further, having learned something from it. Recovery: not applicable. Completion: not changed by this interaction alone.

**Add or remove a candidate.** Trigger: an explicit change to the named set. Precondition: at least two candidates must remain. System Response: re-evaluates the set; reasoning already established for unchanged candidates is not redone from scratch. Possible Outcomes: a new winner, trade-off, or tie. Recovery: not applicable. Completion: not yet reached.

**Refine a constraint.** Trigger: an explicit change to a previously stated preference. Precondition: none. System Response: hands back to Recommendation, carrying the current candidate set and Preference Summary forward. Possible Outcomes: proceeds into Recommendation's own contract. Recovery: not applicable here. Completion: not reached at Comparison in this case.

**Request Beer Detail, or Price Verification, for one candidate.** Trigger: an explicit request naming one member of the set. Precondition: none beyond the candidate already being part of the named set. System Response: hands off, carrying that one SKU forward. Possible Outcomes: proceeds into the requested screen's own contract. Recovery: not applicable here. Completion: not reached at Comparison in this case.

---

## 8. State Machine

**Initial.** Entry: arrival with a named candidate set. Exit: the set is evaluated at least once. Permitted transitions: to Evaluating. Forbidden: presenting a Comparison Result before any evaluation occurs.

**Evaluating.** Entry: every time the candidate set or its inputs change, including the first arrival. Exit: the tie-breaker rule and trade-off logic are applied. Permitted transitions: to Resolved, if a winner, trade-off, or tie is determined; to Clarifying, if one further question would resolve genuine ambiguity; to Recovering, if a candidate can't be resolved. Forbidden: posing a clarifying question without first attempting evaluation.

**Clarifying.** Entry: one further question would resolve the remaining ambiguity. Exit: the question is answered. Permitted transitions: to Evaluating, for a final pass. Forbidden: posing a second clarifying question under any circumstance.

**Resolved.** Entry: a winner, trade-off, or tie has been determined. Exit: the person selects, accepts a tie, asks "why," refines a constraint, or requests a hand-off. Permitted transitions: to Completed; to Recommendation, to Beer Detail, or to Price Verification, on explicit request. Forbidden: presenting a result without its Explanation and Confidence attached.

**Recovering.** Entry: a candidate in the named set can't be resolved. Exit: the unresolvable candidate is removed or replaced, or the person abandons the comparison. Permitted transitions: to Evaluating, once the set is corrected. Forbidden: silently dropping the unresolvable candidate without informing the person.

**Completed.** Entry: an explicit selection or tie acceptance. Exit: none — terminal for this interaction. Forbidden: any further automatic comparison or prompt.

---

## 9. Dependencies

**Decision Engine Model** — indirectly, through the shared Decision Moment governing whether a candidate set resolves to a winner or a trade-off/tie.

**Beer Knowledge Model** — directly. Every per-candidate fact referenced here originates from that document's classifications.

**Recommendation Framework** — directly, and most load-bearing. The tie-breaker rule, the trade-off framework, and the confidence-expression rules are what Section 6 of this contract directly operationalizes.

**Information Architecture** — directly. This screen's ownership, its possible exits, and its status as a destination screen are defined there.

**Experience Flows** — directly. The Beer Comparison flow, and the recovery flows for a tie, a trade-off, and a changed comparison target, all live on this screen.

**Content Architecture** — directly. This screen's composition in Section 5 is a direct citation.

**Feature Inventory** — directly. Beer Comparison is the Experience this screen embodies, and its explicit dependency on Beer Detail and the Trade-off/Tie-handling Engine Behavior is drawn directly from that document.

---

## 10. Constraints

Cannot search the catalog for candidates not already provided. Cannot synthesize a Full Recommendation from a freshly gathered preference profile. Cannot perform verification delta computation. Cannot explain a single beer without reference to another. Cannot push toward a beer outside the original comparison request. Cannot manufacture a winner to avoid a tie or trade-off. Cannot ask more than one clarifying question. Cannot merge per-candidate confidence with result-level confidence into one figure.

---

## 11. Failure Conditions

**Insufficient differentiation.** Detection: candidates remain indistinguishable after the tie-breaker rule is applied, and no further clarifying question would resolve it. Recovery: present the honest Tie Disclosure — this is a complete answer, not a failure requiring further search. Progress Preservation: the full candidate set and any Preference Summary remain intact.

**Unresolvable candidate.** Detection: a member of the named set can no longer be resolved against the catalog. Recovery: inform the person plainly and invite removal or replacement of that one candidate; never silently drop it without saying so. Progress Preservation: the remaining resolvable candidates and any established Preference Summary stay intact.

**Open gap, flagged rather than resolved, per policy:** every worked example of comparison reasoning across the ten frozen documents — the tie-breaker rule, the Decision Moment governing winner-versus-trade-off, the Trade-off object itself — is framed around exactly two candidates. Comparison is explicitly scoped to "two or more," but **no frozen document addresses how the same logic scales to three or more candidates**, particularly the case of a non-transitive or partial ordering — for instance, Candidate A beating Candidate B, B being tied with Candidate C, but A beating C outright. Whether this should be presented as one combined result, as several pairwise sub-comparisons, or resolved some other way is genuinely undecided, and this is worth a deliberate decision rather than an invented resolution here, consistent with how the equivalent gaps were handled for Home, Recommendation, and Beer Detail.

---

## 12. Acceptance Criteria

✓ Comparison never includes a candidate that wasn't part of the original request.
✓ A Comparison Result is never presented without the Recommendation Framework's tie-breaker rule having been applied first.
✓ A Tie Disclosure is never replaced with an arbitrary pick.
✓ A Trade-off is never presented without its constituent facts alongside it.
✓ No more than one clarifying question is ever posed in a single comparison.
✓ Per-candidate confidence and result-level confidence are always kept visibly distinct, never merged.
✓ Comparison never states or implies that its conclusion reflects a search of the whole catalog.
✓ Refining a constraint always hands back to Recommendation rather than being resolved on this screen.

---

## 13. Validation

✓ No Product Definition Document violated — no new capability introduced beyond what's already named.
✓ No Recommendation Framework violated — the tie-breaker, trade-off, and confidence rules are applied exactly as defined, with no substitute logic invented.
✓ No Information Architecture ownership violated — this screen's ownership matches its IA entry exactly, including its explicit exclusion of open-ended discovery.
✓ No Experience Flow violated — the Beer Comparison flow and its associated recovery flows map cleanly onto this contract.
✓ No Content Architecture violated — this screen's composition matches that document's entry directly.
✓ No new capability introduced — every behavior here traces to an already-named Experience or Feature.
✓ No hidden assumptions introduced — one genuine gap is named rather than silently resolved: how comparison logic scales beyond two candidates, flagged in Section 11, left open pending an explicit decision.

---

## 14. Future Compatibility

**Natural future evolution:** richer Style Benchmark integration once that Platform Service matures; a formal resolution of the Section 11 gap, defining exactly how three-or-more-candidate comparisons should be structured and presented.

**Forbidden future evolution:** this screen ever performing its own catalog search to add candidates the person didn't name. This screen ever computing a verification delta or a Full Recommendation itself, rather than handing off to the screen that owns each. This screen ever presenting a manufactured winner to avoid the discomfort of a tie or trade-off, regardless of how much more polished a single clean answer might look. This screen ever merging per-candidate and result-level confidence into a single score for the sake of a simpler-looking output.
