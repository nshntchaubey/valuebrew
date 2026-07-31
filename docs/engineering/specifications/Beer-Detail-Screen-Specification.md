# ValueBrew — Engineering Screen Specification: BEER DETAIL

**Document type:** Engineering Screen Specification (not a Screen Contract).
**Implements:** Beer Detail Screen Contract (13), in full.
**Built under:** the Canonical Screen Specification Template's citation discipline — every field filled by citation or explicitly marked unspecified.
**Consumers:** UI/UX design, Flutter engineering, QA engineering.
**Version:** 1.0.
**Status:** Draft, pending engineering review. Contains one flagged cross-document inconsistency requiring architecture-layer attention before final sign-off — see §4 and §13.

---

## 1. Screen Purpose

Beer Detail presents everything known about one already-identified SKU, completely enough that the person can confidently understand it before deciding what to do next. It is the canonical home for a SKU's Verified and Computed Facts, and, when an anchor situation applies, the surfaced Confirm-as-Is judgment.

*Citation: Beer Detail Screen Contract (13), §1.*

---

## 2. User Goals

- "I'm holding this / I already have one in mind" — arriving with a specific SKU already identified, wanting a complete, confident picture of it.
- Wanting to know, without having asked directly, whether this already-identified beer is already the strongest available fit.

*Citation: User Interaction Model (06), §1; Information Architecture (08), §2.*

---

## 3. Entry Conditions

| Condition | Known state on arrival |
|---|---|
| **Identified SKU already resolved** — the sole precondition for this screen to load at all | The specific SKU. Nothing else is guaranteed. |
| **Entry context** (how this SKU was reached) | Determines whether an anchor situation applies — see §6 and §9. The precise determining rule is an open architectural gap, not resolved by this specification. |

*Citation: Beer Detail Screen Contract (13), §3.*

This screen has no other precondition. It performs no progressive gathering and requests nothing before rendering.

*Citation: Beer Detail Screen Contract (13), §4 ("Information Request — none. Beer Detail asks no progressive questions of any kind").*

---

## 4. Exit Conditions

**Confirmed, contract-backed transitions, per the Navigation Contract's own Screen Graph and Transition Contracts:**

| Trigger | Destination |
|---|---|
| Explicit request to check a charged price | Price Verification |
| Explicit signal of openness to alternatives, or a direct comparison request | Comparison |
| Explicit acceptance of a surfaced Confirm-as-Is judgment | Decision Complete (no screen change) |
| Finished viewing, with no anchor situation present, or no further action taken | Decision Complete — the "lighter" completion path, legitimate in its own right |

*Citation: Beer Detail Screen Contract (13), §4, §7; Navigation Contract (16), §3, §6.*

**Flagged inconsistency — not resolved here.** Information Architecture states plainly that "backing out of Beer Detail returns to whichever screen led there — Search/Browse Results, Recommendation, or Comparison — never defaulting to Home regardless of origin" (IA §4). The Navigation Contract, however, does not include a Beer Detail → Recommendation edge anywhere: it's absent from the Screen Graph's direct edges (§3), Recommendation's own Entry Points are stated as "from Home or from Comparison" only (§4), and no Beer Detail → Recommendation Transition Contract exists (§6). The Navigation Contract is the more recent, purpose-built, and internally self-consistent source of truth for transitions specifically — the ADR records its creation as the deliberate decision to make it "the single synthesized source of truth for every transition, superseding any individual screen's own restatement of it" (ADR §3). On that basis, this specification treats **Beer Detail → Comparison and Beer Detail → Price Verification as the only confirmed outbound transitions**, and does not specify a Beer Detail → Recommendation path. **This is a genuine cross-document inconsistency, not a deliberate deferral, and should be raised for formal architecture review before backward navigation toward Recommendation is built.**

*Citation: Information Architecture (08), §4; Navigation Contract (16), §3, §4, §6; ADR (19), §3.*

---

## 5. Information Hierarchy

Directly citing Content Architecture §3's Beer Detail entry, without redesign:

- **Primary:** Beer Identity, Legal Price, Alcohol Content, Size, Alcohol-Adjusted Value, Style Benchmark where available.
- **Supporting:** the Confirm-as-Is judgment, when an anchor situation applies.
- **Contextual:** how this SKU was reached, since that determines whether Confirm-as-Is applies at all.
- **Explanation:** attached to the Confirm-as-Is judgment, when surfaced.
- **Confidence:** attached to Alcohol-Adjusted Value and Style Benchmark specifically.
- **Completion:** reached when the person accepts the confirmation, or is otherwise satisfied.

*Citation: Content Architecture (10), §3; Beer Detail Screen Contract (13), §5.*

**A property distinguishing this screen from every other, stated with the emphasis the canon itself gives it:** every piece of content here rests on Verified or Computed Facts alone. No Soft-preference-driven content ever appears. This means Confidence on this screen is **uniformly high across everything shown** — there is no mixed Hard/Strong/Soft confidence split here the way there is on Recommendation, and this specification does not build one.

*Citation: Beer Detail Screen Contract (13), §6.*

---

## 6. Screen Sections

Four functional sections:

**A. Beer Facts** — always present once loaded: Beer Identity, Legal Price, Alcohol Content, Size, Alcohol-Adjusted Value, and Style Benchmark when available.

**B. Confirm-as-Is** — conditionally present, only when an anchor situation applies; always carries its Explanation and Confidence as intrinsic, non-detachable sub-parts.

**C. Actions** — Request Price Verification, Request Comparison, and, when Confirm-as-Is is present, Accept and Ask "Why."

**D. Recovery** — visible only when the identified SKU cannot be resolved.

*Citation: Beer Detail Screen Contract (13), §5, §7, §8.*

**A precision worth stating on price specifically, given how directly it's flagged for fidelity:** Section A's price content is Legal Price only — the government-published reference figure. Observed/Charged Price never appears anywhere on this screen, under any condition; that content is exclusively Price Verification's.

*Citation: Beer Detail Screen Contract (13), §2 MUST NEVER; Information Architecture (08), §3.*

**How these sections are visually arranged is a design decision. Intentionally left unspecified by the Canonical Architecture.**

---

## 7. Every UI Element

| Element | Purpose | Required Data | Optional Data | Visibility Rule |
|---|---|---|---|---|
| **Beer Identity Display** | Identify which beer/SKU this is | Name, brand, style | — | Always visible once loaded |
| **Legal Price Display** | Show the government-published reference price | Legal Price figure | — | Always visible once loaded; never displays Observed/Charged Price |
| **Alcohol Content (ABV) Display** | Show alcohol strength | ABV figure | — | Always visible once loaded |
| **Size/Package Format Display** | Show size and format | Size/format figure | — | Always visible once loaded |
| **Alcohol-Adjusted Value Display** | Show cost per unit of alcohol | The computed figure, carrying the same high confidence as its inputs | — | Always visible once loaded — one of the "at minimum" elements this screen must present |
| **Style Benchmark / Value Percentile Display** | Show relative standing within style | The percentile/relative-standing figure | — | Shown only when the underlying Platform Service is available; **its absence must never be treated as a missing Primary element** |
| **Confirm-as-Is Judgment Display** | State whether this SKU is already the strongest fit within known constraints | The judgment; its Explanation, naming which inputs and tier; its Confidence | — | Only when entry context indicates an anchor situation applies — the exact determining rule is an open gap, see §9 and §13. **Never shown without Explanation and Confidence simultaneously present.** |
| **Price Verification Hand-off Action** | Let the person explicitly request a charged-price check | The already-identified SKU | — | Always available; invitation-only, never automatic |
| **Comparison Hand-off Action** | Let the person signal openness to alternatives or request a direct comparison | The current SKU, carried as one candidate | — | Always available; invitation-only, never automatic |
| **Accept Confirm-as-Is** | Register explicit acceptance of the surfaced judgment | — | — | Only when Confirm-as-Is is present |
| **Ask "Why" (re Confirm-as-Is)** | Re-surface the existing Explanation | — | — | Only when Confirm-as-Is and its Explanation already exist |
| **"SKU Not Found" Recovery Display** | State plainly that the identified SKU cannot be resolved | — | — | Only in the Recovering state |

