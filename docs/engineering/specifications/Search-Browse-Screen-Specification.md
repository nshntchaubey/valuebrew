# ValueBrew — Engineering Screen Specification: SEARCH / BROWSE RESULTS

**Document type:** Engineering Screen Specification (not a Screen Contract).
**Implements:** Search/Browse Results Screen Contract, in full.
**Built under:** the Canonical Screen Specification Template's citation discipline — every field filled by citation or explicitly marked unspecified.
**Consumers:** UI/UX design, Flutter engineering, QA engineering.
**Version:** 1.0.
**Status:** Draft, pending engineering review. Contains one previously-acknowledged open gap (candidate list revalidation on backward entry) — see §10 and §13.

---

## 1. Screen Purpose

Search/Browse Results presents candidate SKUs matching a query or browse selection, and lets a person move to a specific one. It is the resolution screen for Beer/SKU Identification — Home initiates this Experience, this screen completes it — and it never performs any reasoning of its own.

*Citation: Search/Browse Results Screen Contract, §1.*

---

## 2. User Goals

- "I know roughly what I'm looking for" — searching toward a specific, already-imagined beer.
- "I don't have an anchor" — browsing without a fixed target.
- "I want to compare beers" — a comparison intent, resolved here through the same query mechanism as any other search, per the approved routing clarification carried forward from Home.

*Citation: Information Architecture (08), §5; Search/Browse Results Screen Contract, §2.*

---

## 3. Entry Conditions

| Condition | Known state on arrival |
|---|---|
| **Fresh arrival from Home**, a new query or browse selection expressed | The query or browse criteria; any Preference Summary already established at Home |
| **Backward navigation from Beer Detail**, where this screen was the originating screen | The previously-established candidate list, restored rather than re-queried |

*Citation: Search/Browse Results Screen Contract, §3, §7.*

This screen has no other entry path and performs no reasoning before rendering — it matches, it does not evaluate.

*Citation: Search/Browse Results Screen Contract, §2 MUST NEVER.*

---

## 4. Exit Conditions

| Trigger | Destination |
|---|---|
| Exactly one candidate selected | Beer Detail — carrying that one resolved SKU |
| Two or more candidates selected | Comparison — carrying the full selected set, never partial |
| Zero candidates match the query or browse selection | Back to Home — Recovering state, Preference Summary intact |
| Explicit statement of a new, unrelated intent | Back to Home |

*Citation: Search/Browse Results Screen Contract, §2, §4, §7.*

**This screen never itself reaches Decision Complete.** Its composition always routes onward, by design — consistent with Home's own non-terminal nature.

*Citation: Content Architecture (10), §3; Search/Browse Results Screen Contract, §5, §8.*

---

## 5. Information Hierarchy

Directly citing the Screen Contract's own Section 5, itself a direct citation of Content Architecture §3, without redesign:

- **Primary:** Beer Identity, abbreviated, per candidate.
- **Supporting:** enough Legal Price or Alcohol-Adjusted Value to distinguish candidates at a glance, where available.
- **Contextual:** the query or browse criteria that produced these candidates.
- **Confidence:** minimal — Beer Identity is Verified and uniformly high; nothing here is inferred.
- **Recovery:** "no beer identified," if nothing matches.
- **Completion:** not applicable; this composition always routes onward.

*Citation: Content Architecture (10), §3; Search/Browse Results Screen Contract, §5.*

**Stated with the emphasis the "routing layer, not a recommendation engine" framing requires:** the Supporting figure (Legal Price or Alcohol-Adjusted Value) is shown to help distinguish candidates — it is never used to rank, sort by implied quality, or otherwise evaluate them. Nothing on this screen constitutes a judgment about which candidate is better. That reasoning belongs exclusively to Recommendation or Comparison, never here.

*Citation: Search/Browse Results Screen Contract, §2 MUST NEVER; Information Architecture (08), §3.*

---

## 6. Screen Sections

Two functional sections, deliberately minimal, matching this screen's bounded role:

**A. Candidate List** — Beer Identity per candidate, plus the permitted supporting figure where available, plus the originating query or browse criteria as context. Present from the moment candidates are found or restored.

**B. Recovery** — "no beer identified," visible only when zero candidates match.

*Citation: Search/Browse Results Screen Contract, §5, §7, §8.*

