# Architecture Reconciliation Report — Enterprise Catalog Research

*Every file in `docs/research/enterprise_catalog_research/` read directly (18 subdirectory research files, plus the 12 top-level synthesis documents already fully absorbed earlier in this project's Project Brain construction, plus a direct re-verification of `karnataka-beer-catalog.json`'s actual schema and field population). Compared against the full canonical set: Project Brain, Product Definition, The ValueBrew Experience, Beer Knowledge Model 2.0, Decision Engine 2.0, Domain Model 1.0, Catalog Specification 1.0, Interaction Model 2.0, Conversation Model 1.0, Beer Entity Specification 1.0, the 20-document Canonical Architecture, the Flutter implementation, the KSBCL pipeline, and Evolution of ValueBrew. No new architecture proposed here — only classification.*

---

## Category A — Already Fully Represented (the overwhelming majority)

The bulk of this research corpus is already fully absorbed into the canonical set, most directly into Beer Knowledge Model 2.0's Composition/Economic/External-Identifier domains and Catalog Specification 1.0. Confirmed, not re-derived:

- No automated source exists anywhere for ABV — confirmed independently across every brewery, retailer, and open-dataset file read.
- Madhuloka is the strongest retail source; Living Liquidz is down; Tonique is stale (April 2023) with a leftover placeholder phrase; Bira91.com's official domain is broken (serves an unrelated site with a mismatched TLS certificate); corporate brand sites are marketing pages behind age-gates, not pricing sources.
- No public authoritative Indian GTIN lookup exists; GS1 India's DataKart has no public API; UPCitemdb had zero coverage on tested Indian beer barcodes; Go-UPC's terms explicitly prohibit redistribution; Open Food Facts is the only free, commercially-reusable, verified source with real Indian beer GTINs (confirmed again directly in this pass: Kingfisher 8905002180007, Tuborg Strong 8906018940104, Bira "Boom" 8908005126324, Budweiser variants).
- Volza, DGCI&S, Section 135AA, and Zauba's staleness — the entire import-market legal-risk picture — confirmed unchanged.
- Karnataka Excise Department's site was unreachable (DNS failure); data.gov.in returned zero relevant datasets; the Kerala BEVCO Kaggle dataset remains the only comparable government-sourced structural template, for the wrong state.
- Arbor Brewing's Goa-only retail vs. Bangalore taproom-only distinction, and STOK's 7%/8% ABV self-contradiction — both re-confirmed, both already load-bearing examples throughout the canonical set.
- I directly re-verified `karnataka-beer-catalog.json` itself: 216 items, schema does include `abv`, `gtin`, `calories`, and `karnataka_price_observations` fields, with ABV populated for only 28 of 216 (≈13%) and GTIN for 11 of 216 (≈5%) — this is the exact severity already reflected in Catalog Specification 1.0's launch-gating rule for ABV.

None of this changes any existing document. It confirms them.

---

## Category B — Same Idea, Better Explained

- **Onlinealcohol.in's WooCommerce Store API** is described here with more technical precision (exact endpoint shapes, `X-WP-Total` headers, verified live JSON) than anywhere in the canonical set, which already correctly identifies it as the best-structured secondary source. The underlying conclusion is unchanged; the research corpus simply documents *why* more concretely than my own synthesis needed to at the time.
- **Livcheers' explicit bot-blocklist** (named bots: SemrushBot, AhrefsBot, MJ12bot, GPTBot, Bytespider, CensysInspect) is more specific than the "explicit no-scrape policy" framing already used throughout the canonical set — same conclusion, sharper evidence for it.

Neither changes any document's content, only strengthens citations already made.

---

## Category C — Genuinely New Knowledge, Should Probably Become Canonical

