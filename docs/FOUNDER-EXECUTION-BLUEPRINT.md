# ValueBrew — Founder Execution Blueprint

*Canonical execution plan until launch. Strategy is closed: ValueBrew is the consumer beer-recommendation app; the KSBCL pipeline is infrastructure and a moat, not the product; no B2B pivot now; consumer validation comes first. This document does not revisit any of that. It only answers: how do we get a real person to successfully use this app, as fast and as cheaply as possible.*

---

## Part 1 — Current State

| Dimension | State Today | Biggest Bottleneck |
|---|---|---|
| **Product** | 4 of 6 canonical screens shipped (Home, Recommendation, Beer Detail, Price Verification), fully spec'd. **[RC1 status note, 2026-08-14]: now run against real data (57 SKUs, 8 beers) and verified end-to-end with zero errors — the "placeholder catalog" and "never run against real data" claims here are from before RC1.** Still never used by a real human. | Has never been used by a real person. |
| **Engineering** | 571 tests, zero architectural pattern breaks across 8 milestones, rigorous governance discipline. **[RC1 status note: now 905 tests (585 Flutter + 320 Python), `flutter analyze` clean.]** | Not currently the constraint — this dimension is ahead of every other one and doesn't need more investment right now. |
| **Data** | KSBCL pipeline produces real government pricing (Stages 1–3 frozen/tested, 4–5 implemented), but has an active, unpatched `true_prior_map` defect that can corrupt canonical identity on rerun, has no built join to the app's `catalog.json`, and has zero ABV/style coverage — no automated source for either exists. **[RC1 status note: the join to `catalog.json` now exists and is automated (`tool/catalog_builder/`); ABV/style coverage is still manually sourced (label photography) and remains the binding constraint — 253 enriched SKUs are blocked purely on missing ABV. The `true_prior_map` defect is unchanged.]** | No real, ABV-complete catalog reaches the app. **[Partially superseded: a real catalog now reaches the app — 57 SKUs — though ABV coverage remains the limiting factor for growing it further.]** |
| **Legal** | Alcohol-advertising/promotion regulatory status of the app as designed has never been checked. Only a narrower, unrelated question (import-data resale) was researched. | Complete unknown, with zero mitigation started. |
| **Design** | Behavior specified in exhaustive detail (Screen Contracts); zero visual/interaction design work, zero real-device usability evidence. | No idea whether the actual experience works for a real person. |
| **Business** | No monetization model, pricing, or unit economics anywhere — deliberately deferred, per the fixed strategy, until after validation. | Not a launch blocker, but a known gap to revisit immediately post-validation. |
| **Validation** | Zero. No user, recruited or otherwise, has ever touched the app or the idea. | **The single largest bottleneck in the company, full stop.** |

---

## Part 2 — Critical Path

Target: *a real person downloads ValueBrew from the Play Store and successfully uses it to decide which beer to buy.*

Only what's actually required to get there, in order:

1. **Legal clearance** — confirm the app as designed is publishable.
2. **Minimal real catalog** — ~100–150 hand-collected SKUs with real ABV, style, size, price.
3. **Real-data integration** — wire the catalog into the existing 4 screens, replacing the placeholder.
4. **Manual QA on real devices** — the full flow works end-to-end with real data.
5. **Compliance basics** — age gate, privacy policy, content rating.
6. **Closed field validation** — real Bangalore beer buyers, behavioral evidence, not self-report alone.
7. **Fix what validation surfaces.**
8. **Submit and launch.**

Everything else — the pipeline defect fix, full pipeline-to-app automation, Search/Browse, Comparison, GTIN/GS1 work, monetization design, marketing, partnerships, B2B exploration — is parking lot (Parts 4–5).

---

## Part 3 — Execution Roadmap

### Phase 0 — Legal Clearance
- **Objective:** Confirm the app can legally exist as designed.
- **Deliverables:** A written legal opinion or a documented, source-cited founder research pass on Karnataka/India alcohol advertising and promotion rules as applied to price-comparison and recommendation apps.
- **Exit criteria:** A clear yes/no/with-conditions answer, in writing, naming any required constraints (disclaimers, language restrictions, age-verification standard).
- **Dependencies:** None — this is the true first step.
- **Effort:** 3–5 days.
- **Biggest risk:** Real answer is "not as designed" and forces language/UX changes into the canon's own Lexicon (e.g. "Recommend," comparative claims) — better to discover this now than after Phase 2.

### Phase 1 — Minimal Real Catalog
- **[RC1 status note, 2026-08-14]: superseded by a different approach** — an automated Catalog Builder was built instead of hand-collecting a shelf-walk catalog; current real output is 57 SKUs / 8 beers, below this phase's 100–150 target. See `docs/PROJECT-BRAIN.md` §16.
- **Objective:** Get 100–150 real, ABV-complete, Karnataka-priced SKUs into `catalog.json`.
- **Deliverables:** A prioritized shelf-walk list (top KSBCL-confirmed and Madhuloka-listed brands); label photos for ABV/style; observed real prices; hand-entered catalog data.
- **Exit criteria:** ≥100 SKUs, every one with non-null ABV, style, size, container type, and a dated real price.
- **Dependencies:** Phase 0 cleared.
- **Effort:** 1–2 weeks, mostly non-engineering.
- **Biggest risk:** Manual collection takes longer than estimated; coverage gaps for less-common brands testers actually ask about.

