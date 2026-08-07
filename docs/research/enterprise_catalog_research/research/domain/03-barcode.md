# Domain Research: Barcode/GTIN identifier sources for Indian beer SKUs (GS1 India, DataKart, UPCitemdb, Go-UPC, Barcode Lookup, Open Food Facts)

**Research track:** `barcode`

## Summary
GS1 India (via gs1india.org) is the sole authority issuing "890"-prefixed GTINs in India and confirmed real, tiered registration fees (verified from an official PDF: e.g. ~Rs 48,135 for 100 barcodes/1 year at the lowest turnover slab, up to ~Rs 324,146 for 100,000 barcodes/10 years at the highest slab) — but it is a registration/issuance system for brand owners, not a public lookup API, and its FAQ/registration pages contain no mention of alcohol, beer, or excise-specific rules or exclusions. DataKart is GS1 India's own national product-data repository (free + "Premium" paid tier) fed by brand owners' uploads and integrated with the global GS1 Cloud registry; it has no documented public API and third-party commercial lookup access requires contacting GS1 India directly ("DataKart for Retailers/Solution Providers" subscription) — pricing not published. Among generic lookup APIs, UPCitemdb (free/DEV $99/PRO $699 per month, verified via its live docs) returned zero matches for four real Indian beer GTINs, while Go-UPC (paid tiers $74.95–$795/month, verified via its own site) matched 4 of 5 tested Indian beer barcodes, apparently because such regional/niche products get into its index via crowdsourced or aggregator sources rather than direct GS1/manufacturer feeds. Barcode Lookup (barcodelookup.com) could not be verified at all — it blocked both automated fetch and curl with a bot-detection wall, so its actual India/beer coverage and pricing are unconfirmed. The most concretely verified evidence of real Indian beer GTINs in the wild came from Open Food Facts (a free, open, ODbL-licensed, non-profit, crowdsourced database), which returned confirmed, live records for Kingfisher (8905002180007), Tuborg Strong (8906018940104), Budweiser India variants, Bira 91 Boom (8908005126324), and several Coolberg non-alcoholic beers — 26 India-tagged "beer" search hits total in one query — giving ValueBrew a free, commercially reusable (with attribution/share-alike) starting corpus, though its data is crowdsourced and not guaranteed accurate/complete by its own terms.

## Sources
### GS1 India — official site (homepage)
- URL: https://www.gs1india.org
- Confidence: High
- Coverage: National (India) GTIN issuance authority, not a product-lookup database
- Reliability: Official government-linked standards body
- Refresh Frequency: unknown
- Notes: Verified via direct fetch. Confirms GS1 India is the Ministry of Commerce/Industry-backed sole issuer of '890'-prefix barcodes in India; links to registration and GTIN-validation services. No pricing or alcohol/beer info on this page.

### GS1 India — Register for Barcodes page
- URL: https://www.gs1india.org/register-for-barcodes
- Confidence: High
- Licensing: N/A — registration service, not data licensing
- Recommendation: Primary route for ValueBrew or beer manufacturers to obtain/verify GTIN registration status, but does not provide third-party lookup
- Notes: Verified via direct fetch (curl). Describes the 4-part fee structure (registration + subscription + refundable security deposit + GST) and links to the actual current fee-structure PDF. No mention of alcohol/liquor/beer/excise/FSSAI anywhere on the page (checked via keyword search of full page text — all absent).

### GS1 India Barcode/GCP Fee Structure PDF (effective 1 Oct 2025)
- URL: https://admin.gs1india.org/uploads/GCP_Barcodes_Fee_structure_effective_from_Oct_2025_34e8624051.pdf
- Confidence: High
- Refresh Frequency: Stated 'effective from 1st Oct 2025' — will need re-check periodically as GS1 India revises fees
- Notes: Verified by directly reading the PDF (5 pages). Contains full fee tables by annual turnover slab (10 slabs, Rs 5 crore to >1000 crore), barcode-capacity tier (100/1,000/10,000/100,000 GTINs) and subscription duration (1/2/3/5/10 years). Example real figures: 100 barcodes/1yr/turnover up to Rs 5 crore = Rs 48,135 total (Rs 26,000 registration + Rs 12,250 subscription + Rs 6,885 GST(18%) + Rs 3,000 security deposit); 100,000 barcodes/10yr/turnover >Rs 1000 crore = Rs 324,146 total (10-year tier drops the security deposit).

