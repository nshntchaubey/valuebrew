# Deliverable 9 — Gap Analysis

# Deliverable 9: Gap Analysis — Karnataka Beer Master Database

Scope: what this session's research (5 domain reports + the 216-SKU extraction) could NOT reliably establish, field by field, with the specific SKUs/sources implicated and a concrete next step to close each gap.

---

## 0. Structural gap: the extraction schema itself has no columns for the fields that matter most

The 216-SKU catalog's schema is `beer_name / brand / brewery / style / size / price_count / sources / confidence`. It has **no field for ABV, no field for actual ₹ price (only a `price_count` tally of how many price observations existed — never the number itself), no GTIN/barcode field, no calorie/nutriment field, and no launch-date field.** This means even where the underlying domain research *did* surface a hard number — e.g. Heineken Original 5% ABV / 42 kcal per 100ml (heineken.com/in/en/our-products/heineken-original/), or UBL's Kingfisher Smooth Karnataka pricing (₹100/330ml can, ₹120/330ml bottle, ₹155/500ml can, ₹200/650ml bottle, per the SEBI Reg 30 PDF) — that data was never carried into the structured catalog row for the corresponding SKU.
**Fix:** Before the next extraction pass, add `abv_pct`, `mrp_inr`, `gtin`, `kcal_per_100ml`, `launch_date` as first-class columns, and re-run the Madhuloka/KSBCL/UBL-PDF scrapers to populate them — the raw source pages already contain most of this; it's a re-extraction problem, not a re-research problem.

---

## 1. Karnataka MRP / retail price — present in source but not extracted as a number

