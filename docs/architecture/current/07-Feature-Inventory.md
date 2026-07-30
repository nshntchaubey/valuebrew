# ValueBrew — Feature Inventory
### The canonical inventory of every product capability implied by the six frozen documents, refined for cross-functional use and for internal conceptual consistency. Not a PRD, not information architecture, not UI design. Answers one question: what exactly is the user able to do with this product?

---

## 1. Capability vs. Mechanism

A **capability** is something the canon evidences a need for. A **mechanism** is one of possibly several implementation choices that satisfy a capability, without changing what the Decision Engine or Recommendation Framework actually does underneath it. The canon is deliberately mechanism-agnostic; this inventory does not need to be, and mechanisms are treated below as their own layer, not folded into capability decisions.

---

## 2. Feature Taxonomy — Abstraction Layers

Every item in this document belongs to exactly one of the six layers below. No item is described in more than one layer's terms — this section exists specifically to enforce that, after an earlier draft occasionally gave Features their own "entry points" as if they were independent destinations, which they are not.

**Module** — a coherent, top-level area of the product, made up of one or more Experiences. A Module is what a roadmap would be organized around.

**Experience** — a complete, nameable interaction with its own entry point and its own end state. Something a person would describe as "I did X." Experiences may route through or invoke one another, but each has an independent beginning.

**Feature** — a capability that exists *within*, or attaches *across*, one or more Experiences. A Feature is never itself a destination — it has no independent entry point, only a place it attaches to or modifies.

**Engine Behavior** — an internal rule governing how the Decision Engine reasons or responds. Never directly interacted with; experienced only through its effect on a Feature or Experience.

**Platform Service** — shared infrastructure every Experience, Feature, and Engine Behavior depends on, but which is not itself part of any interaction.

**Mechanism** — an implementation-level method for satisfying a capability. Never canonically mandated or excluded; justified on ordinary product grounds, not by citation to the frozen documents.

---

## 3. Product Modules

**Discovery Module**
Experiences: Beer/SKU Identification, Beer Detail.

**Verification Module**
Experiences: Price Verification.

**Recommendation Module**
Experiences: Full Recommendation.
Features belonging to this Module: Confirm-as-Is, Low-Confidence Response, Planning Mode, Proxy-Buying Mode, Preference Input Handling (budget, style, strength, size, brand, and — distinctly flagged for its different canonical confidence — occasion).

**Comparison Module**
Experiences: Beer Comparison.

**Cross-cutting Features** — belong to no single Module, since they attach across all of them: Recommendation Explanation, "Why"/Learning Query Handling.

**Engine Behaviors** — apply across the entire product, not owned by any one Module: Progressive Question-Asking, Segment-Appropriate Restraint, Confidence Communication, Trade-off and Tie-handling logic.

**Platform Services** — depended on by everything above, owned by none of it: Beer Knowledge Base/Catalog, Style Benchmark/Relative Value Ranking computation, State & Flow Management.

**Mechanisms** — serve specific Experiences without altering them: Search, Browse, Barcode Scan, Image Recognition, all currently serving Beer/SKU Identification only.

**One clarification worth making explicit, since it resolves something the previous draft left ambiguous:** the same underlying logic can appear at two different layers without contradiction. Trade-off and Tie-handling is an Engine Behavior, always present, Core from day one, because Full Recommendation cannot ethically function without it. Beer Comparison is a separate Experience that *uses* that same behavior but wraps it in its own dedicated, user-initiated destination — and that Experience can be deferred without deferring the behavior itself. These are not the same commitment, and treating them as one was the source of the earlier draft's inconsistency.

---

## 4. Product Capabilities

Each item below is tagged with its layer. Entry points and outcomes are given only for genuine **Experiences** — Features do not have independent entry points, only a place they attach.

**Beer/SKU Identification** — *Experience, Discovery Module.*
Outcome: the user leaves knowing the engine has correctly identified the specific beer they mean.
Entry points: Home, Search, Browse.
Served by mechanisms: Search, Browse, Barcode Scan, Image Recognition.

**Beer Detail** — *Experience, Discovery Module.*
Outcome: the user leaves with a clear picture of what this specific beer costs, how strong it is, and how it stacks up on value.
Entry points: Search, Browse, Recommendation, Comparison.

**Price Verification** — *Experience, Verification Module.*
Outcome: the user leaves with confidence that a specific price is legitimate, or a plain statement that it isn't.
Entry points: Beer Detail, Home (direct verification intent).

