# ValueBrew — Engineering Screen Specification: RECOMMENDATION

**Document type:** Engineering Screen Specification (not a Screen Contract).
**Implements:** Recommendation Screen Contract (12), in full.
**Built under:** the Canonical Screen Specification Template's citation discipline — every field filled by citation or explicitly marked unspecified.
**Consumers:** UI/UX design, Flutter engineering, QA engineering.
**Version:** 1.0.
**Status:** Draft, pending engineering review.

---

## 1. Screen Purpose

Recommendation collects necessary preference inputs progressively and produces the Full Recommendation synthesis — the product's stated core purpose. It is the sole screen where the Decision Engine's constraint-weighing, trade-off resolution, and confidence separation become visible to a person, expressed entirely through Recommendation Explanation and Confidence Communication.

*Citation: Recommendation Screen Contract (12), §1.*

---

## 2. User Goals

- "I haven't chosen a beer yet" — arriving with no anchor, seeking the full synthesis.
- "I want recommendations within a budget" — arriving budget-first.
- "I'm planning before going shopping" — the same synthesis, carrying a standing lower-confidence caveat throughout.
- "I'm buying this for someone else" — the same synthesis, defaulting conservatively unless recipient preference is known.

*Citation: User Interaction Model (06), §1; Decision Engine Model (03), §2 (Journeys 1, 3, 4, 5); Experience Flows (09), §2.*

---

## 3. Entry Conditions

| Condition | Known state on arrival |
|---|---|
| **From Home**, budget/preference/no-anchor intent expressed | Whatever preference inputs were already stated at Home, possibly none. Any Planning Mode or Proxy-Buying Mode flag, carried as a variant of this same transition. |
| **From Comparison**, an explicit constraint refinement | The current candidate set and full Preference Summary, per Comparison's own hand-back. |
| **On recovery bounce-back at Home**, preserved Preference Summary carried into a fresh Recommendation entry | Any Preference Summary established before a prior failed identification attempt. |

*Citation: Recommendation Screen Contract (12), §3; Navigation Contract (16), §4, §6 ("Home → Recommendation," "Comparison → Recommendation").*

Referenced on every entry: the Beer Knowledge Base across the full catalog — Legal Price, Alcohol Content, and Size for every candidate SKU — and the Style Benchmark, where available.

*Citation: Recommendation Screen Contract (12), §3.*

---

## 4. Exit Conditions

| Trigger | Destination |
|---|---|
| Explicit acceptance of a recommendation, trade-off resolution, or tie | Decision Complete (terminal, no screen change) |
| Explicit request for fuller context on the recommended SKU | Beer Detail |
| A trade-off or tie is surfaced and richer treatment is invited | Comparison |

*Citation: Recommendation Screen Contract (12), §4, §7; Navigation Contract (16), §6.*

Decision Complete on this screen is reached **exclusively by an explicit User Decision** — never inferred from inaction, never advanced automatically.

*Citation: Recommendation Screen Contract (12), §6 ("Decision Complete is reached when: the person — never the system — accepts").*

---

## 5. Information Hierarchy

Directly citing Content Architecture §3's Recommendation entry, in full, without redesign:

- **Primary:** the Recommendation object once produced, or the next progressive question before that.
- **Supporting:** Preference Summary as established so far.
- **Contextual:** which entry point led here, since that determines whether Planning Mode or Proxy-Buying Mode applies.
- **Progressive:** the next question — the canonical home for progressive information in the entire product.
- **Explanation:** attached to the Recommendation, always.
- **Confidence:** attached to the Recommendation, always separated by Hard/Strong versus Soft contribution.
- **Recovery:** for Low-Confidence Response or Conflicting Constraints specifically.
- **Completion:** reached the moment the person accepts.

*Citation: Content Architecture (10), §3; Recommendation Screen Contract (12), §5.*

**A structural rule that governs every element below:** Confidence and Explanation are never standalone objects. Confidence "exists only attached to another object, never standalone" and Explanation is "user-facing content, always attached, never standalone." Neither may be represented in this specification, or built, as an independently optional or independently visible component.

