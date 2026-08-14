# ValueBrew — Catalog Contract 1.0

*An interface contract, not an implementation document. This defines the exact structure of the production `catalog.json` artifact — every root key, every field on every entity, every relationship, and every rule that makes a given file valid or invalid. Grounded directly in the real, shipped Dart models (`lib/catalog/domain/catalog.dart`, `style.dart`, `benchmark.dart`, `lib/shared_domain/beer.dart`, `sku.dart`, all read in full for this document) and the actual current `catalog/catalog.json`, cross-referenced against Catalog Implementation Architecture, Catalog Builder Architecture, Catalog Specification 1.0, Beer Knowledge Model 2.0, Domain Model 1.0, Beer Entity Specification 1.0, and the Product Decisions Register. Version 1 only — no Version 2 field, no speculative extension, is proposed anywhere below. Every genuine incompatibility this document's own inspection surfaced is flagged separately, in its own paragraph, never silently resolved.*

---

## Part 1 — Purpose

**What `catalog.json` is.** The single, complete, self-contained snapshot of everything ValueBrew currently knows about the Karnataka beer catalog — every Style, every Beer, every purchasable Sku, and every computed Style Benchmark — as one JSON document. It is the one and only data source the running Flutter app ever reads for product knowledge; nothing in the app queries `pricing_data/` or `enrichment/` directly, at any point, confirmed by direct inspection of every real screen this session's four Experience Specifications already documented.

