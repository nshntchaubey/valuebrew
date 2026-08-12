# Enterprise Research Reconciliation

*A reconciliation, not a summary, and not a redesign. Every document under `docs/research/enterprise_catalog_research/` was read in full for this pass — not skimmed, not sampled: all 11 top-level deliverables, all 7 `research/domain/*.md` raw agent outputs, all 12 `research/catalog-sources/*.md` raw extraction outputs, and `karnataka-beer-catalog.json`/`.csv` inspected directly, field by field, via Python. Cross-referenced against the full current architecture: Project Brain, Product Definition, Beer Knowledge Model 2.0, Decision Engine 2.0, Domain Model 1.0, Catalog Specification 1.0, Catalog Contract 1.0, Beer Entity Specification 1.0, Catalog Builder Architecture, Catalog Implementation Architecture, Catalog Builder Implementation Design, Beer Knowledge Base Architecture, and the Product Decisions Register. Every idea below is classified into exactly one of five categories. No architecture is proposed. No contradiction is silently resolved.*

**Categories, used consistently below:**
**A** — Already fully absorbed into current architecture.
**B** — Present in the research, but improved or replaced by current architecture (the underlying need survived; the specific mechanism didn't).
**C** — Valuable, evidenced knowledge that has **not** yet been incorporated and should be recovered before implementation begins.
**D** — Historical only — useful for understanding how the corpus was produced, never to influence implementation.
**E** — A contradiction, either between the research and current canon, or discovered inside the research corpus itself. Documented, not resolved.

---

## Part 1 — Topic-by-Topic Reconciliation

### Source hierarchies
**A.** The research's Tier 0–3 source ranking (KSBCL as regulatory/price ground truth; Madhuloka as retail breadth; brand pages as spec/ABV metadata; Open Food Facts as barcode bootstrap) is the direct ancestor of, and is fully restated in, Catalog Builder Architecture Part 3's Government/Manufacturer/Retailer/Manual-Observation/Future-Enrichment table. No daylight between them.

**C.** One specific source class named repeatedly and with real evidentiary weight in the research — **United Breweries' SEBI Regulation 30 filings** (`unitedbreweries.com/pdf/Material Events/`) as an early-warning, structured "new SKU launching in Karnataka" signal, sometimes carrying exact per-SKU Karnataka pricing before a beer ever reaches KSBCL's own monthly list — was already flagged once, in the earlier Architecture Reconciliation Report (Category C1 there), as worth adopting. It was never actually carried into Catalog Builder Architecture's Stage 1 ("New SKU Discovered," §Part 2), which today names only the KSBCL monthly PDF as the discovery trigger. This is a real, still-open recovery — see Part 4, item 1.

### Brewery knowledge / contract brewing / supplier vs. brewery
**A.** Fully absorbed, and this is the cleanest, most complete recovery in the whole corpus. The real, confirmed contract-brewing evidence (Budweiser bottled by S P R Distilleries Pvt Ltd under KSBCL Supplier Code 0212; Guinness imported via Brindco Enterprises under Code 0972) is cited directly in Catalog Builder Architecture Part 4's Brewery row and in Catalog Contract 1.0 Part 4's own flagged licensed-supplier-vs-brand-owner caveat. Nothing further to recover here.

### Style classification
**A.** The general principle — style has no automated source anywhere, must come from brand-owner pages, and a single self-contradicting source (STOK's own spec table vs. its own FAQ) must never be silently resolved — is fully present in Catalog Builder Architecture Part 4 and the Catalog Enrichment Playbook Part 5/6.

**C.** One specific, non-obvious technique the research proved out repeatedly (Carlsberg Elephant, Tuborg Green/Strong, 1664 Blanc) — cross-referencing a brand's **global parent-company catalog** by name-match when the India-specific site omits ABV/style, while treating an origin-field mismatch (e.g., an entry's `Brand Origin: Malaysia` when the India site states an India launch) as a hard signal *not* to trust the match — is real, useful, and not written down anywhere in the Catalog Enrichment Playbook's research workflow (Part 4), which currently only names "the brewery's own official site" as a single, undifferentiated tier. See Part 4, item 2.

### ABV acquisition
**A.** Fully absorbed. The research's central, load-bearing conclusion — no web source reliably publishes ABV for the Karnataka catalog; it must come from physical label photography, and a source's own internal self-contradiction (STOK 7% vs. 8%) must be broken by the physical can, never picked arbitrarily — is exactly Catalog Builder Architecture §0.3/Part 1's founding premise and the Catalog Enrichment Playbook Part 5's own resolution rule, word for word in spirit.

### Catalog acquisition (strategy, verification protocol, cadence)
**B.** The overall shape survived — tiered sourcing, a verification step before publication, a discovery pipeline — but the *specific mechanism* was replaced. The research proposes a formal database-level "two-source verification gate" (§3 of the acquisition playbook) before any fact is marked "Verified" in a live record. Current architecture replaced this with a simpler, one-founder-scale rule: one real, citable Manufacturer-tier source is sufficient (Catalog Enrichment Playbook Part 4: "you do not need two sources to agree before you can record a fact"). This is a deliberate, reasoned substitution appropriate to today's scale, not an oversight — but it is also a genuine disagreement worth stating plainly rather than papering over. See Part 5 (Category E), item 1.

**C.** The research's **field-specific re-verification cadence table** (KSBCL/Madhuloka prices: weekly; UBL filings: weekly; brand spec pages: quarterly; full site-health check: monthly) is a concrete, well-reasoned answer to a question Beer Knowledge Base Architecture explicitly left open on purpose ("no periodic re-check mechanism exists, and none is invented here," Part 5). This is a ready-made, evidenced answer sitting unused. See Part 4, item 3.

### Schema ideas / production database ideas
**B/D mixed** — covered in full in Part 3 below, since the request asks for a dedicated audit of `03-production-database-schema.md`. Headline: the *principle* of immutable, append-only facts survived and was simplified (git history replaces a formal claims-ledger); the *numeric confidence-scoring formula* did not survive and must never be recovered — it directly contradicts the Beer Knowledge Model's own permanent rule against blending confidence into one number.

### Enrichment workflow
**B**, overall — the Catalog Enrichment Playbook is a direct, simplified descendant of the research's acquisition playbook, with the two Category C carve-outs above and the Category E disagreement on verification strictness.

### Source reliability (which specific sites were up/down/broken on 2026-08-05)
**D.** Confirmed, correctly, as historical-only already by the earlier Architecture Reconciliation Report, and this pass agrees on every point: Living Liquidz down, Bira91.com serving a foreign TLS cert, Tonique stale since April 2023, Livcheers' explicit bot-blocklist. None of this should influence architecture; all of it is a snapshot of one day.

### Search strategy
**C, but explicitly gated.** `10-search-engine-design.md` is the single most substantial piece of unabsorbed material in the whole corpus — and appropriately so, since Search/Browse Results has no Screen Contract anywhere in current canon (Product Decisions Register D2, the single most structurally significant open item in the entire architecture). Nothing in it should be built today. But one specific sub-idea — the **alias/synonym design** (a curated brand-abbreviation table plus a per-entity `search_aliases` field, seeded directly from real observed retailer misspellings) — is relevant *right now*, independent of whether Search/Browse itself is ever built, because it's needed for entity resolution during enrichment, not just for a future search box. See Part 4, item 4.

### Data validation
**A**, mostly — duplicate-row detection, category mistagging, and stale-placeholder-content heuristics are all directly reflected in Catalog Builder Architecture Part 7's validation rules (the contamination-filter rule is a direct structural descendant of the research's "category mistagging" finding, even though the specific evidence differs — a Cadbury bar tagged "Beers" on Open Food Facts vs. a real whisky tagged "beer" in `beer_master.csv`).

