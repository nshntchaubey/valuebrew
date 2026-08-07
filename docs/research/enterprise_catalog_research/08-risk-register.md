# Deliverable 8 — Risk Register

# Deliverable 8: Risk Register — ValueBrew Karnataka Beer Database

Grounded in the six domain research passes and the 216-SKU extraction run. Ratings are Likelihood/Impact on a Low/Medium/High scale, assessed as of 2026-08-05.

## Summary Table

| # | Risk | Category | Likelihood | Impact | Owner action |
|---|------|----------|------------|--------|---------------|
| 1 | Go-UPC/commercial barcode data redistributed in violation of ToS | Licensing | Medium | High | Do not build resellable DB on Go-UPC data |
| 2 | OFF data reused without attribution/share-alike compliance | Licensing | Low | Medium | Add attribution + ODbL notice |
| 3 | GS1 DataKart terms undisclosed, could restrict resale | Licensing | Medium | Medium | Get terms in writing before relying on it |
| 4 | Scraping importer-identity trade data violates Customs Act §135AA | Scraping/Legal | Low-Medium | High (criminal) | Avoid identity-level import data entirely |
| 5 | Corporate/retailer ToS breach or bot-block escalation (UBL Cloudflare, Livcheers explicit bot-block) | Scraping/Legal | Medium | Medium | Respect robots.txt; no automation against Livcheers |
| 6 | Single-vendor dependency on KSBCL PDFs/DGCI&S for regulatory pricing/duty data | Gov-source dependency | High | Medium | Treat as supplementary, not real-time feed |
| 7 | Karnataka Excise Dept. site unreachable — no official state dataset available | Gov-source dependency | High (confirmed now) | Medium | Manual periodic check; no automation dependency |
| 8 | No public GTIN lookup exists for India; barcode coverage is sparse and inconsistent | GS1/barcode | High (confirmed) | Medium | Treat barcodes as enrichment, not join key |
| 9 | Commercial lookup APIs have near-zero India-beer coverage (UPCitemdb 0/4) | GS1/barcode | High (confirmed) | Low-Medium | Don't budget for UPCitemdb; pilot Go-UPC narrowly |
| 10 | Core retail source outages/breakage (Living Liquidz down, Bira91.com broken, Zauba stale, Beerbasket API 500s) | Retailer dependency | High (confirmed) | High | Multi-source redundancy; no single point of failure |
| 11 | Retailer sites explicitly block automated collection (Livcheers robots.txt) | Retailer dependency | High (confirmed) | Medium | Respect the block; don't scrape Livcheers |
| 12 | Catalog drift / staleness with no lastmod signals anywhere | Maintenance | High | Medium | Build re-crawl cadence + diffing, not one-time pull |
| 13 | Brand/SKU naming inconsistency breaks matching/dedup logic | Maintenance | High (confirmed) | Medium | Canonical brand-name mapping table, human-reviewed |
| 14 | Internal source contradictions (ABV, style) undermine "authoritative" claim | Maintenance | Medium | High (core value prop) | Confidence-tiering + flag conflicts, don't silently pick one |

---

## 1. Licensing Risks

### 1.1 Go-UPC data redistribution would breach vendor ToS
- **Evidence:** Go-UPC's Terms and Conditions (fetched 19 Mar 2025 version) "explicitly PROHIBITS reselling, redistributing, or making the Service or Product Data publicly available" — yet Go-UPC is the *only* commercial lookup API that showed real coverage of Indian beer GTINs (4 of 5 test barcodes matched, vs. 0 of 4 for UPCitemdb).
- **Likelihood:** Medium — this only bites if/when ValueBrew actually pulls barcode enrichment from Go-UPC into a product that's shown to customers or resold as a dataset.
- **Impact:** High — a B2B data product's core asset (its database) built partly on data it's contractually forbidden to republish is an existential legal/IP risk, not a nuisance.
- **Mitigation:** Never treat Go-UPC as a source of *record* for barcodes in a published catalog. If used, use only for internal QA/spot-checking of self-sourced GTINs, and get explicit written confirmation from Go-UPC about redistribution rights before any commercial use.

