# ValueBrew — KSBCL Stage 2 (Beer Identification) Architecture

### The complete design for Stage 2 of the KSBCL beer pricing pipeline. Governed by [`KSBCL-Beer-Pricing-Pipeline-Architecture.md`](KSBCL-Beer-Pricing-Pipeline-Architecture.md) (the overall pipeline design, §2 and §6 in particular) and built directly on top of [`KSBCL-Stage-1-Extraction-Contract.md`](KSBCL-Stage-1-Extraction-Contract.md) (the frozen contract Stage 2 consumes). Architecture only — nothing in this document has been implemented. Where this document goes beyond, refines, or challenges the master architecture's brief Stage 2 sketch, that is called out explicitly, with the evidence behind it, per this design phase's own brief.

**Status: Stage 2 Architecture is frozen (§17). One Product Decision Required remains open (§17) and does not block implementation start — it gates only the specific rule governing multi-word vocabulary matching across alternate punctuation. No code exists for Stage 2.**

---

## 0. Sources consulted

Before drafting anything, the following were read in full: the master pipeline architecture (all 12 sections), the Stage 1 contract (all 12 sections), the app's `Style` and `Benchmark` domain models (`lib/catalog/domain/style.dart`, `benchmark.dart`), the Beer Knowledge Model (`docs/architecture/current/05-Beer-Knowledge-Model.md`) and the Architectural Decisions Record, and — unexpectedly relevant — an existing research corpus at `docs/research/enterprise_catalog_research/` documenting real Karnataka beer brand/brewery/supplier-code data, real observed misspellings and abbreviations from Karnataka retail sources, and a proposed enterprise-scale catalog schema. That corpus was **not produced by this pipeline and does not govern it** — it is a separate research effort for a much larger future catalog system — but it supplies real evidence used throughout this document, always clearly labeled as coming from a source other than the actual KSBCL PDF. Two dedicated design passes (this document's author, and one parallel background agent focused specifically on adversarially stress-testing edge cases, validation, and error handling) fed into the draft below, followed by an independent adversarial review (§14).

---

## 1. Purpose

**Stage 2 owns exactly one decision, made once per row, for every row in Stage 1's `structured_rows.csv`:** is this row beer, and how confident is that decision. Concretely, Stage 2:

- Reads every row Stage 1 accepted — all alcohol categories, not beer-filtered, per the Stage 1 contract's explicit guarantee that no category filtering has happened yet.
- Classifies each row via a deterministic, config-driven, fully auditable heuristic (§4) — never a machine-learning model, never a human-in-the-loop-per-row process.
- Assigns a confidence tier (High / Medium / Low) to every row that matched *anything at all*; rows matching nothing get no per-row record at all, by design (§4.6).
- Detects Duty-Free channel membership (`is_duty_free`) — a separate, independent text-pattern check, not entangled with the beer/not-beer decision itself.
- Produces a complete, machine-parseable audit trail of every classification decision that reached candidate status, plus a persistent cross-month record of what's already been seen and what's still awaiting human review.
- Owns the external, versioned configuration (`beer_classification.yaml`) that holds the style-keyword, brand-name, and exclusion-term vocabularies — never hardcoded in code, per the master architecture's §6.3.

**Stage 2 explicitly does NOT own:**

- **Name normalization** — casing, `×`/`x` unification, redundant supplier-code-suffix stripping, or extracting `pack_size_ml`/`pack_count`/`container_type` into structured fields. That is Stage 3's job in full. Stage 2 does its own matching directly against `item_name_raw`, with only a minimal, local case/whitespace fold applied purely for matching purposes (§4.1) — never a substitute for Stage 3's `normalized_name_key`.
- **Canonical product identity** — whether two different Item Codes are the same real-world product. Stage 4's job entirely; Stage 2 has no concept of "the same beer under a different code."
- **Style or brand as catalog entities.** This is the single most important boundary in this document and is restated explicitly in §5 and §6: Stage 2's "style detection" and "brand detection" are **classification signals**, not taxonomy assignment. Stage 2 never writes a `style_id` matching the app's `Style` domain model, never assigns a canonical brand identity, and never claims a beer "is a Witbier" as a stored fact — it only records *which keyword or brand-name string caused a row to be classified as beer*, for audit. A genuine, structured Style/Brand/Brewery taxonomy — the kind sketched in the research corpus's `brand`/`brewery`/`style` tables — is explicitly Future Enrichment territory per the master architecture's §10, sourced from outside KSBCL (KSBCL's PDF never states style, ABV, or brand ownership as structured facts; only free-text product names).
- **Pricing, price history, or "live" status** — Stage 5's job, untouched here.
- **The decision to exclude Duty-Free rows from the retail catalogue** — already made at the master-architecture level (§12.2: DF rows excluded from `beer_master.csv`, preserved in `beer_master_duty_free.csv`). Stage 2 only detects and tags the fact; it never acts on it.
- **Anything about barcodes, ABV, calories, imagery, or descriptions** — never touched anywhere in this pipeline's Phase 1 scope, and Stage 2 reserves nothing for them (unlike Stage 5's `gtin`/`gtin_confidence` placeholder columns, which exist for a documented reason — Stage 2 has no analogous need, since nothing about beer identification benefits from a reserved-but-empty enrichment field).

---

## 2. Inputs

Stage 2 takes exactly two inputs: Stage 1's output for one run, and its own configuration.

### 2.1 `structured_rows.csv` (from Stage 1, frozen contract)

Every guarantee in the Stage 1 contract's §4 ("Acceptance guarantees") is inherited directly and may be relied upon without re-verification:

- Every row's `item_code` matches `^\d{8,11}$` and is unique within the file.
- `item_name_raw` is present, non-empty, and byte-exact from the source PDF — no cleanup of any kind has happened.
- `supplier_name` / `supplier_code` reflect a real, correctly-attributed supplier section (Stage 1's own hardening pass fixed the one known bug here — trailing location text after a supplier's code — so this is now reliable).
- All four price fields and `effective_date` are well-formed, but **carry no signal whatsoever about category** — Stage 2 must not attempt to infer beer-ness from price ranges (a ₹95 case price says nothing about whether something is beer versus a cheap spirit).
- **Every category is present, unfiltered.** ~33,867 rows/month across beer, wine, rum, whisky, vodka, brandy, gin, and RTDs, per the master architecture's own confirmed count.
- `item_code`'s leading digits reflect the *supplier's* ordinal position in the source file, not product category — the master architecture's own documented trap (§1), restated here because it is exactly the kind of shortcut a Stage 2 implementer would be tempted to reach for.

### 2.2 `beer_classification.yaml` (Stage 2's own configuration)

Exactly three top-level keys, matching the master architecture's §6.3 "three lists" precisely, no more and no fewer — each a plain YAML sequence of plain strings, nothing nested:

```yaml
style_keywords:
  - beer
  - lager
  - witbier
  - ...

brand_names:
  - Kingfisher
  - Hoegaarden
  - ...

exclusion_terms:
  - whisky
  - rum
  - ...
```

Entries are authored in natural, human-readable casing and spacing — the loader is responsible for folding both the config's own strings and `item_name_raw` through the identical function before comparison (§4.1), never the other way around. No other keys, no nested structure, no per-entry metadata (weight, alias-kind, etc.) — §4.3 explains why a flat list, not an alias-mapping structure, is the deliberate design here. This file is versioned in git like code, but edited by whoever curates the vocabulary, not necessarily by whoever writes Stage 2's implementation — consistent with the master architecture's §6.3 framing of this as a "permanent abstraction... not a stopgap."

### 2.3 Assumptions

- Stage 2 runs only against a `structured_rows.csv` that exists because Stage 1's run for that `run_month` **succeeded**. Per the Stage 1 contract's atomicity guarantee, a failed Stage 1 run produces no `structured_rows.csv` at all — so "Stage 1 failed, run Stage 2 anyway against whatever's there" is not a real scenario to design for; it's a precondition failure.
- `beer_classification.yaml` is valid and loadable, with at least one entry in `style_keywords` (see §2.4).

### 2.4 Unsupported inputs

- **A missing, malformed, or empty `beer_classification.yaml`** aborts the run outright. Running with an empty or partially-loaded ruleset would silently classify every row as non-beer, with the classifier itself never producing a single error — the single most dangerous failure mode a config-driven system like this can have, because nothing about the output would look obviously wrong (a `classification_audit.csv` with zero rows is not intrinsically suspicious the way a `structured_rows.csv` with zero rows is, since Stage 2's "no match" case is *already* silent by design — see §4.6). This is exactly why §9 proposes a hard structural assert (High-tier count must be non-zero) as a release gate, not just a config-loading check.
- **A `structured_rows.csv` from a different pipeline version** (e.g., missing a column Stage 2 expects) is treated the same way Stage 1 treats an unexpected header: a hard, loud failure, never a best-effort partial read.
- **Attempting to run Stage 2 without a corresponding successful Stage 1 run for that `run_month`** — not supported; there is no independent "Stage 2 standalone" entry point that accepts arbitrary CSV input.

---

## 3. Outputs

Five artifacts, three per-run and two persistent (cross-run). All are new interfaces this document is defining for the first time — the master architecture's §4.2 sketched a five-column `classification_audit.csv`; this document hardens and extends that sketch the same way the Stage 1 hardening pass hardened `RejectedRow`, for the same reason: **once Stage 3 starts, these become public interfaces**, and an ad-hoc or under-specified schema discovered to be wrong after Stage 3 depends on it is expensive to fix. Every deviation from the master architecture's original sketch is justified below, not silent.

### 3.1 `pricing_data/runs/<run_month>/classification_audit.csv` — the primary output

One row per **candidate** — every row from `structured_rows.csv` that matched a style keyword, a brand name, or the exclusion guard, or was escalated by supplier corroboration (§4.5). Rows matching nothing at all get no entry, by design (§4.6) — this file is not a copy of `structured_rows.csv` with a classification column bolted on; it is deliberately much smaller (order of 1,400 rows/month, not 33,867).

| Column | Meaning |
|---|---|
| `run_month` | Consistent with every other per-run artifact in this pipeline. |
| `item_code` | Join key back to `structured_rows.csv`. |
| `confidence_tier` | `high` \| `medium` \| `low`. Never `none` — a `none`-tier row has no row here at all (§4.6). |
| `included` | `true` for high/medium, `false` for low. A pure function of `confidence_tier`, stored anyway for a query-time convenience the same way `Sku.valueVerdict` is stored alongside `valueScore` in the app's own domain model rather than recomputed by every consumer. |
| `matched_signal_type` | `style_keyword` \| `brand_name` \| `supplier_corroboration_only`. The last value is new — see §4.5's None→Low escalation. |
| `matched_term` | The literal string that matched (e.g. `"witbier"`, `"Kingfisher"`). Null only for `supplier_corroboration_only` rows, where by definition no keyword/brand string matched at all. Where more than one style keyword matches, this holds the one earliest in `style_keywords`' declaration order in `beer_classification.yaml` — see §5 for why declaration order is the deterministic tie-break. |
| `exclusion_term_matched` | Null unless a brand-only match was demoted by the exclusion guard (§4.2 rule 3) — the literal spirit-family term that fired (e.g. `"whisky"`). Never populated for a style-keyword match — that match is never vetoed by anything, without exception (§4.2 rule 1). |
| `supplier_known_beer_seller` | Whether this row's supplier is already in `classification_known_terms.csv` as a confirmed beer-carrying supplier. **Not annotation-only** — see §4.5's revised scope: this field now has two distinct, disclosed gating roles (demoting a brand-only match, and escalating a no-match row), in addition to remaining a corroborating annotation on High-tier rows where it has no effect on the outcome. |
| `is_duty_free` | Detected from `item_name_raw` per the exact rule in §4.8, independent of everything else on this row. |
| `classification_config_version` | **Computed precisely, not left to "version/hash" ambiguity (a freeze review found the earlier "mirrors the `*_used` fields" framing didn't actually resolve anything — Stage 1's `*_used` fields are echoed CLI scalars, not file hashes, so there was nothing to mirror).** The value is the first 12 hex characters of the SHA-256 digest of `beer_classification.yaml`'s raw file bytes, computed fresh at the start of every run, before any parsing. Chosen over a git commit hash (adds a runtime dependency on git being available and the file being committed — Stage 1 has no equivalent shell-out dependency anywhere) or a hand-maintained `version:` key (relies on a human remembering to bump it, and would add a fourth top-level key beyond §2.2's exactly-three). A content hash needs no human action, no external tool, and is trivially reproducible by anyone re-hashing the same file bytes at any point in its git history — any change to the file, including a comment or whitespace edit, correctly produces a new version, since the audit question this field answers is "what exact bytes produced this run," not "did the meaning change." |

