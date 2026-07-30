# ValueBrew — Experience Flows
### The canonical, interface-independent journeys. Derived entirely from the eight frozen documents. Not user flows, not wireframes, not a PRD. Answers one question: how should every supported journey unfold from beginning to end, regardless of interface?

---

## 1. Experience Flow Principles

1. Every experience begins with an intent from the User Interaction Model's Intent Map, never from an internal system trigger.

2. Every experience ends with Decision Complete, regardless of which Experience reached it.

3. Every experience asks only for information that would actually change its outcome.

4. Every explanation follows its recommendation, verification, or comparison immediately — never deferred, never requiring a separate request to appear for the first time.

5. Uncertainty is carried throughout an experience, not disclosed only at the end — established explicitly for Planning Mode, and generalized here to any flow with a soft input in play.

6. A system decision moment and a user decision moment are never the same moment. The engine may narrow, weigh, or compute; only the person chooses.

7. Every flow can loop backward into an earlier point without restarting from intent — recovery preserves progress by default.

8. No flow may silently drop a stated Hard Constraint partway through. If it can no longer be satisfied, the flow surfaces that conflict rather than quietly abandoning it.

9. A tie or a trade-off is a valid, complete outcome of a flow, not a failure requiring further search.

10. Every flow is achievable using only the Experiences, Features, and behaviors already named in the Feature Inventory — no flow invents a new capability to resolve a gap.

11. Confidence is stated in the same terms at every decision moment within a flow — it cannot read as certain early and quietly soften later without saying so.

12. Recovery is the default assumption for any interruption; restarting from the very beginning is exceptional, reserved only for a genuine change of intent, not an interruption within the same one.

13. A flow's completion condition must be nameable in one sentence. If it can't be, it isn't ready to be documented as a flow.

14. Every flow respects the Information Architecture's ownership boundaries — moving between Experiences never causes one to perform work owned by another.

15. No flow requires the person to understand *why* the system is asking something, only *what* it's asking.

---

## 2. Canonical Experience Flows

**No-Anchor Recommendation.** Intent: "I haven't chosen a beer yet." Trigger: arriving with no specific beer and no budget yet stated. Information gathered: budget first, then one further preference only if still needed. Reasoning performed: Full Recommendation synthesis, weighing the Hard Constraint against Strong and Soft Preferences, applying the tie-breaker rule if needed. Experiences involved: Beer/SKU Identification, Full Recommendation, optionally Beer Detail. Features invoked: Preference Input Handling, Low-Confidence Response if budget alone leaves the field too open. Cross-cutting behaviors: Recommendation Explanation, Confidence Communication. Completion condition: the person accepts the recommended SKU. Possible refinements: adding a further preference mid-flow, asking "why," moving into Comparison if a genuine trade-off or tie surfaces.

**Budget Recommendation.** Intent: "I want recommendations within a budget." Trigger: a budget is stated as the opening fact. Information gathered: budget already known; the engine checks whether that alone narrows to a confident answer before asking anything else. Reasoning performed: identical Full Recommendation synthesis to the flow above. Experiences: Full Recommendation. Features: Preference Input Handling for anything beyond budget, Low-Confidence Response if needed. Cross-cutting: same as above. Completion: same as above. Worth stating plainly: this flow and No-Anchor Recommendation converge into the identical remaining process the instant budget is known — they differ only in how that first fact arrived, not in anything downstream.

**Anchored Confirmation.** Intent: "I'm holding a beer" / already have one in mind. Trigger: a specific SKU is already identified. Information gathered: none, by default — this is the flow where the engine recommends immediately. Reasoning performed: the Confirm-as-Is judgment, plus the mandatory price-legitimacy check, which surfaces regardless of restraint. Experiences: Beer/SKU Identification, Beer Detail. Features: Confirm-as-Is, Low-Confidence Response (rare, only if the underlying legal price data is itself uncertain). Cross-cutting: Recommendation Explanation, Confidence Communication. Completion: the person accepts the confirmation, or acknowledges a flagged price problem. Possible refinements: the person explicitly asks if something better exists — the one branch point in an otherwise question-free flow, moving into Comparison or a fresh Recommendation flow, only ever at the person's invitation.

