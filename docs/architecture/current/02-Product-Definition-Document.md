# ValueBrew — Product Definition Document (PDD) v2
### Supersedes v1. Built from an explicit founder strategic decision: ValueBrew is a beer decision engine, not a price-fairness or trust-first product. Remains consistent with the frozen Behavioral Hypothesis Model; does not re-open or re-rank prior opportunity analysis.

---

## 1. Product Definition

**ValueBrew is a decision engine that helps a beer buyer in Karnataka choose the best beer for their own budget and preferences — weighing price legitimacy, value for money, alcohol content, style, and occasion together into one recommendation, rather than requiring the buyer to weigh them separately.**

**What it is:** a synthesis engine. Price fairness, cost-per-alcohol value, ABV, calories, style, occasion-fit, and availability are all inputs it reasons over — none of them is the product's identity on its own.

**What it is not:** not a single-purpose price checker, not a pure value-comparison calculator, not a social or ratings platform — though, notably, it does now carry more ambition toward preference-matching than a narrower product would, and that ambition is only as sound as the evidence behind each input it draws on.

**Why it should exist:** no source found anywhere in the model's research combines these attributes into one place. Price, ABV, occasion, and brand are each independently evidenced as real factors people weigh — but nothing evidenced anywhere brings them together into a single guided decision.

**Which customer decision it exists to improve:** "given what I have to spend and what I actually care about, which specific beer should I buy right now?" — a broader question than either price-fairness or value-for-money alone, and one that requires the product to be honest about how confidently it can answer each part of it.

---

## 2. Product Vision

If ValueBrew succeeds completely, a buyer stops having to mentally juggle price, strength, style, and occasion separately every time they choose. The weighing happens for them, calibrated to what they've told the product matters — a fair price, a certain strength, a certain budget, a certain occasion — and the result is a specific, explainable recommendation rather than a pile of separate facts they have to reconcile themselves. This is a more ambitious vision than a single-purpose tool would carry, and that ambition is a deliberate choice, not something the evidence alone would have proposed.

---

## 3. Product Principles

**1. Ground every recommendation in verifiable facts first.** Legal price and actual alcohol content remain the two highest-confidence inputs anywhere in the model. They anchor every recommendation, even as other, softer inputs get added around them.

**2. Never let a synthesized recommendation carry more confidence than its weakest input.** This is more important now than under a narrower product, not less — a single blended "best for you" answer can quietly launder a low-confidence input (taste, preference fit) into something that reads as authoritative. The product must resist that.

**3. Weight each input by its actual evidence strength, not treat all inputs as equally reliable.** Price and ABV rest on strong, current regulatory evidence. Occasion-fit is real but only partially unclaimed territory. Taste-preference matching has essentially no evidence in the model for how it would even be captured. The recommendation logic must reflect that hierarchy honestly, not flatten it.

**4. A recommendation must show its reasoning, not just its output.** Given that this product now blends several inputs of very different confidence levels, "why" a specific beer was recommended is not a nice-to-have — it's the only way a buyer can tell whether the reasoning behind it actually reflects what they said mattered to them.

**5. Preferences are learned from real behavior over time, not assumed upfront.** The model has no evidence at all for how personal preference data would be gathered or modeled. Early versions should treat "preferences" as simple, explicit, buyer-stated inputs — a budget ceiling, a stated style or strength — not a sophisticated personalization system invented ahead of any evidence that one is needed or how it should work.

**6. Stay out of the way of buyers the evidence says are already well served.** The Habitual/Anchored segment shows no identified friction anywhere in the model. A recommendation engine must recognize when someone already knows what they want and not manufacture a decision process where none is wanted.

**7. Don't build for jobs the model can't evidence.** The Fallback JTBD remains almost entirely at Assumption-level in the frozen model. Broadening the product's ambition doesn't retroactively create evidence for this one.

**8. Anchor to objective, verifiable facts until real usage produces behavioral or preference data.** Every strongly evidenced input is public and static. Everything softer must be built to visibly improve as real data accumulates, not be faked into false confidence on day one.

**9. Preserve real differences in how people decide, rather than collapsing them into one recommendation style.** Habitual, Deliberate, Impulse, and preference-driven decision modes are genuinely different in the model. A recommendation engine that treats every visit the same way misrepresents its own foundation.

**10. Stay disciplined to the category the evidence actually supports.** Broadening the product's ambition across attributes is not license to broaden it across categories — nothing in the model evidences a need to serve non-beer decisions.

---

## 4. Core User Decision

**Starting state:** a buyer with a budget in mind and some mix of stated or implicit priorities — price, strength, style, occasion — facing multiple real options, with no way to weigh all of those factors together at once.

**Desired end state:** a specific, explainable recommendation that reflects what they actually said mattered to them, built from inputs the product is honest about the confidence of.

**What "better decision" means here:** not simply "cheapest," and not simply "best value" in isolation — the model's own evidence includes buyers for whom price signals quality, not just cost. "Better" means a recommendation that's transparent about which inputs drove it and how sure the product actually is about each one — never a single number or verdict presented with uniform, unearned authority.

---

## 5. Core Product Capabilities

**Legal Price Verification.** Why it exists: the single highest-confidence finding anywhere in the model. Supports: the price-legitimacy input to every recommendation. Why fundamental: it's the one input whose reliability doesn't depend on anything soft or unproven.

