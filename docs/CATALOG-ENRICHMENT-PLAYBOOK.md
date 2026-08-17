# ValueBrew — Catalog Enrichment Playbook

*An operating manual, written for one founder doing this work by hand. Not architecture — every rule below already exists somewhere in Catalog Builder Architecture, Catalog Implementation Architecture, Catalog Contract 1.0, Catalog Specification 1.0, Beer Knowledge Model 2.0, or the Product Decisions Register. This document does not add a single new decision to any of them. It answers a narrower question: what do you actually do, today, sitting down to turn a row in `beer_master.csv` into a beer someone can trust.*

---

## Part 1 — Overall Philosophy

You're doing this because the machine genuinely can't. `pricing_data/beer_master.csv` — KSBCL's own government price list, run through the pipeline — has a price, a size, a container type, and a legally-supplied name for every real beer sold in Karnataka. It has **no ABV, no style, and no brand identity distinct from the licensed supplier.** Not because nobody built that yet — because the source document itself doesn't contain it. No brewery in India routinely publishes a machine-readable price list. No retailer reliably lists ABV. This was all confirmed directly, source by source, before any of this architecture was written — it isn't a guess.

So there are two kinds of fact in this catalog, and you need to know which one you're touching at every moment. **Automated extraction** is what the pipeline already did for you: price, size, container, the fact that this SKU legally exists. You never touch this. It's already Verified. **Human judgment** is everything the pipeline structurally cannot produce: what ABV this actually is, what style it belongs to, what a person would recognize as the brewery. You produce this, by hand, every time, and it's called Curated — not because it's less trustworthy than Verified, but because it comes from a different kind of evidence: a label you read, a page you checked, not a government filing.

**Never guess. Mark it unknown instead.** A wrong ABV is worse than a missing one — it corrupts the one number the whole app is built around. An honestly-missing fact just means that beer waits one more cycle. Keep that asymmetry in your head every time you're tempted to estimate.

---

## Part 2 — Lifecycle of One SKU

Follow one real row through the whole system, start to finish.

1. **It's a row in `beer_master.csv`.** Machine-produced. Has a price, a size, a `canonical_product_id`, nothing else useful to a person deciding whether to buy it.
2. **You notice it's not enriched yet.** Either you're working through the file top to bottom, or `enrichment_queue.py` told you.
3. **First human touchpoint: does this beer already have a file?** Check `enrichment/beers/` for one whose `canonical_product_ids` list this row's `canonical_product_id`, or whose name is obviously the same beer at a different pack size. If yes, you're just adding this SKU to an existing file. If no, you're creating a new one — you're the one deciding a `beer_key` for it. This decision — which SKUs are "the same beer" — exists nowhere else. Nothing upstream can make it for you.
4. **Second human touchpoint: research.** Style, ABV, brewery identity — Part 4 through Part 6 cover exactly how.
5. **Third human touchpoint: you write the YAML.** Fill in what you found, cite where it came from, note the date.
6. **Fourth human touchpoint: you check it against the quality checklist (Part 7)** before you consider it done.
7. **It sits in `enrichment/` until the next catalog build.** You don't personally run the join, the computation, or the validation — that's the Catalog Builder's job, already fully specified elsewhere. Your work ends the moment the YAML is correct and committed.
8. **The build either includes it or rejects it, with a reason.** If it's rejected, that reason comes back to you — go fix whatever it flagged, don't fight the validator.
9. **It's in `catalog.json`.** Done, until KSBCL republishes next month and you check whether anything about this beer actually changed.

Nine steps. Five of them are you. That's the whole system.

---

## Part 3 — Daily Workflow

**Batch by research type, not alphabetically.** Twenty beers in one sitting goes faster if you do all twenty ABV lookups in a row, then all twenty style calls, than if you fully finish one beer before starting the next — you stay in one mode of attention instead of context-switching every few minutes.