*Citation: Beer Detail Screen Contract (13), §2, §5, §6, §7.*

**No element beyond these twelve is permitted.**

---

## 8. User Interactions

| Canonical action | Detail |
|---|---|
| **View SKU details** | Presents the Section A composition once resolution succeeds. |
| **Accept the Confirm-as-Is judgment** | Requires the judgment already surfaced. Moves Decision Status to Completed. |
| **Ask "why," regarding Confirm-as-Is** | Requires the judgment and its Explanation already present. Re-surfaces existing content; generates nothing new. |
| **Request Price Verification** | Requires only the already-identified SKU. Hands off, carrying the SKU forward; the charged price itself is gathered at Price Verification, not here. |
| **Request Comparison** | Requires only the already-identified SKU. Hands off, carrying the current SKU forward as one candidate. |
| **Leave without an explicit acceptance** | No system response required. Legitimate as a lighter Decision Complete when no anchor situation was ever applicable. |

*Citation: Beer Detail Screen Contract (13), §7.*

**Interaction modality is not specified anywhere in the canon.** Whether any of the above is realized as a tap, a selection, or another mechanism is a design/implementation decision. **Intentionally left unspecified by the Canonical Architecture.** No long-press, scroll, or gesture behavior is canonically defined for this screen.

*Citation: Feature Inventory (07), §1; Review Guide (00), §2.*

---

## 9. States

Mapped exhaustively onto Beer Detail Screen Contract §8's own State Machine. No new state introduced.

| Requested category | Canonical mapping | Notes |
|---|---|---|
| **Initial** | **Loading** | Entry: arrival with an identified SKU reference. Exit: resolution succeeds or fails. No content is presented before resolution completes. |
| **Populated** | **Loaded**, refined further into **Confirming** when an anchor situation applies | Loaded: SKU facts successfully retrieved. Confirming: an anchor situation applies and the Confirm-as-Is judgment has been surfaced — a distinct, richer variant of "populated," not a separate top-level condition. |
| **Unavailable** | **Recovering** | SKU resolution fails. No SKU-specific content presented while in this state. |
| **Recovering (if canonically applicable)** | **Recovering** — the same single canonical state as "Unavailable," above | The canon defines exactly one failure state here, not two. "Unavailable" and "Recovering" collapse to the same condition; presenting them as two distinct states would introduce a state the Screen Contract doesn't define. |
| **Completed (if applicable)** | **Completed** | Applicable, with **two distinct entry paths**, preserved here rather than collapsed into one: (1) explicit acceptance of a surfaced Confirm-as-Is judgment, or (2) satisfied viewing when no anchor situation ever applied — the "lighter" completion, a legitimate outcome in its own right, not a lesser one. |
| **Any other canonical state** | **Handoff-Pending** | Entry: an explicit request for Price Verification or Comparison. Exit: successful transition. This screen's own reasoning is never substituted for the hand-off. |

*Citation: Beer Detail Screen Contract (13), §8; Screen Specification Template (18), §7.*

---

## 10. Validation Rules

- Confirm-as-Is fires **only** when entry context indicates an anchor situation applies. **The exact determining rule is not specified anywhere in the frozen canon** — the Decision Engine Model rules out identification mechanism alone as the signal, but names nothing in its place. **Intentionally left unspecified by the Canonical Architecture.**
- Every displayed fact on this screen must be a Verified or Computed Fact. No Soft-preference-driven content may ever appear here — that remains exclusively Recommendation's domain.
- Confidence on this screen is uniformly high across everything shown; no element on this screen may present a Hard/Strong-versus-Soft confidence split.
- Confirm-as-Is, whenever shown, must carry its Explanation and Confidence simultaneously — never one without the other, never partially.
- Style Benchmark's absence must never be treated as an error condition or a missing required element.
- Price Verification and Comparison hand-offs are always invitation-only, never automatic — **including when an overcharge would hypothetically exist.** The Recommendation Framework's rule that a price-fairness problem "must always surface regardless of restraint" governs what happens once Price Verification has actually been entered and a discrepancy is found there — it does not require or imply this screen proactively triggering a price check on its own initiative. This screen's own MUST list is explicit: the hand-off happens only on explicit request.
- Nothing about this screen's state persists across separate sessions.

