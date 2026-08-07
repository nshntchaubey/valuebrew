# Domain Research: Trade/import-intelligence data sources for detecting new imported beer brands entering India (HSN 2203) — for ValueBrew's Karnataka beer database

**Research track:** `import_market`

## Summary
Zauba.com is still live (not shut down) but its underlying shipment data appears stale — sample records I loaded were dated 2013 and Nov-2016, and the site footer reads "© 2021 Zauba.com," suggesting no meaningful updates in years, likely tied to India's 2016 policy change ending mandatory public trade-data release. Volza is the most viable third-party option I found: I directly loaded its live global "Beer / HSN Code 2203" page (414,386 shipments, 13,603 buyers, 15,983 suppliers) and, critically, its India-specific "Beer Imports in India" page, which showed real, brand-identifiable free-tier shipment snippets (e.g., TUSKER BEER/Kenya Breweries from Kenya, SAIGON EXPORT PREMIUM BOTTLED BEER from Vietnam, Cheetah/Camel/Abest Premium Beer from Vietnam, Sri Lanka canned beer, Namibia "Beer made from malt") for the period Jun 2024–May 2025 (62 shipments, 21 buyers, 24 suppliers) — full buyer/supplier identity and complete bill-of-lading data is paywalled behind a paid subscription (verified tiers: Free 7-day trial, ~$1,500/yr, ~$4,500/yr "Most Popular," ~$9,600/yr Corporate). India's official body, DGCI&S (Directorate General of Commercial Intelligence & Statistics), sells aggregate commodity-level trade data cheaply (₹1/record, Rs.1000 minimum registration) via its Web-based PIS, but explicitly does NOT provide importer/exporter identity for private use — that transaction-level detail (with identity suppressed) is reserved for anti-dumping investigations authorized by DGAD. This directly bears on legality: Section 135AA of the Customs Act, 1962 (2022) criminalizes unauthorized publication of importer/exporter transaction-level trade data (value, classification, quantity, identity), which is the exact kind of data needed to reliably auto-discover "who is importing which new beer brand." Volza and similar aggregators appear to operate by sourcing bill-of-lading data (a different, historically more public data channel than DGCI&S customs filings) rather than DGCI&S records, which is likely why they can still legally sell it, but I could not fully verify Volza's specific legal basis/jurisdiction for Indian bill-of-lading data resale. Net assessment: for ValueBrew's use case (detect new imported beer brands entering Karnataka/India), Volza is the most promising and currently working avenue at moderate cost (~$1,500–$9,600/yr) with real but non-exhaustive product-name-level India beer data; DGCI&S is legally the safest official channel but gives only aggregate, non-brand-level stats; Zauba is unreliable due to apparent data staleness; ImportGenius has a low $199 entry point but its actual India/beer coverage was not verified.

## Sources
### Volza — Global Beer and HSN Code 2203 export/import trade data page
- URL: https://www.volza.com/p/beer/hsn-code-2203/
- Confidence: High
- Coverage: Global: 414,386 import + 414,386 export shipments (duplicated buyer/import totals shown), 13,603 buyers, 15,983 suppliers across 181 importing / 149 exporting countries. Free-tier shows product description, origin/destination, qty, and (sometimes) price for individual shipments, but NOT buyer/supplier company names or full bill-of-lading (paywalled).
- Reliability: Directly loaded and read via browser; content observed included real, dated (as recent as Jul-2025) individual shipment line items with product descriptions like 'RED STRIPE BEER 6PK', 'CORONA EXTRA 4X6', 'STOUT OR PORTER, OTHER BEER INCL ALE'.
- Licensing: Commercial SaaS; paid subscription required for full shipment detail incl. company names/contacts.
- Automation Difficulty: Unclear — no public API observed; likely requires a paid plan and possibly manual export or a vendor-provided API/bulk-download feature not directly verified.
- Refresh Frequency: Page itself timestamped 25-Nov-2025; shipment rows observed up to Jul-2025 — appears to update at least monthly, though exact cadence not confirmed.
- Recommendation: Primary recommended commercial data source to evaluate further, ideally via a trial account, before committing budget.
- Notes: Verified directly by navigating to the live page and reading its accessibility-tree content. Does not by itself show India as a top importer in the global top-30 list, but see the India-specific page below.

