# [Working Name: ValueBrew] — Product Requirements Document
## Phase 1 of 5: Vision, Market Research, User Research, Feature Prioritization

> This is Phase 1 of a phased PRD. Sections 5–16 (UX, Data Model, Technical Architecture, Search, Pricing Intelligence, Value Engine, AI Features, Growth, Monetization, Legal, Roadmap, AI Development Plan) will follow once this foundation is validated. Building all 16 sections in one pass produces shallow, unresearched output on the sections that matter most — this document is deliberately narrower and deeper.

---

## 0. Critical Finding — Read This First

Before any product design, the competitive reality has to be on the table, because it changes what "winning" looks like.

**Livcheers** (Gurugram, founded 2023) already operates a multi-city price comparison and brand discovery platform for beer, wine, and spirits in India, including Bangalore, Mumbai, Delhi, Kolkata, Hyderabad, and Pune. It aggregates prices from public sources, explicitly does not handle delivery, and its own positioning line is "Compare Prices. Browse Collection. Discover Brands. Repeat." That is functionally the same core loop you've described.

**HipBar** (Chennai, founded ~2015, acquired by CRED in 2021, backed by Diageo) owns the transactional side — an RBI-licensed wallet plus age-verified delivery/pickup, active in Bangalore, Hyderabad, Tamil Nadu, and (via a Flipkart partnership) West Bengal and Odisha.

**magicpin** layers store discovery and cashback on top of beer listings, aggregating thousands of liquor stores.

This means "beer price comparison app for India" is not a green field — it's a category with an incumbent already live in your launch city. That's not a reason to stop; it's a reason to be precise about the wedge. The rest of this document is built around one thesis:

**Livcheers is broad and shallow — many alcohol categories, list-and-browse depth. The wedge is narrow and deep: own beer specifically, and go deeper than anyone else on the actual purchase-decision math (cost per ml of alcohol, cost per litre, SKU-level value scoring, freshness/confidence signals) rather than just listing prices.** This is the same playbook Vivino used against generic review apps by going deep on wine, and CamelCamelCamel used by going deep on Amazon pricing instead of general shopping.

If, after reading this, the "many alcohol categories" framing appeals to you more than "beer, done properly" — that's a legitimate call, but it puts you in direct, symmetric competition with a funded incumbent instead of building around them. Recommend confirming this before Phase 2.

---

## 1. Vision

### Mission
Give anyone standing in front of a beer shelf in India the confidence to know, in under five seconds, whether what's in their hand is a good buy — and make that confidence available nowhere else, because nobody else is building the underlying math.

### Problem Statement
Beer buyers in India face a fragmented decision: dozens of SKUs varying by brand, pack size (330ml can / 500ml can / 650ml bottle / pint), ABV, and price — with no standard unit to compare them on. Existing apps solve *discovery* (what beers exist, what do people think of them) or *transactions* (get alcohol delivered), but not the specific moment of "which of these should I actually buy, right now, for the money." That moment is underserved because it requires SKU-level structured data (not just brand-level ratings) and comparison math, which is more data-engineering-intensive than a ratings app and less profitable-looking than a delivery app — which is likely why no one has built it well yet, even with two funded competitors adjacent to it.

### Success Metrics
| Metric | Why it matters |
|---|---|
| **Time-to-decision** (search → decision made) | The core promise is speed; if this creeps past ~10s, the product has failed its own thesis |
| **Weekly repeat search rate** | Beer buying is a low-frequency, high-context event (not daily); repeat usage proves retained trust, not habit |
| **% of searches resulting in a "better alternative" click-through** | Proves the recommendation engine, not just the lookup, is delivering value |
| **Price data freshness (median age of price shown)** | The product's credibility is entirely dependent on data being current; this is the metric most likely to quietly kill the product if ignored |
| **Crowdsourced submission rate per active user** | Since Livcheers/magicpin already aggregate "public" data, defensibility depends on a community data loop they don't have |

