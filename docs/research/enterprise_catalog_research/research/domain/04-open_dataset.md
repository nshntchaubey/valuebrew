# Domain Research: Open datasets for Karnataka/Indian beer product database (ValueBrew research)

**Research track:** `open_dataset`

## Summary
Open Food Facts (OFF) is the only source that actually contains verified Indian beer product entries — confirmed via live API queries on 2026-08-05, including "Kingfisher Beer" (barcode 8905002180007) and "Boom" by Bira (barcode 8908005126324), plus roughly a dozen other India-tagged beer products, out of 22,320 total India-tagged products on OFF. Coverage of Indian beer specifically is thin and data quality varies (e.g. the Kingfisher entry has no ABV or nutriment fields filled in, and some products are mistagged into the Beers category). OFF is ODbL/DBCL licensed, commercially reusable with attribution, updated nightly. "Open Product Data" (OKFN's product.okfn.org / product-open-data.com project) is defunct — its homepage returns a 504 gateway timeout and its GitHub repos have had no real activity since ~2015. Kaggle has no Karnataka-specific beer/alcohol dataset, but one directly relevant find is the Kerala BEVCO Liquor Price List (2025-2026) dataset (CC0, government-sourced, includes beer pricing, ~4,300 items, verified via Kaggle's public dataset-view API) — useful as a structural template even though it covers Kerala, not Karnataka. GitHub searches turned up no maintained Indian-beer or Indian-FMCG-product barcode datasets. data.gov.in returned "No Result" for searches on beer, alcohol, liquor, excise, and Karnataka excise — confirming no relevant Indian government open dataset is currently published there. Karnataka's own excise department website could not be reached (DNS failure) so it remains an unverified gap.

