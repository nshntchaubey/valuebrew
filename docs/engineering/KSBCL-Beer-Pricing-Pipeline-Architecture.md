# ValueBrew — KSBCL Beer Pricing Pipeline Architecture (Phase 1)

### A design document, not an implementation. Produced by inspecting the actual KSBCL "Supplier-wise Item-wise Price List" PDF directly (via `pdfplumber`, not assumed), then fanning out nine focused design passes across its stages and stress-testing the result. Nothing below has been coded. Per the governing brief: *"Only after the architecture is approved should implementation begin."*

**Status: three blocking decisions (§12.1–12.3) have been made by the product owner and are incorporated below** — Python as the implementation language, Duty-Free rows excluded from the retail catalogue but preserved in a side dataset, and KSBCL Item Code demoted from "SKU identity" to "source-system identifier," with a new internally-generated **Canonical Product ID** taking its place as what `beer_master.csv` is actually keyed on. This last decision is a real architectural shift from the original nine-agent design pass (which had defaulted to Item Code as SKU identity) and is threaded through every section below, not bolted on as a footnote. The product owner also directed that this pipeline be treated as **ValueBrew's durable, canonical data platform, independent of the mobile app** — not a Phase-1-only throwaway — which is why the extensibility seams in §10 are written as load-bearing, not speculative.

---

## 0. Why this document looks the way it does

The original brief assumed the source PDF was ~750 pages / ~33,000 rows with a `Category` dimension somewhere in it. Before designing anything, the actual file was inspected directly:

