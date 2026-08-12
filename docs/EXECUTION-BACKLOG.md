# ValueBrew — Master Product Backlog

*Execution backlog derived from the canonical strategy set (Project Brain, Master Roadmap, Roadmap Adversarial Review, Company Design, Unfair Advantage, Investment Committee Review, Founder Execution Blueprint, Founder Operating System). Nothing here introduces a feature unsupported by those documents — this only decomposes the already-approved critical path into Epics → Features → Tasks.*

---

## Part 1 — Epics

### E1. Legal & Regulatory Clearance
- **Purpose:** Confirm ValueBrew, as designed, can legally exist and be published under Karnataka/India alcohol-advertising and promotion rules.
- **Why it matters:** Founder Execution Blueprint Phase 0; Founder OS Prioritization Rule 1 — legal clearance gates all new user-facing surface area.
- **Success criteria:** Written go/no-go/with-conditions answer, with named sources, plus a concrete age-gating requirement.
- **Dependencies:** None — true first step.
- **Priority:** P0
- **Effort:** S

### E2. Minimal Real Catalog Construction
- **Purpose:** Produce a real, ABV-complete Karnataka beer catalog of ≥100 SKUs.
- **Why it matters:** Project Brain §7/§11 — no real, ABV-complete catalog reaches the app today; this is the structural bottleneck identified across every strategy document.
- **Success criteria:** ≥100 SKUs in `catalog.json` schema, each with non-null ABV, style, size, container_type, and a dated real price.
- **Dependencies:** Data collection can start immediately; shipping requires E1 resolved.
- **Priority:** P0
- **Effort:** L

### E3. Real-Data App Integration & QA
- **Purpose:** Prove the existing 4-screen app works end-to-end against real, messy data.
- **Why it matters:** Founder Execution Blueprint Phase 2 — the placeholder catalog has never been tested against real-data edge cases.
- **Success criteria:** All 4 screens complete a full flow with zero crashes on ≥2 physical devices; full test suite passes.
- **Dependencies:** E2.
- **Priority:** P0
- **Effort:** M

### E4. Compliance & Store Readiness
- **Purpose:** Clear every store/regulatory readiness item.
- **Why it matters:** Required for legitimate Play Store submission; several items directly trace to E1's findings.
- **Success criteria:** Age-gate implemented, privacy policy published, content rating completed, store listing assets ready, support channel live.
- **Dependencies:** E1 (requirements), E3 (real screenshots).
- **Priority:** P0/P1 (age-gate + privacy policy are P0; listing polish is P1)
- **Effort:** M

### E5. Analytics & Crash Reporting Infrastructure
- **Purpose:** Ensure launch generates learnable signal.
- **Why it matters:** Founder OS Part 6 — success is measured by real behavior, which requires instrumentation to observe.
- **Success criteria:** Crash reporting wired and confirmed; key usage events logged.
- **Dependencies:** None — fully parallel.
- **Priority:** P1
- **Effort:** S

### E6. Closed Field Validation
- **Purpose:** Confirm real people can use the real app to make a real decision, with behavioral evidence.
- **Why it matters:** Roadmap Adversarial Review's core finding — self-reported satisfaction alone is insufficient evidence; Founder Execution Blueprint Phase 4.
- **Success criteria:** ≥15 real Bangalore beer buyers complete the flow; majority show confirmed behavior change, not just stated approval.
- **Dependencies:** E2, E3, core of E4.
- **Priority:** P0
- **Effort:** M

### E7. Data Asset Protection (KSBCL Pipeline Defect Fix)
- **Purpose:** Fix the `true_prior_map` defect in `canonical_resolve.py` before any future real pipeline rerun.
- **Why it matters:** Unfair Advantage's compounding-asset analysis + Founder OS Failure Framework #4 — this defect risks permanently corrupting an irreplaceable asset (the price ledger / identity map), independent of the app launch.
- **Success criteria:** Fix implemented, regression-tested against the diagnosed scenario, independently reviewed.
- **Dependencies:** None — fully parallel to the launch critical path.
- **Priority:** P2 (not launch-blocking; the launch catalog bypasses the pipeline entirely)
- **Effort:** M

### E8. Launch Execution
- **Purpose:** Submit and ship.
- **Success criteria:** App live on the Play Store.
- **Dependencies:** E1, E2, E3, E4, E6.
- **Priority:** P0
- **Effort:** S

---

## Part 2 — Features

