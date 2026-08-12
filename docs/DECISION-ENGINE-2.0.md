# ValueBrew Decision Engine 2.0

*The reasoning specification — how ValueBrew thinks, not how it's coded. Built entirely from the canonical Screen Contracts (via their citation-only Specifications, which restate Contract validation rules verbatim), the Recommendation Framework, the Decision Engine Model, the ADR, Beer Knowledge Model 2.0, and Generation 1's own reasoning code, reconciled into one document. Every claim below is tagged: unmarked text restates something already established in the canon; **[Inference]** extends established principles into a case the canon doesn't directly address; **[Flagged Gap]** names a place the architecture genuinely doesn't yet define the reasoning, requiring a real Product Decision before it can be built.*

---

## Part 1 — The Five Reasoning Surfaces

| Surface | The question it actually answers | Status |
|---|---|---|
| **Recommendation** | "Given what I've told you, which beer should I buy?" | Built |
| **Beer Detail** | "What is this specific thing, completely — and, if I already had it in mind, was that a good pick?" | Built (Confirm-as-Is unbuilt) |
| **Price Verification** | "Is what I'm being charged fair?" | Built |
| **Comparison** | "Between these specific beers I already have in mind, which is better — or are they genuinely equal?" | Specified, not built |
| **Search/Browse** | "Which real, catalogued thing did I mean?" | No Screen Contract exists at all |

Each reasons about a different question and owns a different, non-overlapping slice of judgment — no two surfaces ever re-derive the same conclusion.

---

## Part 2 — Recommendation

**1. The question:** which beer, of everything available, best fits what's actually been said.

**2. Knowledge domains required:** Identity, Composition, Economic, Comparative, Provenance/Confidence.

**3. Mandatory facts:** a budget. Nothing proceeds — no candidate set exists to reason over — without it, because it's a Hard Constraint.

**4. Optional facts:** style (a Strong Preference, if given). Canon additionally names strength, size, and brand as inputs the Decision Engine Model orders after budget and style — none of these are gathered in the current build; V1 stops at budget + one optional style.

**5. Explicitly forbidden assumptions:** budget or style are never inferred from anything but an explicit statement. A question is never asked whose answer couldn't change the outcome. A question is never asked about an input already stated. A highest-value pick is never substituted for a genuine tie.

**6. How uncertainty propagates:** every input's own confidence tier (Verified/Computed/Human Judgment) is carried forward into the eventual Explanation, never smoothed into one blended figure at the point of decision.
**[Flagged Gap]** — no canonical rule addresses what happens when a candidate SKU has an *incomplete* fact the ranking needs — specifically, Beer Knowledge Model 2.0 establishes that Composition Knowledge (ABV) is genuinely absent for most of the real catalog today. Nothing in the Recommendation Screen Contract, the Decision Engine Model excerpts available, or the ADR says whether a SKU with a null ABV should be silently excluded from value-based ranking, included with an honest caveat, or something else. This is a real, load-bearing gap the current documentation does not resolve, and it will be hit immediately the moment a real, incomplete catalog is loaded.

**7. When it must refuse to answer:** when no real candidate satisfies the stated Hard Constraint at all — this is Conflicting Constraints, not a silent failure and not a forced pick.

**8. When it asks another question:** exactly the Recommendation Screen Contract's own threshold, reproduced here as the reasoning model's literal rule — justified when two or more candidates remain indistinguishable on every known Hard and Strong input *and* the next question's answer would actually separate them; forbidden when a single candidate already dominates, when the remaining candidates differ only on a Soft input (a Trade-off or Tie is the honest response instead), when the question would touch an input already stated, or when no further Hard or Strong input remains to ask about (Low-Confidence Response applies instead of asking indefinitely).

