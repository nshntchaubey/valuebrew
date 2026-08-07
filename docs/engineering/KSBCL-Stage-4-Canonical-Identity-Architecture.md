# ValueBrew — KSBCL Stage 4 (Canonical Identity Resolution) Architecture

### The complete design for Stage 4 of the KSBCL beer pricing pipeline. Governed by [`KSBCL-Beer-Pricing-Pipeline-Architecture.md`](KSBCL-Beer-Pricing-Pipeline-Architecture.md) (§2, §4.4, §4.5, §6.5, §7.1, §8.3, §9, §10.1, §10.5, §11, §12.3 in particular) and built directly on top of [`KSBCL-Stage-3-Normalization-Architecture.md`](KSBCL-Stage-3-Normalization-Architecture.md) (frozen) and the recorded [`KSBCL-Stage-4-Identity-Decision.md`](KSBCL-Stage-4-Identity-Decision.md). Where this document departs from the master architecture's original §4.4 mechanism, the departure is cited explicitly as flowing from the recorded Identity Decision — never a silent change.

**Status: DRAFT — first pass, not reviewed, not frozen.** This document follows the same architecture standard applied to Stage 2 and Stage 3, but is explicitly not being proposed as ready to freeze. Every place a genuine judgment call was made rather than derived from an already-decided document is recorded in §13, "Architecture Questions Deferred to Freeze Review," and is not to be treated as settled by virtue of appearing in the body text above it. **Revised twice.** First, in §6/§7/§3.2, to correct a confirmed contradiction: the original draft removed master §4.4's price/`effective_date` review gate unconditionally, when only its cross-supplier configuration is actually addressed by the recorded Identity Decision — the same-supplier configuration master built that gate for was restored unchanged. Second, in §6/§7/§3.2/§8, to implement the recorded Stage 4 Identity Resolution Decision 2 (`KSBCL-Stage-4-Identity-Decision.md`): when a key matches more than one existing, live canonical product, Stage 4 does not choose among them — it defers to manual review. That behavior is a recorded product decision, not an architectural inference.

---

## 0. Sources consulted

The master pipeline architecture (§2's pipeline diagram; §4.4's original matching key, resolution logic, and `item_code_canonical_map.csv` schema sketch; §4.5's note that `representative_item_code` selection belongs to the master-construction step; §6.5's channel-independence decision; §7.1's two-diffs-at-two-grains framing; §8.3's duplicate-item-code failure mode; §9's validation checklist; §10.1's future-enrichment join-target framing; §10.5's non-assumption list; §11's build-order note that auto-merge and manual-review must ship together; §12.3's original canonical-identity decision). Stage 3's frozen architecture (§9 in particular, which already states the exact handoff contract this document inherits rather than re-derives). The four product-design documents and the recorded Identity Decision, all now internally consistent per the prior documentation-governance pass. Real Stage 3 output for 2026-06 (`pricing_data/runs/2026-06/normalized_rows.csv`, 1,714 rows, joined against `structured_rows.csv` on `item_code`) was queried directly to validate the mechanism proposed below against real data — not invented examples — the same discipline Stage 2 and Stage 3 held themselves to.

---

## 1. Purpose and scope

**Stage 4 owns exactly one job:** resolving every beer row Stage 3 normalized to a stable `canonical_product_id`, representing retail SKU identity as defined by the recorded Identity Decision, and recording that resolution in a permanent, append-mostly map. Concretely, Stage 4:

- Reads every row present in this run's `normalized_rows.csv` (Stage 3's own frozen contract already restricts this to Stage 2's `included = true` rows — Stage 4 does not re-derive or re-check inclusion).
- Determines, for each `item_code` not already mapped from a prior run, whether it belongs to an existing canonical product or is the first sighting of a new one.
- Produces `item_code_canonical_map.csv` — the permanent record of every `ksbcl_item_code` ever seen and the canonical product it belongs to.
- Produces `canonical_resolution_review.csv` — this run's informational flags for human awareness (§7; its role is narrower than the master's original sketch, for reasons cited there).
- Is deterministic and idempotent given a fixed prior map state and a fixed row-processing order (§8).

