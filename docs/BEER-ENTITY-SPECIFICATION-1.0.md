# ValueBrew — Beer Entity Specification 1.0

*The single canonical Beer entity, reconciling Beer Knowledge Model 2.0, Domain Model 1.0, and Catalog Specification 1.0 into one attribute-by-attribute reference every future implementation (catalog.json, Flutter, the pipeline, an eventual API) can map onto. No JSON, no Dart, no SQL — the conceptual entity, once, so it never needs re-deriving from three separate documents again.*

**Table legend:** *Represents* = what the attribute means · *Fact type* = Verified / Computed / Curated (Human Judgment) · *Lifecycle* = Immutable (set once, never changes) or Mutable (can be revised) · *Launch* = Critical / Recommended / Optional / Future · *Scope* = Persistent or Session · *If missing* = product behavior when absent.

---

## 1. Beer

| Attribute | Represents | Fact type | Lifecycle | Launch | Scope | If missing |
|---|---|---|---|---|---|---|
| `id` | stable identity reference | Computed (assigned at resolution) | Immutable | Critical | Persistent | not possible — a Beer without an id doesn't exist in the catalog |
| `name` | the recognizable brand name | Verified | Mutable (a real rename is rare but possible) | Critical | Persistent | not possible — folds into Identity's "must exist" rule |
| `brewery` | the manufacturing/brand-owner name, as a plain attribute, not a separate entity | Verified (KSBCL) or Curated (retailer-sourced, gap-filled) | Mutable | Recommended | Persistent | gracefully omitted, never guessed |
| `styleId` | reference to the owning Style | Curated (a categorization decision, not extracted) | Mutable (recategorization is rare but not forbidden) | Critical | Persistent | the Beer can still exist and be priced; Style Standing and the style filter simply don't apply to it |
| `isCraft` | whether this is an independent/craft brand vs. a mass-market one | Curated | Mutable | Optional | Persistent | omitted — no behavior currently depends on it |

**Reconciliation note:** Domain Model 1.0 already resolves the question of whether Brewery deserves its own entity — the planned Flutter Implementation Architecture proposed a separate `Brand`, the shipped app never built one, and this document canonicalizes the shipped, simpler shape. `Brewery` is an attribute of `Beer`, not its own entity, unless a real need (contract-brewing disambiguation, still an unconfirmed KSBCL-side business question) forces the split later.

**[Recovered from Generation 1, not existing Gen 2 canon]** `isCraft` appeared in Generation 1's `Beer` model and nowhere in the current canon. Nothing depends on it today; it's named here so a future reintroduction doesn't need rediscovering from scratch.

---

## 2. Style

| Attribute | Represents | Fact type | Lifecycle | Launch | Scope | If missing |
|---|---|---|---|---|---|---|
| `id` | stable identity reference | Computed | Immutable | Critical | Persistent | not possible |
| `name` | the category label (Lager, Stout, IPA, ...) | Curated | Immutable in practice | Critical | Persistent | not possible |
| `description` | a plain-language gloss of the category | Curated | Mutable | Optional | Persistent | gracefully omitted |
| `typicalAbvRange` | a rough, descriptive expectation for the category, distinct from the computed Style Benchmark | Curated | Mutable | Optional | Persistent | omitted — not currently used by any reasoning surface |

**[Recovered from Generation 1, not existing Gen 2 canon]** `description` and `typicalAbvRange` both appeared on Generation 1's `Style`/`Category` model. Neither is required, neither is currently used by any built reasoning surface, and neither should be confused with the *computed* Style Benchmark below — this is a curated, descriptive expectation about a category in general, not a statistical fact derived from the current catalog.

---

## 3. Sku

The purchasable unit — where the bulk of the model's real weight sits.

