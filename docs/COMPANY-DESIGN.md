# ValueBrew — Company Design

*Written treating ValueBrew as a startup that has just finished its technical foundation. Sources: `docs/PROJECT-BRAIN.md`, `docs/MASTER-ROADMAP.md`, `docs/ROADMAP-ADVERSARIAL-REVIEW.md`. The roadmap itself is frozen and not revisited here — this is about what company gets built around it.*

---

## Part 1 — The Company

**What ValueBrew actually does today** is a narrow thing: help one person in one city decide whether one beer is a good deal. That is not a company. It's a feature.

**What ValueBrew could become**, if the underlying capability is aimed correctly: **the trusted, canonical source of truth for a regulated, fragmented, information-asymmetric market — India's alcohol pricing and product data — starting with beer in Karnataka.** The evidence for this is not the app. It's everything *around* the app: a five-stage pipeline that turns an adversarial, inconsistent government PDF into structured, versioned, auditable data; a governance model with eleven extracted conventions specifically about never inventing a fact; and a market-research corpus that independently confirms almost every other source in this category is broken, stale, or self-contradicting (Living Liquidz down, Zauba stale since 2013, Tonique dated 2023 with a live "coming soon" placeholder, Bira91's own domain unreachable, STOK's own page disagreeing with itself on ABV). **Nobody else in this market has bothered to do this rigorously.** That's the real asset.

**Mission:** Make it structurally impossible for information asymmetry to cost an Indian alcohol buyer money — starting by being the one source in the category that never guesses, never silently resolves a conflict, and never goes stale without saying so.

**Vision (5–10 years):** ValueBrew becomes the data and trust layer underneath India's alcohol retail — not necessarily the app a consumer opens every day, but the pipeline that retailers, distributors, journalists, and eventually other consumer products build on, state by state, category by category, the same way a weather API becomes infrastructure rather than a destination. The consumer app is the wedge and the validation instrument, not necessarily the endgame.

**Competitive advantage:** The willingness to do the unglamorous work competitors have skipped — parsing a government PDF correctly, cross-checking a contradiction instead of hiding it, physically photographing a label because no API will ever have it — combined with an engineering discipline that makes the resulting data actually trustworthy in a category where trust is the scarce resource, not the data itself.

**Moat:** (1) The pipeline itself — hard to replicate without the same painstaking, adversarially-reviewed discipline; a fast-follower with more capital but less discipline will ship worse data faster, and in a trust-driven category that's a losing trade. (2) Physically-collected data (ABV, label facts) that cannot be scraped — every hour spent walking Bangalore stores is a real, non-arbitrageable cost a copycat has to pay again. (3) Regulatory know-how in a category most well-funded entrants will get sloppy about (Section 135AA, state-specific excise rules) — a barrier that protects the careful player, not the fast one. (4) Eventually, direct data-supply relationships with retailers/distributors, which compound the way any two-sided marketplace's data advantage compounds.

**Why this company deserves to exist:** Because right now, in Karnataka, a beer buyer trying to find out whether they're being overcharged has to trust either a retailer with every incentive to overcharge them, or a patchwork of scraped, stale, contradictory websites — and the market research proves this isn't a hypothetical, it's the observed state of every alternative source checked. Somebody rigorous should own that gap. The evidence in this repository says the team behind ValueBrew is unusually well-suited to be that somebody — *if* the company gets built around that strength instead of around a single, unvalidated consumer feature.

---

## Part 2 — The Product

**Is the current 4-screen consumer recommendation app the best possible first product? No.**

It's a reasonable *engineering* deliverable. It is not the smallest thing that tests whether the company's actual thesis — that trustworthy alcohol pricing data is valuable enough for someone to change behavior or pay for it — is true. It bundles three untested bets into one product: that people will open a dedicated app before buying beer, that price-per-alcohol is the comparison they actually want, and that a polished recommendation UX is necessary to prove either of those things. All three could be wrong independently, and the current product doesn't let you tell which one failed if it does.

**Better wedge:** Don't build a recommendation app. Build a **radically simple, always-current price-and-fact lookup**, distributed through the cheapest possible channel — a WhatsApp/Telegram bot, or a bare webpage — where someone can ask "what's the real price of Kingfisher Strong 650ml" and get a source-cited, confidence-labeled answer pulled from the same KSBCL data the pipeline already produces. This tests the actual differentiator (trustworthy data, repeat-worthy enough to come back to) without requiring the Recommendation Engine, the Screen Contracts, or a native app at all.

**Beachhead market:** Stay in Bangalore — the market research is already built around it and the KSBCL pipeline is Karnataka-specific by construction — but narrow the *customer*, not just the geography (see Part 3).