*Citation: Beer Detail Screen Contract (13), §2, §6, §10, §11; Recommendation Framework (04), §3.*

---

## 11. Accessibility Considerations

**Intentionally left unspecified by the Canonical Architecture**, per the Screen Specification Template's own placeholder discipline — no dedicated accessibility standard yet exists anywhere in the canon.

*Citation: Screen Specification Template (18), §11.*

The one constraint statable with canonical authority: no element may be introduced for accessibility purposes beyond the twelve named in §7. Worth flagging for this screen specifically: because Confidence here is uniform (not split, unlike Recommendation), there is no requirement to structurally distinguish confidence tiers within this screen's content — a simplification that should carry through to whatever accessible presentation is eventually built, not be reintroduced as a false parallel to Recommendation's screen.

*Citation: Beer Detail Screen Contract (13), §6.*

---

## 12. Copy Requirements

Exact wording remains a design/content deliverable. What follows are the requirements that wording must satisfy.

- **Observed/Charged Price must never appear in any copy on this screen, under any circumstance.**
- **"Correct price" must never be used in place of "Legal Price"** — the canon reserves "correct" for exactly this kind of loose, unearned moral framing the Lexicon warns against.
- **"Confirm" must always be paired with "-as-Is" when referring to the Feature specifically**, never used alone, to avoid confusion with unrelated actions like confirming an order.
- **No invented substitute may be offered or implied when a SKU cannot be found** — the recovery message states the fact plainly, without suggesting an alternative beer.
- **No forbidden terms, per the Canonical Interaction Lexicon:** "Score" or "Rating," anywhere. Bare, unqualified "Best." "Verify," used loosely, outside Price Verification's own scope.
- **The Confirm-as-Is judgment's copy must state which inputs and confidence tier produced it**, using the same Recommendation Explanation structure reused everywhere else in the canon — not a screen-specific variant.

*Citation: Beer Detail Screen Contract (13), §6; Canonical Interaction Lexicon (17), §3, §5.*

---

## 13. Edge Cases

**Backward navigation from Beer Detail toward Recommendation.** Already treated in full in §4 above. Restated here for completeness: this is a genuine inconsistency between Information Architecture and the Navigation Contract, not a deliberate deferral, and it is not resolved by this specification. **Flagged for architecture-layer review before this specific backward path is built.**

**The exact rule determining whether an anchor situation applies.** Already an explicitly flagged open gap in the frozen Screen Contract itself. **Intentionally left unspecified by the Canonical Architecture; pending ADR resolution (Engineering Planning Roadmap, item 1.2).**

**Arrival from Recommendation, carrying an already-produced Recommendation object for this SKU.** Information Architecture's own ownership rule is clear on one part of this: "if a person drills into the recommended SKU via Beer Detail, that's a reference to the same information, not a second copy of it" — so the Recommendation object itself must never be recomputed here. What remains genuinely open is whether this specific entry context — arriving with an already-recommended SKU — is itself sufficient to constitute the "anchor situation" that triggers Confirm-as-Is. This is a plausible reading, not a confirmed one. **Intentionally left unspecified by the Canonical Architecture; must not be assumed true when this screen is built.**

**Style Benchmark not yet available for a given SKU's style.** Fully resolved, not a gap: the figure is simply omitted, gracefully, without being treated as an error.

**A person requests Comparison directly after accepting a Confirm-as-Is judgment.** Fully resolved: Confirming permits a transition to Handoff-Pending on explicit request, exactly like the unconfirmed path.

**The precise trigger for "finished viewing" when no anchor situation applies.** The Screen Contract's own language is "the person is finished viewing... or no further action taken" — this does not name a specific triggering event (an explicit dismissal, navigating away, a timeout, or otherwise). **Intentionally left unspecified by the Canonical Architecture; likely an implementation-level detection concern rather than a product-behavior gap, but not resolved by any cited document.**

---

## 14. Analytics Candidates