| Attribute | Represents | Fact type | Lifecycle | Launch | Scope | If missing |
|---|---|---|---|---|---|---|
| `id` | stable identity reference | Computed | Immutable | Critical | Persistent | not possible |
| `beerId` | reference to parent Beer | Computed | Immutable | Critical | Persistent | not possible |
| `sizeMl` | the exact volume | Verified/Computed (extracted) | Immutable — a size change is a *new* Sku, never an edit to this one | Critical | Persistent | not possible — folds into Identity's rule |
| `containerType` | bottle / can / etc. | Verified/Computed | Immutable, same reasoning as size | Critical | Persistent | not possible |
| `packCount` | wholesale case size, an identity-resolution input more than a display fact | Verified/Computed | Immutable per listing generation | Optional (display) / Critical (identity resolution) | Persistent | not surfaced to any reasoning surface if absent — its role is upstream, in KSBCL's own matching key |
| `abv` | alcohol content | **Verified only — never estimated, never computed, never inherited** | Mutable, but only via a genuine re-confirmation (reformulation risk), never silently | **Critical — the true launch-readiness gate** | Persistent | **the Sku exists in the catalog but is excluded from value-based ranking** — this is a product policy, not a rendering fallback |
| `calories` | secondary composition fact | Verified only, same discipline as ABV | Mutable, same reformulation caveat | Optional | Persistent | gracefully omitted |
| `legalPrice` | the current, government-verified reference price | Verified — the single highest-confidence fact in the model | Mutable | Critical | Persistent | Price Verification and value-based ranking are both unavailable for this Sku |
| `priceEffectiveDate` | when the current price was last confirmed true | Computed (from source data) or Curated (recorded at manual collection) | Mutable, updates whenever price does | Recommended | Persistent | the price is treated as unconfirmed-fresh, never assumed current by default |
| `costPerLitre`, `costPerMlAlcohol` | Value Metrics | Computed — derived from `legalPrice` + `abv`, no independent source | Not independently mutable — recomputed whenever an input changes | Critical (derived automatically once inputs exist) | Persistent Computed View | absent whenever either input is absent — never partially estimated |
| `styleStanding` | better/typical/worse-than-peers judgment | Computed | Recomputed whenever Value or the Style Benchmark changes | Recommended | Persistent Computed View | gracefully omitted, never a guess dressed as a comparison |
| `availabilityStatus` | LIVE / DELISTED | Verified | Mutable — this is expected to change over a Sku's life | Critical | Persistent | treated as unavailable, never assumed present by default |
| `channel` | standard retail vs. duty-free | Verified | Immutable per Listing, though a Sku can span both channels via different Listings | Critical | Persistent | treated as standard retail only, until confirmed otherwise |
| `gtin` | external barcode identifier(s) | Curated (external source) | Immutable once confirmed | Future | Persistent | absent by default — a reserved, deliberately empty seam |
| *(meta)* confidence tier per fact above | which of Verified/Computed/Human Judgment each other attribute is | Computed classification | Set alongside the fact it describes | Critical, as a discipline | Persistent | never allowed to be missing — every fact must carry a tier, even in a tiny hand-built launch catalog |

**On `legalPrice` specifically — a boundary that must never blur:** the value shown here is a *derived, representative* figure, resolved deterministically (newest effective date, lowest item code as tiebreak) from whichever `Listing` currently represents this Sku — it is not independently stored truth. See Section 4.

**[Recovered from Generation 1, not existing Gen 2 canon]** `priceEffectiveDate` as a Sku-level, potentially user-visible attribute is a direct recovery of Generation 1's provenance-strip idea, already recommended in Beer Knowledge Model 2.0 and the Catalog Specification. `gtin` as a *plural-capable* attribute (multiple regional barcode variants per Sku) is likewise a Generation 1 insight worth preserving, not rediscovering, whenever this seam is ever filled.

**What must never be confused with a Sku attribute:** Charged Price. It is never stored here, never even transiently attached to this entity — it belongs entirely to a separate Session Object that merely *references* a Sku's `id`. See Section 7.

---

## 4. Listing

**[This entity is missing from the current shipped app, per Domain Model 1.0's own finding — included here in full because a canonical specification should describe it correctly the first time it's built, not leave it to be rediscovered.]**

