# KSBCL Stage 4 — Identity Decision Record

### The authoritative record of every Stage 4 product decision — decisions that shape canonical-identity behavior but cannot be derived from engineering analysis of the frozen repository alone. Stage 4 architecture implements what's recorded here; it does not re-derive or re-justify it.

**Scope note (Decision 1):** `pack_count`'s exclusion from canonical identity is already convergent across the four product-design documents and is not reopened here.

---

## Decision 1 — `supplier_code` and Canonical Identity

## 1. Decision to be made

**Does `supplier_code` participate in canonical product identity, or is it metadata attached to a listing beneath canonical identity?**

---

## 2. Two acceptable options

**Option 1 — Exclude.** `supplier_code` is not part of what makes two rows "the same product." Canonical identity is `(normalized_name_key, pack_size_ml, container_type)` only.

**Option 2 — Include.** `supplier_code` remains part of canonical identity, alongside the same three components. Two rows that are identical in name, size, and container but differ in supplier are different canonical products.

---

## 3. Consequences of each option

**Option 1 — Exclude:**
- The seven real supplier listings found for "Kingfisher Strong Premium Beer 650ml" (₹80–190) collapse into one canonical product.
- Stage 4 must still define how a single canonical product presents multiple concurrent supplier prices — this decision does not settle that mechanism, only that the need for one exists.
- If it later turns out that differently-supplied listings are materially different products rather than regional listings of one specification, this option understates that difference until corrected, and correcting it means splitting a canonical product that has already accumulated history.
- Matches the search, comparison, recommendation, and detail-page expectations described in `KSBCL-Stage-4-User-Mental-Model.md`.

**Option 2 — Include:**
- Canonical identity stays closer to the master architecture's originally frozen key.
- Supplier-level distinctions remain independently addressable as their own canonical products, so no product difference is ever hidden by the identity model itself.
- Produces the catalog fragmentation already documented — the same real beer appearing as multiple canonical products differing only by supplier — which `KSBCL-Stage-4-User-Mental-Model.md`'s journeys describe as reading as broken or duplicated to a user, unless a presentation-layer grouping is added on top of canonical identity.
- If it later turns out these listings are in fact interchangeable, consolidating them requires the canonical-to-canonical merge capability already named (but not built) in `KSBCL-Stage-4-Canonical-Identity-Settlement.md` §4.

---

## 4. Which existing documents are superseded, by option

| Document | Under Option 1 (Exclude) | Under Option 2 (Include) |
|---|---|---|
| `Canonical-Identity-Product-Discussion.md` | Open question §3 closed; nothing contradicted | Open question §3 closed; nothing contradicted |
| `Canonical-Identity-Settlement.md` | §1 recommendation stands as final; its confidence rating should be read as decided-by-product-owner, not evidence-alone | §1 recommendation and confidence rating are superseded |
| `Product-Identity-Charter.md` | §3/§5's "open case" for `supplier_code` is closed; principles 1–4 are unaffected either way | §3/§5's "open case" for `supplier_code` is closed; principles 1–4 are unaffected either way |
| `User-Mental-Model.md` | Its conclusion on `supplier_code` placement stands as final | Its conclusion on `supplier_code` placement is superseded; the journey-level UX observations may still motivate a presentation-layer grouping across canonical products, but not a change to canonical identity itself |

---

## 5. What Stage 4 architecture would assume under each option

**Under Option 1:** the matching key is `(normalized_name_key, pack_size_ml, container_type)`. Every `item_code` sharing those three values, regardless of supplier, resolves to one `canonical_product_id`. Stage 4 architecture must additionally specify how multiple suppliers' concurrent prices are represented and selected for display under that one canonical product — this is inherited, open design work, not settled by this decision.

**Under Option 2:** the matching key is `(normalized_name_key, pack_size_ml, container_type, supplier_code)`. Different suppliers of the same name/size/container produce distinct `canonical_product_id`s. Stage 4 architecture inherits an earlier priority on the canonical-to-canonical merge capability named in `Canonical-Identity-Settlement.md` §4, since consolidating supplier-distinct products later depends on it.

