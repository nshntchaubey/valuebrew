# [Working Name: ValueBrew] — Product Requirements Document
## Phase 2 of 5: UX Architecture, Screens & States, Data Model

> Every major decision in this document is tagged [P#] referencing the 10 product philosophy principles established before this phase. Principle key at the bottom for reference.

---

## 1. Information Architecture & Navigation

```
Home
 ├─ Search
 │   └─ Beer Detail / Value Breakdown
 │        ├─ Similar & Better Alternatives
 │        ├─ Price History
 │        └─ Confirm / Submit Price
 ├─ Scan (barcode)
 │   └─ Beer Detail / Value Breakdown (same screen as above)
 ├─ Group & Budget Mode
 │   └─ Multi-beer basket recommendation
 ├─ Nearby Stores (secondary, map-based)
 └─ My Decisions (personal history — ratings, confirmed prices, past picks)
```

**Home screen behavior is explicitly stateful, not fixed** [P5, P7, P9]:
- **Cold-start (0–4 confirmed decisions):** Home opens directly to Search + Scan, no personalized module. No taste quiz, no onboarding preference form — nothing is asked, only offered [P9].
- **Warmed (5+ confirmed decisions):** Home begins surfacing a lightweight "worth checking out" module above search, sourced from passive behavior (what was searched, confirmed, rated) — never from an explicit preference form [P9]. This is the seed of the recommendation-first destination state, introduced gradually rather than as a launch-day bet.

The nav is deliberately four items, not eight. Barcode/receipt-upload/store-locator are all real features from the original brief, but none of them earn a permanent nav slot at launch — they live inside the core loop (scan is a mode of search, not a separate destination) [P5].

---

## 2. Core Screen: Beer Detail / Value Breakdown

This is the single most important screen in the product — the one screen that has to carry the entire "answer, don't list" promise.

**Layout, top to bottom:**
1. Beer name, brewery, style tag
2. **The single number**: Value Score, large, with a one-line plain-language verdict ("Good value" / "Fair" / "Overpriced for this ABV") — never just a bare score [P2]
3. **Provenance strip**, directly under the score, always visible, never a tooltip you have to hunt for: "Price confirmed 2 days ago by 3 people" or "Estimated — no confirmed price yet, tap to confirm" [P1, P4]
4. SKU breakdown: size, ABV, calories, cost/litre, cost/ml-of-alcohol
5. "Similar & better value" — ranked list, not alphabetical, each entry showing its own value score for direct comparison
6. "Rate this" — lightweight, one-tap taste tags (not a text review requirement) — feeds personalization without asking for it explicitly [P9]
7. "Confirm this price" or "Submit a price" — see Section 4

**Why the provenance strip is non-negotiable, not a nice-to-have:** this is the single highest-leverage application of Principle 1 in the entire product. A value score with no visible confidence signal is functionally indistinguishable from Livcheers' plain price listing — the provenance strip *is* the differentiation, not a footnote to it.

---

## 3. Empty, Loading, and Error States — Designed First

Per Principle 10, these are specified before the happy path screens above, not after.

| State | Trigger | Design response | Principle |
|---|---|---|---|
| **No price data for a known beer in this city** | Beer exists in catalog, zero confirmed prices locally | Show the SKU/ABV/calorie facts (always known, static data) with an honest "No confirmed price yet — be the first" CTA, never hide the beer or show a stale/wrong number | P4, P1 |
| **Barcode not recognized** | Scan doesn't match any SKU | Fall straight into search pre-filled with whatever OCR/metadata was captured, plus a lightweight "help us add this" flow — framed as unlocking the answer for *this* scan, not a generic contribution ask | P3, P4 |
| **Zero search results** | Typo or genuinely uncatalogued beer | Fuzzy "did you mean," plus the same "help us add this" path — never a dead end | P4 |
| **Cold-start home (first open)** | New user, 0 decisions logged | Straight to Search + Scan, zero forms, zero quiz | P5, P9 |
| **Submission pending moderation** | User just submitted a price | Immediate acknowledgment + provisional display marked "unconfirmed, pending" rather than silence until reviewed — the contributor should see their own contribution reflected instantly, even before full trust promotion | P3, P1 |
| **Network/search timeout** | Connectivity issue | Show last-known cached result set with an explicit "showing saved results" flag rather than a blank spinner or silent failure | P1, P7 |

---

## 4. Price Submission Flow — the Flywheel's Core Mechanism

Designed explicitly around Principle 3 and Principle 6: contribution must pay the contributor back immediately, or it won't scale.

1. User scans or searches a beer with no confirmed local price, **or** taps "confirm/update" on an existing one.
2. Enters price (photo-of-receipt OCR pre-fills this where possible — future phase; MVP is manual entry with a numeric keypad, not a form).
3. **Immediately** (not after moderation) the user sees their own full value breakdown computed from what they just entered — this is the payoff that makes step 2 worth doing [P3].
4. Behind the scenes: the submission enters a moderation/consensus pipeline (outlier detection against Benchmark data, duplicate detection against recent submissions for the same SKU+store) before being promoted to the canonical, publicly-shown Price. Until promoted, it's visibly marked "unconfirmed" to *other* users, but already fully usable by the person who submitted it [P1, P4].

This directly operationalizes the flywheel from Principle 6: every submission both serves the submitter instantly and compounds freshness for everyone else.

---

## 5. Group & Budget Mode

Secondary but high-value flow (ranked #5 in the earlier top-ten decisions). Kept deliberately simple for MVP: enter a budget and a headcount, get a ranked basket combining 2–3 SKUs across value and style variety, not just "cheapest N items." This is explicitly *not* built as a separate app section with its own navigation weight [P5] — it's a mode entered from Search, one extra input, not a parallel product.

---

## 6. Data Model

### 6.1 Core Entities

- **Beer** — id, name, brewery, style_id, description, is_craft (bool)
- **Style/Category** — id, name (Lager, Wheat, Stout, IPA, etc.), typical ABV range
- **SKU** — id, beer_id, size_ml, package_type (bottle/can/pint), abv, calories, barcode(s) — one SKU can have multiple regional barcode variants
- **State** — id, name, regulatory_flag (digital-engagement-permitted / restricted), MRP_regime (fixed / deregulated) — this field exists specifically because of the Karnataka deregulation finding; it is not safe to assume this is static, so it is versioned, not hardcoded
- **City** — id, name, state_id
- **Retailer** — id, name (nullable — many stores are independent)
- **Store** — id, name, retailer_id (nullable), city_id, geo (lat/lng), address
- **Price** — id, sku_id, store_id, amount, confirmed_at, confidence_score, source (crowdsourced/manual/OCR), submitted_by (user_id, nullable for anonymized aggregation)
- **PriceSubmission** — id, sku_id, store_id, amount, submitted_by, submitted_at, moderation_status (pending/promoted/rejected/duplicate), promoted_to_price_id (nullable) — kept as a distinct entity from Price so raw submissions and canonical, trusted prices are never conflated [P1, P4]
- **User** — id, home_city_id, taste_profile (JSON, built from behavior not forms), contribution_count, trust_score
- **Rating** — id, user_id, sku_id, score, taste_tags (array), submitted_at
- **ValueScore** — id, sku_id, city_id, cost_per_litre, cost_per_ml_alcohol, percentile_in_style, computed_at — a computed/cached entity, not user-entered
- **Benchmark** — id, style_id, city_id, avg_cost_per_ml_alcohol, updated_at — the reference distribution ValueScore percentiles are computed against
- **Decision** — id, user_id, sku_id, action (viewed/confirmed_price/chose_alternative/rated), occurred_at — this table is what powers both the North Star Metric ("Weekly Decisions Made," from Phase 1) and the personalization signal for Principle 9; it is the single most important table for proving product-market fit early, and should exist from day one even though nothing in the UI directly displays it yet

### 6.2 Relationships (ER, simplified)

```
Beer 1───* SKU
SKU  1───* Price ───* Store
SKU  1───* PriceSubmission ───* Store
SKU  1───* Rating ───* User
SKU  1───1 ValueScore (per City) ───* Benchmark (per Style, per City)
Store *───1 City ───1 State
User 1───* PriceSubmission
User 1───* Decision ───1 SKU
```

### 6.3 Indexes

- `SKU.barcode` — indexed, non-unique (multiple SKUs can legitimately share a regional barcode variant in edge cases)
- `Price(sku_id, store_id, confirmed_at DESC)` — the freshness-lookup path, hit on every Beer Detail screen load
- Full-text / trigram index on `Beer.name` + `Beer.brewery` — powers the sub-second search from Principle 5's core loop
- Geospatial index on `Store.geo` — powers Nearby Stores
- `PriceSubmission(sku_id, store_id, submitted_at)` — powers duplicate-detection at write time, not just read time

### 6.4 Caching Strategy

- **ValueScore and Benchmark are expensive aggregates** — cached per SKU×City with invalidation triggered by a new *promoted* Price landing for that SKU+city, not on a fixed timer alone. This keeps freshness honest [P1, P4] without recomputing on every single read.
- **Search autocomplete** — cached aggressively (short TTL, high hit rate expected given a finite, slow-growing beer catalog relative to query volume)
- **"Similar & better value" list** — shorter TTL than search, since it depends on ValueScore freshness directly

---

## Principle Key (for reference through remaining phases)

1. Trust via visible, structured proof (Airbnb)
2. Expose system state to reduce anxiety (Uber)
3. Contribution must serve the contributor first (Waze)
4. "Correct enough now" beats "perfect eventually" (Google Maps)
5. Protect the smallest possible habit loop (Duolingo)
6. Optimize the flywheel, not the funnel (Amazon)
7. Become infrastructure, not a destination (CamelCamelCamel)
8. Every transaction leaves a durable personal artifact (Vivino, Spotify)
9. Personalize from behavior, never from asking (Spotify)
10. Storyboard failure states before happy paths (Airbnb)

---

## What's Next

- **Phase 3:** Technical Architecture (stack, hosting, search engine implementation) + Pricing Intelligence detail (OCR, fraud/spam/outlier detection logic behind the moderation pipeline sketched in Section 4) + Search implementation specifics
- **Phase 4:** Value Engine formula specification + AI Features + Growth mechanics (tying explicitly back to Principles 3 and 6) + Monetization + full Legal/Compliance detail
- **Phase 5:** Phased Roadmap + AI Development Plan (Claude Code / Cursor-ready task breakdown)