### 3.2 `pricing_data/runs/<run_month>/classification_new_entities.csv` — per-run novelty diff

One row per style keyword, brand name, or supplier code that matched **this run** but does not yet appear in the persistent ledger (§3.4). Columns: `entity_type` (`style_keyword` \| `brand_name` \| `supplier_code`), `value`, `sample_item_code`, `sample_item_name_raw`. This is the concrete artifact fulfilling the master architecture's §6.4 "new-entity diff" requirement — deliberately a single unified file across all three entity types rather than three near-duplicate files.

### 3.3 `pricing_data/runs/<run_month>/classification_run_summary.json` — aggregate report

A **separate file from Stage 1's `run_summary.json`**, not an added key inside it — see §3.5 for why. Contains: total candidate rows, counts by tier, `matched_signal_type` breakdown, exclusion-guard fire count, unfamiliar-supplier demotion count, None→Low escalation count, `is_duty_free` count and ratio, `is_bootstrap_run` (§3.4), and `classification_config_version`. Written atomically, all-or-nothing, exactly like every other artifact in this pipeline (Stage 1 contract §7) — a failed Stage 2 run leaves a `status: "failed"` summary with whatever partial counts accumulated, never a half-written `classification_audit.csv`.

### 3.4 `pricing_data/classification_known_terms.csv` — persistent, cross-run

One row per (`entity_type`, `value`) ever matched in any run, ever. Append-mostly: a genuinely new term gets a new row; a term seen again just updates `last_seen_run_month` and increments `times_seen`. This is the baseline `classification_new_entities.csv` is diffed against — without a persistent record of "what's already known," the word "new" has no meaning across months. This mirrors `item_code_canonical_map.csv`'s established pattern from the master architecture (a permanent, append-mostly ledger living at `pricing_data/` root, not inside any single run's folder) — the same structural pattern applied to a different kind of fact.

| Column | Meaning |
|---|---|
| `entity_type` | `style_keyword` \| `brand_name` \| `supplier_code` |
| `value` | The literal string/code. |
| `first_seen_run_month` | The `run_month` of the chronologically earliest run that has ever recorded this entity — never the earliest-*processed*, the earliest by calendar order. Set once on the row's creation; may still be lowered later, but only by the older-month-rerun rule below, never by ordinary newer-month processing. |
| `last_seen_run_month` | The `run_month` of the chronologically latest run that has ever recorded this entity — never the most-recently-*processed*, the latest by calendar order. Updated only by the newer-month-run rule below; an out-of-order run for an older month never changes it. |
| `times_seen` | The count of distinct runs in which this entity was recorded at least once (never a count of row-occurrences within a run). Incremented by exactly 1 per qualifying run, per the rule below — see that rule's closing paragraph for the one case where this count is not guaranteed exact. |

