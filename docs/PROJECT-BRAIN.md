# ValueBrew — Project Brain

*Canonical knowledge consolidation. Single source of truth for product, architecture, engineering process, and data-pipeline state. Supersedes any prior summary document, including `docs/PROJECT-BRIEFING-FOR-CHATGPT.md` (stale as of 2026-08-07) wherever they conflict.*

---

## 1. What ValueBrew Is

ValueBrew is a decision engine that helps a beer buyer in Karnataka, India choose the best beer for their own budget and preferences — a mobile app that recommends beer by value (cost per unit of alcohol), verifies whether a charged price matches the legal reference price, and compares named candidates. It is not a browse-everything catalog app and not a social/rating app.

**Founding rejections (permanent, PDD-level):**
- No accounts, no login, no cross-session persistence of anything a person states. Every interaction begins fresh. (Session-only Preference Summary, Observed Price — never stored.)
- No numeric "score" or "rating" anywhere. No single blended confidence figure.
- No inferred/learned personalization from behavior — every Constraint must be explicitly stated by the user.
- Does not claim to find "the objectively best beer in existence" — Recommendation is scoped to what it actually searched; Comparison is scoped to only the named candidates handed to it.

**Two philosophically distinct product surfaces exist in this repository, and must not be conflated:**
1. **The ValueBrew mobile app** (Flutter, `lib/`) — the consumer product, governed by the 20-document Canonical Architecture.
2. **The KSBCL pricing pipeline** (`tool/ksbcl_pricing_pipeline/`) — an independent Python data-engineering workstream that ingests Karnataka's official government liquor price list and produces the catalog data the app will eventually consume. It is not sequenced against the app's engineering documentation flow and has its own architecture, product decisions, and governance model.

---

## 2. Product Philosophy & Principles

- **Explainability over speed.** Every Recommendation, Trade-off, and Verification Result carries a mandatory, immediate Explanation — never deferred to a separate request. A wrong recommendation must be a specific, disputable data point, not a reason to distrust the whole system.
- **Confidence honesty over display simplicity.** Confidence is never collapsed into one blended figure. High-confidence (Verified/Computed Fact) and low-confidence (Human Judgment / Soft Preference) content must always remain visibly separated, however inconvenient.
- **Ties are legitimate, complete answers.** Forcing an arbitrary pick when two SKUs are genuinely equal misrepresents what the engine knows. A Tie Disclosure is never a failure state.
- **Never invent behavior at a lower layer.** A gap in the canon is raised against the canon, never silently resolved by an engineer, a specification author, or a data-pipeline stage. This is the single most repeated discipline across both the app and the KSBCL pipeline.
- **Recovery preserves progress.** Restarting from nothing is the exception, not the default, on any failure path.
- **Navigation never reasons.** A transition carries context between screens that reason; it never reasons itself. `ValueBrewNavigator` is the sole class permitted to trigger a screen transition.
- **Segment-appropriate restraint.** Hand-offs between screens (e.g., Beer Detail → Price Verification) are always invitation-only, never automatic — even following a finding that would justify escalation.
- **Confirm, then extend (never build for a hypothetical).** A rule, exception, or vocabulary entry is added only after a real, confirmed instance appears in actual data.
- **Asymmetric risk default: false split beats false merge.** Under genuine uncertainty, the architecture consistently prefers under-action (excluding, not merging, not auto-resolving) because a false negative is cheaply corrected later while a false positive silently corrupts data or trust.
- **Every claim is classified: Evidence / Inference / Hypothesis / Opinion**, and reclassification over time is expected, not a failure (per `COLLABORATION-GOVERNANCE.md`).

---

## 3. Architecture — The Canonical Layer (Product Truth)

`docs/architecture/current/` holds 20 frozen, numbered documents (00–19) that are the single source of product truth — behavior-first, platform-independent. Nothing below this layer may redefine product behavior; a gap found lower down is raised against the canon, never resolved locally.

**Document set (00–19), by role:**
- **00** Architecture Review Guide — process discipline for reviewing canon changes.
- **01–07** Product foundation: Product Definition Document (PDD, has a v1→v2 revision), Behavioral Hypothesis Model, Decision Engine Model, Recommendation Framework, Beer Knowledge Model, User Interaction Model, Feature Inventory.
- **08** Information Architecture — ownership rules; a fact is *referenced* across a screen boundary, never *re-hosted*.
- **09** Experience Flows.
- **10** Content Architecture — Primary/Supporting/Contextual/Progressive/Explanation/Confidence/Recovery/Completion composition categories.
- **11–15** Five Screen Contracts: Home, Recommendation, Beer Detail, Comparison, Price Verification.
- **16** Navigation Contract — the single synthesized source of truth for every transition; supersedes any individual Screen Contract's own restatement.
- **17** Canonical Interaction Lexicon — every term's precise definition, 10 Canonical Distinctions, 9 forbidden synonyms (never "Score"/"Rating"/bare "Best"/loose "Verify"/"Correct price" for "Legal Price"/etc.).
- **18** Canonical Screen Specification Template — the template every Engineering Screen Specification must instantiate by citation only.
- **19** Architectural Decisions Record (ADR) — the *why* behind every boundary; 8+ named decision-making principles, one **Major Architectural Decision left explicitly Open** (see §14).

`docs/architecture/archive/` holds a prior major version (an earlier, richer prototype: full RecommendationEngine/Policy/Scorer/Strategy stack, Favorites, Compare, Filtering, Sorting, Search) superseded by the current 20-document canon per README's own "Versioning" statement. This archived design is directly corroborated by real, unreachable code still sitting in `lib/` (see §6).

**10 Canonical Distinctions worth internalizing:** Recommendation vs. Comparison (search-the-catalog vs. reason-only-about-handed-candidates); Better vs. Recommended (bounded claim vs. catalog-wide claim); Verified vs. Computed (both high-confidence, differ in whether sourced or derived); Recovery vs. Clarification (failure vs. bounded single-question ambiguity); Journey vs. Experience; Experience vs. Screen; Transition vs. Navigation; Explanation vs. Confidence (why vs. how-sure); Fact vs. Preference; Decision vs. Recommendation; Behavior vs. Implementation.

