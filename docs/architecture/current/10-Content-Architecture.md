# ValueBrew — Content Architecture
### Sits between Experience Flows and Screen Specifications. Derived entirely from the nine frozen documents. Not screens, not layout, not navigation. Answers one question: how should information be composed so that every screen communicates consistently?

---

## 1. Content Architecture Principles

1. Decision before detail — whatever the person actually asked for appears before the facts that produced it, never buried beneath them.

2. Facts before inference — Verified and Computed Facts always precede Human Judgment or soft-preference-driven content.

3. Explanation follows conclusion immediately — never precedes it, never requires separate navigation to appear the first time.

4. Confidence accompanies every piece of inferred content at the point it appears, never as a separate summary shown elsewhere.

5. Recovery information appears only when a recovery condition is actually active — never pre-emptively, never by default.

6. Progressive information never appears alongside a completed decision. Once Decision Complete, questions don't linger.

7. Comparison and trade-off information is presented as a genuine unit — a trade-off is never split so that one side's facts appear without the other's.

8. Occasion and other low-confidence, deferred inputs never receive the same informational weight as budget or core preferences, mirroring their canonical MVP tier.

9. Charged/observed price information never appears outside a Price Verification composition, since it is transient, transaction-level knowledge, not catalog knowledge.

10. Every composition contains exactly the information needed to reach Decision Complete for its Experience — no more, no less.

11. Information that doesn't depend on the underlying facts is never presented as if it does.

12. A tie or trade-off is composed as a complete answer, never as an incomplete or degraded version of a single-winner recommendation.

13. Information never appears twice within a composition — where two objects would say the same thing, one is dropped or merged into a single, unambiguous statement.

14. The person is never shown information that requires understanding the Decision Engine's internal reasoning to interpret correctly.

15. Content order is derived from the Information Priority Rules in Section 4, never from convenience of source or ease of retrieval.

---

## 2. Information Objects

**Beer Identity** — Purpose: identifies which beer is meant. Source: Beer Knowledge Base. Confidence: Verified Fact, high. Lifetime: persistent. Dependencies: none.

**Legal Price** — Purpose: the government-published reference price. Source: Beer Knowledge Base, Regulatory category. Confidence: Verified Fact, high, though dynamic — subject to refresh per the documented history of regulatory change. Lifetime: persistent. Dependencies: none.

**Observed/Charged Price** — Purpose: what a person reports being charged. Source: user-reported, in the moment. Confidence: high assuming honest reporting, not independently verifiable. Lifetime: transient, exists only within one Price Verification interaction. Dependencies: Beer Identity.

**Alcohol Content (ABV)** and **Size/Package Format** — Purpose: inputs to value computation. Source: Beer Knowledge Base, Physical category. Confidence: Verified Fact. Lifetime: persistent. Dependencies: none.

**Alcohol-Adjusted Value** — Purpose: cost per unit of alcohol. Source: computed from Legal Price, ABV, and Size. Confidence: Computed Fact, carrying the same high confidence as its inputs. Lifetime: recomputed whenever underlying facts change, never stored as independent truth. Dependencies: Legal Price, Alcohol Content, Size.

**Style Benchmark / Value Percentile** — Purpose: relative standing within a style. Source: computed aggregate across the catalog. Confidence: Computed Fact, high, though its Important-not-Core MVP status means it may be absent early. Lifetime: recomputed as the catalog changes. Dependencies: Alcohol-Adjusted Value across all SKUs sharing a style.

**Verification Result** — Purpose: states whether Observed Price sits at, above, or below Legal Price. Source: computed. Confidence: high — a Computed Fact built from two Verified Facts. Lifetime: transient. Dependencies: Legal Price, Observed Price.

**Recommendation** — Purpose: the specific SKU or set selected as the answer to a Full Recommendation. Source: computed from Preference Summary and catalog data. Confidence: composite — blends high-confidence Hard/Strong-driven content with lower-confidence Soft-driven content, which is exactly why Confidence must always travel with it, never separately. Lifetime: transient. Dependencies: Preference Summary, Alcohol-Adjusted Value, Style Benchmark where available.

**Comparison Result** — Purpose: the outcome of comparing named candidates — a winner, a trade-off, or a tie. Source: computed. Confidence: same composite treatment as Recommendation. Lifetime: transient. Dependencies: Alcohol-Adjusted Value per candidate, Preference Summary.

**Trade-off** — Purpose: names the specific dimensions on which candidates differ when no clean winner exists. Source: computed, a component of Comparison Result or an embedded Recommendation. Confidence: an unusual object — the facts it states are high-confidence even when the resolution itself is low-confidence; these two must never be conflated into one figure. Lifetime: transient. Dependencies: Comparison Result or Recommendation.

**Preference Summary** — Purpose: everything stated so far — budget, style, strength, size, brand, occasion, recipient information if applicable. Source: user-provided, this interaction only. Confidence: high once stated, internally graded by input type. Lifetime: transient, session-only, never persisted across interactions, consistent with the canon's rejection of accounts. Dependencies: none — this is an origin object.