### Volza — Beer Imports in India page
- URL: https://www.volza.com/p/beer/import/import-in-india/
- Confidence: High
- Coverage: India-specific: 62 import shipments, 21 buyers, 24 suppliers for TTM Jun 2024–May 2025. Free preview rows show real brand-identifiable product descriptions for shipments INTO India, e.g. 'TUSKER BEER 330ML; KENYA BREWERIES' (Kenya→India), 'SAIGON EXPORT PREMIUM BOTTLED BEER' (Vietnam→India), 'Cheetah Premium Beer', 'Camel Premium red label beer', 'Abest Premium Beer' (all Vietnam→India), 'CANNED BEER LESS THAN 350 ML' (Sri Lanka→India), 'Beer made from malt - Traditional A' (Namibia→India), 'MALT BEER... OTHER' (Ukraine→India).
- Reliability: Directly loaded and read via browser (accessibility tree extraction); this is the single most directly relevant and useful piece of evidence found for ValueBrew's exact use case.
- Licensing: Commercial SaaS; buyer/supplier company names and full bill-of-lading gated behind paid subscription.
- Automation Difficulty: Same caveats as global Volza page — no public API confirmed; scraping the free-tier preview would only surface product-description text, not buyer identity, and Volza's Terms of Service (not reviewed) may restrict scraping.
- Refresh Frequency: Page dated 08-Apr-2026; most recent shipment row observed was 26-Jun-2025 — roughly a 9-10 month lag between newest visible free-tier shipment and page-generation date, though this may reflect the free-tier's rolling TTM window rather than true latency (unverified).
- Recommendation: Test the free 7-day trial specifically filtered to India + HSN 2203 to assess real completeness and update cadence before purchasing a paid tier.
- Notes: This page's free preview already reveals enough brand-level detail (e.g., Tusker, Camel, Cheetah, Abest, Saigon Export) to be useful for 'new brand' detection without even paying, though it is capped/truncated ('View More Shipments' requires subscription) and coverage completeness (62 shipments over ~1 year) seems low relative to India's actual import volume, suggesting Volza's India-beer dataset may be partial.

### Volza Pricing page
- URL: https://www.volza.com/pricing/
- Confidence: High
- Coverage: Subscription tiers observed: Free trial ($0, 7-day); Startup tier (~$1,500/yr); a 'Most Popular' mid tier (~$4,500/yr); Corporate tier (~$9,600/yr).
- Reliability: Directly loaded and read via browser prior to context compaction (noted in session record); not re-verified in this final pass but was directly observed earlier in the same session.
- Recommendation: Budget ~$1,500-$4,500/yr as a starting estimate for a single-country/product-focused subscription; confirm exact tier limits (query volume, countries, users) before purchase.

### Zauba (zauba.com) import shipment data
- URL: https://www.zauba.com/import-BEER-MADE-FROM-MALT-hs-code.html
- Confidence: Medium
- Coverage: Historically covered India import shipment records by HS code, including beer (HSN 2203); sample records observed were dated 2013, and a separate mobile-phone HS-code sample page showed records dated Nov-2016.
- Reliability: Site is live and loads (after an initial Cloudflare interstitial) — directly verified via browser navigation — contradicting a literal reading of 'Zauba shut down.' However, footer text read '© 2021 Zauba.com,' and no records newer than 2016 were observed in my sampling, suggesting the data pipeline is frozen/stale rather than actively shut down.
- Recommendation: Do not rely on Zauba for current/new-brand detection; treat as historical/archival reference only pending further verification of any actual shutdown date or successor product.
- Notes: Distinct from ZaubaCorp (zaubacorp.com) and zauba.company, which are separate MCA/company-registry products, NOT import shipment data — do not conflate these when evaluating 'Zauba's successor.'

