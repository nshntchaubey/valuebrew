# ValueBrew — KSBCL Stage 5 (Master + History) Architecture

### The complete design for Stage 5 of the KSBCL beer pricing pipeline — the final Phase 1 stage, producing the actual deliverables: `beer_master.csv`, `beer_master_duty_free.csv`, `beer_price_history.csv`. Governed by [`KSBCL-Beer-Pricing-Pipeline-Architecture.md`](KSBCL-Beer-Pricing-Pipeline-Architecture.md) (§4.5, §4.6, §6.5, §7, §9, §10 in particular) and built directly on top of [`KSBCL-Stage-4-Canonical-Identity-Architecture.md`](KSBCL-Stage-4-Canonical-Identity-Architecture.md) (frozen).

**Status: DRAFT — reviewed once (independent adversarial pass), corrected, not yet frozen.** Follows the same architecture standard applied to Stages 2–4. Every remaining genuine judgment call is recorded in §12, "Architecture Questions Deferred to Freeze Review." **One Product Decision has been made and recorded: §6.3's freeze-at-last-known-values behavior for a fully-delisted channel is confirmed (product owner, 2026-08-07) — see §6.3.**

---

## 0. Sources consulted

The master pipeline architecture in full (§2's pipeline diagram; §4.5/§4.6's `beer_master.csv`/`beer_master_duty_free.csv`/`beer_price_history.csv` field sketches; §6.5's channel-independence decision; §7's two-diffs-at-two-grains framing and exact event-classification rule; §9's history/relational validation checklist; §10's enrichment-seam framing; §11's build-order note that Stage 5 must prove the "unchanged → no history row" path via a second, even if conceptual, run before being trusted). Stage 4's frozen architecture (§2.1, §3.1, §4, §6 — the exact shape of `item_code_canonical_map.csv` this stage reads). Real Stage 1/2/3/4 output for 2026-06 (`structured_rows.csv`, `classification_audit.csv`, `normalized_rows.csv`, `item_code_canonical_map.csv`) was queried directly to validate every mechanism below against real data — not invented examples.

**A real constraint on this document's own validation, disclosed rather than worked around:** this is the first month this pipeline has ever run end-to-end. There is no second month's PDF yet, so the `PRICE_CHANGE`/`CORRECTION`/`DELISTED` branches of §5 below cannot be exercised against two real, different monthly snapshots — only `INITIAL_BACKFILL` can be. Master's own §11 build-order note anticipates exactly this gap and prescribes a *conceptual* rerun (re-running this same month's data against itself) to prove the "unchanged → no history row" path produces zero spurious events before the pipeline is trusted against a genuinely new month. That conceptual proof is this document's real-data validation for everything except the three genuinely time-dependent branches, which remain validated by construction (traced against master's own literal rule, §5.2) rather than by a real second data point.

---

## 1. Purpose and scope

**Stage 5 owns exactly two jobs:** (1) maintaining `beer_price_history.csv` — an append-only, per-`ksbcl_item_code` ledger of every price ever observed — and (2) maintaining `beer_master.csv`/`beer_master_duty_free.csv` — the current, overwritten-each-run snapshot of every canonical product, one row per (`canonical_product_id`, channel). Concretely, Stage 5:

