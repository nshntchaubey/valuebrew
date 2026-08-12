# Beer Knowledge Model 2.0

*What ValueBrew must actually know to deliver the experience described in `THE-VALUEBREW-EXPERIENCE.md` — organized by domain, not by field. Not a schema. Not a product redesign. Built from the canonical Beer Knowledge Model, the KSBCL pipeline's real data realities, Generation 1's original data model, and the Product Definition's seven knowledge categories, reconciled into one definitive model.*

---

## 1. Identity Knowledge

**Why it exists:** everything else in this model attaches to a specific, correctly-resolved real thing. Get this wrong and every other domain's facts get misattributed to the wrong product.
**Product moments:** Home's Anchor-Known routing (once built), Beer Detail's "what am I looking at," Recommendation's candidate set, Price Verification's exact-SKU binding, Comparison's named candidates.
**Source of truth:** the KSBCL pipeline's normalization (Stage 3) and canonical identity resolution (Stage 4) — the matching key is brand/style + pack size + container type, with `supplier_code` deliberately excluded per the recorded Identity Decision.
**Confidence representation:** the existing `match_confidence` tiers (`deterministic_high` / `manual_confirmed` / `unreviewed`) map directly to Verified-tier display — never surfaced to a user as a number.
**Freshness representation:** `first_seen_run_month` / `last_seen_run_month` — identity, once resolved, is durable; freshness here means "still active," not "recently changed."
**Must never infer:** two similarly-named listings are never assumed to be the same product without an exact key match — the asymmetric-risk default (false split over false merge) governs this domain more than any other.
**Can be computed:** name normalization and pack-size/container extraction are fully deterministic, code-computed facts from raw text.
**Requires manual enrichment:** resolving genuinely ambiguous multi-candidate matches (the `ambiguous_key_multiple_candidates` review queue) requires a human decision.
**Belongs in the launch catalog:** identity resolved directly, by hand, for the ~100–150 launch SKUs — this doesn't need the automated pipeline to be trustworthy at this scale.
**Belongs in future enrichment:** scaling to the full KSBCL catalog via the automated pipeline once its known defect is fixed; eventually a coarser "product family" grouping layer for browsing, explicitly never redefining canonical identity itself — a seam the KSBCL architecture already names but never builds.

---

## 2. Composition Knowledge

**Why it exists:** this is the fact that makes "value" mean anything. Without ABV, cost-per-ml-of-alcohol can't be computed, and the entire product collapses into "just a price list" — indistinguishable from any retailer's website.
**Product moments:** Recommendation's value ranking, Beer Detail's facts row, Comparison's per-candidate facts, every Value Score shown anywhere.
**Source of truth:** the physical label. Confirmed, exhaustively, by the market research corpus — no brewery site, no retailer, and no barcode API reliably publishes ABV for the Karnataka catalog.
**Confidence representation:** binary in practice — confirmed-from-a-physical-label (Verified), or absent (null). No "estimated ABV" tier should ever exist; an estimate here is precisely the kind of invented fact the entire project's discipline forbids.
**Freshness representation:** the date of the label confirmation. ABV rarely changes for an established SKU, but reformulation is real, which is exactly why the canon already classifies Physical facts as needing periodic re-checking, not one-time capture.
**Must never infer:** never estimate ABV from a style's typical range, never carry an ABV over from a similarly-named product, never treat "most lagers are about 5%" as a substitute for a confirmed number.
**Can be computed:** derived facts (cost-per-ml-alcohol) are computed once ABV is known — ABV itself is never computed, only observed.
**Requires manual enrichment:** entirely. This is the one domain in the whole model that is 100% manual-collection-dependent today.
**Belongs in the launch catalog:** a confirmed ABV is the actual gating criterion for "launch-ready" — a SKU without one shouldn't be eligible for value-based recommendation, not just missing a nice-to-have field.
**Belongs in future enrichment:** a systematic label-photography pass beyond the launch set; a possible future brewery-direct data relationship (the only plausible path beyond manual collection, per the market research); calories as a lower-priority secondary fact, same sourcing constraint.