### GS1 India — DataKart service page
- URL: https://www.gs1india.org/services/datakart
- Confidence: High
- Licensing: Not publicly documented; brand owners upload their own data
- Recommendation: Contact GS1 India (implementation@gs1india.org / registration@gs1india.org) to negotiate a 'DataKart for Solution Providers' commercial data-access arrangement — pricing/terms not public
- Notes: Verified via direct fetch. DataKart is GS1 India's national product-data repository, integrated with global GS1 Cloud; free basic tier plus paid 'DataKart Premium' (adds Digital Link QR, FSSAI license mapping, better search ranking). No public API documented; no alcohol/beer-specific info; no published quantitative coverage stats found on this page.

### GS1 India — GTIN Validation service page
- URL: https://www.gs1india.org/services/gtin-validation
- Confidence: High
- Automation Difficulty: High for programmatic/API use — appears to be a manual web form + email-based bulk process, not a documented REST API
- Notes: Verified via direct fetch. Single-GTIN validation is available via a web widget (example shown: '9506000140445'); bulk validation requires emailing GS1 India an Excel list. Requires subscribing to 'DataKart for Retailers' for ongoing/bulk access. No published pricing, rate limits, or third-party commercial-use terms found.

### UPCitemdb — API documentation/pricing (devs.upcitemdb.com, plan page)
- URL: https://www.upcitemdb.com/wp/docs/main/development/plan/
- Confidence: High
- Coverage: Confirmed NO coverage for the 4 Indian beer barcodes tested — claims 718M+ global UPC/EAN entries overall but this did not translate to Indian beer coverage in this sample
- Reliability: Established/long-running lookup service, but this specific vertical (Indian beer) is a coverage gap
- Licensing: Non-refundable monthly subscription; ToS (fetched from upcitemdb.com/terms) grants a 'limited, non-exclusive, non-transferable' license for the customer's own operations — did not find explicit resale/redistribution prohibition language in the excerpt retrieved, but standard SaaS terms imply no redistribution rights
- Notes: Verified via direct fetch and via live API test calls (curl against api.upcitemdb.com/prod/trial/lookup). Plans: FREE (100 lookups/day, 20 searches/day, no signup), DEV ($99/month, 20,000 lookups/day), PRO ($699/month, 150,000 lookups/day) — dollar figures verified via a separate fetch of devs.upcitemdb.com. Live test: looked up 4 confirmed real Indian beer GTINs (Kingfisher 8905002180007, Tuborg 8906018940104, Budweiser-India 8902246004984, Bira91 8908005126324) — all returned zero matches ("total":0).

### Go-UPC — Barcode API pricing page
- URL: https://go-upc.com/api
- Confidence: High
- Coverage: Partial but meaningfully better than UPCitemdb for this Indian-beer sample (4/5 vs 0/4) — inferred (not confirmed) that Go-UPC aggregates from crowdsourced/open sources similar to Open Food Facts rather than direct GS1 feeds
- Reliability: Medium-High for coverage; but commercial redistribution use is explicitly restricted by ToS
- Licensing: Verified via fetch of go-upc.com/terms-and-conditions/ (dated 19 Mar 2025): explicitly PROHIBITS reselling, redistributing, or making the Service or Product Data publicly available, and prohibits replicating/mimicking the UI; data is 'a limited, non-exclusive subscription' with no ownership transfer — meaningful constraint for ValueBrew if the intent is to republish barcode data in its own database
- Notes: Verified via direct fetch. Tiers: Developer $74.95/mo (5,000 req/mo), Startup $245/mo (45,000 req/mo), Enterprise $795/mo (450,000 req/mo). Live coverage test via curl against go-upc.com/search for 5 real Indian beer GTINs found via Open Food Facts: matched Tuborg Strong (8906018940104), Budweiser 0.0 Non-Alcoholic (8902246004984), Bira 91 Boom (8908005126324), Coolberg Mint (8906144570480) — 4/5 found; Kingfisher (8905002180007) returned 'Product Not Found'.

### Barcode Lookup (barcodelookup.com)
- URL: https://www.barcodelookup.com
- Confidence: Low
- Notes: UNVERIFIED — every attempt to fetch this site (both WebFetch and direct curl with browser User-Agent) returned HTTP 403 with a 'Security Verification' bot-block page. Could not confirm pricing, coverage, India/alcohol category support, or licensing terms. Any claims about this service found elsewhere should be treated as unverified.

