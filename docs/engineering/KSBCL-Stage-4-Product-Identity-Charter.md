# KSBCL Stage 4 — Product Identity Charter

### Not an architecture document. No algorithm, schema, matching key, or implementation appears below. One question only: **what does a canonical product represent inside ValueBrew?** The master pipeline architecture's existing framing (§4.4/§4.5) is treated as one proposal to evaluate, not a starting truth — where it's right, that's shown from first principles, not assumed.

**Status note:** §3 and §5 below identify `supplier_code`'s place in identity as the one question this document could not settle on principle alone. It has since been resolved by product-owner decision — see `KSBCL-Stage-4-Identity-Decision.md`, the single authoritative source. The reasoning below is left intact as the record of why that decision was necessary.

---

## 1. First principles, before looking at KSBCL at all

Strip away the data source entirely. Any retail-comparison product has to answer one question before anything else can be built: **what is the thing a price is attached to?** Get that wrong and every downstream feature — "is this a good price," "is this the same as what I saw yesterday," "what should I try next" — inherits the error silently, because nothing downstream re-derives identity; everything just trusts it.

There are two fundamentally different, both legitimate, answers a product designer could give:

- **A recipe/brand answer**: "Kingfisher Strong" is one thing, regardless of what it's poured from or how much of it there is. This is the mental model a *discovery* experience wants — browsing, recommending, "have you tried this beer."
- **A purchasable-unit answer**: "Kingfisher Strong, 650ml, bottle" is one thing; "Kingfisher Strong, 330ml, can" is a different thing. This is the mental model a *comparison* experience needs — you cannot say a price is fair or unfair without knowing exactly what's being priced.

Neither is "more correct" in the abstract. Which one ValueBrew needs depends entirely on what ValueBrew is actually for.

---

## 2. What ValueBrew's own stated features require

