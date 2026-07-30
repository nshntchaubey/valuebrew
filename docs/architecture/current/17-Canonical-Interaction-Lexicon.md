# ValueBrew — Canonical Interaction Lexicon
### The project's dictionary. Purely terminological — zero new behavior, zero navigation, zero implementation, zero new concepts. Every definition below traces to an existing canonical document.

---

## 1. Purpose

This document exists so that every future specification, implementation, prompt, UI design, engineering document, or AI agent working on ValueBrew uses exactly the same vocabulary, with exactly the same meaning. Where two prior documents used different words for the same concept, this lexicon normalizes them — the normalization is noted explicitly wherever it occurs, so the drift is visible rather than silently erased.

---

## 2. Design Philosophy

Every term here has exactly one owner, one precise meaning, and one first canonical source. A term is included only if it is actually used with load-bearing precision somewhere in the canon — this is a dictionary of what the product's architecture depends on, not a glossary of convenient labels. Where a word is dangerous because it's easy to reach for informally but means something narrower or different in the canon, that danger is named directly in Section 5, not left for someone to discover by accident.

---

## 3. Canonical Terms

### Recommendation & Comparison Outcomes

**Recommendation** — *Definition:* the specific SKU, or bounded set, selected as the answer to Full Recommendation, synthesized by searching the entire catalog against a stated Preference Summary. *Owner:* Recommendation Screen Contract; Recommendation Framework. *Inputs:* Preference Summary, catalog facts. *Outputs:* a Recommendation object, always paired with Recommendation Explanation and Confidence. *Not to be confused with:* Comparison, which never searches the catalog; Confirm-as-Is, which checks only an already-known anchor. *First Canonical Source:* Product Definition Document.

**Comparison** — *Definition:* the evaluation of relationships among two or more already-named candidate SKUs, never extending to a catalog search. *Owner:* Comparison Screen Contract; Feature Inventory. *Inputs:* a Candidate Set, optionally a Preference Summary. *Outputs:* a Comparison Result — a Winner, a Trade-off Explanation, or a Tie Disclosure. *Not to be confused with:* Recommendation. *First Canonical Source:* Feature Inventory.

**Trade-off** — *Definition:* the object naming the specific dimensions on which candidates genuinely differ, used when no clean Winner exists. *Owner:* Recommendation Framework, Section 4. *Inputs:* per-candidate facts, Preference Summary. *Outputs:* a Trade-off object, always shown with its constituent facts. *Not to be confused with:* Tie, which states there is no remaining meaningful difference at all. *First Canonical Source:* Recommendation Framework, Section 4.

**Tie** — *Definition:* the state in which candidates are genuinely equivalent on every known input, after the tie-breaker rule has already been applied and failed to differentiate them. *Owner:* Recommendation Framework, Sections 2 and 5. *Inputs:* per-candidate facts, exhausted tie-breaker logic. *Outputs:* a Tie Disclosure. *Not to be confused with:* Trade-off. *First Canonical Source:* Recommendation Framework, Section 2.

**Winner** — *Definition:* the single candidate that dominates on every known Hard Constraint and Strong Preference within a bounded comparison or recommendation. *Owner:* Recommendation Framework; Comparison and Recommendation Screen Contracts. *Inputs:* Hard Constraint satisfaction, Strong Preference matching. *Outputs:* one selected SKU. *Not to be confused with:* "Recommended" — a Winner within Comparison's bounded set is not the same claim as a catalog-wide Recommendation. *First Canonical Source:* Recommendation Framework, Section 2.

**Better** — *Definition:* a relative, dimension-bound claim that one candidate outperforms another on a named axis, or dominates cleanly within a bounded set — never a claim about the whole catalog. *Owner:* Comparison Screen Contract, Section 6. *Inputs:* per-candidate Alcohol-Adjusted Value or other named facts. *Outputs:* a comparative statement, scoped only to the named candidates. *Not to be confused with:* Recommended (see Section 4). *First Canonical Source:* Comparison Screen Contract, Section 6.

**Recommended** — *Definition:* the status of the SKU produced by Full Recommendation's catalog-wide search and synthesis. *Owner:* Recommendation Screen Contract. *Inputs:* Preference Summary, the full catalog. *Outputs:* the Recommendation object. *Not to be confused with:* Better. *First Canonical Source:* Product Definition Document.