**9. How candidates are narrowed:** filter strictly by every stated Hard Constraint first — nothing that violates one is ever a candidate, regardless of anything else about it. Among survivors, if one dominates on every known Strong Preference, it wins outright. If multiple survivors differ only on Soft inputs, that difference becomes a Trade-off Explanation or a Tie Disclosure — never a forced pick.

**10. How explanations are generated:** always in the same moment as the conclusion, never as a second pass. **[Inference, recovered from Generation 1]** — the canon states this as a principle ("Explanation always accompanies Recommendation") but the specific mechanical guarantee that makes it *actually true* — computing score and explanation from the same underlying comparison logic, so an explanation can never disagree with the score it's justifying — is not spelled out anywhere in the current canonical documents at the reasoning-specification level. Generation 1's engine enforced exactly this (`SimilarityStrategy.score()` and `.explain()` calling the same private comparison helper). Nothing in Gen 2 principles contradicts this; it's fully compatible and should be adopted as a requirement of this reasoning model, not just a UI-layer nicety.

**11. How ties are detected and preserved:** a tie is a Resolved-state outcome, never a Recovering condition. Once the tie-breaker rule (Comparison and Recommendation share this) has been applied and genuinely fails to differentiate, the tie is disclosed plainly as a complete answer — never softened, apologized for, or presented as incomplete.

**12. How conflicting constraints are handled:** when a stated Hard Constraint and Strong Preference together exclude every real candidate, both tension-producing inputs are named explicitly and stay visible — the Hard Constraint is never silently relaxed to manufacture an answer.

**13. How low-confidence situations are handled:** fires when too little is known to meaningfully distinguish among a large field in a way an honest explanation could describe. The response is either a request for the single most useful next input, or a clearly labeled provisional answer — never continued indefinite questioning.

---

## Part 3 — Beer Detail

**1. The question:** what is this exact, already-identified thing — completely — and (only if an Anchor Situation applies) was choosing it a good call.

**2. Knowledge domains required:** Identity, Composition, Economic (Legal Price only), Comparative, Availability, Provenance/Confidence, Freshness.

**3. Mandatory facts:** the SKU is already resolved before this reasoning surface is ever reached — identification is a precondition, not something decided here.

**4. Optional facts:** Style Benchmark standing, shown only where a benchmark exists and gracefully omitted otherwise; the Confirm-as-Is judgment, shown only when an Anchor Situation applies.

**5. Explicitly forbidden assumptions:** Observed/Charged Price never appears here under any condition. This screen never performs verification, comparison, or recommendation reasoning of its own — it never decides, it only presents. A missing Style Benchmark is never treated as an error.

**6. How uncertainty propagates:** confidence here is uniformly high by construction — every fact on this screen is Verified or Computed, never Soft-preference-driven, so there's no Hard/Strong/Soft split to manage the way Recommendation has.

**7. When it must refuse to answer:** when the identified SKU can't actually be resolved — a Recovering state, stating the fact plainly, never inventing a substitute.

**8. When it asks another question:** never. Beer Detail asks no progressive question of any kind — this is an explicit, absolute Screen Contract rule, not a simplification.

**9. How candidates are narrowed:** not applicable — this surface reasons about exactly one already-identified thing, never a set.

**10. How explanations are generated:** only the Confirm-as-Is judgment, when present, carries an Explanation — the surrounding facts are direct, Verified/Computed statements that don't require justification the way a judgment does.

**11. Ties:** not applicable — nothing here is being ranked against alternatives.

**12. Conflicting constraints:** not applicable — no constraints are gathered on this screen.

**13. Low-confidence situations:** not applicable in Recommendation's sense, but this is exactly where the canon's own most consequential open gap lives:
**[Flagged Gap, already canonically acknowledged]** — the rule determining *when* an Anchor Situation applies at all (and therefore when Confirm-as-Is should even attempt to fire) is unresolved. This isn't a low-confidence output problem; it's an unresolved *trigger* problem, upstream of any reasoning the judgment itself would perform.

---

## Part 4 — Price Verification