**How these sections are visually arranged, and whether Search-originated and Browse-originated candidates are visually distinguished, is a design decision. Intentionally left unspecified by the Canonical Architecture.**

*Citation: Information Architecture (08), §8.*

---

## 7. Every UI Element

| Element | Purpose | Required Data | Optional Data | Visibility Rule |
|---|---|---|---|---|
| **Candidate List Display** | Show every matching candidate's abbreviated identity | Beer Identity, abbreviated, per candidate | Legal Price or Alcohol-Adjusted Value per candidate, where available | Visible once candidates are found (new query) or restored (backward entry from Beer Detail) |
| **Query/Browse Criteria Display** | Show what produced this candidate list | The query or browse criteria as carried from Home | — | Visible alongside the Candidate List whenever it's present |
| **Single Selection Mechanism** | Select exactly one candidate, resolving toward Beer Detail | — | — | Available once at least one candidate is present |
| **Multi-Selection Mechanism** | Select two or more candidates, resolving toward Comparison | — | — | Available once at least two candidates are present |
| **Abandon Action** (MAY) | Let the person state a new, unrelated intent, returning to Home | — | — | Optional; presence and form left to design, per the Screen Contract's own MAY allowance |
| **"No Beer Identified" Recovery Display** | Communicate that nothing matched, and return to Home | — | — | Only in the Recovering state |

*Citation: Search/Browse Results Screen Contract, §2, §5, §7.*

**No element beyond these six is permitted.** In particular, no element may imply a ranking, a "best match," or any other evaluative framing — this screen assembles candidates; it does not judge them.

---

## 8. User Interactions

| Canonical action | Detail |
|---|---|
| **Arrive with a query or browse selection** | Candidates are matched against the Beer Knowledge Base. No content is presented before matching completes. |
| **Select one candidate** | Hands off to Beer Detail, carrying that one resolved SKU and any Preference Summary. |
| **Select multiple candidates** | Hands off to Comparison, carrying the full selected set and any Preference Summary — never fewer than what was actually selected. |
| **Return via backward navigation from Beer Detail** | The previously-established candidate list is restored, without re-executing the query. |
| **Abandon for a new, unrelated intent** | Returns to Home. |

*Citation: Search/Browse Results Screen Contract, §7.*

**Interaction modality — how a query is entered, how candidates are selected — is not specified anywhere in the canon.** Search and Browse are themselves Mechanisms, "never canonically mandated," and neither this screen's own contract nor any upstream document names a specific input modality. **Intentionally left unspecified by the Canonical Architecture.** No long-press or gesture behavior beyond selection is canonically defined.

*Citation: Feature Inventory (07), §1; Review Guide (00), §2.*

---

## 9. States

Mapped exhaustively onto the Screen Contract's own State Machine. No new state introduced.

| Requested category | Canonical mapping | Notes |
|---|---|---|
| **Initial** | **Querying** | Entry: arrival from Home with a new query or browse selection. Exit: candidates resolve, found or not. |
| **Loading (only if canonically justified)** | **Justified — maps directly to Querying** | Unlike Home or Recommendation, this screen's transitional matching moment is itself a named canonical state, since resolving a query or browse selection against the catalog is exactly the operation Querying exists to cover. No separate state is invented; the existing one already serves this purpose. |
| **Populated** | **Results** | Entry: one or more candidates found from a new query/browse selection, or restored from backward navigation out of Beer Detail. |
| **Empty results** | **Recovering** | Entry: the query or browse selection yields zero matching candidates — the "no beer identified" condition. |
| **Unavailable** | **No canonical concept beyond "empty results" exists.** A broader technical unavailability (service failure, network loss) is not addressed anywhere in the canon. **Intentionally left unspecified by the Canonical Architecture.** |
| **Recovering (if applicable)** | **Recovering** — the same single canonical state as "Empty results," above | Both requested categories collapse to one canonical state, consistent with the pattern established across the other four specifications. |
| **Completed (if applicable)** | **Not applicable — by design.** | This screen never reaches Decision Complete; its composition always routes onward, per Content Architecture's own explicit statement. |
| **Any other canonical state** | **Handoff-Pending** | Entry: an explicit selection has been made — one candidate, or two or more. Exit: successful transition to Beer Detail or Comparison. |

