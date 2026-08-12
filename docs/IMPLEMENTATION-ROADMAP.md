# ValueBrew — Implementation Roadmap

*The final bridge between architecture and code. Not another architecture document — every decision this document depends on has already been made, across the Project Brain, the Product Decisions Register, the Execution Backlog, and every catalog/recommendation implementation document this session produced. This document answers exactly one question: if a new engineer joined tomorrow, in what order should they build ValueBrew. Grounded in a fresh, direct re-verification of the actual repository state (run immediately before writing this document, not assumed from memory) and the current, uncommitted working tree. After this document, the next activity is writing software.*

---

## Part 1 — Current State

**Production-ready — built, correct, requires no further work for the path this document defines:**
- **KSBCL pipeline, Stages 1–5** (`tool/ksbcl_pricing_pipeline/`) — real, tested, producing `pricing_data/beer_master.csv` monthly. **Caveat, not a build gap: see Implementation Blockers.**
- **Flutter catalog loading** (`CatalogRepository`, `CatalogLocalCache`, `CatalogRemoteSource`) — confirmed, again, by direct inspection of `catalog_provider.dart` for this document: fully wired to production (`SharedPreferencesCatalogLocalCache`, `HttpCatalogRemoteSource`), not test stubs.
- **Remote catalog distribution** — the jsDelivr CDN mirror of `catalog/catalog.json` is live and configured (`AppConstants.remoteCatalogUrl`); no server, no new infrastructure needed.
- **Recommendation Engine** (`lib/features/recommendation/domain/`) — pure, correct, already matches Decision Engine 2.0's reasoning model exactly; needs no change for real-catalog integration (Recommendation Engine Implementation, §0).
- **Recommendation screen** (`lib/features/recommendation/presentation/`) — real, reachable, already verified against the domain layer (Recommendation Widget Specification).
- **Beer Detail screen** (`lib/features/beer_detail/presentation/`) — real, reachable, already verified (Beer Detail Experience Specification); one safe, scoped copy fix identified there (a bare "Value score: N" string) but not yet applied.
- **Price Verification screen** (`lib/features/price_verification/presentation/`) — real, reachable, already verified (Price Verification Experience Specification) — the most precisely-matched implementation found in this whole review; no changes proposed.
- **Home screen** (`lib/features/discovery/presentation/`) — real, reachable, minimal, correctly scoped to its own doc comment's admission that Search/Browse and Price Verification entry points "arrive incrementally."

**Partially complete:**
- **`catalog/catalog.json`** — exists, loads, parses correctly, but is still the original 1-SKU hand-authored placeholder (confirmed again by direct inspection: `catalog_version: 1`, one SKU). Not a real, Catalog-Builder-produced artifact.
- **The whiskey-contamination fix** — confirmed, by direct inspection of the current working tree, to already exist: `tool/ksbcl_pricing_pipeline/beer_classification.yaml` and `tests/test_classify.py` are both modified (uncommitted), adding `whiskey` to the exclusion vocabulary. **But it has not been applied to real data** — `pricing_data/beer_master.csv` still contains both confirmed contaminated rows (`CP0000001`, `CP0000955`), because Stages 4–5 were deliberately not re-run after the fix landed (Project Brain §11, item 4). The fix is real; the data it should have cleaned is not yet clean.

**Specified but unbuilt:**
- **`tool/catalog_builder/`** — the entire package (19 modules, 6 CLIs) is fully specified in Catalog Builder Implementation Design; zero lines of it exist (confirmed by direct search immediately before writing this document).
- **`enrichment/`** — the Beer Knowledge Base directory, fully specified in Beer Knowledge Base Architecture; does not exist anywhere in the repository.
- **Comparison screen** — fully specified (Comparison Experience Specification); the real, canonical implementation has zero lines of code. `lib/features/compare/` exists but is confirmed, again, unreachable from `app.dart` — dead Generation 1 code, not a partial implementation of the real thing.

**Completely absent:**
- Search/Browse Results — not merely unbuilt, has no Screen Contract anywhere in canon (Product Decisions Register D2). Genuinely a step further back than "specified but unbuilt."
- Any validation tooling for `enrichment/` or `catalog.json` (`schema_validate.py`, `cross_reference_validate.py`, etc.) — none exists.
- Any build manifest, versioning tooling, or CLI of any kind for the catalog side.

---

## Part 2 — Build Order

*One sequence, each step justified by what it structurally requires from the step before it. Reuses Catalog Implementation Backlog's own already-established sequencing for the catalog-internal steps (its Part 4) rather than re-deriving it; adds the steps before and after that backlog's own scope.*

