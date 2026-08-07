# Domain Research: Karnataka Beer / Brewery Market Intelligence (India)

**Research track:** `brewery`

## Summary
I researched official websites and, where available, SEBI regulatory filings/press releases for the major national brewers (United Breweries/Kingfisher, Heineken India, AB InBev India, Carlsberg India, Bira91) and the Karnataka-based craft breweries/brewpubs (Simba, Geist, Arbor Brewing, Toit, STOK, Goa Brewing Co, Byg Brewski, Windmills Craftworks, Murphy's). The strongest, most verifiable data came from United Breweries' investor-relations PDF filings (SEBI Regulation 30 disclosures), which explicitly confirm Karnataka-specific product launches with dates, categories, and in one case exact per-SKU pricing (Kingfisher Smooth: Karnataka launch Jan 28, 2026, 330ml can/bottle, 500ml can, 650ml bottle). Heineken India's official product pages give ABV and calorie data per 100ml for Heineken Original, Silver, and 0.0, but these are global/India-brand pages, not Karnataka-specific SKUs. Carlsberg India's official newsroom confirms a Mysuru (Karnataka) brewery producing Carlsberg and Tuborg brands with a ₹100 crore can-line investment. AB InBev India's Karnataka presence (Mysuru manufacturing unit, Bengaluru HQ, ₹400 crore expansion) is corroborated by press coverage, but AB InBev's own India site (abinbevindia.in) is only an age-gate with no product data. Bira91's official domain (bira91.com) currently resolves to a broken/parked default Apache page (verified via direct curl), so no data could be sourced from it; ABV figures for Bira91 variants (4-7%) came only from Wikipedia/third-party sites, not an official source. Karnataka-local craft brands (Simba, Geist, STOK, Toit, Arbor Brewing) have official sites with partial specs; notably Arbor Brewing's canned retail product is stated to be sold only in Goa (not Karnataka) despite having a Bengaluru brewpub, and Byg Brewski/Windmills Craftworks appear to be brewpub/event-venue only with no retail packaged product found. No brewery's official site or catalogue was found to publish GTIN/UPC/barcode identifiers anywhere.

## Sources
### United Breweries Limited — official investor PDF: Kingfisher Smooth Karnataka launch (SEBI Reg 30 filing + press release)
- URL: https://www.unitedbreweries.com/pdf/Material%20Events/Regulation%2030%20SEBI%20(LODR)%20Regulation%202015%20-%20Launch%20of%20Kingfisher%20Smooth-Karnataka.pdf
- Confidence: High
- Refresh Frequency: Filed per product launch, irregular (multiple per year)
- Recommendation: Excellent structured source for launch-event data; monitor unitedbreweries.com/pdf/Material Events/ folder for new filings.
- Notes: Directly fetched and text-extracted (pdftotext) from the official unitedbreweries.com domain. States: Kingfisher Super Smooth Strong Premium Beer launched in Karnataka effective Jan 28, 2026; category 'Strong Beer'; domestic market only. Press release gives pricing: INR 100/330ml can, INR 120/330ml bottle, INR 155/500ml can, INR 200/650ml bottle, available across leading retail outlets in Karnataka. Also lists UBL's current brand portfolio (Kingfisher Strong, Premium, Ultra, Ultra Max, Ultra Witbier, Heineken Original, Heineken Silver, Amstel Grande, Heineken 0.0).

### United Breweries Limited — official investor PDF: Kingfisher Ultra Max Draught Beer Karnataka launch
- URL: https://www.unitedbreweries.com/pdf/Material%20Events/Regulation%2030%20SEBI%20(LODR)%20Regulations%202015%20-%20Launch%20of%20Kingfisher%20Ultra%20Max%20Draught%20Beer.pdf
- Confidence: High
- Notes: Fetched and text-extracted directly. Confirms 'Kingfisher Ultra Max Draught Beer' launched in Karnataka market on March 7, 2024, category 'Premium Strong Beer', domestic market (state of Karnataka) explicitly named.

### United Breweries Limited — official investor PDF: Kingfisher Ultra Witbier launch (brewed in Mysore, Karnataka)
- URL: https://www.unitedbreweries.com/pdf/Material%20Events/Launch%20of%20Kingfisher%20Ultra%20Witbier.pdf
- Confidence: High
- Notes: Confirms Dec 3, 2019 launch; produced at Chamundi-Mysore, Karnataka facility; ABV 'lower than 5%'; 3 SKUs — 330ml bottle, 500ml can, 650ml bottle, priced Rs.110/150/185 respectively 'in Karnataka state' per the press release text (national launch but Karnataka pricing explicitly given).

### United Breweries Limited — official website (age-gated; sitemap)
- URL: https://www.unitedbreweries.com
- Confidence: Medium
- Recommendation: Use the /pdf/Material Events/ regulatory-filing PDFs as the reliable machine-readable data source instead of the marketing site.
- Notes: Verified: homepage is an age-verification gate with no product data directly visible; sitemap lists brand names (Kingfisher Strong, KF Flavours Lemon/Mango, Kingfisher Premium, Amstel Grande, KF Ultra, KF Ultra Max, KF Ultra Witbier) but no ABV/calorie/package data on the sitemap itself and no downloadable product catalogue PDF found.

### Heineken India — official product page: Heineken Original
- URL: https://www.heineken.com/in/en/our-products/heineken-original/
- Confidence: High
- Notes: Verified via direct fetch. States ABV 5%; nutrition '176kJ / 42 kcal' per 100ml; mentions a 500ml can format ('Hnk Can 500Ml'). Not Karnataka-specific — brand-level India page.

### Heineken India — official product page: Heineken Silver
- URL: https://www.heineken.com/in/en/our-products/heineken-silver/
- Confidence: High
- Notes: Verified via direct fetch. ABV 4%; '146 kJ / 35 kcal' per 100ml; available in 500ml can and bottle.

### Heineken India — official product page: Heineken 0.0
- URL: https://www.heineken.com/in/en/our-products/heineken-0-0/
- Confidence: High
- Notes: Verified via direct fetch. ABV 'less than 0.03%'; '21 kcal/100ml'; 33cl (330ml) bottle.

### Heineken India — products index
- URL: https://www.heineken.com/in/en/our-products/
- Confidence: High
- Notes: Lists Heineken Original, Heineken 0.0, Heineken Silver, Draught Beer, 'The Can' (500ml). No Karnataka-specific confirmation on this page; Heineken brands in India are brewed/sold via United Breweries, which is the entity that files Karnataka-specific launches (see UBL sources above).

### AB InBev India — official site (age gate only)
- URL: https://abinbevindia.in/
- Confidence: Medium
- Notes: Verified via direct fetch: page is only an age/location verification gate; Karnataka appears as a selectable state in the dropdown but no product, ABV, or package data is present anywhere on the page.

### AB InBev global — Our Brands page
- URL: https://www.ab-inbev.com/our-brands
- Confidence: Medium
- Notes: Confirms Budweiser and Corona Extra as global AB InBev brands; Hoegaarden was not found listed on this page (not confirmed as current global brand from this source). No India or Karnataka-specific data.

### Deccan Herald — 'Beer maker AB InBev to expand operations in Karnataka'
- URL: https://www.deccanherald.com/india/karnataka/beer-maker-ab-inbev-to-expand-operations-in-karnataka-1168832.html
- Confidence: Low
- Notes: Could not be fetched directly (403 Forbidden on retry); title/snippet only sourced via search-result listing, not full-text verified. Treat as unverified/plausible, not confirmed by direct read.

### Precize.in — 'AB InBev plans Rs 400 Cr investment to expand its operations in Karnataka'
- URL: https://precize.in/unlistedsharesnews/ab-inbev-plans-rs-400-cr-investment-to-expand-its-operations-in-karnataka
- Confidence: Medium
- Notes: Verified via direct fetch. Confirms Rs 400 crore Karnataka expansion investment and Bengaluru HQ/innovation center presence; third-party news aggregator, not AB InBev's own site, so treat as corroboration rather than primary confirmation.

### Carlsberg India — official Products/Tuborg page
- URL: https://www.carlsbergindia.com/our-products/beers-you-love/tuborg/
- Confidence: Medium
- Notes: Verified via fetch; only breadcrumb/nav content returned, no ABV/calorie/package data extracted from this specific URL.

### Carlsberg India — official Tuborg Green product page
- URL: https://www.carlsbergindia.com/products/tuborg/tuborg-green/
- Confidence: High
- Notes: Verified via direct fetch. Confirms package sizes: 330ml bottles, 500ml cans, 650ml bottles. No ABV or calorie figures present on the page itself.

### Carlsberg India — official newsroom: Mysuru can-line inauguration
- URL: https://www.carlsbergindia.com/latest-news/carlsberg-india-inaugurates-new-can-line-at-mysuru-brewery/
- Confidence: High
- Notes: Verified via direct fetch on carlsbergindia.com. Confirms Carlsberg India brewery at Nanjangud taluk, Mysuru, Karnataka (28 acres) manufacturing both Carlsberg and Tuborg brands; ₹100 crore can-line investment (22,000 cans/hour) plus a separately announced ₹350 crore Invest Karnataka 2025 pledge.

### Bira91 — official domain (bira91.com)
- URL: https://bira91.com/
- Confidence: High
- Recommendation: Re-check bira91.com periodically; use stores.bira91taproom.com or Wikipedia as interim references, clearly labeled as non-primary.
- Notes: Directly verified by curl: as of this research the domain serves a default 'Apache2 Ubuntu Default Page' (parked/misconfigured), not a functioning Bira91 site. TLS certificate also does not match the domain (cert issued for *.ksmart.live). No product data could be sourced from the official domain at time of research.

### Wikipedia — Bira 91
- URL: https://en.wikipedia.org/wiki/Bira_91
- Confidence: Medium
- Notes: Verified via fetch. Lists variants: Bira91 White, Blonde (cited as 4.9% ABV), Strong (~7% ABV), Light, IPA; article text on White's ABV was internally inconsistent (4% cited separately from the 4.9% figure). Secondary source only — not an official confirmation.

### Simba Beer — official site (simbabeer.com)
- URL: https://simbabeer.com
- Confidence: High
- Notes: Verified via direct fetch. Confirms maker 'Sona Beverages Pvt. Ltd.'; confirms distribution explicitly includes Bengaluru ('Now Roaring in Goa, Bengaluru, Delhi, Mumbai, Gurgaon, and many more') — direct official confirmation of Karnataka availability. Variant names (Jungle Wheat, Jungle Stout) given but no ABV on this page.

### Simba Beer — official 'Our Beers' page
- URL: https://simbabeer.com/our-beers/
- Confidence: Medium
- Notes: Verified via fetch; lists categories Wit, Stout, Lager, Strong but no ABV/calorie/package data on the overview page itself; the Lager sub-page also had no spec data.

### Livcheers — Simba price listing, Bangalore
- URL: https://www.livcheers.com/bangalore/brand/simba
- Confidence: Medium
- Notes: Third-party retail price aggregator, not official. Verified via fetch; lists 9 Simba SKUs with sizes (330ml/500ml/650ml) and Bangalore retail prices (₹110–₹170), but no ABV. Useful corroboration of Karnataka retail availability and package sizes, but not a primary/official source.

### unsobered.com — Simba beer guide (third-party)
- URL: https://unsobered.com/simba
- Confidence: Low
- Notes: Third-party beer-review/price blog giving ABV figures (Wit 4.5-5%, Stout ~4.8%, Strong 5%, Lager 4.5%) not corroborated by Simba's own official site. Treat as unverified inference pending an official spec sheet.

### Geist Brewing Co. — official site (geist.in)
- URL: https://www.geist.in
- Confidence: Medium
- Notes: Verified via fetch. Confirms brewpub + retail hybrid model ('Find Geist in Stores,' 'beer takeaway'); no specific beer names/ABV/package sizes found on the pages fetched (homepage, /locations). One named beer, 'Uncle Dunkel' (Bavarian dark wheat, gold at 2025 European Beer Star Awards), mentioned but without ABV.

### Geist Brewing Co. — official locations page
- URL: https://www.geist.in/locations
- Confidence: High
- Notes: Verified via fetch. Confirms 3 Bengaluru, Karnataka locations with full addresses (Old Madras Road/Hoskote, Rajajinagar/Orion Mall, Hennur/Bhartiya Mall).

### Arbor Brewing Company India — official site (arborbrewing.in)
- URL: https://www.arborbrewing.in
- Confidence: High
- Notes: Verified via fetch. Confirms one Bengaluru, Karnataka brewpub location (Magrath Rd, Ashok Nagar) with 8 named on-tap beers and ABV/IBU for each (e.g., Idaho 7 Lager 5.2% ABV, Smooth Criminal 8.0% ABV). Important finding: the site states packaged/canned retail beer (Bangalore Bliss Hefeweizen 5.5% ABV, Beach Shack IPA 6.0% ABV) is 'Retailing only across Goa' — i.e. NOT confirmed retail-available in Karnataka despite the Bengaluru brewpub. No calorie data found.

### Toit — official beer listing page
- URL: https://toit.in/beer/
- Confidence: Medium
- Notes: Verified via fetch. Lists 7 core beers (Banger Lager, Basmati Blonde, Hefeweizen, India Pale Ale, Nitro Stout, Red Ale, Tint-In-Wit) across Bangalore (2 locations), Pune, Mumbai; states beer is available 'at an MRP store near you' implying some retail packaging, but does not specify which SKUs or confirm Karnataka-specific packaged retail vs. on-tap only.

### Toit — official product page: Banger Lager
- URL: https://toit.in/beer/banger-lager/
- Confidence: High
- Notes: Verified via fetch. ABV 4.5%. No calorie or package-size data present.

### Toit — official product page: Basmati Blonde
- URL: https://toit.in/beer/toit-basmati-blonde/
- Confidence: High
- Notes: Verified via fetch. ABV 4.6%. No calorie or package-size data present.

### Mount Everest Breweries — official STOK product page
- URL: https://mounteverestbreweries.com/products/stok/
- Confidence: High
- Notes: Verified via fetch. Full spec table: STOK Strong (7% ABV, IBU 12), STOK Lager (4.8% ABV, IBU 15), STOK Wheat (4.7% ABV, IBU 12); all three offered in 325ml, 650ml, and 500ml-can sizes. Note: page's own FAQ section contradicts the spec table by listing STOK Strong at '8% ABV' — an internal inconsistency on the official site itself, flagged rather than resolved.

### STOK India — official homepage (stokindia.com)
- URL: https://stokindia.com
- Confidence: Medium
- Notes: Verified via fetch. Confirms 3 variants (Lager, Strong, Wheat) with marketing descriptions but no ABV/calorie/package data on this page; states availability 'across India' without Karnataka-specific confirmation on this page.

### Brewer World — 'STOK Beer Debuts in Bengaluru with a Chill-Focused Launch'
- URL: https://www.brewer-world.com/stok-beer-debuts-in-bengaluru-with-a-chill-focused-launch/
- Confidence: Medium
- Notes: Trade-press article (not official STOK/Mount Everest Breweries source), verified via fetch. Confirms an official STOK launch event in Bengaluru (Ashok Nagar) with Strong/Wheat/Lager variants; mentions a planned draught rollout 'soon' — corroborates but is not itself a primary/official confirmation of ongoing Karnataka retail sales.

### Goa Brewing Co. — official site (goabrewing.co)
- URL: https://goabrewing.co
- Confidence: Low
- Notes: Verified via fetch: site appears to be a minimal placeholder/under-construction page with tagline only ('Non Conformist Beers'); no product list, ABV, package size, or Karnataka-availability information found. Cannot confirm whether Goa Brewing Co. products are sold in Karnataka from official sources.

### Byg Brewski — official 'Packages' page
- URL: https://bygbrewski.com/packages/
- Confidence: Medium
- Notes: Verified via fetch. Page is about catered event packages, not retail beer products; only mentions 'Freshly Brewed Beers (Availability Of The Day)' with no brand names or specs. No evidence found (on this page) that Byg Brewski sells packaged/retail beer; appears to be a brewpub/event-venue model only.

### Windmills Craftworks — official site (windmills-india.com)
- URL: https://windmills-india.com/index.html
- Confidence: High
- Notes: Directly fetched via curl and inspected raw HTML. Confirms 5+ named house beers with ABV/IBU (e.g., Hefeweizen ABV 4.96% IBU 15; session ale ABV 4.2%; Stout ABV 6.3%; Hazy IPA ABV 6.1% IBU 32; West Coast IPA ABV 6.8% IBU 64). No mentions anywhere on the page of 'retail,' 'takeaway,' 'store,' or 'bottle' — strong evidence this is a brewpub-only (on-tap) operation with no packaged retail product, in Bengaluru (Whitefield), Karnataka.

### Murphy's official global site (Heineken UK)
- URL: https://www.heineken.co.uk/murphys
- Confidence: Low
- Recommendation: Flag to product team: verify whether 'Murphy's' in the ValueBrew brief refers to the Irish Stout brand (no confirmed India retail presence found) or the Bengaluru brewpub venue 'Murphy's Brewhouse' (a bar, not a packaged-beer brewery).
- Notes: Not directly fetched in this session (only surfaced via search-result snippet); Murphy's Irish Stout appears to be a Heineken-owned international brand with UK/Ireland focus. No India- or Karnataka-specific official page or confirmation was found. The 'Murphy's' results in India context mostly resolved to 'Murphy's Brewhouse,' an unrelated Bengaluru brewpub venue (at The Paul hotel) — these should not be conflated with the Murphy's Irish Stout beer brand.

### GS1 India — official site
- URL: https://www.gs1india.org/
- Confidence: Medium
- Recommendation: No brewery researched was found to publish GTIN/UPC/barcode numbers on its own official website or catalogue. This should be treated as a confirmed data gap across the entire brand set, not just an omission from this report.
- Notes: Verified via fetch. Confirms GS1 India issues barcodes with prefix '890' and offers 'DataKart' as an internal product-data repository for registered businesses, but no public GEPIR-style consumer lookup for competitor GTINs was found described on the site.

## Key Findings
- United Breweries (Kingfisher/Heineken licensee in India) publishes the most reliable Karnataka-specific product data via SEBI Regulation 30 regulatory filing PDFs at unitedbreweries.com/pdf/Material Events/ — these give exact launch dates, categories, and (in the Kingfisher Smooth case) full per-SKU Karnataka retail pricing across four package sizes (330ml can/bottle, 500ml can, 650ml bottle).
- Kingfisher Ultra Max Draught Beer was confirmed launched specifically in the Karnataka market on March 7, 2024 (Premium Strong Beer category), per an official UBL filing.
- Kingfisher Ultra Witbier (ABV <5%) has been brewed at United Breweries' Chamundi-Mysore, Karnataka facility since Dec 2019, with Karnataka-specific pricing (Rs.110/150/185 across 330ml bottle/500ml can/650ml bottle) stated in the official press release.
- Heineken India's official brand pages (heineken.com/in/en) give ABV and per-100ml calorie data for Heineken Original (5% ABV, 42 kcal/100ml), Heineken Silver (4% ABV, 35 kcal/100ml), and Heineken 0.0 (<0.03% ABV, 21 kcal/100ml) — these are India brand pages but not confirmed Karnataka-specific SKUs.
- Carlsberg India officially operates a brewery in Nanjangud taluk, Mysuru, Karnataka, producing both Carlsberg and Tuborg brands, confirmed via Carlsberg India's own newsroom (₹100 crore can-line investment, ₹350 crore further Karnataka pledge).
- AB InBev India's official consumer-facing site (abinbevindia.in) is only an age/location gate with zero product data; Karnataka operations (Mysuru manufacturing, Bengaluru HQ, ₹400 crore expansion) are corroborated only by third-party press, not by AB InBev's own product pages.
- Bira91's official domain (bira91.com) is currently broken/misconfigured, serving a default Apache placeholder page with a mismatched TLS certificate — verified directly via curl. No official ABV/package/GTIN data could be sourced from Bira91 at all in this research pass.
- Simba beer (maker: Sona Beverages Pvt. Ltd.) explicitly confirms Bengaluru distribution on its own official site, and third-party retail listings (Livcheers) show 9 Karnataka-priced SKUs (330/500/650ml, ₹110-₹170), though no official ABV figures were found on Simba's own site.
- Arbor Brewing Company operates a Bengaluru, Karnataka brewpub with 8 named on-tap beers (ABV/IBU given for each), but its own official site states packaged/canned retail beer is 'Retailing only across Goa' — meaning its packaged product is NOT confirmed available in Karnataka despite the Bengaluru taproom.
- Windmills Craftworks and Byg Brewski appear, based on their official sites, to be brewpub/event-venue operations only, with no evidence of packaged retail beer products for sale (no 'bottle', 'retail', 'takeaway', or 'store' references found on Windmills' site; Byg Brewski's site is centered on catered event packages).
- Mount Everest Breweries' official STOK product page gives full specs (Strong 7% ABV, Lager 4.8% ABV, Wheat 4.7% ABV; all in 325ml/500ml-can/650ml) but has an internal inconsistency where its own FAQ separately states 8% ABV for STOK Strong.
- No brewery examined (national or Karnataka craft) was found to publish GTIN/UPC/barcode numbers on its official website, product page, or any catalogue PDF — this is a confirmed, consistent gap across the entire researched set, not specific to any one brand.
- 'Murphy's' in the brief is ambiguous: the Irish Stout brand (Heineken-owned, UK/Ireland-focused) has no confirmed India presence found, while most India search results for 'Murphy's' actually refer to 'Murphy's Brewhouse,' an unrelated Bengaluru bar/brewpub venue at The Paul hotel — these are likely different entities and should be disambiguated with the requester.

## Risks
- Several PDF/press-source dates in search results appear to be in 2025/2026, i.e. the future relative to typical training data — these were independently verified by direct fetch/pdftotext extraction in this session, but the requester should be aware the underlying environment's current date is 2026-08-05, so 'recent' launches referenced (e.g. Jan 2026 Kingfisher Smooth Karnataka launch) are current-appearing filings, not fabricated future dates.
- Many secondary/tertiary sources (price-comparison blogs like unsobered.com, liquorsai.com, madirakeprice.com) publish ABV and pricing figures with no visible sourcing or verification methodology; these should be treated as low-confidence and cross-checked against official brand sites before use in the ValueBrew database.
- WebFetch tool results are AI-summarized paraphrases of page content, not raw HTML/text (except where I used curl+pdftotext directly) — there is residual risk that the summarization step dropped or slightly misstated a number; the highest-confidence facts in this report are the ones I extracted directly via curl/pdftotext (UBL PDFs, Windmills raw HTML).
- abinbevindia.in, budweiser.com, and most Carlsberg/AB InBev consumer sites are age-gated, so confirming Karnataka-specific SKU-level ABV/calorie/package data for Budweiser, Corona, Hoegaarden, and Tuborg variants beyond what was captured here would likely require either simulating age-gate interaction (not attempted) or relying on secondary retail-price sites, which were explicitly deprioritized per the no-fabrication instruction.
- Bira91's official domain being down/misconfigured at the time of this research is a time-sensitive finding — it should be re-verified before final publication in case it was a transient outage rather than a permanent issue.
- GTIN/UPC absence is based on searching official sites and general GS1 India site content; it does not rule out GTINs being registered privately in GS1's non-public database (GEPIR-equivalent) — this is a case of 'not found on public official sources' rather than 'confirmed does not exist'.

## Unverifiable / Blocked
- Deccan Herald article on AB InBev Karnataka expansion could not be fetched directly (403 Forbidden) — only the title/snippet from search results was available, so its content is unverified beyond the snippet.
- Toit's specific claim of retail/MRP-store beer availability could not be tied to specific SKUs or confirmed as Karnataka-specific (vs. Pune/Mumbai) from the pages fetched.
- Goa Brewing Co.'s Karnataka availability (or lack thereof) could not be determined — its official site had essentially no content beyond a name and tagline.
- Could not determine Hoegaarden's current India/Karnataka retail status from any official AB InBev or India-specific source — only third-party price-comparison sites referenced it, and abinbevindia.in gave no product data.
- wine-searcher.com page intended to check Murphy's Irish Stout India availability returned HTTP 403 and could not be read.
- Could not access any GS1 India or GEPIR-style public database entry confirming or denying GTIN registration for any specific beer brand/SKU — GS1 India's site describes an internal DataKart tool, not a public lookup, and no public lookup tool for Indian GTINs was found or tested.
- Byg Brewski's broader site (beyond /packages/) and any potential separate retail/e-commerce presence were not fully explored; the 'no packaged retail beer' finding is based on one page only and should be treated as provisional.
