# ValueBrew Canonical Architecture — Independent Review

**Reviewer role:** External architecture reviewer (Principal Engineer / Staff Product Engineer / Mobile Architect)
**Scope reviewed:** The nineteen frozen documents (01–19) plus the Architecture Review Guide (00), read in the canon's own declared order.
**Mandate:** Assess implementability, not product direction. The architecture is treated as frozen. Findings below are restricted to the three categories the canon itself invites: things genuinely missing, things that contradict each other, and things stated with more confidence than they've earned — never new features, never redesign.

---

## How to read this document

Section 1 works through each of the nineteen documents individually, against the ten-point methodology requested. Section 2 steps back and evaluates the canon as a system. Section 3 gives the honest engineering-manager verdict on whether this repository could be handed to five independent senior engineers today. Section 4 is the itemized findings list, each one citing the exact document and section it comes from.

One general observation before the detail: this is an unusually disciplined piece of architecture work. The Evidence/Inference/Hypothesis/Assumption labeling in the Behavioral Hypothesis Model, the citation discipline running through all nineteen documents, and the self-correcting history visible in the Feature Inventory and Price Verification Screen Contract are genuinely rare in practice. That's stated plainly here because it matters for calibrating what follows — the issues below are real, but they are the issues of a rigorous process, not a sloppy one. A rigorous process that still produces four real contradictions across nineteen documents is worth taking seriously, precisely because rigor is what's supposed to prevent that.

---

## 1. Per-Document Review

### 00 — Architecture Review Guide
**Purpose:** Orient an external reviewer before they touch the canon — reading order, scope, principles, known gaps, feedback taxonomy.
**Responsibilities:** Framing only; introduces no architecture of its own.
**Boundary check:** Clean — explicitly disclaims introducing new content, and largely keeps that promise.
**Contradictions with prior docs:** None; it's the last document written, citing everything before it.
**Assumptions:** That a reviewer needs this scaffolding at all — reasonable, given nineteen documents.
**Hidden coupling:** None found.
**Missing dependencies:** None.
**Terminology:** Consistent with the Lexicon.
**Implementation leakage:** None.
**Quality score: 9/10.** The one soft critique: a guide this good at pre-supplying the exam questions risks a reviewer treating the canon's own self-diagnosis (Section 6, Section 9) as the whole of what needs checking. It isn't — see Section 4 below.

### 01 — Behavioral Hypothesis Model
**Purpose:** Ground the entire product in labeled secondary research before any product decision is made.
**Responsibilities:** Behavioral pathways, segments, JTBDs, frictions, opportunity space, confidence map. Correctly stays out of product decisions.
**Boundary check:** Clean — this document never prescribes a feature, only evidences a job.
**Contradictions:** None; it's the root.
**Assumptions:** Explicitly and extensively labeled throughout — this is the document's core discipline, and it holds up under scrutiny. Several "Evidence" labels rest on non-India, non-beer, or single-source findings (Section 6's Confidence Map is honest about this), which is a real evidentiary weakness in the underlying research, not a flaw in how the document represents that research.
**Hidden coupling:** None.
**Missing dependencies:** None — it's the foundation.
**Terminology:** Introduces the Evidence/Inference/Hypothesis/Assumption vocabulary cleanly; used consistently downstream.
**Implementation leakage:** None.
**Quality score: 9/10.**

### 02 — Product Definition Document
**Purpose:** Convert the behavioral model into founding product commitments.
**Responsibilities:** Definition, vision, principles, boundaries, V1 scope. Correctly stays out of screens or reasoning mechanics.
**Boundary check:** Clean.
**Contradictions:** None with 01.
**Assumptions:** One worth naming: Section 11 states a Fallback/substitute-suggestion capability "should probably never exist," which is a stronger, more permanent-sounding rejection than the underlying evidence supports. JTBD-4 in the Behavioral Hypothesis Model is labeled **Low confidence, entirely unobserved** — not disconfirmed, just never observed. Proxy-Buying (JTBD-5) carries comparably thin evidence and is treated as *deferred*, not *rejected*. The canon applies two different evidentiary standards to two similarly weak findings without explaining why. See Finding Mi2.
**Hidden coupling:** None.
**Missing dependencies:** None.
**Terminology:** Clean, and this is where several canonical terms (Recommendation, Recommended) first get their authoritative source per the Lexicon.
**Implementation leakage:** None.
**Quality score: 8.5/10.**

