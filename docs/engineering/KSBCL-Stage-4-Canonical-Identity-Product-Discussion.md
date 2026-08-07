# Stage 4 (Canonical Identity Resolution) — Product Design Discussion

### Not an architecture document. No mechanism, schema, or algorithm is proposed here. The goal is narrower: state precisely what the master architecture has already decided about canonical beer identity, and name — without resolving — the product-level questions that decision leaves open. Stage 4's architecture document is not drafted until this is reviewed and closed out.

**Status note:** the two open questions this document raises below — SKU-vs-family grain (§2) and `supplier_code`'s place in identity (§3) — have since been resolved by product-owner decision. See `KSBCL-Stage-4-Identity-Decision.md`, the single authoritative source. The remaining open item (§4, consolidating already-live canonical products) is unaffected and still open.

---

## 1. What the master architecture already decided

Cited directly from [`KSBCL-Beer-Pricing-Pipeline-Architecture.md`](KSBCL-Beer-Pricing-Pipeline-Architecture.md) — these are frozen, not up for re-litigation here:

- **KSBCL's Item Code is a source-system identifier, never the SKU identity** — preserved exactly, forever, never modified (§12.3).
- **`canonical_product_id`, a new, internally-generated, stable ID, is the actual SKU identity** — what `beer_master.csv` is keyed on, unique per row by construction (§4.4, §4.5, §12.3).
- **The matching key**, used both to test for auto-merge and to group review candidates: `(normalized_name_key, pack_size_ml, pack_count, container_type, supplier_code)` — five components (§4.4).
- **Auto-merge requires more than the matching key**: an item_code only auto-merges into an *existing* canonical product if the matching key **and** current price **and** `effective_date` all match exactly (§2, §4.4). A matching-key match with a different price or date creates a **new** canonical product and a flagged review candidate instead (the confirmed real "Budweiser Magnum" item-code-succession pattern).
- **Merging beyond auto-merge is exclusively human-confirmed, one-directional, and audited** — never automatic (§4.4, §12.3).
- **A canonical product is not assumed to map to exactly one item_code forever** — item-code succession/reissue is expected and already disproven as a 1:1 assumption (§10.5).
- **`item_code_canonical_map.csv` never deletes or renumbers an item_code** — only adds rows or, on an explicit human-confirmed merge, updates a mapping's `canonical_product_id` (§4.4).
- **Canonical identity is channel-independent** — the same real beer sold both duty-free and standard-retail shares one `canonical_product_id` (§6.5, §12.2).
- **Future enrichment should join on `canonical_product_id`, not `ksbcl_item_code`** — canonical product is explicitly framed as "the real-world-product identity, which is the semantically correct join target" (§10.1).
- **Lifecycle (LIVE/DELISTED, never deleted, can reactivate)** is specified precisely at the *item-code* level (§7.2) and stated to apply "the same event-classification logic... simply run at different keys" at the canonical-product level (§7.1, §4.5's `status`/`delisted_run_month` fields). This is a reasonable, cited inference for canonical products, not a separate explicit restatement — flagged below as worth confirming, not because it's genuinely in doubt.

**What this amounts to:** the master has fully decided the *mechanism* for testing whether two rows are the same canonical product, and the *audit discipline* around merging. It has not stated what canonical identity is *for*, at a product level — which is where the open questions below come from.

---

## 2. Two identity models the master's key conflates

The master never says this explicitly, but the matching key answers a more specific question than "is this the same beer" — it answers "is this the same **retail SKU**, from the same **supplier**, right now."

- **Retail SKU identity** — what a shopper actually picks up: brand + style + volume + container. Two different volumes of "Kingfisher Strong" are two different things a shopper chooses between.
- **Product (or product-family) identity** — a coarser grouping: "Kingfisher Strong Beer" as a brand+style, independent of which pack size or container currently expresses it.

The current key operates at (and beyond) SKU grain — it doesn't just include volume/container, it also includes `pack_count` (a wholesale case-size fact) and `supplier_code` (a distribution-channel fact), neither of which a shopper ever perceives as part of "which product this is."

**Open question 1 — is `canonical_product_id` meant to be SKU identity, or is a coarser product-family grouping also needed?** The master never names this second layer at all. If ValueBrew ever wants to show "Kingfisher Strong — available in 330ml can, 500ml can, 650ml bottle" as one browsable entry with SKU variants underneath, that's a concept this document doesn't currently have room for — not because it was rejected, but because it was never asked. Worth deciding now, since it changes what `canonical_product_id` is allowed to mean before Stage 4 is built, not after.

**Resolved** — `canonical_product_id` represents retail SKU identity (brand/style + `pack_size_ml` + `container_type`), not a coarser product family. See `KSBCL-Stage-4-Identity-Decision.md`.

---

## 3. Two components of the matching key that may not belong in identity at all

Both of these were already flagged as open, unresolved questions during Stage 3's own review — carried forward here rather than re-derived, since Stage 4 is where they actually need an answer.

**`pack_count`.** A real beer's case size is a wholesale procurement fact between KSBCL and a specific supplier — not something a shopper buying one bottle ever perceives, and not something that stays constant even for a genuinely unchanged product (the same real SKU can be cased at 12 for one supplier and 24 for another with nothing about the product itself different). Including it in the identity key risks the *opposite* of the master's own "no duplicate live SKUs" goal: it can fragment one real retail SKU into multiple canonical products purely because of how KSBCL happened to case it for a given supplier that month.

**`supplier_code`.** This one is new to this document, surfaced directly by real Stage 3 output during acceptance review, not by inference: `structured_rows.csv` for 2026-06 shows real rows like "Kingfisher Strong Premium Beer 650ML" listed by *six different suppliers* — United Breweries (three separate entity listings), Blossom Industries, Mount Everest Breweries — at six different prices (₹125–₹190). Under the current key, each becomes a *separate* canonical product, because `supplier_code` is part of identity. Is that the right model of "one canonical beer" — six canonical products for what is, to a shopper, obviously one beer at six regionally-varying prices? Or should regional supplier variance be represented as multiple concurrent *listings*/*price points* under one canonical product, the same way `beer_master.csv` already represents multiple time-varying prices for one item_code via `beer_price_history.csv`?

**Resolved** — regional supplier variance is represented as listings beneath one canonical product; `supplier_code` is not part of canonical identity. See `KSBCL-Stage-4-Identity-Decision.md`.

**Why this matters now, not later:** both of these are currently load-bearing parts of the auto-merge test. Changing either after Stage 4 has already run for real months means retroactively re-grouping canonical products that already have real, accumulated history — a materially harder migration than deciding the question before the first Stage 4 run.

---

## 4. `canonical_product_id` lifecycle

**Already decided:** created once per genuinely new SKU (by the current key's definition); never deleted or reused; a mapped item_code can go `DELISTED` and later reactivate to `LIVE` without a new ID (item-code-level pattern, extended by the "same logic, different key" framing to canonical level); a canonical product can accumulate many item_codes over its life (succession), never assumed 1:1.

**Not addressed anywhere in the master:** what happens when two *already-existing, already-live* canonical products are later discovered to be the same real product — a genuine identity-resolution correction, not an item-code succession. The master's merge mechanism (§4.4) only describes folding a *new item_code* into an *existing* canonical product; it has no described path for consolidating two canonical products that already have their own accumulated `item_code_canonical_map.csv` rows and (once Stage 5 exists) their own price history. If either open question above (§3) is resolved in a way that *narrows* the identity key later, this exact scenario — two canonical products that should become one — is precisely what that migration would require. Worth deciding whether this needs its own mechanism now, or is explicitly deferred with the risk named.

---

## 5. What depends on `canonical_product_id` being right

Concretely, not speculatively — all of it already named in the master:

- `beer_master.csv`'s core structural guarantee, "no duplicate live SKUs," is only true *by construction* because `canonical_product_id` is unique per row (§4.4/§4.5, checked in §9's validation).
- Every app-facing feature the master explicitly lists as reading `beer_master.csv` exclusively — Price Verification, Value Score, the recommendation engine, retail comparisons (§6.5) — inherits whatever `canonical_product_id` gets right or wrong, since none of them re-derive identity themselves.
- Future enrichment (barcode, brewery data, crowd-sourced facts) is explicitly designed to join on `canonical_product_id`, not `ksbcl_item_code` (§10.1) — meaning a wrong or too-narrow identity model doesn't just affect today's catalog, it affects the join key every future data source will be matched against.

---

## 6. Summary — existing decisions vs. open product decisions

| Question | Status |
|---|---|
| Item Code is not SKU identity; `canonical_product_id` is | **Decided** (§12.3) |
| The 5-component matching key + price/date-for-auto-merge mechanism | **Decided** (§4.4) |
| Merges beyond auto-merge are human-confirmed, one-directional, audited | **Decided** (§4.4, §12.3) |
| Canonical products can accumulate item_codes over time, never 1:1 | **Decided** (§10.5) |
| Channel-independence (DF and retail share one canonical product) | **Decided** (§6.5, §12.2) |
| Lifecycle: never deleted, LIVE/DELISTED, reactivation | **Decided, by extension of the item-code-level rule** — worth an explicit one-line confirmation, not a live question |
| Whether `canonical_product_id` is SKU identity or also needs a coarser product-family layer | **Resolved** — retail SKU identity; see `KSBCL-Stage-4-Identity-Decision.md` (§2 above) |
| Whether `pack_count` (procurement case size) belongs in the identity key | **Open** — already flagged during Stage 3, unresolved (§3 above) |
| Whether `supplier_code` belongs in the identity key, or regional variance should live under one canonical product | **Resolved** — excluded, represented as a listing; see `KSBCL-Stage-4-Identity-Decision.md` (§3 above) |
| Whether/how two already-live canonical products can ever be consolidated after the fact | **Open** (§4 above) |

---

No architecture is proposed here, and nothing above should be read as a recommendation — the point of this document is only to make the open questions visible and separate from what's already settled, before Stage 4's architecture gets drafted against them.
