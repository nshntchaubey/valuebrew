# ValueBrew — Beer Knowledge Base Architecture

*Not catalog.json. Not the app model. Not the KSBCL pipeline. This document specifies the human-maintained knowledge repository those three are downstream of — the `enrichment/` directory Catalog Implementation Architecture named and gave an initial shape, elevated here to its own complete, dedicated specification. Nothing below redesigns the Catalog Builder, catalog.json's schema, the Beer/Sku/Style/Benchmark entities, or the enrichment editing workflow — every one of those is treated as frozen, cited by reference, never re-derived. Grounded in Beer Knowledge Model 2.0, Beer Entity Specification 1.0, Catalog Specification 1.0, Catalog Builder Architecture, Catalog Implementation Architecture, Catalog Builder Implementation Design, the Catalog Enrichment Playbook, Catalog Contract 1.0, the Product Decisions Register, and direct, repeated inspection of `pricing_data/`, `catalog/`, `tool/ksbcl_pricing_pipeline/`, and the enterprise catalog research corpus across this session — confirmed once more before writing this document that `enrichment/` did not yet exist anywhere in the repository at the time. **[RC1 status note, 2026-08-14]: `enrichment/` now exists — 65 curated beer families, 346 grouped SKUs, per `docs/PROJECT-BRAIN.md` §16.***

---

## Part 1 — Purpose

**Why this repository exists.** Catalog Builder Architecture already established the founding fact this whole document extends: KSBCL's own government price list — the entire automated input to this system — contains no ABV, no Style, and no brand identity distinct from the licensed supplier of record. Not a gap the pipeline failed to close; a direct consequence of what the source document is. Every fact that makes a beer *recognizable* rather than merely *priced* has to come from somewhere else, and that somewhere is a human, reading a label or a brewery's own page, recording what they found. This repository is where that recording happens, permanently, in one place, structured so it can be trusted and reused rather than re-discovered every time.

**Why `catalog.json` is not the source of truth.** `catalog.json` is a build output — regenerated in full on every real publish (Catalog Contract 1.0 Part 2), disposable and perfectly reconstructable from its two real inputs at any time. If it were deleted entirely tonight, nothing real would be lost — a fresh Catalog Builder run against `pricing_data/beer_master.csv` and this repository would reproduce it exactly. **The reverse is not true.** `catalog.json`'s own schema, confirmed directly against the real Dart models in Catalog Contract 1.0, carries no source attribution, no observed date, no note about which brewery's page an ABV came from or when someone last checked it — every one of those facts exists only here, in this repository, never downstream of it. Delete this repository and months of real, hard-won research vanish with no way to reconstruct it from `catalog.json` alone. **This repository is the actual asset. `catalog.json` is a lossy projection of it, produced for exactly one consumer — the Flutter app — that doesn't need to know where a fact came from, only what it currently is.**

---

## Part 2 — Repository Layout

Exactly the structure Catalog Implementation Architecture Part 1 already established, given its complete, final shape here. **[RC7.7 addition, 2026-08-17]:** one new file type, `rejected_evidence.yaml`, was added — see Part 11. Every other statement below about "no new directory or file type" predates that addition and should be read as applying to everything except it.

```
enrichment/
  README.md               # editing guide — points here, and to the Catalog Enrichment Playbook
  styles.yaml              # the full style vocabulary — one flat file, not one-per-style
  rejected_evidence.yaml   # researched evidence found and deliberately not curated (Part 11)
  beers/
    <beer_key>.yaml         # one file per Beer — every pack size it comes in, together
```

**Naming.** `<beer_key>` is a stable, human-assigned, lowercase snake_case slug (`kingfisher_premium.yaml`, `tuborg_strong.yaml`) — chosen once, at the moment a beer is first enriched, and never renamed casually afterward, since it is also the literal `Beer.id` a real, already-published `catalog.json` may already reference (Catalog Contract 1.0 Part 4). Renaming a `beer_key` after publication is a real identity change, not a cosmetic edit — treat it with the same seriousness Catalog Builder Architecture already gives to any identity-affecting change.

