# Agent 10 — Founder Execution Team: Operational Plan

# ValueBrew: Build Plan for Karnataka's Authoritative Beer Database

## Bottom line

216 rows this session is not 216 authoritative SKUs. Strip out duplicates and metadata-only rows and you have roughly **~100 SKUs with a real observed Karnataka retail price** (KSBCL + Madhuloka), and **~115 rows that are brand-catalog metadata with zero price data** (UB, Carlsberg, Heineken, AB InBev, Bira91 official pages all show `price_count: 0`). That distinction is the single most important thing to fix before you call anything "authoritative" — a database of brand names without Karnataka MRP is a Wikipedia page, not a moat.

The real total Karnataka packaged-beer SKU universe (brand × pack-size, which is how KSBCL and retailers actually itemize) is most likely **400–600 SKUs**, not 1,000+. Getting to 500 is achievable through better digital harvesting; getting past that requires relationships (KSBCL, distributors, breweries), not more scraping.

## 1. Audit what you actually have

Look at the catalog by source-type:

| Source | SKUs | Has real price? | Value |
|---|---|---|---|
| KSBCL supplier price list | 18 | Yes (official govt MRP) | Highest — this is the ground truth, but only 18 of what is presumably a much longer master list were captured |
| Madhuloka (madhuloka.com) | ~85-90 | Yes | High — real Bangalore retail prices, server-rendered, easy to scrape |
| Living Liquidz (via Wayback) | ~10 | No | Low — site is down (HTTP 503 "under maintenance"), archived data only |
| UB / Carlsberg / Heineken / AB InBev / Bira91 official brand pages | ~55 | No | Metadata only (style, size, ABV where disclosed) — good for enrichment, useless alone for pricing |
| Simba/Geist/Toit/Arbor multi-source | ~19 | Mostly no | Style/ABV metadata, brewpub-vs-retail ambiguity (Arbor's canned beer is Goa-only, not Karnataka, despite a Bengaluru taproom) |
| Open Food Facts | ~15 | No | Low-confidence, some corrupted fields ("brand: the originl", garbled product names) |

**A data-provenance flag you should resolve immediately**: your own "web scraping feasibility" research report explicitly states it crawled KSBCL's official site (`ksbcl.karnataka.gov.in`) and found *no visible SKU-level price pages* — only PDFs like duty slabs. Yet the SKU catalog has 18 KSBCL rows with `confidence: High` and real prices, sourced to "KSBCL — official Government of Karnataka PSU website, Supplier-wise Item-wise Price List." Either a different crawl found a page the feasibility researcher missed, or that page is one you haven't fully mapped yet. This is your single highest-leverage thing to re-investigate this week — if there's a "Supplier-wise Item-wise Price List" page/download that yielded 18 rows, it almost certainly has 150-400 more rows behind it (KSBCL is Karnataka's sole govt wholesale distributor, so its item list is close to the complete legal SKU universe).

Also flag: duplicate/unresolved entries — "Heineken Silver" appears 3 separate times with different price points and no reconciled size; "Knock Out Tin," "Budweiser Magnum Tin," "Simba Roar Strong" each appear twice. Your effective *unique* SKU count today is closer to **180-190**, not 216, once you dedupe.

## 2. How big is the real universe?

Reasoning from what's in front of you: distinct beer **products** (brand+variant, ignoring pack size) visible across all sources is roughly 100-130 — Kingfisher family (~8), UB's broader portfolio (Bullet, London Pilsner, Zingaro, Kalyani Black Label, Cannon, UB Export, ~7 more), Heineken family (~5), Carlsberg/Tuborg family (~8), AB InBev (Budweiser variants, Corona, Hoegaarden, Haywards, Knock Out, ~8), Bira91 (~12 named variants), Simba (~6), Geist (~4), Toit (~7), craft/regional (White Owl, Woodpecker, Kolt, Effingut, Stangen, Hunter, Grizly, ~10), imports (Guinness, Peroni, Stella Artois, Corona, Amstel, ~6).

Each of those is typically sold in 2-4 Karnataka pack formats (330ml bottle/can/pint, 500ml can, 650ml bottle) — that's the multiplier KSBCL and retailers actually use as distinct line items. **100-130 products × ~3.5 avg pack formats ≈ 400-450 SKUs.** Add rotating/niche imports that Volza's India-beer page surfaced in its free preview (Tusker/Kenya, Saigon Export/Vietnam, Cheetah/Camel/Abest/Vietnam, Sri Lanka canned beer, Namibia malt beer — 62 shipments, 21 buyers over one year) and you get another 20-40 transient SKUs that come and go.

**Realistic target: 400-600 SKUs is the true addressable universe today. 1,000 is not achievable by counting real, currently-sold Karnataka packaged beer SKUs — it would require either counting every historical/discontinued SKU or padding with non-alcoholic malt beverages and soda line-extensions (Kingfisher/Tuborg Zero water and soda, which UB's own site lists as separate products but which aren't beer).** Set your public target at 500 SKUs, and be honest internally that 1,000 means redefining scope (e.g., including all discontinued/seasonal variants, non-alcoholic malt drinks, or multi-year historical price snapshots).