**1. The question:** is this specific charged price fair, relative to the legal reference.

**2. Knowledge domains required:** Identity, Economic (both Legal Price and the entered Charged Price), Freshness.

**3. Mandatory facts:** the SKU's identity, its Legal Price (already known), and the Charged Price, which must be entered — this is the one reasoning surface where a fact is mandatory *from the user*, not just mandatory to already exist.

**4. Optional facts:** none — this is a two-input decision with no refinement step, unlike Recommendation's optional style question.

**5. Explicitly forbidden assumptions:** the charged price is never rounded, estimated, or silently interpreted when it's imprecise or approximate — this is explicitly named as unresolved by the Screen Contract itself, and the current build does not fill the gap by inference. Price Verification never escalates into Recommendation or Comparison on its own initiative, even after finding an overcharge.

**6. How uncertainty propagates:** minimal by design — given two precise numbers, the classification is a clean, deterministic three-way split. All the real uncertainty in this surface concentrates in exactly one place: what counts as a valid charged-price input in the first place.

**7. When it must refuse to answer:**
**[Flagged Gap, already canonically acknowledged]** — a charged price that can't be cleanly interpreted as a number is the one case this surface doesn't yet have a defined response for. Neither "refuse and ask again" nor "accept and flag low-confidence" has been decided.

**8. When it asks another question:** never — no progressive gathering exists here; this is single-shot input, then verdict.

**9. How candidates are narrowed:** not applicable — one SKU, one verdict, no set to narrow.

**10. How explanations are generated:** via three explicitly separated confidence dimensions named in the Screen Contract — identification confidence, legal-reference confidence, and verification-outcome confidence — each stated in plain text rather than combined into one figure.

**11. Ties:** not applicable — "at legal price" is itself a clean, unambiguous outcome, not a tie between competing answers.

**12. Conflicting constraints:** not applicable — nothing is being weighed against anything else.

**13. Low-confidence situations:**
**[Inference]** — Recommendation has a named Low-Confidence Response Recovery State for exactly this shape of problem (too little to go on, respond honestly rather than guess). Price Verification has no equivalent named state for its own analogous case (an imprecise charged price). Given the same "silence is better than a guess" principle governs both surfaces, it would be internally consistent for Price Verification to eventually gain its own equivalent Recovery State rather than leaving the imprecise-price case as an undefined edge. This is a reasoned suggestion for how the existing gap could be closed consistently with the rest of the model — not a decision this document is making on its own authority.

---

## Part 5 — Comparison *(specified, not yet built)*

**1. The question:** between these specific, named beers — never more, never fewer than what was handed to it — which is better, or are they genuinely equal.

**2. Knowledge domains required:** Identity, Composition, Economic, Comparative, Provenance/Confidence.

**3. Mandatory facts:** at least two already-identified, resolvable candidates. This surface never searches the catalog on its own — every candidate must arrive already named.

**4. Optional facts:** a Preference Summary carried in from wherever this comparison was entered (Search/Browse, Recommendation, or Beer Detail).

**5. Explicitly forbidden assumptions:** no candidate is ever added beyond what was explicitly handed in. The result never implies or claims catalog-wide "recommended" status — only a bounded claim about the named set. A winner is never manufactured to avoid presenting a genuine Trade-off or Tie. A Trade-off is never presented without its constituent facts alongside it.