- **750 pages, 33,867 product rows — confirmed.** (A separate file-size estimate the tooling initially reported, "152 pages," was wrong; `pdfplumber` opening the real file reports 750, matching the brief. Noted here only because it's the kind of silent discrepancy this whole document exists to not repeat.)
- **There is no category column.** None. Beer, wine, rum, whisky, vodka, brandy, gin, and RTDs are interleaved in one table, distinguished only by free-text product names.

That single fact reshapes almost everything downstream — beer identification has to be a text-classification problem, not a filter. Everything in this document is grounded in rows actually pulled from the real file (page numbers, item codes, and prices quoted below are real, not illustrative), plus a full 750-page scan for every row matching `\bbeer\b` (1,389 of 33,867 rows — a confirmed *undercount*, see §6).

---

## 1. Ground truth: the source PDF, as it actually is

**Columns** (table header repeats on every page): `SR NO | ITEM NAME | ITEM CODE | EFFECTIVE DATE | DECLARED PRICE | LANDED COST | KSBCL SELLING PRICE | MRP`.

**Three row shapes share one extracted table, and must be told apart before anything else happens:**
1. **Product rows** — the real data.
2. **Supplier section-header rows** — `Supplier : <Full Legal Name> (<4-digit code>)`, e.g. `Supplier : B9 Beverages Pvt Ltd Sub-Lessee of Regent Beers and Wines Ltd (0260)`. 675 of these exist in the file. Every row after one, until the next, belongs to that supplier. This context **carries across page breaks** — the header row repeats per page, but supplier sections do not restart.
3. **Filler/marker rows** — e.g. `1 | - | - | - | (values in Rs.)`. Discard.

**Item Code** is numeric (8–11 digits), unique per row *within one monthly snapshot* (verified: 0 duplicates among 1,389 sampled beer rows). Its leading digits track the **supplier's ordinal position in the file** (supplier #1 → codes starting `1…`, supplier #2 → `2…`, confirmed by cross-referencing supplier section boundaries) — **not** product category. This is an easy, wrong shortcut to reach for; it's flagged here so nobody has to rediscover it by producing a silently wrong classifier.

**A systematic PDF extraction artifact** affects ~70% of sampled price cells: `pdfplumber` tokenizes some numeric values into two adjacent strings with a spurious internal space — the true value `140.00` extracts as `"1 40.00"`. Confirmed on 970 of 1,389 sampled beer rows, on the MRP column specifically; there is no structural reason it wouldn't affect the other three price columns identically (same font-kerning cause), so all four must be defended identically. This is a rendering artifact of the source file, not real data, and not the same thing as Indian comma-grouping (`"6,199.00"`), which is separately real formatting to parse correctly.

**A non-obvious, empirically-verified pricing fact:** `MRP` is always the printed **per-single-unit** retail price. `Landed Cost` and `KSBCL Selling Price` are **case-level totals** whenever a SKU is sold as a case — **whether or not the case count is stated in the item name.** Example: `Original Bira 91 White Beer 650ML(0260)` states no case count at all, yet `KSBCL Selling Price = 2,181.80` and `MRP = 200.00` — these only reconcile against an *assumed* implicit case size of 12 (2,181.80 / 12 ≈ 181.8, a plausible ~10% margin below MRP). 482 of 1,389 beer rows have no case-multiplier text at all. **Nothing in the source states the case size for these rows** — treating the four price columns as directly comparable, or guessing a case size to normalize them, would both be inventing a fact the data doesn't contain. See §5.4 and §12.

**Effective Date** spans **2006–2026 within a single snapshot** — most SKUs haven't had a price change in years. Each Item Code appears exactly once per monthly file, holding whatever price is currently live. **The PDF is a point-in-time snapshot, not a ledger** — real history can only be built by diffing this month's snapshot against the pipeline's own previously stored state. The pipeline is inherently stateful/incremental across monthly runs, never a one-shot transform.

**~10% of beer rows (138 of 1,389) carry a `-DF` suffix** — Duty Free / bonded-warehouse retail, a different channel and pricing basis than standard Karnataka retail, mixed into the same file. Whether these belong in "the Karnataka beer catalogue" is a product question (§12), not a data one.

**Genuine duplicate-Item-Code cases exist for identical products.** On page 186 alone (supplier `Anheuser Busch Inbev India Ltd (0217)`), `Haywards 5000 Premium Strong Beer 650ML×12Btls` appears under **both** item codes `2170902700` and `2170903000`, with identical name, price, and effective date. The same pattern repeats for two other products on the same page. Separately, `Budweiser Magnum Beer-CAN 330ML×24Cans` appears under item code `2170900611` (eff. 25-Aug-25) *and* `2171700211` (eff. 12-May-26, different price) — this looks like a re-issuance, not a true duplicate, but nothing in the source states that relationship explicitly. See §5.5 and §12.

**Environment note:** `pdftoppm`/`pdftotext` (poppler) are not installed in the dev environment; `pdfplumber` (pure Python, pip-installable) was installed and used, via `extract_tables()` — never `extract_text()`, which was confirmed to jumble column boundaries far worse.

---

## 2. Overall pipeline architecture

```
Raw PDF (monthly release)
        │
        ▼
┌─────────────────────┐
│ Stage 1: Extraction  │  pdfplumber extract_tables(), page-by-page, sequential.
│                      │  Tracks current-supplier context across pages. Classifies
│                      │  every row as header / supplier-header / filler / product.
│                      │  Strips the whitespace-tokenization artifact from every
│                      │  numeric cell. Validates each product row; failures are
│                      │  logged and dropped, never silently kept or crash the run.
└─────────┬────────────┘
          │ structured_rows  (ALL categories — 33,867 rows/month, not beer-filtered yet)
          ▼
┌─────────────────────┐
│ Stage 2: Beer        │  Layered text match against item_name: style/keyword
│ Identification       │  allowlist (primary) → brand allowlist (secondary) →
│                      │  spirit-term exclusion guard. Every row gets a
│                      │  confidence tier (high/medium/low/none) and a reason,
│                      │  never a bare boolean.
└─────────┬────────────┘
          │ classified beer candidates (~1,389+/month, confidence-tagged)
          ▼
┌─────────────────────┐
│ Stage 3:             │  Formatting-only cleanup: unicode/symbol/whitespace
│ Normalization        │  unification for a comparison key; structured extraction
│                      │  of pack_size_ml / pack_count / container_type; numeric
│                      │  and date cleanup. Raw values always preserved alongside.
└─────────┬────────────┘
          │ normalized + structured rows
          ▼
┌─────────────────────┐
│ Stage 4: Canonical    │  Item Code is a SOURCE-SYSTEM identifier only — never
│ Identity Resolution   │  the SKU identity (decided, §12.3). Every item_code is
│                      │  mapped to a stable, internally-generated
│                      │  canonical_product_id via item_code_canonical_map.csv.
│                      │  Auto-merge into an existing canonical product ONLY on
│                      │  a full deterministic match (name+pack+price+date all
│                      │  identical); a partial match (e.g. same name/pack,
│                      │  different price/date — item-code succession) gets a
│                      │  NEW canonical id plus a flagged suggestion for manual
│                      │  review, never an automatic merge.
└─────────┬────────────┘
          │ resolved rows + item_code_canonical_map.csv
          ▼
┌─────────────────────┐
│ Stage 5: Master +     │  Diffs this run's resolved rows (rolled up to
│ History               │  canonical_product_id) against last run's
│                      │  beer_master.csv. Classifies every change (NEW_ITEM /
│                      │  PRICE_CHANGE / CORRECTION / DELISTED / unchanged).
│                      │  beer_price_history.csv stays keyed by ksbcl_item_code
│                      │  (provenance/audit, per decision §12.3) — never by
│                      │  canonical_product_id.
└─────────┬────────────┘
          │
          ▼
   beer_master.csv (canonical, standard-retail channel)
   beer_master_duty_free.csv (canonical, duty-free channel — decided §12.2)
   beer_price_history.csv (item-code-level, both channels)     ◄── Phase 1 deliverables
          │
          ▼
   (out of Phase 1 scope, named only to shape today's schema)
   Future: enrichment sources join on canonical_product_id, not ksbcl_item_code
   (§10.2) → catalog-build step → catalog.json
```

Every stage produces an audit artifact, not just its "clean" output — this is deliberate. A pipeline that runs unattended forever needs every decision to be reconstructable without re-reading the source PDF.

---

## 3. Folder structure

```
tool/ksbcl_pricing_pipeline/          # pipeline code + config (naming matches the
  config/                             # repo's existing tool/ convention for
    beer_classification.yaml          # maintenance scripts, e.g. tool/generate_brand_assets.dart)
    supplier_aliases.yaml             # confirmed supplier-name aliases; starts empty
    normalization_spec.md             # versioned, documented normalization rules
  extract.py                          # Stage 1
  classify.py                         # Stage 2
  normalize.py                        # Stage 3
  resolve_canonical.py                # Stage 4 — canonical identity resolution
  history.py                          # Stage 5
  validate.py                         # cross-cutting checks, run at every stage boundary
  run_pipeline.py                     # orchestrator / monthly entrypoint

pricing_data/                         # repo root, sibling to catalog/ — deliberately
  raw_pdfs/YYYY-MM/                   # NOT inside catalog/: this is raw pipeline
    <source>.pdf                      # output/audit trail, not the app's published
  runs/YYYY-MM/                       # catalog. A future catalog-build step reads
    structured_rows.csv               # from here to help produce catalog.json —
    classification_audit.csv          # it does not live here itself.
    canonical_resolution_review.csv   # this run's flagged possible-supersession
                                       # candidates awaiting manual review
    rejected_rows.csv
    run_summary.json
    pipeline.log
  item_code_canonical_map.csv         # append-mostly; every ksbcl_item_code ever
                                       # seen, mapped to a canonical_product_id
  beer_master.csv                     # canonical products, standard-retail channel,
                                       # current live snapshot, overwritten each run
  beer_master_duty_free.csv           # canonical products, duty-free channel —
                                       # same canonical_product_id space, kept
                                       # structurally separate from retail (§12.2)
  beer_price_history.csv              # append-only, keyed by ksbcl_item_code
                                       # (both channels), accumulates forever
  archive/
    beer_master_YYYY-MM.csv           # dated snapshots, for rollback/diff without
                                       # depending on git history of a CSV
```

`catalog/catalog.json` (existing) and `pricing_data/` are kept structurally separate on purpose: `catalog.json` is the app's published, bundled artifact; `pricing_data/` is this pipeline's own working state. A future catalog-build step is the only thing that reads from `pricing_data/` to help produce a new `catalog.json` — the app itself never reads `pricing_data/` directly.

**Decided (§12.1):** Python, kept fully outside the Flutter app's dependency graph — `pdfplumber` is already verified against this exact file; Dart's PDF-table-extraction ecosystem is materially weaker, and this pipeline's outputs are language-agnostic CSVs the app never imports code from.

---

## 4. CSV / data schemas

### 4.1 Stage 1 output — `structured_rows` (per-run audit artifact, all categories)

| Field | Notes |
|---|---|
| `item_code` | validated numeric, 8–11 digits |
| `item_name_raw` | untouched, byte-for-byte |
| `supplier_name`, `supplier_code` | from the active supplier-header context, never re-derived from the item name string |
| `effective_date_raw`, `effective_date` | `DD-Mon-YY` string, plus parsed ISO date |
| `declared_price_raw` / `declared_price`, `landed_cost_raw` / `landed_cost`, `ksbcl_selling_price_raw` / `ksbcl_selling_price`, `mrp_raw` / `mrp` | raw string + whitespace-stripped parsed decimal, for all four columns identically |
| `source_page` | for traceability back to the PDF |
| `run_month` | this run's period key |

### 4.2 Stage 2 output — `classification_audit`

| Field | Notes |
|---|---|
| `item_code` | |
| `classification` | `beer` \| `not_beer` \| `needs_review` |
| `confidence_tier` | `high` (style-keyword match) \| `medium` (brand-only match) \| `low` (borderline/exclusion conflict) \| `none` |
| `matched_on` | `style_keyword:<term>` \| `brand_name:<term>` \| none |
| `is_duty_free` | bool, from `-DF` suffix detection |
| `supplier_known_beer_seller` | bool, corroborating-only signal, never a gate |

### 4.3 Stage 3 additions — normalization

| Field | Notes |
|---|---|
| `display_name` | `item_name_raw` with only the trailing `(NNNN)` supplier suffix stripped and whitespace collapsed — human-readable, source casing preserved |
| `normalized_name_key` | fully case-folded, symbol-unified — comparison key only, never displayed |
| `pack_size_ml` | parsed numeric |
| `pack_count` | **nullable** — absence is preserved, never defaulted |
| `container_type` | controlled vocabulary: `bottle` \| `can` \| `pet_bottle` \| `tetra_pack` \| `unknown` |
| `suffix_malformed` | bool — true when the trailing `(NNNN)` suffix was missing its opening paren in source |

### 4.4 Stage 4 output — Canonical Identity Resolution *(revised per decision §12.3 — Item Code is a source-system identifier, not SKU identity)*

Two artifacts, not one:

**`item_code_canonical_map.csv`** — append-mostly, the permanent record of every KSBCL Item Code ever seen and what canonical product it belongs to. Never deletes or renumbers an Item Code; only ever adds rows or, on an explicit human-confirmed merge, updates a mapping's `canonical_product_id` (itself a fully audited action, never silent).

| Field | Notes |
|---|---|
| `ksbcl_item_code` | preserved exactly, **never modified** — the authoritative source-system key |
| `canonical_product_id` | stable, internally-generated ID — the real SKU identity the app and `beer_master.csv` are keyed on |
| `supplier_name`, `supplier_code` | |
| `match_confidence` | `deterministic_high` (auto-merged on an exact key match, §4.4 below) \| `manual_confirmed` (a human reviewed a flagged suggestion and confirmed the link) \| `unreviewed` (brand-new canonical product, nothing to confirm yet) |
| `matched_rule` | `exact_key_match` \| `manual_review` \| `new_canonical` |
| `item_status` | `LIVE` \| `DELISTED` — at the *item-code* level, independent of the canonical product's own `status` (a canonical product can stay `LIVE` via one item code while another mapped to it goes `DELISTED`) |
| `first_seen_run_month`, `last_seen_run_month` | |

**Matching key** (used both to test for an auto-merge and to group candidates for review): `(normalized_name_key, pack_size_ml, pack_count, container_type, supplier_code)`.

**Resolution logic per item_code, each run:**
- Already mapped (seen in a prior run) → no action beyond updating `last_seen_run_month`/`item_status`.
- Not yet mapped, and an *existing* canonical product has a mapped item_code whose matching key **and current price and effective_date all match exactly** → auto-map to that `canonical_product_id`, `match_confidence = deterministic_high`. This is the "very high confidence" bar the product owner set for automatic merging — it's the Haywards 5000 / Knock Out / Royal Challenge pattern from page 186, where two item codes carry byte-identical name, price, and date.
- Not yet mapped, and an existing canonical product has a mapped item_code with a matching key but a **differing price or effective_date** (the Budweiser Magnum pattern — looks like the same product re-issued under a new code) → a **new** `canonical_product_id` is created for this item_code (never silently merged), and a suggestion row is written to `canonical_resolution_review.csv` (`item_code`, `suggested_canonical_product_id`, `reason: possible_supersession`) for manual review. If a human later confirms it's the same product, `item_code_canonical_map.csv` is updated to repoint this item_code at the existing canonical product — a deliberate, audited, one-directional merge action, never automatic.
- No match at all → brand-new canonical product.

This is the mechanism that resolves the tension the original nine-agent design flagged as unresolved (§12.3, §12.4 below) — Item Code stays permanent and untouched in the map and in `beer_price_history.csv`; `canonical_product_id` is what "SKU identity" and "no duplicate live SKUs" actually mean for `beer_master.csv`.

### 4.5 `beer_master.csv` / `beer_master_duty_free.csv` — the Phase 1 deliverable, one row per **live canonical product**

Same schema, two files — split by channel per decision §12.2. A canonical product can in principle appear in both (if the same real-world beer has both a standard-retail and a duty-free item code mapped to it), each file showing that channel's own current price.

| Field | Notes |
|---|---|
| `canonical_product_id` | the SKU identity (§4.4) — **unique per row by construction**, satisfying "no duplicate live SKUs" literally, not by convention |
| `representative_item_code` | which mapped `ksbcl_item_code` currently supplies the price fields below (the newest-`effective_date` one among this canonical product's live, same-channel mapped item codes; lowest item code breaks a tie) — a display/aggregation convenience, never a claim that the other mapped item codes stop existing (they remain in `item_code_canonical_map.csv` and `beer_price_history.csv`) |
| `item_name_raw`, `display_name`, `normalized_name_key` | from the representative item code, §4.3 |
| `pack_size_ml`, `pack_count`, `container_type` | §4.3 |
| `declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp` | current values from the representative item code, **at native/unconverted granularity** — no invented per-unit conversion (§5.4) |
| `effective_date` | current/live, government-declared |
| `status` | `LIVE` \| `DELISTED` — `LIVE` as long as at least one mapped item code in this channel is `LIVE` |
| `delisted_run_month` | nullable — set when the *last* live mapped item code in this channel delists |
| `classification_confidence`, `classification_matched_on` | §4.2, from the representative item code |
| `gtin`, `gtin_confidence` | **nullable, reserved placeholder**, keyed to `canonical_product_id` — Phase 1 populates neither; see §10.2 (revised to join on canonical product, not Item Code) |
| `source_pdf_reference` | |
| `first_seen_run_month`, `last_updated_run_month` | |

### 4.6 `beer_price_history.csv` — append-only, accumulates forever, **keyed by `ksbcl_item_code`** (decided §12.3: provenance/audit stays at the source-system level, never rolled up to canonical product)

| Field | Notes |
|---|---|
| `history_id` | surrogate key, stable even if future logic changes how "new" is decided |
| `ksbcl_item_code` | |
| `event_type` | `INITIAL_BACKFILL` \| `NEW_ITEM` \| `PRICE_CHANGE` \| `CORRECTION` (see §7 for exact classification rule) |
| `effective_date`, `effective_date_raw` | government-declared |
| `declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp` | the full price tuple at this event, all four columns |
| `previous_declared_price`, `previous_landed_cost`, `previous_ksbcl_selling_price`, `previous_mrp`, `previous_effective_date` | nullable, prior state at the time of this event |
| `observed_run_month`, `observed_at` | the pipeline's own clock — distinct from `effective_date` |
| `source_pdf_reference` | |

> **Synthesis note:** the historical-pricing design pass that produced §7's event-classification logic was briefed assuming a single scalar price field, and flagged that assumption explicitly ("no evidence of multiple price columns was surfaced"). The source data in fact has four price columns (§1). The schema above extends that stage's design to carry all four, with the classification rule (§7) keyed primarily on `effective_date` + `mrp` — MRP being the one confirmed-comparable, per-unit figure — while a change in *any* of the four at an unchanged `effective_date` still counts as a `CORRECTION`. Flagged here rather than silently patched.

**No separate history row is written on delisting** — `status`/`delisted_run_month` (at the item-code level in `item_code_canonical_map.csv`, and rolled up to the canonical level in `beer_master.csv`) carry that fact. `beer_price_history.csv`'s stated purpose is *prices ever seen*; delisting isn't a price event.

**A canonical-product-level "price over time" view — e.g. showing one continuous price line across an item-code succession the way §4.4's manual-confirm merges would imply — is a *derived, computed-on-read join* (`item_code_canonical_map.csv` ⋈ `beer_price_history.csv`), not a new stored Phase 1 file.** Storing it separately would duplicate a source of truth that already exists across two files; computing it on demand keeps `beer_price_history.csv` a pure, append-only record of exactly what KSBCL published, per Item Code, forever.

---

## 5. Normalization rules

Formatting normalization only — **never** inventing, correcting, or completing what KSBCL actually published. Three concrete example variants from the brief (`"Kingfisher Premium Beer Bottle 650ml"` / `"Kingfisher Premium Bottle 650 ML"` / `"KINGFISHER PREM 650ML"`) illustrate the boundary precisely: the first two are a pure formatting problem (same words, different spacing/casing/unit format) and normalization converges them. The third drops words and abbreviates ("PREM" for "Premium") — that is **not** a formatting difference, and expanding "PREM" to "Premium" would be inventing text that isn't there. That's a separate, later fuzzy-matching/alias-table concern, not something this stage does implicitly (§12.7).

**5.1 Ordered rules producing `normalized_name_key`:** Unicode NFKC normalization → unify `×`/`x`/`X` multiplier symbols → collapse/trim whitespace → strip the redundant trailing `(NNNN)` supplier-code suffix (tolerant of the confirmed missing-paren malformation, via an optional-open-paren pattern) → unify volume-unit casing/spacing (`650ML`/`650 ML`/`180Ml` → one form) → case-fold. Nothing beyond this — no stemming, no word reordering, no filler-word removal, no abbreviation expansion.

**5.2 Three tiers, always kept, never lossy:** `item_name_raw` (immutable audit anchor) → `display_name` (suffix-stripped, whitespace-collapsed, source casing preserved — for UI/reports) → `normalized_name_key` (fully folded — matching only, never displayed). `normalized_name_key` is also the primary component of the Stage 4 canonical-identity matching key (§4.4) — computed once, here, by one documented function, not re-derived per consumer.

**5.3 Structured extraction (additive, never replacing raw text):** `pack_size_ml`, `pack_count` (nullable — many rows genuinely state none), `container_type` (controlled vocabulary; an unrecognized token becomes `unknown` + a review flag, never a best guess), `suffix_malformed` (audit flag for the missing-paren case). A name that doesn't match the expected pattern at all gets `extraction_incomplete: true` and nulls, never a guessed value.

**5.4 Price/date cleanup, applied to all four price columns identically:** strip *all* internal whitespace before anything else (defeats the tokenization artifact, §1) → parse Indian comma-grouping → store as fixed-point decimal (not binary float, to avoid currency drift) → keep `*_raw` alongside every parsed value. Dates: explicit `DD-Mon-YY` format parsing (not a locale-guessing parser), with an explicit, documented two-digit-year pivot rule (`00–99 → 20xx`, since no row predates 2000) rather than a library default nobody chose on purpose.

**5.5 Case-level vs. per-unit price — deliberately *not* resolved here.** All four price fields are kept at their native, printed granularity. No per-unit conversion is computed in this stage, and in particular **no case size is assumed for the 482 bare-volume rows** — doing so would fabricate a fact (case size) the source doesn't contain, for exactly the reason §1 flags it. If a per-unit figure is ever needed, it belongs in one explicit, named, reviewable later computation — never folded silently into "clean" data.

**What is never touched:** the actual brand/product vocabulary, any abbreviation, any pack-count that isn't stated, `item_name_raw` itself (never overwritten), and any row that fails to parse (flagged, never dropped or defaulted).

---

## 6. Beer identification heuristics

**The core problem:** no category column exists (§1), and a literal `\bbeer\b` match **undercounts** real beer SKUs — confirmed directly: `Hoegaarden Witbier 330ML×24Btls(0217)` is a real, confirmed beer SKU with no "beer" substring anywhere in its name. 108 distinct suppliers had at least one beer-keyword row in the sampled scan, and most of them are general liquor distributors (names containing "Distilleries"/"Spirits") carrying a handful of beer SKUs alongside whisky/rum/brandy — so **supplier identity can never be the primary filter**, only corroborating metadata.

**6.1 Layered classification, in order:**
1. **Style/keyword allowlist** (primary, high confidence): `beer`, `lager`, `strong beer`, `witbier`, `wheat beer`, `stout beer`, `ale`, `ipa`/`indian pale ale`, `pilsner`, `porter`. This is the layer that catches the Hoegaarden case.
2. **Brand allowlist** (secondary, medium confidence, fires only when style matching misses): Kingfisher, Royal Challenge, Haywards 5000, Knock Out, Budweiser, Hoegaarden, Simba, Tuborg, Carlsberg, Witlinger, Bira 91 ("Original Bira 91" included as the same brand family).
3. **Exclusion guard** (applied after 1+2 flag a candidate): spirit-family terms (`whisky`, `rum`, `brandy`, `vodka`, `gin`, etc.) that would veto a *brand-only* match, but never veto an unambiguous *style-keyword* match.
4. **Supplier corroboration** — annotation only (`supplier_known_beer_seller: bool`), never a gate.

**6.2 Confidence tiers drive action, never a bare include/exclude:** High (style match) → auto-include. Medium (brand-only match) → auto-include, flagged for monthly spot-check. Low (exclusion conflict, or match from an unfamiliar supplier) → **excluded by default**, flagged for human review. None → excluded, no per-row flag needed (this is the expected outcome for the ~32,000 non-beer rows). The exclude-by-default choice on Low-confidence rows follows directly from the brief's "never invent" principle: a false inclusion pollutes the catalogue with a wrong item; a false exclusion just delays a real one by one review cycle. The two are not symmetric risks.

**6.3 Maintainability:** the three lists (style keywords, brand names, exclusion terms) live in one external, versioned config file (`tool/ksbcl_pricing_pipeline/config/beer_classification.yaml`) — never hardcoded regex in a script. This is a **permanent** abstraction, justified because KSBCL is not expected to ever add a category column; it is not a stopgap for something a future milestone removes. Kept deliberately simple for Phase 1 — no fuzzy/edit-distance matching, no ML classifier; those would be premature against one month of verified data.

**6.4 Monthly self-check, since this must run unattended forever:** every run emits an aggregate sanity report (counts by confidence tier, count swings vs. last month), a **new-entity diff** (brands/styles seen for the first time, surfaced so a human can promote them into the allowlist rather than letting flagged rows silently pile up), and a supplier diff (new beer-carrying suppliers). This turns "run and trust" into "run and confirm."

**6.5 Duty-Free rows — decided (§12.2):** `is_duty_free` (from the `-DF` suffix) determines which of the two channel output files (§4.5) a row's canonical product feeds — `beer_master.csv` (standard retail) or `beer_master_duty_free.csv` (duty-free). Both channels flow through the *same* canonical-identity resolution (§4.4), so a beer sold in both channels resolves to one shared `canonical_product_id`, not two unrelated identities. Neither dataset is deleted or dropped; only the retail file is treated as ValueBrew's default-facing catalogue (recommendation engine, Price Verification, Value Score, retail comparisons all read `beer_master.csv` only).

---

## 7. Historical price strategy

**7.1 Core fact driving this design:** a single monthly snapshot has exactly one row per Item Code, holding whatever price is currently live — it is never itself a ledger (§1). Real history only exists by diffing this run's resolved rows against previously stored state. The pipeline is stateful across runs by necessity, not by choice.

**Two diffs happen, at two different grains, per decision §12.3:** `beer_price_history.csv` is written per `ksbcl_item_code` against `item_code_canonical_map.csv`'s prior state (the diff described in §7.2 below, unchanged from the original design). Separately, `beer_master.csv`/`beer_master_duty_free.csv` are written per `canonical_product_id`, using each canonical product's `representative_item_code` (§4.5) as the value source for that comparison. The two diffs share the same event-classification logic; they simply run at different keys.

**7.2 The diff, per Item Code, run over run:**
- **Not in prior master** → brand new. First-ever pipeline run → `INITIAL_BACKFILL`. Any later run → `NEW_ITEM`. Master row created, `status = LIVE`.
- **In both, `effective_date` and price tuple identical** → unchanged. No history row.
- **In both, something differs:**
  - Later `effective_date` → `PRICE_CHANGE` (the ordinary case — a real forward-moving price move).
  - Same `effective_date`, price tuple differs → `CORRECTION` (KSBCL re-published a fix for the same declared date).
  - **Earlier** `effective_date` than what's on record → `CORRECTION` (a retroactive/backdated republish — itself the anomaly worth recording, regardless of whether price also changed).
  - In all three sub-cases, `beer_master.csv` is unconditionally overwritten to mirror this run's values — each monthly PDF is KSBCL's assertion of current truth; classification governs how the *transition* is logged in history, never which value wins in master. This avoids a whole class of special-casing.
- **In prior master, absent from this run** → `status = DELISTED`, `delisted_run_month` set. **Row is never deleted** — deleting it would make a future reappearance indistinguishable from a genuinely new Item Code. No history row (§4.6). Reappearance later simply re-enters the normal diff against the still-present master row and flips `status` back to `LIVE`, for free.

**7.3 Price can legitimately *drop*, not just rise** — nothing in this design assumes monotonic price increase, and nothing should (§9 flags this as a specific validation trap to avoid).

**7.4 First-ever run:** every row becomes `INITIAL_BACKFILL`, deliberately distinct from `NEW_ITEM` so a reader never has to infer "was this really the SKU's first price, or just the first the pipeline happened to see" from date arithmetic — a row whose `effective_date` reads `2006` on an `INITIAL_BACKFILL` event is expected and means exactly what it says: the pipeline is bootstrapping against KSBCL's already-old data, not that ValueBrew has been tracking prices since 2006.

**7.5 "Newest" is defined by government-declared `effective_date`, never by pipeline run/ingestion date** — `beer_master.csv` exists to answer "what is legally true right now" (feeding the app's Price Verification feature), and ingestion date is an artifact of when this pipeline happened to run, not a legal fact.

---

## 8. Error handling

**8.1 Row-level failures never abort the run; they're logged and dropped.** Every product row is validated (Item Code format, date parses, all four prices parse to a positive decimal post-cleanup, name non-empty, supplier context present) before being trusted. A row that fails is written to `rejected_rows.csv` with its raw cells, page number, and the specific rule it failed — never silently absent, never silently kept.

**8.2 Aggregate/structural failures abort the run.** A page yielding zero recognizable rows (outside an allowlisted "expected blank page" reason), a column-header mismatch against the expected schema (defends against KSBCL silently renaming/reordering a column — §9 covers this as a validation rule too), or the rejected-row count exceeding a documented threshold (§12.5) — these stop the run rather than publishing output someone might mistake for complete.

**8.3 Extraction-bug-shaped failures (same Item Code twice in one run) hard-fail**, distinct from real-world data conditions (two different Item Codes that look like the same product), which are **flagged for manual review via `canonical_resolution_review.csv`, never auto-merged and never failed** — see §4.4.

**8.4 No mid-run checkpointing.** A full extraction empirically takes ~275 seconds — cheap enough that a failed run is simply re-run from page 1 rather than carrying the correctness risk of resuming with stale mid-run state (e.g., a supplier context checkpointed mid-section).

**8.5 Idempotent, all-or-nothing output.** Each stage writes to a new run-dated artifact (or a temp location promoted atomically on success) — a failed run produces no new artifact and never overwrites the previous month's good output in place.

**8.6 Logging tiers, scoped to what a monthly, human-supervised batch job actually needs:** DEBUG (routine skips — filler/supplier-header rows recognized), WARNING (a row dropped, with reason — expected occasionally, reviewed via the rejected-rows log), ERROR/abort (structural breakage per §8.2). No remote log aggregation or alerting is proposed for Phase 1 — this is monthly and human-reviewed, not a live service; revisit only if that changes.

---

## 9. Data validation

Automated checks run on **every** monthly output before `beer_master.csv`/`beer_price_history.csv` are promoted from candidate to accepted:

**Structural**
- Column headers match the expected schema by name, not position (defends directly against a future KSBCL format change silently shifting which field lands where — the single highest-leverage schema-drift risk for a pipeline meant to run for years).
- Every page yields a recognizable row set; unexpected zero-row pages abort the run.
- Total row count falls within a *rolling* historical band (median of the last N runs ± tolerance), not one hardcoded number that goes stale.
- Row-type classification counts (header/filler/product) logged and compared month over month.

**Field-level**
- Required fields non-null for every product row.
- All four price fields, post whitespace-stripping, match a strict numeric pattern; anything that still fails is quarantined, never coerced to 0/null.
- `MRP > 0` — hard reject otherwise (a `0.00` beer would otherwise enter the catalogue looking real and free).
- `MRP` within a plausible absolute range (tunable) — outliers flagged, not auto-accepted or auto-rejected.
- `effective_date` parses and isn't in the future relative to the PDF's own publication.

**Relational**
- `canonical_product_id` unique within `beer_master.csv` / `beer_master_duty_free.csv` (true by construction per §4.4/§4.5, checked anyway).
- `ksbcl_item_code` unique within `item_code_canonical_map.csv` — a repeat is the Case (a) extraction-bug scenario (§4.4), and hard-fails the run.
- **The MRP-vs-KSBCL-Selling-Price sanity check is applied only to rows where a case multiplier was actually parsed from the name** — applying it blindly to the 482 bare-volume rows would flag ~35% of real beer rows as false anomalies (§1, §5.5). Rows without a parsed multiplier are excluded from this specific check and separately counted as "case size unknown," not silently passed or silently failed.
- Classification match-reason ratio (style-word vs. brand-only matches) tracked month over month as a drift signal.
- `-DF` row count as a fraction of total, compared against the ~10% historical baseline.

**History**
- Price-history writes are idempotent per `(item_code, effective_date, price tuple)` — re-running the same month's PDF produces zero duplicate history rows.
- History only grows where the tuple actually differs from the last recorded state — never a wholesale "insert everything every month" (which the 2006–2026 date spread in §1 would otherwise fabricate thousands of phantom monthly events for unchanged SKUs).
- Price changes beyond a documented magnitude threshold are flagged in **either** direction — decreases are not treated as more suspicious than increases, and neither is auto-corrected.

**Supplier**
- New supplier names fuzzy-matched against a maintained alias table; near-matches (e.g., `"United Breweries Ltd"` vs. `"United Breweries Ltd-Nanjangud"` — same legal entity or a different regional plant is a real-world fact the PDF text alone can't settle) are flagged for human confirmation, never auto-merged.

**Ranked by how badly silent failure would corrupt the catalogue if missed:**
1. The MRP whitespace-tokenization artifact (§1, §5.4) — affects ~70% of price values; a careless parse produces a plausible-looking, wrong price at massive scale.
2. Keyword-only beer detection undercounting real SKUs (§6) — a false negative doesn't corrupt data, it erases a real beer from the catalogue with zero error signal.
3. Item-Code succession/reuse (§4.4) silently auto-merging into the wrong canonical product, or — the opposite failure — a real supersession never getting reviewed and sitting as two orphaned canonical products forever. This is why §4.4's auto-merge bar is "exact match only," never a fuzzy one.
4. Blind case-size assumptions feeding the MRP-vs-Selling-Price check (§5.5, §9) — either mass-false-rejects ~35% of real rows, or someone "fixes" that by hardcoding an assumed case size that's wrong for many products.
5. Column schema drift from positional (rather than header-name) parsing — the failure most likely to activate *later*, since this pipeline runs for years against a government publisher that can change formatting without notice.

---

## 10. Future enrichment strategy

**This pipeline is directed to become ValueBrew's durable, canonical data platform, independent of the mobile app** — not a Phase-1-only throwaway (per product-owner decision, see status note at top). Everything below is written accordingly: the seams named here are load-bearing for that goal, not speculative future-proofing.

**10.1 Why this shapes Phase 1's schema now.** No enrichment source (GS1, brewery sites, retailers, Untappd) shares any key with KSBCL's data. The only usable join signal, ever, is fuzzy matching on normalized name + pack size — which is exactly why `normalized_name_key`, `pack_size_ml`, `pack_count`, and `container_type` are first-class fields computed once during Normalization (§5) by one documented function, rather than being re-derived by every future enrichment job with its own ad hoc rules. **With `canonical_product_id` now the SKU identity (§4.4, decided §12.3), future enrichment sources should join against `canonical_product_id`, not `ksbcl_item_code`** — the canonical product is explicitly defined as the real-world-product identity, which is the semantically correct join target; `ksbcl_item_code` is a source-system key that can churn (§1) for a product whose real-world identity hasn't changed at all.

**10.2 Barcode/GTIN — a reserved, empty seam, not a built feature.** `gtin`/`gtin_confidence` are reserved on `beer_master.csv`, keyed to `canonical_product_id` (revised from the original design's item-code keying, now that canonical products exist) — nullable, unpopulated in Phase 1, purely to avoid a breaking schema migration later. This is **not** a promise that barcode matching ships soon: even at the canonical-product level, the relationship to GTIN should be assumed many-to-many-over-time (a canonical product's real-world packaging could change under one stable canonical ID) — so the real future home for this is a `canonical_product_gtin_map` join table (mirroring `item_code_canonical_map.csv`'s own shape: both IDs, observed-date ranges, a confidence tier), with the flat `gtin` column on `beer_master.csv` only ever a denormalized "current best guess" convenience once that table exists. General industry knowledge suggests India-market barcode coverage for regional beers is sparse — **explicitly flagged as unverified against this dataset**, not measured, and not something to plan a coverage target around without an actual audit (§12.6).

**10.3 Confidence tiers extend the app's existing discipline, never blend into it.** The app already treats price/ABV/identity as Verified Facts that must never be silently overwritten by inference (`docs/architecture/current/05-Beer-Knowledge-Model.md`). Enrichment data is not entitled to that tier for free: a brewery's own published ABV is Verified, but from a *different* verifying authority than KSBCL, and must stay attributable to its own source, never merged into KSBCL's pricing facts. A retailer-scraped fact is closer to Human Judgment (a copy of a copy, may be stale/wrong for the specific pack variant). Untappd/BeerAdvocate/RateBeer facts are explicitly crowd-sourced and must always be visibly labeled as such. Concretely, every future enrichment field should carry `{ value, source_type, source_name, confidence_tier, observed_at }` as a unit — never a bare scalar — mirroring the pattern `price_source` already establishes next to `price` on the app's existing `Sku` model.

**10.4 Where enrichment sits:** as **per-source tables** (`brewery_site.csv`, `gs1_barcode.csv`, `untappd.csv`, …), each carrying its own match confidence against a `canonical_product_id`, joined but never pre-merged into one table — merging early would force a conflict-resolution decision (whose ABV wins) that belongs to a not-yet-built catalog-build step, and would erase per-field provenance that §10.3 requires stay visible. That catalog-build step — reading `beer_master.csv` as the spine, left-joining each enrichment source, applying the Verified/Computed/Human-Judgment hierarchy — is explicitly **out of Phase 1 scope**, named here only because it's what justifies Phase 1's shape. `canonical_product_id` is a natural long-term candidate to become (or map 1:1 to) the app's future `Sku.id` in `catalog.json`, since both sit at the same real-world-product-plus-pack grain — noted here as an observation for that future catalog-build step, not a Phase 1 commitment.

**10.5 What Phase 1 must not bake in:** no assumption that one Beer maps to exactly one Style forever (no style data exists yet); no assumption of a 1:1 canonical-product↔GTIN relationship (§10.2); no assumption that a canonical product maps to exactly one `ksbcl_item_code` forever (already disproven by the confirmed item-code-succession pattern, §1, §4.4); no assumption that enrichment arrives complete or synchronously; no assumption that today's normalization function is final (it should be versioned so a future correction doesn't silently invalidate old matches); no invented `style`/`brand`/ABV field on `beer_master.csv` beyond what §4.4/§4.5 already define — KSBCL's data has none of those, and inventing one now means guessing at facts before any enrichment source exists to inform that guess.

---

## 11. Recommended implementation order

1. **Extraction (Stage 1) + its validation harness together, not sequentially** — the whitespace-tokenization defense and row classification are the highest-leverage, easiest-to-get-silently-wrong pieces in the whole pipeline (§9's #1 risk); build the check as part of the stage, not after.
2. **Beer identification (Stage 2) against the full 33,867-row extraction**, with the monthly self-check report (§6.4) built from day one — this is what turns the classifier from "trust it" into "confirm it," and doing it late means a month of unaudited classification decisions to retroactively review.
3. **Normalization (Stage 3)**, since Stage 4 and 5 both depend on `normalized_name_key`/`pack_size_ml`/`pack_count`/`container_type` existing.
4. **Canonical Identity Resolution (Stage 4)**, deliberately after normalization so its matching key is built on clean structured fields, not raw text. Build the `deterministic_high` auto-merge path and the manual-review flagging path (`canonical_resolution_review.csv`) together, from day one — shipping only the auto-merge path first would silently under-flag real supersession cases with no way to tell later that review was ever supposed to happen.
5. **Master + History (Stage 5)** — both diffs (§7.1: item-code-level history, canonical-level master), run first as `INITIAL_BACKFILL` against no prior state, then re-run conceptually against itself to prove the "unchanged → no history row" path actually produces zero spurious events (§7.3, §9's history checks) before it's trusted against a second real month.
6. **Full validation checklist (§9) wired to abort/promote the run**, and the folder/archive structure (§3) — before the *second* real monthly run, since that's the first point the diff logic (Stage 5) and the archive/rollback story actually get exercised for real.
7. **Barcode/enrichment schema seam (§10.2's reserved columns) added at Stage 5's schema definition**, not bolted on later — cheap now, expensive as a migration later. No matching logic ships in Phase 1.

This order front-loads the two stages most likely to silently corrupt data if under-built (extraction's numeric parsing, beer identification's recall) and pushes the two-run proof point (history correctness) to before the pipeline is trusted unattended.

---

## 12. Decisions

Per the project's Handling Ambiguity policy, these were surfaced rather than resolved by guessing. The three that blocked writing any code have been decided by the product owner; the rest have documented safe defaults and don't block starting implementation.

### Resolved

**12.1 — Implementation language: Python**, kept fully outside the Flutter app's dependency graph. Rationale (product owner): this is an offline data-engineering pipeline, not part of the Flutter runtime — optimize for correctness, determinism, and repeatable monthly ingestion, not for staying in one language. Outputs are language-agnostic CSV/JSON artifacts the app simply consumes. Reinforced by the direction that this pipeline is meant to later ingest additional sources (manufacturer sites, GS1/GTIN, retailers) without ever requiring a Flutter app change — Python's ecosystem is the better fit for that ongoing role, not just for this one PDF.

**12.2 — Duty-Free rows: excluded from the canonical retail catalogue, preserved in a separate dataset.** `beer_master.csv` represents Karnataka standard retail pricing only — the recommendation engine, Price Verification, Value Score, and retail comparisons all read from it exclusively. DF rows are never deleted; they're extracted into `beer_master_duty_free.csv`, sharing the same `canonical_product_id` space where the underlying product matches (§4.4, §6.5), so the data is available for a future feature without touching today's product surfaces.

**12.3 — "No duplicate live SKUs" resolved via a new indirection layer, not by picking a side of the original tension.** KSBCL Item Code is a **source-system identifier**, never the SKU identity — preserved exactly, forever, and never modified, exactly as originally required. A new, stable, internally-generated **Canonical Product ID** is the actual SKU identity `beer_master.csv` is keyed on, connected to Item Codes via `item_code_canonical_map.csv` (§4.4). This is a materially different design than the original nine-agent pass defaulted to (which had kept Item Code itself as the SKU-identity unit); it's threaded through §2–§11 above, not just recorded here. It also resolves what was originally flagged as a separate open question (Item-Code succession/continuity, e.g. the Budweiser Magnum pattern): a succession is just a manual-review-confirmed merge in the same mapping table, using the same mechanism as an exact-duplicate merge — no separate concept needed. Automatic merging is restricted to deterministic, very-high-confidence matches only (full name+pack+price+date equality); anything less exact creates a new canonical product and is flagged for manual review, never auto-merged.

### Open, non-blocking — safe defaults documented, revisit with real run history

**12.4 — Validation abort thresholds.** What rejected-row percentage, or row-count deviation from the rolling baseline, should abort a run vs. just warn? No historical run data exists yet to set this non-arbitrarily — start conservative (e.g., abort above 1–2% rejected) and tune after 2–3 real monthly runs.

**12.5 — Barcode coverage audit.** The "sparse India-market coverage" claim behind §10.2's long-horizon framing is general industry knowledge, not measured against this dataset. Doesn't block Phase 1 (no barcode matching ships), but should happen before any future barcode milestone is scheduled or promised.

**12.6 — Abbreviation/alias resolution** (e.g., `"PREM"` → `"Premium"`). Confirmed out of Normalization's scope (§5) since expanding it would be inventing text. Does this belong to a future fuzzy-matching stage with its own maintained, human-reviewed alias table, or is it out of scope entirely for Phase 1's identity model? Affects whether the brief's own three example name variants ever fully converge, or only two of the three do.

**12.7 — Enrichment source licensing.** Untappd, BeerAdvocate, and RateBeer's terms need a legal/licensing check before any future ingestion, per the brief's own "respect licensing" instruction — not a Phase 1 blocker, flagged so it isn't forgotten by the time §10 becomes actionable.

With §12.1–12.3 resolved, implementation of Stages 1–5 as designed above can begin.
