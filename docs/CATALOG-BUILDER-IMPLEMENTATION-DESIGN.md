# ValueBrew — Catalog Builder: Implementation Design

*Engineering architecture for a real Python package, not pseudocode and not a redesign of anything already decided. Catalog Builder Architecture, Catalog Implementation Architecture, Catalog Contract 1.0, the Product Decisions Register, Beer Knowledge Model 2.0, Domain Model 1.0, and Catalog Specification 1.0 are all treated as frozen inputs here — every module below exists to implement a rule one of those documents already states, never to invent a new one. Grounded directly in the real `tool/ksbcl_pricing_pipeline/` package (every module file read via its actual directory listing, `validate.py` and `classification_config.py` read in full for their real conventions), the real `pricing_data/`, `catalog/`, `lib/catalog/`, and `lib/shared_domain/` contents already inspected across the four prior catalog documents this session produced.*

---

## 0. Conventions This Design Reuses, Not Invents

Four real, evidence-confirmed conventions from `tool/ksbcl_pricing_pipeline/` govern every design choice below, cited once here rather than re-justified in every Part:

1. **Module naming.** `<concept>_models.py` for dataclasses, `<concept>_io.py` for read/write persistence, `<concept>_reader.py` for specialized parsers, `run_stageN.py`-shaped files as thin CLI entrypoints separate from the logic modules they call, a single `validate.py`-shaped module per validation concern. Confirmed directly from the real package's own file listing (`classification_models.py`, `canonical_map_io.py`, `normalized_rows_reader.py`, `run_stage2.py`–`run_stage5.py`, `validate.py`).
2. **Two-tier error handling.** A row-level failure is returned as a data value (`RejectedRow`, confirmed in `validate.py`) and never raised; a structural/aggregate failure is raised as a named exception (`PipelineValidationError`, same file) that the caller treats as an abort. This design reuses the identical two-tier shape throughout, never inventing a third error-handling style.
3. **Content-hash versioning.** `ClassificationConfig` (confirmed in `classification_config.py`) is versioned by a `hashlib` content hash of its own source file, not a hand-maintained version number — this is the exact mechanism Catalog Implementation Architecture's own Part 6 already proposed reusing for `enrichment_snapshot_version`, and this document treats that as settled, not re-decided.
4. **A dependency manifest already exists, scoped to `tool/ksbcl_pricing_pipeline/`** — `tool/ksbcl_pricing_pipeline/requirements.txt` (confirmed by direct read), pinning `pdfplumber`, `pytest`, and `PyYAML`. No `pyproject.toml` or `setup.py` exists at any level, and no manifest exists at the `tool/` root shared across packages. `import yaml` (`classification_config.py`) is already a real, working dependency, and it is already declared in that manifest. **This design introduces no new external dependency** — PyYAML is already in active use for exactly the kind of config parsing the new package also needs — and should extend the existing `tool/ksbcl_pricing_pipeline/requirements.txt` (or a manifest scoped equivalently to `tool/catalog_builder/`) rather than leaving any new dependency undeclared.

---

## Part 1 — Overall Package Structure

**Location: `tool/catalog_builder/`**, sibling to `tool/ksbcl_pricing_pipeline/` — already the location Catalog Implementation Architecture Part 7 named; this document gives it its internal shape.