**Trade-off Explanation** — *Definition:* the presented form of a Trade-off object, naming differing dimensions alongside their supporting facts. *Owner:* Decision Engine Model, Section 5. *Inputs:* a Trade-off object. *Outputs:* user-facing content pairing the claim with its facts. *Not to be confused with:* Tie Disclosure. *First Canonical Source:* Decision Engine Model, Section 5.

**Tie Disclosure** — *Definition:* the presented form of a Tie — an honest statement that named candidates are equivalent on everything known to matter. *Owner:* Decision Engine Model, Section 5. *Inputs:* a Tie state. *Outputs:* user-facing content stating the equivalence plainly. *Not to be confused with:* Trade-off Explanation. *First Canonical Source:* Decision Engine Model, Section 5.

### Constraints & Preferences

**Constraint** — *Definition:* any stated input that bounds or shapes an outcome — the general term covering Hard Constraint, Strong Preference, and Soft Preference collectively. *Owner:* Recommendation Framework, Section 2. *Inputs:* user-stated budget, style, strength, size, brand, occasion. *Outputs:* a classified input feeding Preference Summary. *Not to be confused with:* Preference Summary, the aggregate; Constraint is any one member of it. *First Canonical Source:* Recommendation Framework, Section 2.

**Hard Constraint** — *the canonical term; see Section 4's normalization note regarding "Hard Preference."* *Definition:* a stated input that must never be violated, most commonly budget. *Owner:* Recommendation Framework, Section 2. *Inputs:* an explicit budget or hard exclusion. *Outputs:* a non-negotiable filter on the candidate set. *Not to be confused with:* Strong Preference, which can be traded off; "Hard Preference," an informal variant this lexicon retires in favor of the precise term. *First Canonical Source:* Recommendation Framework, Section 2.

**Strong Preference** — *Definition:* an explicitly stated input, not framed as absolute, that dominates ranking but can be traded off if no option satisfies it within budget. *Owner:* Recommendation Framework, Section 2. *Inputs:* stated style, strength, or size. *Outputs:* a high-weight, non-absolute ranking factor. *Not to be confused with:* Hard Constraint or Soft Preference. *First Canonical Source:* Recommendation Framework, Section 2.

**Soft Preference** — *Definition:* a stated input carrying comparatively thin supporting evidence — occasion, brand affinity not framed as a requirement. *Owner:* Recommendation Framework, Section 2. *Inputs:* stated occasion or brand affinity. *Outputs:* a nudge on ranking, always visibly lower-confidence than Hard or Strong inputs. *Not to be confused with:* Strong Preference. *First Canonical Source:* Recommendation Framework, Section 2.

**Preference Summary** — *Definition:* the complete, session-only collection of everything a person has stated. *Owner:* Content Architecture; Decision Engine Model. *Inputs:* every Constraint stated across an interaction. *Outputs:* the aggregate Recommendation and Comparison both weigh against. *Not to be confused with:* a persistent profile — Preference Summary is never persisted across sessions. *First Canonical Source:* Decision Engine Model, Section 3.

**Preference Refinement** — *Definition:* an explicit, mid-interaction change to a previously stated Constraint, re-triggering evaluation without restarting. *Owner:* Experience Flows, Section 5; Recommendation Screen Contract. *Inputs:* an updated Constraint. *Outputs:* re-evaluation against the otherwise-unchanged Preference Summary. *Not to be confused with:* starting a new interaction. *First Canonical Source:* Experience Flows, Section 5.

**Contextual Signal** — *Definition:* a category of input, currently unused, reserved for inferred data such as time of day or location. *Owner:* Recommendation Framework, Section 2. *Inputs:* none currently populated. *Outputs:* none — intentionally empty by design. *Not to be confused with:* Soft Preference, which is stated explicitly, not inferred. *First Canonical Source:* Recommendation Framework, Section 2.

### Facts & Confidence

**Verified Fact** — *Definition:* ground-truth catalog knowledge — Beer Identity, Legal Price, Alcohol Content, Size — sourced directly, never independently inferred. *Owner:* Beer Knowledge Model, Section 3. *Inputs:* government publication, manufacturer declaration. *Outputs:* the highest-confidence tier in the canon. *Not to be confused with:* Computed Fact. *First Canonical Source:* Beer Knowledge Model, Section 3.