- Reads every `ksbcl_item_code` ever known to `item_code_canonical_map.csv` (Stage 4's permanent state) — not just item_codes in this run's `normalized_rows.csv` — since a `DELISTED` item_code still needs its master/history state carried forward untouched (§5, §6).
- For each such item_code present in this run's `structured_rows.csv`, diffs its current price tuple + `effective_date` against the last state recorded in `beer_price_history.csv`, and appends a history row exactly when something changed (§5).
- Rolls that same information up to the canonical-product level, per channel, and overwrites `beer_master.csv`/`beer_master_duty_free.csv` accordingly (§6).
- Is deterministic and idempotent given a fixed prior state (`beer_price_history.csv`'s last-known-per-item_code state, and the prior `beer_master.csv`/`beer_master_duty_free.csv`) and a fixed row-processing order (§8).

**Stage 5 explicitly does NOT own:**

- **Canonical identity resolution** — already decided by Stage 4. Stage 5 treats `canonical_product_id` and `item_code_canonical_map.csv`'s other fields as given, frozen inputs; it never creates, merges, or repoints a mapping.
- **Beer/not-beer classification, `is_duty_free` detection** — already decided by Stage 2. Stage 5 reads `is_duty_free` as a fact already computed there; it never re-derives it from `item_name_raw`.
- **Normalization** — already decided by Stage 3. `display_name`, `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type` are read as given.
- **Any enrichment (GTIN, ABV, calories, images, multi-source reconciliation)** — explicitly out of Phase 1 scope (master §10); the reserved `gtin`/`gtin_confidence` columns stay null.
- **A catalog-build step producing `catalog.json`** — master §10.4 names this as a distinct, not-yet-built future step that reads `beer_master.csv` as its spine. Stage 5 produces that spine; it does not consume it.
- **A canonical-product-level "price over time" view** — master §4.6 is explicit this is a derived, computed-on-read join (`item_code_canonical_map.csv` ⋈ `beer_price_history.csv`), never a separately stored file.

---

## 2. Inputs and outputs

### 2.1 Inputs

- **`structured_rows.csv`** (Stage 1, frozen, this `run_month`): `item_name_raw`, `supplier_name`, `supplier_code`, `declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp`, `effective_date` — the price tuple every diff in this document is computed from, plus `item_name_raw` for `beer_master.csv`'s own `item_name_raw` field (§3.1).
- **`run_summary.json`** (Stage 1, frozen, this `run_month`, `pricing_data/runs/<run_month>/`): `source_pdf_reference` — the only place this value actually exists; it is not a field on `structured_rows.csv` itself, and every schema in this document (§3.1, §3.2) requires it.
- **`classification_audit.csv`** (Stage 2, frozen, this `run_month`): `is_duty_free` (channel routing, §6.1), `confidence_tier`/`matched_signal_type`+`matched_term` (for `beer_master.csv`'s `classification_confidence`/`classification_matched_on` fields, §3.1). **Not every `LIVE` item_code has a row here.** This file is a real, strict subset of `structured_rows.csv` — confirmed on the real 2026-06 data, 4,518 scored rows out of 33,853 total — since Stage 2 only scores rows that match at least one signal at all. An already-mapped item_code can be genuinely `LIVE` (per Stage 4's `item_status`, driven by `structured_rows.csv` presence alone) while having no row here this run, or a row with `confidence_tier = none`, if Stage 1 stops extracting it entirely, or if Stage 2 simply doesn't score it as beer-like this run. §4's representative-eligibility rule and §6.3's freeze mechanism together define what happens in that case — this file's absence is never treated as an error.
- **`normalized_rows.csv`** (Stage 3, frozen, this `run_month`): `display_name`, `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type` — carried onto `beer_master.csv` from whichever item_code is selected as representative (§4).
- **`item_code_canonical_map.csv`** (Stage 4, frozen, permanent state, `pricing_data/`): every `ksbcl_item_code` ever seen, its `canonical_product_id`, `supplier_code`, and `item_status`. This is Stage 5's row set — Stage 5 processes every row here, not only rows touched this run (§1).
- **The prior run's `beer_price_history.csv`** (Stage 5's own permanent state, append-only): specifically, the most recent row per `ksbcl_item_code`, used as the "prior state" side of the item-code-level diff (§5). On a first-ever run, empty (bootstrap, §5.4).
- **The prior run's `beer_master.csv` / `beer_master_duty_free.csv`** (Stage 5's own permanent state, overwritten each run): used as the "prior state" side of the canonical-level diff (§6), and — only for a (`canonical_product_id`, channel) pair with zero currently-eligible `LIVE` item_codes this run — as the frozen values §6.3 carries forward untouched. On a first-ever run, empty (bootstrap).

### 2.2 Outputs

- **`beer_price_history.csv`** (`pricing_data/`, permanent, append-only — master §3, §4.6). Never updated or deleted; only ever appended to.
- **`beer_master.csv`** (`pricing_data/`, permanent, overwritten each run — master §3, §4.5). Standard-retail channel.
- **`beer_master_duty_free.csv`** (`pricing_data/`, permanent, overwritten each run — master §3, §4.5, §6.5). Duty-free channel. Same schema as `beer_master.csv`, same `canonical_product_id` space.
- **`archive/beer_master_<run_month>.csv`** (and a duty-free counterpart) — a dated snapshot of this run's master output, per master §3's archive convention, so a specific month's exact published state is recoverable without depending on git history of an overwritten file.

