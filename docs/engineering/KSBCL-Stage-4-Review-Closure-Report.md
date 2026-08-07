# KSBCL Stage 4 — Review Closure Report

### A historical record of the review that produced Stage 4's frozen architecture, the two Identity Decisions, and Repository Governance. This document does not re-open, re-analyze, or re-litigate anything — it records what happened and why the review concluded.

---

## 1. Review objective

To determine whether Stage 4 (Canonical Identity Resolution) — architecture drafted against Master, the frozen Stage 1–3 contracts, and an initially-undecided product-design phase — was internally consistent, correctly derived from what the repository had already decided, and free of any defect that would have prevented it from legitimately freezing under the same discipline Stage 2 and Stage 3 had already been held to. A secondary objective emerged partway through: whether the discipline used to review Stage 4 itself pointed to a governance model the repository had been following all along, and whether that model was complete enough to hand to whoever writes Stage 5.

---

## 2. Review methodology — progressive adversarial verification

No finding was accepted on first appearance. Each candidate defect, governance rule, or convention was subjected to deliberate, multi-angle attempts at disproof — checked against explicit repository text, checked for a higher-level constraint that already resolved it, checked for whether it was a re-derivation of a mistake already made and reverted, and checked for whether it merely restated something already established under a different name. A finding was retained only if it survived every attempt made to eliminate it. This discipline was applied recursively — including to the review's own emerging conclusions, to the governance model extracted from the review, and finally to the governance model's own wording. The review's depth is a consequence of applying this standard to itself, not of open-ended searching.

---

## 3. Major architecture corrections actually adopted

**The cross-supplier merge-mechanism scope was corrected.** The first draft removed master §4.4's price/`effective_date` review gate unconditionally when only the cross-supplier configuration was authorized by the recorded Identity Decision. The mechanism was restructured (§6, steps 2a/2b) so the gate is removed only where the Identity Decision actually applies, and restored unchanged — with a confirmed real citation (the Budweiser Magnum pair, item_codes `2170900611`/`2171700211`) — for the same-supplier configuration master originally built it for.

**Multi-candidate identity ambiguity handling was implemented.** Once the above correction made cross-supplier collisions possible for the first time, a further gap emerged: no rule existed for an item_code whose key matched more than one existing canonical product. This was resolved by Identity Decision 2 (below) and implemented directly into §6 (a new 2a sub-branch), §7 (a new review reason, `ambiguous_key_multiple_candidates`), §3.2, §8, and §13.

These are the only two changes actually written into Stage 4's frozen text during this review.

---

## 4. Product Decisions created

**Identity Decision 1 — `supplier_code` excluded from canonical identity.** Settled after an extended product-design phase (Product Discussion → Settlement → Charter → User Mental Model) established that the question hinged on an unconfirmed factual premise and a genuine philosophy-of-catalog question no amount of engineering analysis could close.

**Identity Decision 2 — multi-candidate ambiguity resolved by deferral (Option F), not automatic resolution.** Settled after repeated attempts to derive the answer from the frozen repository alone explicitly failed; confirmed as a genuine risk-tolerance choice, not a fact in dispute, and evaluated directly against ValueBrew's stated principles before being recorded.

Both decisions are recorded in `KSBCL-Stage-4-Identity-Decision.md` and are cited explicitly, by name, everywhere Stage 4's architecture departs from master's original mechanism.

---

## 5. Findings investigated and ultimately rejected

- A citation mismatch between Stage 3 §9 (claiming a three-way join) and Stage 4's actual two-file input scope — collapsed; no functional divergence, Stage 4 needs nothing from the third file.
- A miscitation of master §8.3 in Stage 4 §10 — documentation-only, no behavioral consequence.
- A proposed missing "key registry" persistent entity to explain the multi-candidate tie-break — collapsed on its own follow-up review; the underlying fact is fully derivable on demand, no storage was ever missing.
- A proposed required audit-trail entity (who/when/prior-value) for a human-confirmed repoint — downgraded to an implementation convenience once shown not to be explicitly required or logically unavoidable.
- `canonical_resolution_review.csv`'s per-run scope, initially treated as a data-loss risk — collapsed once shown the underlying collision fact is permanently re-derivable from already-persistent data.
- A missing update rule for `first_seen_run_month`/`last_seen_run_month` under out-of-order reruns — raised by direct analogy to a bug Stage 2 had once made and fixed, but collapsed once that analogy was disallowed as evidence: Stage 4's own text has exactly one literal reading (`first_seen_run_month` immutable after creation, `last_seen_run_month` a simple overwrite), with no ambiguity within its own words.
- Stage 5's future canonical-level rollup depending on `item_status` alone — resolved as Stage 5's own future hardening responsibility, structurally identical to how Stage 2, 3, and 4 each hardened their own terse master sketch, not a Stage 4 or repository-level defect (after one inconsistent detour where it was briefly re-escalated before being corrected back to this conclusion).
- Two candidate governance conventions proposed during the search for gaps in Repository Governance — "no finding should be accepted without deliberate multi-angle disproof" and "every stage document explicitly declares what it does not own" — both investigated at length and rejected: the first governs review methodology, not the repository itself; the second collapses into master's own §2 pipeline diagram combined with the existing no-silent-override convention.
- Several further candidate conventions (row-level/structural-failure isolation, rolling-baseline metric tracking, reserved empty schema seams, decision-recording format, the run-dated archive mechanism) — each investigated and rejected, either for collapsing into an already-explicit master statement or for falling short of independent replication across multiple stages.
- A proposed narrowing of Convention #2 to distinguish "master merely naming something" from "master actively relying on it elsewhere" — investigated in detail and ultimately rejected: the distinction was drawn by Stage 3, once, to justify one decision, and was never independently generalized elsewhere in the repository. Encoding it as a repository-wide rule would have overstated what the repository itself established.

