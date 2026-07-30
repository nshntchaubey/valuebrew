# ValueBrew — Screen Contract: BEER DETAIL
### The canonical, implementation-independent contract for the Beer Detail screen. Derived entirely from the ten frozen documents plus the Home and Recommendation Screen Contracts. Not UI, not wireframes, not a PRD.

---

## 1. Screen Identity

**Screen Name:** Beer Detail.

**Purpose:** present everything known about one already-identified SKU, completely enough that the person can confidently understand it before deciding what to do next.

**Owning Module:** Discovery Module.

**Owning Experience:** Beer Detail.

**Canonical Role:** the explanatory screen for a single beer — the canonical home for a SKU's Verified and Computed Facts, and, when an anchor situation applies, the surfaced Confirm-as-Is judgment.

**Why this screen exists independently:** Search/Browse Results deliberately shows only abbreviated identity, never full detail, per its own ownership boundary. Recommendation performs multi-candidate synthesis from preference inputs — a fundamentally different operation from presenting one already-known SKU's facts. Price Verification and Comparison each require inputs Beer Detail doesn't have and must never try to gather itself — a charged price, or multiple named candidates. Beer Detail is the one screen whose entire content is derivable from a single known SKU alone, with nothing further required.

---

## 2. Screen Contract

**MUST:**
- Present Beer Identity, Legal Price, Alcohol Content, Size, and Alcohol-Adjusted Value for the identified SKU, at minimum.
- Present Style Benchmark and value percentile when available, gracefully omitting them when not — their absence is never treated as a missing Primary object.
- Surface the Confirm-as-Is judgment, with its Explanation and Confidence attached, whenever the entry context indicates an anchor situation applies.
- Reach Decision Complete either when the person accepts the Confirm-as-Is judgment, or, absent an anchor situation, when the person is simply satisfied with the information viewed.
- Hand off to Price Verification only on an explicit request to check a charged price.
- Hand off to Comparison only on an explicit signal of openness to alternatives or a direct comparison request.

**MAY:**
- Offer a way to initiate either hand-off directly from this screen.
- Hold the SKU's facts in view indefinitely while the person considers what to do next, without forcing a decision.

**MUST NEVER:**
- Perform the verification delta computation itself.
- Perform multi-candidate comparison reasoning itself.
- Perform Full Recommendation synthesis from preference inputs.
- Display Observed/Charged Price, under any circumstance.
- Push an alternative or a comparison unprompted, however much better an alternative might be.
- Present the Confirm-as-Is judgment, or any content on this screen, without its Explanation and Confidence attached.
- Persist anything across separate sessions.

---

## 3. Inputs

**Known Information:** the identified SKU. This is a precondition for the screen loading at all — Beer Detail has nothing to show without one.

**Referenced Information:** the Beer Knowledge Base, for every Verified Fact about this SKU; the Style Benchmark computation, where available.

**Interaction State:** whether an anchor situation applies, which determines whether the Confirm-as-Is judgment fires. See Section 11 — the exact rule for this determination is a flagged open gap, not resolved here.

**Cross-cutting Behaviors:** Recommendation Explanation and Confidence Communication are both directly reused on this screen, not reinvented. Learning ("Why") applies specifically to the Confirm-as-Is judgment when it's present. Decision Complete is directly reachable here.

**Recovery State:** "SKU not found" — if the identified SKU can no longer be resolved against the catalog, for instance from a stale reference.

---

## 4. Outputs

**Transition** — to Price Verification, on explicit request; to Comparison, on explicit request or a signaled openness to alternatives.

**Decision** — a system decision: whether the Confirm-as-Is judgment applies, and what it concludes, when the anchor condition is met.

**Recommendation** — none produced independently. The Confirm-as-Is judgment is a narrow, single-SKU judgment, not a Full Recommendation, and must never be presented as though it were one.

**Recovery** — "SKU not found," produced if the identification can't be resolved.

**Information Request** — none. Beer Detail asks no progressive questions of any kind.

**State Change** — Decision Status moving from Loading to Loaded, and from there to Completed, or to a hand-off transition.

---

## 5. Information Composition

Directly citing Content Architecture Section 3's Beer Detail entry, not redesigning it. Primary: Beer Identity, Legal Price, Alcohol Content, Size, Alcohol-Adjusted Value, Style Benchmark where available. Supporting: the Confirm-as-Is judgment, when an anchor situation applies. Contextual: how this SKU was reached, since that determines whether Confirm-as-Is applies at all. Explanation: attached to the Confirm-as-Is judgment when it's surfaced. Confidence: attached to Alcohol-Adjusted Value and Style Benchmark specifically. Completion: reached when the person accepts the confirmation, or is otherwise satisfied.