---

## 3. Public contract

### 3.1 `beer_master.csv` / `beer_master_duty_free.csv`

One row per (`canonical_product_id`, channel) — not one row per `canonical_product_id` (§4 explains why a canonical product can legitimately have a row in both files).

| Field | Notes |
|---|---|
| `canonical_product_id` | Stage 4's identity (§3.1 of that document). Unique per row within a given file by construction; a canonical product with live item_codes in both channels has one row in each file, never two rows in the same file. |
| `representative_item_code` | which mapped `ksbcl_item_code`, among this canonical product's item_codes *in this channel*, currently supplies every field below (§4). |
| `item_name_raw`, `display_name`, `normalized_name_key` | from the representative item_code (Stage 1/3). |
| `pack_size_ml`, `pack_count`, `container_type` | from the representative item_code (Stage 3). |
| `declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp` | from the representative item_code's current `structured_rows.csv` values, at native/unconverted granularity (master §5.4/§5.5 — no per-unit conversion invented here either). |
| `effective_date` | from the representative item_code. |
| `status` | `LIVE` \| `DELISTED` — `LIVE` as long as at least one mapped item_code in this channel is `LIVE` per `item_code_canonical_map.csv`'s `item_status` (§4.4 of master; §6.2 below). |
| `delisted_run_month` | nullable; set the run this channel's last `LIVE` item_code becomes `DELISTED`; cleared (`null`) again if a later run brings any item_code in this channel back to `LIVE` (§6.4). |
| `classification_confidence`, `classification_matched_on` | from the representative item_code's `classification_audit.csv` row (`confidence_tier`, and `matched_signal_type:matched_term` or `none`). |
| `gtin`, `gtin_confidence` | reserved, always `null` in Phase 1 (master §10.2). |
| `source_pdf_reference` | this run's source PDF identifier. |
| `first_seen_run_month` | the run this (`canonical_product_id`, channel) pair first got a row in this file — **never changes once set**, even as `representative_item_code` changes run over run. |
| `last_updated_run_month` | the most recent run that wrote this row, whether or not any field actually changed value (§6.4 — this is a "we looked" marker, not a "something changed" marker; that distinction is `beer_price_history.csv`'s job). |

### 3.2 `beer_price_history.csv`

One row per price-changing event, per `ksbcl_item_code`, ever. Never updated, never deleted.

| Field | Notes |
|---|---|
| `history_id` | surrogate key. |
| `ksbcl_item_code` | |
| `event_type` | `INITIAL_BACKFILL` \| `NEW_ITEM` \| `PRICE_CHANGE` \| `CORRECTION` (§5.2). |
| `effective_date`, `effective_date_raw` | this event's government-declared date. |
| `declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp` | the full price tuple at this event. |
| `previous_declared_price`, `previous_landed_cost`, `previous_ksbcl_selling_price`, `previous_mrp`, `previous_effective_date` | nullable — `null` for `INITIAL_BACKFILL`/`NEW_ITEM` (nothing to compare against), populated for `PRICE_CHANGE`/`CORRECTION`. |
| `observed_run_month`, `observed_at` | this pipeline's own clock. |
| `source_pdf_reference` | |

**No `DELISTED` event type exists here** (master §4.6) — delisting is carried entirely by `item_code_canonical_map.csv`'s `item_status` and `beer_master.csv`'s `status`/`delisted_run_month`; `beer_price_history.csv`'s stated purpose is prices ever seen, and delisting isn't a price event.

---

## 4. Representative item_code selection

**Per (`canonical_product_id`, channel), not per `canonical_product_id`.** Master §4.5 already scopes this correctly ("this canonical product's live, same-channel mapped item codes") — a canonical product with both a standard-retail and a duty-free item_code mapped to it gets independently evaluated once for each channel, producing up to two rows, one per file, each with its own representative_item_code drawn only from that channel's own live item_codes.

**Rule (master §4.5, unchanged):** among this (`canonical_product_id`, channel)'s currently-`LIVE` mapped item_codes, the one with the newest `effective_date` wins; the lowest `ksbcl_item_code` breaks an exact tie.

**Real example — CP0000013, the 10-supplier Kingfisher group (§4 of the Stage 4 architecture's own cited example):** all ten item_codes are standard-retail (no `-DF` suffix), so this canonical product has exactly one channel row, in `beer_master.csv`. Querying their real `effective_date`s: `2640900200` (2025-05-22) is the newest of the ten — `2020900300` (2019-04-03), `2580900200` (2018-05-23), `2710900200` (2017-05-15), `2720900200` (2020-05-09), `2730900200` (2019-04-27), `2770901600` (2020-05-14), `2780900100` (2012-06-26), `2790900100` (2016-04-06), `2850900400` (2012-01-20) are all older. `2640900200` is `beer_master.csv`'s representative for CP0000013, carrying its own price tuple (`mrp = 190.00`, `declared_price = 574.05` — these are different, real columns; not a typo) and its own `display_name`/`pack_size_ml`/etc. from Stage 3 — even though the other nine remain fully present, live, and priced in `item_code_canonical_map.csv` and (once a second month exists) `beer_price_history.csv`.

**Real example — CP0000832, a duty-free beer (`Buho Witbier-Can-DF-500ML X 24Btls.`, item_code `3510952013`, supplier 0351):** `classification_audit.csv` marks this item_code `is_duty_free = true`, so this canonical product's only channel row is in `beer_master_duty_free.csv`, never `beer_master.csv` — confirming the channel split is real, not hypothetical, in the current dataset (205 of 1,714 included beer item_codes are duty-free this run, close to master §1's ~10% baseline expectation).

**What happens when a channel has zero currently-`LIVE` item_codes (fully delisted in that channel):** the literal rule above has nothing to select from. §6.3 resolves this — the row is never recomputed from empty; it's frozen at its last-known representative/price values and only `status`/`delisted_run_month` change.

**A currently-`LIVE` item_code is only eligible to be a representative if it is present in this run's `normalized_rows.csv`.** `beer_master.csv`'s representative fields draw from three different upstream files (§3.1: `classification_confidence`/`classification_matched_on` from `classification_audit.csv`; `display_name`/`normalized_name_key`/`pack_size_ml`/`pack_count`/`container_type` from `normalized_rows.csv`), and `normalized_rows.csv`'s own frozen contract (Stage 3 architecture §2.1) restricts it to exactly Stage 2's `included = true` rows — a strictly narrower, sufficient condition than merely "has a `classification_audit.csv` row," since a `confidence_tier = low` row that Stage 2 excluded by default (master §6.2) gets a `classification_audit.csv` row but never a `normalized_rows.csv` one, and would otherwise pass a looser check while still lacking the Stage 3 fields the representative row needs. (An earlier version of this rule checked only for a `classification_audit.csv` row, which was too permissive — caught while implementing, before any code shipped against it.) Being `LIVE` (per Stage 4's `item_status`, based on `structured_rows.csv` presence — Stage 4 architecture §3.1, §6) and being *included as beer by Stage 2 this run* are two independent facts: it is entirely possible for an already-mapped item_code to remain genuinely `LIVE` while Stage 2 excludes it this run (`confidence_tier = none`, or `low` and excluded by default) or doesn't score it at all. Such an item_code is excluded from representative eligibility for this run only — it does not lose its mapping, its `LIVE` status, or its place in `beer_price_history.csv`'s diff (§5, which needs no classification or normalization data at all). If every `LIVE` item_code in a channel is ineligible this way, that channel's row is treated exactly as §6.3 describes for a fully-delisted channel — frozen, not recomputed from an unclassifiable source — even though, strictly, something in that channel is still `LIVE`. This has not yet been observed in the real, single-month dataset (every currently-mapped item_code was, by construction, eligible the run it was first mapped), but is a reachable, real state for any later run.

---

## 5. `beer_price_history.csv` — the item-code-level diff

**Grain: per `ksbcl_item_code`**, run over run, against the last row this item_code has in `beer_price_history.csv`. This departs from master §7.1's literal phrasing ("written... against `item_code_canonical_map.csv`'s prior state") — checked directly against the map's real, frozen schema (Stage 4 architecture §3.1; confirmed against the actual CSV header on disk), it carries no price fields at all, only identity/status fields. `beer_price_history.csv`'s own last row per item_code is the only place a prior price state actually exists to diff against; master's sentence is read here as describing the *relationship* (this diff happens using Stage 4's map to know which item_codes exist), not the literal comparison target.

### 5.1 Which item_codes participate

Every item_code present in this run's `structured_rows.csv` **and** already known to `item_code_canonical_map.csv` (i.e., every item_code Stage 4 has ever resolved, whether newly created this run or already mapped from a prior run). An item_code absent from this run's `structured_rows.csv` entirely contributes no history event this run (§6.3 handles its master/status implications separately) — there is no price to diff, since KSBCL published nothing for it.

### 5.2 The diff, per item_code (master §7.2, unchanged, hardened for the field-level detail of "price tuple")

- **No prior `beer_price_history.csv` row exists for this item_code** → first sighting.
  - First-ever pipeline run overall (no `beer_price_history.csv` exists at all yet) → `event_type = INITIAL_BACKFILL`.
  - Any later run → `event_type = NEW_ITEM`.
  - `previous_*` fields: `null` in both cases.
- **A prior row exists, and this run's (`declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp`, `effective_date`) tuple is identical to that prior row's** → unchanged. No history row written.
- **A prior row exists, and something in that five-field tuple differs:**
  - This run's `effective_date` is **later** than the prior row's → `event_type = PRICE_CHANGE`.
  - This run's `effective_date` **equals** the prior row's, but at least one of the four price fields differs → `event_type = CORRECTION`.
  - This run's `effective_date` is **earlier** than the prior row's → `event_type = CORRECTION` regardless of whether any price field also differs (master §7.2: the backdating itself is the anomaly worth recording).
  - In every one of these three cases, `previous_*` is populated from the prior row's own tuple, and a new row is appended — never an update to the prior row, which stays exactly as it was written.

**"Price tuple identical" means all four price fields, not just `mrp`.** Master §4.6's synthesis note calls out `mrp` as "the one confirmed-comparable, per-unit figure" for context on why it's singled out in that note's own discussion, but §7.2's actual diff rule (and §4.6's own field list, "the full price tuple at this event") is unambiguous that unchanged/changed is evaluated across all four price columns together — a change in `landed_cost` alone, with `mrp` and `effective_date` both unchanged, is still a real `CORRECTION` event, not silently absorbed into "unchanged."

### 5.3 Idempotency (master §9's History checks)

**"The last row this item_code has in `beer_price_history.csv`" (§5) means the single most recent row, full stop — never excluding rows written by an earlier attempt at this same `run_month`.** This is the entire mechanism, and it is sufficient on its own: because `beer_price_history.csv` is append-only with no in-place update (§3.2), a rerun's diff naturally compares this run's current tuple against whatever was *already* written the first time this `run_month` ran — including a real event from that first attempt. If nothing has changed since, the comparison correctly concludes "unchanged" and appends nothing. Master §9's exact bar — "re-running the same month's PDF produces zero duplicate history rows" — is satisfied by this alone, with no special-casing of `run_month` needed anywhere in this stage. See §8 for why this is a materially different (and simpler) situation than Stage 4's own rerun fix, which this document's first draft incorrectly copied.

### 5.4 Bootstrap (first-ever run)

Every item_code in `item_code_canonical_map.csv` this run gets exactly one `INITIAL_BACKFILL` row, using its current `structured_rows.csv` tuple. An `effective_date` reading `2012` or `2006` on an `INITIAL_BACKFILL` row is expected (master §7.4) — it means KSBCL's own data is that old, not that ValueBrew has tracked it that long.

---

## 6. `beer_master.csv` / `beer_master_duty_free.csv` — the canonical-level diff

**Grain: per (`canonical_product_id`, channel)**, run over run, against the prior run's own row in whichever of the two files already has one for this pair.

### 6.1 Determining channel

**Channel bucketing is driven by each currently-`LIVE` item_code's own current `is_duty_free` value, every run — never frozen from a prior run's classification.** This is what master §6.5 literally says ("`is_duty_free`... determines which... output file a row's canonical product feeds"), and the first draft of this section got it wrong by proposing the opposite (reading channel from Stage 5's own prior output file, treating it as permanent once assigned). That was an unscoped, undisclosed override of §6.5's literal words, caught by adversarial review — nothing in master supports treating channel as frozen the way `canonical_product_id` itself is frozen (§4.4), and a real, if currently unobserved, scenario shows why it can't be: if a `ksbcl_item_code`'s name gains or loses a `-DF` suffix in a republish (master §1 already documents item-code data being messier than it looks), `is_duty_free` for that specific item_code changes, and its contribution to channel bucketing must change with it.

Concretely, per (`canonical_product_id`, channel) pair, each run:

- **A canonical product has at least one currently-`LIVE` item_code whose current `is_duty_free` matches this channel** → this channel's row is live this run; proceed to §6.2. (A canonical product with live item_codes on both sides of `is_duty_free` gets a live row in both files — master §4.5's "can in principle appear in both" case — each computed independently.)
- **A canonical product has zero currently-`LIVE` item_codes matching this channel, but this channel already has a row from a prior run** → §6.3 applies. Critically, this frozen row is never touched or re-bucketed regardless of what any item_code's `is_duty_free` says this run — there is nothing to recompute for a row that isn't being written to, so no channel lookup happens for it at all. The frozen row simply stays in whatever file it already lives in.
- **A canonical product has zero currently-`LIVE` item_codes matching this channel, and no prior row exists there either** → no row exists in this file for this canonical product; nothing to do.

### 6.2 The diff itself

For each (`canonical_product_id`, channel) pair with at least one currently-`LIVE` item_code in that channel (per `item_code_canonical_map.csv`'s `item_status`, §6 of the Stage 4 architecture):

- Recompute `representative_item_code` per §4.
- Pull that item_code's current `structured_rows.csv`/`normalized_rows.csv`/`classification_audit.csv` fields and write them into the row's price/name/pack/classification fields, **unconditionally overwriting whatever was there before** — master §7.2's own stated reasoning applies unchanged: "each monthly PDF is KSBCL's assertion of current truth; classification governs how the *transition* is logged in `beer_price_history.csv`, never which value wins in master."
- Set `status = LIVE`. Clear `delisted_run_month` if it was previously set (§6.4).
- `last_updated_run_month = this run_month`, always — whether or not any field's value actually changed from last run.
- `first_seen_run_month`: set only when this row is being created for the first time; otherwise carried forward unchanged from the prior row.

### 6.3 Delisting

For each (`canonical_product_id`, channel) pair with an existing row in a prior run's output, but **zero** currently-`LIVE` item_codes in that channel this run:

- The row is **not deleted** (master §7.2, same reasoning as the item-code level: deleting it would make a future reappearance indistinguishable from a genuinely new canonical product).
- `status = DELISTED`. `delisted_run_month = this run_month`, but only if it wasn't already set from an earlier run (a canonical product that's been `DELISTED` for several consecutive runs keeps the run_month it *first* went dark, not the most recent run that merely re-confirmed it's still gone).
- Every other field (`representative_item_code`, price/name/pack fields, `classification_confidence`, etc.) is **frozen exactly as it was in the prior run's row** — this is the resolution to §4's "zero live item_codes, nothing to select a representative from" gap: there is nothing to recompute, so nothing is recomputed. The row shows the last real values KSBCL ever published for this product, not blanks and not stale-but-silently-relabeled-as-current values.

  **Decided (product owner, 2026-08-07):** this freeze behavior — never blanking the price/name fields, gating staleness entirely through `status`/`delisted_run_month` — is confirmed as `beer_master.csv`'s actual behavior, not left as an open question. Rationale: consistent with this project's standing posture of never deleting or erasing a real fact (Repository Governance conventions 6 and 7); any feature reading this file is expected to check `status` before treating the price fields as current, the same discipline already required of `item_code_canonical_map.csv`'s own `LIVE`/`DELISTED` item-level status.
- `last_updated_run_month = this run_month` still updates, recording that this run *checked* and confirmed the delisted state, distinct from `delisted_run_month`, which records when it *became* delisted.

### 6.4 Reappearance

If a channel that was `DELISTED` gains a `LIVE` item_code again in a later run, §6.2 applies exactly as if nothing special happened — `status` flips back to `LIVE`, `delisted_run_month` is cleared to `null`, and `representative_item_code`/price fields recompute fresh from whatever is live now. No separate "reactivation" event type exists, mirroring master §7.2's identical treatment of item-code-level reappearance.

---

## 7. Relationship between the two diffs

The two diffs (§5, §6) share the same underlying classification logic (`INITIAL_BACKFILL`/`NEW_ITEM`/`PRICE_CHANGE`/`CORRECTION` reasoning) but run at different keys and write to different files, exactly as master §7.1 specifies — they are not the same computation applied twice. A single `structured_rows.csv` row feeds both: unconditionally into §5's per-item_code history diff, and — only when that item_code happens to be its (`canonical_product_id`, channel) pair's current representative — into §6's master row. An item_code can have a real `PRICE_CHANGE` event written to `beer_price_history.csv` in a run where it is *not* the representative (e.g., it's one of the Kingfisher group's nine non-representative item_codes) — its price history is still fully and independently tracked, even though `beer_master.csv` shows a different item_code's values for that canonical product that run.

---

## 8. Determinism guarantees

Like Stage 4, Stage 5 has persistent, cross-run state by design — its determinism claim is conditioned on that state.

**Given a fixed prior state** (the last-known-per-item_code slice of `beer_price_history.csv`, and the prior `beer_master.csv`/`beer_master_duty_free.csv`) **and a fixed row-processing order for this run's `structured_rows.csv`**, both diffs are fully determined — the same input state and the same row set always produce the same output.

**Why Stage 5's rerun-safety mechanism is not the same as Stage 4's, and must not be copied from it.** This document's first draft copied Stage 4's `first_seen_run_month != run_month` exclusion pattern into §5 unmodified. That was wrong, caught by adversarial review, and worth recording exactly why, since the two stages' persistent state is structurally different in a way that matters:

- `item_code_canonical_map.csv` (Stage 4) is a **current-state table**, one row per item_code, updated in place. A rerun that didn't exclude this run_month's own prior effects would see every item_code as "already mapped" and silently skip re-deriving them — which is why Stage 4 needs to *deliberately forget* this run_month's own entries before recomputing, to force the same recomputation (and the same review rows) to happen again.
- `beer_price_history.csv` (Stage 5) is **append-only, no per-key uniqueness, never updated in place** (§3.2). Applying the same "forget this run_month's own rows" trick here doesn't force safe recomputation — it forces the diff to compare against a *stale, pre-this-month* baseline while this run's actual input data already reflects the change, concluding "changed" a second time and appending a duplicate event. Traced concretely: a real `PRICE_CHANGE` in month M gets recorded once correctly; excluding it on a rerun of M makes the diff compare M's data against month M−1 again, conclude `PRICE_CHANGE` again, and append a second, duplicate history row for the same event — the exact violation of master §9's idempotency bar this section exists to prevent.

The correct mechanism needs no exclusion at all — see §5.3. An append-only ledger's own last row already *is* "what happened last time," including a first attempt at this exact `run_month`; comparing against it, unconditionally, is what makes a rerun idempotent. Stage 4 needed an exclusion specifically because its state is mutable and would otherwise look "already settled" on a rerun; Stage 5's state is never mutable, so it never looks that way to begin with.

---

## 9. Auditability

`beer_price_history.csv` is itself the audit trail for every price fact ever published — combined with `item_code_canonical_map.csv`'s `first_seen_run_month`/`last_seen_run_month` and `beer_master.csv`'s own `first_seen_run_month`/`last_updated_run_month`, the full lifecycle of any canonical product (when it first appeared, every price it ever held, when and whether it went dark) is reconstructable without re-reading any source PDF — the same reconstructability bar every earlier stage's audit artifact meets. The `archive/beer_master_<run_month>.csv` snapshots (§2.2) additionally let a specific month's exact published master state be recovered even after later runs have overwritten the live file.

---

## 10. Failure modes

**Row-level:** none beyond what §6.3 already treats as an ordinary outcome — a channel with zero live item_codes is a legitimate, non-error state, not a failure requiring an abort or a flag.

**Structural failures, hard-abort the run (mirroring Stages 1–4's own posture):**
- **Join integrity** — a `ksbcl_item_code` present in `item_code_canonical_map.csv` and marked `item_status = LIVE`, but entirely absent from this run's `structured_rows.csv`. This is the one join Stage 5 requires to hold: Stage 4's own `item_status` rule (Stage 4 architecture §3.1, per the fix recorded there) defines `LIVE` *as* "present in `structured_rows.csv`," so this combination should be structurally impossible given `item_code_canonical_map.csv` is this run's own freshly-updated output — checked anyway. **Absence from `classification_audit.csv` specifically is never a failure** — §2.1 and §4 establish that as a normal, expected condition, not a structural break; an earlier draft of this section incorrectly listed it as one, caught by adversarial review.
- **Zero rows in `item_code_canonical_map.csv`** — Stage 5 cannot run against a pipeline that has never resolved a single item_code; aborts, mirroring Stage 4's own zero-rows check one stage further upstream.
- **A duplicate (`canonical_product_id`, channel) row appearing in a single run's own output** — the extraction-bug-shaped failure this document's own construction should make structurally impossible (§6 processes each pair at most once per run), checked anyway per the same defensive posture every earlier stage applies to its own equivalent invariant.
- **A corrupted or unreadable prior `beer_price_history.csv`, `beer_master.csv`, or `beer_master_duty_free.csv`** — mirroring Stage 4's identical check on `item_code_canonical_map.csv` (Stage 4 architecture §10). This is arguably higher-stakes here than at Stage 4: silently treating a corrupted Stage 5 prior state as an empty bootstrap would mark every already-tracked item_code `INITIAL_BACKFILL`/`NEW_ITEM` a second time, permanently corrupting an append-only ledger that (unlike a current-state map) can never be rebuilt clean from `beer_price_history.csv` alone. Aborts rather than guessing.

**No mid-run checkpointing, idempotent all-or-nothing output** — mirrors master §8.4/§8.5 and every earlier stage: a failed run produces no partial update to `beer_price_history.csv`, `beer_master.csv`, or `beer_master_duty_free.csv`, and never overwrites the previous good state in place.

---

## 11. Relationship to Stage 4 and future work

**Stage 4** hands off exactly what its own architecture already commits to: `canonical_product_id`, `item_status`, `supplier_code` per `ksbcl_item_code`. Stage 5 does not ask Stage 4 to change anything about its frozen contract, and does not re-derive or second-guess any identity resolution Stage 4 has already made — including item_codes still sitting in `canonical_resolution_review.csv` awaiting manual review, which Stage 5 treats identically to any other resolved item_code (their `match_confidence` is informational metadata about *how* they were resolved, never a filter on *whether* Stage 5 includes them).

**Future enrichment and the catalog-build step** (master §10) read `beer_master.csv` as their spine once they exist — genuinely out of scope here, named only because it's the reason `canonical_product_id` (not `ksbcl_item_code`) is this document's every join key, exactly as master §10.1 directs.

---

## 12. Architecture Questions Deferred to Freeze Review

1. **Validation abort thresholds for Stage 5 specifically** (row-count deviation, an implausible fraction of canonical products delisting in one run) — master §12.4 leaves this open pipeline-wide pending real run history; Stage 5 inherits that same open status rather than inventing its own number here.
2. **Whether a canonical product that has been `DELISTED` in a channel for many consecutive runs should ever be pruned from `beer_master.csv`'s *default* view** (as opposed to the underlying file, which per §6.3 never deletes anything) — a display/UI question for whatever eventually reads `beer_master.csv`, not something this document resolves.
3. **This document's real-data validation gap, disclosed in §0**: the `PRICE_CHANGE`/`CORRECTION`/`DELISTED` branches have not yet been exercised against two genuinely different monthly snapshots, only reasoned about against master's literal rule plus a conceptual same-month rerun. Freeze review should treat this as open until a second real month's PDF is processed, per master §11's own build-order note.
4. ~~§6.3's "freeze at last-known values" for a fully-delisted channel~~ — **resolved.** Flagged by adversarial review as a genuine judgment call not derivable from master's text (master §7.2 only ever needed to preserve a bare `status`/`delisted_run_month` at the item-code level, since `item_code_canonical_map.csv` carries no price fields to freeze in the first place). Escalated to the product owner and confirmed — see the recorded decision in §6.3.
