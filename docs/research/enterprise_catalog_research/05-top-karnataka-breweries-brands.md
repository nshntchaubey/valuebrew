# Deliverable 5 — Top Karnataka Breweries & Brands

# Deliverable 5: Top Karnataka Breweries & Brands

Methodology: I ranked confidence using three independent Karnataka-specific signals, in order of strength: (1) KSBCL — the Karnataka government's own liquor corporation price list (the single most authoritative "this SKU is legally sold in Karnataka today" signal in this dataset); (2) direct listing on a Bangalore-based online retailer (Madhuloka); (3) a brewery's own official site/SEBI filing stating Karnataka distribution or a Karnataka manufacturing facility. Brands with only (3) and no retail/KSBCL confirmation are flagged **Medium**; brands found only on a brand's national/global site with zero Karnataka-specific corroboration are flagged **Low/Unconfirmed**.

---

## 1. United Breweries Ltd (UBL) — part of The HEINEKEN Company
**Website:** unitedbreweries.com (age-gated marketing site; no downloadable full product catalogue PDF, but individual SEBI Regulation 30 launch-disclosure PDFs exist per product at `unitedbreweries.com/pdf/Material Events/…`, each with launch date/category and sometimes exact Karnataka retail pricing)
**Catalogue/PDF:** Partial — no master catalogue, but per-SKU regulatory PDFs exist for several launches (Kingfisher Smooth, Ultra Max Draught, Ultra Witbier).
**Karnataka manufacturing:** Confirmed — Chamundi/Nanjangud unit, Mysore, Karnataka.

| Brand | KA Confidence | Why |
|---|---|---|
| Kingfisher Premium Lager | High | KSBCL Supplier Code 0210 (Nanjangud), also on Madhuloka |
| Kingfisher Strong / Bullet Super Strong | High | KSBCL Supplier Code 0206 |
| Heineken Lager / Heineken Silver | High | KSBCL Supplier Code 0210; also Madhuloka |
| Kingfisher Ultra, Ultra Max, Ultra Witbier | High | UBL SEBI filings explicitly name Karnataka launch dates/pricing; also on Madhuloka (KF Ultra, Ultra Max, Ultra Witbier SKUs) |
| Kingfisher Storm | Medium | Appears on Madhuloka (Bangalore retailer) as "KF Storm Bottle/Tin" — not covered in domain research reports, so brewery/parent confirmed only by brand name |
| UB Export (Lager/Strong) | High | Directly listed on Madhuloka (UB Premium/Strong Bottle/Tin/Pint) |
| Heineken 0.0, Heineken Draught, Heineken Silver Draught | Medium | Confirmed on Heineken India national site (heineken.com/in) and UBL brand page; no KSBCL/Karnataka-retail line-item found in this catalog |
| Amstel Grande | Medium | On UBL's own brand page + Living Liquidz (via Wayback, site was down) — no direct KSBCL/Madhuloka confirmation |
| London Pilsner (Premium & Strong) | Medium | UBL official site + Living Liquidz Wayback archive only — no KSBCL/Madhuloka line item |
| Cannon 10000, Kalyani Black Label Strong, Zingaro | **Low/Unconfirmed** | Only found on UBL's own brand-portfolio page; zero corroboration from KSBCL, any Karnataka retailer, or retail pricing data — treat as "sold somewhere in UBL's national portfolio," not confirmed Karnataka-available |
| KF Flavours (Lemon Masala, Mango Berry Twist) | **Low/Unconfirmed** | Official site only, no Karnataka retail signal |
| Kingfisher-branded soda/water (Packaged Drinking Water, Strong Power Soda, Ultra Premium Soda) | N/A (non-alcoholic) | Not beer — exclude from beer SKU count but note as adjacent UBL products |

---

