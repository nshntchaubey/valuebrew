# ValueBrew — KSBCL Stage 1 (Extraction) Contract

### The permanent contract Stage 1 (Extraction) provides, and that every later stage of the KSBCL beer pricing pipeline is entitled to depend on. Governed by [`KSBCL-Beer-Pricing-Pipeline-Architecture.md`](KSBCL-Beer-Pricing-Pipeline-Architecture.md) (the overall design, covering Stages 1–5 and future enrichment); this document describes only what Stage 1 actually ships, as a standalone reference that requires no Python knowledge to read. Implemented at `tool/ksbcl_pricing_pipeline/` (`models.py`, `parsing.py`, `validate.py`, `extract.py`, `io_writers.py`, `config.py`, `run_pipeline.py`).

**Status: Stage 1 is approved, implemented, hardened, and frozen.** Sections 9 and 12 below define exactly what "frozen" means and what it takes to change.

---

## 1. Purpose

**Stage 1 is responsible for exactly one thing:** turning one monthly KSBCL "Supplier-wise Item-wise Price List" PDF into a clean, validated, machine-readable table of every priced line item in that PDF — across **every** alcohol category, not beer alone — plus a complete, auditable record of everything that didn't make it in and why.

Concretely, Stage 1:
- Opens the PDF and walks it page by page, in order.
- Classifies every row it encounters (a repeated table header, a supplier section marker, a filler/spacer row, or a real product row).
- Tracks which KSBCL supplier is currently "active" as it reads down the file, since that context is never restated on every row.
- Cleans the four price columns and the effective-date column of known PDF-rendering artifacts (see §10).
- Validates every candidate product row against a fixed set of rules (§6).
- Writes out everything that passed, everything that didn't, and a summary of the whole run.

**Stage 1 is explicitly NOT responsible for:**
- Deciding what's beer and what isn't. Every category KSBCL prices (beer, wine, rum, whisky, vodka, brandy, gin, RTDs, …) passes through Stage 1 unfiltered. Category classification is Stage 2.
- Cleaning up or standardizing product *names* (casing, `×` vs `x`, redundant supplier-code suffixes, pack-size extraction). That's Stage 3.
- Deciding whether two different KSBCL Item Codes refer to the same real-world product. That's Stage 4.
- Tracking price history across months, or deciding what's "currently live." That's Stage 5.
- Anything related to barcodes, ABV, brewery, style, or any other enrichment. Not in this pipeline's Phase 1 scope at all.

If a future reader is trying to figure out *which* stage owns a piece of behavior and it isn't listed under "responsible for" above, it does not belong in Stage 1 — see §8.

---

## 2. Inputs

**Supported input:** exactly one KSBCL "Supplier-wise Item-wise Price List" PDF per run, supplied as a file path, together with the calendar month it represents (`YYYY-MM`, e.g. `2026-06`) supplied by the operator — Stage 1 never infers the period from the PDF's own text.

**Assumptions Stage 1 makes about that PDF**, all grounded in the architecture's ground-truth inspection of a real file:
- It is a native, text-layer PDF — pdfplumber can extract selectable table text from every page. A scanned/image-only PDF is **not supported**; there is no OCR fallback anywhere in this stage.
- Every page's table carries a repeated 8-column header, always containing (in any order — see §6) `SR NO`, `ITEM NAME`, `ITEM CODE`, `EFFECTIVE DATE`, `DECLARED PRICE`, `LANDED COST`, `KSBCL SELLING PRICE`, `MRP`.
- Product rows live inside "supplier sections," each introduced by a row whose Item Name reads `Supplier : <Name> (<4-digit code>)`, optionally followed by trailing text (a plant/city name has been observed in the real file) — see §10.
- Effective dates are written `DD-Mon-YY` (e.g. `13-May-26`).
- Price cells are Indian-formatted decimals with exactly two decimal places (e.g. `6,199.00`, `1,20,166.05`), sometimes corrupted by a PDF-rendering artifact that splits a value into two tokens with a spurious space (e.g. `1 40.00` for `140.00`) — Stage 1 defeats this unconditionally on every price cell.