### 03 — Decision Engine Model
**Purpose:** The conceptual reasoning model — Journeys, inputs, progressive gathering, recommendation types, confidence, design principles.
**Responsibilities:** Correctly stays a "thinking model," never an algorithm or UI.
**Boundary check:** Clean in isolation.
**Contradictions:** This is where a real cross-document issue originates. Section 4's Progressive Information Gathering places occasion inside the live, ordered question sequence ("strength/ABV and style before occasion") — i.e., something the engine actively asks about, just last. Four documents later, the Feature Inventory declares occasion **excluded from Core V1** entirely and defers it to Future. Neither document was revised to reconcile the other. See Finding M2 — this is the most consequential finding in this review.
**Assumptions:** Journey 4 and Journey 5 are included "for conceptual completeness" despite deferred/unconfirmed evidentiary status — this is stated honestly, not a violation.
**Hidden coupling:** None beyond the occasion issue above.
**Missing dependencies:** None.
**Terminology:** Clean; Journey vocabulary is used consistently everywhere downstream.
**Implementation leakage:** None.
**Quality score: 9/10** (docked for the occasion inconsistency it originates, even though the fault is shared with document 07).

### 04 — Recommendation Framework
**Purpose:** The reasoning rules — constraint tiers, tie-breaking, trade-off framework, explanation rules.
**Responsibilities:** Clean, load-bearing, and precise — this document is quoted almost verbatim by every downstream Screen Contract.
**Boundary check:** Clean.
**Contradictions:** Section 2 lists occasion as a live Soft Preference tier member, consistent with document 03, inconsistent with document 07's later Future-tier exclusion — same root issue as above, not a new one.
**Assumptions:** None flagged that aren't already flagged upstream.
**Hidden coupling:** None.
**Missing dependencies:** None substantive, but see terminology note below.
**Terminology:** This is the one document among the ten foundational documents whose header omits an explicit "derived from N frozen documents" provenance statement — every other document in the sequence states this. Minor, but it breaks an otherwise universal convention. See Finding Mi1.
**Implementation leakage:** None.
**Quality score: 8.5/10.**

### 05 — Beer Knowledge Model
**Purpose:** The domain and knowledge architecture — what data exists, its confidence tier, its lifetime.
**Responsibilities:** Clean; explicitly excludes a Store/Retailer entity and defends that exclusion against the evidence.
**Boundary check:** Clean — stays conceptual, never proposes a schema.
**Contradictions:** None found.
**Assumptions:** None beyond what's already inherited.
**Hidden coupling:** None.
**Missing dependencies:** None.
**Terminology:** Introduces Verified/Computed/Human Judgment cleanly; used with discipline everywhere downstream, including the one place (Price Verification Screen Contract) where a document later needs to *split* one of its own categories more finely.
**Implementation leakage:** None.
**Quality score: 9/10.**

### 06 — User Interaction Model
**Purpose:** How a person engages with the reasoning above, independent of screens.
**Responsibilities:** Intent map, interaction states, flows, principles. Correctly stops short of screens or wireframes.
**Boundary check:** Clean.
**Contradictions:** None found.
**Assumptions:** None beyond upstream.
**Hidden coupling:** The interaction states here (Exploring, Narrowing, Evaluating, Comparing, Confirming, Learning, Decision Complete) are a real design achievement — they map cleanly onto every Screen Contract's later State Machine without needing to be reinvented per screen.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8.5/10.**