**C.** One validation category is real, well-evidenced, and currently missing entirely: **taproom-only vs. actual retail availability.** The research proved this exact failure mode concretely — Arbor Brewing Company has a real Bengaluru taproom, but its own site states its canned/retail product is "Retailing only across Goa"; Windmills Craftworks and Byg Brewski show zero retail/bottle/takeaway language anywhere and appear to be on-premise-only. Nothing in Catalog Builder Architecture's Part 7 validation rules or Beer Knowledge Base Architecture's schema catches "this brewery has a confirmed Karnataka presence, but this specific packaged SKU is not actually sold there." See Part 4, item 5.

### GTIN
**A.** Thoroughly absorbed already — Open Food Facts as the only currently-safe, redistributable source; Go-UPC's ToS explicitly forbidding redistribution; GS1 India's DataKart having no public API — all cited directly and correctly in Catalog Specification 1.0, Catalog Builder Architecture Part 4, and Beer Knowledge Base Architecture Part 3/10.

### Images
**A.** The research's `image` table design (polymorphic entity reference, `license`, `license_requires_attribution`, defaulting new rows to `unknown-do-not-redistribute` until legal clears them) is cited directly, by name, as the source of Catalog Builder Architecture Part 7's own image-licensing validation rule. Already credited, already absorbed.

