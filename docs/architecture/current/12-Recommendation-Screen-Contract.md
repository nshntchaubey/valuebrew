# ValueBrew — Screen Contract: RECOMMENDATION
### The canonical, implementation-independent contract for the Recommendation screen. Derived entirely from the ten frozen documents. Not UI, not wireframes, not a PRD. This is the most important Screen Contract in the canon — it is the only place the Decision Engine's reasoning is exposed to a person without exposing its internal implementation.

---

## 1. Screen Identity

**Screen Name:** Recommendation.

**Purpose:** collect necessary preference inputs progressively and produce the Full Recommendation synthesis — the product's stated core purpose, per the Product Definition Document.

**Owning Module:** Recommendation Module.

**Owning Experience:** Full Recommendation.

**Canonical Role:** the sole screen where the Decision Engine's constraint-weighing, trade-off resolution, and confidence separation become visible to a person, expressed entirely through Recommendation Explanation and Confidence Communication rather than through anything resembling internal reasoning steps.

**Why this screen exists independently:** every other screen assumes something specific is already known — Beer Detail assumes an identified SKU, Price Verification assumes a SKU and a charged price, Comparison assumes named candidates. Recommendation is the only screen that begins from preference and budget alone, with no SKU assumed at all, and it is the only screen responsible for the full, multi-step Progressive Question-Asking discipline. Merging it into Home or Beer Detail would collapse the distinction the Information Architecture protects between "an anchor already exists" (near-zero friction, per Segment-Appropriate Restraint) and "no anchor exists, real synthesis is required" — which is this screen's entire reason for being.

**A precise clarification, since the canon is easy to misread here:** Comparison's own composition permits "at most one clarifying question," which might look like a second instance of progressive question-asking. It is not the same behavior. Comparison's single, bounded clarification is a narrow exception justified only by already having named candidates in hand. Recommendation's Progressive Question-Asking is the full, iterative, evidence-ordered process the Decision Engine Model defines — and it is the only screen where that full process legitimately runs.

---

## 2. Screen Contract

**MUST:**
- Treat budget as the first-priority input whenever it isn't already known.
- Ask a further question only when its answer would materially change which candidate or candidates are recommended.
- Produce a recommendation — a single winner, a Trade-off Explanation, or a Tie Disclosure — the moment Hard Constraints are satisfiable and known Strong Preferences are sufficient to identify a confident or honestly bounded candidate set.
- Never withhold a recommendation solely because an optional, Soft, or low-confidence input — occasion, brand affinity — remains unstated.
- Attach Recommendation Explanation immediately alongside every recommendation, trade-off, or tie it produces.
- Attach Confidence Communication to every recommendation, explicitly separating the Hard/Strong-driven portion from any Soft-driven portion.
- Treat every stated Hard Constraint as inviolable, never overridden in service of a "better-looking" answer.
- Enter a Low-Confidence Response only when genuinely insufficient information exists to distinguish among candidates at all — never as a substitute for simply lacking a Soft input.
- Recognize Planning Mode and Proxy-Buying Mode as attached Features, applying their respective caveats or conservative defaults without becoming separate screens.

**MAY:**
- Hand off to Beer Detail, for the recommended SKU, or to Comparison, when a genuine trade-off or tie would benefit from richer multi-candidate treatment.
- Accept a refined or changed preference mid-flow and re-evaluate without restarting.

**MUST NEVER:**
- Ask a second question once the first has already produced a confident recommendation.
- Ask about occasion, brand, or any other Soft input before budget or an already-relevant Strong Preference.
- Present a recommendation as a single, blended confidence figure that doesn't separate Hard/Strong content from Soft content.
- Force a single winner when the only remaining difference between close candidates is a Soft Preference — a Trade-off Explanation or Tie Disclosure is required instead.
- Withhold any recommendation because occasion or brand preference wasn't stated. This is repeated deliberately from the MUST list above, given how easy it would be to violate by accident.
- Silently drop or reinterpret a stated budget to produce an answer that looks more impressive.
- Perform Price Verification's computation, or Comparison's dedicated multi-candidate reasoning, as this screen's own standalone output.
- Persist Preference Summary across separate sessions.

---

## 3. Inputs

**Known Information:** whatever preference inputs have already been established — possibly none. Any Planning Mode or Proxy-Buying Mode flag carried from Home. Any Preference Summary preserved from a recovery or clarification at Home.

**Referenced Information:** the Beer Knowledge Base across the full catalog — Legal Price, Alcohol Content, and Size for every candidate SKU — and the Style Benchmark, where available.