**Step 0 — Resolve the pipeline data-integrity risk before touching Stage 2–5 again.** The whiskey fix cannot be safely applied to real data by simply re-running Stages 2–5, because Stage 4's `canonical_resolve.py` carries a live, unfixed defect (`true_prior_map` construction) that can corrupt the canonical identity map on a same-month rerun (Project Brain §11, item 3). This must be understood and either fixed or explicitly, safely worked around (e.g., a from-scratch rebuild rather than an in-place rerun) before Step 1 can proceed with real confidence. **This comes first because every later step trusts `beer_master.csv` being correct, and right now that trust is not yet earned for a rerun.**

**Step 1 — Build the pure-computation layer of the Catalog Builder** (`models.py`, `value_metrics.py`, `benchmarks.py`, `value_score.py`). These have zero dependency on real data or on `enrichment/` existing — they're pure functions over in-memory fixtures. **This comes before anything else buildable because every later catalog-side module depends on it, and it's the cheapest, fastest thing to get right first** (Catalog Builder Implementation Design, Part 10).

**Step 2 — Build the loading layer** (`beer_master_reader.py`, `enrichment_reader.py`, `enrichment_schema.py`) **and, in parallel, scaffold `enrichment/`** (`README.md`, seed `styles.yaml`, empty `beers/`). These two can genuinely proceed together — the reader code needs fixture data to test against, and scaffolding the real directory produces exactly that. **This comes after Step 1 because both readers parse into the dataclasses Step 1 defined.**

**Step 3 — Enrich a first real batch of beers** (Catalog Enrichment Playbook's own 20-per-session cadence, run a handful of times) **against the real, current `beer_master.csv`.** This can start the moment Step 2's scaffolding exists — it does not need `join.py` or any further code, only a place to write files. **This comes here, not later, because it's the actual long pole of the whole roadmap (founder research time, not engineering time), and starting it late for no reason simply delays everything after it.**

**Step 4 — Build the join layer** (`join.py`) **and the contamination/validation layer** (`contamination_filter.py`, `schema_validate.py`, `cross_reference_validate.py`, `business_rules.py`, `validation_report.py`), **testing the contamination filter directly against the two real confirmed contaminated rows.** This comes after Step 3 produces at least a few real enriched beers to join against, and after Step 1/2 provide the data shapes it operates on.

**Step 5 — Build the serialization layer** (`assemble.py`, `version.py`, `catalog_writer.py`, `build_manifest.py`, once its file location is decided). **This is the first point a complete, real, non-placeholder `catalog.json` can exist.** It depends on every prior step.

**Step 6 — Run the first real end-to-end build, verify it by hand against Catalog Contract 1.0, and confirm the real, unchanged `Catalog.fromJson` parses it without error.** This is a verification step, not new code — the schema was never going to change, so this is about proving the pipeline, not the app.

**Step 7 — Commit the real `catalog/catalog.json` to `main`; verify the jsDelivr URL serves it.** Zero new code — this is Catalog Implementation Architecture's own already-confirmed-working distribution path, exercised for the first time with real content.

**Step 8 — Verify the running app against real content**, across Home → Recommendation → Beer Detail → Price Verification, on at least one real device or simulator. This is the first point every already-built screen is actually proven against reality rather than a placeholder or a unit-test fixture.

**Comparison, Search/Browse, remaining CLI tools (`validate_enrichment.py`, `diff_catalog.py`, `enrichment_report.py`, `merge_review.py`), and Generation 1 dead-code removal are all explicitly not in this sequence** — none of them are required to reach the goal Part 4 defines, and Execution Backlog's own Prioritization (P3) already, independently, defers Comparison and Search/Browse past launch. Building them earlier would not be wrong, only unnecessary for this specific path.

---

## Part 3 — Milestones

Each milestone has one concrete, binary completion test — not a percentage, not a feeling.

**M1 — Beer Knowledge Base exists.**
*Test:* `enrichment/styles.yaml` and at least 20 real `enrichment/beers/*.yaml` files exist, each referencing a real `canonical_product_id` present in the current `beer_master.csv`, and each passes `enrichment_schema.py`'s structural validation with no errors.

**M2 — Catalog Builder produces a valid `catalog.json`.**
*Test:* running `build_catalog.py` end to end against real `pricing_data/` and real `enrichment/` produces a file that (a) passes every rule in Catalog Contract 1.0's validation contract, including the structural round-trip through the app's real `Catalog.fromJson`, and (b) correctly rejects both confirmed contaminated rows, by design, not by accident.

**M3 — Real catalog loads in the app.**
*Test:* `catalog/catalog.json` is replaced with M2's real output, committed to `main`, and a fresh app install (or an existing install's remote-fetch check) successfully loads it with no `CatalogParseException` and no fallback to a cached/bundled placeholder.

