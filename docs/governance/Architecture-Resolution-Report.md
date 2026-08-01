# ValueBrew — Architecture Resolution Report

**Produced by:** Architecture Review Board, following independent re-validation of the External Reviewer's findings.
**Subject:** Disposition of findings C1, M1, M2, M3, M4 against the nineteen-document canon.
**Purpose:** Record what the Board decided, where each accepted item must be edited, and whether the canon can be frozen as Canonical Architecture v1.0 once those edits are made.

This report records outcomes only. It does not draft replacement prose for any canonical document — per the canon's own discipline, that belongs to whoever holds the pen on the affected document, cited against this report the way every existing decision is cited against the ADR.

---

## 1. Final Findings Summary

| ID | Reviewer's original call | Board's final classification | Final severity | Verdict | Blocks v1.0 freeze? |
|---|---|---|---|---|---|
| C1 | Critical — capability undeliverable | Documentation clarity issue | Major | ⚠️ Accept with clarification | No, but should close before freeze |
| M1 | Major — citation drift | Documentation clarity issue | Minor | ⚠️ Accept with clarification | No |
| M2 | Major — cross-document contradiction | Documentation clarity issue (unresolved ambiguity, not contradiction) | Major | ⚠️ Accept with clarification | No, but should close before freeze |
| M3 | Major — reachable gap | Genuine architectural defect | Major | ✅ Accept | **Yes** |
| M4 | Major — stale claim | Documentation synchronization issue | Major | ✅ Accept | No |

All five findings are accepted in some form. None were discarded. Two were downgraded from the original review's framing (C1: Critical → Major; M1: Major → Minor); one was reclassified in *kind* without a severity change (M2: contradiction → ambiguity, still Major); two were confirmed unchanged (M3, M4).

---

## 2. Resolution Entries

Each entry below follows the canon's own Decision-record format (Context / Decision / Consequences), extended with the two fields this exercise specifically requires: exact update location, and freeze impact.

---

### C1 — Home's comparison-routing path is real but nowhere stated as one path

**Context:** Home Screen Contract commits, in its own Failure Conditions and Acceptance Criteria, to telling out-of-scope users that comparing beers is a supported capability. On reread, a complete resolution path exists without inventing anything — Home's own "Initiate Search or Browse" trigger, Information Architecture's Search/Browse Results entry ("select multiple to enter Comparison directly"), and Feature Inventory's own listing of "Search results" as a Beer Comparison entry point together form a citation-backed chain. No document currently states that chain as a single, named sequence.

**Board Decision:** Accept as a documentation clarity issue. The capability is deliverable through existing rules; what's missing is a single, explicit statement tying three already-correct rules together, in the same spirit as the Screen Specification Template's own citation discipline.

**Exact Update Location:**
- **Primary:** Home Screen Contract (11), **Section 7 — Interaction Contract**, "Initiate Search or Browse" entry. Add an explicit clause naming a comparison-intent statement (two or more beers named at once) as a qualifying instance of "a query or browse selection is expressed," with a citation to Information Architecture Section 2 (Search/Browse Results) and Feature Inventory Section 4 (Beer Comparison entry points).
- **Secondary:** Home Screen Contract (11), **Section 13 — Validation**. Add a resolution note in the same style already used there for the unsupported-intent gap ("This resolves what an earlier version of this contract left as an open gap"), so the closure is recorded the way every other resolved gap in this document already is.