### Aliases / naming conventions
**C.** The single clearest, most concretely-evidenced recovery in this entire reconciliation. The research didn't just theorize about naming inconsistency — it *caught real instances of it happening*, in data ValueBrew's own KSBCL pipeline output shares the same character with: "KF" → Kingfisher, "BUDWIESER" (a literal misspelling, verbatim from Madhuloka), "Bira 91" returning zero Open Food Facts hits while only "Bira" matches. Beer Knowledge Base Architecture's Beer YAML schema (Part 3) has **no alias field of any kind** today. See Part 4, item 4 (bundled with the search-strategy alias design, since they're the same underlying idea observed from two different angles).

### Research heuristics
**A.** The corpus's own operating discipline — never fabricate, omit rather than guess, separate verified fact from inference, cite every claim, prefer a direct `curl`/`pdftotext` extraction over an AI-summarized `WebFetch` pass for anything high-stakes — is exactly the discipline this entire project's Evidence/Inference/Recommendation convention already descends from, and every catalog document produced this session has followed it without exception.

### Catalog quality
**A.** The research's own README is explicit that `karnataka-beer-catalog.csv`/`.json` is "a pre-canonicalization staging table, not the production `brand` table" — and every catalog document this session has produced treats it exactly that way: the real Catalog Builder reads only from `pricing_data/beer_master.csv` (the KSBCL pipeline's own fresh, 2026-06 output), never from this research corpus's static 2026-08-05 snapshot. This boundary has never been violated anywhere in current architecture, and is worth stating explicitly rather than assuming.

### Karnataka catalog data (the specific brand/SKU findings)
**D**, for the specific point-in-time findings (which exact SKUs were High/Medium/Low confidence on 2026-08-05) — superseded by the real, live, monthly KSBCL pipeline, which is now the actual authority. **A**, for the *methodology* behind those findings (rank confidence by KSBCL > direct retail listing > brand-site-only, in that order) — this is exactly Catalog Builder Architecture's own confidence hierarchy.

### Production database ideas
Covered in full in Part 3.

---

## Part 2 — Audit: `karnataka-beer-catalog.json`