### C1. United Breweries' SEBI Regulation 30 filings as a structured Karnataka-specific data source
**What it is:** UBL's investor-relations PDFs (regulatory disclosures of new product launches) give exact Karnataka launch dates, product categories, and — in the Kingfisher Smooth case — complete per-SKU Karnataka retail pricing across four package sizes, directly fetched and text-extracted from `unitedbreweries.com/pdf/Material Events/`.
**Where it came from:** `research/domain/01-brewery.md`.
**Why it matters:** this is a source class not cited anywhere in the current canonical set — official, structured, machine-readable, and specifically Karnataka-scoped, distinct from both KSBCL and retail scraping. It's a genuinely new option for sourcing Economic and Availability knowledge for at least one major brewer.
**Which documents it would affect:** Catalog Specification 1.0 (Economic Knowledge's source-of-truth options), Beer Knowledge Model 2.0.
**Decision type:** Documentation update to add as a cited future source. Becomes an Engineering Decision only if a future enrichment pass is actually built against it.

### C2. Concrete evidence of real brewery-vs-supplier divergence (contract brewing)
**What it is:** KSBCL's own supplier register lists "Budweiser Premium King Of Beers" and "Budweiser Magnum Beer" under Supplier Code 0212 — S P R Distilleries Pvt Ltd, explicitly noted as "AB InBev brand under contract bottler," and Guinness under Supplier Code 0972 via Brindco Enterprises, an importer, not a brewery at all.
**Where it came from:** `research/catalog-sources/00-...ksbcl-official.md`.
**Why it matters:** this directly bears on the KSBCL Stage 4 Identity Decision's own named, previously *unconfirmed* business premise — whether differently-supplied listings of the same name reflect genuine contract-brewing arrangements. This is real, concrete evidence the premise holds at least sometimes; it does not resolve the deeper interpretive question (what a price spread across such suppliers actually means), but it moves "unconfirmed assumption" toward "confirmed to occur in at least two real cases."
**Which documents it would affect:** Catalog Specification 1.0's Brewery domain (already carries a caveat about this exact distinction, currently unevidenced — this makes it evidenced), Beer Entity Specification 1.0's Brewery attribute, and potentially the KSBCL Stage 4 product-design documents themselves (outside this reconciliation's direct authorship scope, but worth flagging to whoever owns that document set).
**Decision type:** A **Product Decision** if it changes how "Brewery" should ever be displayed to a user (e.g., distinguishing "brewed by" from "supplied by" in copy) — the Conversation Model currently has no rule for this distinction at all. Otherwise, a documentation update.

### C3. GS1 India's exact, current GTIN registration fee structure
**What it is:** real, tiered fees directly read from GS1 India's own current fee-structure PDF — e.g., ₹48,135 total for the smallest package (100 barcodes, 1 year, turnover ≤₹5 crore) up to ₹324,146 for the largest (100,000 barcodes, 10 years, turnover >₹1000 crore).
**Where it came from:** `research/domain/03-barcode.md`.
**Why it matters:** the canonical set only ever discussed GTIN *lookup* (finding existing barcodes). This is the first concrete pricing for the opposite direction — ValueBrew *registering* its own GTINs — a strategic option not previously priced anywhere.
**Which documents it would affect:** Catalog Specification 1.0's External Identifier domain, the V2 Enrichment Roadmap.
**Decision type:** Currently hypothetical — no action needed unless a future Product Decision considers ValueBrew becoming a GTIN registrant, which nothing today suggests is planned.

### C4. "Murphy's" brand disambiguation
**What it is:** the Irish Stout brand "Murphy's" (Heineken-owned, UK/Ireland-focused) has no confirmed India presence; nearly all India search results for "Murphy's" actually resolve to "Murphy's Brewhouse," an unrelated Bengaluru bar/brewpub venue.
**Where it came from:** `research/domain/01-brewery.md`.
**Why it matters:** small but concrete — prevents a real, specific misattribution if this name is ever added to the catalog.
**Which documents it would affect:** Catalog Specification 1.0's Identity domain, as a disambiguation note.
**Decision type:** Documentation only.

### C5. KSBCL's exact, current, real PDF source URL
**What it is:** the literal, verified URL for the official Karnataka price list PDF (`ksbcl.karnataka.gov.in/uploads/supplier%20wise%20item%20wise%20pricing%20details%20as%20on%2030_1784703781.pdf`), confirmed via direct government-site navigation, not inferred.
**Where it came from:** `research/catalog-sources/00-...ksbcl-official.md`.
**Why it matters:** none of the KSBCL pipeline architecture documents I've extracted give this literal URL — they describe Stage 1's extraction process generically. This is a concrete, independently-obtained access path.
**Which documents it would affect:** Catalog Specification 1.0's Legal Price source-of-truth citation; the KSBCL pipeline's own documentation (outside this report's authorship scope).
**Decision type:** Documentation update — should first be cross-checked against what `tool/ksbcl_pricing_pipeline/` actually fetches today, which this reconciliation pass did not directly verify.

### C6. Minor additional import-data leads: ImportGenius and TRADESTAT
**What it is:** ImportGenius (a $199 entry-price India trade-data product, coverage unverified) and TRADESTAT (a free, official Government of India aggregate trade-statistics portal), named as alternatives to Volza/DGCI&S/Zauba.
**Where it came from:** `research/domain/05-import_market.md`.
**Why it matters:** minor, low-confidence, but genuinely not cited anywhere in the current canonical set.
**Which documents it would affect:** Catalog Specification 1.0's Future Expansion section on import-brand detection.
**Decision type:** Documentation only, low priority — neither has been independently verified even by this research corpus's own account.

---

## Category D — Contradicts Existing Material

**D1. An internal contradiction inside the research corpus itself, not a contradiction with canonical ValueBrew architecture.** `09-gap-analysis.md` (already read and reconciled earlier in this project) claims the catalog schema has no ABV/GTIN/price fields at all. Directly re-verifying `karnataka-beer-catalog.json` in this pass confirms the opposite: the schema *does* carry `abv`, `gtin`, `calories`, and `karnataka_price_observations` fields — they are simply sparsely populated (ABV on 28 of 216 items, GTIN on 11). This does not contradict Beer Knowledge Model 2.0 or Catalog Specification 1.0, both of which already correctly treated ABV as the critical, thin-coverage gap without relying on the incorrect "no field exists" framing — it only confirms that the gap-analysis document's own specific claim about the schema's shape was wrong, and that Project Brain's earlier flag of this inconsistency was correct to leave standing rather than silently resolve.

---

## Category E — Historical Only, Preserve for Context, Do Not Adopt

Nearly every environment-specific technical detail in the retail and scraping-feasibility research — specific Cloudflare header signatures, exact curl commands, DNS resolution quirks observed on 2026-08-05, the precise HTTP status codes returned by each site on that date — is a time-bound snapshot of research process, not durable product knowledge. It's valuable as a record of *how* the corpus was produced and *what was true on that date*, and should stay exactly where it is (in the research files themselves), but none of it belongs promoted into a canonical document, since every one of these facts is expected to drift (a site coming back online, a Cloudflare rule changing, a domain being reconfigured). The one exception already promoted: the *durable conclusions* drawn from this research (no ABV source exists, no GTIN source exists, Madhuloka is the strongest retail source) are already Category A, not E — it's specifically the moment-by-moment verification trail that stays historical.

---

## Summary

The reconciliation confirms: **this research corpus was already thoroughly absorbed** into the canonical set during the original Project Brain construction and Beer Knowledge Model 2.0/Catalog Specification 1.0 authorship — nothing here requires reopening or rewriting anything already built. Six genuinely new items surfaced (C1–C6), of which only two carry real near-term weight: **C2 (concrete contract-brewing evidence)**, which sharpens an already-flagged caveat with real proof rather than assumption, and **C1 (SEBI filings as a new source class)**, which adds a genuinely new sourcing option not previously on record. The rest are minor, low-priority, or purely documentary. One internal inconsistency in the source material itself was reconfirmed (D1), with no impact on canonical architecture.

Nothing found here answers, on its own, what the next canonical document ought to be — that decision, per your instruction, comes next.
