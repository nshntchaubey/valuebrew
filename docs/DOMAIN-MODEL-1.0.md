# ValueBrew Domain Model 1.0

*The conceptual business model — what fundamentally exists in the ValueBrew universe, not how it's stored or coded. Reconciled from the canonical Beer Knowledge Model, the shipped V1 domain code, the planned Flutter Implementation Architecture, the KSBCL pipeline's own entity model, Beer Knowledge Model 2.0, Decision Engine 2.0, and Generation 1's original data model. Where documents disagree, the disagreement is named and resolved, not silently picked.*

---

## Classification Categories, Defined Once

- **Entity** — has its own identity, independent lifecycle, referenceable from more than one place.
- **Value Object** — has no identity of its own; exists only as an attribute of something else, defined entirely by its value.
- **Reference Data** — the stable, shared universe everything else operates over. (Most Reference Data in this model is *also* an Entity — the two aren't opposites, and this document says so explicitly wherever both apply, rather than forcing a false single label.)
- **Computed View** — a specific, per-instance fact derived from other data, recomputable on demand, never itself a primary source of truth.
- **Derived Knowledge** — a broader, aggregate synthesized understanding, not tied to one instance (a Computed View is often built *from* Derived Knowledge, not the same thing as it).
- **Session Object** — exists only for the duration of one interaction; never persisted, by explicit product decision.

---

## Part 1 — Entities (Reference Data)

### Beer
1. **Why it exists:** the recognizable, named thing a person thinks of when they think of a beer — a brand and a style, before any question of size or price.
2. **What it represents:** a real-world product identity at the level a person actually talks about ("Kingfisher Strong"), one level coarser than a purchasable unit.
3. **Core responsibilities:** anchors every Sku that's a variant of it; carries the facts that don't vary by size or container (name, brewery, style, whether it's craft).
4. **Relates to:** owns/anchors one or more `Sku`; references one `Style`.
5. **Owned by:** the Catalog.
6. **Referenced by:** `Sku`, `Recommendation Result`, `Comparison Result`, `Verification Result` — always by ID, never embedded, at any point one of these crosses a screen boundary.
7. **Persistent, computed, or session-only:** persistent Reference Data.
8. **Lifecycle:** created once when a genuinely new product first appears in the source data; never deleted; can go dormant (see `Sku` availability) and reappear.
9. **Reasoning that depends on it:** Recommendation's candidate identity, Beer Detail's identity display, Comparison's candidate naming.
10. **Screens that use it:** Home (indirectly, via routing intent only), Recommendation, Beer Detail, Comparison (specified, unbuilt).
11. **Knowledge domain that owns its attributes:** Identity Knowledge.
12. **Pipeline stages that produce or update it:** KSBCL Stage 3 (normalization) supplies the name; Stage 4 (canonical identity resolution) is what actually decides two listings are the same Beer/Sku.
13. **Can it exist independently:** yes, conceptually — a Beer can exist with zero currently-live Sku variants (fully delisted), though it becomes practically invisible to every reasoning surface at that point.
14. **Must never become part of this entity:** a price, an ABV, a size, or a container type — all of those belong one level down, on `Sku`, because a single Beer can have variants that differ on every one of them.

**Reconciliation note:** the planned Flutter Implementation Architecture proposed a separate `Brand` entity distinct from `Beer`. The shipped app never built one — `brewery` is a plain field directly on `Beer`. This document canonicalizes the shipped, simpler model. A separate `Brand` entity should only be introduced if a real need emerges (e.g., the still-unconfirmed contract-brewing question already flagged in the KSBCL docs, where one brand might legitimately have multiple licensed breweries) — not spec­ulatively.

---

### Style
1. **Why it exists:** the category a Beer belongs to, and the reference group everything in Comparative Knowledge is measured against.
2. **What it represents:** a recognized beer category (Lager, Wheat, Stout, IPA, etc.) — not a fact about any one product, a grouping concept.
3. **Core responsibilities:** anchors every `Beer` that belongs to it; anchors the one `Style Benchmark` computed for it.
4. **Relates to:** referenced by `Beer`; owns exactly one `Style Benchmark`.
5. **Owned by:** the Catalog.
6. **Referenced by:** `Beer`, `Style Benchmark`, `Style Standing`.
7. **Persistent, computed, or session-only:** persistent Reference Data.
8. **Lifecycle:** effectively permanent — new styles are rare and are a curation decision, not a per-run pipeline output.
9. **Reasoning that depends on it:** Recommendation's optional Strong Preference filter; Beer Detail and Comparison's Style Standing display.
10. **Screens that use it:** Recommendation, Beer Detail, Comparison (specified, unbuilt).
11. **Knowledge domain that owns its attributes:** Identity Knowledge.
12. **Pipeline stages that produce or update it:** not currently produced by the KSBCL pipeline at all — style classification for a given Beer is presently a curation/enrichment task, not an automated pipeline output. **[Flagged inconsistency]** — this is worth naming plainly: the app's domain model treats Style as foundational and always-known, but nothing in the actual data pipeline currently assigns it reliably at scale.
13. **Can it exist independently:** yes — a Style can exist (and have a Benchmark) even before any Beer is confirmed to belong to it, though that's not a useful state in practice.
14. **Must never become part of this entity:** any single beer's own facts — Style is a category, never a product.

---

### Sku
1. **Why it exists:** the actual purchasable unit — the thing a price attaches to, per the Product Identity Charter's own generative test: the smallest unit for which a price comparison is fair and meaningful.
2. **What it represents:** one specific brand + style + size + container combination.
3. **Core responsibilities:** carries every fact that genuinely varies within a Beer (size, container, ABV, current representative price, current availability); is the unit every reasoning surface actually compares.
4. **Relates to:** belongs to exactly one `Beer`; may currently be represented by one or more `Listing`s; has one `Value` computed view and one `Style Standing` computed view.
5. **Owned by:** the Catalog, via its parent `Beer`.
6. **Referenced by:** `Recommendation Result`, `Comparison Result`, `Verification Result`, `Preference Summary`'s implicit candidate set — always by ID across any screen boundary.
7. **Persistent, computed, or session-only:** persistent Reference Data.
8. **Lifecycle:** created once, on first sighting of a genuinely new size/container combination; never deleted or renumbered; can go LIVE → DELISTED → LIVE again without losing identity.
9. **Reasoning that depends on it:** the unit every one of the five reasoning surfaces in Decision Engine 2.0 actually operates on.
10. **Screens that use it:** all of them.
11. **Knowledge domain that owns its attributes:** split across Identity (which Sku this is), Composition (ABV), Economic (its current representative price), Availability (LIVE/DELISTED, channel).
12. **Pipeline stages that produce or update it:** Stage 3 (pack-size/container extraction) and Stage 4 (canonical identity resolution) together determine identity; Stage 5 (representative-item-code selection) determines which real-world listing currently represents its displayed price.
13. **Can it exist independently:** no — always requires a parent `Beer`.
14. **Must never become part of this entity:** which supplier currently sells it — that's a fact about a `Listing`, deliberately excluded from Sku/canonical identity by the recorded Stage 4 Identity Decision.

**Reconciliation note — this is the model's single most important duplicated-concept finding:** the app's `Sku` and the KSBCL pipeline's `canonical_product_id`-identified product describe the *exact same conceptual thing* — a retail purchasable unit, identified by brand/style + size + container. They currently exist as two independent, unconnected representations, because no catalog-build step joins `beer_master.csv` into `catalog.json` yet (already established in the Project Brain as the product's core structural bottleneck). This document treats them as one entity, conceptually — `Sku` in the app's language, `canonical_product_id` in the pipeline's — and names the missing join as the concrete, mechanical thing standing between them, not two different ideas needing reconciliation.

**Overload risk, worth naming explicitly:** `Sku` is currently asked to do two jobs at once — hold the *identity* of a purchasable unit, and hold the *single current representative price/fact set* for it. Stage 5's representative-selection rule already treats these as conceptually distinct (an identity that can have several concurrent listings, only one of which is currently "the" displayed price) — see `Listing`, below, for the entity this points toward.

---

### Listing — **missing from the current app domain model, present in KSBCL's own architecture**
1. **Why it exists:** a real `Sku` can be concurrently supplied by more than one supplier, at more than one price, and the KSBCL pipeline's own product-design documents (the User Mental Model) already describe exactly this as a two-layer shape — "canonical product = stable identity; listing = a supplier's current offer, its own price, its own availability" — real, confirmed in the actual 2026-06 data (one SKU with ten concurrently live listings spanning ₹80–190).
2. **What it represents:** one supplier's current offer of one `Sku`.
3. **Core responsibilities:** carries the supplier identity, the price that supplier is currently charging, and that listing's own liveness — none of which belong on `Sku` itself.
4. **Relates to:** belongs to exactly one `Sku`; one of a Sku's Listings is selected, deterministically, as that Sku's current representative price (Stage 5's own rule: newest effective date, lowest item code as tiebreak).
5. **Owned by:** its parent `Sku`.
6. **Referenced by:** `Price Observation` (each observation is of one Listing's price at one point in time).
7. **Persistent, computed, or session-only:** persistent Reference Data.
8. **Lifecycle:** created when a supplier's item_code is first mapped to a canonical Sku; can go LIVE/DELISTED independently of the Sku it belongs to (a Sku can remain LIVE via one Listing even as another goes dark).
9. **Reasoning that depends on it:** none of the five reasoning surfaces reason about Listings directly today — they all reason about Sku's already-collapsed representative price. This is precisely why the concept is currently invisible at the app layer.
10. **Screens that use it:** none currently — this is a **flagged missing entity**, not a built one.
11. **Knowledge domain that owns its attributes:** Economic Knowledge (price), Availability Knowledge (liveness), a supplier identifier that Identity Knowledge deliberately excludes from Sku identity itself.
12. **Pipeline stages that produce or update it:** Stage 4 (each mapped item_code is, conceptually, a Listing) and Stage 5 (which selects one Listing per Sku as representative).
13. **Can it exist independently:** no — always requires a parent Sku.
14. **Must never become part of this entity:** it must never be promoted to define Sku identity itself — that's the exact thing the recorded Stage 4 Identity Decision excluded on purpose.

**Why this matters enough to flag as missing, not just theoretical:** The ValueBrew Experience document's own generational note about Price Verification already identifies the practical consequence of this gap — the current app has no visible mechanism for "this beer has multiple current prices depending on where you buy it," even though the underlying data (and the KSBCL team's own product design) already models exactly that reality. This isn't a hypothetical future capability; it's a real thing the data already contains that the app's domain model currently has no entity to hold.

---

### Catalog
1. **Why it exists:** the one thing every screen actually loads and reasons against — the whole currently-known universe of Beers, Skus, Styles, and Benchmarks.
2. **What it represents:** a complete, internally consistent snapshot, not a live, continuously-updating feed.
3. **Core responsibilities:** the single point every other Reference Data lookup (`resolveBeer`, `resolveStyle`, `resolveSku`, `resolveBenchmark`) resolves against.
4. **Relates to:** contains every `Beer`, `Style`, `Sku`, and `Style Benchmark` currently known.
5. **Owned by:** nothing — it's the root.
6. **Referenced by:** every screen, via the one shared loading provider.
7. **Persistent, computed, or session-only:** loaded once per session from a persistent source (currently a bundled JSON file), held in memory for that session's duration.
8. **Lifecycle:** replaced wholesale on each load — there is no partial update; a new Catalog snapshot supersedes the old one entirely.
9. **Reasoning that depends on it:** all of it — nothing reasons about a Beer, Sku, or Style except through a loaded Catalog.
10. **Screens that use it:** all of them.
11. **Knowledge domain that owns its attributes:** not applicable — Catalog is a container, not itself a fact-bearer.
12. **Pipeline stages that produce or update it:** none directly today — the KSBCL pipeline produces `beer_master.csv`; the step that would turn that into a loadable Catalog snapshot is the very join gap already named under `Sku`, above.
13. **Can it exist independently:** no — it's meaningless without the entities it contains, and nothing else can exist, in the app's actual operation, without it.
14. **Must never become part of this entity:** anything session-scoped — a `Preference Summary` or an `Observed Price` is never stored inside the Catalog, under any circumstance, because the Catalog is shared, persistent Reference Data and those are explicitly, permanently not.

---

## Part 2 — Persistent Event Entity

### Price Observation
1. **Why it exists:** a record that a specific Listing's price was confirmed, at a specific point in time — the raw material both Legal Price display and any future price-trend feature are built from.
2. **What it represents:** one government-published price fact about one Listing, at one moment.
3. **Core responsibilities:** never updated once written; the sole source from which "has this price changed" is ever determined.
4. **Relates to:** belongs to one `Listing` (via its item_code); conceptually the ancestor of whatever price is currently shown as a Sku's representative.
5. **Owned by:** its parent `Listing`, transitively its Sku.
6. **Referenced by:** nothing currently — the app doesn't yet expose price history to any screen; this entity exists today entirely inside the KSBCL pipeline (`beer_price_history.csv`).
7. **Persistent, computed, or session-only:** persistent, append-only.
8. **Lifecycle:** written once, never modified, never deleted — this is the one entity in the entire model explicitly designed to accumulate forever rather than represent current state.
9. **Reasoning that depends on it:** none of the five reasoning surfaces reason about this directly today — it's the raw ledger a future price-trend or freshness display would read from.
10. **Screens that use it:** none currently.
11. **Knowledge domain that owns its attributes:** Economic Knowledge (the price itself), Freshness Knowledge (when it was true).
12. **Pipeline stages that produce or update it:** Stage 5, exclusively — this is its sole source and sole writer.
13. **Can it exist independently:** no — always tied to a specific Listing and, transitively, Sku.
14. **Must never become part of this entity:** any notion of "submitted by," "trust score," or moderation status — this is a direct, deliberate structural echo of Generation 1's rejected `PriceSubmission`/`Price` split, adapted compatibly: the *shape* (an append-only observation ledger distinct from current-state) survives, because it serves the same "never erase a real fact" governance already established for the KSBCL pipeline — but the crowdsourcing/trust/moderation apparatus that originally motivated that shape in Generation 1 stays permanently rejected, since it depends on accounts.

---

## Part 3 — Derived Knowledge and Computed Views

### Style Benchmark — Derived Knowledge
1. **Why it exists:** a price or a Value figure means little in isolation — this is the reference distribution that makes "typical for this style" a real, computable claim.
2. **What it represents:** an aggregate statistical summary of price-per-alcohol across every Sku currently sharing a Style — not a fact about any one beer.
3. **Core responsibilities:** the single source `Style Standing` (below) is computed against.
4. **Relates to:** belongs to one `Style`; every `Sku` of that Style contributes to it and is, in turn, evaluated against it.
5. **Owned by:** its parent `Style`.
6. **Referenced by:** `Style Standing`.
7. **Persistent, computed, or session-only:** a Computed/cached aggregate, recomputed whenever the underlying data changes — not independently sourced.
8. **Lifecycle:** recomputed, not appended to — unlike Price Observation, an old Benchmark value isn't kept once a newer one is computed, since the current standing judgment always wants the current distribution.
9. **Reasoning that depends on it:** Beer Detail's and Comparison's Style Standing display.
10. **Screens that use it:** Beer Detail, Comparison (specified, unbuilt).
11. **Knowledge domain that owns its attributes:** Comparative/Benchmark Knowledge.
12. **Pipeline stages that produce or update it:** not currently produced by the KSBCL pipeline — computed entirely at the app layer, from whatever Skus are in the loaded Catalog.
13. **Can it exist independently:** yes, conceptually — a Style Benchmark can exist even where no single Sku's Style Standing is currently being displayed.
14. **Must never become part of this entity:** a single beer's own facts — this is aggregate knowledge, not a per-product record.

**Recovery, formalized here:** Beer Knowledge Model 2.0 already recommended reintroducing Generation 1's `p25`/`p50`/`p75` percentile structure, once the reserved fields have real data volume behind them, rather than the current shipped `p50`-only split. This document confirms Style Benchmark as the correct entity to carry that richer structure when it's reintroduced — no new entity is needed, only a richer shape for this one.

### Value (Alcohol-Adjusted Value) — Computed View
1. **Why it exists:** the product's core differentiator — price alone means nothing without knowing how much alcohol it buys.
2. **What it represents:** cost-per-litre and cost-per-ml-of-alcohol for one specific Sku, at its currently-known price and ABV.
3. **Core responsibilities:** feeds every ranking decision Recommendation makes, and the headline figure on Beer Detail.
4. **Relates to:** computed from one `Sku`'s Economic and Composition facts; feeds `Style Standing`.
5. **Owned by:** conceptually owned by its `Sku`, though not itself persisted as a separate stored fact in the shipped app today (see reconciliation, below).
6. **Referenced by:** `Recommendation Result`, `Comparison Result`.
7. **Persistent, computed, or session-only:** Computed View, recomputed whenever price or ABV changes.
8. **Lifecycle:** has no independent lifecycle — it's a live derivation, not a stored fact with its own history.
9. **Reasoning that depends on it:** Recommendation's entire ranking logic; Comparison's per-candidate facts.
10. **Screens that use it:** Recommendation, Beer Detail, Comparison (specified, unbuilt).
11. **Knowledge domain that owns its attributes:** derived jointly from Economic and Composition Knowledge.
12. **Pipeline stages that produce or update it:** none — purely an app-layer computation over Sku's price and ABV.
13. **Can it exist independently:** no — meaningless without a Sku with both a known price and a known ABV, and **[Flagged Gap, carried forward from Decision Engine 2.0]** nothing in the canon currently says what should happen to this computation when ABV is null, which Beer Knowledge Model 2.0 established is the normal state for most of the real catalog today.
14. **Must never become part of this entity:** any subjective judgment — Value is a number, never a rating; Style Standing (below) is where the judgment lives.

**Reconciliation note:** the planned Flutter Implementation Architecture proposed a distinct `DerivedValueProfile` entity for this. The shipped app never built a separate entity — the fields live directly on `Sku`. This document treats Value as a genuine Computed View conceptually, regardless of where it's physically held, precisely so a future refactor toward an explicit, freshness-stamped Value object (per the freshness recovery already recommended in Beer Knowledge Model 2.0) doesn't require re-deriving this concept from nothing.

### Style Standing — Computed View
1. **Why it exists:** turns a raw Value number into the plain judgment Beer Detail and Comparison actually display — better/typical/worse than peers.
2. **What it represents:** one Sku's position relative to its Style Benchmark, at the moment it's computed.
3. **Core responsibilities:** the single fact that lets a person answer "is this a good deal for this kind of beer" without doing the math themselves.
4. **Relates to:** computed from one `Sku`'s Value against its `Style Benchmark`.
5. **Owned by:** conceptually its `Sku`.
6. **Referenced by:** Beer Detail's display, Comparison's per-candidate facts.
7. **Persistent, computed, or session-only:** Computed View.
8. **Lifecycle:** no independent lifecycle — recomputed whenever Value or the Style Benchmark changes.
9. **Reasoning that depends on it:** Beer Detail's and Comparison's presentation of comparative standing.
10. **Screens that use it:** Beer Detail, Comparison (specified, unbuilt).
11. **Knowledge domain that owns its attributes:** Comparative/Benchmark Knowledge.
12. **Pipeline stages that produce or update it:** none — app-layer only.
13. **Can it exist independently:** no — requires both a Sku's Value and a Style Benchmark to exist.
14. **Must never become part of this entity:** the word "Score" or "Rating" in any of its three states' labels — the Lexicon's forbidden-terminology rule applies at this exact point.

---

## Part 4 — Session Objects

### Preference Summary
1. **Why it exists:** the collection of everything a person has actually stated, for exactly one interaction.
2. **What it represents:** the running record of Constraints gathered during one Recommendation flow.
3. **Core responsibilities:** the only thing Recommendation's reasoning is allowed to treat as known preference — nothing else is ever assumed.
4. **Relates to:** composed of `Constraint` value objects, each tagged Hard/Strong/Soft.
5. **Owned by:** the current session only — nothing owns it beyond that.
6. **Referenced by:** carried forward across a Recommendation → Beer Detail or → Comparison hand-off, by explicit design, never re-derived at the destination.
7. **Persistent, computed, or session-only:** **session-only, absolutely** — this is the entity the "no accounts" decision is most directly enforced through.
8. **Lifecycle:** created empty at the start of a Recommendation interaction; discarded completely when the session ends; never reloaded, never merged with a past session's summary, because none exists to merge with.
9. **Reasoning that depends on it:** all of Recommendation's threshold logic (Decision Engine 2.0, Part 2).
10. **Screens that use it:** Recommendation, carried into Comparison (specified, unbuilt) and referenced (not re-gathered) on Beer Detail.
11. **Knowledge domain that owns its attributes:** not applicable — this isn't catalog knowledge, it's a record of what a person said.
12. **Pipeline stages that produce or update it:** none — entirely app-layer, entirely session-scoped.
13. **Can it exist independently:** no — meaningless without an active session.
14. **Must never become part of this entity:** anything inferred rather than stated — this is the exact entity the ADR's rejected "inferring unstated preferences" alternative would have touched, and it stays untouched by design.

### Constraint — Value Object
1. **Why it exists:** the single unit of "something a person said mattered," tagged by how much it matters.
2. **What it represents:** one stated preference — a budget, a style — carrying its own Hard/Strong/Soft weight.
3. **Core responsibilities:** tells the reasoning model exactly how much authority this input has (a Hard Constraint can never be violated; a Strong Preference can be traded off; a Soft Preference is the substance of a Trade-off Explanation).
4. **Relates to:** exists only inside a `Preference Summary`.
5. **Owned by:** its parent `Preference Summary`.
6. **Referenced by:** nothing independently — it has no identity of its own outside its parent collection.
7. **Persistent, computed, or session-only:** session-only, inheriting its parent's lifecycle entirely.
8. **Lifecycle:** added when stated, replaced (not accumulated) when the same input is later changed mid-flow — all *other* already-stated Constraints are preserved when one is refined.
9. **Reasoning that depends on it:** the entire Hard/Strong/Soft filtering and Trade-off logic in Decision Engine 2.0.
10. **Screens that use it:** Recommendation.
11. **Knowledge domain that owns its attributes:** not applicable — this is a fact about a person's statement, not catalog knowledge.
12. **Pipeline stages that produce or update it:** none.
13. **Can it exist independently:** no.
14. **Must never become part of this entity:** a numeric weight exposed to the user as a score — the tier (Hard/Strong/Soft) is a reasoning input, never a displayed number.

### Observed / Charged Price — Session Object
1. **Why it exists:** the one number in the entire product that's reported, not known — what a person says they were actually charged.
2. **What it represents:** a claim about one specific transaction, for exactly one Price Verification.
3. **Core responsibilities:** the only input to Price Verification's classification besides the SKU's own Legal Price.
4. **Relates to:** compared against one `Sku`'s Legal Price to produce a `Verification Result`.
5. **Owned by:** the current session only.
6. **Referenced by:** nothing — by explicit rule, this value is never carried forward to any other screen, including Beer Detail on the way back from Price Verification.
7. **Persistent, computed, or session-only:** session-only, with deliberately *no repository or storage adapter at all* — a stronger guarantee than most session objects, which at least have the theoretical shape of something storable.
8. **Lifecycle:** entered, used once, discarded — does not even survive the Price Verification screen's own hand-off back to Beer Detail.
9. **Reasoning that depends on it:** Price Verification's entire classification.
10. **Screens that use it:** Price Verification only.
11. **Knowledge domain that owns its attributes:** Economic Knowledge, but explicitly the *reported*, not *sourced*, half of it.
12. **Pipeline stages that produce or update it:** none — this never touches the pipeline at all.
13. **Can it exist independently:** no.
14. **Must never become part of this entity:** any persistence mechanism whatsoever, under any future refactor — this is one of the most explicitly, repeatedly protected non-features in the entire canon.

---

## Part 5 — Reasoning Outputs (Computed Views, Ephemeral)

### Recommendation Result
1. **Why it exists:** the object Recommendation actually produces — a winner, or one of its honest alternatives.
2. **What it represents:** either a single winning Sku with its Explanation, or (as `Recommendation Tie`) a set of `Tied Candidate`s with one shared Explanation covering the set, or a named "no recommendation exists yet" outcome.
3. **Core responsibilities:** the sealed set of every honest shape a Recommendation answer can take — deliberately closed, so a new outcome type can never be silently added without every consumer being forced to handle it.
4. **Relates to:** references its winning or tied `Sku`(s) and their parent `Beer`(s) by full value internally (a domain function's own return shape, not a navigation boundary — the "prefer IDs" rule doesn't apply to this internal shape the way it does the moment this result crosses into navigation).
5. **Owned by:** nothing — produced fresh by each Recommendation reasoning pass, never stored.
6. **Referenced by:** the screen that requested it; only the winning/tied Sku's *ID* is what actually crosses into a navigation hand-off toward Beer Detail.
7. **Persistent, computed, or session-only:** ephemeral Computed View — exists only for the duration of one rendering.
8. **Lifecycle:** created fresh on every Recommendation evaluation; discarded the moment the person navigates away or refines a Constraint (which triggers a fresh evaluation, not a patch of the old result).
9. **Reasoning that depends on it:** it *is* the output of Decision Engine 2.0's Recommendation reasoning, Part 2.
10. **Screens that use it:** Recommendation.
11. **Knowledge domain that owns its attributes:** composes facts from Identity, Composition, Economic, and Comparative Knowledge, plus its own Explanation and Confidence.
12. **Pipeline stages that produce or update it:** none — purely app-layer reasoning output.
13. **Can it exist independently:** no.
14. **Must never become part of this entity:** a numeric confidence blended into one figure — Confidence stays a structurally separate, attached Value Object (below), never folded into this result's own headline number.

### Comparison Result *(specified, not yet built)*
Identical treatment to `Recommendation Result`, with two structural differences worth naming precisely: it carries *two* confidence layers rather than one (per-candidate and result-level, never merged), and its Trade-off/Tie variants are bounded to exactly the candidates explicitly handed in — it never has a "no result exists yet" shape the way Recommendation does, since Comparison is never entered without at least two already-resolved candidates to begin with.

### Verification Result
1. **Why it exists:** the object Price Verification actually produces.
2. **What it represents:** a flat classification (below/at/above), never a sealed hierarchy — the Beer Knowledge Model defines this as one classification, not several differently-shaped outcomes, so there's no per-verdict data that would justify branching the type the way Recommendation's outcomes are branched.
3. **Core responsibilities:** carries the verdict, the two prices being compared, and an Explanation naming the three confidence dimensions.
4. **Relates to:** compares one `Sku`'s Legal Price against a session-only Observed Price.
5. **Owned by:** nothing — ephemeral.
6. **Referenced by:** the Price Verification screen only.
7. **Persistent, computed, or session-only:** ephemeral Computed View.
8. **Lifecycle:** created on each verification request; discarded on navigation away.
9. **Reasoning that depends on it:** Decision Engine 2.0, Part 4.
10. **Screens that use it:** Price Verification.
11. **Knowledge domain that owns its attributes:** Economic Knowledge, Freshness Knowledge.
12. **Pipeline stages that produce or update it:** none directly — consumes Stage 5's price output, produces nothing back into the pipeline.
13. **Can it exist independently:** no.
14. **Must never become part of this entity:** the charged price it was built from, once the person navigates away — consistent with `Observed Price`'s own non-persistence.

---

## Part 6 — Value Objects (Never Standalone)

### Confidence / Knowledge Tier
Exactly one of Verified, Computed, or Human Judgment — attached to a fact, never independently meaningful. Owns nothing, is owned by whatever fact it describes. Explicitly, canonically forbidden from ever being blended into a single number across multiple facts.

### Explanation
The stated reasoning behind a Recommendation, Trade-off, or Verification verdict — always attached, generated together with the conclusion it explains (per Decision Engine 2.0's recovered Generation-1 mechanical guarantee), never presented standalone, never generated as a separate pass that could drift from what it's explaining.

### Availability
LIVE or DELISTED, plus channel (standard retail or duty-free) — an attribute of `Sku` (via its `Listing`s), never an entity with independent meaning apart from the thing it describes.

---

## Part 7 — Explicitly Not Modeled (Preserved Rejections)

- **User / Account** — no accounts exist; there is no entity here to model, on purpose.
- **Store / City / State / Retailer** — Generation 1's geospatial model; cut once, never revived, not part of this model.
- **Rating** — incompatible with the Lexicon at the terminology level, not just a missing feature.
- **PriceSubmission with moderation status / trust score** — the *shape* survives, appropriately adapted, as `Price Observation`; the crowdsourcing/trust apparatus that originally required it does not.
- **Decision (per-user event log)** — would require a User entity to attach to; doesn't exist for the same reason.

---

## Part 8 — Consolidated Findings

**Missing entity:** `Listing` — fully specified in the KSBCL pipeline's own product-design documents, real in the actual data, and currently absent from the app's domain model entirely.

**Duplicated concept, now reconciled:** `Sku` (app) and `canonical_product_id` (pipeline) are the same entity, described independently by two documents that were never joined — the missing join is a concrete, known engineering gap, not a conceptual disagreement.

**Overloaded entity:** `Sku` currently holds both identity and current-representative-price in one place, which the pipeline's own Stage 5 logic already treats as two separate concerns — `Listing` is exactly the entity that resolves this overload once it's built.

**Conceptual inconsistency, reconciled:** the planned architecture's `Brand`/`DerivedValueProfile` entities were never built; this document canonicalizes the shipped, simpler shapes and treats the planned entities as legitimate future refinements, not current gaps.

**Flagged, unresolved (carried forward from Beer Knowledge Model 2.0 and Decision Engine 2.0):** no entity in this model currently defines what happens to `Value`/`Style Standing` when a Sku's Composition Knowledge is incomplete — the same gap named twice already, now located precisely at the entity level: it lives in `Value`'s own computation, point 13.
