# ValueBrew — User Interaction Model
### The canonical interaction model governing how a human engages with the Decision Engine, across any future interface. Derived entirely from the Behavioral Hypothesis Model, Product Definition Document v2, Decision Engine Model, Recommendation Framework, and Beer Knowledge Model. Not a UI document, not wireframes, not information architecture.

---

## 1. User Intent Map

**"I haven't chosen a beer yet."** Wants: to arrive at a specific choice. Already knows: possibly a budget, possibly nothing at all. Doesn't know: which beer, or whether any real trade-off exists between candidates. The engine should accomplish: narrow to a confident recommendation using the minimum necessary questions, budget first.

**"I'm holding a beer" / "I already have one in mind."** Wants: reassurance, not a new search. Already knows: the specific SKU. Doesn't know: whether the price is fair, and may not care whether something else is technically better. The engine should accomplish: a fast, low-friction confirmation — never an unrequested pitch for an alternative.

**"I want to compare beers."** Wants: a direct answer between named candidates, not a funneled recommendation from scratch. Already knows: the specific options. Doesn't know: which one, if any, genuinely wins, or whether they're actually equivalent. The engine should accomplish: a trade-off explanation, or an honest statement that they're tied.

**"I want to verify a price."** Wants: a narrow, specific answer — nothing broader. Already knows: the SKU and what they were charged. Doesn't know: whether that charge is legally accurate. The engine should accomplish: the verification delta, stated plainly, with nothing else attached unless asked for.

**"I'm planning before going shopping."** Wants: a plan, not necessarily a completed purchase decision. Already knows: possibly an occasion or timeframe. Doesn't know: what will actually be available or priced by the time they're at the shelf. The engine should accomplish: the same recommendation logic as any other no-anchor intent, but explicitly carrying a lower confidence ceiling throughout, not just at the end.

**"I want recommendations within a budget."** Wants: the same as the first intent, but budget-led from the first word. Already knows: the budget. Doesn't know: which specific SKU fits it best. The engine should accomplish: treat budget as the first, hardest filter before anything else is asked.

**"I'm buying this for someone else."** Wants: a choice that will land well with someone whose taste they may not fully know. Already knows: possibly very little about the recipient. Doesn't know: what that person would actually want. The engine should accomplish: default to a conservative, clearly-labeled-as-provisional recommendation, escalating in confidence only if real recipient information is offered.

---

## 2. Interaction States

**Exploring.** Purpose: no anchor exists yet, nothing has been narrowed. Entry: no SKU identified, no or minimal constraints stated. Exit: a first constraint is given (→ Narrowing) or a specific SKU is named (→ Confirming). Engine behavior: invite one low-friction first input — a budget is the natural default — without pushing a premature recommendation. What the user should understand before leaving: that even one answer moves things forward meaningfully.

**Narrowing.** Purpose: constraints are being gathered progressively. Entry: at least one constraint is known and more than one real candidate remains. Exit: either enough is known to reach a confident answer (→ Evaluating) or the person stops answering (→ the engine recommends with whatever it has, per the discipline against asking more than the minimum). Engine behavior: ask exactly one well-ordered question at a time — budget, then anchor-check, then style or strength, occasion last, matching the evidence-strength ordering already established. What the user should understand: which of their own answers is currently shaping the outcome.

**Evaluating.** Purpose: known candidates are being weighed against stated constraints. Entry: enough is known to compare real options. Exit: a clean recommendation emerges (→ Confirming) or a genuine trade-off or tie is found (→ Comparing). Engine behavior: apply the Recommendation Framework's constraint tiers exactly, without shortcuts. What the user should understand: whether they're about to see one answer or a real trade-off, not be left waiting on an opaque process.

**Comparing.** Purpose: multiple genuine candidates are presented together. Entry: no single option wins cleanly. Exit: the person picks one (→ Confirming) or changes a constraint (→ back to Narrowing). Engine behavior: present the trade-off in the person's own stated terms; never invent a tiebreaker they never asked for. What the user should understand: specifically what differs between the options, not just that a difference exists.

**Confirming.** Purpose: a specific SKU is being checked or affirmed. Entry: a SKU is known, and either verification or a straightforward fit-check is the goal. Exit: a result is delivered (→ Decision Complete), or a real problem is found, which must always surface regardless of how the interaction started. Engine behavior: default to a fast, low-friction answer; never manufacture an alternative that wasn't asked for. What the user should understand: whether their choice is fine as-is, or precisely what's off about it.

**Learning.** Purpose: the person wants the reasoning behind something they've already been given, not a new answer. Entry: a prior recommendation or verification exists, and a "why" is being asked. Exit: satisfied by the explanation (→ Decision Complete) or the explanation surfaces a constraint they now want to change (→ Narrowing or Comparing). Engine behavior: apply the Recommendation Framework's explanation rules directly — what's certain, what's inferred, and why. What the user should understand: exactly which inputs and confidence levels produced the earlier answer.

**Decision Complete.** Purpose: the interaction has reached a resolved point. Entry: any prior state reaching a satisfying result. Exit: this state is terminal for this interaction — a new one starts fresh rather than extending it. Engine behavior: do nothing further unless asked; do not manufacture continued engagement. What the user should understand: that they have what they came for, plainly, with no expectation of further interaction required.

