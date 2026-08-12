# Recommendation Experience — Definitive Build Specification

*A build specification, not an architecture document. Every choice below either (a) restates a canonical MUST, (b) resolves an implementation-level ambiguity the canon already permits — decided here, not left open, and (c) is marked **[PRODUCT DECISION REQUIRED]** where the canon genuinely doesn't yet decide the question. Nothing in category (c) is silently resolved. Built from Decision Engine 2.0, Interaction Model 2.0, Conversation Model 1.0, Beer Knowledge Model 2.0, Domain Model 1.0, Catalog Specification 1.0, the shipped V1 Flutter implementation, and Generation 1's UI/engineering conventions where compatible.*

---

## 0. Scope and Non-Goals

**In scope:** the full Recommendation flow as canonically specified and already partially shipped — budget entry, optional style refinement, and the four honest outcome shapes (Winner, Tie, Conflicting Constraints, Low-Confidence Response) — including the Planning Mode variant.

**Explicitly out of scope, not oversights:**
- Named Recommendation Profiles (Budget Drinker, Craft Explorer, etc.) — a deliberately configurable future seam per Decision Engine 2.0 Part 9, never built, not built here.
- Strength, size, and brand as gathered inputs — canonically named as future ordered inputs, not part of V1's actual scope (budget + one optional style only).
- Any inferred or behavior-based personalization — permanently rejected.
- A UI entry point via Search/Browse — that screen has no Contract and does not exist; this spec assumes entry only via Home.
- Barcode scan as an identification mechanism — canonically unblocked but not part of this flow.
- Comparison hand-off UI polish — Comparison itself is specified but unbuilt; this spec defines only the *trigger point* for it, not its own screen.

---

## 1. Complete User Journey

Home (`homeToRecommendation({isPlanning})`) → **Initial** → **Gathering** (Budget, then conditionally Style) → **Evaluating** (transient, on every new input) → one of **Recommending (Winner)**, **Recommending (Tie)**, **Recovering (Conflicting Constraints)**, **Recovering (Low-Confidence)** → **Completed** (explicit acceptance) or a hand-off to Beer Detail / (future) Comparison / back into refinement.

---

## 2. State-by-State Specification

### 2.1 Initial / Budget Gathering

**Purpose:** capture the one mandatory Hard Constraint.

