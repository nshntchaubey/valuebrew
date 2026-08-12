# ValueBrew — Catalog Specification 1.0

*What ValueBrew knows about a beer, why, and where it comes from — not a schema. Built from Beer Knowledge Model 2.0, Domain Model 1.0, the KSBCL pipeline's real data realities, the market research corpus's confirmed gaps, and Generation 1's own catalog fields. Every domain is classified into exactly one of five categories: Launch Critical, Launch Recommended, Product Enrichment, Trust & Governance, Future Expansion.*

---

## Part 1 — Launch Critical Domains

### Identity
**Why:** every other domain attaches to a specific, correctly-resolved real thing — get this wrong and everything else is misattributed. **Source of truth:** KSBCL Stage 3/4's normalization and canonical identity resolution at pipeline scale; for the launch catalog, resolved directly by hand against the KSBCL list and Madhuloka. **Confidence:** Verified Fact once resolved, or Human Judgment for a manually-confirmed ambiguous match. **Obtained:** computation (pipeline) or direct research (launch). **Update frequency:** durable once resolved. **Experiences:** all five. **Reasoning surfaces:** all five — nothing reasons about anything until identity is correct. **When missing:** the SKU simply isn't in the catalog — there's no "identity: null" state, only "not yet resolved." **Persistence:** persistent Reference Data.