### 07 — Feature Inventory
**Purpose:** The capability taxonomy — Module/Experience/Feature/Engine Behavior/Platform Service/Mechanism — and MVP classification.
**Responsibilities:** This is the strongest single document in the canon. It is also the only one that documents its own prior mistakes in the text (Confirm-as-Is briefly having an independent entry point; Trade-off/Tie-handling being conflated with the Comparison Experience) rather than silently fixing them.
**Boundary check:** Clean and rigorously self-enforcing (Section 2's own six-layer taxonomy is a genuine discipline, not decoration).
**Contradictions:** This is the document that introduces the occasion Core/Future split without reconciling it against document 03. See Finding M2.
**Assumptions:** None beyond upstream.
**Hidden coupling:** Section 3's explicit clarification that Trade-off/Tie-handling (Engine Behavior, Core) and Beer Comparison (Experience, Important-Soon-After) are not the same commitment is exactly the kind of hidden-coupling risk the Review Guide asks reviewers to hunt for — and it's already caught and resolved here. Genuinely good work.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None — Mechanisms are explicitly kept out of the canonical tier system, correctly.
**Quality score: 9/10.**

### 08 — Information Architecture
**Purpose:** Screens, from the user's perspective — inventory, responsibilities, navigation model, entry points, ownership.
**Responsibilities:** Clean ownership statements per screen, each with an explicit "does not own."
**Boundary check:** Clean.
**Contradictions:** None found directly, but this is the document that locks in six screens while explicitly declining to write a contract for one of them (Search/Browse Results) — the seed of the canon's most consequential open gap. That deferral is stated honestly (Section 8's "Assumptions made explicitly" acknowledges the gap exists), which is good practice, but the downstream consequences turn out to be larger than this document implies. See Finding C1.
**Assumptions:** Three are explicitly named in Section 8 — good discipline, genuinely rare to see done this cleanly.
**Hidden coupling:** None beyond the SBR gap.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8.5/10.**

### 09 — Experience Flows
**Purpose:** Interface-independent, end-to-end journeys for all seven canonical flows.
**Responsibilities:** Clean; correctly stays out of screens and layout.
**Boundary check:** Clean.
**Contradictions:** Section 2's Price Verification flow entry states this flow carries "the highest, most uniform Confidence Communication anywhere in the canon." Six documents later, the Price Verification Screen Contract explicitly identifies this exact claim as an oversimplification and replaces it with a three-dimensional confidence model, one dimension of which is *not* uniformly high. Document 09 itself was never revised to match. Two frozen documents now make textually different claims about the same behavior. See Finding M4.
**Assumptions:** Journey 4/5 confidence-ceiling handling is stated plainly and consistently with upstream documents.
**Hidden coupling:** None beyond the above.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8/10** (docked specifically for the un-reconciled confidence claim).

### 10 — Content Architecture
**Purpose:** How information should be composed and ordered on any given screen.
**Responsibilities:** Clean; Information Objects, Compositions, and Priority Rules are precise and genuinely useful as a build reference.
**Boundary check:** Clean.
**Contradictions:** Principle 8 correctly reflects the Feature Inventory's occasion-deprioritization, but Section 2's own Preference Summary definition lists occasion as a standing component of that object without qualification — consistent with the "volunteered, not solicited" reading of the occasion issue, but not explicit about it. Reinforces Finding M2 rather than introducing a new one.
**Assumptions:** None beyond upstream.
**Hidden coupling:** None.
**Missing dependencies:** None.
**Terminology:** Section 7's description of Alcohol-Adjusted Value's dependency chain is precise and correctly distinguishes Beer Detail as *display* owner from the Platform Service as *computation* owner — but see Information Architecture's looser phrasing on the same fact, Finding Mi4.
**Implementation leakage:** None.
**Quality score: 9/10.**

