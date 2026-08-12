# ValueBrew Interaction Model 2.0

*How ValueBrew behaves while a person is using it — every interaction modeled as a sequence of decisions, not a screen layout. Built from the canonical State Machines (via the Screen Specifications' verbatim restatements), the Navigation Contract, Decision Engine 2.0, and The ValueBrew Experience. No UI, no components, no layout — only behavior.*

---

## Part 1 — Home

**Trigger:** app opened fresh, or a Recovery bounce-back from Search/Browse with zero matches.
**What ValueBrew knows:** nothing about this person; on a bounce-back, whatever Preference Summary existed before the failed attempt.
**What it still needs to know:** which of three paths (Recommendation, Price Verification, or — architecturally — Search/Browse) the expressed intent maps to.
**Question asked:** none by default — Home waits for an expressed intent rather than prompting for one.
**Why:** Home owns routing only; prompting with a menu would be Home performing classification work that belongs to whatever it routes toward.
**When it deliberately does not ask further:** once an intent is confidently classified, it routes immediately — no confirmation step ("did you mean...?") beyond the one clarifying question below.
**After each possible answer:**
- A budget/preference/no-anchor intent (including Planning-ahead, a flagged variant, not a separate path) → routes to Recommendation.
- An explicit verification intent → routes to Price Verification.
- A query or browse selection, including one naming two or more specific beers → would route to Search/Browse — **architecturally, today, there is nowhere for this to go.**
- An intent confirmed outside the product's four capabilities → Out-of-Scope, all four capabilities restated verbatim.
- A genuinely ambiguous intent → exactly one Clarifying Question, never a second.
**What causes branching:** the classification of the expressed intent alone — not asked, inferred from what's said (the classification *mechanism* itself is unspecified by canon; only the required *outcome* is).
**What causes convergence:** not applicable — Home never converges anything, it only disperses.
**What ends the interaction (for Home specifically):** it never does — Home never reaches Decision Complete, by design, always handing off.
**What survives:** any Preference Summary from before a bounce-back.
**What's deliberately forgotten:** everything, the moment the app is closed — nothing about a Home visit persists across sessions.

---

## Part 2 — Recommendation

**Trigger:** a hand-off from Home (with or without Planning Mode flagged).
**What ValueBrew knows at entry:** whatever was already said at Home, if anything — possibly nothing at all.
**What it still needs to know:** at minimum, a budget (Hard Constraint) — nothing else is required to eventually produce an honest answer.

**Question sequence (Gathering ↔ Evaluating, iterative):**
- Budget is asked first, since it eliminates the most candidates fastest.
- Style is asked next, **but only if it would actually change the outcome** — this is the exact canonical threshold, restated as an interaction rule: justified when 2+ candidates remain indistinguishable on everything known *and* the answer would separate them; forbidden when one candidate already dominates, when survivors differ only on a Soft input (a Trade-off/Tie is the honest response instead), when the question would touch an input already stated, or when no further Hard/Strong input remains (Low-Confidence Response applies instead).

**Why each question is necessary:** every question asked is one that could change which candidate wins — nothing is ever asked to "feel thorough."
**When it deliberately does not ask:** the moment the threshold above says a further question can't change the outcome — asking anyway would be a delay dressed as diligence, explicitly forbidden.

**After each possible outcome (Evaluating → one of five terminal shapes):**
- One candidate dominates → **Recommending**, with Explanation and Confidence attached in the same moment, never before or after.
- Multiple candidates tied on everything known → **Recommending (Tie Disclosure)** — a complete, Resolved-state answer, never a Recovery.
- Nothing satisfies the stated Hard Constraint → **Recovering (Conflicting Constraints)**, both tension-producing inputs named and kept visible.
- Too little is known to distinguish a large field honestly → **Recovering (Low-Confidence Response)** — either one more targeted question, or a clearly labeled provisional answer.
- **[Newly discovered gap]** a candidate SKU with incomplete Composition Knowledge (no confirmed ABV) enters the evaluation — no canonical rule defines whether it's silently excluded, included with a caveat, or something else. This interaction sequence currently has an undefined branch at exactly this point.

**What causes branching:** the threshold logic above, evaluated fresh every time new information arrives (a genuine re-entry into **Evaluating**, not a patch of the prior state).
**What causes convergence:** refining a previously-answered input replaces that one Constraint while preserving every other already-stated one, then re-runs Evaluating from current state — never a restart from zero.
**What ends the interaction:** an explicit, person-initiated action only — accepting a recommendation, a Trade-off side, or a Tie. Never inferred from inaction, never advanced automatically.
**What survives past this screen:** the winning/tied SKU's identity and the full Preference Summary, carried forward to Beer Detail (or Comparison, once built) by explicit hand-off.
**What's deliberately forgotten:** the specific sequence of questions asked and answered — only the resulting Preference Summary state matters going forward, not the path taken to reach it.

**Planning Mode, as a modifier on this entire sequence, not a separate one:**
- Present from the very first response through every subsequent one — a standing caveat, never a one-time disclaimer that can be missed.
- **[Newly discovered gap]** no interaction is defined for turning Planning Mode off within one continuous session — someone who starts planning ahead and then realizes they're actually at the store now has no modeled path back to an un-flagged Recommendation state.

---

## Part 3 — Beer Detail

**Trigger, today:** exclusively a hand-off from Recommendation (Beer Detail has no other reachable entry point in the shipped app). Architecturally, an Anchor-Known arrival via Search/Browse is the intended second entry — currently impossible, since that screen doesn't exist.
**What ValueBrew knows:** the identified SKU, and everything the Catalog holds about it.
**What it still needs to know:** nothing — this screen gathers no input at all.
**Question asked:** none, ever. Beer Detail asks no progressive question of any kind — an absolute rule, not a simplification.
**Why:** this screen's entire job is presenting already-known facts at uniformly high confidence; introducing a question here would mean introducing Soft-preference reasoning, which belongs exclusively to Recommendation.
**When it deliberately does not ask:** always — there's no conditional case where this screen asks something.

**States and what triggers each:**
- **Loading** on arrival, until resolution succeeds or fails.
- **Loaded**, refined into **Confirming** only if an Anchor Situation applies — **[flagged, canonically acknowledged gap]** the exact rule for *when* an Anchor Situation applies is unresolved, so this refinement currently has no defined trigger at all, only a defined *shape* for what happens if it fires.
- **Recovering** if the identified SKU can't actually be resolved — states the fact plainly, invents no substitute.
- **Completed** via two distinct, equally legitimate paths: explicit acceptance of a Confirm-as-Is judgment, or simply being satisfied and leaving with no further action — the "lighter" completion, never treated as lesser.
- **Handoff-Pending** on an explicit request toward Price Verification or (once built) Comparison.

**What causes branching:** entirely upstream — whatever entry context determined Anchor Situation status, itself unresolved.
**What causes convergence:** none needed — this screen has no gathering phase to converge from.
**What ends the interaction:** either terminal path in Completed, or a hand-off elsewhere.
**What survives:** the SKU's identity, carried into whichever screen is requested next.
**What's deliberately forgotten:** nothing new is created here to forget — this screen only reads.

---

## Part 4 — Price Verification

**Trigger:** an explicit request from Beer Detail — invitation-only, never automatic, even after a prior overcharge finding elsewhere.
**What ValueBrew knows:** the SKU's identity and its Legal Price.
**What it still needs to know:** the charged price — the one mandatory input this screen requires *from the person*, not just mandatory to already exist.
**Question asked:** effectively one — "what were you charged" — single-shot, not progressive.
**Why:** this is a two-fact classification, not a search; nothing about asking more would make the verdict more honest.
**When it deliberately does not ask further:** always, past the one input — no refinement step exists here.

**After the answer:**
- A precise, interpretable number → classified below/at/above Legal Price, with the three confidence dimensions (identification, legal reference, verification outcome) stated as the Explanation.
- **[Flagged, canonically acknowledged gap]** an imprecise or approximate charged price → no defined interaction exists. Neither "ask again" nor "accept and flag low-confidence" has been decided.

**What causes branching:** the precision of the single input alone.
**What causes convergence:** not applicable — no multi-step gathering exists to converge.
**What ends the interaction:** the verdict itself is the terminal output of this screen — Price Verification never reaches Decision Complete on its own; it only ever hands back to Beer Detail or ends the session outright.
**What survives:** the SKU's identity only, carried back to Beer Detail.
**What's deliberately forgotten, absolutely:** the charged price itself — it has no repository, no storage adapter, and does not survive even the hand-off back to the very next screen. This is the single strongest forgetting guarantee anywhere in the product.

---

## Part 5 — Comparison *(specified, not yet built)*

**Trigger:** explicit request from Beer Detail (carrying one candidate), from Search/Browse (carrying a multi-select), or from Recommendation (a Trade-off or Tie inviting richer treatment).
**What ValueBrew knows:** exactly the named candidates it was handed — never more.
**What it still needs to know:** whatever, if anything, one clarifying question could resolve.
**Question asked:** at most one, ever, in a single comparison cycle — a hard cap, stricter than Recommendation's iterative allowance, because the candidate set here is already bounded.
**Why the cap is exactly one, not zero or several:** the search space is already narrow (named candidates only); one question is enough headroom to resolve genuine ambiguity without re-opening the kind of open-ended gathering Recommendation owns.
**When it deliberately does not ask:** if the tie-breaker rule alone would resolve it, or if no single question could plausibly separate the candidates.

**Resolution sequence (Evaluating → Resolved):**
- Apply the shared tie-breaker rule first, always, before considering a Tie legitimate.
- A clean winner → **Resolved (Winner)**.
- A genuine differentiator on a Soft input → **Resolved (Trade-off Explanation)**, shown with its constituent facts alongside it, never separated across views.
- The tie-breaker rule genuinely fails to differentiate → **Resolved (Tie Disclosure)** — only reachable after the rule has actually been tried, never assumed.
- A named candidate can't be resolved → **Recovering**, scoped to that one candidate only, never the whole comparison.

**What causes branching:** the tie-breaker rule's outcome, applied once, deterministically.
**What causes convergence:** adding or removing a candidate re-evaluates the set, but reasoning already established for *unchanged* candidates is never redone from scratch.
**What ends the interaction:** explicit selection of a winner (following a Trade-off or a dominant candidate) or explicit acceptance of a tie.
**What survives:** the current candidate set and Preference Summary, carried forward on a hand-off to Beer Detail (one candidate), Price Verification (one candidate), or back to Recommendation (a constraint refinement — always treated as a hand-back, never a restart).
**What's deliberately forgotten:** nothing unique to this screen — it inherits whatever forgetting rules already govern the objects it's handling (Preference Summary, session-only; no persisted comparison history).

**[The single most consequential undefined interaction in this entire model]** every sequence above assumes exactly two candidates. The moment a genuine third candidate is in play — whether entered directly here or surfaced from a 3+-way tie inside Recommendation itself — none of the tie-breaker, Trade-off, or Tie Disclosure sequencing above has a defined generalization.

---

## Part 6 — Search/Browse *(no Screen Contract exists — this section describes the thinnest, most provisional interaction sequence in the model)*

**Trigger, as designed but not built:** a query or browse selection expressed at Home, or a backward navigation from Beer Detail.
**What ValueBrew would know:** the query/browse criteria and the Catalog.
**What it would still need to know:** nothing beyond matching, since this surface never evaluates.
**Question asked:** none — this surface matches, it does not reason, and asks nothing.

**States, as far as the existing Specification (unusually, ahead of its own Contract) actually defines them:**
- **Querying** on arrival with a new query/browse selection.
- **Results** once one or more candidates are found, or restored on backward navigation.
- **Recovering** on zero matches — a plain "no beer identified," never an invented substitute.
- **Handoff-Pending** on selection: exactly one selected → Beer Detail; two or more → Comparison.

**After each possible outcome:**
- One match selected → hands off, carrying that one SKU.
- Two or more selected → hands off, carrying the full set, never partial.
- Zero matches → returns to Home's Recovering state, any existing Preference Summary intact.

**What causes branching:** literal match count against the query — never a quality judgment, never a ranking by implied fit.
**What causes convergence:** not modeled — **[flagged, canonically acknowledged gap]** whether refining a query mid-session should revalidate the restored candidate list or simply redisplay it as last known is explicitly unresolved.
**What ends the interaction:** this surface never reaches Decision Complete on its own — composition always routes onward, by design.
**What survives:** any Preference Summary present at arrival, carried to wherever this hands off.
**What's deliberately forgotten:** nothing unique — but there is, structurally, almost nothing here to forget, since this surface performs no reasoning to begin with.

**[Newly discovered gap]** the Specification is also explicit that "changing or refining a query/selection before confirming a hand-off" — the moment-to-moment mechanics of building a selection, as opposed to its resolved outcome — is intentionally left unspecified. This is a real interaction-sequence gap, not just a missing screen.

---

## Part 7 — Cross-Cutting Behaviors

### Hard vs. Soft Constraints
A Hard Constraint (budget) can never be violated by any candidate shown, under any circumstance. A Strong Preference (style, today) can dominate a ranking but can be traded off against in a Trade-off Explanation. A Soft Preference is exactly the substance a Trade-off or Tie is built from — never enough on its own to eliminate a candidate outright.

### Clarification Questions — three distinct mechanisms, not one
This model preserves a real, load-bearing canonical distinction that's easy to blur: **Home's single Clarifying state**, **Comparison's capped-at-one Clarifying Question**, and **Recommendation's iterative Progressive Question-Asking** are three separate mechanisms, not one concept applied three places. The Lexicon itself names this explicitly — "Progressive Question... not to be confused with Clarifying Question, which belongs only to Comparison" — and Home's own single-question mechanism is a third, independent instance of the same discipline (ask exactly one, never a second) applied to intent classification rather than candidate narrowing.

### Recovery States, consolidated
Every Recovery condition in the product is named, scoped, and never silent: Home's "no beer identified" and Out-of-Scope; Recommendation's Conflicting Constraints and Low-Confidence Response (the only screen with two distinct Recovery shapes); Beer Detail's SKU Not Found; Price Verification's unresolved imprecise-input gap (the one Recovery-shaped case with no defined Recovery state yet); Comparison's per-candidate Recovering (never whole-comparison); Search/Browse's zero-match Recovering.

### Tie Handling
Identical philosophy wherever it appears — a tie is a Resolved-state, complete, honest answer, never a Recovery, never softened or apologized for. Recommendation's version can involve any number of tied candidates; Comparison's is bounded by whatever candidate set it was handed, and only fires once the shared tie-breaker rule has actually been tried and failed.

### Conflicting Constraints
Currently modeled only inside Recommendation. Both tension-producing inputs are named and stay visible; the Hard Constraint is never silently relaxed to manufacture an answer. No equivalent concept exists anywhere else in the product today — not because it's been ruled out elsewhere, but because no other surface currently gathers enough constraints for the concept to apply.

### Low Confidence
Modeled explicitly only in Recommendation, as a Recovery State. **[Inference, carried from Decision Engine 2.0]** Price Verification's imprecise-charged-price gap is structurally the same shape of problem without a named Recovery State of its own — flagged again here specifically as an interaction-sequencing gap, not just a reasoning gap.

### Explanation Timing
Always generated in the same moment as the conclusion it justifies, never as a separate pass. **[Recovered from Generation 1, not existing Gen 2 canon at the mechanical level]** the specific guarantee that makes this actually true — computing a score and its explanation from the same underlying comparison logic — should govern every interaction sequence above that produces an Explanation, not only Recommendation's.

### Navigation Ownership
`ValueBrewNavigator` is the only thing that ever triggers a transition between the sequences above — no screen ever decides, on its own, to move to another screen. Every hand-off described in this document (SKU identity, Preference Summary, candidate sets) crosses that one boundary and nowhere else.

### Session Boundaries
Preference Summary and Observed/Charged Price exist only for the duration of one continuous session, full stop. **[Newly discovered gap]** the mechanics of what "one continuous session" means at a platform level — specifically, how a platform-level back gesture mid-Recommendation should be intercepted or redirected, since Home is never a legal backward-navigation destination through the app's own controls — is explicitly left unspecified by Home's own Screen Contract, restated here because it's an interaction-sequencing question, not just an implementation detail.

### Graceful Degradation
Every sequence above already assumes at least one catalog gap is normal, not exceptional: a missing Style Benchmark is omitted, never treated as an error; a missing ABV — per the Catalog Specification — removes a candidate from value-based ranking rather than breaking the sequence; a missing Brewery field is simply absent from display. No interaction sequence in this model should ever halt because a piece of catalog knowledge is missing — it should narrow what can be honestly said, never crash what can be said at all.

---

## Part 8 — Closing Artifacts

### 1. The Complete Interaction State Machine

```
                         ┌─────────────────────────────┐
                         │            HOME              │
                         │  Initial → Clarifying (≤1)   │
                         │  → Out-of-Scope / Recovering │
                         │  (never reaches Completed)   │
                         └───────┬──────────┬───────────┘
             homeToRecommendation│          │ (Price Verification entry
             ({isPlanning})      │          │  not directly from Home in
                                 ▼          │  the shipped graph — reached
                    ┌─────────────────────┐ │  only via Beer Detail)
                    │    RECOMMENDATION    │ │
                    │ Initial→Gathering⇄   │ │
                    │ Evaluating→          │ │
                    │  Recommending        │ │
                    │  (incl. Tie) OR      │ │
                    │  Recovering          │ │
                    │  (Conflicting /      │ │
                    │   Low-Confidence)    │ │
                    │ → Completed          │ │
                    └──────────┬────────────┘ │
      recommendationToBeerDetail│(skuId)       │
                                ▼               │
                    ┌─────────────────────┐    │
                    │     BEER DETAIL      │◄───┘
                    │ Loading→Loaded/      │  beerDetailToPriceVerification(skuId)
                    │  Confirming*→        │──────────────┐
                    │  Completed OR        │              │
                    │  Recovering          │◄─────────────┤ priceVerificationToBeerDetail(skuId)
                    │ → Handoff-Pending     │              │
                    └───────────┬───────────┘              ▼
                                │                ┌─────────────────────┐
                    [Comparison,│unbuilt]        │  PRICE VERIFICATION  │
                                ▼                │ Awaiting→Verifying→  │
                    ┌─────────────────────┐      │  Verified OR         │
                    │     COMPARISON       │      │  Recovering (gap)    │
                    │ Initial→Evaluating⇄  │      │ (never Completed —    │
                    │  Clarifying (≤1)→    │      │  always hands back)   │
                    │  Resolved (Winner /  │      └─────────────────────┘
                    │  Trade-off / Tie) OR │
                    │  Recovering (scoped) │
                    │ → Completed          │
                    └─────────────────────┘

  [SEARCH/BROWSE — no Screen Contract; drawn dashed, since it doesn't
   structurally exist in the frozen Navigation Contract graph today]
   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
   │ Querying→Results→      │
   │ Handoff-Pending OR      │
   │ Recovering              │
   │ (never Completed)       │
   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```
*Confirming's trigger (Anchor Situation) is itself an undefined branch — see Part 8.4.

### 2. All Interaction Entry Points
- Fresh app open → Home, Initial.
- A failed Search/Browse attempt → Home, Recovering (Preference Summary preserved).
- A budget/preference/planning-ahead intent at Home → Recommendation, Initial.
- An explicit verification intent at Home → **architecturally undefined in the frozen graph** — Price Verification's only real, built entry point today is from Beer Detail, not directly from Home, despite Home's own Screen Contract naming a verification intent as one of its three routes. *(Restated as a finding, not resolved here — this is a real, discoverable tension between Home's stated routing table and the shipped Navigation Contract's actual edges.)*
- A Recommendation outcome (winner or any tied candidate) → Beer Detail.
- An explicit price-check request at Beer Detail → Price Verification.
- A return from Price Verification → Beer Detail.
- (Unbuilt) a Search/Browse selection, or a Recommendation Trade-off/Tie inviting richer treatment → Comparison.
- (Unbuilt) a query/browse expression at Home → Search/Browse.

### 3. All Terminal States
- Recommendation's **Completed**, reached only by explicit acceptance.
- Beer Detail's **Completed**, reached by explicit Confirm-as-Is acceptance *or* simple satisfied departure — the only screen with two legitimate terminal paths.
- Comparison's **Completed** (unbuilt), reached by winner selection or tie acceptance.
- **Never terminal on their own:** Home (always routes onward), Price Verification (always hands back or the session simply ends outside the app's own state machine), Search/Browse (always routes onward, unbuilt).

### 4. Every Undefined Interaction Discovered
1. What happens to a Recommendation candidate with incomplete Composition Knowledge (Part 2).
2. Imprecise/approximate charged-price handling (Part 4) — already canonically acknowledged.
3. The Anchor Situation trigger rule for Confirm-as-Is (Part 3) — already canonically acknowledged.
4. 3+-candidate comparison and tie logic (Part 5) — already canonically acknowledged, the most consequential.
5. Query/selection refinement mechanics on Search/Browse (Part 6) — already canonically acknowledged.
6. **No interaction exists for exiting Planning Mode once entered, within one session** (Part 2) — newly discovered here.
7. **No defined interception behavior for a platform-level back gesture mid-Recommendation**, given Home is never a legal backward destination through the app's own controls (Part 7, Session Boundaries) — newly discovered here, restated as an interaction gap rather than only an implementation footnote.
8. **A real tension between Home's stated routing table and the shipped Navigation Contract's actual edges** for the verification-intent path (Part 8.2) — newly discovered here.
9. Whether Price Verification should gain a Low-Confidence-equivalent Recovery State (Part 7) — a reasoned suggestion, not a decision.

### 5. Every Product Decision Still Required Before Implementation
- A rule for candidates with missing catalog facts in Recommendation's ranking (#1 above).
- Imprecise charged-price handling (#2).
- The Anchor Situation trigger rule (#3).
- 3+-candidate comparison and tie generalization (#4).
- Search/Browse's entire Screen Contract — the root cause of #5, #8, and this document's dashed, provisional Search/Browse section entirely.
- Whether Planning Mode needs an explicit exit interaction, or is intentionally one-way for the duration of a session (#6).
- How a platform back-gesture should behave mid-Recommendation (#7).
- Reconciling Home's routing table against the actually-shipped Navigation Contract graph for the Price-Verification-from-Home path (#8).
- Whether to build a Low-Confidence-equivalent Recovery State for Price Verification (#9).
- Whether the Verification History proposal named in the Catalog Specification is compatible enough with the product's restraint principles to pursue at all.

None of these are resolved by this document. Naming them precisely is the document's actual job.