**6. How uncertainty propagates via two distinct layers, never merged:** per-candidate confidence (uniformly high, the same as Beer Detail, since each candidate's own facts are Verified/Computed) and result-level confidence (which can be genuinely low even when every underlying fact is certain, whenever the differentiator between candidates is a Soft Preference rather than a Hard or Strong one).

**7. When it must refuse to answer:** when one named candidate can no longer be resolved (a stale reference) — Recovering, scoped to that one candidate specifically, never treated as the whole comparison failing.

**8. When it asks another question:** at most one clarifying question, ever, in a single comparison — a hard cap, explicitly stricter than Recommendation's iterative allowance, because the candidate set here is already bounded and known.

**9. How candidates are narrowed:** not narrowing in Recommendation's sense (the set is fixed by the caller) — instead, a resolution sequence: apply the shared tie-breaker rule first; only once it genuinely fails to differentiate does a Tie Disclosure legitimately fire, never before that rule has actually been tried.

**10. How explanations are generated:** a Trade-off Explanation is always shown together with the specific facts that produced it — never as a separate view a person has to piece together themselves.

**11. Ties:** identical philosophy to Recommendation's, applied to a bounded set — a Resolved-state outcome, not a failure, reached only after the tie-breaker rule has been tried and hasn't worked.

**12. Conflicting constraints:** structurally different from Recommendation here — Comparison doesn't gather its own Hard Constraints; it inherits whatever Preference Summary was carried in from wherever it was entered, so a genuine constraint conflict at this surface is really a Recommendation-layer question being carried forward, not something Comparison resolves itself.

**13. Low-confidence situations:** not modeled as a separate state here — Comparison's honesty about uncertainty is fully captured by the dual confidence layers in point 6; there's no additional Low-Confidence Recovery State layered on top.

**[Flagged Gap, the single most consequential one in this entire specification]** — every rule above assumes exactly two candidates. The moment a third genuine candidate enters (whether via Comparison directly, or via a 3+-way tie surfacing from Recommendation's own tie-handling), none of the tie-breaker, Trade-off, or Tie Disclosure logic above has a defined generalization. This is not a Comparison-screen-only problem — it's reachable from Recommendation's own Core reasoning the moment three candidates tie on a Soft input, independent of whether the Comparison surface is ever entered at all.

---

## Part 6 — Search/Browse *(no Screen Contract exists — reasoning described here is the thinnest and most provisional in this document)*

**1. The question:** which real, catalogued thing did the person actually mean.

**2–13.** Almost none of the fifteen points can be answered with canonical authority here, because **no Screen Contract has ever been written for this surface** — the single Open, non-Accepted decision in the entire Architectural Decisions Record. What little is known comes from a Screen *Specification* that exists unusually ahead of its own Contract, and even that document is explicit about what this surface does *not* do:

- It **matches, it does not evaluate** — no ranking by implied quality, no ordering by anything resembling recommendation logic.
- It never claims a "best match" — only what matched a query or browse selection, presented without characterization.
- Zero candidates → a plain, honest "no beer identified" recovery, never an invented substitute.
- One selected match → hands off to Beer Detail. Two or more selected → hands off to Comparison. Never partial, never more than what was actually selected.

**[Flagged Gap]** — beyond this, there is no defined reasoning model at all: no rule for how fuzzy or literal the matching should be, no rule for ranking multiple literal matches against each other for display order, and no rule for how a restored candidate list (returning from Beer Detail) should be revalidated versus simply redisplayed. Generation 1 had a real, working fuzzy-match implementation here — a legitimate starting reference for whatever matching logic eventually gets specified, not a design problem to solve from nothing.

---

## Part 7 — Cross-Cutting Reasoning Rules (Apply to All Five Surfaces)

- **Never invent a fact.** Absence is represented as absence, never filled with a plausible guess — this is the single rule every surface above inherits without exception.
- **Confidence is never blended into one figure**, anywhere, regardless of which surface is reasoning.
- **Explanation is computed together with its conclusion**, never derived afterward as a separate pass — canonically stated as a principle for Recommendation; **[Inference]** this document extends it as a requirement for Comparison's Trade-off Explanation too, since nothing in the canon suggests the guarantee should be weaker there, and the risk it protects against (an explanation quietly drifting from what actually drove the result) applies identically.
- **A tie, wherever one is genuinely possible, is a complete answer — never a failure requiring further probing.**
- **[Inference]** — under genuine uncertainty, the reasoning model should default toward the less committal answer (a Tie or Recovery State) over a confident-looking guess, mirroring the asymmetric-risk default already explicitly adopted by the KSBCL pipeline's own governance ("false split beats false merge"). This isn't yet stated as an app-level ADR decision the way it is for the pipeline — it's a reasonable, consistent extension of an already-adopted principle, flagged here as exactly that, not as settled canon.

---

## Part 8 — Ownership Matrix

| Reasoning responsibility | Owner | Never performed by |
|---|---|---|
| Deciding which SKU best fits stated preferences | Recommendation | Beer Detail, Comparison |
| Presenting complete facts about one identified SKU | Beer Detail | Recommendation, Comparison |
| Classifying a charged price against the legal reference | Price Verification | Every other surface |
| Judging one already-known SKU against another named SKU | Comparison | Recommendation (which only ever compares against the whole catalog, never two named things) |
| Matching a query/browse selection to real catalog entries | Search/Browse | Every other surface (none of them search) |
| Deciding *whether* an Anchor Situation applies to a given Beer Detail visit | **Unowned — the unresolved gap itself** | — |

---

## Part 9 — Deterministic vs. Deliberately Configurable

**Permanent, deterministic — not open to future variation without a new, deliberate Product Decision:**
- Budget is always a Hard Constraint.
- Explanation always accompanies a Recommendation, Trade-off, or Verification verdict, in the same moment it first appears.
- A genuine tie is always disclosed, never resolved by invention.
- No accounts, no inferred preferences, no persisted user identity anywhere in the reasoning.
- Price Verification never escalates on its own initiative.

**Deliberately configurable, by design — future variation is expected and welcome here:**
- *Which* Strong Preferences are collected and in what order (today: style only; the Decision Engine Model already names strength, size, and brand as future candidates for this same ordered sequence).
- The specific numeric thresholds behind "worth mentioning" in an explanation, and any per-dimension weighting a future scoring approach might use — **[Recovered from Generation 1]** Gen 1's own `RecommendationPolicy` pattern (rules injected into an engine that holds none of its own) is a compatible, reusable shape for exactly this kind of configurability, and nothing in Gen 2's principles argues against reviving it.
- A future named Recommendation Profile (e.g., a budget-conscious mode weighting price more heavily) — Gen 1 planned this and never built it; Gen 2's constraint-tier model could accommodate an equivalent without restructuring the reasoning above it.

---

## Part 10 — Consolidated List of Flagged Gaps

1. No rule for a Recommendation candidate with incomplete Composition Knowledge (Part 2.6) — **newly surfaced by this document**, not previously named anywhere in the canon.
2. Imprecise/approximate charged-price handling (Parts 4.5, 4.7) — already canonically acknowledged.
3. The Anchor Situation trigger rule for Confirm-as-Is (Part 3.13) — already canonically acknowledged.
4. Ambiguous preference-type statements on Recommendation — already canonically acknowledged, not separately detailed above since it doesn't change any of the thirteen points' structure, only which bucket a given input falls into.
5. 3+-candidate comparison and tie logic (Part 5, closing) — already canonically acknowledged, and the single most consequential gap in this entire specification.
6. Whether Price Verification should gain its own Low-Confidence-equivalent Recovery State (Part 4.13) — **a reasoned suggestion from this document**, not a decision.
7. The mechanical score-and-explanation-together guarantee, as an explicit reasoning-model requirement rather than only a stated principle (Part 2.10, Part 7) — **recovered from Generation 1**, compatible with and recommended for adoption by Gen 2.
8. Search/Browse's entire reasoning model beyond "match, don't evaluate" (Part 6) — the most structurally significant gap in the whole product, restated here specifically in terms of how it limits any future narrowing/matching logic.

None of these gaps are resolved by this document. Naming them precisely — not guessing past them — is itself the discipline this entire reasoning model is built on.