**Computed Fact** — *Definition:* a figure derived transparently from Verified Facts — Alcohol-Adjusted Value, Verification Delta — recalculated whenever its inputs change, never independently stored. *Owner:* Beer Knowledge Model, Section 3. *Inputs:* one or more Verified Facts. *Outputs:* a figure carrying the same high confidence as its inputs. *Not to be confused with:* Human Judgment, the lowest-confidence tier. *First Canonical Source:* Beer Knowledge Model, Section 3.

**Human Judgment** — *Definition:* the lowest-confidence knowledge tier — occasion-fit tagging, any future taste assessment — always labeled as interpretation. *Owner:* Beer Knowledge Model, Section 3. *Inputs:* subjective classification. *Outputs:* content flagged explicitly as interpretation, never given Verified or Computed authority. *Not to be confused with:* Computed Fact. *First Canonical Source:* Beer Knowledge Model, Section 3.

**Confidence** — *Definition:* the stated certainty level attached to any content, derived from whether it is a Verified Fact, a Computed Fact, or Human Judgment. *Owner:* Beer Knowledge Model; Recommendation Framework. *Inputs:* the classification of whatever it's attached to. *Outputs:* never standalone — always attached to another object. *Not to be confused with:* Explanation. *First Canonical Source:* Beer Knowledge Model, Section 3.

**Confidence Communication** — *Definition:* the Engine Behavior requiring high- and low-confidence content to remain visibly separated, never blended into one figure. *Owner:* Recommendation Framework, Section 1; Decision Engine Model, Section 6. *Inputs:* the Confidence tiers of the content being presented. *Outputs:* separated, never-merged statements. *Not to be confused with:* Confidence itself — Confidence is the property, Confidence Communication is the rule governing its expression. *First Canonical Source:* Decision Engine Model, Section 6.

### Price & Verification

**Observed Price** — *also referred to as "Charged Price"; both name the same object, see Section 4.* *Definition:* what a person reports having been charged for a specific SKU, never independently verifiable. *Owner:* Beer Knowledge Model; Price Verification Screen Contract. *Inputs:* user report. *Outputs:* one input to the Verification Delta. *Not to be confused with:* Legal Price. *First Canonical Source:* Beer Knowledge Model, Sections 1 and 3.

**Legal Price** — *Definition:* the government-published Maximum Retail Price for a specific SKU, dynamic and subject to periodic regulatory refresh. *Owner:* Beer Knowledge Model, Section 1. *Inputs:* state excise publication. *Outputs:* the reference point for every Verification Delta. *Not to be confused with:* Observed Price. *First Canonical Source:* Beer Knowledge Model, Section 1.

**Verification Delta** — *Definition:* the computed comparison between Observed Price and Legal Price, classified as at, below, or above the reference. *Owner:* Price Verification Screen Contract, Section 6. *Inputs:* Observed Price, Legal Price. *Outputs:* a Verification Result. *Not to be confused with:* Verification Result — the Delta is the computation, the Result is the presented outcome. *First Canonical Source:* Beer Knowledge Model, Section 4.

**Verification Result** — *Definition:* the presented classification of a Verification Delta. *Owner:* Price Verification Screen Contract. *Inputs:* a computed Verification Delta. *Outputs:* user-facing content, always paired with its Explanation. *Not to be confused with:* Verification Delta itself. *First Canonical Source:* Content Architecture, Section 2.

**Confirmation / Confirm-as-Is** — *Definition:* "Confirmation" is the general outcome of affirming an already-identified SKU is already the strongest available fit; "Confirm-as-Is" is the specific canonical Feature producing this judgment. *Owner:* Feature Inventory; Beer Detail Screen Contract. *Inputs:* an anchor SKU's own facts. *Outputs:* a judgment, paired with Explanation and Confidence. *Not to be confused with:* Recommendation — Confirm-as-Is never searches beyond the one known anchor. *First Canonical Source:* Decision Engine Model, Section 5.

### Beer & Catalog Objects

**SKU** — *Definition:* a specific size, package, and ABV variant of a Beer — the atomic unit that price, alcohol content, and size attach to. *Owner:* Beer Knowledge Model, Section 1. *Inputs:* manufacturer declaration. *Outputs:* the unit every screen ultimately reasons about. *Not to be confused with:* Beer, the identity concept a SKU belongs to. *First Canonical Source:* Beer Knowledge Model, Section 1.