**Alcohol-Adjusted Value Comparison.** Why it exists: a clean, evidenced information gap, now backed by a real regulatory reform tying legal price directly to alcohol content. Supports: the value-for-money input. Why fundamental: it's the second highest-confidence input in the entire model.

**Budget and Preference Input Handling.** Why it exists: this is now the explicit, stated core of the product — without it, there's no actual recommendation, only a lookup tool. Supports: budget constraints, stated style/strength preference, occasion context. Why fundamental despite resting on the model's weaker evidence: the founder's decision makes this load-bearing regardless of its current confidence level — which is exactly why Principle 5 exists, to keep this capability honest about what it doesn't yet know.

**Honest, Explainable Recommendation Output.** Why it exists: blending several inputs of different confidence levels into one answer is the product's single largest risk of overclaiming. Supports: trust across every JTBD the recommendation touches. Why fundamental: without visible reasoning, a wrong recommendation breaks trust completely; with it, a wrong recommendation is just a data point the product can visibly improve from.

**Segment-Appropriate Restraint.** Why it exists: the Habitual segment has no identified friction anywhere in the model. Supports: not intruding on buyers who don't need a recommendation at all. Why fundamental: a recommendation engine that can't recognize when no recommendation is needed misrepresents its own research.

---

## 6. Product Boundaries

**ValueBrew WILL:** verify legal pricing as a foundational input; compute alcohol-adjusted value as a second foundational input; accept explicit budget and preference inputs and weigh them into one recommendation; show the reasoning behind every recommendation, including how confident each input actually is.

**ValueBrew WILL NOT, for now:**
- **Restaurant or bar discovery** — out of the model's evidenced scope (off-trade only).
- **Alcohol delivery or e-commerce** — no evidenced demand for transaction facilitation, and a commercial incentive inside the recommendation layer would undermine the honesty Principle 2 depends on.
- **A full social or ratings platform** — the model's taste- and quality-adjacent findings are its thinnest. A lightweight, honest feedback mechanism to gradually improve preference-matching may eventually be worth exploring once real usage exists — this stays a deferred question, not a "never," precisely because "preferences" is now core to the product's stated purpose.
- **A loyalty or rewards program** — never appears anywhere in the model.
- **Sophisticated, upfront personalization** — nothing evidences how this should work yet; it must be earned from real behavior, not assumed into the first release.

---

## 7. Product Philosophy

**ValueBrew believes that beer buying should never require a person to mentally juggle price, strength, style, and fairness separately in order to make a good decision for their own budget and taste.**

This shapes every future decision the same way: any input the product can verify or compute reliably belongs inside the recommendation with real confidence attached. Any input the product is still guessing at — taste, personal preference beyond what's explicitly stated — must be visibly and honestly treated as less certain, never smoothed over to make the recommendation feel more complete than it actually is.

---

## 8. Success Definition

**For the user:** they receive a specific, explainable recommendation that genuinely fits their stated budget and priorities, without having had to cross-reference price, ABV, and style themselves — and if the recommendation is wrong, they can see why, rather than simply losing trust in the whole product.

**For the product:** its recommendations are trusted enough that people act on them, and transparent enough that a single wrong recommendation doesn't collapse confidence in every other one.

**For the business:** it becomes the place people default to before buying — not because of one single mechanic, but because its overall reasoning, across many different people's different priorities, consistently holds up.

---

## 9. V1 Scope

**Essential for V1:** Legal Price Verification and Alcohol-Adjusted Value Comparison, as the two highest-confidence inputs; simple, explicit Budget and Preference input handling — a budget ceiling and a stated style or strength preference, nothing more sophisticated yet; Honest, Explainable Recommendation output, showing which inputs drove each result and how confident the product actually is in each one.

**Intentionally deferred:** any learned or inferred personalization beyond what's explicitly stated; a richer occasion-fit dimension, given the model's own note that this space is partially served elsewhere already; any lightweight feedback mechanism for gradually improving preference-matching, held pending real usage rather than built speculatively; any accommodation for proxy buying, given the model's explicitly unknown prevalence for this behavior.

**Should probably never exist:** a dedicated fallback/substitute-suggestion capability, since the model itself never actually observed this moment's existence or resolution, only inferred it. E-commerce, delivery, a full social/ratings platform, and loyalty mechanics remain outside the product regardless of how the core purpose has broadened.

---

## 10. Product Manifesto

**What is ValueBrew?**

ValueBrew is a decision engine, not a lookup tool. It exists to take everything that actually matters when choosing a beer — a fair price, real value for money, alcohol strength, style, occasion, budget — and weigh it together into one specific, honest recommendation, instead of leaving a buyer to reconcile all of that in their own head.

It does not pretend every input it uses is equally certain. Where the evidence is strong — that a price is legally fair, that one beer gives more alcohol per rupee than another — it says so plainly and with real confidence. Where the evidence is thin — what someone actually prefers, beyond what they've explicitly told it — it says that plainly too, and earns more certainty only as real usage gives it reason to.

It is not trying to become everything a beer app could be. It is trying to be right, specifically, about the one recommendation in front of the person holding it — and to be honest, every time, about how sure it actually is.

Anyone building anything for ValueBrew should be able to ask one question of any new idea: does this make the recommendation more honest and more useful, or does it just make the product feel more complete? If it's the second, it isn't ValueBrew, no matter how reasonable it sounds.
