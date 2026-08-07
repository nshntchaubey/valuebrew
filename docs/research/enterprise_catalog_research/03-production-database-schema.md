# Deliverable 3 — Production Database Schema

# ValueBrew Master Beer Database — Production Schema Design

Scope: India-wide, 50,000+ SKU capacity, Karnataka-only pricing live today. Designed against the actual data patterns surfaced in this session's research (KSBCL government price lists, UBL SEBI filings, Madhuloka/onlinealcohol.in retail scrapes, Open Food Facts GTINs, brand-site marketing pages, and multiple internally-contradictory or unreachable sources). Every design decision below is traceable to a concrete problem seen in that data — called out inline as `# Evidence:`.

---

## 0. Design principles (non-negotiable)

1. **Claims are immutable, facts are derived.** Every scraped/observed value is written once and never edited or deleted. What the UI calls "the ABV" or "the price" is a *materialized, recomputed* pointer to the best current claim — not a field anyone overwrites in place.
2. **Disagreement is data, not noise.** When KSBCL says ₹155 and Madhuloka says ₹162 for the same SKU, both rows persist forever with their own source and confidence. `# Evidence: STOK's own official page contradicts itself — spec table says 7% ABV, FAQ on the same page says 8%. Same-source self-contradiction must be representable.`
3. **Sources are ranked, not trusted equally.** A SEBI regulatory PDF fetched with `pdftotext` outranks an AI-paraphrased WebFetch summary of a marketing page. `# Evidence: research report itself flags "WebFetch results are AI-summarized paraphrases... residual risk the summarization step dropped or slightly misstated a number."`
4. **Sources go stale and go dark.** Bira91.com currently serves an Apache default page; Living Liquidz returns 503; Zauba is a zombie site with 2016-era data under a 2021 footer. The schema must track reachability/staleness as a first-class fact, not just "last successful value."
5. **Geography is a fact with provenance, not a boolean flag on Beer.** Arbor Brewing's packaged beer is retail-available in Goa but explicitly *not* Karnataka despite a Bengaluru taproom — availability must be state-scoped, source-scoped, and support a confirmed-*unavailable* state, not just "unknown."
6. **Identity ≠ Brand ≠ Manufacturer.** Budweiser is owned by AB InBev but bottled under contract by "S P R Distilleries Pvt Ltd" (KSBCL Supplier Code 0212); Kingfisher Premium (bottle, code 0210) and Kingfisher Premium Can (code 0202) are registered under different KSBCL supplier codes for the same brand. Brand ownership, physical brewing location, and state-excise registration are three separate relationships.
7. **National scale, Karnataka data.** All tables are state-agnostic by design (no `karnataka_` prefix baked into core entities except the two explicitly requested MRP tables) so the other 27 states/UTs slot in without a schema migration.

---

## 1. Entity-relationship overview

```mermaid
erDiagram
    COMPANY ||--o{ BREWERY : operates
    COMPANY ||--o{ BRAND : owns
    BRAND ||--o{ BEER : "has line extensions"
    STYLE ||--o{ BEER : classifies
    BEER ||--o{ SKU : "packaged as"
    PACKAGE_TYPE ||--o{ SKU : "packaged in"
    BREWERY ||--o{ STATE_REGISTRATION : "registered to brew under"
    BRAND ||--o{ STATE_REGISTRATION : "brand registered via"
    SKU }o--|| STATE_REGISTRATION : "priced under"
    SKU ||--o{ GTIN_CLAIM : "identified by"
    SKU ||--o{ ALCOHOL_PERCENT_CLAIM : "has ABV claims"
    SKU ||--o{ CALORIE_CLAIM : "has calorie claims"
    SKU ||--o{ VOLUME_CLAIM : "has volume claims"
    SKU ||--o{ KARNATAKA_MRP_HISTORY : "has price observations"
    SKU ||--|| KARNATAKA_MRP_CURRENT : "resolves to"
    SKU ||--o{ AVAILABILITY_BY_STATE : "available in"
    SKU ||--o{ IMAGE : "depicted by"
    BEER ||--o{ ALIAS : "known as"
    BRAND ||--o{ ALIAS : "known as"
    SKU ||--o{ SEARCH_KEYWORD : "matched by"
    SOURCE ||--o{ EVIDENCE : "produces"
    EVIDENCE ||--o{ ALCOHOL_PERCENT_CLAIM : supports
    EVIDENCE ||--o{ KARNATAKA_MRP_HISTORY : supports
    EVIDENCE ||--o{ GTIN_CLAIM : supports
    SKU ||--o{ AUDIT_TRAIL : "change log"
    SKU ||--o{ DUPLICATE_CANDIDATE : "flagged against"
```

---

## 2. Table catalog

Types are Postgres-flavored; adapt as needed. `BIGINT GENERATED ALWAYS AS IDENTITY` for all surrogate PKs. All canonical (non-ledger) tables carry `is_active BOOLEAN DEFAULT TRUE`, `superseded_by_id BIGINT NULL`, `row_version INT DEFAULT 1`, `created_at`/`updated_at TIMESTAMPTZ` — **true DELETE is never used**, only soft-delete + supersede pointer, so old FKs and external links never 404.

### 2.1 Reference / master data

