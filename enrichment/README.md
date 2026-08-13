# enrichment/

The Beer Knowledge Base — the human-curated repository of everything ValueBrew knows about a beer that `pricing_data/beer_master.csv` structurally cannot contain: ABV, Style, brewery-as-marketing-identity, images, and every future curated field. See `docs/BEER-KNOWLEDGE-BASE-ARCHITECTURE.md` for the full specification and `docs/CATALOG-ENRICHMENT-PLAYBOOK.md` for the day-to-day workflow of actually doing this work.

## Layout

```
enrichment/
  README.md          # this file
  styles.yaml         # the full style vocabulary — one flat file, not one-per-style
  beers/
    <beer_key>.yaml    # one file per real Beer — every pack size it comes in, together
  candidates/
    <canonical_product_id>.yaml   # raw, per-SKU drafts — see below
```

## `beers/` vs. `candidates/`

**`beers/<beer_key>.yaml`** is the real, canonical Beer Knowledge Base — exactly the schema Beer Knowledge Base Architecture Part 3 defines. Every file here represents one real Beer (a name, brewery, style, ABV) grouping one or more `canonical_product_id`s at different pack sizes. This is what the Catalog Builder actually reads.

**`candidates/<canonical_product_id>.yaml`** is not part of that schema and is never read by the Catalog Builder. It's a generated starting point — one draft per SKU-grain `canonical_product_id`, pre-filled with the objectively-known identity fields (`item_name_raw`, `display_name`) and explicit `null`/TODO placeholders for every curated field. Deciding which candidates are genuinely the same real beer, and folding one or more of them into a real `beers/<beer_key>.yaml` file, is a human act — nothing in this repository infers that grouping automatically (Catalog Implementation Architecture Part 2, Catalog Enrichment Playbook Part 2).

Regenerate `candidates/` at any time from the current `pricing_data/beer_master.csv` via `python -m tool.catalog_builder.generate_enrichment_candidates` — it's fully disposable and gets overwritten, never hand-edited.

## Editing `beers/`

See the Catalog Enrichment Playbook for the full workflow. In short: never guess a fact — mark it `unknown` instead; every curated fact carries a real citation (`source_type`/`source_name`/`observed_at`/`observed_by`); validate before you commit.