## Sources
### Open Food Facts (world.openfoodfacts.org)
- URL: https://world.openfoodfacts.org/product/8905002180007/kingfisher-beer
- Confidence: High
- Coverage: Global open food/beverage database. Verified live: "Kingfisher Beer" entry exists (brand Kingfisher, country India, quantity 650ml, category Lagers, barcode 8905002180007). ABV/nutriments/price fields are empty on this entry. Combined keyword ("beer") + country=India search via legacy API (https://world.openfoodfacts.org/cgi/search.pl) returned 26 hits, of which ~14 were genuinely beer-category after manual filtering (some hits mistagged, e.g. a Cadbury chocolate bar tagged "Beers"). Confirmed additional India beer entries: "Boom" by Bira (8908005126324, category Beers, country India, via https://world.openfoodfacts.org/api/v2/product/8908005126324.json), Tuborg Strong Beer, Budweiser (India), Haywards, Anchor White, Kimaya Himalayan "yavira." Total India-tagged products on OFF (any category): 22,320, verified via CGI search count field.
- Reliability: Medium — API was intermittently unstable during this session (multiple "Page temporarily unavailable"/"Unscheduled downtime" responses on retries); succeeded on repeated attempts. All reported data came from calls that returned valid JSON.
- Licensing: Verified via https://world.openfoodfacts.org/terms-of-use: Database structure under Open Database License (ODbL) 1.0; individual contents under Database Contents License (DBCL) 1.0; images under CC BY-SA 3.0. Explicitly permits commercial use with attribution and share-alike on derivatives.
- Automation Difficulty: Low for single-product lookups (stable JSON API); Medium for bulk/filtered queries — the newer search-a-licious endpoint (search.openfoodfacts.org) gave inconsistent results (0 or all-10000) for certain filter combinations, while the legacy cgi/search.pl endpoint was reliable for tag-filtered queries.
- Refresh Frequency: Nightly dumps/exports per OFF's official /data page (verified via fetch).
- Notes: "Bira91"/"Bira 91" text search returned no direct matches; only the brand tag "Bira" (on product "Boom") was found. Worth noting for ValueBrew's own search/matching design.

### Open Product Data (OKFN product-open-data.com / product.okfn.org)
- URL: https://github.com/rufuspollock-okfn/opd-product-browser-web
- Confidence: High
- Coverage: Historical OKFN project for a general public barcode/product database (not food- or alcohol-specific). No live, queryable dataset found today.
- Reliability: Low — homepage http://www.product-open-data.com/ returned HTTP 504 on direct curl (2026-08-05); http://product.okfn.org returned a 301 redirect with no confirmed working destination.
- Licensing: No license set on the main opd-product-browser-web repo (license field null per GitHub API); a sibling admin-tooling repo is MIT but that's not the data itself.
- Automation Difficulty: N/A — no live endpoint found.
- Refresh Frequency: None — inactive since ~2015 (repo pushed_at 2015-04-24 per GitHub API).
- Notes: Inference (not direct confirmation) that the project was formally discontinued — based on dead homepage plus stale repo timestamps.

### Kaggle: Kerala BEVCO Liquor Price List (2025-2026)
- URL: https://www.kaggle.com/datasets/tolstoyjustin/kerala-bevco-liquor-price-list-2025-2026
- Confidence: High
- Coverage: Verified via Kaggle's public dataset-view API: official 2025-2026 price list from Kerala State Beverages Corporation (BEVCO), covering FMFL, IMFL, Beer, and Wine — over 4,300 unique items with Item Code, Brand/Description, Volume(ml), Landed Cost, Import Fee, Special Fee, Cess, Warehouse Price, Shop Price (MRP). This is Kerala, NOT Karnataka — no equivalent Karnataka dataset found on Kaggle after searching "karnataka liquor" and "karnataka" broadly.
- Reliability: High confidence in the metadata (directly fetched via API); did NOT download/inspect the actual CSV contents, so exact beer-brand coverage (e.g. Kingfisher/Bira presence) is unverified.
- Licensing: CC0: Public Domain (verified via API field licenseNameNullable).
- Automation Difficulty: Low — Kaggle's public list/view API worked without authentication; downloading the actual file would require a Kaggle API token (not attempted).
- Refresh Frequency: Unclear, likely annual (tied to state price-circular cycle); not explicitly stated in metadata.

### Kaggle: general beer-related datasets (search results)
- URL: https://www.kaggle.com/datasets/rdoume/beerreviews
- Confidence: High
- Coverage: Verified via Kaggle public search API: ~20 beer-related datasets exist but nearly all are Western/craft-beer review or production datasets (Beer Reviews, Brewer's Friend Beer Recipes, Craft Beers Dataset, Beer Production, Beer Profile and Ratings, etc). None focus on India or Karnataka. Direct searches for "Kingfisher" and "Bira91" returned zero relevant results (Kingfisher search returned only unrelated bird-species datasets).
- Reliability: High — public API accessible without auth barrier during this session.
- Licensing: Mixed per-dataset (CC0, ODbL/DBCL, CC BY 4.0, Apache 2.0, or "Unknown") — verified via API licenseNameNullable field per dataset.
- Automation Difficulty: Low — api/v1/datasets/list endpoint accessible without authentication for search/listing.

### GitHub public repositories (beer / Indian FMCG / Karnataka excise search)
- URL: https://github.com/brewdega/open-beer-database-dumps
- Confidence: High
- Coverage: Searched via GitHub search API for: "beer india dataset," "indian beer dataset," "open beer database," "FMCG india dataset," "karnataka excise," "excise india dataset," "kingfisher bira beer." Found only generic Western open-beer-database projects (e.g. open-beer-database-dumps: 32 stars, last pushed 2012-08-18, license null per GitHub API), generic unrelated FMCG dashboard repos, and one "Karnataka_excise_Licences" repo that on inspection is just a minimal HTML/README web-app shell (5 commits, no license, no beer-brand content) — not a real dataset.
- Reliability: Medium — hit GitHub's unauthenticated API rate limit (60 req/hr) partway through, so a few planned follow-up queries could not run; completed queries returned consistent, verifiable results.
- Licensing: Varies per repo; the closest "open beer database" repo has license=null.
- Automation Difficulty: Medium — GitHub's public search API is easy to call but rate-limited (60/hr) without a token.

### data.gov.in (Government of India Open Data Platform)
- URL: https://www.data.gov.in/search?title=beer
- Confidence: High
- Coverage: Directly fetched search-results pages for "beer," "alcohol," "liquor," "excise," "Karnataka excise," and "Karnataka" — every one returned the literal text "No Result" in the HTML (verified by grep on fetched HTML, HTTP 200 responses). No relevant dataset currently exists on this platform.
- Reliability: High — direct page fetch with HTTP 200 and explicit "No Result" text confirmed in returned HTML.
- Licensing: N/A — no dataset found.
- Automation Difficulty: Medium — bare domain data.gov.in issues a 302 redirect to www.data.gov.in and seems to want a standard browser User-Agent header; otherwise scriptable via simple GET requests.
- Notes: Karnataka's own excise department site (excise.karnataka.gov.in) could not be reached at all — DNS resolution failed from this sandbox ("Could not resolve host"). Unverified either way; flagged under unverifiable_or_blocked.

## Key Findings
- Open Food Facts DOES contain real Indian beer entries, directly verified: "Kingfisher Beer" at https://world.openfoodfacts.org/product/8905002180007/kingfisher-beer (barcode 8905002180007, category "Lagers," country India, 650ml) and "Boom" by Bira at https://world.openfoodfacts.org/product/8908005126324/boom (barcode 8908005126324, category "Beers," country India).
- A combined keyword+country-tag search on OFF ("beer" + countries=India) returned exactly 26 raw hits, of which roughly 14 were genuinely beer-category products after manual filtering; the rest were mistagged or irrelevant (e.g., a Cadbury chocolate bar erroneously carrying the "Beers" category tag) — a real, verified data-quality/tagging issue.
- No OFF entries found under a plain "Bira91" or "Bira 91" text search — only the brand tag "Bira" (on the "Boom" product) surfaced; a naming/search-matching gap worth noting for ValueBrew's own search UX design.
- Open Food Facts data is licensed ODbL (structure) + DBCL (contents) + CC BY-SA (images), explicitly commercial-use-friendly with attribution — directly quoted from https://world.openfoodfacts.org/terms-of-use.
- "Open Product Data" (the OKFN project referenced in the brief) is effectively dead: its homepage (product-open-data.com) returned HTTP 504 on direct fetch, and its GitHub code hasn't been meaningfully updated since ~2015.
- Kaggle has no Karnataka-specific beer dataset, but does have a high-quality, CC0-licensed, government-sourced Kerala BEVCO liquor price list (2025-2026) covering beer/IMFL/wine pricing for ~4,300 items — a useful structural template even though it's the wrong state.
- data.gov.in (India's official open data portal) returned literal "No Result" for every alcohol/beer/excise-related search term tried, including "Karnataka excise" — confirming no official Indian government open dataset on beer/alcohol products currently exists on that platform.
- No maintained GitHub repository combining "Indian beer" with structured product data (brand, ABV, barcode, price) was found; existing "open beer database" GitHub projects are all Western/craft-beer-focused and largely dormant (last activity 2012-2023).

## Risks
- OFF's Indian beer coverage is thin and inconsistently tagged — ValueBrew cannot rely on OFF alone for a comprehensive Karnataka beer catalog; would need supplementing with manual/scraped data from retailers, brand sites, or state excise price circulars.
- OFF's API showed intermittent outages and rate-limiting during this research session (multiple "Page temporarily unavailable"/"Unscheduled downtime" responses) — any production integration should include retry logic and not assume 100% uptime.
- The newer search-a-licious OFF search endpoint behaved unpredictably with certain filter combinations (returning 0 or all-10000 results) — the older cgi/search.pl legacy endpoint was more reliable for tag-filtered queries; this inconsistency could silently produce wrong "zero results" answers if not caught.
- No confirmed source at all for Karnataka-specific excise/price data; the only comparable government-sourced dataset found (Kerala BEVCO on Kaggle) is for a different state and its applicability to Karnataka pricing/brands is unverified.
- GitHub API rate-limiting (unauthenticated, 60 req/hr) was hit during research, meaning a small number of planned follow-up searches were not completed — a low-probability chance a relevant niche repo was missed.

## Unverifiable / Blocked
- Karnataka Excise Department's own website (excise.karnataka.gov.in) could not be reached — DNS resolution failed from this environment. Could not verify whether Karnataka publishes its own open price list/dataset the way Kerala BEVCO does.
- Did not download or inspect the actual CSV/file contents of the Kerala BEVCO Kaggle dataset — only its metadata/description was verified via the Kaggle API, so exact brand-level coverage (e.g., presence of Kingfisher/Bira SKUs) within that file is unconfirmed.
- Precise total count of OFF products simultaneously tagged category="Beers" AND country="India" could not be obtained — repeated attempts to query this combined filter via both the legacy and search-a-licious APIs failed or were rate-limited; the reported ~14-26 figure comes from a keyword-based ("beer" text search + India country filter) query, not a strict category+country tag intersection.
- Could not determine whether Open Food Facts' "Bira91" brand gap is due to the brand simply not having been contributed yet, versus being present under an unindexed/different tag — no direct way to enumerate all brand tags was found working within the session's rate limits.