**Unsupported inputs — behavior, not just a caveat:**
- A PDF with zero pages: the run aborts (§7).
- A page whose table extraction yields more than one table, or none at all: the run aborts. Stage 1 never guesses which of several tables is authoritative.
- A page whose header row is missing or doesn't contain all 8 expected column names: the run aborts.
- Any file that isn't a valid PDF `pdfplumber` can open: the run aborts with the underlying error logged (§7).
- A `--run-month` that doesn't match `YYYY-MM`: rejected at startup, before any PDF processing begins.

Stage 1 takes no other configuration that changes *what* it extracts — only *how strictly* it validates (see §6's tunable thresholds) and *where* it writes output (§3). Nothing about the input path, output path, or any threshold is hardcoded.

---

## 3. Outputs

Every run writes into `pricing_data/`, at the repository root, under two run-scoped locations keyed by `run_month`:

| Path | Contents |
|---|---|
| `pricing_data/raw_pdfs/<run_month>/<original filename>` | An archived, byte-identical copy of the input PDF. Written unconditionally, before extraction even starts, so a failed run still leaves the exact input file available for debugging. |
| `pricing_data/runs/<run_month>/structured_rows.csv` | **The primary output.** One row per accepted product row. |
| `pricing_data/runs/<run_month>/rejected_rows.csv` | One row per candidate product row that failed validation. |
| `pricing_data/runs/<run_month>/run_summary.json` | One JSON object summarizing the whole run: counts, thresholds used, and (on failure) the abort reason. |
| `pricing_data/runs/<run_month>/pipeline.log` | The complete log of the run, at whatever `--log-level` was requested. |

`structured_rows.csv` and `rejected_rows.csv` are written together, atomically, only on a fully successful run (§7) — never partially.

### 3.1 `structured_rows.csv` — **frozen public interface**

One row per accepted product row, in this exact column order:

| Column | Meaning |
|---|---|
| `item_code` | KSBCL's own Item Code, preserved byte-exact. **Must always be read back as a string** — see §9. |
| `item_name_raw` | The Item Name cell exactly as printed in the PDF. Untouched — no cleanup of any kind happens in Stage 1. |
| `supplier_name` | The supplier name from the nearest preceding `Supplier : …` row in the file. |
| `supplier_code` | That supplier's 4-digit code, as a string. |
| `effective_date_raw` | The Effective Date cell exactly as printed (`DD-Mon-YY`). |
| `effective_date` | The same date, parsed to ISO-8601 (`YYYY-MM-DD`). Two-digit years are always resolved as `20xx` (see §10). |
| `declared_price_raw` / `declared_price` | Declared Price: the cell exactly as printed, and the cleaned decimal value. |
| `landed_cost_raw` / `landed_cost` | Landed Cost: same pairing. |
| `ksbcl_selling_price_raw` / `ksbcl_selling_price` | KSBCL Selling Price: same pairing. |
| `mrp_raw` / `mrp` | MRP: same pairing. |
| `source_page` | The PDF page number this row was read from (1-indexed), for traceability. |
| `run_month` | The `YYYY-MM` period this run represents. |

Every `*_raw` field is preserved specifically so a dispute about "what did KSBCL actually print" can always be resolved without re-opening the PDF. The four parsed price fields are fixed-point decimals, never binary floats, always to two decimal places.

### 3.2 `rejected_rows.csv` — **stable public interface**

| Column | Meaning |
|---|---|
| `run_month` | Same as above. |
| `source_page` | Same as above. |
| `raw_row` | The complete original row, every cell, as a JSON array string — not a Python `repr()`, deliberately, so any tool (not just Python) can parse it. |
| `reason_code` | A short, stable, machine-parseable code identifying which rule failed. Drawn from a small closed vocabulary — see §5. Never a free-form or ad-hoc-concatenated string. |
| `reason_detail` | Free-text elaboration (the offending raw value, or a computed value), scoped to that one `reason_code`. May be empty. |

### 3.3 `run_summary.json` — **stable, additive-only interface**

A single JSON object per run. Existing keys are never renamed or repurposed; new keys may be added over time as long as that doesn't change the meaning of an existing one. Current keys: `run_month`, `source_pdf_reference`, `started_at`, `finished_at`, `status` (`"success"` \| `"failed"`), `abort_reason`, `total_pages`, `header_rows_seen`, `supplier_header_rows_seen`, `filler_rows_seen`, `product_rows_seen`, `product_rows_accepted`, `product_rows_rejected`, `rejected_rows_by_reason` (a `{reason_code: count}` map), `distinct_supplier_sections_seen`, and the five `*_used` fields recording the actual thresholds this run applied (`rejected_row_abort_pct_used`, `mrp_min_used`, `mrp_max_used`, `row_count_min_used`, `row_count_max_used`).

### 3.4 `pipeline.log`

Not a structured interface — a plain-text operator log, DEBUG/WARNING/ERROR (see §7). No downstream stage should ever parse this file for data; it exists for humans.

---

## 4. Acceptance guarantees

Every row in `structured_rows.csv` is guaranteed to satisfy **all** of the following, unconditionally:

- `item_code` matches `^\d{8,11}$` — 8 to 11 digits, nothing else.
- `item_name_raw` is present and non-empty.
- `supplier_name` / `supplier_code` reflect a real `Supplier : …` row that was actually seen earlier in the same file — never null, never inferred, never defaulted.
- `effective_date` is a real calendar date, and is not later than the last day of the run's `run_month`.
- All four price fields parsed successfully to a **strictly positive** decimal with exactly two decimal places.
- `item_code` is unique across the entire file for this run — if KSBCL's own PDF ever contained the same Item Code twice, the run would have aborted (§7) rather than silently keeping one copy.

**What downstream stages may safely assume from the above:** every field on every row is well-formed and internally consistent by the rules stated above, and nothing else. Downstream stages must **not** assume:
- That a row is beer (no category filtering has happened — §1).
- That the name is in any normalized/comparable form (no cleanup has happened — §1).
- That two rows with a similar name are, or aren't, the same real-world product (no identity resolution has happened — §1).
- That the four price columns are directly comparable to each other or across rows — they are preserved exactly as KSBCL published them, at whatever per-unit/case-level granularity the source used, with no reinterpretation (architecture §5.5).
- That `effective_date` reflects when the price changed relative to *last month's* file — Stage 1 has no memory of previous runs; that comparison is Stage 5's job.

---

## 5. Rejection guarantees

A candidate product row is rejected — written to `rejected_rows.csv`, excluded from `structured_rows.csv`, and never causing the run itself to fail — for exactly one of these reasons (`reason_code` values, grouped by cause):

| Cause | `reason_code` values |
|---|---|
| No active supplier context yet | `no_active_supplier_context` |
| Item Name missing/blank | `missing_item_name` |
| Item Code doesn't match `^\d{8,11}$` | `invalid_item_code_format` |
| Effective Date missing, unparseable, or calendar-invalid | `missing_effective_date`, `unparseable_effective_date`, `invalid_calendar_date` |
| Effective Date later than the run's month | `effective_date_after_run_month` |
| A price cell missing or fails to parse | `missing_declared_price` / `unparseable_declared_price`, and the equivalent pair for `landed_cost`, `ksbcl_selling_price`, `mrp` |
| A price parsed but wasn't strictly positive | `declared_price_not_positive`, `landed_cost_not_positive`, `ksbcl_selling_price_not_positive`, `mrp_not_positive` |
| MRP outside an operator-configured plausible range (off by default, §6) | `mrp_below_configured_min`, `mrp_above_configured_max` |

**What information is preserved:** the row's *entire* original content (`raw_row`, as JSON), which page it came from, which run it belongs to, and exactly one `reason_code` + `reason_detail` identifying the first rule it failed. A row is checked against the rules in a fixed order and rejected on the first failure — a row failing multiple rules only ever shows the first one.

**What downstream stages should never expect:**
- Rejected rows are **not** retried, corrected, or reprocessed by Stage 1 or any later stage automatically. A human decides what (if anything) happens next.
- A rejected row's Item Code is **not** guaranteed absent from `structured_rows.csv` — nothing prevents the *same real-world product* from also having a separate, correctly-formatted row elsewhere in the file (this has been observed for real: several genuinely malformed KSBCL Item Codes co-exist with cleanly-formatted rows for what looks like the same product line — see §10).
- The count of rejected rows can differ from `product_rows_seen − product_rows_accepted` for exactly one number: never — those two are always consistent by construction, but a *reason breakdown* should always be read from `rejected_rows_by_reason` / `rejected_rows.csv`, not inferred.

---

## 6. Validation guarantees

**What Stage 1 validates, exactly:**

*Row-level (produces a rejection, never aborts the run):*
- Item Code format, Item Name presence, Effective Date parseability/validity/recency, all four price fields' parseability and strict positivity, and (only if configured) MRP's plausible range.

*Structural / aggregate (aborts the run — see §7):*
- The PDF has at least one page.
- Every page yields exactly one extracted table, with a header row containing all 8 expected column names (matched **by name**, not by fixed position — see §9).
- No page yields zero rows.
- No Item Code repeats among accepted rows anywhere in the file.
- At least one product row was accepted overall.
- The overall rejected-row rate does not exceed `--rejected-row-abort-pct` (default 2.0%).
- If configured, total accepted rows fall within `--row-count-min` / `--row-count-max`.

**What Stage 1 intentionally does *not* validate** — not oversights, deliberate scope boundaries:
- Whether a row is beer, wine, spirits, or anything else (Stage 2).
- Name formatting consistency, or whether a pack size/count/container type can be extracted from the name (Stage 3).
- Whether the printed MRP is consistent with Landed Cost / KSBCL Selling Price for a given pack size — this specifically requires knowing the case size, which is not reliably derivable for every row (architecture §5.5), and Stage 1 never guesses it.
- Whether a supplier's name this month matches a slightly different spelling of the same supplier from a previous month (a "supplier alias" concern belonging to later validation, not Stage 1, which has no cross-run memory at all).
- Whether an Item Code that disappeared from this month's file was legitimately discontinued versus a data-entry gap — Stage 1 has no concept of "previous month" (Stage 5).
- Anything requiring information from outside this one PDF.

---

## 7. Failure guarantees

**Atomicity.** `structured_rows.csv`, `rejected_rows.csv`, and a `status: "success"` `run_summary.json` are written together, or not at all. Every file write goes through a write-to-temp-then-atomic-rename, so a crash mid-write can never leave a half-written file that a later process might mistake for complete.

**Idempotency.** Re-running Stage 1 against the same PDF and the same `--run-month` overwrites that run's outputs deterministically — never appends, never duplicates. Given identical input, `structured_rows.csv` and `rejected_rows.csv` are byte-identical run over run (verified directly against the real 750-page file, three consecutive runs). Only `run_summary.json`'s timestamps differ between runs.

**Abort conditions.** Listed exhaustively in §6's "structural / aggregate" bullets, plus: the input PDF path doesn't exist or isn't a file (checked before anything else runs), and any unexpected error not otherwise covered (caught, logged with a full traceback, never allowed to crash silently).

**Partial summaries.** If a run aborts partway through — say, on page 421 of 750 — `run_summary.json` still reflects everything genuinely accumulated before the abort: total page count (once the PDF was opened), every row-count field, and the rejection breakdown so far. It is never a blank slate. `status` is `"failed"` and `abort_reason` states specifically what went wrong (including the page number, for page-level failures).

**Logging.** Three levels: DEBUG for routine, expected skips (a repeated header, a recognized filler row); WARNING for every individual row rejection, with its reason and full raw content; ERROR for anything that aborts the run, including a full traceback for unexpected errors. Both the console and `pipeline.log` receive the same level of detail, controlled by `--log-level` (default `INFO`, which suppresses the per-row DEBUG noise but keeps every WARNING and ERROR).

**What "failure" never does:** it never leaves `structured_rows.csv` or `rejected_rows.csv` in a partially-written or stale state from a prior successful run — a failed run leaves the *previous* successful run's files exactly as they were, and adds only an updated `run_summary.json` (status `"failed"`) and `pipeline.log` for that run_month.

---

## 8. Non-goals

Explicitly deferred, not because they're unimportant, but because they belong to a different, later stage:

**Stage 2 (Beer Identification):** deciding whether a row is beer at all; any brand/style/keyword matching; Duty-Free channel tagging; classification confidence tiers.

**Stage 3 (Normalization):** name formatting cleanup (unicode/casing/whitespace unification); extracting `pack_size_ml`, `pack_count`, `container_type` from free text; producing a `normalized_name_key` for matching.

**Stage 4 (Canonical Identity Resolution):** deciding whether two different Item Codes represent the same real-world product; assigning a `canonical_product_id`; the `item_code_canonical_map.csv` mapping table; anything about the Budweiser-Magnum-style "same product, reissued code" pattern beyond simply preserving both rows as-is.

**Stage 5 (Master + History):** everything about "what's currently live," `beer_master.csv` / `beer_master_duty_free.csv`, price-change classification (`NEW_ITEM` / `PRICE_CHANGE` / `CORRECTION` / delisting), and `beer_price_history.csv`.

**Future enrichment (out of Phase 1 entirely):** barcode/GTIN, ABV, brewery, style, images, descriptions, and every external source named in the architecture's §10 — none of it is referenced, reserved, or hinted at anywhere in Stage 1's output.

---

## 9. Invariants

Properties that must never change silently — any change to any of these is, by definition, a new architecture decision, not an implementation detail (see §12):

1. **`structured_rows.csv`'s 16 columns, their names, and their order are frozen exactly as listed in §3.1.**
2. **`item_code` means KSBCL's own Item Code, preserved byte-for-byte** — never reformatted, coerced to a numeric type, zero-padded, or truncated. It is a *source-system identifier*, not a claim about real-world product identity (that distinction belongs to Stage 4's `canonical_product_id`).
3. **`supplier_name` / `supplier_code` mean "the supplier section this row physically appeared under in the PDF, in reading order"** — nothing more. Two rows with the same supplier fields are not guaranteed to be from the same physical page, only the same unbroken section.
4. **`declared_price`, `landed_cost`, `ksbcl_selling_price`, `mrp` mean "exactly what KSBCL printed for this column, cleaned of PDF-rendering artifacts only."** No unit conversion, no case-size normalization, no reinterpretation ever happens to these four values inside Stage 1.
5. **`effective_date` means the government-declared date this price took effect** — never the date this pipeline happened to observe it.
6. **A row appearing in `structured_rows.csv` means "this row passed every check in §4," and nothing more** — not "this is beer," not "this is a live/current price," not "this is a unique real-world product."
7. **Item Code is unique within `structured_rows.csv` for any single run** — enforced by aborting the run if violated, never by silently dropping one copy.
8. **All four price fields are fixed-point decimals with exactly two decimal places** — never binary floats, in memory or on disk.
9. **`rejected_rows.csv`'s `reason_code` vocabulary is closed and stable** (§5's table) — a new failure mode gets a new, additively-introduced code; existing codes are never renamed or repurposed.
10. **Every write is atomic and every successful run's pair of CSVs is internally consistent** (`product_rows_accepted` in the summary always equals the row count in `structured_rows.csv`, and likewise for rejected).