**`company`** — legal entities: brand owners, contract bottlers, importers. Separates "who owns the brand" from "who brews it."
| Column | Type | Key | Notes |
|---|---|---|---|
| company_id | BIGINT | PK | |
| legal_name | TEXT | NOT NULL | e.g. "United Breweries Limited", "S P R Distilleries Pvt Ltd", "B9 Beverages Pvt. Ltd." |
| company_type | TEXT | CHECK IN ('brand_owner','contract_bottler','importer','distributor','conglomerate') | one company can hold multiple roles — see `company_role` join table if multi-role needed at scale |
| parent_company_id | BIGINT | FK → company.company_id, NULL | e.g. UBL is part-owned/licensed by Heineken; models group structures |
| country | TEXT | NOT NULL | |
| hq_state | TEXT | NULL | |
| website_url | TEXT | NULL | |
| website_reachable | BOOLEAN | DEFAULT TRUE | flips false when e.g. abinbevindia.in age-gate or bira91.com serves Apache default |
| last_reachability_check_at | TIMESTAMPTZ | | |

**`brewery`** — physical manufacturing sites.
| Column | Type | Key | Notes |
|---|---|---|---|
| brewery_id | BIGINT | PK | |
| operator_company_id | BIGINT | FK → company.company_id, NOT NULL | |
| plant_name | TEXT | NOT NULL | e.g. "Nanjangud unit", "Chamundi-Mysore facility", "Mysuru brewery (Nanjangud taluk)" |
| address | TEXT | NULL | |
| state | TEXT | NOT NULL | for Karnataka-plant tagging (Carlsberg Mysuru, UBL Nanjangud, AB InBev Mysuru) |
| country | TEXT | NOT NULL | |
| capacity_notes | TEXT | NULL | free text, e.g. "22,000 cans/hour can-line, ₹100cr investment" |

**`brand`** — the marketing brand (Kingfisher, Tuborg, Bira 91), independent of package/size.
| Column | Type | Key | Notes |
|---|---|---|---|
| brand_id | BIGINT | PK | |
| owner_company_id | BIGINT | FK → company.company_id, NOT NULL | |
| brand_name | TEXT | NOT NULL, UNIQUE(canonical form) | canonicalized display name |
| parent_brand_id | BIGINT | FK → brand.brand_id, NULL | e.g. "Bira 91 Boom" could roll up to "Bira 91"; "Kingfisher Ultra Max" rolls up to "Kingfisher" — see note below on where line-extension hierarchy actually lives |
| country_of_origin | TEXT | NULL | e.g. Amstel = Netherlands heritage, Tuborg = Denmark |
| is_nonalcoholic_line | BOOLEAN | DEFAULT FALSE | Heineken 0.0, Budweiser 0.0 |

> **Design note on brand vs. beer hierarchy:** "Kingfisher" is a brand; "Kingfisher Ultra Witbier" is a *beer* (product line) under that brand; "Kingfisher Ultra Witbier 500ml can" is a *SKU*. We do **not** model sub-brand as another level of `brand` — `beer.brand_id` + `beer.name` is sufficient and avoids infinite regress (Bira91→Boom→Boom Classic→Boom Strong). `parent_brand_id` exists only for genuinely separate legal brand families under one owner (e.g., UB owns both "Kingfisher" and "London Pilsner" and "Bullet" as distinct brands, not variants of one brand).

**`style`** — beer style taxonomy, hierarchical (BJCP-inspired but flattenable).
| Column | Type | Key | Notes |
|---|---|---|---|
| style_id | BIGINT | PK | |
| style_name | TEXT | NOT NULL | e.g. "Witbier", "Strong Lager", "Dry Stout" |
| parent_style_id | BIGINT | FK → style.style_id, NULL | e.g. "Strong Lager" → parent "Lager" |
| style_category | TEXT | CHECK IN ('Lager','Ale','Stout/Porter','Wheat/Witbier','Hybrid/Other','Non-Alcoholic') | top-level bucket for filtering |

**`package_type`** — reference list.
| Column | Type | Key | Notes |
|---|---|---|---|
| package_type_id | BIGINT | PK | |
| name | TEXT | UNIQUE | 'Bottle','Can','Draught/Keg','Growler' |
| is_onpremise_serving | BOOLEAN | DEFAULT FALSE | flags "Pint"/"Tin" ambiguity — see §6 |

**`beer`** — a product line, independent of package size (the thing a consumer would call "a beer").
| Column | Type | Key | Notes |
|---|---|---|---|
| beer_id | BIGINT | PK | |
| brand_id | BIGINT | FK → brand.brand_id, NOT NULL | |
| name | TEXT | NOT NULL | canonical display name, e.g. "Kingfisher Ultra Witbier" |
| canonical_key | TEXT | GENERATED, UNIQUE | normalized slug used for entity-resolution blocking: `lower(brand)+lower(name)` with abbreviations expanded — see §5 |
| style_id | BIGINT | FK → style.style_id, NULL | |
| description | TEXT | NULL | |
| is_alcoholic | BOOLEAN | DEFAULT TRUE | FALSE for Heineken 0.0, Budweiser 0.0, Tuborg Zero Soda |
| is_flavored | BOOLEAN | DEFAULT FALSE | TRUE for KF Lemon Masala, Hoegaarden Rosee |
| is_beverage_not_beer | BOOLEAN | DEFAULT FALSE | catches non-beer SKUs that leak into scrapes, e.g. "Kingfisher Premium Packaged Drinking Water," "Tuborg Zero Soda" — kept in-schema but excluded from default beer counts |

### 2.2 State excise / regulatory registration

