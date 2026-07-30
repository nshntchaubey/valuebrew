# ValueBrew — Canonical Architectural Decisions Record (ADR)
### Records why the architecture is shaped the way it is. Introduces zero new behavior, zero new requirements, zero implementation. Every entry traces to one or more of the twenty documents already frozen.

---

## 1. Purpose

Twenty documents establish *what* ValueBrew is and *how* it behaves. None of them, individually, explains *why* the boundaries fall where they do — why Comparison can't simply be folded into Recommendation, why Price Verification never escalates, why a whole screen was left uncontracted. This document exists so that a future reviewer, designer, engineer, or AI system can ask "why is it built this way" and get a real answer, sourced from decisions that were actually made, not reconstructed after the fact.

---

## 2. Decision-Making Philosophy

**Single Responsibility.** Every screen's Owns/Does Not Own split, and every document's own stated scope, exists because responsibility was repeatedly narrowed rather than left to overlap — demonstrated most clearly in the Feature Inventory's layer taxonomy and every Screen Contract's Section 2.

**Separation of Concerns.** Recommendation, Comparison, Verification, and Detail were kept as four distinct reasoning operations rather than one general-purpose screen, and the Decision Engine Model, Recommendation Framework, and Beer Knowledge Model were kept as three separate documents rather than one, even though they interlock constantly.

**Progressive Disclosure.** Demonstrated directly in the Decision Engine Model's discipline of asking only questions that change the outcome, and in the Content Architecture's rule that information appears only when it's needed, not by default.

**Explicit Ownership.** Every piece of information in the Content Architecture and Information Architecture has exactly one canonical home; every Feature in the Feature Inventory has exactly one owning Module.

**Explainability.** Demonstrated by the Recommendation Framework's mandatory, immediate Explanation requirement, applied without exception across every Screen Contract.

**Traceability.** Every one of the twenty prior documents ends with a Validation section requiring every claim to trace to something already established — this document is itself built under that same requirement.

**Evidence over intuition.** Demonstrated most explicitly in the Behavioral Hypothesis Model's Evidence/Inference/Hypothesis/Assumption labeling discipline, carried forward into every architectural document's insistence on citation over invention.

**Session-first architecture.** Demonstrated by the Product Definition Document's rejection of accounts, and by the Beer Knowledge Model's classification of Preference Summary and Observed Price as transient, never persisted.

**Minimal assumptions.** Demonstrated by the repeated policy, across all five Screen Contracts, of flagging a genuine ambiguity rather than inventing a resolution for it.

**Additional principles, demonstrated but not named in the original list:**

**Graceful degradation under uncertainty** — Low-Confidence Response exists specifically so the product never fakes certainty it doesn't have, rather than blocking outright.

**Non-destructive recovery** — every Recovery Flow preserves established progress by default; restarting from nothing is treated as the exception, not the norm.

**Terminological discipline** — the existence of the Canonical Interaction Lexicon as its own document, specifically to catch and correct drifted wording before it spreads.

**Layered, non-contradictory authority** — every document explicitly forbids reinterpreting the ones frozen before it, creating a strict, checkable hierarchy rather than a set of documents that could quietly disagree with each other.

---

## 3. Major Architectural Decisions

**Decision: Recommendation and Comparison remain separate Experiences.**
Status: Accepted.
Context: both reason about which SKU is preferable, and both draw on the same underlying Trade-off/Tie-handling Engine Behavior, making a merge tempting on the surface.
Decision Made: Recommendation searches the entire catalog from a preference profile; Comparison only ever reasons about candidates it was explicitly handed, never searching.
Alternatives Considered: the Feature Inventory's own MVP classification review explicitly asked whether a dedicated Comparison destination was needed at all, noting a person could approximate the same outcome by requesting Full Recommendation repeatedly — this alternative was rejected in favor of keeping the underlying behavior Core while treating the dedicated destination as a later, Important-Soon-After addition.
Consequences: "better" (bounded, dimension-scoped) and "recommended" (catalog-wide) remain distinct claims that can never be confused for each other.
Affected Canonical Documents: Feature Inventory, Recommendation Framework, Recommendation Screen Contract, Comparison Screen Contract.