**A realistic session, 20 beers:**
1. **Triage (5 minutes).** Pull 20 unenriched rows from `beer_master.csv`. Skim the names. Group them: which ones are brands you already know well (Kingfisher, Tuborg, Bira — you can move fast), which ones need real research (an unfamiliar craft brand, an import).
2. **Beer-family grouping (5–10 minutes).** For each group, decide: is this a new beer, or another pack size of one you've already enriched? Create empty `beer_key` files now for the genuinely new ones, so you're not doing this decision mid-research later.
3. **Research pass (the bulk of the time — see Part 4).** Work through Style, then ABV, then Brewery, for the whole batch, in that order — Style is fastest to resolve (a small fixed list, often obvious from the name), ABV takes longest (needs a real citable source), Brewery is usually already sitting right there in `beer_master.csv`'s supplier field.
4. **Write it down as you go**, not after — a source you checked five minutes ago is easy to cite accurately; a source you checked an hour ago, from memory, is not.
5. **Run `validate_enrichment.py`** (or its manual-checklist equivalent, Part 7, until that tool exists) against everything you just wrote.
6. **Commit.** One commit per session is fine at this volume — you don't need to commit per-beer. What matters is that every commit is enrichment-only, never mixed with anything else you happen to be touching in the repo that day.

**Validation rhythm:** validate before you commit, every time, not once a week. A malformed YAML file caught the moment you write it costs you thirty seconds. The same file caught during a monthly catalog build costs you a build failure and a context switch back into work you've already mentally closed.

**Commit rhythm:** small, frequent, enrichment-only commits beat one giant "enriched 200 beers" commit. If you made a real mistake on beer #47, you want to revert one file's worth of history, not untangle it from 199 others.

---

## Part 4 — Research Workflow

**Where to look, in order, and stop the moment you have a real answer — don't keep searching past a good source out of habit.**

