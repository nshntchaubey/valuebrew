# ValueBrew — Session Summary

*A closeout snapshot, not a permanent architecture document. Written for a human (or AI) reading this repository months from now with no memory of how it got this way. `PROJECT-BRAIN.md` is the durable index; this file is a point-in-time account of one long working session that took ValueBrew from "canonical architecture frozen, no catalog-build step exists" to "the entire path to a real, working, real-data build is specified and sequenced." If this file and `PROJECT-BRAIN.md` ever disagree, trust `PROJECT-BRAIN.md`.*

---

## What was accomplished

Fourteen new documents, covering three layers:

**Consolidation.** `PRODUCT-DECISIONS-REGISTER.md` — every unresolved Product Decision scattered across the entire canon, found, deduplicated (21 from ~30 individually-named items), classified, prioritized, and dependency-mapped. Nothing resolved; everything made visible in one place for the first time.

**Catalog architecture.** `CATALOG-BUILDER-ARCHITECTURE.md` → `CATALOG-IMPLEMENTATION-ARCHITECTURE.md` → `CATALOG-CONTRACT-1.0.md` → `CATALOG-BUILDER-IMPLEMENTATION-DESIGN.md` → `CATALOG-ENRICHMENT-PLAYBOOK.md` → `BEER-KNOWLEDGE-BASE-ARCHITECTURE.md` — a complete specification for the missing piece of the system: how a beer moves from a government price list to a trustworthy, published `catalog.json`, and the human-maintained repository (`enrichment/`) that makes it possible.

**Recommendation and reconciliation.** `RECOMMENDATION-ENGINE-IMPLEMENTATION.md` — a full specification of the existing engine, concluding it needs no change. `ENTERPRISE-RESEARCH-RECONCILIATION.md` — every document in the earlier market-research corpus read in full and reconciled against current canon, five genuine recoveries identified, three contradictions documented and left unresolved.

**Execution.** `CATALOG-IMPLEMENTATION-BACKLOG.md` and `IMPLEMENTATION-ROADMAP.md` — the translation of all of the above into an actual build order, milestones with completion tests, a critical path, and a dependency graph.

---

## Important discoveries

**The Flutter app's catalog-loading infrastructure is already fully built.** `CatalogRepository`, `CatalogLocalCache`, and a working `HttpCatalogRemoteSource` wired to a live jsDelivr CDN mirror of this repo's own `catalog/catalog.json` — confirmed by direct inspection, not assumed. The entire remaining gap is `tool/catalog_builder/` (zero code) and `enrichment/` (does not exist). This was not known or recorded anywhere before this session.

**The Recommendation Engine needs zero changes for real-catalog integration.** It was already written as a pure function over an arbitrary `Catalog`. The Generation 1 code sitting alongside it in the same directory (`RecommendationEngine`, `WeightedScorer`, `SimilarityStrategy`, a "Recommendation Profile" persona system) is real, well-engineered, and has no canonical basis — confirmed unreachable from `app.dart`, recommended for deletion, not migration.

**Two confirmed, live contamination rows exist in the real pipeline output today**, and only one is fixed. `CP0000001` (a Budweiser whiskey, caught by a brand-name false positive) is closed by the whiskey-exclusion-terms fix already sitting in the working tree, uncommitted. `CP0000955` (a Glenfiddich whisky matched via `style_keyword:ipa` at high confidence, because its own product name contains "IPA") is not, and cannot be, fixed the same way — the pipeline's exclusion guard never vetoes a style-keyword match by design. This is exactly why the catalog architecture specifies an independent contamination gate at the build layer, not reliance on Stage 2 alone.

**A newly-discovered defect blocks applying the whiskey fix to real data.** `canonical_resolve.py` has a `true_prior_map` construction bug that can corrupt the canonical identity map on a same-month rerun. The fix exists in code; the data it should clean has not been cleaned, because re-running Stages 4–5 to pick it up is not yet safe. This is Step 0 of the implementation roadmap.

**Two Lexicon violations were found in shipped copy** — a bare "Value score: N" number on both the real Recommendation and Beer Detail screens, both direct violations of the Canonical Interaction Lexicon's oldest rule. Both are documented as small, safe, ready-to-apply fixes, not yet applied.

---

## Architecture decisions made during this session

None. Every document produced this session either consolidates already-made decisions (Product Decisions Register), specifies implementation for already-frozen product behavior (the entire catalog and recommendation arc), or sequences already-specified work (the backlog and roadmap). Nothing in the 20-document Canonical Architecture, the Beer Knowledge Model, the Decision Engine Model, or any Screen Contract was reopened or revised.

---

## Implementation readiness

**Production-ready, unchanged:** KSBCL pipeline (Stages 1–5), Flutter catalog-loading stack, Recommendation Engine, Home/Recommendation/Beer Detail/Price Verification screens.
**Partially complete:** `catalog/catalog.json` (still a 1-SKU placeholder); the whiskey fix (real, uncommitted, unapplied).
**Specified but unbuilt:** `tool/catalog_builder/`, `enrichment/`, the canonical Comparison screen.
**Completely absent:** Search/Browse Results (no Screen Contract exists), every catalog-side validation/CLI tool.

The full build order, six milestones (M1–M6), critical path, dependency graph, and risk register live in `IMPLEMENTATION-ROADMAP.md`. This file does not repeat them.

---

## Known blockers

1. **`true_prior_map` defect** (`canonical_resolve.py`) — no Product Decisions Register entry; a pure engineering defect, blocks Step 0 of the roadmap.
2. **Build-manifest file location** — undecided between `catalog/` and `pricing_data/runs/YYYY-MM/`.
3. **`contamination_filter.py`'s vocabulary source** — undecided whether to import the KSBCL pipeline's live config or maintain an independent copy.
4. **Product Decisions Register D1** (incomplete-ABV handling) — does not hard-block anything; a documented safe default (exclude, don't guess) is already in use throughout.
5. **Product Decisions Register D19** (no committed Beer Knowledge Base data-source decision) — in substance, already answered by this session's own catalog architecture arc; the Register itself was never formally updated to say so.

---

## Next immediate task

Per `IMPLEMENTATION-ROADMAP.md`, Part 2, Step 0: investigate and safely resolve the `true_prior_map` defect (or establish a safe rerun workaround) before touching Stages 2–5 again. Everything else in the roadmap is sequenced behind this.

---

## Addendum — closeout audit, same day

Widening the closeout audit to `tool/`, `test/`, and root files (beyond `docs/`) surfaced two more facts, neither an architecture decision, both worth recording precisely rather than folding in silently:

- `tool/ksbcl_pricing_pipeline/requirements.txt` exists and is tracked, committed since the pipeline's foundational commit — it pins `pdfplumber`, `pytest`, `PyYAML`. This corrects one sentence in `CATALOG-BUILDER-IMPLEMENTATION-DESIGN.md` §0.4, which claimed no such manifest exists anywhere in the repository. The document's actual conclusion is unaffected.
- Exactly 22 test files exercise the confirmed-dead Generation 1 lineage (8 Recommendation-side, 14 across Favorites/Filtering/Sorting/Search/WrongReport/Compare). Any future deletion of Gen1 source code needs to account for deleting these too — not previously sized precisely anywhere in this session's documents.