## 3. Hours to get from 216 → 500

**Phase 1 — Finish digital harvesting (20-30 hours, 1-2 weeks).** This is where AI-agent-assisted scraping still has ROI:
- Re-investigate and fully crawl whatever KSBCL page/download produced the 18 rows (highest priority — could single-handedly add 100-300 SKUs with official MRP)
- Finish Madhuloka's full 6-page beer category pagination (you have ~85-90 of its ~103; the gap is small but free)
- Pull onlinealcohol.in's working WooCommerce Store API (`/wp-json/wc/store/v1/products?category=<beer_id>`) — only 12 beer SKUs but a clean JSON feed, ~1 hour
- Scrape beerbasket.in's `/type/domestic-indian-beer/` HTML (its JSON API 500-errors, but the taxonomy page renders fine) — a few hours, expect heavy overlap with Madhuloka
- Parse Tonique's static price table (633 rows, mixed alcohol types, dated April 2023 — treat every price as unverified until cross-checked) — a few hours, low-trust supplement only
- Dedup pass across all of the above (fuzzy-match brand+size to collapse the "Heineken Silver ×3" problem) — 4-6 hours, needs human sign-off, not just AI matching

Realistic yield: **+150-200 net new/verified unique SKUs → ~350-400 total**, with maybe 200-250 carrying real Karnataka MRP.

**Phase 2 — Relationship-driven push (40-60 hours over 3-6 weeks).** This is where you actually cross 400 into 500+, and it's not scraping, it's founder time on the phone/email:
- Formal request to KSBCL for the complete electronic Supplier-wise Item-wise Price List (see partnerships below)
- Direct outreach to 2-3 Karnataka distributors for full brewery order sheets (MRP + case pack + new launches ahead of shelf)
- Direct outreach to Carlsberg India, UB, and the smaller craft players (Simba/Sona Beverages, Geist, Toit) for spec sheets — these have far less bureaucracy than national players and are your fastest wins
- Filling ABV — genuinely no retail-scraping source in this research had ABV consistently; it exists only fragmentarily on brand pages (Heineken: 5%/4%/<0.03%; STOK: internally contradicts itself, 7% vs 8% for STOK Strong) — ABV will remain manual/brewery-sourced for the foreseeable future

**Phase 3 — Ongoing field verification (15-20 hrs/month, indefinite).** Physical shelf walks across Bangalore + Mysuru/Mangaluru/Hubballi to catch regional and imported SKUs that never appear online (this is literally how Volza's data shows small imported lots — Tusker, Saigon Export, Cheetah — entering India; nothing in your digital sources will reliably surface these before they're on a shelf).

**Total: ~80-120 combined founder+AI hours over 6-8 weeks to responsibly reach 500 SKUs with real Karnataka pricing.** Treat "1,000 SKUs" as a 4-5 month program, not a sprint, and only if you also expand scope as noted above.

## 4. Manual vs semi-automated vs fully automated

**Fully automated (build once, ~1-3 hrs/month upkeep):**
- Madhuloka category scrape — Odoo, server-rendered HTML, permissive robots.txt, no bot protection observed; cron nightly
- onlinealcohol.in via its live WooCommerce Store API — cleanest JSON of anything found; cron nightly
- Open Food Facts API pull for GTIN/barcode enrichment — free, ODbL-licensed, commercially reusable with attribution; weekly
- KSBCL price list, once you've re-identified the exact page/endpoint that produced your 18 rows — likely monthly (tied to duty/price revision cycles)

**Semi-automated (needs a human in the loop):**
- beerbasket.in HTML scrape — JSON API is broken (500 errors), and the site is full of SEO-mill cruft (hundreds of near-duplicate "/alcohol-delivery-in-<city>" pages including *US* city names) — automate the fetch, but a human must sanity-check every batch
- Tonique's static price table — stale (2023 timestamp, "price list coming soon" placeholder text still embedded) — never trust without cross-check
- Brand official sites (UB, Carlsberg, Heineken, AB InBev) for ABV/style/launch metadata — age-gates and Cloudflare cookies mean scrapers need session/cookie handling, and layouts will drift; review each new page manually
- Cross-source dedup/entity resolution — AI-assisted fuzzy matching, but a human must approve merges (e.g., is "Carlsberg Smooth" on carlsbergindia.com the same product as "Carlsberg Smooth Draught" on the global catalog, listed with a different ABV and Malaysian origin? Your own research flagged this as unresolved.)

