# Search Engine Design (supporting Deliverable 3/9)

# ValueBrew Search System Design — Karnataka Beer SKU Database

## 0. What the actual catalog tells us to design for

Before picking an engine, look at what's actually in the 216-SKU extract — the design has to survive this, not a clean textbook catalog:

- **Retailer-name chaos**: Madhuloka alone gives us `"KF ULTRA MAX"`, `"KF STRONG TIN"`, `"KF PREMIUM PINT"`, `"BUDWIESER TIN"` (misspelled), `"CARLSBERG MIRACLE CAN 500"` — i.e., brand is frequently *encoded as a prefix abbreviation* ("KF", "UB") rather than a normalized field, and typos are real, not hypothetical.
- **Brand/brewery/style fields are sparse**: many rows have `"brewery":""`, `"style":""` — confidence is explicitly tracked per-field in the source data (`"confidence":"Medium"/"Low"`). Search relevance and boosting should be confidence-aware.
- **Size is a free-text mess**: `"650ML x 12 Btls"`, `"330 ml"`, `"500ML CAN"`, `"Bottle: 650 mL, 330 mL; Can: 500 mL"`. There is no canonical `size_ml` integer anywhere in the source — this must be normalized at ingestion, not at query time.
- **GTIN/barcode coverage is almost nonexistent from Karnataka retail/regulatory sources** (KSBCL, Madhuloka, UBL, Carlsberg, Heineken sites — confirmed, no brewery publishes GTINs). The only real GTINs we have come from Open Food Facts (e.g. Kingfisher `8905002180007`, Tuborg Strong `8906018940104`, Bira 91 Boom `8908005126324`, Budweiser `8902246004984`) and cover a tiny fraction of SKUs. **Design the schema so GTIN is a nullable, best-effort attribute, not a primary key**, and plan a manual/OCR barcode-capture workflow to backfill it over time (own-photograph pipeline), since no external source will hand it to us.
- **Duplicates/near-duplicates are the norm**: `"HEINEKEN SILVER"` appears 3 times across sources with different confidence; `"Kingfisher Premium"` appears from KSBCL, Madhuloka, and UBL with different size-string formats. Search must run over **canonicalized products**, not raw source rows, or ranking will be dominated by whichever brand happens to have the most duplicate scraped rows.

These five facts drive every choice below.

---

## 1. Architecture: Postgres (system of record) + OpenSearch (query layer)

```
┌─────────────────┐   outbox / logical      ┌───────────────────┐
│   PostgreSQL     │   replication (CDC)     │   OpenSearch        │
│  (canonical DB)  │ ───────────────────────▶│  (search index)     │
│  brewery, brand,  │                        │  beers_v1 (alias)   │
│  beer, sku, alias,│                        │  edge-ngram +        │
│  gtin, retailer_  │                        │  phonetic + fuzzy    │
│  listing tables   │◀─── admin curation UI ─│  analyzers           │
└─────────────────┘   writes back to alias   └───────────────────┘
                        table via app, not
                        directly to index
```

**Why not just Postgres `pg_trgm`/`tsvector`?** It's a legitimate MVP-day-one option (see §9, "Day-1 shortcut") and I'd actually start there literally this week given 216 rows. But ValueBrew's stated ambition is pan-India expansion plus a phonetic-matching requirement — Postgres has no phonetic analyzer beyond the crude `fuzzystrmatch` Soundex/Metaphone (English-tuned, poor on Indian brand names), no edge-ngram autocomplete primitive, and synonym/alias handling has to be hand-rolled in SQL. It works at 216 rows and breaks down operationally past ~50-100K SKUs with concurrent facet + fuzzy + autocomplete queries.