**Beer Identity** — *Definition:* the name, brand, and style of a beer — a Verified Fact. *Owner:* Beer Knowledge Model. *Inputs:* catalog data. *Outputs:* the identifying content shown on Beer Detail and referenced everywhere. *Not to be confused with:* SKU — Identity is shared across a Beer's variants; a SKU is one specific variant. *First Canonical Source:* Beer Knowledge Model, Sections 1 and 2.

**Alcohol-Adjusted Value** — *Definition:* the Computed Fact expressing cost per unit of alcohol for a SKU. *Owner:* Beer Knowledge Model, Section 4. *Inputs:* Legal Price, Alcohol Content, Size. *Outputs:* the core figure behind the product's value-comparison capability. *Not to be confused with:* cost per litre, a simpler, unadjusted companion figure. *First Canonical Source:* Beer Knowledge Model, Section 4.

**Style Benchmark** — *Definition:* the reference distribution of Alcohol-Adjusted Value figures across all SKUs sharing a style, used to compute relative standing. *Owner:* Beer Knowledge Model, Sections 1 and 4. *Inputs:* Alcohol-Adjusted Value across a style's SKUs. *Outputs:* a value percentile. *Not to be confused with:* Alcohol-Adjusted Value itself — the Benchmark is the reference group, the Value is the individual figure. *First Canonical Source:* Beer Knowledge Model, Section 1.

**Candidate Set** — *Definition:* the specific group of already-identified SKUs under active consideration in a Recommendation or Comparison. *Owner:* Comparison and Recommendation Screen Contracts. *Inputs:* identified SKUs. *Outputs:* the scope a Comparison Result or Recommendation is bounded to. *Not to be confused with:* the whole catalog — a Candidate Set is always a bounded subset. *First Canonical Source:* Feature Inventory.

### Architecture Layers

**Journey** — *Definition:* a named path through the Decision Engine's reasoning, defined by what's known and needed — No-Anchor, Anchored, Planning, Proxy, and so on. *Owner:* Decision Engine Model, Section 2. *Inputs:* the person's starting situation. *Outputs:* which recommendation logic applies. *Not to be confused with:* Experience — a Journey describes the reasoning path, an Experience is the product-facing capability carrying it out. *First Canonical Source:* Decision Engine Model, Section 2.

**Experience** — *Definition:* a complete, nameable interaction with its own entry point and end state. *Owner:* Feature Inventory, Section 2. *Inputs:* a triggering intent. *Outputs:* a Decision Complete state. *Not to be confused with:* Screen (the contract specifying it) or Feature (which has no independent entry point). *First Canonical Source:* Feature Inventory, Section 2.

**Feature** — *Definition:* a capability existing within, or attaching across, one or more Experiences — never itself a destination. *Owner:* Feature Inventory, Section 2. *Inputs:* an active Experience it attaches to. *Outputs:* a modification of that Experience's behavior. *Not to be confused with:* Experience. *First Canonical Source:* Feature Inventory, Section 2.

**Engine Behavior** — *sometimes shortened to "Behavior"; see Section 4.* *Definition:* an internal rule governing how the Decision Engine reasons or responds. *Owner:* Feature Inventory, Section 2. *Inputs:* the state of an active Experience. *Outputs:* never directly visible — experienced only through its effect on a Feature or Experience. *Not to be confused with:* Feature, which is user-facing in effect. *First Canonical Source:* Feature Inventory, Section 2.

**Platform Service** — *Definition:* shared infrastructure every Experience, Feature, and Engine Behavior depends on but which is not itself part of any interaction. *Owner:* Feature Inventory, Section 2. *Inputs:* none from any single interaction — persists across all of them. *Outputs:* the data and computation every other layer draws from. *Not to be confused with:* Engine Behavior, which governs reasoning within one interaction. *First Canonical Source:* Feature Inventory, Section 2.

**Module** — *Definition:* a coherent, top-level area of the product made up of one or more Experiences. *Owner:* Feature Inventory, Section 3. *Inputs:* none directly — an organizing category, not a computation. *Outputs:* groups Experiences for ownership purposes. *Not to be confused with:* Experience. *First Canonical Source:* Feature Inventory, Section 3.

