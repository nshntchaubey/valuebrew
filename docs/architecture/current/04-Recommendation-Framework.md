# ValueBrew — Recommendation Framework
### The canonical reasoning rules governing how the Decision Engine evaluates options and arrives at a recommendation. Not an algorithm, not a scoring model, not an implementation document — a set of rules any future implementation must obey.

---

## 1. Recommendation Objective

A recommendation is not "good" because it's simply right. Four separate qualities have to be distinguished, because they can fail independently of each other:

**Correct** — the underlying facts are accurate: the legal price check is right, the alcohol-adjusted value math is right. This is achievable with real confidence for catalog-side facts. It is not achievable with the same certainty for anything touching soft preference or taste-fit, since there's no ground truth the engine can check itself against there.

**Useful** — the recommendation actually moves the person's real decision forward. A mathematically correct answer that ignores a stated preference is useless, however accurate its arithmetic is.

**Explainable** — the reasoning can be stated in plain terms a person can evaluate for themselves, not just accept on faith.

**Trustworthy** — this is not a fourth ingredient to add directly. It's what accumulates, over repeated interactions, from consistently being correct, useful, and explainable at once. Trust cannot be manufactured by asserting confidence; it can only be earned by never having to hide the reasoning behind a recommendation. A single recommendation that's correct but unexplained can still quietly erode trust the moment it's ever wrong — because without visible reasoning, a wrong answer looks like the whole system failed, not like one input was misjudged.

---

## 2. Decision Constraints

**Hard Constraints — must never be violated.** A stated budget ceiling. Any explicit hard exclusion the person states as an absolute limit, not a preference ("must be under 6% ABV," not just "I tend to prefer lighter beers"). Legal and factual accuracy — the engine must never assert something false about price or content to make an answer look cleaner. These belong here because violating any of them doesn't produce a worse recommendation, it produces an illegitimate one.

**Strong Preferences.** Explicitly stated, but not framed as an absolute limit — a preferred style, a preferred strength range, a preferred size. These should dominate ranking, but unlike Hard Constraints, the engine may recommend across them if no option satisfies all of them within budget — and only ever by surfacing that trade-off explicitly, never by quietly picking a winner.

**Soft Preferences.** Occasion-fit, brand affinity not stated as a requirement, price-as-quality-signal reasoning. These belong at a lower tier specifically because the frozen model's own evidence for how reliably they predict a good outcome is thin. They can nudge a recommendation, but must always be visibly distinguished from the higher tiers, never blended into the same confidence.

**Contextual Signals.** Time of day, location, prior behavior. This category exists in the framework for completeness, but is currently empty in practice — inferring anything from these is explicitly deferred per the canon until real usage earns it. Its presence here is a documented decision, not an oversight.

**Tie-breakers.** When options are equally matched on every stated Hard and Strong input, the tie should be broken using the highest-confidence *remaining* differentiator — typically alcohol-adjusted value, since it's one of the two most confidently evidenced facts available — never an arbitrary default, and never a preference the person never actually stated.

---

## 3. Recommendation Scenarios

**Journey 1 (no anchor, no constraints).** Appropriate type: a Low-Confidence Response until at least a budget or one Strong Preference exists. Recommendations should change as each new input arrives, narrowing further. There is no "current choice" to keep here.

**Journey 2 (anchor known).** Default appropriate types: Price Verification, then Confirm-as-is if the anchor already holds up. Recommendations should change only in two cases — the person explicitly signals openness to alternatives, or a price-fairness problem is found, which must always surface regardless of restraint, since it's the single highest-confidence concern in the whole model and should never be suppressed to avoid friction. Absent either, the engine should explicitly recommend **keeping the current choice** — this is the clearest, most legitimate instance of that outcome anywhere in the framework.

**Journey 3 (budget/preference stated, no anchor).** Appropriate types: Full Recommendation, or Trade-off Explanation when no option wins cleanly. Should change as preferences are refined; should stay identical if the same inputs are given again unchanged — consistency itself is part of being trustworthy.

**Journey 4 (planning ahead).** Same recommendation types as Journey 3, but every output must carry the lower confidence ceiling already established in the Decision Engine Model — this framework does not relax that; it inherits it directly.

**Journey 5 (proxy buying).** Default to a Low-Confidence Response with a conservative, low-risk suggestion, unless recipient preference is known — in which case it should be treated exactly like a Strong Preference belonging to the actual consumer. Should not change toward more confident territory without new recipient information becoming available.

---

## 4. Trade-off Framework

