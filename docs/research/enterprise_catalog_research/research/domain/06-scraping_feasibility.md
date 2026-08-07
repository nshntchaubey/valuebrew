# Domain Research: Karnataka beer database — web scraping feasibility of retail/brand/regulatory source sites

**Research track:** `scraping_feasibility`

## Summary
I fetched robots.txt and homepage/product HTML for each requested source directly (curl/WebFetch) on 2026-08-05. Two sources — madhuloka.com and KSBCL's official govt site — are realistic, low-to-medium-effort scraping targets: madhuloka.com is a server-rendered Odoo storefront with visible beer SKUs, prices, brand, and size in raw HTML, no Cloudflare/CAPTCHA observed. KSBCL's real site is ksbcl.karnataka.gov.in (ksbcl.com 301-redirects there), a plain government portal with an open robots.txt, but I found no visible retail price-list/product pages on the crawled pages — only PDFs (e.g., duty slabs) — so it is more useful for regulatory/duty data than SKU-level beer data, and would need PDF parsing. livingliquidz.com was unreachable — every request (multiple retries, with and without www) returned HTTP 503 "App Under Development," so I could not evaluate its scraping surface at all. Corporate brand sites (unitedbreweries.com, carlsbergindia.com, heineken.com/in, abinbevindia.in) are marketing sites, not e-commerce/pricing sources: they are server-rendered (Drupal/Umbraco/WordPress) so BeautifulSoup-class tools would technically work, but United Breweries is Cloudflare-fronted with a mandatory Drupal age-gate form (cookie/CSRF token, no JS challenge observed) and none of these four sites expose SKU-level pricing or ABV tables for individual beer products — they show brand names/marketing copy only. bira91.com is not reachable as the Bira 91 site: it consistently returned an Apache2 "It works" default page over HTTPS with a certificate for an unrelated domain (*.ksmart.live), meaning the DNS record for bira91.com no longer points at Bira's actual infrastructure; I located www.bira91.beer and stores.bira91taproom.com as alternative candidates via search but did not verify them by direct fetch. www.kingfisherworld.com resolves but serves an unrelated third-party medical app ("GemGP"), not a Kingfisher beer site — I could not find a working kingfisherworld/kingfisherbeer property with beer content. www.heinekenindia.com could not be resolved by any DNS resolver I used (timed out); the working India-specific Heineken presence I actually verified is heineken.com/in/en/home, which redirected/loaded successfully.

## Sources
### Madhuloka (madhuloka.com)
- URL: https://www.madhuloka.com/shop/category/beer-3
- Confidence: High
- Coverage: Verified: robots.txt (200, allows all, lists sitemap.xml). Homepage, /shop, /shop/category/beer-3, and a product detail page (/shop/m000067-carlsberg-miracle-can-500-3401) all returned HTTP 200 with beer product names, prices in INR, brand, and size (e.g. 'Carlsberg India', '500 ml') present in the raw HTML from a plain curl request (no JS execution).
- Reliability: Server header identifies Odoo.sh; no Cloudflare/CAPTCHA/challenge markers observed in headers or body across ~6 fetches.
- Licensing: Not checked — robots.txt permits crawling broadly; no explicit scraping ToS reviewed.
- Automation Difficulty: Low-Medium. BeautifulSoup/requests sufficient — content is fully server-rendered. Pagination via ?page=N query param confirmed working. Category slugs discovered for beer and other alcohol types (beer-3, whisky-7, etc). No JSON API found. Estimate: ~8-16 hours to build a working scraper; low maintenance burden expected, estimate 1-3 hrs/month.
- Recommendation: Best candidate of all sources tested for SKU-level beer price/brand/size data. Recommend prioritizing as primary retail-price source.
- Notes: ABV not observed on the one product page checked (only Country/Brand/Size shown) — treat ABV as unverified for this source.