**Organization.** Flat under `beers/` — no subdirectory by style, brewery, or first letter. Catalog Implementation Architecture's own Part 8 already confirmed this scales cleanly through several thousand files; a nested structure would only add a layer of arbitrary categorization (which subdirectory does a beer with an ambiguous style belong under?) with no real benefit at this system's actual scale.

**What does not live here, stated once so it doesn't need repeating in every later Part:** anything Verified/government-sourced (price, size, container type — `pricing_data/beer_master.csv`, never duplicated here); anything Computed (Benchmark, Value Score, cost-per-ml-alcohol — `catalog.json` only, generated fresh every build); the published catalog itself.

---

## Part 3 — Beer YAML

*The complete, canonical field list — consolidating what Catalog Implementation Architecture Part 2 introduced with what Catalog Contract 1.0's own frozen Beer/Sku schema requires as input, given its final, authoritative shape here.*

| Field | Required | Type | Notes |
|---|---|---|---|
| `beer_key` | **Required** | string | Matches the filename; becomes `catalog.json`'s `Beer.id` verbatim at build time |
| `canonical_product_ids` | **Required**, ≥1 | list of string | Every KSBCL `canonical_product_id` (from `pricing_data/item_code_canonical_map.csv`) that is a pack size of this beer — the sole join key the Catalog Builder uses (Catalog Builder Implementation Design Part 4) |
| `name` | **Required** | string | Cleaned display name — see Catalog Builder Architecture Part 4's own "Curated cleaned display name" treatment |
| `brewery` | **Required** | string | Defaults to `beer_master.csv`'s own `supplier_name`; see Catalog Contract 1.0 Part 4's own flagged, still-open licensed-supplier-vs-brand-owner caveat — not resolved by this document |
| `style` | **Required**, or explicitly `unknown` | string | References a `style_key` in `styles.yaml` — see Part 4 |
| `is_craft` | Optional, defaults `false` | boolean | Product Decisions Register D14's own low-stakes item; not required to have a considered value |
| `abv` | **Required**, or explicitly `unknown` | source-attribution block (Part 5) | Beer-level default, applied to every listed SKU unless overridden |
| `calories_per_100ml` | **Required**, or explicitly `unknown` | source-attribution block (Part 5) | Milestone 7's own fix for a real gap this table never covered: manufacturers publish a concentration (kcal per 100ml), not a per-pack total, so that is exactly what this field holds. `Sku.calories`, the per-pack total the app shows, is computed once at build time from this value and each SKU's own `size_ml` — never entered manually, never duplicated per pack size, no per-SKU override needed. **[RC6.0 correction, 2026-08-15]:** this row's own requiredness (the key must be present, as a real block or the literal `unknown`) is unchanged and still enforced by `enrichment_schema.py`. What changed is downstream: `Sku.calories` is **no longer** required-and-non-nullable at the catalog-publication level — Product Decisions Register D22 downgraded a beer's unresolved `calories_per_100ml` from a build-blocking condition to a `missing_calories` warning (`business_rules.py`). This row's own "Required" marking, and the universal rule restated just below, both now have an explicit exception — see there. |
| `images` | Optional | list | Product Decisions Register D15 remains open on whether this is ever required — treated as optional here, unchanged from Catalog Implementation Architecture's own position |
| `skus` | Optional | map, keyed by `canonical_product_id` | Per-SKU overrides only, for a fact that genuinely differs by pack size (Part 2 of Catalog Implementation Architecture's own worked example: a draught-strength variant with a different ABV than the packaged default) |

**Required vs. optional, restated as a single, plain rule:** every field above marked Required must resolve to either a real, cited value **or** an explicit `unknown` marker (Part 5) — that part is unconditional; a field simply absent from the file (neither filled nor marked `unknown`) is a structural validation failure (Part 7), not a silent gap, for every Required field with no exception. **What is no longer universally true, since Product Decisions Register D22 (RC6.0 correction):** resolving to a real value (not `unknown`) is not the same as *needing* one to publish. For `abv` and `style`, an unresolved `Required` field (still marked `unknown`) does block a beer from entering a catalog build, exactly as this rule originally stated. For `calories_per_100ml` specifically, it no longer does — a beer with `calories_per_100ml: unknown` can enter a catalog build, carrying a `missing_calories` warning instead of being excluded. The structural requirement (the key exists, as a block or `unknown`) and the publication consequence (blocks vs. warns) are now two separately-tracked things for this one field, where they used to be the same thing for every Required field alike.

**Lifecycle.** Created once, the first time any of a beer's pack sizes is enriched (Catalog Enrichment Playbook Part 2, step 3). Edited indefinitely afterward as better sources are found, new pack sizes appear in `beer_master.csv`, or a correction is needed (Part 6). Never deleted — see Part 6's deprecation treatment.

**Ownership.** The founder, today, per the Catalog Enrichment Playbook — this document does not change who edits these files, only formalizes their final shape.

---

## Part 4 — Style Registry

`styles.yaml`, flat, per Catalog Implementation Architecture Part 2:

| Field | Required | Notes |
|---|---|---|
| `style_key` | Required | Referenced by every Beer's `style` field |
| `name` | Required | Display name |
| `description` | Required | Short, human-readable |

**`typical_abv_range` is not part of this repository's frozen contract, and is not added here.** Beer Entity Specification 1.0 proposed it; Catalog Contract 1.0 explicitly declined to adopt it into Version 1, on the record, and this document does not silently reopen that decision — restated here rather than redesigned.

**Benchmark ownership — the sharpest boundary this Part draws, worth stating with real emphasis.** `Benchmark` (per-style `avg`/`p25`/`p50`/`p75`/`sample_size`) **has no representation anywhere in this repository, and never will.** It is Computed, deterministically, from whatever Sku population a given catalog build actually admits — Catalog Contract 1.0 Part 6 already states this exactly, and Catalog Builder Implementation Design's own `benchmarks.py` module is where it's actually produced. A founder editing `enrichment/` has no way to set a Benchmark value, and should never look for one here — it doesn't exist until the Catalog Builder computes it fresh, every single build.

**Vocabulary governance.** `styles.yaml` is deliberately kept small — Catalog Specification 1.0's own framing, "a few dozen entries, not hundreds" — and the Catalog Enrichment Playbook's own Part 6 already states the operating discipline: check whether an existing style genuinely fits before adding a new one, and only add one when an existing style would actually misrepresent a beer's peer group for Value Score comparison. This document adds nothing to that rule beyond restating it as this file's own governing constraint.

---

## Part 5 — Source Attribution

**The attribution unit**, applied everywhere a Curated fact is recorded (today: `abv`; extensible without new architecture to any future Curated field, per Catalog Builder Architecture Part 4's own general pattern):

| Field | Required | Notes |
|---|---|---|
| `value` | Required, unless the whole block is `unknown` | The fact itself |
| `source_type` | Required | `manufacturer` \| `manual_observation` — the two tiers the Catalog Enrichment Playbook's own research workflow (Part 4 of that document) actually produces; a retailer listing is explicitly corroboration-only and is never recorded as a claim's `source_type` on its own |
| `source_name` | Required | A specific citation — "United Breweries official product page," not merely "the internet" |
| `observed_at` | Required | The date this specific fact was checked — never the date the file was created, since a file accumulates facts checked on different dates |
| `observed_by` | Required | Who — today, always the founder; the field exists so this remains true and checkable as more people are ever involved |

**`manual_observation` includes verified photographs.** A clear, verified photograph of the manufacturer's own printed label — not only physical possession of the product — satisfies `manual_observation`, provided the founder personally confirms the photograph matches the exact beer and pack size, and `source_name` cites the specific photograph (or the page containing it), never the general hosting site. This does not create a new `source_type` value and does not relax any of the four required fields above.

**Evidence.** Never a plain scalar. A `value` with no `source_name`/`observed_at` attached is not a fact this repository can hold — Part 5 of Catalog Builder Architecture's own already-frozen rule ("an ABV claim sourced to nothing citable" is a validation failure, Part 7 below) is what this attribution unit exists to make mechanically enforceable, not merely advisory.

**Confidence.** Every fact recorded through this unit is **Curated**, always — never Verified (KSBCL never states it, so this repository can never promote it to that tier no matter how many times it's confirmed) and never Computed (nothing here is derived; it's observed). This is the exact three-tier language Beer Knowledge Model 2.0 and Catalog Builder Architecture already use, reused here without variation.

**Observed dates.** Recorded per-fact, not per-file — a beer whose ABV was checked in one session and whose Style was assigned in a different, later session carries two different `observed_at` values, one per attribution block, never one shared file-level date pretending both facts are equally fresh.

**Verification — no periodic re-check mechanism exists, and none is invented here.** Catalog Specification 1.0's own Freshness domain already states the operating discipline generally ("must be deliberately recorded at manual-collection time"); nothing in any frozen document establishes a cadence for re-verifying an already-Curated fact, and this document does not add one. A fact recorded once, correctly, with a real citation, remains valid until something — a spot check (Catalog Enrichment Playbook Part 8), a correction (Part 6, below), or a future reformulation risk someone happens to notice — prompts a human to look again.

---

## Part 6 — Versioning

**History and Git — the entire mechanism, no new system layered on top.** Every file in this repository is a normal, git-tracked text file. Every change is a normal commit. This is not a simplification made for this document's convenience — it is Catalog Implementation Architecture's own already-frozen position (Part 6: "Enrichment data is versioned by git history — not a new system, a direct reuse of the one this repository already has"), restated here as this repository's permanent versioning mechanism.

**Corrections.** When a better source is found — a brewery corrects a published ABV, a founder notices a Style was misassigned — the fix is an ordinary edit, an ordinary commit. The old value is not specially preserved anywhere inside the YAML file itself; it is preserved in git history, retrievable via `git log`/`git blame` the same way any other correction to any other file in this repository already is. This is a deliberate difference from KSBCL's own `beer_price_history.csv`, worth naming so it isn't mistaken for an inconsistency: that ledger is append-only because it exists to prove what the government actually published, at a specific date, forever — a legal/audit requirement. A Curated fact carries no equivalent legal weight; git's own ordinary history is sufficient provenance for "we used to think this ABV was X, we now believe it's Y, here's when and why that changed."

**Deprecation.** **Recommendation, not previously specified anywhere, offered here since the request asks for it directly:** when every `canonical_product_id` a beer file lists has gone `DELISTED` in `pricing_data/item_code_canonical_map.csv`, the file is **not deleted.** It simply stops being joinable to any `LIVE` row, and the Catalog Builder's own join logic (Catalog Builder Implementation Design Part 4) naturally excludes it from the next `catalog.json` without any special-casing. This mirrors the KSBCL pipeline's own established discipline exactly — "row is never deleted... deleting it would make a future reappearance indistinguishable from a genuinely new Item Code" (KSBCL Beer Pricing Pipeline Architecture §7.2) — extended here to enrichment files for an identical reason: a delisted beer returning to the market later should re-enter cleanly, with its existing research intact, not force someone to re-research a beer this repository already knew.

---

## Part 7 — Validation

*Reused directly from Catalog Builder Implementation Design's own Part 6, scoped here specifically to what validates this repository, distinct from what only makes sense once it's joined against the pipeline.*

**Structural — validates this repository in complete isolation, no other input needed.** Every YAML file parses; every Required field (Part 3) is present, either filled or explicitly `unknown`; every attribution block (Part 5) that isn't `unknown` carries all five of its own required fields; every `style` reference resolves to a real `style_key` in `styles.yaml`. This is `enrichment_schema.py`'s own already-specified job (Catalog Builder Implementation Design Part 3), reused unchanged here.

**Cross-reference — validates this repository against its one real external dependency, `pricing_data/`.** Every `canonical_product_id` a beer file lists actually appears somewhere in the current `pricing_data/item_code_canonical_map.csv`; no `canonical_product_id` is claimed by two different `beer_key`s at once (Catalog Builder Implementation Design Part 4's own flagged join-layer rule). This is the one validation category that cannot run against this repository alone — it requires the pipeline's own current output as a second input, which is exactly why it's a distinct category from structural validation above.

**Publication — validates whether a given beer, having passed the two categories above, is actually allowed to enter a `catalog.json` build.** Every field Catalog Builder Architecture's own Part 5 already marks mandatory (ABV, Style, per Product Decisions Register D1's provisional-mandatory treatment) must be a real value, not `unknown` — a beer with an honest `unknown` ABV passes structural and cross-reference validation cleanly, and is still correctly excluded from that specific build, exactly as Catalog Implementation Architecture Part 3's `unenriched_skus.csv` already reports.

---

## Part 8 — Relationship to Catalog Builder

**Exactly where the Builder consumes this repository.** `enrichment_reader.py` and `enrichment_schema.py` (Catalog Builder Implementation Design Part 3) are the *only* code that reads any file in this repository. `join.py` (same document, Part 4) is the *only* code that connects a file here to a real `beer_master.csv` row, via `canonical_product_id`. Nothing else, anywhere in the Catalog Builder, opens a file under `enrichment/` directly.

**Exactly where responsibilities stop.** This repository never computes anything (Part 4's Benchmark boundary, restated at the system level: computation begins in `value_metrics.py`/`benchmarks.py`/`value_score.py`, entirely downstream, never here). This repository never validates a build-level rule on its own — it can be internally consistent (every style reference resolves, every attribution block is complete) while still producing a beer the Catalog Builder correctly excludes from a specific build (missing ABV, a stale `canonical_product_id` a merge repointed). This repository has no knowledge of `catalog.json`'s own shape at all — a founder editing a beer's Style never needs to know or care what key name that becomes in the published JSON; that translation belongs entirely to `assemble.py` and `catalog_writer.py` (Catalog Builder Implementation Design Part 7). **The boundary, stated as one sentence:** this repository holds Curated facts, keyed by identity; the Catalog Builder is the only thing that ever turns those facts into a product.

---

## Part 9 — Scaling

**100, 500, and 2,000 beers** — reused directly from Catalog Implementation Architecture's own already-frozen Part 8, not re-derived: one file per beer scales cleanly through all three sizes; git remains fully functional and diffable; the only real transition is when `enrichment_report.py` (Catalog Builder Implementation Design Part 8) graduates from nice-to-have to necessary, already named at 2,000 beers by the Catalog Enrichment Playbook's own Part 9. Nothing about this repository's shape changes across these three sizes.

**Multi-city — genuinely new ground, not addressed by any frozen document, and flagged here rather than resolved.** Every fact this repository is designed to hold — Style, ABV, Brewery identity, Images — describes the *product itself*, not the market it's sold in; a Kingfisher Premium's ABV doesn't change because it's sold in a second state. In that specific sense, this repository's own field design (Part 3) already generalizes past Karnataka with zero change. **But `canonical_product_ids` (Part 3's own join field) is a flat list assuming exactly one identity namespace — KSBCL's — and that assumption is real, load-bearing, and would break the moment a second state's own excise pipeline (with its own, entirely separate identity system, the same way KSBCL's `canonical_product_id` space has no relationship to any other state's numbering) needed representing.** No such second pipeline exists today. No Product Decision anywhere in the register authorizes building toward one — Catalog Implementation Architecture's own Part 10 names "a national or multi-state catalog" as an explicit non-goal, not a deferred one. **This document does not propose restructuring `canonical_product_ids` into a source-scoped shape (e.g., keyed by which state's pipeline produced each ID) to prepare for that future** — doing so now would be designing against a decision that doesn't exist yet, exactly what the instructions warn against. This is named here as a real, identifiable seam that a future multi-state Product Decision would need to revisit, not as a gap in today's design.

---

## Part 10 — Future Evolution

**What belongs here, stated as a single test:** any fact about a real beer that (a) has no automated source and (b) can be attached to a real citation once a human finds one. Style, ABV, and Brewery-marketing-identity (once Catalog Contract 1.0's own still-open licensed-supplier-vs-brand-owner question is resolved) already pass this test today. Images, Food Pairing, and every other Product Enrichment domain Catalog Specification 1.0 already named (Flavor, Aroma, Bitterness, Body, Sweetness, Ingredients, Awards, Brewery Story) would pass the same test the moment their own still-open Product Decisions (Product Decisions Register D15, D16) are actually resolved toward building them — at which point they extend this repository's schema additively, the same way `abv`'s attribution block already works, not as a new kind of repository.

**What never belongs here, stated with the same permanence Catalog Implementation Architecture's own Part 10 already established, restated here because a "future evolution" section is exactly where such a boundary quietly erodes if it isn't restated:**
- **Anything Computed** — Benchmark, Value Score, cost-per-ml-alcohol — permanently, per Part 4's own boundary. Computation happens in the Catalog Builder, never here, no matter how tempting it might someday feel to "just cache" a computed value alongside the fact it's derived from.
- **Anything Verified/government-sourced** — price, size, container type, `canonical_product_id` itself — these are read from `pricing_data/`, never duplicated or overridden here. This repository joins to that data; it never re-states or contradicts it.
- **Observed/Charged Price, under any framing, ever** — the one permanent, canon-wide prohibition every catalog document in this session has restated without exception; this repository is not an exception either.
- **Ratings or Scores, of any kind** — the Canonical Interaction Lexicon's forbidden-terminology rule applies to this repository's own field design exactly as it applies to the app's copy.
- **AI-generated content, for any field, ever** — restated from Catalog Implementation Architecture Part 10 at full strength: every field this repository holds requires a citable `source_type`/`source_name`/`observed_at`/`observed_by`. A model-generated value has no such citation and would corrupt the exact property — a founder or future reviewer being able to trust every fact here because it traces to something real — that this entire repository exists to guarantee.

---

## Part 11 — Rejected-Evidence Record

**[RC7.7 addition, 2026-08-17]** — approved RC7.6, infrastructure built RC7.7 exactly as approved. Everything below is new; nothing in Parts 1–10 is redefined by it.

**What this is, and what it deliberately is not.** A rejected-evidence entry is not a Beer/SKU field the way everything in Part 3 is — it records the *opposite* of a curated fact: a piece of researched evidence that was found during Catalog Enrichment Playbook Part 4's research workflow and specifically **not** used. Without a durable record of that, a rejection is invisible the moment the founder moves on — the next research pass (possibly the same founder, months later, with no memory of the first attempt) has no way to know a source was already checked and found wanting, and re-does the same dead-end search. This record exists purely to make that already-spent effort reusable.

**Location and shape.** `enrichment/rejected_evidence.yaml` — one flat file, the same top-level shape `styles.yaml` uses (a list of mappings, not one file per entry). Every entry:

| Field | Required | Type | Notes |
|---|---|---|---|
| `subject_type` | Required | string | `beer` \| `brewery` — closed, mirroring the two kinds of subject this repository already models |
| `subject_key` | Required | string | A real `beer_key` (if `subject_type` is `beer`) or a `brewery` string already used by at least one `enrichment/beers/*.yaml` file (if `brewery`) — enforced by cross-reference validation, the same discipline Part 7 already applies to `style` references |
| `field` | Required | string | The Beer/SKU field the evidence was about — `abv`, `calories_per_100ml`, `style`, `brewery`, etc. |
| `value_found` | Required | string | The value that was found and rejected, exactly as found — not whatever value (if any) was ultimately curated instead |
| `source_type` | Required | string | `manufacturer` \| `manual_observation` — the same closed vocabulary Part 5's attribution block already uses; not a new vocabulary |
| `source_name` | Required | string | A specific citation, same discipline as Part 5 |
| `reason_type` | Required | string | Closed enum — see the taxonomy below |
| `reason_detail` | Required | string | A free-text explanation of the specific rejection — why this value, from this source, didn't become the curated fact |
| `observed_at` | Required | date | When this piece of evidence was found and rejected |
| `observed_by` | Required | string | Who |
| `recheck_after` | Optional | date | When it's worth looking again, if this rejection reason implies that — omitted when it doesn't |

**Reason taxonomy — approved RC7.6, closed, enforced by `enrichment_schema.py`:**

| `reason_type` | Meaning |
|---|---|
| `wrong_variant` | The value was real, but for a different variant, strength, or pack size of the product than the one being enriched. |
| `wrong_product_line` | The value belonged to a different, confusably-named product entirely — not the beer being enriched at all. |
| `access_blocked` | A source likely holding the fact exists but couldn't be reached or read (paywall, region lock, a dead page, an illegible label photo) — often worth a `recheck_after`. |
| `imprecise_value` | A real, on-topic value was found, but not precise enough to cite (e.g. rounded or ranged, where an exact figure is required). |
| `incompatible_unit` | The value used a unit or basis that doesn't match this schema's field (e.g. ABV proof instead of percent, per-pack calories where per-100ml is required) and couldn't be safely converted. |
| `conflicting_source_subordinate` | A real value from a real source, but the Catalog Enrichment Playbook's own source-priority order (Part 4 of that document) already provided a different value from a higher-priority source. |

**Citation discipline is identical to Part 5's — deliberately, not by coincidence.** `source_type`/`source_name`/`observed_at`/`observed_by` are the exact same four fields, meaning the exact same thing, enforced the exact same way. A rejected finding is still a real, sourced observation; it earns the same citation rigor an accepted one does; Part 5's "never a plain scalar" rule applies here without exception.

**Append-only.** Entries are never edited or removed by hand — `tool/catalog_builder/record_rejected_evidence.py` is the only supported way to add one, and it only ever appends (Part 3 of the Catalog Builder Implementation Design's own CLI philosophy, reused here rather than reinvented). A genuine correction to an already-recorded rejection (a `reason_detail` typo, say) is a normal, ordinary git edit to the YAML file directly, exactly as Part 6 already describes for Beer files — "append-only" governs how new findings are added, not whether the file is ever touched by a human editor at all.

**Relationship to the Catalog Builder — deliberately none, as of RC7.7.** `rejected_evidence.yaml` is not read by `enrichment_reader.py`, `join.py`, `build_catalog.py`, or any other Catalog Builder module. It has no effect on `catalog.json`, on which SKUs publish, or on any validation a beer file undergoes. This is a research-support record, not an input to the product — the same relationship `enrichment/README.md` and Part 8 already describe for this whole repository generally, just stated explicitly for this one file since it's new.

**Historical backfill is pending, not done.** As of RC7.7, `rejected_evidence.yaml` is empty. The six historical rejected-evidence cases referenced during RC7.6's approval are not reconstructible from anything in this repository and were deliberately not fabricated to fill this file — see `enrichment/rejected_evidence.yaml`'s own header comment. They will be added by a dedicated future migration (RC7.8), sourced only from authoritative material: repository history, accepted research reports, or supplied transcripts — never from memory or reconstruction.

**[RC7.8 addendum, 2026-08-17]:** RC7.6's specific six-case list remains unlocated — it is not recorded anywhere this repository's own history, documentation, or the RC7.8 audit could check it against. RC7.8's audit instead searched already-committed `enrichment/beers/*.yaml` citations directly, on the theory that a founder's own accepted ABV citation sometimes narrates a rejected alternate value inline while explaining why it wasn't used. Two such cases were found, fully sourced, and recorded: `miller_high_life_premium` (a Molson Coors "Lower Alcohol" regulatory variant at 3.7% ABV, rejected as `wrong_variant`) and `stok_strong_fine` (Mount Everest Breweries' own FAQ stating 8% ABV, rejected as `conflicting_source_subordinate` in favor of the site's structured spec table). Both are real, independently verifiable, and satisfy this document's evidence standard — but neither is confirmed to be one of RC7.6's original six; that correspondence cannot be checked. A third likely case (an access-blocked domain at B9 Beverages/Bira 91, referenced narratively in `docs/PROJECT-BRAIN.md` §16) was found but not recorded — no per-beer citation exists to source it from, and `access_blocked` cases in general expose a real, unresolved schema question: `value_found` has no natural answer when access failed before any value was ever read. Flagged for whoever next touches this schema, not fixed here.