### Packaging (size, container type)
**Why:** the Product Identity Charter's own test — "the smallest unit for which a price comparison is fair and meaningful" — depends on knowing exact size and container; get this wrong and a comparison is unfair by construction. **Source of truth:** KSBCL's extraction grammar; direct label reading at launch. **Confidence:** Verified/Computed. **Obtained:** computation or direct observation. **Update frequency:** durable — a packaging change is a new SKU, not an update to an old one. **Experiences:** all five (it's part of what makes a SKU a SKU). **Reasoning:** Recommendation and Comparison's candidate distinction; Price Verification's implicit size-specific legal price. **When missing:** the SKU isn't considered resolved — folds back to Identity's rule. **Persistence:** persistent.

### Style
**Why:** the reference group everything comparative depends on, and Recommendation's one optional Strong Preference input. **Source of truth:** **not currently produced by the KSBCL pipeline at all** — this is a genuine, confirmed insufficiency (already flagged in Domain Model 1.0). For both the pipeline's future scale-up and the launch catalog, Style is a curation decision, not an automated extraction. **Confidence:** Curated Knowledge — a categorization judgment, not an extracted fact. **Obtained:** manual assignment against a fixed, small style vocabulary. **Update frequency:** durable. **Experiences:** Recommendation, Beer Detail, Comparison. **Reasoning:** Recommendation's style filter; Style Benchmark's grouping. **When missing:** the SKU can still exist and be recommended on price/value alone — Style is required for the Style Standing feature specifically, not for basic function. **Persistence:** persistent.

### ABV / Alcohol Content
**Why:** the single fact that makes "value" mean anything — without it, ValueBrew is indistinguishable from a plain price list. **Source of truth:** the physical label. **Confirmed, exhaustively, by the market research:** no brewery site, retailer, or barcode API reliably publishes this for the Karnataka catalog — **this is the sharpest insufficiency in the entire specification.** **Confidence:** Verified Fact only — no estimated-ABV tier should ever exist. **Obtained:** manual label photography/OCR. **Update frequency:** periodic re-check for genuine reformulation risk, not a one-time capture. **Experiences:** all five, at least indirectly (it's the base of Value Metrics). **Reasoning:** Recommendation's entire ranking; Comparison's per-candidate facts. **When missing:** the SKU exists in the catalog but is **not eligible for value-based ranking** — this is the actual, practical gating rule for "launch-ready," restated here as a catalog policy, not just an engineering concern. **Persistence:** persistent.

### Legal Price
**Why:** the fact that makes Price Verification possible and the price half of every Value Metric. **Source of truth:** KSBCL's official government price list. **Confidence:** the single highest-confidence fact in the entire catalog — always Verified. **Obtained:** government data (pipeline), or direct transcription from the same government source for the launch catalog. **Update frequency:** monthly, matching KSBCL's own publication cadence. **Experiences:** Price Verification (primary), Recommendation (budget filtering), Beer Detail, Comparison. **Reasoning:** Price Verification's entire classification; Recommendation's Hard Constraint gate. **When missing:** a SKU with no confirmed Legal Price cannot support Price Verification and shouldn't be shown as recommendable on value grounds either. **Persistence:** persistent.

### Availability
**Why:** knowledge without this is trivia — a person needs to know something's actually obtainable. **Source of truth:** KSBCL's item status (LIVE/DELISTED, sourced from published-listing presence); direct shelf confirmation at launch. **Confidence:** binary, Verified. **Obtained:** computed from source presence, or direct observation. **Update frequency:** monthly at pipeline scale; at each shelf-walk for the launch catalog. **Experiences:** implicitly gates all five. **Reasoning:** every recommendation implicitly assumes availability; nothing should surface a delisted SKU as a live pick. **When missing:** treat as unavailable, never assume presence by default. **Persistence:** persistent.

### Value Metrics (cost/litre, cost/ml-of-alcohol)
**Why:** this is the product's core differentiator made concrete. **Source of truth:** computed, not separately sourced — entirely derived from Legal Price and ABV. **Confidence:** Computed Fact, inheriting the weaker of its two inputs' confidence — if ABV is missing, this doesn't exist either, per the ABV domain's own gating rule. **Obtained:** computation, automatic the moment its two inputs exist. **Update frequency:** recomputed whenever price or ABV changes — no independent freshness of its own. **Experiences:** Recommendation, Beer Detail, Comparison. **Reasoning:** Recommendation's entire ranking logic. **When missing:** the SKU is excluded from value-based reasoning, not shown with an invented or estimated figure. **Persistence:** Computed View, not independently persisted.

---

## Part 2 — Launch Recommended Domains

### Brewery
**Why:** a fact people recognize a beer by, and part of basic identity display. **Source of truth:** KSBCL's supplier legal entity name — **with a real, confirmed caveat worth stating plainly: KSBCL's "supplier" is the entity that supplied a listing, which is not always the same as the entity that actually brewed the product** (contract-brewing is an explicitly unconfirmed business question in the KSBCL Stage 4 documents). For retailer-sourced (non-KSBCL) rows, the market research directly confirms brewery attribution is frequently blank or inferred with a caveat. **Confidence:** High for KSBCL-sourced legal entity names; Medium/Low for retailer-inferred attributions, honestly labeled as such. **Obtained:** government data, cross-walked against brand-owner pages where gaps exist. **Update frequency:** durable. **Experiences:** Beer Detail primarily. **Reasoning:** minimal — not a ranking input today. **When missing:** gracefully omit rather than guess. **Persistence:** persistent.

### Style Benchmark
**Why:** the reference distribution that makes "typical for this style" a real, computable claim. **Source of truth:** computed from the full set of catalogued SKUs sharing a Style — never independently sourced. **Confidence:** Computed Fact, but only as reliable as its sample size; a thin style should never produce a benchmark presented with the same weight as a well-populated one. **Obtained:** computation. **Update frequency:** recomputed whenever underlying data changes. **Experiences:** Beer Detail, Comparison. **Reasoning:** Style Standing's entire basis. **When missing (thin sample):** gracefully omitted, never a low-confidence guess dressed as a real comparison. **Persistence:** Derived Knowledge, not independently persisted.
**Recovered insight, not existing canon:** the current shipped model uses only a median split, having rejected a fuller `p25`/`p50`/`p75` percentile design as "uncited" during its own review — but that richer structure is exactly what Generation 1's original data model specified, for exactly this purpose. This document, following Beer Knowledge Model 2.0, recommends reintroducing it once real data volume supports it — not required for launch.

### Freshness
**Why:** a fact with no age attached is pretending to be more permanent than it is. **Source of truth:** the `run_month`/`effective_date` fields already tracked through the KSBCL pipeline; the collection date for any manually-gathered fact. **Confidence:** not applicable — freshness is orthogonal to confidence, a fact can be old and still fully Verified. **Obtained:** automatically tracked at pipeline scale; must be deliberately recorded at manual-collection time (cheap, easy to skip). **Update frequency:** continuous — it's the "as of" pointer for every other domain. **Experiences:** implicitly all five; would be explicitly user-visible if the recovered Generation 1 provenance-strip idea is adopted (see Part 6). **Reasoning:** none directly today, but should gate any future "how confident am I in this price" display. **When missing:** treat any undated fact as effectively unverifiable for freshness purposes, not as automatically current. **Persistence:** persistent metadata attached to every other domain's facts.
**Recovered insight, not existing canon:** Generation 1 surfaced this directly to users ("price confirmed 2 days ago"); Generation 2 tracks it internally but has never shown it. **This domain is also, per the Evolution of ValueBrew document, the second time the team has correctly identified something as "cheap and important" and then not built it — worth not repeating a third time, even at launch scale, where simply recording a collection date costs nothing.**

---

## Part 3 — Trust & Governance Domains

### Confidence / Provenance (cross-cutting, not a per-beer fact)
**Why:** without an explicit tier attached to every other domain's facts, everything looks equally certain, which is dishonest whenever it isn't. **Source of truth:** the canonical Beer Knowledge Model's own three-tier classification, applied consistently. **Confidence:** this domain *is* the confidence classification — it doesn't itself need one. **Obtained:** assigned at the moment any other fact is captured, whether by pipeline or manual collection. **Update frequency:** static per fact, unless the fact itself is re-verified. **Experiences:** all five, structurally. **Reasoning:** the discipline underneath every reasoning surface in Decision Engine 2.0. **When missing:** never allowed to be missing — every fact must carry a tier, even at launch scale with a tiny hand-built catalog.

### Regulatory Metadata (jurisdiction-level, not per-beer)
**Why:** age-gating requirements and advertising-language constraints that the product's own copy and access rules must satisfy — this isn't a fact about a beer, it's a fact about the jurisdiction the product operates in. **Source of truth:** **real legal research that already exists** — Generation 1's own Phase 1 PRD, Section 2.5, already documented the relevant findings (alcohol cannot be sold online in most of India, Google Play's alcohol-content policy, state-by-state variance). **Confidence:** Curated Knowledge, dated to the project's founding, requiring re-verification, not fresh research from zero (already flagged as a correction to this session's own earlier strategy work in Evolution of ValueBrew). **Obtained:** legal research, re-verified periodically. **Update frequency:** low, but genuinely non-zero — regulation can change. **Experiences:** governs Home's age-gate, and the Lexicon's own forbidden-terminology rules across every screen. **Reasoning:** not part of Decision Engine 2.0's per-beer reasoning at all — this is a single, app-wide record, not a per-SKU field.
**Recovered insight, not existing canon:** Generation 1's data model proposed a versioned, per-state `regulatory_flag`/`MRP_regime` — never built, since the product has stayed Karnataka-only. Worth preserving as a real, previously-modeled idea if the product ever expands beyond one state, rather than rediscovering it.

### External Identifiers (GTIN / Barcode)
Fully specified in Beer Knowledge Model 2.0 (Domain 8) and Domain Model 1.0. Category: Trust & Governance in the sense that it would be an *external* verification cross-reference, but its actual timing is **Future Expansion** — the reserved fields stay empty at launch, exactly as the KSBCL architecture already intends. No source of truth exists today with adequate coverage for this catalog.

### Price History (already collected, not yet surfaced)
**Why it matters as a Trust & Governance concern:** this is the pipeline's own audit trail (`beer_price_history.csv`), append-only, already accumulating — it exists today, entirely inside the pipeline, with no consuming experience. **Source of truth:** KSBCL Stage 5, exclusively. **Confidence:** Verified, inheriting Legal Price's own strength. **Obtained:** automatic pipeline output. **Update frequency:** every run, append-only, never overwritten. **Experiences:** none today. **Reasoning:** none today — pure future raw material. **When missing:** not applicable at pipeline scale (it's already being collected); simply absent for the hand-built launch catalog, which has no history to draw on yet by definition. **Persistence:** persistent, permanent, accumulating.

### Verification History — **a new proposal, explicitly not existing canon**
**Why it might exist:** an aggregate, anonymous signal — "what fraction of price checks across the catalog this month found a shelf price above the legal reference" — is a genuine trust-and-governance signal distinct from any individual verification, and compatible with the no-accounts principle specifically *because* it would be aggregate, never per-person. **Source of truth:** would be computed from Verification Results, if those were ever logged in aggregate (they currently aren't — Verification Result is explicitly ephemeral and non-persisted per Domain Model 1.0). **Confidence:** would be Computed. **Obtained:** would require a deliberate, new decision to aggregate anonymized verification outcomes — not a natural extension of anything currently built. **Update frequency:** would be continuous if built. **Experiences:** none today — this is a proposal, not a specification of something that exists. **Reasoning:** none today. **When missing:** simply doesn't exist — flagged here only because the user's own list of examples named it, and honesty requires saying plainly that this is new territory, not recovered or existing canon, and would need its own Product Decision (specifically: does aggregating verification outcomes, even anonymized, sit comfortably with the product's restraint principles, or does it risk becoming a "gotcha" metric the product was never designed to be) before being built.

---

## Part 4 — Product Enrichment Domains (Grounded, Not Required for Launch)

### Food Pairing
**Recovered insight, not existing canon at the product-decision level, but a real, cited Generation 1 idea:** Generation 1's own architecture document names this explicitly as a designed Extension Point — "once pairing data exists in the catalog schema, this is a new RecommendationReason value plus one new SimilarityStrategy implementation... adding a dimension never requires touching an existing strategy." Nothing in Gen 2 principles conflicts with this. **Source of truth:** would require curated content, not extractable from any current pipeline source. **Confidence:** Curated Knowledge. **Category:** Product Enrichment, genuinely future, but grounded in a real prior design rather than invented fresh here.

### Calories
Present in Generation 1's model, absent from current canon entirely, already flagged as a legitimate reintroduction candidate in Beer Knowledge Model 2.0. Same sourcing constraint as ABV (label-dependent, no automated source), same confidence rule (Verified only, never estimated). **Category:** Product Enrichment.

---

## Part 5 — Future Expansion: Sensory & Narrative Knowledge (Honestly Ungrounded)

**Flavor Profile, Aroma, Body, Bitterness, Sweetness, Ingredients, Awards, Brewery Story, Images** — none of these appear anywhere in the canonical architecture, the Beer Knowledge Model, Domain Model 1.0, Generation 1's data model, or the KSBCL pipeline. They are named here only because they appeared as illustrative examples in the request that produced this document, and honesty requires saying plainly: **there is no source of truth, no confidence rule, and no existing Product Decision behind any of them.** Including full ten-point specifications for these would manufacture false specificity about things the product has never actually decided to model.

What can be said honestly: any of these, if pursued, would almost certainly require Curated Knowledge (brewery-provided or manually written, not extractable), would sit at Human Judgment or Curated confidence at best, and — per the product's own forbidden-terminology discipline — would need careful review against the Lexicon before any of them risk sounding like a disguised rating (a "flavor score," for instance, would be exactly the kind of thing the Lexicon already forbids). **Images** specifically is the one item in this group plausibly needed for basic usability regardless of any deeper enrichment ambition, and deserves an explicit, small Product Decision of its own before launch, rather than silent inclusion or silent omission.

None of this cluster should be treated as roadmapped. It's named, not specified.

---

## Part 6 — Session Information (Not Catalog Data, Named for Completeness)

### Charged Price
Not part of the catalog at all — this is Session Information, existing entirely outside the catalog's boundary. Reported by a person, for one Price Verification, with no repository or storage adapter, discarded the moment the session ends. Included here only because it was named in the original list of examples; it is deliberately, permanently excluded from the catalog itself (see Part 8).

---

## Part 7 — Complete Catalog Capability Matrix

| Domain | Recommendation | Beer Detail | Price Verification | Comparison* | Search/Browse* |
|---|---|---|---|---|---|
| Identity | ✅ | ✅ | ✅ | ✅ | ✅ |
| Packaging | ✅ | ✅ | ✅ (implicit) | ✅ | ✅ |
| Style | ✅ (optional) | ✅ | — | ✅ | — |
| ABV | ✅ | ✅ | — | ✅ | — |
| Legal Price | ✅ (budget filter) | ✅ | ✅ | ✅ | — |
| Availability | ✅ (implicit) | ✅ | — | ✅ | ✅ |
| Value Metrics | ✅ | ✅ | — | ✅ | — |
| Brewery | — | ✅ | — | ✅ (minor) | — |
| Style Benchmark | — | ✅ | — | ✅ | — |
| Freshness | — | (recommended) | (recommended) | — | — |
| Confidence/Provenance | ✅ | ✅ | ✅ | ✅ | — |
| Regulatory Metadata | app-wide | app-wide | app-wide | app-wide | app-wide |
| GTIN | — | — | — | — | (future, if barcode-scan built) |
| Food Pairing | (future) | (future) | — | — | — |

*Comparison and Search/Browse are specified/unbuilt and partially unbuilt respectively — their columns reflect what the specifications already require, not current shipped behavior.

---

## Part 8 — Launch-Minimum Catalog Specification

For a SKU to count as launch-ready, all of the following must be true, concretely and checkably:

1. Identity resolved — brand, style category assigned, size and container confirmed.
2. Legal Price present, real, and dated.
3. ABV present and confirmed from a physical label — no exceptions, no estimates.
4. Availability confirmed at time of collection (genuinely on-shelf or on the government list, not carried over from stale research).
5. Every fact above carries an honest confidence tier and a collection date, however small the catalog is — this is the discipline the Evolution document found has been skipped twice already.
6. Brewery and Style Benchmark are **not** required for launch-readiness — both degrade gracefully by design, and requiring them would block launch on domains the product is explicitly built to tolerate gaps in.

A launch catalog of ~100–150 SKUs meeting all six conditions is sufficient. A larger catalog missing condition 3 for even one SKU is not launch-ready for that SKU — it can exist in the catalog, but must not be surfaced in value-based reasoning until ABV is confirmed.

---

## Part 9 — Version 2 Enrichment Roadmap

In priority order, each grounded in an already-identified real need, not invented fresh:

1. **Scale identity resolution and price data via the automated KSBCL pipeline**, once its known defect is fixed — the natural next step once the hand-built launch catalog has validated demand.
2. **Systematic ABV/label photography pass** beyond the launch set — still the one domain with no automation path; this stays manual, just at greater volume.
3. **Surfaced freshness** — the recovered Generation 1 idea, made visible in Beer Detail and Price Verification, not just tracked internally.
4. **Richer Style Benchmark** — reintroducing the `p25`/`p50`/`p75` structure once data volume supports it.
5. **Brewery attribution cleanup** — cross-walking retailer-sourced rows against KSBCL's own supplier data to close the confirmed accuracy gap.
6. **GTIN/external identifiers** — pursued only if a real barcode-scan capability or external data partnership materializes; the seam stays reserved and empty until then.
7. **Food Pairing** — the one genuinely grounded sensory-adjacent extension, per Generation 1's own cited design, still requiring a real Product Decision to prioritize.
8. **Regulatory Metadata generalization** — versioned, per-state, only if the product ever expands beyond Karnataka.
9. **Verification History (aggregate)** — the new proposal named in Part 3, only after its own Product Decision about whether it fits the product's restraint principles.
10. **Sensory/narrative knowledge** — deliberately last, and deliberately unscoped, pending a Product Decision this document does not make.

---

## Part 10 — Permanent Exclusions

Fields that should never exist in ValueBrew, and why, restated here specifically as catalog policy rather than only as entities in Domain Model 1.0:

- **A user-level rating or review score** — permanently incompatible with the Lexicon's forbidden-terminology rule at the data-model level, not just the UI level.
- **Personal purchase history or a per-user decision log** — requires a User entity that doesn't exist and won't, per the founding no-accounts decision.
- **Store or precise-location-level pricing** — Generation 1 proposed and built toward this; cut once, never revived; Availability stops at channel (retail vs. duty-free), never resolves to a coordinate.
- **A trust score or contributor reputation field** — depends on the crowdsourced-submission apparatus that was rejected twice, independently, by two different planning processes.
- **An inferred taste or preference profile** — a direct, permanent reversal preserved from Generation 1's own "personalize from behavior" principle, which the canonical ADR explicitly rejects.
- **An unmoderated, unattributed price with no provenance** — every price in this catalog, whether government-sourced or manually collected, must carry a confidence tier and a collection date; a price with neither should never be allowed into the catalog at all, regardless of how it was obtained.
- **Any estimated or computed ABV** — the one fact in this entire specification that must always be Verified or absent, never interpolated, never inherited from a similar product, under any future pressure to fill a gap faster.