*Citation: Content Architecture (10), §2; Canonical Interaction Lexicon (17), §3.*

---

## 6. Screen Sections

Seven functional sections, defined by behavior:

**A. Progressive Question** — visible only during Gathering; exactly one active question at a time.

**B. Preference Summary Display** — visible from the moment any input exists; grows as more is given.

**C. Recommendation Output** — visible only during Recommending; a single Winner, a Trade-off Explanation, or a Tie Disclosure, with Explanation and Confidence as intrinsic, non-detachable sub-parts, never a separate optional section.

**D. Mode Indicator** (Planning / Proxy-Buying) — present throughout the entire interaction once flagged, not confined to the final output.

**E. Recovery** — visible only during Recovering; Low-Confidence Response or Conflicting Constraints, mutually exclusive.

**F. Actions** — Accept, Ask "Why," Refine a Preference, Request Comparison.

**G. Preference Refinement Entry** — the mechanism by which a previously given input is updated mid-flow.

*Citation: Recommendation Screen Contract (12), §5, §6, §7, §8.*

**How these sections are visually arranged is a design decision. Intentionally left unspecified by the Canonical Architecture.**

---

## 7. Every UI Element

| Element | Purpose | Required Data | Optional Data | Visibility Rule |
|---|---|---|---|---|
| **Progressive Question** | Present the single active question, ordered by evidence strength | The question content, addressing one of: budget, style, strength, size, or brand, per Decision Engine Model §4's ordering. **Whether occasion is ever actively solicited here — as opposed to only recognized if volunteered elsewhere — is unresolved by the frozen canon (see §10 and §13 below). Intentionally left unspecified pending ADR resolution.** | None | Visible only in Gathering state; never two questions active simultaneously |
| **Preference Summary Display** | Show what's been established so far | Every stated input to date (budget, style, strength, size, brand, and occasion/recipient info if applicable) | — | Visible from first input onward |
| **Recommendation Output** | Present the produced Recommendation — Winner, Trade-off Explanation, or Tie Disclosure | The Recommendation object (selected SKU(s), reasoning, confidence structure); its Explanation, naming which inputs contributed at which tier; its Confidence, explicitly separated into Hard/Strong-driven versus Soft-driven portions | — | Visible only in Recommending state; **never shown without Explanation and Confidence simultaneously present — this is a hard coupling, not a UI preference** |
| **Mode Indicator** | Surface Planning Mode or Proxy-Buying Mode, carrying its standing caveat throughout | Which mode is active, and its caveat requirement (lower confidence ceiling for Planning; conservative-default framing for Proxy) | — | Present from arrival through every subsequent screen state once flagged — never collapsed into a one-time disclaimer |
| **Recovery Display** | Communicate Low-Confidence Response or Conflicting Constraints | Which condition applies; for Conflicting Constraints, both named, tension-producing inputs, both kept visible | — | Visible only in Recovering state; mutually exclusive between the two conditions |
| **Accept** | Register the person's explicit acceptance of the current output | — | — | Visible only once a Recommendation, Trade-off, or Tie exists |
| **Ask "Why"** | Re-surface the existing Explanation | — | — | Visible only once an Explanation object exists |
| **Refine a Preference** | Update a previously given input | The input being changed | — | Visible once at least one input already exists |
| **Request Comparison** | Hand off to Comparison, carrying the candidate set and Preference Summary | — | — | Visible only once a genuine trade-off or tie has been surfaced |

*Citation: Recommendation Screen Contract (12), §2, §5, §6, §7; Decision Engine Model (03), §4; Experience Flows (09), Principle 5.*

**No element beyond these nine is permitted.**

---

## 8. User Interactions