---

## Decision Rationale

ValueBrew is a consumer product, not a procurement system: the question a user is answering is "which beer do I want," not "which supplier delivered this particular batch." Canonical identity exists to model the former — the product a customer intends to buy — while supplier identity models a separate, operationally real fact: who currently supplies that product. A shopper's mental model of "the same beer" does not change when the supplier behind a listing changes, so folding supplier into canonical identity would mean the identity model is answering a question no user is actually asking. Keeping the two separate preserves one stable product across search, comparison, and recommendation, regardless of how many suppliers currently offer it. It also keeps the door open cheaply: multiple suppliers, regional pricing, listing-level price history, and future listing-only attributes (freshness, distributor, contract-brew source) can all be added beneath a canonical product without ever redefining what canonical identity itself means. Including supplier in identity would produce the opposite outcome — every new supplier of an existing beer minting a new "product" — which matches neither how a customer thinks about the catalog nor how comparison and recommendation are meant to work.

## Decision recorded

**Status: Decided.**

**Decision: Option 1 — Exclude `supplier_code` from canonical identity.** Recorded by the Product Owner, 2026-08-06.

`canonical_product_id` represents a retail SKU: brand/style + `pack_size_ml` + `container_type`. `supplier_code` is not part of canonical identity; supplier-specific information belongs beneath the canonical product as a listing. This document is now the single authoritative source for `supplier_code`'s status in canonical identity. The product-design phase is complete. Stage 4 architecture may begin.

---

## Decision 2 — Multi-Candidate Identity Ambiguity

### Context

A configuration Decision 1 doesn't address: once a same-supplier `possible_supersession` case (master §4.4) has split one matching key across two live `canonical_product_id`s, a later, different-supplier item_code sharing that same key has more than one canonical product it could legitimately attach to. No document in the frozen repository determines which one is correct, or whether the question should even be resolved automatically — this is a policy choice about how to handle ambiguity, not an engineering fact derivable from anything already on record.

### Decision to be made

When a not-yet-mapped item_code's matching key exactly matches more than one existing, distinct, live `canonical_product_id`, should Stage 4:

- **Option A** — deterministically attach it to one of them automatically (e.g., the earliest-established one), or
- **Option F** — treat the ambiguity itself as requiring manual review, leaving the item_code as its own canonical product until a human resolves it?

### Accepted trade-off

Option F costs more review volume: every new listing landing on an already-unresolved key adds to a queue already waiting on a human, and that queue can grow for as long as the original dispute stays open. It also costs some near-term catalog tidiness — a real beer may appear as more than one entry until someone consolidates them.

### Rationale

The two options fail differently, and the difference matters more than the trade-off's cost. An automatic tie-break that turns out wrong fails silently — it blends a listing into a comparison set it may not belong in, with nothing in the system ever prompting anyone to check a "successful" automatic match. Deferring to review fails visibly — a few redundant-looking catalog entries a human can notice and fix. For a product whose core value is a trustworthy price comparison, an invisible correctness error in that comparison is worse than a visible completeness gap in the catalog — the same asymmetry (false merge worse than false split) already governing every other identity decision in this pipeline. A deterministic tie-break would also assert a specific attribution — this listing belongs with this bucket, not that one — without evidence for that specific choice, which is a narrower instance of exactly the kind of invented fact this pipeline avoids everywhere else.

### Decision recorded

**Status: Decided.**

**Decision: Option F — ambiguity is preserved, not resolved automatically.** Recorded by the Product Owner, 2026-08-06.

When a not-yet-mapped item_code's matching key exactly matches more than one existing, live `canonical_product_id`, Stage 4 does not choose among them. The item_code becomes its own canonical product, and a row is written to `canonical_resolution_review.csv` for each candidate it matched, naming every one, for manual review. This document is now the single authoritative source for how Stage 4 handles multi-candidate identity ambiguity. Stage 4 architecture implements this decision; it does not derive it.