### Key permanent decisions (ADR, all Accepted unless noted)
- Recommendation and Comparison remain separate Experiences sharing one underlying Trade-off/Tie Engine Behavior.
- Beer Detail never recommends; Confirm-as-Is is a Feature of the Recommendation Module surfaced on Beer Detail, not an independent capability.
- Price Verification is isolated and never escalates on its own initiative, even after an overcharge finding.
- Home owns routing and nothing else; never reaches Decision Complete; never a legitimate backward-navigation destination.
- **Open (the only non-Accepted Major Architectural Decision in the entire canon): Search/Browse Results has no Screen Contract.** This leaves two Navigation Contract graph edges (Home→Beer Detail, Home→Comparison) incompletely specified. Flagged explicitly, not resolved.
- Preference Summary is session-only.
- Recommendation alone owns full iterative Progressive Question-Asking; Comparison is capped at exactly one Clarifying Question.
- Confidence is never collapsed into a single figure.
- Observed/Charged Price is transient — never persisted, never displayed outside Price Verification.
- No accounts exist.
- Product mechanisms (search, browse, future scan) are never canonically mandated or excluded — only capabilities require canonical evidence.
- Every screen has a bounded, non-overlapping responsibility (Owns / Does Not Own, stated explicitly per Screen Contract).

### The five canonically-acknowledged open gaps (repeated verbatim across Review Guide §9, ADR §7, and each affected Screen Contract's own §11)
1. Search/Browse Results has no Screen Contract (the single most structurally significant open item).
2. Approximate/imprecise charged-price handling on Price Verification is unresolved.
3. The rule determining Anchor Situation applicability on Beer Detail is unresolved.
4. Ambiguous preference-type statements on Recommendation (e.g., a number that could be budget or size) are unresolved.
5. Comparison logic beyond two candidates is unresolved — the underlying tie-breaker/trade-off machinery is worked out only for exactly two candidates anywhere in canon, and this gap is independently reachable from Recommendation's own Core V1 threshold rule (a genuine tie of 3+ candidates), not only from the Comparison screen.

Deferred (not gaps, by design): a future Accessibility standard and a future Telemetry/analytics framework — both explicitly reserved, unfilled placeholders (Screen Specification Template §11–12) until a dedicated standard exists.

---

## 4. Engineering Layer — From Canon to Flutter (Planned)

`docs/engineering/` is where the frozen canon becomes buildable software. It defines *how*, never *what*. Reading order: Engineering Planning Roadmap → Flutter Implementation Architecture → Implementation Bootstrap Plan → Engineering Screen Specifications → Flutter Implementation.