**Interaction State:** Decision Status reflecting where the progressive gathering process currently stands — see the State Machine in Section 8 for the exact stages.

**Cross-cutting Behaviors:** Recommendation Explanation, Confidence Communication, and Learning ("Why") are all actively present on this screen. Decision Complete is directly reachable here.

**Recovery State — precisely two, and deliberately not three:** Low-Confidence Response, when too little is known to distinguish among candidates at all; Conflicting Constraints, when a stated Hard Constraint and a stated Strong Preference together exclude every real candidate. **A Trade-off or a Tie is explicitly not a recovery state** — both are valid, complete recommendation outcomes, per the Recommendation Framework, and must never be treated or presented as a failure requiring recovery.

---

## 4. Outputs

**Transition** — to Beer Detail, if the person wants fuller context on the recommended SKU; to Comparison, if a trade-off or tie is surfaced and richer multi-candidate treatment is invited.

**Decision** — a system decision: the recommendation itself. Never confused with the person's own decision to accept it — see Section 6 for the explicit separation.

**Recommendation** — the actual object produced: a single winner, a Trade-off Explanation, or a Tie Disclosure. Produced the moment Section 6's threshold for "a recommendation exists" is met.

**Recovery** — Low-Confidence Response or Conflicting Constraints, produced the moment either condition is detected, never manufactured to avoid a genuinely available recommendation.

**Information Request** — the next progressive question, produced only when Section 6's threshold for "another question is justified" is met.

**State Change** — Decision Status advancing through Gathering, Evaluating, and into either Recommending or Recovering, and finally into Completed.

---

## 5. Information Composition

Directly citing Content Architecture Section 3's Recommendation entry, not redesigning it. Primary: the Recommendation object once produced, or the next progressive question before that. Supporting: Preference Summary as established so far. Contextual: which entry point led here, since that determines whether Planning Mode or Proxy-Buying Mode applies. Progressive: the next question — this is the canonical home for progressive information in the entire product. Explanation: attached to the Recommendation, always. Confidence: attached to the Recommendation, always separated by Hard/Strong versus Soft contribution. Recovery: for Low-Confidence Response or Conflicting Constraints specifically. Completion: reached the moment the person accepts.

---

## 6. Behavioral Rules

This section states the exact thresholds requested, as testable rules, not general guidance.

**Another question is justified when:** two or more candidates remain that are currently indistinguishable given every known Hard and Strong input, *and* the candidate question is one whose answer would actually separate them.

**Another question is forbidden when:** a single candidate already dominates on every known Hard and Strong input (a recommendation already exists — asking more would violate the rule against unnecessary questions); *or* the remaining candidates differ only on a Soft input, in which case a Trade-off Explanation or Tie Disclosure is the correct, complete response instead of continued probing; *or* the question would touch an input already stated; *or* no further Hard or Strong input remains to ask about at all, in which case Low-Confidence Response applies instead of continuing indefinitely.

**A recommendation exists when:** at least one real candidate satisfies every stated Hard Constraint, *and either* exactly one candidate dominates on every known Strong Preference, *or* multiple candidates remain but differ only on Soft Preferences — in which case the Trade-off Explanation or Tie Disclosure itself **is** the recommendation, not an absence of one.

**A recommendation does not yet exist when:** no candidate satisfies the stated Hard Constraint at all — this is Conflicting Constraints, not Low-Confidence; *or* too little is known to meaningfully distinguish among a large field of Hard-Constraint-satisfying candidates in any way an honest explanation could describe — this is Low-Confidence Response, and it requests the single most useful next input, never a guess dressed up as an answer.

**Confidence must be displayed:** every time a recommendation, trade-off, or tie is shown. Never optional, never deferred to a later screen or a "why" request — the first display already carries it.

**Explanation must appear:** immediately alongside every recommendation, trade-off, or tie, in the same moment it's first shown.

**Recovery begins when:** either Conflicting Constraints or Low-Confidence Response is detected, per the definitions above — never manufactured when a genuine recommendation is actually available.

**Decision Complete is reached when:** the person — never the system — accepts a recommendation, a trade-off resolution, or a tie as their answer. This is exclusively a User Decision Moment; see Section 6's continuation below.

**System Decisions versus User Decisions on this screen, kept explicitly separate:**

*System decides:* which question to ask next, if any; whether a recommendation currently exists; whether the honest resolution is a single winner or a trade-off/tie; what confidence to attach to each part of the output; when Recovery begins.