- **KSBCL** ("Karnataka State Beverages Corporation Limited — Supplier-wise Item-wise Price List") is cited as the source for 18 SKUs (Kingfisher Premium, Bullet, Heineken, Budweiser, Carlsberg Elephant, Tuborg, Bira 91, White Owl, Woodpecker, Guinness, Kolt) — this is the single most authoritative Karnataka retail-price source available (it's the state-owned monopoly wholesaler), yet **no actual ₹ figure was captured for any of these 18 rows.**
- **Madhuloka**: ~103 beer SKUs were browsed but again no price value was retained in the summary (only a `price_count` presence flag), despite the underlying research report ("Karnataka/Bangalore online liquor retailers") confirming Madhuloka product pages carry `itemprop=price` microdata directly in HTML.
- Living Liquidz's 9 SKUs are sourced from a Wayback Machine archive of unknown date, so even if prices were captured they'd be stale by an unknown margin.

**Fix:** Re-scrape KSBCL's price-list page/PDF and Madhuloka's `/shop/category/beer-3/page/N` pages specifically for the price field (it's already proven scrapable — Odoo `itemprop=price`), and timestamp every price pull. For KSBCL, also capture the "duty slab" PDFs referenced in the site-feasibility report — Karnataka excise duty is a distinct line item from MRP and matters for margin analysis.

## 2. ABV — almost entirely absent at the Karnataka-SKU level

Confirmed ABV numbers exist only for a handful of **brand-level, not Karnataka-package-level**, entries: Heineken Original (5%), Heineken Silver (4%), Heineken 0.0 (<0.03%), Kingfisher Ultra Witbier ("<5%" per UBL PDF), STOK Strong/Lager/Wheat (7%/4.8%/4.7%, but with an internal contradiction on Mount Everest Breweries' own site listing Strong at 8% in its FAQ), Toit Banger Lager (4.5%) and Basmati Blonde (4.6%), assorted Arbor/Windmills on-tap beers, and third-party (non-official, low-confidence) figures for Bira91 variants and Simba variants (unsobered.com, Wikipedia). For the 103 Madhuloka SKUs, the 18 KSBCL SKUs, and nearly all the 25+ Bira91/Geist/Toit variant listings in the catalog, **ABV is simply not recorded anywhere in this research.**
**Fix:** ABV is legally required on Indian beer labels — the fastest, cheapest path is photographing/OCR-ing back labels at point of sale (a field team walking 5-10 Bangalore stores could cover 80%+ of the catalog in a day), cross-checked against FSSAI label-registration filings if accessible. This is far more reliable than scraping, since almost no retailer or brand site publishes ABV consistently (Madhuloka's one checked product page had none).

## 3. GTIN / Barcode — a confirmed, structural data gap across the entire industry, not just this session

No brewery's official site publishes GTINs (confirmed explicitly in the barcode-sources report). Open Food Facts has real GTINs for only ~14-26 India-tagged beer entries system-wide (Kingfisher 8905002180007, Tuborg Strong 8906018940104, Bira "Boom" 8908005126324, Budweiser India, Coolberg, etc.) — a tiny fraction of the 216-SKU catalog. Commercial lookup APIs are worse for this vertical: UPCitemdb returned **zero** matches on 4 tested Indian beer GTINs; Go-UPC matched 4/5 but its ToS explicitly prohibits reselling/redistributing/publishing the data it returns, which rules it out as a source ValueBrew could build a public database from. GS1 India's DataKart (the "official" repository) has no public API and undisclosed commercial-access pricing.
**Fix:** Two parallel tracks — (a) treat Open Food Facts as a free, ODbL-licensed seed and contribute back (its terms permit commercial reuse with attribution); (b) directly email GS1 India (`implementation@gs1india.org` / `registration@gs1india.org`) to price out a "DataKart for Solution Providers" commercial feed — this is the only channel confirmed to have comprehensive, authoritative Indian GTINs, but pricing/terms must be negotiated, not scraped.

## 4. Duplicate/ambiguous SKU rows with no disambiguating field

Several catalog rows are literal duplicates with degraded confidence and no way to tell them apart: "HEINEKEN SILVER" appears 3 times (one High-confidence row with size=330ml, two Medium-confidence rows with blank size, `price_count`:2 — the Madhuloka source note admits "multiple listings at ₹120/₹155/₹195 suggest different sizes but not confirmed"). Same pattern for "KNOCK OUT TIN," "SIMBA ROAR STRONG," "BUDWEISER MAGNUM TIN," "KF PREMIUM TIN," "KF STRONG TIN." These are almost certainly different pack sizes (pint/tin/bottle at different ml) that got merged during dedup without preserving the size attribute that would have disambiguated them.
**Fix:** Re-scrape Madhuloka product detail pages (not just category listing pages) for these ~10 ambiguous names — the detail page schema.org microdata includes size/price per the feasibility report; this is a re-crawl, not new research.

## 5. Style/category — missing or merely inferred-from-name for the majority of Madhuloka SKUs

Roughly 70 of the ~103 Madhuloka-sourced rows have a blank `style` field; where a style is present it is frequently caveated "(from product name)" or "(inferred, not confirmed on this site's page)" — e.g. "SIMBA STOUT PINT" → style "Stout (from product name)." Madhuloka's storefront simply doesn't expose a style/category attribute per the site-feasibility report ("Country/Brand/Size shown" — no style).
**Fix:** Style has to come from brand-owner sources, not the retailer. Cross-reference each brand against Carlsberg Group's global catalog (already used successfully for Tuborg/Carlsberg entries), UBL's `/our-brands` pages, and Mount Everest Breweries' STOK spec table — all three are confirmed server-rendered and scrapable without JS execution.

## 6. Brewery/manufacturing-site attribution — inconsistent and mostly blank for Madhuloka rows

The KSBCL-sourced rows have excellent brewery detail (exact legal entity + KSBCL supplier code, e.g. "United Breweries Ltd (Nanjangud unit) — KSBCL Supplier Code 0210"). The Madhuloka-sourced rows are the opposite: most have a blank `brewery` field, and where populated it's often a generic brand-owner guess with an explicit caveat (e.g. Hoegaarden's brewery listed as "Ab Inbev (listed as 'Brand' on site, likely importer not literal brewery)"). We do not have a confirmed manufacturing/bottling location for the large majority of Madhuloka SKUs.
**Fix:** Match Madhuloka SKU names against the KSBCL supplier-code table (which does have this) — KSBCL is the wholesale gatekeeper for all beer sold in Karnataka, so every legally-sold SKU should appear there with a supplier code; this cross-walk alone would close most of this gap without new scraping.

## 7. Craft brewery retail-vs-tap-only status — genuinely unresolved for several brands

Arbor Brewing's official site explicitly states its packaged/canned beer is "Retailing only across Goa," yet its Bengaluru brewpub taps are in the catalog implicitly via the domain report — whether any Arbor SKU is actually purchasable in Karnataka retail is unconfirmed either way. Toit's site says beer is available "at an MRP store near you" but never names which SKUs or confirms Karnataka vs. Pune/Mumbai. Byg Brewski's site (checked one page only, "/packages/") shows no evidence of packaged retail product at all — brewpub/event-only is a provisional finding, not confirmed. Windmills Craftworks shows zero retail/bottle/takeaway language anywhere on its site — likely on-tap-only, but not independently confirmed by, e.g., a Karnataka excise retail license lookup.
**Fix:** This needs a phone call / distributor inquiry, not more web research — call Toit's and Byg Brewski's stated retail contacts, or check KSBCL's supplier list for their legal entity names (Byg Brewski, Windmills) to see if they hold a Karnataka bottling/retail supply license at all.

## 8. Non-KSBCL retail pricing recency — unverifiable freshness across every site checked

None of the six retail sites investigated (Madhuloka, Living Liquidz, Tonique, Online Alcohol, Beer Basket, Livcheers) expose reliable per-product `lastmod` timestamps. Tonique's price table carries a stale placeholder phrase ("Price list coming soon") next to live-looking prices and a 2023-04-10 schema.org `dateModified` — meaning any price pulled from it could be up to 3 years old. Living Liquidz's 9 catalog SKUs came from a Wayback Machine snapshot of unknown vintage because the live site is in a confirmed multi-session HTTP 503 outage.
**Fix:** Timestamp every future scrape at capture time and treat any figure without a capture date as unusable for pricing decisions; deprioritize Tonique entirely until it shows a live update; recheck livingliquidz.com periodically (it may come back) rather than relying on the Wayback snapshot going forward.

## 9. Bira91's own official channel — unreachable this session

`bira91.com` served an Apache default page with a TLS cert for an unrelated domain (`*.ksmart.live`) on every attempt — this is Bira's own primary domain, not a scraping target site, so its ~14 Bira91 catalog rows all trace back to Wayback Machine archives or Wikipedia (explicitly flagged Low/Medium confidence, with an internally-inconsistent ABV figure on Wikipedia itself for Bira91 White: 4% vs. 4.9%).
**Fix:** Retest `bira91.com` periodically (may be a transient misconfiguration); in parallel, verify the two unconfirmed candidate domains surfaced only via search (`www.bira91.beer`, `stores.bira91taproom.com`) by direct fetch — neither was actually loaded this session.

## 10. Calorie/nutriment data — brand-level only, and only for 3 SKUs system-wide

Calories per 100ml exist only for Heineken Original (42 kcal), Heineken Silver (35 kcal), Heineken 0.0 (21 kcal) — all from heineken.com/in brand pages, not Karnataka-specific packaging. Zero calorie data exists for any Kingfisher, Tuborg, Carlsberg, Bira91, Budweiser, or craft-brewery SKU in the 216-row catalog.
**Fix:** Same remediation as ABV (#2) — this is a label-photography/OCR problem, not a web-research problem, since almost no Indian beer brand publishes nutriment data online (Open Food Facts' Kingfisher entry, for instance, has all nutriment fields empty).

## 11. New-import-brand detection — a real capability gap with an unresolved legal question attached

Volza's free-tier preview shows genuine brand-identifiable new-import signal (Tusker/Kenya, Saigon Export/Vietnam, Cheetah/Camel/Abest/Vietnam, Sri Lanka canned beer) but is capped at 62 shipments/year for India+HSN2203 in the free tier, and full buyer/supplier identity requires a paid plan (~$1,500-$9,600/yr). More importantly, whether republishing importer-identity-linked shipment data would run afoul of **Section 135AA of the Customs Act, 1962** could not be verified from primary source this session — every direct link to the statute's text (indiacode.nic.in, sooperkanoon.com, taxtmi.com, llmadvocates.com) 404'd or was blocked; the only evidence is a Bing AI-summary and unverified secondary headlines.
**Fix:** Do not build a "new imported brand" feature on identity-linked trade data until (a) a Volza paid trial is run to confirm real completeness/lag, and (b) Indian legal counsel independently confirms Section 135AA's scope and whether reselling bill-of-lading-sourced (vs. DGCI&S customs-declaration) data is a safe distinction — this is a compliance gate, not a data gap that more scraping can close.

## 12. Non-alcoholic / soda / water line extensions miscategorized as beer — a data-hygiene gap, not a missing field

The catalog includes several UBL/Carlsberg SKUs that are explicitly *not* beer — "Kingfisher Premium Packaged Drinking Water," "Kingfisher Strong Power Soda," "Kingfisher Ultra Premium Soda," "Tuborg Zero Packaged Drinking Water," "Tuborg Zero Soda," "Carlsberg Elephant Strong Soda." These were correctly flagged Low/Medium confidence but remain in a 216-count "SKU catalog" that a stakeholder could easily mis-cite as 216 *beers*.
**Fix:** Add a `category` (beer / non-alcoholic-beer / soda / water) filter at ingestion so headline SKU counts aren't inflated; this is a one-line dedup/tagging fix against data already in hand.

## 13. Livcheers and other client-rendered/JS-gated retailers — technically inaccessible without a policy trade-off

Livcheers' catalogue is Next.js client-rendered with no product JSON visible in static HTML, and its robots.txt explicitly disallows `/api/` and blocklists a long list of named scraping bots (GPTBot, Bytespider, AhrefsBot, etc.) — a clear stated no-scraping policy. This means its Bangalore-specific pricing (confirmed to exist via UI text mentions of "Beer"/"Kingfisher") is currently a total blind spot.
**Fix:** Do not scrape against Livcheers' stated policy. If its data is wanted, pursue an official data-partnership/API conversation with Livcheers directly rather than technical workarounds.

## 14. Karnataka Excise Department's own dataset — unreachable, and no government open-data equivalent to Kerala's exists

`excise.karnataka.gov.in` failed DNS resolution outright this session. `data.gov.in` returned literal "No Result" for every beer/alcohol/excise/Karnataka-excise search term tried. The only comparable government-sourced open dataset found is Kerala BEVCO's Kaggle-hosted price list (CC0, ~4,300 items) — useful only as a structural template, not Karnataka data.
**Fix:** Retry `excise.karnataka.gov.in` from a different network (this may be a local DNS/sandbox artifact rather than the site being down — KSBCL's own site, `ksbcl.karnataka.gov.in`, *was* reachable) and explore its ERP/OFS login and "supplier list"/"purchaser code" sub-pages, which were seen but not explored this session and may contain the exact duty/price data currently missing.

---

### Priority ranking for closing gaps (founder view)

1. **MRP/price extraction from KSBCL + Madhuloka** (#1) — highest ROI, data already proven accessible, just wasn't captured as a number.
2. **ABV + calories via label photography** (#2, #10) — no web source will ever reliably give this; budget a field-data-collection pass now rather than more scraping later.
3. **KSBCL supplier-code cross-walk to fix brewery/style blanks** (#5, #6) — a join against data already in hand, not new research.
4. **GS1 DataKart commercial-access conversation** (#3) — start now since pricing/terms negotiation will take calendar time regardless.
5. **Legal review of Section 135AA before any import-brand-detection feature** (#11) — gates a whole future product line; resolve before investing further in Volza.