*Treated as a historical artifact, not assumed correct. Every field checked directly against the current architecture stack, with real population statistics computed via direct Python inspection of the actual 216-row file (not the README's summary of it).*

| Field | Real population | Does current architecture have an equivalent? | Where | Recover? |
|---|---|---|---|---|
| `beer_name` | 216/216 (100%) | Yes — `Beer.name` | Catalog Contract 1.0 Part 4 | No — already superseded by KSBCL's own `item_name_raw`/`display_name` |
| `brand` | 215/216 (99.5%) | **No direct equivalent.** Current `Beer` has no separate `brand` field distinct from `name` | — | **No** — Domain Model 1.0 already considered and rejected a separate Brand-vs-Beer split for launch scope (the real `Beer` class conflates them, deliberately, per Beer Entity Specification 1.0). Not a gap; a considered simplification. |
| `brewery` | 128/216 (59.3%) | Yes — `Beer.brewery` | Catalog Contract 1.0 Part 4 | No, already equivalent, though the still-open licensed-supplier-vs-brand-owner question (same one flagged repeatedly across this session) applies equally here |
| `style` | 105/216 (48.6%), and where present, frequently caveated "(from product name)" — i.e. inferred, not confirmed | Yes — `Beer.styleId` | Catalog Contract 1.0 Part 4 | No — but the sparse, inferred-not-confirmed population rate is itself direct evidence for why Style is Curated, never automated (already correctly reflected in Catalog Builder Architecture) |
| `abv` | **True population is 24/216 (11.1%), not the 28/216 a naive non-empty check suggests** — 4 of the 28 "filled" cells literally contain the string `"unknown"` rather than a real value, and several genuinely-filled cells are long free-text sentences with embedded citations and caveats, not a clean numeric field (e.g. `"Between 5% and 8% (site states a range...)"`, `"7.2% (sourced from carlsberggroup.com...)"`) | Yes structurally — `Sku.abv`, a clean `double` | Catalog Contract 1.0 Part 5 | No — the real schema is already a stricter, better-typed superset of this field; recovering the free-text/caveat style would be a regression |
| `calories` | 4/216 (1.9%) | Yes — `Sku.calories` | Catalog Contract 1.0 Part 5 | No — already equivalent, and the near-total absence here is exactly why Catalog Specification 1.0 never treated calories as Launch Critical |
| `size` | 106/216 (49.1%), free text (`"650ML x 12 Btls"`, `"330 ml"`) | Yes, but Computed/normalized — `Sku.sizeMl`, an `int` | Catalog Contract 1.0 Part 5; KSBCL pipeline Stage 3 | No — the free-text form is exactly the problem KSBCL Stage 3's structured extraction already solves properly |
| `package_type` | 169/216 (78.2%), free text (`"Bottle, case of 12"`, `"Tin/Can"`) | Yes, but a closed enum — `Sku.packageType` | Catalog Contract 1.0 Part 5 | No — though see the already-flagged, real `PackageType` enum vs. `container_type` mismatch (Catalog Contract 1.0 Part 5) for a genuinely live version of this same normalization problem |
| `karnataka_price_observations` | 126/216 (58.3%) in the JSON, as an array of `{value, source, source_url, confidence}` objects, where `value` is itself free text (`"Rs. 110.00 per bottle (item code..., price effective...)"`) — **not a clean numeric price**, though the sibling CSV does have one (see Part 2's own note below and Part 5, item 2) | Yes — `Sku.price`, `priceLastChecked`, `priceSource` | Catalog Contract 1.0 Part 5 | No — already a cleaner, better-typed equivalent |
| `gtin` | 11/216 (5.1%) | Not yet in the real `Sku` schema at all (reserved in the pipeline, absent from the app model) | Catalog Contract 1.0 Part 5 (explicitly not added, Version 1 discipline) | No — correctly deferred, not a gap |
| `barcode` | 11/216 (5.1%), always identical to `gtin` on the same row | No separate equivalent, and none needed — `barcode` and `gtin` are the same fact here, never actually distinct | — | No |
| `image_url` | 99/216 (45.8%) | Not in the real `Sku`/`Beer` schema | Beer Knowledge Base Architecture Part 3 (`images`, still-open per D15) | No — correctly gated behind the still-open Images decision |
| `manufacturer_url` | 187/216 (86.6%) | No equivalent anywhere, and none needed — this is a research citation, not a product fact | — | No |
| `sources` / `confidence_score` / `last_verified_note` | 216/216 (100%) each | Yes, conceptually — the source-attribution unit (`source_type`, `source_name`, `observed_at`, `observed_by`) | Beer Knowledge Base Architecture Part 5 | **Already recovered and improved** — the current attribution unit is more structured (four discrete typed fields vs. one free-text sentence) than anything in this JSON |

**Summary judgment:** every field in `karnataka-beer-catalog.json` that matters has either a direct, cleaner equivalent in current architecture already, or is correctly and deliberately deferred behind a still-open Product Decision (Images, GTIN). Nothing here warrants recovery on its own. Its actual value, already realized, was as a *proof of concept* — confirming real ABV/style/GTIN facts exist and are reachable — not as a data source to be ingested.

---

## Part 3 — Audit: `03-production-database-schema.md`

**What survived.** The core philosophy — claims are immutable, disagreement is data not noise, sources are ranked not trusted equally, confidence must be tracked per-fact — is fully present in Catalog Builder Architecture Part 1 and Beer Knowledge Base Architecture Part 1, in spirit and mostly in exact language. The GTIN-as-optional-enrichment-never-a-join-key principle survived unchanged. The image-licensing discipline survived and is directly credited.

**What disappeared intentionally.** The entire Postgres-plus-OpenSearch, 50,000-SKU, multi-table claims-ledger architecture (company/brewery/brand/beer/sku/gtin_claim/alcohol_percent_claim/karnataka_mrp_history/evidence/source/audit_trail — twenty-plus tables) was explicitly, deliberately not adopted. Catalog Implementation Architecture Part 8 names this directly: it is "the right reference to revisit" only once Product Decisions Register D19 (no committed decision on the Beer Knowledge Base's real backend) is ever resolved toward a database-backed platform — not before. This is not an oversight; it is a scale-appropriate decision, stated as such, on the record, more than once across this session's documents.

**What disappeared accidentally — or at least, without ever being deliberately weighed.** Two things:
1. The **field-specific re-verification cadence** (Part 4 of this document, item 3) — the production schema's own `recency_decay_factor` (30-day price half-life vs. 730-day ABV/style half-life) encodes exactly the same insight the acquisition playbook states in plain language, and neither made it into Beer Knowledge Base Architecture, which explicitly punted on staleness entirely.
2. The **taproom-vs-retail availability distinction** (Part 4, item 5) — nothing in the schema or any later document ever proposed a field for it, even though the underlying research evidence (Arbor Brewing) was gathered in the same research pass.

**What deserves recovery.** Items 1 through 5 in Part 4, below — nothing beyond them.

**What should stay dead, explicitly, not merely unmentioned.** The **numeric confidence-scoring formula** (§6 of the schema document: `source_tier_weight × extraction_method_multiplier × recency_decay_factor + corroboration_bonus − contradiction_penalty`, clamped to a single float). This is not simply unabsorbed — it is **structurally incompatible** with the Beer Knowledge Model's own repeatedly, permanently enforced rule that confidence must never be blended into one number, stated as the single most consistently-cited discipline across the entire canonical architecture (Recommendation Framework, every Screen Contract, the Canonical Interaction Lexicon). Recovering this formula, even partially, would directly violate frozen canon. It should remain in the research corpus, cited here as historical, and nowhere else.

---

## Part 4 — Category C Recoveries (Full Detail)

### 1. UBL Regulation 30 SEBI filings as a new-SKU discovery signal
**Source document:** `research/domain/01-brewery.md`; restated in `04-catalog-acquisition-playbook.md` §5; already flagged once, undeployed, in `ARCHITECTURE-RECONCILIATION-REPORT.md` (Category C1).
**Exact concept:** United Breweries publishes SEBI Regulation 30 disclosure PDFs at `unitedbreweries.com/pdf/Material Events/` for every new product launch, including Karnataka-specific launch dates and, occasionally, full per-SKU Karnataka pricing (the Kingfisher Smooth filing gives exact pricing across four package sizes) — often *before* a new SKU would ever appear in KSBCL's own next monthly price list.
**Why it still matters:** it is the only structured, dated, official early-warning signal for a brand-new Karnataka SKU found anywhere in the entire research corpus — cheaper to catch here than to wait for retail sighting.
**Where it belongs:** Catalog Builder Architecture Part 2, as an additional Stage 1 discovery trigger alongside the KSBCL monthly PDF, or as a new "candidate SKU, pending KSBCL confirmation" status in the Catalog Builder's own pipeline.
**Implementation impact:** low — a simple, low-frequency (irregular filing cadence, "multiple per year") folder-watcher and PDF-text-extract, feeding a pending-review queue, not a build-blocking dependency.
**Affects:** Catalog Builder Architecture (Part 2, Stage 1) — nowhere else.

### 2. Cross-referencing a brand's global parent catalog, with an origin-mismatch veto
**Source document:** `research/catalog-sources/07-carlsberg-india-carlsbergindia-com-and-carlsberg-group-globa.md`.
**Exact concept:** when a brand's India-specific site omits ABV/style, check the parent company's global brand catalog for a name-matching entry — but treat a conflicting `Brand Origin` field (e.g., a "Carlsberg Smooth Draught" global entry listing Malaysia, when the India site describes an India-launched "Carlsberg Smooth") as a hard veto against using that match, not a minor caveat.
**Why it still matters:** it produced real, otherwise-unobtainable ABV figures (Carlsberg Elephant 7.2%, Tuborg Green 4.6%, Tuborg Strong 6.1%) while also correctly declining to report a plausible-looking but likely-wrong figure (Carlsberg Smooth's 4.8%, from the Malaysia-origin entry).
**Where it belongs:** Catalog Enrichment Playbook Part 4, as a named research step between "the brewery's own official site" and "a retailer listing" — currently the Playbook treats "brand's own site" as one undifferentiated tier with no guidance for this specific, real scenario.
**Implementation impact:** none — this is pure operator guidance, no code or schema change.
**Affects:** Catalog Enrichment Playbook only.

### 3. Field-specific re-verification cadence
**Source document:** `04-catalog-acquisition-playbook.md` §4.
**Exact concept:** different fields decay at different rates and should be re-checked on different schedules — price weekly, new-launch-signal sources (UBL filings) weekly, brand spec pages (ABV/style) quarterly, full site-health (is a source still reachable, has its structure changed) monthly, any single-source/Low-confidence record re-attempted every two weeks until resolved or explicitly marked as staying single-source.
**Why it still matters:** Beer Knowledge Base Architecture explicitly, on the record, declined to specify any staleness/re-verification cadence at all ("no periodic re-check mechanism exists, and none is invented here," Part 5) — this is a ready-made, well-reasoned answer to a question current architecture deliberately left open, not a new idea being proposed for the first time.
**Where it belongs:** Beer Knowledge Base Architecture Part 5 (Source Attribution) or a future revision of it, and Catalog Builder Architecture Part 7 (Validation) as a new staleness-flag rule keyed by field type rather than one uniform rule.
**Implementation impact:** low-to-moderate — no new data field is strictly required (an `observed_at` timestamp already exists per fact, per Beer Knowledge Base Architecture Part 5), only a scheduling/reporting rule in the (not yet built) `enrichment_report.py` tool.
**Affects:** Beer Knowledge Base Architecture, Catalog Builder Architecture — a genuine candidate for a fresh Product Decision, since it changes founder workflow expectations, not just tooling.

### 4. Alias / synonym field, seeded from real observed misspellings and abbreviations
**Source documents:** `10-search-engine-design.md` §4 (the alias/synonym design in full); `04-catalog-acquisition-playbook.md` §6 ("Brand-name normalization gaps"); `research/catalog-sources/01-madhuloka...md` (the literal `"BUDWIESER TIN"` misspelling); `research/domain/04-open_dataset.md` (Bira 91 vs. Bira mismatch on Open Food Facts).
**Exact concept:** a small, curated table mapping known abbreviations, misspellings, and marketing aliases (`KF`/`King Fisher` → Kingfisher; `BUDWIESER` → Budweiser; `Bira`/`Bira91`/`Bira 91` → Bira 91) to a canonical entity, seeded directly from real scraped-data typos rather than invented ahead of time.
**Why it still matters:** this is not speculative — the exact misspelling `"BUDWIESER"` is sitting, verbatim, in real research data already gathered against the same retail landscape ValueBrew's own KSBCL pipeline draws from, and the Beer Knowledge Base's own Beer YAML schema (Beer Knowledge Base Architecture Part 3) has no field to record it at all today.
**Where it belongs:** Beer Knowledge Base Architecture Part 3, as a new optional `aliases` field on the Beer YAML schema. Whether it should also become a Catalog Contract 1.0 field (i.e., published into `catalog.json` for the app's own future search/matching use) is a separate, larger question gated behind Search/Browse Results itself having a Screen Contract at all (Product Decisions Register D2) — this recovery is scoped only to the *enrichment-side* recording of aliases, not to building search.
**Implementation impact:** low at the enrichment layer (one new optional list field, no join/computation impact); potentially significant if and when it's ever promoted into `catalog.json`, which this document does not propose.
**Affects:** Beer Knowledge Base Architecture directly; Catalog Contract 1.0 only if a future Product Decision extends it there; Product Decisions Register, as a candidate new entry for "should aliases become an app-facing field."

### 5. Taproom-only vs. actual retail availability, as an explicit validation rule
**Source documents:** `research/domain/01-brewery.md` (Arbor Brewing's own site: "Retailing only across Goa," despite a Bengaluru taproom); `research/catalog-sources/09-multi-source-simba...md` (the same Arbor finding, re-confirmed independently by the catalog-extraction pass); `04-catalog-acquisition-playbook.md` §6 (the explicit recommended schema fix: separate `has_bengaluru_taproom` and `retail_available_karnataka` booleans, plus a `channel` field).
**Exact concept:** a brewery having a confirmed Karnataka physical presence (a taproom, a brewpub) must never be treated as evidence that its packaged retail product is available in Karnataka — these are two independent facts, and the research caught a real, named brewery (Arbor) where they diverge, plus two more (Windmills Craftworks, Byg Brewski) that appear to have no packaged retail product in any state.
**Why it still matters:** ValueBrew's Product Definition is specifically about recommending *purchasable, packaged* beer — a beer enriched and published based only on "this brewery is Karnataka-based" without confirming actual retail availability would recommend something a person cannot actually buy, which is a direct, real product-quality failure mode, not a hypothetical one.
**Where it belongs:** Catalog Builder Architecture Part 7 (Validation), as a new rule; Beer Knowledge Base Architecture Part 3, as a candidate new field on the Beer YAML schema (a plain `retail_confirmed: bool` note, or simply a documented requirement that a beer's `canonical_product_ids` — which only ever come from `beer_master.csv`, a retail-price list by construction — already structurally guarantee this, since a brewpub-only beer would never appear there at all).
**Implementation impact:** potentially **zero new code** — worth stating precisely, since this may already be structurally solved rather than genuinely missing: every `canonical_product_id` a Beer YAML file can reference comes from KSBCL's own retail price list, which a taproom-only beer with no packaged SKU would never appear in to begin with. The real, live risk this research actually points at is narrower than the general principle: a founder manually enriching a beer by researching its *brewery* first (rather than starting from a real `beer_master.csv` row) could be tempted to assume Karnataka retail availability from a taproom's existence — a workflow discipline question, not a schema gap.
**Affects:** Catalog Enrichment Playbook (a new explicit caution in the research workflow), Catalog Builder Architecture (confirm, don't newly invent, that this is already structurally guarded).

---

## Part 5 — Contradictions (Category E), Documented Not Resolved

**1. Verification strictness: two-source gate vs. one-good-source.** The Enterprise Research's acquisition playbook (`04-catalog-acquisition-playbook.md` §3) states plainly that "no single-source fact (price, ABV, size, brewery) should reach a 'Verified' state" and that a single-source ABV/style must be published labeled "Single-source, unverified" until a second source corroborates it. The Catalog Enrichment Playbook (Part 4, this session) states the opposite operating instruction: "you do not need two sources to agree before you can record a fact... the moment you have one real, citable source" is the point to stop researching and move on. These are genuinely different philosophies, not a wording difference — the research optimizes for defensive, corroborated confidence at real operational cost; the current Playbook optimizes for founder throughput at one-person scale, accepting single-source Curated facts as sufficient once properly cited. **Not resolved here.** Both are internally coherent; which one governs going forward is a real, live product/process decision this document does not make.

**2. The catalog's own price field: "doesn't exist" vs. actually exists, in the sibling file.** Gap Analysis (`09-gap-analysis.md` §0) states as its headline structural finding that the extraction schema "has no field for actual ₹ price (only a `price_count` tally of how many price observations existed — never the number itself)." Direct inspection of `karnataka-beer-catalog.csv` for this reconciliation found this to be **only true of the JSON form** — the CSV has two clean, populated numeric columns, `karnataka_price_min` and `karnataka_price_max` (e.g., `110.0, 110.0` for Kingfisher Premium), entirely absent from Gap Analysis's own characterization. This is an internal inconsistency inside the Enterprise Research corpus itself, between one deliverable's stated finding and another deliverable's actual data. **Not resolved here** — noted because it means Gap Analysis's own "Fix" recommendation (re-scrape specifically to add a numeric price field) was already partially moot at the moment it was written, for the CSV if not the JSON.

**3. KSBCL's site: "no SKU-level price pages found" vs. 17 real priced SKUs successfully extracted from it.** `research/domain/06-scraping_feasibility.md` concludes KSBCL's site exposes "duty slabs" in PDFs but found no SKU/price listing page. The independent catalog-extraction pass (`research/catalog-sources/00-karnataka-state-beverages...md`) *did* successfully locate and parse KSBCL's real "Supplier-wise Item-wise Price List" PDF and extracted 17 real, priced SKUs from it. This contradiction is already self-acknowledged inside the corpus itself (`11-founder-execution-plan.md` §1 calls it out directly as the single highest-priority thing to re-investigate). **This document does not re-resolve it either — but notes that it has been operationally superseded, not by any document, but by the fact that `tool/ksbcl_pricing_pipeline/` (this session's own, later, independent work) now successfully parses this exact PDF in full, monthly, at production scale.** The original contradiction stands as a historical curiosity; the underlying question it raised has a real, working answer elsewhere in this repository now.

---

## Part 6 — Answer to the Governing Question

**"Is there any durable knowledge from the Enterprise Research corpus that deserves to become part of the production architecture?"**

Yes, five specific, narrow things — no more, no less, all detailed in full in Part 4: a new-SKU discovery signal (UBL SEBI filings) currently unused by Catalog Builder Architecture's own discovery stage; a specific brand-catalog cross-referencing technique with an origin-mismatch veto rule, missing from the Catalog Enrichment Playbook's research workflow; a field-specific re-verification cadence, answering a question Beer Knowledge Base Architecture deliberately left open; an alias/synonym field for the Beer YAML schema, justified by a real, verbatim misspelling already sitting in this repository's own research data; and an explicit taproom-vs-retail validation discipline, which on close inspection may already be structurally guaranteed rather than genuinely missing.

Everything else of real substance in the corpus — the source-tier hierarchy, the contract-brewing evidence, the ABV/GTIN sourcing conclusions, the image-licensing discipline, the general enrichment-workflow shape — was already fully absorbed, in most cases explicitly credited by name in the documents that absorbed it. The one large body of unabsorbed work, the national-scale Postgres-plus-OpenSearch production schema and its search-engine design, was not overlooked; it was weighed and deliberately deferred, on the record, more than once, as the correct answer only for a scale and a Product Decision (D19, and a hypothetical future Search/Browse Screen Contract) that don't exist yet. And one piece of it — the numeric confidence-scoring formula — should never be recovered under any circumstance, because it isn't merely unabsorbed, it's incompatible with a rule the rest of this architecture treats as inviolable.

Three genuine contradictions were found and are recorded, not resolved: a real disagreement about how strict source verification should be, an internal inconsistency inside the research corpus's own two catalog-deliverable formats, and an internal inconsistency about KSBCL's own scrapability that has since been operationally settled by later, independent work in this same repository.