---

## 3. Economic Knowledge

**Why it exists:** the two numbers that make Price Verification possible, and the price half of every Value Score.
**Product moments:** Price Verification's entire reason to exist; Recommendation's Hard Constraint filtering; Beer Detail's Legal Price display; Value Score everywhere.
**Source of truth:** **Legal Price** — KSBCL's official government price list, via the pipeline's representative-item-code selection. **Charged Price** — the person, entered fresh every single time, sourced from nowhere else.
**Confidence representation:** Legal Price is the single highest-confidence fact in the entire model — always Verified, always government-sourced, never estimated. Charged Price carries no confidence tier at all — it isn't a fact the product claims to know, it's a fact the person is reporting about their own transaction.
**Freshness representation:** Legal Price carries its `run_month`/`effective_date` explicitly. A multi-supplier SKU's displayed price already follows a deterministic, disclosed rule (newest effective date, lowest item code breaks ties) — never a smoothed average.
**Must never infer:** never estimate a "typical" price when a real one isn't available; never blend multiple suppliers into one averaged figure.
**Can be computed:** cost-per-litre and cost-per-ml-alcohol are fully computed from this domain plus Composition — never independently sourced.
**Requires manual enrichment:** none at pipeline scale; for the hand-built launch catalog, prices are manually collected from the same real sources (the KSBCL list plus direct retail observation) the pipeline would otherwise automate.
**Belongs in the launch catalog:** every SKU needs a dated, real price — already the plan, and non-negotiable.
**Belongs in future enrichment:** full pipeline automation at scale; eventually, surfacing multi-supplier price *variance itself* as a signal — already confirmed real in the KSBCL research (one SKU showed a 2.4× spread across suppliers) — rather than always collapsing it to a single representative figure.

---

## 4. Comparative / Benchmark Knowledge

**Why it exists:** a price means little in isolation. "Is this good" only makes sense relative to what's typical for beers like it.
**Product moments:** Beer Detail's Style Benchmark standing, Recommendation's implicit ranking, Comparison's "what's actually different" dimension.
**Source of truth:** computed from the full set of SKUs sharing a style — never independently sourced.
**Confidence representation:** a Computed Fact, but only as reliable as its sample size. A style with very few SKUs should never produce a benchmark presented with the same weight as a style with dozens.
**Freshness representation:** recomputed whenever the underlying price or composition data changes — a benchmark is only as fresh as its least-fresh input.
**Must never infer:** never publish a benchmark for a style whose sample is too thin to mean anything — gracefully omit rather than imply a comparison that isn't statistically real.
**Can be computed:** entirely — a pure derived-data domain.
**Requires manual enrichment:** none directly, though it inherits every gap in the domains beneath it.
**Belongs in the launch catalog:** whatever the launch set actually supports, honestly labeled as thin where it is.
**Belongs in future enrichment — recovered from Generation 1:** the current shipped model uses only the median (`p50`) for a three-way better/typical/worse split, having rejected a fuller `p25`/`p50`/`p75` design as "uncited" during its own review. **Generation 1's original data model already specified exactly this richer percentile structure**, for the explicit purpose of a more precise standing judgment than one midpoint allows — that reasoning simply was never written down anywhere Generation 2 could find it. This document is that missing citation. The fields already exist in the canon, reserved and unused; reintroducing them once real data volume supports it is not new invention, it's restoring an idea the product already had.

---

## 5. Availability Knowledge