A trade-off can only ever be reasoned about *within* the space a Hard Constraint allows — never as a way to cross one. Hard Constraints are not one side of a trade-off; they're the boundary trade-offs happen inside of.

When two Strong Preferences conflict with each other (style versus strength, say), the engine must not silently resolve the conflict by picking a winner — this is exactly what the Trade-off Explanation recommendation type exists for. The reasoning gets surfaced; it doesn't get buried.

When a Strong Preference could be traded against a higher-confidence fact — a different style, but meaningfully better alcohol-adjusted value — the engine may suggest this, but only ever as a visible option to consider, never as an override of what was actually stated. The person's own stated preference always outranks the engine's own judgment about what would be smarter.

Every trade-off must be framed against what the person actually said, not against what the engine assumes they'd probably want — "this is different from your stated style, but meaningfully better value, since you didn't set a hard style limit," not "this is objectively the smarter pick."

Magnitude matters even without numbers: a difference too small to plausibly matter to the actual decision shouldn't be surfaced as a trade-off at all. Presenting a trivial difference as a meaningful choice adds noise the person never asked to weigh.

---

## 5. Recommendation Boundaries

**Insufficient information.** If too little is known to responsibly reach a Full Recommendation, the engine should not force one — it should ask the single most useful remaining question, or offer a clearly labeled provisional starting point, never a confident-sounding guess dressed up as a real answer.

**Multiple equally good options.** A genuine tie, even after the tie-breaker rule in Section 2 is applied, should be presented as a tie — "these are equivalent on everything you've told me matters" is a complete, honest recommendation. Forcing an arbitrary pick here would misrepresent what the engine actually knows.

**Conflicting preferences.** If a stated budget and a stated Strong Preference together rule out every real option, the engine must surface that conflict directly, rather than quietly deciding which constraint to honor and which to drop on the person's behalf.

**Weak evidence behind an input itself.** Whenever an input the engine is using — occasion-fit especially — rests on thin evidence in the frozen model, the recommendation must communicate that specifically, not just generically. Naming *why* confidence is limited (a genuine tie, a real conflict, a thinly evidenced input, simply too few inputs) is itself part of being explainable, not a separate courtesy on top of it.

---

## 6. Recommendation Explanation

**What should always be explained:** which inputs contributed, and at what tier — which Hard Constraint was satisfied, which Strong Preference was matched or traded off, which Soft Preference nudged the outcome — along with the confidence attached to each one, and any trade-off made and the reasoning behind it.

**What should remain hidden:** only the technical mechanics of *how* something was computed — nothing about *why* a recommendation was made should ever be treated as hidden. If an explanation of the reasoning would be embarrassing to surface, that's a sign the reasoning itself is flawed, not a case for concealing it.

**How trade-offs should be presented:** in plain comparative language, tied directly to what the person actually stated — never with invented precision, like a false-sounding match percentage. The same discipline against fake numerical weighting that governs the trade-off framework governs how trade-offs are described, too.

**How confidence should be expressed:** in terms a person can act on — "I'm confident about the price and the value math; based on what you told me, this also seems to fit the style you're after" — never collapsed into one blended confidence figure that hides which parts are solid and which are a best guess.

---

## 7. Recommendation Principles

1. A recommendation must never violate a Hard Constraint, even when doing so would look like a "smarter" answer.
2. Every recommendation must be traceable to specific, named inputs — never an unexplained output.
3. High-confidence facts and low-confidence inferences must never be merged into a single, unlabeled judgment.
4. A genuine tie must be presented as a tie, never forced into an arbitrary decision.
5. Conflicting stated preferences must be surfaced, never silently resolved by discarding one of them.
6. Every trade-off must be explained against what the person actually said, never against what the engine assumes they'd prefer.
7. A trivial difference between options is not a trade-off worth presenting.
8. Confidence must be expressed in terms a person can act on, never as a single opaque score.
9. The engine must never claim more certainty about taste or preference fit than the evidence behind that input actually supports.
10. Recommending that a person keep their current choice is a complete, legitimate outcome — not a failure to produce something new.
11. Under genuine uncertainty, the engine should offer either its single most useful next question or a clearly labeled provisional answer — never a confident-sounding guess.
12. Nothing about *why* a recommendation was made should ever need to be hidden from the person receiving it.
13. These rules must hold regardless of whatever specific algorithm, model, or interface eventually implements them — the reasoning is canonical; the technology underneath it is not.
14. The same inputs, given again unchanged, must produce the same recommendation — stability is part of what makes a system trustworthy.
15. Every recommendation exists to serve the specific person receiving it, not to showcase how sophisticated the system producing it is.