**Mechanism** — *Definition:* an implementation-level method for satisfying a capability — search, browse, a future barcode scan — never canonically mandated or excluded. *Owner:* Feature Inventory, Section 1. *Inputs:* ordinary product or engineering constraints, not canonical evidence. *Outputs:* a way to enter an Experience, currently only formalized for Beer/SKU Identification. *Not to be confused with:* Capability or Experience — a Mechanism is how, not what. *First Canonical Source:* Feature Inventory, Section 1.

### Interaction & State

**Interaction** — *Definition:* the general term for a person's engagement with the product across states, from Exploring through Decision Complete. *Owner:* User Interaction Model. *Inputs:* an intent. *Outputs:* a Decision Complete state. *Not to be confused with:* Transition — an Interaction spans multiple states, a Transition is one move between two. *First Canonical Source:* User Interaction Model, Section 2.

**Transition** — *Definition:* a single, specific move from one screen or state to another, always traceable to an explicit trigger. *Owner:* Navigation Contract. *Inputs:* a trigger, satisfied preconditions. *Outputs:* a new screen or state, plus carried-forward context. *Not to be confused with:* Navigation (the whole graph of legal Transitions) or Hand-off (a specific kind of Transition). *First Canonical Source:* Navigation Contract, Section 6.

**Hand-off** — *Definition:* a Transition that moves a person between screens while carrying established context forward, never restarting. *Owner:* Navigation Contract, Section 2. *Inputs:* the sending screen's current context. *Outputs:* the receiving screen inheriting that context. *Not to be confused with:* a restart, which begins from nothing. *First Canonical Source:* Navigation Contract, Section 2.

**State** — *Definition:* a specific, named condition a screen or interaction is in. *Owner:* each Screen Contract's own State Machine section. *Inputs:* an entry condition. *Outputs:* permitted or forbidden onward transitions. *Not to be confused with:* Decision Status — State is the condition itself, Decision Status is the tracked value showing which State applies. *First Canonical Source:* User Interaction Model, Section 2.

**Decision Status** — *Definition:* the tracked value indicating where an interaction currently stands. *Owner:* Content Architecture; State & Flow Management (Platform Service). *Inputs:* every State transition within an interaction. *Outputs:* referenced by every screen's composition to know what to show. *Not to be confused with:* State itself. *First Canonical Source:* Content Architecture, Section 2.

**Completion / Decision Complete** — *Definition:* the terminal state of an interaction — nothing further is required, nothing is artificially extended. *Owner:* User Interaction Model; every Screen Contract's own State Machine. *Inputs:* an explicit User Decision to accept an outcome. *Outputs:* the end of the current interaction. *Not to be confused with:* any other State — this is uniquely terminal. *First Canonical Source:* User Interaction Model, Section 2.

**Recovery** — *Definition:* the general process of resolving a condition preventing a screen from proceeding normally, always preserving established progress by default. *Owner:* Experience Flows, Section 5. *Inputs:* a detected failure condition. *Outputs:* a resumed normal State once resolved. *Not to be confused with:* Recovery State — Recovery is the process, Recovery State is one specific named condition within it. *First Canonical Source:* Experience Flows, Section 5.

**Recovery State** — *Definition:* a specific, named condition requiring Recovery — Low Confidence, Conflicting Constraints, SKU Not Found, Unresolvable Candidate. *Owner:* each Screen Contract's own Failure Conditions section. *Inputs:* a trigger specific to that condition. *Outputs:* a Recovery process, resolving in place per the Navigation Contract's general pattern. *Not to be confused with:* a Tie or Trade-off, which are never classified as Recovery States. *First Canonical Source:* Recommendation Screen Contract, Section 3.

**Clarifying Question** — *Definition:* the single, bounded question Comparison may ask — at most one — when what matters most between named candidates hasn't been stated. *Owner:* Comparison Screen Contract. *Inputs:* an ambiguous but potentially resolvable candidate set. *Outputs:* at most one further input. *Not to be confused with:* Progressive Question, which belongs only to Recommendation's iterative, multi-step process. *First Canonical Source:* Content Architecture, Section 3.