**Why it exists:** knowledge without this is trivia — a person needs to know something is actually obtainable, not just theoretically catalogued.
**Product moments:** implicitly gates every recommendation (a delisted SKU shouldn't be recommended), Beer Detail's status, channel-appropriate Price Verification (standard retail vs. duty-free).
**Source of truth:** the KSBCL pipeline's item status (LIVE/DELISTED, sourced from raw published-listing presence — corrected once already from an earlier defect that used the wrong signal) and channel classification.
**Confidence representation:** binary and Verified — a SKU either appears in the current government list or it doesn't. No partial-availability state exists.
**Freshness representation:** the run a SKU first went dark is tracked separately from the run that last reconfirmed that state — both should be preserved, never collapsed into one timestamp.
**Must never infer:** never assume a SKU is still available because it was last month; never infer availability from a retailer's website when the government list is silent.
**Can be computed:** the LIVE/DELISTED classification is directly computed from source presence, never judged.
**Requires manual enrichment:** physical shelf-walk confirmation for the hand-built launch catalog, since it isn't running through the automated pipeline yet.
**Belongs in the launch catalog:** every SKU confirmed genuinely available at the time of collection, not carried over from stale research.
**Belongs in future enrichment:** store-level or regional availability — Generation 1 proposed a full geospatial Store/City model for this, never built, and not part of this model today. A legitimate future direction if the product ever needs finer-than-city granularity, not a gap in the current model.

---

## 6. Provenance & Confidence Knowledge

**Why it exists:** this is knowledge *about* the knowledge. Without it, every fact in every other domain looks equally certain, which is dishonest whenever they aren't.
**Product moments:** every screen that shows a fact at all — Beer Detail's uniform-confidence display, Recommendation's Hard/Strong/Soft separation, Price Verification's three distinct confidence dimensions.
**Source of truth:** the canonical Beer Knowledge Model's own three-tier classification (Verified / Computed / Human Judgment), applied consistently across every domain above.
**Confidence representation:** never a blended number — always the tier itself, visible and structurally separate from the fact it describes.
**Freshness representation:** not this domain's job — freshness belongs to Domain 7; this domain is purely about certainty, not age.
**Must never infer:** a Computed Fact never borrows Verified-tier presentation, and a Human Judgment never presents with the same confidence as a Verified Fact.
**Can be computed:** the tier itself is usually knowable directly from which process produced the fact — a classification, not a computation.
**Requires manual enrichment:** none — this is a discipline applied to every other domain, not a separately sourced fact.
**Belongs in the launch catalog:** every hand-collected fact needs its tier assigned honestly at entry — this shouldn't be skipped just because the catalog is small.
**Belongs in future enrichment:** nothing new — this domain doesn't grow, it just gets applied more consistently at scale.

---

## 7. Freshness Knowledge

**Why it exists:** a fact with no age attached is a fact pretending to be more permanent than it is.
**Product moments:** implicitly everywhere a price or availability fact is shown; explicitly, this is the domain Generation 1 exposed directly to users and Generation 2 currently doesn't — a gap named plainly in `THE-VALUEBREW-EXPERIENCE.md`.
**Source of truth:** the `run_month`/`effective_date` fields already tracked throughout the KSBCL pipeline, and label-photo dates for Composition facts.
**Confidence representation:** not applicable directly — freshness is orthogonal to confidence; a fact can be old but still fully Verified, just possibly stale.
**Freshness representation:** this domain *is* the freshness representation — every other domain should be able to point back to an "as of" date recorded here.
**Must never infer:** never let a stale fact display with no indication of its age, and never treat "no fresher data available" as equivalent to "confirmed current."
**Can be computed:** age itself (now minus last-confirmed date) is trivial once the underlying date is tracked.
**Requires manual enrichment:** none beyond making sure every manual data-collection task records its own collection date — free to capture, expensive to reconstruct later.
**Belongs in the launch catalog:** every hand-collected fact carries its collection date from day one. This is exactly the kind of "cheap and important" item the Evolution document found the team has already skipped twice, across two full product generations. This should not be the third time.
**Belongs in future enrichment — recovered from Generation 1:** surfacing "as of" dates directly in Beer Detail and Price Verification, not just tracking them internally, is a genuine, justified recovery of a real idea Generation 2 dropped without ever explicitly deciding to drop it.

---

## 8. External Identifier Knowledge (GTIN / Barcode)

**Why it exists:** a reserved, deliberately unused seam for a future join key against external enrichment sources — named explicitly in the KSBCL master architecture, never built.
**Product moments:** none today; would eventually support a barcode-scan identification mechanism (canonically unblocked, already reconsidered once in the ADR, never built) and cross-referencing against external sources.
**Source of truth:** none reliable exists yet — confirmed exhaustively by the market research: no public authoritative Indian GTIN lookup, no brewery publishes barcodes, commercial APIs have poor coverage for this catalog.
**Confidence representation:** when populated, must carry its own explicit source tag — never presented with the same confidence as a KSBCL-sourced fact.
**Freshness representation:** low priority — a GTIN doesn't change once assigned, so freshness matters far less here than anywhere else in this model.
**Must never infer:** never guess a GTIN from a similar product; never treat a low-confidence fuzzy barcode-API match as equivalent to a confirmed government or brand-source barcode.
**Can be computed:** nothing — this is externally sourced or it's null.
**Requires manual enrichment:** yes, if ever pursued — either a paid GS1 relationship or manual cross-referencing against sparse existing open sources.
**Belongs in the launch catalog:** not required — the reserved fields stay empty, exactly as the KSBCL architecture already intends.
**Belongs in future enrichment — recovered from Generation 1:** Generation 1's own SKU model stored *multiple regional barcode variants per SKU*, not a single value — a real, correct insight (one physical product can legitimately carry more than one barcode across regional packaging runs) worth preserving rather than rediscovering if this domain is ever filled in.

---

## Recovered from Generation 1 (Explicit)

1. **Percentile-band Style Benchmark** (`p25`/`p50`/`p75`, Domain 4) — the fields already exist in canon, reserved and unused; this document is the citation Generation 2's own review was missing when it simplified to a single median.
2. **Visible freshness display** (Domain 7) — Generation 1's "confirmed 2 days ago" provenance strip; recommend surfacing "as of" dates directly to users, not only tracking them internally.
3. **Calories as a secondary composition fact** (Domain 2) — present in Generation 1's model, absent from the current canon entirely; legitimate to reintroduce, not a new invention, if ever prioritized.
4. **Multiple regional barcode variants per SKU** (Domain 8) — Generation 1's plural `barcode(s)` design; correct and worth preserving whenever GTIN work resumes.

## Preserved Rejections (Explicit)

1. **No inferred ABV or style from averages or similar products** — the single point in this entire model where the temptation to guess is highest, and where the "never invent a fact" discipline matters most.
2. **No user-specific taste or preference persistence anywhere in this model** — every Soft Preference is session-only, explicitly stated, never derived from past behavior, preserving the ADR's direct rejection of Generation 1's "personalize from behavior" principle.
3. **No crowdsourced submission or moderation entity** — Economic Knowledge's Charged Price is reported once, per session, never accumulated into a trust-scored contributor system.
4. **No Rating or Score entity anywhere** — Comparative Knowledge stays a computed, style-relative standing, never a subjective, user-submitted rating, preserving the Lexicon's forbidden-terminology rule at the data-model level, not just the UI level.
5. **No store or location-level entity** — Availability Knowledge stops at channel (retail vs. duty-free), never resolves to a specific shop or coordinate, preserving the canon's decision not to build Generation 1's proposed Nearby Stores model.

## Deliberately Excluded Domains

Not modeled at all, on purpose, not by oversight:

- **User/Account Knowledge** — no accounts exist; there is nothing here to model.
- **Crowdsourced Submission Knowledge** — rejected structurally, twice, by two independent planning processes.
- **Rating/Review Knowledge** — incompatible with the Lexicon at the terminology level.
- **Location/Store Knowledge** — proposed once in Generation 1, cut, never revived; a legitimate future direction, not a current gap.

## What Feeds Each Capability

| Capability | Domains it depends on |
|---|---|
| **Recommendation** | Identity, Composition, Economic, Comparative, Provenance/Confidence |
| **Beer Detail** | Identity, Composition, Economic (Legal Price only), Comparative, Availability, Provenance/Confidence, Freshness |
| **Price Verification** | Identity, Economic (both prices), Freshness |
| **Comparison** *(specified, not yet built)* | Identity, Composition, Economic, Comparative, Provenance/Confidence |

Every capability depends on Identity Knowledge being correct first — it's the one domain every other domain silently assumes.