**Price Verification.** Intent: "I want to verify a price." Trigger: a specific SKU and a specific charged price are both known. Information gathered: the charged price, if not already given. Reasoning performed: the verification delta against the legal reference. Experiences: Beer/SKU Identification, Price Verification. Features: none beyond the verification computation itself — this flow stays deliberately narrow, answering only what was asked. Cross-cutting: Recommendation Explanation, and notably the highest, most uniform Confidence Communication anywhere in the canon, since this rests entirely on the two highest-confidence facts available. Completion: the delta is stated and acknowledged. Possible refinements: the person asks what to do about an overcharge, answered honestly within scope — the fact is restated, never escalated into a dispute-resolution capability that doesn't exist; the person asks if something better exists, the same invitation-only branch as Anchored Confirmation.

**Beer Comparison.** Intent: "I want to compare beers." Trigger: two or more specific candidates already named. Information gathered: at most one clarifying question about what matters most, only if not already stated. Reasoning performed: Trade-off/Tie-handling logic across the named candidates. Experiences: Beer/SKU Identification and Beer Detail per candidate, Beer Comparison. Features: none beyond the comparison logic itself; Low-Confidence Response if a clarifying question goes unanswered with nothing else to go on. Cross-cutting: Recommendation Explanation, Confidence Communication. Completion: the person selects one candidate, or accepts an honest tie disclosure. Possible refinements: adding or removing a candidate mid-comparison, or adjusting a constraint and returning into a Recommendation flow, holding the comparison set rather than discarding it.

**Planning Ahead.** Intent: "I'm planning before going shopping." Trigger: the decision is explicitly for a future occasion, not an immediate purchase. Information gathered: the same as Budget/No-Anchor Recommendation, but every output additionally carries the standing lower-confidence caveat from the very first response, not only the last. Reasoning performed: identical Full Recommendation synthesis, with Planning Mode attached. Experiences: Full Recommendation. Features: Planning Mode, Preference Input Handling, Low-Confidence Response. Cross-cutting: Recommendation Explanation, explicitly restating the caveat every time it appears, not just once; Confidence Communication. Completion: the person accepts a provisional plan, understood explicitly as a plan, not a completed purchase decision. Possible refinements: re-entering this same flow again closer to the actual purchase, without Planning Mode, for a firmer answer — a legitimate, evidence-consistent way this flow resolves over time rather than in one sitting.

**Buying for Someone Else.** Intent: "I'm buying this for someone else." Trigger: the beer is explicitly for someone else's consumption. Information gathered: whatever is known about the recipient's preference, asked once and not pressed further if nothing is offered. Reasoning performed: Full Recommendation synthesis, defaulting conservatively unless recipient information exists, in which case it's treated as a genuine Strong Preference. Experiences: Full Recommendation. Features: Proxy-Buying Mode, Preference Input Handling. Cross-cutting: Recommendation Explanation, explicitly naming the lower confidence here as distinct from an ordinary self-purchase flow; Confidence Communication. Completion: the person accepts the recommendation, explicitly marked as provisional. Possible refinements: offering more recipient detail after an initial conservative answer, looping back into re-evaluation with that new Strong Preference, never a restart.

---

## 3. Decision Moments

**"Has enough been gathered to recommend confidently?"** — occurs in No-Anchor, Budget, Planning, and Proxy flows. Known: whatever inputs have been given so far. Unknown: whether remaining candidates are meaningfully different from each other. Confidence: high if budget plus a Strong Preference narrows to one clear winner; low if only budget is known and several candidates remain close. Becomes possible: the moment an additional question would no longer change which candidate wins.