### DGCI&S — Data Dissemination Policy and Fee Structure
- URL: https://www.dgciskol.gov.in/data_dissemination_fee_structure.aspx
- Confidence: High
- Coverage: Official aggregate export/import statistics by Commodity x Country x Port combinations; also a Web-based PIS with 2/4/6/8-digit commodity, country, and port-level data for the latest 24 months.
- Reliability: Directly loaded and read via browser; page states 'last modified 14/Jun/2021' but is the live official fee-structure page on the government's own domain.
- Licensing: Government Priced Information System (PIS): Rs. 1.00 per output record + CD/postage; Web-PIS: Rs. 1.00/record with Rs. 1,000 registration advance (Rs. 200 minimum balance).
- Refresh Frequency: Web-based PIS advertised as providing 'latest 24-months Final Export/Import Data.'
- Recommendation: Useful only for aggregate beer-import trend/volume tracking (e.g., total litres of HSN 2203 imported into India per period), not for auto-discovering specific new brands or importers.
- Notes: Explicitly states: 'Transaction Level Data: ...transaction-wise import data, SUPPRESSING THE IDENTITY OF THE IMPORTERS are provided to different private users for anti-dumping investigations after proper authentication by [DGAD]... The identity particulars of exporters/importers, like name, address and IE code are not provided under any circumstances [to general/aggregate data users].' This means DGCI&S's official/legal channel cannot supply importer-identity or brand-level detail for a use case like ValueBrew's.

### DGCI&S — FAQ page
- URL: https://dgciskol.gov.in/faq.aspx
- Confidence: High
- Coverage: Confirms: 'Aggregate level trade data by Country × Commodity and Country × Port × Commodity are disseminated by the DGCI&S to the private users on payment basis. Transaction level details with the name, address of exporter/importer, commodity exported/imported etc. are NOT provided for private use.' Cost: Rs. 1/record + 10% service charge (min Rs.100) + Rs.15 CD + Rs.25 postage.
- Reliability: Directly loaded and read via browser (content extracted via a saved a11y-tree JSON and parsed with a Python script for size reasons); official government domain.
- Recommendation: Confirms DGCI&S is a legally clean but data-quality-insufficient (aggregate only, no identity) source for this use case.

### TRADESTAT (Government of India, Ministry of Commerce)
- URL: https://tradestat.commerce.gov.in
- Confidence: Medium
- Coverage: Free, official aggregate India export/import statistics portal; observed via Bing search result snippet dated '19 May 2026' referencing EIDB/MEIDB/FTPA modules; not independently re-loaded/read in full during this session (was verified earlier pre-compaction per session history).
- Reliability: Government domain; snippet-level confirmation only in this final pass.
- Recommendation: Use for high-level aggregate beer-import trend context only; not brand/importer-level.

### ImportGenius — India trade data landing page
- URL: https://www.importgenius.com
- Confidence: Low
- Coverage: A $199 entry price point for India-related datasets was observed on an India-datasets landing page earlier in this research session (pre-compaction), but the exact scope of what that $199 tier includes (one-time report vs. subscription; HSN-2203/beer coverage specifically) was not verified in this session.
- Reliability: Price point directly observed on-page per prior session notes, but not re-verified in this final pass and scope/coverage remains unconfirmed.
- Recommendation: Worth a follow-up trial/quote request to clarify what the $199 price actually buys before considering it further.

### Section 135AA of the Customs Act, 1962 — statutory text (via Bing AI Overview / search snippets)
- URL: https://laws.llmadvocates.com/section
- Confidence: Medium
- Coverage: Statutory text substance (as surfaced in a Bing AI Overview I read via the browser, citing llmadvocates.com/TaxGuru): '(1) If a person publishes any information...furnished to customs by an exporter or importer...relating to the value or classification or quantity of goods entered for export or import...along with the identity of the person...[criminal penalty]. (2) Nothing contained in this section shall apply to (a) any publication made by or on behalf of the Central Government; (b) data sourced from such publication for trade trend analysis and dissemination.'
- Reliability: IMPORTANT CAVEAT: I could NOT directly load the primary source. The exact URL https://laws.llmadvocates.com/section-135aa-of-the-customs-act1962-protection-of-data/ returned a 404 'Not Found' page when I navigated to it directly. Similarly, https://sooperkanoon.com/customs-act-1962-section-135aa failed to load any content, https://www.indiacode.nic.in returned 403 Forbidden, taxguru.in's specific article URL 404'd, and www.taxtmi.com's bare-act URL returned 'Access denied.' The statutory text quoted above is therefore only corroborated via a Bing-generated AI Overview summary (which itself cites these sources) plus matching secondary reporting (Telegraph India headline 'Modi government gags flow of export-import data', TaxGuru headline 'Govt criminalise illicit publication of Import and Export Data', both dated Feb 2022, seen only as SERP snippets) — I did not independently load and read the full text of any of these three secondary articles either.
- Recommendation: ValueBrew should have Indian legal counsel independently verify the current text and scope of Section 135AA (and whether/how it applies to a foreign SaaS vendor like Volza reselling bill-of-lading-sourced data to an Indian company) before building a product feature that depends on importer-identity-level Indian trade data.
- Notes: This is the single most important LEGAL RISK finding for ValueBrew, but confidence is Medium (not High) specifically because I was unable to directly fetch any primary or secondary full-text source — only a search-engine-synthesized summary and headline snippets.