### Phase 2 — Real-Data Integration & QA
- **[RC1 status note, 2026-08-14]: substantially complete** — real catalog loads, Recommendation → Beer Detail verified end-to-end with zero errors; physical-device QA specifically not yet done.
- **Objective:** Prove the existing app works end-to-end against real, messy data.
- **Deliverables:** `catalog.json` swapped in; full manual walkthrough of all 4 screens; new tests for real-data edge cases the placeholder never exercised (missing fields, near-duplicate names).
- **Exit criteria:** A complete recommendation → detail → verification flow runs with zero crashes on ≥2 physical Android devices; existing test suite passes against the real-catalog build.
- **Dependencies:** Phase 1 complete.
- **Effort:** 3–5 days.
- **Biggest risk:** Real data breaks assumptions the placeholder never tested — expect this phase to surface bugs, budget for it.

### Phase 3 — Compliance & Store Prep
- **Objective:** Clear every named store/regulatory readiness item.
- **Deliverables:** Age-gating implementation; published privacy policy; Play Store content rating; store listing assets built from the real-catalog build.
- **Exit criteria:** Every item in Part 7's checklist that belongs to this phase is objectively met.
- **Dependencies:** Can start once Phase 0 is cleared; doesn't need to wait for Phase 2 to finish.
- **Effort:** 3–5 days, largely parallelizable with Phase 1/2.
- **Biggest risk:** Alcohol-content apps face real store-review scrutiny; underestimating this delays submission at the worst possible time.

### Phase 4 — Closed Field Validation
- **Objective:** Confirm real people can use the real app to make a real decision.
- **Deliverables:** 15–20 real Bangalore beer buyers using the real-catalog app; behavioral follow-up (did they actually buy differently), not just satisfaction survey.
- **Exit criteria:** A majority show a specific, confirmable instance of the app changing a real purchase decision.
- **Dependencies:** Phase 2 and Phase 3 complete.
- **Effort:** 1 week.
- **Biggest risk:** A recruited panel is prone to the Hawthorne effect (people are nicer to a founder's app when they know they're being watched) — mitigate by following up on actual behavior, not just asked opinion.

### Phase 5 — Launch
- **Objective:** Ship.
- **Deliverables:** Bug fixes from Phase 4; final store listing; submission.
- **Exit criteria:** App is live on the Play Store.
- **Dependencies:** Phase 4 shows real signal.
- **Effort:** 2–3 days + store review turnaround (outside your control).
- **Biggest risk:** Review turnaround time and any last-minute compliance findings.

**Total estimated critical-path effort: roughly 5–7 weeks of founder time**, most of it non-engineering.

---

## Part 4 — Parallel Work

Safe to run alongside the critical path without slowing it:

