# ValueBrew — Catalog Implementation Architecture

*An implementation architecture document, not a product document. Catalog Builder Architecture (frozen, assumed) already answers what the lifecycle is and who's responsible for each stage. This document answers one narrower, mechanical question: how do we actually build and maintain the Beer Knowledge Base — files, formats, scripts, and sequencing — that produces `catalog.json`. Grounded in direct inspection of the current repository (no implementation of this system exists anywhere in it, confirmed by search before writing a line of this document), the real KSBCL pipeline's own established conventions, and the app's own already-shipped catalog-loading code.*

---

## 0. Ground Truth Statement — Report Before Redesign

Per the explicit instruction to stop and report rather than redesign anything already built, two things were found before this document was written, and neither is proposed again below:

**1. No catalog-enrichment or catalog-build implementation exists anywhere in this repository.** A direct search for `enrichment`, `catalog_builder`, `build_catalog`, and `beer_knowledge` across every Python, YAML, JSON, and Markdown file outside `docs/` returned nothing. This confirms Catalog Builder Architecture's own §0 finding still holds: the gap between `pricing_data/beer_master.csv` and `catalog/catalog.json` is real, current, and unaddressed by any existing code. Everything in Parts 1–9 below is genuinely new implementation, not a redesign of something that already exists.

**2. The app-side half of "how does a new catalog reach a user" is already fully built, tested-shaped, and must not be redesigned here.** `lib/catalog/data/catalog_repository.dart` implements a three-tier load order — bundled asset → local cache (`SharedPreferences`) → remote source — already wired to compare `catalog_version` and prefer whichever is newest. `lib/catalog/data/catalog_remote_source.dart` implements `HttpCatalogRemoteSource`, a real, working HTTP fetch with a 4-second timeout and full failure-mode handling (network down, timeout, non-200, unparseable body — every one caught and treated as "no update," never a crash). `lib/core/constants/app_constants.dart` already points this at a **live, configured distribution channel**: `https://cdn.jsdelivr.net/gh/nshntchaubey/valuebrew@main/catalog/catalog.json` — a jsDelivr CDN mirror of this repo's own `catalog/catalog.json`, requiring no separate hosting, no server, and no new infrastructure of any kind. **The practical consequence, stated plainly because it changes what this document needs to design:** the entire "publish a new catalog to users" problem is already solved. A correctly-built `catalog/catalog.json`, committed to `main` with a higher `catalog_version` than before, reaches every already-installed app automatically, the next time each one checks. This document's job stops at producing that file correctly — it does not need to design distribution, caching, or update-checking, and does not do so anywhere below.

---

## Part 1 — Overall Repository Layout

**Where enrichment data should live: a new top-level `enrichment/` directory, sibling to `catalog/` and `pricing_data/`.** This is a direct extension of a pattern the repository has already established twice, not a new convention invented here. The KSBCL pipeline architecture states its own reasoning for `pricing_data/`'s placement explicitly: *"repo root, sibling to catalog/ — deliberately NOT inside catalog/: this is raw pipeline output/audit trail, not the app's published catalog."* `enrichment/` sits in exactly the same relationship to `catalog/` that `pricing_data/` does — working, human-curated source material that a build step reads from, never the app's own published artifact. Three top-level data directories, three distinct roles: `pricing_data/` (automated, government-sourced, pipeline-owned), `enrichment/` (manual, human-curated, founder-owned — new, specified here), `catalog/` (published, app-bundled, build-step-owned, already exists).