### KSBCL official site
- URL: https://ksbcl.karnataka.gov.in/
- Confidence: Medium
- Coverage: Verified: ksbcl.com returns HTTP 301 redirecting to https://ksbcl.karnataka.gov.in/ (confirmed via curl -I), and that target loads (HTTP 200) with Kannada-language government portal content. robots.txt at this domain is fully open ('Disallow:' empty). Found links to PDF documents (e.g. a 'duty slab' PDF) but did not locate a page listing individual beer SKUs/prices/ABV.
- Reliability: No anti-bot/Cloudflare signals observed; plain government CMS.
- Licensing: Government site — likely public information but no explicit terms reviewed.
- Automation Difficulty: Medium — HTML shell is simple/server-rendered, but useful data appears to be inside linked PDFs, requiring pdfplumber-style parsing. Estimate 16-30 hours including PDF parsing; maintenance effort uncertain (PDF structure not examined).
- Recommendation: Useful for regulatory/duty/excise reference data, not confirmed useful for per-SKU beer pricing. Flag for follow-up crawl of ERP/OFS login and supplier-list sub-pages.

### livingliquidz.com
- URL: https://www.livingliquidz.com/
- Confidence: High
- Coverage: Verified: every fetch attempt (www and non-www, multiple retries) returned HTTP 503 with an 'App Under Development / under maintenance' HTML page. robots.txt request also returned the same 503 maintenance page.
- Reliability: Consistent across retries — appears to be a genuine outage/maintenance state, not a bot block (no CAPTCHA/Cloudflare challenge markers).
- Automation Difficulty: Unknown/blocked — cannot assess DOM structure, anti-bot posture, or JS-rendering requirement while the site is down.
- Recommendation: Re-check later; cannot commit an effort estimate until the site is back up. Do not build against this source yet.

### United Breweries Limited (unitedbreweries.com)
- URL: https://www.unitedbreweries.com/our-brands
- Confidence: High
- Coverage: Verified: robots.txt (200) is a standard Drupal robots file. Homepage 302-redirects to /age-gate/1; the age-gate page and /our-brands both load as HTML (200) once past the redirect, but both are gated by a Drupal form (age_gate_thc_user_form) requiring a birthdate/country submission with a CSRF form_build_id token before real brand content is shown.
- Reliability: Cloudflare-fronted (server: cloudflare, cf-ray headers, __cf_bm and _cfuvid cookies present) but no JS 'checking your browser' challenge or CAPTCHA observed on direct curl requests — blocking mechanism observed was the Drupal age-gate form, not a bot-detection challenge.
- Automation Difficulty: Medium. Content is server-rendered (Drupal); scraper must programmatically submit the age-gate form (fetch form_build_id token, POST birthdate/country) and manage session cookies. Estimate: 12-20 hours; moderate maintenance risk if Cloudflare bot rules tighten.
- Recommendation: Corporate/brand marketing site — verified pages show brand names/marketing copy, not confirmed to contain per-SKU pricing or ABV tables. Useful for brand metadata only.

### Bira 91 (bira91.com)
- URL: https://bira91.com/
- Confidence: Medium
- Coverage: Verified: bira91.com resolves via DNS to 13.126.12.28 (AWS) and, on repeated HTTPS fetches, consistently returned an Apache2 Ubuntu default 'It works' page rather than a Bira 91 site. A TLS certificate check (openssl s_client) showed the certificate served is for '*.ksmart.live' — an unrelated domain — indicating bira91.com's current infrastructure is not (or no longer) Bira's actual site.
- Reliability: N/A — target site content not actually reachable at this URL as tested.
- Automation Difficulty: Cannot assess — no real Bira 91 content was retrievable at bira91.com in my testing.
- Recommendation: Do not build a scraper against bira91.com as given. Via search I found two unverified alternative candidate URLs that may be the current Bira 91 web presence: www.bira91.beer and stores.bira91taproom.com — these were NOT directly fetched/confirmed by me and must be independently verified before any engineering commitment.

### Kingfisher World (kingfisherworld.com)
- URL: https://www.kingfisherworld.com/
- Confidence: High
- Coverage: Verified: kingfisherworld.com resolves and returns HTTP 200, but the page title is 'GemGP' with meta description 'GemGP by VitalGems - General Practitioners Solutions' and author 'Health E-Solutions B.V.' — a medical/healthcare SaaS app, unrelated to Kingfisher beer.
- Reliability: Confirmed via direct fetch of both robots.txt and root path — same unrelated app content in both.
- Automation Difficulty: N/A — wrong site.
- Recommendation: kingfisherworld.com is not a Kingfisher-beer property. unitedbreweries.com/our-brands lists Kingfisher as a UB brand instead. I attempted https://www.kingfisherbeer.com/ and it failed to resolve/connect, so I cannot confirm any dedicated Kingfisher brand site.