---

## 6. Behavioral Rules

Confirm-as-Is fires only when the entry context indicates an anchor situation applies — the precise rule determining this is the open gap flagged in Section 11.

**Every piece of content on this screen rests on Verified or Computed Facts alone.** No Soft-preference-driven content ever appears on Beer Detail — that is exclusively Recommendation's domain. This is the single most important distinguishing property of this screen relative to Recommendation, and it has a direct consequence: **Confidence on Beer Detail is uniformly high across everything shown here**, since nothing displayed is built from a Soft Preference. There is no "mixed confidence" case on this screen the way there is on Recommendation — worth stating explicitly rather than leaving implicit, since a future designer might otherwise assume this screen needs the same Hard/Strong-versus-Soft confidence split that Recommendation requires. It doesn't, because that split doesn't arise here at all.

Recommendation Explanation is directly reused on this screen, not reinvented — applied here specifically to explain the Confirm-as-Is judgment, using the exact same structure the Recommendation Framework defines everywhere else.

Hand-offs to Price Verification or Comparison are always invitation-only, consistent with Segment-Appropriate Restraint — never offered automatically, never pushed on someone who hasn't asked.

---

## 7. Interaction Contract

**View SKU details.** Trigger: arrival at this screen with an identified SKU. Precondition: a SKU must already be resolved. System Response: presents the composition from Section 5. Possible Outcomes: the person accepts a surfaced confirmation, requests a hand-off, or simply finishes viewing. Recovery: "SKU not found," if resolution fails. Completion: not yet reached at this point.

**Accept the Confirm-as-Is judgment.** Trigger: an explicit acceptance, when the judgment has been surfaced. Precondition: an anchor situation must apply and the judgment must already be shown. System Response: Decision Status moves to Completed. Possible Outcomes: Decision Complete. Recovery: not applicable. Completion: reached.

**Ask "why," regarding the Confirm-as-Is judgment.** Trigger: an explicit request. Precondition: the judgment, and its Explanation, must already exist. System Response: the existing Explanation is re-surfaced; nothing new is generated. Possible Outcomes: the person accepts afterward, or requests a hand-off having learned something from it. Recovery: not applicable. Completion: not changed by this interaction alone.

**Request Price Verification.** Trigger: an explicit intent to check a charged price. Precondition: none beyond an already-identified SKU. System Response: hands off to Price Verification, carrying the SKU forward; the charged price itself is gathered there, not here. Possible Outcomes: proceeds into Price Verification's own contract. Recovery: not applicable here. Completion: not reached at Beer Detail in this case.

**Request Comparison.** Trigger: an explicit signal of openness to alternatives, or a direct comparison request. Precondition: none beyond an already-identified SKU. System Response: hands off to Comparison, carrying the current SKU forward as one candidate. Possible Outcomes: proceeds into Comparison's own contract. Recovery: not applicable here. Completion: not reached at Beer Detail in this case.

**Leave without an explicit acceptance.** Trigger: the person is finished viewing, with no anchor situation present, or no further action taken. Precondition: none. System Response: none required. Possible Outcomes: a lighter form of Decision Complete is reached — satisfied viewing, without a formal Confirm-as-Is acceptance, is itself a legitimate completion when no anchor confirmation was ever applicable to begin with. Recovery: not applicable. Completion: reached.

---

## 8. State Machine

**Loading.** Entry: arrival with an identified SKU reference. Exit: the SKU resolves successfully, or resolution fails. Permitted transitions: to Loaded, to Recovering. Forbidden: presenting any content before resolution completes.

**Loaded.** Entry: the SKU's facts are successfully retrieved. Exit: an anchor situation is evaluated. Permitted transitions: to Confirming, if an anchor situation applies; directly to Completed (the lighter case), if it doesn't and the person is satisfied; to Handoff-Pending, on an explicit request. Forbidden: surfacing a Confirm-as-Is judgment without first resolving whether the anchor condition is met.

**Confirming.** Entry: an anchor situation applies and the Confirm-as-Is judgment has been surfaced. Exit: the person accepts, asks "why," or requests a hand-off. Permitted transitions: to Completed, to Handoff-Pending. Forbidden: presenting the judgment without its Explanation and Confidence.

**Handoff-Pending.** Entry: an explicit request for Price Verification or Comparison. Exit: successful transition. Permitted transitions: to Price Verification, to Comparison. Forbidden: performing either screen's reasoning here instead of handing off.

**Recovering.** Entry: SKU resolution fails. Exit: not applicable within this screen — this state has no further legitimate exit besides leaving the screen entirely, since Beer Detail has nothing further to offer once resolution has failed. Forbidden: presenting any SKU-specific content while in this state.