**M4 — Every existing screen renders real data correctly.**
*Test:* Home, Recommendation, Beer Detail, and Price Verification each complete a real, human-driven flow against the real catalog with zero crashes and no visibly wrong content (a beer's name, price, and ABV on screen match what's actually in `catalog.json`).

**M5 — Recommendation produces a correct, sensible answer against real data.**
*Test:* a human enters a real, plausible budget and optionally a real style, and the returned `RecommendationOutcome` (a winner, a tie, or an honest no-match) is independently checked by hand against the real catalog's own prices and Value Scores and found correct — not merely "did not crash," but "the math is actually right for this real data."

**M6 — A founder validates it in a real store.**
*Test:* standing in an actual Karnataka retail liquor outlet, the founder uses a real build of the app, on a real device, against the real published catalog, to check a real price or get a real recommendation, and the result matches what's actually on the shelf. This is Part 4's own terminal goal, restated here as a milestone with its own test.

---

## Part 4 — Critical Path

**The question this Part answers is narrower than "launch."** Execution Backlog's own critical path (E1 → E2 → E3 → E6 → E8) is the path to a public Play Store submission — it includes legal clearance, compliance, and closed field validation with recruited outside participants. **None of that is required for a founder to stand in a store with a real build.** This document's critical path is a strict subset of Execution Backlog's, scoped to exactly Part 3's M1–M6.

**The shortest real path:**
Step 0 (pipeline data-integrity resolved) → Step 1+2 (computation + loading layer, parallelizable with each other) → Step 3 (real enrichment, ≥20 beers — the actual long pole) → Step 4 (join + validation) → Step 5 (serialization) → Step 6 (verify build) → Step 7 (publish) → Step 8 (verify app) → M6.

**Explicitly moved off this critical path, with the reason each one is off it:**
- **E1 (Legal & Regulatory Clearance), E4 (Compliance & Store Readiness), E6 (Closed Field Validation), E8 (Launch Execution)** — all Execution Backlog epics, all real, all P0 *for public launch*, none required for a founder's own private, real-data build to exist and work correctly.
- **E5 (Analytics & Crash Reporting)** — Execution Backlog already marks this fully parallelizable with no dependency on anything else; it adds nothing to whether the app works correctly with real data.
- **E7 (the `true_prior_map` pipeline defect fix, as a general-purpose engineering investment)** — Execution Backlog marks this P2, "not optional in the longer term" but explicitly optional for this launch. **Important distinction, not a contradiction:** Step 0 above already requires *understanding and safely handling* this defect before re-running the pipeline once; E7 is the larger, separate question of formally fixing it as reusable infrastructure. The narrow, one-time need is on the critical path; the general fix is not.
- **Comparison, Search/Browse, remaining CLI convenience tools, Generation 1 cleanup** — per Part 2's own closing note; independently confirmed by Execution Backlog's own P3 list.

---

## Part 5 — Dependency Graph

```
Step 0 (pipeline data-integrity resolved)
        │
        ▼
Step 1 (pure computation) ──┐
                             ├──▶ Step 2 (loaders + enrichment/ scaffold)
        (no dependency       │           │
         between 1 and 2 —   │           ▼
         genuinely            │    Step 3 (real enrichment, 20+ beers)
         independent,         │           │            ▲
         build in either      │           │            │
         order or together)   │           │     (Step 3 can start the moment
                               │           │      Step 2's scaffold exists —
                               │           │      does not wait for Step 4/5
                               │           │      to be written)
                               ▼           ▼
                        Step 4 (join + contamination + validation)
                               │
                               ▼
                        Step 5 (serialization: assemble/version/write)
                               │
                               ▼
                        Step 6 (first real build, verified by hand)
                               │
                               ▼
                        Step 7 (commit + publish, zero new code)
                               │
                               ▼
                        Step 8 (verify every screen against real data)
                               │
                               ▼
                              M6
```

**The single real bottleneck:** Step 3. Every engineering step around it (Steps 1, 2, 4, 5) is small, mechanical, and fast — realistically days, not weeks, per Catalog Implementation Backlog's own Part 6 risk assessment. Step 3 is bounded by real human research time, not code, and nothing downstream of it can complete without at least enough real beers enriched to make a build worth running.