**"Is the anchor still the best fit?"** — Anchored Confirmation. Known: the anchor SKU's own price, ABV, and size. Unknown: whether a better-value alternative exists that the person hasn't considered. Confidence: high on the anchor's own legitimacy and standing; the "is this really best" judgment is deliberately never volunteered unless invited, which is itself the correct behavior, not a gap. Becomes possible: immediately, the moment the anchor's own facts are known.

**"Is this price legitimate?"** — Price Verification. Known: the legal reference price, the reported charged price. Unknown: structurally nothing — this is the one decision moment in the entire canon that doesn't degrade under uncertainty, since both inputs are the highest-confidence facts in the model. Confidence: high, always. Becomes possible: immediately, once both facts are known.

**"Does any candidate win outright, or is this a trade-off or tie?"** — Beer Comparison, and embedded within any Recommendation flow where multiple close candidates remain. Known: each candidate's facts and computed value. Unknown: which of several close candidates the person would actually prefer, when the difference touches only a Soft Preference. Confidence: high on the underlying facts, genuinely low on declaring one winner when the difference is soft. Becomes possible: when the differentiating factor is Hard or Strong, a clean recommendation is possible; when it's only Soft, the honest resolution *is* the decision not to force a single winner.

**"How much weight does a stated recipient preference carry?"** — Buying for Someone Else. Known: whatever the buyer reported about the recipient, if anything. Unknown: whether that secondhand information is accurate. Confidence: inherently capped below an ordinary self-purchase flow, regardless of how much recipient detail exists. Becomes possible: as soon as either a conservative default is acceptable, or recipient information exists to treat as a Strong Preference.

---

## 4. User Decision Moments

Kept strictly separate from Section 3 — these are choices only the person makes, never the engine.

Choosing to state a budget or preference, or to decline to. Choosing to accept a recommendation, or to ask "why" first. Choosing to signal openness to alternatives after a confirmation or verification. Choosing which specific candidates to compare. Choosing a winner from a trade-off, or accepting a tie as the answer. Choosing to refine a stated constraint after seeing a result. Choosing to report what a recipient might want, or to leave it unknown. Choosing whether to treat a planning-ahead result as final, or to return closer to the purchase moment for a firmer answer.

---

## 5. Recovery Flows

**No beer identified.** The identification attempt yields nothing. Recovery: return to intent capture, but preserve any budget or preference already stated — if the person pivots into a no-anchor Recommendation flow instead, nothing already given is lost.

**Too little information.** Low-Confidence Response fires. Recovery: the single most useful next question is asked; nothing already given is re-asked. This is a recovery in place, not a restart.

**Tie.** Tie Disclosure is presented as a complete, valid outcome. Recovery, if the person wants a further push: one more preference dimension is requested, not a restart of the whole flow.

**Trade-off.** Trade-off Explanation is presented. Recovery: the person picks a side or refines a constraint, either of which preserves everything already established.

**User changes preference.** Recovery: re-enter evaluation with the updated Strong Preference; budget and any other unchanged inputs are preserved.

**User changes budget.** Recovery: this can genuinely invalidate a prior recommendation, since a Hard Constraint can never be violated — but any stated Strong or Soft Preferences are preserved; only the budget-driven candidate set is recomputed.

**User changes comparison target.** Recovery: Comparison re-evaluates with the new candidate set; reasoning already surfaced for the unchanged candidates is not redone from scratch.

**When a full restart genuinely is warranted, stated plainly rather than left implicit:** only when the underlying intent itself changes — someone verifying a price who suddenly wants an unrelated recommendation for a different occasion entirely is not recovering from an interruption, they're beginning a genuinely new journey, and starting fresh there is correct, not a failure of recovery design.

---

## 6. Cross-Flow Consistency

**Recommendation Explanation** behaves identically across all seven flows: it appears immediately alongside its answer, separates certain from inferred content the same way every time, and never requires a separate request to appear for the first time.