**`state_registration`** — the crucial join that explains why the same brand shows different supplier codes for different package formats (`# Evidence: KSBCL Supplier Code 0210 for Kingfisher Premium bottle vs. 0202 for Kingfisher Premium Can`).
| Column | Type | Key | Notes |
|---|---|---|---|
| registration_id | BIGINT | PK | |
| brand_id | BIGINT | FK → brand.brand_id, NOT NULL | |
| brewery_id | BIGINT | FK → brewery.brewery_id, NOT NULL | actual manufacturing/bottling plant |
| state_code | TEXT | NOT NULL | ISO-3166-2:IN, e.g. 'IN-KA' |
| excise_supplier_code | TEXT | NULL | KSBCL's "Supplier Code" field, verbatim |
| effective_from | DATE | NULL | |
| effective_to | DATE | NULL | |
| source_id | BIGINT | FK → source.source_id | |
| UNIQUE | | (state_code, excise_supplier_code) | |

### 2.3 SKU and identifiers

**`sku`** — the sellable unit: beer × package × volume × pack count.
| Column | Type | Key | Notes |
|---|---|---|---|
| sku_id | BIGINT | PK | |
| beer_id | BIGINT | FK → beer.beer_id, NOT NULL | |
| package_type_id | BIGINT | FK → package_type.package_type_id, NOT NULL | |
| volume_ml | INT | NULL | canonical resolved volume; NULL if genuinely unresolved (see `volume_claim`) |
| pack_count | INT | DEFAULT 1 | 12 for "650ML x 12 Btls" case-packs seen in KSBCL data |
| price_basis | TEXT | CHECK IN ('per_unit','per_case') | KSBCL price rows are frequently per-case; retail sites are per-unit — **must not be conflated** |
| registration_id | BIGINT | FK → state_registration.registration_id, NULL | which excise registration this priced line corresponds to, when known |
| sku_status | TEXT | CHECK IN ('active','discontinued','unverified_size','pending_review') DEFAULT 'pending_review' | `unverified_size` covers the many Madhuloka rows like "KF Premium Pint" / "KF Strong Tin" with no ml on the product page |
| canonical_display_name | TEXT | NOT NULL | e.g. "Kingfisher Ultra Witbier — 500ml Can" |
| UNIQUE | | (beer_id, package_type_id, volume_ml, pack_count) WHERE volume_ml IS NOT NULL | prevents dupes once volume is known |

**`gtin_claim`** — barcode observations (append-only; a SKU may have zero, one, or conflicting GTIN claims).
| Column | Type | Key | Notes |
|---|---|---|---|
| gtin_claim_id | BIGINT | PK | |
| sku_id | BIGINT | FK → sku.sku_id, NOT NULL | |
| gtin_value | CHAR(14) | NOT NULL | normalize to GTIN-14 (zero-pad EAN-13/UPC-A) |
| gtin_type | TEXT | CHECK IN ('EAN-13','UPC-A','GTIN-14') | |
| country_prefix_check | TEXT | NULL | should start with '890' for India-issued (per GS1); flag if not, per research's India-prefix finding |
| evidence_id | BIGINT | FK → evidence.evidence_id | |
| confidence_score | NUMERIC(4,3) | | see §7 |
| is_current_best | BOOLEAN | DEFAULT FALSE | exactly one TRUE per sku_id, maintained by nightly resolver, never by direct app write |
| observed_at | TIMESTAMPTZ | | |
| notes | TEXT | | e.g. "Sourced from Open Food Facts (crowdsourced, ODbL); no official brewery site publishes GTINs — confirmed gap across entire researched brand set." |

`# Evidence: GTIN coverage is essentially zero from official sources; only Open Food Facts (crowdsourced) yields real India-beer GTINs, e.g. Kingfisher 8905002180007, Tuborg Strong 8906018940104, Bira 91 Boom 8908005126324. Go-UPC's ToS explicitly forbid redistributing its data — never ingest Go-UPC results into a table designed to be re-served to ValueBrew's own users; OFF (ODbL/CC-BY-SA, commercial-use-permitted with attribution) is the only currently-safe bulk source.`

### 2.4 Disputed-fact claim ledgers (ABV, Calories, Volume)

All three follow the same pattern: append-only, never updated in place, one `is_current_best` winner materialized per SKU by the nightly resolver.