**Full Recommendation** — *Experience, Recommendation Module.*
Outcome: the user leaves with one specific beer to buy, or an honest trade-off between close options, matched to what they said mattered to them.
Entry points: Home, Planning.

**Beer Comparison** — *Experience, Comparison Module.*
Outcome: the user leaves understanding specifically what differs between named options, or that they're genuinely equivalent.
Entry points: Beer Detail, Search results, Recommendation.

**Confirm-as-Is** — *Feature, Recommendation Module.* Attaches to: Beer Detail. Not an independent destination — it is the recommendation logic ("is this already the best fit") surfaced at the moment a person views detail on an already-identified beer.

**Low-Confidence Response** — *Feature, Recommendation Module.* Attaches to: Full Recommendation, Beer Comparison, Price Verification — any Experience where insufficient information exists. Not itself a destination; a response mode any of the above can produce.

**Planning Mode** — *Feature, Recommendation Module.* Attaches to: Full Recommendation only. A caveat-carrying modifier, not a separate build.

**Proxy-Buying Mode** — *Feature, Recommendation Module.* Attaches to: Full Recommendation only. A conservative-default modifier, not a separate build.

**Preference Input Handling** — *Feature, Recommendation Module.* Attaches to: Full Recommendation, Beer Comparison. Covers budget, style, strength, size, and brand inputs uniformly. Occasion is included here, not as a separate Feature, but flagged distinctly because its canonical confidence — and therefore its MVP tier — differs from the other input types it sits alongside.

**Recommendation Explanation** — *Cross-cutting Feature.* Attaches to: every Experience above. Never a destination of its own.

**"Why"/Learning Query Handling** — *Cross-cutting Feature.* Attaches to: the output of any prior Experience. Retrieves and re-presents Recommendation Explanation's reasoning after the fact; generates nothing new itself.

---

## 5. MVP Classification

Tested with one question throughout: if this item disappeared, would the MVP still fulfill the Product Definition Document's stated purpose? Layer is noted alongside each item, since an Experience and the Engine Behavior it depends on can legitimately sit in different tiers, as explained in Section 3.

**Core V1:**
- Beer/SKU Identification (Experience) — nothing else can function without it.
- Beer Detail (Experience) — without it, a person has no way to see what the engine knows before deciding what to ask for next.
- Price Verification (Experience) — explicit Essential in the Product Definition Document.
- Full Recommendation (Experience) — the product's stated core purpose.
- Confirm-as-Is (Feature) — without it, an anchor-known interaction has no default behavior, breaking Segment-Appropriate Restraint, itself Core.
- Recommendation Explanation (Feature) — explicit Essential; without it, every other Core item violates the Recommendation Framework's explainability rule.
- Low-Confidence Response (Feature) — without it, the engine has no honest behavior under the uncertainty the Behavioral Hypothesis Model documents throughout.
- Preference Input Handling (Feature) — for budget, style, strength, size, and brand specifically; occasion is excluded from this Core commitment, see Future below.
- Progressive Question-Asking, Segment-Appropriate Restraint, Confidence Communication, Trade-off/Tie-handling logic (Engine Behaviors) — non-negotiable; every Core Experience above would violate the Recommendation Framework without them.
- Beer Knowledge Base/Catalog, State & Flow Management (Platform Services) — structurally required by every Core item above.

**Important Soon After:**
- Beer Comparison (Experience) — the dedicated, user-initiated, multi-candidate destination. Its underlying Trade-off/Tie-handling behavior is Core and cannot be deferred; the standalone destination wrapping it can be, since a person can approximate the same outcome by requesting Full Recommendation more than once.
- "Why"/Learning Query Handling (Feature) — inline explanation is Core; a separate after-the-fact retrieval on top of it is a real improvement, not a structural requirement.
- Style Benchmark/Relative Value Ranking (Platform Service) — alcohol-adjusted value stands alone as an absolute figure without this; the richer relative framing is worth building soon, not on day one.
- Planning Mode (Feature) — the underlying Full Recommendation logic is Core; this specific caveat-carrying treatment deserves its own refinement pass.

**Future:**
- Proxy-Buying Mode (Feature) — explicitly deferred given the model's unknown prevalence for this behavior.
- Occasion as an input within Preference Input Handling — explicitly deferred given the model's own note that this space is partially served elsewhere already.