**Completed.** Entry: an explicit acceptance, or satisfied viewing with no anchor situation present. Exit: none — terminal for this interaction. Forbidden: any further automatic content or prompt.

---

## 9. Dependencies

**Decision Engine Model** — indirectly. Beer Detail corresponds to Journey 2 (anchor known), though it performs none of that Journey's broader reasoning itself.

**Beer Knowledge Model** — directly. Every Verified and Computed Fact shown here originates from that document's classifications.

**Recommendation Framework** — directly, for the Confirm-as-Is judgment specifically, and for the Explanation and Confidence rules this screen reuses without modification.

**Information Architecture** — directly. This screen's ownership, its possible exits, and its status as a destination screen are defined there.

**Experience Flows** — directly. The Anchored Confirmation flow lives on this screen.

**Content Architecture** — directly. This screen's composition in Section 5 is a direct citation.

**Feature Inventory** — directly. Confirm-as-Is is the Feature this screen surfaces, and this screen is explicitly named as the entry point through which that Feature attaches.

---

## 10. Constraints

Cannot perform the verification delta computation. Cannot perform multi-candidate comparison reasoning. Cannot perform Full Recommendation synthesis. Cannot display Observed/Charged Price under any circumstance. Cannot push an alternative or a comparison unprompted. Cannot present the Confirm-as-Is judgment without its Explanation and Confidence attached. Cannot persist anything across separate sessions. Cannot present any Soft-preference-driven content — that remains exclusively Recommendation's domain.

---

## 11. Failure Conditions

**SKU not found / stale reference.** Detection: the identified SKU can no longer be resolved against the catalog. Recovery: state plainly that the beer can't be found, without inventing a substitute or silently redirecting elsewhere. Progress Preservation: not applicable — there is no prior context on this screen to preserve, since it depends entirely on a single, freshly-arriving identification.

**Open gap, flagged rather than resolved, per policy:** the frozen canon establishes that "how this SKU was reached... determines whether Confirm-as-Is applies," but no document specifies the actual rule determining that. The Decision Engine Model states that identification mechanism (search, scan, or otherwise) is irrelevant to whether an anchor situation exists, which suggests mechanism alone can't be the determining signal — but nothing in the ten frozen documents states what the determining signal actually is instead. Whether Confirm-as-Is should fire based on the entry point (arriving via direct search versus general browsing), based on some other contextual marker, or always fire regardless of entry path, is genuinely undecided. This is worth a deliberate decision of the same kind already made for Home's unsupported-intent case and Recommendation's ambiguous-preference case, rather than an assumption made silently here.

---

## 12. Acceptance Criteria

✓ Beer Detail never displays Observed/Charged Price under any condition.
✓ Beer Detail never performs verification, comparison, or recommendation reasoning itself.
✓ Every piece of content shown carries uniformly high confidence, since nothing here is built from a Soft Preference.
✓ The Confirm-as-Is judgment, whenever it appears, always carries its Explanation and Confidence.
✓ A hand-off to Price Verification or Comparison only ever occurs on an explicit request, never automatically.
✓ Decision Complete is reachable both through an explicit confirmation acceptance and through simple satisfied viewing when no anchor situation applies.
✓ Style Benchmark's absence, when it hasn't yet been built, is never treated as a missing required element.

---

## 13. Validation

✓ No Product Definition Document violated — no new capability introduced beyond what's already named.
✓ No Recommendation Framework violated — the Confirm-as-Is judgment follows the same Explanation and Confidence rules used everywhere else, without exception.
✓ No Information Architecture ownership violated — this screen's ownership matches its IA entry exactly, including its explicit exclusion of Observed/Charged Price.
✓ No Experience Flow violated — the Anchored Confirmation flow maps cleanly onto this contract.
✓ No Content Architecture violated — this screen's composition matches that document's entry directly.
✓ No new capability introduced — every behavior here traces to an already-named Experience or Feature.
✓ No hidden assumptions introduced — one genuine gap is named rather than silently resolved: the exact rule determining whether an anchor situation applies, flagged in Section 11, left open pending an explicit decision.

---

## 14. Future Compatibility

**Natural future evolution:** richer Style Benchmark integration as that Platform Service matures beyond its Important-Soon-After status; a more precise resolution of the Section 11 gap, once decided, refining exactly which entry contexts trigger Confirm-as-Is.

**Forbidden future evolution:** this screen ever computing a verification delta, a comparison, or a full recommendation itself, rather than handing off to the screen that owns each. This screen ever displaying Observed/Charged Price, or any Soft-preference-driven content, regardless of how convenient it might seem to surface it here. This screen persisting anything about a person's viewing history across sessions, without first revisiting the Product Definition Document's boundary against accounts.