**Consequences once resolved:** The Search/Browse Results gap (ADR Section 7) is no longer implicated by a Home-level promise; it remains an open gap for its own, smaller reason (its own Screen Contract still doesn't exist), not because Home depends on it silently.

**Freeze impact:** Does not block freeze on its own — no invented behavior is required to ship correctly today — but should close before freeze so the frozen baseline doesn't carry a promise with an implicit, unstated resolution.

---

### M1 — Screen Contract header wording overstates what Section 9 documents

**Context:** Beer Detail, Comparison, and Price Verification each open with "Derived entirely from the ten frozen documents **plus** [named prior Screen Contracts]," but Section 9 in each case lists only load-bearing rule dependencies — a convention Home Screen Contract itself already establishes correctly, by explicitly marking two of its own ten foundational citations "not directly." The convention was applied consistently across all five contracts; only the header's phrasing implies a stronger, fuller citation guarantee than Section 9 was ever designed to provide.

**Board Decision:** Accept as a documentation clarity issue, narrowly scoped to wording. No synchronization actually failed.

**Exact Update Location:**
- Beer Detail Screen Contract (13), **header line** (the descriptive line beneath the title).
- Comparison Screen Contract (14), **header line**.
- Price Verification Screen Contract (15), **header line**.
- All three: soften "Derived entirely from... plus the [Screen Contracts]" to distinguish sequencing citation ("written after, and consistent with") from rule-dependency citation (what Section 9 actually enumerates), matching the precision Home's own Section 9 already models.

**Consequences once resolved:** Header language and Section 9 content agree in what they each claim, closing the only mechanically-checkable inconsistency this review found.

**Freeze impact:** Does not block freeze — cosmetic, and the cheapest fix of the five. Recommended to close before freeze anyway, given its near-zero cost.

---

### M2 — Whether "occasion" is actively solicited or only passively recognized in V1

**Context:** Decision Engine Model and Recommendation Framework describe occasion as a live input inside the full conceptual reasoning model. Feature Inventory defers "occasion as an input within Preference Input Handling" to Future. Recommendation Screen Contract's MUST rules presuppose occasion is already recognizable. The canon has a precedent for reconciling exactly this shape of tension — Trade-off/Tie-handling stays Core as an Engine Behavior while the standalone Comparison Experience wrapping it is staged to Important-Soon-After, with Feature Inventory explicitly stating "these are not the same commitment." That precedent plausibly extends to occasion (Soft Preference recognition stays Core; *active solicitation* of occasion is what's deferred) — but, unlike the Comparison case, the canon never states this reconciliation for occasion specifically, and it demonstrably knows how, having flagged the adjacent Contextual Signals category as "currently empty in practice" in the same document.

**Board Decision:** Accept as an unresolved ambiguity requiring one explicit decision, not a genuine contradiction requiring reconciliation of opposing rules. Held at Major severity because the two plausible readings produce materially different Recommendation-screen behavior.

**Exact Update Location:**
- **Primary:** Architectural Decisions Record (19), **Section 3 — Major Architectural Decisions**. Add a new entry, in the existing Context / Decision Made / Alternatives Considered / Consequences format, stating explicitly whether occasion is (a) recognized as a Soft Preference only if volunteered, never solicited, in V1, or (b) fully absent from V1's reasoning until promoted. This is the correct home for the decision, matching how the canon already resolved the structurally identical Comparison-vs-Trade-off/Tie-handling tension.
- **Secondary:** Feature Inventory (07), **Section 5**, Core V1 bullet for Preference Input Handling — add a citation to the new ADR entry.
- **Secondary:** Recommendation Screen Contract (12), **Section 2** (MUST / MUST NEVER entries referencing occasion) — add the same citation.

**Consequences once resolved:** Recommendation's own state machine has a settled answer for whether occasion ever enters Preference Summary in V1, closing the one finding in this review capable of producing genuinely different implementations from five different engineers.

**Freeze impact:** Does not require inventing new behavior to close, but does require someone to make a real product-scope call that the canon has deliberately never delegated to a lower layer. Should close before freeze — this is exactly the category of decision the canon's own "never invent behavior at lower layers" rule says must be made explicitly, at the ADR layer, before implementation begins.

---

### M3 — Recommendation's own tie-break/trade-off logic is undefined past two candidates

**Context:** Comparison Screen Contract's Section 11 already names the beyond-two-candidates gap, and correctly scopes it as spanning "every worked example of comparison reasoning across the ten frozen documents" — not a Comparison-only problem. Recommendation Screen Contract's own Section 6 threshold for "a recommendation exists" permits multiple remaining candidates differing only on Soft Preferences, with no cap on candidate count, meaning this exact gap is reachable inside Core V1's Recommendation flow. Recommendation's own Section 11 — otherwise the most thorough Failure Conditions list in the canon, naming even a narrow gap like ambiguous preference typing — does not list this exposure.

**Board Decision:** Accept as a genuine architectural defect. This is the one finding where no citation-backed resolution path exists anywhere in the current text; an implementer hitting three close candidates inside Recommendation has nothing to build from without inventing behavior the canon explicitly says must not be invented at this layer.

**Exact Update Location:**
- **Primary:** Recommendation Screen Contract (12), **Section 11 — Failure Conditions**. Add a fourth entry — analogous in form to the three already present — naming the beyond-two-candidates exposure as it occurs inside Recommendation specifically, cross-cited to Comparison Screen Contract's Section 11 entry for the same underlying gap.
- **Secondary:** Architectural Decisions Record (19), **Section 7 — Known Limitations**. Amend the existing "Comparison logic beyond two candidates is unresolved" entry to state explicitly that this gap is reachable from both the Comparison Experience and Recommendation's own Core V1 synthesis path, correcting the current framing that scopes it to Comparison alone.

