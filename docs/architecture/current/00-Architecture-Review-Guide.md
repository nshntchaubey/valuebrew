# ValueBrew — Canonical Architecture Review Guide
### Written for external reviewers. Introduces no new behavior, no new implementation, no new architecture. Every statement below traces to a document already frozen in the canon. This is not a defense of the architecture — it is a framework for critically evaluating it.

---

## 1. Purpose

This guide exists to make an external review of the ValueBrew canon possible without requiring the reviewer to reconstruct, from nineteen separate documents, what's actually being asked of them. It answers five practical questions before the review begins: what is this canon, in what order should it be read, what is it already committed to, what should a reviewer actively try to break, and how should findings be reported back.

It is deliberately not a summary of the architecture's merits. A summary written by the same process that produced the architecture would be structurally biased toward defending it. This document instead orients the reviewer toward the canon's own stated trade-offs, its own admitted gaps, and its own rejected alternatives — all of which are already on the record — so that the review starts from what the canon says about itself, not from a pitch.

---

## 2. Scope

**In scope for this review:**
Product architecture and behavior · ownership boundaries between screens, Modules, and Experiences · the Decision Engine's reasoning rules · navigation and state transitions · what each screen is responsible for and explicitly is not · the information model (what data exists, who owns it, how long it lives) · the reasoning model (Hard/Strong/Soft constraint tiers, tie-breaking, confidence) · the interaction model (states, recovery, completion) · canonical terminology and whether it's used consistently.

**Explicitly out of scope for this review:**
Visual design, wireframes, layout, typography, color, animation · any specific implementation, codebase, or technology stack · frontend or backend framework choices · database or infrastructure design · accessibility and telemetry specifics (the canon itself defers these — see Section 9).

This split is not arbitrary — it's the canon's own, stated as a deliberate sequencing decision: every architectural document through the Navigation Contract was built under an explicit prohibition on discussing layout, color, typography, or components, so that behavior would be locked down before UI design has anything left to accidentally decide on its own. Reviewing UI questions against this canon is reviewing something it never claimed to answer.

**A scope clarification worth stating plainly, since it affects what "the canon" actually means:** the frozen set is nineteen documents, not the nineteen named in the original review request. Two corrections, made here for accuracy rather than left silent:

- **"Platform Services" is not a standalone document.** It's a layer in the Feature Inventory's own abstraction taxonomy (Module, Experience, Feature, Engine Behavior, Platform Service, Mechanism), populated by items like the Beer Knowledge Base/Catalog and State & Flow Management. It's real and reviewable, but reviewers should look for it inside the Feature Inventory, not as a nineteenth document alongside it.
- **The Behavioral Hypothesis Model is a standalone frozen document** — the secondary-research foundation everything else is evidenced against — and belongs in the set even though it wasn't named in the original list. It's the single most load-bearing document for judging whether any capability is actually justified, since it's where the canon's Evidence/Inference/Hypothesis/Assumption labeling discipline originates.

The nineteen actual documents: Behavioral Hypothesis Model, Product Definition Document, Decision Engine Model, Recommendation Framework, Beer Knowledge Model, User Interaction Model, Feature Inventory, Information Architecture, Experience Flows, Content Architecture, five Screen Contracts (Home, Recommendation, Beer Detail, Comparison, Price Verification), Navigation Contract, Canonical Interaction Lexicon, Canonical Screen Specification Template, and this Architectural Decisions Record.

---

## 3. Reading Order

Recommended sequence, with the reasoning for each step:

1. **Behavioral Hypothesis Model** — read first because everything downstream claims to be evidenced against it. Its Evidence/Inference/Hypothesis/Assumption labels are the yardstick every later confidence claim should be checked against.
2. **Product Definition Document** — the founding commitments (no accounts, no fallback/substitute suggestions, the four supported capabilities) that every later document treats as fixed.
3. **Decision Engine Model** and **Recommendation Framework** — the reasoning rules (constraint tiers, tie-breaking, confidence separation) that every screen later operationalizes.
4. **Beer Knowledge Model** — the domain and data model these reasoning rules actually run against.
5. **User Interaction Model** — how a person engages with all of the above across any interface, independent of screens.
6. **Feature Inventory** — the first document to state, by its own header, that it must remain re-derivable from the six documents above alone. It's the classification layer (Core / Important Soon After / Future / Out of Scope) everything else inherits.
7. **Information Architecture** — states by its own header that it's derived from the seven documents above; this is where screens first get named.
8. **Experience Flows** — states it's derived from the eight documents above; this is where named screens become end-to-end journeys.
9. **Content Architecture** — states it's derived from the nine documents above; this is where journeys become what's actually displayed, and in what order.
10. **The five Screen Contracts** (Home, Recommendation, Beer Detail, Comparison, Price Verification) — each states it's derived from the ten documents above (1–9 plus itself building on the others), with Beer Detail and Comparison explicitly also citing the Screen Contracts written before them.
11. **Navigation Contract** — states it's derived from the ten documents plus all five Screen Contracts; read last among the behavioral documents because it depends on every one of them.
12. **Canonical Interaction Lexicon** — a cross-cutting glossary citing terms back to their first canonical source across everything above; useful earlier as a reference, but its own citations only make sense once the source documents are known.
13. **Canonical Screen Specification Template** — the one implementation-facing document in the set, explicitly built last in sequence, after every behavioral document and the Lexicon existed to cite.
14. **Architectural Decisions Record (this document's own companion)** — read last. It doesn't establish new behavior; it explains *why* the boundaries above fall where they do, and is only meaningful once the boundaries themselves are already familiar.

The rationale for this order isn't stylistic — it's the literal dependency chain each document declares about itself in its own header. Reading out of this order means reading a document's stated citations before you've seen what they refer to.

---

## 4. Architectural Principles

The full elaboration lives in the ADR, Section 2 — this guide references it rather than restating it. The recurring principles a reviewer will see demonstrated repeatedly, not just asserted once:

Single Responsibility · Separation of Concerns · Progressive Disclosure · Explicit Ownership · Explainability · Traceability · Evidence over intuition · Session-first architecture (no accounts, no persistent profiles) · Minimal assumptions (ambiguity is flagged, never silently resolved) · graceful degradation under uncertainty · non-destructive recovery · terminological discipline · layered, non-contradictory authority (no document may reinterpret one frozen before it).

A reviewer's job is not to confirm these principles are named — they clearly are. It's to test whether they actually hold under pressure, which is what Sections 5 and 6 below are for.

---

## 5. Questions Reviewers Should Ask

**Product**
- Does the Product Definition Document's rejection of accounts and Fallback/substitute-suggestion still hold given how the product has to behave when Legal Price Verification alone finds an overcharge? Is "never recommend an alternative, ever, even here" actually the right line, or a line that was easy to state before a hard case existed?
- Is "value for money" — the model's own single most important negative finding, per the Behavioral Hypothesis Model — solid enough ground to build a whole product's core purpose on?

**Architecture**
- Does Recommendation-versus-Comparison actually stay distinct in practice, or does a person asked to "compare" two beers they found via search implicitly want catalog-wide reasoning anyway?
- Is Search/Browse Results' missing Screen Contract (Section 9) a genuine sequencing gap, or a sign that a sixth screen was quietly avoided because it didn't fit the five-screen story cleanly?

**UX**
- Home routes to exactly three destinations and never becomes a back-navigation target. Does that actually match how people expect to move backward through a shopping decision, or is it an architecturally clean rule imposed on a messier real behavior?
- Every recommendation, verification, and comparison carries mandatory, immediate Explanation. Does that serve every real interaction, or does it add friction in the cases — Journey 2's "keep the current choice," for instance — where a person wanted a fast, low-friction confirmation and got a paragraph of reasoning instead?

**Engineering**
- The Screen Specification Template requires every field to trace to a citation, with no invention permitted at that layer. What happens the first time an implementer hits a case the citation genuinely doesn't cover — does the process actually stop and escalate, or does it get quietly filled in?

**Scalability**
- Comparison's own logic is explicitly unaddressed beyond two candidates (Section 9). Is this a minor gap, or does it block the Comparison Experience from being usable the moment a person tries to compare three real options?

**Maintainability**
- Twenty-one documents (per the ADR's own count) is a real ongoing cost to keep mutually consistent. Has that cost actually been tested — for example, by deliberately trying to update one document and seeing how many others required a matching edit?

**Complexity**
- Fourteen-section Screen Contracts were justified as buying away "silent behavioral drift between implementations." Has that specific claim — two independent designers producing nearly identical wireframes from the contract alone — actually been tested against real designers, or only asserted?

**Commercial viability**
- Confidence honesty was chosen over a single blended score "even at the cost of a more complex output." Does a first-time user actually tolerate three separately labeled confidence tiers, or does this trade-off assume a more patient user than will actually show up?

**Future extensibility**
- The canon states new capabilities require real usage evidence before promotion from Future to Core. What's the actual mechanism for gathering that evidence, given the product itself rejects persistent user data?

**Explainability**
- Recommendation Explanation is reused verbatim on Beer Detail for Confirm-as-Is. Does the same explanation structure actually make sense for "here's why I recommend this" and "here's why your existing choice is fine," or were these forced into one template because the canon prefers not inventing a second one?

**Documentation quality**
- The canon's own headers self-report an incrementing document count (six, seven, eight, nine, ten "frozen documents") that a reviewer can actually check against the reading order in Section 3. Does that count hold up cleanly end to end, or does it drift anywhere?

---

## 6. Common Failure Modes

Reviewers should actively search for these, using the specific tensions the canon itself already surfaces as the starting point, not a generic checklist:

- **Over-engineering.** The ADR names this cost directly: fourteen-section Screen Contracts, twenty-one total documents. Worth testing whether the overhead the ADR claims it buys is real or assumed.
- **Hidden coupling.** Recommendation and Comparison share the same underlying Trade-off/Tie-handling Engine Behavior while being kept as separate Experiences — check whether that separation is actually clean in the Navigation Contract's graph, or whether the shared behavior leaks assumptions across the boundary.
- **Duplicate ownership.** The canon claims every information object has exactly one home (Information Architecture Section 7). Spot-check a few — Alcohol-Adjusted Value, for instance, appears on Beer Detail, Comparison, and Recommendation — and confirm it's genuinely referenced, never recomputed independently in more than one place.
- **Leaky abstraction.** Confirm-as-Is is classified as a Feature belonging to the Recommendation Module's logic, merely surfaced on Beer Detail. Check whether Beer Detail's own contract actually respects that, or whether it's quietly doing judgment work of its own.
- **Circular dependency.** Trace the "derived from N frozen documents" chain in Section 3 end to end — a genuine circular reference would be a real find, not a stylistic complaint.
- **State explosion.** Five known open gaps (Section 9) is a low number today; check whether resolving any one of them (especially Comparison beyond two candidates) would multiply the state machine in a way the current Screen Contracts aren't built to absorb.
- **Implicit behavior.** The canon insists every transition traces to an explicit trigger. Test the two paths that pass through the uncontracted Search/Browse Results screen (Section 9) specifically — this is exactly where an implicit transition is most likely to have crept in, since no contract governs it yet.
- **Contradictions.** Cross-check the self-reported document counts in the headers (Section 3) for internal consistency — this is a mechanically verifiable thing to check, not a judgment call.
- **Excessive documentation.** Already named as a trade-off by the ADR itself; the question isn't whether it's true, but whether it was worth it.
- **Feature creep.** Check every "Future" and "Important Soon After" item in the Feature Inventory against the Behavioral Hypothesis Model's actual evidence — the canon claims strict evidence gating, so this is checkable, not just askable.
- **Premature abstraction.** Contextual Signals exists as a Recommendation Framework constraint tier that's "currently empty in practice" by its own admission — worth asking whether it should exist in the model at all before any evidence justifies it.

---

## 7. Feedback Classification

- **Critical** — violates a stated MUST NEVER in a Screen Contract, or reopens a foundational commitment (accounts, persistent profiles, Fallback/substitute-suggestion) the Product Definition Document explicitly rejected.
- **Major** — doesn't break an explicit rule, but exposes a real problem inside one of the five documented Known Limitations (Section 9), or a genuine gap the canon hasn't yet admitted to.
- **Minor** — a real inconsistency, but narrow in effect — for instance, a term used slightly differently than the Canonical Interaction Lexicon defines it, without changing any actual behavior.
- **Editorial** — formatting, section count, phrasing clarity — doesn't touch behavior or ownership at all.
- **Future Consideration** — matches something the canon already places in "Important Soon After" or "Future" in the Feature Inventory; worth logging, not worth blocking on.
- **Out of Scope** — visual design, implementation, or technology-stack feedback, per Section 2 above.

---

## 8. Review Rules

Reviewers should: challenge assumptions rather than accept them because they're written down confidently. Prefer simpler architectures where a simpler one would serve the same evidenced need. Point out unnecessary abstractions — a layer that exists but adds no checkable value. Question document boundaries — just because two concerns were split into separate documents doesn't mean the split was correct. Identify missing capabilities the evidence actually supports but the canon doesn't yet serve. Attack scalability, usability, maintainability, and commercial viability directly, using the questions in Section 5 as a starting point, not a ceiling.

Never preserve the architecture simply because it already exists, is internally consistent, or was arrived at carefully. Internal consistency is necessary but not sufficient — a self-consistent architecture can still be wrong about what it should be building.

---

## 9. Known Open Questions

These are the gaps the canon has already surfaced against itself. Reviewers should treat these as the starting list, not invent new ones without first confirming they aren't already covered here:

1. **Search/Browse Results has no Screen Contract.** The single most structurally significant open item — it leaves two edges in the Navigation Contract's graph (Home→Beer Detail, Home→Comparison) formally incomplete rather than merely deferred.
2. **Approximate or imprecise charged-price handling is unresolved.** Nothing specifies whether Price Verification requires an exact figure or can work with a range.
3. **The rule determining whether an Anchor Situation applies on Beer Detail is unresolved.** Entry context is stated to determine this, but no document names the actual determining signal — and the Decision Engine Model rules out identification mechanism alone as that signal.
4. **Ambiguous preference-type statements on Recommendation are unresolved.** Nothing specifies how to handle an input that could plausibly be more than one preference type at once (a number that could be a budget or a size, for instance).
5. **Comparison logic beyond two candidates is unresolved.** Every worked tie-break and trade-off example in the canon assumes exactly two candidates; three-or-more, and particularly non-transitive results, are unaddressed.

Additionally, deferred rather than open — these are acknowledged placeholders, not gaps awaiting a decision: a future accessibility standard, telemetry/analytics event schemas, and implementation guidance generally (the canon is deliberately behavior-first throughout).

---

## 10. Success Criteria

A successful review does not produce approval. It produces a better architecture — either through confirmed weak points that need a real decision (Section 9's five gaps are the clearest existing candidates), through a genuine simplification the canon hadn't considered, or through evidence that a currently-Accepted decision (ADR Section 3) should be reopened.

Any resolution reached through this review should itself be recorded the way the ADR records everything else: with its own Context, Decision Made, and Consequences — never folded silently into whichever document it happens to touch.

---

## 11. Validation

Every claim in this guide traces to a specific canonical document: Sections 2–3 to the documents' own self-declared scope and dependency headers; Section 4 to the ADR's Section 2; Sections 5–6 to specific, named tensions and trade-offs already on record in the ADR, Screen Contracts, and Feature Inventory; Section 9 to the ADR's Section 7 and the matching Screen Contracts' own Section 11 entries, verbatim in substance. No new gap, principle, or decision was introduced anywhere above that the canon doesn't already state. The two scope corrections in Section 2 (Platform Services as a layer, not a document; the Behavioral Hypothesis Model's inclusion) are the only points where this guide adds information beyond straightforward citation, and both are offered as accuracy corrections rather than architectural opinions.

This document introduces no new behavior, no new implementation, and no new architecture. It is the final document in the Canonical Architecture package.