*User decides:* what to answer, or whether to answer at all; whether to accept the recommendation, ask "why," or refine a preference; which side of a trade-off to choose, or to accept a tie as the answer; when the interaction reaches Decision Complete.

**The system never simulates or presumes a user decision, and the user is never asked to simulate a system decision.** A future interface that lets someone "accept" a recommendation before the system has actually produced one, or that lets the system silently treat inaction as acceptance, violates this section directly.

---

## 7. Interaction Contract

**Answer a progressive question.** Trigger: a question is currently active. Precondition: exactly one question is active at a time, per Section 6. System Response: the answer is added to Preference Summary, and Section 6's thresholds are re-evaluated. Possible Outcomes: a recommendation now exists, another question is justified, or Recovery begins. Recovery: not applicable to this interaction itself. Completion: not applicable yet.

**Accept a recommendation.** Trigger: an explicit user action following a displayed recommendation. Precondition: a recommendation, trade-off, or tie must already exist. System Response: Decision Status moves to Completed. Possible Outcomes: Decision Complete. Recovery: not applicable. Completion: reached.

**Ask "why."** Trigger: an explicit request following any displayed output. Precondition: an Explanation object must already exist to retrieve. System Response: the existing Explanation is re-surfaced; nothing new is generated. Possible Outcomes: the person accepts afterward, or refines a preference having learned something from the explanation. Recovery: not applicable. Completion: not changed by this interaction alone.

**Refine or change a preference.** Trigger: an explicit statement that updates a previously given input. Precondition: none. System Response: the updated input replaces the prior one in Preference Summary; every other established input is preserved; Section 6's thresholds are re-evaluated from the current state, not from scratch. Possible Outcomes: a new recommendation, a new question, or Recovery, depending on the updated evaluation. Recovery: if the change is to budget specifically and now conflicts with a Strong Preference, Conflicting Constraints may begin. Completion: not applicable yet.

**Signal openness to alternatives, or request comparison.** Trigger: an explicit request following a recommendation. Precondition: a recommendation must already exist. System Response: hands off to Comparison, carrying the current candidate set and Preference Summary forward. Possible Outcomes: proceeds into Comparison's own contract. Recovery: not applicable here. Completion: not reached at Recommendation itself in this case.

---

## 8. State Machine

**Initial.** Entry: first arrival at Recommendation, from Home or a hand-off. Exit: any known input is present, or the first progressive question is posed. Permitted transitions: to Gathering. Forbidden: directly to Recommending or Recovering without at least one evaluation pass.

**Gathering.** Entry: at least one input is known but Section 6's threshold for "a recommendation exists" isn't yet met. Exit: an answer is given, or no further question is justified. Permitted transitions: to Evaluating. Forbidden: asking two questions without an intervening evaluation.

**Evaluating.** Entry: every time new information arrives, including the very first. Exit: Section 6's thresholds are checked. Permitted transitions: to Recommending, if a recommendation now exists; to Gathering, if another question is justified; to Recovering, if Low-Confidence or Conflicting Constraints applies. Forbidden: skipping evaluation and asking another question directly from Gathering.

**Recommending.** Entry: Section 6's "a recommendation exists" threshold is met. Exit: the person accepts, asks "why," refines a preference, or requests comparison. Permitted transitions: to Completed, to Comparison (hand-off), back to Evaluating if a preference is refined. Forbidden: presenting a recommendation without its attached Explanation and Confidence.

**Recovering.** Entry: Low-Confidence Response or Conflicting Constraints is detected. Exit: the person provides more information, changes the conflicting input, or accepts the honest limitation as the answer. Permitted transitions: to Evaluating, if new information resolves the condition; to Completed, if the person accepts a provisional or bounded answer as sufficient. Forbidden: silently discarding the Preference Summary that led here.

**Completed.** Entry: the person's explicit acceptance, per Section 6's User Decision definition. Exit: none — this is terminal for the current interaction. Forbidden: any further automatic question or recommendation.

---

## 9. Dependencies

**Decision Engine Model** — directly. Its Journeys, its Progressive Question-Asking discipline, and its recommendation type definitions are the direct source of this screen's core behavior.

**Beer Knowledge Model** — directly. Verified and Computed Facts, and the Style Benchmark, are what this screen's Confidence tiers and value comparisons are built from.

**Recommendation Framework** — directly, and most load-bearing of all. The constraint tiers (Hard/Strong/Soft), the trade-off and tie rules, and the confidence-expression rules are what Section 6 of this contract directly operationalizes.