## 2. Carlsberg India Pvt Ltd
**Website:** carlsbergindia.com (Umbraco CMS, server-rendered; no downloadable master catalogue found, but individual product pages exist e.g. `/products/tuborg/tuborg-green/`)
**Catalogue/PDF:** No.
**Karnataka manufacturing:** Confirmed — brewery at Nanjangud taluk, Mysuru, Karnataka (₹100 cr can-line + ₹350 cr further Invest Karnataka pledge, per Carlsberg India's own newsroom).

| Brand | KA Confidence | Why |
|---|---|---|
| Tuborg Strong, Tuborg Green | High | KSBCL Supplier Code 0205; also on Madhuloka |
| Carlsberg Elephant (Strong) | High | KSBCL Supplier Code 0205 |
| Carlsberg (Miracle Can, Strong, Smooth) | High | Directly on Madhuloka Bangalore |
| Tuborg Classic w/ Scotch Malts, Tuborg Ice Draft | Medium | Official carlsbergindia.com only, no KSBCL/Madhuloka line item |
| 1664 Blanc | **Low/Unconfirmed** | Official site notes "in selected states" — Karnataka not confirmed either way |
| Tuborg Zero (water/soda), Carlsberg Elephant Strong Soda | N/A (non-alcoholic) | Not beer |

---

## 3. AB InBev India (brands, contract-bottled locally by S P R Distilleries Pvt Ltd — KSBCL Supplier Code 0212)
**Website:** abinbevindia.in (age/location gate only — verified via direct fetch; zero product/ABV data on the public site). Ownership of this domain by AB InBev is inferred from search results, not directly confirmed by ab-inbev.com or a press release.
**Catalogue/PDF:** No — site is an age gate with no product pages accessible.
**Karnataka manufacturing/bottling:** Confirmed via KSBCL supplier registry (SPR Distilleries) + Mysuru manufacturing unit reported in press (Deccan Herald/Precize — not independently verified full-text).

| Brand | KA Confidence | Why |
|---|---|---|
| Budweiser Premium, Budweiser Magnum | High | KSBCL Supplier Code 0212; also Madhuloka |
| Haywards 5000, Knock Out | High | Directly on Madhuloka |
| Hoegaarden (base, Rosee, Nectarine variants) | High | Directly on Madhuloka |
| Corona Extra, Stella Artois | High | Directly on Madhuloka |
| Budweiser 0.0, Budweiser 0.0 Green Apple, Budweiser Beats | **Low/Unconfirmed** | Only on AB InBev's own national site; no KSBCL/Madhuloka listing found |

---

## 4. B9 Beverages (Bira 91)
**Website:** bira91.com is currently **broken** — verified via curl to serve a default Apache placeholder page with a mismatched TLS cert (`*.ksmart.live`). No live official site could be used as a source; data below comes from KSBCL, Madhuloka, and Wayback Machine archives of bira91.com only.
**Catalogue/PDF:** No official catalogue reachable at present.

| Brand | KA Confidence | Why |
|---|---|---|
| Bira 91 Blonde Summer Lager, Bira 91 Boom Super Strong | High | KSBCL Supplier Code 0214 |
| Bira 91 Rise (Rice), Boom Strong, Light, White, Blonde, Gold Wheat Strong, IPA | High (retail-confirmed) | All appear as distinct SKUs on Madhuloka's Bangalore beer category |
| Bira 91 Malabar Stout, Superfresh White (Citrus/Mango/Berry), IPA w/ Pomelo, Bira 91 Gold | **Low/Unconfirmed** | Sourced only from Wayback archives of the now-broken bira91.com; no KSBCL/retail corroboration for Karnataka |

---

## 5. Woodpecker Distilleries and Breweries Pvt Ltd
**Website:** Not directly identified/verified in this research (no official site fetched).
**Catalogue/PDF:** No.
**Karnataka:** High confidence — this is itself a Karnataka-registered KSBCL supplier (Code 0213).

| Brand | KA Confidence |
|---|---|
| White Owl Boss Strong Premium Lager | High — KSBCL listed |
| Woodpecker Natural Lager Glide Premium Mild Beer | High — KSBCL listed |

---

## 6. Khoday Breweries Ltd
**Website:** Not verified in this research.
**Catalogue/PDF:** No.
**Karnataka:** High — Bangalore-headquartered legacy distiller/brewer, KSBCL Supplier Code 0204.

| Brand | KA Confidence |
|---|---|
| Kolt Extra Strong Beer | High — KSBCL listed |

---

## 7. Diageo (Guinness — imported)
**Website:** Global Heineken/Diageo brand sites not independently verified for India-specific Guinness data in this research pass.
**Catalogue/PDF:** No.
**Karnataka:** High — imported and distributed via Brindco Enterprises Pvt Ltd, Bangalore, KSBCL Supplier Code 0972; also on Madhuloka.

| Brand | KA Confidence |
|---|---|
| Guinness Draught (Can) / Guinness Tin | High — KSBCL + Madhuloka |

---

## 8. Sona Beverages Pvt Ltd (Simba)
**Website:** simbabeer.com — verified live, explicitly states distribution "Now Roaring in Goa, Bengaluru, Delhi, Mumbai, Gurgaon…" (direct official confirmation of Karnataka availability). No ABV/catalogue PDF on the site.
**Catalogue/PDF:** No.

| Brand | KA Confidence | Why |
|---|---|---|
| Simba Roar Strong, Simba Jungle Stout, Simba Stout Pint | High | Directly on Madhuloka Bangalore |
| Simba Wit, Simba Jungle Wheat, Simba Roar Premium, Simba Light Pint, Simba Wit Pint | Medium | Same brand family confirmed in Bengaluru per official site, but this exact SKU not independently priced/listed |
| Simba Lager (generic) | Low | Only from third-party review site (unsobered.com), not confirmed by Simba's own site or Karnataka retail |

---

## 9. Geist Brewing Co.
**Website:** geist.in — verified 3 Bengaluru locations (Old Madras Rd/Hoskote, Rajajinagar/Orion Mall, Hennur/Bhartiya Mall) with retail takeaway model.
**Catalogue/PDF:** No.
**Karnataka confidence:** High — this is a Bengaluru-headquartered brewery with confirmed local retail footprint.

| Brand | KA Confidence |
|---|---|
| Kamacitra (IPA), Uncle Dunkel (dark wheat), Witty Wit (witbier), James/James Blond (strong blond ale) | High — all four appear as distinct SKUs on Madhuloka |

---

## 10. TOIT
**Website:** toit.in — 2 Bengaluru brewpub locations confirmed; states beer available "at an MRP store near you" but doesn't name specific retail SKUs.
**Catalogue/PDF:** No.

| Brand | KA Confidence | Why |
|---|---|---|
| Stray Apple, Toit Tint-In-Wit | Medium-High | Both appear as named SKUs on Madhuloka's Bangalore catalog |
| Banger Lager, Basmati Blonde, Hefeweizen, India Pale Ale, Red Ale, Nitro Stout | Medium | Confirmed on tap at Bengaluru brewpubs (official site), but not confirmed as packaged retail SKUs in Karnataka in this dataset |

---

## 11. Mount Everest Breweries (STOK)
**Website:** mounteverestbreweries.com/products/stok/ — full spec table (Strong 7% ABV, Lager 4.8%, Wheat 4.7%; note: site's own FAQ contradicts with "8% ABV" for Strong — an internal inconsistency, flagged not resolved).
**Catalogue/PDF:** Product spec page exists; no formal PDF catalogue.
**Karnataka confidence:** **Medium** — trade press (Brewer World) confirms an official STOK launch event in Bengaluru (Ashok Nagar), but no KSBCL listing or retailer SKU found in this catalog confirming ongoing retail sale.

---

## Brewpub-only / explicitly NOT confirmed for Karnataka retail

| Brewery | Website | Status |
|---|---|---|
| **Arbor Brewing Company** | arborbrewing.in | Bengaluru brewpub (8 on-tap beers, e.g. Idaho 7 Lager, Smooth Criminal) confirmed, but the site itself states its packaged/canned retail beer (Bangalore Bliss Hefeweizen, Beach Shack IPA) is **"Retailing only across Goa"** — explicitly NOT Karnataka despite the Bengaluru taproom. Treat as brewpub-only for Karnataka. |
| **Windmills Craftworks** | windmills-india.com | Bengaluru (Whitefield) brewpub; site has zero mentions of "retail," "bottle," "takeaway," or "store" — strong evidence of on-tap-only operation, no packaged Karnataka retail product. |
| **Byg Brewski** | bygbrewski.com | Bengaluru event-venue/brewpub model; "Packages" page describes catered events with "Freshly Brewed Beers (Availability Of The Day)" — no brand names, no evidence of packaged retail product. |
| **Goa Brewing Co.** | goabrewing.co | Placeholder/under-construction site; Karnataka availability (or lack thereof) is completely unconfirmed either way. |

---

## Unconfirmed / needs disambiguation

- **Murphy's** — ambiguous in the brief: Murphy's Irish Stout (Heineken-owned, UK/Ireland brand) has no confirmed India presence found; most "Murphy's" India search hits are actually **Murphy's Brewhouse**, an unrelated Bengaluru bar venue at The Paul hotel, not a packaged beer brand. Flag for founder clarification before treating as a SKU source.
- **Grizly** (Peach & Black Tea, Pineapple & Okinawa), **Stangen** (Weiss Bier), **Peroni Nastro Azzurro**, **Hunter** (Strong Premium) — all appear as directly-listed, priced SKUs on Madhuloka's Bangalore beer shelf (so retail availability itself is High confidence), but **no brewery/parent company was identified** for Grizly, Stangen, or Hunter in any research report. Peroni is an Asahi-owned Italian brand with presumed India import/distribution not otherwise verified here. These need a dedicated brewery-identification pass before they can be added to the authoritative master database with a producer field populated.
- **Effingut** (Effin Light Lagered Ale, Incider Ale — Cherry Berry/Kashmiri Apple/Mango variants) — appears only via a Wayback Machine archive of Living Liquidz (site was down at research time); confidence Low. Effingut is a known Bengaluru-area craft brewer by reputation, but this was not independently verified in any research report in this dataset — do not state "Bengaluru-based" as fact until confirmed.

---

## Bottom line for the founder

1. **Highest-trust backbone for the initial database:** KSBCL's own supplier-wise price list (13 SKUs across 8 suppliers) is the only source that is simultaneously official, Karnataka-specific, and current — everything on it should be marked High confidence with no caveats.
2. **Madhuloka (Bangalore retailer) is your best volume source** for cross-confirming which of the "brand exists nationally" SKUs (from UBL/Carlsberg/AB InBev/Bira91 official sites) are *actually* on shelf in Karnataka right now — roughly 60+ of the 216 catalog SKUs get a confidence bump this way.
3. **Do not silently upgrade** brand-site-only entries (Cannon 10000, Kalyani Black Label, Zingaro, Budweiser 0.0 variants, most of Bira91's flavored/craft line, 1664 Blanc, most Toit/STOK core beers) to "available in Karnataka" — they are national/global catalogue entries with zero Karnataka-specific corroboration in this research pass.
4. **Arbor Brewing is the clearest trap**: it has a real Bengaluru taproom, which could tempt someone to mark its canned beers "Karnataka available" — the brewery's own site explicitly contradicts that for retail.