**Confidence** — Purpose: states how certain the engine is about a specific piece of content. Source: derived from the Beer Knowledge Model's Verified/Computed/Human Judgment classification of whatever it's attached to. Lifetime: exists only attached to another object, never standalone. Dependencies: whatever it describes.

**Explanation** — Purpose: states which inputs produced a Recommendation, Verification Result, or Comparison Result, and at what confidence. Source: derived from the reasoning behind its parent object. Lifetime: tied to its parent's lifetime. Dependencies: its parent object plus Confidence.

**Decision Status** — Purpose: tracks where an interaction stands — gathering information, resolved, in recovery. Source: State & Flow Management. Lifetime: transient, exists only for one interaction. Dependencies: none directly, but referenced by every composition to know what to show.

**Recovery Information** — Purpose: names what's missing or in conflict when a flow can't proceed cleanly. Source: computed at the moment a recovery condition is detected. Lifetime: transient, exists only while the condition is active. Dependencies: whatever object triggered it.

---

## 3. Content Compositions

**Home.** Primary: an invitation to state an intent — nothing beer-specific yet. Recovery: "no beer identified" information, if arriving as a bounce-back. Nothing else applies; this composition is transient by nature and never itself reaches Decision Complete.

**Search/Browse Results.** Primary: Beer Identity, abbreviated, per candidate. Supporting: enough of Legal Price or Alcohol-Adjusted Value to distinguish candidates at a glance, where available. Contextual: the query or browse criteria that produced these candidates. Confidence: minimal — Beer Identity is Verified and uniformly high, nothing inferred yet. Recovery: "no beer identified," if nothing matches. Completion: not applicable; this composition always routes onward.

**Beer Detail.** Primary: Beer Identity, Legal Price, Alcohol Content, Size, Alcohol-Adjusted Value, Style Benchmark where available. Supporting: the Confirm-as-Is judgment, when an anchor situation applies. Contextual: how this SKU was reached, since that determines whether Confirm-as-Is applies at all. Explanation: attached to the Confirm-as-Is judgment when surfaced. Confidence: attached to Alcohol-Adjusted Value and Style Benchmark specifically, distinguishing Verified from Computed content. Completion: a genuine Decision Complete point if the person accepts the confirmation.

**Recommendation.** Primary: the Recommendation object once produced; before that, the next progressive question — this is the canonical home for progressive information. Supporting: Preference Summary as established so far. Contextual: which entry point led here, since that determines whether Planning Mode or Proxy-Buying Mode is engaged. Explanation: attached to the Recommendation. Confidence: attached to the Recommendation, explicitly separating its Hard/Strong-driven portion from any Soft-driven portion. Recovery: for insufficient information, conflicting preferences, or an unresolved trade-off/tie. Completion: Decision Complete once accepted.

**Price Verification.** Primary: the Verification Result. Supporting: Legal Price and Observed Price, shown together, since the result means nothing without both. Contextual: Beer Identity, referenced rather than re-owned. Progressive: a request for Observed Price, if not yet given — the one progressive step this composition needs. Explanation: states the delta plainly. Confidence: uniformly high, the one composition in the entire product that doesn't degrade under uncertainty. Completion: Decision Complete once acknowledged.

**Comparison.** Primary: the Comparison Result — a clear winner, or a Trade-off/Tie. Supporting: Beer Identity and Alcohol-Adjusted Value for every candidate, shown together, since comparison only means something with all candidates present at once. Contextual: Preference Summary, so the person can see what was actually weighed. Progressive: at most one clarifying question. Explanation: attached to the Comparison Result, especially load-bearing whenever a Trade-off is involved. Confidence: attached per candidate and to the overall result. Recovery: for a Tie, an unresolved Trade-off, or insufficient differentiation. Completion: Decision Complete once a winner is chosen or the tie/trade-off is accepted as the answer.

---

## 4. Information Priority Rules

1. Decision > Facts > Explanation > Actions — the answer always outranks the details behind it, which outrank the reasoning behind those, which outranks any further action available.

2. Verification Result > Legal Price > Charged Price — the delta itself matters more than either raw number alone.

3. Comparison Result > Trade-off > Supporting Facts — the outcome always outranks the specific dimensions that produced it.

4. Hard Constraint satisfaction > Strong Preference match > Soft Preference nudge — this mirrors the Recommendation Framework's own constraint tiers directly and governs every Recommendation and Comparison composition.

5. Confidence-bearing content always outranks confidence-free content of the same type — a Verified Fact about price precedes a Human-Judgment-tier inference about taste fit, even if both are technically supporting information.

6. Recovery Information, when active, outranks Progressive Information — something genuinely wrong or missing gets named before another routine question is asked.

7. Explanation outranks unrelated Contextual information — why something was recommended matters more than how the person arrived at this screen.

8. Persistent information is never displaced by transient information within the same composition — they coexist, but transient content never pushes persistent content out of primary position.

---

## 5. Information Relationships

