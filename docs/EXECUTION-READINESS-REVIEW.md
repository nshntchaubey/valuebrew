# ValueBrew — Execution Readiness Review

*Auditing `docs/EXECUTION-BACKLOG.md` for operational stall points only. Strategy is frozen and not touched here — this is a Staff EM/PM/COO review of whether Sprint 1 can actually start tomorrow and run cleanly to launch.*

---

## Part 1 — Hidden Dependencies

| Missing | Why it blocks | First discovered | Severity |
|---|---|---|---|
| **Google Play Developer account creation and identity verification.** No task anywhere creates or verifies this account. Google's verification for new developer accounts routinely takes days and has gotten stricter, not looser. | F8.2 (submission) cannot happen without an active, verified account. | Sprint 5 — the worst possible moment. | **High** |
| **Play Store's own alcohol-content policy**, distinct from Indian law. E1 researches Indian regulation; nothing tasks researching Google's own content policy for alcohol-related apps, which could impose separate declarations or restrictions independent of legal clearance. | Could reject the app at F8.3 even after Indian law is fully cleared. | Sprint 5, at submission. | **High** |
| **Google Play's closed-testing requirement for new developer accounts.** Google frequently requires a minimum closed-testing period with a minimum tester count before allowing production release from a new account — this may mean E6 (field validation) and F8.2 (submission) need to route through the *same* Play Console mechanism, not be sequential separate steps. | Changes the actual shape of E6→E8, not just the timing. | Sprint 5, when actually attempting to submit. | **High** |
| **Physical device access.** E3/F3.4 requires two physical Android devices of different manufacturer/OS. Nothing confirms the founder owns or can borrow a second one. | Blocks F3.4 completion. | Sprint 3. | Low-Medium |
| **Legal counsel identity and availability.** E1/F1.2 assumes counsel can be engaged and turn around an opinion inside Sprint 1. Nobody is named, and no fallback exists if they're slow or unreachable. | The literal first task on the critical path has no bounded worst-case duration. | Sprint 1, immediately. | **High** |
| **App signing key generation and backup.** No task exists for this at all. | Doesn't block *this* release, but mismanaging it silently forecloses future updates. | Not until the first post-launch update is needed — invisible until then. | Medium-High (delayed-onset) |
| **Data source continuity for E2.** Project Brain's own market research already found roughly half of Karnataka retail data sources broken or stale. Nothing in the backlog names a fallback if Madhuloka or a planned shelf-walk location is unavailable mid-collection. | Stalls F2.2/F2.3 with no documented Plan B. | Sprint 2, during collection. | Medium |
| **Karnataka's legal drinking age isn't explicitly sourced anywhere** before F4.1 hard-codes an age-gate threshold. | A wrong number baked into the gate is a compliance defect, not a UX bug. | Sprint 1/3, when the age-gate spec is written. | Low |
| **Privacy policy hosting.** F4.2 says "publish at a stable URL" without naming where — no domain or hosting decision exists yet. | Small, but currently undefined. | Sprint 1/3. | Low |

---

## Part 2 — False Assumptions

| Assumption | Classification | Cost if false |
|---|---|---|
| Legal clearance resolves within Sprint 1 (~1 week) | **Hypothesis/Opinion** — no evidence counsel is identified or fast; the Brain's own research already showed a *narrower* legal question was hard to source cleanly | The entire 5-sprint plan slips from day one, with no stated trigger for when to escalate |
| 100–150 SKUs are collectible by one person in 1–2 weeks | **Inference** — extrapolated from a founder-execution-plan estimate that was actually about scaling to 500–600 SKUs over months, never independently verified at this smaller scope | Sprint 2 overruns, cascades through everything after it |
| Confirmed data sources (Madhuloka, etc.) stay accessible through the collection window | **Hypothesis** — directly contradicted by the Brain's own finding that roughly half of evaluated sources were already broken at time of research | Forces slower, physical-only collection with no time buffer built in |
| 15–20 recruitable users can be scheduled within Sprint 4's window | **Hypothesis/Opinion** — no evidence of an existing network the founder can tap on short notice | Sprint 4 slips, or the sample shrinks below what's meaningful |
| The existing 571-test app will behave correctly against real data with only minor fixes | **Inference** — based on rigor demonstrated against *specified* test cases, not against unpredictable real-world input, which has never been tried | E3's M-effort estimate could be significantly wrong |
| A new Play Developer account can publish immediately once created | **Opinion**, contradicted by common current Google Play policy (see Part 1) | Sprint 5 slips at the least recoverable point in the plan |
| The founder has uninterrupted availability across the full 5–9 week span | **Opinion**, never stated or tested anywhere in the canonical set | General schedule slippage, no single failure point |