**Smallest product capable of proving the core insight:** A single-purpose lookup tool with zero screens beyond a search box, backed by real KSBCL data, used by a few dozen real people over a few weeks, measured on one thing: do they come back a second time without being asked to. That's a testable proxy for "is this trustworthy and valuable enough to matter" that can be built in days, not the weeks the current app's remaining milestones assume.

---

## Part 3 — The Customer

**Ideal first customer:** Not the average casual beer buyer picking up whatever's cold. The ideal first customer is the **repeat, price-aware enthusiast** — someone who buys beer weekly or more, already shops around (the kind of person Madhuloka's own multi-supplier listings exist for), and is annoyed enough by inconsistent pricing to seek out a better source unprompted. This person will use a bare lookup tool without needing a polished app to be convinced.

**Who to deliberately ignore, for now:** Impulse buyers who decide at the shelf (they will never open an app or bot first, no matter how good it is). Anyone outside Bangalore (the data doesn't support them yet, and diluting focus there wastes the beachhead). Price-insensitive premium buyers (they're not the segment this data helps). And — deliberately — retailers and distributors as *paying* customers, for now. Serving consumers and B2B simultaneously from day one splits focus before either side is proven.

**Second customer:** Once individual repeat users trust the data, the natural second customer is **content and community, not commerce** — the beer enthusiasts, home-bar owners, and small reviewers/bloggers already implicitly present in the market research (Toit, craft-brewery communities) who need a reliable ABV/price citation and would embed or reference ValueBrew as a source. This is low-cost, high-leverage distribution that doesn't require a sales process.