---

## 3. Interaction Flows

**Flow A — No anchor, seeking a recommendation within budget.** Intent: the best fit for a stated budget. Engine understanding: enters Exploring, treats budget as the first Hard Constraint. Information collection: budget first if not given, then one further preference question only if real candidates still remain close. Recommendation: a Full Recommendation once enough is known. Explanation: separates what's certain (legal price, alcohol-adjusted value) from what's inferred (style fit). User response: accepts, asks why not a different option (→ Learning), or adds a new constraint (→ back to Narrowing). Next interaction: Decision Complete, or another pass through Narrowing/Evaluating.

**Flow B — Anchored, seeking confirmation.** Intent: "is this one okay?" Engine understanding: enters Confirming directly, SKU already known. Information collection: none, by default. Recommendation: Confirm-as-is, or a Price Verification result. Explanation: a plain statement of legitimacy and standing, with no unrequested alternative attached. User response: accepts, or explicitly asks if something better exists — only then does the interaction move into Evaluating/Comparing. Next interaction: Decision Complete, or a fresh Evaluating pass if invited.

**Flow C — Explicit comparison.** Intent: which of these named options is better. Engine understanding: enters Comparing directly. Information collection: only a single clarifying preference if what matters most hasn't been stated. Recommendation: a Trade-off Explanation, or an honest tie. Explanation: side-by-side reasoning tied to what was actually stated. User response: picks one (→ Confirming) or asks to adjust a constraint (→ Narrowing). Next interaction: as above.

**Flow D — Explicit price verification.** Intent: "am I being charged fairly?" Engine understanding: enters Confirming, narrowly scoped. Information collection: the SKU and the charged price, close to mandatory here specifically. Recommendation: the verification delta, stated plainly. Explanation: fair, or above the legal price, with the specific difference named. User response: satisfied, or — if overcharged — may ask what to do, which the engine should answer honestly within its actual scope, stating the fact rather than offering to intervene, since dispute resolution was never an evidenced capability. Next interaction: Decision Complete.

**Flow E — Planning ahead.** Intent: what to get for a future occasion. Engine understanding: the same as Flow A, but flagged from the very first response with the lower confidence ceiling established in the Decision Engine Model. Information collection: same ordering as Flow A. Recommendation: a Full Recommendation, explicitly caveated throughout, not only at the end. Explanation: identical structure to Flow A plus the standing caveat about real-time availability and price. User response: accepts as a provisional plan, or refines further. Next interaction: Decision Complete — worth noting this closes the interaction, not necessarily the purchase, since the actual transaction hasn't happened yet.

**Flow F — Buying for someone else.** Intent: a good choice on someone else's behalf. Engine understanding: enters Exploring under Journey 5's conservative default. Information collection: asks once whether anything is known about the recipient; if nothing is offered, proceeds directly to a conservative recommendation rather than asking further generic questions that wouldn't reduce the real uncertainty. Recommendation: a Full Recommendation explicitly framed as a safe default, or, if recipient information exists, treated as a genuine Strong Preference. Explanation: honest that confidence here is inherently lower than an ordinary self-purchase flow. User response: accepts, or offers more recipient detail (→ back into Narrowing with that as a new input). Next interaction: Decision Complete, with the provisional nature of the confidence stated plainly, not smoothed over.

---

## 4. Interaction Principles

1. **Ask a question only when its answer would actually change which candidate the engine settles on.** Anything else is friction without purpose.

2. **Infer nothing beyond what a SKU's own catalog facts make trivially certain.** Inference from behavior or context remains deferred until real usage earns it — the interaction layer must not quietly reintroduce guessing dressed up as a smoother experience.

3. **Recommend immediately whenever an anchor SKU is already known and nothing further has been requested.** This is the Confirming state's default, protecting exactly the segment the evidence says needs the least intervention.

4. **Compare only when a genuine trade-off or tie exists, or when explicitly asked to.** Comparison is entered because the evidence calls for it, never applied as a default mode to every interaction.

5. **Explain every recommendation, verification, and comparison, every single time** — never abbreviated to a bare answer, regardless of which interface is asking.

6. **The same rules govern every interface.** A chatbot, a voice assistant, and a mobile screen must ask, infer, recommend, compare, and explain by identical logic — only presentation differs, never the underlying discipline.

7. **Every state transition must be traceable to something the person actually did or said.** The engine does not move itself forward without a triggering signal.

8. **Decision Complete must never be artificially extended.** Once someone has what they came for, the interaction ends — it is not a state to be prolonged for engagement's sake.

9. **The Learning state exists specifically for "why," and must never be conflated with a request for a new recommendation.** Asking why something was suggested is not the same question as asking for something different, and the engine's response must recognize which one was actually asked.

10. **Uncertainty must be carried visibly through every state it applies to, not disclosed only at the end.** A planning-ahead confidence ceiling belongs in the first response as much as the last.

11. **Every flow must be able to loop backward, not only forward.** Refining a constraint mid-Evaluating should return cleanly to Narrowing, never force the interaction to restart from nothing.

12. **No principle here may be satisfied by contradicting the Recommendation Framework, the Decision Engine Model, or the Beer Knowledge Model.** This document governs how a person experiences those rules — it does not replace them.