**Out of Scope:**
- Any Fallback/substitute-suggestion capability at any layer — the Product Definition Document states this "should probably never exist."
- Any Profile, login, or account system; e-commerce or delivery; a social or ratings platform; a loyalty program; sensory or flavor attributes; AI-generated flavor descriptions; crowdsourced ratings; inferred popularity; store-level price comparison.

Mechanisms are never classified in this tier system at all — which specific identification method ships first is an implementation decision made against ordinary product constraints, not a canonical one.

---

## 6. Feature Dependencies

**Beer Detail** depends on: Beer/SKU Identification (Experience), Beer Knowledge Base/Catalog (Platform Service), Style Benchmark (Platform Service, once available).

**Price Verification** depends on: Beer/SKU Identification (Experience), Beer Knowledge Base/Catalog (Platform Service).

**Full Recommendation** depends on: Beer Knowledge Base/Catalog (Platform Service), Progressive Question-Asking (Engine Behavior), Preference Input Handling (Feature), Recommendation Explanation (Feature).

**Confirm-as-Is** depends on: Beer Detail (Experience), Price Verification (Experience), Segment-Appropriate Restraint (Engine Behavior).

**Beer Comparison** depends on: Beer Detail (Experience, once per candidate), Trade-off/Tie-handling (Engine Behavior), Recommendation Explanation (Feature).

**"Why"/Learning Query Handling** depends on: Recommendation Explanation (Feature) directly.

**Planning Mode, Proxy-Buying Mode** each depend on: Full Recommendation (Experience) directly — both are modifiers, not independent builds.

---

## 7. Feature Relationships

**No-anchor, budget-led:**
Home → Beer/SKU Identification → Full Recommendation → Recommendation Explanation → Decision Complete.

**Anchor already known:**
Search or Browse → Beer Detail → Confirm-as-Is → Recommendation Explanation → Decision Complete
*or, if openness is signaled:* → Beer Comparison → Decision Complete.

**Explicit price check:**
Home → Beer/SKU Identification → Price Verification → Recommendation Explanation → Decision Complete.

**Explicit comparison:**
Search (multiple candidates) → Beer Detail (each) → Beer Comparison → Recommendation Explanation → Decision Complete.

**Planning ahead:**
Home (planning intent) → Full Recommendation, with Planning Mode attached → Recommendation Explanation (carrying the standing caveat) → Decision Complete.

**Revisiting reasoning:**
Any completed Experience above → "Why"/Learning Query Handling → back to Decision Complete, or forward into a refined Full Recommendation.

Every composition terminates the same way: Recommendation Explanation feeding into Decision Complete. No journey in this product should end anywhere else.

---

## 8. Feature Principles

1. Every feature must trace back to a specific user intent named in the User Interaction Model.
2. No feature exists to increase engagement or time spent. Every feature exists to shorten or improve one specific decision.
3. A feature's classification must be justified by evidence strength in the Behavioral Hypothesis Model, never by how easy it would be to build.
4. No feature may claim more confidence than the Beer Knowledge Model's classification of its underlying facts actually supports.
5. A feature serving only a deferred or excluded capability must not be built, however small the increment seems in isolation.
6. Engine Behaviors and Shared Platform Services must never be presented to a person as if they were features in their own right.
7. Every user-facing item must be explainable under the Recommendation Framework's rules, or it isn't ready to exist yet.
8. A new item must never require reinterpreting or weakening any of the six frozen documents to make sense.
9. Items must degrade gracefully under low confidence, rather than being blocked entirely or faked with false certainty.
10. No item should exist because a competitor has it. Only because a canonical document evidences the need for it.
11. The absence of an item is exactly as deliberate as the presence of one, and deserves to be documented as such.
12. Every dependency must be named explicitly before an Experience is classified as Core — it cannot be Core if something it structurally depends on isn't.
13. Adding an item must never silently expand what "preference" or "recommendation" means beyond what the Product Definition Document already defines.
14. An item deferred to Future may only be promoted once real usage evidence justifies it — internal enthusiasm is not sufficient grounds.
15. Mechanisms are implementation choices, not canonical commitments — a capability may be served by more than one mechanism, or a new one later, without requiring any change to the canon.
16. Every item in this inventory belongs to exactly one abstraction layer — Module, Experience, Feature, Engine Behavior, Platform Service, or Mechanism. An item described in more than one layer's terms, or given properties that belong to a different layer, is a sign this document needs correcting, not the layer definitions.
17. This inventory itself must remain re-derivable from the six frozen documents alone. If an item can't be traced back to one of them, it does not belong here.