**Layout (top to bottom, per Content Architecture's Primary category):** a single, large, unmissable prompt — this is the entire screen's content until answered. No catalog content, no facts, no confidence indicators yet (nothing to be confident about).

**Copy:**
> "What's your budget?"
> *(helper text, smaller, secondary weight)* "We'll find the best value beer within it."

**Component:** a numeric input field, ₹-prefixed, large touch target, auto-focused on entry. **[Resolved]** No stepper, no slider — free numeric entry, since a budget is a specific number a person already has in mind, not a range to explore.

**Planning Mode banner, if flagged:** persists from this very first screen, small but always visible, never a dismissible one-time toast:
> "Planning ahead — prices may shift by the time you shop."

**Interaction:** submit via a clear "Continue" action or the input's own submit/return action. **[Resolved]** No auto-advance on typing-pause; budget is a Hard Constraint and deserves a deliberate confirmation, not an accidental one.

**Transition out:** on submit, moves to **Evaluating**.

---

### 2.2 Style Refinement (Conditional Gathering)

**Trigger:** only reached if the Decision Engine 2.0 §10 threshold fires — two or more candidates remain indistinguishable on budget alone *and* a style answer would actually separate them. **[Resolved, not a build choice but restated for implementability]** if the threshold doesn't fire, this state is skipped entirely — the flow goes straight from budget to an outcome. The build must never show this screen "just in case."

**Copy:**
> "Any style you're after?"
> *(secondary, always visible)* "No preference" — a real, equally-weighted option, not a buried skip link.

**Component:** a single-select chip group, using the pipeline's own controlled style vocabulary as the real, grounded option set — Lager, Strong Beer, Wheat Beer, Stout, IPA, Pilsner, Porter, Ale — **[Resolved]** rather than inventing a separate UI-facing taxonomy, this reuses the exact vocabulary already governing beer classification elsewhere in the product, so a style named here always means the same thing everywhere else in ValueBrew.

**Interaction:** tap one chip, or tap "No preference." **[Resolved]** Single-select only — Style is one Strong Preference in the current model, not a multi-select filter.

**Transition out:** re-enters **Evaluating** with the refined Preference Summary.

---

### 2.3 Evaluating (Transient)

**Purpose:** the moment between an input and an honest answer. Entered every time new information arrives, including the very first evaluation.

**Visual treatment:** a skeleton-loading placeholder, reusing the shipped `SkeletonBox` pattern already established at Beer Detail and Price Verification — **[Resolved, direct reuse of existing convention]** not a new loading pattern invented for this screen.

**Duration:** this is local computation over an already-loaded Catalog — no network call. **[Resolved]** the skeleton should render only if evaluation takes long enough to be perceptible (a brief minimum-display floor to avoid a jarring flash), never as a disguise for artificial latency.

**No copy.** A skeleton communicates "working," not a message.

---

### 2.4 Recommending — Winner

**Layout, following Content Architecture's composition categories in order:**
1. **Primary** — the winning beer's identity (name, brewery if available, size) and its Legal Price, stated plainly.
2. **Supporting** — Value/Style Standing, in plain language, never a bare number. **[Recovered from Generation 1]** Generation 1's Beer Detail used exactly this pattern — "a one-line plain-language verdict... never just a bare score." This build recovers that pattern here: *"Better value than typical for this style"* / *"Typical value for this style"* / *"Below typical value for this style"* — directly phrasing the three canonical Style Standing values, never a number, and gracefully omitted entirely if no Style Benchmark exists for this beer's style.
3. **Explanation** — always present in the same moment, following the certainty-then-judgment register shift:
   > "This fits your ₹[budget] budget — [ABV]% ABV, ₹[X] per litre — and seems to match the [style] you said you wanted."

   **[Resolved, per the canon's own literal cited example]** certain facts (price, ABV) stated as plain fact; the style match stated with "seems to," marking it as a judgment, not a verified fact.
4. **Confidence** — carried entirely by the sentence structure above, never a separate badge or number, per the Conversation Model's confidence-communication rule.
5. **Actions:**
   - **"See full details"** — primary action, hands off to Beer Detail carrying the SKU's identity.
   - **"Why this one?"** — secondary, expands/re-emphasizes the *same* Explanation already shown, never generates new content. **[Resolved]** implemented as a progressive-disclosure expansion (a slightly fuller restatement of the same reasoning), not a hidden-by-default explanation — the short form is always visible; this action only deepens it.
   - **"Change your answers"** — returns to refinement, preserving every other already-stated Constraint.

**Trust signal:** the Legal Price is never visually distinguished with a badge or icon suggesting extra authority beyond what the sentence itself states — its trustworthiness comes from being stated as plain fact, consistent with "price is a fact, not a feeling."

---

### 2.5 Recommending — Tie

**Layout:**
1. **Primary** — a plain statement that this is a genuine, complete answer:
   > "A couple of options tie for the best fit."
2. **Candidate list** — each tied candidate shown with the same identity + price + style-standing treatment as the Winner state, in the order the reasoning produced them (never re-sorted to imply a hidden ranking).
3. **Shared Explanation**, using the canon's own literal phrase:
   > "These are equivalent on everything you've told me matters."
4. **Actions, per candidate:** "See full details" only. **[Resolved]** no per-candidate "Why this one" — the shared explanation already covers the set; repeating it per-candidate would imply a distinction that doesn't exist.

**Explicitly forbidden here:** any visual emphasis (size, color, order) that would make one tied candidate look like the "real" pick. **[Resolved]** identical visual treatment for every candidate in the tie.

---

### 2.6 Recovering — Conflicting Constraints

**Trigger:** the stated budget and style together exclude every real candidate.

**Copy, naming both tension-producing inputs plainly, never dropping either silently:**
> "Nothing fits both your ₹[budget] budget and [style] — you'll need to loosen one of these."

**Component:** two clearly labeled adjustment paths, presented as equal alternatives:
- "Change budget"
- "Drop the [style] preference"

**[Resolved]** neither option is pre-selected or visually favored — the person decides which constraint to relax, the product never silently picks for them.

---

### 2.7 Recovering — Low-Confidence Response

**Trigger:** too little is known to distinguish among a large field honestly.

**Copy (single most useful next question form):**
> "I don't have enough to narrow this down yet — [the one specific next question]."

**Copy (provisional-answer form, when no further question would help):**
> "Here's a reasonable option based on what you've told me so far — though with less certainty than usual."
*(followed by one candidate, clearly labeled as provisional — not styled identically to a confident Winner card)*

**[Resolved]** the provisional-answer card uses a visually distinct treatment (e.g., a lighter-weight border or a small "provisional" label) from the confident Winner state — this is a legitimate implementation choice within the canon's requirement that low-confidence content never be presented with the same visual weight as high-confidence content.

---

### 2.8 Completed

**Trigger:** explicit acceptance of a Winner, a side of a Trade-off (future, via Comparison), or a Tie candidate.

**Behavior:** no dedicated "completed" screen — accepting *is* the hand-off to Beer Detail. **[Resolved]** Recommendation itself has no terminal visual state of its own; Decision Complete is represented by having left the flow, not by a confirmation screen, consistent with the canon's own description of Recommendation's Completed state.

---

## 3. Cross-Cutting Specification

### 3.1 Typography Intent
Budget prompt and outcome headline carry the heaviest visual weight on their respective screens — the single thing the screen exists to communicate. Explanation text is set noticeably lighter/smaller than the headline, signaling "supporting reasoning," never competing with the primary fact. Style-standing verdict text sits between the two in weight — important, but secondary to identity and price. **[Resolved]** no custom typeface; standard platform type scale, consistent with Generation 1's and the shipped Gen 2 app's shared "no custom design system" convention.

### 3.2 Spacing Intent
Generous spacing around the budget input on the Initial state — it is the only thing on screen and should feel unhurried. Outcome states use tighter, list-like spacing between Primary/Supporting/Explanation blocks so the full answer is visible without excessive scrolling on a typical phone screen. Tied candidates spaced identically to each other, reinforcing their equivalence visually as well as textually.

### 3.3 Iconography
Minimal, standard platform icons only — no custom illustration, no mascot, consistent with Generation 1's explicit precedent (stock favorite/favorite-border icons, no custom animation) and Generation 2's "no custom design system" convention. A single, consistent info-style affordance for "Why this one?" — the same icon everywhere it appears, never a different glyph per screen.

### 3.4 Animations and Transitions
**[Resolved, and this resolution is itself a citation, not an invention]** minimal to none. Both Generation 1's UI Philosophy ("no custom animation... consistent, deliberate constraint across every UI milestone") and Generation 2's shipped convention (no custom design system anywhere) converge on the same answer independently. Screen transitions use standard platform push/pop navigation animation only. The skeleton-to-content transition on leaving **Evaluating** is a simple cross-fade, not a custom reveal.

### 3.5 Accessibility
**No formal canonical accessibility standard exists yet** — this is explicitly, deliberately deferred at the architecture layer (Screen Specification Template §11 remains a placeholder). This build applies sensible baseline platform hygiene only, not a new standard: adequate touch target sizes on the budget input and style chips, semantic labels on every interactive element, and — directly required by the canon's own content rule, not just general best practice — the Style Standing verdict and the certainty/judgment register shift must never rely on color alone to communicate their distinction, since a real accessibility standard doesn't exist yet to specify how. **[PRODUCT DECISION / DESIGN DECISION REQUIRED]** a genuine accessibility standard, once ratified, should be re-applied to this screen; nothing here should be read as that standard.

### 3.6 Explanation Behavior (Consolidated)
Every Explanation on this screen is generated in the same computational pass as the conclusion it explains — **[Recovered from Generation 1, adopted as a build requirement, not just a UI convention]** score and explanation must be derived from the same underlying comparison logic, so the two can never drift apart. "Why this one?" and equivalent affordances only ever re-surface this same content, never compute something new on tap.

### 3.7 Confidence Presentation (Consolidated)
Never a number, a percentage, or a star rating, anywhere on this screen. Certainty is communicated by sentence register alone — plain statement for Verified/Computed facts, softened language ("seems to," "based on what you've told me") for anything resting on a Soft Preference match.

### 3.8 Information Priority
Per Content Architecture: Primary (identity + price) always above the fold on every outcome state; Supporting (value standing) immediately below; Explanation always visible, never behind an extra tap to *see that it exists* (only its *fuller* form is behind "Why this one?"); Recovery content, when active, replaces the Primary/Supporting/Explanation region entirely rather than being appended below a failed attempt at showing them.

### 3.9 Offline Behavior
The entire Recommendation flow operates against an already-loaded, bundled Catalog — no network dependency for the reasoning itself, consistent with V1's "no backend" architecture. The only failure mode is the Catalog failing to load at all, which is a technical/infrastructure failure, not a Recommendation-specific concern — handled by the shared `ErrorStateView` pattern already established elsewhere in the app, **never** relabeled as a Low-Confidence Response. This is a direct, explicit restatement of the canon's own rule that technical failures and Recovery States must never be conflated.

### 3.10 Data Dependencies
Per Catalog Specification 1.0: Identity and Packaging (mandatory, gates candidacy at all), Economic/Legal Price (mandatory), Composition/ABV (mandatory for value-based ranking — see the flagged gap below), Comparative/Style Benchmark (optional, gracefully omitted), Provenance/Confidence tiers (mandatory discipline, applied to every fact shown).

### 3.11 Analytics Events (Proposed Naming, Not Yet Built)
Consistent with the Founder Execution Blueprint's own plan to wire analytics as a pre-launch priority — proposed event names, to be implemented against the app's existing `AnalyticsSink` seam once that work begins: `recommendation_flow_started`, `budget_submitted`, `style_question_shown`, `style_selected` / `style_skipped`, `recommendation_outcome_shown` (with outcome type: winner / tie / conflicting / low_confidence), `explanation_expanded`, `recommendation_accepted`, `preference_refined`, `planning_mode_active`.

### 3.12 Implementation Notes
- Reuse `ErrorStateView` and `SkeletonBox` exactly as already established — do not introduce parallel loading/error components for this screen.
- Follow the shipped convention of private, screen-local widgets promoted to shared status only once a genuine second consumer exists — do not pre-extract a `RecommendationOutcomeCard` as a shared component speculatively.
- The domain function `generateRecommendation` already implements the ranking/tie logic described in Decision Engine 2.0; this spec describes how its output should be presented, not a change to that logic.
- Style options should be sourced from the same controlled vocabulary the classification pipeline uses, not hand-duplicated into the UI layer.

---

## 4. Edge Cases

- A candidate SKU with no confirmed ABV — see **Product Decision Required, item 1**, below.
- Budget entered as zero or a clearly invalid number — treated as an incomplete Hard Constraint, not submitted; the "Continue" action should not be reachable until a plausible positive number is entered. **[Resolved]** this is basic input validation, not a canon-level judgment call.
- Style question skipped, then budget refined afterward — the threshold logic re-runs fresh (per Decision Engine 2.0), potentially surfacing the style question again if it would now separate remaining candidates. **[Resolved]** this is the threshold rule operating correctly, not a new edge case needing special handling.
- Every candidate within budget has no Style Benchmark for its style — the Value/Style Standing line is omitted for all of them; the recommendation itself still proceeds normally on price/ABV alone.

---

## 5. Explicit Non-Goals (Restated)

No Recommendation Profiles, no strength/size/brand gathering, no inferred personalization, no Search/Browse entry point, no Comparison screen itself (only its trigger), no accounts, no persisted history of past recommendations, no rating or scoring language anywhere on this screen.

---

## 6. Items Requiring a Product Decision — Not Resolved Here

1. **What the Recommendation ranking should do with a candidate SKU that has an incomplete Composition Knowledge fact (no confirmed ABV).** This has now been flagged across Beer Knowledge Model 2.0, Decision Engine 2.0, Interaction Model 2.0, and Domain Model 1.0. It is flagged here a final time, at the exact point implementation would need it resolved: does an incomplete-ABV SKU get silently excluded from candidacy, included with an explicit caveat, or something else? **This build cannot correctly handle a real, incomplete launch catalog until this is decided** — it should be treated as a blocking dependency for shipping this screen against real data, not a detail to default on quietly during implementation.
2. **Whether Planning Mode needs an explicit exit interaction within one session.** Flagged in Interaction Model 2.0. This build deliberately does **not** add an ad hoc "exit planning mode" control, since inventing one would be inventing product behavior the canon hasn't authorized. Until decided, Planning Mode should be treated as one-way for the duration of a session once entered.
3. **A genuine accessibility standard** — this build applies baseline hygiene only (§3.5); a real standard is a future Product/Design Decision, not something this specification can originate.
4. **Whether any warmth beyond the Conversation Model's own current "minimal personality" recommendation is appropriate.** This build follows that document's existing working recommendation, which is itself explicitly labeled as an inference, not settled canon — noted here so a future tone decision doesn't need to rediscover that the current copy's calm register is a choice, not a requirement.

None of these four are decided by this document. Everything else above is either a direct restatement of canon or a resolved implementation choice made within the room canon already leaves for it.
