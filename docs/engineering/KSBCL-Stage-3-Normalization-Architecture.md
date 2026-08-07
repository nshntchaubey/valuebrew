# ValueBrew — KSBCL Stage 3 (Normalization) Architecture

### The complete design for Stage 3 of the KSBCL beer pricing pipeline. Governed by [`KSBCL-Beer-Pricing-Pipeline-Architecture.md`](KSBCL-Beer-Pricing-Pipeline-Architecture.md) (§2, §4.3, §5, §11, §12.6 in particular) and built directly on top of [`KSBCL-Stage-1-Extraction-Contract.md`](KSBCL-Stage-1-Extraction-Contract.md) and [`KSBCL-Stage-2-Beer-Identification-Architecture.md`](KSBCL-Stage-2-Beer-Identification-Architecture.md), both frozen. Per explicit instruction, this document's scope is held strictly to what the master architecture already calls Stage 3 (Normalization); canonical identity resolution (Stage 4) and Master + History (Stage 5) are not designed here.

**Status: FROZEN. Implemented (`tool/ksbcl_pricing_pipeline/normalize.py`, `normalize_models.py`, `normalize_stage.py`, `run_stage3.py`), run against real 2026-06 data (1,714 rows), and accepted after an independent data-only acceptance review. Both the architecture and the implementation are a stable upstream contract for Stage 4 onward — no further architectural, behavioral, or implementation changes except a reproducible bug fix, a master-architecture change, or an explicitly requested vocabulary/configuration update.**

---

## 0. Sources consulted

