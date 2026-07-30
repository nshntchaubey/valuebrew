# ValueBrew — Decision Engine Model
### The canonical conceptual reasoning model. Derived entirely from the frozen Behavioral Hypothesis Model and Product Definition Document v2. Not an algorithm, not a UI — a thinking model.

---

## 1. Decision Philosophy

**ValueBrew does not recommend the objectively best beer. It recommends the beer that best fits what this specific person has told it matters, weighted honestly by how confident the engine actually is in each factor it used to get there.**

"Best" is not a universal ranking. It is not "cheapest," and it is not a single, all-encompassing quality score — no such score is evidenced anywhere in the canon, and inventing one would violate the product's own founding discipline. "Best" is relative to three things, in a fixed order of trust: what the person explicitly constrained (a budget, a stated preference), what the engine can verify with real confidence (legal price, alcohol-adjusted value), and, only where explicitly volunteered, softer preferences the engine has no independent way to confirm (style affinity, occasion fit). The engine's job is never to decide what "best" universally means — only to reason honestly, every time, about what best means for the person in front of it, given only what it actually knows.

---

## 2. User Journeys

**Journey 1 — No anchor, no stated constraints.** What the engine knows: nothing yet. What it still needs: at minimum a starting constraint (a budget, or a stated preference) before it can reason at all. Decision it improves: the core synthesis decision from the Product Definition Document — "which beer, given what I care about." This is the Deliberate/Exploratory pathway from the frozen model, entered with nothing to anchor on.

**Journey 2 — A specific beer already identified.** However the identification happened (by name, by scan, by simply being in hand) is irrelevant to this conceptual model — the engine only cares that a specific SKU is now known. What the engine knows: every catalog fact about that SKU (price, ABV, size). What it still needs: little, by default — the frozen model found no evidenced friction for buyers who already know what they want. Decision it improves: primarily price-legitimacy confirmation; alternative-value comparison only if the person signals openness to it, never pushed uninvited.

**Journey 3 — Budget and/or preferences stated, no specific beer yet.** What the engine knows: explicit constraints. What it still needs: only as many further preference dimensions as are required to narrow to a confident answer — see Section 4. Decision it improves: the full synthesis recommendation, the product's stated core purpose.

**Journey 4 — Planning ahead, before a store visit.** Flagged honestly: the frozen model treats "decisions made before reaching the shelf" as an unresolved Hypothesis, not a confirmed behavior. What the engine knows: possibly an occasion or timeframe. What it still needs: the same inputs as Journey 3, but with a structurally lower confidence ceiling on the output, since real-time availability and current price at whatever store is eventually visited cannot be verified in advance. The engine should be explicit about this ceiling rather than presenting an advance recommendation with the same confidence as an in-the-moment one.

**Journey 5 — Buying on someone else's behalf.** Included for conceptual completeness, though the Product Definition Document explicitly defers building for this journey given the model's "unknown prevalence" finding. What the engine knows: typically nothing about the actual consumer's taste. What it still needs: whatever the buyer can report of the recipient's preference, and failing that, a deliberately conservative, low-risk default rather than a confident guess. Decision it improves: JTBD-5, at low priority.

---

## 3. Inputs

**Catalog-side facts — never asked of the user, always already known once a SKU is identified:** legal price, alcohol content, size/format, calories, brand, style. These come directly from the two highest-confidence capabilities in the Product Definition Document and should never be re-requested from a person.

**User-preference inputs, all explicit for now — inference is explicitly deferred by the canon:**

- **Budget.** Explicit. Optional, but central to the product's full stated purpose. Confidence: high once given.
- **Selected/anchor beer.** Explicit or resolved by whatever identification method is used. Optional. Confidence: high once resolved to one SKU.
- **Preferred style.** Explicit only — inferring this from unobserved history is explicitly out of scope per the Product Definition Document. Optional. Confidence: high once stated, though the model's own evidence for how strongly style-fit should influence an outcome is only moderate.
- **Preferred strength/ABV range.** Explicit. Optional. Confidence: high once given.
- **Preferred size/format.** Explicit. Optional. Confidence: high once given.
- **Preferred brand.** Explicit. Optional. Confidence: high once given, though the model gives little reason to expect this is commonly volunteered upfront rather than surfacing through Journey 2's anchor selection instead.
- **Occasion.** Explicit. Optional. Confidence: moderate at best — this remains one of the frozen model's more thinly evidenced inputs, and should be weighted accordingly, never treated as equal in reliability to budget or ABV.
- **Price actually charged or observed.** Explicit. Mandatory only for verification-type recommendations. Confidence: high assuming honest reporting — the engine has no independent way to confirm what a person tells it they were charged.
- **Recipient preference** (Journey 5 only). Explicit if known, absent otherwise. Confidence: low, and deprioritized consistent with the Product Definition Document's deferral of this journey.

**Explicitly excluded for now:** inferred contextual signals — time of day, location, past browsing or purchase history. The Product Definition Document defers all learned or inferred personalization until real usage justifies it. Listed here only so their absence is a documented decision, not an oversight.

---

## 4. Progressive Information Gathering

**First priority:** budget, if not already known — it's the single input most directly tied to the product's stated purpose and narrows the field the most per question asked.

**Second:** whether a specific beer is already in mind — this single question determines which journey applies at all, and resolving it early prevents asking preference questions to someone who's already decided (a direct violation of restraint if asked anyway).