- **`true_prior_map` pipeline defect fix** — protects a real, compounding strategic asset (the canonical identity map), but the launch catalog bypasses the pipeline entirely, so it doesn't block Phase 1–5.
- **KSBCL-pipeline-to-`catalog.json` join automation** — genuinely useful future infrastructure, but the hand-built catalog makes it unnecessary for this launch.
- **Lightweight crash reporting/analytics wiring** — should land *before* launch (it's how you learn from it), but doesn't block any critical-path phase and can be built quietly in parallel.
- **Deeper legal/ToS/liability research** (beyond Phase 0's go/no-go) — can continue after the initial clearance without blocking anything downstream.
- **Branding and visual polish** — valuable, but doesn't gate a functional validation test.
- **Documentation upkeep** (Project Brain, etc.) — low-cost, purely internal, never on the critical path.
- **Partnership conversations** (e.g. Madhuloka) — real relationship-building value, doesn't require app or catalog completion to start.

Each of these is off the critical path because none of them changes whether Phase 0–5 can proceed — they either protect assets that aren't needed for *this* launch, or they generate value that compounds independently of the launch date.

---

## Part 5 — Deferred Work ("Not Now")

- **Full KSBCL pipeline scaling past ~150 SKUs.** Not needed to validate the app; real work, wrong time.
- **Search/Browse Results and Comparison screens.** Canon itself already treats these as non-Core-V1; nothing about launch requires them.
- **GTIN/barcode enrichment, GS1 DataKart relationship.** No launch-blocking dependency on either.
- **B2B/API exploration of any kind.** Explicitly out of scope by the fixed company strategy.
- **Formal Accessibility/Telemetry standards.** Canonically deferred pending a future dedicated standard — correct to leave alone.
- **Monetization/business model design.** Deliberately deferred until real usage exists to design around — revisit immediately after Phase 4, not before.
- **Multi-city or multi-state expansion.** Premature by every measure; the beachhead isn't even validated yet.
- **Native-app polish** (animations, micro-interactions, visual refinement beyond functional). Costs real time and validates nothing.
- **Legacy code cleanup in `lib/`.** Real technical debt, zero launch impact.

Each item here is valuable eventually and explicitly not worth founder time before a real person has used the app.

---

## Part 6 — Founder Weekly Allocation (Next 90 Days)

| Area | % | Justification |
|---|---|---|
| **Engineering** | 25% | Real, necessary work now directly on the critical path — wiring real data, QA, compliance implementation, fixing what validation surfaces. Higher than in earlier strategic exploration because we're now executing the build, not deciding whether to. |
| **Data** | 20% | The hand-built catalog (label photography, price collection) is a genuine, large time cost and sits squarely on the critical path. |
| **User research / validation** | 20% | Still the ultimate gate before spending anything on launch — running Phase 4 and interpreting it honestly deserves a large, protected share of time. |
| **Product** | 15% | Scoping the minimal test product, triaging validation feedback, deciding what's a real bug versus noise. |
| **Legal** | 10% | Front-loaded on purpose — this was flagged as the single most dangerous under-investment in prior review, and it now sits at the very start of the critical path. |
| **Business** | 5% | Kept alive as a placeholder hypothesis, not built out — per the fixed strategy, real business-model work starts after validation, not before. |
| **Marketing** | 3% | Minimal — recruiting validation participants and store-listing copy, nothing beyond that. |
| **Operations** | 2% | Just enough logistics (scheduling shelf-walks, validation sessions) to keep the plan moving. |

**Total: 100%.**

---

## Part 7 — Launch Readiness Checklist

Every item objectively verifiable — no vague standards.

- [ ] A written legal opinion, or documented founder research citing named regulatory sources, confirms the app as designed complies with applicable Karnataka/India alcohol-advertising rules.
- [ ] Age-gating is implemented and blocks any user who does not confirm legal drinking age.
- [ ] A privacy policy is published at a stable, public URL and linked from the Play Store listing.
- [ ] The Play Store content-rating questionnaire is completed and the app carries an appropriate alcohol-content rating.
- [ ] `catalog.json` contains at least 100 SKUs, each with a non-null ABV, style, size, container type, and a dated real Karnataka price observation.
- [ ] All 4 shipped screens (Home, Recommendation, Beer Detail, Price Verification) complete a full user flow against the real catalog with zero crashes, verified on at least 2 physical Android devices.
- [ ] The existing automated test suite passes with zero failures against the real-catalog build.
- [ ] At least 15 real individuals (not solely the founder) have completed a full recommendation → detail → verification flow, and a majority show a specific, confirmed instance of the app changing a real purchase decision.
- [ ] Basic crash reporting/analytics is wired and confirmed to receive events from a real test session.
- [ ] Store listing assets (icon, screenshots from the real-catalog build, description) are complete and use only Lexicon-consistent language — no unqualified "Best," no "Score"/"Rating."
- [ ] A monitored support/contact channel exists for user-reported price errors.
- [ ] The app has been submitted to Play Store review and either passed or has an open, actively-tracked review ticket.

---

## Part 8 — CEO Memo

**To:** The Founder
**Re:** How to think for the next six months

You've spent months proving you can build correct software against ambiguous, adversarial inputs. That's real, and it's rare. It is not the skill this phase needs. The skill this phase needs is tolerance for shipping something imperfect fast enough to learn from it.

Three concrete shifts, starting now:

**Stop treating "unspecified" as a reason to stop.** Your entire engineering history shows a pattern: when something isn't fully specified, you name the gap and refuse to guess. That's correct discipline for a data pipeline processing government records. It is the wrong instinct for building a v1 catalog or running a user test — here, "good enough, dated, and labeled as a guess" beats "not done because it isn't perfect yet." A hand-typed catalog with 120 SKUs and an honest gap for the 121st is a shippable asset. A perfect, fully-automated pipeline with zero users is not.

**Measure yourself in real people, not real tests.** 571 passing tests told you the software does what you specified. It has told you nothing about whether anyone wants what you specified. For the next six months, the only number that should make you feel good is "how many real strangers used this and did something different afterward." Everything else — test count, document count, architectural cleanliness — is a distraction until that number exists.

**Legal and data collection are not blockers to route around — they're the actual work now.** You will spend more hours this quarter walking Bangalore stores with a camera and reading regulatory text than writing Dart or Python. That is correct. It will feel like a demotion from "engineer" to "operator." It isn't — it's the only path from what you've built to something that reaches a real person's hand.

You don't need to become a different kind of founder. You need the same rigor pointed at a faster feedback loop: real catalog, real device, real stranger, real behavior, in weeks, not another architecture document. Everything you've built survives that shift intact — it's still there when you're ready to scale it. It just isn't the thing standing between you and launch anymore. Time is.