| Attribute | Represents | Fact type | Lifecycle | Launch | Scope | If missing |
|---|---|---|---|---|---|---|
| `id` | stable identity reference | Computed | Immutable | Future (entity doesn't exist yet) | Persistent | the whole entity is currently absent — see below |
| `skuId` | reference to parent Sku | Computed | Immutable | Future | Persistent | — |
| `supplierCode` / `supplierName` | who currently supplies this specific listing | Verified | Mutable across the listing's life (rare) | Future | Persistent | — |
| `price` | this listing's own current price | Verified | Mutable | Future | Persistent | — |
| `effectiveDate` | when this listing's price was last confirmed | Verified | Mutable | Future | Persistent | — |
| `itemStatus` | LIVE / DELISTED, at the listing level | Verified | Mutable | Future | Persistent | — |
| `ksbclItemCode` | the source-system identifier, preserved exactly, never reused | Verified | Immutable | Future | Persistent | — |
| `isCurrentRepresentative` | whether this Listing is the one currently determining its Sku's displayed price | Computed | Recomputed each run, per the deterministic selection rule | Future | Persistent Computed View | — |

**Why this matters enough to specify now, not just note as missing:** a real Sku can have several concurrent Listings — the KSBCL research already confirmed one SKU with ten concurrent supplier listings spanning ₹80–190. Today, `Sku.legalPrice` silently collapses that reality to one deterministically-chosen figure. Building `Listing` doesn't change that collapsing behavior for display — it makes the collapsing an explicit, inspectable computation over real, individually-modeled entities, rather than an opaque single value with no visible history of the choice behind it.

---

## 5. Style Benchmark

Attached to `Style`, not `Beer` or `Sku` — Derived Knowledge, an aggregate, never a per-product record.

| Attribute | Represents | Fact type | Lifecycle | Launch | Scope | If missing |
|---|---|---|---|---|---|---|
| `styleId` | which Style this benchmark describes | Computed | Immutable | Recommended | Persistent Derived Knowledge | — |
| `p50` | the median value figure across the style's current Skus | Computed | Recomputed whenever underlying data changes | Recommended | Persistent Computed View | Style Standing is unavailable for every Sku of this Style |
| `p25`, `p75` | wider percentile bounds | Computed | Recomputed, same as p50 | **Future — recovered candidate** | Persistent Computed View | absent today by design, not by gap |
| `sampleSize` | how many Skus the benchmark is actually based on | Computed | Recomputed | Recommended (as a discipline) | Persistent | a benchmark with too small a sample should never be published at all, regardless of whether this field exists to record why |
| `computedAt` | freshness stamp for the whole benchmark | Computed | Updates whenever recomputed | Recommended | Persistent | the benchmark is treated as unconfirmed-fresh, same discipline as `priceEffectiveDate` |

**[Recovered from Generation 1, formally reconciled here]** `p25`/`p75` are the exact fields Beer Knowledge Model 2.0 already recommended reintroducing — Generation 1's own original design, rejected once during the canonical rebuild's review as "uncited," now citable. Their launch status is deliberately **Future**, not Optional — they require real data volume to mean anything, which a ~100–150 SKU launch catalog won't reliably provide per style.

---

## 6. Price History (Price Observation)

An event, not a current-state fact — belongs to `Listing`, transitively to `Sku`.

| Attribute | Represents | Fact type | Lifecycle | Launch | Scope | If missing |
|---|---|---|---|---|---|---|
| `id` | stable identity reference | Computed | Immutable | Future (not surfaced to any experience yet) | Persistent, append-only | — |
| `listingId` | which Listing this observation is of | Computed | Immutable | Future | Persistent | — |
| `price` | the price observed at this moment | Verified | **Never mutated once written — this is the one entity in the whole model built to accumulate forever, not represent current state** | Future | Persistent, append-only | — |
| `effectiveDate` | the government-declared date this price took effect | Verified | Immutable | Future | Persistent | — |
| `eventType` | INITIAL_BACKFILL / NEW_ITEM / PRICE_CHANGE / CORRECTION | Computed | Immutable | Future | Persistent | — |
| `observedAt` | the pipeline's own clock, when this record was actually written | Computed | Immutable | Future | Persistent | — |

**[Recovered structural pattern from Generation 1, compatible not literal]** this entity is a direct, adapted echo of Generation 1's rejected `PriceSubmission`/`Price` split — the *shape* (an append-only observation ledger distinct from current state) survives because it serves the same "never erase a real fact" governance already established elsewhere in this project; the crowdsourcing/moderation apparatus that originally motivated that shape in Generation 1 does not survive, and is not being recovered here.

---

## 7. Explicitly Not a Beer-Entity Attribute: Charged Price

Named here only to close a real risk of confusion: a person's reported charged price is **never** an attribute of `Sku`, `Listing`, or any other entity in this specification. It is a Session Object (Domain Model 1.0, Part 4) that transiently references a `Sku.id` and nothing more — no repository, no storage adapter, discarded the moment the session ends, and never even carried across the very next screen transition. It appears in this document exactly once, here, specifically to prevent a future implementer from reaching for it while filling in `Sku`'s attribute table above.

---

## Closing Artifacts

### 1. Canonical Beer Composition
```
Style ──1───* Beer ──1───* Sku ──1───* Listing ──1───* Price History
  │                          │
  └── Style Benchmark        └── Style Standing, Value Metrics (Computed Views, not stored facts)
```
A `Beer` is a name, a brewery, and a Style reference. Every fact that actually varies — size, container, ABV, price, availability — lives one level down, on `Sku`. Every fact about who currently supplies a Sku at what price lives one level further down, on `Listing`, today entirely absent from the shipped app. Every historical price fact lives one level below that, already being collected, entirely unsurfaced.

### 2. Attribute Ownership Matrix

| Entity | Owns |
|---|---|
| **Beer** | name, brewery, styleId, isCraft |
| **Style** | name, description, typicalAbvRange |
| **Sku** | sizeMl, containerType, packCount, abv, calories, legalPrice (derived), priceEffectiveDate, costPerLitre, costPerMlAlcohol, styleStanding, availabilityStatus, channel, gtin |
| **Listing** *(missing today)* | supplierCode/Name, its own price, its own effectiveDate, its own itemStatus, ksbclItemCode |
| **Style Benchmark** | p50 (shipped), p25/p75 (recovered, future), sampleSize, computedAt |
| **Price History** | price, effectiveDate, eventType, observedAt — one row per real change, forever |
| **(Session, not an entity)** | Charged Price — never owned by any catalog entity |

### 3. Mandatory vs. Optional Attributes
**Mandatory (Critical) at launch:** Beer.name, Beer.styleId, Sku.sizeMl/containerType, **Sku.abv (the true gate)**, Sku.legalPrice, Sku.availabilityStatus, Sku.channel, every fact's confidence tier.
**Recommended:** Brewery, priceEffectiveDate, Style Benchmark's p50, Style Standing.
**Optional:** Beer.isCraft, Style.description/typicalAbvRange, calories.
**Future:** Listing (the entire entity), gtin, Style Benchmark's p25/p75, Price History surfaced to any experience.

### 4. Persistent vs. Session Attributes
Everything in Sections 1–6 is persistent Reference Data or persistent Derived Knowledge. The one, sole, deliberate exception in the entire model is Charged Price (Section 7) — session-only, with no persistence mechanism permitted under any future refactor.

### 5. Immutable vs. Mutable Attributes
**Immutable:** every identity attribute (all `id` fields), Sku's sizeMl/containerType (a change is a new Sku, never an edit), `ksbclItemCode`, Price History's every field once written.
**Mutable:** name (rarely), brewery, styleId (rarely), abv/calories (only via genuine re-confirmation, never silently), legalPrice, priceEffectiveDate, availabilityStatus, channel, every Computed View (recomputed, not edited).

### 6. Dependencies Between Entities
`Sku` depends on `Beer` and, transitively, `Style`. `Listing` depends on `Sku`. `Price History` depends on `Listing`. `Style Benchmark` depends on `Style` and aggregates across every `Sku` currently belonging to it. `Value Metrics` and `Style Standing` are Computed Views with no independent existence — they depend on `Sku.legalPrice` + `Sku.abv`, and on `Style Benchmark`, respectively, recomputed fresh rather than stored as separate source-of-truth facts.

### 7. Evolution Over a Beer's Lifecycle
A `Beer` is created once, on first sighting of a genuinely new brand/style combination, and never deleted. Each `Sku` variant is created independently, the first time its specific size/container is seen, and likewise never deleted or renumbered — only its `availabilityStatus` changes, potentially many times, as it goes LIVE → DELISTED → LIVE again without ever losing identity. `Listing`s are created as suppliers are mapped and can each independently go dark while their parent `Sku` stays LIVE via a different Listing. `Price History` accumulates forever, one row per genuine change, never overwritten. `Style Benchmark` is the only entity in this model that is *recomputed*, not accumulated — its past values are never kept once a newer computation exists, since a standing judgment always wants the current distribution, not a history of past ones.

### 8. Remaining Product Decisions
- Whether `packCount` should remain part of Identity resolution at all (already flagged in the Project Brain and Decision Engine 2.0, restated here as it directly determines whether it belongs on `Sku` as an attribute or purely inside pipeline-internal matching logic).
- Whether `Listing` should be built as a real entity now, or remain a documented-but-unbuilt gap until a real multi-supplier display need is validated.
- Whether `Style.typicalAbvRange` (Curated, descriptive) risks being confused with `Style Benchmark` (Computed, statistical) badly enough to need a stronger naming distinction before either is built.
- Whether `isCraft` is worth recovering at all, given nothing currently depends on it and no reasoning surface has ever named a need for it.
- The same unresolved gap named in every document before this one: what happens to `costPerLitre`/`costPerMlAlcohol`/`styleStanding` when `Sku.abv` is null — restated here, one final time, at the exact attribute level where it will actually need to be implemented.