**Why OpenSearch over Elasticsearch, Typesense, Meilisearch, Algolia:**
- **OpenSearch** (Apache-2.0 fork of ES 7.10, AWS-managed option available) gives all four hard requirements natively in one engine: edge-ngram tokenizer (prefix/autocomplete), fuzzy queries with Levenshtein automata (typo tolerance), the `analysis-phonetic` plugin (Double Metaphone / Beider-Morse — actual phonetic matching, not just edit-distance), and a synonym token filter (alias table). No licensing cost, no vendor lock (unlike Elastic's post-7.10 SSPL fields or Algolia's per-record pricing).
- **Typesense/Meilisearch** are excellent for #1 (prefix) and #2 (typo tolerance via BK-tree/Levenshtein) with far less ops overhead — genuinely good day-1 alternatives if you want to avoid running a JVM cluster. But neither ships a real phonetic algorithm; you'd be relying on edit-distance to catch sound-alike misspellings, which fails on cases like a consumer typing "Toyt" for "Toit" or "Simbaa" for "Simba" where the edit distance is small anyway (so it's a wash there) but fails harder on genuinely different-looking phonetic collisions (e.g., regional transliteration spellings). Given phonetic matching is explicitly in the spec, OpenSearch is the more defensible choice; Typesense is my fallback recommendation if the team wants zero JVM ops burden and is willing to treat phonetic matching as "mostly covered by typo tolerance."
- **Algolia**: great DX, but per-record/per-search pricing is a bad fit for a data-heavy, low-margin liquor-retail use case at India scale, and it's a black box for the phonetic/synonym tuning this catalog needs.

**Recommendation: OpenSearch, self-hosted or via AWS OpenSearch Service, single 2-node cluster (t3.small) is massive overkill-proof for even 50K SKUs.**

---

## 2. Canonical DB schema (Postgres)

The current 216-row extract is *retailer-listing-grain*, not product-grain. Split it:

```sql
CREATE TABLE brewery (
  brewery_id      BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,             -- 'United Breweries Limited'
  parent_company  TEXT,                      -- 'The HEINEKEN Company'
  karnataka_plant TEXT,                      -- 'Nanjangud, Mysuru' (nullable)
  ksbcl_supplier_code TEXT,                  -- '0210' -- ground-truth join key to KSBCL
  source_confidence TEXT CHECK (source_confidence IN ('High','Medium','Low'))
);

CREATE TABLE brand (
  brand_id        BIGSERIAL PRIMARY KEY,
  canonical_name  TEXT NOT NULL,             -- 'Kingfisher'
  brewery_id      BIGINT REFERENCES brewery(brewery_id)
);

CREATE TABLE beer (                          -- canonical product, size-independent
  beer_id         BIGSERIAL PRIMARY KEY,
  brand_id        BIGINT REFERENCES brand(brand_id),
  name            TEXT NOT NULL,             -- 'Kingfisher Ultra Max'
  style           TEXT,                      -- 'Premium Strong Lager'
  abv             NUMERIC(3,1),               -- nullable, per data gap
  is_flavoured    BOOLEAN DEFAULT FALSE,
  is_nonalcoholic BOOLEAN DEFAULT FALSE,
  data_confidence TEXT CHECK (data_confidence IN ('High','Medium','Low'))
);

CREATE TABLE sku (                           -- the actual purchasable unit
  sku_id          BIGSERIAL PRIMARY KEY,
  beer_id         BIGINT REFERENCES beer(beer_id),
  pack_type       TEXT CHECK (pack_type IN ('bottle','can','pint','tin','draught')),
  size_ml         INTEGER,                   -- normalized: 330, 500, 650 — NOT free text
  pack_count      INTEGER DEFAULT 1,         -- '650ML x 12 Btls' -> 12
  gtin            TEXT UNIQUE,               -- nullable; 890-prefixed when known
  gtin_source     TEXT,                      -- 'openfoodfacts' | 'manual_photo' | NULL
  ksbcl_item_code TEXT,
  UNIQUE (beer_id, pack_type, size_ml, pack_count)
);

CREATE TABLE retailer_listing (              -- raw provenance, one row per source observation
  listing_id      BIGSERIAL PRIMARY KEY,
  sku_id          BIGINT REFERENCES sku(sku_id),
  retailer        TEXT NOT NULL,             -- 'Madhuloka' | 'KSBCL' | 'OnlineAlcohol' ...
  raw_name        TEXT NOT NULL,             -- verbatim scraped string, e.g. 'KF ULTRA MAX'
  price_inr       NUMERIC(8,2),
  observed_at     TIMESTAMPTZ,
  source_url      TEXT
);

CREATE TABLE alias (                         -- THE synonym/abbreviation table — see §4
  alias_id        BIGSERIAL PRIMARY KEY,
  surface_form     TEXT NOT NULL,             -- 'kf', 'bud', 'king fisher'
  target_type      TEXT CHECK (target_type IN ('brand','beer','style')),
  target_id        BIGINT NOT NULL,           -- FK to brand.brand_id or beer.beer_id
  alias_kind        TEXT CHECK (alias_kind IN ('abbreviation','misspelling','transliteration','marketing_alias')),
  weight            NUMERIC(3,2) DEFAULT 1.0,  -- confidence/strength, feeds synonym boost
  UNIQUE (surface_form, target_type, target_id)
);
```

