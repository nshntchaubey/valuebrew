# Deliverable 2 — Catalog Acquisition Strategy

# ValueBrew — Deliverable 2: Catalog Acquisition Strategy

## Bottom line

We have two different jobs that require two different kinds of sources, and conflating them is the biggest risk in the current 216-SKU catalog:

1. **"What is the legal/official Karnataka MRP and who is the licensed supplier?"** → only **KSBCL** can answer this authoritatively.
2. **"What SKUs actually exist, at what shelf price, in what pack sizes, with what brand/style metadata, and eventually what barcode?"** → this is a **retailer-scrape + brand-site + open-database** aggregation problem, led by **Madhuloka**.

Nothing in the research shows any brand's own site (UBL, Heineken, Carlsberg, AB InBev, Bira91) publishing a routine, structured price list — those are marketing/investor sites. Treat them as metadata enrichment only, never as the price source.

---

## Priority order

### Tier 0 (do this week) — Karnataka MRP authority: KSBCL

**Source:** Karnataka State Beverages Corporation Limited, `ksbcl.karnataka.gov.in` (note: `ksbcl.com` 301-redirects here — use the `.gov.in` domain).

- This is the only source in our research that is a **Government of Karnataka PSU** with **Supplier Code**–level mapping (e.g., Kingfisher = Supplier Code 0210, Bullet = 0206, Carlsberg Elephant = 0205, Bira 91 = 0214) — this is the ground truth for "which legal entity actually supplies this SKU in Karnataka," which no retailer or brand site gives us.
- **Important gap to close immediately:** the 17 KSBCL-sourced SKUs already in the catalog (Kingfisher Premium/Strong, Bullet, Heineken, Budweiser, Carlsberg Elephant, Tuborg, Bira 91, White Owl, Woodpecker, Guinness, Kolt) came from a "Supplier-wise Item-wise Price List," but our own later scraping-feasibility pass on `ksbcl.karnataka.gov.in` did **not** find a live HTML price-list page — it only found linked PDFs (e.g., duty slabs). This means the price list is almost certainly a **PDF document**, not a scrapable page, and we don't currently have its exact URL on file. **Action: track down and archive the specific PDF (or ERP/OFS portal page, which was not explored) that produced the existing 17 records before building any recurring ingestion job.** Budget for PDF-table parsing (pdfplumber-class tooling), not BeautifulSoup.
- Use KSBCL for: legal MRP ceiling, brewery-to-brand mapping, and confirming which SKUs are *actually* excise-cleared for Karnataka sale (this is the one thing retail sites can't tell us — a Madhuloka listing doesn't prove state-level legality).
- Do not use KSBCL for: breadth (it only gave us the "headline" SKU per brand family — 650ML x 12 case packs — not the full pint/tin/can variant sprawl retailers carry).

### Tier 1 (weeks 1–2) — Retail SKU/price breadth: Madhuloka first, then Online Alcohol as a cross-check

**1. Madhuloka (`madhuloka.com`) — primary retail source, build this first.**
- Richest Karnataka-relevant catalog found: ~103 beer SKUs across a dedicated `/shop/category/beer-3` taxonomy, ~1,603 total product URLs in `sitemap.xml`.
- Fully permissive `robots.txt` (`User-agent: *`, no Disallow), no Cloudflare/CAPTCHA challenge observed on repeated fetches, server-rendered Odoo HTML (no JS execution needed) — confirmed low-to-medium scraping difficulty, estimated 8–16 hours to build, 1–3 hrs/month to maintain.
- Gives brand, size, price, and (per the scraping-feasibility check) sometimes Country/Brand/Size fields — but **not ABV**, confirmed absent on the one product page inspected. Don't expect ABV from this source.
- No JSON/REST API exists (all Odoo autocomplete endpoints tested returned 404) — this has to be HTML scraping via the sitemap + paginated category pages (`/shop/category/beer-3/page/N`).
- This should become ValueBrew's **primary, recurring** ingestion job — it's the best combination of breadth, reliability, and low legal/technical friction of everything tested.