### Carlsberg India (carlsbergindia.com)
- URL: https://www.carlsbergindia.com/
- Confidence: High
- Coverage: Verified: robots.txt (200) is an Umbraco-style file (Disallow: /umbraco/, Crawl-delay: 10, lists many Carlsberg Group country-site sitemaps including carlsbergindia.com). Homepage loads (200) with server-rendered brand copy (Carlsberg Smooth, Tuborg Classic, Tuborg Strong Lager, Tuborg Green Lager, Carlsberg Elephant Lager, with launch years and origin country). A guessed 'who-we-are/our-products' sub-path returned 404 — exact product-listing sub-page URL not found.
- Reliability: Cloudflare-fronted (server: cloudflare, cf-ray present) but content returned directly via plain curl with no CAPTCHA/JS-challenge encountered.
- Automation Difficulty: Low-Medium if the real product-listing URL is found (BeautifulSoup sufficient, server-rendered); estimate 8-15 hours, but exact per-brand detail page structure and ABV/size presence not verified.
- Recommendation: Good candidate for brand metadata (names, launch year, origin) but not verified to contain retail pricing. Respect robots.txt Crawl-delay: 10 (~1 req/10s).

### AB InBev India (abinbevindia.in)
- URL: https://abinbevindia.in/
- Confidence: Medium
- Coverage: Verified via search (duckduckgo.com/html) that abinbevindia.in is associated with AB InBev India, then directly fetched: root 302-redirects (x-redirect-by: WordPress header) to /consent/, which loads (200) with page title 'ABInBev' and a location/age 'responsible drinking' consent form listing Indian states including Karnataka.
- Reliability: No Cloudflare/CAPTCHA observed; server: nginx; standard WordPress redirect-based age/location gate.
- Automation Difficulty: Low-Medium — WordPress sites are typically server-rendered; consent gate appears to be a simple redirect/cookie gate, though content behind it was not fetched/verified. Estimate 8-15 hours pending verification.
- Recommendation: Plausible AB InBev India site, but domain ownership was inferred only from search results, not confirmed via ab-inbev.com or a press release — treat as unconfirmed canonical domain.

### Heineken India presence (heineken.com/in/en/home)
- URL: https://www.heineken.com/in/en/home
- Confidence: Medium
- Coverage: Verified: www.heinekenindia.com failed to resolve via DNS in repeated attempts (multiple resolvers/tools) and a direct HTTPS connection to an IP found via one earlier successful DNS answer was reset. As a substitute I searched and found heineken.com/in/en/home, which returned HTTP 200 with title 'Welcome to the world of Heineken® | Heineken.com' and server-rendered (Umbraco CMS) links to /in/en/our-products/, /in/en/our-products/heineken-original/, /in/en/our-products/heineken-0-0/, /in/en/our-products/draught-beer/. robots.txt on heineken.com (200) is Umbraco-style and lists an /in/en/sitemap.xml.
- Reliability: No Cloudflare/CAPTCHA observed (ASP.NET/IIS-style ARRAffinity cookies present, consistent with Azure/IIS hosting).
- Automation Difficulty: Low-Medium — content is server-rendered per-country subpaths; BeautifulSoup sufficient. Estimate 8-15 hours. Not confirmed to contain per-SKU pricing.
- Recommendation: Use heineken.com/in/en/ as the working substitute for the requested heinekenindia.com, since the latter domain could not be reached. Flag this substitution clearly since it is a different hostname than specified.