| Canonical action | Detail |
|---|---|
| **Answer a progressive question** | Adds the answer to Preference Summary; re-evaluates §10's thresholds. Exact input modality (text, selection, or otherwise) is unspecified — see below. |
| **Accept a recommendation** | Moves Decision Status to Completed. Requires a recommendation, trade-off, or tie already present. |
| **Ask "why"** | Re-surfaces the existing Explanation; generates nothing new. |
| **Refine or change a preference** | Replaces a prior input in Preference Summary; all other established inputs preserved; thresholds re-evaluated from current state, not from scratch. |
| **Signal openness to alternatives / request comparison** | Hands off to Comparison, carrying the current candidate set and Preference Summary forward. |

*Citation: Recommendation Screen Contract (12), §7.*

**Interaction modality (tap, text input, selection, gesture) is not specified anywhere in the canon.** The canon defines the required system response to each action, never the physical mechanism producing it. **Intentionally left unspecified by the Canonical Architecture.** No long-press, scroll, or gesture behavior is canonically defined for this screen; each is a layout/implementation decision.

*Citation: Feature Inventory (07), §1; Review Guide (00), §2.*

---

## 9. States

Mapped exhaustively onto Recommendation Screen Contract §8's own State Machine. No new state is introduced.

| Requested category | Canonical mapping | Notes |
|---|---|---|
| **Initial** | **Initial** | First arrival, from Home or a hand-off. Exit: any known input is present, or the first progressive question is posed. |
| **Loading** | **No canonical "Loading" state exists.** The transitional moment between arrival and the first evaluation pass is covered by the Initial → Gathering → Evaluating sequence itself. No new state introduced, per the Screen Specification Template's own rule. |
| **Recommendation available** | **Recommending** | Entry: §6's "a recommendation exists" threshold is met. Never presented without Explanation and Confidence attached. |
| **Clarification (if applicable)** | **Does not apply to this screen under that name.** Recommendation has no "Clarifying" state. That term and its bounded, single-question mechanism belong exclusively to Comparison (Canonical Interaction Lexicon: "Progressive Question... Not to be confused with: Clarifying Question," which "belongs only to Comparison"). The equivalent concept here is **Gathering** — a categorically different, full, iterative, evidence-ordered process, per Recommendation Screen Contract §1's own explicit clarification distinguishing the two. |
| **Low confidence** | **Recovering** (Low-Confidence Response variant) | One of exactly two Recovering sub-conditions. Requests the single most useful next input, or offers a clearly labeled provisional answer. |
| **Recovering** | **Recovering** (Conflicting Constraints variant, included for completeness) | Entry: a stated Hard Constraint and Strong Preference together exclude every candidate. Both conflicting inputs remain visible. |
| **Completed** | **Completed** | Entry: explicit User Decision only. Terminal — no further automatic question or recommendation. |
| **Any other canonical state** | **Evaluating** | Entered every time new information arrives, including the very first. Exit: §6's thresholds are checked, routing to Recommending, back to Gathering, or into Recovering. |

*Citation: Recommendation Screen Contract (12), §8; Canonical Interaction Lexicon (17), §3 ("Clarifying Question" vs. "Progressive Question"); Screen Specification Template (18), §7.*

**Stated with the emphasis this deserves, given the explicit instruction not to simplify it:** a Trade-off or a Tie is **not** a Recovering condition under any circumstance. Both are complete, valid outcomes of the **Recommending** state. Recovering is reserved exclusively for Low-Confidence Response and Conflicting Constraints — "precisely two, and deliberately not three."

*Citation: Recommendation Screen Contract (12), §3.*

---

## 10. Validation Rules

Reproduced in full from Recommendation Screen Contract §6, as exact, testable thresholds — not condensed:

**Another question is justified when:** two or more candidates remain that are currently indistinguishable given every known Hard and Strong input, *and* the candidate question is one whose answer would actually separate them.

**Another question is forbidden when:** a single candidate already dominates on every known Hard and Strong input; *or* the remaining candidates differ only on a Soft input, in which case a Trade-off Explanation or Tie Disclosure is the correct response instead of continued probing; *or* the question would touch an input already stated; *or* no further Hard or Strong input remains to ask about, in which case Low-Confidence Response applies instead of continuing indefinitely.