**Progressive Question** — *Definition:* one step in Recommendation's iterative, evidence-ordered gathering process, asked only when its answer would materially change the outcome. *Owner:* Decision Engine Model, Section 4; Recommendation Screen Contract. *Inputs:* the current, incomplete Preference Summary. *Outputs:* one further Constraint, narrowing the candidate set. *Not to be confused with:* Clarifying Question. *First Canonical Source:* Decision Engine Model, Section 4.

**Explanation** — *Definition:* the stated reasoning behind a Recommendation, Verification Result, or Comparison Result. *Owner:* Recommendation Framework, Section 6. *Inputs:* the reasoning that produced its parent object. *Outputs:* user-facing content, always attached, never standalone. *Not to be confused with:* Confidence — Explanation states why, Confidence states how sure. *First Canonical Source:* Recommendation Framework, Section 6.

**Recommendation Explanation** — *Definition:* the specific, canonical Feature implementing Explanation, reused identically across every screen that needs it. *Owner:* Feature Inventory. *Inputs:* a Recommendation, Verification Result, or Comparison Result. *Outputs:* the attached reasoning, using the same structure everywhere. *Not to be confused with:* Explanation as a general concept — Recommendation Explanation is the one canonical Feature that always implements it. *First Canonical Source:* Feature Inventory, Sections 2 and 3.

### Anchor & Intent

**Anchor Situation** — *Definition:* the condition in which a person already has a specific SKU in mind before deliberation begins. *Owner:* Decision Engine Model, Journey 2; Beer Detail Screen Contract. *Inputs:* an already-identified SKU. *Outputs:* triggers the Confirm-as-Is judgment. *Not to be confused with:* simply identifying a SKU through browsing without a strong anchor framing — not every identification is an Anchor Situation. *First Canonical Source:* Decision Engine Model, Section 2.

**Unsupported Intent** — *Definition:* an expressed intent that cannot be mapped to any supported ValueBrew capability because it falls outside the product's domain. *Owner:* Home Screen Contract. *Inputs:* an expressed intent. *Outputs:* a boundary explanation and a restatement of the four supported capabilities. *Not to be confused with:* Ambiguous Intent, which is plausibly inside scope but unclear. *First Canonical Source:* Home Screen Contract, Section 11.

**Low Confidence [Response]** — *Definition:* the Feature triggered when genuinely insufficient information exists to distinguish among candidates. *Owner:* Recommendation Screen Contract. *Inputs:* an evaluated candidate set with no meaningful differentiation possible. *Outputs:* a request for the single most useful next input, or a labeled provisional answer. *Not to be confused with:* withholding a recommendation for a missing Soft Preference alone — this must never trigger Low Confidence. *First Canonical Source:* Decision Engine Model, Section 5.

---

## 4. Canonical Distinctions

**Recommendation vs. Comparison.** Recommendation searches the whole catalog from a preference profile. Comparison only ever reasons about candidates it was explicitly handed, never searching.

**Better vs. Recommended.** Better is a bounded, dimension-scoped claim about named candidates. Recommended is the output of a catalog-wide search — a claim Comparison is never entitled to make.

**Verified vs. Computed.** Verified Facts are sourced directly and never inferred. Computed Facts are derived transparently from Verified Facts, but carry the same high confidence, since deriving isn't the same as guessing.

**Recovery vs. Clarification.** Recovery resolves a genuine failure condition — insufficient information, an unresolvable reference. Clarification is a bounded, single-question resolution of ambiguity that doesn't rise to the level of a failure at all.

**Journey vs. Experience.** A Journey is the Decision Engine's own reasoning path. An Experience is the product-facing capability that carries a Journey out.

**Experience vs. Screen.** An Experience is the behavioral concept. A Screen is where that concept is specified as a testable contract.

**Transition vs. Navigation.** A Transition is a single edge — one move, one trigger. Navigation is the entire graph of legal Transitions considered together.

**Explanation vs. Confidence.** Explanation states why a conclusion was reached. Confidence states how certain that conclusion is. They always travel together, but they answer different questions.

**Fact vs. Preference.** A Fact is something the product knows, sourced externally. A Preference is something a person states, sourced from them, and is never treated with the same unconditional authority as a Fact.

**Decision vs. Recommendation.** A Decision, per the Recommendation Screen Contract's own distinction, is something the system computes — which question to ask, whether a recommendation exists. A Recommendation is one specific kind of output a Decision can produce; not every Decision produces one.