```
tool/catalog_builder/
  __init__.py                      # package docstring, cites this design doc + the three frozen
                                    # architecture docs, states what's implemented vs. not (mirrors
                                    # ksbcl_pricing_pipeline/__init__.py's own convention exactly)

  models.py                        # every dataclass this package operates on — see Part 3-7

  beer_master_reader.py            # Part 3: loads + validates pricing_data/beer_master.csv
  enrichment_reader.py             # Part 3: loads + validates enrichment/beers/*.yaml, styles.yaml
  enrichment_schema.py             # Part 3: the expected YAML shape, Layer-1 validation rules

  join.py                          # Part 4: canonical_product_id -> beer_key resolution
  merge_check.py                   # Part 4: stale-reference detection against item_code_canonical_map.csv

  value_metrics.py                 # Part 5: cost_per_litre, cost_per_ml_alcohol
  benchmarks.py                    # Part 5: per-style avg/p25/p50/p75/sample_size
  value_score.py                   # Part 5: value_score + value_verdict, depends on benchmarks.py

  contamination_filter.py          # Part 6: the spirit-term exclusion gate (Catalog Builder
                                    # Architecture's Step 2 fix) — see Part 6's flagged ambiguity
                                    # about where its vocabulary should actually live
  schema_validate.py               # Part 6: Catalog Contract 1.0 §8 shape/enum rules
  cross_reference_validate.py      # Part 6: Catalog Contract 1.0 §7 FK integrity + duplicate-ID checks
  business_rules.py                # Part 6: Catalog Builder Architecture §7 rules not covered above
  validation_report.py             # Part 6: aggregates all of the above into one structured report

  assemble.py                      # Part 7: builds the in-memory Style/Beer/Sku/Benchmark graph
  version.py                       # Part 7: reads previous catalog_version, increments by one
  build_manifest.py                # Part 7: writes the build manifest — see Part 7's flagged ambiguity
  catalog_writer.py                # Part 7: serializes the assembled graph to catalog/catalog.json

  build_catalog.py                 # Part 8 CLI: end-to-end orchestration, mirrors run_pipeline.py's role
  validate_enrichment.py           # Part 8 CLI: Layer-1 validation only, standalone
  validate_catalog.py              # Part 8 CLI: full validation layer against a built catalog.json
  diff_catalog.py                  # Part 8 CLI: compares two catalog.json files
  enrichment_report.py             # Part 8 CLI: human-readable "still needs enrichment" report
  merge_review.py                  # Part 8 CLI: thin wrapper around merge_check.py

  tests/
    __init__.py
    test_<module>.py               # one per logic module — see Part 9
    fixtures/                      # golden + failure fixtures — see Part 9
```

**Responsibilities, at the directory level.** Loading (Part 3) never validates business meaning, only shape and parseability. Joining (Part 4) never computes or validates, only resolves identity. Computation (Part 5) never reads files or validates, pure functions over already-loaded, already-joined data. Validation (Part 6) never mutates anything, only inspects and reports. Serialization (Part 7) never re-validates — it trusts Part 6 already ran and blocked publication if it needed to. CLI modules (Part 8) contain no logic of their own beyond argument handling and calling into the layers above, mirroring exactly how `run_stage2.py`–`run_stage5.py` relate to `classify_stage.py`/`normalize_stage.py`/`canonical_resolve.py`/`stage5_resolve.py` in the real, existing package.

---

## Part 2 — Execution Pipeline

Exactly which module executes in which order, for a full `build_catalog.py` run — responsibilities only, cross-referenced directly against Catalog Implementation Architecture Part 3's already-frozen twelve steps:

| Step (Catalog Implementation Architecture) | Executing module(s) | Responsibility |
|---|---|---|
| 1. Load pipeline output | `beer_master_reader.py` | Read `pricing_data/beer_master.csv` only — never the duty-free file, per the already-frozen exclusion |
| 2. Contamination filter | `contamination_filter.py` | Reject any row matching the spirit-term vocabulary, regardless of `classification_confidence` |
| 3. Load enrichment data | `enrichment_reader.py`, `enrichment_schema.py` | Read every `enrichment/beers/*.yaml` and `enrichment/styles.yaml`, validated at Layer 1 as they're read |
| 4. Join | `join.py` | Resolve each surviving candidate's `beer_key`; unmatched rows recorded, never dropped silently |
| 5. Assemble Beer/Style records | `assemble.py` (first pass) | One Beer per referenced `beer_key`, one Style per referenced `style_key` |
| 6. Compute per-SKU derived fields | `value_metrics.py` | `cost_per_litre`, `cost_per_ml_alcohol` |
| 7. Compute Benchmarks | `benchmarks.py` | Per-style `avg`/`p25`/`p50`/`p75`/`sample_size`, over this build's own admitted Sku population only |
| 8. Compute value_score/value_verdict | `value_score.py` | Depends on Step 7's output, per Sku |
| 9. Assemble final object | `assemble.py` (second pass), `version.py` | Full `Catalog` graph plus the incremented `catalog_version` and `generated_at` |
| 10. Validation gate | `schema_validate.py`, `cross_reference_validate.py`, `business_rules.py`, `validation_report.py` | Every rule in Catalog Contract 1.0 §8 and Catalog Builder Architecture §7, aggregated into one pass/block decision |
| 11. Write | `catalog_writer.py`, `build_manifest.py` | `catalog/catalog.json` plus its build manifest — only reached if Step 10 blocks nothing |
| 12. Publish | *(none — human action)* | Commit and push, per Catalog Implementation Architecture §0.2's own finding that distribution is already built and needs no code here |

