# Stage 4 Canonical Identity — Settling the Product Semantics

### Follow-up to `KSBCL-Stage-4-Canonical-Identity-Product-Discussion.md`. Still not an architecture document — no mechanism, schema, or algorithm is proposed. This one takes a position on each of the four open questions, grounded in the master architecture's own stated goals and the real 2026-06 dataset, and separates a clear recommendation from a genuinely open call in each case.

**Status note:** the `supplier_code` position below (§1) is now the recorded product decision — see `KSBCL-Stage-4-Identity-Decision.md`, the single authoritative source. §2–§4 are unaffected by that decision.

---

## 1. Should `supplier_code` participate in canonical identity?

**Recommendation: No — it's source metadata, not product identity.**

The master's own test for what belongs in `canonical_product_id` is explicit: it's "the real-world-product identity, the semantically correct join target" (§10.1). `supplier_code` fails that test directly — it answers *who delivered this listing to KSBCL*, not *what the product is*. A shopper choosing a bottle off a shelf has no visibility into, and no interest in, which of several regional distributors supplied it.

**Confirmed by real data, not just argued from principle:** `structured_rows.csv` for 2026-06 shows "Kingfisher Strong Premium Beer 650ML" listed by six different suppliers — United Breweries (three separate entity listings across regional plants), Blossom Industries, Mount Everest Breweries — at six different prices, ₹125 to ₹190. Under the current key, that becomes six separate canonical products for what is, to a shopper, unambiguously one beer at regionally varying prices.

**Nothing is lost by removing it from the key.** `supplier_code` stays a per-`item_code` field on `item_code_canonical_map.csv` regardless — the master's own schema already carries it there independent of whether it's part of the *matching* key (§4.4). `beer_price_history.csv` is already keyed at `ksbcl_item_code` grain, not canonical grain (§12.3, §4.6) — so per-supplier price history is fully preserved either way. And `beer_master.csv`'s existing `representative_item_code` mechanism (§4.5: "the newest-`effective_date` one... lowest item code breaks a tie") already knows how to pick one price to show when multiple item_codes map to one canonical product — exactly the machinery needed to collapse six supplier listings into one displayed price, with zero new mechanism required.

I don't see a stated ValueBrew feature that needs per-supplier product differentiation — Price Verification, Value Score, and retail comparisons (§6.5) are all framed as *product-vs-product* comparisons, never *distributor-vs-distributor* for the same product. If anything, six near-identical cards differing only by supplier would be catalog clutter, not a feature.

---

## 2. Should `pack_count` participate in canonical identity?

**Recommendation: No — same reasoning as `supplier_code`, on principle; the real data neither confirms nor contradicts it this month.**

`pack_count` is a wholesale order-line fact — how many units KSBCL bundles for one transaction — not a property of the retail item. A consumer buying one bottle never encounters "case of 12" vs. "case of 24" as a product distinction; that choice belongs to whoever is placing a wholesale order, not to the retail SKU itself.

**Honest accounting of what the real data actually shows:** I checked directly for the pattern I expected — the same product (identical `normalized_name_key` + `pack_size_ml` + `container_type`) appearing at different `pack_count` values, either within one supplier's own listings or across suppliers. **Zero such cases exist in the real 2026-06 snapshot.** This doesn't weaken the conceptual argument (a wholesale case-size fact can be stable for months and still be the wrong *kind* of fact to hang product identity on), but it does mean I can't point to a concrete instance of `pack_count` fragmenting identity the way I can for `supplier_code`. The risk is real in principle and already flagged once (the Budweiser-style item-code-succession pattern shows KSBCL *does* re-list the same product differently over time) but isn't independently confirmed to have fired yet for `pack_count` specifically, this month.

Same "nothing is lost" argument as §1 applies: `pack_count` remains available per-`item_code` for whatever validation purpose Stage 3 already established it for (the MRP-vs-selling-price sanity check), just not used to define sameness.

---

## 3. What does `canonical_product_id` represent?

**Recommendation: retail SKU identity — brand + style + volume + container. Not a product family, and not something broader.**

Once `supplier_code` and `pack_count` are set aside (§1, §2), what's left in the matching key is exactly `(normalized_name_key, pack_size_ml, container_type)` — the precise set of facts a shopper actually distinguishes between on a shelf. That's a deliberate, narrow answer, not a default: the master's stated *purpose* for `beer_master.csv` — Price Verification and Value Score (§6.5) — requires this exact granularity. You cannot verify a price or compute a value score without knowing the specific size and container; collapsing "Kingfisher Strong" across all its pack sizes into one entry would break the feature the master built Stage 4 to serve, not just leave a gap.

This directly resolves the product-family question raised in the earlier discussion document: a coarser "Kingfisher Strong — available in three sizes" grouping is a real, plausible future need, but it is **not** what `canonical_product_id` should become. If ValueBrew wants that browsing view later, it should sit *above* `canonical_product_id` as an additional grouping layer (e.g. a family ID referencing multiple canonical products), never as a redefinition of what canonical identity already correctly does at SKU grain.

---

## 4. Should two existing canonical products ever be merged, and what would Stage 4 need to preserve history safely?

**Recommendation: don't build the merge workflow now — no confirmed need yet, the same "confirm, then build" discipline this whole project has applied everywhere else — but the schema should not foreclose it. One small, specific addition earns its place; nothing else does.**

The reassuring finding first: the master's *existing*, already-frozen design is substantially merge-safe by construction, without any new mechanism. `beer_price_history.csv` is keyed at `ksbcl_item_code`, never at `canonical_product_id` (§12.3) — so a future canonical-level correction never touches the most valuable, hardest-to-regenerate historical data at all. `item_code_canonical_map.csv`'s `canonical_product_id` column is already described as updatable on a human-confirmed action (§4.4) — merging two existing canonical products is a small conceptual extension of a capability that already exists (repoint every `item_code` currently mapped to the retiring ID onto the surviving one), not a new one. And `beer_master.csv` is already rebuilt from current state each run, so the retired canonical product's row simply stops being produced once nothing maps to it anymore — no deletion logic needed.

**One real gap, worth naming precisely:** nothing today would record that a `canonical_product_id` was ever retired, or what it became. Master §10.1 explicitly designs future enrichment to join against `canonical_product_id` — if an external source ever joined against an ID that later gets merged away, there's currently no way for it to discover the redirect. The smallest capability worth reserving is a **retired-ID audit record** (old ID → surviving ID, when, why, human-confirmed) — conceptually one small step beyond `item_code_canonical_map.csv` itself, not a new category of mechanism. This mirrors exactly how the master already reserves `gtin`/`gtin_confidence` as empty-but-present columns for a capability not yet built (§10.2) — the same "reserve the seam, don't build the feature" pattern, applied here to one specific, narrow gap rather than a general merge workflow.

---

## Summary of positions taken

| Question | Position | Confidence |
|---|---|---|
| `supplier_code` in identity? | No | Decided — recorded product decision, see `KSBCL-Stage-4-Identity-Decision.md` |
| `pack_count` in identity? | No | Moderate — sound in principle, not yet independently confirmed by an observed fragmentation case |
| What is `canonical_product_id`? | Retail SKU identity (name + size + container) | High — required by the master's own stated Price Verification / Value Score purpose |
| Build canonical-to-canonical merge now? | No — but reserve a retired-ID redirect record as a named, empty seam | High on both halves |

Nothing above has been written into any architecture yet — these are recommended settlements, ready for confirmation before Stage 4's architecture is drafted against them.