### North Star Metric
**Weekly Decisions Made** — a "decision" = a user views a beer's full value breakdown and either (a) taps "buy this" intent, (b) taps a suggested alternative, or (c) submits/confirms a price. This ties directly to the core promise (fast decisions) rather than vanity metrics like DAU or searches, which reward browsing over deciding.

### Product Principles
1. **Answer, don't list.** Every screen should end in a decision, not a table the user has to interpret themselves.
2. **Depth over breadth, for now.** Beer only, done exhaustively, beats "all alcohol" done shallowly — this is the entire competitive thesis against Livcheers.
3. **Freshness is the product.** A stale price is worse than no price; the app must be honest about confidence, not just complete.
4. **Never facilitate the sale.** Given India's alcohol e-commerce regulation (see Section 2.5), the product must stay a comparison/decision layer, not a transaction layer — this is also a legal necessity, not just a design choice.
5. **The community is the moat.** Public-source price aggregation is replicable in a weekend; a trusted, high-frequency contributor base is not.

---

## 2. Market Research

### 2.1 Competitive Landscape

| Player | Model | Category scope | Geography | Strength | Gap you can exploit |
|---|---|---|---|---|---|
| **Livcheers** | Price/brand comparison, public-source aggregation, no delivery | Beer, wine, spirits | 6+ metros incl. Bangalore | First-mover, multi-city coverage already live | Shallow per-SKU data; no alcohol-per-rupee style value math; no visible crowdsourcing/freshness signal; general-purpose, not beer-optimized UX |
| **HipBar** | RBI-licensed wallet + delivery/pickup | Beer, wine, spirits | Bangalore, Hyderabad, TN, WB, Odisha (state-dependent) | Real transactions, Diageo/CRED backing, regulatory groundwork already done | Not a decision tool — assumes you already know what to buy |
| **magicpin** | Store discovery + cashback, beer content/blog | Beer-focused content, broader local commerce | Pan-India metros | Strong store network, SEO content reach | Not a real-time SKU comparison tool; cashback-driven, not decision-driven |
| **Untappd / Vivino** (int'l reference) | Ratings, check-ins, social discovery | Beer / wine globally | Global, weak India depth | Habit-forming social loop, huge catalog | Explicitly not shopping-decision focused (per your own brief) — the gap you're targeting |
| **Comparify** (adjacent, India) | Cross-app price comparison for cabs/grocery/food delivery | Non-alcohol | India | Proves Indian consumers already adopt "compare before you buy" apps for other categories | Doesn't touch alcohol — validates category behavior, not a direct competitor |
| **State portals** (e.g., Chhattisgarh CSMCL) | Government-run ordering | Category-dependent | State-specific | Official, compliant | Clunky, state-siloed, zero UX investment |

**Read:** No player currently combines (1) SKU-level granularity, (2) explicit value-per-rupee math, and (3) a visible freshness/confidence system. That combination is the opening.

### 2.2 SWOT

**Strengths:** Founder has real engineering background to direct AI tooling; clear, narrow initial market (Bangalore) with strong beer culture and craft scene; principled non-transactional model sidesteps the hardest regulatory problems.

**Weaknesses:** No existing user base or data; pre-launch, competing against a funded incumbent with 2+ years of head start on coverage; "price app" categories have historically struggled with data freshness at scale (see Section 2.4 risk).

**Opportunities:** Karnataka permits some digital alcohol commerce and has a strong urban craft-beer culture; a beer-only focus can go deeper than any competitor's beer coverage; value-math (cost/ml alcohol) is a genuinely unbuilt feature nobody in this set offers.

**Threats:** Livcheers or magicpin could add SKU-level value scoring faster than you can build a user base, since they already have coverage and distribution; state-level alcohol advertising/e-commerce law can change abruptly and unevenly (see 2.5); low switching cost — nothing stops a user from checking two apps.

### 2.3 Porter's Five Forces

- **New entrant threat: Moderate-high.** The core feature (price list + math) is not hard to clone technically; the defensibility has to come from data freshness and community, not the UI.
- **Supplier power (retailers/data sources): Low-moderate.** No retailer has to cooperate for the MVP (public-source + crowdsourced data), but formal retailer partnerships would meaningfully increase data quality later.
- **Buyer power: High.** Zero cost to switch between comparison apps; the product has to win on trust and speed every single session, not lock-in.
- **Threat of substitutes: High.** Asking a store clerk, or just picking a familiar brand, is the default "no app" behavior being displaced — the bar isn't "better than Livcheers," it's "better than not checking at all."
- **Competitive rivalry: Moderate, concentrated.** Two credible, funded players already exist in adjacent positions (Livcheers on comparison, HipBar on transaction); rivalry will intensify if either moves into your specific wedge.

### 2.4 Market Sizing (estimates — methodology-sensitive, treat as directional)

Beer-market-size research reports for India vary widely by methodology — figures range from roughly **$6–9B to $14–18B for 2025**, depending on whether on-trade (bars/restaurants) is included and how craft/premium segments are counted. Use a mid-range figure (~$9–14B) as a working assumption, not a cited fact, until this is cross-checked against a primary source (e.g., IWSR or Euromonitor, which require paid access).

- **TAM:** All legal-drinking-age beer buyers in India engaging in off-trade (retail) purchase — tens of millions of people, loosely bounded by the ~$9–14B off-trade beer market.
- **SAM:** Urban smartphone users in states with digitally-engaged retail alcohol culture and no outright ban on such apps (Karnataka, Maharashtra, West Bengal, Telangana, Delhi, Goa, etc.) — realistically a low-to-mid single-digit-million user base in year 1–2 metro focus.
- **SOM (Bangalore, Year 1):** A realistic beachhead target is tens of thousands of monthly active users pulled from Bangalore's urban, craft-beer-literate population — this should be validated with real user interviews before being treated as a planning number, not derived top-down from TAM.

### 2.5 Legal & Regulatory Reality (critical constraint, not an afterthought)

- **Alcohol cannot be bought or sold online in most of India by law** — this is precisely why HipBar operates as a payment wallet + delivery logistics layer rather than an "online store," and why Livcheers explicitly states it does not offer home delivery. Your "never facilitate the sale" principle (1.4) isn't just good product design — it's very likely a legal necessity for a fast, low-friction, single-state launch.
- **Google Play** prohibits depicting or encouraging alcohol use by minors and portraying excessive/binge drinking favorably, and treats apps as "age-restricted" only if alcohol sale is the app's focus — a comparison app that doesn't sell should sit in a materially easier compliance lane than a delivery app, but still needs a clean age-gate at onboarding and careful ad/content review.
- **State-by-state variance is real and non-optional to design for:** Karnataka, Maharashtra, West Bengal, and a few others permit varying degrees of digital alcohol engagement; several states restrict it heavily. The data model (Section 6, Phase 2) needs a state-level feature flag from day one, not retrofitted later.
- Advertising alcohol (even indirectly) is restricted under Indian advertising codes and via app-store ad policy; monetization design (Phase 2, Section 13) needs to route around direct alcohol-brand advertising, not just Play Store policy compliance.

---

## 3. User Research

### 3.1 Personas

**"Rahul the Regular"** — 27, works in tech in Bangalore, buys beer 2–3x/week for himself and casual gatherings. Knows his 4–5 go-to brands but is price-sensitive and hates feeling like he overpaid. JTBD: *"When I'm at the store and my usual brand looks pricier than I remember, I want to know instantly if it's actually a bad deal or just my imagination, so I don't either overpay or walk away from something fine."*

**"Priya the Host"** — 31, hosts get-togethers monthly, buying for a group with mixed preferences and a budget. JTBD: *"When I'm buying for 8 people with different tastes, I want to quickly compare value across several beers at once, so I maximize what the group gets for the budget without spending 20 minutes reading labels."*

**"Arjun the Explorer"** — 24, craft-beer enthusiast, wants to try new styles but is wary of paying a premium for something that isn't actually better. JTBD: *"When I see an unfamiliar craft beer, I want to know if the price premium is justified by ABV/quality/rarity or if it's just marketing, so I can decide if it's worth the risk."*

**"Deepa the Deal-Hunter"** — 35, buys beer occasionally, highly price-conscious, willing to visit a slightly farther store to save money. JTBD: *"When I'm about to buy, I want to know if a nearby store has the same beer cheaper, so I don't leave money on the table for a five-minute walk."*

### 3.2 Pain Points (validated by market gap, not yet by direct interviews)
- No standard unit to compare a 330ml can against a 650ml bottle against a pint.
- Price memory is unreliable — "is this normal or did it go up?" has no easy answer today.
- Existing apps (Livcheers, magicpin) show *a* price, not whether that price is *good*.
- Discovering a "better" alternative currently requires already knowing the category well.

### 3.3 User Stories (sample, Must-Have tier)
- *As Rahul,* I want to search a beer by partial name and see results in under a second, so I don't stand in the aisle waiting.
- *As Priya,* I want to see a value score alongside price so I don't have to do the ABV/price/size math myself.
- *As Arjun,* I want to see "similar beers" ranked by value, not just alphabetically or by rating.
- *As Deepa,* I want to know how recently a price was confirmed, so I can trust it before walking somewhere else.

### 3.4 Emotional Arc
Anxiety ("am I about to overpay / pick something bad?") → Relief (instant, legible answer) → Confidence (decision made, no regret) → Advocacy (tells a friend, or contributes a price next time). The product's entire UX should be optimized for compressing the anxiety-to-confidence gap to near-zero, since that gap is the whole reason the product exists.

---

## 4. Feature Prioritization (MoSCoW)

### Must Have (MVP — Bangalore launch)
- Instant search (beer name, brand, partial match, <1s response)
- Full SKU breakdown per beer: size, ABV, price, cost/litre, cost/ml-of-alcohol, calories
- **Value Score** — the single differentiating number vs. Livcheers/magicpin's plain listings
- "Similar beers" and "better value alternatives" ranked list
- Crowdsourced price submission (simple flow — this is the data moat Livcheers doesn't visibly have)
- Price freshness / confidence indicator ("last confirmed 2 days ago")
- Bangalore store coverage, city-scoped launch
- Basic age-gate onboarding (legal necessity, not optional)

### Should Have (v2)
- Barcode scanning for instant lookup in-aisle
- Nearby store price comparison with map
- Price history / trend per SKU
- Receipt OCR to auto-submit prices (accelerates data density)
- Personal taste-profile-based recommendations

### Could Have (v3+)
- Karnataka-wide, then multi-city expansion
- Community leaderboards / "Beer Scout" gamification for top contributors
- Retailer-side partnership dashboards
- Push notifications for price drops on saved beers

### Won't Have (initially — explicitly out of scope)
- **Any in-app purchase, checkout, or delivery flow** — stay a decision layer, not a transaction layer (legal + focus reasons, Section 2.5)
- Spirits, wine, or other alcohol categories — the entire competitive thesis depends on beer-only depth (Section 0)
- Social/check-in features (Untappd's lane, not the wedge here)
- National launch — premature before Bangalore data density and retention are proven

**Reasoning note:** Every "Must Have" item is chosen specifically to be something Livcheers, HipBar, or magicpin does not currently do well or at all — SKU-level value math, visible freshness signals, and a crowdsourcing loop. Anything that doesn't sharpen that differentiation is deliberately deferred, even if it's a good idea in isolation.

---

## What's Next

This covers Sections 1–4 of the original 16-section brief. Recommended next phases:

- **Phase 2:** UX (screens, flows, wireframes) + Data Model (entities, ER diagram, caching strategy)
- **Phase 3:** Technical Architecture + Search implementation + Pricing Intelligence (OCR, fraud/spam prevention, verification)
- **Phase 4:** Value Engine formulas + AI Features + Growth + Monetization + Legal/Compliance detail
- **Phase 5:** Phased Roadmap + AI Development Plan (the Claude Code / Cursor-ready task breakdown)

Before Phase 2, it's worth deciding: proceed as beer-only against Livcheers' broader-but-shallower position, or reconsider scope now that the competitive picture is clear — since that decision materially changes the data model and UX in Phase 2.