**2. Online Alcohol (`onlinealcohol.in`) — secondary, cheap validation layer.**
- The only retailer with a genuinely working structured JSON API (`/wp-json/wc/store/v1/products`), confirmed live with clean price/image/category fields — lowest automation cost of any source tested.
- But its Beer category is small (12 SKUs vs. Madhuloka's ~103) and the site carries heavy ad-network scripts, which lowers our trust in its data quality.
- **Use case:** cross-validate a subset of Madhuloka prices cheaply via API rather than as a primary catalog. Not worth building a full pipeline around given its narrow beer coverage.

**3. Living Liquidz (`livingliquidz.com`) — retry later, don't build against it now.**
- Returned HTTP 503 "under maintenance" on every path tried (www and non-www) in the latest research pass — this is a real outage, not a bot block.
- The Wayback Machine archive already gave us useful historical SKUs (Amstel Grande, Bira White, London Pilsner, several Kingfisher/Tuborg variants, Effingut ciders) at Medium/Low confidence — keep these as provisional records, but **do not treat archived prices as current MRP**, and re-check the live site periodically (e.g., monthly) to see if it's back before investing engineering time.

**Deprioritize:** Tonique.in (single static price table, dated April 2023 metadata, contains a leftover "Price list coming soon" placeholder — stale by its own evidence) and Beerbasket.in (Store API `/products` endpoint 500-errors consistently; site is padded with templated "alcohol delivery in `<city>`" SEO pages including irrelevant US cities, which undermines confidence in the rest of its data). Both are HTML-scrapable in principle but not worth prioritizing over Madhuloka/Online Alcohol.

**Do not scrape:** Livcheers.com — its `robots.txt` explicitly disallows `/api/` and blocks a long named list of scraping bots (SemrushBot, AhrefsBot, GPTBot, Bytespider, etc.). This is an explicit, stated crawling policy; building automation against it — even if technically possible via JS rendering — means disregarding the operator's stated wishes. Skip it.

### Tier 2 (weeks 2–4) — Brand/product metadata enrichment (NOT pricing)

These sources exist to fill in **style, ABV, package sizes, brewery entity, and launch history** for SKUs we've already found via KSBCL/Madhuloka — none of them give Karnataka MRP:

- **United Breweries (`unitedbreweries.com`)** — the SEBI Regulation 30 PDF filings under `/pdf/Material Events/` are the single best structured source for **launch-event data with dates and categories**, and occasionally include actual Karnataka price points tied to a specific launch (e.g., Kingfisher Smooth: ₹100/330ml can, ₹120/330ml bottle, ₹155/500ml can, ₹200/650ml bottle, per the Jan 2026 filing; Kingfisher Ultra Witbier: ₹110/150/185 across 330ml bottle/500ml can/650ml bottle from the 2019 filing). Treat this as a **launch-detection feed**, not a live price list — filings are irregular (a few per year), and the main brand pages themselves are behind a Drupal age-gate with no product/price data.
- **Heineken India (`heineken.com/in/en`)** — reliable ABV and calorie-per-100ml figures for Original (5% ABV, 42 kcal/100ml), Silver (4% ABV, 35 kcal/100ml), 0.0 (<0.03% ABV, 21 kcal/100ml). No Karnataka-specific or pricing data. Note `heinekenindia.com` does not resolve — use the `.com/in/en` path.
- **Carlsberg India (`carlsbergindia.com`)** — good for brand/style/size metadata (confirmed 330/500/650ml pack sizes for Tuborg Green) and confirms the Mysuru, Karnataka brewery producing both Carlsberg and Tuborg. No ABV, no pricing on the pages checked.
- **AB InBev India (`abinbevindia.in`)** — resolves to a WordPress consent/age gate; a Karnataka-state dropdown exists but we never verified content behind it. Treat brand ownership of this domain as **inferred, not confirmed** (only found via third-party search, not an ab-inbev.com citation) — low priority until independently confirmed.
- **Bira91.com** — currently broken: serves a default Apache page with a mismatched TLS cert (`*.ksmart.live`), i.e., DNS no longer points at Bira's real site. Do not build against it. Use Wayback Machine archives (already reflected in the catalog at Low/Medium confidence) as a stopgap, and separately verify the unconfirmed candidate domains `www.bira91.beer` / `stores.bira91taproom.com` before relying on them.
- **Craft brands (Simba, Geist, Toit, Arbor Brewing, STOK/Mount Everest Breweries)** — official sites give style/ABV for on-tap and some packaged SKUs, but **two explicit exclusions matter for a Karnataka-only catalog**: Arbor Brewing's packaged retail beer is stated on its own site as "retailing only across Goa" despite its Bengaluru brewpub — don't list its canned SKUs as Karnataka-available. Windmills Craftworks and Byg Brewski show no retail/bottle/takeaway language anywhere on their sites — treat both as **brewpub-only, no packaged SKUs to catalog at all**.

### Tier 3 (as needed) — Barcode/GTIN enrichment

- **Open Food Facts** is the only free, commercially-reusable (ODbL/DBCL, explicit commercial-use permission with attribution) source that returned real Indian beer GTINs during direct API testing — confirmed live records for Kingfisher (8905002180007), Tuborg Strong (8906018940104), Budweiser India, and Bira 91 Boom (8908005126324). Use it as a **barcode-matching enrichment pass** over our existing SKU list, not a discovery source — coverage is thin (~14-26 genuine India-beer hits after filtering out mistagged entries) and quality is uneven (one hit was a Cadbury bar mistagged "Beers"). Every match needs manual QA before being trusted.
- **Avoid Go-UPC** for anything we intend to redistribute: its Terms of Service explicitly prohibit reselling or "making the Service or Product Data publicly available" — using it to power a ValueBrew-facing barcode lookup would violate its ToS even though its India-beer coverage (4 of 5 tested) is better than UPCitemdb's (0 of 4).
- **Skip UPCitemdb** (zero coverage on every Indian beer barcode tested) and **Barcode Lookup** (blocked every fetch attempt with bot detection — completely unverified, don't assume anything about it).
- **GS1 India / DataKart** is not a lookup service for us — it's a registration system for brand owners. If we ever need authoritative GTIN-existence checks at scale, that requires directly contacting GS1 India about a paid "DataKart for Solution Providers" subscription (pricing not published, must be negotiated) — not worth pursuing until the rest of the catalog is built.

### Tier 4 (optional, only if we build a "new brand entering India" alert feature) — Trade data

- **Volza** (`volza.com/p/beer/import/import-in-india/`) is the only working option here — its free preview already shows brand-identifiable import shipment descriptions (Tusker/Kenya Breweries, Saigon Export, Cheetah/Camel/Abest from Vietnam, Sri Lanka canned beer) for India, HSN code 2203. Paid tiers run ~$1,500–$9,600/yr. This is **not Karnataka-specific** and its India-beer coverage (62 shipments/year in the free tier) looks thin relative to actual import volume.
- **Legal caution:** Section 135AA of the Customs Act, 1962 criminalizes unauthorized publication of importer/exporter identity-linked transaction data. Our research could not directly verify the statute's exact text (every primary-source URL 404'd or was blocked) — this is flagged as **Medium confidence, not confirmed**. If we ever build on Volza, get counsel to confirm we're only republishing product-description-level data, never importer identity.
- **Skip Zauba** (data is stale — sampled records dated 2013/2016, footer reads "© 2021") and **DGCI&S** (legally clean but only gives aggregate country×commodity stats, explicitly withholds importer identity — useless for brand-level detection).

---

## Sequencing summary

| Order | Source | Purpose | Effort/Risk |
|---|---|---|---|
| 1 | KSBCL price list (locate exact PDF/portal page) | Authoritative Karnataka MRP + legal supplier mapping | Medium (PDF parsing; URL not yet confirmed) |
| 2 | Madhuloka | Primary retail SKU/price/size breadth | Low-Medium (8-16 hrs build) |
| 3 | Online Alcohol JSON API | Cheap price cross-check | Low, narrow coverage |
| 4 | UB SEBI Reg 30 filings | Launch-event detection + occasional official Karnataka pricing | Low effort, irregular cadence |
| 5 | Heineken/Carlsberg/AB InBev brand pages | ABV/style/size metadata | Low-Medium, no pricing |
| 6 | Open Food Facts | Barcode enrichment | Low effort, needs manual QA |
| 7 | Living Liquidz (retry) | Second retail cross-check once live again | Blocked until site returns |
| 8 | Volza (optional) | New-imported-brand alerts | Paid, legal review first |

**Explicitly excluded from any catalog build:** Livcheers (robots.txt forbids it), Bira91.com (dead), UPCitemdb/Barcode Lookup (no usable coverage or unverifiable), Zauba (stale), Go-UPC (ToS forbids redistribution), Windmills Craftworks/Byg Brewski (no packaged retail product), Arbor Brewing's packaged cans (Goa-only, not Karnataka).