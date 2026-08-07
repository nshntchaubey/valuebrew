# Deliverable 7 — Automation Roadmap

# ValueBrew — Deliverable 7: Automation Roadmap

## Framework

| Tier | Definition | Criteria used below |
|---|---|---|
| **Fully Automated** | Runs unattended on a schedule with no human in the loop; stable machine-readable contract | Documented JSON/REST API, permissive ToS, no anti-bot, no legal ambiguity |
| **Semi-Automated** | Scriptable, but needs a human checkpoint — either because it's HTML (breaks on redesign), a PDF (needs parsing + spot-check), or has legal/ToS terms requiring judgment calls | HTML scraping w/ no anti-bot, PDF extraction, form/token submission, gated APIs with usage restrictions |
| **Manual** | A person must visit, read, judge, negotiate, or wait — not worth automating yet, or automation is blocked (technically, legally, or by site policy) | Site down/broken, explicit bot-blocking, age-gates with unclear ToS, negotiated commercial data deals, unverifiable legal risk |

---

## 1. Retail/e-commerce SKU sources

| Source | Category | Why |
|---|---|---|
| **Madhuloka.com** | **Semi-Automated → target Fully Automated** | Odoo storefront, fully permissive robots.txt, no Cloudflare/CAPTCHA observed, pagination confirmed (`/shop/category/beer-3/page/N`), ~103 beer SKUs w/ price+brand+size in raw HTML. No JSON API exists (all Odoo autocomplete endpoints 404'd), so it's HTML-parsing, not an API — hence "semi" until a scraper is built and proven stable, then treat as de-facto automated with monitoring. **This is the single best data source in the whole research set.** |
| **Online Alcohol (onlinealcohol.in)** | **Fully Automated** | Genuine live WooCommerce Store REST API (`/wp-json/wc/store/v1/products`), clean JSON, pagination headers, robots.txt doesn't block `/wp-json/`. Small catalogue (12 beer SKUs) — good as a cross-check feed, not primary. |
| **Beer Basket (beerbasket.in)** | **Semi-Automated** | Categories API works but products API 500s consistently (site bug, not blocking) → fallback is HTML scraping of `/type/<slug>/` taxonomy pages, which do render. Heavy SEO-mill cruft lowers trust — treat as tertiary. |
| **Tonique.in** | **Manual/low-priority Semi-Automated** | Single static HTML table (633 rows), no pagination, dated April 2023 in its own schema.org metadata with a leftover "coming soon" placeholder string. Scriptable but not worth it — stale data risk outweighs scraping effort. |
| **Living Liquidz** | **Manual (blocked)** | HTTP 503 "under maintenance" on every path, both www/non-www, confirmed on repeated retries. Current catalog entries sourced via Wayback Machine only — that's a manual, one-off archive pull, not a repeatable pipeline. Recheck monthly; don't build against it now. |
| **Livcheers.com** | **Manual — do not automate** | robots.txt explicitly disallows `/api/` and blocklists a long list of named scraping bots (GPTBot, AhrefsBot, Bytespider, etc.). This is an explicit policy signal, not just a technical obstacle. Any use of this site should be a human occasionally checking prices in a browser, never a scraper. |
| **KSBCL (Government of Karnataka)** | **Semi-Automated** | Real official domain is `ksbcl.karnataka.gov.in` (ksbcl.com 301s there), robots.txt fully open. But the Supplier-wise Item-wise Price List that produced our highest-confidence 18 SKUs lives in linked documents (PDF duty slabs etc.), not a browsable HTML catalogue — needs a PDF-parsing pipeline (pdfplumber-style) with a human spot-check on each new price cycle given this is meant to be our *most authoritative* pricing source. |

## 2. Brand/corporate official sites

| Source | Category | Why |
|---|---|---|
| **United Breweries — SEBI Reg.30 filing PDFs** (`unitedbreweries.com/pdf/Material Events/`) | **Semi-Automated** | This is genuinely the best "new launch" signal in the whole dataset — dated, structured, sometimes contains full Karnataka per-SKU pricing (e.g. Kingfisher Smooth: ₹100/330can, ₹120/330btl, ₹155/500can, ₹200/650btl). Build a folder-watcher that polls this path and diffs for new PDFs, auto-extracts via pdftotext, but keep a human-validation gate before writing launch/price facts into the DB — these are exactly the "authoritative" facts a mistake would be most costly on. |
| **United Breweries — main site (age-gate)** | **Manual** | Cloudflare-fronted + Drupal age-gate form requiring CSRF `form_build_id` token submission. Technically scriptable (no JS challenge observed) but low value — the sitemap lists brand names only, no ABV/size/price data behind the gate that isn't already in the PDFs above. Not worth the engineering cost. |
| **Heineken.com/in/en** | **Semi-Automated** | Server-rendered (Umbraco), no anti-bot, ABV + kcal/100ml data confirmed on ~5 product pages (Original, Silver, 0.0). Small, stable page set — script it once, re-check quarterly rather than building continuous monitoring. |
| **Carlsberg India (carlsbergindia.com)** | **Semi-Automated** | Cloudflare-fronted but no CAPTCHA; robots.txt specifies `Crawl-delay: 10`. Confirmed brand/size data on some pages, but the actual India product-listing URL structure isn't fully mapped (a guessed sub-path 404'd) — needs a short discovery pass before scripting, then respect the 10s crawl delay. |
| **AB InBev India (abinbevindia.in)** | **Manual** | Only a WordPress consent/age-gate redirect verified; content behind it was never fetched/confirmed. Domain ownership itself is inferred from search results, not confirmed via ab-inbev.com. Needs manual verification before any automation investment. |
| **Bira91.com** | **Manual (blocked)** | Domain resolves to a broken Apache default page with a mismatched TLS cert (`*.ksmart.live`) — this is not Bira's site currently. All Bira91 SKU data in the catalog came from Wayback Machine archives, which is inherently a manual, point-in-time pull. Candidate live alternates (`bira91.beer`, `stores.bira91taproom.com`) are unverified — a human needs to confirm these before any scraper is written. |
| **Kingfisherworld.com** | **N/A — dead end** | Confirmed to be an unrelated third-party medical SaaS app ("GemGP"). Drop from the source list entirely; UB's own `/our-brands` page is the correct Kingfisher reference. |