---

## 6. Governance extracted from repeated repository practice

Eleven conventions, none stated anywhere as a single explicit policy, all demonstrated independently and repeatedly across Stage 2, Stage 3, and Stage 4: master-sketch hardening; no silent override of explicit prior text; the architecture-vs-product decision boundary; confirm-then-extend; the asymmetric-risk default; never inventing a fact; mandatory audit artifacts; determinism (not fabricated accuracy) as the correctness bar; freeze readiness without full resolution; disclosed review history; and real-data grounding. These are recorded in `KSBCL-Repository-Governance.md`. The document itself was subjected to the same adversarial standard applied to the architecture — checked for completeness (no missing convention survived a systematic search) and for calibration (each convention's wording checked against whether it claimed more than the evidence supports). One calibration defect was confirmed and remains uncorrected as of this report — see §8.

---

## 7. Final repository status

- **Master, Stage 1, Stage 2, Stage 3** — unchanged throughout this review. No defect was found that met the bar for reopening any of them.
- **Stage 4 Architecture** — revised twice, as recorded in its own status banner: once to correct the merge-mechanism scope (§3), and once to implement Identity Decision 2 (§4). Both revisions are cited to their authorizing decision.
- **Identity Decision document** — extended once, from a single decision to two, both recorded with rationale, accepted trade-off, and status.
- **Repository Governance** — published once, containing eleven conventions extracted from repeated demonstration across the repository.

---

## 8. Remaining known issue(s)

Two issues were confirmed during this review and remain unresolved in the actual, current text as of this report — neither was fixed, only diagnosed and agreed:

1. **Stage 4's `item_status` computation.** The frozen text still computes `item_status` from `normalized_rows.csv` presence rather than `structured_rows.csv` presence, meaning an item still genuinely published by KSBCL but excluded from a given run's beer classification would be incorrectly marked `DELISTED`. This was confirmed, independently re-verified, and never disputed across multiple rounds of adversarial testing — it is a genuine defect against master §7.5's explicit purpose statement, not a matter of interpretation. It was never written into Stage 4's document.

2. **Repository Governance's Convention #6 citation.** The convention cites `item_status` as a positive demonstration of "never invent a fact," when it is in fact the one confirmed exception. The convention's stated principle is correct and independently supported by its other citations (Stage 1, Stage 3); only this one citation is factually wrong and needs removing or correcting. This was also never applied to the document.

Both issues have an agreed, precise diagnosis and an agreed minimal correction; neither required further analysis to resolve, only an edit that was not made during this review.

---

## 9. Why this review is considered complete

Every substantive mechanism in Stage 4 was tested to the point where further adversarial passes stopped finding anything new — the multi-candidate tie-break, the out-of-order rerun question, and the review-queue persistence question were each raised as plausible defects and each collapsed under direct testing against the repository's own text, not merely reconsidered and dropped. The two genuine decisions the architecture actually needed were identified, correctly distinguished from architecture-resolvable questions, and recorded. The governance model underlying all of this was itself searched for gaps and checked for overclaim, with each successive round finding fewer and smaller issues until a full, dedicated search for a missing convention and a full, dedicated calibration pass over all eleven existing conventions each returned only one confirmed, narrow finding apiece — one of which was itself later shown, under the same standard, to be an over-generalization that should not be adopted. That diminishing return, reproduced consistently across independent search strategies, is the review's actual stopping condition. What remains is not unexamined — it is two precisely diagnosed, agreed corrections awaiting application, not open questions awaiting further review.