**Stage 4 explicitly does NOT own:**

- **`beer_master.csv` / `beer_master_duty_free.csv` construction** — Stage 5's job entirely (master §2, §4.5). Stage 4 produces the mapping Stage 5 reads; it does not select a `representative_item_code`, does not compute a canonical-level `LIVE`/`DELISTED` status, and does not write either master file.
- **Price history** — Stage 5's job entirely (master §4.6, §7).
- **Beer/not-beer classification** — already decided by Stage 2.
- **Normalization** — already decided by Stage 3; Stage 4 treats `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type`, and `display_name` as given, frozen inputs.
- **Consolidating two already-separately-created canonical products** ("canonical-to-canonical merge") — explicitly out of scope; see §12.
- **Any UI or display-layer grouping** — Stage 4 produces data, never a presentation concept. Whether or how the app surfaces multiple listings under one canonical product is entirely downstream of this document.
- **Barcode/GTIN or any other enrichment join** — master §10.2, out of Phase 1 scope; this document only shapes `canonical_product_id` so that future join can happen (master §10.1).
- **Abbreviation/alias expansion, supplier-name aliasing, per-unit price computation** — master §12.6, §9, §5.5 respectively; unchanged, not re-litigated here.

---

## 2. Inputs and outputs

### 2.1 Inputs

- **`normalized_rows.csv`** (Stage 3, frozen, this `run_month`): `item_code`, `display_name`, `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type`. Defines Stage 4's row set exactly — one row per `item_code` in scope for this run.
- **`structured_rows.csv`** (Stage 1, frozen, this `run_month`): joined on `item_code` for the fields Stage 3 does not carry — `supplier_name`, `supplier_code`, `declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp`, `effective_date`. Stage 4 is the first stage to need price and supplier information alongside normalized name/pack fields in one place.
- **The prior run's `item_code_canonical_map.csv`** (Stage 4's own persistent state, `pricing_data/item_code_canonical_map.csv`, master §3) — every `ksbcl_item_code` ever resolved by a previous run, and what it was resolved to. On a first-ever run, this input is empty (bootstrap; §8).

### 2.2 Outputs

- **`item_code_canonical_map.csv`** (`pricing_data/`, permanent, append-mostly — master §3, §4.4). Every `ksbcl_item_code` ever seen across all runs, each mapped to a `canonical_product_id`. Never deletes or renumbers a row; an existing row is only ever updated in place for `item_status`, `last_seen_run_month`, or (on an explicit human-confirmed action) `canonical_product_id` itself.
- **`canonical_resolution_review.csv`** (`pricing_data/runs/<run_month>/`, per-run — master §3). This run's newly observed informational flags. Scoped narrower than the master's original sketch; see §7 for what changed and why.

---

## 3. Public contract

### 3.1 `item_code_canonical_map.csv`

| Field | Notes |
|---|---|
| `ksbcl_item_code` | Preserved exactly, never modified — the authoritative source-system key (master §4.4). |
| `canonical_product_id` | Stable, internally-generated ID — the SKU identity per the recorded Identity Decision. Opaque, permanent, never reused or renumbered. Its concrete generation format (sequential, UUID, prefixed string, or otherwise) is an implementation-time choice, not fixed by this document — the only architecture-level requirement is that it be stable and never collide. |
| `supplier_name`, `supplier_code` | Carried on the map regardless of the fact that neither participates in the matching key (§4) — this is source/listing metadata about this specific `item_code`, not a claim about canonical identity. |
| `match_confidence` | `deterministic_high` (exact matching-key match against an existing canonical product's already-mapped item code) \| `manual_confirmed` (a human confirmed a link that the mechanism itself did not establish) \| `unreviewed` (brand-new canonical product; nothing to confirm). |
| `matched_rule` | `exact_key_match` \| `manual_review` \| `new_canonical`. |
| `item_status` | `LIVE` \| `DELISTED` — at the item-code level only. Stage 4 sets this from whether the item_code is present in this run's `normalized_rows.csv`; it does not compute or roll this up to a canonical-level status (that is Stage 5's job, master §4.5). |
| `first_seen_run_month`, `last_seen_run_month` | |

