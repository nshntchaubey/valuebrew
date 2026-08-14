# ValueBrew — Catalog Implementation Backlog

**[HISTORICAL — superseded by RC1, 2026-08-14.** This backlog's Part 5 task list (38 tasks) is complete: `tool/catalog_builder/` and `enrichment/` are both built, tested, and shipped; `catalog/catalog.json` is real, generated production output. Kept as the historical record of the plan that was executed, not as a current-state document — see `docs/PROJECT-BRAIN.md` §16 for current status. The rest of this document is left unedited below.]**

*An implementation audit, not architecture. Every decision this document depends on has already been made, across Decision Engine 2.0, Beer Knowledge Model 2.0, Domain Model 1.0, Beer Entity Specification 1.0, Catalog Specification 1.0, Catalog Contract 1.0, Catalog Builder Architecture, Catalog Implementation Architecture, Catalog Builder Implementation Design, the Catalog Enrichment Playbook, the Beer Knowledge Base Architecture, the Recommendation Engine Implementation, and the four Experience Specifications — all read in full again for this audit, cross-checked directly against the actual repository state. This document adds no new decision anywhere. It answers one question only: what code, in what order, gets the repository from where it stands today to a real, populated `catalog.json` running inside the app.*

---

## Part 1 — Current Implementation Status

| Subsystem | Status | Evidence |
|---|---|---|
| **KSBCL pipeline, Stages 1–5** (`tool/ksbcl_pricing_pipeline/`) | **Exists** | Real, tested, ~35 Python modules; a real 2026-06 run produced 1,005 live retail rows in `pricing_data/beer_master.csv`, 152 duty-free rows, 1,715 rows in `item_code_canonical_map.csv` |
| **Beer classification / contamination guard** (Stage 2) | **Partially exists** | The exclusion-guard mechanism exists and fired 59 times in the 2026-06 run — but two confirmed non-beer rows (`CP0000001` Budweiser whiskey, `CP0000955` Glenfiddich whisky) are currently live in `beer_master.csv` today, undetected |
| **Beer Knowledge Base** (`enrichment/`) | **Missing** | Directory does not exist anywhere in the repository (confirmed by direct search before this audit) |
| **Catalog Builder** (`tool/catalog_builder/`) | **Missing** | Directory does not exist; zero lines of code against a fully specified design |
| **Recommendation Engine** (`lib/features/recommendation/domain/`) | **Exists, complete** | `generate_recommendation.dart` and its three supporting files are real, correct per Decision Engine 2.0, and require no change for catalog integration |
| **`catalog.json`** (production artifact) | **Missing** (a placeholder exists) | `catalog/catalog.json` is a hand-authored, 1-SKU file, unconnected to any real pipeline output |
| **Flutter catalog loading** (`CatalogRepository`, `CatalogLocalCache`, `CatalogRemoteSource`) | **Exists, complete, fully wired to production** | `catalog_provider.dart` confirmed directly: `catalogRepositoryProvider` already constructs `SharedPreferencesCatalogLocalCache` and `HttpCatalogRemoteSource` for real use, not test stubs; six real test files already exist under `test/unit/catalog_*` |
| **Remote catalog update (CDN)** | **Exists, unverified against real content** | `AppConstants.remoteCatalogUrl` is a real, live jsDelivr mirror of this repo's own `catalog/catalog.json`; it has never yet served anything but the 1-SKU placeholder |
| **Validation** (enrichment schema, cross-reference, business rules) | **Missing** | Zero validation code exists anywhere for this layer; fully specified, nothing written |
| **CLI tools** (`build_catalog.py` and five others) | **Missing** | Zero CLI scripts exist |
| **Generation 1 dead code** (`models/`, `policy/`, `scoring/`, `services/`, `providers/recommendation_providers.dart`, the second `beer_detail_screen.dart`, the second `home_screen.dart`, `features/compare/`, `features/favorites/`, `features/filtering/`, `features/sorting/`) | **Not removed** | Confirmed unreachable from `app.dart` across four prior sessions of direct inspection; still present in the repository |

---

## Part 2 — Implementation Dependency Graph

Every box is a real file or directory. Every arrow is real work — either already done (✓) or still required (→ **BUILD**).

```
pricing_data/beer_master.csv                    [EXISTS — real, 1,005 live rows]
        │
        │ ✓ (already produced, monthly, by Stages 1–5)
        ▼
[STAGE-2 CONTAMINATION FIX]  ──────────────────► → BUILD: a second, independent
        │                                            spirit-term gate, run before
        │                                            or inside the Catalog Builder
        ▼
enrichment/ (styles.yaml, beers/*.yaml)          [MISSING — → BUILD: directory,
        │                                          schema, README, then real
        │                                          curated content per beer]
        │
        │ → BUILD: enrichment_reader.py, enrichment_schema.py
        ▼
tool/catalog_builder/ (19 modules + 6 CLIs)      [MISSING — → BUILD: entire package,
        │                                          per Catalog Builder Implementation
        │                                          Design Parts 1–8]
        │
        │ → BUILD: join.py, value_metrics.py, benchmarks.py, value_score.py,
        │   contamination_filter.py, schema_validate.py,
        │   cross_reference_validate.py, business_rules.py, assemble.py
        ▼
catalog/catalog.json (real, production content)  [MISSING — currently a
        │                                          1-SKU placeholder]
        │
        │ ✓ pubspec.yaml already bundles this exact path — no change needed
        ▼
lib/catalog/data/CatalogRepository               [EXISTS, COMPLETE]
        │
        │ ✓ already wired: bundled asset → SharedPreferencesCatalogLocalCache
        │   → HttpCatalogRemoteSource, in catalog_provider.dart
        ▼
Running app                                       [EXISTS, COMPLETE —
                                                     will render real data the
                                                     moment real data exists]
        │
        │ → VERIFY (not build): commit real catalog.json to main, confirm the
        │   jsDelivr URL actually serves it, confirm an installed app picks
        │   it up via its next remote check
        ▼
Every already-installed app                       [reached automatically,
                                                     zero new code, per
                                                     Catalog Implementation
                                                     Architecture §0.2]
```

**The single sentence this graph reduces to:** everything left of `catalog/catalog.json` is missing; everything right of it already exists and works. The entire remaining implementation effort is concentrated in exactly two places — `enrichment/`'s real content, and `tool/catalog_builder/`'s real code.

---

## Part 3 — Missing Code

*Pure inventory. No field, module, or rule listed here is newly decided — every one is already specified in Catalog Builder Implementation Design (module architecture), Catalog Contract 1.0 (schema), Catalog Builder Architecture (validation rules), or the Beer Knowledge Base Architecture (enrichment schema).*

**Python modules, `tool/catalog_builder/` — none exist:**
`__init__.py` · `models.py` · `beer_master_reader.py` · `enrichment_reader.py` · `enrichment_schema.py` · `join.py` · `merge_check.py` · `value_metrics.py` · `benchmarks.py` · `value_score.py` · `contamination_filter.py` · `schema_validate.py` · `cross_reference_validate.py` · `business_rules.py` · `validation_report.py` · `assemble.py` · `version.py` · `build_manifest.py` · `catalog_writer.py`

**CLI entrypoints — none exist:**
`build_catalog.py` · `validate_enrichment.py` · `validate_catalog.py` · `diff_catalog.py` · `enrichment_report.py` · `merge_review.py`

**Validators — none exist, distinct from the modules above by rule content, not by file:**
- Structural: `enrichment_schema.py` (required keys, ABV range, attribution-block completeness)
- Cross-reference: `cross_reference_validate.py` (`Sku.beer_id`→`Beer.id`, `Beer.style_id`→`Style.id`, `Benchmark.style_id`→`Style.id`, duplicate-ID detection — this last check is confirmed, per Catalog Contract 1.0 Part 7, to be enforced nowhere at all today, in either the app or any pipeline code)
- Business rules: `business_rules.py` (missing mandatory fields, broken image licensing, stale-price and listing-inconsistency warnings)
- Contamination: `contamination_filter.py` (the independent spirit-term gate)
- Schema/enum: `schema_validate.py` (including the confirmed `package_type`/`container_type` closed-enum mismatch — real 2026-06 data shows a 29.6% `unknown` container-type rate that the app's `PackageType.fromJson` cannot parse at all)

**YAML schema and scaffolding — none exist:**
`enrichment/README.md` · `enrichment/styles.yaml` (needs real seed content) · `enrichment/beers/` (empty directory, needs real files)

**Test infrastructure — none exists:**
`tool/catalog_builder/tests/__init__.py` · one `test_<module>.py` per logic module (≈14 files) · `tests/fixtures/` (a golden-catalog fixture pair, and dedicated failure fixtures — including the two real, already-confirmed contamination rows as regression fixtures)

**Missing Flutter integration: none.** Confirmed directly, again, for this audit — `CatalogRepository`, `CatalogLocalCache`, `CatalogRemoteSource`, and the production `catalogRepositoryProvider` wiring are all complete, tested-shaped, and require zero new code. The only Flutter-adjacent gap is **verification**, not implementation: nothing has yet confirmed the app renders correctly against a real, multi-hundred-SKU `catalog.json`, only against the 1-SKU placeholder and small unit-test fixtures.

**Missing build manifest location: unresolved, not merely unbuilt.** Catalog Builder Implementation Design Part 7 already flagged this as an open implementation ambiguity — `build_manifest.py` cannot be finished until this is decided. Listed here again because it blocks a specific, real file from being written, not because it's new.

---

## Part 4 — Implementation Order

*Reusing the sequencing Catalog Builder Implementation Design Part 10 already fixed, expressed here as one linear path to a first production catalog, with the enrichment side interleaved where it actually has to happen.*

1. **Fix the Stage-2-independent contamination gate.** The two confirmed live rows must stop being publishable before anything else is trustworthy — this is the one item on this list that touches existing pipeline-adjacent behavior rather than purely new code, so it goes first, gated on the cross-package-dependency ambiguity (Part 6) being resolved one way or the other.
2. **`models.py`.** Zero dependencies — the base of everything else.
3. **`value_metrics.py`, `benchmarks.py`, `value_score.py`.** Pure computation, no I/O, testable immediately in isolation.
4. **`beer_master_reader.py`, `enrichment_reader.py`, `enrichment_schema.py`.** Depend only on `models.py`.
5. **Scaffold `enrichment/`** — `README.md`, seed `styles.yaml`, empty `beers/` — the first point real curated data can be written at all.
6. **`join.py`.** Depends on step 4's output shapes.
7. **First real enrichment batch** — enough beers (Catalog Enrichment Playbook's own 20-per-session cadence, run a handful of times) to have a real, non-trivial candidate set to build against.
8. **`contamination_filter.py`, `schema_validate.py`, `cross_reference_validate.py`, `business_rules.py`, `validation_report.py`.** Exercised immediately against step 7's real data and the two known contamination fixtures.
9. **`assemble.py`, `version.py`, `catalog_writer.py`, `build_manifest.py`** (location decided per Part 6). First point a complete, real `catalog.json` can be produced.
10. **`build_catalog.py`.** Thin orchestration over steps 2–9.
11. **First real end-to-end build.** Diff its output against the current placeholder by hand; confirm the real, already-existing `Catalog.fromJson` parses it without any app-side change.
12. **Commit the real `catalog/catalog.json` to `main`.** Verify the jsDelivr URL actually serves it.
13. **Verify in the running app.** Confirm `catalogProvider` picks up the real content, either via a fresh install (bundled asset) or a remote-fetch check on an existing one.
14. **Remaining CLI tools and tests** (`validate_enrichment.py`, `validate_catalog.py`, `diff_catalog.py`, `enrichment_report.py`, `merge_review.py`, golden/regression suite) — deferred behind step 13, per Catalog Implementation Architecture's own already-frozen sequencing, since none of them block the first real catalog from existing.

**This is the exact sequence; nothing on this list can move earlier than its stated dependency without redoing work.**

---

## Part 5 — Developer Backlog

*Atomic tasks. One engineer, one task, one Definition of Done, nothing larger than one day. Numbered to match Part 4's phases, not a separate ordering.*

| # | Task | Definition of Done |
|---|---|---|
| 1 | Resolve the contamination-filter dependency question (import KSBCL's `beer_classification.yaml` vs. maintain an independent copy) | A decision is recorded (even informally, in a commit message or a one-line note) and `contamination_filter.py`'s design is unblocked |
| 2 | Write `contamination_filter.py` (or its equivalent inside the pipeline, per task 1's outcome) | Rejects both `CP0000001` and `CP0000955` from the real, current `beer_master.csv`; passes a unit test asserting exactly that |
| 3 | Create `tool/catalog_builder/` package skeleton (`__init__.py` only, docstring citing the implementation design doc) | `python -m tool.catalog_builder` imports cleanly with no error |
| 4 | Write `models.py` | Every dataclass named in Catalog Builder Implementation Design Part 1 exists; no logic, no I/O |
| 5 | Write `value_metrics.py` + its unit test | `cost_per_litre`/`cost_per_ml_alcohol` match hand-computed values for 3 fixture SKUs |
| 6 | Write `benchmarks.py` + its unit test | Given a fixture Sku population, `avg`/`p25`/`p50`/`p75`/`sample_size` match hand-computed values |
| 7 | Write `value_score.py` + its unit test | Given a fixture Benchmark, `value_score`/`value_verdict` match hand-computed values for at-median, above-median, and below-median fixtures |
| 8 | Write `beer_master_reader.py` + its unit test | Parses a small fixture CSV into `BeerMasterRow`s; a header mismatch raises, a bad row is excluded and reported, not raised |
| 9 | Write `enrichment_schema.py` + its unit test | Validates a fixture set of well-formed and malformed enrichment YAML; every required key/attribution-block rule is exercised by at least one failing fixture |
| 10 | Write `enrichment_reader.py` + its unit test | Loads a fixture `enrichment/` tree into `EnrichmentBeer`/`StyleDef` objects; a malformed file is excluded and reported, not fatal to the whole load |
| 11 | Create `enrichment/README.md` | States the file shape from Beer Knowledge Base Architecture Part 3, points to the Catalog Enrichment Playbook for workflow |
| 12 | Create `enrichment/styles.yaml` with real seed content | Contains every style already implied by real, currently-enriched-or-about-to-be-enriched `beer_master.csv` rows (start small — Lager, Strong Lager, whatever the first batch actually needs) |
| 13 | Enrich the first 20 real beers (Catalog Enrichment Playbook, one session) | 20 `enrichment/beers/*.yaml` files exist, each passing `enrichment_schema.py`'s own validation |
| 14 | Write `join.py` + its unit test | Given fixture `BeerMasterRow`s and `EnrichmentBeer`s, correctly pairs matches and correctly routes non-matches to an "unenriched" list; a duplicate `canonical_product_id` mapping raises |
| 15 | Write `schema_validate.py` + its unit test | Rejects a fixture Sku with a `container_type` outside the app's closed `PackageType` enum; accepts a fixture Sku with valid `bottle`/`can`/`pint` |
| 16 | Write `cross_reference_validate.py` + its unit test | Rejects a fixture Sku with a dangling `beer_id`; rejects a fixture set with a duplicate `Style.id` |
| 17 | Write `business_rules.py` + its unit test | Rejects a fixture Sku missing ABV; flags (does not reject) a fixture Sku with a stale `priceLastChecked` |
| 18 | Write `validation_report.py` + its unit test | Aggregates fixture validator outputs into one pass/block verdict with itemized reasons |
| 19 | Write `merge_check.py` + its unit test | Given a fixture `item_code_canonical_map.csv` with one repointed ID, correctly flags the one enrichment file referencing it |
| 20 | Decide and document the build-manifest file location | A path is chosen (e.g. `catalog/catalog_build_manifest.json` or `pricing_data/runs/YYYY-MM/catalog_build_manifest.json`); `build_manifest.py`'s design is unblocked |
| 21 | Write `assemble.py` | Given joined, computed, validated fixture data, produces an in-memory Style/Beer/Sku/Benchmark graph matching Catalog Contract 1.0's shape exactly |
| 22 | Write `version.py` + its unit test | Reads a fixture prior `catalog_version`, returns it plus one; returns `0`+1 when no prior catalog exists |
| 23 | Write `build_manifest.py` | Writes a manifest with the pipeline-run reference and enrichment content-hash, at the location task 20 fixed |
| 24 | Write `catalog_writer.py` + its unit test | Serializes a fixture assembled graph to JSON matching Catalog Contract 1.0's field names exactly; round-trips through the real Dart `Catalog.fromJson` shape (checked by hand against Parts 2–6 of that contract) |
| 25 | Write `build_catalog.py` | Runs steps 4–24 end to end against the real, current `pricing_data/` and `enrichment/`; exits non-zero on any blocking validation failure |
| 26 | Run the first real end-to-end build | A real `catalog.json` candidate exists on disk, distinct from the current placeholder, containing the 20 beers from task 13 |
| 27 | Diff the real build output against the current placeholder by hand | A written note (even brief) confirms every field matches Catalog Contract 1.0's schema and every value traces to a real source |
| 28 | Parse the real build output through the app's real `Catalog.fromJson` (a throwaway script or a widget test) | No exception; every field populates as expected |
| 29 | Replace `catalog/catalog.json` with the real build output; increment `catalog_version` | File committed |
| 30 | Verify the jsDelivr URL serves the new file | A direct fetch of `AppConstants.remoteCatalogUrl` returns the new content, confirmed by hand |
| 31 | Verify the running app against the new content (fresh install and/or remote-fetch path) | Home → Recommendation → Beer Detail all render real data correctly for at least one real query |
| 32 | Write `validate_enrichment.py` (CLI wrapper around task 9's logic) | Runs standalone against `enrichment/`, no `beer_master.csv` load required |
| 33 | Write `validate_catalog.py` (CLI wrapper around tasks 15–18's logic) | Runs standalone against a built `catalog.json` |
| 34 | Write `diff_catalog.py` | Given two `catalog.json` files, reports added/removed/changed SKUs |
| 35 | Write `enrichment_report.py` (CLI wrapper around task 14's "unenriched" output) | Reports every unmatched `canonical_product_id` and every enriched beer still missing a mandatory field |
| 36 | Write `merge_review.py` (CLI wrapper around task 19) | Reports every stale enrichment reference in human-readable form |
| 37 | Write the golden-catalog test | A fixed fixture set produces a byte-identical expected `catalog.json`, checked into `tests/fixtures/` |
| 38 | Write the regression test against real `pricing_data/runs/2026-06` | Asserts `catalog_version` increments correctly and no previously-published Sku silently disappears without a named reason |
| **—** | *Not required to reach a first production catalog; listed for completeness only* | Delete the eleven confirmed-dead Generation-1 files/directories named in Part 1 |

---

## Part 6 — Critical Risks

*Implementation risk only — nothing about product strategy, market fit, or business decisions.*

**The whiskey contamination gate is not yet built, and building it late means it ships in the first real catalog.** Two confirmed non-beer rows sit in `beer_master.csv` today. If task 1/2 slips behind task 26 (the first real build), those rows are eligible for enrichment and publication like any other candidate — a founder enriching beers by hand has no independent signal telling them a given `canonical_product_id` is actually a whisky.

**The `package_type`/`container_type` enum mismatch will silently shrink the enrichable candidate pool by roughly 30% if not resolved before large-scale enrichment begins.** Real 2026-06 data shows a 29.6% `unknown` container-type rate. Every one of those rows fails `schema_validate.py` (task 15) today, by design — meaning a founder could spend real research time enriching a beer whose SKU can never actually publish, discovering this only when the build rejects it. Sequencing enrichment (task 13 onward) after `schema_validate.py` exists (task 15) — rather than the linear order in Part 4 — would surface this earlier and cheaper; this is worth a deliberate resequencing decision before task 13 begins at any real volume.

**The duplicate-ID validation gap (Catalog Contract 1.0 Part 7) is enforced nowhere today, in the app or the pipeline.** Until `cross_reference_validate.py` (task 16) exists, a hand-authoring mistake in `enrichment/` producing two `beer_key`s that collide, or two Styles with the same `id`, would only surface as a downstream app bug, not a build-time failure.

**Two implementation ambiguities (Catalog Builder Implementation Design Part 6/7) currently block real code from being finished, not just being started.** The contamination-filter dependency question (task 1) and the build-manifest location (task 20) both have to be *decided*, not merely implemented — leaving either open past the task that depends on it stalls real, otherwise-ready work.

**Enrichment volume is the actual critical path, not code.** Every Python module in this backlog is small, pure, and fast to build and test — realistically days, not weeks, of engineering time in total. The first production catalog's real bottleneck is task 13 and its repetitions: real human research, one beer at a time, at whatever pace the Catalog Enrichment Playbook's own 20-per-session cadence actually sustains. Any schedule for "first production catalog" should be built around enrichment throughput, not module count.

**No test coverage exists for any of this today, because none of the code exists today.** Stated plainly as a risk, not a status: every module in Part 5 has its test written in the same task as the module itself specifically to prevent a scenario where the whole `tool/catalog_builder/` package gets built first and tested only at the end, against a real catalog, where a bug is far more expensive to trace back to its source module.

---

## Part 7 — Definition of "Version 1 Complete" (Catalog Builder)

The Catalog Builder is Version 1 Complete at the exact moment all of the following are simultaneously true:

- `build_catalog.py` runs end to end against the real, current `pricing_data/` and `enrichment/`, with no manual intervention beyond invoking it.
- The `catalog.json` it produces passes every rule in Catalog Contract 1.0 Part 8's validation contract, including the structural round-trip check against the app's real `Catalog.fromJson`.
- The independent contamination gate correctly rejects both confirmed real adversarial fixtures (`CP0000001`, `CP0000955`) and any equivalent case a fixture is later added for.
- Every module and CLI listed in Part 3 exists, with its own passing unit test.
- The golden-catalog test and the real-data regression test (Part 5, tasks 37–38) both exist and pass.
- No open implementation ambiguity from Catalog Builder Implementation Design (Parts 6–7) remains undecided.

**Not required for Version 1 Complete:** any specific number of enriched beers. Version 1 Complete is a statement about the *tool* being correct and finished, independent of how much real content has been fed through it yet.

---

## Part 8 — Definition of "Launch Ready"

The app has transitioned from placeholder catalog to real catalog at the exact moment all of the following are simultaneously true:

- `catalog/catalog.json` in the repository is a genuine Catalog Builder output, not the hand-authored placeholder — its `generated_at` and build manifest trace to a real `build_catalog.py` run.
- It has been committed and pushed to `main`.
- A direct fetch of `AppConstants.remoteCatalogUrl` returns that exact content.
- A real, running instance of the app — fresh install or an existing install's next remote-fetch check — successfully loads it and renders at least one real Recommendation, one real Beer Detail, and one real Price Verification against genuinely enriched data, with no parse error and no validation failure surfaced anywhere in that path.
- The SKU count and field completeness in that catalog satisfy every Launch-Critical requirement Catalog Specification 1.0 already named — restated, not redefined, here: every published SKU carries Beer Identity, Legal Price, Size/Package, and ABV, at minimum.

**Not required for Launch Ready:** every CLI tool from Part 5 built (tasks 32–38 are explicitly deferrable, per Part 4's own sequencing); Generation 1 dead code removed; any enrichment field beyond what Catalog Builder Architecture already marks Launch Critical.
