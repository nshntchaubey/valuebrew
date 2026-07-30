# ValueBrew — Beer Knowledge Model
### The canonical domain and knowledge architecture. Derived entirely from the frozen Behavioral Hypothesis Model, Product Definition Document v2, Decision Engine Model, and Recommendation Framework. Not a schema, not an implementation design — the conceptual knowledge this product is entitled to hold.

---

## 1. Domain Model

**Beer** — the conceptual product identity (a name, a brand, a style). Why it exists: it's the thing a person actually refers to when stating a preference or an anchor. Relates to: groups one or more SKUs; carries Brand and Style as identifying facts.

**Brand / Brewery** — who makes it. Why it exists: supports brand-preference inputs and the model's own evidenced finding that price can function as a quality signal tied to brand. Relates to: groups Beers under a producer identity.

**Beer Style** — lager, wheat, stout, and so on. Why it exists: supports the Strong Preference "preferred style" input and the thinner-evidenced occasion-fit reasoning. Relates to: classifies Beers; anchors the Style Benchmark below.

**SKU** — a specific size, package, and ABV variant of a Beer. This is the atomic unit the rest of the model reasons over, not the Beer itself — price, alcohol content, and size are all facts about a specific SKU, not a brand or beer name in the abstract. Why it exists: it's the actual thing a person buys, and the actual thing Legal Price Verification and Alcohol-Adjusted Value Comparison attach to. Relates to: belongs to one Beer; carries Legal Price, ABV, and size as its core attributes.

**Legal / Reference Price** — the government-published price for a specific SKU. Why it exists: the single highest-confidence capability in the whole canon depends entirely on this existing and staying current. Relates to: attaches to SKU; sourced externally from regulatory publication, not from the product itself.

**Observed / Charged Price** — what a person reports having been charged, in a specific transaction. Why it exists: without it, there's nothing to verify against the Legal Price. Relates to: exists only in the context of one interaction — it is not catalog knowledge about the SKU, it's a transient fact about one purchase.

**Derived Value Profile** — the alcohol-adjusted value and related computed figures for a SKU. Why it exists: this is the entire mechanism behind the second-highest-confidence capability. Relates to: computed from a SKU's price and ABV; compared against the Style Benchmark to produce relative standing.

**Style Benchmark** — the reference distribution of value figures across SKUs within one Style. Why it exists: a single SKU's value figure means little without something to compare it to — this is what makes "better value than typical for this style" a meaningful statement rather than an isolated number. Relates to: aggregates over all SKUs sharing a Style.

**User Preference / Constraint Set** — budget, preferred style, preferred strength, preferred size, preferred brand, occasion, stated exclusions. Why it exists: this is what the Recommendation Framework's Hard Constraint, Strong Preference, and Soft Preference tiers actually operate on. Relates to: exists only for the duration of one interaction, not as permanent knowledge about a beer.

**Recommendation** — the produced artifact tying together the SKU(s) selected, the reasoning that selected them, and the confidence structure behind that reasoning. Why it exists: it's the actual output the rest of this model serves. Relates to: references one or more SKUs, the Preference Set that shaped it, and the specific Hard/Strong/Soft factors that contributed.

**Deliberately excluded from this domain model:** a Store or Retailer entity as a first-class concept. The frozen canon found no evidence of legal, store-to-store price variation in Karnataka — only illegal overcharging against a single legal reference price. Modeling stores as a rich comparison entity would misrepresent what the evidence actually supports; the verification delta below handles the real, evidenced problem without needing one.

---

## 2. Beer Attribute Taxonomy

**Identity** — name, brand, style label. Objective, Verified once catalogued. Static. Directly influences recommendations, through matching against stated brand and style preferences.

**Regulatory** — legal/reference price, any duty classification affecting it. Objective, Verified, sourced externally. **Dynamic, not static** — the frozen model documents a real, repeated history of excise changes, so this attribute must be treated as needing periodic refresh, never assumed permanent. Directly influences recommendations — this is the core input to the highest-confidence capability in the canon.

**Physical** — alcohol content, size/volume, package format. Objective, Verified, manufacturer-declared. Static per SKU, though a SKU should be treated as a point-in-time fact, not an eternal one, since reformulation is possible. Directly influences recommendations — the core input to the second-highest-confidence capability.