`build_catalog.py` is the only module that calls every other module in this table, in this exact order, and is itself the sole owner of that ordering — no other module reaches into another layer out of sequence.

---

## Part 3 — Data Loading Layer

**`beer_master_reader.py`.** Reads `pricing_data/beer_master.csv` (never `beer_master_duty_free.csv`) into a list of `BeerMasterRow` dataclass instances (Part 1's `models.py`), one field per CSV column, using the exact real schema Catalog Builder Architecture §0.3 already confirmed (`canonical_product_id`, `item_name_raw`, `pack_size_ml`, `container_type`, `mrp`, `effective_date`, `classification_confidence`, `classification_matched_on`, etc.). **Validation before parsing**, mirroring `validate.py`'s own row-level-vs-structural split: a missing/renamed column header is a structural failure (raised, aborts — the same defense the real pipeline's own Stage 1 already applies to its source PDF, reused here against `beer_master.csv`'s own header); an individual row with an unparseable price or a malformed date is a row-level failure (recorded, never raised, excluded from the returned row list, and reported the same way `rejected_rows.csv` already reports Stage 1 failures).

**`enrichment_reader.py`.** Reads every file under `enrichment/beers/*.yaml` into `EnrichmentBeer` instances, and `enrichment/styles.yaml` into a list of `StyleDef` instances. A malformed individual beer YAML file is a row-level-shaped failure (that one file is excluded and reported, the rest of the build continues) — **Recommendation, not yet decided upstream:** treating one bad enrichment file as row-level rather than structural is consistent with the two-tier convention in §0.2 and with Catalog Implementation Architecture Part 4's own framing (a founder's edit to one beer's file "cannot affect any other beer's file"), but no prior document explicitly states which tier a malformed enrichment file belongs to — this design recommends row-level, and flags that recommendation as its own choice, not a restatement of settled canon.

**`enrichment_schema.py`.** Defines the required-key/type shape every `EnrichmentBeer`/`StyleDef` must satisfy — `beer_key`, `canonical_product_ids`, `name`, `style`, `abv` (with its own nested `value`/`source_type`/`source_name`/`observed_at`/`observed_by` shape, per Catalog Implementation Architecture Part 2) — and is the module `enrichment_reader.py` calls at load time. This is Catalog Implementation Architecture Part 5's "Layer 1" validation, given its own module rather than folded into the reader, so it can also be called standalone by `validate_enrichment.py` (Part 8) without loading anything else.

---

## Part 4 — Join Layer

**`join.py`.** Builds a reverse index — `canonical_product_id → beer_key` — from every loaded `EnrichmentBeer`'s `canonical_product_ids` list (Part 2 of Catalog Implementation Architecture). For each surviving `BeerMasterRow` (post-contamination-filter), looks up its `canonical_product_id` in that index. A match produces a joined `(BeerMasterRow, EnrichmentBeer)` pair, carried into Part 5. **No match is a row-level failure, never an abort** — the row is written to the "unenriched" output (the same list `enrichment_report.py`, Part 8, reads), exactly matching Catalog Implementation Architecture Part 3 Step 4's own already-frozen behavior. **Duplicate mapping — a `canonical_product_id` listed under two different `beer_key`s — is a structural failure**, since it represents an ambiguous, contradictory identity claim; this is not named explicitly anywhere upstream, and is flagged here as a new validation rule this design introduces at the join layer, not a restatement of an existing one.

**`merge_check.py`.** Cross-checks every `canonical_product_id` referenced anywhere under `enrichment/` against the current `pricing_data/item_code_canonical_map.csv`, specifically looking for an ID that a confirmed merge has since repointed (Catalog Builder Architecture Part 6's own already-named integration seam). This module's output does not feed the main build pipeline directly — it is read by `merge_review.py` (Part 8) as a standalone check, run independently of `build_catalog.py`, since a stale reference is something a human needs to *fix* in `enrichment/`, not something the build itself can silently route around.

---

## Part 5 — Computation Layer

**`value_metrics.py`.** Two pure functions, no I/O, no side effects: `cost_per_litre` from `price` and `size_ml`; `cost_per_ml_alcohol` from `price`, `size_ml`, and `abv`. Depends only on `models.py`'s Sku-shaped data — the single easiest layer in the whole package to unit test in isolation, per Part 9.

**`benchmarks.py`.** For each Style present in the current build's admitted Sku population, aggregates every admitted Sku's `cost_per_ml_alcohol` sharing that style and computes `avg`, `p25`, `p50`, `p75`, `sample_size` — matching Catalog Contract 1.0 Part 6's schema exactly. **Dependency: runs after `value_metrics.py`** (needs `cost_per_ml_alcohol` already computed per Sku) **and after `join.py`** (needs to know which Skus are actually admitted to this build). A Style with zero admitted Skus produces no Benchmark entry at all — omission, not a zero-filled row, per Catalog Contract 1.0 Part 6's own already-frozen rule.

**`value_score.py`.** Depends directly on `benchmarks.py`'s output: computes `value_score` (an inverted percentile of a Sku's `cost_per_ml_alcohol` within its own Style's just-computed Benchmark) and `value_verdict` (a fixed mapping from `value_score`, matching `ValueVerdict`'s three real values — `great_value`/`fair_value`/`overpriced`, confirmed directly against `lib/shared_domain/sku.dart`). **This module cannot run before `benchmarks.py`, and `benchmarks.py` cannot run before `value_metrics.py` — a strict three-step dependency chain, not parallelizable within one build.**

---

## Part 6 — Validation Layer

**`contamination_filter.py`.** Implements Catalog Builder Architecture's Step 2 fix directly: reject any `BeerMasterRow` whose `item_name_raw` matches the spirit-family exclusion vocabulary, independent of `classification_confidence`. **Flagged implementation ambiguity, not resolved here:** the KSBCL pipeline's own exclusion vocabulary already exists, live, in `tool/ksbcl_pricing_pipeline/config/beer_classification.yaml`, loaded via `classification_config.py`. This design does not decide whether `contamination_filter.py` should **import that existing config directly** (creating a real, cross-package dependency from `tool/catalog_builder/` on `tool/ksbcl_pricing_pipeline/`, but guaranteeing the two vocabularies can never drift apart) or **maintain its own independent copy** (no cross-package coupling, but a real, concrete risk that the two lists silently diverge over time — the exact class of risk Catalog Builder Architecture's own Part 7 already worries about for adjacent reasons). Both options are legitimate; neither is chosen here.

**`schema_validate.py`.** Every rule in Catalog Contract 1.0 §8, levels 2–3: correct top-level shape, every entity's required fields present, every enum value within its closed set — **including the already-flagged `package_type` incompatibility** (Catalog Contract 1.0 Part 5): a Sku whose source `container_type` is `pet_bottle`, `tetra_pack`, or `unknown` fails this check today, by design, since the real app's `PackageType` enum cannot represent any of the three. This module is where that already-known, already-live incompatibility is actually enforced as a build-blocking rule, not merely documented.

**`cross_reference_validate.py`.** Catalog Contract 1.0 §7's FK integrity rules — every `Sku.beer_id` resolves to a real `Beer.id`, every `Beer.style_id` resolves to a real `Style.id`, every `Benchmark.style_id` resolves to a real `Style.id` — plus the duplicate-ID check Catalog Contract 1.0 §7 itself flagged as unenforced anywhere in the real app code today. **This module is the first place in the entire system that check would ever actually run.**

**`business_rules.py`.** The remaining Catalog Builder Architecture §7 rules not already covered above: missing mandatory fields (ABV, treated as provisionally mandatory per Product Decisions Register D1, exactly as Catalog Contract 1.0 Part 8 already frames it — not a new decision made here); broken/unlicensed image references (blocks); stale-price and listing-inconsistency flags (warnings only, never blocking, per Catalog Implementation Architecture Part 5's own already-frozen distinction).

**`validation_report.py`.** Aggregates the output of all four modules above into one structured result distinguishing blocking failures from warnings — mirroring the shape of the real pipeline's own `RunSummary`/`run_summary.json` pattern (counts, reasons, never a bare pass/fail boolean with no detail). `build_catalog.py` inspects only this module's aggregate verdict to decide whether Step 11 (Part 2) runs at all.

---

## Part 7 — Serialization Layer

**`assemble.py`.** Builds the in-memory object graph — lists of `Style`/`Beer`/`Sku`/`Benchmark`-shaped dataclasses matching Catalog Contract 1.0 Parts 3–6 field-for-field — from the joined, computed, validated data produced by every prior layer. Runs twice in the pipeline (Part 2's table): once early, to establish which Beers/Styles exist at all before computation needs them; once at the end, to produce the final, complete graph including every computed and validated field.

**`version.py`.** Reads the `catalog_version` of the currently-published `catalog/catalog.json` (falling back to `0` if none exists — the very first build) and returns exactly that value plus one, per Catalog Contract 1.0 Part 2's already-frozen "monotonically incremented by exactly one" rule. No other versioning logic belongs in this module.

**`build_manifest.py`.** Writes the build manifest Catalog Implementation Architecture Part 3 Step 11 and Part 6 already call for: which `pricing_data/runs/YYYY-MM/` run, and which `enrichment/` content-hash snapshot (per §0.3's reused convention), produced this exact `catalog_version`. **Flagged implementation ambiguity, not resolved here: where this manifest file should actually live.** Catalog Implementation Architecture named the *concept* without naming a path. Two candidates, neither decided: alongside `catalog/catalog.json` itself (discoverable, but `catalog/` is documented elsewhere as "the app's published, bundled artifact" — the manifest is not bundled or consumed by the app, so co-locating it there would mix two different roles in one directory); or under `pricing_data/runs/YYYY-MM/`, extending that directory's already-established "one run's full audit trail lives here" convention one step further to include the catalog build that consumed it. This design does not choose between them.

**`catalog_writer.py`.** Serializes the final assembled graph to `catalog/catalog.json`, in exactly the JSON shape Catalog Contract 1.0 Parts 2–6 define — the one place `json.dump`-equivalent output happens in the whole package. Trusts that Part 6's validation layer already ran and blocked anything that would produce an invalid file; performs no validation of its own.

---

## Part 8 — CLI Architecture

*Responsibilities only, no argument syntax, per the instruction — each entrypoint's name and role already fixed by Catalog Implementation Architecture Part 7; this section gives each one its internal call shape.*

**`build_catalog.py`.** Runs Part 2's full pipeline end to end, in order, calling every layer's modules exactly once, and exits non-zero if `validation_report.py`'s aggregate verdict blocks publication — the direct analogue of `run_pipeline.py`'s role for the KSBCL pipeline.

**`validate_enrichment.py`.** Calls `enrichment_reader.py`/`enrichment_schema.py` only — Layer 1 validation, standalone, fast enough to run before every commit touching `enrichment/`, requiring no `beer_master.csv` load at all.

**`validate_catalog.py`.** Calls the full Part 6 validation layer against either an already-published `catalog/catalog.json` (a standalone health check) or a freshly-assembled candidate (what `build_catalog.py` calls internally at its own Step 10) — the same validation logic, two different entry points into it.

**`diff_catalog.py`.** Loads two `catalog.json` files and reports added, removed, and materially-changed Skus between them — reads only, calls nothing from the loading/join/compute/validate layers, since both inputs are already-built, already-valid catalogs.

**`enrichment_report.py`.** Calls `join.py` against the current `beer_master.csv` and `enrichment/` tree, and reports every unmatched `canonical_product_id` plus every matched Beer still missing a Launch-Critical field — the concrete CLI form of the "Enrichment Queue" responsibility Catalog Builder Architecture's own Part 8 already named.

**`merge_review.py`.** Calls `merge_check.py` only, and reports its findings in human-readable form.

---

## Part 9 — Testing Architecture

**Unit tests, one `tests/test_<module>.py` per logic module** (`value_metrics`, `benchmarks`, `value_score`, `join`, `contamination_filter`, `schema_validate`, `cross_reference_validate`, `business_rules`) — mirroring the real package's own exact convention (`test_canonical_key.py`, `test_matching.py`, `test_validate.py`, one file per module, confirmed directly from the real `tests/` directory listing). Every pure-computation module (`value_metrics.py`, `benchmarks.py`, `value_score.py`) is testable with plain in-memory data, no fixture files needed at all — the cheapest, fastest tests in the whole suite, and per Part 10, the first ones that can actually be written.

**Golden catalog tests.** A small, fixed, hand-crafted `beer_master.csv` fixture plus a matching `enrichment/` fixture tree, run through the full `build_catalog.py` pipeline, with the resulting `catalog.json` compared field-for-field against a checked-in expected output. **[Inference, not directly confirmed]** this mirrors the general "fixture in, expected artifact out" shape already implicit across the real pipeline's own `test_run_stage2.py`–`test_run_stage5.py` files (inferred from their naming and role in the pipeline, not verified by reading their full contents for this document) — flagged as inference rather than confirmed evidence, since those specific test files weren't read in full here.

**Regression tests.** Re-run the full build against a fixed, real historical input — specifically **recommended: `pricing_data/runs/2026-06`'s own real output**, since it is the one real dataset already confirmed, in this session's own prior inspection, to contain the two known contamination cases (`CP0000001`, `CP0000955`) — asserting `catalog_version` increments correctly, and that no previously-published Sku silently disappears between runs without a named reason in the validation report.

**Validation fixtures, one per rule, engineered to trigger exactly one failure each:** a row missing ABV; a `package_type`/`container_type` value outside the app's closed enum (directly exercising the flagged incompatibility from Part 6); a dangling `beer_id` reference; a duplicate `style_id`; an unlicensed image entry. **Recommendation:** the two real, already-confirmed contaminated rows (`CP0000001` — Budweiser whiskey via brand-name false-positive; `CP0000955` — Glenfiddich "IPA Experiment" whisky via style-keyword false-positive) should be used directly as `contamination_filter.py`'s own regression fixtures, rather than constructing synthetic equivalents — they are real, proven, already-adversarial cases sitting in this repository's own data today, and a filter that doesn't reject both of them, byte for byte as they exist in the real `beer_master.csv`, is not actually fixed.

**Failure fixtures:** malformed YAML (unparseable, missing required key); a `beer_master.csv` with a renamed/missing column header (structural failure, should abort); an unparseable individual price cell (row-level failure, should exclude that row only, matching §0.2's two-tier convention).

---

## Part 10 — Implementation Roadmap

*Smallest sequence, ordered by dependency, translating Catalog Implementation Architecture's own already-frozen Part 9 migration plan into module-build order — not a new sequence, a more granular expression of the same one.*

1. **`models.py`** — zero dependencies, pure dataclasses. Nothing else can be written before this exists.
2. **`value_metrics.py`, `benchmarks.py`, `value_score.py`** — depend only on `models.py`'s Sku shape, no I/O at all. **The single cheapest, fastest-to-test layer in the whole package** — buildable and fully unit-testable before any file-reading code exists, using only in-memory fixture data.
3. **`beer_master_reader.py`, `enrichment_reader.py`, `enrichment_schema.py`** — depend on `models.py`; testable independently against small fixture files, with no join logic needed yet.
4. **`join.py`** — depends on both readers' output shapes (step 3); testable with small, hand-built fixture sets pairing a few `BeerMasterRow`s against a few `EnrichmentBeer`s.
5. **`contamination_filter.py`, `schema_validate.py`, `cross_reference_validate.py`, `business_rules.py`, `validation_report.py`** — depend on steps 2–4's combined output. **This is the first point the two real confirmed contamination fixtures (Part 9) can actually be exercised.**
6. **`assemble.py`, `version.py`, `catalog_writer.py`, `build_manifest.py`** — depend on everything above. **This is the first point a complete, real, non-placeholder `catalog.json` can actually be produced** — the natural point to first run the golden-catalog test (Part 9), since only now does a stable output shape exist to snapshot.
7. **`build_catalog.py`** — thin orchestration only, depends on every module above already working.
8. **Golden and regression tests** (Part 9) — written once step 6/7 produces a real, stable artifact, not before, since there is nothing yet to compare against earlier.
9. **`merge_check.py`, `validate_enrichment.py`, `validate_catalog.py`, `diff_catalog.py`, `enrichment_report.py`, `merge_review.py`** — every one of these is a thin wrapper around logic already built in steps 1–6; genuinely deferrable, matching Catalog Implementation Architecture's own already-frozen Part 9 sequencing (its steps 7–8), not a new deferral decided here.

**What can be tested first, stated plainly since it's the most actionable fact in this roadmap:** step 2's three computation modules. They need no CSV, no YAML, no file I/O, no fixtures beyond a few hand-written in-memory dataclass instances — every other module in this package depends, directly or transitively, on getting these three right first.