### 11 — Home Screen Contract
**Purpose:** The single entry point; capture intent, route it, do no reasoning of its own.
**Responsibilities:** Otherwise excellent — this contract visibly repairs its own earlier gap (Section 13's Validation explicitly notes the unrecognized-intent failure mode was previously open and is now resolved), which is exactly the kind of self-correcting discipline this canon does well elsewhere.
**Boundary check:** This is where the review's single Critical finding lives. Section 11's Failure Conditions and Section 12's Acceptance Criteria both require Home to restate "the four supported capabilities — identify a beer, recommend a beer, verify a price, compare beers" to any out-of-scope user. But Section 2's MUST NEVER list forbids Home from transitioning directly to Comparison, and Section 7's Interaction Contract defines only four recognized intent-expression triggers — none of them a comparison-intent trigger. Home is contractually required to advertise a capability it has no defined mechanism to route toward. See Finding C1.
**Contradictions:** The contradiction above is internal to this single document — not a cross-document drift, which if anything makes it more surprising, since this document is otherwise the most reflective one in the canon about its own gaps.
**Assumptions:** Section 13 names one explicitly (Planning/Proxy routing as a flagged Recommendation variant) — good practice.
**Hidden coupling:** None beyond the Comparison-routing gap.
**Missing dependencies:** None additional.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8/10** — the score would be a 9 were it not for a genuinely load-bearing internal contradiction in a document that otherwise sets the standard for the rest of the canon.

### 12 — Recommendation Screen Contract
**Purpose:** The core synthesis screen — the only place the Decision Engine's reasoning becomes visible to a person.
**Responsibilities:** This is the strongest Screen Contract in the set. Section 6's behavioral thresholds ("Another question is justified when...", "A recommendation exists when...") are genuinely testable rules, not prose — this is what implementation-ready specification actually looks like, and the rest of the canon should be held to this bar.
**Boundary check:** Clean, with the one caveat below.
**Contradictions:** Inherits the occasion Core/Future ambiguity (Finding M2) directly — the MUST list requires the screen to never withhold a recommendation for a missing occasion input and never ask about occasion before budget, both of which presuppose occasion is a live, in-scope input, which Feature Inventory says it isn't for V1.
**Assumptions:** Section 11 names its one open gap (ambiguous preference-type statements) honestly rather than resolving it silently — correct practice.
**Hidden coupling:** None beyond the above.
**Missing dependencies:** Section 9's Dependencies list omits the Home Screen Contract, despite this screen receiving Planning/Proxy mode flags that originate at Home's hand-off. Minor, but a real citation gap. See Finding Mi5.
**Terminology:** Clean and precise — the System-Decision-vs-User-Decision split in Section 6 is a highlight of the entire canon.
**Implementation leakage:** None.
**Quality score: 9/10.**

### 13 — Beer Detail Screen Contract
**Purpose:** Present everything known about one already-identified SKU; surface Confirm-as-Is when an anchor situation applies.
**Responsibilities:** Clean, single-purpose, correctly excludes Observed/Charged Price absolutely.
**Boundary check:** Section 6 correctly and explicitly states this screen carries no Soft-preference content and therefore no mixed-confidence case — good, proactive clarification of something a future implementer might otherwise get wrong.
**Contradictions:** None found beyond the header/dependency issue below.
**Assumptions:** Section 11 honestly names its one open gap — the exact rule for when an anchor situation applies — rather than inventing a resolution.
**Hidden coupling:** None found; this screen's making its own anchor-situation determination is a legitimate reading of "surfacing a Feature," not a leak, and the canon already flags the exact rule as undecided.
**Missing dependencies:** This document's header explicitly claims derivation from "the ten frozen documents plus the Home and Recommendation Screen Contracts," but Section 9's own Dependencies list cites only the ten foundational documents — Home and Recommendation are named in the header but never actually cited in the body. See Finding M1.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8/10.**

### 14 — Comparison Screen Contract
**Purpose:** Reason about relationships among already-named candidates; never search the catalog.
**Responsibilities:** Clean; the "Better vs. Recommended" distinction in Section 6 is precise and does real work preventing scope confusion with Recommendation.
**Boundary check:** Clean.
**Contradictions:** Same header/Section-9 mismatch as document 13. See Finding M1.
**Assumptions:** Section 11 honestly names the two-candidate limitation as unresolved. The severity of this gap is understated by its placement, however — see below.
**Hidden coupling:** The N>2 gap isn't confined to the deferrable Comparison Experience. Recommendation's own Section 6 ("multiple candidates remain but differ only on Soft Preferences") does not restrict itself to exactly two remaining candidates, meaning the same unresolved logic can surface inside Core V1 Recommendation the moment three or more candidates tie or trade off — not only inside the Important-Soon-After Comparison Experience the canon frames it under. See Finding M3.
**Missing dependencies:** Same as Finding M1.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8/10.**

### 15 — Price Verification Screen Contract
**Purpose:** Answer exactly one question — was the charged price correct — and nothing else.
**Responsibilities:** The tightest-scoped contract in the canon; the MUST NEVER list (no recommendation, ever, even after an overcharge) is unambiguous and consistently enforced elsewhere (ADR Section 3, Navigation Contract Section 10).
**Boundary check:** Clean.
**Contradictions:** This document explicitly corrects an earlier canonical claim from Experience Flows (Section 6's three-dimension confidence split versus document 09's "uniformly high"). Correcting a genuine oversimplification is good practice; leaving the corrected document unrevised is not. See Finding M4.
**Assumptions:** Section 11 honestly names the imprecise-charged-price gap.
**Hidden coupling:** None beyond the above.
**Missing dependencies:** Same header/Section-9 mismatch pattern as documents 13 and 14. See Finding M1.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8.5/10** — the self-correction is a real strength; the score reflects the citation gap and the un-reconciled upstream document, not the correction itself.

### 16 — Navigation Contract
**Purpose:** Every legal and illegal transition between the five contracted screens.
**Responsibilities:** Clean synthesis — correctly states it invents nothing, only consolidates what five separate contracts already established.
**Boundary check:** Clean, and this document is honest about its own incompleteness (Section 1 states plainly that two edges through Search/Browse Results can't be fully specified).
**Contradictions:** None substantive found. One formatting ambiguity: Section 3's Screen Graph line "C → PV · PV → C is **not** a direct edge" can be misread on first pass as declaring both directions non-edges; Sections 4 and 6 resolve it correctly (C → PV is a real edge; only PV → C is not), but a document whose entire purpose is removing ambiguity should not itself require cross-referencing to disambiguate its own graph notation. See Finding Mi3.
**Assumptions:** None beyond the SBR gap, already flagged.
**Hidden coupling:** None found beyond what's already known.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 8.5/10.**

### 17 — Canonical Interaction Lexicon
**Purpose:** One dictionary, one meaning per term, for every future implementer.
**Responsibilities:** Clean, and the Forbidden Synonyms section (Section 5) is a genuinely practical, specific piece of governance — "Suggest" vs "Recommend," "Score" being banned outright — this is exactly the kind of concrete guardrail that prevents drift in a real engineering org.
**Boundary check:** Clean.
**Contradictions:** None found.
**Assumptions:** None.
**Hidden coupling:** None.
**Missing dependencies:** None.
**Terminology:** This document *is* the terminology authority; no issues found in its own usage.
**Implementation leakage:** None.
**Quality score: 9/10.**

### 18 — Canonical Screen Specification Template
**Purpose:** The master template for turning a frozen Screen Contract into an implementer-facing specification.
**Responsibilities:** Correctly introduces no new authority; every field instruction points back to citation, never invention.
**Boundary check:** Clean, and appropriately restrained — Sections 11 and 12 are honest placeholders rather than invented accessibility/telemetry content.
**Contradictions:** None found.
**Assumptions:** None.
**Hidden coupling:** None.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None — correctly, since this document's whole job is to organize existing decisions, not add new ones.
**Quality score: 8.5/10** — untested rather than flawed: no actual screen specification has yet been produced from it, so its real-world usability under Finding M1's citation gaps (a template built on the assumption that "citation alone" fields are always fillable) hasn't been exercised.

### 19 — Architectural Decisions Record
**Purpose:** Explain *why* the boundaries fall where they do.
**Responsibilities:** Thorough and honest — correctly marks Search/Browse Results "Open," not "Accepted," resisting the temptation to smooth over its own biggest gap.
**Boundary check:** Clean.
**Contradictions:** None found in its own content, though its Section 3 entry on confidence collapse frames the Price Verification correction of document 09 as a pure virtue without noting that document 09 itself remains textually unrevised — a missed opportunity, since this document's entire purpose is to catch exactly this kind of residue. See Finding M4.
**Assumptions:** None beyond what's cited.
**Hidden coupling:** None found beyond what's already known.
**Missing dependencies:** None.
**Terminology:** Clean.
**Implementation leakage:** None.
**Quality score: 9/10.**

---

## 2. Cross-Cutting Architectural Review

**Internal consistency.** Strong overall, but not perfect — four real, checkable contradictions exist across nineteen documents (Section 4 below), concentrated exactly where the review guide suggested looking: in what a document claims about itself (headers vs. bodies) and in claims that quietly went stale as later documents refined them.

**Completeness.** The canon is honest about five open gaps, which is a genuine strength — most architecture documents this size pretend to completeness they don't have. But one of those five (Search/Browse Results) is under-rated in its own documentation. It's filed as "two incomplete navigation edges." It's actually the only resolution path for a capability Home's own contract promises, which makes it a blocker, not a footnote.

**Traceability.** Excellent in design, imperfect in execution. The citation discipline is real — but Finding M1 shows that by document 13, three documents in a row started claiming provenance in their headers that their own Dependencies sections didn't back up. This is worth taking seriously as a leading indicator: if drift appeared here, at nineteen documents, it will compound as the canon grows.

**Separation of concerns / single responsibility.** This is the canon's strongest property. The Owns/Does-Not-Own discipline in every Screen Contract, the six-layer Feature Inventory taxonomy, and the explicit "Better vs. Recommended" distinction in Comparison all hold up under adversarial reading. The guide's suggested failure mode — that Recommendation and Comparison's shared Trade-off/Tie-handling behavior might leak across their boundary — does not materialize; it's explicitly anticipated and correctly resolved in Feature Inventory Section 3.

**Document ordering / navigation between documents.** The dependency chain is genuinely linear, not circular — verified by tracing every "derived from N documents" header end to end. The one wrinkle is that the ordering discipline itself weakened slightly for the Screen Contracts (Finding M1) and for Recommendation Framework's missing provenance line (Finding Mi1).

**Behavioral determinism.** High for the paths the canon actually specifies — Recommendation Screen Contract Section 6 in particular is a model of testable, unambiguous rule-writing. It drops to genuinely non-deterministic the moment an implementation hits one of the five open gaps, or the occasion ambiguity, or Home's comparison-routing gap — at which point five different engineers would legitimately produce five different, individually defensible resolutions.

**Implementation readiness.** See Section 3 below — this is the most important open question in the whole review.

**Maintainability.** The cost is real, not theoretical, and Finding M1 is the proof: even during the initial production of this canon, citation discipline visibly slipped once the Screen Contracts started referencing each other. Nineteen documents is a lot to keep synchronized by hand, and the evidence suggests it's already starting to show.

**Scalability.** The domain model (SKU as atomic unit, Style Benchmark as reference distribution) scales cleanly with catalog size. The interaction model does not yet scale past two comparison candidates — a real, not hypothetical, constraint the moment someone compares three beers on a shelf. See Finding M3.

**Extensibility.** Genuinely well set up — Mechanisms are explicitly kept outside the canonical tier system, so new identification methods (a future barcode scanner, say) require zero canon changes. Future capability promotion is gated on evidence, not enthusiasm, and that gate is enforced consistently.

**Multi-engineer buildability.** See Section 3.

---

## 3. Implementation Readiness Assessment

**Acting as the Engineering Manager: could I confidently assign this repository to five independent senior engineers and expect them to build substantially the same application?**

**No — not with confidence, and not because the architecture is weak.** It's the opposite problem: this is one of the more rigorous specifications I've reviewed, which makes the gaps that do exist more consequential, not less, because engineers working from a document this precise will trust it completely — right up until they hit one of the places it genuinely doesn't have an answer.

Here's the concrete failure mode. The canon's own rule — stated repeatedly, and it's the right rule — is that a missing behavior is never invented at a lower layer; it's raised back against the document that should have specified it. That's correct discipline. But it only works if the gaps are rare and off the beaten path. They aren't:

- **Comparing three beers, not two,** is not an edge case in a beer-comparison product. It's one of the most obvious things a real user does the first week the app ships, and the tie-breaker and trade-off logic — the actual engine, not just the standalone Comparison screen — has no defined behavior past two candidates (Finding M3). Five engineers hit this in week one, not year one, and each will make a reasonable, different call.
- **A person who can't remember the exact price they were charged** ("around 110, not sure exactly") is an everyday occurrence for a Price Verification product, and the canon has no answer for it.
- **Whether "occasion" is even a real input in V1** is directly contradicted between two frozen documents (Finding M2). One engineer builds the progressive-question step for it; another doesn't. That's not a minor UI difference — it changes what data the Recommendation screen's state machine has to track.
- **A user who says "compare these two beers" while still at Home** has no defined path through the specification at all (Finding C1), because the screen meant to handle that hand-off has no contract, and Home's own interaction contract doesn't even recognize comparison as an expressible intent.

None of this is invented pessimism — every one of these is a documented gap or a documented contradiction, cited against the exact section it comes from, in Section 4 below. The point is narrower and more specific than "the architecture has gaps": it's that the gaps sit on the paths a real user takes constantly, not on the rare paths the canon's own risk language implies. The whole reason for fourteen-section Screen Contracts, per the ADR itself, was to buy away "silent behavioral drift between implementations." That bet has not yet been tested against real independent builders, and the four findings above are exactly where I'd expect that bet to fail first if it were tested today.

**What I would tell five engineers if forced to start now:** build everything that isn't touched by Section 4's Critical and Major findings — which is most of the product, and it's genuinely well-specified — and stop at each of those four boundaries for a real decision, not an improvised one. Shipping around those four points without resolving them first is how a five-engineer team quietly ships five different products wearing the same UI.

---

## 4. Findings

### Critical

**C1 — Home cannot deliver on a capability it is contractually required to promise.**
*Home Screen Contract, Section 11 (Failure Conditions) and Section 12 (Acceptance Criteria), in contradiction with Section 2 (MUST NEVER) and Section 7 (Interaction Contract).*
Home's Failure Conditions and Acceptance Criteria both require restating "the four supported capabilities — identify a beer, recommend a beer, verify a price, **compare beers**" to any out-of-scope user. But Section 2 forbids Home from transitioning directly to Comparison, and Section 7 defines exactly four recognized intent-expression triggers — Search/Browse, Recommendation intent, Verification intent, Planning/Proxy intent — none of which is a comparison intent. A person who hears "I can compare beers for you" and says "compare these two" has no defined next step in this contract. This also means the Search/Browse Results gap (already logged as "Open" in the ADR, and treated there as two merely-incomplete navigation edges) is load-bearing in a way the canon hasn't admitted: it's the only plausible resolution path for a promise Home itself makes, and even that resolution isn't defined in Home's own Interaction Contract. This should be resolved with the same explicit-decision discipline the canon already used for its five acknowledged gaps, and Search/Browse Results' priority should be raised accordingly.

### Major

**M1 — Screen Contract headers claim citations their own Dependencies sections don't contain.**
*Beer Detail Screen Contract (13), Comparison Screen Contract (14), Price Verification Screen Contract (15), each Section 9.*
Each document's header claims derivation from prior Screen Contracts ("plus the Home and Recommendation Screen Contracts," "plus the Home, Recommendation, and Beer Detail Screen Contracts," and so on) — but each document's own Section 9 Dependencies list cites only the ten foundational documents, never the prior Screen Contracts named in its own header. This is mechanically checkable and it's real: the citation trail these documents promise doesn't exist in their own bodies. It's a small thing individually, but it's the exact kind of drift the canon's own "no hidden assumptions introduced" validation checklists claim to catch, and it didn't catch this one, three documents in a row.

**M2 — Whether "occasion" is a live V1 input is contradicted across four documents.**
*Decision Engine Model (03), Section 4; Recommendation Framework (04), Section 2; Feature Inventory (07), Section 5; Recommendation Screen Contract (12), Section 2.*
The Decision Engine Model places occasion inside the actively-asked Progressive Question-Asking sequence (last in priority, but present). The Recommendation Framework lists it as a live Soft Preference tier member. The Feature Inventory then explicitly excludes occasion from Core V1's Preference Input Handling and defers it to Future. The Recommendation Screen Contract's own MUST list still requires the engine to never ask about occasion before budget and never withhold a recommendation for its absence — both of which presuppose it's a real, in-scope input. No document reconciles these. A charitable reading (occasion is accepted only if volunteered, never solicited) is plausible but never actually stated anywhere in the canon — and the canon's own habit of documenting exactly this kind of reconciliation elsewhere (see the Progressive-vs-Clarifying-Question ADR entry) makes its absence here notable, not incidental. This is the single most consequential finding in this review, because it changes what the Recommendation screen's state machine has to track in V1.

**M3 — The unresolved beyond-two-candidates gap is reachable from Core V1, not only from the deferrable Comparison Experience.**
*Comparison Screen Contract (14), Section 11; Recommendation Screen Contract (12), Section 6; Feature Inventory (07), Section 5.*
The canon frames the N>2 comparison gap as confined to the Important-Soon-After Comparison Experience, deferrable because "a person can approximate the same outcome by requesting Full Recommendation more than once" (ADR, Section 3). But Recommendation's own Section 6 threshold for "a recommendation exists" explicitly allows for multiple remaining candidates differing only on Soft Preferences — with no restriction to exactly two. The same unresolved tie-breaking and trade-off logic is therefore reachable from Core V1's own Recommendation flow the moment three or more candidates remain close, not only from the screen the canon has permission to defer.

**M4 — Experience Flows and Price Verification Screen Contract make different claims about the same behavior, and only one was ever corrected.**
*Experience Flows (09), Section 2 (Price Verification flow entry); Price Verification Screen Contract (15), Section 6.*
Document 09 states the Price Verification flow carries "the highest, most uniform Confidence Communication anywhere in the canon." Document 15 explicitly identifies this as an oversimplification and replaces it with three separate confidence dimensions, one of which is honestly capped below "uniformly high." Document 15 says so in its own text — this is a genuine, good-faith correction, not an oversight. But document 09 was never revised to match, leaving two frozen documents making literally different claims about the same flow, discoverable only by a reader who happens to reach document 15. This is a small, real breach of the canon's own stated principle that no document may reinterpret one frozen before it — worth a one-line amendment to document 09, cheaply fixed.

### Minor

**Mi1 — Recommendation Framework's header omits the provenance statement every other foundational document includes.** *Recommendation Framework (04), header.* Every other document in the ten-document foundation states "Derived entirely from the frozen [N documents]." Document 04 doesn't. Purely editorial, but breaks an otherwise-universal convention worth restoring for consistency.

**Mi2 — Fallback/substitute-suggestion and Proxy-Buying receive different treatment despite comparably thin evidence.** *Product Definition Document (02), Sections 6 and 9, against Behavioral Hypothesis Model (01), JTBD-4 and JTBD-5.* Both rest on Low-confidence, largely unobserved evidence. One is "deferred," the other "should probably never exist." The canon doesn't explain the asymmetry.

**Mi3 — An ambiguously formatted line in the Navigation Contract's own screen graph.** *Navigation Contract (16), Section 3.* "C → PV · PV → C is not a direct edge" can be misread on first pass; Sections 4 and 6 resolve it correctly, but a document whose stated purpose is removing ambiguity shouldn't need cross-referencing to disambiguate its own notation.

**Mi4 — Loose phrasing conflates display ownership with computation ownership for Alcohol-Adjusted Value.** *Information Architecture (08), Section 7.* Calls Beer Detail "the canonical home" for the figure; Content Architecture (10) correctly attributes the actual computation to a Platform Service. Not a functional bug — Beer Detail Screen Contract never claims to compute it — but loose enough to mislead a future implementer into wiring the computation into the wrong layer.

**Mi5 — Recommendation Screen Contract's Dependencies section omits Home Screen Contract.** *Recommendation Screen Contract (12), Section 9.* This screen receives Planning/Proxy mode flags originating at Home's hand-off, per Home's own Interaction Contract, but Home Screen Contract is never listed as a dependency.

### Future Consideration / Nice-to-Have

- Prioritize resolving the N>2 comparison gap and Home's comparison-intent routing gap ahead of the other three acknowledged open gaps, given Findings C1 and M3 show both are reachable from paths more common than the canon's current framing suggests.
- A lightweight, even scripted, citation-lint pass across every document's header claims versus its own Section 9 Dependencies list — Finding M1 shows this has already drifted once, at only nineteen documents; it will be cheaper to catch now than after further growth.
- Reconsider whether the volume of Proxy-Buying documentation (full interaction flows, screen states, and explicit Screen Contract clauses across six-plus documents) is proportionate to its status as an explicitly deferred, Low-confidence, Future-tier capability — a documentation-investment question, not a behavioral one, and not urgent.
- A one-line amendment to Experience Flows (09) pointing forward to Price Verification Screen Contract (15)'s refinement would resolve Finding M4 cheaply, without reopening either document's substance.

---

## Closing Summary

This is a well-built architecture, and it should be evaluated as one — the failure modes the Review Guide asked reviewers to hunt for (hidden coupling, circular dependency, feature creep, leaky abstraction) mostly do not materialize on close inspection, and where they were a real risk, the canon had already caught and resolved them itself. That's a genuinely high bar, and it's cleared more often than not.

But "mostly consistent" is not the same claim as "implementation-ready," and the gap between those two is exactly Section 4 above: one internal contradiction serious enough to block a documented user-facing promise, and three cross-document contradictions concentrated on the paths real users will actually take in the first week of use. None of these require redesigning anything — each is fixable with the same tool the canon already uses successfully five times over: a named, explicit decision, recorded the way the ADR records everything else. The architecture doesn't need to change. Four specific gaps in it do need to close before five engineers can be trusted to close them identically on their own.