**Third, only if no anchor exists:** one preference dimension at a time, in order of evidence strength — strength/ABV and style before occasion, since occasion carries the weakest evidence in the model of any input listed.

**When a question becomes unnecessary:** the moment enough is known to distinguish a small set of genuinely different candidates. If two more questions would only reorder options that are already functionally equivalent given what's known, neither question is worth asking.

**When to stop asking altogether:** once remaining candidates are few enough and different enough that further questions would cost more in effort than they'd add in confidence — this is a direct application of the product's founding discipline against unnecessary friction.

**When to recommend immediately, asking nothing:** Journey 2, by default — an anchor beer already resolves most of what the engine needs, and the frozen model gives no reason to interrupt a buyer who already knows what they want.

---

## 5. Recommendation Types

**Price Verification.** Confirms or flags a specific price against the legal reference. Used whenever a SKU and an observed price are both known — most often Journey 2.

**Confirm-as-is.** States plainly that the current choice already looks like the best available fit within known constraints. Used in Journey 2 whenever the anchor genuinely is the strongest option — never replaced with a manufactured alternative just to appear useful.

**Value Comparison / Alternative Suggestion.** Surfaces a similar or better-value option. Used only when either the person has signaled openness to alternatives, or a full recommendation (Journey 1/3) naturally surfaces one — never pushed uninvited onto someone who already has an anchor and hasn't asked.

**Full Budget/Preference Recommendation.** The core synthesis output combining every known constraint into a specific answer. Used in Journeys 1, 3, and 4.

**Trade-off Explanation.** Lays out why one candidate isn't a clean winner against another — cheaper but weaker on strength, say. Used whenever no single option dominates on every input the person has stated.

**Low-Confidence / Insufficient-Information Response.** States plainly that too little is known to recommend with real confidence, and either asks the single most useful next question or offers a clearly-labeled provisional starting point. Used whenever the confidence rules in Section 6 aren't met.

---

## 6. Recommendation Confidence

**High confidence, stated as such without hedging:** anything resting purely on catalog-side facts and the two highest-confidence capabilities — legal price verification, alcohol-adjusted value comparison. These rest on the model's strongest evidence and should read that way.

**Acknowledged uncertainty, always visible, never hidden inside a clean-looking answer:** anything where style, occasion, or brand preference materially shaped the outcome. The engine should be able to say, in effect, "on price and value, here's what I'm sure of — on fit for your taste, here's my best read from what you told me," rather than blending both into one unlabeled recommendation.

**Why this matters for trust, directly from the Product Definition Document's own reasoning:** a wrong recommendation with visible reasoning is a data point the person can disagree with on a specific factor. A wrong recommendation with no visible reasoning reads as the whole system being unreliable. The difference between those two outcomes is entirely the explanation, not the accuracy.

---

## 7. Conceptual Decision Flow

**User Context** — whichever journey applies, established from however much is already known at the moment of engagement.

**↓ Known Information** — catalog facts for any identified SKU, plus whatever explicit inputs have already been given.

**↓ Remaining Uncertainty** — the gap between what's known and what's needed to reach a confident recommendation type, per Section 6's thresholds.

**↓ Information Gathering (only if the uncertainty is large enough to matter)** — one question at a time, ordered by evidence strength, stopping the moment further questions stop changing the outcome.

**↓ Evaluation** — weighing known constraints against catalog data, keeping high-confidence and low-confidence inputs visibly separate rather than merged into one score.

**↓ Recommendation** — one of the six types from Section 5, chosen by which journey and which confidence level actually apply.

**↓ Explanation** — a plain statement of what drove the recommendation, explicitly separating what the engine is sure of from what it's inferring from stated preference.

---

## 8. Design Principles

1. **Ask only questions that would actually change the outcome.** A question whose answer can't shift the recommendation isn't worth the effort it costs.

2. **Never ask for information the engine already has** — catalog facts, or preferences already stated earlier in the same interaction.

3. **Recommend only within what the person has explicitly constrained.** A stated budget or preference is a hard boundary, not a suggestion the engine can quietly override.

4. **Keep high-confidence facts and low-confidence inferences visibly separate in every recommendation** — never blend legal price and alcohol-adjusted value with soft taste-fit into one unlabeled answer.

5. **Every recommendation must be explainable in plain terms.** If the reasoning can't be stated simply, the recommendation isn't ready to be made.

6. **Default to confirmation, not persuasion, whenever an anchor is already known and no openness to alternatives has been signaled.** The frozen model found no friction to solve here — don't invent one.

7. **State insufficient information plainly rather than guessing with false confidence.** "I don't know enough yet" is a legitimate, honest recommendation type.

8. **Never infer an unstated preference.** Inference is deferred until real usage earns it — guessing at what wasn't said isn't a shortcut, it's an overclaim.

9. **Treat the person's stated constraint as always outranking the engine's own reasoning**, not the other way around.

10. **Never ask more than the minimum number of questions needed to reach a confident answer** — every additional question has a real cost that must be justified on its own.

11. **Never present a recommendation as universally "the best beer."** Only ever the best fit for what this specific person has said matters to them.

12. **Let low-evidence journeys — proxy buying especially — degrade to conservative, low-risk defaults rather than fabricate confidence about something the engine genuinely doesn't know.**