**Nutritional** — calories. Objective, Verified. Static. Worth stating plainly: nothing in the frozen model's own decision-factor research evidences calories as something that actually drives a purchase decision — this attribute exists for explanation and completeness, not because it's been shown to influence recommendation weight.

**Commercial** — observed/charged price. Subjective in the sense that it's user-reported and not independently verifiable by the engine. Dynamic and transaction-specific — this is not catalog knowledge stored about a SKU at all, it exists only within one verification interaction.

**Availability** — whether a SKU is currently obtainable. Explicitly not pursued as catalog knowledge. This ties directly to the Fallback JTBD, which the Product Definition Document already states "should probably never exist" as a dedicated capability — building real availability tracking would mean building for a job the canon never evidenced.

**Sensory** — flavor, tasting notes, quality descriptors. This category exists in the taxonomy for structural completeness and is **deliberately empty**. Every reference to taste or quality anywhere in the frozen canon is flagged as thin, single-source, or entirely unevidenced. Populating this category would mean the product claiming certainty it doesn't have — a direct violation of the Recommendation Framework's ninth principle.

**Derived Metrics** — alcohol-adjusted value, cost per litre, value percentile within style. Computed, never independently stored or hand-entered. Dynamic — recalculated whenever the Regulatory or Physical facts they're built from change. Directly influences recommendations; this is the literal mechanism of the value-comparison capability.

---

## 3. Objective vs Subjective Knowledge

**Verified Facts** — Beer identity, legal/reference price, alcohol content, size, package format. Treatment: these are ground truth. They should be refreshed on a cycle matched to their real-world volatility — price especially, given the documented pattern of repeated regulatory change — and never manually overridden by inference or crowd input.

**Computed Facts** — alcohol-adjusted value, cost per litre, value percentile, the verification delta between charged and legal price. Treatment: always derived transparently from Verified Facts, recalculated whenever those facts change, never hand-entered as if they were independent data. Despite being "derived" rather than directly given, these should be presented with the same high confidence as the Verified Facts they're built from — the arithmetic itself carries no uncertainty, even though the number is computed rather than looked up.

**Human Judgment** — any occasion-fit tagging, any future taste or quality assessment, any subjective classification (whether something counts as "craft," for instance). Treatment: this is the lowest-confidence category in the model, and must always be visibly labeled as interpretation, never presented with the same authority as a Verified or Computed Fact. Right now, this category has almost nothing populated in it, and that's intentional, not incomplete.

---

## 4. Derived Knowledge

**Alcohol-adjusted value** — a figure combining price and alcohol content to represent cost per unit of alcohol. Why it exists: it's the entire mechanism behind the model's second-highest-confidence capability, and it doesn't need to be stored, only computed whenever price or ABV are known.

**Cost per litre / cost per ml** — the plainer, unadjusted unit price. Why it exists: a simpler secondary fact worth showing alongside the alcohol-adjusted figure for explanation, without asserting it's the primary basis for a recommendation.

**Verification delta** — whether an observed/charged price sits at, above, or below the legal reference price. Why it exists: this is the actual computation underlying Price Verification, the single most confidently evidenced capability in the entire canon.

**Value percentile / relative standing within style** — where a SKU's alcohol-adjusted value sits relative to the Style Benchmark. Why it exists: a raw value figure means little in isolation; this is what makes "better value than typical for this style" a meaningful, explainable statement rather than an arbitrary number.

None of these require inventing new logic beyond what's already established elsewhere in the canon — they're named here only as concepts the knowledge model must support, not as new formulas.

---

## 5. Knowledge Required for V1

**Essential:** Beer and SKU identity (name, brand, style); legal/reference price per SKU; alcohol content per SKU; size and package format per SKU; the verification delta; alcohol-adjusted value. Why: these directly and only support the two capabilities the Product Definition Document names as Essential for V1 — Legal Price Verification and Alcohol-Adjusted Value Comparison.

**Important:** cost per litre, as a simpler explanatory companion figure; the Style Benchmark and value percentile, needed to support Trade-off Explanation and richer comparison; calories, for explanation and completeness even though it isn't evidenced to drive recommendation weight.