**Decision: Beer Detail never recommends.**
Status: Accepted.
Context: Beer Detail needs to show value standing, which requires some judgment-adjacent computation — the Confirm-as-Is outcome.
Decision Made: Confirm-as-Is is classified as a Feature belonging to Recommendation Module's logic, surfaced on Beer Detail, never an independent recommendation capability belonging to Beer Detail itself.
Alternatives Considered: an earlier draft of the Feature Inventory gave Confirm-as-Is its own independent entry point, as though it were a standalone Experience; this was explicitly corrected once the layer-consistency pass identified it as a Feature, not an Experience.
Consequences: Beer Detail's confidence profile stays uniformly high, since no Soft-preference content ever appears there — a clean, distinguishing property of that screen alone.
Affected Canonical Documents: Feature Inventory, Beer Detail Screen Contract, Information Architecture.

**Decision: Price Verification is isolated and never escalates.**
Status: Accepted.
Context: an earlier strategic pass (the Behavioral Hypothesis Model's opportunity ranking) treated price fairness as a candidate for the product's entire founding identity, before a later, explicit founder decision broadened the core purpose to a fuller decision engine.
Decision Made: Price Verification remains its own bounded screen regardless of that broadening — it never recommends an alternative or opens a comparison on its own initiative, even following an overcharge finding.
Alternatives Considered: the founder's own strategic override explicitly weighed narrowing the whole product around Price Verification versus broadening it into the current decision-engine framing, and chose the latter while still preserving this screen's bounded behavior intact.
Consequences: an overcharge finding is never diluted by an unprompted upsell, preserving trust in the single highest-confidence claim anywhere in the canon.
Affected Canonical Documents: Behavioral Hypothesis Model, Product Definition Document, Price Verification Screen Contract.

**Decision: Home owns routing, and nothing else.**
Status: Accepted.
Context: every other screen assumes something specific is already known; Home is the only point where nothing is.
Decision Made: Home captures intent and routes it, performing no Experience-level reasoning of its own.
Alternatives Considered: the Home Screen Contract itself states directly that merging Home into any single destination screen would force a premature commitment to one Experience before the person has expressed which one they want.
Consequences: Home never reaches Decision Complete, and is never a legitimate backward-navigation destination from any other screen.
Affected Canonical Documents: Home Screen Contract, Information Architecture, Navigation Contract.

**Decision: Search/Browse Results has no Screen Contract.**
Status: **Open — this is a documented gap, not a settled decision, and should not be read as equivalent to the entries above.**
Context: the Information Architecture names six screens; only five received individual Screen Contracts.
Decision Made: none — this reflects a sequencing gap in how the canon was built, flagged explicitly in the Navigation Contract rather than resolved there.
Alternatives Considered: not applicable — nothing was weighed and rejected here; the gap was simply never closed.
Consequences: two edges in the Navigation Contract's graph — Home to Beer Detail, Home to Comparison — cannot be fully specified until this is resolved.
Affected Canonical Documents: Information Architecture, Navigation Contract.

**Decision: Preference Summary is session-only.**
Status: Accepted.
Context: the Product Definition Document rejects accounts and persistent profiles as part of the product's founding identity.
Decision Made: Preference Summary exists only for the duration of one interaction and is never carried into a future session.
Alternatives Considered: the Feature Inventory and Product Definition Document both explicitly frame future personalization as *deferred*, not permanently rejected — meaning persistence was a considered future possibility, consciously not adopted now.
Consequences: no cross-session personalization exists anywhere in the current canon; every interaction begins fresh.
Affected Canonical Documents: Product Definition Document, Beer Knowledge Model, Content Architecture, Decision Engine Model.

**Decision: Recommendation alone owns full Progressive Question-Asking.**
Status: Accepted.
Context: Comparison's own composition also permits "at most one clarifying question," which could be misread as a second instance of the same mechanism.
Decision Made: the Recommendation Screen Contract explicitly distinguishes the two — Comparison's bounded, single-question exception is not the same behavior as Recommendation's full, iterative, evidence-ordered process.
Alternatives Considered: treating both as the same underlying mechanism was the natural first reading, and was explicitly corrected once the distinction was drawn out.
Consequences: Comparison stays fast and narrow; the cost of full multi-step gathering belongs to Recommendation alone.
Affected Canonical Documents: Decision Engine Model, Recommendation Screen Contract, Comparison Screen Contract, Canonical Interaction Lexicon.

**Decision: Comparison asks at most one Clarifying Question.**
Status: Accepted.
Context: Comparison already has named candidates in hand, unlike Recommendation, which starts from nothing.
Decision Made: capped at exactly one question, since the search space is already bounded.
Alternatives Considered: not separately documented beyond the general reasoning in the preceding entry.
Consequences: if one question doesn't resolve the comparison, the honest response is a Trade-off or a Tie, never further probing.
Affected Canonical Documents: Content Architecture, Comparison Screen Contract.

**Decision: Ties are accepted as legitimate, complete outcomes.**
Status: Accepted.
Context: forcing a decision where none is warranted misrepresents what the product actually knows.
Decision Made: a Tie Disclosure is a complete answer, never a failure state and never replaced with an arbitrary pick.
Alternatives Considered: the Recommendation Framework's own Section 5 explicitly weighs and rejects forcing an arbitrary tiebreak when options are genuinely equivalent.
Consequences: trust is preserved even when the product has no confident single answer, and this shapes the explicit Recovery-versus-Tie distinction carried through to the Lexicon.
Affected Canonical Documents: Recommendation Framework, Experience Flows, Comparison Screen Contract, Canonical Interaction Lexicon.

**Decision: Confidence is never collapsed into a single figure.**
Status: Accepted.
Context: the Beer Knowledge Model's three-tier fact classification would be meaningless if every output blended the tiers together.
Decision Made: high- and low-confidence content must always remain visibly separated, however inconvenient that is for a simple display.
Alternatives Considered: the Price Verification Screen Contract explicitly identifies and corrects an earlier, looser "uniformly high confidence" characterization, splitting it into three distinct, honestly-scoped dimensions — a real, documented instance of rejecting an oversimplification once it was examined closely.
Consequences: a single wrong recommendation doesn't collapse trust in the whole system, since the specific uncertain input remains visible and disputable.
Affected Canonical Documents: Beer Knowledge Model, Recommendation Framework, Decision Engine Model, Price Verification Screen Contract.

**Decision: Explanation always accompanies Recommendation.**
Status: Accepted.
Context: a recommendation with no visible reasoning reads as unreliable the first time it's ever wrong.
Decision Made: Explanation is mandatory and immediate, never deferred to a separate request.
Alternatives Considered: not separately documented as a rejected alternative beyond the principle's repeated, unqualified statement across every relevant document.
Consequences: a wrong recommendation becomes a specific, disputable data point rather than a reason to distrust the whole system.
Affected Canonical Documents: Recommendation Framework, Decision Engine Model, all five Screen Contracts.

**Decision: Observed Price is transient.**
Status: Accepted.
Context: it is user-reported, tied to one transaction, and not independently verifiable.
Decision Made: never persisted, never displayed outside Price Verification, never merged into catalog knowledge.
Alternatives Considered: the Beer Knowledge Model's own Section 7 explicitly names a crowd-verified price ledger as something that "may be added later, if a lightweight feedback mechanism is ever built" — a real, considered future possibility, deliberately not adopted into the current architecture.
Consequences: V1 stays simple, and no unearned trust infrastructure is built ahead of real usage evidence justifying it.
Affected Canonical Documents: Beer Knowledge Model, Price Verification Screen Contract.

**Decision: No accounts exist.**
Status: Accepted.
Context: the product's Core V1 scope doesn't require cross-session personalization to fulfill its stated purpose.
Decision Made: no login, no persistent profile, no cross-session storage of anything a person states.
Alternatives Considered: both the Product Definition Document and Feature Inventory frame lightweight future personalization as explicitly deferred, not rejected outright — the alternative was considered and consciously postponed, not foreclosed.
Consequences: every Screen Contract inherits this as a hard constraint, and Navigation never treats any screen as account-gated.
Affected Canonical Documents: Product Definition Document, Beer Knowledge Model, all five Screen Contracts, Navigation Contract.

**Decision: Product mechanisms are intentionally unconstrained.**
Status: Accepted.
Context: an early Feature Inventory draft excluded Barcode Scan as a capability, holding it to the same evidence bar as a canonical capability rather than treating it as an implementation choice.
Decision Made: mechanisms — search, browse, a future scan — are never canonically mandated or excluded; only capabilities require canonical evidence.
Alternatives Considered: the Feature Inventory's own refinement pass explicitly identifies and reverses the earlier, over-conservative treatment.
Consequences: new identification mechanisms can be added or swapped freely without requiring any change to the canon, as long as they serve an already-named capability.
Affected Canonical Documents: Feature Inventory, Canonical Interaction Lexicon.

**Decision: Every screen has a bounded, non-overlapping responsibility.**
Status: Accepted.
Context: several screens plausibly touch the same underlying question — Beer Detail and Recommendation both bear on "is this a good choice"; Comparison and Recommendation both bear on "which is better."
Decision Made: every Screen Contract states both what it owns and what it explicitly never owns, and no responsibility appears in two places at once.
Alternatives Considered: the Feature Inventory's layer-consistency refinement explicitly corrects earlier drafts that blurred exactly this boundary — Confirm-as-Is briefly having its own entry point, Trade-off/Tie-handling being conflated between the Comparison Experience and the underlying Engine Behavior.
Consequences: any new feature can be checked against exactly one screen's ownership, with no ambiguous overlap to resolve.
Affected Canonical Documents: every Screen Contract, Information Architecture, Feature Inventory.

**Decision: Navigation owns transitions, not individual screens.**
Status: Accepted.
Context: five Screen Contracts each independently described their own transitions, risking drift between, for instance, Beer Detail's account of a hand-off to Comparison and Comparison's account of that same hand-off.
Decision Made: the Navigation Contract exists as the single synthesized source of truth for every transition, superseding any individual screen's own restatement of it.
Alternatives Considered: the alternative — leaving transition logic distributed across five separate documents — is precisely the state that existed before the Navigation Contract was created; producing it was itself the explicit decision to consolidate.
Consequences: the whole transition graph can be validated once for internal consistency, rather than requiring five documents to be manually cross-checked against each other.
Affected Canonical Documents: Navigation Contract, all five Screen Contracts.

---

## 4. Architectural Trade-offs

**More documents versus cleaner ownership.** Twenty-one separate documents were produced rather than one large one, because every attempt to collapse layers together (seen directly in the Feature Inventory's own refinement history) produced exactly the kind of ownership confusion the later, more granular structure eliminated. The cost is real: more documents to keep consistent. The alternative's cost, demonstrated concretely by the Feature Inventory's own early drafts, was worse — ownership that couldn't be checked at all.

**More explicit contracts versus higher documentation overhead.** Each Screen Contract runs to fourteen sections, considerably more than a typical UI spec would carry. This was accepted deliberately so that "two independent designers would produce nearly identical wireframes" from the contract alone — the overhead buys away a specific, named risk: silent behavioral drift between implementations of the same screen.

**Behavior-first versus UI-first.** Every architectural document through the Navigation Contract was built with an explicit prohibition on discussing layout, color, typography, or components. This was a deliberate sequencing choice, not an oversight — behavior was locked down first so that UI design, whenever it begins, has nothing left to accidentally decide on its own.

**Explainability versus speed.** Mandatory, immediate Explanation on every recommendation, verification, and comparison result adds a real cost — more to compute, more to display, more for a person to read past before reaching an answer. This was accepted because the alternative, demonstrated by the confidence-collapse decision in Section 3, produces a system that looks faster but is less trustworthy the first time it's wrong.

**Confidence honesty versus display simplicity.** A single blended score would be materially simpler to show than three separately labeled confidence tiers. This was rejected in favor of honesty about what's actually known, even at the cost of a more complex output.

---

## 5. Rejected Alternatives

**Monolithic screen ownership** — one general-purpose screen handling search, recommendation, comparison, and verification together — was rejected in favor of five bounded screens, each with an explicit Does-Not-Own list.

**A universal recommendation engine** that always tries to produce a single best answer, regardless of how much is actually known, was rejected in favor of Low-Confidence Response and honest Trade-off/Tie outcomes.

**Persistent user profiles** were rejected for the current architecture, per the Product Definition Document, though explicitly left open as a future possibility rather than permanently foreclosed.

**Implicit or automatic navigation** — a screen transitioning without an explicit trigger — was rejected throughout; every transition in the Navigation Contract traces to a stated user action or a defined system completion.

**Automatic escalation** — Price Verification pivoting into Recommendation or Comparison on its own following a discrepancy — was explicitly rejected in that screen's own Constraints.

**Score-based recommendation** — collapsing a beer's suitability into one numeric figure — was rejected throughout, most explicitly in the Beer Knowledge Model's exclusion of any such score and the Recommendation Framework's ban on blended confidence.

**Inferring unstated preferences from behavior or context** was rejected for the current architecture; every Constraint must be explicitly stated, never guessed at, until real usage evidence someday justifies otherwise.

---

## 6. Guiding Rules

**Never invent behavior at lower layers.** Demonstrated by every Screen Contract's insistence that a missing rule is a gap to flag against the Screen Contract, never something to resolve locally.

**Behavior precedes implementation.** Demonstrated by the entire document sequence — Screen Contracts, the Navigation Contract, and the Canonical Interaction Lexicon were all completed before the Screen Specification Template, the first implementation-facing artifact, was created.

**Ownership is explicit.** Demonstrated throughout the Information Architecture and every Screen Contract's Owns/Does-Not-Own structure.

**Recovery preserves progress.** Demonstrated across every Recovery Flow in Experience Flows and every Screen Contract's own Failure Conditions section.

**Navigation never reasons.** Demonstrated by the Navigation Contract's own Section 2 — a transition carries context between screens that reason; it never reasons itself.

**Facts and Preferences never merge.** Demonstrated by the Beer Knowledge Model's strict separation of catalog knowledge from user-stated Constraints, and the Recommendation Framework's constraint tiers.

**Explanation and Confidence remain separate.** Demonstrated repeatedly — Explanation states why, Confidence states how sure, and no document ever merges the two into one statement.

**Every gap is named, never silently resolved.** Demonstrated by the explicit Open Gap Policy carried through all five Screen Contracts and into the Navigation Contract — five distinct, unresolved ambiguities exist in the canon today, and every one of them was surfaced rather than quietly assumed away.

---

## 7. Known Limitations

**Search/Browse Results remains uncontracted** — no Screen Contract exists for it, leaving two edges in the Navigation Contract's graph incompletely specified. The single most structurally significant open item in the canon, since it's the only gap that leaves an already-frozen document formally incomplete rather than merely pending a future decision.

**Approximate or imprecise charged-price handling is unresolved** — nothing in the canon specifies whether Price Verification should require an exact figure or accommodate a range.

**The rule determining whether an Anchor Situation applies on Beer Detail is unresolved** — entry context is stated to determine this, but no document specifies the actual determining signal.

**Ambiguous preference-type statements on Recommendation are unresolved** — nothing specifies how to handle an input that could plausibly be more than one preference type at once.

**Comparison logic beyond two candidates is unresolved** — every worked example of tie-breaking and trade-off reasoning in the canon assumes exactly two candidates; three-or-more, and particularly non-transitive results, are unaddressed.

**A future accessibility standard is deferred**, per the Screen Specification Template's own placeholder section.

**Telemetry is deferred**, per the same template, pending a dedicated analytics framework.

**No implementation guidance exists yet** — the canon, through the Screen Specification Template, remains entirely behavior-first; no code, framework, or technical architecture has been decided.

---

## 8. Future Evolution

Every prior document's own Future Compatibility or Future Extensions section already establishes the same underlying pattern, restated here once, generally: new capabilities may be added only once real usage evidence justifies them, never on internal enthusiasm alone. New behavior must always be introduced at the correct layer — a new Engine Behavior belongs in the Decision Engine Model or Recommendation Framework, never invented inside a Screen Contract or specification. Any resolution of the five open gaps in Section 7 must itself be recorded as a new entry in this ADR, with its own Context, Decision Made, and Consequences, rather than silently folded into whichever document it touches. The architecture is expected to grow outward — new screens, new Modules, eventually new capabilities — but never to grow by quietly reinterpreting a decision already recorded here as Accepted.

---

## 9. Validation

Every decision recorded in Section 3 traces to at least one specific canonical document named in its Affected Canonical Documents field. Every Alternative Considered is either drawn from an explicit statement already present in the canon or, where no such statement exists, the field says so rather than inventing one. The one decision marked Open rather than Accepted — Search/Browse Results — is presented honestly as an unresolved gap, not smoothed into the appearance of a settled choice. No new rationale was invented anywhere in this document that could not be traced back to something the canon already states.
