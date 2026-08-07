# KSBCL Stage 4 — User Mental Model

### Not architecture, not a database document, not an implementation document. One question: when a ValueBrew user thinks they're looking at "a beer," what should they actually experience? Reasoned entirely from the user's seat, using the Product Identity Charter as the starting frame. Internal pipeline mechanics appear only where they'd leak into what the user sees.

**Status note:** the conclusion below on `supplier_code`'s placement is now also the recorded product decision — see `KSBCL-Stage-4-Identity-Decision.md`, the single authoritative source.

---

## Seven journeys

For each: what does the user expect to still be "the same beer," and what do they expect to be a genuinely different one.

### Searching for a beer

A user types "Kingfisher Strong." They expect a short, recognizable list of *choices* — not a wall of near-duplicates. "Kingfisher Strong 330ml Can" and "Kingfisher Strong 650ml Bottle" read as two legitimate results, because picking a size is a real decision the user makes. Seven results that differ only by which company supplied that particular batch would read as broken — the same beer listed seven times, not seven beers.

**Same beer:** different supplier, same size/container. **Different beer:** different size, different container.

### Comparing two beers

Comparing "Kingfisher Strong" against "Tuborg Strong" only feels fair if both sides are pinned to a matched size — comparing a 330ml can's price to a 650ml bottle's price without normalizing feels like a rigged comparison, not a helpful one. But the user comparing them has no reason to know or care which supplier is behind either side's price — that's invisible plumbing to a comparison, not part of what's being compared.

**Same beer:** any supplier, matched size/container. **Different beer:** different size/container.

### Seeing multiple prices

This is the journey where supplier stops being invisible and becomes actively useful — but not as separate products. "Kingfisher Strong 650ml Bottle: ₹125 near you, ₹145 elsewhere, ₹190 at a third location" is exactly the information a price-comparison feature exists to surface, and it only makes sense presented as *one beer, several current prices* — the way a flight search shows one route with several fares underneath it, not seven separate flights. If this information were instead split into seven separate beer cards, the feature that most needs supplier variance to be useful would be the one place it looks like a bug.

**Same beer, multiple listings:** this is precisely where a layered structure — one product, several supplier-level prices beneath it — stops being a design nicety and becomes what the feature requires to work at all.

### Seeing regional availability

A user in one district and a user in another both think they're looking at "Kingfisher Strong 650ml" — they just see different availability and pricing depending on which supplier serves their area. Neither user experiences "a different beer that happens to share a name"; they experience the same beer with local availability. This is the journey where the earlier open question from the Charter — are differently-supplied listings actually the same specification — mattered most directly to the user: the entire "available near you" framing implicitly promises "it's the same beer, just sourced locally." That question is now settled by product-owner decision (`KSBCL-Stage-4-Identity-Decision.md`): listings are treated as the same canonical product by design. The risk this journey names is therefore a known, accepted consequence of that decision, not a silent gap.

### Viewing recommendations

"You might also like" should suggest genuinely different beers — a different brand or style — not a different size of the beer the user is already looking at. Nobody wants "Kingfisher Strong 330ml Can" recommended to them as a discovery while they're already looking at the 650ml bottle; that's not a recommendation, that's the same product in another size, and belongs on the product's own page as an option, not in a "you might also like" rail. Supplier is invisible here too — nobody wants "Kingfisher Strong, but from a different supplier" recommended as if it were a new beer to try.

**This is where the coarser, brand/style-level grouping from the Charter earns its keep** — recommendations naturally operate one level up from purchasable-unit identity, grouping *across* sizes and containers of a family, never fragmenting by supplier.

### Viewing beer details

One detail page should represent one purchasable thing — a specific size and container, since that's the actual decision a shopper is making. What belongs *on* that page, without needing its own page: current price(s) and availability broken down by supplier/region (journey 3), and a clearly separate "also available in" cross-link to sibling sizes of the same family (journey 5). What must never happen: the page silently showing one supplier's price as *the* price with no indication others exist, or splitting into multiple pages purely because multiple suppliers exist.

### Viewing future price history

This is the journey that most concretely decides the question. A user looking at "how has this beer's price changed" expects one continuous, sensible line. Now consider what happens if supplier is *not* preserved as its own thing beneath the beer, and instead each month's chart point is silently drawn from whichever supplier happens to be "the" price that month: the line would jump from ₹125 to ₹190 to ₹145 and back — not because the real beer's price is genuinely volatile, but because the chart is secretly hopping between different suppliers' listings every time the underlying selection changes. That's not a price history, it's noise wearing a price history's clothes, and it would actively mislead a user into thinking a stable product's price is chaotic when it isn't.

**This is the strongest single argument in this document.** A trustworthy price-history feature requires supplier-level listings to keep their *own* independent, continuous history — which only works if supplier was never collapsed into "the beer" in the first place, but was always a distinct thing living beneath it.

---

## What this means for `supplier_code`

Every journey points the same direction, and none point the other way:

- Search, comparison, recommendations, and the detail page all want supplier to be **invisible or secondary** — never a reason to show the same beer twice.
- Seeing multiple prices and regional availability want supplier to be **visible, but as a listing under one beer**, not as the beer itself.
- Price history **requires** supplier-level continuity to be preserved independently, or the feature breaks in a way that actively misleads users.

No journey wants `supplier_code` to define a *different beer*. Several journeys need supplier-level information to still exist and stay independently trustworthy. Those two facts together only have one shape: **`supplier_code` is an attribute of a listing beneath canonical identity, never a component of canonical identity itself.** This is also the recorded product decision (`KSBCL-Stage-4-Identity-Decision.md`); the journeys above are the user-experience case for it, not a separate, competing conclusion.

This resolves more than just "in or out." The Charter's now-resolved question — whether differently-supplied listings are genuinely the same specification or not — turns out to matter *less* once this layered shape is adopted, not more. Either way, the user still sees one canonical beer with clearly attributed listings beneath it; if it's ever confirmed that a particular supplier's listing is meaningfully different, that becomes a labeling/disclosure decision on that one listing (e.g., a "contract-brewed by X" note), not a reason to have split the beer into a separate product in the first place. The layered model is the one shape that degrades gracefully regardless of which way that open question eventually resolves.

---

## The shape this implies

**Canonical product** = the thing every non-price-history, non-comparison-shopping journey treats as stable: brand + style + size + container. This is what a search result, a recommendation, and a detail page are *about*.

**Listing** = a supplier's current offer of that canonical product — its own price, its own availability, its own history over time. This is what journeys 3, 4, and 7 need to exist independently and stay trustworthy.

A canonical product can have one listing or several; the user never needs to know or care which, until the moment they're comparing prices or checking availability — at which point seeing several is exactly the point.

Nothing here specifies how a listing is represented, stored, or computed — that is Stage 4 architecture's job, not this document's. What's settled is only the shape the user experience requires: **two layers, not one**, with `supplier_code` living in the lower one.