---

## Part 3 — Founder Bottlenecks (Sequencing Only, No Hiring)

The founder is currently scheduled to be the legal researcher, the field data collector, the engineer, and the user researcher — often in the *same week*. That's four fundamentally different work-modes (deep reading, physical travel, focused coding, live human interaction), and Sprint 1 as written already asks for all four at once (E1 plus starting F2.1, F4.2, E5, and F6.1).

**Recommended sequencing corrections (no headcount, no roadmap change):**
- **Batch by work-mode, not by epic.** Don't run legal research and physical shelf-walks in the same week. Dedicate Sprint 1 entirely to legal — it's the literal gate, and it deserves uninterrupted deep-focus time, not a week shared with four other epics.
- **Front-load every async, founder-idle dependency on day one.** Kick off Google Play Developer account verification and legal-counsel engagement on day 1 of Sprint 1, in parallel with active founder research — their waiting time should overlap with active work, not follow it sequentially.
- **Batch travel.** Consolidate E2's shelf walks into as few contiguous trips as possible rather than spreading them thin across the collection window.
- **Separate "heads-down" and "in-person" sprints where possible.** Legal reading and engineering both suffer badly from interruption; don't schedule them against each other even where the dependency graph technically allows overlap.
- **Time-box documentation explicitly.** Given the demonstrated pattern in this project of extensive written output, set a hard, small cap on documentation time per sprint — this is the same failure mode the Founder Operating System already names (engineering/documentation completeness substituting for execution), now applied specifically to process documentation during execution.

---

## Part 4 — Sprint Audit

**Sprint 1 — Clear the Gate.** Objective clear. Workload is **not realistic**: five different epics (E1, F2.1, F4.2, E5, F6.1) are touched in one week, exactly the context-switching risk Part 3 flags. Hidden blocker: no bounded worst-case for legal turnaround, no escalation trigger. Missing deliverable: Play Developer account creation/verification isn't started here despite being a pure async task that should begin immediately. Premature work: starting F6.1 recruitment before legal clears risks having to re-approach participants under changed framing if legal comes back "with conditions." **Fix:** Sprint 1 = E1 only, plus kick off the Play Developer account application (async, doesn't compete for attention).

**Sprint 2 — Collect the Data.** Objective clear. Workload risk: bundling physical data collection with "begin age-gate implementation" mixes travel/logistics work with engineering again. Hidden blocker: no fallback if a planned retail location is closed or a source goes down mid-sprint. Missing deliverable: no mid-sprint SKU-count checkpoint to catch a shortfall early. **Fix:** add a mid-sprint checkpoint; move engineering entirely to Sprint 3.

**Sprint 3 — Wire It In.** Objective clear, but if Sprint 2's engineering work is deferred here as recommended, this sprint now carries catalog assembly, all of E3, age-gate implementation, *and* content rating — genuinely heavy. Missing deliverable: no task for app signing key setup, which needs to exist before any real release build does. **Fix:** add signing-key setup explicitly; consider moving content rating to Sprint 5 since it's more naturally coupled to the actual Play Console submission flow than to engineering QA.

**Sprint 4 — Validate.** Objective clear. Workload risk: running 15–20 sessions plus behavioral follow-up in the same week as finishing store-listing assets and the support channel dilutes attention on the sprint that matters most. Hidden blocker: behavioral follow-up (F6.3) inherently requires *calendar* time after each session — waiting for someone's next real purchase doesn't compress into "1 week of active work," it spans real time that may bleed past the sprint boundary. Missing deliverable: **no numeric definition of "majority" is pinned down anywhere** — this is decided after seeing results, not before, which quietly reintroduces the exact self-report-adjacent ambiguity the Roadmap Adversarial Review already warned against. **Fix:** pin the exact go/no-go threshold (e.g., "≥8 of 15 confirmed") *before* Sprint 4 starts; move F4.4/F4.5 out of this sprint.

**Sprint 5 — Launch.** Objective clear, but the S-effort estimate (2–3 days) is very likely wrong given Part 1's findings — developer account verification lag, a possible mandatory closed-testing period, and Google's own alcohol-content policy review could each independently extend this sprint by days to weeks. **Fix:** treat store-mechanics research as a Sprint 0/Sprint 1 task, not a Sprint 5 discovery, and budget this sprint a much wider window.

---

## Part 5 — Launch Risk (If the Backlog Runs Exactly as Written)

Ranked by probability:

1. **Play Store's own submission mechanics — developer account verification lag, a mandatory closed-testing period, or Google's alcohol-content policy — derail the timeline or the approval itself**, discovered only at the very end because nothing in the backlog tasks these store-specific requirements separately from Indian law.
2. **Legal clearance takes materially longer than Sprint 1's window**, because counsel availability was never verified and there's no defined escalation trigger — since this gates everything, a stall here has no contained blast radius.
3. **Catalog collection (E2) falls short of 100 SKUs** because a confirmed data source goes dark mid-collection, consistent with the Brain's own finding that half of researched sources were already broken, with no fallback documented.
4. **Field validation produces an ambiguous result** because the "majority shows behavior change" threshold was never numerically defined in advance — the founder ends up making a subjective launch call under schedule pressure, undermining the entire point of behavioral (not self-report) validation.
5. **Context-switching drag** from interleaving legal, data, engineering, and user-research work within the same weeks compounds a 20–30% slowdown across every sprint, with no single dramatic failure point — making it hard to even diagnose while it's happening.

---

## Part 6 — Execution Debt

**Acceptable debt (fine to defer):** no CI/CD pipeline yet — manual builds are fine at this scale. No dedicated catalog-entry tooling — a spreadsheet-to-JSON manual process is fine for a one-time 100–150 SKU launch catalog. Deferring the `true_prior_map` pipeline fix past this launch — genuinely safe since the launch catalog bypasses the pipeline entirely.

**Dangerous debt (will bite hard if postponed):**
- **App signing key management**, generated informally with no backup. Invisible today, and potentially catastrophic — mismanaging it can make future app updates impossible, forcing a brand-new listing that loses every review and install.
- **Treating Play Store's alcohol content policy as "probably covered by the legal work."** It isn't the same gate. Deferring explicit research on it risks discovering a conflict only at final submission, the single most expensive place to find it.
- **Leaving the E6 validation threshold undefined.** Cheap to fix now (one sentence, pinned in advance); expensive later — either the result gets rationalized after the fact, or the entire validation phase needs to be rerun once the ambiguity is noticed.
- **No documented fallback data source for E2.** A one-line contingency plan today; a lost sprint if a primary source disappears mid-collection with nothing else lined up.

---

## Part 7 — Kill Test

If the goal were to make this launch fail without touching the roadmap, the highest-leverage attacks are:

- **Let the legal step quietly become "founder feels satisfied" instead of a real, sourced opinion.** It's the step most vulnerable to being under-resourced by a time-pressured founder eager to get to "real" work, and if it's wrong, everything built afterward is retroactively worthless.
- **Never pin the E6 validation threshold.** Leave "majority" undefined, so any result can be rationalized as good enough — this quietly defeats the entire purpose of the behavioral-evidence discipline the whole strategy stack was built to enforce.
- **Never research Play Store's actual submission mechanics until the day of submission.** Guarantees a maximally expensive, maximally late surprise, right when everyone believes the work is essentially done.
- **Keep Sprint 1 bundling five unrelated work-modes.** The resulting context-switching drag compounds invisibly across every sprint — by the time the whole plan is visibly behind schedule, there's no single moment anyone can point to as "the" cause, which makes it hard to even diagnose in flight.
- **Let the app signing key get generated carelessly during a rushed final sprint, with no backup.** Doesn't kill this launch — plants a landmine that kills the ability to ever update the app again, which looks like success right up until it doesn't.

---

## Part 8 — Final Verdict

**C — Significant execution blockers remain.**

Not A: the backlog cannot start tomorrow with confidence — the Play Store submission mechanics gap alone (Part 1) could derail or double the length of the final sprint, and this was never tasked anywhere.

Not D: this isn't a case of incomplete planning in the conceptual sense — the epics, features, tasks, dependencies, and sprints are genuinely well-structured and traceable to the canonical strategy documents, exactly as intended.

**Not B either**, and this distinction matters: "a small number of operational corrections" undersells what was found. Three of the gaps identified here are not polish items — they're gaps that could each independently derail either the launch timeline (Play Store mechanics, legal turnaround with no bounded worst case) or the validity of the launch decision itself (the unpinned E6 threshold, which directly reintroduces the self-report ambiguity the Roadmap Adversarial Review already flagged as a serious methodological risk at the strategy level, now recurring unaddressed at the execution level). Per the Founder Operating System's own principle that legal clearance gates all new user-facing surface area, and the Project Brain's own market-research evidence that data-source continuity in this market cannot be assumed, the backlog as currently specified does not yet honor its own frozen strategy's standards.

**The fix is bounded and specific, not a redesign:** add the missing Play Store mechanics research as an explicit Sprint 0/Sprint 1 task, identify and confirm legal counsel before Sprint 1 begins, pin the E6 numeric threshold before Sprint 4, add the app-signing-key task, and de-interleave Sprint 1's five bundled epics. None of this touches the frozen strategy or the roadmap's sequence — it closes the operational gaps between what the backlog assumes and what's actually been verified.
