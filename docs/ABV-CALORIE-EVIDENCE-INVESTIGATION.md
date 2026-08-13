# ValueBrew — ABV & Calorie Evidence Investigation

**Decision adopted 2026-08-13.** The Part 5 clarification below — a verified photograph of the manufacturer's own printed label qualifies as `manual_observation` — has been incorporated into `docs/CATALOG-ENRICHMENT-PLAYBOOK.md` (Part 4, new Step 1a) and `docs/BEER-KNOWLEDGE-BASE-ARCHITECTURE.md` (Part 5). No schema or code changes were made. This document is retained as the record of the evidence and reasoning behind that decision.

*A research document, not architecture. Nothing here is adopted — every recommendation below is a proposal for you to accept, reject, or amend. Produced after four real founder enrichment sessions hit the identical wall on every single beer: `beer_master.csv` has no ABV or calorie source, and neither, in practice, does anything else tried so far. This document asks one question with evidence, not opinion: is the current evidence standard — Manufacturer-tier only, meaning the manufacturer's own official publication or direct physical observation of the product — actually achievable for a founder building this catalog primarily through desk research, or does it need to change, and by how little?*

---

## Part 1 — Audit: What the Documentation Actually Requires

**The standard is uniformly hard everywhere it appears. There is no soft version anywhere in the canon.**

| Layer | Exact language | Hard or soft? |
|---|---|---|
| `enrichment_schema.py` (code) | `_VALID_SOURCE_TYPES = {"manufacturer", "manual_observation"}` — any other value is a structural validation failure | **Hard.** Enforced, not advisory. |
| Beer Knowledge Base Architecture Part 5 | *"the two tiers the Catalog Enrichment Playbook's own research workflow actually produces; a retailer listing is explicitly corroboration-only and is never recorded as a claim's `source_type` on its own"* | **Hard.** |
| Catalog Builder Architecture Part 3/4 | *"never estimated from a 'typical style' figure"*; *"an ABV claim with no cited source is rejected outright, never silently accepted"* | **Hard.** |
| Catalog Enrichment Playbook Part 1/4/5/10 | *"A label is Manufacturer-tier evidence, full stop"*; *"the honest answer is Unknown, not 'close enough'"*; *"the brewery wins, always"* | **Hard**, repeatedly, in absolute language. |

I found **zero instances**, anywhere in the frozen canon, of language that treats a well-corroborated retailer or aggregator figure as sufficient, even as a fallback. This surprised me going in — I expected to find at least one place where the standard softened under real-world pressure. It doesn't. Every document independently arrived at the same hard line.

**One structurally important finding:** `manual_observation` is not a third, weaker tier below `manufacturer`. Per Catalog Builder Architecture Part 1, it means *"a human... directly reading a label, a can, or a brewery's own page and recording what it says, with the observation itself as the citable evidence."* Both `manufacturer` and `manual_observation` are Manufacturer-tier in substance — they differ only in whether the founder read it off the company's own web page or off the company's own physical product. This distinction matters directly for the recommendation in Part 5.

---

## Part 2 — Real Evidence, Source by Source

Investigated for the four beers already enriched (Kingfisher Premium, Kingfisher Strong Premium, UB Export Strong Premium, UB Export Premium Lager — all United Breweries). Every finding below is from an actual visit this session, not a general claim.

**Manufacturer website — reachable, but empty of the data needed.** Earlier automated research (`WebFetch`) reported `unitedbreweries.com` as unreachable behind an age gate. That conclusion was too strong. Using an interactive browser, the age gate is a single trivial date-of-birth entry — genuinely no obstacle to a human. Past it, I reached the real, official `Kingfisher Premium` brand page (confirmed real pack sizes: 330ml, 500ml can, 650ml — matching our own candidate data exactly). **The page contains brand marketing copy only — no ABV, no calories, anywhere in the text.** Product photography exists but is not legible at any resolution the page serves. This is the single most important finding in this document: the access problem from the earlier dry run was partly a tooling artifact, but the *deeper* problem is real and not a tooling problem — the manufacturer's own official site does not publish this data at all, for any of the four beers checked.