*Citation: Search/Browse Results Screen Contract, §8; Content Architecture (10), §3; Screen Specification Template (18), §7.*

---

## 10. Validation Rules

- Every selection must resolve to one or more specific, catalog-known SKUs before any hand-off — a selection is never passed onward unresolved.
- Exactly one candidate selected resolves to Beer Detail; two or more resolves to Comparison — never an ambiguous or partial outcome.
- A query naming two or more specific beers at once is treated as an ordinary, valid basis for multi-select-eligible candidates — never rejected as unsupported, never routed as if it were a Recommendation or Verification intent.
- Any Preference Summary present at arrival must remain present at whichever screen this one hands off to.
- Zero matching candidates always returns to Home's Recovering state — never an invented substitute, never a silent dead end.
- No candidate may be added to a hand-off set beyond what was actually selected.
- Full SKU detail never appears on this screen, under any condition.
- Observed/Charged Price never appears on this screen, under any condition.
- No search, browse, or selection action is ever gated behind login or an account.
- Nothing about this screen's state persists across separate sessions.
- This screen never performs Full Recommendation synthesis, Price Verification computation, or Comparison's own tie-breaking or trade-off reasoning — it matches candidates against a query; it does not evaluate them.

*Citation: Search/Browse Results Screen Contract, §2, §6, §10.*

**Genuinely unresolved by the frozen canon — must not be filled by inference at this layer:** whether the candidate list restored on backward navigation from Beer Detail should be revalidated against the catalog first, or simply redisplayed as last known. **Intentionally left unspecified by the Canonical Architecture; flagged in the Screen Contract itself as pending a future decision.**

*Citation: Search/Browse Results Screen Contract, §11.*

---

## 11. Accessibility Considerations

**Intentionally left unspecified by the Canonical Architecture**, per the Screen Specification Template's placeholder discipline.

*Citation: Screen Specification Template (18), §11.*

The one constraint statable with canonical authority: no element may be introduced beyond the six named in §7. Worth flagging for this screen specifically: since single- and multi-selection are governed by different downstream consequences (Beer Detail versus Comparison), whatever accessible presentation is eventually built must make that distinction perceivable at the moment of selection, not only after the hand-off has already occurred.

*Citation: Search/Browse Results Screen Contract, §2, §6.*

---

## 12. Copy Requirements

Exact wording remains a design/content deliverable. What follows are the requirements that wording must satisfy.

- **No evaluative language of any kind** — no "best match," no "top pick," no implied ranking. This screen states what matched; it never characterizes how good a match is.
- **No catalog-specific content beyond abbreviated identity and the permitted supporting figure** — no full detail, no Observed/Charged Price, ever.
- **No invented substitute may be offered or implied when nothing matches** — the recovery message states the fact plainly.
- **No forbidden terms, per the Canonical Interaction Lexicon:** "Score" or "Rating," anywhere. "Suggest" or "Recommend," in any form — this screen recommends nothing.

*Citation: Search/Browse Results Screen Contract, §2, §5; Canonical Interaction Lexicon (17), §3, §5.*

---

## 13. Edge Cases

**Whether a restored candidate list (backward navigation from Beer Detail) should be revalidated against the catalog.** Already an explicitly flagged open gap in the frozen Screen Contract itself. **Intentionally left unspecified by the Canonical Architecture; pending future ADR resolution.**
*Citation: Search/Browse Results Screen Contract, §11.*

**A query naming only one beer.** Fully resolved, not a gap: this is an ordinary search, not a comparison intent — it resolves to Beer Detail on a single match, exactly like any other search.
*Citation: Search/Browse Results Screen Contract, §6.*

**Candidates produced by Search versus Browse mechanisms shown together.** Fully resolved: both are accepted equally, presented within a single shared composition, with no requirement to visually distinguish their origin.
*Citation: Information Architecture (08), §8; Search/Browse Results Screen Contract, §2 MAY.*

**Changing or refining a query or selection before confirming a hand-off.** The exact interaction mechanics of adjusting a selection before it's finalized are not addressed — the canon defines the resolved outcome of a selection, not the moment-to-moment mechanics of building one. **Intentionally left unspecified by the Canonical Architecture.**

**A person searches, then separately browses, accumulating candidates across two distinct query attempts.** Not addressed anywhere in the canon — whether this constitutes one evolving candidate set or requires starting over is undecided. **Intentionally left unspecified by the Canonical Architecture.**