**Information Architecture** — directly. This screen's ownership, its entry and exit points, and its exclusive claim to Preference Input Handling are defined there.

**Experience Flows** — directly. The No-Anchor, Budget, Planning, and Buying-for-Someone-Else flows all live on this screen.

**Content Architecture** — directly. This screen's composition in Section 5 is a direct citation.

**Feature Inventory** — directly. Confirm-as-Is, Low-Confidence Response, Planning Mode, Proxy-Buying Mode, and Preference Input Handling are all Features this screen owns as attached capabilities.

---

## 10. Constraints

Cannot perform Price Verification's computation. Cannot perform Comparison's dedicated multi-candidate reasoning as its own standalone output, though it may hand off to it. Cannot display Observed/Charged Price. Cannot override or reinterpret a stated Hard Constraint. Cannot ask a question whose answer wouldn't change the outcome. Cannot withhold a recommendation because a Soft input alone is missing. Cannot blend Hard/Strong and Soft confidence into a single unlabeled figure. Cannot persist Preference Summary across separate sessions. Cannot treat a Trade-off or Tie as a failure state rather than a complete answer.

---

## 11. Failure Conditions

**Conflicting Constraints.** Detection: a stated Hard Constraint (budget) and a stated Strong Preference together exclude every real candidate. Recovery: surface the conflict directly, naming which two stated inputs are in tension, and invite the person to relax one of them. Progress Preservation: both conflicting inputs remain visible and named, not silently discarded in favor of one over the other.

**Low-Confidence Response.** Detection: too little is known to meaningfully distinguish among Hard-Constraint-satisfying candidates. Recovery: request the single most useful next input, or offer a clearly labeled provisional answer if the person prefers not to continue. Progress Preservation: everything already known remains intact.

**An ambiguous preference statement — flagged honestly as an open question, not resolved here.** Detection: a stated input could plausibly be interpreted as more than one preference type (for instance, a number that could be a budget or a size). **No canonical resolution for this specific case exists across any of the ten frozen documents.** Given how directly this touches the Recommendation Framework's rule against misapplying a stated constraint, this is worth a deliberate decision of the same kind just made for Home's unsupported-intent case, rather than an assumption made silently here.

---

## 12. Acceptance Criteria

✓ No question is ever asked whose answer could not change which candidate is recommended.
✓ A recommendation is never withheld solely because occasion, brand, or another Soft input is missing.
✓ Every recommendation, trade-off, or tie carries its Explanation and its Confidence at the moment it first appears, not afterward.
✓ A Trade-off or Tie is never presented as, or treated as, a recovery condition.
✓ A stated Hard Constraint is never silently overridden, in any recommendation this screen produces.
✓ No more than one question is ever active at a time.
✓ Decision Complete is only ever reached through an explicit User Decision, never inferred from inaction or automatically advanced.
✓ Confidence is never expressed as a single blended figure across Hard/Strong and Soft content.

---

## 13. Validation

✓ No Product Definition Document violated — the core purpose is served exactly as defined, with no new capability introduced.
✓ No Recommendation Framework violated — every constraint tier, trade-off rule, and confidence-expression rule from that document is directly operationalized in Section 6.
✓ No Information Architecture ownership violated — this screen's ownership matches its IA entry exactly, including its exclusive claim on Preference Input Handling.
✓ No Experience Flow violated — the No-Anchor, Budget, Planning, and Proxy flows all map cleanly onto this contract's states and interactions.
✓ No Content Architecture violated — this screen's composition matches that document's entry directly.
✓ No new capability introduced — every behavior here traces to an already-named Experience or Feature.
✓ No hidden assumptions introduced — one genuine gap is named rather than silently resolved: the ambiguous-preference-statement failure mode in Section 11, left open pending an explicit decision, consistent with how the equivalent gap was handled on Home.

---

## 14. Future Compatibility

**Natural future evolution:** richer Style Benchmark integration as that Platform Service matures beyond its Important-Soon-After status; a lightweight feedback mechanism for gradually improving preference-matching, if real usage ever justifies building it, per the Product Definition Document's own deferred language.

**Forbidden future evolution:** inferring an unstated preference from behavior or context, which remains deferred by the canon until real usage earns it; persisting Preference Summary across sessions without first revisiting the Product Definition Document's rejection of accounts; blending Hard/Strong and Soft confidence into a single score for the sake of a cleaner-looking interface; treating a Trade-off or Tie as something to be optimized away rather than presented honestly, no matter how sophisticated future scoring becomes.