**Fully manual (no automation path exists today):**
- Getting KSBCL's complete official list beyond whatever partial page you've found — likely requires a direct ask or RTI-style request, not a scraper
- ABV data — no retail site reliably has it; must come from breweries directly
- Physical retail shelf audits for regional/imported SKUs
- GS1/DataKart access — GS1 India's GTIN validation and DataKart bulk access are manual/email-based (`registration@gs1india.org`, `implementation@gs1india.org`), no public API, pricing not published
- Resolving self-contradicting source data (STOK's own product page vs. its own FAQ disagreeing on ABV for STOK Strong)

## 5. Throughput model

- **Weeks 1-2 (digital harvest sprint):** 15-25 net-new verified SKUs/day → +250-300 for the month, reaching ~470-500 cumulative
- **Weeks 3-6 (outreach ramps up, digital sources exhausted):** 5-10 SKUs/day, driven by distributor/brewery responses rather than scraping → +100-150, reaching ~600-650
- **Month 3+ (maintenance + field verification):** 1-3 SKUs per store visit or brewery call; diminishing returns digitally → +50-100/month
- Getting cleanly to 1,000 on a single founder's time is a **4-5 month program**, and only if you either add a second person for field verification or expand scope to include non-alcoholic malt lines and historical/discontinued SKUs.

## 6. Partnership and outreach playbook (ranked by leverage)

1. **KSBCL** — highest leverage, bar none. It's Karnataka's sole govt wholesale distributor for beer; its Supplier-wise Item-wise Price List is the closest thing to ground truth for the entire legal SKU universe with official MRP. Since your catalog already has 18 rows sourced to this list, first re-trace exactly how those were obtained and scale it. If it's not a clean public page, retail licensees (CL2/CL9 holders) already receive this list electronically — cultivating one retailer relationship (e.g., Madhuloka, since they're already your best digital source) to share or corroborate the KSBCL feed could be faster than a formal government request.
2. **Distributors/C&F agents for UB, Carlsberg India, AB InBev** — each maintains its own current SKU+MRP+scheme sheet for retailer ordering. Two or three of these relationships would give you near-real-time new-launch visibility before shelf (UB already files SEBI Regulation 30 disclosures for every Karnataka launch at `unitedbreweries.com/pdf/Material Events/` — worth monitoring that folder directly, it's the single richest structured official source found in this research, giving exact launch dates, categories, and even per-SKU pricing in the Kingfisher Smooth filing).
3. **Craft/local breweries (Simba/Sona Beverages, Geist, Toit, Arbor)** — smaller, less bureaucratic, more likely to just hand you a spec sheet. Note Arbor's packaged retail beer is explicitly Goa-only per their own site, despite a Bengaluru taproom — worth confirming directly with them whether that's still true.
4. **Carlsberg India (Mysuru brewery)** — they just announced a ₹100 crore can-line investment and a further ₹350 crore Invest Karnataka 2025 pledge; a Karnataka-native data startup is a plausible local-partnership story for their comms/govt-relations team.
5. **Bira91/B9 Beverages** — their official domain (`bira91.com`) is currently broken (serving an Apache default page with a mismatched TLS cert), so their digital presence is a gap you can't fill by scraping — worth a direct outreach, they may not even know their own site is down.
6. **GS1 India** — for GTIN/barcode legitimacy; no brewery in this research publishes barcodes on its own site, so this is a real, confirmed gap. Contact `registration@gs1india.org` about a DataKart-for-Solution-Providers arrangement; pricing isn't public but as a narrow vertical player you may get a better rate than a generic lookup service.
7. **Volza** — a 7-day free trial scoped to India + HSN 2203 (beer) could function as an early-warning system for new imported brands before they hit KSBCL/retail (its free preview already showed real product names: Tusker, Saigon Export, Cheetah, Camel, Abest). Budget ~$1,500-4,500/yr if it proves out. Get counsel comfortable with Section 135AA of the Customs Act (2022, criminalizes unauthorized publication of importer-identity trade data) before republishing anything beyond product names.
8. **Open Food Facts** — not a partnership, but contribute back: fix the mistagged entries you've already found (a Cadbury bar tagged "Beers"; "Bira 91" not matching because OFF only has the brand tag "Bira") — cheap goodwill, and it improves a source you're already drawing from.

## 7. Immediate next 5 actions

1. Re-trace exactly how the 18 KSBCL rows were sourced and attempt to scale that to the full list — highest ROI action available this week.
2. Run a dedup/merge pass on the existing 216 rows before adding anything new (you're currently overcounting by ~15-20 rows).
3. Finish the cheap, already-proven-clean sources: Madhuloka's remaining pages, onlinealcohol.in's JSON API.
4. Draft outreach to 2-3 Karnataka beer distributors and Madhuloka for a data-sharing relationship — this is the fastest path past the ~400 SKU digital ceiling.
5. Flag internally that ABV, GTIN, and "authoritative Karnataka MRP for anything beyond KSBCL/Madhuloka" are manual/relationship problems, not scraping problems — don't burn more engineering hours trying to automate around them.