### E1 Features
- **F1.1 — Regulatory Research Pass.** Research applicable Karnataka/India alcohol-advertising law as it applies to price-comparison/recommendation apps. *User value:* none directly — protects the company's right to exist. *Engineering value:* defines UI/copy constraints. *Dependencies:* none. *Acceptance:* documented findings with citations and a preliminary risk assessment.
- **F1.2 — Legal Opinion / Escalation.** Engage counsel if F1.1 surfaces ambiguity. *Dependencies:* F1.1. *Acceptance:* written go/no-go/with-conditions answer.
- **F1.3 — Age-Gating Requirement Definition.** Determine the specific age-verification standard required. *Dependencies:* F1.1. *Acceptance:* a concrete, implementable spec.

### E2 Features
- **F2.1 — SKU Prioritization List.** Build a ranked shortlist of ≥150 candidate SKUs from KSBCL-confirmed brands + Madhuloka's top listings. *User value:* ensures launch coverage matches what testers will search for. *Dependencies:* none. *Acceptance:* ranked list with source noted per SKU.
- **F2.2 — Physical Data Collection (ABV/Style).** Shelf-walk and photograph labels for the shortlist. *User value:* enables the core value-comparison feature to compute at all. *Dependencies:* F2.1. *Acceptance:* ≥100 SKUs with confirmed ABV + style.
- **F2.3 — Price Collection.** Record real, dated retail prices. *User value:* enables Price Verification. *Dependencies:* F2.1. *Acceptance:* ≥100 SKUs with a dated real price.
- **F2.4 — Catalog Assembly.** Hand-enter collected data into `catalog.json`'s existing schema. *Dependencies:* F2.2, F2.3. *Acceptance:* file validates and loads with ≥100 complete SKUs.

### E3 Features
- **F3.1 — Catalog Swap-In.** Replace the placeholder with the real catalog. *Dependencies:* E2. *Acceptance:* app builds and loads without parse errors.
- **F3.2 — Real-Data Edge Case Testing.** Manually walk all 4 screens against real data. *Dependencies:* F3.1. *Acceptance:* full flow completes without crash; new edge cases logged.
- **F3.3 — New Automated Tests.** Cover any edge case found in F3.2. *Dependencies:* F3.2. *Acceptance:* new tests pass; full suite green.
- **F3.4 — Physical Device Verification.** Confirm on ≥2 real Android devices. *Dependencies:* F3.1. *Acceptance:* verified on 2 distinct devices.

### E4 Features
- **F4.1 — Age-Gating Implementation.** Build the mechanism per F1.3's spec. *Dependencies:* F1.3. *Acceptance:* blocks access on decline.
- **F4.2 — Privacy Policy.** Write and publish. *Dependencies:* none. *Acceptance:* live at a stable URL, linked in-app.
- **F4.3 — Play Store Content Rating.** Complete Google's questionnaire. *Dependencies:* F1.1. *Acceptance:* rating certificate obtained.
- **F4.4 — Store Listing Assets.** Icon, real-catalog screenshots, Lexicon-consistent description. *Dependencies:* E3. *Acceptance:* full asset set ready.
- **F4.5 — Support Channel.** Monitored contact for price-error reports. *Dependencies:* none. *Acceptance:* address live and linked.

### E5 Features
- **F5.1 — Crash Reporting Integration.** Wire a lightweight SDK. *Dependencies:* none. *Acceptance:* a test crash is captured and visible.
- **F5.2 — Minimal Usage Analytics.** Instrument the app's existing `AnalyticsSink` seam for key events. *Dependencies:* F5.1 (shared infra, or independent). *Acceptance:* events logged and visible for a real session.

