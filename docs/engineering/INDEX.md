# ValueBrew Engineering Documentation — Index

This index is the table of contents for the Engineering folder. Each entry below states a document's purpose, what it depends on, what it produces, and where it sits in the recommended reading order. Consult the README for the philosophy behind these documents; consult this index for what to read and in what sequence.

---

## 1. Engineering Planning Roadmap

**Purpose:** Sequences the work needed to move from frozen architecture to engineering-ready specifications — which artifacts remained, in what order, what could proceed in parallel, and what constitutes MVP implementation readiness.

**Inputs:** The full Canonical Architecture; the Architecture Resolution Report.

**Outputs:** A dependency-ordered inventory of the remaining architecture-closure and specification work, and the criteria distinguishing MVP-required work from deferrable work.

**Dependencies:** None — the first document in this folder.

**Recommended reading order:** 1

---

## 2. Home Engineering Screen Specification

**Purpose:** Translates the Home Screen Contract into a build-ready specification for the product's sole entry point and routing screen.

**Inputs:** Home Screen Contract; Search/Browse Results Screen Contract (for the comparison-intent routing clarification); Canonical Interaction Lexicon.

**Outputs:** Complete UI element, state, interaction, validation, and acceptance-criteria definitions for Home, with every requested category either mapped to a canonical state or explicitly marked unspecified.

**Dependencies:** Engineering Planning Roadmap.

**Recommended reading order:** 2

---

## 3. Search/Browse Results Engineering Screen Specification

**Purpose:** Translates the Search/Browse Results Screen Contract into a build-ready specification for the routing layer between Home and the two candidate-resolution screens.

**Inputs:** Search/Browse Results Screen Contract; Home Screen Contract (shared entry context); Beer Detail and Comparison Screen Contracts (hand-off preconditions).

**Outputs:** Complete specification of query/browse matching, candidate presentation, single- and multi-selection behavior, and hand-off logic — deliberately non-evaluative throughout.

**Dependencies:** Home Engineering Screen Specification.

**Recommended reading order:** 3

---

## 4. Recommendation Engineering Screen Specification

**Purpose:** Translates the Recommendation Screen Contract into a build-ready specification for the product's core synthesis screen.

**Inputs:** Recommendation Screen Contract; Decision Engine Model; Recommendation Framework.

**Outputs:** Complete specification of progressive questioning, Confidence Communication, Trade-off and Tie handling, Recommendation Explanation, and Recovery behavior, reproducing the Screen Contract's testable thresholds in full rather than in summary.

**Dependencies:** Engineering Planning Roadmap. Benefits from, but does not require, Home and Search/Browse Results context for its entry conditions.

**Recommended reading order:** 4

---

## 5. Beer Detail Engineering Screen Specification

**Purpose:** Translates the Beer Detail Screen Contract into a build-ready specification for the single-SKU explanatory screen.

**Inputs:** Beer Detail Screen Contract; Content Architecture; Recommendation Engineering Screen Specification (for the reused Explanation/Confidence structures).

**Outputs:** Complete specification of Verified and Computed Fact presentation, the Confirm-as-Is judgment, Style Benchmark graceful degradation, and hand-off behavior toward Price Verification and Comparison.

**Dependencies:** Recommendation Engineering Screen Specification; Search/Browse Results Engineering Screen Specification.

**Recommended reading order:** 5

---

## 6. Comparison Engineering Screen Specification

**Purpose:** Translates the Comparison Screen Contract into a build-ready specification for the multi-candidate reasoning screen.

**Inputs:** Comparison Screen Contract; Recommendation Framework; Recommendation and Beer Detail Engineering Screen Specifications.

**Outputs:** Complete specification of Trade-off Explanation and Tie Disclosure presentation, the dual-layer (per-candidate and result-level) Confidence model, and candidate-set management.

**Dependencies:** Recommendation Engineering Screen Specification; Beer Detail Engineering Screen Specification.

**Recommended reading order:** 6

---

## 7. Price Verification Engineering Screen Specification

**Purpose:** Translates the Price Verification Screen Contract into a build-ready specification for the bounded, single-purpose price-checking screen.

**Inputs:** Price Verification Screen Contract; Beer Knowledge Model.

**Outputs:** Complete specification of the three-dimension Confidence model, evidence-versus-conclusion presentation, and the screen's single, invitation-only hand-off to Beer Detail.

**Dependencies:** Home Engineering Screen Specification; Beer Detail Engineering Screen Specification (shared hand-off relationship).

**Recommended reading order:** 7

---

## Engineering Documentation Flow

```
Engineering Planning
        ↓
Engineering Specifications
        ↓
Flutter Implementation
```

**Engineering Planning** — the Roadmap, establishing what must exist and in what order.

**Engineering Specifications** — the six screen-level translations of the Canonical Architecture, in the reading order above.

**Flutter Implementation** — everything after this folder: widgets, APIs, backend design, and code. Outside this folder's scope entirely.