### Open Food Facts (world.openfoodfacts.org) — free/open crowdsourced product database
- URL: https://world.openfoodfacts.org
- Confidence: High
- Coverage: Confirmed non-zero, real coverage of Indian beer SKUs incl. major national brands (Kingfisher/United Breweries, Tuborg/Carlsberg India, Budweiser/AB InBev India) and craft brand Bira 91; craft brand 'Bira 91' searched by that exact term returned 0 results (the correct listed brand name in OFF is 'Bira', not 'Bira 91') — a naming/normalization caveat
- Reliability: Crowdsourced, non-profit; site's own terms explicitly disclaim guarantee of accuracy/completeness — data should be treated as a useful seed/cross-reference, not authoritative
- Licensing: Verified via fetch of world.openfoodfacts.org/terms-of-use: database structure under Open Database License (ODbL), individual data contents under Database Contents License, images under CC BY-SA — all explicitly described as free licenses permitting commercial use and reproduction, subject to attribution and share-alike for derivative works.
- Automation Difficulty: Low — simple documented REST/JSON API, rate-limited (encountered intermittent 503s without a descriptive User-Agent header; a real, identifying UA is recommended per site guidance of '1 API call = 1 real scan')
- Recommendation: Best currently-verified free, commercially-reusable data source for cross-referencing Indian beer GTINs; ValueBrew should treat it as a bootstrap/seed source, not a sole source of truth, and should independently verify against manufacturer packaging/GS1 registration where stakes are high
- Notes: Verified via multiple direct JSON API calls (curl with a custom User-Agent, since default UA got 503s). Confirmed live records including exact GTIN/EAN 8905002180007 for 'Kingfisher Beer' (brand: Kingfisher, categories: en:beers > en:lagers, countries: India) fetched via /api/v2/product/{code}.json. A country+keyword search (search_terms=beer, countries contains india, page_size=50) returned count=26 India-tagged results including Kingfisher, Tuborg (2 SKUs), Budweiser India (2 SKUs), Bira 91 Boom, several Coolberg non-alcoholic 'beers', Ginsberg, Haywards, Yavira, and others — with real EAN/GTIN codes attached to nearly all.

### Wikipedia — List of GS1 country codes
- URL: https://en.wikipedia.org/wiki/List_of_GS1_country_codes
- Confidence: Medium
- Reliability: Wikipedia — generally reliable for this kind of standardized reference fact but not a primary GS1 source; cross-checked against gs1india.org's own claim of being 'the only authorised body...to provide barcodes starting with 890', which matches
- Notes: Verified via direct fetch. Confirms India's GS1 prefix is '890' (single 3-digit prefix, not a numeric range) — useful for ValueBrew to sanity-check that a barcode is India-issued by checking the first 3 digits.

## Key Findings
- GS1 India confirmed as sole official Indian GTIN-issuing body (prefix 890); registration fees are real, tiered by turnover and barcode volume, and were directly read from GS1 India's own current fee-structure PDF (effective 1 Oct 2025) — e.g. Rs 48,135 total for the smallest package (100 barcodes, 1 year, turnover ≤Rs5 crore) up to Rs 324,146 for the largest (100,000 barcodes, 10 years, turnover >Rs1000 crore).
- No mention of alcohol, liquor, beer, or excise-specific rules, exclusions, or special procedures was found anywhere in GS1 India's registration, FAQ, or GTIN-validation pages that were fetched — inference (not stated by GS1 India) is that beer/alcohol manufacturers register GTINs through the same general process as any other FMCG brand owner, with excise licensing handled separately by state authorities (e.g. Karnataka State Excise / KSBCL) outside the GS1 system.
- DataKart is GS1 India's own repository (fed by brand-owner uploads, synced to global GS1 Cloud) and is the closest thing to an 'official' Indian product/GTIN database, but it has no public API and third-party commercial access (e.g., for a startup like ValueBrew) requires a paid 'DataKart for Solution Providers'-type subscription whose price is not published online and must be negotiated directly with GS1 India.
- Real, verified evidence that Indian beer manufacturers DO register/use GS1 GTINs in practice: found live, valid-looking barcodes on Open Food Facts for Kingfisher (United Breweries), Tuborg (Carlsberg India), Budweiser India (AB InBev), Bira 91, and Coolberg (non-alcoholic beer) — all using the correct '890'-prefixed Indian GS1 numbering.
- Among generic commercial barcode-lookup APIs tested live: UPCitemdb had ZERO coverage of 4 confirmed Indian beer GTINs despite claiming 718M+ global entries; Go-UPC had partial coverage (4 of 5 Indian beer GTINs matched) but Go-UPC's own Terms and Conditions explicitly prohibit reselling/redistributing/making the product data publicly available — a material constraint if ValueBrew wants to build and republish its own barcode-linked database using Go-UPC data.
- Barcode Lookup (barcodelookup.com) could not be evaluated at all due to bot-blocking (403 on every fetch attempt, browser UA included) — this is a real gap in the research, not a finding about the service itself.
- Open Food Facts is presently the strongest verified free option: ODbL/CC-BY-SA licensed, explicitly commercial-use-permitted, live API confirmed working, and directly returned real Indian beer product/GTIN records — but it is crowdsourced with no completeness/accuracy guarantee (stated explicitly in its own terms) and would need to be supplemented/verified, not relied on alone.