*(Product philosophy / feature reasoning — not derived from the June dataset, derived from the master architecture's own description of what reads `beer_master.csv`, §6.5.)*

Master architecture names four consumers: the recommendation engine, Price Verification, Value Score, and retail comparisons. Testing each against the two models above:

- **Price Verification** — "is this price, on this exact item, correct" — cannot function at recipe grain. It requires knowing the exact size and container in front of the user. **Purchasable-unit grain required.**
- **Retail comparisons** — comparing a price across shops is only meaningful if it's the same exact thing in both places. Mixing a 330ml-can price into a 650ml-bottle comparison isn't a comparison, it's noise. **Purchasable-unit grain required.**
- **Value Score** — needs a price-per-volume computation, which needs an exact size to divide by. The *score* could theoretically be rolled up to a coarser grain later, but its underlying computation is purchasable-unit grain. **Purchasable-unit grain required at the base.**
- **Recommendation engine** — "try this next" naturally reasons at brand/style/taste level. Recommending a 330ml can as a "different experience" from a 650ml bottle of the identical beer would be a strange recommendation. **Recipe grain is the natural fit.**

Three of four stated features fail without purchasable-unit grain. One wants the coarser grain, but isn't broken by having the finer one available underneath it (a recommendation engine can reason over "beers a user has tried," a set easily derived from purchasable-unit rows sharing a brand/style, without needing a separate top-level ID). The reverse isn't true — Price Verification and retail comparisons cannot be *derived* from recipe-grain data once volume/container information has been discarded.

**This is the first principle: identity has to serve the feature that would break without it, not the feature that merely prefers a different grain.**

---

## 3. The generative test

A single question resolves every specific field debate without treating each as its own argument: **is this the smallest unit for which a price comparison is fair and meaningful?**

Applied to each candidate identity component:

- **Volume (`pack_size_ml`)** — clearly yes. A bigger bottle costing more isn't automatically worse value; comparing across sizes without normalizing is exactly the kind of unfair comparison this test exists to prevent.
- **Container (`container_type`)** — yes. A can and a bottle of the identical beer and volume have genuinely different production/distribution costs and are a real choice a shopper makes, not an incidental fact about how KSBCL happened to write the row.
- **Case size (`pack_count`)** — no, cleanly. Buying two boxes of the same cereal isn't a different product from buying one; a wholesale order of 12 vs. 24 units is a *quantity*, and quantity is never product identity in any retail mental model. This isn't a judgment call, it's a category error to include it.
- **Supplier (`supplier_code`)** — genuinely undetermined by the test alone, and this is the one place the test exposes a real fork rather than resolving it. If two suppliers' listings are the identical specification distributed through different regional channels, comparing their prices *is* the fair, meaningful comparison the whole feature exists to surface. If they're materially different products that happen to share a name, comparing them is misleading. The test doesn't fail here — it correctly identifies that the answer depends on a fact this document cannot establish on its own (§5). **Resolved by product-owner decision** — see `KSBCL-Stage-4-Identity-Decision.md`.

---

## 4. What the real data shows, and what it doesn't

*(Every number below is from the real 2026-06 Stage 3 output. Labeled by kind.)*

- **Fact**: 1,714 real included rows collapse to 1,122 distinct purchasable-unit names (brand+style+size+container, before even considering supplier or case size). A further, approximate collapse to ~653 groups occurs if size/pack text is stripped entirely, approximating brand+style-only grouping. Purchasable-unit grain is already meaningfully coarser than raw rows; recipe grain would be roughly half again as coarse as that.
- **Fact**: "Kingfisher Strong Premium Beer 650ml" alone is listed by seven distinct company names — not seven codes for one company — at prices from ₹80.00 to ₹190.00, a 2.4× spread.
- **Fact**: 245 of 315 real multi-supplier product groupings (78%) span genuinely different company names, not regional codes of one brand owner.
- **Business assumption, not confirmed by anything in this dataset**: that these different companies are contract-brewing the identical specification under license (a documented, common practice in Indian beer distribution) rather than producing materially different products that share a brand name. KSBCL's price list carries no recipe, ABV, or quality signal — this cannot be settled by looking at more rows of the same kind of data.
- **Open question the data cannot resolve**: whether a 2.4× price spread on "the same" product is itself informative (a real, meaningful "better deal available elsewhere" signal ValueBrew should surface) or a warning sign that these aren't the same product at all. Both readings are consistent with everything in the dataset.

---

## 5. `supplier_code`, `pack_size_ml`, `pack_count`, `container_type` as consequences, not debates

None of these are independent questions once §1–§3's principle is fixed. Each is just an application of "does this belong in the smallest unit for a fair, meaningful price comparison":

- `pack_size_ml`, `container_type` — **in**, directly, by the test in §3. Not close calls.
- `pack_count` — **out**, directly, by the same test. A quantity, not a product attribute, in every ordinary retail mental model.
- `supplier_code` — **the one component the principle cannot settle alone.** It resolves the instant one factual premise is answered: *are differently-supplied listings of the same name the same specification, or not?* That premise is a business/domain judgment call (or a piece of outside knowledge about Indian contract brewing this document doesn't have authority to assert), not something derivable from more analysis of this dataset. **Resolved by product-owner decision** — see `KSBCL-Stage-4-Identity-Decision.md`.

This is the practical payoff of starting from a principle instead of debating four fields separately: three of the four were never actually in question — they were only *presented* as four parallel debates in earlier drafts of this discussion. There is exactly one open decision, not four.

---

## 6. Reversibility — why this decision, and only this one, has to be made before Stage 4 runs

Not every identity-adjacent decision carries the same cost if it's wrong.

- **Cheap to add later**: a coarser, recipe-grain browsing/recommendation layer sitting *on top of* purchasable-unit identity. It can always be computed after the fact from existing brand/style text — nothing about building it later requires touching or re-deriving anything already committed.
- **Expensive to change later**: the composition of what defines a purchasable unit itself (whether `supplier_code` is in or out). Once real months of data accumulate — mapped item codes, human-confirmed review decisions, and (per the master's own design intent) external enrichment sources joined against these IDs — narrowing the definition later means splitting canonical products that already have real history attached to them; widening it later means merging canonical products that already have independent histories. Both are real data-migration problems, not configuration changes, and both risk breaking whatever already joined against the old grouping.

This is the actual reason this question is worth stopping for before architecture is drafted: getting the *coarse-vs-fine layering* decision wrong costs little; getting the *composition of the fine-grain unit* wrong costs real, accumulated data once Stage 4 has run for real.

---

## Answers to the five questions

1. **What entity should `canonical_product_id` represent?** The smallest unit for which a price comparison is fair and meaningful — a purchasable retail unit (brand + style + volume + container). Not a recipe/brand family; not a wholesale order line.
2. **What mental model will users naturally expect?** Genuinely underdetermined by "naturally expected" alone — both a single product page with size options, and separate listings per exact size, are common, legitimate patterns in real apps. What breaks the tie is §2: three of ValueBrew's four named features cannot function without purchasable-unit precision, so that has to be the base layer regardless of which browsing pattern is chosen on top of it later.
3. **What business capabilities depend on that choice?** Price Verification and retail comparisons directly; Value Score's underlying computation; and, per the master's own stated intent, every future enrichment source, which is designed to join against this exact ID (§10.1) — meaning the cost of getting the grain wrong compounds with every future data source added on top.
4. **Which decisions are reversible, which get expensive?** Adding a coarser grouping layer later: cheap, purely additive. Changing what composes the fine-grain unit after real data has accumulated: expensive, a genuine migration, not a config change (§6).
5. **`supplier_code`/`pack_size_ml`/`pack_count`/`container_type`** — all four resolve as direct consequences of one test (§3, §5), not four separate debates. Three resolve cleanly. One — `supplier_code` — depended on a factual premise about Indian contract-brewing practice that this document did not have the authority or the data to settle; it has since been resolved by product-owner decision (see `KSBCL-Stage-4-Identity-Decision.md`).

---

## The smallest set of principles

1. A canonical product is the smallest unit for which a price comparison is fair and meaningful — not a recipe, not a wholesale order line.
2. Identity serves the feature that breaks without it, not the feature that merely prefers a coarser view.
3. Any field is in or out of identity by asking, concretely: does varying this field, alone, change what's fair to compare? Volume and container pass; order quantity fails; supplier is the one open case.
4. A coarser browsing/recommendation layer can always be added later at near-zero cost — it should never be allowed to complicate or delay the fine-grain decision, which cannot be added or corrected cheaply once real data accumulates.
5. Everything above resolves except one question: whether differently-supplied listings of the same name are the same specification. That was the one decision Stage 4's architecture was waiting on — it has since been made (see `KSBCL-Stage-4-Identity-Decision.md`).

No architecture is proposed here. With the one open question in §5/§6 now settled, Stage 4's architecture follows from principles 1–4 almost without further debate.