**A recommendation exists when:** at least one real candidate satisfies every stated Hard Constraint, *and either* exactly one candidate dominates on every known Strong Preference, *or* multiple candidates remain but differ only on Soft Preferences — in which case the Trade-off Explanation or Tie Disclosure itself **is** the recommendation, not an absence of one.

**A recommendation does not yet exist when:** no candidate satisfies the stated Hard Constraint at all (Conflicting Constraints, not Low-Confidence); *or* too little is known to meaningfully distinguish among a large field of Hard-Constraint-satisfying candidates in any way an honest explanation could describe (Low-Confidence Response).

**Confidence must be displayed:** every time a recommendation, trade-off, or tie is shown — never optional, never deferred to a later screen or a "why" request.

**Explanation must appear:** immediately alongside every recommendation, trade-off, or tie, in the same moment it's first shown.

**System decides:** which question to ask next, if any; whether a recommendation currently exists; whether the honest resolution is a single winner or a trade-off/tie; what confidence to attach to each part of the output; when Recovery begins.

**User decides:** what to answer, or whether to answer at all; whether to accept, ask "why," or refine; which side of a trade-off to choose, or to accept a tie; when Decision Complete is reached.

*Citation: Recommendation Screen Contract (12), §6.*

**Two thresholds remain genuinely unresolved by the frozen canon and must not be filled by inference at this layer:**

1. **Ambiguous preference-type statements** — an input that could plausibly be interpreted as more than one type at once (a number that could be a budget or a size). No canonical resolution exists.
   *Citation: Recommendation Screen Contract (12), §11.*
2. **Whether the "multiple candidates remain but differ only on Soft Preferences" threshold, when it applies to three or more candidates, produces a resolvable Trade-off/Tie or requires different handling.** The underlying tie-breaker and trade-off logic this threshold depends on is worked out only for exactly two candidates anywhere in the canon; this exposure is reachable inside this screen's own Core V1 flow, independent of whether the separate Comparison Experience ships.
   *Citation: Comparison Screen Contract (14), §11; Resolution Report, Finding M3; Engineering Planning Roadmap, item 1.5.*

**Both are marked "Intentionally left unspecified by the Canonical Architecture." Neither may be resolved by design or engineering judgment at this layer — each requires a new ADR decision per the Roadmap before this specification can be finalized against it.**

---

## 11. Accessibility Considerations

**Intentionally left unspecified by the Canonical Architecture**, for the same reason established on the Home specification: the Screen Specification Template reserves this as a placeholder pending a dedicated accessibility standard not yet established anywhere in the canon.

*Citation: Screen Specification Template (18), §11.*

The one constraint statable with canonical authority: no element may be introduced for accessibility purposes beyond the nine named in Section 7. A particular consequence worth flagging for this screen specifically, given the volume of simultaneously-present information: **Confidence Communication's requirement that Hard/Strong content and Soft content remain visibly, structurally separated is a canonical content requirement, not a styling suggestion** — however this screen is built, that separation must be perceivable by whatever means the eventual accessibility standard requires, not only by visual proximity or color.

*Citation: Recommendation Framework (04), §1, §6; Recommendation Screen Contract (12), §2, §6.*

---

## 12. Copy Requirements

Exact wording remains a design/content deliverable. What follows are the requirements that wording must satisfy.

