# ValueBrew — Master Roadmap

*Strategic analysis and execution plan, built on `docs/PROJECT-BRAIN.md`. Written from the perspective of a founder/PM/staff-engineer/investor evaluating this project for the first time. Opinionated by design.*

---

## 1. Maturity Assessment

| Dimension | Maturity | Evidence |
|---|---|---|
| **Product vision** | High (arguably over-mature) | 20 frozen canonical documents, a full Lexicon, an ADR with named principles. More design rigor than most funded seed-stage startups have at Series A. |
| **User value** | Unvalidated | Zero evidence anywhere in the Brain of a real user touching the app. No usability findings, no retention data, no "does this change what someone buys" evidence. The entire value thesis (alcohol-adjusted value comparison) is internally authored, never user-tested. |
| **Data quality** | **Weakest link, by a wide margin** | App requires non-nullable ABV/style per SKU; KSBCL data has neither; market research confirms no scraping path exists for ABV — it requires physical label photography. Real catalog with confirmed Karnataka pricing is ~100–190 SKUs today, not the 1,000 originally targeted. Even KSBCL's own pipeline has an active, unfixed defect that can silently corrupt canonical identity on rerun. |
| **Recommendation engine** | Mature for its scope, but starved | `generateRecommendation`/`verifyPrice` are well-built, well-tested, compiler-enforced against invalid states. But it operates on budget + one optional style only, and has never run against a real, ABV-complete catalog. A well-built engine with nothing real to run on. |
| **Engineering architecture** | Very high — possibly too high | 571 tests, zero architectural pattern breaks across 8 milestones, a governance model with 11 extracted conventions. This is enterprise-grade discipline applied to a pre-revenue, pre-user, solo-founder product. |
| **Mobile application** | Thin slice, well-executed | Only 4 of 6 canonical screens exist (Home, Recommendation, Beer Detail, Price Verification). No Search/Browse, no Comparison. Never run against real production data end-to-end. |
| **User experience** | Unknown | No user testing evidence exists anywhere in the corpus. |
| **Scalability** | Premature concern | A full Postgres+OpenSearch design exists on paper for a product with no backend and 216 unverified SKUs. This is solving a problem the product doesn't have yet. |
| **Launch readiness** | Low | No catalog-build step connecting KSBCL's `beer_master.csv` to the app's `catalog.json` (explicitly named as unbuilt future work in the pipeline's own master architecture). App store compliance (age-gating, content rating, alcohol-advertising rules) is a tracked, unactioned risk. No committed backend decision. |

**Bottom line:** ValueBrew has built a cathedral of process around an empty catalog. The rigor is real and mostly not wasted — but it has been spent in the wrong order. Everything downstream of data is more mature than the data itself.

---

## 2. The Current Bottleneck

**There is no real, ABV-complete Karnataka beer catalog reaching the app — and the pipeline that would produce one does not exist end-to-end.**

Two structural facts make this the single limiting factor, not one of several equally-important gaps:

1. **The KSBCL pipeline and the app have never been connected.** Stage 5 produces `beer_master.csv`; the app consumes a bundled `catalog.json` (per `pubspec.yaml`, per CLAUDE.md's "no backend in V1, local JSON catalogue"). The step that would turn one into the other is explicitly named in the pipeline's own master architecture as *future, not-yet-built work* (§8, master §10.4). Nothing in the Brain describes this step existing.
2. **Even if that join existed today, it would produce a catalog that can't power the core feature.** ValueBrew's entire differentiator is alcohol-adjusted value — price divided by ABV. KSBCL's government price list has no ABV field. The market research corpus confirms, independently and repeatedly, that no scraping source reliably has it either. The only real path is physical label photography — a task that has not been scoped, scheduled, or started against the actual launch SKU list.

Every other maturity gap is downstream of this one. The engine can't be validated without real data. The UX can't be tested without something real to show a user. Launch readiness is moot without a catalog to launch with. Scalability work is solving for a scale the product hasn't earned yet. Fix the data problem and every other dimension becomes testable within days; leave it, and the other eight dimensions can improve indefinitely without the product getting closer to a real user's hands.

---

## 3. Dependency Graph

**Must happen first (nothing else matters until these are true):**
- Decide the launch catalog's actual size and sourcing method (see §5 — this decision itself gates everything downstream)
- Acquire real ABV + style + price for the launch SKU set, by whatever method the above decision picks
- Get that data into `catalog.json` in the schema the app already expects
- Smoke-test the existing 4-screen app end-to-end against that real catalog (not the placeholder)

**Can happen in parallel (independent of the data work, don't block it and aren't blocked by it):**
- App Store / Play Store compliance research: age-gating requirements, content rating, India alcohol-advertising regulatory check (currently untracked as a *legal* question, only tracked as a generic "compliance" risk — see §5 critique)
- Fixing the `true_prior_map` defect in `canonical_resolve.py` (only matters once the pipeline is actually relied on for a rerun — not before)
- Backend/hosting decision for future versions (irrelevant to a bundled-JSON V1 launch)
- Legacy-code-lineage cleanup in `lib/`

**Nice-to-have (real value, not launch-blocking):**
- Search/Browse Results Screen Contract + screen
- Comparison screen
- GTIN/barcode enrichment, GS1 DataKart relationship
- Full KSBCL-pipeline automation and scaling past the launch SKU set
- OpenSearch/Postgres backend

**Post-launch (don't even plan these yet):**
- Canonical-to-canonical merge mechanism
- Accessibility/Telemetry standards
- Pan-India expansion
- Import-brand detection (legally gated behind Section 135AA review regardless)
- Trade-off Explanation / second Strong Preference / Confirm-as-Is

---

## 4. Roadmap to Play Store Launch (v1, pre-critique)

### Milestone 1 — Fix the Data Foundation
- **Goal:** Make it possible to get real, ABV-complete data into the app at all.
- **Deliverables:** A catalog-build script (`beer_master.csv` + hand-collected ABV/style → `catalog.json`); fix or work around the `true_prior_map` defect if the pipeline will be rerun before launch.
- **Success criteria:** One command turns pipeline output into a valid `catalog.json` the app already knows how to load.
- **Risks:** Scope creep into building the full future enrichment architecture instead of the minimum join needed for launch.
- **Effort:** 3–5 days.
- **Why here:** Nothing downstream can be tested against anything real until this exists.

### Milestone 2 — ABV/Style Enrichment for a Launch-Scoped SKU Set
- **Goal:** Real ABV, style, size, and price for enough SKUs to make the app actually useful in one city.
- **Deliverables:** A curated, prioritized SKU list (start from KSBCL's confirmed rows + Madhuloka's top sellers); a physical label-photography pass at a handful of Bangalore retailers; ABV/style entered against the catalog schema.
- **Success criteria:** ≥100 SKUs with real, verified ABV + price + style.
- **Risks:** This is manual, unglamorous, and easy to under-budget; it is also the actual bottleneck, so it cannot be skipped or automated away.
- **Effort:** 1–2 weeks, mostly non-engineering time.
- **Why here:** This is the literal bottleneck identified in §2 — nothing else in the roadmap outranks it.

### Milestone 3 — Real-Catalog Integration & Validation
- **Goal:** Prove the existing 4-screen app actually works end-to-end against real data.
- **Deliverables:** `catalog.json` swapped in for the placeholder; every existing screen (Home, Recommendation, Beer Detail, Price Verification) manually walked through against real SKUs; regression pass on the 571 existing tests plus new tests for real-data edge cases (missing ABV, duplicate names, price gaps).
- **Success criteria:** A person can complete a real recommendation → detail → price-verification flow on a real device against real Bangalore beers, start to finish, with no crashes and no obviously wrong output.
- **Risks:** Real data will violate assumptions the placeholder never tested (blank fields, duplicate near-identical names) — expect this milestone to surface bugs, not just confirm success.
- **Effort:** 1 week.
- **Why here:** This is the first point where the product can be evaluated as a product, not as an architecture exercise.

### Milestone 4 — Compliance & Store Readiness
- **Goal:** Clear the known, named release-readiness risks.
- **Deliverables:** Age-gating/verification approach; content-rating declaration; published privacy policy; store listing assets.
- **Success criteria:** App passes Play Store's own content-review checklist for alcohol-related apps.
- **Risks:** Alcohol-related apps face non-trivial store review scrutiny; underestimate this and it becomes a launch blocker discovered too late.
- **Effort:** 3–5 days, can start earlier in parallel.
- **Why here:** Genuinely parallelizable with M1–M3; sequenced here only because it doesn't matter until there's an app worth submitting.

### Milestone 5 — Closed Field Validation
- **Goal:** Find out if real people want this before spending more on data breadth.
- **Deliverables:** 15–20 real Bangalore beer buyers using the real-catalog app; structured feedback on whether the recommendation/verification loop changes a real purchase decision.
- **Success criteria:** A majority of testers report the app told them something they didn't already know, or changed what they bought.
- **Risks:** This is the step most likely to invalidate the whole product thesis — that's the point of running it before scaling the catalog further.
- **Effort:** 1 week.
- **Why here:** Cheapest possible test of the single most unvalidated dimension (user value), run as soon as there's something real to test.

### Milestone 6 — Launch Polish & Submission
- **Goal:** Ship.
- **Deliverables:** Bug fixes from M5 feedback; final store listing; submission.
- **Success criteria:** App is live on the Play Store.
- **Risks:** Store review turnaround time; last-minute compliance findings.
- **Effort:** 1 week + review turnaround (variable, outside your control).
- **Why here:** Terminal milestone.

---

## 5. Self-Critique — Attacking This Roadmap

Playing the founder trying to kill this project:

**Sequencing mistake — you're still gating the whole roadmap on 100+ SKUs of manually-photographed data before ever showing a human the app.** Milestone 5 (the only step that tests the actual unvalidated risk — does anyone want this) is dead last, after two full milestones of data collection. If the answer to "do people want alcohol-adjusted value comparison" is no, you will have spent 3+ weeks finding that out the slow way. Field validation should move earlier and the catalog it's tested against should be smaller.

**Hidden assumption — the core product thesis itself is untested, and the roadmap treats it as settled.** Nowhere in the entire Brain is there evidence anyone has confirmed that "cost per unit of alcohol" is a real purchase driver for Karnataka beer buyers, as opposed to brand loyalty, taste, or availability. The roadmap should not assume the recommendation engine's premise is correct; it should be built to falsify it cheaply.

**Missing work — there is no legal/regulatory review of whether an app that publishes alcohol prices and recommendations is even permissible in Karnataka.** The Brain tracks import-data legal risk (Section 135AA) in exhaustive detail but never once raises the more basic question: does India or Karnataka restrict alcohol advertising/promotion in a way that touches a price-comparison-and-recommendation app? This is a real launch-blocking unknown that isn't in the roadmap at all.

**Unnecessary work, flagged directly — the entire KSBCL five-stage pipeline, its governance model, and its adversarial-review discipline may be solving a problem this stage of the company doesn't have yet.** It is genuinely impressive engineering. It is also, per the Brain's own founder-execution-plan document, slower and more expensive than the alternative: one person with a spreadsheet and a phone camera can hand-build a 100–150 SKU launch catalog in about a week — faster than fixing the pipeline's defect, building a catalog-join step, and scaling automated ABV sourcing that doesn't actually exist yet. **Milestone 1 as written (fix the pipeline, build the automated join) is over-engineering for a launch catalog this size.** The KSBCL pipeline is real, valuable infrastructure — for scaling past several hundred SKUs. It is not on the critical path to a first launch.

**Opportunity to simplify — collapse the launch catalog to a hand-curated list, sidestep the pipeline entirely for v1.** Skip the `true_prior_map` fix, skip the automated catalog-build step, skip KSBCL-pipeline reliance altogether for launch. Manually assemble ~100 SKUs (name, brand, style, size, ABV via label photo, an observed retail price) directly into `catalog.json`'s existing schema. This is not a lesser version of the roadmap — it's a faster path to the exact same Milestone 3 outcome, without touching Python at all.

**Another simplification — Milestone 4 (compliance) doesn't need to wait for a real catalog; some of it (privacy policy, age-gate mechanism, the regulatory question above) should start on day one, in parallel with the manual catalog build, not sequenced as its own milestone later.**

---

## 6. Revised Roadmap

### Milestone 1 — Hand-Built Launch Catalog (replaces old M1 + M2)
- **[RC1 status note, 2026-08-14]: superseded by a different approach.** Rather than a hand-built catalog bypassing the KSBCL pipeline, an automated Catalog Builder (`tool/catalog_builder/`) was built to join the pipeline's real pricing data against a curated `enrichment/` knowledge base — see `docs/PROJECT-BRAIN.md` §16. Current real output: 57 publication-ready SKUs across 8 beers, below this milestone's 100-SKU target (253 more are enriched but blocked on missing ABV). Left below as the original, not-taken plan.
- **Goal:** Get 100–150 real, ABV-complete, Karnataka-priced SKUs into `catalog.json`, without touching the KSBCL pipeline.
- **Deliverables:** A short, prioritized shelf-walk list (Madhuloka's top sellers + confirmed KSBCL brands); label photos for ABV/style; prices from the shelf walk or Madhuloka's site; hand-entered `catalog.json`.
- **Success criteria:** ≥100 SKUs, every one with real ABV, real style, real size, real price.
- **Risks:** Manual data entry errors; coverage gaps for less common brands. Acceptable — this is a validation catalog, not the permanent one.
- **Effort:** 1 week, mostly non-engineering.
- **Why here:** This is the fastest possible route to a real, testable product. No pipeline, no defect fix, no automated join required.

### Milestone 2 — Legal/Regulatory Check (new, runs in parallel with M1)
- **Goal:** Confirm an alcohol price-comparison-and-recommendation app is legally publishable in Karnataka/India at all, and what constraints (advertising language, disclaimers, age-gating) apply.
- **Deliverables:** A short legal opinion or informed founder research pass, specifically on alcohol advertising/promotion regulation as it applies to a recommendation app (distinct from the transaction/e-commerce question, which the app doesn't touch — it never facilitates a purchase).
- **Success criteria:** A clear yes/no/with-conditions answer, in writing.
- **Risks:** This could be a genuine blocker discovered too late if skipped; treat as unblocking, not optional.
- **Effort:** 2–4 days, can run fully in parallel with M1.
- **Why here:** Should never have been buried inside a later "compliance" milestone — it's a go/no-go question, not a checklist item.

### Milestone 3 — Real-Catalog App Validation
- **[RC1 status note, 2026-08-14]: substantially complete.** The real catalog (57 SKUs) loads and Recommendation → Beer Detail was verified end-to-end with zero errors; not yet walked through on a physical Android device specifically.
- **Goal:** Confirm the existing 4-screen app works end-to-end against real, messy, hand-collected data.
- **Deliverables:** `catalog.json` swapped in; manual walkthrough of all four screens; new tests for real-data edge cases the placeholder never exercised.
- **Success criteria:** A complete recommendation → detail → verification flow works on a real device with no crashes.
- **Risks:** Real data will break assumptions the placeholder didn't test.
- **Effort:** 3–5 days.
- **Why here:** Unchanged in logic from the original M3, just reached faster.

### Milestone 4 — Field Validation (moved earlier, smaller catalog is fine)
- **Goal:** Find out if the core thesis is real, before investing further.
- **Deliverables:** 15–20 real Bangalore beer buyers, given the real-catalog app, asked whether it changed a real decision.
- **Success criteria:** A majority say it told them something they didn't know or changed what they bought.
- **Risks:** This might fail — that's the point of running it now, cheaply, instead of after scaling the catalog.
- **Effort:** 1 week.
- **Why here:** Moved up from position 5 to position 4 specifically because it's the highest-information, lowest-cost step in the whole roadmap, and everything after it should be conditioned on its result.

### Milestone 5 — Store Readiness & Submission
- **Goal:** Ship, assuming M4 validates the thesis.
- **Deliverables:** Age-gating implementation, content rating, privacy policy, store listing, submission.
- **Success criteria:** Live on the Play Store.
- **Risks:** Store review scrutiny for alcohol-related content.
- **Effort:** 1 week + review turnaround.
- **Why here:** Only reached once M4 says it's worth reaching.

### Explicitly deferred, not forgotten
KSBCL pipeline automation, the `true_prior_map` fix, the catalog-build join, and scaling past ~150 SKUs all become **real** work again the moment M4 validates the thesis and the catalog needs to grow past what one person can hand-build. That's the correct trigger for reinvesting in the pipeline — not before.

---

## 7. The Single Highest-Leverage Next Task

**Hand-build a ~100-SKU real Karnataka catalog and put the existing app in front of 15–20 real beer buyers to see whether alcohol-adjusted value comparison actually changes what they buy.**

Not "fix the `true_prior_map` defect." Not "build the catalog-join pipeline." Not "resolve the Search/Browse Results canonical gap." Every one of those is real, correctly-identified work — and every one of them is engineering completeness, not leverage. None of them tells you whether ValueBrew should exist.

This task is the highest-leverage thing on the board because it's the cheapest available experiment that tests the one assumption everything else in the Project Brain quietly depends on: that a Karnataka beer buyer actually wants price-per-alcohol as a decision input. Twenty canonical documents, 571 tests, an eleven-convention governance model, and a five-stage data pipeline have all been built on top of that assumption without ever testing it against a real person. If it's true, this task is a week's detour before the "real" roadmap resumes exactly where the original plan had it. If it's false, it's the cheapest possible way to find that out — before the pipeline is fixed, before the catalog is scaled to 500 SKUs, before a single Play Store review cycle is spent on it.