### 3.2 `canonical_resolution_review.csv`

| Field | Notes |
|---|---|
| `run_month` | Which run produced this flag. |
| `item_code` | The item_code the flag concerns — the one that did **not** auto-attach. |
| `canonical_product_id` | The **new** canonical product created for this item_code (§6, step 2b, or step 2a's multi-candidate branch) — never one of the existing ones it was compared against. |
| `reason` | `possible_supersession` — master §4.4's own reason, restored unchanged (§7) — or `ambiguous_key_multiple_candidates` — per the recorded Stage 4 Identity Resolution Decision 2 (`KSBCL-Stage-4-Identity-Decision.md`), §7. |
| `matched_item_code` | For `possible_supersession`: the existing, same-supplier item_code whose price or `effective_date` did not match. For `ambiguous_key_multiple_candidates`: one of the multiple qualifying candidate item_codes — one row is written per candidate (§7). |

This file is where a human's confirmation is required before two item_codes are ever treated as the same canonical product (§6, step 2a's multi-candidate branch or step 2b; §7) — a row here means the automated mechanism explicitly declined to resolve the relationship, not that a merge already happened. No field on this file represents anything beyond §7's own resolution flow: a human either confirms a link (repointing an item_code onto the correct existing canonical product, per §9) or does nothing, leaving the canonical products as they are.

---

## 4. Canonical identity model

**`canonical_product_id` represents a retail SKU** — brand/style + `pack_size_ml` + `container_type` — per the recorded Identity Decision, not a coarser product family and not a wholesale order line. `supplier_code` is explicitly excluded: it is carried on `item_code_canonical_map.csv` as descriptive metadata about a specific `item_code` (§3.1), never as a component of what makes two rows "the same product."

**Matching key:** `(normalized_name_key, pack_size_ml, container_type, pack_count)`.

This is the master's original five-component key (§4.4) with `supplier_code` removed, per the recorded Identity Decision, which explicitly supersedes that one component. **`pack_count` remains in the key.** The Identity Decision resolved `supplier_code` only; it did not rule on `pack_count`, and master §4.4 still names `pack_count` as a required component. Two of the four product-design documents (Settlement, Charter) argued for excluding it, but neither was elevated to a recorded product-owner decision the way `supplier_code` was — Stage 3's own architecture explicitly declined to act on this same point for the same reason (§12.2 of that document). This document carries `pack_count` forward unchanged rather than silently applying an analysis that was never formally decided (§13, item 2).

**Channel independence is unchanged from master** (§6.5, §12.2): both the standard-retail and duty-free channels flow through this same resolution mechanism and share one `canonical_product_id` space. A beer sold in both channels resolves to one canonical product, not two.

**Real-data validation.** Querying the real June 2026 output directly: 1,714 included rows collapse to 1,122 distinct groups under this four-component key — 719 groups of exactly one `item_code` (no attach event), and 403 groups where two or more item_codes share an identical key (at least one attach event each; the largest such group has 10 item_codes). "Kingfisher Strong Premium Beer 650ml" illustrates the mechanism concretely and splits into exactly two such groups, not one:

- Ten item_codes (`2020900300`, `2580900200`, `2640900200`, `2710900200`, `2720900200`, `2730900200`, `2770901600`, `2780900100`, `2790900100`, `2850900400`) share the key `("kingfisher strong premium beer 650ml", 650, unknown, null)` — no case-multiplier text, no recognized container word — spanning ten distinct suppliers (United Breweries under four different regional entity names, Blossom Industries, Mount Everest Breweries, Bombay Breweries, Wave Distilleries, Impala Distillery) at prices from ₹80.00 to ₹190.00.
- A separate six item_codes (`2060901000`, `2060903700`, `2100900200`, `2100904800`, `2640900400`, `2930900200`) share the key `("kingfisher strong premium beer 650mlx12btls", 650, bottle, 12)` — explicit ×12 bottle case text — at ₹180.00–185.00.

These are two genuinely different structured facts (case size and container are both actually stated differently in the source text), so two canonical products is the correct outcome, not a defect. Within the first group, two of the ten item_codes (`2060901000`/`2060903700`, and separately `2100900200`/`2100904800`, both within the second group) additionally share the same supplier, price, and effective date as each other — the exact scenario master's original design built the auto-merge mechanism for (the page-186 Haywards 5000 pattern). That scenario is a strict subset of the rule below and is handled correctly by it.

---

## 5. `canonical_product_id` lifecycle

