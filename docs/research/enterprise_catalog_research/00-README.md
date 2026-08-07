# ValueBrew — Karnataka Beer Master Database: Research & Acquisition Program

**Session date:** 2026-08-05
**Status:** Phase 1 complete (strategy + first-pass live catalog extraction). NOT the final 500–1,000 SKU catalog — see honest gap accounting below.

---

## ⚠️ Important correction to the original brief

The brief for this project stated "I have attached a document describing product vision, architecture, licensing decisions..." and instructed me to treat it as the governing document. **No such document was actually received in this session.** I did not fabricate a reconciliation against it. Everything here is my own recommended architecture and strategy, built from live research. If that document exists, share it in a follow-up session and I'll run a reconciliation pass against these deliverables.

---

## What actually happened this session

I ran a 28-agent orchestrated workflow (0 agent errors) in three phases:

1. **Domain research** (7 parallel agents) — government sources, brewery intelligence, retail intelligence, barcode/GTIN sources, open datasets, import/trade intelligence, scraping feasibility.
2. **Live catalog extraction** (12 parallel agents) — actually fetched real Karnataka government/retail/brewery sites and extracted real SKU records, under a strict no-fabrication rule (omit/blank rather than guess).
3. **Synthesis** (9 parallel agents) — schema, search design, acquisition strategy, playbook, brewery/brand list, automation roadmap, risk register, gap analysis, founder plan — each grounded only in the actual findings from phases 1–2.

**Headline result: 222 raw SKU records extracted live → deduplicated to 216 merged Karnataka beer SKUs**, of which:
- **126 (58%)** have at least one Karnataka price observation
- **82 (38%)** are High confidence, 105 Medium, 29 Low
- **11** have a GTIN captured
- Sourced from **50 distinct brands**

This is short of the 500–1,000 SKU target — **that target was not achievable for real, verified data in a single research session**, and I did not pad the numbers to get there. See "Path to 500–1,000" below.

### The most important find: KSBCL's real price list

The government catalog-extraction agent found and verified the actual **Karnataka State Beverages Corporation Limited supplier-wise item-wise price list** — a genuine 750-page, 15.5MB PDF at `https://ksbcl.karnataka.gov.in/uploads/supplier%20wise%20item%20wise%20pricing%20details%20as%20on%2030_1784703781.pdf`, linked from the real government homepage `ksbcl.karnataka.gov.in`. It contains official MRP, declared price, landed cost, and KSBCL selling price for every registered beer SKU in Karnataka, with supplier/brewery codes, item codes, and effective dates. Only 17 rows were transcribed this session (a demonstration sample) — **the full 750 pages have not yet been parsed**. This is the single highest-leverage next action (see Gap Analysis and Playbook).

Separately, the **domain-research agent tasked with surveying government sources broadly (Agent 1's mandate) returned an empty placeholder result** — a real failure, not zero findings. It should be re-run. The KSBCL discovery above came from the independent catalog-extraction agent, not from that survey.

### Confirmed dead ends (documented, not fabricated)
- **Living Liquidz** — site returns HTTP 503 "under maintenance" (Microsoft-IIS, Retry-After 3600), confirmed on repeated fetches. Historical data pulled from Wayback Machine archive instead (10 SKUs, lower confidence).
- **Tonique** — real physical retail chain, confirmed via independent LBB.in corroboration, but has **no browsable online SKU catalogue** — only a marketing landing page. Zero SKUs reported, as instructed.
- **Booozie.com** — domain parked/for sale via GoDaddy. Dead.
- **Talli Drinks, Beer Basket** — found via search, but explicitly serve Mumbai/Thane and non-Karnataka states respectively per their own footers (Beer Basket's "Bengaluru" URL slug contradicts its own delivery-area footer, which excludes Karnataka). Documented as false leads for future scrapers to avoid.
- **Bira91.com** — official domain resolved to a broken/parked Apache default page at time of check; data instead sourced from Wayback Machine archives (lower confidence) and the KSBCL price list (high confidence, since Bira91 is a registered KSBCL supplier).

---

## File index

| File | Deliverable | Contents |
|---|---|---|
| `01-master-source-matrix.md` / `.csv` | Deliverable 1 | Every source discovered across all 7 domain-research tracks + 12 live catalog-extraction sources (89 rows total), with coverage/confidence/recommendation |
| `02-catalog-acquisition-strategy.md` | Deliverable 2 | Which sources to use, in what priority order, and why |
| `03-production-database-schema.md` | Deliverable 3 | Normalized schema for 50,000+ SKUs, entity resolution, provenance/confidence design |
| `04-catalog-acquisition-playbook.md` | Deliverable 4 | Step-by-step operational handbook |
| `05-top-karnataka-breweries-brands.md` | Deliverable 5 | Every major brewery/brand with Karnataka-availability confidence |
| `karnataka-beer-catalog.csv` / `.json` | Deliverable 6 | **216 verified Karnataka beer SKUs** (the initial catalog — see caveats above) |
| `07-automation-roadmap.md` | Deliverable 7 | Manual / semi-automated / fully-automated categorization per source |
| `08-risk-register.md` | Deliverable 8 | Licensing, scraping, legal, dependency, maintenance risks |
| `09-gap-analysis.md` | Deliverable 9 | Every field/source that couldn't be verified this session + how to close it |
| `10-search-engine-design.md` | (supports Deliverable 3) | Autocomplete, fuzzy/phonetic search, alias design |
| `11-founder-execution-plan.md` | (Agent 10 brief) | Operational plan: hours, throughput, manpower, partnerships |
| `research/domain/*.md` | raw domain-research agent outputs (7 files) | Full source-by-source detail behind the matrix |
| `research/catalog-sources/*.md` | raw catalog-extraction agent outputs (12 files) | Pre-dedupe SKU records with full access notes/provenance per source, before merge |

---

## Known data-quality issue to fix before this catalog is used in production

Brand names in the merged CSV are **not yet normalized** — e.g. `Bira`, `Bira 91`, and `Carlsberg` vs `Carlsberg (Tuborg)` appear as distinct brand strings, and a few rows have inference commentary baked directly into the `brand` field (e.g. `"Kingfisher (brand field on record is blank; inferred from product_name text 'Kingfisher ultra')"`). This happened because the merge step deliberately preserved each source agent's raw field values with zero LLM rewriting (to avoid silently distorting data) — the entity-resolution/canonicalization step described in the DB schema (Deliverable 3) has **not yet been run** against this data. Treat `karnataka-beer-catalog.csv` as a pre-canonicalization staging table, not the production `brand` table.

---

## Path to 500–1,000 verified SKUs

The single biggest unlock is **parsing the full 750-page KSBCL PDF** already downloaded this session — it alone likely contains several hundred registered beer SKUs with official MRP. That is a mechanical, well-scoped follow-up task (chunk the PDF, run structured extraction per chunk, validate row counts against the page count) and should be the very next session's top priority — details in `04-catalog-acquisition-playbook.md` and `09-gap-analysis.md`.