**Behavior vs. Implementation.** A Behavior (Engine Behavior) is a canonical rule that must hold regardless of how it's built. Implementation is the specific code, interface, or algorithm satisfying that rule — and it may change freely, provided the Behavior it satisfies does not.

---

## 5. Forbidden Synonyms

**"Suggest"** should not replace "Recommend" unless Recommendation's actual ownership and reasoning apply — using it loosely implies a lower-stakes claim than the canon's Recommendation Framework actually governs.

**"Best"**, used alone and unqualified, should never substitute for "Recommended" or "Better" — the Decision Engine Model explicitly states the product "does not recommend the objectively best beer," and "best" as a bare word reintroduces exactly the universal claim that principle exists to forbid.

**"Score" or "Rating"** should never appear anywhere in a specification, since no numeric scoring or rating system exists anywhere in the canon — the Beer Knowledge Model explicitly excludes Sensory data, and the Recommendation Framework explicitly forbids collapsing confidence into a single blended figure, which a "score" would almost certainly imply.

**"Match" or "Fit"**, used as a noun standing in for an outcome, should not silently replace "Recommendation" or "Better" — both words are vague enough to blur which of the two, very differently scoped, claims is actually being made.

**"Verify"**, used loosely to describe Recommendation or Comparison reasoning, is forbidden — it is reserved exclusively for Price Verification's specific delta computation, and using it elsewhere would imply a certainty level those other Experiences don't carry.

**"Confirm"**, used alone without "-as-Is," risks confusion with unrelated actions like confirming an order — always pair it with its full canonical term when referring to the Feature specifically.

**"Personalize" or "Personalization"**, used casually, is dangerous because the canon explicitly defers all learned or inferred personalization — using the word loosely in a spec or prompt risks implying a capability that does not yet exist.

**"Correct price"** should not replace "Legal Price" — "correct" implies a moral or absolute judgment, where the canon's own framing is precise and narrower: a legally published reference figure, nothing more.

**"Alternative"**, used as a generic catch-all, should not replace "Comparison" or "Trade-off" — it appears informally in a few places (Alternative/Value Suggestion) but should always be qualified by its owning Feature, never used as a loose substitute for a more precise term.

---

## 6. Naming Rules

**Capitalization.** Every canonical term, when used in its precise technical sense, is capitalized exactly as it appears in Section 3 — "Recommendation," "Hard Constraint," "Decision Complete." When a word is used in its ordinary English sense rather than its canonical one, it is not capitalized.

**Pluralization.** Standard English pluralization applies — SKUs, Experiences, Hard Constraints — never an apostrophe-s form.

**Abbreviations.** SKU is itself the standard form and needs no further abbreviation. ABV may be used as shorthand for Alcohol Content only after the full term has appeared once in a given document.

**Canonical phrasing.** Compound terms are always hyphenated exactly as defined — "Confirm-as-Is," never "Confirm As Is" or any other variant. "Trade-off" is always hyphenated, never "Tradeoff" or "Trade off."

**Cross-reference conventions.** The first reference to another canonical document in any new document uses its full name — "the Recommendation Framework," never an informal shorthand — with subsequent references in the same document permitted to use a shortened but still unambiguous form.

---

## 7. Validation

✓ Every term in Section 3 traces to at least one specific, named canonical document.
✓ No term was invented for this lexicon that didn't already exist somewhere in the fifteen prior canonical documents or five Screen Contracts.
✓ Every normalization in Section 4 and the "Not to be confused with" fields preserves the original meaning of both source terms rather than inventing a new, third meaning.
✓ Every forbidden synonym in Section 5 is justified by a specific canonical rule it would otherwise risk violating.

---

## 8. Future Compatibility

A future document may add a new term to this lexicon only if it can name the specific canonical document the term traces back to, following exactly the same discipline used throughout Section 3. A new term must never redefine or narrow an existing entry — if a future concept seems to overlap with something already defined here, that overlap must be resolved as a new Canonical Distinction in Section 4, not by quietly repurposing an existing word. Any future normalization of drifted terminology, in the spirit of Section 4's existing notes, should state plainly which prior documents used which wording, exactly as this document did for "Hard Constraint" versus "Hard Preference," so the correction remains visible rather than silently absorbed.