**Planning phases (Engineering-Planning-Roadmap.md):** Phase 0 (five Resolution Report closure edits) gates everything. Phase 1 (five ADR-level product decisions: 1.1 SBR Contract, 1.2 Anchor rule, 1.3 ambiguous-preference rule, 1.4 imprecise-price rule, 1.5 3+-candidate logic) fans out in parallel. Phase 2 (six Engineering Screen Specifications). MVP readiness was defined by 5 precise, checkable conditions — **this gate was never actually fully closed** (SBR Contract and the Navigation Contract's SBR-dependent edges remain open; decision 1.5 was never formally ADR-recorded) — yet implementation proceeded anyway on a deliberately narrower 4-screen scope. This is a real, acknowledged discrepancy between the stated plan and what shipped, not silently reconciled anywhere in the documentation.

**Engineering Screen Specifications:** All six (Home, Recommendation, Beer Detail, Comparison, Price Verification, Search/Browse Results) were completed and exist under `docs/engineering/specifications/`, each a citation-only restatement of its Screen Contract via the Template — even though Comparison wasn't MVP-required and Search/Browse Results got a Specification *ahead of* ever receiving its own canonical Screen Contract (an explicitly flagged sequencing irregularity, unresolved).

**Known Limitations (per Engineering CHANGELOG v1.0.0), several genuinely unresolved as of the last engineering-doc pass:** occasion input handling; beyond-two-candidate trade-off/tie logic; anchor-situation determination rule; imprecise charged-price handling; candidate-list revalidation on backward navigation from Beer Detail to Search/Browse; the Beer Detail↔Recommendation navigation relationship; Search/Browse Results resolution when Price Verification is entered directly from Home.

**Flutter Implementation Architecture (planned, v0.1):** Pragmatic Clean Architecture (domain/data/presentation per feature), feature-first top folder structure. Riverpod (code-gen flavor) for state management, one sealed-state Notifier per screen. `go_router` wrapped behind a single `ValueBrewNavigator`. `drift`/SQLite for local catalog cache only (never session state). No DI framework beyond Riverpod's own provider graph. Two separate error categories: canonical Recovery States (domain-level, never thrown) vs. technical/infrastructure failures (never mapped onto a Recovery State). Planned 9-milestone Bootstrap sequence (M0–M9), later reordered so Navigation Contract enforcement (M3) moves before any screen work, since Home structurally depends on the navigator to route at all.

---

## 5. Engineering Layer — What Was Actually Built (V1, Frozen)

**`docs/engineering/Version-1-Architecture-Reference.md` is the sole authority on current app behavior** — where the planning docs above (implementation/20-23) describe intended scope and the Engineering Retrospective describes *how* it was built, this document describes *what actually exists*, and wins on any conflict.

### V1 scope
Four screens only: **Home → Recommendation → Beer Detail ⇄ Price Verification.** Search/Browse Results and Comparison were never built into the app (specs exist; screens don't).

```
Home ──homeToRecommendation({isPlanning})──> Recommendation
Recommendation ──recommendationToBeerDetail(skuId)──> Beer Detail
Beer Detail ──beerDetailToPriceVerification(skuId)──> Price Verification
Price Verification ──priceVerificationToBeerDetail(skuId)──> Beer Detail
```
IDs cross navigation boundaries, never computed objects — every screen re-resolves its own data from the one in-scope `Catalog` via `catalog_lookups`, so no screen can ever display a stale fact its origin screen already had fresher.

### What V1 solves
The two highest-confidence Essential capabilities from the PDD — Legal Price Verification and Alcohol-Adjusted Value Comparison — plus simple budget/style preference handling and an honest recommendation output including genuine Tie Disclosure.

### What V1 intentionally excludes, and exactly why (not silently narrowed — each has a stated blocker)
- **Search/Browse Results** — blocked, canon: no Screen Contract exists.
- **Comparison** — blocked, canon (3+-candidate scaling unresolved) *and* repository (depends on Trade-off, itself blocked) *and* would duplicate Recommendation's own tie rendering even if built, violating the anti-duplication rule.
- **Trade-off Explanation** — blocked, repository: requires two simultaneous Strong Preferences; only budget (Hard) + one optional style (Strong) currently exist.
- **Preference expansion** (strength, size, brand) — same missing-second-Strong-Preference blocker.
- **Confirm-as-Is** — blocked, canon + repository: requires an anchor-known entry path (Search/Browse) that doesn't exist.
- **Confidence Communication as a formal cross-cutting system** — deferred, not blocked: every input Recommendation uses today is uniformly high-confidence, so building it now would add zero informational variance.
- **Proxy-Buying Mode** — blocked, canon, *explicitly by product authorship* (PDD names it directly as deferred, unlike every other architectural deferral in this list).
- **Why/Learning Query Handling** — deferred, not blocked: nothing hidden exists yet that would need retrieval.
- **Low-Confidence Response** — blocked, repository: today's two-input surface always resolves to a definite outcome.
- **Accounts/login/cross-session persistence** — permanent, PDD-level rejection.

### Design principles proved out over 9 shipped milestones (M0–M8, then a formal "no M9 exists" conclusion)
1. Screens never compute another screen's logic.
2. IDs cross navigation boundaries, never computed objects.
3. Formatting belongs exclusively in `display_formatting.dart`.
4. Lookups belong exclusively in `catalog_lookups.dart`.
5. Presentation owns only presentation; domain owns business reasoning (zero Flutter imports in `generateRecommendation`/`verifyPrice`).
6. Compiler-enforced evolution over nullable state — `RecommendationOutcome`'s sealed hierarchy gaining a 4th subtype (`RecommendationTie`, Milestone 5) forced every renderer to handle it; this is called "the strongest evidence in the whole project" that the original sealed-type choice was correct.
7. No speculative abstractions — extraction only after a *third* real consumer, never before (repeatedly demonstrated, never violated).
8. Widget-local transient state, not lifted into providers unless proven necessary — this paid off unexpectedly when M8's Price-Verification-round-trip state preservation "worked for free."

### The formal closure: no Milestone 9 exists
The Engineering Retrospective (permanently closed, never updated) concludes independently that every remaining canonical capability traces to a missing, contradictory, or explicitly deferred piece of *canon*, not to unfinished engineering — the repository is "now primarily constrained by product definition, not by engineering." Future V2 work begins **only** on one of four triggers: a new self-documented repository defect, a revised canonical document, a revised/superseded Product Definition Document, or a new Screen Contract authored for a currently-uncontracted capability (Search/Browse Results is the standing example). Absent one of these four, no further architecture discovery, milestone planning, or implementation should be undertaken.

### Repository maturity assessment (as of Retrospective close)
Architectural maturity: **high** (zero pattern changes across 8 milestones). Testing maturity: **strong**, 571 tests as of M8, one known test-basename collision (legacy vs. canonical file) unresolved. Documentation maturity: strong at canon layer, small-and-itemized staleness at engineering layer (addressed in the same pass that produced the Retrospective). Repository maturity: **mixed, honestly so** — the canonical tree is clean; a substantial *unreachable legacy tree still exists alongside it*, catalogued in a dedicated Repository Stewardship Audit but never acted on. This is the single biggest open technical-debt item in the Flutter codebase (see §6).

### The single biggest lesson (verbatim, from the Retrospective's own closing self-assessment)
*"A canon gap is never resolved by inventing an answer at implementation time — it is named and left alone."* Connects Comparison's unresolved 3+-candidate scaling, Confirm-as-Is's undefined trigger, the Home/Price-Verification navigation contradiction, and Style Benchmark's originally-over-specified 4-band design (corrected to 3 bands before shipping).

---

## 6. Repository Structure — Two Code Lineages (Load-Bearing Discrepancy)

Two independent lines of evidence converge on the same finding, and both must be surfaced prominently:

1. **Code-side evidence** (git history, file mtimes, `app.dart` import-reachability): `lib/` contains a substantially richer, already-implemented app — full RecommendationEngine/Policy/Scorer/Strategy stack, Favorites, Compare, Filtering, Sorting, a second Home screen, a second Beer-Detail screen — that predates the "Canonical Architecture rebuild" and is now structurally **unreachable** from `ValueBrewApp` (`lib/app.dart` imports only `features/discovery/presentation/home_screen.dart` and `navigation/value_brew_navigator.dart`). One dangling cross-reference remains (`beer_list_tile.dart` → old `beer_detail/screens/beer_detail_screen.dart`).
2. **Documentation-side evidence** (independent extraction of `docs/architecture/archive/`): the archived `architecture.md` describes exactly this same richer, already-built codebase (with its own internal 467-vs-296-tests contradiction inside that one document), while `docs/architecture/INDEX.md` simultaneously claims "Implementation: Not Started" — an internal documentation contradiction that exists independently of the code question.

**Conclusion (high confidence, triangulated four ways):** this is a real, superseded prior prototype lineage, never deleted, sitting dead in the tree. The Repository Stewardship Audit referenced in the Engineering Retrospective catalogued this but explicitly did not act on it — it remains real, current technical debt.

**Canonical (live) tree today:** `discovery/`, `recommendation/{domain,presentation}`, `beer_detail/{domain,presentation}`, `price_verification/`, `shared/`, `navigation/` — clean and fully accounted for.

**Repository conventions (V1 Architecture Reference §8, active):** `const` used everywhere the constructor allows, for consistency even where no call site benefits. Hand-rolled equality/hashCode/toString on every domain type — no `equatable`/`collection` packages. Private widgets promoted out of their file only once a second real consumer exists (none has yet, anywhere in this codebase). Doc comments explain *why*, not *what*, and are corrected the moment they stop being accurate (caught and fixed multiple times in this repository's own history).

---

## 7. Data Model & Catalog Philosophy (App Side)

- Beer Knowledge Model classifies every fact as **Verified** (sourced directly, never inferred), **Computed** (derived transparently from Verified facts, same high confidence as Verified since deriving isn't guessing), or **Human Judgment** (Soft-preference-driven, low confidence, always visibly separated).
- **Prefer IDs over embedded objects across any boundary** — a navigation boundary or a persisted-file boundary — unless the object is a domain function's own internal return value never crossing such a boundary (e.g., `generateRecommendation`'s `RecommendationResult` legitimately embeds full `Sku`/`Beer` objects because it's not a navigation edge). This is a project-wide coding principle (CLAUDE.md) independently re-derived and demonstrated inside the KSBCL pipeline's own architecture documents.
- The app's data model requires **non-nullable ABV and style for every catalog entry** — but KSBCL's official pricing data carries neither. The `docs/research/enterprise_catalog_research/` corpus (§9 below) is the only current source for this data and is a **required blocker for a real catalog, not a "phase 2" nice-to-have** — this was still unresolved as of the last known snapshot (2026-08-07 briefing) and remains unresolved per the freshest market-research documents read in this session.
- Style Benchmark (relative value standing vs. a style's typical price) ships in V1 as a 3-way `StyleStanding` split (`betterThanTypical`/`typical`/`worseThanTypical`) computed off `Benchmark.p50` alone — deliberately the smallest classification the canon actually specifies. An earlier 4-band `p25`/`p50`/`p75` design was drafted and rejected before implementation once checked against the canon and found uncited; `p25`/`p75` remain unused, reserved for a future milestone that actually needs them.

---

## 8. KSBCL Pricing Pipeline (Independent Data-Engineering Workstream)

An entirely separate Python pipeline (`tool/ksbcl_pricing_pipeline/`) that ingests Karnataka's official monthly liquor price-list PDF and resolves it into a stable, queryable catalog. Real production output lives in `pricing_data/` (git-ignored). Five stages:

| Stage | Purpose | Status |
|---|---|---|
| 1 — Extraction | Raw PDF → `structured_rows.csv` | Frozen, implemented, tested |
| 2 — Beer Identification | Beer/not-beer classification, persistent known-terms ledger + review queue | Frozen, implemented, tested |
| 3 — Normalization | Name folding, pack-size/container extraction | Frozen, implemented, tested |
| 4 — Canonical Identity Resolution | Stable `canonical_product_id` per real-world SKU | Architecture frozen (revised 3×); **implemented** (per git history, though the extracted architecture docs' own "not yet implemented" status line is stale relative to that) |
| 5 — Master + History construction | `beer_master.csv`/`beer_master_duty_free.csv`, `beer_price_history.csv` | Architecture drafted, reviewed once, not fully frozen; **implemented** per git history |

Real validation: run against the actual June 2026 KSBCL price list (1,714 included beer rows; 182 tests as of the Stage 1–3 snapshot).

### The identity-model decision chain (Stage 4) — fully resolved, permanently authoritative
A five-document product-design phase (Product-Discussion → Settlement → Charter → User-Mental-Model → Identity-Decision) settled two Product Decisions, both recorded 2026-08-06 by the Product Owner, both now permanent unless new evidence reopens them:

- **Decision 1 (Exclude):** `canonical_product_id` = retail SKU identity = `(normalized_name_key, pack_size_ml, container_type)`. `supplier_code` is explicitly **excluded** from canonical identity — it's a listing-level attribute, not a product-identity component. Rationale distilled to one generative test: *"is this the smallest unit for which a price comparison is fair and meaningful?"* Volume and container pass that test; case size (`pack_count`) fails it categorically; supplier depended on an unconfirmed factual premise (contract-brewing practice) the documents had no authority to settle — so it was a genuine product-owner call, not derivable from data alone.
- **Decision 2 (Preserve ambiguity, Option F):** when a not-yet-mapped item_code's key matches more than one existing live canonical product, Stage 4 does **not** auto-resolve — it creates a new canonical product and flags every candidate for manual review (`canonical_resolution_review.csv`, reason `ambiguous_key_multiple_candidates`). Chosen because an automatic tie-break fails silently (an invisible correctness error), while deferring to review fails visibly (a noticeable, fixable completeness gap) — the same false-merge-worse-than-false-split asymmetry governing every other identity decision in this pipeline.

`pack_count` **remains** in the matching key today, unlike `supplier_code` — two product-design documents argued for excluding it on principle, but that argument was never formally elevated to a product-owner decision, and Stage 4's architecture explicitly declines to act on it unilaterally (flagged as an open freeze-review item).

### Real-data validation of the matching key (2026-06 run)
1,714 rows collapse to 1,122 distinct groups. "Kingfisher Strong Premium Beer 650ml" alone splits into two genuinely different groups (case-labeled ×12-bottle listings vs. unlabeled listings) spanning ten suppliers at ₹80–190 — confirmed the correct outcome under the four-component key, not a defect.

### KSBCL Repository Governance — 11 conventions extracted from repeated practice (not new policy)
1. Master's terse field sketches are meant to be hardened by the stage that implements them, not re-litigated.
2. Explicit prior text (master's or an earlier recorded decision's) is never silently overridden; an authorized departure is scoped exactly to what authorized it, never further.
3. **Architecture vs. Product Decision boundary:** architecture resolves what's derivable from something already stated and doesn't change what the product promises; a Product Decision is required when the disagreement is about values or risk tolerance, not facts.
4. Confirm, then extend — never build for an unconfirmed hypothetical.
5. Under genuine uncertainty, default favors under-action (exclusion, non-merging) over over-action.
6. Never invent a fact the source doesn't state — leave null/unknown rather than guess. (One confirmed historical exception, since corrected: `item_status` was originally derived from a downstream, filtered signal rather than the direct source signal — fixed via the "Fix item_status source" commit.)
7. Every stage produces an audit artifact for every rejected/excluded/flagged row — nothing silently dropped.
8. Correctness means determinism, explainability, and non-regression — never a fabricated accuracy percentage against a target nobody could verify.
9. **A stage may freeze with a genuine question still open**, provided the frozen text gives that question one explicit, deterministic, fully-implementable default today.
10. Review history — including reversed mistakes — is disclosed, not erased.
11. Every rule is grounded in real, confirmed data; hypothetical examples are always labeled as such.

### Stage 5 design decisions worth preserving
- Representative item_code selection is **per (canonical_product_id, channel) pair**, never per canonical product alone — newest `effective_date` wins, lowest `ksbcl_item_code` breaks ties.
- Channel (standard-retail vs. duty-free) bucketing must be **recomputed every run** from each currently-LIVE item_code's own current `is_duty_free` value — a first draft got this wrong (treated channel as frozen/permanent) and was corrected by adversarial review before shipping.
- Delisting freeze behavior (confirmed Product Decision, 2026-08-07): when a (canonical_product_id, channel) pair has zero currently-live item_codes, its `beer_master.csv` row is **frozen at last-known values**, never blanked — staleness is gated entirely through `status`/`delisted_run_month`, consistent with the project's standing "never erase a real fact" convention.
- `beer_price_history.csv`'s rerun-safety mechanism is **deliberately different** from Stage 4's `item_code_canonical_map.csv` mechanism, and this distinction matters: Stage 4 is a current-state table (needs a "forget this run_month's own entries" exclusion rule to force safe recomputation on rerun); Stage 5's history ledger is append-only (comparing unconditionally against its own last row is what makes it idempotent — copying Stage 4's exclusion pattern here would have produced duplicate history rows on rerun; caught and corrected before implementation).

---

## 9. Karnataka Beer Market Research (Catalog Content Sourcing)

A large (~18-file) market-research corpus assessing where real Karnataka beer catalog data (ABV, style, GTIN, retail MRP) can actually come from, separate from the KSBCL pipeline itself.

**Key confirmed facts (evidence-tier):**
- The extracted 216-SKU sample catalog is **not** 216 authoritative SKUs — roughly ~100 have a real observed Karnataka retail price; the rest are brand-metadata-only rows. Effective unique count after dedup is closer to 180–190.
- Realistic addressable universe: **400–600 SKUs**, not 1,000 — the original 500–1,000 target requires either scope redefinition (including discontinued/seasonal SKUs, non-alcoholic line extensions) or is simply not achievable by counting currently-sold Karnataka packaged beer.
- **No public authoritative GTIN lookup exists for India.** GS1 India's own service is a manual/email bulk process, not a documented API. No brewery's official site publishes barcodes. Open Food Facts has real GTINs for only a small fraction of SKUs — treat GTIN as an optional, nullable enrichment field, never a join key.
- **ABV is a structural gap, not a scraping problem.** Almost no retailer or brand site publishes ABV consistently. It's legally required on Indian labels, so the fastest real path is **physical label photography/OCR at point of sale**, not more web research.
- **DGCI&S cannot legally supply identity-level import/export data** for private use (confirmed by their own published policy) — any import-brand-tracking feature must be scoped to aggregate volume/trend data only, or gated on independent legal review of Volza / Section 135AA exposure before building anything on identity-linked shipment data.
- Karnataka Excise Department's own site (`excise.karnataka.gov.in`) was unreachable during this research (DNS failure) — genuinely unresolved whether that's transient or the site is down/nonexistent; worth re-attempting from a different network before concluding no equivalent to Kerala's public BEVCO price list exists.
- Roughly half of evaluated third-party retail sources are non-functional, stale, or partially broken today (Living Liquidz 503s, Bira91's own official domain unreachable, Zauba stale since 2013/2016, Beerbasket's product API 500s, Tonique stale since April 2023 with a leftover "coming soon" placeholder next to live-looking prices). Madhuloka is currently the strongest single retail source but represents a real concentration/single-point-of-failure risk.
- A recurring, real "same-source self-contradiction" example: Mount Everest Breweries' own STOK page states 7% ABV in its spec table and 8% in its own FAQ, unresolved as of this research. The correct system behavior (already reflected in the proposed schema design) is to **surface both values with a conflict flag**, never silently pick a winner.
- Arbor Brewing's own site states its packaged retail is "Retailing only across Goa" despite a Bengaluru taproom — the canonical illustration, repeated across nearly every research document, of why taproom presence must never be conflated with confirmed retail availability.

**Recommended search-engine design (proposed, not built — no backend exists yet under V1's "local JSON catalogue" architecture):** Postgres as system of record with a 5-table schema (`brewery`/`brand`/`beer`/`sku`/`retailer_listing`/`alias`), an explicit entity-resolution step before any indexing (fuzzy-match + human-review queue, never silent auto-merge of retailer listings into one product), and OpenSearch (edge-ngram + phonetic + fuzzy) as the query layer once traffic justifies it — with an explicit, cheaper Postgres-`pg_trgm` day-1 shortcut recommended for the current ~216-row scale. This entire research corpus describes a **future backend system that does not exist in the current V1 codebase**; the most directly actionable artifact today is the 216-SKU JSON file as a seed for V1's stated "local JSON catalogue" architecture — everything else here is forward-looking design for a later milestone, not something to build under CLAUDE.md's "one task at a time" / "do not implement future milestones" discipline.

**Founder-level priority order for closing the real catalog gap:** (1) re-trace and scale whatever KSBCL page/PDF produced the 18 confirmed KSBCL rows — highest ROI, could add 100–300 SKUs of official-MRP data; (2) ABV + calories via label photography — no scraping path exists; (3) KSBCL-supplier-code cross-walk to fill blank brewery/style fields on retailer-sourced rows — a join against data already in hand; (4) start a GS1 DataKart commercial-access conversation now, since negotiation takes calendar time; (5) legal review of Section 135AA before any import-brand-detection feature.

---

## 10. Engineering & Review Discipline (Cross-Workstream)

Both the Flutter app's Engineering Retrospective and the KSBCL pipeline's Repository Governance independently converge on nearly identical practices, despite being separate workstreams with no stated cross-reference — treat this convergence as a real, load-bearing project-wide standard, not a coincidence:

- **Never invent a trigger rule, threshold, or classification the canon/master doesn't specify** — cite the smallest thing actually written down.
- **Never trust a stated claim about repository state without checking it directly** (`git status`, direct file read) — demonstrated repeatedly catching false "already committed" claims.
- **Never let an implementation summary substitute for reading the actual diff during review.**
- **Independent, zero-context adversarial review is what actually finds defects** — the original author re-reading their own draft consistently does not.
- **Checking a rule against a specific, named, real data row** (not a hypothetical) is what actually catches bugs — demonstrated repeatedly on both sides of the repo.
- **A correction applied in one place must be checked against every other document/file describing the same thing** — failing to do this was named "the single largest source of extra review cycles" in the KSBCL pipeline's own history, and the same class of defect (stale doc comments describing shipped behavior as unbuilt) recurred six separate times in the Flutter app's history.
- **When to stop reviewing:** once a fresh, independently-derived pass — not a checklist re-run — turns up nothing new. Not before.
- **A process that always finds something to build is indistinguishable from one that manufactures work** — "no further milestone/decision exists" is proof of health, not failure, when it recurs consistently across independent re-derivations.

---

## 11. Current Known Defects & Technical Debt

1. **Unreachable legacy Flutter code lineage in `lib/`** (§6) — catalogued by a Repository Stewardship Audit, never removed. Real, acknowledged, unresolved.
2. **One test-basename collision** between a legacy and canonical test file (per Retrospective, unresolved as of its close).
3. **Item-code canonical-identity permanence defect in `canonical_resolve.py`** (`true_prior_map` construction, roughly lines 104–122): on a same-month rerun, the true-prior-map exclusion logic can swallow the entire canonical map, causing an item's row to be lost and its `canonical_product_id` reused for an unrelated product. Discovered live during this session's Whiskey-fix propagation work. **Not documented anywhere in the KSBCL architecture docs** — those describe the intended design (including the correct, already-implemented Stage 4 "persist matching-key fields directly on the map" fix for a *different*, already-resolved defect — the delisted-item-code-reappearance gap, closed via `backfill_canonical_map_key_2026_08.py`, a one-time migration script with its own passing test suite). The `true_prior_map` defect is a distinct, newer finding, currently real and unfixed. A Recovery Plan (V5) was executed live in this session to restore the real production data corrupted by triggering this defect (evidence preserved under `pricing_data/incident-evidence/2026-08-12-stage4-whiskey-rerun/`); Stage 4 and Stage 5 were deliberately **not re-run** as part of that recovery, and the architectural fix for `true_prior_map` itself remains deferred to future engineering work.
4. **Whiskey misclassification fix** (item_code `1390101301`, "Budweiser Magnum Double Barrel Blended American Whiskey") — **fixed and committed** (`07982a2`, "Fix whiskey misclassification exclusion-term gap", corrected at the RC1 checkpoint from this document's prior "uncommitted" claim): `whiskey` added to `exclusion_terms` in `beer_classification.yaml`, regression test rewritten in `test_classify.py`. The plural "Whiskies" form was deliberately *not* added — no confirmed misclassification exists for it yet, per the confirm-then-extend discipline. The stale `PROJECT-BRIEFING-FOR-CHATGPT.md` (dated 2026-08-07) still describes this as unfixed; that briefing is now superseded by this document on this point.
5. **Beer Detail ⇄ Recommendation navigation inconsistency** between two frozen canonical documents — flagged in both the Beer Detail Engineering Specification and the Flutter Implementation Architecture's own Implementation Risks; formally unresolved, explicitly not built around (the navigator omits this edge entirely pending formal architecture review).
6. **Search/Browse Results Engineering Specification exists without its own canonical Screen Contract** — an irregularity that mirrors exactly the situation that triggered the Price Verification Repository Synchronization Patch, but no equivalent patch was ever produced for it.
7. **Minor cross-document count inconsistencies** in the KSBCL market-research corpus (KSBCL-sourced SKU counts reported as 13, 17, and 18 in different documents) and in `docs/architecture/archive/architecture.md` itself (467-tests-header vs. 296-tests-body internal contradiction) — low-stakes, worth a note if anyone audits exact figures, not worth chasing further.

---

## 12. Open Questions (Requiring New Evidence or a Product Decision Before Proceeding)

- Whether `pack_count` should be excluded from Stage 4's canonical-identity matching key (argued for on principle by two product-design documents, never formally decided).
- Whether NULL/`unknown` matching-key components (`pack_count`, `container_type`) should participate in Stage 4's automatic exact-match attachment, or be excluded in favor of a stronger false-split bias.
- Whether Stage 4's `canonical_resolution_review.csv` needs cross-run tracking/acknowledgment for an unactioned flag.
- Whether a human-confirmed canonical-identity repoint needs explicit audit fields (who/when/prior value) beyond what `match_confidence`/`matched_rule` currently show.
- Whether a canonical-to-canonical merge mechanism (consolidating two already-separately-created canonical products) is ever needed — deliberately deferred; only a "reserve the retired-ID redirect seam, don't build the feature" recommendation exists, never formally ratified.
- Which of the app's five canonically-acknowledged gaps (§3) gets resolved first, and by whom — none currently has an assigned owner or target date.
- Whether `excise.karnataka.gov.in`'s unreachability during market research was transient or the site is genuinely down/nonexistent.
- Whether the Karnataka contract-brewing practice assumption underlying Stage 4 Identity Decision 1 is actually true (unconfirmed business premise, explicitly named as such).
- Whether the 2.4× price spread observed across suppliers of "the same" KSBCL-listed beer is a meaningful price-comparison signal or evidence the listings aren't truly identical — explicitly unresolved even after the identity-grouping question itself was settled.

---

## 13. Decisions That Must Not Be Revisited Without New Evidence

- No accounts, ever, in the current architecture (PDD-level; only a future, explicit revision of the PDD itself could reopen this).
- `supplier_code` excluded from KSBCL canonical product identity (formally recorded product-owner decision, 2026-08-06).
- Multi-candidate canonical-identity ambiguity is preserved, never auto-resolved (formally recorded product-owner decision, 2026-08-06).
- Stage 5's delisted-channel freeze-at-last-known-values behavior (formally recorded product-owner decision, 2026-08-07).
- The four canonical Screen Contracts' Owns/Does-Not-Own boundaries (Home routes only; Beer Detail never recommends; Price Verification never escalates on its own; Comparison never searches the catalog).
- Confidence is never collapsed into a single blended figure, anywhere in the product.
- The nine forbidden Lexicon synonyms.

---

## 14. Historical / Superseded (For Context Only — Not Governing)

- The archived pre-canon prototype architecture (`docs/architecture/archive/`) — superseded by the current 20-document canon; its code remains physically present but unreachable in `lib/` (§6).
- Pre-canon release artifacts (an old `CHANGELOG.md`/`README.md`/`privacy_policy.md` describing a browse/filter/favorites app) — discovered mid-session during release prep, resolved by asking rather than guessing, and rewritten to describe only the canonical rebuild.
- Stage 4's first architecture draft, which removed the same-supplier price/date review gate unconditionally instead of scoping it only to the newly-possible cross-supplier configuration — corrected via review before freeze.
- Stage 5's first draft, which treated channel bucketing as frozen/permanent and copied Stage 4's rerun-safety exclusion pattern verbatim into an append-only ledger where it would have caused duplicate history rows — both corrected via review before implementation.
- The original four-band Style Benchmark design (`p25`/`p50`/`p75`) — considered, found uncited against the canon, replaced with the shipped 3-way `p50`-only split before implementation.
- `item_status`'s original derivation from a downstream, filtered signal (`normalized_rows.csv` presence) rather than the direct source signal (`structured_rows.csv` presence) — a confirmed real defect, since fixed (git: "Fix item_status source and propagate the correction across KSBCL docs").
- The stale `docs/PROJECT-BRIEFING-FOR-CHATGPT.md` (2026-08-07) — superseded by this document wherever the two disagree, specifically on the Whiskey-fix status (now fixed, uncommitted) and the existence of the `true_prior_map` defect (newly discovered, not in that briefing at all). **Addendum, later the same day:** the repository's own `.gitignore` was subsequently amended (uncommitted, as of this addendum) to explicitly exclude that file from version control, with the comment "One-off status export for sharing outside this repo — not engineering documentation, deliberately not source-controlled." This is a second, independent, later confirmation that the file is retired, not merely superseded — see §16 below.

---

## 15. Catalog & Recommendation Architecture (Produced After §1–14, Same Overall Effort)

*Everything in this section was written after the consolidation above and is additive to it — nothing in §1–14 is superseded by anything here except where explicitly noted. Fourteen new documents now exist under `docs/`, moving the project from "canonical architecture frozen, no catalog-build step exists" to "the catalog-build step, the Beer Knowledge Base, and the Recommendation Engine are all fully specified, and the implementation sequence to build them is written down."*

**The document set, in the order they were produced, each building on the last:**
`PRODUCT-DECISIONS-REGISTER.md` (a consolidated, deduplicated register of every unresolved Product Decision found across the entire canon, classified by category, priority, and dependency — not a new architecture document, a discovery-and-consolidation exercise) → `CATALOG-BUILDER-ARCHITECTURE.md` → `CATALOG-IMPLEMENTATION-ARCHITECTURE.md` → `CATALOG-CONTRACT-1.0.md` → `CATALOG-BUILDER-IMPLEMENTATION-DESIGN.md` → `CATALOG-ENRICHMENT-PLAYBOOK.md` → `RECOMMENDATION-ENGINE-IMPLEMENTATION.md` → `BEER-KNOWLEDGE-BASE-ARCHITECTURE.md` → `CATALOG-IMPLEMENTATION-BACKLOG.md` → `ENTERPRISE-RESEARCH-RECONCILIATION.md` → `IMPLEMENTATION-ROADMAP.md`. (Four further documents — `BEER-KNOWLEDGE-MODEL-2.0.md`, `DOMAIN-MODEL-1.0.md`, `CATALOG-SPECIFICATION-1.0.md`, `BEER-ENTITY-SPECIFICATION-1.0.md`, plus `DECISION-ENGINE-2.0.md`, `INTERACTION-MODEL-2.0.md`, `CONVERSATION-MODEL-1.0.md`, and the four Experience Specifications — `RECOMMENDATION-EXPERIENCE-SPECIFICATION.md`, `RECOMMENDATION-WIDGET-SPECIFICATION.md`, `BEER-DETAIL-EXPERIENCE-SPECIFICATION.md`, `PRICE-VERIFICATION-EXPERIENCE-SPECIFICATION.md`, `COMPARISON-EXPERIENCE-SPECIFICATION.md` — plus `ARCHITECTURE-RECONCILIATION-REPORT.md`, preceded this arc and are treated as already-frozen inputs to it, not part of it.)

**The single most consequential finding in this whole arc, worth stating at Project Brain altitude:** the Flutter app's own catalog-loading and remote-update infrastructure (`CatalogRepository`, `CatalogLocalCache`, `HttpCatalogRemoteSource`, wired to a live jsDelivr CDN mirror of this repo's own `catalog/catalog.json` in `catalog_provider.dart`) is **already fully built and production-wired** — confirmed by direct inspection, more than once, across this arc. This was not previously recorded anywhere in §1–14. The gap recorded here as "entirely open" has since been closed: `tool/catalog_builder/` is fully implemented and tested (320 Python tests), `enrichment/` exists and holds 65 curated beer families, and the RC1 production catalog has been generated from them — see §16, which is the authoritative current-state record superseding this paragraph's original claim.

**Second major finding: the Recommendation Engine (`lib/features/recommendation/domain/`) needs no change for catalog integration.** It is already a pure function over an arbitrary `Catalog`, with no hardcoded assumption about size or content. The Generation 1 lineage sitting alongside it (`models/`, `policy/`, `scoring/`, `services/`, `providers/recommendation_providers.dart`, `widgets/recommendation_profile_bottom_sheet.dart`) is real, well-engineered code for a product surface — ranked "Similar beers"/"Better value" lists, a persona-switching "Recommendation Profile" — with no canonical basis anywhere in the current architecture, confirmed unreachable from `app.dart`. It should be deleted, not migrated; its score-and-explain-together *pattern* is worth recovering conceptually only if a second ranking dimension is ever specified, per a real Product Decision — not today.

**Third finding, extending §11 item 4 without rewriting it:** the whiskey-classification fix in the working tree closes only one of the two confirmed live contamination vectors (`CP0000001`, a brand-name false positive). The second confirmed row (`CP0000955`, "Glenfiddich Experimental Series #01... IPA Experiment," matched via `style_keyword:ipa` at *high* confidence) is not, and structurally cannot be, fixed by adding exclusion terms — the pipeline's own exclusion guard is designed to never veto a style-keyword match. This is exactly why `CATALOG-BUILDER-ARCHITECTURE.md` and every document downstream of it specify an *independent* contamination gate at the catalog-build layer, not reliance on Stage 2 alone. The two findings corroborate each other rather than conflicting.

**Fourth finding: two Lexicon violations were found in shipped, real copy** — a bare "Value score: N" number on both the real Recommendation screen's winning-outcome explanation and the real Beer Detail screen's value line — both direct violations of the Canonical Interaction Lexicon's oldest, most repeated rule (§17, "never Score/Rating"). Both are documented as small, safe, ready-to-apply copy fixes (`RECOMMENDATION-WIDGET-SPECIFICATION.md`, `BEER-DETAIL-EXPERIENCE-SPECIFICATION.md`), not yet applied to the code.

**Fifth finding: the Comparison screen has zero real implementation.** `lib/features/compare/` exists but is confirmed, again, unreachable from `app.dart` — Generation 1 dead code, not a partial build of the canonical thing `COMPARISON-EXPERIENCE-SPECIFICATION.md` describes. Consistent with §5's own "V1 scope: four screens only" finding; not a new discrepancy, a continued one.

**The Product Decisions Register's own headline numbers:** 21 decisions, after aggressive deduplication of roughly 30 individually-named open items scattered across the whole canon. Three are P0 (launch blockers): no committed decision on the Beer Knowledge Base's real data source; app-store alcohol-content compliance, untracked; incomplete-ABV ranking behavior. One genuine cross-document contradiction is recorded rather than resolved: Information Architecture and the Navigation Contract disagree about whether a Beer Detail → Recommendation edge should exist — confirmed still live in `ValueBrewNavigator`'s actual missing method.

---

## 16. Implementation Readiness (`IMPLEMENTATION-ROADMAP.md`, the Terminal Document of This Arc)

**Updated at RC1 checkpoint (2026-08-14) — this paragraph is now the authoritative current-state record for the catalog-builder arc, superseding §15's original claim above and the stale split that used to appear here:**

- **Production-ready:** the KSBCL pipeline, the Flutter catalog-loading stack, the Recommendation Engine, the Home/Recommendation/Beer Detail/Price Verification screens, **and, as of this checkpoint, `tool/catalog_builder/`** — implemented and tested (320 Python tests, `flutter analyze` clean, 585 Flutter tests), including a full CLI surface (`create_beer.py`, `update_beer.py`, `validate_beer.py`, `generate_enrichment_candidates.py`, `build_catalog.py`, and others) that did not exist when this document was last written.
- **Real, generated, and verified against the live app:** the Beer Knowledge Base under `enrichment/` — at the RC1 checkpoint, 65 curated beer families (`enrichment/beers/*.yaml`), grouping 346 SKUs (`canonical_product_id`s) in total. Of those, **57 SKUs across 8 beers currently pass full validation and appear in the generated production catalog** (`catalog/catalog.json`, `catalog_version: 2`, built via `build_catalog.py --write`, manifest at `catalog/catalog_build_manifest.json`). `catalog/catalog.json` is **no longer the 1-SKU placeholder** this document previously described — that placeholder has been overwritten with real build output, spot-verified byte-for-byte against what the live Flutter app actually serves. The remaining 289 grouped-but-not-yet-published SKUs, and the further 1,004 raw candidate rows under `enrichment/candidates/` still awaiting curation, are blocked by evidence/identity/container-type gaps in the underlying data — not by any tooling defect. **[RC2 status note, 2026-08-14]: these grouping figures are now superseded — see the fourth addendum below for the current, final state (278 beer entities, 915 grouped SKUs). The 57-SKU/8-beer publishable figure is unchanged.**
- **Still specified but unbuilt:** the canonical Comparison screen.
- **Still completely absent:** Search/Browse Results (no Screen Contract exists at all, not merely unbuilt).
- **Corrects §11 item 4 and this section's own prior text:** the whiskey misclassification fix is **committed** (`07982a2`, "Fix whiskey misclassification exclusion-term gap"), not uncommitted as previously recorded here. Whether it has been applied to a fresh Stages 2–5 KSBCL rerun is a separate, KSBCL-pipeline-side question this catalog-builder checkpoint did not re-verify — treat that specific sub-claim as unconfirmed rather than restating the old "not yet applied" text as still true.

**The `true_prior_map` defect note below is unchanged by this checkpoint** — it belongs to the KSBCL pipeline workstream, not the catalog-builder arc this session covered, and was out of scope for RC1 verification:

**The one genuine implementation blocker on the critical path, restated here since it directly extends §11 item 3 without rewriting it:** the `true_prior_map` defect must be understood and either fixed or safely worked around *before* Stages 2–5 can be safely re-run to apply the whiskey fix to real data — this is Step 0 of the build order, ahead of every other engineering step.

**Milestones defined (each with its own completion test, not repeated here):** M1 Beer Knowledge Base exists → M2 Catalog Builder produces a valid `catalog.json` → M3 real catalog loads in the app → M4 every existing screen renders real data correctly → M5 Recommendation produces a correct, sensible answer against real data → M6 a founder validates it in a real store. **As of this RC1 checkpoint, M1–M5 are confirmed complete** — verified directly this session: the real catalog builds and validates (M1–M2), loads in the running Flutter app (M3), the Recommendation → Beer Detail flow renders real catalog data correctly with no console errors (M4), and produces sensible, correctly-sourced recommendations against the real 57-SKU/8-beer data (M5). **M6 (a founder validates it in a real store) has not happened** — it is a real-world action outside the scope of any engineering or release-checkpoint session. The critical path to M6 is explicitly narrower than Execution Backlog's own public-launch critical path (§ not previously cross-referenced in this document) — legal clearance, compliance, and closed field validation are all real and all still required for launch, just not for M6.

**`docs/PROJECT-BRIEFING-FOR-CHATGPT.md`'s status is now fully settled, not merely "stale":** the repository's own `.gitignore` (amended the same day as this addendum, uncommitted at time of writing) explicitly excludes it from version control going forward, on the stated grounds that it was a one-off external status export, never intended as ongoing engineering documentation. This document (`PROJECT-BRAIN.md`) is the sole, permanent master index; that briefing should be treated as retired, not updated.

---

*Addendum note: §15–16 above extend this document to cover the full catalog-and-recommendation implementation architecture arc produced after the original 2026-08-12 consolidation. Nothing in §1–14 was rewritten to produce this addendum — only appended to, per the same discipline the original document already states for itself (a conflict is noted, never silently resolved).*

**Second addendum, from a closeout repository audit the same day:** two further facts, discovered by widening the audit to `tool/`, `test/`, and root files, neither reflected above. First: `tool/ksbcl_pricing_pipeline/requirements.txt` exists and is tracked (since commit `d5a1e71`), pinning `pdfplumber`, `pytest`, and `PyYAML` — this corrects `CATALOG-BUILDER-IMPLEMENTATION-DESIGN.md` §0.4's claim that no dependency manifest exists anywhere in the repository; that document's actual conclusion (PyYAML needs no new dependency risk) still holds, only its stated reasoning was wrong. Second: precisely 22 real, presumably-passing test files exercise the confirmed-dead Generation 1 lineage (8 for `RecommendationEngine`/`WeightedScorer`/`SimilarityStrategy`/`RecommendationPolicy`/`RecommendationProfile`, 14 more across Favorites/Filtering/Sorting/Search/WrongReport/Compare) — deleting that source code, as multiple documents in §15 recommend, requires deleting these 22 files too, not previously sized precisely anywhere.

**Third addendum, RC1 release checkpoint (2026-08-14):** the catalog-builder arc described as an open gap throughout §15–16 above is now closed. `tool/catalog_builder/` is implemented and tested; `enrichment/` holds 65 curated beer families grouping 346 SKUs; the production catalog has been generated (`catalog/catalog.json`, `catalog_version: 2`, 8 beers, 57 publication-ready SKUs, manifest at `catalog/catalog_build_manifest.json`) and verified — both structurally against the enrichment repository and live, against the running Flutter app. §15's "concentrated in exactly two places" claim and §16's original four-way readiness split are corrected in place above rather than left standing; see those sections for the full current state. This addendum also corrects one unrelated standing error caught during the same pass: the whiskey misclassification fix (§11 item 4) was recorded as "uncommitted" but has in fact been committed (`07982a2`) since this document's prior revision. The `true_prior_map` defect (§11 item 3) and the KSBCL-pipeline-side question of whether the whiskey fix has been applied to a fresh Stages 2–5 rerun were both out of scope for this checkpoint and remain exactly as previously recorded.

**Fourth addendum, RC2 checkpoint (2026-08-14):** across the RC2.1–RC2.4 sessions, the Beer Knowledge Base grew from 65 to **278 beer entities**, grouping **915 of 1002 admitted SKUs (91.3%)** — up from 346 (34.5%) at the RC1 checkpoint. The **57-SKU/8-beer publishable figure is unchanged**, since RC2 was explicitly scoped to identity/grouping work, not ABV/calorie evidence gathering (RC2.1 established that manufacturer-tier remote evidence for ABV/calories is exhausted for nearly all remaining brands; that finding stands unchanged). RC2.4 produced a Final Exception Register cataloguing every one of the 51 remaining ordinary-backlog SKUs individually, each tagged with why it can't be grouped under the current evidence policy and whether manual (physical-label) observation would resolve it (yes, for all of them, but at low per-item value — 1–4 SKUs each). Three categories of SKU are explicitly out of the Beer Knowledge Base's scope by founder decision, not backlog: Hill Station Hard Cider (16 SKUs), Grizly Hard Seltzer (17 SKUs), and Kingfisher Bohemia (3 SKUs, wine-varietal-named products) — all treated as upstream beer-classification issues. Two rows (Budweiser Magnum, Glenfiddich Experimental IPA) remain correctly unenriched as confirmed KSBCL-pipeline contamination. **The Beer Knowledge Base is considered complete under the current evidence policy** — remaining work is publication evidence gathering (manual observation), not further identity research.
