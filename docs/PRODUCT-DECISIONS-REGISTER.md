# ValueBrew — Product Decisions Register

*Not an architecture document. A discovery-and-consolidation register of every unresolved Product Decision that already exists, explicitly, somewhere in this repository's canon. Built by reading the 20-document canonical architecture (`docs/architecture/current/`), every Engineering Screen Specification, every Experience Specification produced this session, Decision Engine 2.0, Interaction Model 2.0, Domain Model 1.0, the Beer Knowledge Model (both the original and 2.0), the Catalog Specification, the Conversation Model, the Beer Entity Specification, the Navigation Contract, the ADR, the Architecture Resolution Report, the Architecture Reconciliation Report, the Project Brain, the Flutter Implementation Architecture and its sync patches, and the KSBCL Stage 4 product-facing documents. Nothing here is decided. Nothing here is invented. Where two frozen documents disagree, the disagreement is recorded, not resolved.*

---

## How to Read This Register

Every decision below carries an ID (D1–D21) used consistently across all eight parts. **Evidence** means a document states the gap explicitly. **Inference** is flagged wherever this register connects two documents' evidence into one merged decision rather than quoting either directly — per the deduplication instruction, this happens in a handful of places (D9, D13, D14, D16) and is called out each time.

---

# Part 1 — Master Decision Inventory