### tpm.in article on Indian trade data publication history
- URL: https://www.tpm.in
- Confidence: Medium
- Coverage: Historical narrative on India's trade-data publication policy shifts (2004 Notification 128/2004-Customs enabling publication; 2016 Notification 140/2016-Customs ending mandatory publication; 2022 Section 135AA criminalization; Trade Notice 1/2022 restoring limited DGCI&S access for anti-dumping investigations).
- Reliability: Successfully fetched via WebFetch earlier in this research session (per session history); this is one of the only successful direct fetches of a secondary legal-history source. Not re-fetched in this final pass to confirm the exact URL still resolves.
- Recommendation: Useful corroborating timeline, but should still be cross-checked against a primary legal source or counsel.

### ZaubaCorp / zauba.company (company registry products — explicitly NOT trade-shipment data)
- URL: https://www.zaubacorp.com
- Confidence: Medium
- Coverage: MCA/company-registry and corporate-intelligence data, unrelated to import/export shipment records.
- Reliability: Observed/disambiguated during earlier browsing in this session; not re-verified in this final pass.
- Recommendation: Do not use as a substitute for Zauba's original trade-data product — it answers a different question (company registration lookup) than 'who is importing this beer brand.'

## Key Findings
- Volza directly and currently exposes brand-identifiable beer-import shipment data specifically for India (verified live page: https://www.volza.com/p/beer/import/import-in-india/), showing real product descriptions such as 'TUSKER BEER... KENYA BREWERIES' (Kenya→India), 'SAIGON EXPORT PREMIUM BOTTLED BEER' (Vietnam→India), 'Cheetah Premium Beer', 'Camel Premium red label beer', 'Abest Premium Beer' (Vietnam→India), and 'CANNED BEER LESS THAN 350 ML' (Sri Lanka→India) in its FREE preview tier — this is strong direct evidence that Volza (unpaid preview alone) could plausibly support ValueBrew's 'detect new imported beer brands' use case, at least partially.
- Volza's India-beer coverage (62 shipments over TTM Jun2024-May2025, 21 buyers, 24 suppliers) is comparatively small relative to India's actual beer import market, suggesting either a coverage gap/lag in Volza's dataset for this specific HSN code/country combination, or that most of India's HSN-2203 volume is genuinely modest — this could not be disambiguated further without a paid account.
- Zauba.com is technically still online (not literally 'shut down' as the task brief assumed) but its sampled shipment data (2013, Nov-2016 records; footer '© 2021 Zauba.com') strongly suggests the underlying data pipeline is stale/frozen, likely as a consequence of India's 2016 policy change (Notification 140/2016-Customs) ending mandatory public trade-data disclosure.
- India's official DGCI&S channel is legally the cleanest source but is explicitly restricted by its own published policy from providing importer/exporter identity to private users for any purpose other than DGAD-authorized anti-dumping investigations — meaning it cannot itself be used to auto-discover which specific companies are importing which specific new beer brands, only aggregate volume/value trends.
- Section 135AA of the Customs Act, 1962 (added 2022) appears to criminalize unauthorized publication of importer/exporter transaction-level trade data including identity — this is a material legal-risk consideration for any product design that would republish or display Indian importer-identity-linked shipment data sourced other than through Central Government-authorized channels; however, this finding rests on secondary/AI-summarized sources, not a directly-loaded primary legal text, and should be independently confirmed by counsel.
- Third-party aggregators like Volza (and reportedly ImportGenius, Seair, Cybex Exim, Eximpedia, etc., none of which I could fully verify in depth) appear to source their India data from bill-of-lading / manifest records (a different, historically more openly available data channel than DGCI&S's customs-declaration data), which may be why they can still commercially sell India shipment data despite Section 135AA and DGCI&S's restrictions — but I could not verify this legal distinction directly and it should not be assumed safe without counsel review.

## Risks
- Legal risk: If ValueBrew's product surfaces importer/exporter identity information tied to Indian customs transaction data (as opposed to bill-of-lading-sourced data resold by a third party like Volza), it could run afoul of Section 135AA of the Customs Act, 1962 — this needs a proper legal opinion, not just this research.
- Data completeness/coverage risk: Volza's India-beer dataset (62 shipments/year in the free preview) seems small; if it under-covers India's actual beer import volume, ValueBrew could miss real new-brand entries or get a skewed picture, especially for smaller Karnataka-specific importers/distributors who may not show up prominently in a global aggregator's India-wide dataset.
- Latency risk: The gap between Volza's page-generation date (Apr 2026) and its most recent visible free-tier shipment record (Jun 2025) suggests possible data lag of many months, though this could also just reflect a fixed trailing-12-month window rather than true pipeline latency — unconfirmed either way.
- Vendor/legal-basis risk: I could not verify Volza's own legal basis/jurisdiction claims for reselling India shipment/bill-of-lading data, nor whether its Terms of Service permit programmatic scraping/automation (relevant to ValueBrew's stated goal of 'auto-discovering' brands) — this must be confirmed directly with Volza (e.g., via their sales team) before building automation on top of it.
- Zauba data staleness risk: If ValueBrew were to rely on Zauba for any purpose, the apparent multi-year staleness of its underlying data (last confirmed live records circa 2016, footer dated 2021) makes it unsuitable for detecting NEW brands entering the market today.
- Confidence-labeling risk on the legal-history narrative: My understanding of the 2004→2016→2022 Indian trade-data-publication policy timeline rests substantially on an AI-generated Bing summary and unfetchable secondary sources (multiple candidate URLs for Section 135AA's text and history returned 404/403 errors when I tried to load them directly) — the underlying facts could be incomplete or slightly inaccurate and should be re-verified against a primary legal database (e.g., India Code, once directly accessible) before any business decision is made.

## Unverifiable / Blocked
- Primary statutory text of Section 135AA of the Customs Act, 1962: https://www.indiacode.nic.in returned 403 Forbidden; https://laws.llmadvocates.com/section-135aa-of-the-customs-act1962-protection-of-data/ returned 404; https://sooperkanoon.com/customs-act-1962-section-135aa failed to load any content; https://www.taxtmi.com/bare-act?tab=customs&submenu=customs_act&child=135AA returned 'Access denied'; a specific TaxGuru article URL guessed for this topic returned TaxGuru's own 404 page.
- Whether Volza's India bill-of-lading-sourced data (as opposed to DGCI&S customs-declaration data) is legally distinct enough from Section 135AA's scope to be clearly compliant — I found no source directly addressing this specific legal distinction; this is inference on my part, not a verified fact.
- Full completeness of Volza's India + HSN-2203 coverage (i.e., whether 62 shipments/year is the true total or an artifact of the free-preview filter/window) — would require a paid trial account to confirm.
- Exact automation/API capability and Terms-of-Service restrictions for Volza (whether ValueBrew could legally and technically build automated 'new brand' detection on top of it) — not disclosed on the public pages I could load; would require direct vendor contact.
- ImportGenius's specific India/HSN-2203/beer coverage and what its observed $199 price point actually includes — not re-verified in this session; flagged as Low confidence.
- Cybex Exim, Export Genius, Seair Exim, and Eximpedia — named as potential alternative providers in the original task scope but not directly investigated/verified in this research session due to time constraints; their India/beer-HSN-2203 coverage, pricing, and legal posture remain completely unverified.
- TRADESTAT's exact current data granularity/lag — only a Bing snippet (dated 19 May 2026) was observed in this final pass; the page itself was not re-loaded and read directly in this session (though it reportedly was in an earlier part of the session, per prior research notes).