---

## 14. Analytics Candidates

Names only, no schema, properties, or tooling defined, per the Screen Specification Template's placeholder discipline.

*Citation: Screen Specification Template (18), §12.*

- Screen viewed (Search/Browse Results reached, by query or browse origin)
- Candidates found (count)
- No candidates found ("no beer identified" recovery shown)
- Single candidate selected (Beer Detail hand-off)
- Multiple candidates selected (Comparison hand-off)
- Backward navigation received from Beer Detail
- Abandoned for a new, unrelated intent (return to Home)

*Citation: Screen Specification Template (18), §12.*

---

## 15. Non-functional Requirements

**Intentionally left unspecified by the Canonical Architecture** for responsiveness, performance budgets, offline behavior, and platform expectations.

*Citation: Review Guide (00), §2; ADR (19), §7.*

The one grounded, citable fact: this screen's Referenced Information requires the Beer Knowledge Base to match candidates — unlike Home, this screen has a real catalog data dependency from the moment it's entered.

*Citation: Search/Browse Results Screen Contract, §9.*

---

## 16. Acceptance Criteria

Restated directly from the Search/Browse Results Screen Contract §12:

✓ A selection of exactly one candidate always transitions to Beer Detail; a selection of two or more always transitions to Comparison — never a mixed or partial outcome.
✓ No candidate is ever added to a hand-off set beyond what was actually selected.
✓ Full SKU detail never appears on this screen under any condition.
✓ Observed/Charged Price never appears on this screen under any condition.
✓ A query naming multiple beers is treated as an ordinary basis for multi-select into Comparison, never as unsupported.
✓ Zero matching candidates always returns to Home's Recovering state, never an invented substitute.
✓ Any Preference Summary present at arrival is still present at whichever screen this one hands off to.
✓ A backward navigation from Beer Detail restores the prior candidate list without re-querying.
✓ Nothing about this screen's state persists across separate sessions.
✓ This screen never reaches Decision Complete on its own.

*Citation: Search/Browse Results Screen Contract, §12.*

---

## 17. Traceability Matrix

| Specification Section | Canonical Source(s) |
|---|---|
| 1. Screen Purpose | Search/Browse Results Screen Contract §1 |
| 2. User Goals | Information Architecture §5; Search/Browse Results Screen Contract §2 |
| 3. Entry Conditions | Search/Browse Results Screen Contract §3, §7 |
| 4. Exit Conditions | Search/Browse Results Screen Contract §2, §4, §7, §8; Content Architecture §3 |
| 5. Information Hierarchy | Content Architecture §3; Search/Browse Results Screen Contract §5; Information Architecture §3 |
| 6. Screen Sections | Search/Browse Results Screen Contract §5, §7, §8; Information Architecture §8 |
| 7. Every UI Element | Search/Browse Results Screen Contract §2, §5, §7 |
| 8. User Interactions | Search/Browse Results Screen Contract §7; Feature Inventory §1; Review Guide §2 |
| 9. States | Search/Browse Results Screen Contract §8; Content Architecture §3; Screen Specification Template §7 |
| 10. Validation Rules | Search/Browse Results Screen Contract §2, §6, §10, §11 |
| 11. Accessibility Considerations | Screen Specification Template §11; Search/Browse Results Screen Contract §2, §6 |
| 12. Copy Requirements | Search/Browse Results Screen Contract §2, §5; Canonical Interaction Lexicon §3, §5 |
| 13. Edge Cases | Search/Browse Results Screen Contract §6, §11; Information Architecture §8 |
| 14. Analytics Candidates | Screen Specification Template §12 |
| 15. Non-functional Requirements | Review Guide §2; ADR §7; Search/Browse Results Screen Contract §9 |
| 16. Acceptance Criteria | Search/Browse Results Screen Contract §12 |

---

## Document Notes

This is the smallest and most tightly bounded specification of the six produced so far — six UI elements against Recommendation's nine or Comparison's fourteen — and that's a direct, intended consequence of this screen's role as a routing layer rather than a reasoning one. Every place this document was tempted to add evaluative language (a "best match" label, an implied ranking by value) was deliberately declined, consistent with the Screen Contract's own absolute prohibition on this screen ever performing recommendation, verification, or comparison reasoning itself.