- **Confidence must be expressed in terms a person can act on, never collapsed into one blended figure.** The canon's own illustrative structure: *"I'm confident about the price and the value math; based on what you told me, this also seems to fit the style you're after"* — cited here as the required structural pattern (certain content stated separately from inferred content), not as literal mandated text.
- **Trade-offs must be framed against what the person actually said, never against what the engine assumes they'd prefer.** Canonical example of correct framing: *"this is different from your stated style, but meaningfully better value, since you didn't set a hard style limit."* Canonical example of forbidden framing: *"this is objectively the smarter pick."*
- **No invented numerical precision** — no false-sounding match percentages or similar fabricated figures, in confidence statements or trade-off descriptions alike.
- **A genuine tie must be stated plainly as a tie** — "these are equivalent on everything you've told me matters" is a complete, honest answer, never softened into an apology or a forced pick.
- **Forbidden terms, per the Canonical Interaction Lexicon:** "Score" or "Rating," anywhere. Bare, unqualified "Best." "Suggest" in place of "Recommend" where Recommendation's actual reasoning applies. "Match" or "Fit" as a noun standing in for the outcome. "Personalize/Personalization" used loosely.
- **A trivial difference between options must never be presented as a trade-off worth weighing.**

*Citation: Recommendation Framework (04), §4, §6, §7; Canonical Interaction Lexicon (17), §3, §5.*

---

## 13. Edge Cases

**An input ambiguous between two preference types (e.g., a number that could be a budget or a size).** No canonical resolution exists. **Intentionally left unspecified by the Canonical Architecture; pending ADR resolution.**
*Citation: Recommendation Screen Contract (12), §11.*

**Three or more candidates remaining after every Hard and Strong input is applied, differing only on a Soft Preference.** The Trade-off/Tie logic this screen's own §6 threshold calls for in this situation is worked out only for exactly two candidates anywhere in the canon. **Intentionally left unspecified by the Canonical Architecture; pending ADR resolution.**
*Citation: Comparison Screen Contract (14), §11; Resolution Report, Finding M3.*

**Whether occasion, once volunteered (never solicited), is recognized and weighted as a Soft Preference, or excluded from V1 reasoning entirely.** Decision Engine Model §4 and Recommendation Framework §2 describe it as a live input; Feature Inventory §5 defers "occasion as an input" to Future. **Intentionally left unspecified by the Canonical Architecture; pending ADR resolution.**
*Citation: Resolution Report, Finding M2; Engineering Planning Roadmap, item 1.3.*

**Budget changed mid-flow.** This is fully resolved, not a gap: it can genuinely invalidate a prior recommendation, since a Hard Constraint can never be violated — but any stated Strong or Soft Preferences are preserved; only the budget-driven candidate set is recomputed.
*Citation: Experience Flows (09), §5.*

**A stated budget and a stated Strong Preference together exclude every real candidate.** Fully resolved: Conflicting Constraints fires, naming both tension-producing inputs, never silently discarding one in favor of the other.
*Citation: Recommendation Screen Contract (12), §11.*

**A person accepts a Planning Mode recommendation, then returns closer to the actual purchase for a firmer answer.** Fully resolved: this is a legitimate re-entry into the same flow without Planning Mode attached, not a restart and not a contradiction of the earlier, more conservative answer.
*Citation: Experience Flows (09), §2.*

**A Trade-off or Tie is mistakenly treated as a failure requiring further probing.** This must never occur — both are complete answers, and no further question may be asked once the honest resolution is a Trade-off or Tie rather than a single winner.
*Citation: Recommendation Screen Contract (12), §3, §6.*

---

## 14. Analytics Candidates

Following the same convention established for Home: names only, no schema, properties, or tooling defined, per the Screen Specification Template's placeholder discipline.

*Citation: Screen Specification Template (18), §12.*

- Screen viewed (Recommendation reached)
- Progressive question presented, by dimension
- Progressive question answered
- Preference refined mid-flow
- Recommendation produced (winner)
- Trade-off Explanation produced
- Tie Disclosure produced
- Low-Confidence Response triggered
- Conflicting Constraints triggered
- Explanation requested ("why")
- Recommendation accepted (Decision Complete)
- Comparison requested from a surfaced trade-off/tie
- Beer Detail requested for the recommended SKU
- Planning Mode engaged
- Proxy-Buying Mode engaged

*Citation: Screen Specification Template (18), §12 ("plausible future telemetry candidates, without naming actual event schemas").*

---

## 15. Non-functional Requirements