---

## 10. Known limitations

Discovered and accepted during Stage 1's build and its full-file run against the real 750-page KSBCL PDF — recorded here so they are never rediscovered as if new:

- **Genuine source-data corruption exists in KSBCL's own export**, independent of anything this pipeline does: Item Codes with a trailing letter (`044301010A2`), at least one rendered in spreadsheet scientific notation (`3.08015E+11` — a clear artifact of the source being generated from Excel), and at least one with a stray non-numeric character (a backtick). These are correctly rejected, not repaired — Stage 1 has no way to know what the "correct" code should have been, and inventing one would be worse than leaving the row out.
- **A hard dependency on the PDF being a native, text-layer document.** There is no OCR path. If KSBCL ever ships a scanned PDF, Stage 1 fails outright (most likely as a header-mismatch or zero-row abort) rather than degrading gracefully.
- **Column detection is name-based but only defensive against missing columns, not extra ones.** If a future KSBCL release adds a 9th column, Stage 1 will not notice or complain — it only requires that the 8 known names are present somewhere in the header row. An added column is silently ignored.
- **The "effective date not after run_month" check trusts the operator's `--run-month` input completely.** Stage 1 never cross-checks it against the PDF's own "AS ON DD.MM.YYYY" text (which appears in the page header text, but is not part of the extracted table and is not read by this stage). A wrong `--run-month` would likely (though not certainly) surface as an elevated rejection rate tripping the abort threshold, not a direct, named error.
- **The two-digit-year pivot (`YY` → always `20YY`) is a standing assumption**, correct for the entire range this pipeline has ever seen (2006–2026) and for the foreseeable operational life of the product, but not correct forever — it will need revisiting well before the year 2099.
- **Case-level vs. per-unit price ambiguity is preserved, not resolved**, by design (architecture §5.5, §9). Roughly a third of real beer rows state no case-multiplier in the name at all, meaning `landed_cost` / `ksbcl_selling_price` cannot always be reliably converted to a per-unit figure. Stage 1 does not attempt it, and no downstream stage should assume it has been done.
- **The duplicate-Item-Code check only covers a single run's file.** It cannot and does not detect an Item Code that was reused across different months for what might be an unrelated product, or the reverse — that requires cross-run state Stage 1 doesn't keep (Stage 4/5 territory).
- **Three validation thresholds have no architecture-specified value** and are operator-configured: `--rejected-row-abort-pct` (defaults to 2.0, following the architecture's own suggested starting point), `--mrp-min`/`--mrp-max`, and `--row-count-min`/`--row-count-max` (both pairs default to unset/inert until a real multi-month baseline exists to justify a number).

---

## 11. Relationship to later stages

**Stage 2 may rely on, without re-deriving or re-validating:**
- Every guarantee in §4 holding for every row in `structured_rows.csv`.
- `item_name_raw` being the untouched source text — Stage 2's classification heuristics operate on this field (or a copy it normalizes itself; Stage 1 provides no normalized variant).
- `supplier_name` / `supplier_code` being trustworthy as a *corroborating* signal (per the architecture's own explicit warning that supplier identity must never be the primary classification signal).
- The complete absence of category information — Stage 2 must derive it entirely from `item_name_raw`, `supplier_name`, and the two related config files described in the architecture (`beer_classification.yaml`, not owned by Stage 1).
- Every row in the file being present exactly once, for exactly one real Stage 1 pass — no hidden duplication, no missing pages.

**Stage 2 must NOT assume:**
- That `structured_rows.csv` contains only beer, or that non-beer categories have been excluded, filtered, or flagged in any way.
- That any two rows with similar names are related — that's not decided until Stage 4.
- That `item_code` says anything about category (its leading digits reflect supplier ordinal position in the source file, not product type — a documented trap in the architecture itself, §1).
- That rejected rows are recoverable, retryable, or safe to ignore as "duplicates already present elsewhere" — see §5.
- That any field beyond the 16 listed in §3.1 exists on `structured_rows.csv`. If Stage 2 needs something else, that is a new, explicit schema change requiring the process in §12 — never an assumption.

The same three points apply transitively to Stage 3 and Stage 4: they consume Stage 2/3's own outputs, not `structured_rows.csv` directly, but nothing in this document should be read as implying Stage 1 anticipates or special-cases their needs beyond what's stated here.

---

## 12. Change policy

**Stage 1 is frozen as of this document.** §3.1 (`structured_rows.csv`), §3.2 (`rejected_rows.csv`), and every invariant in §9 are public interfaces that Stage 2 is about to start building against.

From this point forward:

- **Any change to `structured_rows.csv`'s columns, names, order, or field meanings** — adding, removing, renaming, or reinterpreting a column — **requires an explicit architecture decision**, recorded the same way §12 of the architecture document records one (a numbered decision with context, the decision made, and consequences), never a silent code change justified only by convenience for whichever stage is being built at the time.
- **`rejected_rows.csv`'s schema and `reason_code` vocabulary** follow the same rule — new codes may be *added* without a formal decision (they're additive and don't break an existing consumer), but changing or removing an existing code's meaning requires one.
- **`run_summary.json` may grow additively** (new keys) without a formal decision; renaming or repurposing an existing key does not.
- **Internal implementation details not covered by this document** — module layout inside `tool/ksbcl_pricing_pipeline/`, the exact regex patterns, internal helper function names — remain free to change as long as every guarantee in this document keeps holding. This document describes contracts, not code, on purpose (per the brief that produced it) — refactoring Stage 1 internally is always allowed; changing what it *promises* is not, without going through this policy.

---

**Stage 1 is frozen, documented, and ready for Stage 2.**