**Brewery spec sheets / technical PDFs.** None found, for any of the four beers, after direct searching. No evidence one exists publicly.

**Product labels, via photography.** Not directly reachable (no founder has the physical product in hand for a remote session). Indirectly reachable through crowd-uploaded photos on Open Food Facts — see below — with a real, demonstrated identity risk.

**Excise registrations / government filings.** KSBCL's own pricing data (`beer_master.csv`) — already confirmed, repeatedly, this session — carries no ABV or calorie field at all; it is a price and identity register, nothing else. **FSSAI** (India's food-safety regulator) does require alcoholic beverage registration, but its public lookup tool takes a *14-digit license number as input* — it is a verification tool, not a search-by-product-name database. There is no practical path from "I want Kingfisher Premium's ABV" to an FSSAI record without already knowing which license to check, and no confirmation that a found record would even contain ABV/calorie figures rather than just safety-compliance metadata.

**Open Food Facts — real data exists, with a real, demonstrated trust problem.** A genuine barcode entry for "Kingfisher Beer – 650ml" (`8905002180007`) carries real nutrition data — `71 kcal per 100ml`, structured macros — that reads as photo-derived, not invented (the ingredients field literally transcribes `"SINCE 1857 KINGFISHER STRONG BEER KINGFI THE KING OF GOOD 2"`, clearly OCR'd or hand-copied from an actual label photo). **But that label is for Kingfisher *Strong*, filed under a generic "Kingfisher Beer" entry that doesn't distinguish Premium from Strong.** This is exactly the failure mode the current standard exists to prevent — a real, sourced fact attached to the wrong product. Using it without independently re-verifying which product the underlying photo actually shows would be a real trust violation, not a hypothetical one.

**GS1 / GEPIR.** Checked directly. **Confirmed to carry no product-attribute data at all** — a GTIN resolves only to the owning company, never to nutrition facts or ABV. Ruled out entirely, not merely deprioritized.

**Distributor catalogs.** Not directly tested; by the canon's own existing taxonomy these are Retailer-tier by definition, same disqualification as below.

**Retailer sites, Untappd, BeerAdvocate, RateBeer, nutrition-tracking apps (MyNetDiary, MyFoodDiary, SnapCalorie, etc.).** All checked, repeatedly, across all four beers this session and the prior one. All structurally excluded from `source_type` today — and correctly so, per Part 1's audit; nothing here argues these should become directly citable. Worth recording as a fact, not a recommendation: these sources are **highly mutually consistent** — "4.8% ABV" for Kingfisher Premium and "8% ABV" for the Strong variants appear across many independent instances of this source class, every time. Consistency is not the same as a citable source, and this document does not treat it as one.

**Archived webpages (Wayback Machine).** Attempted; rate-limited (`429`) before a usable result was returned. Genuinely inconclusive — not a negative finding, an untested one. Worth a founder's own follow-up, not a claim made here.

---

## Part 3 — Is the Current Standard Operationally Achievable?

**As currently written and currently practiced, no — not for beers researched remotely, which is the realistic mode for the large majority of a 100+ SKU catalog.**

The evidence: four real beers, four real research sessions, one consistent result — `0 of 4` reached a citable Manufacturer-tier source through remote research. This is not a sampling artifact; the same specific wall was hit each time (official site reachable, but marketing-only; every other real source structurally excluded by design).

The standard **is** achievable in exactly one mode: a founder who physically holds the product and reads the label. Playbook Part 4 already ranks this as source #1, "full stop" — correctly. But for a catalog aiming at 100+ SKUs built substantially at a desk, treating "the brewery's own official site" as a real, working fallback (Part 4, source #2) does not hold up under this session's evidence. It is the theoretical second option that, in practice, resolves to zero real facts.

---

## Part 4 — Risks of Changing Anything Here

Named explicitly, since this field feeds the one number (Value Score) the whole product exists to get right:

- **The exact failure this standard was built to prevent is demonstrably real, not theoretical** — the Kingfisher Strong/Premium mislabeling on Open Food Facts is direct, first-hand proof that third-party crowd data can attach a real fact to the wrong product.
- **Any widening of what counts as citable evidence must not blur the line between "I observed this myself" and "someone else told me this."** The entire trust model rests on that line.
- **A photo is not automatically equivalent to physical possession.** A photo can be of the wrong product, an old formulation, a different market's packaging, or simply illegible — all real risks a physical can doesn't have.

---

## Part 5 — Recommended Policy

**Do not add a new source tier. Do not touch the schema. Clarify what `manual_observation` already, ambiguously, allows.**

The schema already has exactly the right shape: `manufacturer` (their own official publication) and `manual_observation` (a human directly reading the manufacturer's own real content, cited). The Playbook's own Part 4 narrowed `manual_observation` to *"if you physically have one"* — narrower than the architecture's own definition requires. That narrowing, not the schema, is what's blocking real progress.

**Recommended clarification:** `manual_observation` legitimately includes reading a clear, legible **photograph** of the real product's own label — retailer product photography, a crowd-uploaded photo (Open Food Facts and similar), a distributor catalog image — under two conditions, both mandatory:

1. **The founder personally verifies the photo is genuinely of the specific product being enriched** — matching brand, style, and pack size visible in the photo itself, never trusting the hosting page's own title or category alone. (This directly closes the exact failure mode found in Part 2 — the fix is "verify before citing," not "avoid photos entirely.")
2. **`source_name` cites the specific photo, not the general site** — e.g. `"product label photo, Open Food Facts barcode 8905002180007, verified against visible pack size and branding, checked 2026-08-13"` — never `"Open Food Facts"` alone. The claim must stay exactly as falsifiable and re-checkable as a physical-label citation already is.

This is a documentation change only. `source_type` stays `manual_observation`, exactly as already defined — no new enum value, no code change, no schema change, nothing for `enrichment_schema.py` to enforce differently than it already does. It closes the actual gap this session's evidence found (photos of real labels exist and are usable; the Playbook just never told anyone they counted) without opening the one this document's own evidence shows is real (unverified third-party claims).

**What this does not change:** retailer text claims, Untappd/BeerAdvocate/RateBeer figures, and nutrition-tracker numbers remain exactly as excluded as they are today. Nothing about the hard "Manufacturer-tier only" standard changes — only which real-world artifacts count as satisfying it.

---

## Exact Documentation Changes Proposed (not applied)

**`docs/CATALOG-ENRICHMENT-PLAYBOOK.md`, Part 4, item 1** — currently:

> *"1. The can or bottle itself, if you physically have one. The single best source that exists. A label is Manufacturer-tier evidence, full stop."*

Proposed addition immediately after it (new item, not a rewrite of the existing one):

> *"1a. A clear, legible photograph of the real product's own label — a retailer's own product photo, a crowd-uploaded photo (e.g. Open Food Facts), a distributor catalog image — counts the same way, on two conditions: you personally confirm the photo matches this exact beer and pack size (never trust the hosting page's own title alone), and you cite the specific photo, not the general site, in `source_name`. This is still manual observation of the manufacturer's own real content — it is not a retailer's claim about a number."*

**`docs/BEER-KNOWLEDGE-BASE-ARCHITECTURE.md`, Part 5** — currently defines `manual_observation` without stating whether a photographed label qualifies. Proposed addition to that field's own row:

> *"Manual observation includes a clear, verified photograph of the real product's own label — not only physical possession — provided the founder personally confirms product identity from the photo itself and cites the specific photo in `source_name`."*

Neither change touches `enrichment_schema.py`, `CATALOG-CONTRACT-1.0.md`, or any Product Decision. Both are clarifications of an existing, already-adopted category, not new architecture.

---

## Summary

Manufacturer-tier evidence, as the canon already defines it, is real and achievable — just not through the one channel the Playbook implicitly leaned on (the brewery's own website), which this session's direct evidence shows doesn't carry this data for any of the four beers tried. The smallest fix is not to lower the bar; it's to recognize that a verified photograph of a real label is the same evidence a physical can already is, and to say so explicitly where the Playbook currently doesn't.