**Confidence Communication** behaves identically across all seven flows: high-confidence facts and low-confidence inferences remain visibly distinguished everywhere, with the one notable variation being *degree*, not *mechanism* — Price Verification is uniformly high-confidence by nature; Planning Ahead and Buying for Someone Else are uniformly capped lower by nature. The rule producing that distinction is the same rule in every flow.

**Decision Complete** behaves identically across all seven flows: nothing further is required once reached, and nothing is artificially extended, regardless of which flow or Experience arrived there.

**Learning ("Why?")** behaves identically across all seven flows: available wherever Recommendation Explanation appears, always retrieving the same underlying reasoning rather than generating something new, and never treated as equivalent to a fresh recommendation request.

---

## 7. Flow Validation

**Every Experience appears:** Beer/SKU Identification (No-Anchor, Anchored Confirmation, Price Verification, Comparison), Beer Detail (Anchored Confirmation, Price Verification, Comparison), Price Verification (its own flow), Full Recommendation (No-Anchor, Budget, Planning, Proxy), Beer Comparison (its own flow).

**Every Feature appears:** Confirm-as-Is (Anchored Confirmation), Low-Confidence Response (No-Anchor, Budget, Comparison, Planning, Proxy), Planning Mode (Planning Ahead), Proxy-Buying Mode (Buying for Someone Else), Preference Input Handling (No-Anchor, Budget, Planning, Proxy).

**Every Entry Point is supported:** opening, searching, browsing, planning, price verification, recommendation, and comparison all map directly onto the seven flows documented above, matching the Information Architecture's own Section 5.

**Every Module participates:** Discovery, Verification, Recommendation, and Comparison all appear across the seven flows.

**Every journey ends:** each flow states an explicit, single-sentence completion condition.

**No unsupported branch exists:** every refinement named in Section 2 routes into an already-documented flow or recovery — none invents a new capability.

**No duplicated reasoning exists:** the decision moments in Section 3 are shared, singular processes referenced across multiple flows, never reimplemented separately per flow — "has enough been gathered" is one piece of reasoning used by four different flows, not four different versions of the same question.

---

## 8. Experience Principles — Governing Future Experience Design

1. No future UI may skip an explanation to save space. Recommendation Explanation is non-negotiable content, not an optional enhancement.

2. No future UI may merge a system decision moment with a user decision moment into one indistinguishable action. A person must always be able to tell when they chose something versus when the engine did.

3. No future interface may ask a question the person has already answered, regardless of how that interface is structured.

4. No future UI may present a tie or a trade-off as an error state or a failure. Both are complete, honest outcomes.

5. No future UI may collapse Planning Mode's standing caveat into a one-time disclaimer shown only at the start or end.

6. No future UI may add a persistent profile, history, or account surface without first revisiting the Product Definition Document's boundary against one.

7. No future UI may allow a restart to discard preserved context when a recovery flow was available instead.

8. No future UI may present Confidence Communication as a single blended score, regardless of how compact the interface needs to be.

9. No future UI may introduce a decision-making shortcut — a default, an auto-selection — that the Recommendation Framework doesn't already describe.

10. No future UI may hide the reasoning behind a recommendation behind anything other than the explicitly designed "Why" affordance.

11. No future UI may treat Proxy-Buying Mode's conservative default as equivalent in confidence to an ordinary self-purchase recommendation.

12. No future UI may introduce a flow not documented here. A genuinely new journey requires this document to be extended first, never improvised in design.

13. No future UI may resolve a conflict between a stated Hard Constraint and a stated Strong Preference silently — the conflict must remain visible.

14. No future UI may treat Decision Complete as a springboard into another action the person didn't ask for.

15. This document, together with the eight it depends on, is the complete reference. No future experience decision may be made by design instinct alone when a canonical answer already exists here.