### E6 Features
- **F6.1 — Recruit Test Participants.** 15–20 real, repeat Bangalore beer buyers (per Company Design's "ideal first customer" — not impulse buyers). *Dependencies:* none. *Acceptance:* participants confirmed.
- **F6.2 — Run Validation Sessions.** Real or simulated purchase decisions using the real-catalog app. *Dependencies:* E3, F6.1. *Acceptance:* all sessions complete, data logged.
- **F6.3 — Behavioral Follow-Up.** Confirm whether recommendations were actually acted on. *Dependencies:* F6.2. *Acceptance:* follow-up data collected within a defined window.
- **F6.4 — Synthesize Validation Results.** Compile into a go/no-go call. *Dependencies:* F6.3. *Acceptance:* written summary with a majority-behavior-change determination.

### E7 Features
- **F7.1 — Root-Cause Fix.** Correct `true_prior_map` construction. *Dependencies:* none. *Acceptance:* implemented and unit-tested against the diagnosed scenario.
- **F7.2 — Regression Test for the Incident.** Reproduce the corruption scenario, confirm it's fixed. *Dependencies:* F7.1. *Acceptance:* test fails pre-fix, passes post-fix.
- **F7.3 — Independent Review Before Next Real Rerun.** Per Founder OS's adversarial-review discipline. *Dependencies:* F7.1, F7.2. *Acceptance:* review documented before any future real pipeline run.

### E8 Features
- **F8.1 — Final Checklist Verification.** Walk Part 8's checklist item by item. *Dependencies:* E1–E6. *Acceptance:* every item confirmed true.
- **F8.2 — Play Console Submission.** Build and submit. *Dependencies:* F8.1. *Acceptance:* submitted.
- **F8.3 — Review Response.** Handle any rejection feedback. *Dependencies:* F8.2. *Acceptance:* approved and live.

---

## Part 3 — Tasks

### E1
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Research Karnataka Excise Act / Rules for advertising restrictions | Legal/Founder | — | Documented findings with citations |
| Research ASCI / advertising-standards guidance as applied to app store listings | Legal/Founder | — | Documented findings |
| Confirm informational (never transactional) framing avoids e-commerce/direct-sale prohibitions | Legal/Founder | — | Written confirmation |
| Compile risk-assessment summary, self-review via Founder OS decision framework | Founder | above | Summary document exists |
| Engage counsel/paid consult if ambiguity found | Founder/Legal | F1.1 | Consult booked/completed |
| Obtain written legal opinion | Legal | above | Opinion received |
| Draft age-gating mechanism spec | Founder/Legal | F1.1 | Written spec |
| Cross-check spec against Google Play's alcohol-app policy | Product | above | Confirmed compatible |

### E2
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Extract KSBCL-confirmed SKU list from `pricing_data/beer_master.csv` | Founder | — | List extracted |
| Cross-reference Madhuloka's top listings to reach ≥150 SKUs | Founder/Research | above | Combined list |
| Rank list by likely tester familiarity | Product | above | Ranked list |
| Identify 3–5 Bangalore retail locations to visit | Founder | ranked list | Visit plan |
| Conduct shelf walk(s), photograph labels | Founder/Research | visit plan | Photo set covering ≥100 SKUs |
| Transcribe ABV/style from photos into a working spreadsheet | Founder | photos | Spreadsheet with ≥100 rows |
| Record shelf-observed prices during the same walk | Founder | shelf walk | Prices logged |
| Spot-check a sample against Madhuloka's listed prices | Founder | prices logged | Discrepancies noted |
| Confirm `catalog.json`'s existing schema | Engineering | — | Schema documented |
| Convert spreadsheet into `catalog.json` | Engineering | spreadsheet, schema | Script or documented process exists |
| Generate real `catalog.json`, validate it loads | Engineering | above | Loads in debug build without error |

### E3
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Swap catalog asset into build | Engineering | E2 | Build compiles with real catalog |
| Walk Home→Recommendation with 5 varied inputs | Engineering/Founder | above | Completes each time, issues logged |
| Walk Beer Detail for 10 random real SKUs | Engineering/Founder | above | No crashes, correct display |
| Walk Price Verification for 10 SKUs, varied charged prices | Engineering/Founder | above | Verdicts render correctly |
| Write regression tests for any bug found | Engineering | above | Tests pass |
| Install and run on Device A | Engineering | build | Verified |
| Install and run on Device B (different manufacturer/OS) | Engineering | build | Verified |

### E4
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Implement age-confirmation screen/dialog | Engineering | F1.3 | Implemented, testable |
| Test decline blocks further access | Engineering | above | Verified |
| Draft privacy policy text (incl. crash/analytics disclosure) | Founder/Legal | E5 scope known | Draft complete |
| Publish policy to a stable URL | Engineering | draft | Live URL |
| Complete Play Console content rating questionnaire | Founder | F1.1 | Rating certificate received |
| Capture screenshots from real-catalog build on a real device | Founder/Design | E3 | Screenshot set complete |
| Write store description copy, checked against Lexicon | Product | — | Copy finalized |
| Prepare/confirm app icon asset | Design | — | Meets Play Store spec |
| Create monitored support email | Founder | — | Address active |
| Add support contact link in-app and in listing | Engineering | above | Link functional |

### E5
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Add crash-reporting dependency, initialize in `main.dart` | Engineering | — | SDK integrated |
| Trigger and confirm a test crash appears in dashboard | Engineering | above | Confirmed |
| Implement concrete `AnalyticsSink` for key events | Engineering | — | Events fire correctly |
| Verify events visible from a manual test session | Engineering | above | Confirmed |

### E6
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Define recruitment criteria (repeat buyer, Bangalore, price-aware) | Founder | — | Criteria documented |
| Recruit 15–20 participants | Founder | above | Confirmed |
| Prepare session script/consent process | Product | — | Script ready |
| Conduct sessions (sideload/closed track) | Founder | E3, participants | All sessions run |
| Schedule and conduct follow-up check-ins | Founder | sessions | Follow-ups logged |
| Compile results, compute % showing behavior change | Founder/Product | above | Summary written |
| Make go/no-go call per Founder OS decision framework | Founder | above | Decision recorded |

### E7
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Re-read `canonical_resolve.py` ~lines 104–122, confirm root cause | Engineering | — | Confirmed |
| Implement corrected `true_prior_map` construction | Engineering | above | Code change made |
| Write test reproducing corruption against pre-fix code | Engineering | above | Test fails on old code |
| Confirm test passes against fixed code | Engineering | above | Passes |
| Independent (non-self) review of the fix | Engineering (2nd reviewer) | above | Review documented |

### E8
| Task | Owner | Dependencies | DoD |
|---|---|---|---|
| Walk full launch checklist (Part 8) item by item | Founder | E1–E6 | All items checked |
| Build release APK/AAB | Engineering | above | Artifact ready |
| Upload to Play Console, complete listing, submit | Founder | above | Submitted |
| Monitor review status | Founder | above | Status tracked |
| Address rejection feedback, resubmit if needed | Engineering/Founder | above | Resolved |

---

## Part 4 — Critical Path

**Blocking (sequential):** E1 → E2 → E3 → E6 → E8, with E4's core items (age-gate implementation, privacy policy) starting once E1 defines requirements and completing before E8.

**Parallelizable without slowing the critical path:** E5 (analytics/crash reporting) — no dependency on anything else. E7 (pipeline defect fix) — fully independent; the launch catalog bypasses the pipeline entirely. F4.2 (privacy policy drafting) — can start day one. F6.1 (recruiting validation participants) — can start immediately, doesn't need the app to exist yet.

**Optional relative to this launch:** none of E1–E6, E8 are optional — every one is on the checklist. E7 is the only epic that is genuinely optional *for this launch specifically*, though not optional in the longer term per Founder OS's asset-protection principle.

---

## Part 5 — Prioritization

Assigned at Feature level; tasks inherit their Feature's priority unless noted.

| Priority | Meaning | Features |
|---|---|---|
| **P0 — Blocks launch** | Nothing ships without this | F1.1, F1.2, F1.3, F2.1–F2.4, F3.1–F3.4, F4.1, F4.2, F6.1–F6.4, F8.1–F8.3 |
| **P1 — Required before launch** | On the launch checklist, not itself a hard technical blocker for earlier phases | F4.3, F4.4, F4.5, F5.1, F5.2 |
| **P2 — Improves launch** | Real value, doesn't gate submission | E7 (F7.1–F7.3) |
| **P3 — Post-launch** | Explicitly deferred per Founder Execution Blueprint Part 5 | Pipeline scaling past ~150 SKUs, Search/Browse & Comparison screens, GTIN/GS1 work, any B2B exploration, formal Accessibility/Telemetry standards, monetization design, multi-city expansion, native-app visual polish, legacy code cleanup in `lib/` |

**Why:** P0 items are exactly the ones on Founder Execution Blueprint's critical path (Part 2) and Launch Readiness Checklist (Part 7) that gate submission. P1 items are checklist-required but don't block earlier phases from proceeding — content rating, listing assets, and instrumentation can trail slightly behind engineering work without stalling it. P2 protects a real, compounding asset but was explicitly scoped out of this launch's dependency chain in the Founder Execution Blueprint. P3 is the "Not Now" list, carried over verbatim from that same document — nothing here is reprioritized, only reorganized into the P-scale.

---

## Part 6 — Sprint Planning

**Sprint 1 — Clear the Gate.** Objective: resolve legal clearance and stand up parallel infrastructure. Work: E1 (all features), start F2.1, start F4.2 (privacy policy draft), start E5 (crash reporting + analytics), start F6.1 (recruitment criteria + outreach begins).

**Sprint 2 — Collect the Data.** Objective: get real ABV, style, and price data for the launch catalog. Work: F2.2, F2.3, continue F6.1 recruitment, F4.1 age-gate implementation begins once F1.3 is done.

**Sprint 3 — Wire It In.** Objective: assemble the real catalog and prove the app works against it. Work: F2.4, all of E3, finish F4.1, F4.2, F4.3.

**Sprint 4 — Validate.** Objective: get behavioral evidence from real people. Work: all of E6, finish F4.4 (using screenshots from E3), finish F4.5.

**Sprint 5 — Launch.** Objective: submit and ship. Work: all of E8.

**Threaded throughout, no dedicated sprint:** E7 (pipeline defect fix) — picked up whenever engineering has slack between sprints; not sequenced against any of the above.

Each sprint has exactly one objective; no sprint mixes unrelated epics.

---

## Part 7 — Risk Register

| Epic | Technical Risk | Product Risk | Legal Risk | Schedule Risk | Mitigation |
|---|---|---|---|---|---|
| **E1** | — | — | Real regulatory constraint forces a redesign of core Lexicon language after the fact | Legal review takes longer than a solo founder's sprint | Run this first, alone, blocking, before any other work starts — exactly as scoped |
| **E2** | Hand-entered data has transcription errors | 100–150 SKUs may not cover what a tester actually asks for | — | Manual collection takes longer than the 1–2 week estimate | Spot-check a sample against a second source; prioritize list by real popularity, not convenience |
| **E3** | Real data breaks assumptions the placeholder never tested | — | — | Bug-fixing after discovery could extend this phase | Budget slack time in the estimate; treat this phase as expected-to-find-bugs, not a formality |
| **E4** | Age-gate implementation bugs allow bypass | — | Content rating answers must match legal findings exactly | Store review scrutiny for alcohol content | Cross-check every compliance artifact against E1's written findings before submission |
| **E5** | SDK integration conflicts with existing dependencies | — | Crash/analytics data collection must be disclosed in the privacy policy | — | Coordinate F5.* completion with F4.2's privacy policy draft |
| **E6** | — | Recruited panel is subject to the Hawthorne effect (participants act nicer than real users) | — | Follow-up window (1–2 weeks) extends this phase | Use behavioral follow-up, not just session-day sentiment, exactly as scoped in F6.3 |
| **E7** | A rushed fix introduces a new correctness bug in the identity-resolution logic | — | — | Low — fully parallel, no launch pressure | Independent review before the fix is trusted (F7.3), never self-approved |
| **E8** | Release build issues discovered only at submission time | — | — | Play Store review turnaround is outside founder control | Complete F8.1's full checklist walk-through before submitting, not after |

---

## Part 8 — Launch Checklist

*Directly traceable to the Founder Execution Blueprint's Part 7, reorganized here by the Epic that owns it.*

- [ ] **(E1)** A written legal opinion, or documented founder research citing named regulatory sources, confirms the app as designed complies with applicable Karnataka/India alcohol-advertising rules.
- [ ] **(E4/F4.1)** Age-gating is implemented and blocks any user who does not confirm legal drinking age.
- [ ] **(E4/F4.2)** A privacy policy is published at a stable, public URL and linked from the Play Store listing.
- [ ] **(E4/F4.3)** The Play Store content-rating questionnaire is completed and the app carries an appropriate alcohol-content rating.
- [ ] **(E2)** `catalog.json` contains at least 100 SKUs, each with a non-null ABV, style, size, container type, and a dated real Karnataka price observation.
- [ ] **(E3)** All 4 shipped screens (Home, Recommendation, Beer Detail, Price Verification) complete a full user flow against the real catalog with zero crashes, verified on at least 2 physical Android devices.
- [ ] **(E3)** The existing automated test suite passes with zero failures against the real-catalog build.
- [ ] **(E6)** At least 15 real individuals have completed a full recommendation → detail → verification flow, and a majority show a specific, confirmed instance of the app changing a real purchase decision.
- [ ] **(E5)** Basic crash reporting/analytics is wired and confirmed to receive events from a real test session.
- [ ] **(E4/F4.4)** Store listing assets (icon, screenshots from the real-catalog build, description) are complete and use only Lexicon-consistent language — no unqualified "Best," no "Score"/"Rating."
- [ ] **(E4/F4.5)** A monitored support/contact channel exists for user-reported price errors.
- [ ] **(E8)** The app has been submitted to Play Store review and either passed or has an open, actively-tracked review ticket.