**Consequences once resolved:** The gap remains open (a genuine, not-yet-decided product question about three-or-more-candidate reasoning), but it becomes an *acknowledged*, correctly-scoped open gap rather than a silent one — bringing it in line with the canon's own standard for how every other open gap is handled.

**Freeze impact:** **Blocks freeze.** This is the only finding where the fix required is not solely documentation — closing the citation gap (adding it to Section 11) makes the limitation honestly visible, but the underlying behavioral question (what should Recommendation actually do with three close candidates) still needs a real decision before this path can be implemented without invention. The canon may freeze with this decision still *open*, exactly as it already does for the other five acknowledged gaps — but only if Recommendation's own Section 11 is updated first to admit the gap exists there. Freezing without that update would mean shipping a document that doesn't yet know about its own most reachable failure mode.

---

### M4 — Experience Flows still states a confidence claim Price Verification has already corrected

**Context:** Experience Flows states the Price Verification flow carries "the highest, most uniform Confidence Communication anywhere in the canon." Price Verification Screen Contract explicitly identifies this as an oversimplification and replaces it with three separated confidence dimensions, naming the correction in its own text. Price Verification Screen Contract is authoritative and correct; Experience Flows was simply never revised to match.

**Board Decision:** Accept as a documentation synchronization issue. The underlying behavior was never actually in dispute between the two documents — only the written claim in the earlier one has gone stale.

**Exact Update Location:**
- Experience Flows (09), **Section 2**, Price Verification flow entry — the "Cross-cutting" field's confidence characterization. Replace "the highest, most uniform Confidence Communication anywhere in the canon" with a forward citation to Price Verification Screen Contract Section 6's three-dimension model, matching that document's own language rather than restating a now-superseded summary.

**Consequences once resolved:** No document in the canon makes an unrevised claim that a later, more specific document has already corrected — closing the one place this review found where the "no document may reinterpret one frozen before it" principle was, in effect, broken in one direction without being reconciled in the other.

**Freeze impact:** Does not block freeze — Price Verification Screen Contract, the document any implementer actually builds against, already carries the correct rule. Low priority; can be closed opportunistically, before or shortly after freeze.

---

## 3. Freeze Confirmation

**Once the following five edits are made, the Board confirms the architecture can be frozen as Canonical Architecture v1.0:**

1. Home Screen Contract (11), Sections 7 and 13 — name the comparison-intent routing path (C1).
2. Beer Detail (13), Comparison (14), Price Verification (15) — soften header citation wording to match Section 9 (M1).
3. Architectural Decisions Record (19) Section 3, with downstream citations in Feature Inventory (07) Section 5 and Recommendation Screen Contract (12) Section 2 — record the occasion-recognition decision (M2).
4. Recommendation Screen Contract (12) Section 11, and Architectural Decisions Record (19) Section 7 — admit the beyond-two-candidates gap is reachable from Recommendation, not only Comparison (M3).
5. Experience Flows (09) Section 2 — replace the superseded confidence claim with a citation to Price Verification's corrected model (M4).

**Basis for this confirmation:** After the Board's re-validation, only one finding (M3) constitutes a genuine defect requiring behavior an implementer cannot currently derive from the text without inventing it — and even that finding does not require the underlying product question to be *answered* before freeze, only *acknowledged* in the same place every other open question in this canon already is. The other four findings are documentation-quality issues: two clarify wording that already resolves cleanly on close reading (C1, M1), one records a real but freeze-compatible decision the canon has already shown it knows how to make explicit (M2), and one closes a stale claim that never affected actual implementation behavior (M4).

This mirrors the canon's own established precedent exactly: Canonical Architecture v1.0 was never going to freeze with zero open questions — it already carries five self-acknowledged gaps in the Architectural Decisions Record, Section 7, and the repository's own status is "Frozen for External Review," not "complete." What freeze requires, by the canon's own standard, is not the absence of open questions — it's that every open question is *named*, in the correct document, rather than sitting undiscovered in the gap between two documents that each assume the other has it covered. Once the five edits above are made, that standard is met for all five findings raised in this review, and the Board sees no remaining basis to withhold freeze.