**Format: YAML for enrichment source data, justified directly by existing repository precedent, not by abstract preference.** `tool/ksbcl_pricing_pipeline/config/beer_classification.yaml` already answers a structurally identical question — "how should versioned, human-edited, PR-reviewed domain data be stored in this repo" — and the answer the repository already gave is YAML. Reusing that answer here is consistent with the instruction not to invent new conventions where one already exists. Concretely, weighed against the alternatives named in the request:
- **CSV** is what `pricing_data/` already uses, correctly, because pipeline output is naturally row-shaped (one observation per row) and append-only. Enrichment data is not row-shaped in the same way — it's a nested record per Beer (a name, a Style reference, an ABV claim with its own source/date/observer, a list of image references) — and CSV has no clean way to express that nesting or to carry an inline comment explaining *why* a given fact was recorded a certain way. Recommended against, for enrichment specifically.
- **JSON** is the correct format for the *output* (`catalog.json` must match `Catalog.fromJson` exactly, and does) but is a poor format for *hand-edited source* data: no comments, and `git diff` on JSON is noticeably harder to review at a glance than YAML's. Recommended against for the source layer; already correct and unchanged for the output layer.
- **SQLite** has no precedent anywhere in this repository, would introduce a binary dependency that can't be reviewed via `git diff` — the single most consistently repeated discipline throughout the KSBCL pipeline's own architecture (audit trails, `rejected_rows.csv`, `run_summary.json`, all plain text, all diffable) — and is unjustified at the scale Part 8 actually plans for (thousands, not millions, of SKUs). Recommended against.
- **YAML**, therefore: human-editable directly in any text editor, diffable in a PR the same way every other change to this repository already is, supports comments (so an ABV claim's source can be documented inline, not just in a separate field), and has direct, working precedent in this exact repository for exactly this kind of data.

```
enrichment/                      # NEW — human-curated source data, sibling to catalog/ and pricing_data/
  README.md                      # editing guide for whoever curates this (see Part 4)
  styles.yaml                    # flat list — a few dozen styles, doesn't need one file each
  beers/
    <beer_key>.yaml               # one file per Beer — see Part 2 for exactly what beer_key is and why
```

---

## Part 2 — Beer Knowledge Base Organization

**The organizing unit is the Beer, not the SKU — and this requires one genuinely new identity concept this document must name explicitly, since nothing upstream provides it.** The KSBCL pipeline's `canonical_product_id` is confirmed, directly from its own architecture document (§4.4), to be **SKU-grain**: "the real SKU identity the app and `beer_master.csv` are keyed on." A single beer sold in three pack sizes gets three separate `canonical_product_id`s, with no existing field anywhere in the pipeline's output grouping them as "the same beer." The app's own `Beer`/`Sku` split, however, requires exactly that grouping to exist (`Sku.beerId` references one `Beer`). **This grouping does not exist anywhere in canon today, and this document does not invent an automated way to produce it** — attempting to auto-derive it (e.g., by stripping size text from `normalized_name_key`) would be guessing at an identity fact, the exact thing Part 1 of Catalog Builder Architecture forbids. **New Engineering Decision, flagged here rather than assumed:** grouping multiple `canonical_product_id`s into one Beer is itself a Curated act, performed by whoever enriches a SKU for the first time, by hand, the same way every other enrichment fact in this system is Curated. A `beer_key` (a stable, human-assigned slug, e.g. `kingfisher_premium`) is created once, and every `canonical_product_id` belonging to that beer is listed under it.

**One YAML file per Beer**, keyed by `beer_key`:

```yaml
# enrichment/beers/kingfisher_premium.yaml
beer_key: kingfisher_premium
canonical_product_ids:            # every KSBCL canonical SKU identity that is this beer, at any pack size
  - CP0000011                     # 650ml bottle
  - CP0000012                     # 330ml can
name: "Kingfisher Premium"
brewery: "United Breweries"       # marketing identity — see Catalog Builder Architecture Part 4's
                                   # own flagged, still-open licensed-supplier-vs-brand-owner question
style: lager                      # references a style_key in styles.yaml — ID reference, never embedded
is_craft: false
abv:                              # beer-level default, applies to every listed SKU unless overridden below
  value: 4.8
  source_type: manufacturer
  source_name: "United Breweries official product page"
  observed_at: "2026-08-10"
  observed_by: founder
images: []                        # empty until Product Decisions Register D15 is resolved
skus:                             # optional — only when a fact genuinely differs by pack size
  CP0000012:
    abv:
      value: 5.0
      source_type: manufacturer
      source_name: "..."
      observed_at: "2026-08-10"
      observed_by: founder
```

**Relationships are represented by explicit ID reference, never embedding — this is not a new rule, it is the exact discipline already governing every real model in `lib/shared_domain/` and `lib/catalog/domain/` (`Sku.beerId`, `Beer.styleId`, `Benchmark.styleId`, all plain string/reference fields, never nested objects), and it is the project's own stated Coding Principle (`CLAUDE.md`: "Prefer IDs over embedded objects unless the architecture explicitly requires embedding").** `style` in a beer file is a `style_key` string, resolved against `styles.yaml` at build time, exactly the way `Beer.styleId` is resolved against `catalog.styles` at read time in the app today.

**`styles.yaml`** — flat, not one-file-per-style, since Catalog Specification 1.0's own scope is a few dozen styles at most, not thousands:
```yaml
- style_key: lager
  name: "Lager"
  description: "Crisp, mild bitterness"
  typical_abv_range: [4.0, 5.5]   # Beer Entity Specification 1.0's own addition, Curated confidence
```

**`Benchmark` has no enrichment storage at all, and none is proposed.** It is Computed, deterministically, from the Sku population within a Style at catalog-build time — Catalog Builder Architecture already establishes this exactly, and this document does not add a hand-edited representation of something that must never be hand-edited.

---

## Part 3 — Catalog Builder Pipeline: `beer_master.csv` → `catalog.json`

Every step, in order, with its intermediate artifact named explicitly — none of these artifacts exist yet; this is the specification for producing them.

**Step 1 — Load pipeline output.** Read `pricing_data/beer_master.csv` only (never `beer_master_duty_free.csv` — the KSBCL pipeline's own §12.2 decision already excludes duty-free from every retail-facing surface, reused unchanged here). Read-only; this step never writes back to `pricing_data/`.

**Step 2 — First validation gate: contamination filter.** Apply Catalog Builder Architecture's own Part 7 rule directly: reject any row whose `item_name_raw` matches the pipeline's own existing spirit-family exclusion vocabulary (`whisky`/`whiskey`, `rum`, `brandy`, `vodka`, `gin`), **regardless of `classification_confidence`** — this is the fix for the two confirmed-live contaminants (`CP0000001`, `CP0000955`) Catalog Builder Architecture's own §0 found. Output: `catalog_candidates.csv` (rows that pass) and `catalog_rejected.csv` (rows that fail, each with a named reason — never a silent drop, matching the pipeline's own `rejected_rows.csv` discipline).

**Step 3 — Load enrichment data.** Read every file under `enrichment/beers/*.yaml` and `enrichment/styles.yaml`.

**Step 4 — Join.** For each row in `catalog_candidates.csv`, look up which `beer_key` (if any) lists its `canonical_product_id`. Any candidate with no matching `beer_key` is excluded from this build and written to `unenriched_skus.csv` — a new, explicit "still needs a human" report, which is exactly the input the Enrichment Queue tool (Catalog Builder Architecture, Part 8) needs to surface.

**Step 5 — Assemble Beer and Style records.** One `Beer` entry per `beer_key` present in the joined set; one `Style` entry per `style_key` referenced by at least one included Beer.

**Step 6 — Compute per-SKU derived fields.** `cost_per_litre` and `cost_per_ml_alcohol`, from `beer_master.csv`'s own price fields plus the resolved ABV (beer-level default or SKU-level override, per Part 2) — pure arithmetic, no judgment, matching exactly what the real `Sku` model's own doc comment already describes these fields as.

**Step 7 — Compute Benchmarks.** For each Style present in this build, aggregate `cost_per_ml_alcohol` across every included Sku sharing that style; compute `avg`, `p25`, `p50`, `p75`, `sample_size` — matching `Benchmark.fromJson`'s schema exactly.

**Step 8 — Compute `value_score`/`value_verdict` per Sku**, from its own `cost_per_ml_alcohol` against its Style's freshly-computed Benchmark — an inverted percentile, matching `Sku`'s own doc comment exactly ("an inverted percentile of `costPerMlAlcohol` within this SKU's style benchmark").

**Step 9 — Assemble the final JSON object**: `catalog_version` (the previous published value, plus one — see Part 6), `generated_at` (build timestamp), `styles`, `beers`, `skus`, `benchmarks` — the exact top-level shape `Catalog.fromJson` already expects, unchanged.

**Step 10 — Second validation gate: schema and rule check.** Run Catalog Builder Architecture's full Part 7 rule set (missing mandatory fields, orphan references, broken image licensing, stale prices, listing inconsistencies) plus a structural check that the assembled JSON actually round-trips through the app's own `Catalog.fromJson`/`toJson` shape — the hard technical floor beneath every product-level rule. A failure here blocks Step 11 entirely.

**Step 11 — Write `catalog/catalog.json`** (this repository's own file — the same one `pubspec.yaml` bundles and the jsDelivr CDN already mirrors), plus a build manifest recording which `pricing_data/runs/YYYY-MM/` run and which `enrichment/` git commit produced this exact `catalog_version` (the direct analogue of `beer_master.csv`'s own `source_pdf_reference` field, one layer up, as Catalog Builder Architecture's own Stage 7 already calls for).

**Step 12 — Publish.** Per §0.2 above: commit and push to `main`. **No further step is needed** — distribution is already built and already configured.

---

## Part 4 — Editing Workflow

**Adding a new beer.** Create `enrichment/beers/<new_beer_key>.yaml`; list at least one `canonical_product_id` found in the current `beer_master.csv`; fill `name`, `style`, `abv` (Catalog Builder Architecture's own mandatory-field list, Part 5). Nothing else is required to pass validation, though Style/ABV are what actually unlock ranking (same document, same Part).

**Adding ABV, Style, Brewery, or an Image to an existing beer.** Edit that beer's existing YAML file directly — add or change the relevant top-level key, or add a per-SKU override under `skus:` when a fact genuinely varies by pack size (Part 2). There is no separate "add a field" workflow; every field lives in the same file, edited the same way.

**"Without breaking anything," concretely:** three independent safety nets, none of them new inventions — (1) the enrichment-file schema validator (`validate_enrichment.py`, Part 7) catches a malformed YAML file or an out-of-range ABV before it ever reaches a build; (2) the catalog-build's own Step 10 validation gate catches anything that would produce a broken `catalog.json`, so a bad edit can never reach the published artifact even if it somehow passed step 1; (3) ordinary git/PR review — every enrichment change is a plain-text diff against a previous, working state, reviewable and revertable the same way every other change to this repository already is, requiring no new process. A founder editing one beer's YAML file cannot affect any other beer's file, and cannot affect `pricing_data/` or the KSBCL pipeline at all — the join in Part 3, Step 4 is the only place enrichment and pipeline data ever meet, and it happens at build time, never by direct mutation of either source.

---

## Part 5 — Validation Architecture

**Layer 1 — Enrichment-file validation, runs on every enrichment edit (locally, before commit, and again in CI on every PR touching `enrichment/`).** Blocks: a YAML file that doesn't parse; a missing required key (`beer_key`, `canonical_product_ids`, `name`); an ABV outside a plausible sanity range; a `style` reference with no matching `style_key` in `styles.yaml`; a `canonical_product_id` that doesn't appear anywhere in the current `beer_master.csv` (a stale or typo'd reference). Warns only: an ABV claim with `source_type: manufacturer` but no `source_name` populated (should be filled, doesn't block); an image entry with `license: unknown` (Catalog Builder Architecture's own Part 7 rule makes this a hard block *at publication*, but a warning at the enrichment-edit layer is enough to let a founder stage an image entry before its license is confirmed, as long as it can never reach Step 11 unresolved).

**Layer 2 — Catalog-build validation, runs on every build attempt, before Step 11 writes anything.** This is Catalog Builder Architecture's own Part 7 rule set, reused exactly, not re-derived: duplicate identities (structurally impossible by construction, per Part 3 Step 5's own grouping, checked anyway); invalid ABV; missing mandatory fields; style mismatch (the contamination filter, Step 2, applied as a build-time gate independent of whether it was already caught earlier); orphan references (a Sku whose Beer or Style doesn't resolve); broken images (unlicensed, blocks); stale prices (flags for review, per Product Decisions Register D11 — does not block, since D11 itself is unresolved and this document takes no position on it); listing inconsistencies (a large cross-supplier price spread on one canonical product — flags for review, per Catalog Builder Architecture's own treatment, does not block).

**What blocks Publication (Step 11 never runs):** any Layer 2 rule marked "blocks" above, plus a failed structural round-trip through `Catalog.fromJson`/`toJson` (Part 3, Step 10).

**What is warnings-only, surfaced but never blocking:** stale-price flags, listing-inconsistency flags, single-source-ABV-with-no-corroboration (worth a note in the build report, since Catalog Builder Architecture never required corroboration as a mandatory bar), and any Layer 1 warning that a human chose to leave unresolved before committing.

---

## Part 6 — Versioning

**`catalog_version` itself needs no new mechanism — it already has one, fully built, and this document reuses it unchanged.** `CatalogRepository` and `HttpCatalogRemoteSource` already compare `catalog_version` as a plain monotonically-increasing integer (confirmed directly in both files, §0.2). The Catalog Builder's own Step 9 simply reads the previously-published value and increments it by exactly one per real publish — no semantic versioning, no date-encoding, nothing beyond what the app already expects and already works with.

**Enrichment data is versioned by git history — not a new system, a direct reuse of the one this repository already has.** Every `enrichment/*.yaml` file is a normal repository file; every change is a normal commit, PR-reviewed, diffable, revertable. No separate database, changelog file, or audit table is proposed for enrichment itself. What *is* newly recommended, directly modeled on a pattern the KSBCL pipeline already uses for exactly this purpose — `classification_config_version`, confirmed as a content hash (`"8b9d82b45497"`) in the real `classification_run_summary.json` this document inspected — is that the build manifest (Part 3, Step 11) record an **`enrichment_snapshot_version`**, a content hash of the `enrichment/` directory's state at build time, alongside the pipeline run it was built against. This gives every published `catalog_version` full, exact traceability back to both of its two real inputs, reusing an already-established repository convention rather than inventing a new one.

**How monthly KSBCL updates interact with manually curated data — exactly Catalog Builder Architecture's own Part 6, restated at the mechanical level this document owns.** Because `canonical_product_id` is append-mostly and stable across pipeline runs (the entire point of the pipeline's own Stage 4 design), an `enrichment/beers/*.yaml` file's `canonical_product_ids` list continues to resolve correctly against a new month's `beer_master.csv` without any change, as long as no `canonical_product_id` it references was ever merged into another. **The one integration seam Catalog Builder Architecture already flagged and this document must operationalize:** if `pricing_data/item_code_canonical_map.csv` ever repoints a `canonical_product_id` (a human-confirmed merge, per the pipeline's own §4.4), any enrichment file still referencing the old ID becomes stale. Part 7's `merge_review.py` is the concrete tool that checks for this on every build, per Catalog Builder Architecture's own already-named requirement — this document does not introduce a new decision here, only the script that enforces the one already on record.

---

## Part 7 — Tooling

*Responsibilities only, per the instruction — no flags, no argument shapes, no UI. All five live under `tool/catalog_builder/`, following the exact placement convention `tool/ksbcl_pricing_pipeline/` and `tool/generate_brand_assets.dart` already establish for cross-cutting maintenance scripts that aren't part of the Flutter app itself.*

**`build_catalog.py`** — runs Part 3's full pipeline, Steps 1–11. The one tool every other tool exists in service of; everything else either prepares its inputs or inspects its outputs.

**`validate_enrichment.py`** — Layer 1 of Part 5, standalone and fast enough to run before every commit; does not require `beer_master.csv` to be loaded, only the `enrichment/` tree and `styles.yaml` cross-references.

**`validate_catalog.py`** — Layer 2 of Part 5, runnable against either a already-published `catalog.json` (a health check) or a freshly-assembled candidate before it's written (what `build_catalog.py` calls internally at Step 10).

**`diff_catalog.py`** — compares two `catalog.json` files (typically the currently-published one against a fresh build's candidate) and reports added, removed, and materially-changed SKUs — the concrete CLI form of the "Publication Preview" responsibility Catalog Builder Architecture's own Part 8 already named without specifying tooling for.

**`enrichment_report.py`** — reads `unenriched_skus.csv` (Part 3, Step 4's own output) and reports, per beer already enriched, which Launch-Critical fields are still missing — the concrete CLI form of the "Enrichment Queue" responsibility Catalog Builder Architecture's Part 8 already named.

**`merge_review.py`** — cross-checks every `canonical_product_id` referenced anywhere under `enrichment/` against the current `item_code_canonical_map.csv`, flagging any that a confirmed merge has since repointed — the concrete implementation of the integration seam named in Part 6 above and in Catalog Builder Architecture's own Part 6.

---

## Part 8 — Future Scalability

**100 → 500 → 5,000 SKUs, without redesign, because every mechanism specified above is already O(n) or better, and the storage shape doesn't change with scale — only its size does.** One YAML file per Beer at 5,000 SKUs means, at a generous 2–3 pack sizes per beer, somewhere around 1,500–2,500 small files — an entirely ordinary size for a git repository (many real open-source projects hold far more), still fully diffable, still fully reviewable per-file in a PR, still requiring no tooling beyond what Part 7 already specifies. The join in Part 3, Step 4 is a straightforward hash-map lookup keyed on `canonical_product_id`; nothing about it degrades qualitatively between 100 and 5,000 rows.

**What genuinely would need revisiting, named explicitly rather than solved here:** well beyond 5,000 SKUs — and explicitly not at any scale this document, the Catalog Specification, or the Product Decisions Register currently plans for — a flat `enrichment/beers/*.yaml` directory starts to strain plain manual browsing (though `grep`/`git` themselves remain fine indefinitely). **This is precisely the condition under which the enterprise catalog research corpus's own national-scale, multi-table Postgres design (`docs/research/enterprise_catalog_research/03-production-database-schema.md`) becomes the right reference to revisit** — Catalog Builder Architecture already named this explicitly as unadopted research, not decided architecture, contingent on Product Decisions Register D19 ever being resolved toward a database-backed platform. This document's own architecture is deliberately the *simpler*, repository-native answer for the scale everything else in the canon actually plans for, and its own natural retirement condition is exactly that future decision, not a shortfall in what's specified here.

---

## Part 9 — Migration Plan

*Smallest sequence, front-loading correctness, deferring convenience tooling until real usage shows it's needed — consistent with the project's own stated discipline against premature abstraction.*

1. **Create the `enrichment/` directory structure** (`styles.yaml` seeded with the handful of real styles already implied by current `beer_master.csv` rows; `beers/` empty; `README.md` documenting the shape in Part 2). Zero code.
2. **Hand-enrich a small first batch of real SKUs** (10–20) directly against the live `beer_master.csv` — proves the workflow end to end before any tooling exists to automate it, and surfaces any real gap in Part 2's schema early, while it's cheap to fix.
3. **Build `build_catalog.py`** (Part 3, Steps 1–11) against that small enriched set — correctness first, no CLI polish, no flags beyond what's needed to run it.
4. **Build `validate_catalog.py`**, wiring Catalog Builder Architecture's Part 7 rules in full, including the contamination filter that fixes the two confirmed-live whiskey rows.
5. **Run the first real build**, diff its output by hand against the current 1-SKU placeholder `catalog.json`, and confirm the app's own existing `CatalogRepository`/`Catalog.fromJson` parses it without any app-code change — this is a verification step, not an implementation one, since the schema is already unchanged and already correct.
6. **Commit `catalog/catalog.json` to `main`; verify the jsDelivr URL actually serves the new content.** Zero new code — this milestone exists purely to confirm the already-built distribution path (§0.2) works end to end with a real, non-placeholder catalog for the first time.
7. **Build `validate_enrichment.py` and `enrichment_report.py`**, once the manual workflow from steps 1–2 has actually produced real friction worth automating away — not before.
8. **Build `diff_catalog.py` and `merge_review.py`**, genuinely deferred conveniences, built only once a second real monthly enrichment cycle (Part 6) has actually happened and proven the integration seam they guard against is worth tooling for rather than checking by hand once.

---

## Part 10 — Explicit Non-Goals

**Barcode scanning.** GTIN enrichment itself is Future Expansion per Catalog Specification 1.0; a scanning *capability* is further still, and this document's schema (Part 2) reserves the field without building anything that populates or reads it via a scanner.

**A national or multi-state catalog.** The KSBCL pipeline is Karnataka-only by its own explicit, frozen design; nothing in this document assumes or prepares for a second state's data, and doing so would be a schema-level decision this document has no authority to make.

**Ratings.** Permanently excluded, not merely unscheduled — the Canonical Interaction Lexicon's forbidden-terminology rule against "Score" or "Rating" applies to any future field this system might otherwise be tempted to add, and this document introduces none.

**Taste modeling / sensory data.** Flavor, Aroma, Body, Bitterness, Sweetness, Ingredients — the entire cluster Catalog Specification 1.0 and Product Decisions Register D16 already name as deliberately unscoped. This document's `enrichment/` schema (Part 2) has no field for any of them, and adding one would be exactly the kind of premature specification Catalog Specification 1.0 itself already declined to produce.

**AI-generated enrichment, of any kind, for any field.** Not merely unscheduled — actively incompatible with this entire document's own foundation. Every enrichment field specified in Part 2 requires a citable `source_type`/`source_name`/`observed_at`/`observed_by` — a Manufacturer publication or a Manual observation, per Catalog Builder Architecture's own Part 1 and Part 3. A model-generated ABV or Style guess has no such citable source and would violate the Beer Knowledge Model's foundational "never invent" principle at the exact point this whole system exists to protect. This is named as a permanent exclusion, not a future possibility.

**A general-purpose, multi-source, confidence-scored claims-ledger database.** The enterprise catalog research corpus's own national-scale design is real, well-considered, and explicitly not what this document builds — see Part 8's own honest account of when that design would actually become the right one to revisit.

**Automated Style or ABV inference of any kind**, including fuzzy matching against a style's "typical" range to guess a missing value. Catalog Builder Architecture's Part 1 already established why manual enrichment is structurally necessary for exactly these two fields; this document's tooling (Part 7) is built entirely to make human judgment faster to apply, never to replace it.

**Real-time or push-based catalog updates.** The jsDelivr-CDN-plus-version-check model already built into the app (§0.2) is an eventual-consistency mechanism, checked on each app launch/foreground, not a live push — this document does not attempt to change that behavior, only to make sure a correct file exists for it to eventually fetch.