- **Created** exactly once, the first time an `item_code` is resolved that does not exactly match any existing canonical product's key (§6). Never created speculatively, never pre-allocated.
- **Never deleted, never renumbered, never reused** — mirrors the permanence master already requires of `ksbcl_item_code` itself (§4.4).
- **Can accumulate any number of mapped item_codes over its life** — both across runs (item-code succession, e.g. a KSBCL re-issuance) and within a single run (multiple suppliers' concurrent listings, §4, §6). No 1:1 assumption between a canonical product and an item_code is made anywhere in this design, consistent with master §10.5.
- **Item-level status only.** Stage 4 sets `item_status` (`LIVE`/`DELISTED`) per mapped `item_code` based on that item_code's presence in the current run. It does not compute a canonical-product-level status — a canonical product with at least one `LIVE` item_code and several `DELISTED` ones is a fact Stage 5 rolls up (master §4.5), not one Stage 4 asserts.
- **No lifecycle event this document defines for the canonical product itself** — unlike `beer_price_history.csv`'s event types (master §4.6), `item_code_canonical_map.csv` is current-state, not an append-only ledger of events. Its own history — when a canonical product first appeared, when an item_code attached to it — is fully recoverable from `first_seen_run_month`/`last_seen_run_month` per row plus the run-dated archive (master §3), without a separate event log.

---

## 6. Exact merge semantics

**Resolution, per `item_code`, each run, processed in `structured_rows.csv`'s original row order (load-bearing for determinism, §8):**

1. **Already mapped** (present in the prior `item_code_canonical_map.csv` state, or mapped earlier in this same run) → no identity action; `last_seen_run_month` and `item_status` are updated only.
2. **Not yet mapped, and its matching key (§4) exactly equals the matching key of at least one already-mapped item_code.** Two sub-cases, distinguished by whether that match is available from a supplier *other than* this item_code's own, or only from the *same* supplier:
   - **2a — a different-supplier match exists.** Consider every already-mapped item_code sharing the exact key that belongs to a `supplier_code` other than this item_code's own, and the distinct, live `canonical_product_id`s they belong to.
     - **Exactly one such canonical product** → this item_code **attaches unconditionally** to it. `match_confidence = deterministic_high`, `matched_rule = exact_key_match`. No price or `effective_date` comparison gates this — per the recorded Identity Decision, differently-supplied listings of the same SKU are one canonical product regardless of price, "not as separate canonical products."
     - **More than one such canonical product** — possible once a same-supplier `possible_supersession` split (2b, below) has already divided this key across two canonical products — this item_code does **not** attach to any of them. Per the recorded Stage 4 Identity Resolution Decision 2 (`KSBCL-Stage-4-Identity-Decision.md`), the ambiguity is preserved, not resolved automatically: a **new** `canonical_product_id` is created for this item_code (`match_confidence = unreviewed`, `matched_rule = new_canonical`), and a row is written to `canonical_resolution_review.csv` for each candidate, `reason = ambiguous_key_multiple_candidates` (§7).
   - **2b — only same-supplier matches exist.** If every already-mapped item_code sharing the exact key belongs to the *same* `supplier_code` as this item_code, master §4.4's original bar applies, unchanged: attach only if price *and* `effective_date` also match exactly against at least one of them (`match_confidence = deterministic_high`, `matched_rule = exact_key_match`). If price or `effective_date` differs from all of them, this item_code does **not** attach — a **new** `canonical_product_id` is created instead, and a row is written to `canonical_resolution_review.csv` with `reason = possible_supersession` (§7) for manual review, exactly as master §4.4 specifies.
   - Where both a different-supplier match resolving to exactly one canonical product, and a same-supplier, non-matching-price/date match, exist for the same key, 2a's single-candidate branch governs — the cross-supplier evidence is sufficient on its own under the Identity Decision, and no additional flag is written for the same-supplier relationship in that case.
3. **Not yet mapped, and no exact key match exists anywhere** → a **new** `canonical_product_id` is created for this item_code. `match_confidence = unreviewed`, `matched_rule = new_canonical`.

**Why 2a departs from master's original mechanism, and 2b does not.** Master §4.4's original design gated every automatic merge on a full match — key, price, *and* `effective_date` — flagging anything less for manual review. Under the original five-component key (supplier included), an exact key match could only ever occur between two listings from the *same* supplier, so that gate was, in substance, always a same-supplier test; master's own worked example for the "key matches, price/date differs" branch is a same-supplier pair (§1: "Budweiser Magnum Beer-CAN 330ML×24Cans" under item codes `2170900611` and `2171700211`, both supplier 0217, confirmed real: ₹155.00/2025-08-25 and ₹140.00/2026-05-12). Removing `supplier_code` from the key, per the recorded Identity Decision, makes an exact key match reachable across different suppliers for the first time — and only for that new configuration does the Identity Decision say anything at all. It says nothing about the same-supplier configuration; master's original text, including its explicit "never automatic" language for a same-supplier key match with a price or date difference, governs that case unchanged, which is what 2b restores. Confirmed against real data: the Budweiser Magnum pair above is current in the 2026-06 run; under 2b it is correctly held apart pending manual review, not silently merged.

**Why 2a's multi-candidate branch defers rather than picks.** Once a same-supplier split (2b) has divided one key across two canonical products, a later cross-supplier item_code sharing that key has more than one valid attachment target, and nothing in the frozen repository determines which one is correct — this is not derivable from master, the Stage 1–3 contracts, or the Identity Decision by further analysis. The recorded Stage 4 Identity Resolution Decision 2 settles it as a matter of product policy: the ambiguity is preserved, not resolved by an automatic rule. This document implements that decision; it is not an architectural inference from anything stated elsewhere.

**Null/unknown key components.** `pack_size_ml = NULL` (Stage 3's sole "extraction failed entirely" signal, §3.1 of that document) is treated as insufficient for any exact-match attachment — an item_code with a null `pack_size_ml` is always its own new canonical product, regardless of what any other item_code's key looks like, since matching on an absent value would be exactly the kind of guess this pipeline never makes. `pack_count = NULL` and `container_type = unknown` are both legitimate, non-error values under Stage 3's own stated semantics (not signals of failure) and are treated as ordinary values participating in exact matching like any other — `NULL` matches `NULL`, `unknown` matches `unknown`, within an otherwise-exact key match. This distinction — and whether it is the right one — is flagged for freeze review (§13, item 3).

**Bootstrap (first-ever run).** Every item_code starts unmapped. Processing proceeds in the same deterministic row order; the first item_code seen for a given key becomes a new canonical product, and every subsequent item_code sharing that exact key within the same run attaches to it under step 2, with no special-cased "first run" behavior needed.

---

## 7. Review queue semantics

Master §4.4 defines `canonical_resolution_review.csv`'s purpose precisely: an item_code whose matching key matches an existing canonical product's mapped item_code, but whose price or `effective_date` does not, is never auto-merged — it gets a new `canonical_product_id` of its own and a flagged row, reason `possible_supersession`, awaiting a human's confirmation before any merge happens. This is unchanged by the recorded Identity Decision, which addresses only whether `supplier_code` participates in the matching key — it says nothing about this gate. §6, step 2b restores it exactly, correctly scoped to the same-supplier configuration master was always describing (§6's citation of the real Budweiser Magnum pair, both item_codes supplier 0217).

**`possible_supersession`** — the sole reason this document defines, master's own, unchanged. Written whenever §6 step 2b declines to auto-attach. `matched_item_code` (§3.2) records the same-supplier item_code whose price or `effective_date` didn't match, for a human to compare against. The row does not gate the pipeline's own progress — the flagged item_code already has its own new `canonical_product_id` by the time the row is written — but it does gate whether the two are ever *treated* as one canonical product: only a human's confirmed repoint (§9) can do that, never this document's own mechanism.

**The cross-supplier attachment path (§6, step 2a) writes no review-queue row when exactly one candidate canonical product qualifies.** That configuration did not exist under the original five-component key, and the Identity Decision's resolution of it, where it applies, is unconditional, not provisional — no reason is invented here for it.

**`ambiguous_key_multiple_candidates`** — the second reason this document defines, per the recorded Stage 4 Identity Resolution Decision 2 (`KSBCL-Stage-4-Identity-Decision.md`), not derived from master or any other frozen document. Written whenever §6 step 2a's condition is satisfied by more than one distinct, live canonical product. One row is written per candidate — all sharing the same flagged `item_code` and `run_month`, each citing a different `matched_item_code` — collectively naming every canonical product the key matched, for a human to consolidate. As with `possible_supersession`, the flagged item_code already has its own new `canonical_product_id` by the time these rows are written; nothing waits on them.

**What is not built, unchanged from master:** any mechanism for a human to mark a `possible_supersession` row "resolved" other than the repoint itself (§9) — master §4.4 describes exactly one resolution path (a human-confirmed repoint of `item_code_canonical_map.csv`) and no other queue-state machinery. Whether some additional acknowledgment concept is wanted remains open (§13, item 4).

---

## 8. Determinism guarantees

Unlike Stage 3 (a pure function with no cross-run state), Stage 4 has persistent state (`item_code_canonical_map.csv`) by design — its determinism claim is conditioned on that state, the same way Stage 2's is (Stage 2 architecture §9.1).

**Given:**
- a fixed prior `item_code_canonical_map.csv` state (this run's legitimate input, the previous run's legitimate output), and
- a fixed row-processing order for this run's `normalized_rows.csv` / `structured_rows.csv` join,

resolution for every item_code in this run is fully determined — the same input state and the same row set always produce the same map. **Row-processing order is load-bearing, not incidental**, because §6's within-run attachment behavior depends on it (an item_code can attach to a canonical product created earlier in the same run's processing, so which item_code is treated as "first" — and therefore becomes the canonical product's originating entry rather than an attachment to it — is a function of order). This document fixes that order to `structured_rows.csv`'s own original row order, mirroring the precedent Stage 3 already established for its own determinism claim.

**Where a key matches more than one existing canonical product** (§6, step 2a's multi-candidate branch), the rule remains fully deterministic without needing a tie-break: per the recorded Stage 4 Identity Resolution Decision 2, the outcome is always to defer to review rather than choose among the candidates, so the same input state always produces the same (non-)choice.

**Re-running an already-processed month** against the same prior map state deterministically reproduces the same `item_code_canonical_map.csv` and `canonical_resolution_review.csv` for that run — never appends, never duplicates, mirroring Stage 1's and Stage 3's own idempotency bar.

---

## 9. Auditability

**What is directly auditable from `item_code_canonical_map.csv` as specified:** which run first saw a given item_code (`first_seen_run_month`); whether an item_code's canonical product was assigned by exact-key mechanism or by a human (`match_confidence`, `matched_rule`); the item_code's own supplier and current liveness. Combined with the run-dated archive already required by master §3, the full sequence of monthly map states is reconstructable without re-reading the source PDF, the same reconstructability guarantee every earlier stage's audit artifact provides.

**What is not fully auditable as specified, and is flagged rather than silently resolved:** master describes a human-confirmed repoint of `canonical_product_id` (the only path to `manual_confirmed`) as "a deliberate, audited... action, never automatic" (§4.4), but neither master's own field list nor this document adds a field recording *who* confirmed it, *when*, or what the item_code's `canonical_product_id` was immediately before the repoint. `match_confidence` changing to `manual_confirmed` shows *that* a human acted, not the specifics of the action. Whether this needs its own explicit audit fields is deferred (§13, item 5) rather than answered by inventing columns master never specified.

---

## 10. Failure modes

**Row-level:** none beyond what §6 already specifies as ordinary outcomes — an incomplete key (`pack_size_ml = NULL`) is a legitimate, non-error state that always produces a new canonical product, not a failure requiring a flag or an abort.

**Structural failures, hard-abort the run (mirroring Stage 1–3's own posture):**
- **Join integrity** — an `item_code` present in `normalized_rows.csv` but absent from `structured_rows.csv` (needed for `supplier_code`/price/`effective_date`), or vice versa. Structurally should be impossible given both are frozen outputs of prior stages for the same `run_month`, checked anyway (the same defensive posture Stage 3 §2.4 applies to its own equivalent check).
- **Zero rows to process** — an empty `normalized_rows.csv` for this run_month aborts, mirroring Stage 2's and Stage 3's own zero-included-rows hard assert.
- **A corrupted or unreadable prior `item_code_canonical_map.csv`** — Stage 4 cannot safely resolve identity against unknown prior state; this aborts rather than silently treating the run as a fresh bootstrap.
- **A duplicate `ksbcl_item_code` appearing twice within `item_code_canonical_map.csv` itself** — the extraction-bug-shaped failure master §8.3 already names, hard-fails distinctly from the real-world "two different item_codes, same product" condition, which is never a failure (§6).

**No mid-run checkpointing, idempotent all-or-nothing output** — mirrors master §8.4/§8.5 exactly; a failed run produces no partial `item_code_canonical_map.csv` update and never overwrites the previous good state in place.

---

## 11. Relationship to Stage 3 and Stage 5

**Stage 3** hands off exactly what its own §9 already commits to: `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type` (four of this document's matching-key inputs) and `display_name` (for Stage 5's eventual human-facing use). Stage 4 additionally reads `supplier_code`, the four price fields, and `effective_date` directly from `structured_rows.csv` — Stage 3 never touches these, and this document does not ask Stage 3 to change anything about its own frozen contract.

**Stage 5** reads `item_code_canonical_map.csv` as its own join key into `structured_rows.csv`/`normalized_rows.csv`, to build `beer_master.csv`/`beer_master_duty_free.csv` (master §4.5) and `beer_price_history.csv` (master §4.6, §7). Stage 4 does not select a `representative_item_code`, does not compute canonical-level `LIVE`/`DELISTED` status, and does not touch price history in any form — all three remain entirely Stage 5's design. One observation is worth carrying forward without resolving it here: master §4.5's `representative_item_code` mechanism was designed to pick *one* price to display per canonical product; the real multi-supplier groups validated in §4 above (e.g., ten concurrently live listings of one Kingfisher SKU at prices from ₹80 to ₹190) mean Stage 5 inherits a materially larger "how many concurrent listings does one canonical product actually have, and how should that be represented" question than master's original single-supplier-oriented design anticipated. This document does not answer that question — it belongs entirely to Stage 5's own architecture — but is noted here since it is a direct, foreseeable consequence of this document's own identity model.

---

## 12. Explicit non-goals

- **Consolidating two already-separately-created canonical products** ("canonical-to-canonical merge"). Already discussed and deliberately deferred in `KSBCL-Stage-4-Canonical-Identity-Settlement.md` §4 — no confirmed need yet, and building it now would be exactly the kind of premature feature this project's discipline avoids. This document does not reopen that deferral or build the reserved "retired-ID redirect record" seam it named; both remain future work, not Stage 4 Phase-1 scope.
- **`beer_master.csv` / `beer_master_duty_free.csv` construction, `representative_item_code` selection, canonical-level `LIVE`/`DELISTED` status, price history** — all Stage 5 (§11 above).
- **Fuzzy, edit-distance, or ML-based matching of any kind.** The matching key (§4) is always an exact match — this mirrors master §6.3's own stated posture toward Stage 2 ("no fuzzy/edit-distance matching... premature") and Stage 3's identical discipline; nothing about canonical identity resolution changes that stance.
- **Barcode/GTIN or any other enrichment join** — master §10.2, out of Phase 1; this document only ensures `canonical_product_id` is a stable, well-formed join target for that future work (master §10.1).
- **Abbreviation/alias expansion, supplier-name aliasing, per-unit price computation** — inherited exclusions from master §12.6, §9, §5.5; not re-litigated here.
- **Any UI, app-facing, or presentation-layer design.** Nothing in this document assumes or specifies how multiple listings under one canonical product are ever displayed — that is entirely downstream of Phase 1's data platform and outside this document's authority.
- **A human-facing workflow or tool for acting on `canonical_resolution_review.csv`.** This document specifies the file's contents (§3.2, §7); how or whether a human interacts with it operationally is not designed here.

---

## 13. Architecture Questions Deferred to Freeze Review

Recorded here rather than resolved silently, per this document's explicit drafting instruction. None of the following should be read as decided by virtue of a draft position appearing in the body text above.

1. **Whether `pack_count` should remain part of the matching key.** Master §4.4 still requires it, and no recorded Identity Decision has superseded that requirement, so this document keeps it in (§4). But `KSBCL-Stage-4-Canonical-Identity-Settlement.md` and `KSBCL-Stage-4-Product-Identity-Charter.md` both argued, on principle, for excluding it — that analysis was never elevated to a formal decision. Worth an explicit product-owner ruling, one way or the other, before freeze — the same discipline just applied to `supplier_code`.
2. **Whether `pack_count = NULL` and `container_type = unknown` should participate in exact-match attachment like any other value, or should be excluded from auto-matching the same way `pack_size_ml = NULL` is (§6).** This document's draft position treats them as legitimate values per Stage 3's own stated semantics; a more conservative alternative would treat any incompletely-specified key as ineligible for automatic attachment, favoring an even stronger bias toward false-split over false-merge.
3. **Whether `canonical_resolution_review.csv` needs any cross-run tracking or acknowledgment mechanism at all**, given an unactioned `possible_supersession` flag from a prior run is not carried forward or re-surfaced by anything in this design beyond what `item_code_canonical_map.csv` itself already shows (§3.2, §7). Whether that's acceptable, or whether Stage 4 needs something closer to Stage 2's persistent, episode-based review-queue lifecycle, is open.
4. **Whether a human-confirmed `canonical_product_id` repoint needs its own explicit audit fields** (who, when, prior value) beyond what `match_confidence`/`matched_rule` already show (§9). Master's own language ("audited... action") implies some record is expected; neither master's field list nor this document currently supplies one.