## Risks
- GS1 India's registration process is for brand owners issuing their own GTINs — it is NOT a lookup/verification service for a third party like ValueBrew to identify already-existing SKUs; ValueBrew cannot use GS1 India registration to build a lookup database, only DataKart (paid, terms undisclosed) offers that.
- Commercial lookup APIs (UPCitemdb, Go-UPC) have real, verified gaps or restrictions for this specific vertical: UPCitemdb showed 0% coverage on the small Indian-beer sample tested, and Go-UPC's ToS forbid redistributing the data it returns — building ValueBrew's own resellable/shareable database directly from Go-UPC data would likely violate its terms.
- Barcode Lookup's coverage, pricing, and terms remain completely unverified due to bot-blocking; do not assume any characteristics about it without separate verification (e.g., via an official paid account or a different access method).
- Open Food Facts data is community-contributed and its own terms disclaim accuracy/completeness guarantees; the absence of a product (e.g., no 'Bira 91' hit until searched as 'Bira') does not mean the product lacks a real GTIN — it may simply not be catalogued yet, so absence-of-evidence is not evidence-of-absence.
- Alcohol/excise product data intersects with state excise regulation (e.g., Karnataka State Beverages Corporation Ltd, KSBCL) which is a wholly separate regulatory/distribution system from GS1 barcoding — this research did not find any formal linkage or requirement connecting GS1 GTIN registration to state excise licensing, and that gap was not resolved (see unverifiable_or_blocked).
- GS1 India fee structure is dated 'effective from 1st Oct 2025' and is explicitly subject to revision — any pricing quoted should be re-verified against the live PDF link before being used in a business plan, as GS1 India revises this periodically.

## Unverifiable / Blocked
- Barcode Lookup (barcodelookup.com) pricing, coverage, and licensing terms — blocked by bot-detection (403 'Security Verification') on every fetch attempt (WebFetch and curl with browser User-Agent).
- Whether GS1 India has any formal linkage, exemption, or special process for alcohol/beer/excise goods specifically — no such language was found on any GS1 India page fetched (register-for-barcodes, GTIN-validation, DataKart, homepage), so this appears to be simply unaddressed publicly, not confirmed either way.
- Exact pricing for GS1 India's DataKart for Retailers/Solution Providers commercial subscription (needed for third-party lookup access) — not published online; GS1 India directs inquiries to registration@gs1india.org / implementation@gs1india.org.
- Total product/brand/company counts in DataKart (GS1 India's own repository) — the page references icons for 'companies' and 'products listed' but no actual numbers were rendered in the fetched text.
- Whether Kingfisher's absence from Go-UPC (while present on Open Food Facts) reflects a genuine data gap in Go-UPC's index or a transient/lookup-specific issue — only a single query was tested per barcode; not exhaustively re-tested.
- Could not run a live enterprise/internal web search tool (the plugin_search_search__search tool repeatedly returned 'Token expired or invalid' errors) — relied on WebFetch, direct curl, and a browser tool instead; some breadth of general web search (e.g., for other regional barcode-lookup vendors beyond the ones named in the brief) was not attempted as a result.