### 1.2 Open Food Facts reuse without honoring ODbL/DBCL/CC-BY-SA terms
- **Evidence:** OFF confirmed real Indian beer records (Kingfisher 8905002180007, Bira "Boom" 8908005126324, Tuborg, Budweiser India, Coolberg) under ODbL (structure) + DBCL (contents) + CC BY-SA (images) — commercial use is explicitly permitted but requires attribution and share-alike treatment of derivative *databases* (not necessarily the whole product, but this needs a lawyer's read given ODbL's "derivative database" definition).
- **Likelihood:** Low that this becomes a real dispute (OFF is a nonprofit, unlikely to enforce aggressively) but easy to get wrong by omission.
- **Impact:** Medium — reputational/legal exposure if ValueBrew's product visibly incorporates OFF fields without the required notice, and a share-alike obligation could force ValueBrew to open-source portions of its own database it didn't intend to.
- **Mitigation:** Maintain a clear provenance tag per field (e.g., `source: OFF`, `license: ODbL-1.0`) in the schema from day one; publish attribution; get IP counsel to confirm whether ValueBrew's *combined* database (proprietary scrape + OFF fields) triggers ODbL's share-alike clause or stays clear of it (this is a real open legal question the research did not resolve).

### 1.3 GS1 India DataKart commercial-access terms are undisclosed
- **Evidence:** DataKart (GS1 India's own repository, synced to GS1 Cloud) is the closest thing to an "official" Indian GTIN database, but "no public API documented... third-party commercial access requires contacting GS1 India directly... pricing not published."
- **Likelihood:** Medium — if ValueBrew pursues this channel it will hit an opaque negotiation, not a self-serve signup.
- **Impact:** Medium — could block or delay a planned data pipeline, or come with resale restrictions ValueBrew doesn't discover until after integration work is sunk.
- **Mitigation:** Contact GS1 India (registration@gs1india.org / implementation@gs1india.org) early and in writing to get DataKart-for-Solution-Providers pricing and resale terms *before* architecting anything around it.

---

## 2. Scraping / ToS / Legal Risks

### 2.1 Importer-identity trade data (Section 135AA, Customs Act 1962) — the sharpest legal risk found
- **Evidence:** Section 135AA (added 2022, per secondary-source summaries — the *primary statutory text could not be directly verified*: indiacode.nic.in returned 403, three other candidate URLs 404'd/access-denied) reportedly criminalizes unauthorized publication of importer/exporter transaction-level trade data including identity. Volza's free-tier India-beer page already surfaces brand-identifiable shipment data (Tusker/Kenya Breweries, Saigon Export, Cheetah, Camel, Abest) which is exactly the category of data this section may restrict if resold with identity attached.
- **Likelihood:** Low-Medium for ValueBrew specifically today (it's not currently building an import-tracking feature), but rises to High the moment "detect new imported brands entering Karnataka" becomes a roadmap item.
- **Impact:** High — this is a criminal statute, not a civil ToS matter; the downside is not "lose a data source," it's regulatory/criminal exposure for the company.
- **Mitigation:** Do not build any feature that republishes importer/exporter *identity* tied to shipment records sourced outside Central-Government-authorized channels. Before touching Volza (or any bill-of-lading aggregator) for this use case, get an Indian legal opinion on (a) the actual current text of §135AA and (b) whether bill-of-lading-sourced resale (Volza's likely data pathway) is legally distinct from DGCI&S customs-declaration data. Treat DGCI&S's own aggregate (non-identity) statistics as the only legally clean substitute for trend-level "is beer import volume growing" questions.

### 2.2 Explicit anti-scraping postures on named retail sites
- **Evidence:** Livcheers.com's robots.txt "explicitly disallows /api/... and fully blocks a long list of named SEO/scraping bots (SemrushBot, AhrefsBot, MJ12bot, GPTBot, Bytespider, CensysInspect, etc.)" — "a clear, explicit signal that this operator does not want automated crawling of any kind." United Breweries is Cloudflare-fronted with `__cf_bm`/`_cfuvid` bot-management cookies present (no active challenge observed yet, but the tooling is live).
- **Likelihood:** Medium — easy to violate accidentally if a generic crawler is pointed at "all Karnataka liquor retailers" without per-site policy review.
- **Impact:** Medium — IP bans, escalating Cloudflare challenges, and reputational/commercial risk if a retailer notices and objects publicly (bad for a startup trying to be seen as the "authoritative," trustworthy database).
- **Mitigation:** Maintain a per-source robots.txt/ToS compliance ledger (already effectively started in the research — Madhuloka permissive, KSBCL permissive, Livcheers explicit no, UBL Cloudflare-monitored-but-not-blocking). Hard-exclude Livcheers from any automated pipeline. Rate-limit UBL/Carlsberg fetches (Carlsberg's own robots.txt specifies `Crawl-delay: 10`) and monitor for challenge pages appearing over time — build a kill-switch, not just a "keep retrying" scraper.

### 2.3 No ToS review performed on corporate brand sites (UBL, Carlsberg, Heineken, AB InBev)
- **Evidence:** Research report explicitly flags: "Corporate brand sites... may not legally intend their marketing content to be scraped for a commercial product database — no ToS review was performed."
- **Likelihood:** Medium.
- **Impact:** Medium — these are large multinationals (Heineken, AB InBev) with legal departments; a cease-and-desist is a plausible, if not severe, outcome, and could sour a future distribution/partnership conversation.
- **Mitigation:** Get an actual ToS review done for the four corporate domains before scaling automation beyond spot-checks; prefer their official regulatory filings (UBL's SEBI Reg-30 PDFs are public disclosure documents, a much safer legal basis than scraping marketing pages) as the primary structured source for those brands.

---

## 3. Government-Source Dependency Risk

### 3.1 KSBCL is the backbone of the current price/SKU dataset but is PDF/portal-based and unautomatable at scale
- **Evidence:** KSBCL is the single largest confidence-"High" contributor in the 216-SKU catalog (all the Supplier-Code-tagged rows). Yet the broader scraping-feasibility report found KSBCL's real site (ksbcl.karnataka.gov.in) exposes duty/price data mainly "inside linked PDFs, requiring pdfplumber-style parsing," with ERP/OFS login portals and supplier-list sections left unexplored.
- **Likelihood:** High that this remains a manual/semi-manual, brittle pipeline rather than a clean automated feed.
- **Impact:** Medium — it's ValueBrew's most authoritative government source, so breakage here directly undermines the "most authoritative Karnataka beer database" positioning, but the impact is degraded freshness, not total data loss (other sources partially overlap).
- **Mitigation:** Build a dedicated PDF-parsing job with schema validation and a human QA step, not a generic HTML scraper. Explore the unexplored ERP/OFS/supplier-list sections directly with KSBCL (a government-to-startup outreach may get a cleaner data-sharing arrangement than scraping).

### 3.2 DGCI&S explicitly cannot supply the identity-level data ValueBrew would want for import tracking
- **Evidence:** DGCI&S's own FAQ states aggregate country×commodity data is sold to private users, but "Transaction level details with the name, address of exporter/importer... are NOT provided for private use" — full stop, by official policy.
- **Likelihood:** High (this is a confirmed, permanent policy constraint, not a probabilistic risk).
- **Impact:** Medium — closes off the "legally cleanest" path to brand-level import intelligence, pushing ValueBrew toward the riskier Volza/§135AA territory in section 2.1 if it wants that feature at all.
- **Mitigation:** Scope any import-tracking feature down to aggregate volume/trend reporting only (which DGCI&S *can* legally supply), and treat brand-level "who's importing what" as a Phase-2+ feature gated on a legal opinion, not a Phase-1 deliverable.

### 3.3 Karnataka's own excise department site is currently unreachable
- **Evidence:** "excise.karnataka.gov.in could not be reached — DNS resolution failed from this sandbox." Could not confirm whether Karnataka publishes anything like Kerala's BEVCO price list.
- **Likelihood:** High this remains an open gap in the near term (unverified whether it's a transient network issue or the site being genuinely down/nonexistent).
- **Impact:** Medium — Karnataka has no confirmed public government price-list equivalent to Kerala's BEVCO dataset (found on Kaggle, CC0), so ValueBrew cannot currently lean on a state-published open dataset the way a Kerala-focused competitor could.
- **Mitigation:** Re-attempt access from a different network/VPN; if genuinely unreachable, contact KSBCL/Karnataka Excise directly to ask whether an equivalent price circular exists in a different format (physical circular, RTI request, etc.) rather than assuming absence.

### 3.4 data.gov.in has zero relevant datasets
- **Evidence:** Searches for "beer," "alcohol," "liquor," "excise," and "Karnataka excise" all returned literal "No Result."
- **Likelihood:** High (confirmed, not speculative).
- **Impact:** Low — this just means one candidate source is a dead end; doesn't change the plan, just removes an option.
- **Mitigation:** Don't allocate engineering time to monitoring data.gov.in for this vertical; periodically re-check only opportunistically (e.g., quarterly), not as a maintained pipeline.

---

## 4. GS1/Barcode Limitations

### 4.1 No public, authoritative GTIN lookup exists for India at all
- **Evidence:** GS1 India's GTIN Validation service is a single-barcode web widget plus an email-based bulk process for DataKart subscribers — "not a documented REST API." No brewery's own official site (UBL, Heineken, Carlsberg, AB InBev, Bira91, Simba, Geist, Toit, STOK, etc.) was found to publish GTIN/UPC/barcode numbers anywhere — confirmed as "a consistent gap across the entire researched set."
- **Likelihood:** High — this is a structural, confirmed absence, not a probability.
- **Impact:** Medium — barcodes cannot be ValueBrew's primary SKU-matching/dedup key; the database has to key on brand+variant+size+brewer instead, which is inherently fuzzier (as the naming-inconsistency issues in the catalog — "BUDWIESER" misspelling, "Bira 91" vs "Bira," multiple size-less duplicate rows — already demonstrate).
- **Mitigation:** Design the schema so GTIN is an optional enrichment field, not the join key. Invest instead in a canonical brand/variant/size taxonomy with fuzzy-matching + human review for dedup, which the 216-SKU extraction already shows is necessary regardless (many rows have blank size/brewery and duplicate near-identical names).

### 4.2 Commercial barcode APIs have poor, inconsistent India-beer coverage
- **Evidence:** UPCitemdb returned zero matches on 4 confirmed real Indian beer GTINs despite claiming 718M+ global entries. Go-UPC matched 4/5 but (per 1.1) can't be redistributed. Barcode Lookup (barcodelookup.com) is completely unverifiable — blocked every fetch attempt with a bot-detection wall.
- **Likelihood:** High that any given commercial API will underperform expectations for this specific vertical.
- **Impact:** Low-Medium — mainly a wasted-spend risk if ValueBrew signs an annual contract assuming broad coverage.
- **Mitigation:** Do not commit to a paid annual plan (UPCitemdb DEV $99/mo, Go-UPC $74.95–795/mo) without first running a coverage pilot against a representative sample of the actual 216-SKU list, not just the 4-5 barcodes tested in this research pass.

### 4.3 No GS1/alcohol-specific regulatory linkage found — ambiguity on excise interplay
- **Evidence:** "No formal linkage or requirement connecting GS1 GTIN registration to state excise licensing" was found; this is described as "simply unaddressed publicly, not confirmed either way."
- **Likelihood:** Medium this creates confusion later (e.g., if ValueBrew tries to cross-reference GTINs against KSBCL supplier codes and assumes a relationship that doesn't exist).
- **Impact:** Low-Medium — a modeling/assumption risk more than a hard blocker.
- **Mitigation:** Treat GTIN and KSBCL Supplier Code as two independent identifier systems in the schema; do not build logic that assumes one implies or validates the other.

---

## 5. Retailer Dependency Risk

### 5.1 Confirmed outages/breakage across multiple named retail sources — no single retailer is reliable alone
- **Evidence, all directly verified this session:**
  - **Living Liquidz** — HTTP 503 "under maintenance" on every path (www and non-www), reproduced across repeated attempts.
  - **Bira91.com** — serves an unrelated Apache default page with a TLS cert for `*.ksmart.live`; the brand's real official web presence could not be confirmed at all (candidates `bira91.beer` / `stores.bira91taproom.com` found only via search, not verified).
  - **Zauba.com** — technically live but data is stale (sample records dated 2013/Nov-2016, footer "© 2021 Zauba.com").
  - **Beerbasket.in** — WooCommerce Store API products endpoint 500-errors consistently (3/3 attempts); only the categories endpoint works.
  - **Tonique.in** — single static HTML price table dated April 2023 in its own schema.org metadata, containing a leftover "Price list coming soon" placeholder phrase alongside real-looking prices.
- **Likelihood:** High — this is already realized, not speculative; roughly half of the retail sources evaluated are non-functional, stale, or partially broken *today*.
- **Impact:** High — if ValueBrew's pipeline architecture assumes any single one of these as a dependable feed, that assumption is already false; a "most authoritative" claim built on one retailer is fragile by construction.
- **Mitigation:** Explicitly design for source redundancy from day one: Madhuloka (best-verified, ~103 beer SKUs, permissive robots.txt, no anti-bot signals) as primary, KSBCL as the regulatory-price cross-check, Onlinealcohol.in's genuine WooCommerce Store API as a secondary structured cross-validation source (small but clean), and treat Living Liquidz/Zauba/Tonique/Beerbasket as "recheck periodically, don't build on" rather than active pipeline components. Re-verify Bira91's actual current domain via the brand's social media or a distributor before investing scraper effort there.

### 5.2 Livcheers explicitly signals it does not want to be scraped
- **Evidence:** (repeated from 2.2 for retailer-specific framing) robots.txt disallows `/api/` and blocks a long list of named bots; data is client-rendered Next.js with no product JSON visible in raw HTML.
- **Likelihood:** High (confirmed policy).
- **Impact:** Medium — removes one more retailer from the usable pool, reinforcing 5.1's concentration risk onto Madhuloka.
- **Mitigation:** Exclude entirely; do not attempt to reverse-engineer its API even though it's technically discoverable, given the explicit policy statement.

### 5.3 Concentration risk: Madhuloka alone contributes the largest share of retail SKU rows in the 216-SKU catalog
- **Evidence:** Cross-referencing the catalog summary, the large majority of retail-sourced rows (as opposed to brand-site or KSBCL rows) cite "Madhuloka" as the sole source, many at "Medium" confidence with blank size/brewery fields (e.g., "HEINEKEN TIN," "KNOCK OUT PINT," multiple duplicate near-identical rows with `price_count: 2` and no distinguishing size).
- **Likelihood:** High that a Madhuloka outage, redesign, or ToS change would materially degrade the catalog's freshness and completeness overnight.
- **Impact:** High, precisely because this is the best and most-relied-upon retail source — its loss isn't cushioned by an equally good backup today (Onlinealcohol.in's beer category is only 12 SKUs vs. Madhuloka's ~103).
- **Mitigation:** Actively diversify: pursue Onlinealcohol.in's API more deeply, re-test Beerbasket's categories-only endpoint periodically for a products-endpoint fix, and periodically re-check Living Liquidz — the goal being at least two independently-healthy retail sources at all times, not one primary plus a pile of broken fallbacks.

---

## 6. Ongoing Maintenance Risk

### 6.1 No freshness/lastmod signal exists on almost any source
- **Evidence:** Madhuloka's sitemap.xml shows a `<lastmod>` only on the contact-us page, none on product pages. KSBCL, Tonique, and most brand sites showed no reliable per-item update timestamps. OFF's per-product staleness is likewise unknown at the field level.
- **Likelihood:** High (confirmed, structural).
- **Impact:** Medium — ValueBrew cannot claim real-time accuracy without its own re-crawl-and-diff process; presenting scraped-once data as "live" would itself become a credibility risk for a company whose value proposition is authoritativeness.
- **Mitigation:** Build a scheduled re-crawl (e.g., weekly for Madhuloka/KSBCL, monthly for brand sites) with diffing against the prior snapshot, and store `last_verified_at` per field/source in the schema — make staleness visible internally and, where relevant, to customers, rather than implying real-time truth.

### 6.2 Catalog snapshot is explicitly point-in-time and will drift
- **Evidence:** The Karnataka/Bangalore retailer report states plainly: "Sitemap-derived counts... are point-in-time snapshots from this session's fetch and will drift as catalogues change."
- **Likelihood:** High.
- **Impact:** Medium.
- **Mitigation:** Same re-crawl cadence as 6.1; version the catalog (e.g., `catalog_version: 2026-08-05`) so any downstream consumer knows exactly which snapshot they're looking at.

### 6.3 Brand/SKU naming inconsistency will keep breaking automated dedup
- **Evidence, directly visible in the 216-SKU catalog itself:** "Bira 91" vs. "Bira" (OFF's brand tag is "Bira," not "Bira 91" — a confirmed naming/normalization gap); "BUDWIESER TIN" (site's own misspelling); many rows are literally the same product name with `price_count: 2` and blank size ("HEINEKEN SILVER" appears twice, "KNOCK OUT TIN" appears twice, "KF STRONG TIN" appears twice) — the extraction process itself could not always resolve whether these are true duplicates or distinct size variants.
- **Likelihood:** High — this is already observed in the current 216-row dataset, not a future risk.
- **Impact:** Medium — left unresolved, it inflates apparent SKU counts, undermines dedup logic, and would surface as visible "why do you have this beer listed twice with no size" errors to end users, which is reputationally costly for an "authoritative" database.
- **Mitigation:** Build and maintain a canonical brand/variant name-mapping table with human review for every new source ingested (not fully automatable given misspellings like "BUDWIESER" and brand-tag mismatches like Bira/Bira91); treat any SKU with blank size/brewery as "needs enrichment," not as a finished record.

### 6.4 Internal contradictions inside single "official" sources undermine confidence scoring
- **Evidence:** Mount Everest Breweries' own STOK product page lists STOK Strong at 7% ABV in its spec table but 8% ABV in its own FAQ on the *same page*. Carlsberg's India-branded "Carlsberg Smooth" may or may not be the same product as the global catalog's Malaysia-origin "Carlsberg Smooth Draught" (4.8% ABV) — flagged as unresolved. Bira91's official site itself could not be reached to verify current ABV values at all.
- **Likelihood:** Medium-High that more such contradictions surface as coverage expands beyond the ~6 domains researched so far.
- **Impact:** High relative to ValueBrew's core value proposition — if the "most authoritative" database silently picks one of two conflicting official numbers without flagging the conflict, and a customer or journalist catches the discrepancy against the brand's own published FAQ, that's a direct hit to the trust the whole business is built on.
- **Mitigation:** Never silently resolve a same-source contradiction. Surface both values with a `conflict: true` flag and source citations, use a documented tie-breaking policy (e.g., "spec table over FAQ, product page over hub page") only as a default *display* value, and route flagged conflicts to a human review queue rather than auto-resolving.

---

## Cross-Cutting Recommendation

The single biggest structural risk across all six categories is **concentration on sources that are individually unverified-at-scale or already partially broken** (Madhuloka for retail volume, KSBCL PDFs for regulatory pricing, OFF/Go-UPC for barcodes, Volza for trade intelligence) combined with **zero freshness signal** anywhere in the ecosystem. ValueBrew's competitive moat as "most authoritative" depends less on any single clever scrape and more on (a) source redundancy, (b) a re-crawl-and-diff cadence with visible staleness metadata, (c) a conflict-surfacing (not conflict-hiding) data model, and (d) a standing legal review checkpoint before any feature that touches importer-identity trade data or resold third-party barcode data.