**`alcohol_percent_claim`**
| Column | Type | Key | Notes |
|---|---|---|---|
| claim_id | BIGINT | PK | |
| sku_id | BIGINT | FK → sku.sku_id, NULL | nullable — many ABV facts are stated at the *beer* level, not per-SKU (Heineken's site gives ABV once for "Heineken Original," not per pack size) |
| beer_id | BIGINT | FK → beer.beer_id, NULL | at least one of sku_id/beer_id required (CHECK) |
| abv_value | NUMERIC(4,2) | NOT NULL | percent, e.g. 4.96 |
| evidence_id | BIGINT | FK → evidence.evidence_id | |
| confidence_score | NUMERIC(4,3) | | |
| has_internal_conflict | BOOLEAN | DEFAULT FALSE | TRUE for e.g. STOK Strong, where the *same page* states both 7% (spec table) and 8% (FAQ) — both rows get this flag and neither auto-wins |
| is_current_best | BOOLEAN | DEFAULT FALSE | |
| observed_at | TIMESTAMPTZ | | |

**`calorie_claim`**
| Column | Type | Key | Notes |
|---|---|---|---|
| claim_id | BIGINT | PK | |
| sku_id / beer_id | BIGINT | FK, nullable pair as above | |
| kcal_value | NUMERIC(6,2) | NOT NULL | |
| basis | TEXT | CHECK IN ('per_100ml','per_serving','per_bottle') NOT NULL | Heineken's own pages report **per-100ml**, not per-bottle — mixing bases is a real corruption risk if not tracked explicitly |
| evidence_id | BIGINT | FK | |
| confidence_score | NUMERIC(4,3) | | |
| is_current_best | BOOLEAN | | |

**`volume_claim`**
| Column | Type | Key | Notes |
|---|---|---|---|
| claim_id | BIGINT | PK | |
| sku_id | BIGINT | FK → sku.sku_id, NOT NULL | |
| volume_ml | INT | NULL | NULL when the raw label is non-numeric ("Pint," "Tin") |
| raw_label | TEXT | NOT NULL | verbatim source text, e.g. "650ML x 12 Btls," "Pint," "500 ML CAN" |
| pack_count_claimed | INT | DEFAULT 1 | |
| evidence_id | BIGINT | FK | |
| confidence_score | NUMERIC(4,3) | | |
| is_current_best | BOOLEAN | | |

`# Evidence: ~40% of the 216-SKU Madhuloka extract has size "Pint"/"Tin"/blank rather than a real ml value — this is the single largest normalization problem in the current catalog and is exactly why volume needs its own claim ledger instead of being a bare SKU column.`

### 2.5 Pricing (Karnataka, current + historical)

**`karnataka_mrp_history`** — append-only ledger, one row per price observation, ever. This *is* the source of truth; nothing here is ever updated or deleted.
| Column | Type | Key | Notes |
|---|---|---|---|
| price_obs_id | BIGINT | PK | |
| sku_id | BIGINT | FK → sku.sku_id, NOT NULL | |
| price_inr | NUMERIC(10,2) | NOT NULL | |
| price_type | TEXT | CHECK IN ('KSBCL_MRP','retailer_listed','brand_press_release_MRP') NOT NULL | KSBCL's number is the government MRP; Madhuloka's is a retailer's listed price — these answer different questions and must never be merged into one column |
| price_basis | TEXT | CHECK IN ('per_unit','per_case') | mirrors sku.price_basis at time of observation, since case-size can change |
| evidence_id | BIGINT | FK → evidence.evidence_id | |
| confidence_score | NUMERIC(4,3) | | |
| observed_at | TIMESTAMPTZ | NOT NULL | when the price was scraped/filed |
| effective_date | DATE | NULL | for cases like the UBL SEBI filing giving an explicit launch/pricing effective date (e.g. Kingfisher Smooth, Jan 28 2026) |
| INDEX | | (sku_id, observed_at DESC) | partition by year at 50k-SKU × daily-crawl scale |

**`karnataka_mrp_current`** — materialized/derived, one row per SKU, rebuilt nightly by the resolver job. Never hand-edited; if it's wrong, fix the ledger or the confidence weights, then rebuild.
| Column | Type | Key | Notes |
|---|---|---|---|
| sku_id | BIGINT | PK, FK → sku.sku_id | |
| resolved_price_inr | NUMERIC(10,2) | | winning value per §6 merge rules |
| resolved_price_obs_id | BIGINT | FK → karnataka_mrp_history.price_obs_id | pointer to the winning ledger row — full traceability |
| price_type_used | TEXT | | which price_type won (govt MRP is preferred when available, see §6) |
| all_current_candidates | JSONB | | denormalized snapshot of *all* non-superseded conflicting prices at resolution time, e.g. `[{"source":"KSBCL","price":155,"type":"MRP"},{"source":"Madhuloka","price":162,"type":"retailer_listed"}]` — lets the product UI show "MRP ₹155 · seen at ₹162 online" without a join, while `karnataka_mrp_history` remains the audit-grade record |
| last_resolved_at | TIMESTAMPTZ | | |

### 2.6 Availability by state

**`availability_by_state`**
| Column | Type | Key | Notes |
|---|---|---|---|
| availability_id | BIGINT | PK | |
| sku_id | BIGINT | FK → sku.sku_id, NOT NULL | |
| state_code | TEXT | NOT NULL | ISO-3166-2:IN |
| availability_status | TEXT | CHECK IN ('confirmed_available','confirmed_unavailable','unknown','discontinued') NOT NULL | three-state, not boolean — required to encode "Arbor Brewing packaged beer retails only in Goa, NOT Karnataka, despite a Bengaluru taproom" as a *confirmed_unavailable* fact rather than silence |
| channel | TEXT | CHECK IN ('off_premise_retail','on_premise_only','import_only','online_delivery') | Windmills Craftworks / Byg Brewski are on_premise_only with no packaged retail found |
| evidence_id | BIGINT | FK | |
| confidence_score | NUMERIC(4,3) | | |
| observed_at | TIMESTAMPTZ | | |
| UNIQUE | | (sku_id, state_code, channel, evidence_id) | multiple evidences per (sku,state) are expected and kept, not collapsed |

### 2.7 Images

**`image`**
| Column | Type | Key | Notes |
|---|---|---|---|
| image_id | BIGINT | PK | |
| entity_type | TEXT | CHECK IN ('sku','beer','brand','brewery') | |
| entity_id | BIGINT | NOT NULL | polymorphic; app-layer FK, not DB-enforced (or use table-per-type junctions if strict FK integrity required) |
| storage_url | TEXT | NOT NULL | CDN/object-storage key, not hot-linking third-party sites |
| image_type | TEXT | CHECK IN ('label','can','bottle','logo','lifestyle') | |
| license | TEXT | NOT NULL | e.g. 'CC-BY-SA-3.0 (Open Food Facts)', 'unknown-do-not-redistribute' |
| license_requires_attribution | BOOLEAN | | |
| source_id | BIGINT | FK → source.source_id | |
| is_primary | BOOLEAN | DEFAULT FALSE | |
| retrieved_at | TIMESTAMPTZ | | |

`# Evidence: OFF images are CC BY-SA (redistributable with attribution); Madhuloka/retailer product images have no stated license — default new rows to 'unknown-do-not-redistribute' until legal clears each retailer's ToS, rather than assuming reuse rights.`

### 2.8 Provenance, evidence, and source trust

**`source`** — one row per distinct data provider (not per page).
| Column | Type | Key | Notes |
|---|---|---|---|
| source_id | BIGINT | PK | |
| source_name | TEXT | NOT NULL | e.g. "KSBCL official price list," "Madhuloka," "Open Food Facts," "unsobered.com" |
| source_tier | INT | CHECK 1–6 | see §7 weight table |
| base_trust_weight | NUMERIC(4,3) | | tier default, overridable per-source |
| domain | TEXT | | |
| robots_txt_allows_crawl | BOOLEAN | | Livcheers explicitly disallows /api/ and blocks named bots — must be FALSE and enforced at the crawler config level, not just documented |
| crawl_delay_seconds | INT | DEFAULT 1 | e.g. Carlsberg's Umbraco robots.txt specifies Crawl-delay:10 |
| is_reachable | BOOLEAN | DEFAULT TRUE | flips FALSE for Living Liquidz (503), bira91.com (wrong cert/Apache default), Goa Brewing Co (placeholder) |
| last_reachability_check_at | TIMESTAMPTZ | | |
| licensing_notes | TEXT | | e.g. "Go-UPC ToS prohibits redistribution — lookup-only, never persist raw response for re-serving" |

**`evidence`** — one row per raw fetch, immutable, linked from every claim table above.
| Column | Type | Key | Notes |
|---|---|---|---|
| evidence_id | BIGINT | PK | |
| source_id | BIGINT | FK → source.source_id, NOT NULL | |
| url | TEXT | NOT NULL | |
| http_status | INT | | |
| extraction_method | TEXT | CHECK IN ('curl_pdftotext','curl_html','browser_a11y_tree','ai_summarized_webfetch','manual_entry','vendor_api_json') NOT NULL | drives the extraction-method confidence multiplier in §7 |
| raw_content_hash | TEXT | | dedupe re-crawls of unchanged pages |
| raw_snippet | TEXT | | truncated raw text/JSON actually used, for audit — not the full page, to keep row size sane |
| fetched_at | TIMESTAMPTZ | NOT NULL | |
| retrieval_job_id | BIGINT | FK → ingestion_job.job_id | |

### 2.9 Alias, search, and entity resolution support

**`alias`** — alternate names for brand/beer/brewery/style entities.
| Column | Type | Key | Notes |
|---|---|---|---|
| alias_id | BIGINT | PK | |
| entity_type | TEXT | CHECK IN ('brand','beer','brewery','style') | |
| entity_id | BIGINT | NOT NULL | |
| alias_text | TEXT | NOT NULL | |
| alias_type | TEXT | CHECK IN ('abbreviation','misspelling','local_language','retailer_sku_label','former_name') | e.g. "KF"→Kingfisher (abbreviation), "BUDWIESER"→Budweiser (misspelling, verbatim from Madhuloka), "Tin"/"Can" mapping |
| source_id | BIGINT | FK, NULL | NULL for system-curated/dictionary aliases |
| confidence_score | NUMERIC(4,3) | | |

**`search_keyword`** — autocomplete/search index feed, decoupled from alias so it can hold weighted/partial/phonetic tokens without polluting canonical naming.
| Column | Type | Key | Notes |
|---|---|---|---|
| keyword_id | BIGINT | PK | |
| entity_type | TEXT | | |
| entity_id | BIGINT | | |
| keyword | TEXT | NOT NULL | |
| locale | TEXT | DEFAULT 'en-IN' | room for Kannada-script terms later |
| weight | NUMERIC(4,3) | DEFAULT 1.0 | |

**`duplicate_candidate`** — queue for near-matches the resolver isn't confident enough to auto-merge.
| Column | Type | Key | Notes |
|---|---|---|---|
| candidate_id | BIGINT | PK | |
| entity_type | TEXT | CHECK IN ('beer','sku','brand','brewery') | |
| entity_id_a | BIGINT | NOT NULL | |
| entity_id_b | BIGINT | NOT NULL | |
| similarity_score | NUMERIC(4,3) | | |
| match_features | JSONB | | per-field similarity breakdown, for reviewer transparency |
| status | TEXT | CHECK IN ('pending','confirmed_merge','confirmed_distinct') DEFAULT 'pending' | |
| reviewed_by | TEXT | NULL | |
| reviewed_at | TIMESTAMPTZ | NULL | |

**`merge_log`** — permanent record of executed merges, with redirect support.
| Column | Type | Key | Notes |
|---|---|---|---|
| merge_id | BIGINT | PK | |
| entity_type | TEXT | | |
| surviving_id | BIGINT | NOT NULL | |
| merged_id | BIGINT | NOT NULL | old ID, kept alive as a redirect via `is_active=FALSE, superseded_by_id=surviving_id` on the original row |
| merge_reason | TEXT | | |
| matched_on | TEXT | | e.g. "exact GTIN match," "0.94 fuzzy name+brand+volume" |
| merged_at | TIMESTAMPTZ | | |
| merged_by | TEXT | | 'auto_resolver' or human reviewer id |

### 2.10 Audit trail

**`audit_trail`** — generic change log across all canonical (non-ledger) tables. Claims tables don't need this (they're append-only by construction); this covers edits to master records themselves (brand renamed, style reclassified, human override of a resolver decision).
| Column | Type | Key | Notes |
|---|---|---|---|
| audit_id | BIGINT | PK | |
| table_name | TEXT | NOT NULL | |
| row_pk | BIGINT | NOT NULL | |
| operation | TEXT | CHECK IN ('insert','update','soft_delete','merge','resolver_recompute') | |
| old_value | JSONB | NULL | |
| new_value | JSONB | NULL | |
| changed_by | TEXT | NOT NULL | 'ingestion_job:#123', 'resolver:nightly', or human user id |
| changed_at | TIMESTAMPTZ | NOT NULL | |
| reason | TEXT | NULL | |