Names only, no schema, properties, or tooling defined, per the Screen Specification Template's placeholder discipline.

*Citation: Screen Specification Template (18), §12.*

- Screen viewed (Beer Detail reached, by SKU)
- Confirm-as-Is judgment surfaced
- Confirm-as-Is accepted (Decision Complete via confirmation)
- Explanation requested ("why," re Confirm-as-Is)
- Price Verification requested from this screen
- Comparison requested from this screen
- SKU-not-found recovery shown
- Screen exited without explicit acceptance (lighter completion)

*Citation: Screen Specification Template (18), §12.*

---

## 15. Non-functional Requirements

**Intentionally left unspecified by the Canonical Architecture** for responsiveness, performance budgets, offline behavior, and platform expectations — none are addressed anywhere in the canon.

*Citation: Review Guide (00), §2; ADR (19), §7.*

The one grounded, citable fact: this screen's Referenced Information requires the Beer Knowledge Base for every Verified Fact shown, and the Style Benchmark computation where available. Style Benchmark is an Important-Soon-After Platform Service, not Core V1 — this screen must degrade gracefully in its absence, exactly as already specified in §7 and §10, never treating that absence as an error.

*Citation: Beer Detail Screen Contract (13), §3; Feature Inventory (07), §5.*

---

## 16. Acceptance Criteria

Restated directly from Beer Detail Screen Contract §12:

✓ Beer Detail never displays Observed/Charged Price under any condition.
✓ Beer Detail never performs verification, comparison, or recommendation reasoning itself.
✓ Every piece of content shown carries uniformly high confidence, since nothing here is built from a Soft Preference.
✓ The Confirm-as-Is judgment, whenever it appears, always carries its Explanation and Confidence.
✓ A hand-off to Price Verification or Comparison only ever occurs on an explicit request, never automatically.
✓ Decision Complete is reachable both through an explicit confirmation acceptance and through simple satisfied viewing when no anchor situation applies.
✓ Style Benchmark's absence, when it hasn't yet been built, is never treated as a missing required element.

*Citation: Beer Detail Screen Contract (13), §12.*

---

## 17. Traceability Matrix

| Specification Section | Canonical Source(s) |
|---|---|
| 1. Screen Purpose | Beer Detail Screen Contract §1 |
| 2. User Goals | User Interaction Model §1; Information Architecture §2 |
| 3. Entry Conditions | Beer Detail Screen Contract §3, §4 |
| 4. Exit Conditions | Beer Detail Screen Contract §4, §7; Navigation Contract §3, §4, §6; Information Architecture §4; ADR §3 |
| 5. Information Hierarchy | Content Architecture §3; Beer Detail Screen Contract §5, §6 |
| 6. Screen Sections | Beer Detail Screen Contract §5, §7, §8; Information Architecture §3 |
| 7. Every UI Element | Beer Detail Screen Contract §2, §5, §6, §7 |
| 8. User Interactions | Beer Detail Screen Contract §7; Feature Inventory §1; Review Guide §2 |
| 9. States | Beer Detail Screen Contract §8; Screen Specification Template §7 |
| 10. Validation Rules | Beer Detail Screen Contract §2, §6, §10, §11; Recommendation Framework §3 |
| 11. Accessibility Considerations | Screen Specification Template §11; Beer Detail Screen Contract §6 |
| 12. Copy Requirements | Beer Detail Screen Contract §6; Canonical Interaction Lexicon §3, §5 |
| 13. Edge Cases | Beer Detail Screen Contract §11; Information Architecture §4, §7; Navigation Contract §3, §4, §6 |
| 14. Analytics Candidates | Screen Specification Template §12 |
| 15. Non-functional Requirements | Review Guide §2; ADR §7; Beer Detail Screen Contract §3; Feature Inventory §5 |
| 16. Acceptance Criteria | Beer Detail Screen Contract §12 |

---

## Document Notes

One item in this specification was discovered rather than merely inherited: the Beer Detail → Recommendation navigation inconsistency in §4 and §13. It is documented, not resolved, and is flagged for formal architecture review — consistent with this document's role as a translation of frozen architecture, not a revision of it.