## Key Findings
- madhuloka.com is the strongest scraping candidate found: fully server-rendered Odoo storefront, no anti-bot protection detected, beer SKU name/price/brand/size visible in plain HTML, working pagination via ?page=N and category slugs like /shop/category/beer-3.
- KSBCL's real official domain is ksbcl.karnataka.gov.in (ksbcl.com 301-redirects there); robots.txt is fully open, but I did not find beer SKU/price pages on the crawled pages — the useful-looking data (e.g. duty slabs) is inside linked PDFs, requiring PDF parsing, not simple HTML scraping.
- livingliquidz.com is completely unreachable (HTTP 503 'under maintenance') across every path/hostname variant tried; no engineering assessment is possible until the site is back online.
- bira91.com does not serve Bira 91 content in my tests — it returns an Apache default page with a TLS certificate for an unrelated domain (*.ksmart.live); the real current Bira 91 web presence, if any, was not directly confirmed by me (candidates found only via search: www.bira91.beer, stores.bira91taproom.com).
- kingfisherworld.com is an unrelated third-party medical SaaS app (GemGP), not a Kingfisher beer property.
- www.heinekenindia.com could not be resolved via DNS in my environment; I substituted the verified working heineken.com/in/en/home page, which is server-rendered and lists Heineken India product pages.
- Corporate brand sites I could verify (unitedbreweries.com, carlsbergindia.com, heineken.com/in, abinbevindia.in) are all server-rendered HTML (Drupal/Umbraco/WordPress respectively) — none required a headless browser/JS execution to see main content in my tests — but none were confirmed to expose per-SKU retail pricing or ABV data; they appear to be marketing/investor-relations sites, not price databases.
- United Breweries is the only source among those tested that is both Cloudflare-fronted AND has a mandatory interactive age-gate form (Drupal age_gate_thc_user_form with CSRF form_build_id) that a scraper must programmatically complete; no CAPTCHA or JS 'checking your browser' challenge was observed, but Cloudflare bot-management cookies (__cf_bm) are present, a risk factor not directly tested.
- No JSON/XHR API endpoints were discovered on any site — all data observed was embedded directly in server-rendered HTML; this favors BeautifulSoup/requests-style scrapers over Playwright/Selenium for every source that was actually reachable.

## Risks
- No source verified to date provides comprehensive, structured ABV data for beers — this is a significant gap for a 'beer database' use case and needs a dedicated follow-up check.
- Corporate brand sites (UB, Carlsberg, Heineken, AB InBev) may not legally intend their marketing content to be scraped for a commercial product database — no ToS review was performed.
- United Breweries' Cloudflare bot-management cookies (__cf_bm, _cfuvid) suggest active bot-traffic monitoring; sustained automated scraping could trigger blocking even though no challenge was observed in light testing.
- DNS/network instability was observed in my own environment for several domains (heinekenindia.com, kingfisherbeer.com, bira91.com's real target) — some failures may be specific to my network/DNS resolver rather than genuine site issues; independent re-verification from a different network is recommended.
- KSBCL's site structure was only lightly explored (home page + robots.txt); it has ERP/OFS login portals and a 'supplier list'/'purchaser code' section that were not explored and might contain more relevant regulated pricing/product data behind login — unverified.
- livingliquidz.com's outage state is unverified as temporary vs. permanent; if permanent, this removes one of the two named retail sources entirely from the feasibility pool.

## Unverifiable / Blocked
- livingliquidz.com — could not evaluate anti-bot posture, JS-rendering requirement, or JSON endpoints because the site returned HTTP 503 'under maintenance' on every attempt.
- bira91.com — could not evaluate the actual Bira 91 site's scraping feasibility because the domain does not currently serve Bira 91 content; candidate alternate domains (bira91.beer, stores.bira91taproom.com) were found via search only and not directly fetched/verified.
- www.heinekenindia.com — could not resolve via DNS in my environment across multiple attempts/resolvers, and a direct connection to an IP obtained from one successful resolution was reset.
- www.kingfisherbeer.com — attempted as a possible alternate Kingfisher brand domain; the connection did not complete (HTTP_CODE:000) so I could not confirm whether a Kingfisher-specific brand microsite exists.
- Whether abinbevindia.in is AB InBev's actual, company-sanctioned India domain — inferred only from third-party search results, not from a citation on ab-inbev.com or a press release confirming ownership.
- KSBCL's ERP login, OFS login, and 'supplier list'/'purchaser code' sections — not explored, so unknown whether they expose structured beer product/price data of value.
- Whether any of the verified-reachable sites (madhuloka.com, KSBCL, UB, Carlsberg, Heineken, AB InBev) expose ABV data anywhere — only one madhuloka product page was checked, and it did not show ABV.