**Intentionally left unspecified by the Canonical Architecture** for responsiveness, performance budgets, offline behavior, and platform expectations — none are addressed anywhere in the canon.

*Citation: Review Guide (00), §2; ADR (19), §7.*

The one grounded, citable fact: this screen's Referenced Information requires the full Beer Knowledge Base catalog and, where available, the Style Benchmark. Style Benchmark is an Important-Soon-After Platform Service, not Core V1 — this screen must therefore degrade gracefully in its absence, presenting Alcohol-Adjusted Value as an absolute figure without relative-standing percentile, never treating the Benchmark's absence as a missing required element.

*Citation: Recommendation Screen Contract (12), §3; Feature Inventory (07), §5; Content Architecture (10), §9.*

---

## 16. Acceptance Criteria

Restated directly from Recommendation Screen Contract §12:

✓ No question is ever asked whose answer could not change which candidate is recommended.
✓ A recommendation is never withheld solely because occasion, brand, or another Soft input is missing.
✓ Every recommendation, trade-off, or tie carries its Explanation and its Confidence at the moment it first appears, not afterward.
✓ A Trade-off or Tie is never presented as, or treated as, a recovery condition.
✓ A stated Hard Constraint is never silently overridden, in any recommendation this screen produces.
✓ No more than one question is ever active at a time.
✓ Decision Complete is only ever reached through an explicit User Decision, never inferred from inaction or automatically advanced.
✓ Confidence is never expressed as a single blended figure across Hard/Strong and Soft content.
✓ Planning Mode's standing caveat appears from the first response through every subsequent one, never collapsed to a single disclaimer.
✓ Proxy-Buying Mode's conservative default is never presented at the same confidence as an ordinary self-purchase recommendation.

*Citation: Recommendation Screen Contract (12), §12; Experience Flows (09), §8 (Principles 5, 11).*

---

## 17. Traceability Matrix

| Specification Section | Canonical Source(s) |
|---|---|
| 1. Screen Purpose | Recommendation Screen Contract §1 |
| 2. User Goals | User Interaction Model §1; Decision Engine Model §2 |
| 3. Entry Conditions | Recommendation Screen Contract §3; Navigation Contract §4, §6 |
| 4. Exit Conditions | Recommendation Screen Contract §4, §6, §7; Navigation Contract §6 |
| 5. Information Hierarchy | Content Architecture §2, §3; Recommendation Screen Contract §5; Canonical Interaction Lexicon §3 |
| 6. Screen Sections | Recommendation Screen Contract §5, §6, §7, §8 |
| 7. Every UI Element | Recommendation Screen Contract §2, §5, §6, §7; Decision Engine Model §4; Experience Flows §8 |
| 8. User Interactions | Recommendation Screen Contract §7; Feature Inventory §1; Review Guide §2 |
| 9. States | Recommendation Screen Contract §3, §8; Canonical Interaction Lexicon §3 |
| 10. Validation Rules | Recommendation Screen Contract §6, §11; Comparison Screen Contract §11; Resolution Report M2, M3 |
| 11. Accessibility Considerations | Screen Specification Template §11; Recommendation Framework §1, §6 |
| 12. Copy Requirements | Recommendation Framework §4, §6, §7; Canonical Interaction Lexicon §3, §5 |
| 13. Edge Cases | Recommendation Screen Contract §11; Comparison Screen Contract §11; Experience Flows §2, §5; Resolution Report M2, M3 |
| 14. Analytics Candidates | Screen Specification Template §12 |
| 15. Non-functional Requirements | Review Guide §2; ADR §7; Feature Inventory §5; Content Architecture §9 |
| 16. Acceptance Criteria | Recommendation Screen Contract §12; Experience Flows §8 |

---

## Document Notes

Two items in this specification are marked unresolved rather than filled: ambiguous preference-type handling (already an open item in the frozen Screen Contract itself) and the occasion/beyond-two-candidate questions carried forward from the Resolution Report. Neither is a gap introduced by this document — both were already open before this specification was written, and both remain exactly as open after it.