## 3. Karnataka craft/brewpub sites (Simba, Geist, Toit, Arbor, STOK, Windmills, Byg Brewski, Goa Brewing)

| Category | Why |
|---|---|
| **Manual** | Every one of these is low-SKU-count (5-8 beers each), several are brewpub-only with no packaged retail product (Windmills, Byg Brewski, and Arbor's canned product is Goa-only despite a Bengaluru taproom), and none expose ABV/size/price in a structured, scrapable format worth automating. This whole tier is better handled as a human doing a quarterly manual pass across ~8 sites than building 8 bespoke scrapers for a few dozen SKUs total. STOK's official spec page (mounteverestbreweries.com) is the one partial exception — it's clean HTML with a full ABV/IBU/size table, but it has an internal self-contradiction (7% vs 8% ABV for STOK Strong) that requires human adjudication regardless of scraping. |

## 4. Barcode/GTIN enrichment

| Source | Category | Why |
|---|---|---|
| **Open Food Facts** | **Fully Automated** | Stable, documented JSON API (`/api/v2/product/{code}.json`, `/cgi/search.pl`), ODbL/DBCL/CC-BY-SA licensing explicitly permits commercial reuse with attribution. Confirmed live records for Kingfisher, Tuborg, Budweiser India, Bira, Coolberg. This is the only source in the whole research set that is simultaneously free, legal-to-republish, and has a real API — build this first for barcode enrichment. |
| **GS1 India / DataKart** | **Manual (business-dev track, not engineering)** | Registration is for brand owners issuing their own GTINs, not a lookup service for a third party like ValueBrew. Bulk/commercial lookup access ("DataKart for Solution Providers") requires direct negotiation with GS1 India — pricing isn't published. This is a procurement/BD task, not something to build against. |
| **UPCitemdb** | **Manual — deprioritize** | Verified 0/4 real Indian beer GTINs matched despite claiming 718M+ global entries. Paid API with zero demonstrated coverage for this exact use case — don't spend engineering time here. |
| **Go-UPC** | **Semi-Automated, internal-use only** | Matched 4/5 tested Indian beer GTINs — real coverage — but its own ToS (verified, dated 19 Mar 2025) explicitly prohibits reselling/redistributing/publicly exposing the data it returns. Usable only as an internal QA cross-check on our own barcode data, never as a source we display or republish. Flag this constraint to whoever integrates it. |
| **Barcode Lookup** | **Manual (blocked)** | 403 bot-block on every attempt, both WebFetch and curl w/ browser UA. Completely unverified — don't plan around it until someone gets a paid account and tests it manually. |

## 5. Trade/import intelligence (new imported-brand detection)

| Source | Category | Why |
|---|---|---|
| **Volza (beer/HSN 2203, India page)** | **Manual — hold, legal review required before any automation** | Free-tier preview genuinely shows brand-identifiable new import data (Tusker/Kenya Breweries, Saigon Export, Cheetah/Camel/Abest from Vietnam, etc.) — real signal for "new imported brand entering India" detection. But: (1) no public API confirmed, only browser-rendered preview; (2) Section 135AA of the Customs Act, 1962 appears to criminalize unauthorized publication of importer/exporter transaction-level trade data — this was only corroborated via a Bing AI summary and secondary snippets (every primary legal source URL 404'd/403'd in testing), so **confidence is Medium, not High**, and counsel must confirm whether Volza's bill-of-lading-sourced data is legally distinct from DGCI&S customs-declaration data before ValueBrew republishes anything derived from it. Treat as a monthly manual browse task, not a scraper, until legal clears it. |
| **DGCI&S (official Government channel)** | **Manual** | Legally the cleanest source, but explicitly aggregate-only (Country × Commodity × Port) — no importer identity for private use under any circumstances. Access itself is a manual registration + per-record purchase (₹1/record via Web-PIS) process, not an API. Useful only for aggregate import-volume trend commentary, not brand discovery. |
| **Zauba.com** | **Manual — do not build against** | Site loads but sample records are dated 2013/Nov-2016 with a "© 2021 Zauba.com" footer — the underlying pipeline is stale/frozen, almost certainly tied to India's 2016 policy change ending mandatory trade-data disclosure. Not worth any engineering time. |
| **ImportGenius, Seair, Cybex Exim, Eximpedia** | **Manual — unverified, needs a scoping call** | $199 entry point observed for ImportGenius but scope/coverage not verified; the others weren't investigated at all in this research pass. |

## 6. Open datasets

| Source | Category | Why |
|---|---|---|
| **Kaggle — Kerala BEVCO Liquor Price List** | **Manual (one-time reference)** | CC0, ~4,300 items, high-quality metadata, but it's Kerala not Karnataka. Value is as a *structural template* (item code/brand/volume/landed cost/warehouse price/shop price schema) for designing our own Karnataka price-list ingestion — a one-time human review, not a recurring pull. |
| **data.gov.in** | **N/A** | Literal "No Result" for beer/alcohol/liquor/excise/Karnataka-excise searches — confirmed no dataset exists. Nothing to build. |
| **Open Product Data (OKFN)** | **N/A — dead project** | Homepage 504s, GitHub repo dormant since ~2015. Drop entirely. |
| **Karnataka Excise Dept (excise.karnataka.gov.in)** | **Unresolved — needs retry from a different network** | DNS failure in this sandbox; genuinely unknown whether Karnataka publishes its own BEVCO-style price list. This is the single most important open question for "authoritative" positioning and should be manually re-checked before deciding it's a dead end. |

---

## Engineering priority order (build queue)

1. **Madhuloka scraper** (Semi→Fully Automated). Highest SKU density (~103 beer SKUs, ~1,603 products site-wide), zero anti-bot resistance, permissive robots.txt. Biggest ROI in the whole set — build first, add a nightly cron + diff-alert on price/SKU changes.
2. **Open Food Facts API integration** (Fully Automated). Free, legally clean (ODbL/CC-BY-SA, commercial reuse OK with attribution), stable JSON. Use for barcode enrichment/cross-referencing on top of the Madhuloka catalogue. Low effort, do this in parallel with #1.
3. **KSBCL PDF ingestion pipeline** (Semi-Automated). This is the *government-authoritative* pricing source — worth the extra PDF-parsing effort because it's the strongest "we are the authoritative source" credibility anchor. Add a human spot-check step given stakes.
4. **Online Alcohol WooCommerce API hookup** (Fully Automated). Cheap add-on once #1 is built — use purely as a cross-validation feed against Madhuloka prices.
5. **UB SEBI filing watcher** (Semi-Automated). Build a poller on `unitedbreweries.com/pdf/Material Events/` for new-launch detection — this is genuinely differentiated content (exact launch dates + sometimes full Karnataka pricing) nobody else is likely tracking. Keep a manual-approval gate before publishing extracted facts.
6. **Heineken + Carlsberg brand-page scripts** (Semi-Automated, low frequency). Small, stable page sets — script once for ABV/size enrichment, re-run quarterly rather than continuously monitoring.
7. **Craft brewery manual sweep** (Manual, quarterly). Simba/Geist/Toit/Arbor/STOK/Windmills/Byg Brewski/Goa Brewing — not worth bespoke scrapers for ~40 total SKUs; assign a human quarterly pass.
8. **Go-UPC internal QA check** (Semi-Automated, internal-only). Use to validate our own barcode data; do not expose or republish per its ToS.
9. **Hold / do not build now**: Bira91.com (broken domain — wait for a confirmed live alternate), Living Liquidz (503 outage — recheck monthly), Livcheers (explicit anti-scraping policy — respect it), Zauba (stale data), UPCitemdb (zero coverage), Barcode Lookup (unverifiable, bot-blocked).
10. **Legal-gated, not engineering-gated**: Volza / trade-import brand detection. Get counsel to confirm Section 135AA scope and Volza's ToS before writing any scraper — this could be a valuable "new imported brand" alert feature, but building it before legal clearance is the highest-risk item in this entire roadmap.
11. **BD track, not engineering**: GS1 India DataKart commercial access — pursue as a partnership/procurement conversation in parallel, not a sprint item.

### Key risks to flag to the team now
- **Legal**: Section 135AA (Customs Act) risk on any importer-identity-linked trade data (Volza) is only Medium-confidence-verified — get counsel before touching this, not after building it.
- **ToS**: Go-UPC and any Living Liquidz/Livcheers scraping would violate explicit terms/robots.txt — engineering should not route around these without a policy decision from leadership.
- **Data quality**: No source found publishes ABV consistently — this is a real product gap; STOK's own official page contradicts itself (7% vs 8%) — expect to need per-brand manual ABV verification regardless of how good the scraping gets.
- **Fragility**: Bira91.com and Living Liquidz being down/broken right now means two of our named "core" sources are currently non-functional — the roadmap above deliberately routes primary reliance to Madhuloka + Open Food Facts + KSBCL instead.