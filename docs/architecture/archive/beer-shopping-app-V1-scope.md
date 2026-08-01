# [Working Name: ValueBrew] — V1 Scope & Execution Plan
## Ruthless MVP definition — supersedes Phase 2 scope for initial build

> This document is the actual build spec for the first 30 days. Phase 2 (full PRD) remains the long-term design reference, but nothing beyond what's listed here should be built until the assumptions below have real answers from real users.

---

## Core promise being tested
"Help a user standing in front of a beer shelf make a better purchase decision in under 5 seconds."

## V1 Feature Set (build this, nothing more)
1. Search (name/brand, fuzzy match) — only entry point, no barcode/scan
2. Manually-seeded catalog, ~100–150 SKUs covering common Bangalore shelf presence
3. Value Score (cost/litre, cost/ml-of-alcohol, percentile within style)
4. Beer Detail screen: SKU picker, price, score, one-line verdict, "last checked [date]"
5. Ranked "similar / better value in this style" list
6. "This looks wrong" flag — routes to founder, not a moderation pipeline

**Architecture note:** no backend required at this scale. A Flutter app reading a bundled or remotely-fetched JSON catalog, computing the score locally, is sufficient and correct for this size of problem.

## Explicitly cut from V1
Barcode/camera/shelf-scan · full PriceSubmission + moderation/consensus pipeline · user accounts/auth · ratings/reviews/taste tags · recommendation-first home · Group & Budget Mode · nearby-store/map/live geospatial pricing · receipt OCR · "My Decisions" UI (keep the underlying event log, drop the screen) · multi-city/multi-state logic

## Fake/manual/human-operated instead of engineered
- **Catalog seed data**: Karnataka's May 2026 deregulated MRP list (government-published) + magicpin/Livcheers/city-guide data + direct store visits
- **Freshness/moderation**: "this looks wrong" taps go directly to the founder — spreadsheet-tracked, not a pipeline
- **Similar/alternatives ranking**: precomputed offline via script against the seed catalog
- **Support**: direct message/email, not a ticketing system
- **User research**: direct interviews via personal network / Bangalore craft-beer communities, not analytics dashboards
- **Keep from day one despite being "engineering"**: a simple event log (search, view, score-view) — cheap now, expensive to reconstruct later

## Riskiest assumptions to validate with the first 100 users
1. People actually check an app mid-purchase, standing in a store — not just decide on instinct
2. The Value Score is something people weigh, not just raw price
3. A small, manually-updated, honestly-labeled dataset is trustworthy enough without live crowdsourcing
4. Search-only friction is acceptable — barcode isn't required yet
5. Beer specifically is the category people want this for, not whisky (which dominates the market by value)
6. Karnataka's newly deregulated pricing produces ongoing real variation, not a one-time re-basing that quickly flattens

Validation approach for each is direct usage-pattern tracking (search timing, click-through to alternatives, flag-tap rate, category drift in feedback) plus direct interviews — not surveys before there's real usage to ask about.

## Day 1 → Day 30

| Days | Focus |
|---|---|
| 1–3 | Build seed catalog by hand from MRP list + existing aggregator data + store visits |
| 3–7 | Build Value Score/Benchmark logic as a standalone script against the seed catalog |
| 5–10 | Build the app: Search → Beer Detail → similar/alternatives, no accounts, no server |
| 10–14 | Dogfood in real Bangalore stores; fix obvious data/UX issues |
| 14–18 | Soft-launch to 10–20 people from personal network / a Bangalore craft-beer community |
| 18–25 | Iterate on what actually broke, informed by direct interviews against the assumptions above |
| 25–30 | Expand toward first 100 users via relevant communities; read repeat-visit rate and Weekly Decisions Made as the real PMF signals |

Nothing from Phase 2's full design (submission pipeline, recommendation engine, barcode, multi-city) should be built until at least assumptions 1–3 above have a real answer.