`retailer_listing.raw_name` is deliberately kept verbatim and never cleaned in place — it's the training data for the alias table and for catching new abbreviations retailers invent.

---

## 3. Entity resolution before indexing (critical, not optional)

Given the duplicate problem (`HEINEKEN SILVER` x3, `Kingfisher Premium` from 3+ sources), **do not index `retailer_listing` rows directly**. Run a resolution step that:

1. Normalizes `raw_name` (uppercase-fold, strip punctuation, expand known abbreviations from the alias table — `KF → Kingfisher`, `UB → United Breweries/UB Export`) into a candidate `(brand, beer_name, pack_type, size_ml)` tuple.
2. Matches against existing `beer`/`sku` rows using trigram similarity (`pg_trgm` `similarity()` > 0.6) + exact brand match as a gate.
3. On no match, queues to a human-review inbox (small team, 216 rows — this is a day's work, not an ML project) rather than silently creating a duplicate `beer` row.
4. Rolls `retailer_listing.price_inr` into a `sku`-level `price_range` for display, but keeps per-retailer detail for provenance/drill-down.

Only the resolved `beer`/`sku` rows get pushed to OpenSearch. This alone fixes the "HEINEKEN SILVER appears 3x with different confidence" problem structurally rather than papering over it with search-time deduping.

---

## 4. Alias / synonym table design (this is the core of the UX ask)

Two layers, because they have different update cadences and risk profiles:

### Layer A — curated, versioned synonym file (low volume, high confidence)
Ship as an OpenSearch synonym set (or `synonyms.txt`), covering brand-level abbreviations that are stable and unambiguous. Seeded directly from what we already see in the catalog:

```
# format: comma-separated = equivalence set (bidirectional)
kf, king fisher, kingfisher => kingfisher
bud => budweiser
ub, ub export => united breweries
kbls => kalyani black label
bira, bira91, bira 91 => bira 91
hoegaarden, hogarden, hoegarten => hoegaarden   # phonetic misspellings, belt-and-suspenders with the phonetic field
budwieser, budweisser => budweiser              # exact typo seen in our own catalog (Madhuloka "BUDWIESER TIN")
carlsberg, carsberg => carlsberg
tuborg, toborg => tuborg
```

Note the `budwieser` line is not hypothetical — it's the literal misspelling in the Madhuloka extract (`"BUDWIESER TIN"`). Real scraped-data typos are the best seed list; mine `retailer_listing.raw_name` diffs against resolved brand names monthly and auto-propose new synonym-file entries above a similarity threshold for human sign-off.

### Layer B — the `alias` DB table (dynamic, per-entity, queryable, admin-editable)
This is what "KF Premium" (not just "KF") needs — a *compound* abbreviation that maps to a specific `beer`, not just the brand:

| surface_form | target_type | target | kind |
|---|---|---|---|
| `kf premium` | beer | Kingfisher Premium Lager | abbreviation |
| `kf ultra max` | beer | Kingfisher Ultra Max | abbreviation |
| `kf storm` | beer | Kingfisher Strong (regional naming variant) | abbreviation |
| `bira blonde` | beer | Bira 91 Blonde | marketing_alias |
| `boom` | beer | Bira 91 Boom / Original Bira 91 Boom Super Strong | marketing_alias |
| `1664` | beer | 1664 Blanc | abbreviation |
| `elephant` | beer | Carlsberg Elephant Strong | marketing_alias |

At index time, denormalize this into a **`search_aliases` array field on each document** (not a global synonym filter) — because unlike Layer A, these mappings are per-entity and need to be scoped (e.g. "boom" should only boost Bira products, not act as a global synonym that could collide with an unrelated future SKU named "Boom" from another brewery). This is done via an `input`/`weight` completion field or, more simply, by adding `search_aliases` as a `text` field indexed with the same edge-ngram + standard analyzers as `name`, and querying it with lower boost than the primary name field.

Admin curation workflow: a simple internal screen listing top "raw_name terms with zero/weak matches this week" (from search logs, §7) → one click to add to `alias` table → next reindex picks it up. No ML needed at this scale; this is the highest-leverage, lowest-cost part of the whole system for a 216-SKU catalog and should be built before anything fancier.

---

## 5. OpenSearch index mapping

```json
PUT /beers_v1
{
  "settings": {
    "analysis": {
      "filter": {
        "edge_ngram_filter": {
          "type": "edge_ngram",
          "min_gram": 1,
          "max_gram": 20
        },
        "beer_synonym_filter": {
          "type": "synonym_graph",
          "synonyms_path": "analysis/beer_synonyms.txt",
          "updateable": true
        },
        "phonetic_filter": {
          "type": "phonetic",
          "encoder": "double_metaphone",
          "replace": false
        }
      },
      "analyzer": {
        "autocomplete_index": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "edge_ngram_filter"]
        },
        "autocomplete_search": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding"]
        },
        "synonym_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "beer_synonym_filter"]
        },
        "phonetic_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "phonetic_filter"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "beer_id":        { "type": "keyword" },
      "name": {
        "type": "text",
        "analyzer": "synonym_analyzer",
        "fields": {
          "autocomplete": { "type": "text", "analyzer": "autocomplete_index", "search_analyzer": "autocomplete_search" },
          "phonetic":     { "type": "text", "analyzer": "phonetic_analyzer" },
          "exact":        { "type": "keyword", "normalizer": "lowercase_normalizer" }
        }
      },
      "search_aliases": {
        "type": "text",
        "analyzer": "synonym_analyzer",
        "fields": {
          "autocomplete": { "type": "text", "analyzer": "autocomplete_index", "search_analyzer": "autocomplete_search" }
        }
      },
      "brand":    { "type": "text", "analyzer": "synonym_analyzer", "fields": { "keyword": { "type": "keyword" } } },
      "brewery":  { "type": "text", "fields": { "keyword": { "type": "keyword" } } },
      "style":    { "type": "text", "fields": { "keyword": { "type": "keyword" } } },
      "gtin":     { "type": "keyword" },
      "skus": {
        "type": "nested",
        "properties": {
          "sku_id":     { "type": "keyword" },
          "pack_type":  { "type": "keyword" },
          "size_ml":    { "type": "integer" },
          "pack_count": { "type": "integer" },
          "gtin":       { "type": "keyword" },
          "price_inr":  { "type": "float" }
        }
      },
      "data_confidence": { "type": "keyword" },
      "popularity_score": { "type": "float" },
      "is_available_karnataka": { "type": "boolean" }
    }
  }
}
```

Key design choices:
- `name` is indexed **four ways** simultaneously (standard+synonym, edge-ngram autocomplete, phonetic, exact keyword) — this is the standard "multi-field" pattern that lets one query hit all four requirements in a single `multi_match`/`bool` clause without separate round-trips.
- `skus` is `nested`, not flattened, so a filter on `size_ml=650` doesn't spuriously match a document just because *some other* SKU of that beer happens to be 330ml — nested queries keep the size/pack/gtin/price tuple intact per variant. This directly addresses the "650" / "500 ml" filtering requirement cleanly.
- `gtin` is a plain `keyword` at both beer and sku level, deliberately *not* run through any analyzer — barcode lookup must be an exact `term` query, not full-text (§7).

---

## 6. Query patterns for each required capability

**Autocomplete / prefix (as user types "kingf")**
```json
{
  "query": {
    "bool": {
      "should": [
        { "match": { "name.autocomplete": { "query": "kingf", "boost": 3 } } },
        { "match": { "search_aliases.autocomplete": { "query": "kingf", "boost": 1.5 } } }
      ]
    }
  },
  "size": 8
}
```

**"KF" abbreviation → Kingfisher family**
Resolved via Layer A synonym expansion (`kf → kingfisher`) inside `name`'s `synonym_analyzer` at query time, *plus* Layer B `search_aliases` catching compound forms like "kf premium" as a direct phrase hit with high boost. Both fire in the same query; no special-casing needed at the app layer.

**Typo tolerance ("Budwiser", "Carsberg")**
```json
{ "match": { "name": { "query": "budwiser", "fuzziness": "AUTO", "prefix_length": 1 } } }
```
`fuzziness: AUTO` gives edit-distance 1 for 3-5 char terms, 2 for longer — catches `budwiser→budweiser` (distance 1) and `carsberg→carlsberg` (distance 1) without over-matching short brand tokens like "KF".

**Phonetic ("Toyt" → Toit, "Simbaa" → Simba)**
```json
{ "match": { "name.phonetic": { "query": "toyt", "boost": 0.7 } } }
```
Run as a lower-boosted `should` clause alongside the fuzzy/synonym clauses in one combined `bool` query — phonetic hits rank below exact/fuzzy hits but still surface instead of returning zero results.

**Combined single query** (what the app actually sends per keystroke):
```json
{
  "query": {
    "bool": {
      "should": [
        { "match": { "name.exact": { "query": "<raw_query_lower>", "boost": 10 } } },
        { "match": { "name.autocomplete": { "query": "<raw_query>", "boost": 4 } } },
        { "match": { "name": { "query": "<raw_query>", "boost": 3, "fuzziness": "AUTO" } } },
        { "match": { "brand.keyword": { "query": "<raw_query>", "boost": 3 } } },
        { "match": { "search_aliases": { "query": "<raw_query>", "boost": 2 } } },
        { "match": { "name.phonetic": { "query": "<raw_query>", "boost": 0.6 } } }
      ]
    }
  },
  "function_score": { }
}
```

**GTIN/barcode exact lookup (scan-to-search)**
Bypass the analyzed query path entirely — this must be O(1) exact term lookup, never fuzzy/phonetic (a barcode is either right or it's a different product):
```json
{ "query": { "nested": { "path": "skus", "query": { "term": { "skus.gtin": "8905002180007" } } } } }
```
Given only a handful of SKUs currently have a verified GTIN (per research: Kingfisher, Tuborg Strong, Bira Boom, Budweiser from Open Food Facts), **the app must gracefully fall back to fuzzy name search when the scanned barcode has no index hit**, and log the unmatched barcode to a backfill queue — this will be the common case for now, not the exception.

**Brand/brewery/style/size filter + boost**
Filters go in `bool.filter` (no scoring cost, cacheable); boosts (e.g., "prefer in-stock Karnataka SKUs") go in `function_score`:
```json
{
  "query": {
    "bool": {
      "must": [ { "multi_match": { "query": "kingfisher strong" } } ],
      "filter": [
        { "term": { "brand.keyword": "Kingfisher" } },
        { "nested": { "path": "skus", "query": { "term": { "skus.size_ml": 650 } } } }
      ]
    }
  }
}
```
For a facet UI ("Brand", "Brewery", "Style", "Size"), pair this with `aggs` on `brand.keyword`, `brewery.keyword`, `style.keyword`, `skus.size_ml` so counts update live as filters are applied.

---

## 7. Ranking strategy (function_score, on top of §6's bool query)

```json
{
  "function_score": {
    "query": { "...bool query from §6..." },
    "functions": [
      { "filter": { "term": { "data_confidence": "High" } }, "weight": 1.5 },
      { "filter": { "term": { "data_confidence": "Low" } },  "weight": 0.6 },
      { "field_value_factor": { "field": "popularity_score", "factor": 1.0, "modifier": "log1p", "missing": 0 } },
      { "filter": { "term": { "is_available_karnataka": true } }, "weight": 1.3 }
    ],
    "boost_mode": "multiply",
    "score_mode": "sum"
  }
}
```
Priority order, high to low: **exact name match > prefix/autocomplete match > brand exact match > alias/abbreviation match > fuzzy typo match > phonetic match**, then multiply by confidence and availability weight. `popularity_score` starts as a static seed (national brands like Kingfisher/Bira/Budweiser weighted higher than obscure craft SKUs) and should be replaced with real click/search-conversion signal within the first few weeks of traffic — don't over-engineer this before you have usage data.

**Tie-breaker**: sort ties by `brewery.karnataka_plant IS NOT NULL DESC` — i.e., prefer beers actually brewed/confirmed available in Karnataka (per the UBL/Carlsberg Mysuru research) over nationally-marketed SKUs with unconfirmed Karnataka retail presence (e.g., Arbor Brewing's canned product, which the research explicitly found is "retailing only across Goa" despite the Bengaluru brewpub — don't let that surface above genuinely Karnataka-available SKUs).

---

## 8. Indexing / sync pipeline

Given today's scale (216 SKUs), **do not build Debezium/CDC on day one** — that's premature infra for a founding team. Two-phase plan:

- **Phase 1 (now → first few thousand SKUs, pan-Karnataka)**: nightly batch job (cron) re-exports resolved `beer`+`sku` rows from Postgres, bulk-reindexes into a new `beers_vN` index, then atomically flips the `beers` alias to point at it (zero-downtime reindex pattern). Simple, debuggable, fits a 2-person data team.
- **Phase 2 (pan-India scale, real-time price/availability updates matter)**: move to Postgres logical decoding → Debezium → Kafka → OpenSearch sink connector, so retailer price changes (which will churn constantly once you're scraping dozens of sites) propagate near-real-time without full reindexes.

Trigger reindex on: (a) nightly cron, (b) any `alias` table edit (admin adds a new synonym — should be near-instant, not wait for tomorrow's cron; use `updateable: true` synonym filter and a lightweight `_reload_search_analyzers` call rather than a full reindex for synonym-only changes).

---

## 9. Day-1 shortcut (worth stating explicitly)

If the team wants to ship search *this week* before wiring up OpenSearch: Postgres `pg_trgm` GIN index on a materialized `search_text` column (`name || ' ' || brand || ' ' || COALESCE(search_aliases,'')`), `similarity()` for fuzzy, a hand-written `CASE`-based synonym expansion for the ~15 known abbreviations, and `unaccent`/`fuzzystrmatch` `dmetaphone()` as a crude phonetic bolt-on. This covers 80% of the UX for 216 SKUs with zero new infra. Migrate to OpenSearch once (a) SKU count crosses low thousands, (b) you add other states beyond Karnataka and query volume grows, or (c) the phonetic/synonym tuning outgrows what SQL `CASE` statements can express cleanly. Don't skip straight to OpenSearch if the honest answer is you won't have real traffic for a month — but do build the schema in §2 either way, since that's needed regardless of search engine.

---

## 10. What to log from day one (feeds §4 alias curation + §7 popularity)

Every search request/response pair, specifically: raw query string, zero-result flag, clicked result (if any), and applied filters. Weekly review of the "zero-result queries" list is the single highest-ROI recurring task for this catalog size — it will surface real user shorthand (new brand abbreviations, common Kannada/English code-switch spellings, retailer-specific naming) faster than any amount of upfront synonym engineering, and directly feeds the Layer B alias table in §4.