### 2.11 Ingestion orchestration (supporting table, not in the original list but required to make the workflow real)

**`ingestion_job`**: job_id, source_id, started_at, finished_at, status, rows_ingested, rows_flagged_for_review, error_log. Referenced by `evidence.retrieval_job_id` for full lineage from "this exact overnight crawl" down to "this exact claim row."

---

## 3. Normalization rationale

- **Master data (`company`, `brewery`, `brand`, `style`, `beer`, `sku`, `package_type`, `state_registration`) is in 3NF.** Each describes one real-world thing once; no repeating groups, no derived columns except generated `canonical_key`.
- **Disputed/multi-sourced attributes (ABV, calories, volume, GTIN, price, availability) are deliberately *not* 3NF-collapsed onto the SKU row.** They live in attribute-specific append-only ledgers rather than a single generic EAV table, because:
  - Generic EAV loses type safety (ABV is numeric with a range check; price needs currency/basis; volume needs unit conversion) — attribute-specific tables keep constraints meaningful.
  - Query performance and indexing are far better than a single giant `(entity_id, attribute_name, value_text)` table at 50k SKUs × multiple sources × history.
  - It mirrors exactly how the source data disagrees in practice (ABV self-contradiction on STOK's own page; price basis differing between government MRP and retail listing) — the schema should look like the problem, not like a generic key-value bag that hides it.
- **"Current" tables (`karnataka_mrp_current`, `is_current_best` flags) are materialized caches, not sources of truth.** They can be dropped and fully rebuilt from the ledgers at any time — this is the guarantee that nothing is "silently picked" permanently; it's re-derived nightly from an unchanged, complete history.

---

## 4. Entity resolution & duplicate-detection strategy

The 216-SKU sample already shows the failure modes we must handle at 50k+: identical products appearing under different casing/abbreviation across sources ("HEINEKEN SILVER" appearing 3x with different price_counts), size-less duplicates ("KNOCK OUT TIN" appearing twice), and misspellings ("BUDWIESER TIN").

**Pipeline:**

1. **Canonicalization pass** (deterministic, before any matching): lowercase; strip punctuation; expand a controlled abbreviation dictionary (`KF`→Kingfisher, `Btl`/`Bttl`→Bottle, `Tin`→Can — recorded as `alias.alias_type='retailer_sku_label'`); normalize `ml`/`ML`/`Ml`; correct known misspellings via the `alias` table (`BUDWIESER`→Budweiser) rather than fuzzy-matching every time.
2. **Blocking** (to avoid O(n²) at 50k+ scale): group candidates by `(brand_id, first_significant_token_of_style_or_name)`. Never compare across different brands.
3. **Deterministic auto-merge rules, checked first, in this order:**
   - Exact GTIN match → same SKU, always (barcode is the strongest possible key when present).
   - Exact `(brand, canonicalized_name, package_type, volume_ml, pack_count)` match → same SKU.
4. **Fuzzy scoring for everything else** — weighted composite over: brand match (0.30, must be exact after canonicalization — never fuzzy across brands), name similarity via token-sort/Jaro-Winkler (0.35), style match (0.10), volume match (0.15, with `NULL` volume treated as "unknown, needs review" rather than "matches anything"), package type match (0.10).
   - **score ≥ 0.92** → auto-merge, logged to `merge_log`.
   - **0.75 ≤ score < 0.92** → written to `duplicate_candidate`, held for human review.
   - **score < 0.75** → treated as distinct SKUs.
5. **Ambiguous-size SKUs** (raw label "Pint"/"Tin" with no ml, ~40% of the Madhuloka sample) are ingested as `sku_status='unverified_size'` with `volume_ml = NULL` and a `volume_claim.raw_label` capturing the verbatim text. They are **never auto-merged** into a sized SKU on name-match alone — only once a `volume_claim` resolves the size with sufficient confidence does the resolver attempt the merge, logged via `merge_log.matched_on = 'volume_resolved_post_hoc'`.
6. **Cross-source corroboration as a resolution signal, not just a confidence input:** if KSBCL (government, tier 1) and Madhuloka (retailer, tier 3) both independently produce a candidate for "Kingfisher Ultra Witbier, 500ml can," that agreement itself raises merge confidence — corroboration is symmetric evidence both for *entity identity* and for *fact correctness* (§7).

All merges are reversible: soft-deleted rows keep `superseded_by_id`, so a bad auto-merge can be split back out without losing any original claims.

---

## 5. Merge strategy when sources disagree on a fact

**Rule zero: never overwrite, always append.** Every table in §2.4–2.6 is `INSERT`-only from the application's perspective; there is no `UPDATE karnataka_mrp SET price = ...` anywhere in the ingestion code path.

**Resolution (deriving "current best") runs as a separate, idempotent, re-runnable job**, not at write time:

1. Filter claims to `is_active` sources only (source.is_reachable can still contribute historical claims, just at decayed confidence — see §7).
2. Compute `confidence_score` per claim (§7).
3. **For facts that should be singular** (ABV, calories, GTIN, current price): the highest-confidence claim wins `is_current_best = TRUE`; ties broken by most-recent `observed_at`; internal self-contradictions (`has_internal_conflict = TRUE`, e.g. STOK Strong 7% vs 8%) are excluded from auto-winning entirely and force a `duplicate_candidate`-style review row instead, regardless of confidence score.
4. **For facts that are inherently plural** (retail price across multiple retailers, availability across states): no single winner is computed — `karnataka_mrp_current.all_current_candidates` stores the full current set, with `resolved_price_inr` preferring `price_type='KSBCL_MRP'` (government MRP) when present, falling back to the highest-confidence retailer price only when no government MRP claim exists.
5. **The losing claims are never deleted or hidden** — every UI surface that shows "the ABV" must have a "sources disagree, show all N values" affordance backed directly by the ledger tables, not by a separate audit-only view.
6. **Re-resolution is automatic on new evidence and periodic even without new evidence** (recency decay means yesterday's "current best" price can lose to an older-but-now-relatively-fresher claim if the winning source goes stale — see §7 reachability decay).

---

## 6. Confidence scoring methodology

Every claim's `confidence_score` is a persisted composite so it's auditable, not a black-box float:

```
final_score = clamp(
    source_tier_weight
    × extraction_method_multiplier
    × recency_decay_factor
    + corroboration_bonus
    − contradiction_penalty,
    0.0, 1.0
)
```

**Source tier weights** (calibrated directly from this session's source audit):

| Tier | Weight range | Examples from this session |
|---|---|---|
| 1 — Government / regulatory, direct-fetched | 0.95–1.00 | KSBCL official Supplier-wise Price List; UBL SEBI Reg-30 PDF filings (pdftotext-extracted); DGCI&S aggregate data |
| 2 — Official brand site, structured, direct-fetched | 0.85–0.94 | heineken.com/in product pages with ABV/kcal in page text; carlsbergindia.com Tuborg Green page |
| 3 — Structured retailer API/microdata | 0.70–0.84 | onlinealcohol.in WooCommerce Store API JSON; Madhuloka product pages with schema.org `itemprop=price` microdata |
| 4 — Licensed crowdsourced open data | 0.50–0.69 | Open Food Facts (ODbL, explicit own-terms disclaimer of completeness) |
| 5 — Unstructured HTML scrape / AI-paraphrased fetch | 0.30–0.49 | Madhuloka rows with no microdata, relying on layout heuristics; any WebFetch-summarized (not curl-extracted) page |
| 6 — Secondary/unsourced blogs | 0.10–0.29 | unsobered.com ABV figures; Tonique's stale, placeholder-text price table |

**Modifiers:**
- `extraction_method_multiplier`: `curl_pdftotext`/`vendor_api_json` = 1.00; `curl_html` with microdata = 0.95; `browser_a11y_tree` = 0.90; `ai_summarized_webfetch` = 0.75 (explicit penalty for the exact risk the research flagged: paraphrase may drop or misstate a number); `manual_entry` = per-reviewer, typically 1.00 if a named human verified against physical packaging.
- `recency_decay_factor` = `exp(-age_days / halflife_days)`, with **halflife = 30 days for price claims** (prices move often, tier-1 govt MRP updates are still irregular/event-driven per UBL's own filing cadence), **halflife = 730 days for ABV/style/brewery-relationship claims** (these essentially never change), **halflife = 365 days for availability claims**.
- `corroboration_bonus`: `+0.05` per additional *independent source tier* (not just independent URL) agreeing within tolerance (ABV ±0.1%, price ±5%), capped at `+0.15` total.
- `contradiction_penalty`: `-0.5` applied to **both** conflicting claims when they come from the *same* evidence/source (self-contradiction, e.g. STOK's own spec table vs. its own FAQ) — this is what prevents the resolver from picking a winner out of a source's own internal noise.
- **Reachability decay**: if `source.is_reachable = FALSE` at resolution time, apply an additional `× 0.7` multiplier to that source's *existing* claims and mark them `stale_unverified` in the UI — covers Bira91.com (wrong TLS cert / Apache default page), Living Liquidz (503), Goa Brewing Co. (placeholder site), Zauba (frozen since ~2016 despite a live domain).

All five components are stored as separate columns on each claim row (not just the final float) so a reviewer or a future recalibration can answer "why did this win?" without recomputing history.

---

## 7. Update / ingestion workflow

```
[Source] → [ingestion_job + evidence (raw, immutable)] → [source-specific parser]
   → [staged_candidate] → [entity resolution: blocking + scoring]
   → auto-match (≥0.92) ──────────────► [claim tables, INSERT-only]
   → review queue (0.75–0.92) → human review → [confirmed] → claim tables
   → below 0.75 → new canonical entity created
                                                     │
                                                     ▼
                                    [nightly resolver job: recompute
                                     confidence, pick is_current_best,
                                     rebuild karnataka_mrp_current]
                                                     │
                                                     ▼
                                          [audit_trail on every write
                                           to canonical tables]
```

1. **Landing (immutable, idempotent):** every crawl writes to `evidence` keyed by `raw_content_hash`; unchanged pages are skipped (only `last_seen_at` touched), so re-crawling costs nothing when nothing changed.
2. **Source-specific parsers**, one per source shape actually observed: Odoo-HTML parser (Madhuloka), WooCommerce-Store-API JSON parser (onlinealcohol.in — the one source with a real, clean REST API, per this session's audit), PDF-text parser (KSBCL duty PDFs, UBL SEBI filings), OFF JSON parser. Output lands in `staged_candidate` with a `parser_schema_version` so parser bugs are traceable to affected rows later.
3. **Entity resolution** per §5, writing to canonical tables or `duplicate_candidate`.
4. **Claim insertion** into the relevant append-only ledger(s) with full `evidence_id` linkage and computed confidence.
5. **Nightly resolver** recomputes `is_current_best` flags and rebuilds `karnataka_mrp_current`; this job is the *only* writer of those derived pointers.
6. **Human review queue** surfaces: pending `duplicate_candidate` rows, any claim with `has_internal_conflict=TRUE`, any SKU whose only claims come from `source.is_reachable=FALSE` sources, and price outliers (>3× the median for that brand+volume, auto-flagged before promotion rather than silently trusted). Reviewer decisions are themselves logged as `source_tier=0` ("human_verified", weight 1.0) claims plus an `audit_trail` row with the reviewer's identity — human correction always outranks any scraped source but is still just another row in the ledger, not a magic override field.
7. **Crawl cadence by tier, respecting each source's stated policy:**
   - Tier 1 (KSBCL, UBL filings): weekly poll — low change frequency, highest stakes, matches the SEBI filing cadence pattern observed (irregular, event-driven).
   - Tier 3 structured APIs (onlinealcohol.in): daily for price, weekly for full catalog re-sync.
   - Tier 3 HTML (Madhuloka): daily, respecting its permissive robots.txt with a polite delay (no explicit crawl-delay found, but treat 1 req/sec as a ceiling).
   - Carlsberg India: respect the site's own `Crawl-delay: 10` from robots.txt.
   - **Livcheers.com: never scraped** — its robots.txt explicitly disallows `/api/` and blocks a long list of named bots; this is encoded as `source.robots_txt_allows_crawl = FALSE` and enforced by the crawler framework, not just documented.
   - Unreachable sources (Living Liquidz, bira91.com, Goa Brewing Co.): polled daily specifically to detect recovery, but contribute zero new claims while down, and existing claims decay per §7's reachability penalty.
8. **Data-quality gates before promotion:** schema validation on parser output; price-outlier flagging; orphan detection (SKU with no valid `beer_id`); duplicate-GTIN alerting (same GTIN claimed by two different `sku_id`s → forced review, since that's either an entity-resolution miss or a real-world barcode-reuse case per GS1's own reuse-after-discontinuation policy).
9. **Versioning:** canonical tables carry `row_version`/`updated_at`; every write is mirrored to `audit_trail`. Nothing is ever hard-deleted, so any historical state of the entire catalog is reconstructable.

---

## 8. Scale & performance notes (50,000+ SKUs, national rollout)

- Partition `karnataka_mrp_history` (and its future `*_mrp_history` siblings per state) by `observed_at` year — at daily crawls across tens of thousands of SKUs this table grows fastest.
- Index `sku(beer_id)`, `sku(gtin via gtin_claim.sku_id where is_current_best)`, `availability_by_state(state_code, sku_id)`, `beer(canonical_key)`, and a trigram/GIN index on `beer.name`/`brand.brand_name` for fuzzy search and entity-resolution blocking.
- The table set is **state-agnostic already** — `karnataka_mrp_current`/`karnataka_mrp_history` are the only Karnataka-named tables per the brief; renaming/generalizing them to a `state_mrp_current(sku_id, state_code, ...)` shape is a one-time, low-risk migration when a second state goes live, and can be done by making Karnataka just the first populated `state_code` rather than a schema rewrite — worth doing proactively if the roadmap to all-India is firm, since the brief's naming ("KarnatakaMRP") suggests keeping the requested name for now but the FK/column shape already supports the generalization.
- `image.entity_type/entity_id` is intentionally polymorphic rather than N nullable FK columns — acceptable at this row-count with app-layer integrity checks; revisit with per-type junction tables only if referential-integrity violations become a real incident source.

---

## 9. Explicit data-gap flags carried into the design (do not let the schema imply data that doesn't exist)

- **GTIN is sparse by construction, not by bug** — no brewery in the researched set publishes barcodes officially; expect `gtin_claim` to be empty for the large majority of SKUs at launch. Design queries and UI to treat `NULL`/no-current-GTIN as expected, not exceptional.
- **ABV/calories will be missing for most Madhuloka-sourced SKUs** — that retailer's product pages show brand/size/price but not ABV; only brand-site sources (Heineken, UBL, Carlsberg) and a handful of craft breweries (Arbor, STOK) supplied ABV in this session's research. Don't backfill with assumed/typical-style ABV — leave `is_current_best` unset (no claim) rather than guessing.
- **Import/trade-data features (e.g., "detect new imported brands") must not ingest importer-identity-linked shipment data.** Section 135AA of the Customs Act, 1962 criminalizes unauthorized publication of importer/exporter transaction-level data including identity; if ValueBrew ever adds an "imported brand discovery" feature on top of this schema (e.g., a `trade_signal` table sourced from Volza), it must store only brand/product-description-level signals, never buyer/supplier company identity sourced from customs filings, and legal counsel should sign off before that table is added — flagging this now so it isn't retrofitted under time pressure later.

---

If useful next, I can turn §2 into actual `CREATE TABLE` DDL (Postgres) with all constraints, or produce the nightly resolver job's pseudocode/SQL for `is_current_best` computation.