### D1. Recommendation Ranking Under Incomplete Composition Knowledge
**Description:** What Recommendation's ranking (and, by extension, Value/Style Standing display anywhere else) should do with a candidate SKU that has no confirmed ABV — silently exclude it, include it with an explicit caveat, or something else.
**Why it exists:** the real launch catalog is currently ~87% missing ABV (Architecture Reconciliation Report, confirming `karnataka-beer-catalog.json`: ABV populated on 28/216 items). The reasoning model has no rule for this at all.
**First appeared:** Beer Knowledge Model 2.0.
**Referenced by:** Decision Engine 2.0 (Part 10, item 1 — "newly surfaced by this document"), Interaction Model 2.0 (Part 5, item 1 of "Every Undefined Interaction Discovered"), Domain Model 1.0 (`Value` entity, point 13), Beer Entity Specification 1.0 (§8, "the same unresolved gap named in every document before this one"), Recommendation Experience Specification (§6, item 1 — "this build cannot correctly handle a real, incomplete launch catalog until this is decided"), Recommendation Widget Specification (cites the exact unhandled code line, `generate_recommendation.dart`'s `.where((sku) => sku.price <= budget)` filter).
**Wording evolution:** the wording sharpens with each restatement but the substance never changes — every document independently confirms no resolution exists anywhere, and each treats it as the same gap rather than a new one.

### D2. Search/Browse Results — No Screen Contract
**Description:** The Information Architecture names six screens; only five ever received a Screen Contract. Search/Browse Results has none, which leaves the Navigation Contract structurally incomplete (Home→Beer Detail and Home→Comparison can't be fully specified) and leaves an entire reasoning model undefined. Bundled within this one root gap, per the ADR's and Decision Engine 2.0's own framing, are several concrete facets: no rule for fuzzy vs. literal matching; no rule for ranking multiple literal matches for display order; no rule for whether a restored candidate list (returning from Beer Detail) should be revalidated or simply redisplayed; and (per the Search/Browse Engineering Specification's own additional finding) no rule for whether a search followed by a separate browse attempt accumulates into one evolving candidate set or requires starting over.
**Why it exists:** a sequencing gap in how the canon was built, not a deliberate exclusion (ADR §Open item).
**First appeared:** Information Architecture (naming six screens, contracting five).
**Referenced by:** ADR (the sole item marked **Open** rather than Accepted, and separately named in "Known Limitations" as "the single most structurally significant open item in the canon"), Navigation Contract (§1, §6, §14 — names the two incompletely-specified edges explicitly), Decision Engine 2.0 (Part 10, item 8 — "the most structurally significant gap in the whole product"), Interaction Model 2.0, The ValueBrew Experience ("two gaps run through this entire journey honestly... Search/Browse Results has no canonical screen at all"), Search/Browse Screen Specification (built entirely around this absence, citing "Intentionally left unspecified by the Canonical Architecture" repeatedly).
**Wording evolution:** consistent across every document — this is the one gap every author in this project's history has independently converged on describing the same way, with the same severity.

### D3. The Anchor Situation Trigger Rule (Confirm-as-Is)
**Description:** Beer Detail's Confirm-as-Is judgment fires "whenever the entry context indicates an anchor situation applies" — but no document specifies what that determining signal actually is. The Decision Engine Model rules out identification *mechanism* (search vs. scan) as the signal, which narrows the space without closing it.
**Why it exists:** named as an explicit, deliberate Open Gap Policy item in the Beer Detail Screen Contract itself, not discovered later.
**First appeared:** Beer Detail Screen Contract (§11).
**Referenced by:** ADR (Known Limitations), Beer Detail Engineering Screen Specification (§10, §13), The ValueBrew Experience ("this is itself a named, unresolved canonical gap"), Interaction Model 2.0, Decision Engine 2.0 (Part 10, item 3), Beer Detail Experience Specification (§14 item 4, §20 — restated as the reason Confirm-as-Is remains entirely unbuilt).
**Wording evolution:** none — every restatement is a direct citation of the original, not a reinterpretation.

### D4. Imprecise / Approximate Charged-Price Handling
**Description:** Whether Price Verification should require an exact charged-price figure, accept an approximate range, or handle uncertainty some other way — and what confidence ceiling a delta computed from an approximate figure should honestly be allowed to claim.
**Why it exists:** named explicitly as an open gap in the Price Verification Screen Contract itself (§11).
**First appeared:** Price Verification Screen Contract (§11).
**Referenced by:** ADR (Known Limitations), Repository Sync Patch (Change 2, Change 3, Change 5 — repeatedly insists this must be represented as an explicit Recovery State, "never resolved by inference"), Decision Engine 2.0 (Part 10, item 2), Interaction Model 2.0, Price Verification Experience Specification (§7, §20 — **the real, shipped code has already silently resolved this by inference**, requiring an exactly-parseable number via `double.tryParse()`, which the specification flags as exactly the kind of implementation-layer default the canon warned against).
**Wording evolution:** the canon's own language stays static across every citation; what evolves is the finding that the *implementation* has quietly defaulted to one of the three named options without that default ever being authorized — this is new information this session's own code inspection surfaced, not present in any prior document.

### D5. Comparison Logic Beyond Two Candidates
**Description:** Every tie-breaker, Trade-off, and Tie Disclosure rule in the entire canon assumes exactly two candidates. No document addresses three-or-more, particularly non-transitive results (A beats B, B ties C, but A beats C outright).
**Why it exists:** every worked example across the ten original frozen documents happened to use two candidates; the gap was never deliberately scoped out, only never reached.
**First appeared:** Comparison Screen Contract (§11).
**Referenced by:** ADR (Known Limitations), Comparison Engineering Screen Specification (§10, §13 — its own "flagship open item," Document Notes calls it the screen's "most consequential open architectural question"), Decision Engine 2.0 (Part 5's own flagged gap, restated in Part 10 item 5 as "the single most consequential gap in this entire specification"), Interaction Model 2.0 (identical framing), Comparison Experience Specification (§0, §14, §21 — notes this is not confined to the Comparison screen at all, since a 3+-way Soft-input tie is reachable from inside Recommendation's own Core reasoning independent of whether Comparison is ever entered).
**Wording evolution:** Decision Engine 2.0 is the first document to state explicitly that this gap is *not* Comparison-screen-scoped — every earlier citation (including the original Screen Contract) frames it as belonging to Comparison alone. This is a genuine widening of the gap's understood scope over the project's history, not just a restatement.

### D6. Ambiguous Preference-Type Statements on Recommendation
**Description:** A stated input could plausibly be interpreted as more than one preference type at once (the canon's own example: a number that could be a budget or a size). No rule exists for resolving this ambiguity.
**Why it exists:** named as an explicit open gap in the Recommendation Screen Contract's own Failure Conditions.
**First appeared:** Recommendation Screen Contract (§11).
**Referenced by:** ADR (Known Limitations), Decision Engine 2.0 (Part 10, item 4 — notes it "doesn't change any of the thirteen points' structure, only which bucket a given input falls into").
**Wording evolution:** none — narrowly and consistently restated.

### D7. Whether Price Verification Needs Its Own Low-Confidence Recovery State
**Description:** Recommendation has a named Low-Confidence Response Recovery State; Price Verification does not, despite carrying its own real confidence ceiling (the self-reported charged price). Decision Engine 2.0 raises, without deciding, whether Price Verification should gain an equivalent.
**Why it exists:** proposed by this session's own Decision Engine 2.0 as a "reasoned suggestion... not a decision," explicitly distinguished from the canon's own directly-flagged gaps.
**First appeared:** Decision Engine 2.0 (Part 4.13).
**Referenced by:** Decision Engine 2.0 (Part 10, item 6), Interaction Model 2.0 ("Recovery States, consolidated" — names Price Verification's "unresolved imprecise-input gap" as "the one Recovery-shaped case with no defined Recovery state yet").
**Wording evolution:** this decision did not exist anywhere in the original ten-document canon; it is a genuinely new item this session's own analytical work surfaced, and is marked as such honestly in its own source document.

### D8. Planning Mode Has No Exit Interaction
**Description:** Planning Mode is present from the first Recommendation response through every subsequent one, but no interaction is defined for turning it off within one continuous session — someone who starts planning ahead and later realizes they're at the store now has no modeled path back to an un-flagged state.
**Why it exists:** discovered directly by this session's own Interaction Model 2.0 while mapping every screen's state machine end-to-end; not present in the original ten-document canon.
**First appeared:** Interaction Model 2.0 (Part 2, "Newly discovered gap").
**Referenced by:** Recommendation Experience Specification (§6, item 2 — states the build deliberately does not invent an ad hoc exit control, treating Planning Mode as one-way for the session until this is decided).
**Wording evolution:** none — a single, recent discovery, not yet restated with variation anywhere.

### D9. Conversation Model's Open Tone & Copy Questions (merged cluster — see note)
**Description:** Four related, small, currently-unresolved communication questions, all traceable to the same root cause: **whether any warmth beyond plain factuality is ever appropriate is itself explicitly labeled a genuinely open, undecided Product Decision** — the Conversation Model's own "minimal personality" recommendation is stated as an inference from restraint principles, not a settled prior decision. Downstream of that root question sit three narrower, dependent copy questions: (a) no canonical explanation template exists for Price Verification's verdict sentences, only the three-dimension structure; (b) no canonical guidance exists for whether Comparison's "Ask why" re-surfacing should read identically to its first appearance or acknowledge it's being repeated; (c) no canonical guidance exists for whether a Recovery message should sound different when the underlying gap is itself unresolved architecture (e.g., Search/Browse's non-existence) versus an ordinary runtime condition (zero search results).
**Why it exists:** the Conversation Model was written prescriptively for what already exists, and explicitly declined to originate new tone authority it wasn't asked to settle.
**First appeared:** Conversation Model 1.0 (Part 7, items 1, 2 [renamed 4 for accuracy — see below], 3, 4, 5).
**Referenced by:** Recommendation Experience Specification (§6, item 4, treating the warmth question identically).
**Wording evolution / merge note [Inference — this register's own aggregation]:** Conversation Model 1.0 lists five items in its own Part 7; this register merges four of them (its items 1, 3, 4, 5) into one cluster here since they share the same root cause and would very likely resolve together once the warmth-level question is settled. Its second item — imprecise-charged-price *tone*, once that reasoning gap is resolved — is kept separately merged into **D4** instead, since it's entirely dependent on D4's own resolution and has no independent content until then.

### D10. Beer Detail → Recommendation Navigation — A Genuine Cross-Document Contradiction
**Description:** Information Architecture states plainly that backing out of Beer Detail "returns to whichever screen led there... never defaulting to Home regardless of origin," implying a Beer Detail → Recommendation edge should exist. The Navigation Contract's Screen Graph has no such edge anywhere — not in its direct edges list, not in Recommendation's own stated Entry Points ("from Home or from Comparison" only), and no Transition Contract for it exists. **This is not a gap to be filled; it is two frozen documents disagreeing, and per this register's own instruction, the disagreement is recorded rather than resolved.**
**Why it exists:** the Beer Detail Engineering Screen Specification discovered this directly while tracing exit conditions against both source documents, and states which document it provisionally treats as authoritative for its own purposes (the more recent, purpose-built Navigation Contract) — explicitly without treating that as a resolution of the underlying disagreement.
**First appeared:** Beer Detail Engineering Screen Specification (§4, §13 — "a genuine cross-document inconsistency, not a deliberate deferral").
**Referenced by:** Beer Detail Experience Specification (§14 item 5, §20 — classified there as Engineering Decision Required, restated here as a genuine authority conflict, not merely an implementation question), confirmed independently in `ValueBrewNavigator`'s real source: no `beerDetailToRecommendation` method exists anywhere in its API surface.
**Wording evolution:** the Beer Detail Experience Specification's independent code inspection (this session) confirms the Engineering Specification's document-level finding is also true at the implementation level — the contradiction isn't just theoretical, it's live in the shipped navigator's actual missing method.

### D11. Legal Price Freshness / Staleness Signal
**Description:** Whether any signal beyond the plain last-checked date should ever indicate how stale the Legal Price is considered — and if so, at what threshold, and in what visual form.
**Why it exists:** Generation 1's Beer Detail carried a visible, crowd-sourced freshness strip ("price confirmed 2 days ago by 3 people"); the current canon and implementation have no equivalent at all, leaning entirely on a single authoritative government source with no visible age indicator.
**First appeared:** The ValueBrew Experience (Step 6's own generational note, naming this "a real difference in trust model... worth deciding on purpose, not by default").
**Referenced by:** Price Verification Screen Contract (Future Compatibility — "a possible future indication of the legal reference's own last-confirmed date"), Beer Detail Experience Specification (§14 item 3, §20 — classified as Product Decision Required).
**Wording evolution:** the Screen Contract's own Future Compatibility note is written more tentatively ("a possible future indication") than The ValueBrew Experience's explicit framing as a genuinely open, deliberately-undecided trust-model question — the later document sharpens the earlier one's hedge into a named decision.

### D12. The `Listing` Entity — Build Now or Defer
**Description:** A real SKU can be concurrently supplied by more than one supplier at more than one price (confirmed directly in real 2026-06 KSBCL data: one SKU with ten concurrently live listings spanning ₹80–190). The KSBCL pipeline's own product-design documents already model this as a two-layer shape (canonical product vs. listing); the app's domain model currently collapses both into one `Sku`, an acknowledged overload. Whether to build `Listing` as a real app-level entity now, or leave it a documented-but-unbuilt gap until a real multi-supplier display need is validated, is undecided.
**Why it exists:** discovered directly by this session's Domain Model 1.0 while reconciling the app's domain model against the KSBCL pipeline's own already-built concepts.
**First appeared:** Domain Model 1.0 (`Listing` entity entry, and the `Sku` overload-risk note).
**Referenced by:** Beer Entity Specification 1.0 (§8, "Remaining Product Decisions" — "whether `Listing` should be built as a real entity now, or remain a documented-but-unbuilt gap").
**Wording evolution:** none — a single, recent, consistent finding.

### D13. Whether `pack_count` Belongs in Canonical/SKU Identity (merged cluster — see note)
**Description:** A case size (e.g., cased at 12 vs. 24) is a wholesale procurement fact, not something a shopper perceives, and doesn't stay constant even for a genuinely unchanged product. Including it in identity risks fragmenting one real retail SKU into multiple canonical products.
**Why it exists:** flagged during KSBCL Stage 3's own acceptance review, carried into Stage 4 unresolved.
**First appeared:** KSBCL pipeline (Stage 3 review, per the Stage 4 Product Discussion's own citation).
**Referenced by:** KSBCL Stage 4 Canonical Identity Product Discussion (§3, §6 — explicitly marked **"Open"** in its own summary table, the one item its sibling questions [SKU-vs-family grain, `supplier_code`] resolved but this one didn't), Beer Entity Specification 1.0 (§8 — "whether `packCount` should remain part of Identity resolution at all... restated here as it directly determines whether it belongs on `Sku` as an attribute or purely inside pipeline-internal matching logic").
**Wording evolution / merge note [Inference — this register's own aggregation]:** these are the same underlying question asked at two different architectural layers — the KSBCL pipeline's identity-key composition, and the app's own `Sku` attribute surface — and the Beer Entity Specification's own citation explicitly frames itself as a restatement of the pipeline-layer question, not a new one. Merged into one decision here for exactly that reason.

### D14. Minor Entity Cleanup Decisions (merged cluster)
**Description:** Two small, low-stakes, explicitly-named open items from the same document section: (a) whether `Style.typicalAbvRange` (Curated, descriptive) risks being confused with `Style Benchmark` (Computed, statistical) badly enough to need a stronger naming distinction before either is built; (b) whether `isCraft` is worth recovering at all, given nothing currently depends on it and no reasoning surface has ever named a need for it.
**Why it exists:** both surfaced during the Beer Entity Specification's own reconciliation pass across the three prior model documents.
**First appeared:** Beer Entity Specification 1.0 (§8).
**Referenced by:** no other document — these are single-source, low-priority findings.
**Wording evolution / merge note [Inference — this register's own aggregation]:** merged here purely for economy; both are minor housekeeping questions from the same source paragraph with no independent stakes large enough to warrant separate full treatment across all eight parts of this register.

### D15. Images — An Explicit Small Product Decision Needed Before Launch
**Description:** Of the entire "Product Enrichment" cluster the Catalog Specification named (Flavor Profile, Aroma, Body, Bitterness, Sweetness, Ingredients, Awards, Brewery Story, Images), Images is singled out as different in kind — "plausibly needed for basic usability regardless of any deeper enrichment ambition" — and the document explicitly asks for a small, dedicated Product Decision rather than silent inclusion or silent omission.
**Why it exists:** named directly by the Catalog Specification while classifying enrichment domains, distinguishing Images from the rest of that cluster on launch-readiness grounds specifically.
**First appeared:** Catalog Specification 1.0 (Part 4).
**Referenced by:** no other document.
**Wording evolution:** none — a single, precise statement.

### D16. Future Enrichment Domain Decisions (merged cluster)
**Description:** Three named, explicitly deferred prospective knowledge domains, each requiring its own future Product Decision before any of them is pursued: **Food Pairing** ("the one genuinely grounded sensory-adjacent extension, per Generation 1's own cited design, still requiring a real Product Decision to prioritize"); **Verification History (aggregate)** (an explicitly-labeled *new proposal, not existing canon* — an anonymous, aggregate "what fraction of price checks found an overcharge this month" signal, which the document itself flags as needing a decision about "whether aggregating verification outcomes, even anonymized, sits comfortably with the product's restraint principles, or risks becoming a 'gotcha' metric"); **Sensory/narrative knowledge** broadly (Flavor, Aroma, Body, Bitterness, Sweetness, Ingredients, Awards, Brewery Story) — "deliberately last, and deliberately unscoped, pending a Product Decision this document does not make."
**Why it exists:** the Catalog Specification's own Part 4, deliberately keeping every prospective enrichment domain separate from anything already decided or roadmapped.
**First appeared:** Catalog Specification 1.0 (Parts 3, 4, 9, 10).
**Referenced by:** no other document.
**Wording evolution / merge note [Inference — this register's own aggregation]:** merged into one cluster because all three share an identical disposition in the source document (named, not specified; explicitly not roadmapped; each requires its own future decision) — though each retains a genuinely different priority and risk profile once separated in Parts 4–6 below.

### D17. Consolidating Two Already-Live KSBCL Canonical Products
**Description:** The KSBCL merge mechanism only describes folding a *new* item_code into an *existing* canonical product. It has no described path for the case where two already-existing, already-live canonical products (each with their own accumulated identity-map rows and, once Stage 5 exists, their own price history) are later discovered to be the same real product.
**Why it exists:** never addressed anywhere in the master pipeline architecture — not rejected, simply never reached, and explicitly noted as a scenario that D13's own resolution would make concretely necessary to solve if that identity key is ever narrowed.
**First appeared:** KSBCL Stage 4 Canonical Identity Product Discussion (§4).
**Referenced by:** the same document's own summary table (§6), marked **"Open."**
**Wording evolution:** none — a single, precise, still-open finding.

### D18. App Store Compliance for Alcohol-Related Content Is Untracked
**Description:** ValueBrew recommends, compares, and prices alcoholic beverages. Both major app stores impose category-specific requirements — age-gating/verification, content-rating declarations, a published privacy policy — that nothing in the current implementation architecture assigns an owner to.
**Why it exists:** flagged directly by the Flutter Implementation Architecture's own Implementation Risks section while auditing what blocks a real release, not discovered by this register.
**First appeared:** Flutter Implementation Architecture (Implementation Risks).
**Referenced by:** the same document notes it is "tracked here as a release-readiness risk, owned by Milestone 9 in the Implementation Bootstrap Plan."
**Wording evolution:** none — a single, direct flag, already assigned a nominal owner (M9) but with no actual decision content (what age-gating mechanism, what the privacy policy says) yet produced anywhere.

### D19. No Committed Decision on the Beer Knowledge Base's Real Backend/Data Source
**Description:** What the actual, real, at-scale data source and hosting mechanism for the Beer Knowledge Base will be at launch — explicitly separate from the *architectural* question of what the catalog should contain (already answered exhaustively by the Catalog Specification and the Architecture Reconciliation Report).
**Why it exists:** flagged directly by the Flutter Implementation Architecture as an "open external dependency this document takes no position on," explicitly not blocking implementation start (Milestone 2 can proceed against a stub) but explicitly required before Milestone 6 onward, which depends on real catalog data.
**First appeared:** Flutter Implementation Architecture (Implementation Risks, Implementation Assumptions).
**Referenced by:** implicitly, the entire Architecture Reconciliation Report and Catalog Specification 1.0 — both establish in exhaustive detail *why* this decision is hard (no automated ABV source exists anywhere; no public authoritative GTIN lookup exists; the strongest retail source, Madhuloka, has an explicit bot-blocklist; KSBCL's own PDF is the only government-authoritative price source and is not itself a full catalog) without ever proposing a resolution, since resolving it is explicitly out of scope for either document.
**Wording evolution:** the Flutter Implementation Architecture is the only document that names this as an explicit, owned, undecided *decision point*; every other document treats it as established background fact (the catalog is thin, the data landscape is hostile) without naming "so what do we actually do about launch data sourcing" as a decision anyone is on the hook to make.

### D20. Style Assignment Is Not Currently an Automated Pipeline Output
**Description:** The app's domain model treats Style as foundational and always-known for every Beer. Nothing in the actual KSBCL pipeline currently assigns Style reliably at scale — it is presently a curation/enrichment task, not a pipeline output. This is stated as a flagged inconsistency, not (yet) as a decision with named alternatives — but it directly implies an undecided question: **what should the product do with a real catalog Beer that has no assigned Style**, since Style Standing, Style Benchmark, and Recommendation's own style-refinement step all depend on it existing.
**Why it exists:** discovered directly by this session's Domain Model 1.0 while tracing which pipeline stage actually produces each entity's attributes.
**First appeared:** Domain Model 1.0 (`Style` entity, point 12 — "**[Flagged inconsistency]**").
**Referenced by:** no other document names this explicitly, though it is structurally the same shape of problem as D1 (a Recommendation-and-display-relevant fact that may not exist for a real catalog item) applied to a different attribute.
**Wording evolution:** none — a single, recent finding, not yet restated elsewhere. **[Inference]** this register treats it as a genuine decision-in-waiting (what should downstream reasoning do when Style is missing) rather than only a data-pipeline defect, by direct analogy to D1's own already-recognized shape.

### D21. Formalizing the Mechanical Score-and-Explanation-Together Guarantee
**Description:** Whether the "Explanation is always computed together with its conclusion, never derived afterward as a separate pass" property — already a stated principle for Recommendation, and already recovered from Generation 1 as a genuine mechanical guarantee — should become an explicit, binding reasoning-model requirement for every surface (including Comparison's Trade-off Explanation), rather than remaining an informal, if strongly-recommended, extension.
**Why it exists:** Decision Engine 2.0 recommends this extension explicitly, but labels it "**[Inference]** this document extends it... not yet stated as an app-level ADR decision."
**First appeared:** Decision Engine 2.0 (Part 2.10, Part 7).
**Referenced by:** Decision Engine 2.0 (Part 10, item 7 — "recovered from Generation 1, compatible with and recommended for adoption by Gen 2").
**Wording evolution:** none — a single, low-tension recommendation, not a contested question with real alternatives, included here only because it is explicitly named as unadopted rather than settled.

---

# Part 2 — Decision Classification

| ID | Category | Primary Driver |
|---|---|---|
| D1 | Product | Technical limitation (thin real-catalog ABV coverage) |
| D2 | Product / UX | Values (scope sequencing), also Technical limitation |
| D3 | Product | Values / User research gap — no evidence exists either way |
| D4 | Product | User research gap — no evidence on how people report approximate prices |
| D5 | Product | Values (honesty-under-uncertainty principle) meeting real combinatorial complexity |
| D6 | Product | User research gap |
| D7 | Product | Values (internal consistency of the Recovery-State model) |
| D8 | UX | User research gap (real usage pattern unknown) |
| D9 | UX | Values (unresolved "how much personality" question) |
| D10 | Engineering | Technical limitation — literally two frozen documents contradicting each other |
| D11 | Product | Values (trust-model philosophy: authoritative-source vs. crowd-freshness) |
| D12 | Data / Engineering | Technical limitation meeting real observed data (multi-supplier listings) |
| D13 | Data | Technical limitation (identity-key design under real procurement variance) |
| D14 | Engineering | Product judgment, low stakes |
| D15 | Product | Values (basic-usability threshold) |
| D16 | Product | Business (feature prioritization under limited resources) |
| D17 | Data / Engineering | Technical limitation |
| D18 | Legal | Regulatory uncertainty |
| D19 | Business | Technical limitation (hostile data landscape) meeting Business (build-vs-partner-vs-manual cost) |
| D20 | Data / Product | Technical limitation |
| D21 | Engineering | Product judgment, low stakes |

---

# Part 3 — Blocking Analysis

*Explicit dependency tracing only — no inferred blocking beyond what the source documents actually state or what this session's own direct code/data inspection confirmed.*

| ID | Blocks |
|---|---|
| D1 | Shipping Recommendation against any real, incomplete catalog (Recommendation Experience Specification's own words: "cannot correctly handle a real, incomplete launch catalog until this is decided"); indirectly, Beer Detail's and Comparison's Value/Style Standing display for the same incomplete SKUs |
| D2 | The Home→Beer Detail and Home→Comparison direct-selection paths; Comparison's own primary entry surface (multi-select from Search/Browse); any "I already know what I want" journey that isn't a Recommendation hand-off |
| D3 | Confirm-as-Is (entirely unbuilt as a direct consequence — confirmed in the Beer Detail Experience Specification, zero trace of it anywhere in the real code) |
| D4 | Any UI treatment of an imprecise charged price on Price Verification; already silently defaulted in the shipped code (see D4's own entry) — blocks a *correct*, authorized resolution, not the screen's basic operation, which already works for exact input |
| D5 | Comparison's 3+-candidate path specifically; also, per Decision Engine 2.0's own finding, a reachable branch of Recommendation's own Core reasoning (a 3+-way Soft-input tie), independent of whether Comparison is ever built or entered |
| D6 | A narrow input-classification edge case inside Recommendation's Progressive Question-Asking; does not block ordinary, unambiguous input |
| D7 | Nothing currently — Price Verification's real code already handles its actual confidence ceiling via plain sentence structure without needing a formal Recovery State; this decision blocks only a *future* architectural tidiness improvement |
| D8 | Nothing currently blocking — Planning Mode already works one-way for a session; this blocks only the specific, currently-impossible "turn planning mode off mid-session" interaction |
| D9 | Final copy for Price Verification's verdict sentences, Comparison's "why" re-surfacing copy, and Recovery-message tone generally; does not block any screen's functional behavior |
| D10 | Building any Beer Detail → Recommendation back-navigation edge at all — blocked until one of the two contradicting documents is treated as authoritative by a real decision, not just this register's own provisional citation choice |
| D11 | Nothing currently — this blocks only a *future* freshness-indicator feature, not anything already specified or built |
| D12 | Any future multi-supplier price-spread display (e.g., showing a SKU's ₹80–190 range instead of one collapsed representative price); does not block the current, correctly-scoped single-price display |
| D13 | KSBCL Stage 4's own identity-key finalization for `pack_count` specifically; indirectly, the correctness of `Sku` identity for any beer where case-size variance across suppliers would otherwise fragment one real product into several canonical ones |
| D14 | Nothing currently blocking — both items are pure naming/inclusion housekeeping with zero downstream dependents named anywhere |
| D15 | Nothing currently — blocks only a deliberate decision about whether Images ships as part of the launch catalog spec |
| D16 | Nothing currently — all three are explicitly deferred, unroadmapped future work |
| D17 | Any future KSBCL migration that narrows the identity key (directly named as a consequence of D13's own eventual resolution) |
| D18 | **Blocks actual app store submission outright** — both major stores require these declarations before an app carrying alcohol-related content can be listed at all |
| D19 | **Blocks Milestone 6 onward** in the Implementation Bootstrap Plan (Recommendation, Beer Detail, Price Verification, Comparison all depend on real catalog data); indirectly blocks D1 and D20 from ever being validated against real data rather than the current 1-SKU placeholder catalog. **[RC1 status note, 2026-08-14]: a real catalog now exists (57 SKUs, 8 beers) — D1/D20 can now be checked against real data. This does not itself constitute a formal resolution of D19, which remains open as a decision.** |
| D20 | Any real catalog Beer arriving without an assigned Style — blocks correct behavior of Style Standing display and Recommendation's style-refinement step for such Beers, structurally identical in shape to D1 |
| D21 | Nothing currently — Recommendation and Price Verification's real code already satisfy this property mechanically (confirmed directly in `generate_recommendation.dart` and `verify_price.dart`); this only blocks formal ratification, not behavior |

---

# Part 4 — Launch Priority

| ID | Priority | Rationale |
|---|---|---|
| D19 | **P0** | Blocks every downstream milestone that touches real data; nothing else in this register can be meaningfully validated against reality until this is decided |
| D18 | **P0** | Blocks app store submission outright — a hard gate, not a quality concern |
| D1 | **P0** | Explicitly self-described by its own source document as a blocking dependency for shipping Recommendation against real (incomplete) data — not safely defaultable, since silently excluding vs. silently including incomplete-ABV candidates produces materially different, user-visible recommendation sets |
| D13 | **P1** | Has a safe temporary default (keep the current 5-component key, including `pack_count`, as-is) but real 2026-06 data already shows this risks fragmenting genuine single SKUs; should be closed before the catalog scales much further |
| D3 | **P1** | Confirm-as-Is is a named, real Feature the canon expects to exist eventually; it has a safe temporary default (simply stay unbuilt, as today) but every document that touches Beer Detail treats resolving this as the natural next step once it's prioritized |
| D5 | **P1** | Comparison's two-candidate path is fully buildable without this; the safe default is "ship two-candidate Comparison only, block 3+ candidates at the UI layer" — genuinely safe, but should be resolved before Comparison itself is built, not after, since retrofitting is more expensive than deciding up front |
| D2 | **P1** | The single most structurally significant gap in the canon by the ADR's own words, but has a safe temporary default already in continuous use: every real entry point that would need Search/Browse currently routes around it (Recommendation-only discovery) |
| D4 | **P1** | Has a safe temporary default already shipping (require exact numeric input) — safe in the sense that it doesn't crash or mislead, but not safe in the sense of being an authorized decision; should close before this default calcifies further into being treated as settled by omission |
| D6 | **P2** | A narrow edge case; ordinary, unambiguous Recommendation input already works correctly today |
| D8 | **P2** | No evidence yet that this is a frequently-hit real scenario; safe default (session stays in Planning Mode once entered) already ships |
| D9 | **P2** | Copy polish; does not affect any screen's correctness or safety |
| D10 | **P2** | The contradiction is real but currently inert — no code anywhere attempts this navigation edge, so nothing is currently wrong in the shipped product; should close before anyone builds toward either document without checking the other first |
| D11 | **P2** | Explicitly named as a "worth deciding on purpose, not by default" question, but the current no-signal default is a defensible, working state, not a defect |
| D7 | **P2** | A architectural-consistency nicety; Price Verification's real confidence handling already works correctly without it |
| D12 | **P2** | No current display depends on multi-supplier price spread; the gap is real but not yet product-visible anywhere |
| D17 | **P2** | Contingent entirely on D13's resolution — cannot even be usefully decided until D13 is |
| D20 | **P2** | Same shape as D1 but currently invisible, since no real multi-SKU catalog with missing Style has been loaded into the app yet — will become P0-adjacent the moment D19 is resolved and real data actually loads |
| D15 | **P2** | Explicitly flagged as needing a decision "before launch" by its own source document, but is a narrow, single-attribute question with a safe default (omit Images at launch) already implicitly in effect |
| D14 | **P3** | Zero downstream dependents, explicitly low-stakes by its own source document's framing |
| D16 | **P3** | Explicitly, deliberately unroadmapped by its own source document across all three of its sub-items |
| D21 | **P3** | Already true in practice; this is a documentation/governance formality, not a product-facing question |

---

# Part 5 — Cheapest Validation

| ID | Cheapest resolution path |
|---|---|
| D1 | Product judgment — the three options are already fully enumerated (exclude / include-with-caveat / other); this needs a founder decision, not research, since no amount of user research changes what the honest options are |
| D2 | Product judgment to *scope* it (what should Search/Browse even do, at a Core-V1 level of ambition), then an engineering spike to validate Generation 1's existing fuzzy-match implementation as a starting reference (already flagged by Interaction Model 2.0 as "a legitimate starting reference... not a design problem to solve from nothing") |
| D3 | Product judgment — the Decision Engine Model has already ruled out one candidate signal (identification mechanism); what remains is a short, bounded design exercise, not open research |
| D4 | User research — this is the one item in the register where real evidence (how people actually report prices when uncertain) would genuinely change the right answer, not just validate a guess |
| D5 | Product judgment plus a small engineering spike to enumerate what a 3-candidate non-transitive result even looks like in practice, using the existing 2-candidate logic as a base case |
| D6 | Product judgment — a short, bounded rule ("numbers under N are sizes, over N are budgets," or an explicit disambiguating question) can be judged without research, given how narrow the edge case is |
| D7 | Product judgment — purely an internal-consistency question about the reasoning model's own taxonomy, not something users have an opinion on |
| D8 | User research (or, cheaper, telemetry once any analytics exist — this is exactly the kind of real-usage question analytics instrumentation was proposed for across every Experience Specification in this register) |
| D9 | Product judgment for the root warmth-level question; the three downstream copy questions resolve for free once that's settled |
| D10 | Engineering research — read both documents side by side, confirm which one the team actually wants to be authoritative going forward, and record the resolution as a new ADR entry per the ADR's own Section 8 rule that any gap resolution must be recorded there |
| D11 | Product judgment, informed by a cheap catalog-research check: how frequently does the underlying Legal Price data actually go stale in practice (a fact the KSBCL pipeline's own operational cadence could answer directly) |
| D12 | Product judgment — build it now only if a concrete near-term feature would use it; otherwise, explicitly deferred is the cheap answer, and canon already permits that |
| D13 | Catalog research — directly re-examine the real 2026-06 `structured_rows.csv`/`beer_master.csv` data already cited in the KSBCL Product Discussion document to see how often `pack_count` variance would actually fragment real SKUs, then a short product-judgment call |
| D14 | Product judgment — both are small enough to decide in minutes once someone with authority looks at them |
| D15 | Product judgment — a single, narrow yes/no on launch scope |
| D16 | Product judgment, deferred by design — no validation needed until one of the three is actually being considered for a real roadmap slot |
| D17 | Blocked on D13; once D13 resolves, an engineering spike to design the consolidation mechanism itself |
| D18 | Legal research — this is the one item in the register that specifically and unambiguously requires actual legal/compliance research (app store policy review for alcohol-related content in the target markets), not product judgment |
| D19 | Product judgment plus catalog research — the Architecture Reconciliation Report and the enterprise catalog research corpus already did nearly all the legwork; what remains is a founder-level build-vs-partner-vs-manual-curation decision using research already on file, not new research |
| D20 | Catalog research — directly check how much of the real KSBCL data actually carries a confident Style classification today, the same way ABV coverage was already directly measured |
| D21 | Product judgment — purely a documentation/governance formality; an ADR entry, not a design exercise |

---

# Part 6 — Historical Evolution

| ID | Generation 1 | Generation 2 (canonical rebuild) | Remained unresolved throughout? |
|---|---|---|---|
| D1 | No equivalent reasoning existed — Gen 1's `RecommendationEngine` had no confidence-tiering concept at all | Introduced the Composition Knowledge concept that makes this gap visible for the first time | **Yes, unresolved throughout** — could not have existed as a gap before Gen 2's own knowledge-tiering model created the category it falls into |
| D2 | Had a real, working fuzzy-match implementation (explicitly recoverable per Decision Engine 2.0) | Never rebuilt it; Search/Browse has no Screen Contract at all | **Yes, unresolved throughout**, though Gen 1 offers real salvageable material for whenever it is resolved |
| D3 | No equivalent — Gen 1 had no Confirm-as-Is-shaped feature | Named as a real, specified Feature, deliberately demoted from having its own entry point per an early Feature Inventory correction the ADR records | **Yes, unresolved throughout Gen 2's own history** |
| D4 | No equivalent — Gen 1 had no Price Verification feature at all (confirmed directly, zero trace anywhere in Gen 1's archive or code, per the Price Verification Experience Specification's own search) | Introduced the capability and, separately, the gap | **Yes, unresolved throughout**, and the real shipped code has since silently (not authoritatively) defaulted on it |
| D5 | Gen 1's Compare screen existed but performed no synthesis of any kind — no winner, no trade-off, no tie, so the 3+-candidate question never had anywhere to arise | Introduced Trade-off Explanation and Tie Disclosure, which is what makes a 3+-candidate generalization question exist in the first place | **Yes, unresolved throughout Gen 2**, and explicitly could not have been a Gen 1 question |
| D6 | No equivalent — Gen 1's simpler filter/sort model had no ambiguous-input classification problem | Introduced Hard/Strong/Soft preference typing, which is what creates the ambiguity | **Yes, unresolved throughout Gen 2**, structurally new to this generation |
| D7 | N/A | Raised entirely within this session's own Decision Engine 2.0 | **Never previously identified; unresolved since the moment it was first named** |
| D8 | N/A — no Planning Mode concept in Gen 1 | Introduced Planning Mode; the exit-interaction gap was discovered directly by this session's Interaction Model 2.0 | **Never previously identified; unresolved since the moment it was first named** |
| D9 | Gen 1 had its own, different, unexamined default tone (not audited in this register) | The Conversation Model explicitly declines to settle the warmth question, framing its own "minimal personality" recommendation as an inference, not a decision | **Yes, unresolved throughout Gen 2's own documentation history** |
| D10 | N/A — this is a Gen 2-internal documentation contradiction between two of its own frozen documents | Both contradicting documents (Information Architecture, Navigation Contract) are Gen 2 originals | **Yes, unresolved since the Navigation Contract was written after Information Architecture and never reconciled against it** |
| D11 | **Gen 1 answered this** — a visible, crowd-sourced freshness strip | **Gen 2 intentionally reversed it** — no freshness signal at all, leaning entirely on single-source government authority instead | Explicitly flagged as a deliberate reversal whose correctness is itself the open question, not an oversight |
| D12 | No equivalent concept existed in Gen 1's simpler, single-price data model | Never built; the KSBCL pipeline (a separate, later effort) built the concept first, and the app domain model hasn't caught up to it | **Yes, unresolved**, and interestingly originates from the *catalog pipeline* work rather than either app generation |
| D13 | N/A — Gen 1 had no canonical-identity concept at all; this is purely a KSBCL pipeline question | N/A | **Yes, unresolved since Stage 3's own review**, and explicitly still open per the Stage 4 Product Discussion's own summary table, unlike its two sibling questions which did get resolved |
| D14 | N/A | Raised entirely within this session's Beer Entity Specification | **Never previously identified; unresolved since first named**, low-stakes |
| D15 | Gen 1's data model had no image field either (not confirmed as recovered or original — the Catalog Specification states plainly this was never part of any existing canon) | Never decided one way or the other | **Yes, unresolved throughout**, genuinely new territory per the Catalog Specification's own honest framing |
| D16 | Food Pairing specifically has Gen 1 precedent ("the one genuinely grounded sensory-adjacent extension, per Generation 1's own cited design"); Verification History and the broader sensory/narrative cluster do not | Never pursued any of the three | **Yes, unresolved throughout**, deliberately and explicitly deferred rather than forgotten |
| D17 | N/A — purely a KSBCL pipeline question, no app-generation equivalent | N/A | **Yes, unresolved**, never previously reached since it depends on real accumulated data existing first (which it now does) |
| D18 | N/A — Gen 1 never reached a real release-candidate/app-store-submission stage this thoroughly documented | Flagged directly by this session's own implementation-planning work | **Yes, unresolved**, a genuinely new finding tied to this generation's approach to actual release planning |
| D19 | Gen 1 used whatever ad hoc data it had; no formal sourcing decision was ever made explicitly either | Never formally decided; extensively researched (the entire `enterprise_catalog_research` corpus) but never resolved into an actual sourcing commitment | **Yes, unresolved throughout both generations**, now with an unusually large amount of research already on file to decide from |
| D20 | N/A — Gen 1's simpler model didn't distinguish pipeline-produced facts from curated ones this precisely | Discovered directly by this session's Domain Model 1.0 | **Never previously identified; unresolved since first named** |
| D21 | The mechanical guarantee itself is explicitly **recovered from Generation 1** — Gen 1 already had this property, informally | Gen 2 restated it as a principle for Recommendation specifically but never formally extended or ratified it product-wide | **A Gen 1 idea Gen 2 partially adopted but never formally closed** — the one item in this register that is more "administrative catch-up" than "genuine open question" |

---

# Part 7 — Decision Interactions

**D19 is the root dependency for the largest cluster in this register.** Until the Beer Knowledge Base's real data source is decided, D1 and D20 cannot be validated against anything but a 1-SKU placeholder catalog — both are currently theoretical-but-certain problems that become concretely, visibly urgent the moment real data loads. Resolving D19 doesn't resolve D1 or D20 itself, but it is the precondition for either one mattering in practice. **[RC1 status note, 2026-08-14]: real data now loads (57 SKUs, 8 beers) — D1/D20 are checkable in practice, not merely theoretical, though D19 itself remains formally open.**

**D13 must be resolved before D17 can be meaningfully attempted.** D17 (consolidating two already-live canonical products) is explicitly named, in its own source document, as a scenario that becomes necessary specifically *if* D13 is resolved in a way that narrows the identity key — D17 has no independent content until D13 closes.

**D9's root question (how much warmth) determines whether D9's three downstream copy sub-questions need independent answers at all.** Once the warmth-level decision is made, the Price Verification explanation-template question, the Comparison "why" re-surfacing tone, and the Recovery-message tone question are very likely to resolve as natural, low-effort consequences of that one decision rather than needing separate deliberation — this register keeps them nominally separate (per the instruction not to over-merge) but flags that D9 is the actual leverage point.

**D2 becomes irrelevant to D5 in one specific way, and load-bearing to it in another.** D2 (Search/Browse) is one of Comparison's three named entry paths — if D2 remains unresolved indefinitely, Comparison's *primary* multi-select entry surface stays unreachable, but Comparison's Recommendation-hand-off and Beer-Detail-hand-off entry paths remain fully independent of D2 and would let a 2-candidate Comparison ship without D2 ever being touched. D5 (3+-candidate logic), however, is explicitly *not* contingent on D2 at all — Decision Engine 2.0's own finding is that a 3+-way tie is reachable from inside Recommendation's Core reasoning with no Comparison screen involved whatsoever.

**D3 and D2 share a blocking relationship that isn't obvious from either document alone.** The ValueBrew Experience's own framing states this directly: "the Anchor-Known path only exists today as a hand-off destination, never a true entry point" — because Search/Browse (D2) is what would make Beer Detail reachable *without* going through Recommendation first, and Confirm-as-Is (D3) is specifically scoped to that anchor-known entry pattern. Resolving D2 without also resolving D3 would create real anchor-known traffic with nowhere for the Confirm-as-Is judgment to attach; resolving D3 without D2 leaves the judgment specified but still unreachable in practice, exactly as today.

**D10 does not block anything else in this register, and nothing else blocks it.** It is the one purely self-contained item — a live contradiction between two frozen documents that happens to currently be inert because no code anywhere attempts the navigation edge in question.

**D4's real-code finding changes D7's stakes.** D7 (whether Price Verification needs its own Low-Confidence Recovery State) was raised as an abstract architectural-consistency question. But the Price Verification Experience Specification's own direct code inspection found that the real screen has already silently resolved D4 by requiring exact numeric input — meaning the *concrete* form D7's eventual Recovery State would need to take is now much more specific than it was when Decision Engine 2.0 first raised it in the abstract: it would need to represent specifically "an unparseable or approximate price entry," not a generic confidence shortfall. D4's resolution should therefore be decided before D7's, not after, since D7's own shape depends on it.

**D18 is fully independent of every other item in this register.** It requires legal research, not product or engineering judgment, and nothing else here blocks it or is blocked by it except the release milestone itself.

---

# Part 8 — Executive Summary

**1. How many genuine Product Decisions remain?**
Twenty-one, after aggressive deduplication across every document searched. Four of those twenty-one (D9, D13, D14, D16) are themselves merges of smaller, closely-related sub-questions from the same source documents — so the true count of individually-named open questions across the repository is closer to thirty, consolidated here into twenty-one decision-shaped units worth tracking and closing independently.

**2. How many are actually launch blockers?**
Three are P0: **D19** (no committed real data-sourcing decision — blocks everything downstream that touches real catalog data), **D18** (app store compliance for alcohol content — blocks submission outright, a hard external gate, not a quality judgment), and **D1** (incomplete-ABV ranking behavior — the one reasoning gap explicitly self-described by its own source document as blocking a correct ship against real, incomplete data). Everything else in the register has either a safe, already-shipping temporary default (P1/P2) or is explicitly, deliberately deferred future work (P3).

**3. Which three decisions have the highest leverage?**
**D19** first — it is the root dependency for the largest cluster in the register (Part 7) and the precondition for D1 and D20 ever mattering in practice; closing it doesn't just unblock a milestone, it makes an entire category of currently-theoretical problems become real and testable. **D1** second — it is the single most independently and repeatedly cited unresolved item across the entire canon (six separate documents), and its resolution is a pure product-judgment call with the options already fully enumerated, meaning it's cheap to close and expensive to keep leaving open. **D2** third — the ADR's own words call it "the single most structurally significant open item in the canon," and Part 7 shows it has real, non-obvious downstream relationships to both D3 and D5 that most individual documents don't surface on their own.

**4. Which decisions are repeatedly appearing across multiple documents and should stop propagating into future specifications?**
**D1** (six citing documents), **D2** (six citing documents, including the ADR itself), **D3** (five citing documents), **D5** (five citing documents), and **D4** (five citing documents, now compounded by the real-code finding that it's been silently defaulted rather than decided). Every future specification produced in this project has, so far, correctly re-flagged rather than silently resolved each of these — which is the right discipline to keep — but the repetition itself is now a signal in its own right: these five are mature enough, and cheap enough to decide (per Part 5, four of the five resolve by product judgment alone, no research required), that continuing to re-flag them in yet another future document rather than actually deciding them is starting to cost more than deciding would.

**5. What is the recommended order to close them?**
Not a resolution — an ordering, based strictly on the dependency structure already traced in Part 7 and the priority tiers in Part 4: **first D19** (unblocks real data, the precondition for validating D1 and D20 at all), **then D1** (cheap, fully-scoped, explicitly blocking, and the most-cited item in the register), **then D18** in parallel with either (fully independent, requires only legal research, and is a hard external gate that doesn't get easier by waiting), **then D2** (unblocks the Home→Beer Detail/Comparison direct paths and, per Part 7, has real downstream relationships to D3), **then D3** (only meaningfully useful once D2 makes anchor-known traffic real), **then D13** (before it compounds further as the real catalog scales, and before D17 can even be attempted), **then D5** (before Comparison itself is built, since retrofitting a 3+-candidate model afterward is more expensive than deciding up front), with **D4 resolved before D7** specifically (per Part 7's own finding that D7's shape depends on D4's answer). Everything else in the register — D6, D7, D8, D9, D10, D11, D12, D14, D15, D16, D17, D20, D21 — can reasonably wait behind this sequence without cost, consistent with their P2/P3 placement in Part 4.