The master pipeline architecture (all 12 sections, especially §2's pipeline diagram, §4.3's Stage 3 schema sketch, §5's normalization rules, §11's implementation order, and §12.6's explicit scope exclusion), the Stage 1 Extraction Contract (frozen — every field this stage reads), and the Stage 2 Beer Identification Architecture (frozen — §11 in particular, which already states the exact row-set contract Stage 3 must honor). Real Stage 1/Stage 2 output already on disk (`pricing_data/runs/2026-06/structured_rows.csv`, `classification_audit.csv`, both real, 2026-06) was used throughout to ground every extraction rule below in confirmed, real row text — not invented examples — the same discipline Stage 2's document held itself to.

---

## 1. Purpose

**Stage 3 owns exactly one job:** turning each beer candidate's raw, free-text name into a small set of clean, structured, additive fields — a comparison key and physically-meaningful pack attributes — without inventing, correcting, or completing anything KSBCL didn't actually publish. Concretely, Stage 3:

- Reads every row Stage 2 marked `included = true` (§2.2 below — the exact, already-frozen contract, not re-derived here).
- Produces `display_name` and `normalized_name_key` — the human-readable and matching-only forms of the name (master §5.2).
- Extracts `pack_size_ml`, `pack_count`, `container_type` as structured fields, additively — `item_name_raw` is never overwritten (master §5.3).
- Never guesses: a name that doesn't fit the expected pack-info pattern at all leaves `pack_size_ml`/`pack_count`/`container_type` null/`unknown` rather than a fabricated value — this state is fully recoverable by checking `pack_size_ml IS NULL` and needs no separate flag (§12 records why the schema no longer carries a dedicated `extraction_incomplete` column).
- Is deterministic and idempotent: the same name, under a fixed normalization rule version, always produces the same structured fields (§5 below).

**Stage 3 explicitly does NOT own:**

- **Canonical identity, merging, or deduplication** — whether two rows are "the same beer" is Stage 4's job entirely (master §4.4). Stage 3 produces the *raw material* one component of Stage 4's matching key is built from (`normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type`) — it never itself compares two rows to each other. This document does not answer "what constitutes one canonical beer," "when do two rows become one beer," "when must they remain separate," or "how are manual-review decisions preserved" — those are Stage 4 questions, to be answered in that stage's own architecture document, not here (§9 below).
- **Price history or master construction** — Stage 5's job entirely. This document does not answer "how are historical price changes represented" (master §7, §4.6 already answer this at the master level, for Stage 5).
- **Beer/not-beer classification** — already decided by Stage 2; Stage 3 never re-evaluates `confidence_tier` or `matched_term`, only reads `item_code` to know which rows are in scope.
- **Abbreviation/alias expansion** ("PREM" → "Premium") — explicitly excluded from Normalization by the master's own §12.6, which frames this as a *possible* future fuzzy-matching stage's concern, not resolved and not Stage 3's to resolve.
- **Price/date parsing or cleanup** — see §2.1's note below: this was originally sketched under "Normalization" in the master's §5.4, but has since been fully absorbed by Stage 1's own, later, frozen contract. Stage 3 does not duplicate it.
- **Supplier-name aliasing** (`"United Breweries Ltd"` vs. `"United Breweries Ltd-Nanjangud"`) — master §9's "Supplier" validation check and the reserved `config/supplier_aliases.yaml` seam are cross-cutting validation concerns, not part of §4.3/§5's Stage 3 schema. Not owned here.
- **Per-unit price computation** — explicitly deferred indefinitely by the master's own §5.5; not resurrected here.

---

## 2. Inputs

Stage 3 takes exactly two inputs: Stage 1's output and Stage 2's output, for the same run.

### 2.1 `structured_rows.csv` (from Stage 1, frozen contract)

Every guarantee in the Stage 1 contract's §4 is inherited directly. In particular: `item_name_raw` is present, non-empty, and byte-exact from the source PDF — the only field Stage 3's own normalization logic reads from this file. The four price fields and `effective_date` are already parsed, clean values (fixed-point decimal, ISO date, whitespace-tokenization artifact already defeated, Indian comma-grouping already parsed) — **this is the same cleanup the master's own §5.4 describes under "Normalization,"** word for word (strip internal whitespace → parse Indian comma-grouping → fixed-point decimal; explicit `DD-Mon-YY` parsing with a documented two-digit-year pivot). That description predates Stage 1's own later hardening pass, which fully implemented it as part of Stage 1's frozen contract instead. This is a staleness in the master document, not a live requirement: **Stage 3 does not re-parse, re-clean, or duplicate price/date fields in any way** — it reads `item_name_raw` only, and any consumer needing price/date fields gets them from `structured_rows.csv` directly via the `item_code` join, never re-derived here.

### 2.2 `classification_audit.csv` (from Stage 2, frozen architecture)

Stage 2's own §11 ("Relationship to later stages") already states the exact contract, treated here as binding, not re-derived: *"Stage 3 (Normalization) consumes exactly the rows Stage 2 marked `included = true` — joining `structured_rows.csv` and `classification_audit.csv` on `item_code`... Stage 3 must not assume anything about `matched_term` or `confidence_tier` beyond 'this row is in scope' — no coupling between why a row was classified beer and how its name gets normalized."* Stage 3 reads only `item_code` and `included` from this file; every other Stage 2 column (`confidence_tier`, `matched_term`, `exclusion_term_matched`, `supplier_known_beer_seller`, `is_duty_free`, `classification_config_version`) is opaque to Stage 3 and is available to later stages via the same join, never copied forward here.

**Row-set scoping, stated precisely:** the join is `structured_rows.csv ⋈ classification_audit.csv` on `item_code`, filtered to `included = true`. A row with `confidence_tier = low` (`included = false`) never reaches Stage 3, by construction — normalizing an excluded row's name would be wasted, unaudited work with no consumer, and would risk a later stage accidentally treating its mere presence in a Stage 3 output file as an inclusion signal.

### 2.3 Assumptions

- Stage 3 runs only against a `structured_rows.csv`/`classification_audit.csv` pair from the same, successfully-completed `run_month` — mirroring Stage 2's own §2.3 precondition posture (no "Stage 1 or 2 failed, run Stage 3 anyway" scenario is designed for).
- Every `item_name_raw` reaching Stage 3 is non-empty (guaranteed by Stage 1's contract) but may be arbitrarily messy free text — normalization exists precisely because no further cleanliness is assumed.

### 2.4 Unsupported inputs

- **A `classification_audit.csv` with zero `included = true` rows** aborts the run — mirrors Stage 2's own §9 hard structural assert (a real month always has hundreds of included rows; zero means an upstream failure, not a real data condition).
- **An `item_code` present in `classification_audit.csv` but absent from `structured_rows.csv`, or vice versa for an included item_code** — a join integrity failure, hard-aborts the run. This should be structurally impossible given both files are frozen, unmodified outputs of the same two prior stages for the same `run_month`, but is checked anyway (§7 below), the same defensive posture Stage 1 applies to its own structural invariants.

---

## 3. Outputs

One artifact — the master's own folder structure (§3) never named a Stage 3 output file, only sketching the fields it should eventually carry (§4.3). This document names and fully specifies it, the same way Stage 2's document "hardened and extended" the master's terse `classification_audit.csv` sketch into a complete schema (Stage 2 architecture §3).

### 3.1 `pricing_data/runs/<run_month>/normalized_rows.csv` — the primary output

One row per `item_code` Stage 2 included (§2.2) — never a copy of `structured_rows.csv` with columns bolted on; deliberately the same order of magnitude as `classification_audit.csv` (~1,400–4,500 rows/month, per Stage 2's own real-run range), joined back to it and to `structured_rows.csv` by `item_code`.

| Column | Meaning |
|---|---|
| `run_month` | Consistent with every other per-run artifact in this pipeline. |
| `item_code` | Join key back to `structured_rows.csv` and `classification_audit.csv`. |
| `display_name` | `item_name_raw` with only the trailing `(NNNN)` supplier-code suffix stripped and whitespace collapsed — source casing preserved (master §4.3, §5.2). For UI/reports; never used for matching. |
| `normalized_name_key` | Fully case-folded, symbol-unified comparison key (master §5.1, §5.2) — never displayed. The primary component of Stage 4's future matching key; computed once, here. |
| `pack_size_ml` | Parsed numeric, in millilitres. **Null exactly when pack-info extraction failed to find a volume at all** — a real beer name always states one (§4.4); this is the only signal needed for that condition (§12 records why a separate `extraction_incomplete` flag was removed as redundant with this). |
| `pack_count` | Parsed numeric. **Nullable** — many real rows state no case multiplier at all (master §1, §4.3, §5.3); absence is preserved, never defaulted to 1 or to any other assumed value. Kept public rather than internalized: master §4.4 lists it as a component of Stage 4's canonical-identity matching key, a requirement this document has no authority to change unilaterally (§12 records a self-correction here — an earlier revision of this document recommended making it internal without re-checking this). |
| `container_type` | Controlled vocabulary: `bottle` \| `can` \| `pet_bottle` \| `tetra_pack` \| `unknown` (master §4.3). `unknown` is a legitimate, expected value, not an error — see §4.4. |
| `normalization_rule_version` | See §4.7 — an explicit, hand-maintained version identifier for the normalization algorithm itself, satisfying master §10.5's requirement that "today's normalization function" not be assumed final. |

**On not extending `structured_rows.csv` or `classification_audit.csv` in place:** the same reasoning Stage 2's document gives for keeping `classification_run_summary.json` separate from Stage 1's `run_summary.json` applies identically here — reopening and mutating an already-finalized artifact from an earlier stage would either violate that stage's own atomicity guarantee or require inventing a new one for a file with two writers. A separate, additive `normalized_rows.csv`, joined by `item_code`, keeps every stage's own output self-contained.

---

## 4. Normalization mechanism

### 4.1 One shared fold, feeding both `display_name`'s stripping step and every structured-extraction rule

Every rule below operates on a single, shared, ordered fold of `item_name_raw` (master §5.1), computed once per row:

1. Unicode NFKC normalization.
2. Unify the `×`/`x`/`X` case-multiplier symbol to one canonical character (`x`).
3. Collapse runs of whitespace to a single space, trim.
4. Strip the redundant `(supplier_code)` fragment — matched against this row's own known `supplier_code` (from `structured_rows.csv`), **wherever it appears in the string, not only at the end** (§12 records why: real rows exist where this fragment precedes the volume rather than trailing the name, e.g. `"Sapporo Draft Beer (Can) (0364) 350 Ml"` — a strict-suffix rule misses it). Tolerant of the confirmed missing-paren malformation via an optional-open-paren pattern, e.g. a bare `0364)` with no matching `(` is still recognized and stripped. This remains a strict generalization of the master's original "trailing suffix" framing (master §5.1) — every previously-confirmed trailing example is still matched, since a position-independent search is a superset of a suffix-only one.
5. Unify volume-unit casing/spacing (`650ML` / `650 ML` / `180Ml` → one canonical form, `ml`, with no internal space).
6. Case-fold.

This is exactly master §5.1's ordered list, applied once. `display_name` is produced by stopping after step 4 (suffix-stripped, whitespace-collapsed) and **preserving source casing** from that point — steps 5–6 are matching-only refinements that feed `normalized_name_key` and the structured-extraction rules in §4.4, never `display_name` (master §5.2: `display_name` is "source casing preserved — for UI/reports"). Nothing beyond these six steps: no stemming, no word reordering, no filler-word removal, no abbreviation expansion (master §5.1's closing sentence, restated because §12.6 makes the same point from a different angle).

### 4.2 `display_name`

`item_name_raw` after fold steps 1–4 only, casing preserved. Example (confirmed real row, master §1): `item_name_raw = "Original Bira 91 White Beer 650ML(0260)"` → `display_name = "Original Bira 91 White Beer 650ML"`.

### 4.3 `normalized_name_key`

`item_name_raw` after all six fold steps. Same example → `normalized_name_key = "original bira 91 white beer 650ml"`. Never displayed; comparison use only (Stage 4's future matching key).

### 4.4 Structured extraction: `pack_size_ml`, `pack_count`, `container_type`

Applied to the fully-folded text (post step 6), so casing and unit-spelling variance are already unified before pattern-matching begins — additive extraction, never replacing `item_name_raw` or `display_name` (master §5.3).

**`pack_size_ml`, stated as its own grammar, not a reused vocabulary-boundary rule (§12 records why the earlier version of this rule was wrong):** an earlier draft of this rule reused Stage 2's character-class token-boundary primitive wholesale — correct for detecting an isolated *vocabulary term* amid unpredictable prose, but the wrong tool here. Pack-info text is not unpredictable prose; it is a small, structured sequence (`volume` + `unit` + optional `[multiplier][count][container]`), and Stage 2's boundary rule treats the canonical multiplier character (a letter, per fold step 2) as ordinary, unrelated text immediately after `ml` — which fails on the dominant real naming pattern (confirmed: 948 of 1,714 real included rows in the 2026-06 run state the multiplier with no separator, e.g. `"650ML×12Btls"` → folded `"650mlx12btls"`).

The rule instead: a run of digits (optionally with a decimal point, e.g. `187.5`) immediately followed by the canonical unit token `ml`, where the unit token's right edge is a valid continuation of the pack-info pattern if it is *either* (a) a standard character-class boundary (whitespace, punctuation, end of string — Stage 2's rule, still correct for this side), *or* (b) immediately followed by the canonical multiplier character — that specific adjacency is a defined, expected continuation of this grammar, not competing or ambiguous content. The **first** such match in the folded string is used — declaration-position order, mirroring the same deterministic-first-match discipline Stage 2 applies to its own vocabulary matching. Only `ml` is a confirmed unit in the real KSBCL corpus inspected so far — a bare `l` (litre) unit has no confirmed real instance; per the same confirm-then-extend discipline Stage 2's §4.7 already establishes, `l` is not handled until a real row requires it.

*Must extract* (confirmed real rows):
- `"Haywards 5000 Premium Strong Beer 650ML×12Btls"` (master §1) → `pack_size_ml = 650`
- `"Original Bira 91 White Beer 650ML(0260)"` (master §1, no multiplier at all) → `pack_size_ml = 650`
- `"Batch Distilled Gin-DF 1000ML x 12Btls"` (confirmed real, 2026-06 run — space-separated multiplier) → `pack_size_ml = 1000`

**`pack_count`:** the integer immediately following the canonical multiplier character (`x`, after step 2's unification), itself immediately preceding — or, if the multiplier appears with surrounding whitespace, separated only by whitespace from — a recognized container token (§4.4's container list below) or the end of the pack-info segment. **Nullable**: absent whenever no multiplier is present at all (the Bira 91 example above; master §1 confirms 482 of 1,389 sampled beer rows have no case-multiplier text at all) — never defaulted to 1.

*Must extract* (confirmed real rows):
- `"Haywards 5000 Premium Strong Beer 650ML×12Btls"` → `pack_count = 12`
- `"Budweiser Magnum Beer-CAN 330ML×24Cans"` → `pack_count = 24`
- `"Brewdog Lost Lager DF 330ML X 24Btls."` (confirmed real, 2026-06 run — trailing period after the container word does not block extraction, since punctuation is a token boundary, not part of the token) → `pack_count = 24`

*Must not extract a value* (confirmed real):
- `"Original Bira 91 White Beer 650ML(0260)"` → `pack_count = null`, not `1`.

**`container_type`, a priority order, not a symmetric collision check (§12 records why the earlier "more than one match → `unknown`" rule was a modeling error, not a missing tie-break):** `Can`/`PET`/`Tetra` are deliberate, standalone assertions about the individual unit's physical container. `Btls`/`Bottle`/`Bottles`, when they appear immediately in the multiplier-count segment (the same token that supplies `pack_count`, e.g. the `Btls` in `"...x24Btls"`), are not an independent container claim at all — they function as a generic per-unit count-noun in KSBCL's own naming convention, the same rhetorical role "units" or "pieces" would play. Treating both as equally-weighted, competing evidence for one fact was the actual defect (confirmed on 36 of 1,714 real rows, e.g. `"Royal Challenge Strong Premium Beer-CAN 330MLx24Btls(0217)"`, where the true, standalone answer is `can` and `Btls` is boilerplate).

The rule: `can`/`pet_bottle`/`tetra_pack` keywords (`can`/`cans`, `pet`, `tetra`) take priority wherever they appear in the folded string, word-boundary-anchored per Stage 2's §4.1. `bottle` (`btl`/`btls`/`bottle`/`bottles`) supplies `container_type = bottle` only when none of the three specific keywords are present anywhere in the name. There is no collision case to resolve — the priority order removes the concept entirely, rather than adding a tie-break to it.

*Must extract* (confirmed real rows):
- `"Haywards 5000 Premium Strong Beer 650ML×12Btls"` → `container_type = bottle` (no specific keyword present; `Btls` supplies bottle by default)
- `"Budweiser Magnum Beer-CAN 330ML×24Cans"` → `container_type = can`
- `"Sapporo Draft Beer (Can)-Df 350ml"` → `container_type = can` (parenthetical, no multiplier present at all)
- `"Royal Challenge Strong Premium Beer-CAN 330MLx24Btls(0217)"` → `container_type = can` (the standalone `CAN` qualifier wins over the count-position `Btls`)

*Must default to `unknown`, never guessed* (confirmed real):
- `"Original Bira 91 White Beer 650ML(0260)"` → `container_type = unknown` (no recognized container token anywhere in the name).

### 4.5 Malformation and incomplete-extraction handling — recorded as monitoring signals, not per-row public fields (§12)

**Suffix malformation:** detected during the shared fold's step 4 (§4.1) — a by-product of the fold, true exactly when a `supplier_code)` fragment was recognized and stripped despite no matching open parenthesis in the source. No downstream consumer was found for this fact anywhere in the master architecture or this document's own validation section across repeated review — the strip happens identically either way, and no matching-key or master-schema field depends on it. It is tracked as an aggregate rate in `normalized_run_summary.json` (§7) — a rising rate is a real signal of KSBCL data-quality drift worth a human's attention — but is not a column on `normalized_rows.csv`.

**Incomplete pack-info extraction:** when §4.4's rule finds no volume at all, `pack_size_ml`, `pack_count`, and `container_type` are all left null/`unknown` — a name whose overall pattern can't be recognized is treated as unreliable in full, never partially salvaged (consistent with "never a guessed value" applying to the whole extraction, not field-by-field). This state is fully and unambiguously recoverable by checking `pack_size_ml IS NULL` — per §3.1's own field definition, that is the *only* reason `pack_size_ml` is ever null, so a dedicated `extraction_incomplete` column would carry zero information beyond what the schema's own null-state already states. Tracked as an aggregate rate in `normalized_run_summary.json` (§7), the same as suffix malformation.

No real row confirming either condition has been found in the 2026-06 run inspected so far — both are defensive, specified rules for a case not yet observed, the same posture Stage 2's §8 takes toward several of its own edge cases.

### 4.6 What is never touched

The actual brand/product vocabulary, any abbreviation, any pack-count that isn't stated, `item_name_raw` itself, and any row whose extraction is incomplete (left null, never dropped, never defaulted) — restated from master §5's closing line because it governs every rule above.

### 4.7 `normalization_rule_version` — versioned per master §10.5, by a different mechanism than Stage 2's config hash, for a stated reason

Master §10.5: "no assumption that today's normalization function is final (it should be versioned so a future correction doesn't silently invalidate old matches)." Unlike Stage 2's `beer_classification.yaml`, Stage 3's rules (§4.1–§4.5) are a fixed, deterministic algorithm with no external, curator-edited data file to hash — the rules themselves are code, changed only by an engineer making a deliberate change, not by a non-engineer curator who might forget a manual step. A hand-maintained version constant (e.g. `"stage3-v1"`, bumped alongside any code change to §4.1–§4.5's rules) is therefore the right mechanism here, for the *opposite* reason Stage 2 rejected a hand-maintained version for its own config: Stage 2's version-bump risk was a curator forgetting to touch a data file they weren't otherwise editing; Stage 3's rules can only change via a code change an engineer is already making, where bumping a co-located constant is a normal, low-risk part of that same change. This is a permanent mechanism (not a stopgap for a future automated version scheme) — it exists because there is no natural file to content-hash here, and stays even if the extraction rules are later ported to a config-driven form, at which point *that* change would itself bump the version.

---

## 5. Determinism and idempotency

Stage 3 has no persistent, cross-run state at all — unlike Stage 2's two ledgers, every rule in §4 is a pure function of `(item_name_raw, normalization_rule_version)`. This makes Stage 3's determinism claim unconditional, not scoped the way Stage 2's §9.1 had to be clarified to be: **identical `item_name_raw`, under a fixed `normalization_rule_version`, produces identical structured fields, every time, with no precondition on prior runs, prior state, or run order** — directly testable by re-running the same month any number of times and diffing `normalized_rows.csv`, with no convergence period, matching Stage 1's own idempotency bar exactly (not merely "exactly as," the way Stage 2 had to qualify it).

Re-running an already-processed month deterministically overwrites `normalized_rows.csv` for that `run_month` — never appends, never duplicates, mirroring Stage 1 contract §7 and Stage 2 architecture §8.5 precisely.

---

## 6. Edge cases

| Case | Outcome | Mechanism |
|---|---|---|
| No case multiplier at all (Bira 91 pattern, confirmed real, 482/1,389 sampled) | `pack_size_ml` found, `pack_count = null`, `container_type` from priority-ordered keyword search or `unknown` | §4.4 |
| Container word in a standalone parenthetical, no multiplier (Sapporo pattern, confirmed real) | `pack_count = null`, `container_type` still correctly found | §4.4 (global, priority-ordered search) |
| Container word before the volume (Kilkenny pattern, confirmed real) | `container_type` still correctly found — not positionally anchored | §4.4 |
| Multiplier glued directly to the unit with no separator (`"650ML×12Btls"`, confirmed on 948/1,714 real included rows — the dominant real pattern) | `pack_size_ml` still correctly found — the multiplier is a defined valid continuation, not a boundary violation | §4.4 (fixed) |
| Standalone container qualifier co-occurring with a generic count-noun (`"...-CAN 330MLx24Btls"`, confirmed on 36/1,714 real rows) | `container_type = can` — the standalone qualifier wins, no ambiguity | §4.4 (fixed) |
| Supplier-code parenthetical not trailing (`"Sapporo Draft Beer (Can) (0364) 350 Ml"`, confirmed real) | Stripped correctly regardless of position | §4.1 (fixed) |
| Missing-paren supplier-code malformation | Suffix still stripped from both `display_name` and the matching fold; tracked as an aggregate rate only, not a per-row field | §4.1, §4.5 |
| Space-separated multiplier (`"1000ML x 12Btls"`, confirmed real) | `pack_count` still correctly found | §4.4 |
| Trailing punctuation after container word (`"24Btls."`, confirmed real, from Stage 2's own §4.8) | `pack_count`/`container_type` still correctly found — punctuation is a boundary, not part of the token | §4.4, reusing Stage 2 §4.1's token-boundary rule |
| No recognizable volume anywhere in the name | `pack_size_ml`, `pack_count`, `container_type` all null/`unknown`; recoverable via `pack_size_ml IS NULL` alone | §4.5 — no real row confirmed yet; defensive |
| A row Stage 2 excluded (`included = false`) | Never reaches Stage 3 at all | §2.2 |
| Bare `l` (litre) unit | Not handled — no confirmed real instance; extend only on real evidence, per §4.7's confirm-then-extend posture, matching Stage 2 §4.7 | §4.4 |
| Abbreviated/misspelled words in the name (e.g. a hypothetical "PREM" for "Premium") | Untouched — normalization never expands or corrects vocabulary | §4.6, master §12.6 |

---

## 7. Validation

Mirroring Stage 2's §9 posture (determinism / explainability / non-regression, not an accuracy percentage against a label nobody has):

- **Join integrity**: every `item_code` in `normalized_rows.csv` must appear in both `structured_rows.csv` and `classification_audit.csv` with `included = true`, and every `included = true` item_code in `classification_audit.csv` must appear exactly once in `normalized_rows.csv` — a mismatch in either direction hard-aborts the run (§2.4).
- **`pack_size_ml` null rate tracked against a rolling historical baseline** — a sudden spike signals either a real shift in KSBCL's naming convention or a Stage 3 regression, the same "cheap early-warning wire" role Stage 2's §9 gives its own style:brand ratio metric. This is the aggregate signal that replaces a per-row `extraction_incomplete` column (§4.5, §12).
- **Suffix-malformation rate tracked the same way** — an aggregate-only metric now (§4.5, §12), not a per-row field.
- **`container_type = unknown` rate tracked the same way** — expected to be non-trivial (not every real row states a container word) but a sudden jump is worth surfacing, not silently absorbed.
- **`normalization_rule_version` present and non-null on every row** — the same reconstructability guarantee `classification_config_version` gives Stage 2's output.

---

## 8. Error handling

Row-level extraction failures never abort the run — they leave `pack_size_ml`/`pack_count`/`container_type` null/`unknown` and proceed, the same "flag, don't fail" posture Stage 1 gives per-row validation failures and Stage 2 gives its own None-tier silence. Structural failures (join integrity, zero included rows) abort the run per §2.4, written as a failed `normalized_run_summary.json`-equivalent artifact — this document does not further specify that artifact's exact shape beyond noting it should follow the identical atomic-write, partial-state-on-failure pattern already established by Stage 1's `run_summary.json` and Stage 2's `classification_run_summary.json`, left as an implementation-time detail exactly as several of Stage 2's own logging choices were.

---

## 9. Relationship to later stages

**Stage 4 (Canonical Identity Resolution)** consumes `normalized_rows.csv` joined to `structured_rows.csv` and `classification_audit.csv` on `item_code`. Stage 3 hands off exactly: `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type` (the four components of the master's already-decided matching key, master §4.4 — `supplier_code` being the fifth, sourced directly from `structured_rows.csv`, not from Stage 3), plus `display_name` for eventual human-facing use in `beer_master.csv`. **Stage 3 does not decide, and this document does not answer, any of the following — they belong to Stage 4's own architecture, not here:** what constitutes one canonical beer; what fields *define* canonical identity (the matching key itself is already decided at the master level, §4.4 — Stage 3 only supplies its inputs); when two rows become one beer versus when they must remain separate; how new SKUs attach to an existing canonical beer; how manual-review decisions are preserved. Stage 3's only obligation to Stage 4 is that `normalized_name_key`/`pack_size_ml`/`pack_count`/`container_type` be deterministic, auditable, and never silently guessed — matching Stage 4's own auto-merge bar (master §4.4: "very high confidence... full name+pack+price+date equality") being only as trustworthy as the fields it's computed from.

**Stage 5 (Master + History)** has no direct relationship to Stage 3 at all beyond the same `item_code` join every later stage uses — `display_name`, `pack_size_ml`, `pack_count`, `container_type` flow into `beer_master.csv`'s own schema (master §4.5) via that join, but how historical price changes are represented (`beer_price_history.csv`, master §7) is entirely Stage 5's concern and is not addressed here.

**Future enrichment** — master §10.1 already establishes that `normalized_name_key`, `pack_size_ml`, `pack_count`, and `container_type` are the intended long-term join surface for fuzzy-matching against external enrichment sources, computed once here "by one documented function, rather than being re-derived by every future enrichment job with its own ad hoc rules." This document's §4 is that documented function; nothing further is owed to enrichment from Stage 3 itself.

---

## 10. Non-goals

- **Canonical identity / deduplication** — Stage 4.
- **Price history / master construction** — Stage 5.
- **Beer/not-beer classification** — Stage 2, already decided.
- **Abbreviation/alias expansion** — explicitly out of scope, master §12.6.
- **Price/date parsing** — fully absorbed by Stage 1's frozen contract; not duplicated here (§2.1).
- **Per-unit price computation** — deferred indefinitely, master §5.5.
- **Supplier-name aliasing** — a cross-cutting validation concern (master §9), not part of this stage's schema.
- **A `normalized_name_key` that expands abbreviations, corrects misspellings, or reorders words** — explicitly rejected, master §5.1's closing sentence.

---

## 11. Open questions

1. **Is the bare-`l` (litre) unit ever real in KSBCL data?** Unconfirmed either way — resolved empirically once Stage 3 runs against real data and any row it can't parse a volume from surfaces via `extraction_incomplete`'s tracked rate (§7), not guessed at now (§4.4).
2. **Does the container-type keyword list (`btl`/`can`/`pet`/`tetra` and their variants) need expansion?** The master's own controlled vocabulary (§4.3) includes `pet_bottle`/`tetra_pack` without a confirmed real-row citation for either — carried forward as already-decided at the master level, not re-litigated here, but their actual incidence (if any) in real KSBCL beer rows is unconfirmed and worth watching via `container_type` distribution once Stage 3 runs for real.
3. **Where exactly should a `normalized_run_summary`-equivalent artifact live, and what exact fields belong on it?** Left as an implementation-time choice (§8), the same posture Stage 2's §10 took toward its own log-file placement.
4. **Should `normalization_rule_version` ever need to vary *within* a single run** (e.g. a mid-month hotfix)? Not designed for — the version is fixed for the lifetime of one Stage 3 invocation, matching how `classification_config_version` is fixed for one Stage 2 run; a genuine mid-run rule change is out of scope, the same way a mid-run config edit is undefined for Stage 2.

---

## 12. Review history — freeze review, business-purpose review, and one self-correction

This document went through a full review cycle before this revision. Recorded here for the same reason Stage 2's document records its own review history (§14–§17 of that document): so a future reader sees what was tried, rejected, and why, not just the final shape.

### 12.1 First freeze review — three blocking mechanism defects, all confirmed against real data

An independent review found three genuine architecture gaps, each independently re-verified against the real 2026-06 run before being accepted:

| # | Defect | Real-data confirmation | Resolution |
|---|---|---|---|
| 1 | `pack_size_ml`'s token-boundary rule (reused wholesale from Stage 2 §4.1) fails whenever the unit is glued directly to the multiplier | 948 of 1,714 real included rows (55.3%) — the *dominant* real pattern, not an edge case | §4.4: the rule is now stated as its own grammar, with multiplier-adjacency defined as a valid continuation rather than reusing a vocabulary-matching primitive built for a different problem |
| 2 | `container_type`'s "more than one keyword matches → `unknown`" rule fires on real, unambiguous SKUs | 36 of 1,714 real rows, spanning most major brands' standard case-pack naming convention | §4.4: replaced with a priority order (`can`/`pet_bottle`/`tetra_pack` over `bottle`/`btls`) — the collision concept is removed, not tie-broken |
| 3 | The suffix-strip rule only handled a trailing `(NNNN)` fragment | 2 confirmed real rows with the fragment before the volume, not trailing | §4.1: generalized to a position-independent strip of the row's own known `supplier_code` |

### 12.2 Business-purpose review — what's actually required, and what a semantic and contract-minimization pass found

A second review asked not "is the parser correct" but "does ValueBrew's catalog need this fact." This produced several findings, applied with different outcomes after being checked against the whole pipeline, not just Stage 3 in isolation:

- **`suffix_malformed` and `extraction_incomplete` were removed from the public schema.** No downstream consumer was found for either, in any of master §4.4/§4.5/§9 or this document's own validation section, across the entire review. `suffix_malformed` survives only as an aggregate rate in the run summary (§4.5, §7). `extraction_incomplete` was found to be fully redundant with `pack_size_ml IS NULL` — per this document's own field definition, that null state has exactly one cause, so a second column saying the same thing added no information, only a second value that would need to stay in sync with the first forever.
- **`normalized_name_key` was considered for the same treatment (becoming a shared function Stage 4 calls, rather than a persisted field) and rejected.** Every other stage boundary in this pipeline communicates through a versioned file artifact, never a direct code import; making this one field an exception would introduce a new, less visible kind of coupling (a cross-stage code dependency, invisible to anyone reading only the documented schemas) in exchange for avoiding a cost — schema migration on rule changes — this pipeline already has established tooling for (`normalization_rule_version`, mirroring `classification_config_version`). It remains a public field.
- **`pack_count` was, briefly and incorrectly, recommended for the same "make internal" treatment this document has since reversed.** The reasoning at the time only weighed `pack_count`'s validation use (master §9) and overlooked that master §4.4 *still* lists it as a required component of Stage 4's canonical-identity matching key — a requirement this document was never given authority to change. Making it internal would have silently broken an already-specified Stage 4 contract. It remains a public field. (Separately, and not acted on here: whether procurement case-size *should* be part of canonical identity at all was flagged as worth a future master-level decision — a real observation, but not this document's to resolve, and not a Stage 3 change.)

### 12.3 What this means for the schema

`normalized_rows.csv` carries seven columns, not the original ten: `run_month`, `item_code`, `display_name`, `normalized_name_key`, `pack_size_ml`, `pack_count`, `container_type`, `normalization_rule_version`. (That's eight names — `pack_count` was never actually removed, per §12.2's correction; the net reduction is the two genuinely unjustified fields, `suffix_malformed` and `extraction_incomplete`.)

---

Stage 3 architecture has been through one full review cycle (§12) with every finding resolved, reversed with reasons where a proposed fix didn't hold up, or explicitly carried forward as a flagged-but-out-of-scope observation for a later stage. Implementation followed, was reviewed for defects independently of the architecture, and was run against real 2026-06 data; the output was accepted after an independent, data-only acceptance review. **Stage 3 — architecture and implementation both — is frozen and stable for Stage 4 to build on.**