**Future:** occasion-tag associations between Style and context, held pending real usage per the Product Definition Document's deferral of richer occasion-fit; any lightweight feedback signal that might eventually inform preference-matching, held pending evidence it's worth building; brand-level trust or reputation signals, which don't exist anywhere in the frozen canon yet.

---

## 6. Knowledge Boundaries

**Subjective tasting notes or flavor descriptions** — excluded; the Sensory category is empty by design, given the canon's consistent finding that taste-based capability is the least evidenced area in the entire model.

**Crowdsourced ratings** — excluded as an active knowledge type for V1, consistent with the Product Definition Document's explicit boundary against a full social or ratings platform.

**AI-generated flavor descriptions** — excluded, and worth naming specifically: generating a flavor description would mean asserting sensory knowledge the canon has zero evidence base for, a direct violation of the Recommendation Framework's principle against claiming more certainty than the evidence supports.

**Inferred popularity** — excluded, consistent with the Decision Engine Model's explicit deferral of all inferred contextual and behavioral signals.

**Real-time, store-level availability** — excluded, tied directly to the Fallback JTBD's rejected status.

**Store-specific pricing as catalog knowledge** — excluded; the frozen research found no evidence of legal store-to-store price variation, only illegal overcharging against a single legal reference, which the verification delta already handles without needing a store-comparison concept.

---

## 7. Knowledge Evolution

**What may be added later:** crowd-verified reports of actual charged prices, if a lightweight feedback mechanism is ever built; richer occasion-tag associations; carefully evidenced taste or preference data, but only once real usage — not assumption — justifies it, per the Product Definition Document's own language that preference-learning must be earned, not built ahead of evidence.

**What should never replace a Verified Fact:** any future crowd, inferred, or subjective knowledge must sit *alongside* Verified Facts, never overwrite them. If crowd-reported prices ever diverge from the government's published legal price, that divergence should be surfaced as an additional, clearly labeled signal — never allowed to quietly become the new reference truth in place of the actual legal figure.

**How future learning coexists with objective knowledge:** always additively, always visibly separated — a direct extension, into the knowledge layer itself, of the Recommendation Framework's rule that high-confidence facts and low-confidence inferences must never be merged into one unlabeled judgment.

---

## 8. Beer Knowledge Principles

1. Every attribute must trace to Recommendation, Explanation, User decision-making, or Future learning — nothing exists because it's merely interesting.
2. Verified Facts are the highest-authority layer and must never be silently overwritten by inference, crowd input, or computation.
3. Computed Facts must always be derived transparently from Verified Facts, never hand-entered or asserted independently.
4. Human Judgment must always be labeled as such, never presented with the confidence of a Verified or Computed Fact.
5. Regulatory facts must be treated as dynamic, refreshed on a real cycle, never assumed permanent — the canon's own history of repeated change makes this non-negotiable.
6. The Sensory category remains empty until real usage evidence justifies populating it. Its emptiness is a decision, not a gap to be filled reflexively.
7. Availability and store-level pricing are not first-class catalog knowledge, consistent with the rejected Fallback JTBD and the absence of evidence for legal store-level price variation.
8. The SKU, not the Beer or Brand, is the atomic unit that price, alcohol content, and size attach to — never assume uniformity across a brand's full lineup.
9. Every derived metric must be recomputed whenever its underlying Verified Facts change, never cached as if permanent.
10. No attribute should be added to serve a capability the Recommendation Framework or Decision Engine Model doesn't already call for.
11. New categories of knowledge may be added over time, but only ever alongside existing verified knowledge, never blended into it without clear, visible separation.
12. Crowd-sourced or inferred knowledge, whenever it's eventually added, must be presented as an additional signal, never a silent replacement for a Verified Fact.
13. Knowledge that exists purely for explanation — calories, for instance — must be labeled as such, never mistaken for something proven to drive recommendation weight.
14. For every attribute in this model, it must be possible to answer which specific capability it serves. An attribute with no answer to that question does not belong here.
15. Expanding this knowledge model must never require reinterpreting or weakening any of the four frozen canonical documents it exists to support.