1. **The can or bottle itself, if you physically have one.** The single best source that exists. A label is Manufacturer-tier evidence, full stop.
1a. **A clear, legible photograph of the manufacturer's own printed label also qualifies as manual observation.** You must personally verify that the photograph matches the exact beer and pack size being enriched — never trust the hosting page's own title or category alone. The evidence is the photographed manufacturer label itself, not the website or app hosting it; `source_name` must identify the specific photograph (or the specific page containing it), never the general site. This does not widen what counts as evidence beyond the manufacturer's own label — a retailer's written description, a nutrition table, or a figure from Untappd, BeerAdvocate, RateBeer, a blog, or any similar source remains unacceptable evidence, exactly as before.
2. **The brewery's own official site.** Look for the specific product page — not a generic "our beers" listing. This is your primary source for ABV and calories when you don't have the physical product in hand.
3. **Check whether you've already enriched a sibling pack size of this same beer.** `beer_master.csv` does not carry a supplier/brewery field of any kind — confirmed directly against its real columns, corrected here after an earlier version of this playbook wrongly said otherwise. Brewery has no automated starting point at all; it's researched the same way as everything else in this list. If another pack size of this exact beer already has a real `enrichment/beers/*.yaml` file, its `brewery` value is your fastest, already-cited starting point — otherwise, treat Brewery like any other fact: find it, cite it, write it down.
4. **A retailer listing (Madhuloka, or whichever retailer you're already cross-checking against) — for corroboration only, never as your first or only source.** Retailers routinely show brand, size, and price but not ABV, and their category tagging is not reliable enough to settle a Style question on its own.
5. **Anything else — a review site, a forum, a general web search — is a last resort, and if that's all you can find, the honest answer is Unknown, not "close enough."**

**When to stop searching:** the moment you have one citable, Manufacturer-tier source. You do not need two sources to agree before you can record a fact — corroboration is nice, not required. What you do need is a source you could point to later and say exactly where this came from.

**When to mark Unknown:** after a genuine, real attempt at steps 1–3 above turns up nothing. Not after step 1 alone. Not after a single failed Google search. A beer marked Unknown today isn't lost — it's just not in this build. It'll still be sitting there next cycle, and a better source might exist by then. Publishing a guess to avoid an Unknown is strictly worse than leaving it out — it doesn't just fail to help, it actively corrupts the one number (Value Score) this whole product exists to get right.

---

## Part 5 — ABV Collection Playbook

**ABV is the one field where getting it wrong actually breaks something, not just looks incomplete — treat it with real care.**

**How to verify.** Manufacturer's own page, or the physical label, always. If the beer has a `size_ml` that's genuinely a different SKU from the one the brewery's page describes (a 500ml can vs. a 650ml bottle) — check whether the brewery states ABV per-product or per-pack-size. Most beers have one ABV across every pack size of the same product; some genuinely don't (a draught version can differ slightly from the packaged one). If you're not sure which situation you're in, record it at the Beer level (applies to every SKU) unless you have a specific, cited reason to override one SKU.

**How to resolve conflicting sources.** If the brewery's own site says one number and a retailer says another, **the brewery wins, always** — it's the manufacturer, the retailer is just repeating a number it got from somewhere. If two *different* manufacturer-tier sources genuinely disagree with each other (the brewery's website says one thing, the physical can in front of you says another) — trust the physical can. A website can be stale after a reformulation; the can in your hand is the actual product. Record which one you used and why, in the `source_name` field — don't just silently pick one and move on.

**Confidence rules.** Every ABV you record is Curated — a Manufacturer-sourced fact you personally observed and cited, never Verified (KSBCL never states it, so it can never carry that tier no matter how confident you are) and never a plain scalar with no source attached. If you can't attach a real `source_name` and an `observed_at` date, you don't actually have the fact yet — you have a guess wearing a fact's clothing. Don't record it.

**One habit worth building now, cheap today, expensive to reconstruct later:** always write down the date you checked, even though it feels unnecessary when everything's fresh. Six months from now, "was this ABV ever reformulated" is a real question, and "I checked this on 2026-08-12" is the only thing that lets you answer it honestly instead of re-researching from scratch.

---

**Calorie collection, briefly, since the fact shape differs from ABV.** Record calories using the same sources and the same Part 4 search order, but the field you're filling — `calories_per_100ml` — wants exactly the number a source publishes, never one you've done arithmetic on. A manufacturer's own page almost always states calories as a concentration ("37 kcal per 100ml"), not a per-can or per-bottle total — write down that concentration figure directly. The Catalog Builder computes each SKU's actual per-pack total automatically at build time; you never need to multiply by pack size yourself, and doing so would silently record the wrong thing under the wrong field name. Same Unknown discipline as ABV: no citable source, no number.

---

## Part 6 — Style Assignment Playbook

**How styles should be chosen.** Pick from `enrichment/styles.yaml`'s existing list first. It's meant to stay small — a few dozen entries, not hundreds — so before adding a new style, check whether an existing one genuinely fits. "Strong Lager" is a real, distinct style from plain "Lager" (materially different ABV range, different peer group for Value Score comparison) — that's a legitimate new style. "Kingfisher Ultra" being slightly different from "Kingfisher Premium" is not a new style question at all — that's two different Beers, possibly the same style.

**Only add a new style when an existing one would genuinely misrepresent the beer's peer group** — remember, Style exists specifically to define who a beer gets compared against for Value Score. Two lagers of noticeably different strength shouldn't share a benchmark; two lagers from different breweries at the same strength should.

**Edge cases, handled plainly rather than agonized over:**
- **A flavored variant** (a lemon lager, a fruit-infused wheat beer) — style follows the base beer style unless the flavoring genuinely changes what it should be compared against. When in doubt, use the base style; a flavored lager competing on value against other lagers is a defensible comparison, and inventing a "flavored lager" style for one SKU usually isn't worth the fragmentation.
- **A beer whose name contains a style word that isn't its real style** — the exact trap that let real spirits into the pipeline's own beer classification (a whisky called an "IPA Experiment" because it was cask-finished in IPA barrels). Read what the product actually is, never just pattern-match on a word in its name. This is worth the extra thirty seconds every single time.
- **A genuinely novel craft style you don't recognize** — this is exactly when the physical can/label (Part 4, source #1) earns its keep; craft breweries usually state their own style intent directly on the packaging, more reliably than any external source would guess at.
- **No confident style at all, even after real research** — mark it Unknown, same discipline as ABV. A beer can still exist in the enrichment file with everything else filled in; it just won't get Style Standing until this resolves, and Recommendation's style-refinement step won't be able to use it. This is a known, already-accepted gap (Product Decisions Register D20) — not something this playbook is asking you to solve, only to handle honestly when you hit it.

**Consistency rule, the one that matters most over time:** before assigning a style you haven't used in a while, skim a couple of existing beers already assigned to it. Consistency across the whole catalog matters more than any single beer's classification being perfectly argued — a Value Score is only meaningful if "Lager" means the same thing for beer #4 as it does for beer #400.

---

## Part 7 — Quality Checklist

**Launch-Critical — a beer cannot enter the catalog build without every one of these:**
- [ ] Beer identity (name, cleaned up, not just the raw KSBCL string)
- [ ] Brewery (at minimum, the licensed-supplier name — already sitting in `beer_master.csv`)
- [ ] Style, from the existing `styles.yaml` vocabulary (or explicitly, honestly Unknown — see Part 6)
- [ ] ABV, cited to a real Manufacturer source with a date (or explicitly, honestly Unknown — see Part 5)
- [ ] Size and package type already correct from the pipeline — just confirm they look sane, don't re-derive them
- [ ] Legal Price already correct from the pipeline — same, just a sanity glance
- [ ] Every `canonical_product_id` this beer file lists actually appears in the current `beer_master.csv` (a stale reference from a prior month is a real, catchable mistake)

**Recommended, not blocking — worth doing, never worth holding a beer back over:**
- [ ] An image, if you have one with a license you're actually sure of (Product Decisions Register D15 hasn't settled whether this is required — treat it as nice-to-have until it does)
- [ ] `is_craft` set correctly rather than left at its default
- [ ] A second corroborating source for ABV, if one was easy to find (not worth extra searching purely to get this)

**The one-question test before you move on to the next beer:** if someone else on this project opened this file six months from now with no memory of writing it, could they tell exactly where every fact came from and when? If yes, you're done. If you'd have to guess or re-research to answer that, you're not.

---

## Part 8 — Review Workflow

**Self-review, the cheapest and most important layer.** Before committing a batch, re-read each file once, cold — not while you're still deep in the research mindset that produced it. A five-minute gap between writing and reviewing catches more real mistakes than reviewing immediately, because you're reading it the way a stranger would.

**Spot checks, on a rhythm, not just when something feels off.** Every so often — once a week is reasonable at real volume — pick two or three already-enriched beers at random and re-verify them from scratch, as if you'd never seen them before. This catches the mistakes self-review structurally can't: a source that seemed right at the time but wasn't, a style call that made sense in isolation but looks wrong once you've enriched fifty more beers and built better intuition.

**Catalog Builder validation is the layer that catches everything else, mechanically, every time.** This is not optional and not something you personally need to double-check by hand — `validate_enrichment.py` and the full build's validation gate (Catalog Builder Implementation Design, Part 6) exist specifically so you don't have to manually verify things like "does this ABV fall in a plausible range" or "does this style reference actually exist" every single time. Trust it. If it blocks a beer, the fix is almost always in your YAML, not a false alarm worth arguing with.

**What actually catches a real mistake, layered, in the order it's likely to happen:** self-review catches typos and obviously-wrong values you'd notice on a second read. Spot checks catch a source that was subtly wrong or a judgment call that hasn't aged well. The Catalog Builder's own validation catches anything structural — a dangling reference, a value outside the allowed set, a duplicate ID — regardless of whether you or a reviewer would have caught it by eye. None of these three layers is a substitute for the other two.

---

## Part 9 — Scaling

**This same workflow, unchanged, from 100 beers through 2,000 — the architecture was already built for this, so this playbook doesn't need a different version at each size, only a different pace.**

**At 100 beers (roughly where the launch catalog starts):** everything in Parts 3–8 as written, at a pace of maybe two or three real sessions like the one in Part 3. You'll personally remember most of what you enriched, so spot checks (Part 8) can be light.

**At 500 beers:** the workflow doesn't change, but two habits start to matter more than they did at 100. First, batching (Part 3) becomes more valuable, not less — you'll be doing enough repeated lookups (the same brewery's product line, say) that grouping work by research type saves real time. Second, spot checks need to become a genuine habit with a fixed cadence, not an occasional impulse — at 100 beers you'd probably notice a bad entry eventually just by using the app; at 500, you won't.

**At 2,000 beers:** still the same workflow — one founder, one file per beer, the same five human touchpoints from Part 2 — but this is roughly the point where `enrichment_queue.py` stops being a nice-to-have and starts being how you actually find out what still needs attention, rather than scanning `beer_master.csv` by eye. **This is not a new tool this playbook is introducing** — it already exists and is already in daily use well before 2,000 beers; this is simply the scale at which relying on it, rather than working by eye, becomes the obviously correct call.

**What never changes, at any of these sizes, and is worth stating plainly:** you are still the one deciding Style and ABV for every single beer. This workflow does not get automated as it scales — Catalog Builder Architecture already established why (Part 1 of that document), and nothing about volume changes that reasoning. What scales is how you organize your own time doing it, never who does it.

---

## Part 10 — Founder Operating Principles

**Speed vs. correctness: correctness wins, every time, but speed is still real and worth protecting deliberately.** The way you protect both at once is by not re-litigating the same judgment call repeatedly — once you've decided how to handle a flavored variant (Part 6), don't re-debate it for the next one; apply the same rule and move on. Consistency is what lets you go fast without going careless.

**Unknown vs. guessed — the single most important distinction in this entire playbook, worth internalizing until it's automatic.** An Unknown is honest, costs nothing beyond a beer not being fully ready yet, and can be fixed the moment a real source turns up. A guess dressed as a fact is a landmine — it looks exactly like real data to everyone downstream (the Catalog Builder, the app, a person reading a Value Score) until the day it's wrong, and by then it's already shaped a recommendation someone acted on. When you're not sure which one you're about to write down, you already know the answer: it's a guess. Mark it Unknown instead.

**When to stop researching:** the moment you have one real, citable, Manufacturer-tier source (Part 4). Not when you've exhausted every possible source — when you have *one that's actually good*. Chasing a second or third confirming source for a fact you already have solid evidence for is time better spent on the next beer.

**How to avoid perfectionism, concretely, not just as advice:** remember that nothing you write here is permanent in the way it might feel while you're writing it. Every enrichment file is a plain-text, git-tracked, easily-revised record — Catalog Implementation Architecture built this whole system on exactly that assumption (Part 1's own immutable-vs-mutable-facts discipline: your Curated judgment today can always be superseded by better evidence later, without that ever implying today's version was careless). You are not making one irreversible decision per beer. You're making the best decision available from what you can actually find right now, writing down exactly how you got there, and trusting the system to let you — or someone else — improve it later with no penalty for having been honestly incomplete today.

---

## Part 11 — Physical Evidence Fieldwork

**[RC6.0 note, 2026-08-15 — Superseded, historical only]:** the founder subsequently issued a standing, explicit instruction that physical fieldwork will never be part of this project, superseding this Part's entire premise. RC3.1–RC3.9's remote-only research arc then directly refuted the claim right below that remote research "genuinely runs out" for ABV specifically — real, cited manufacturer ABV was recovered for 7 beers/29 SKUs entirely via web research, with no fieldwork. The finding held up better for calories, which really did remain unrecoverable remotely across every brewery RC3 investigated. This Part is preserved below as a historical record of the tooling built for a phase the project no longer pursues, not as current guidance — do not act on it.

**When remote research stops being the right next step.** Parts 4–5 above describe desk research — a brewery's own site, a global brand database, an official page. For a real, meaningful share of beers, that research genuinely runs out: the manufacturer's own site exists, is reachable, and simply has never published ABV or calories for that specific product. That is not a failure of searching harder — some facts are not on the internet at all, and the only source left is the physical product itself, exactly as Part 4's own item 1 already ranked highest. Three tools exist to make that fieldwork phase as organized as the desk-research phase already was:

**`photo_queue.py` — what to go buy, in what order.** Ranks every Beer still blocked on `missing_abv`/`missing_calories` by how many real SKUs a photo would actually unlock — reusing the exact same join → business rules → cross-reference pipeline every other tool in this system already trusts, so this list changes automatically as evidence lands, never by hand-editing a spreadsheet. **[RC6.0 correction: since Product Decisions Register D22, `missing_calories` no longer appears as a `business_rules.py` rejection reason at all — it's a warning on an already-published SKU. A beer blocked only by unknown calories, with ABV known, is already publishable and correctly does not appear in this queue; it only still lists beers genuinely blocked by `missing_abv`. The tool's own code (`_FIXABLE_REASON_CODES`, `photo_queue.py`) and docstring were not updated to reflect this — they still describe the pre-D22 behavior. This is real, live documentation/tooling drift, not merely a historical note; see the RC6.0 final report's technical-debt list.]**

```
python3 -m tool.catalog_builder.photo_queue --top 10
python3 -m tool.catalog_builder.photo_queue --brewery "AB InBev" --missing-calories
```

**`photo_checklist.py` — what to actually photograph, for one beer.** Prints front label, back label, nutrition panel, ABV declaration, and an optional barcode — skipping any step for a fact already on file (a beer missing only calories doesn't ask you to re-photograph an ABV you already have), and ending with the exact `update_beer.py` command to run once you're back at your desk.

```
python3 -m tool.catalog_builder.photo_checklist --beer-key tuborg_strong_premium
```

**`photo_progress.py` — where the whole repository stands.** A dashboard, not a queue: how many Beers are fully publishable, how many are only waiting on a photo, how many still have a genuinely unresolved identity question (never a photo problem — see the module's own docstring for exactly how it tells the two apart), and how many are otherwise fully evidenced but blocked by something structural a photo can't touch.

```
python3 -m tool.catalog_builder.photo_progress --list
```

**The evidence policy does not change for fieldwork — it is the same one Part 4 already states.** A photo satisfies `manual_observation` under exactly the two conditions Part 4 item 1a already set: you personally confirm the photo matches this exact beer and pack size, and you cite the specific photo — not the general site — in `source_name`. `photo_checklist.py` prints both conditions every time, not as a reminder you can skim past, but as the actual gate between a photo and a recorded fact.

---

## Part 12 — Rejected-Evidence Workflow

**[RC7.7 addition, 2026-08-17]** — approved RC7.6, infrastructure built RC7.7. Full schema and field-by-field detail: `docs/BEER-KNOWLEDGE-BASE-ARCHITECTURE.md` Part 11. This Part covers only the operational question — when and how you actually use it, sitting down doing real research.

**When to record one.** Any time Part 4's research turns up a real, on-topic value you decide *not* to use. Not every failed search — a source that simply had nothing is not rejected evidence, it's just a source that didn't help. Record one specifically when you found *something citable* and had a real reason to set it aside: a retailer's ABV that turned out to be for the wrong pack size, a brewery page whose figure looked suspiciously imprecise, a second source that conflicted with one you'd already trust more. If you're not sure whether what you just saw rises to this bar, ask yourself the same question Part 4 already asks about Unknown: could you point to this later and say exactly what you found and why you didn't use it? If yes, it's worth recording.

**Why bother, when you could just move on.** Because you — or someone else — will hit the same dead end again. A rejected retailer figure you don't record gets re-found, re-read, and re-rejected next month, at the exact same cost it took the first time. Recording it once means the next research pass sees it was already checked and can skip straight past it.

**How.**

```
python3 -m tool.catalog_builder.record_rejected_evidence \
  --subject-type beer --subject-key kingfisher_premium --field abv \
  --value-found "5.2" \
  --source-type manual_observation --source-name "Madhuloka product listing, 21 Aug 2026" \
  --reason-type wrong_variant \
  --reason-detail "Listing's ABV is for the Strong variant; this SKU is the standard Premium." \
  --observed-by founder
```

`--observed-at` defaults to today; add `--recheck-after YYYY-MM-DD` when the rejection reason (`access_blocked`, most often) implies it's worth looking again later. The command refuses to write anything that fails validation — a `--subject-key` that doesn't resolve to a real `beer_key`/`brewery`, an unrecognized `--reason-type`, or a duplicate of an entry already recorded (same subject, field, source, value, and reason) all fail loudly, before anything is written, the same discipline `create_beer.py`/`update_beer.py` already use.

**Reason taxonomy, quick reference** (`wrong_variant`, `wrong_product_line`, `access_blocked`, `imprecise_value`, `incompatible_unit`, `conflicting_source_subordinate`) — full definitions in the Architecture doc's Part 11; pick the one that actually describes why you rejected it, not just the first one that seems close.

**Append-only, same as everything else this playbook asks you to trust the tooling for.** Never hand-edit `enrichment/rejected_evidence.yaml`. Use the command above for every new entry, the same discipline Part 3's validation-before-commit rhythm already asks of everything else you touch in `enrichment/`.

**This file is currently empty of historical entries, on purpose.** RC7.7 built the recording infrastructure only — it did not, and was explicitly instructed not to, invent or reconstruct the rejected-evidence cases from before it existed. If you're the one who remembers a real historical rejection from before this tooling existed, don't hand-write it into the YAML — that's exactly the "never hand-edit" rule above. Record it through the command like any other entry, or hold it for the dedicated RC7.8 backfill pass if you're gathering several at once.