**Always appear together:** Legal Price and Verification Result — verification means nothing without both. Comparison Result and the full candidate set — never partial. Recommendation and Explanation — never one without the other. Confidence and whatever it describes — never standalone.

**Never appear together:** Observed/Charged Price within Beer Detail — that's Price Verification's exclusive territory. A Trade-off stated without its constituent Facts — an unsupported assertion, not an explanation. Occasion-Fit content at equal weight to Budget — a direct violation of Principle 8.

**Dependencies:** Alcohol-Adjusted Value depends on Legal Price, ABV, and Size. Style Benchmark depends on Alcohol-Adjusted Value existing across the catalog. Recommendation depends on Preference Summary. Verification Result depends on both prices. Explanation always depends on its parent object.

**Mutually exclusive:** a Recommendation composition's outcome is either a single winner or a Trade-off/Tie, never both presented as simultaneously true. Decision Status at "Decision Complete" is mutually exclusive with active Progressive Information.

---

## 6. Progressive Disclosure

**Always immediately visible:** the Primary information for whichever Experience is active — the Recommendation itself, the Verification Result, the Comparison Result, the Beer Identity. None of this is hidden behind further interaction, per Principle 1 and the Recommendation Framework's explainability requirement.

**Only appears when needed:** Recovery Information, only while its condition is active. The next Progressive question, only until enough is known. Deeper explanation detail beyond the initial inline statement, reachable through "Why" but never forced on first view. Style Benchmark detail, which can reasonably be a secondary reveal without competing with the primary Alcohol-Adjusted Value figure for attention.

**Why:** this mirrors the Decision Engine Model's discipline against asking unnecessary questions, and the Recommendation Framework's rule against surfacing trivial differences — applied here to information display rather than question-asking.

---

## 7. Cross-cutting Information

**Recommendation Explanation** attaches to Recommendation, Verification Result, and Comparison Result specifically — never presented as a free-floating object separate from what it explains.

**Confidence** attaches to every object above the Verified-Fact tier. Verified Facts don't need explicit confidence language, since they're uniformly high by definition; Computed and Human-Judgment-tier objects always carry it.

**Learning ("Why")** is not a new object — it's a retrieval mechanism that re-surfaces an existing Explanation on request. It never generates new content.

**Decision Complete** is represented by Decision Status reaching its terminal value, behaving identically regardless of which composition it appears in.

**Recovery** is represented by Recovery Information, which can appear within any composition without altering that composition's fundamental priority order — it simply inserts at high priority, per Rule 6, whenever active.

---

## 8. Validation

**Every Experience has a composition:** confirmed — all six are documented in Section 3.

**Every information object has an owner:** confirmed — Beer Identity, Legal Price, ABV, Size, Alcohol-Adjusted Value, and Style Benchmark are owned by Beer Detail; Observed Price and Verification Result by Price Verification; Recommendation and Preference Summary by Recommendation; Comparison Result and Trade-off by Comparison; Confidence, Explanation, Decision Status, and Recovery Information are cross-cutting by design, owned by no single composition, consistent with their nature.

**No information is duplicated:** confirmed with one clarification worth stating explicitly — Legal Price appears in both Beer Detail and Price Verification, but Beer Detail is the canonical display home and Price Verification only references it, matching the Information Architecture's own ownership rule. This is a reference, not a duplication.

**No composition violates the Information Architecture:** confirmed — Observed Price never appears in Beer Detail, matching its explicit exclusion there.

**No composition violates Experience Flows:** confirmed — Comparison's composition treats ties and trade-offs as complete outcomes, not degraded ones, consistent with Experience Flow Principle 9.

---

## 9. Governing Principles

1. No future screen may reorder the Information Priority Rules for visual convenience. Priority is canonical, not a design preference.

2. No future interface may split a Trade-off from its constituent Facts across different views.

3. No future interface may display Observed/Charged Price outside a Price Verification composition.

4. No future interface may present Confidence as an afterthought, separate from the object it describes.

5. No future interface may treat Recovery Information as optional polish — it is required whenever its triggering condition is active.

6. No future interface may persist Preference Summary across sessions without first revisiting the Product Definition Document's boundary against accounts.

7. No future interface may give Occasion or other deferred, low-confidence inputs the same informational prominence as Budget or core preferences.

8. No future composition may show a Recommendation or Comparison Result without its Explanation attached.

9. No new Information Object may be introduced without first tracing it back to the Beer Knowledge Model or Feature Inventory.

10. No composition may hide Primary information behind Progressive or Contextual information.

11. Every future platform must derive its content order from Section 4's priority rules, never invent its own.

12. Style Benchmark and other Important-Soon-After objects may be composed as secondary information once available, but their absence must never be treated as a missing Primary object.

13. No future composition may state a Recommendation, Verification Result, or Comparison Result without its Confidence tier attached, regardless of platform constraints.

14. Learning ("Why") must always retrieve an existing Explanation, never generate new content not already implied by the object it explains.

15. This document, together with the nine it depends on, is the complete reference for content composition. No future screen may resolve an information-ordering question by design instinct when a canonical rule already exists here.