**Execution model — a strict two-phase read-then-write, never interleaved (a freeze review found the original design silent on this, meaning classification could depend on PDF page order within a single run — a real determinism violation against §9's own primary correctness criterion).**

- **Phase 1 (classify):** every row in `structured_rows.csv` is classified using `classification_known_terms.csv` exactly as it existed the moment this run started — a single, frozen, read-only snapshot held constant for every row processed in this phase. Row 5,000's classification never depends on what row 100 in the same run happened to contribute; a supplier is either "familiar" as of the *end of the previous run*, or it isn't, for the entire duration of this run's classification. This alone makes `classification_audit.csv` fully independent of row-processing order — re-running the identical `structured_rows.csv` against the identical prior state always produces byte-identical output.
- **Phase 2 (record), only after Phase 1 completes for every row:** `classification_new_entities.csv` is computed by diffing this run's full result set against the Phase-1 snapshot, and `classification_known_terms.csv` is updated with everything newly or repeatedly seen. Nothing written in Phase 2 is ever visible to Phase 1's decisions, by construction — there is no code path in this design where it could be.

**Write trigger, stated explicitly (not left implicit):** every candidate row in `classification_audit.csv` — every tier, every `matched_signal_type` — contributes exactly one `supplier_code` entry (its own `supplier_code`, updated/incremented like any other entity) and, where applicable, one `style_keyword` or `brand_name` entry for its `matched_term`. A `supplier_corroboration_only` row contributes only the `supplier_code` entry, since no keyword/brand term matched.

**Update semantics — the exact rule for every possible relationship between this run's `run_month` and a given `(entity_type, value)` pair's currently stored state (a freeze review found the literal rule as originally stated — "just updates `last_seen_run_month` and increments `times_seen`" — both double-counted on a same-month rerun and could regress `last_seen_run_month` backward on an out-of-order run, with no guard for either).** For each `(entity_type, value)` pair encountered in this run's Phase 2, compare this run's `run_month` against the entity's existing `last_seen_run_month` (or treat the entity as new if no row exists yet):

1. **No existing row (first time this entity has ever been recorded):** insert a new row. Set `first_seen_run_month` and `last_seen_run_month` both to this run's `run_month`, and `times_seen` to 1.
2. **Same-month rerun** (this run's `run_month` equals the existing `last_seen_run_month`): this run has already been recorded for this entity — skip the update entirely, a true no-op. All three fields are left exactly as they were.
3. **Newer-month run** (this run's `run_month` is chronologically after the existing `last_seen_run_month`): set `last_seen_run_month` to this run's `run_month`, and increment `times_seen` by exactly 1. `first_seen_run_month` is left unchanged.
4. **Older-month rerun** (this run's `run_month` is chronologically before the existing `last_seen_run_month` — an out-of-order run for a past month, processed after a later month has already been recorded): `last_seen_run_month` is left unchanged — it always reflects the chronologically latest run ever recorded for this entity, so an out-of-order run can never regress it. `first_seen_run_month` is lowered to this run's `run_month` only if this run's `run_month` is chronologically before the currently stored value (the true first observation, once discovered, always wins, regardless of processing order); otherwise left unchanged. `times_seen` is incremented by exactly 1.

This makes a rerun of the *current* month a true no-op (matching the idempotency bar Stage 1's contract sets, §7), and makes `first_seen_run_month`/`last_seen_run_month` correct regardless of the order runs are processed in.

**Scope of the guarantee, stated honestly rather than overclaimed:** this rule does not guarantee `times_seen` stays exact if the *same older* month is reprocessed more than once — case 2's no-op check only catches a rerun of the entity's *current* most-recent month, because `first_seen_run_month`/`last_seen_run_month`/`times_seen` alone cannot record which specific historical months have already contributed, only the earliest and latest. This is not a gap introduced by this rule; it is a limit of this three-field schema, and matches rather than falls short of the idempotency bar Stage 1 itself sets — Stage 1's own guarantee (§7) is likewise scoped only to a rerun of the same, current run-month, never to arbitrary reruns of older months. A double-processed older month is corrected the same way this document already handles any other ledger inaccuracy (§10, open question 8/11): a human hand-edits the file directly, the same versioned-artifact correction path already established for `beer_classification.yaml` and this file generally — not a new gap requiring new tooling or schema.

**The first-ever run is not exempt from correctness, but its `classification_new_entities.csv` output needs a distinct label.** Before month 1, this file is empty, so *every* style keyword, brand name, and supplier that fires at all in the first run is indistinguishable from a genuinely novel term discovered in month 13 — and §9's review protocol calls for 100% human review of every "new" row. Mirroring the master architecture's own explicit handling of the identical class of problem for `beer_price_history.csv` (§7.4: `INITIAL_BACKFILL`, "deliberately distinct from `NEW_ITEM` so a reader never has to infer..."), the first-ever Stage 2 run's `classification_new_entities.csv` is tagged with a run-level `is_bootstrap_run: true` flag (in `classification_run_summary.json`, not a per-row field, since it's a property of the whole run, not of any individual term) — signaling to a reviewer that a large "new" count this one time is expected and structural, not a sign the classifier broke.

### 3.5 `pricing_data/classification_review_queue.csv` — persistent, cross-run

One row per distinct Low-tier classification case awaiting a human decision, never duplicated across months for the same unresolved case. Full design and lifecycle rules in §10.

### On not extending Stage 1's `run_summary.json` in place

The Stage 1 contract explicitly frames `run_summary.json` as "stable, additive-only" — new keys may be added over time. A tempting design (proposed by the edge-case stress-test pass during this document's drafting) is for Stage 2 to add a `"stage2"` block directly into that same file. **This document rejects that design.** Stage 1's contract also guarantees that file is written atomically, all-or-nothing, as part of *Stage 1's own* success — a Stage 2 process reopening and mutating an already-finalized artifact from a different stage, potentially on a different day, would either violate that atomicity guarantee or require inventing a new one for a shared file with two writers. A separate `classification_run_summary.json`, following exactly the same atomic-write and partial-summary-on-failure pattern Stage 1 already established, keeps every stage's own success/failure story self-contained and independently reconstructable — consistent with the master architecture's own repeated principle that "every stage produces an audit artifact... reconstructable without re-reading" anything upstream, including another stage's summary file.

---

## 4. Beer identification strategy

### 4.1 The matching surface: `item_name_raw`, with a local fold, not `normalized_name_key`

Stage 2 runs *before* Stage 3 in the fixed pipeline order. It cannot depend on Stage 3's `normalized_name_key` — that field does not exist yet when Stage 2 runs. Stage 2 therefore applies its own **minimal, local** fold purely for matching: Unicode case-fold, collapse of runs of whitespace, and unification of the `×`/`x`/`X` case-multiplier symbol (the same specific normalization the master architecture already documents as necessary, §5.1) — nothing more. This is deliberately a small subset of Stage 3's eventual, fuller normalization, and it is **permanent**, not a stopgap: it exists because of the fixed stage ordering, not because Stage 3 is unbuilt, and it stays even after Stage 3 exists, since Stage 2 must never take a dependency on a later stage's output.

**Matching semantics, stated precisely (a freeze review found this genuinely unspecified for the primary layers — only a short-abbreviation special case existed):** every comparison against `style_keywords`, `brand_names`, and `exclusion_terms` is **word-boundary-anchored**, never a bare substring check, for every entry regardless of length. A term matches only when it appears in the folded `item_name_raw` as a complete token (or, for multi-word entries like `"strong beer"`, a complete token sequence) — never as a substring inside a longer word. This is not a stricter rule reserved for short tokens (§4.7's earlier phrasing implied that); it is the *only* matching rule Stage 2 has, applied uniformly. The reasoning is concrete, not theoretical: this pipeline's own exclusion vocabulary includes `gin`, a 3-letter spirit term that would silently false-positive inside unrelated words under substring matching, and `ale` — a listed style keyword — would do the same inside "sale" or "male." Word-boundary anchoring is what makes the vocabulary-curation discipline in §5 ("style keywords must be beer-specific") actually sufficient in practice, not just in principle.

**Token boundary, defined precisely and exhaustively (a freeze review found this genuinely unspecified along one dimension: whether a transition between letters and digits counts as a boundary):** a token boundary exists at every point where the folded string moves from one character class to a different one — Unicode letter, Unicode digit, or any other character (whitespace, punctuation, symbols) each counting as its own class — and at the start and end of the string. Two adjacent letters are never a boundary; two adjacent digits are never a boundary; a letter immediately followed by a digit, or a digit immediately followed by a letter, is always a boundary, exactly as a letter immediately followed by whitespace or punctuation already is. This is the complete, closed definition of "token" and "word-boundary-anchored" used everywhere above and applies uniformly to every vocabulary matched this way, present or future — it governs by rule, not by per-vocabulary restatement.

**The config file's own entries are folded through the identical function before comparison, never assumed pre-folded by the person editing the file.** A curator writes `beer_classification.yaml` in natural, readable casing (`"Kingfisher"`, `"Beer"`) for human legibility; Stage 2 applies the same case-fold/whitespace-collapse to both sides of every comparison at match time. Requiring the file's author to pre-fold entries by hand would be exactly the kind of human-discipline-dependent step this pipeline's own design consistently avoids elsewhere (e.g., §6.3's config-as-code framing exists specifically so a curator edits meaning, not encoding).

### 4.2 The four-layer mechanism (from the master architecture, adopted and detailed here)

1. **Style-keyword allowlist (primary).** A flat list of unambiguous beer-style/category words — `beer`, `lager`, `strong beer`, `witbier`, `wheat beer`, `stout beer`, `ale`, `ipa`/`indian pale ale`, `pilsner`, `porter`. A match here is **High** confidence and auto-included. This match is **never vetoed or demoted by anything in rules 3 or 4 below, without exception** — the master architecture's §6.1 point 3 states this absolutely ("never veto an unambiguous style-keyword match"), and no condition anywhere in this document overrides it. An earlier draft of this section carved out a narrow exception here for a compound-phrase guard (§8); that exception has been removed after a freeze review found it directly contradicted the master architecture's unqualified text, and Stage 2 has no standing authority to amend a frozen guarantee unilaterally. See §8 for the risk that exception was meant to address and why it is now handled as a documented, unmitigated, monitored item instead.
2. **Brand-name allowlist (secondary).** Fires only when no style keyword matched. A match is **Medium** confidence, provisionally included pending rules 3–4 below.
3. **Exclusion / demotion guard, applied only to a brand-only match.** A brand-only match is demoted to **Low** — excluded by default, queued for review (§10) — if **either** of two independent conditions holds, both drawn directly from the master architecture's own §6.2 ("Low: exclusion conflict, **or** match from an unfamiliar supplier"):
   - **Exclusion conflict**: the row's name also contains a spirit-family term (`whisky`, `rum`, `brandy`, `vodka`, `gin`, …).
   - **Unfamiliar supplier**: the row's `supplier_code` is not yet present in `classification_known_terms.csv` as a confirmed beer-carrying supplier, evaluated against the frozen, run-start snapshot of that file — never against anything written during this same run (§3.4's two-phase execution model).

   Earlier drafts of this document implemented only the first condition and treated supplier familiarity as strictly non-gating, citing the master architecture's separate, more general §6.1 framing ("supplier corroboration... annotation only, never a gate"). That was a real, undisclosed divergence from §6.2's own explicit text, caught in adversarial review (§14) — restoring the "unfamiliar supplier" condition here resolves it directly, by implementing the master architecture's more specific rule rather than only its more general one. See §4.5 for what this does and does not mean for "never a gate."
4. **Supplier corroboration.** The same `supplier_known_beer_seller` fact now has two distinct, disclosed roles (rule 3 above, and §4.5's no-match escalation below) — never a third role of granting automatic inclusion to a row that otherwise matched nothing, and never anything that touches a style-keyword match.

### 4.3 Why a flat string list, not an alias-mapping table

The research corpus's enterprise catalog design (§0) proposes a full `alias` table — surface form → canonical entity, with `alias_kind` (`abbreviation`/`misspelling`/`transliteration`/`marketing_alias`). That system solves a materially different problem: matching *many* messy, independently-formatted retailer sources against a canonical product database for *user-facing search*, where recall and typo-tolerance genuinely matter for UX. Stage 2 solves a narrower problem: classifying rows from *one*, consistently-formatted government source, where the only question is beer/not-beer. An abbreviated or misspelled brand form, if it needs to be recognized at all, is just another literal string added to the same flat `brand_names` list — "Kingfisher" and "KF" are two independent list entries, not an alias pair requiring resolution logic. This avoids building alias-expansion machinery Stage 2 has no confirmed need for (§4.7 explains why "confirmed need" matters here specifically).

### 4.4 Manufacturer / supplier knowledge

The research corpus's brand/supplier research (not KSBCL data, but independently verified Karnataka-specific evidence) gives concrete KSBCL Supplier Codes tied to major beer suppliers — United Breweries (0210, 0206), Carlsberg India (0205), AB InBev's contract bottler S P R Distilleries (0212), B9 Beverages/Bira 91 (0214), Woodpecker Distilleries (0213), Khoday Breweries (0204), and Brindco Enterprises for Guinness (0972), among others. This is a stronger, more specific seed for the "known beer-carrying suppliers" corroboration set than a generic placeholder — but it comes from a **separate research effort**, not from directly cross-referencing Stage 1's actual `supplier_code` output, and must be verified against real Stage 2 runs before being trusted as ground truth (flagged in §13). It is never a primary filter — restated for emphasis, since it is the single easiest rule in this document to accidentally violate under implementation pressure.

### 4.5 Supplier familiarity's two roles — and an honest accounting of what "never a gate" actually means now

This section originally argued that escalating a no-match row via supplier familiarity "does not violate supplier is never a gate for inclusion," on the theory that it only gates *visibility*, never *inclusion*. Adversarial review (§14) tested that claim to its actual conclusion and found it doesn't fully hold: a true silent `none`-tier row has no queue entry and therefore **no path to inclusion at all**, ever, by any means — while a row escalated to Low *can* later be marked `confirmed_beer` by a human. In the only sense that matters operationally, supplier familiarity is the sole gate on whether a row has *any* chance of eventual inclusion. Combined with rule 3's restored "unfamiliar supplier" demotion (§4.2), supplier familiarity now has two genuine, disclosed gating effects, not zero:

1. **Demotes a brand-only match from Medium to Low** when the supplier is unfamiliar (§4.2 rule 3) — directly implementing the master architecture's §6.2.
2. **Escalates a no-match row from silent `none` to a visible, reviewable Low** when the supplier is familiar (this section).

**What genuinely remains true, and is the actual invariant this design protects, stated precisely instead of loosely:** supplier familiarity **never, by itself, grants High or Medium confidence** — it cannot cause automatic inclusion. It only ever moves a row *toward* Low (more scrutiny) or *out of* silence (more visibility), never toward automatic inclusion, and it never touches a style-keyword match under any circumstance. This is a narrower, more honest claim than "never a gate," and it is the one actually being upheld throughout this design. The master architecture's own §6.1 phrasing ("annotation only, never a gate") is superseded here by its own more specific §6.2 rule, per §4.2's note — this document is not overriding the master architecture, it is implementing the more specific of two things the master architecture itself says, and disclosing that the two were previously in unresolved tension.

**Why this still matters, and why the escalation case specifically was proposed:** imported beers with no generic style word — "Corona Extra," "Stella Artois," "Peroni Nastro Azzurro" — are not on the example brand list (and, per §6's revised wording, their presence in actual KSBCL data is itself unconfirmed, not just their allowlist status). A row like this, from a supplier the pipeline already knows sells beer, would otherwise fall to `none` tier with **zero audit trail** — the master architecture's own §6.2 confirms a `none`-tier row gets no per-row flag "as the expected outcome for the ~32,000 non-beer rows," which is correct for genuine non-beer rows and a silent failure for a real beer row the allowlists haven't caught up to. Escalating such a row to `matched_signal_type = supplier_corroboration_only`, Low tier, closes that specific hole.

This is expected to fire rarely once the allowlist matures — its own fire count is one of the monthly self-check metrics in §9, specifically so a persistently high count (meaning the allowlist is chronically behind real data) is itself a visible signal, not a silent, permanent workaround.

### 4.6 False positives and false negatives are not symmetric risks

Restated from the master architecture because it is the single organizing principle behind every tier default in this document: a false inclusion pollutes the catalogue with a wrong item a user might try to buy; a false exclusion just delays a real item by one review cycle. Every default in this design — exclude-by-default on Low, silent-exclude on no-match, never-auto-promote-supplier-alone — follows directly from that asymmetry, not from caution for its own sake.

### 4.7 Deterministic vs. heuristic/fuzzy matching — considered and rejected as the primary mechanism

The governing brief for this design phase is explicit: prefer deterministic rules over AI, prefer reproducibility over convenience, prefer explicit auditability over automation. This was tested against real evidence, not just deferred to as instruction-following:

- **No confirmed instance exists, in the actual KSBCL PDF, of a brand name being misspelled or abbreviated.** The misspellings ("BUDWIESER," "CARSBERG," "HOGARDEN") and abbreviations ("KF," "UB") cited earlier come from a *different*, non-KSBCL retail corpus. They are real evidence of the *class* of risk in Karnataka beer retail data generally, not evidence that this specific government source exhibits it.
- Fuzzy/phonetic matching (Levenshtein distance, Double Metaphone) is itself still deterministic — it would not violate "prefer deterministic over AI" on those grounds alone. It is rejected here for a different reason: it adds real complexity (tunable distance thresholds, false-positive collision risk on short tokens, a second matching code path to audit) against a risk that is not yet confirmed to exist in this pipeline's actual input. Building it now would be solving a problem this pipeline hasn't been shown to have.
- **The adopted policy instead: confirm, then allowlist.** The first time a real misspelling or unrecognized abbreviation actually appears in a KSBCL run, the None→Low escalation net (§4.5) or an exclusion-guard Low flag surfaces it for human review. Once a human confirms it is a genuine, recurring variant of a real brand, it is added as a new literal string to `beer_classification.yaml` — and classifies deterministically and automatically from that point forward. This converts "one human catch, then permanent automation" into the stated policy, rather than pre-guessing which of dozens of theoretically-possible misspellings are worth encoding in advance.
- Short (≤3-character) tokens like "KF" or "UB" get a stricter *curation* bar before being added to the config at all: explicit human confirmation of a real, recurring instance is required, on top of (not instead of) the word-boundary matching now specified uniformly for every entry in §4.1 — a short token's false-positive collision risk from an over-eager addition is categorically worse than a full brand name's, even with word-boundary anchoring already in place. This is a policy constraint on what gets *added* to `beer_classification.yaml`, distinct from the matching mechanics themselves, which no longer vary by token length.

### 4.8 Duty-Free detection — the exact matching rule (a freeze review found "the `-DF` suffix" underspecified and, on the literal reading, wrong against real data)

`is_duty_free` (§1, §2.1, §3.1) is computed by a single, independent check, evaluated once per row, entirely separate from the beer/not-beer decision.

**Matching function: reuses §4.1's word-boundary-anchored matcher exactly, applied to the literal token `df`.** No new matching mechanism is introduced. The same case-folded, whitespace-collapsed comparison already specified for `style_keywords`, `brand_names`, and `exclusion_terms` is used here, searching for the two-letter token `df` anywhere in the folded `item_name_raw`, bounded on each side by a non-alphanumeric character (hyphen or whitespace) or the start/end of the string — never as a substring inside a longer alphanumeric run.

**Not anchored to end-of-string, and not anchored to immediately-preceding the volume field.** Confirmed directly against the real 2026-06 run: the `DF` marker's position relative to the rest of the name is not fixed. It precedes the volume field in most rows (`-DF 750MLx12Btls`), but in others it precedes a parenthetical supplier-code fragment that itself precedes the volume (`-Df (0336) 750 Ml`), or is followed by extra descriptor text before the volume (`-DF - F/W 750MLx12Btls`). An end-of-string or before-volume anchor would silently miss all of these. The only invariant confirmed across every real variant is that `df` appears as an isolated token somewhere in the name.

**Must match** (confirmed real rows, 2026-06 run): `Corona Extra Beer -Df 330ml`, `Brewdog Lost Lager DF 330ML X 24Btls.`, `Antinori-DF-750MLx6Btls.`, `Absolut Vodka Df- 750 Ml`, `Wincarnis Original Tonic Wine-DF - F/W 750MLx12Btls`.

**Must not match**: `df` occurring as part of a longer alphanumeric run with no boundary on either side — e.g. a hypothetical `Sandford Reserve 750ML` (illustrative; no real KSBCL row of this exact shape is confirmed, the same way §4.1 uses `gin`/`ale` substring-collision risk illustratively, not as a confirmed-collision citation).

**Known, disclosed limitation — not mechanism-mitigated, the same treatment §8 already gives the Root Beer/Ginger Beer gap:** a small number of real rows glue `DF` directly onto the preceding word with no separator at all — confirmed: `Chateau Latourdf 750ml`, `Pouilly Fuissedf 750ml`, `Sparkling Winedf 750 Ml`, `Res Pinot Noirdf 750ml`, and others (19 of 33,852 rows in the sampled run, all wine items on inspection — none beer). Word-boundary anchoring, by the identical logic that makes it correct everywhere else in this document, does not catch these — there is no boundary before `df` in `Latourdf`. Building a fused-token exception for 19 confirmed rows (0.06% of the file), none of them beer, would be exactly the kind of unconfirmed-generalization mechanism §4.7 already declines to build; the correct action is disclosure, not new matching machinery. If a beer row with this exact fused pattern is ever confirmed, that becomes new evidence for revisiting this section — not a hypothetical to guard against now. The `is_duty_free` ratio check already specified in §9 (against the ~10% historical baseline) is the mechanism that would surface a shift here empirically, the same role it plays for every other classification metric in this document.

---

## 5. Style detection

**Restated up front, because this section's title invites the wrong reading: this is not style taxonomy assignment.** Stage 2 does not populate anything resembling the app's `Style` domain model (`id`, `name`, `description` — a first-class catalog entity with its own benchmark distribution). Style-keyword matching exists for exactly one purpose: to answer "is this row beer" with high confidence, using domain vocabulary (`lager`, `stout`, `witbier`, …) that is essentially unambiguous to the beer category. Nothing about *which* style keyword matched is treated as a claim about the beer's actual style for any downstream catalog purpose — that fact is recorded (`matched_term`) purely for audit, exactly the way `matched_on` was already scoped in the master architecture's own sketch.

**A concrete, evidence-based constraint on the vocabulary itself:** style keywords must be selected for specificity to the beer category, never for generic strength/quality language that appears across every liquor category. "Strong," "Premium," "Deluxe," "Five Star" appear constantly in whisky and rum names too (`Khodays Five Star Whisky`, `Democrat Extra Spl Whisky`) — including any of these as a bare style keyword would produce mass false positives across ~32,000 non-beer rows. This is stated as a hard design constraint, not a suggestion: `style_keywords` must contain only terms that are, on their own, beer-specific (`beer`, `lager`, `ale`, `stout`, `witbier`, `pilsner`, `ipa`, `porter` — all satisfy this; generic intensity/quality adjectives never do).

**How ambiguity is handled:** a row can legitimately match more than one style keyword (`Simba Roar Series Wild Premium Strong Beer` plausibly contains both `beer` and, if ever added, `strong beer` as a compound term). Consistent with the Stage 1 hardening precedent (first-failing-rule-wins for `RejectedRow`), Stage 2 records a single, decisive term — not because the others don't matter, but because a classification decision should be traceable to one specific, deterministic cause, not an ambiguous set. **The tie-break, stated explicitly and precisely (flagged in adversarial review, §14, as previously asserted but never defined):** `style_keywords` in `beer_classification.yaml` is an ordered list, not a set; the term recorded in `matched_term` is whichever matching keyword appears **earliest in that list's declaration order**. This makes the rule auditable by simply reading the config file top to bottom, and makes it genuinely deterministic — the alternative candidates considered and rejected were leftmost-in-string-position (fragile: depends on exact wording of a name, not on the vocabulary's own structure) and longest-match (adds a second dimension to reason about for no clear benefit at this vocabulary size). The same rule applies identically to `brand_names`.

**How unknown styles behave:** a style word not yet in the allowlist (a niche import style, e.g. "Kellerbier" or "Saison") behaves exactly like any other unrecognized term — the row falls through to brand-matching, then the None→Low supplier escalation, then silent exclusion if none of those fire. This is a real, expected, and only partially-closed gap: if the row's brand *also* isn't recognized and its supplier *isn't yet* a known beer seller, the row disappears with zero signal anywhere. §9's periodic random sample of true-`none` rows exists specifically because this failure mode cannot be closed by any allowlist-based mechanism alone — it can only be bounded and monitored.

---

## 6. Brand detection

**Architecture only, as requested — restating the "not taxonomy" boundary once more since it applies here with equal force:** a brand-name match never creates or references a `brand_id`, never asserts a brewery relationship, and never claims ownership/parent-company facts (the kind of detail the research corpus's `company`/`brand`/`brewery` tables model for a much later system). It is a flat string match against `brand_names`, recorded for audit as `matched_term`.

**Seeding.** The initial `brand_names` list should be seeded from brands *already confirmed against actual KSBCL data* during the master architecture's own ground-truth inspection — with specific page/item-code evidence behind each: Kingfisher, Royal Challenge, Haywards 5000, Knock Out, Budweiser, Hoegaarden, Simba, Tuborg, Carlsberg, Witlinger, Bira 91.

**A separate, explicitly lower-confidence tier: brands worth adding despite no direct KSBCL citation.** Corona, Stella Artois, Guinness, and Peroni are well-known international beer brands and plausible candidates given India's import market — but unlike the eleven brands above, **none of them is backed by a specific page or item-code citation from direct inspection of the actual KSBCL PDF**, only by general market knowledge and (for Guinness) the separate research corpus's claim of a KSBCL supplier registration (§0) that has not itself been cross-checked against Stage 1's real output. Adversarial review (§14) caught an earlier draft of this document calling these four "confirmed" — language that misapplied this document's own confirmed/unconfirmed discipline, the same discipline applied correctly to the soda/water exclusion terms in §8. Corrected framing: these four are reasonable, low-cost allowlist additions precisely *because* being wrong about them costs nothing (an unlisted-but-real brand just falls through to the None→Low escalation net, §4.5, instead of matching directly) — not because their presence in KSBCL data is established fact. Whether any of the four actually appears in the real file is exactly the kind of thing `classification_new_entities.csv` and the review queue will settle empirically once Stage 2 runs (§13, open question).

**Interaction with the exclusion guard.** A brand-only match co-occurring with a spirit-family term demotes to Low (§4.2, rule 3) — defensively guarding against the theoretical case of a shared brand name spanning both a beer and a spirit line (not confirmed to occur in KSBCL data, but cheap to guard against and consistent with the asymmetric-risk principle in §4.6).

**What brand detection is not responsible for resolving:** whether "Bira 91" and "Original Bira 91" (both real, confirmed KSBCL name variants for the same brand family) are the *same brand* is irrelevant to Stage 2 — both contain "Beer" or a style word and classify identically via the style layer regardless of the "Original" prefix. Brand-family consolidation, if it's ever needed as a real entity, is Stage 4/Future-Enrichment territory, not something Stage 2's flat brand list needs to model.

---

## 7. Pack normalization

**Stage 2 does not parse, extract, or normalize pack information in any form.** `pack_size_ml`, `pack_count`, and `container_type` are explicitly Stage 3's owned fields (master architecture §4.3); Stage 2 never produces them, references them, or depends on them for its own classification decision.

The only place pack-related text could plausibly intersect Stage 2's actual job is narrow: certain pack-related qualifiers (`gift pack`, `combo`, `with glass`) are relevant to the beer/not-beer decision **not at all** — a beer gift pack is still beer, and classifies via the ordinary style/brand layers exactly like a standalone bottle. An earlier draft of this document proposed a `combo_pack_suspected` annotation field on that basis, flagging such rows for an unnamed future pricing consumer. Adversarial review (§14) correctly identified this as exactly the kind of invented-ahead-of-need field the master architecture's own §10.5 warns against — no consumer in Stage 4 or Stage 5's design actually reads such a flag, and the underlying pattern (beer gift packs in KSBCL data at all) is itself unconfirmed (§8). That field has been removed from §3.1's schema; it remains recorded only as an open question (§13) should a real consumer and a real, confirmed need ever emerge. Anyone looking for real pack normalization in this pipeline should look at Stage 3's contract once it exists, not here.

---

## 8. Edge cases

The layered mechanism from §4 is evaluated here against specific, concrete cases — a fix is proposed only where the mechanism's own stated rules produce a wrong or silently-wrong outcome, never as a reflexive addition.

### Mixed / assorted packs
A name like `Kingfisher Assorted 6x330ml (3 Lager + 3 Strong)` still contains a style keyword. **Correct outcome, High confidence, no gap.** Pack *composition* is Stage 3's concern, not Stage 2's.

### Gift packs / combo packs
**Not confirmed present in KSBCL's actual beer rows** — the samples directly inspected were single-product listings only — but plausible by analogy to premium-spirits gift packs, a known real category-adjacent product type in Indian liquor retail. A beer-only gift set still carries its style keyword → High confidence, correctly included for the *classification* question, which is the only question Stage 2 answers. The real risk is a pricing one (the row's price may reflect glassware, not just liquid) — squarely out of Stage 2's scope, and (per §7's revised reasoning) not addressed with a speculative annotation field either, since no downstream stage currently names a need for one. If a real pricing-distortion problem from gift packs is later confirmed, the right fix is a field added to whichever stage actually consumes it, justified by that stage's own real requirement — not a flag added here in advance of one.

### Non-beer products (the ~32,000-row default case)
Wine, rum, whisky, vodka, brandy, gin, RTD rows correctly fall to `none` tier — silent exclusion, by design, confirmed correct behavior, not a gap in itself. The real risk this default creates is discussed under "marketing names" below, since the same silence that correctly hides 32,000 real non-beer rows also hides any real beer row the allowlists miss.

### Beer-adjacent non-alcoholic products, including the Root Beer / Ginger Beer risk — accepted and monitored, not mechanism-mitigated

Reasoned from first principles: KSBCL's price list is an **excise price list**, pricing goods subject to alcohol excise duty. A plain branded soda or packaged water has no excise basis for appearing in this document at all — and a real, independently-confirmed data-hygiene problem in the research corpus's *own* (non-KSBCL) catalog is exactly this: "Kingfisher Premium Packaged Drinking Water," "Kingfisher Strong Power Soda," "Tuborg Zero Soda," and "Carlsberg Elephant Strong Soda" all leaked into that retailer-sourced catalog as apparent beer rows. **This is confirmed real elsewhere, and directly informs the exclusion vocabulary here even though it hasn't been confirmed inside the actual KSBCL PDF**: `exclusion_terms` should include `soda`, `packaged drinking water`, and `drinking water` as a defensive measure, priced at near-zero cost, against a *brand-only* match on "Kingfisher" or "Tuborg" ever collateral-matching a non-alcoholic line extension. This exclusion is justified before confirmation inside KSBCL data because (a) the failure mode if it does occur is a false *positive* (worse than a false negative, per §4.6's asymmetry) and (b) the cost is effectively zero. This defense only ever applies to a *brand-only* match, per §4.2 rule 3 — it does not, and cannot, touch a style-keyword match.

**A structurally identical risk exists on the style-keyword path with no defense at all, and this document does not build one.** "Root Beer" and "Ginger Beer" are real, globally-recognized non-alcoholic beverage names that contain the standalone word `beer`. If either ever appears in KSBCL's actual data, it matches the style keyword `beer` directly — High confidence, auto-included, with no mechanism anywhere in this design able to intervene, since a style-keyword match is never vetoed by anything, without exception (§4.2 rule 1). A freeze review considered closing this with a narrow compound-phrase exception to that rule and found it would directly contradict the master architecture's unqualified §6.1 point 3 ("never veto an unambiguous style-keyword match") — a frozen guarantee Stage 2 has no authority to amend on its own. Unlike the soda/water case, **neither "Root Beer" nor "Ginger Beer" is confirmed to exist anywhere in the real KSBCL PDF**, and building a mechanism — one that requires bending a frozen rule — against a purely speculative risk would be inconsistent with this same document's own reasoning in §4.7 for *not* building fuzzy-matching against equally-unconfirmed misspelling risk.

**Accepted resolution:** this risk is left genuinely open and unmitigated by any Stage 2 mechanism, tracked the same way the 0.0%-ABV question below is — via the new-entity diff (§9) and the periodic random `none`/High-tier sample. If either term is ever confirmed to occur in real KSBCL data, the correct next step is an explicit, numbered decision at the master-architecture level (following the same process the master document's own §12 already uses), backed by that real evidence — not a silent local exception inside this document. See §13 for this tracked as an open item.

A 0.0%-ABV "beer" or flavored malt beverage is a genuinely open, unconfirmed question either way — not addressed with a special rule here; watched via the new-entity diff instead (§9).

### Malformed / garbled names reaching Stage 2
Stage 1 already rejects structurally broken rows before Stage 2 ever sees them. What remains is messy-but-valid text: inconsistent case-multiplier notation, heavy adjective stacking ("Knock Out High Punch Strong Beer") — both confirmed normal, neither a gap, since keyword matching is unaffected by surrounding text. A word-level text-splitting artifact inside `item_name_raw` itself (mirroring the confirmed price-cell tokenization bug) is **not confirmed to occur** — the known artifact is tied specifically to numeric cells via font-kerning — but the local whitespace-collapse fold in §4.1 provides cheap, structural insurance against it regardless.

### Imported beers — the sharpest confirmed gap in the *mechanism*, even though the specific brand list is not confirmed against KSBCL data
The gap here is structural and confirmed, independent of which specific brands are involved: any beer with no generic style word in its name, whose brand isn't yet on the allowlist, falls to silent `none` — a real beer disappears with zero trace. Corona, Stella Artois, Guinness, and Peroni are named as illustrative, plausible examples ("Corona Extra," "Stella Artois," "Peroni Nastro Azzurro" — none containing a style word) — per §6's corrected framing, their presence in actual KSBCL data is *not* itself confirmed, only their general real-world existence as import brands. **Two-part fix, scoped honestly:** add these four (and any others a human identifies) to the seed brand list as low-cost, unconfirmed-but-plausible entries (§6), and rely on the None→Low supplier-corroboration escalation (§4.5) as the structural backstop that catches whichever real imports aren't on the list yet — the backstop is the actual fix; the specific brand additions are a head start on it, not a substitute for it.

### Regional / informal spellings and short abbreviations
Addressed fully in §4.7 — confirm-then-allowlist policy, stricter bar for ≤3-character tokens, nothing pre-guessed.

### Marketing names with no style or category word at all
The general form of the Hoegaarden Witbier case, but for a brand *not yet* on the allowlist and with no style word either. Mechanically identical to the unlisted-import gap above and closed by the same mechanism — this is not a separate case requiring its own rule.

### Summary

The table below reflects the design **after** every fix described above and in §14 — i.e., what this document's final, adopted mechanism does, not the intermediate states individual fixes were reasoned against.

| Case | Outcome under the adopted design | Tier | Mechanism responsible |
|---|---|---|---|
| Mixed/assorted packs | Style keyword present | High | §4.2 rule 1 |
| Beer gift/combo pack | Style keyword present | High (classification only; pricing risk out of scope) | §4.2 rule 1 |
| Genuine non-beer category (~32,000 rows) | No match at all | None, silent | §4.6 (by design) |
| Branded non-alcoholic (soda/water) via brand match | Exclusion term present | Low | §4.2 rule 3 (exclusion, brand-only) |
| "Root Beer" / "Ginger Beer" via style-keyword match | No mechanism — style match is never vetoed | High, auto-included | **Known, accepted, unmitigated gap — §8, §13** |
| 0.0% ABV / malt beverage | Depends on wording; no special rule | Varies | Watched via new-entity diff (§9), not hardcoded |
| Case-notation / adjective stacking | Style keyword survives | High | §4.2 rule 1 |
| Name-text word-splitting (unconfirmed risk) | Defended structurally, not with a rule | N/A | Local whitespace fold, §4.1 |
| Brand match from an unfamiliar supplier | Demoted | Low | §4.2 rule 3 (unfamiliar-supplier condition) |
| Unlisted import / unlisted brand, no style word, familiar supplier | Escalated from silent to visible | Low | §4.5 (None→Low escalation) |
| Unlisted import / unlisted brand, no style word, unfamiliar supplier too | No signal at all | None, silent | Known, un-closed residual gap — §13 |
| Real KSBCL misspelling (unconfirmed which) | Same as unlisted-brand cases above | Low or None | §4.7 confirm-then-allowlist policy |
| Short abbreviation (KF/UB) | Same as unlisted-brand cases, plus a stricter bar before ever being added | Low or None | §4.7 |

Two rows in this table have **no mechanism at all** protecting them, and both are worth naming explicitly rather than leaving implicit. "Unlisted import/brand, no style word, unfamiliar supplier too" (a genuinely new brand, at a supplier the pipeline has never seen carry beer before, with a marketing name containing neither a style word nor an allowlisted brand string) is at least *bounded* — not eliminated — by the periodic random `none`-tier sample in §9, since that's where it lands. **"Root Beer / Ginger Beer via style-keyword match" is strictly worse: it has no bounding mechanism at all.** It lands in the High tier, not `none`, so the random `none`-tier sample never sees it; its `matched_term` is `"beer"` — already a known entity from month 1 — so `classification_new_entities.csv` never flags it either; and §9's human-review sampling list has no High-tier sampling category (only a periodic *Medium*-tier spot-check). This is stated plainly rather than glossed over: as designed, this specific risk would only ever surface through some process entirely outside this document (a human happening to notice it while using the app, or a future master-architecture-level audit) — not through anything Stage 2 itself does.

---

## 9. Validation

**What "correctness" can and cannot mean.** There is no ground-truth "this row is definitely beer" label anywhere — not from KSBCL, not from any corpus confirmed to align row-for-row with the real file. Correctness cannot mean an accuracy percentage against a labeled set; proposing one would fabricate a number nobody could check. It can mean:

1. **Determinism** — identical input classifies identically every time, for a fixed config version **and an unchanged `classification_known_terms.csv`/`classification_review_queue.csv` prior state (§3.4)**. Directly testable by re-running the same month twice against that same prior state and diffing the output, exactly as Stage 1's idempotency was verified — **not a claim that two sequential real invocations of a not-yet-converged month are identical to each other, since the persistent ledgers are themselves an output of the first invocation (§3) and, by design, a legitimate input to the second.**
2. **Explainability** — every included or flagged row carries a literal, checkable `matched_term`.
3. **Non-regression** — a confirmed-correct classification stays correct unless the config is deliberately edited (traceable via `classification_config_version`).
4. **A bounded, honest recall proxy** — never a recall *guarantee*, but an empirical, trending signal (the random `none`-tier sample below).

### Monthly self-check additions (beyond aggregate tier counts, new-entity diff, supplier diff already specified at the master-architecture level)

- **Tier-distribution ratio band** — % High/Medium/Low tracked against a rolling median of recent runs, mirroring the master architecture's own §9 row-count band pattern.
- **Total classified-beer count band** — tracked the same way, against the confirmed baseline (~1,389/month).
- **Style : brand match ratio** — a sudden drop is as likely to signal upstream text-extraction loss as anything about Stage 2 itself; a cheap early-warning wire across the Stage 1/2 boundary.
- **Exclusion-guard fire rate** — a spike means either a genuine new spirit SKU sharing a brand word, or an over-broad brand entry.
- **None→Low escalation count** — should trend toward zero as the allowlist matures; a persistently high count means the allowlist is chronically behind, not that the net is failing.
- **`is_duty_free` ratio** — checked against the confirmed ~10% baseline (138/1,389) at Stage 2's own output, before the pipeline-wide check downstream.
- **Hard structural assert: High-tier count must be non-zero.** A real month always contains hundreds of plain "X Beer" rows; zero means the config failed to load or the allowlist is empty — a Stage 2 bug, not a real data condition. This aborts the run, mirroring the master architecture's own §8.2 posture on structural failures — the direct answer to §2.4's unsupported-input case.

### Human review sampling — stratified, not flat-random

A flat random sample across 33,867 rows wastes reviewer time confirming the obvious. Instead:

1. **100% of Low-tier rows** — the review queue's entire content by construction.
2. **100% of `classification_new_entities.csv` items** — highest information value per row reviewed.
3. **100% of None→Low escalation rows** — the safety net in §4.5 only has value if it's actually reviewed, not just logged.
4. **A small, fixed random sample of true-`none` rows every month** (proposed starting point: 25–50, tuned after real run history per the same honest posture the master architecture takes on its own unset thresholds, §12.4) — the only mechanism that checks whether real beer is silently vanishing into the unflagged majority.
5. **A periodic (quarterly, not monthly) sample of already-included Medium-tier rows** — catching the opposite failure, an over-firing brand entry.

### Acceptance criteria — checkable, not statistical

- Zero Low-tier rows past a documented staleness SLA (proposed: 2 monthly cycles) without either a human decision or a logged escalation note.
- A `classification_new_entities.csv` item must not recur as "new" two months running — recurrence signals the confirm-then-allowlist policy didn't actually take effect, a bug, not a data fact.
- Tier-distribution and total-count bands within historical range, plus the High-tier-floor assert, as preconditions for promoting a run's output from candidate to accepted — mirroring the promotion gate the master architecture already applies pipeline-wide.
- The monthly random `none`-tier sample finding a missed beer row is not a failed run — it is the mechanism working exactly as designed: the miss gets triaged into the allowlist, and logged as a real data point toward an empirical (never target-set) sense of the true false-negative rate over time.

---

## 10. Error handling

### The persistent review queue

A `none`-tier row is already fully handled (§4.6/§4.2) — excluded, no gate, no per-row record, by deliberate design for the ~32,000-row default case. The real gap is that `classification_audit.csv` is a **per-run** artifact with no memory across months — it cannot answer "has a human already looked at this exact Low-tier case."

`pricing_data/classification_review_queue.csv` (§3.5) closes this, following the same append-mostly, soft-lifecycle pattern already established by `item_code_canonical_map.csv`:

| Field | Notes |
|---|---|
| `item_code` | |
| `item_name_raw` | Snapshot at first flag. |
| `confidence_tier`, `matched_signal_type`, `matched_term` | From the flag that created this entry. |
| `first_flagged_run_month`, `last_seen_run_month` | |
| `times_seen_unreviewed` | Increments each month the same unresolved case reappears. |
| `review_status` | `pending` \| `confirmed_beer` \| `confirmed_not_beer` \| `stale_ignored` \| `auto_resolved_config_change` |
| `reviewed_by`, `reviewed_at`, `decision_note` | Populated only on a real human action. |
| `classification_config_version` | The ruleset in effect when first flagged. |

**Lifecycle, rewritten after adversarial review (§14) found the original version could produce the exact duplicate it claimed was impossible.** The original rule created a fresh queue row whenever "the underlying facts genuinely changed (different `matched_term`, different reason...)" — but that condition cannot distinguish *the row's real content changing* from *a config edit reclassifying an otherwise-identical row*, and it had no mechanism at all for closing a queue entry once a later config edit resolved it into automatic inclusion. The rule below replaces it, keyed on `item_code` and queue *state*, not on comparing field values across runs:

1. **At most one `pending` entry per `item_code`, ever, by construction.** Each run, for every `item_code` with `confidence_tier = low` in this run's `classification_audit.csv`: if a `pending` entry already exists for that `item_code`, refresh its content fields in place — `matched_term`, `confidence_tier`-driving fields — regardless of *why* it's still Low (real content change or config change; the distinction doesn't matter here, because either way it's still the same open question: does a human think this is beer). If no `pending` entry exists (first flag, or the `item_code`'s last entry was already resolved to `confirmed_beer`/`confirmed_not_beer`/`stale_ignored`), append a fresh row — a genuinely new episode, correctly kept distinct from a prior, already-closed one. **Temporal fields, made mechanically consistent with "a reopened item represents a genuinely new episode":** which of §3.4's four cases governs is determined by which of the two branches above fired — never by any state on a prior, closed row for the same `item_code`.
   - **Refresh branch** (a `pending` entry already exists): its `last_seen_run_month` and `times_seen_unreviewed` are updated by §3.4's cases 2/3/4 exactly, comparing this run's `run_month` against *that pending entry's own* `last_seen_run_month`. Case 1 never applies here, since the row already exists. `first_flagged_run_month` is never modified by this branch, matching §3.4 cases 2–4, which never touch `first_seen_run_month` either.
   - **Fresh-row branch** (no `pending` entry exists): this is unconditionally §3.4's case 1, with no exception. `first_flagged_run_month` and `last_seen_run_month` are both set to this run's `run_month`, and `times_seen_unreviewed` is set to 1, computed from this run alone. A prior, closed row for the same `item_code`, if one exists, is never read and never contributes a field to the new row — its `last_seen_run_month` is irrelevant here, by construction, because it belongs to a different, already-closed episode. This is what "genuinely new episode" means mechanically: a closed episode's data has no bearing on any later one.

   This closes the one respect in which the queue's ordering guarantee previously fell short of the ledger's: within a single open episode, an out-of-order older-month run can never regress that episode's `last_seen_run_month`, and its `times_seen_unreviewed` is subject to the identical, honestly-disclosed limit §3.4 states for `times_seen` — both bounded to that one episode's own lifetime, never carried across a closed-then-reopened boundary.
2. **Reconciliation, run every month, closing the gap the original design left open:** for every currently-`pending` entry, look up its `item_code` in *this run's* `classification_audit.csv`. If it now appears with `confidence_tier` = `high` or `medium`, the row has become auto-included — by a config edit, since Stage 1's underlying facts about that row don't change between runs on their own. Close the entry automatically: `review_status = auto_resolved_config_change`. This is a distinct status from `confirmed_beer`/`confirmed_not_beer` on purpose — those two mean a human reviewed *this queue entry specifically*; `auto_resolved_config_change` means the classification changed out from under it via the config, and the queue is simply catching up, not making a judgment call. This does not contradict "the system never auto-resolves a queue entry" (below) — a human already made the relevant decision, by editing `beer_classification.yaml`, which is itself the governed, versioned, human-authored artifact §2.2 and §6.3 already treat as a deliberate action; closing the queue entry is bookkeeping, not classification.
3. If a `pending` entry's `item_code` doesn't appear in `classification_audit.csv` at all this run (fell to silent `none`, or the item disappeared from `structured_rows.csv` entirely), it stays `pending` and ages normally per the staleness rule below — nothing about its absence this run is treated as a resolution.

**A row that's never reviewed by a human** stays excluded by default forever — the Low-tier default never silently flips to included on its own, and rule 2 above only ever closes an entry because the *config* changed, never because time passed.

**Staleness is measured in calendar time, not re-flag count — the two are distinct metrics with distinct purposes, disambiguated explicitly (a freeze review found the original text used both framings interchangeably without ever stating which one actually gates escalation).** `times_seen_unreviewed` remains on the schema as a diagnostic counter — "how many separate runs has this case actually been re-flagged in" — but it is **not** what the 6-month/12-month thresholds below are measured against, since a genuinely unresolved item that happens to fall out of `structured_rows.csv` for a few months (rule 3 above) would otherwise go stale far more slowly than the calendar time it's actually been sitting unreviewed. The thresholds are measured as **`current run_month − first_flagged_run_month`, in calendar months, regardless of how many of those months the item was actually present or re-flagged**: past 6 calendar months, the entry moves into a "stale unreviewed" bucket surfaced prominently in the monthly report; past 12 calendar months, only an explicit, logged human decision can mark it `stale_ignored` — elapsed time alone never does this automatically. **The 2-month SLA in §9's acceptance criteria, the 6-month "stale unreviewed" escalation, and the 12-month `stale_ignored` threshold measure different things and are not meant to align numerically**: 2 months is a target for how quickly a human *should* act; 6 and 12 months (both now calendar-month-based, consistently) are backstops for what happens when they don't. A queue entry resolved within the 2-month SLA never reaches the 6-month escalation at all in the normal case.

### Logging

- `classification_audit.csv` carries `classification_config_version` on every row (§3.1) — any decision is reconstructable from the exact ruleset that produced it.
- `pipeline.log` (Stage 2's own entries, appended to the same per-run log file Stage 1 already writes to, or a Stage-2-specific log in the same `runs/<run_month>/` folder — an implementation detail, not decided here) records: which config version was loaded, per-tier counts, the None→Low escalation count, the new-entity count, and queue rows added/updated.
- `classification_run_summary.json` (§3.3) gives a human debugging a bad run six months later everything needed — tier counts, escalation counts, new-entity summary, queue delta — without re-running anything or re-deriving state from the raw PDF, matching the diagnostic bar the Stage 1 contract already sets for itself.

---

## 11. Relationship to later stages

**Stage 3 (Normalization)** consumes exactly the rows Stage 2 marked `included = true` — joining `structured_rows.csv` and `classification_audit.csv` on `item_code`, the same normalized-join pattern already established between Stage 1 and Stage 4's `item_code_canonical_map.csv`. Stage 3 must not assume anything about `matched_term` or `confidence_tier` beyond "this row is in scope" — no coupling between why a row was classified beer and how its name gets normalized.

**Canonical products (Stage 4).** No direct relationship for identity resolution itself: Stage 4 only ever matches or creates a canonical product from rows that passed both Stage 2's inclusion and Stage 3's normalization, and Stage 2's confidence tier plays no role in that matching. Separately, Stage 4's `item_status` maintenance for already-mapped item_codes reads `structured_rows.csv` directly (`KSBCL-Stage-4-Canonical-Identity-Architecture.md` §2.1, §3.1) — a check against Stage 1's raw extracted output, not against `included = true` — so an item_code Stage 2 excludes from a given run does not, on that basis alone, get marked `DELISTED`.

**GTIN / barcode search.** No relationship whatsoever. Stage 2 reserves nothing, hints at nothing, and should not be designed with barcode matching in mind at all.

**Future enrichment.** `matched_term` (the specific brand string Stage 2 recorded) is a plausible, low-cost seed for a future brand-entity-resolution effort — but this is a nice-to-have byproduct of doing Stage 2's actual job well, never a requirement Stage 2 is designed around. Building anything into Stage 2 specifically to serve a not-yet-built enrichment system would be exactly the kind of invented-ahead-of-need abstraction the master architecture's §10.5 warns against.

**Recommendation engine.** No direct relationship — several stages and a full catalog-build step removed. Stated plainly here only to close the loop this design phase's brief explicitly asked about; the honest answer is "not applicable at this distance."

---

## 12. Non-goals

Explicitly deferred, restated in one place for a future reader who wants the boundary without re-deriving it from every section above:

- **Style taxonomy** — a real, structured `Style` entity with hierarchy, benchmarking, and a stable ID matching the app's own `Style` domain model. Future Enrichment, sourced from outside KSBCL entirely.
- **Brand/brewery/company entities** — ownership, parent-brand relationships, manufacturing location. Future Enrichment.
- **Name normalization** in any form — Stage 3.
- **Pack structure** (`pack_size_ml`, `pack_count`, `container_type`) — Stage 3.
- **Canonical product identity / deduplication across Item Codes** — Stage 4.
- **Pricing, price history, live/delisted status** — Stage 5.
- **The DF inclusion/exclusion decision itself** — already made at the master-architecture level; Stage 2 only detects the fact.
- **Barcode, ABV, calories, images, descriptions** — never in this pipeline's scope.
- **Fuzzy/phonetic/ML-based matching as the primary mechanism** — explicitly considered and rejected (§4.7), not merely unaddressed.

---

## 13. Open questions

Every unresolved decision, stated plainly rather than silently assumed. None of these block finalizing this document as a design — they are implementation-time decisions or empirical questions that can only be answered once Stage 2 actually runs against real data, exactly the same posture the master architecture takes toward its own §12.4–12.7.

1. **Do the specific misspellings/abbreviations cited from the research corpus actually occur inside the real KSBCL PDF?** Genuinely unknown. Resolved empirically via the confirm-then-allowlist policy (§4.7) once Stage 2 is implemented and run — not resolved by guessing now.
2. **Is the None→Low supplier-corroboration escalation's noise/signal ratio acceptable in practice, and how often will the unfamiliar-supplier demotion (§4.2 rule 3) fire?** Both mechanisms are new, unrun against real data. Their fire counts are monitored metrics (§9) specifically so this gets answered empirically, not assumed.
3. **Are the KSBCL Supplier Codes cited from the research corpus (§4.4), and the four "plausible but unconfirmed" import brands (§6), actually correct/present in KSBCL data?** Neither comes from direct cross-reference against Stage 1's real output. Needs verification against a real run before being trusted, not before being written into this document as a starting point — this is now stated with the correct confidence level throughout (§4.4, §6), not overstated as "confirmed."
4. **Should a periodic broader spot-check of `none`-tier rows (beyond the proposed 25–50/month random sample) ever be warranted, given that tier's entirely-silent failure mode — and specifically given §8's summary table now names an explicit, mechanism-free residual gap (unlisted brand + no style word + unfamiliar supplier)?** A real, only partially closed gap — no default resolution proposed here; it's a review-bandwidth trade-off for whoever owns the monthly process, not a technical question this document can settle.
5. **Should a Low-tier item ever auto-promote after N consecutive unresolved months, without an explicit human edit to the config?** This document's default is no — a human must always explicitly edit `beer_classification.yaml`, and the only automatic queue closure (§10's `auto_resolved_config_change`) is triggered by that edit, never by elapsed time alone. Flagged as open only in case review-team bandwidth later makes the no-auto-promotion default impractical; not recommended to reconsider preemptively.
6. **Is there a real, confirmed need for a pricing-distortion signal on beer gift/combo packs?** The `combo_pack_suspected` field originally proposed for this was removed from §3.1's schema after adversarial review identified it as speculative, with no named downstream consumer (§7, §8). If Stage 4 or Stage 5 later confirms a real need, the field should be added *there*, justified by that stage's own requirement, not resurrected here in advance of one.
7. **Where exactly should Stage 2's log entries live** — appended to Stage 1's existing `pipeline.log`, or a separate Stage-2-specific log file in the same `runs/<run_month>/` folder? Left as an implementation-time choice (§10); either satisfies this document's actual requirement (everything reconstructable from files in that folder).
8. **Is there a correction/retraction path for `classification_known_terms.csv`?** As designed, it only ever grows — a wrongly-seeded brand, style keyword, or (especially) supplier code stays "known" forever, including permanently feeding the None→Low escalation net with a bad supplier corroboration. No dedicated tooling is proposed for this now; the interim answer is that this file, like `beer_classification.yaml`, is a versioned artifact a human can hand-edit and commit, with the edit itself standing as the correction record — matching how config corrections are already handled elsewhere in this pipeline (master architecture §6.3), rather than building a dedicated retraction mechanism against a problem not yet observed in practice.
9. **Should "Root Beer" / "Ginger Beer" (or similar compound non-alcoholic phrases sharing a beer-category word) be defended against at all, given the risk remains unconfirmed against real KSBCL data?** Deliberately left unmitigated by this document (§8) — a proposed style-keyword-veto exception was found, on freeze review, to directly contradict the master architecture's unqualified §6.1 point 3 ("never veto an unambiguous style-keyword match"), and Stage 2 has no authority to amend that unilaterally. If either term is ever confirmed to occur in real KSBCL data (via the new-entity diff or otherwise), the correct next step is an explicit, numbered decision at the master-architecture level, backed by that evidence — not a silent local exception. Until then, this is a named, accepted, monitored gap with no bounding mechanism (§8's summary table).

---

## 14. Adversarial review

An independent review pass was run against the complete draft — a separate agent, with no attachment to the design, explicitly briefed to try to break it, not summarize it favorably. **An earlier version of this section, drafted before that independent pass actually ran, listed four points that were all conclusions the author had already reached while writing the document — not genuine external findings.** That earlier version is not reproduced here; noting its existence and why it was wrong is itself part of an honest account of this document's process.

**What the real review found, and how each finding was resolved:**

1. **[Blocking] Stage 2 silently dropped a Low-confidence pathway the master architecture explicitly specifies** — §6.2's "match from an unfamiliar supplier" route to Low tier was missing entirely, undisclosed as a deviation. **Fixed**: restored as the second condition in §4.2 rule 3, alongside the exclusion guard.
2. **[Should-fix] The claim that supplier corroboration is "never a gate for inclusion" didn't survive scrutiny** — a silent `none`-tier row has no path to inclusion at all, so supplier familiarity was, in the only operationally-meaningful sense, already gating whether inclusion was ever possible. **Fixed**: §4.5 rewritten to state the narrower, actually-true claim (supplier familiarity never *grants* High/Medium confidence on its own) instead of the broader one that didn't hold.
3. **[Should-fix, arguably blocking] The review queue's "never duplicated" promise could be broken by a config edit, with no path to close a queue entry a config edit had already resolved.** **Fixed**: §10's lifecycle rewritten around `item_code` + queue state (at most one `pending` entry, ever) rather than field-value comparison, with an explicit monthly reconciliation step (`auto_resolved_config_change`) closing entries a config edit has already resolved.
4. **[Should-fix] "Confirmed real imports" (Corona, Stella Artois, Guinness, Peroni) misapplied this document's own confirmed/unconfirmed discipline** — no page/item-code citation backs any of the four, unlike the eleven brands that do have one. **Fixed**: §6 and §8 rewritten to state plainly that these are plausible, low-cost additions, not confirmed KSBCL facts.
5. **[Should-fix] The exclusion guard had zero defense on the style-keyword path against a concrete, named risk** — "Root Beer" and "Ginger Beer" both contain the literal word "beer" and would auto-include at High confidence with the exclusion mechanism never even running, an asymmetry with the brand-path soda/water defense that was never justified. **Fixed at the time, then reverted during the subsequent Stage 2 Architecture Freeze review**: the compound-phrase guard proposed here was found, on that later freeze review, to directly contradict the master architecture's unqualified §6.1 point 3 ("never veto an unambiguous style-keyword match") — a frozen guarantee this document has no authority to amend unilaterally, especially against a risk that remains unconfirmed in real KSBCL data. See §15 for the full resolution: the guard was removed, and the risk is now carried as a named, accepted, unmitigated open question (§13, item 9) instead.
6. **[Should-fix] The "priority order" tie-break for multi-style-keyword matches was asserted in §5 but never actually defined**, undermining determinism — the document's own stated primary correctness criterion (§9). **Fixed**: §5 now specifies config declaration order as the explicit rule, with the alternatives considered and why they were rejected.
7. **[Worth-noting] `classification_new_entities.csv` had an unaddressed month-1 bootstrap problem** — every term in the first-ever run would appear as "new," indistinguishable from a genuine later discovery, inconsistent with how carefully the master architecture handled the identical class of problem for `beer_price_history.csv` (`INITIAL_BACKFILL`). **Fixed**: §3.4 adds an explicit `is_bootstrap_run` flag on the first run's summary.
8. **[Worth-noting] The `supplier_code` write-trigger for the persistent ledgers was inferable but never actually stated**, inconsistent with how precisely everything else is pinned down. **Fixed**: §3.4 now states it explicitly.
9. **[Worth-noting] `combo_pack_suspected` was an unrequested field added to a soon-to-be-frozen schema, with no named consumer** — precisely the kind of invented-ahead-of-need addition the master architecture's §10.5 warns against. **Fixed**: removed from §3.1; downgraded to an open question (§13, item 6).
10. **[Worth-noting] §8's summary table mixed pre-fix and post-fix outcomes inconsistently**, making it unclear which rows reflected the shipped design. **Fixed**: table rewritten to uniformly reflect the design after every fix in this section, with the one remaining unmitigated case named explicitly rather than implied.
11. **[Worth-noting] No correction/retraction path exists for `classification_known_terms.csv`.** **Not fixed as new tooling** — carried forward honestly as an open question (§13, item 8), with the interim answer (hand-edit the file, like the config it parallels) stated rather than left implicit.
12. **[Process finding] The original §14 was correctly identified as not being a genuine independent review.** Addressed by this rewrite.

**Verdict from the reviewer: not ready to freeze, pending the five should-fix items above (findings 1–5, plus the tie-break in finding 6).** All six were fixed at the time, as described (finding 5's fix was later reverted — see §15).

---

## 15. Stage 2 Architecture Freeze — resolution of the seven blocking findings

A formal **Stage 2 Architecture Freeze** review followed §14's adversarial pass, run against the complete document by a second independent agent with zero conversation context — a cold read, as an implementer with no ability to ask questions. It found seven **blocking** issues, none of which §14's review had surfaced. Each is resolved below. Per this project's governing rule ("if resolving a blocker requires changing the master pipeline architecture, do not silently redefine it in Stage 2 instead"), every blocker was independently re-verified against the master architecture, the Stage 1 contract, the real Stage 1 implementation, and the domain models before being classified and fixed — none were accepted as correct simply because the freeze review said so.

| # | Blocker | Verdict | Governing citation | Master architecture change required? |
|---|---|---|---|---|
| 1 | `classification_config_version` computation method unspecified | Genuine defect | Stage 1 `config.py` (real code) shows `*_used` fields are echoed CLI scalars, not file hashes — the analogy this document made didn't resolve anything | No — Stage 2-internal |
| 2 | `beer_classification.yaml` structure unspecified | Genuine defect | Master architecture §6.3 specifies "three lists," not a file format | No — Stage 2-internal |
| 3 | Word-boundary vs. substring matching unspecified for primary layers | Genuine defect | Master architecture §6.1 is silent on matching mechanics; Stage 2's own §4.7 only covered short abbreviations | No — Stage 2-internal |
| 4 | Rerun idempotency for the two persistent ledgers unaddressed | Genuine defect | Stage 1 contract §7's explicit, verified idempotency guarantee — Stage 2 made no equivalent claim | No — Stage 2-internal |
| 5 | Staleness clock basis ambiguous (re-flag count vs. calendar time) | Genuine defect | Internal to a mechanism (the review queue) the master architecture doesn't specify at all | No — Stage 2-internal |
| 6 | Within-run read/write ordering against `classification_known_terms.csv` could make classification page-order-dependent | Genuine defect, most severe of the seven | This document's own §9, "identical input classifies identically every time" | No — Stage 2-internal |
| 7 | Compound-phrase guard vetoes a style-keyword match | Genuine defect, direct contradiction | Master architecture §6.1 point 3, verbatim: "never veto an unambiguous style-keyword match" | **Considered and explicitly declined** — see below |

**Resolutions:**

1. **`classification_config_version`** — defined precisely as the first 12 hex characters of SHA-256 over the raw bytes of `beer_classification.yaml`, computed fresh at the start of every run. Chosen over a git-hash (adds a runtime git dependency Stage 1 has never needed) or a hand-maintained version key (relies on human discipline, and would add a fourth top-level config key beyond §2.2's exactly-three). File changed: this document (§3.1).
2. **Config file structure** — specified exactly: three top-level YAML keys, each a flat sequence of plain strings, with an explicit sample. Config entries are authored in natural casing; the loader folds both sides of every comparison identically. File changed: this document (§2.2).
3. **Matching semantics** — made word-boundary-anchored, universally, for every entry in every list (style, brand, exclusion), not just short abbreviations — closing a concrete, named risk this pipeline's own vocabulary already contains (`gin` as an exclusion term, `ale` as a style keyword, both real substring-collision risks). This simplified §4.7 by removing a now-redundant special case, separating *matching mechanics* (universal) from *curation policy* (short tokens still need a stricter human-confirmation bar before being added at all). Files changed: this document (§4.1, §4.7).
4. **Persistent-ledger rerun idempotency** — both `classification_known_terms.csv` and `classification_review_queue.csv` now check whether the current run's `run_month` has already been recorded before incrementing any counter, making a rerun of an already-processed month a true no-op — matching the idempotency bar Stage 1 already established. Files changed: this document (§3.4, §10).
5. **Staleness clock basis** — disambiguated into two distinct, separately-named metrics: `times_seen_unreviewed` (a diagnostic re-flag counter) and calendar-month elapsed time since `first_flagged_run_month` (what the 6-month/12-month escalation thresholds actually measure). File changed: this document (§10).
6. **Within-run determinism** — an explicit two-phase execution model was specified: Phase 1 classifies every row against a frozen, run-start snapshot of `classification_known_terms.csv`; Phase 2, only after Phase 1 completes entirely, computes the new-entity diff and updates the ledger. Nothing written in Phase 2 is ever visible to Phase 1, by construction, making `classification_audit.csv` fully independent of row/page processing order. File changed: this document (§3.4, with a cross-reference from §4.2).
7. **Compound-phrase guard vs. the frozen "never veto" rule** — the exact conflict, and why a master-architecture change was considered and declined, is worth stating plainly rather than just asserting: the guard existed to defend against a risk ("Root Beer"/"Ginger Beer" auto-including as beer) that is **not confirmed to occur anywhere in the real KSBCL PDF**. This document's own §4.7 already argues against building a defense mechanism for the equally-unconfirmed misspelling risk, on the grounds that doing so solves a problem this pipeline hasn't been shown to have. Applying a different standard here — bending a frozen master-architecture guarantee for an unconfirmed risk, while declining to build far cheaper defenses (fuzzy matching) for an equally unconfirmed one — would be inconsistent, not principled. The smallest valid resolution is therefore **not** a master-architecture amendment: the guard's ability to affect a style-keyword match was removed entirely, restoring exact compliance with §6.1 point 3 as written, and the underlying risk is now carried as an explicit, named, unmitigated open question (§13, item 9) with a stated escalation path — a real, numbered master-architecture decision, backed by real evidence, if and when the risk is ever confirmed. Files changed: this document only (§4.2, §3.1, §3.3, §8, §13, §14); **`KSBCL-Beer-Pricing-Pipeline-Architecture.md` was not modified** — it remains exactly as previously frozen.

**Why these are the smallest valid changes:** none of the seven required touching the master architecture, the Stage 1 contract, or any code (none exists yet). All seven are precision/specification fixes within Stage 2's own document — either filling in a genuine gap the master architecture never claimed to fill (1–6), or reverting a local addition that had overstepped this document's authority back to exact compliance with what's already frozen (7).

---

**Stage 2 architecture has been through two independent review passes (§14, §15) with every finding from both resolved or explicitly, honestly carried forward as a non-blocking open question. A third, fully independent freeze review — with no access to either prior review's findings — was then run. Its result is recorded honestly in §16 below: it found new blocking issues, so this document is NOT frozen as of this revision.**

---

## 16. Third Freeze Review — blocking issues found, NOT frozen

A third independent review agent, with zero access to §14/§15's findings and instructed to assume nothing, was run and — critically — instructed to cross-check every claim against the real Stage 1 output the pipeline had already produced (`pricing_data/runs/2026-06/structured_rows.csv`, `run_summary.json`), not just against this document's own internal consistency. It found four issues, three of them blocking, and — unlike either prior review — backed each with specific, real rows already present in the repository. Two of the most severe were independently spot-checked (grep against the real file) before accepting them into this record, and both confirmed exactly as reported:

1. **[Blocking] `is_duty_free` detection ("`-DF` suffix") is underspecified, and the literal reading misses real duty-free beer rows.** The real file contains at least four distinct renderings of the DF marker beyond the documented form — mixed-case `-Df` (confirmed: `Corona Extra Beer -Df 330ml (0351)`, `Guinnes Draught Beer-Bottle-Df 330ml (0351)`, `Heineken Lager Beer-Cans-Df 330ml (0357)`), no-hyphen `DF` (confirmed: `Brewdog Lost Lager DF 330ML X 24Btls.(0351)`), and others. A literal, case-sensitive `-DF` implementation would route real duty-free beer into the standard-retail file, violating the master architecture's frozen §12.2 decision. **Independently re-verified against the real file — confirmed exactly as cited.**
2. **[Blocking] `exclusion_terms` is an open, never-fully-enumerated list, and a real spelling-variant gap produces a confirmed false positive.** `Budweiser Magnum Double Barrel Blended American Whiskey 750MLx12Btls(0139)` is a real row (supplier "John Distilleries Pvt- Ltd-, Goa") that would auto-include as Medium-confidence beer under this document's exact rules as written: no style keyword matches, "Budweiser" matches the brand allowlist, and the exclusion guard's `whisky` entry does not match the American spelling `Whiskey`. **Independently re-verified against the real file — confirmed exactly as cited.**
3. **[Blocking] The word-boundary, no-stemming matching rule has a confirmed plural-form gap.** `\bbeer\b` does not match "Beers" under strict word-boundary matching; 90 real rows use the plural form (e.g. `Budweiser Premium King Of Beers 650ML(0212)`, repeated across at least four suppliers), currently masked only by incidental brand-allowlist overlap, not by the style layer this document describes as the unvetoable, reliable backbone of the whole mechanism. Not previously named in §8's edge-case catalogue or §13's open questions.
4. **[Recommended] Cross-run `run_month` ordering is never stated as a precondition.** The idempotency guards added in §15 (checking `last_seen_run_month` against the current run) correctly handle a rerun of the *same* month, but do not handle an out-of-chronological-order run (e.g., re-running March after June has already advanced the ledgers) — this can regress `last_seen_run_month` backward and double-count `times_seen`. Stage 1's own contract explicitly supports re-running any past month, so this is a real, not hypothetical, operational scenario. **Resolved in a later round**: §3.4's four-case update rule (no existing row / same-month rerun / newer-month run / older-month rerun) now states exactly this, with an honestly-disclosed scope limit — see §17.

**No fix has been applied for any of these four in this revision.** Per the explicit instruction governing this review round, finding new blocking issues means stopping here, not immediately patching and re-declaring frozen — that would repeat exactly the pattern (fix-and-self-certify without a genuinely independent check) this whole review process exists to avoid.

---

## 17. Architecture Close-Out — Final Disposition

Following §16's discovery of new blocking issues, a fourth and final review round applied a stricter, explicitly stated governing rule: **"The Stage 2 architecture must define mechanisms, not today's observed KSBCL spellings. Configuration owns vocabulary. Implementation owns parsing. Tests own observed examples. Architecture owns only rules that two independent engineers would otherwise implement differently."** Applying that rule to every item ever left open across §13, §14, §15, and §16 — plus two new findings the stricter rule itself surfaced — resolves every one of them into exactly one of: fixed and folded into this document's frozen text, configuration, an explicitly recorded product decision, or future implementation work. None remains architecture.

**What closed in this final round:**

- **§4.1** gained a precise, general token-boundary definition (a boundary exists at every transition between Unicode-letter, Unicode-digit, and other-character classes, applying uniformly to every vocabulary matched this way). This closed the one genuine mechanism gap inside §16 finding 1 — which is why that finding's *matching-mechanism* portion is now frozen architecture, while its *lexical-variant* portion (case, hyphenation, spelled-out forms, digit-glued forms — §4.8) is configuration vocabulary content.
- **§10**'s review-queue lifecycle was rewritten into a mechanically verified, exact application of §3.4's ledger update rule, including the case §3.4 has no direct analogue for — a resolved episode reopening later. A closed episode's fields are now explicitly never read by a later one. This fully closes the review-queue-reopening finding.
- **Multi-word token-sequence matching** (whether `"Strong-Beer"` should match the config entry `"strong beer"`) was found, on reflection, not to reduce to any single already-decided principle in this document — it contains two competing, individually legitimate precedents (§4.7's confirm-then-allowlist discipline, and §5.1's formatting-normalization discipline) that point in opposite directions. Choosing between them is a precision/recall risk-tolerance call, not a technical fact derivable from the text — recorded below as a **Product Decision Required**, not resolved here.

### Product Decision Required: multi-word vocabulary matching across alternate punctuation

**The question:** when a config vocabulary entry is a multi-word phrase (e.g. `style_keywords: strong beer`), should the matcher recognize the same two words joined by punctuation other than a single space (e.g. `Strong-Beer`, `Strong/Beer`) as the same phrase?

**Two acceptable directions, both technically sound, both consistent with a different part of this document's existing design philosophy:**

- **(a) Normalize punctuation between tokens.** Extend the existing fold step (§4.1) so that any boundary-class character standing between the declared tokens of a phrase is treated as equivalent to the canonical separator — the same way `×`/`x`/`X` are already unified before matching (§5.1). Higher recall; a small, currently unmeasured increase in false-positive exposure.
- **(b) Treat alternate punctuation as additional vocabulary entries.** Leave the matcher strict — a multi-word entry matches only in its declared, canonically-folded form — and require any confirmed alternate-punctuation form to be added to `beer_classification.yaml` as its own literal entry, exactly like a confirmed brand misspelling (§4.7). Lower recall until a variant is actually observed and curated; no additional false-positive exposure beyond what this design already accepts elsewhere.

**This document intentionally does not choose between them.** The choice is a business risk-tolerance decision — precision versus recall, and how much curation burden the product owner accepts — not a fact this document, or any engineer implementing it, can derive on its own. Architecture is complete once a decision like this is *identified and correctly routed*, not only once every decision has been made. Whichever direction is chosen, the resulting rule is a small, purely mechanical addition to §4.1 with no further architectural consequence.

### Final categorization of every item ever left open

| Item | Source | Category |
|---|---|---|
| Misspellings/abbreviations confirmed in real KSBCL data | §13, item 1 | Future implementation work — empirical validation |
| None→Low escalation / unfamiliar-supplier fire rates | §13, item 2 | Future implementation work — empirical validation |
| Supplier codes / import brands correctness | §13, item 3 | Future implementation work — empirical validation |
| Broader `none`-tier spot-check bandwidth | §13, item 4 | Future implementation work — operational procedure |
| Auto-promote after N unresolved months | §13, item 5 | Product decision (default already set to no; open only for future reconsideration) |
| `combo_pack_suspected` pricing-distortion signal | §13, item 6 | Future implementation work — future-stage-contingent (Stage 4/5) |
| Where Stage 2 log entries live | §13, item 7 | Future implementation work — implementation choice |
| Correction/retraction path for `classification_known_terms.csv` | §13, item 8 | Future implementation work — operational procedure |
| "Root Beer" / "Ginger Beer" unmitigated gap | §13, item 9 | Future implementation work — future-stage-contingent (new master-architecture decision, only if evidence ever appears) |
| `is_duty_free` textual variants (case, hyphenation, spelled-out, digit-glued forms) | §16, item 1 | Configuration |
| `exclusion_terms` — `whisky` / `Whiskey` | §16, item 2 | Configuration |
| `style_keywords` — `Beer` / `Beers` | §16, item 3 | Configuration |
| Cross-run `run_month` ordering | §16, item 4 | Resolved — now frozen architecture (§3.4, §10) |
| Multi-word token-sequence matching across alternate punctuation | Fourth review round, Finding 1 | **Product decision required** (see above) |
| Review-queue reopening mechanics | Fourth review round, Finding 2 | Resolved — now frozen architecture (§10) |

**Disposition:** every item ever opened across §13–§16 is now either fixed and folded into this document's frozen text, permanently classified as configuration vocabulary content, explicitly recorded as a Product Decision Required with both acceptable directions stated, or future implementation/operational/empirical work that needs no further architectural specification to proceed. Nothing remains classified as architecture. No item left on this list would let two competent engineers, given the same product intent, implement different Stage 2 behavior.

---

**Stage 2 Architecture is frozen.**

Any future discovery of additional KSBCL lexical variants shall be handled by configuration or tests unless it exposes a new ambiguity in the matching mechanism itself.