**Genuinely independent work, safe to run in parallel with the critical path without slowing it:** Step 0's investigation can happen while Step 1 is being written (different people, different files, no shared state). E5 (analytics/crash reporting). Any of Execution Backlog's E1/E4 compliance drafting. None of this blocks or is blocked by the critical path above.

---

## Part 6 — Risks During Implementation

*Implementation risk only — nothing about product strategy, market fit, or business decisions.*

**Schema drift.** Catalog Contract 1.0 is frozen, and nothing in this roadmap proposes changing it — but the already-confirmed `PackageType`/`container_type` enum mismatch (roughly 30% of real rows normalize to a value the app's closed enum cannot represent) is a live, present-tense version of this risk, not a hypothetical one. Building `schema_validate.py` (Step 4) before enriching at real volume, not after, is what keeps this from silently discarding a third of the real catalog's candidate rows without anyone noticing until a build fails.

**Enrichment inconsistency.** One founder, working across many sessions, applying judgment calls (Style assignment, ABV source selection) that could easily drift in interpretation over weeks. The Catalog Enrichment Playbook's own spot-check discipline (Part 8) exists specifically for this; skipping it because "M1 just needs 20 beers" is exactly how this risk compounds unnoticed.

**Stale catalog.** The moment M3 is reached, `catalog/catalog.json` is a real, live artifact that must be regenerated on a real cadence (Catalog Implementation Architecture Part 6) as KSBCL republishes monthly — treating the first successful build as a one-time event rather than the start of a recurring process is a real risk to data freshness the moment real users (even just the founder) start relying on it.

**Build reproducibility.** `build_catalog.py` must be deterministic — same `pricing_data/` plus same `enrichment/` must always produce byte-identical output (Recommendation Engine Implementation's own determinism requirement, extended here to the build step that feeds it). Any hidden non-determinism (wall-clock timestamps leaking into computed fields, unstable sort order in the assembled arrays) would make Step 6's manual verification worthless for the next build.

**Accidental manual edits to `catalog.json`.** Catalog Contract 1.0 Part 1 is explicit that nobody is allowed to hand-edit this file — it is a build output. The real, live risk is mundane: a quick manual fix under time pressure (e.g., patching one bad SKU by hand instead of fixing its source `enrichment/` file) that gets silently overwritten and un-fixed on the next real build, with no record of why.

**Regression risk from re-running Stages 2–5.** Already named directly in Part 2, Step 0, and repeated here because it is the single most concrete, evidenced risk in this entire roadmap: the `true_prior_map` defect is real, confirmed, and unfixed, and the whiskey-contamination fix cannot be safely applied to real data without either fixing it or explicitly working around it first.

**Treating "specified" as "safe to skip verifying."** Every screen in Part 1's "production-ready" list was verified against a placeholder or small fixtures, never against a real, multi-hundred-SKU, genuinely messy catalog. M4's test exists specifically because "the architecture document says this screen is correct" and "this screen has never actually rendered real data" are not the same claim.

---

## Part 7 — Engineering Principles

*Consolidated from across the canon, not invented here. Every principle below already exists in a frozen document; this is a single reference list, not a new rule.*

- **Generated artifacts are disposable.** `catalog/catalog.json` can be deleted and perfectly reconstructed from `pricing_data/` plus `enrichment/` at any time (Beer Knowledge Base Architecture Part 1). If it can't be, something upstream is wrong, not the artifact itself.
- **Source attribution is never removed, only added to.** Every Curated fact in `enrichment/` carries its own `source_type`/`source_name`/`observed_at`/`observed_by`; a correction is a new commit, not an edit that erases the old value's trail (Beer Knowledge Base Architecture Part 6 — git history is the record).
- **`catalog.json` is never hand-edited.** It is a build output; the only legitimate way to change its content is to edit `enrichment/` and rebuild (Catalog Contract 1.0 Part 1).
- **Builds are deterministic.** Same inputs, same output, every time — no hidden state, no non-reproducible ordering (Recommendation Engine Implementation; extended to the Catalog Builder throughout Catalog Builder Implementation Design).
- **Validation runs before publication, never after.** A SKU that fails a rule is excluded from that build, with a named reason, never silently included and fixed later (Catalog Builder Architecture Part 7; Catalog Contract 1.0 Part 8).
- **Never guess; mark Unknown instead.** A missing ABV or Style is an honest, temporary gap; a guessed one is indistinguishable from a real fact until it's wrong (Catalog Enrichment Playbook Part 1/10 — the single most repeated discipline across every catalog document this session produced).
- **No fact is ever silently promoted between confidence tiers.** Curated never becomes Verified just because it's been correct for a while; only a genuinely different, authoritative source changes a fact's tier (Catalog Builder Architecture Part 1).
- **Confidence is never collapsed into one blended number**, anywhere in the product — restated directly from Project Brain §13's own list of decisions that must not be revisited without new evidence.
- **Two lineages of code exist in `lib/`; only one is real.** Confirmed repeatedly, screen by screen, across this session — always verify a screen is reachable from `app.dart` before trusting anything about it.
- **When implementation depends on an unresolved Product Decision, build the documented safe default, not a guess** — every screen and every catalog document this session produced already does this (D1's provisional-mandatory ABV treatment, D11's no-freshness-signal default, and so on); this roadmap adds no new instance of this principle, only reuses it.

---

## Part 8 — Definition of Done (Version 1 Complete)

**Not launch. Not growth. Not the future roadmap. Only: what must exist before the implementation phase itself can honestly be called complete.**

Version 1 is complete when all of the following are simultaneously true:
- Every module and CLI named in Catalog Builder Implementation Design exists, with its own passing test (that document's own Part 7's Definition of "Version 1 Complete," restated as a component of this larger one).
- `enrichment/` contains real, validated, cited data for at least the SKU volume Execution Backlog's own E2 already commits to (**≥100 SKUs, each with non-null ABV, style, size, container_type, and a dated real price** — E2's exact success criteria, reused here unchanged).
- M1 through M6, as defined in Part 3, have each individually passed their own stated test — not "probably works," a specific human or automated check that actually ran and passed.
- The Step 0 pipeline data-integrity risk has been either fixed or has a documented, safe, repeatable workaround in active use — not merely "known about."
- `catalog/catalog.json`, as committed on `main`, is a real Catalog Builder output, traceable via its build manifest to the exact `pricing_data/` run and `enrichment/` snapshot that produced it.

**Explicitly not required for Version 1 Complete:** Comparison built. Search/Browse specified or built. Every remaining CLI convenience tool (`diff_catalog.py`, `merge_review.py`, etc.) built. Generation 1 dead code removed. Any item from Execution Backlog's E1/E4/E5/E6/E8. Any Product Decisions Register item resolved beyond what already has a documented safe default in use today.

---

## Implementation Blockers

*Genuine gaps that block the path this document defines. Not solved here. Where a Product Decisions Register entry exists, it's cited; where the blocker is a pure engineering defect with no corresponding product ambiguity, that's stated plainly instead of forcing a false connection.*

1. **The `true_prior_map` defect in `canonical_resolve.py`.** Blocks Step 0 directly, and therefore blocks the entire critical path from starting on trustworthy data. **No Product Decisions Register entry exists for this** — it is a data-integrity engineering defect, not an unresolved product ambiguity, and is tracked instead in Project Brain §11, item 3.
2. **The build-manifest file location** (Catalog Builder Implementation Design Part 7's own flagged ambiguity — `catalog/` vs. `pricing_data/runs/YYYY-MM/`). Blocks Step 5 from being fully specified. No Product Decisions Register entry; a small, self-contained implementation choice, not a product decision, but genuinely undecided today.
3. **The `contamination_filter.py` vocabulary-sourcing ambiguity** (Catalog Builder Implementation Design Part 6 — import the KSBCL pipeline's own live vocabulary vs. maintain an independent copy). Blocks Step 4 from being fully specified, though either answer unblocks it; not resolved here.
4. **Product Decisions Register D1 (incomplete-ABV handling).** Does not hard-block this roadmap — Catalog Builder Architecture's provisional-mandatory treatment is already a documented, safe default in active use throughout every relevant document — but is restated here because it directly shapes what M1's "≥20 beers" and Version 1's "≥100 SKUs" can actually contain: any real SKU with a genuinely unresolvable ABV is correctly excluded, not blocked from being decided about later.
5. **Product Decisions Register D19 (no committed decision on the Beer Knowledge Base's real backend/data source).** Worth flagging precisely: the catalog architecture arc this session produced (Catalog Builder Architecture through Beer Knowledge Base Architecture) is, in substance, the practical answer to D19 for the scale this roadmap targets — but the Register itself was never formally updated to reflect that. This does not block this roadmap's own path; it's noted so a future reader doesn't mistake D19 for still being wide open in the way it originally was.