**Tenth customer:** A retailer or distributor who wants visibility into competitive pricing, or a small data buyer (a journalist, analyst, or brand-owner's market-intelligence function) who wants structured Karnataka pricing trends. This is the first real signal that the data-layer thesis in Part 1 is commercially real, not just architecturally elegant.

---

## Part 4 — Strategy

**If ValueBrew succeeds, it's because:** the team proved, cheaply and early, that trustworthy alcohol pricing data changes real behavior for a real segment, then let the data-pipeline discipline (already genuinely strong) compound into a defensible position that a faster, less careful competitor can't easily copy — expanding state by state the way the KSBCL pipeline was built stage by stage.

**If ValueBrew fails, it's because:** the team kept building — more screens, more tests, more canonical documents — without first spending a week finding out whether anyone actually wants what's being built, and by the time that question got asked, there was no runway left to answer it honestly.

**Five most likely failure modes, ranked by probability:**

1. **The core thesis is wrong.** Beer purchase in India is driven by brand, occasion, and availability far more than by price-per-alcohol comparison shopping — and this has never once been tested against a real person anywhere in the Project Brain. Highest probability, highest impact, and currently the least de-risked assumption in the entire company.
2. **Legal/regulatory exposure kills the product as designed.** India's alcohol advertising and promotion rules are genuinely strict and largely unaddressed in this repository beyond a narrower, unrelated import-data question. A real constraint here could invalidate the product's core language (Recommend, Better, comparative claims) after it's already built.
3. **Data can't scale without capital or a team.** ABV/label data requires physical human effort with no automation path found anywhere in the market research. A solo founder caps this hard around a few hundred SKUs, in one city, indefinitely.
4. **Over-engineering as a failure mode in itself.** The demonstrated pattern — 20 canonical documents, 571 tests, an 11-convention governance model, all before a single real user — is evidence of a founder temperament that reaches for rigor before reaching for a customer. This risk is not hypothetical; it's already partially realized in how this project got to this point.
5. **No monetization path even with adoption.** India generally prohibits direct online alcohol sales, so there's no transaction to take a cut of. Affiliate/referral models need retailer buy-in that doesn't exist yet, and nothing in the Brain or the roadmap has priced this out.

**Mitigations, in the same order:**

1. Run the cheapest possible thesis test (see the adversarial review's concierge-test recommendation) this week, before touching more code.
2. Get an actual legal read — even an informal paid consult — before any public launch, and design the product's language defensively in the meantime.
3. Start B2B/data-partnership conversations in parallel with consumer validation, specifically to test whether the *data itself* has value independent of consumer scale — this both derisks the scaling ceiling and opens a second, cheaper path to revenue.
4. Set a hard, self-enforced rule: no further architecture or process investment until real users have used a real product. This is a discipline fix, not a technical one, and it has to be imposed on purpose because the team's own habits have already shown they won't impose it by default.
5. Treat monetization as a Day-1 design question, not a Day-100 afterthought — sponsored retailer placement, data licensing, or content-adjacent revenue should be sketched now, even roughly, before more product is built on top of an unpriced business model.

---

## Part 5 — Founder Allocation (Next 6 Months)

| Area | % | Why |
|---|---|---|
| **User research** | 20% | The single most unvalidated, highest-risk dimension in the entire company. Every other allocation is downstream of what this discovers. Deserves the largest deliberate share, not leftover time. |
| **Data** | 20% | Still a genuine, real bottleneck — but scoped to the minimum needed to run a validation test, not the full 400–600 SKU vision. Equal weight to user research because you can't test the thesis without *some* real data underneath it. |
| **Engineering** | 15% | Enough to wire real data into what already exists and keep it stable — not enough to build the remaining screens, the pipeline fix, or the automated catalog join. That work isn't earned yet. |
| **Business (strategy, monetization, financial modeling)** | 10% | Currently zero anywhere in the company's documentation. A solo founder needs at least a working hypothesis for how this becomes a business before spending months building toward it — this can't stay an afterthought any longer. |
| **Partnerships** | 10% | A single conversation with a retailer like Madhuloka is cheap, fast, and could simultaneously unlock better data, a distribution channel, and evidence for the B2B thesis. High leverage per hour spent. |
| **Product** | 10% | Defining the smallest test product (the lookup tool, not the full app) and interpreting what user research finds — real work, but secondary to actually doing the research. |
| **Legal** | 7% | Flagged as dangerously under-invested by the adversarial review. Doesn't need to consume large amounts of time, but needs dedicated, early time — not zero, not parallel-and-forgotten. |
| **Marketing** | 5% | Early positioning and messaging tests only — not paid acquisition, which is premature before the thesis is validated. |
| **Operations** | 3% | Minimal at this stage. Just enough to not drop anything; elaborate process here is exactly the trap already visible in the engineering history. |

**Total: 100%.**

The single biggest reallocation this implies relative to the last six months: user research and business strategy go from effectively 0% to 30% combined, and engineering drops from what appears to have been the dominant share to 15%. That's the correction this company needs most.

---

## Part 6 — Brutal Truth

If this were my own money: **I would not fund another engineering sprint on the current roadmap as written. I would tell the founder to pause, run one week of real customer contact, and be honestly prepared to pivot the wedge — not abandon the company, and not blindly continue it either.**

Here's the case, without softening it. This repository contains twenty frozen canonical documents, an Architectural Decisions Record, a five-stage government-data pipeline with its own eleven-convention governance model, and five hundred seventy-one tests — built for a product that has never once been shown to a real human being. That is not a data point buried in the Brain; it is the loudest signal in it. A founder capable of that much discipline is a genuinely rare asset. A founder who spent that discipline before finding a single customer is showing me exactly the failure mode I'd worry most about as an investor: **excellent execution pointed at the wrong question.**

The roadmap you've already approved is, given everything upstream of it, the right roadmap — it correctly refuses to scale the pipeline or the catalog before validating demand. But I want to be honest about what that roadmap actually is: it is a plan to spend more weeks building a real product before finding out if anyone wants it, wrapped around one cheap validation step in the middle. I would not approve *that* structure with my own money. I would insist the cheap step — real conversations with real Bangalore beer buyers, a Wizard-of-Oz test with no code involved — comes first, alone, this week, before another hour goes into the catalog or the app. If it fails, you've lost a week, not a quarter. If it succeeds, everything already built (the engine, the tests, the pipeline discipline) becomes genuinely valuable instead of merely impressive.

I also want to name the thing nobody in this project has said out loud yet: **the current product may be solving a real problem for the wrong business.** The evidence in the Brain points more convincingly toward "we are excellent at turning adversarial government data into trustworthy structured facts" than toward "consumers in Karnataka want a beer-recommendation app." Those are different companies. The first is a data/trust business that could plausibly expand category by category and state by state, sold in part to a small number of serious buyers. The second is a consumer app in a single city, in a single low-frequency, impulse-driven category, with no monetization path anyone has priced out and a real regulatory cloud over its core language. If I had to bet which of those two companies is fundable, it's the first one — and the current roadmap, as approved, is building toward the second.

So: **not abandon.** The underlying capability is real and rare. **Not blind continuation** either — the current plan still risks spending real time proving engineering completeness rather than customer demand. My verdict is **pause the app-building work, run the cheapest possible test of real demand this week, and go into that test genuinely willing to hear that the winning version of this company is a data business serving a handful of serious buyers, not a beer app serving casual consumers.** That is the only version of "continue" I would put my own money behind.