**Who produces it.** The Catalog Builder (`build_catalog.py`, per Catalog Implementation Architecture Part 3 and Part 7) — and only the Catalog Builder. It is generated, never hand-written, from two frozen inputs: `pricing_data/beer_master.csv` (the KSBCL pipeline's own automated output) and `enrichment/` (human-curated YAML, per Catalog Implementation Architecture Part 2). **[RC1 status note, 2026-08-14]:** `catalog/catalog.json` is now a real, Catalog-Builder-produced artifact matching this contract (`catalog_version: 2`, 8 beers, 57 SKUs) — it is no longer the hand-authored placeholder this paragraph originally contrasted it against.

**Who consumes it.** `lib/catalog/data/catalog_repository.dart`'s `CatalogRepository.loadCatalog()`, exclusively — the app's already-built bundled-asset → local-cache → remote-fetch loader, unchanged by this document. Every screen downstream (Home, Recommendation, Beer Detail, Price Verification) reads only the parsed `Catalog` object this repository returns; none of them touch raw JSON.

**Who is allowed to modify it.** Nobody, directly. `catalog/catalog.json` is a build output, not a source file — the same discipline Catalog Implementation Architecture already applies to `pricing_data/beer_master.csv` (pipeline-owned, never hand-edited) extends here: any desired change to the catalog's content is made by editing `enrichment/` and re-running the Catalog Builder, never by hand-editing `catalog/catalog.json` itself. A hand-edit would be immediately, silently overwritten by the next build, and would carry no provenance — exactly the failure mode Catalog Builder Architecture's Part 1 (immutable vs. mutable facts) exists to prevent.

---

## Part 2 — Top-Level Structure

Confirmed directly from `Catalog.fromJson`/`toJson` (`lib/catalog/domain/catalog.dart`) — six root keys, no more, no fewer:

| Root key | Type | Required | Owner | Lifecycle |
|---|---|---|---|---|
| `catalog_version` | integer | yes | Catalog Builder, Step 9 | Monotonically incremented by exactly one on every real publish (Catalog Implementation Architecture Part 6). The single field `CatalogRepository`/`HttpCatalogRemoteSource` already compare to decide whether a fetched catalog is newer than what's cached — this document does not change that mechanism, only confirms this field's contract. |
| `generated_at` | ISO-8601 datetime string | yes | Catalog Builder, Step 9 | Set once, at build time, to the build's own wall-clock time — parsed via `DateTime.parse`, matching `Sku.priceLastChecked`'s own parsing convention. |
| `styles` | array of Style | yes (may be empty in principle; never empty in a real published catalog, since every Beer requires a resolvable Style — see Part 7) | Catalog Builder, Step 5 | Rebuilt in full on every build — not incrementally patched. |
| `beers` | array of Beer | yes (same note) | Catalog Builder, Step 5 | Rebuilt in full on every build. |
| `skus` | array of Sku | yes (same note) | Catalog Builder, Steps 6–8 | Rebuilt in full on every build. |
| `benchmarks` | array of Benchmark | yes; **may legitimately be empty**, and individual Styles may legitimately have none — thin-sample graceful omission is real, frozen behavior (Catalog Specification 1.0, Style Benchmark domain) | Catalog Builder, Step 7 | Fully recomputed on every build — a Benchmark is never carried forward from a prior catalog version, since it must always reflect the current Sku population exactly. |

**No other root key exists, and none is proposed.** In particular, `gtin`, `verification_history`, and any of the Product Enrichment / Future Expansion fields Catalog Specification 1.0 names (Flavor, Aroma, Food Pairing, Images) have no root-level or nested representation anywhere in the real schema today — consistent with that document's own explicit "named, not specified" treatment, and with this document's own instruction not to design Version 2.

---

## Part 3 — Style Schema

| Field | Type | Required | Source | Confidence |
|---|---|---|---|---|
| `id` | string | yes | Assigned at first enrichment (`style_key`, per Catalog Implementation Architecture Part 2) | — (identity, not a fact) |
| `name` | string | yes | Manual curation | Curated |
| `description` | string | yes | Manual curation | Curated |

**Validation rules:** `id` unique within the `styles` array (not currently enforced anywhere in code — see Part 8's flagged gap). No field is optional; the real `Style.fromJson` (`lib/catalog/domain/style.dart`) casts all three directly with `as String`, meaning a missing key throws rather than defaulting.

**Flagged, not resolved: `typicalAbvRange` is not part of the Version 1 contract.** Beer Entity Specification 1.0 (§8, "Remaining Product Decisions") proposes adding `Style.typicalAbvRange` — Curated, descriptive — but this field does not exist anywhere in the real `Style` class today, and Product Decisions Register D14 confirms it as one of the still-open, low-stakes items this proposal was never formally adopted from. **This document does not add it.** Per the explicit instruction not to design Version 2: if this field is ever adopted, it enters as a new, additive, optional field under the versioning discipline Part 9 defines — not retrofitted here.

---

## Part 4 — Beer Schema

| Field | Type | Required | Source | Confidence |
|---|---|---|---|---|
| `id` | string | yes | Assigned at first enrichment (`beer_key`, per Catalog Implementation Architecture Part 2) | — (identity) |
| `name` | string | yes | KSBCL `item_name_raw`/`display_name`, cleaned by manual observation | Verified (raw), Curated (cleaned display form) |
| `brewery` | string | yes | KSBCL `supplier_name` (Verified) — see the flagged licensed-supplier-vs-brand-owner caveat below | Verified (as licensed supplier), not yet distinguished from a marketing-brand identity |
| `style_id` | string | yes | Manual curation, references `Style.id` | Curated |
| `is_craft` | boolean | yes | Manual curation | Curated |

**Beer vs. Sku responsibilities — restated precisely, since this is the one distinction the whole schema depends on.** `Beer` is category-level identity: what it's called, who makes it, what style it belongs to, whether it's craft. `Sku` is the purchasable unit: one specific pack size, at one specific price, with its own ABV and its own computed Value Metrics. A Beer sold in three pack sizes is one `Beer` row and three `Sku` rows — confirmed directly by both the real `Sku.beerId` reference field and the real `Sku` class's own doc comment ("The price, Value Score, and provenance shown on the Beer Detail screen are all attributes of a Sku, not of the Beer itself, since a single beer can have multiple sizes with different per-unit value").

**Identity rules.** `Beer.id` is **not** the same identity space as KSBCL's `canonical_product_id` — this is the single most important identity fact in this whole document, already surfaced in Catalog Implementation Architecture Part 2 and restated here because it governs the entire Beer schema's validity. `canonical_product_id` is SKU-grain (one per pack size); `Beer.id` is a manually-assigned grouping across one or more `canonical_product_id`s. There is no automated function anywhere in this canon that derives one from the other — every `Beer.id` in a real published catalog traces back to a human's explicit `enrichment/beers/<beer_key>.yaml` file.

**Flagged, not silently resolved: the licensed-supplier-vs-brand-owner distinction inside `brewery`.** The Architecture Reconciliation Report already confirmed real cases (Budweiser bottled by S P R Distilleries; Guinness imported by Brindco) where KSBCL's supplier-of-record is not the entity a person would recognize as "who brews this." Catalog Builder Architecture Part 4 names this as still-open. **This document's schema has exactly one `brewery` string field and no separate field for a distinct marketing-brand identity** — the schema itself does not currently support representing both facts at once. This is not a new finding; it is restated here as a schema-level constraint, not resolved.

---

## Part 5 — Sku Schema

Confirmed directly from `lib/shared_domain/sku.dart`, the real, shipped class — thirteen fields, all non-nullable:

| Field | Type | Required | Classification |
|---|---|---|---|
| `id` | string | yes | Identity (Catalog Builder, at join time — Catalog Implementation Architecture Part 2's `canonical_product_id`, or a stable derivative of it) |
| `beer_id` | string | yes | Identity (references `Beer.id`, assigned at enrichment time) |
| `size_ml` | integer | yes | **Pipeline-derived** — KSBCL `pack_size_ml` (Stage 3 structured extraction) |
| `package_type` | enum string: `bottle` \| `can` \| `pint` | yes | **Pipeline-derived**, with a flagged incompatibility — see below |
| `abv` | number (double) | yes | **Manually enriched** — no automated source exists (Catalog Builder Architecture §0.3, Catalog Specification 1.0's own ABV domain) |
| `calories` | integer | yes | **Computed** at build time from the enrichment layer's manually-cited `calories_per_100ml` (a concentration, matching what manufacturer sources actually publish) and this Sku's own `size_ml` — same sourcing constraint as ABV one layer up, no KSBCL source exists |
| `price` | number (double) | yes | **Pipeline-derived** — KSBCL `declared_price`/`mrp` via `beer_master.csv` (the Legal Price) |
| `price_last_checked` | date string | yes | **Pipeline-derived** — KSBCL `effective_date` |
| `price_source` | string | yes | **Pipeline-derived** — a fixed provenance label (e.g. `"karnataka_excise_mrp_2026"`), set by the Catalog Builder, not per-row from `beer_master.csv` directly |
| `cost_per_litre` | number (double) | yes | **Computed** — from `price` and `size_ml` |
| `cost_per_ml_alcohol` | number (double) | yes | **Computed** — from `price`, `size_ml`, and `abv` |
| `value_score` | integer | yes | **Computed** — an inverted percentile of `cost_per_ml_alcohol` within the Sku's Style Benchmark |
| `value_verdict` | enum string: `great_value` \| `fair_value` \| `overpriced` | yes | **Computed**, derived directly from `value_score` |

**Forbidden fields — stated explicitly, not merely absent.** `gtin`/`gtin_confidence`: reserved in `beer_master.csv` itself (Catalog Builder Architecture §0.3) but **not present anywhere in the real `Sku` class**, and not added by this document, consistent with the instruction not to design Version 2. **Observed/Charged Price must never appear anywhere in `catalog.json`, under any field name, at any confidence tier** — this is not a Version 1 omission to fix later; it is a permanent, canon-wide prohibition, stated identically across the Beer Knowledge Model, every Screen Contract, and this session's own Price Verification Experience Specification. `Sku` has no field for it today and must never gain one.

**Flagged, real, evidence-based incompatibility: `package_type`'s closed enum does not cover KSBCL's actual container-type vocabulary.** The real `PackageType.fromJson` (`lib/shared_domain/sku.dart`) recognizes exactly three values — `bottle`, `can`, `pint` — and **throws `ArgumentError` on anything else**, with no fallback case. The KSBCL pipeline's own `container_type` field (Stage 3, Catalog Builder Architecture §0) uses a *different* five-value controlled vocabulary — `bottle | can | pet_bottle | tetra_pack | unknown` — and the real 2026-06 pipeline run recorded `container_type_unknown_rate: 0.296` (`normalized_run_summary.json`, directly inspected) — **roughly 30% of real rows currently normalize to `unknown`, a value the app's `PackageType` enum cannot represent at all.** Additionally, `pint` exists in the app's enum with no KSBCL equivalent (it presumably anticipates a future on-premise/draught concept never present in KSBCL's off-premise retail data). **This is a genuine schema incompatibility between the real Catalog Builder's primary data source and the real app model, confirmed by direct inspection of both, and it is not resolved here** — any SKU whose KSBCL `container_type` is `unknown`, `pet_bottle`, or `tetra_pack` cannot be assembled into a valid `Sku` today without either (a) excluding it from `catalog.json` entirely at the Catalog Builder's validation gate (Part 8, below), or (b) a Product/Engineering Decision to extend `PackageType`'s enum — which this document does not make, since doing so would be designing Version 2. Catalog Implementation Architecture's own Part 3 (Step 10, structural round-trip check) is the concrete mechanism that already catches this today, by rejecting the row rather than crashing the app.

---

## Part 6 — Benchmark Schema

Contract only, per the explicit instruction — no computation logic. Confirmed directly from `lib/catalog/domain/benchmark.dart`:

| Field | Type | Required |
|---|---|---|
| `style_id` | string | yes |
| `avg_cost_per_ml_alcohol` | number (double) | yes |
| `p25` | number (double) | yes |
| `p50` | number (double) | yes |
| `p75` | number (double) | yes |
| `sample_size` | integer | yes |

Every field is Computed, with no independently sourced or curated component — Catalog Specification 1.0 already states this exactly ("Computed Fact... never independently sourced"). A `Benchmark` entry exists only when at least one Sku shares its `style_id`; a Style with no Skus yet, or too few for a meaningful distribution, simply has no corresponding `Benchmark` row — omission, not a null or zero-filled placeholder.

**Flagged documentation error, discovered by this document's own direct code inspection, not previously reported.** Catalog Specification 1.0's own Style Benchmark domain entry (Part 2) states: *"the current shipped model uses only a median split, having rejected a fuller p25/p50/p75 percentile design as 'uncited' during its own review... this document... recommends reintroducing it once real data volume supports it — not required for launch."* **This is factually incorrect against the real, shipped code.** `lib/catalog/domain/benchmark.dart` already implements the full `avg`/`p25`/`p50`/`p75`/`sample_size` structure today, and the real Beer Detail screen already reads `benchmark.p50` directly (confirmed in the Beer Detail Experience Specification's own inspection of `classifyStyleStanding`). Catalog Specification 1.0 appears to describe an earlier, superseded state of the model, not its current, real one. **This document does not silently correct Catalog Specification 1.0** — that document is frozen canon per this document's own instructions — but flags the discrepancy here, plainly, since a future reader relying on Catalog Specification 1.0's own text would be misled about what the real schema already supports.

---

## Part 7 — Cross-Reference Integrity

Every foreign-key relationship in the schema, stated exhaustively:

| Reference | Must always resolve? | May be null? | Forbidden |
|---|---|---|---|
| `Sku.beer_id` → `Beer.id` | **Yes, always** — no real screen has any handling for an unresolved Sku (`resolveBeer` returning `null` is treated as a Recovery/"couldn't be found" condition everywhere it's checked, e.g. Beer Detail's own `ErrorStateView`) | No — the field itself is non-nullable in `Sku`'s real Dart type | A `Sku` whose `beer_id` doesn't appear in `beers` |
| `Beer.style_id` → `Style.id` | **Yes, always** — `Beer.styleId` is non-nullable, and every real screen that resolves it (`resolveStyle`) treats a `null` result as a display gap ("Unknown style"), never a crash, but a *dangling reference* (an ID that resolves to nothing at all) is a data error, not a legitimate "no style" state | No, the field itself | A `Beer` whose `style_id` doesn't appear in `styles` |
| `Benchmark.style_id` → `Style.id` | Yes, when the Benchmark entry exists at all | Not applicable — a Style simply has zero Benchmark entries when no Computed distribution exists yet; this is the schema's *only* legitimate "optional relationship," expressed by array absence, never by a null field | A `Benchmark` whose `style_id` doesn't appear in `styles` |

**A structural fact worth stating plainly, since it shapes every rule above: the real schema has zero nullable fields anywhere, on any of the four entities.** Every field on `Style`, `Beer`, `Sku`, and `Benchmark` is declared `required` in its Dart constructor and cast directly (`as String`, `as num`) in its `fromJson`, with no null-coalescing fallback anywhere. **This means every "graceful omission" the canon describes (Style Benchmark's absence, in particular) is implemented at the array level — an entity simply doesn't appear — never at the field level.** There is no `Sku` with a `null` `abv`, no `Beer` with a `null` `style_id` — either the fact is fully known and the entity is included, or it isn't known and the entity is excluded from that build entirely (Catalog Implementation Architecture Part 3, Step 4's `unenriched_skus.csv`). This is a significant, evidence-based clarification of how Product Decisions Register D1 (the incomplete-ABV gap) actually manifests at the schema level: **there is no schema mechanism today for publishing a Sku with an unknown ABV at all** — D1's three named options ("silently exclude it, include with an explicit caveat, or something else") collapse, at the current schema's own structural limits, to exactly two live options: exclude the Sku, or extend the schema to add a nullable/optional ABV field (which would itself be a Version 2 change, not made here).

**Forbidden, stated explicitly:** duplicate `id` values within any single array (`styles`, `beers`, or `skus`) — not currently validated anywhere in the real code (`Catalog.fromJson` performs no uniqueness check), and flagged here as a gap for Part 8's validation contract to close, not the app's own parsing layer.

---

## Part 8 — Validation Contract

**What makes a `catalog.json` valid, in order of how the real app would actually encounter a failure:**

1. **Valid JSON**, parseable by `jsonDecode` — enforced today by `CatalogRepository._parseCatalog`, throwing `CatalogParseException` otherwise.
2. **Top-level shape matches Part 2** — all six keys present, each of the correct type — enforced today by `Catalog.fromJson`'s own direct casts.
3. **Every entity's fields match its own schema (Parts 3–6) exactly** — every required field present, every enum value within its closed set — enforced today by each entity's own `fromJson`, which throws on any mismatch (a missing key, a wrong type, or an unrecognized enum string, per Part 5's flagged `package_type` incompatibility).
4. **Every cross-reference in Part 7 resolves** — **not enforced anywhere in the real app code today**, a genuine, previously-unflagged gap this document surfaces: `Catalog.fromJson` will happily parse a `Sku` whose `beer_id` matches nothing in `beers`, and the failure only surfaces later, silently, as a `null` from `resolveBeer` wherever that Sku is actually displayed. **This is exactly why Catalog Implementation Architecture's own Step 10 (structural round-trip and rule check) must run before publication** — it is the only place in the whole system this class of error can be caught before it reaches a real user's device.
5. **Every rule in Catalog Builder Architecture's own Part 7** (duplicate identities, invalid ABV, missing mandatory fields, style mismatch, orphan references, broken images, stale prices, listing inconsistencies) — reused here unchanged, not re-derived.

**What blocks publication (Step 11 of the Catalog Builder never runs):** any failure at levels 2–5 above. Level 1 (invalid JSON) is not a real publication scenario — it would mean the Catalog Builder itself failed to serialize its own output, a programming defect, not a data-quality one.

**What is a warning, not a block:** exactly what Catalog Implementation Architecture's own Part 5 already names as warnings-only (stale-price flags, listing-inconsistency flags, single-source-ABV-with-no-corroboration) — this document adds nothing new to that list, since none of those concern the schema contract itself.

---

## Part 9 — Versioning

**`catalog_version` already governs content freshness, not schema shape — this document does not change that, only makes the distinction explicit.** The field exists so `CatalogRepository` can prefer a newer catalog over an older one; it says nothing about whether the newer catalog's *shape* is one an older app build can still parse.

**The real, load-bearing constraint this document's own inspection surfaces: an old, already-installed app can receive a brand-new `catalog.json` at any time, with no app-store review gate in between.** `HttpCatalogRemoteSource` fetches directly from the jsDelivr CDN mirror on every check (Catalog Implementation Architecture §0.2) — there is no version negotiation, no "minimum supported schema" handshake, and no mechanism for an old app build to reject a catalog whose shape it doesn't understand except by crashing on parse (`CatalogParseException`) and falling back to whatever it already had cached, per `CatalogRepository`'s own existing try/catch-and-ignore behavior around the remote-fetch step. **This means schema evolution must be safe for the oldest still-installed app build to encounter at any time, not just for the current one.**

**What this makes safe, confirmed directly from how Dart's `fromJson` methods actually read a `Map<String, dynamic>`:** adding a **new, optional-in-practice** root or entity field is safe, because every real `fromJson` reads named keys explicitly and never validates the *absence* of extra, unrecognized keys — an old app parsing a catalog with one new field it doesn't know about simply never reads that key, and continues working exactly as before. **What is not safe, and would require a coordinated app-side change first, released and adopted before the corresponding catalog.json ever ships:** renaming an existing key, changing an existing field's type, removing a field an old app's `fromJson` still requires, or adding a new value to a closed enum an old app's `fromJson` doesn't recognize (exactly Part 5's `package_type` incompatibility, in miniature — this is precisely the failure mode that already exists today, not a hypothetical future one). **Recommendation, not a decision this document makes on its own authority:** any future schema change should default to purely additive, optional fields wherever possible, and any non-additive change should be treated as requiring its own deliberate compatibility plan — a new `catalog_version` alone is not sufficient protection, since it only ever signals "prefer this one," never "the previous app build can safely read this one."

---

## Part 10 — Annotated Example

*Illustrative, not sourced from any real `beer_master.csv` row — constructed to show every cross-reference clearly, per the instruction. Field names and shapes match Parts 3–6 exactly.*

```json
{
  "catalog_version": 4,
  "generated_at": "2026-09-01T02:15:00Z",

  "styles": [
    {
      "id": "strong_lager",
      "name": "Strong Lager",
      "description": "Higher-ABV lager, typically 7-8% — a distinct peer group from standard lager."
    }
  ],

  "beers": [
    {
      "id": "tuborg_strong",
      "name": "Tuborg Strong",
      "brewery": "Carlsberg India",
      "style_id": "strong_lager",
      "is_craft": false
    }
  ],

  "skus": [
    {
      "id": "tuborg_strong_650",
      "beer_id": "tuborg_strong",
      "size_ml": 650,
      "package_type": "bottle",
      "abv": 8.0,
      "calories": 310,
      "price": 145,
      "price_last_checked": "2026-08-30",
      "price_source": "karnataka_excise_mrp_2026",
      "cost_per_litre": 223.08,
      "cost_per_ml_alcohol": 2.79,
      "value_score": 81,
      "value_verdict": "great_value"
    }
  ],

  "benchmarks": [
    {
      "style_id": "strong_lager",
      "avg_cost_per_ml_alcohol": 3.05,
      "p25": 2.60,
      "p50": 2.95,
      "p75": 3.40,
      "sample_size": 14
    }
  ]
}
```

**How they reference one another, read left to right through the data:** `skus[0].beer_id` (`"tuborg_strong"`) resolves to `beers[0].id` — this Sku is one pack size of that Beer (Part 4/Part 7). `beers[0].style_id` (`"strong_lager"`) resolves to `styles[0].id` — this Beer belongs to that Style (Part 4/Part 7). `benchmarks[0].style_id` (`"strong_lager"`) resolves to the same `styles[0].id` — this is the peer-group distribution that Sku's `value_score` (81) was computed against, using `cost_per_ml_alcohol` (2.79) relative to the Benchmark's own `p25`/`p50`/`p75` (2.60/2.95/3.40) — a figure below the style's median, which is exactly why `value_verdict` reads `"great_value"`, per `Sku`'s own doc comment ("Higher is better value") and `ValueVerdict`'s own display mapping (confirmed in `display_formatting.dart`, read earlier this session: `great_value → "Great value"`). Note `sample_size: 14` on the Benchmark — a real, populated distribution, not the thin-sample case Catalog Specification 1.0 describes as warranting graceful omission; a Style with only one or two Skus would instead have no `benchmarks` entry at all, per Part 6.
