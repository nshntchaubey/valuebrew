# ValueBrew — Product Definition

*The permanent product definition. Written from the product itself, not the engineering behind it — this document should still be true if every line of code were rewritten tomorrow.*

---

## Part 1 — Product Identity

**ValueBrew is the honest second opinion every beer buyer deserves before they hand over their money.**

**What it is:** a decision companion for one specific moment — deciding which beer to buy, checking whether a price is fair, and understanding what you're actually getting for what you're paying. Grounded in real, government-sourced pricing and real beer facts, not vibes or guesses.

**What it is not:** not a social network, not a ratings or review platform, not an e-commerce or delivery app, not a loyalty program, not a general beer encyclopedia. It teaches, incidentally, but it never exists to be browsed for its own sake.

**Who it's for:** the person who cares enough to want a fair deal and an honest answer — a repeat, price-aware buyer standing in front of a real decision, not someone who'd buy the same brand regardless of what the numbers say.

**Who it's not for:** the pure impulse buyer who decides before opening any app; anyone seeking social validation or peer opinions about beer; anyone trying to buy alcohol *through* the app rather than be better informed *before* buying it; anyone below the legal drinking age.

**What problem it solves:** information asymmetry at the exact point of decision. A shelf full of beer tells you nothing about whether ₹190 is fair, whether the bigger bottle is actually the better deal, or whether the beer in your hand is genuinely different from the one next to it. Every other place you'd check that answer is stale, broken, or quietly contradicts itself.

**What promise it makes every time someone opens it:** *it will never tell you something it doesn't actually know, and it will always tell you why.*

---

## Part 2 — Product Principles

**Always show your work.**
*Why it exists:* a recommendation with no reasoning is indistinguishable from a guess, and the first time it's wrong with no explanation, it's the last time it's trusted.
*What it trades off:* a slightly heavier answer than a bare verdict — more to read, in exchange for something worth believing.
*What would violate it:* showing a recommended beer with no stated reason, or a "why" that's generic boilerplate rather than tied to what the person actually asked for.

**Never blend certainty into one number.**
*Why it exists:* a single score hides exactly the thing a careful buyer needs to know — which part of an answer is a fact and which part is a judgment call.
*What it trades off:* simplicity. A "94% match" is easier to design around than an answer that's honest about being partly certain and partly not.
*What would violate it:* any feature that reduces confidence to a single star rating, percentage, or blended score.

**A tie is an honest answer, not a failure.**
*Why it exists:* forcing a winner between two genuinely equivalent options is a lie dressed as helpfulness.
*What it trades off:* sometimes the satisfying, decisive answer isn't available, and the product has to say so plainly.
*What would violate it:* any logic that manufactures a winner to avoid an "unsatisfying" tie.

**Never claim more than what was actually checked.**
*Why it exists:* a comparison between two named beers is not a claim about every beer in existence, and pretending otherwise erodes trust the moment someone finds the exception.
*What it trades off:* less impressive-sounding language, in exchange for language that survives scrutiny.
*What would violate it:* any wording implying catalog-wide authority from a bounded comparison.

**Silence is better than a guess.**
*Why it exists:* an invented fact looks identical to a verified one right up until it's wrong — and by then the damage is done.
*What it trades off:* some answers will show a visible gap ("ABV not yet confirmed") that a less careful competitor would simply make up.
*What would violate it:* filling an unknown field with a plausible-sounding estimate and presenting it as fact.

**Restraint, always invited, never imposed.**
*Why it exists:* a person checking a price doesn't want to be funneled into a comparison or recommendation they didn't ask for, however "helpful" the app thinks it's being.
*What it trades off:* the app sometimes withholds a genuinely useful next step because it wasn't invited to offer it.
*What would violate it:* any hand-off between checking a price, getting a recommendation, and comparing two beers that fires automatically instead of on explicit request.

**Price is a fact, not a feeling.**
*Why it exists:* the product's core credibility rests on price being a verifiable, government-sourced number — never an estimate, a "typical" figure, or a vibe.
*What it trades off:* sometimes the honest legal price and the price on the shelf disagree, and the app has to say so plainly rather than smoothing it over.
*What would violate it:* presenting an estimated or crowd-guessed price with the same visual weight as a verified legal one.

---

## Part 3 — User Moments

**Standing at the shelf, no plan.**
*Mindset:* overwhelmed by choice, wants a quick, defensible answer. *Information needed:* budget, maybe a style preference. *Desired outcome:* one clear pick, or an honest tie, in seconds. *Emotional outcome:* confident, not second-guessing the choice on the walk to the register.

**Already holding a specific beer, wondering if it's a good pick.**
*Mindset:* "I like this — am I about to overpay, or is this actually fine?" *Information needed:* price, ABV, how it stands against its own style. *Desired outcome:* a quick confirm, or a gentle "there's a better option," without being told what to do. *Emotional outcome:* reassured, or informed — never scolded.

**Checking if a charged price is fair.**
*Mindset:* mild suspicion — "did they just overcharge me?" *Information needed:* the government-legal reference price for this exact SKU. *Desired outcome:* a clean, unambiguous answer: below, at, or above. *Emotional outcome:* vindicated if right to have checked, glad they checked if not — either way, in control.

**Comparing two specific beers already in mind.**
*Mindset:* deciding between two known options, not open to a third. *Information needed:* the facts side by side, and an honest trade-off or tie if there's no clean winner. *Desired outcome:* either a confident pick or an honest "these are equivalent — pick by taste." *Emotional outcome:* settled, not steered.

**Planning ahead of a purchase.**
*Mindset:* less urgent, more exploratory — wants a plan to carry into the store, not an instant answer. *Information needed:* the same as an unplanned decision, framed as provisional. *Desired outcome:* a recommendation with an honest caveat that prices may have shifted by the time they get there. *Emotional outcome:* prepared, not falsely certain.

**Buying for someone else.**
*Mindset:* less personal knowledge of what the recipient wants, wants a safe, defensible default. *Information needed:* budget, maybe occasion — nothing assumed the app doesn't actually know. *Desired outcome:* a low-risk, easy-to-justify pick. *Emotional outcome:* relieved of the responsibility of guessing wrong.

**Discovering something new.**
*Mindset:* curious, low-stakes browsing rather than an urgent decision. *Information needed:* honest facts about something unfamiliar, not hype. *Desired outcome:* a reason to try it, grounded in something they already like. *Emotional outcome:* intrigued, not sold to.

**Learning why.**
*Mindset:* curious about the reasoning itself, not just the verdict. *Information needed:* the same explanation the product already generated, surfaced on demand. *Desired outcome:* understanding. *Emotional outcome:* a little smarter, never talked down to.

---

## Part 4 — Core Experiences

**The Honest Verdict.** *Why it matters:* this is the moment ValueBrew replaces guesswork with a defensible answer. *What success feels like:* relief and confidence, not analysis paralysis. *What the user walks away knowing:* exactly which beer fits what they said they wanted, and why — in words they'd repeat to a friend.

**The Fairness Check.** *Why it matters:* the single highest-trust capability the product has — a government-backed fact, not an opinion. *What success feels like:* quiet vindication, or grateful surprise. *What the user walks away knowing:* whether they were charged fairly, in plain terms, with no ambiguity.

**The Full Picture.** *Why it matters:* gives someone everything knowable about a beer they're already holding or considering, without pushing them anywhere. *What success feels like:* quiet completeness — nothing left to wonder about. *What the user walks away knowing:* the real facts behind a beer they might otherwise have judged only by the label.

**The Honest Trade-off.** *Why it matters:* this is where ValueBrew refuses to manufacture false certainty between two real options. *What success feels like:* clarity, even when the honest answer is "it's a genuine tie." *What the user walks away knowing:* specifically what's different between the two beers, and whether that difference actually matters to them.

---

## Part 5 — Product Intelligence

Not fields. Categories of knowledge — the things ValueBrew must actually understand about a beer for its answers to be worth trusting:

**Identity knowledge.** What this beer actually is — brand, style, and the exact purchasable unit (size, container) — enough to know when two listings are the same real thing and when they're not.

**Economic knowledge.** What it actually, officially costs, and how that compares per unit of alcohol against its peers — the real value math, not just a sticker price.

**Composition knowledge.** What's actually in it — alcohol content, at minimum — the fact that makes "value" a meaningful concept instead of just "cheap."

**Comparative knowledge.** How this beer stands relative to its own category — typical, better, or worse than its peers. This is knowledge that only means something in relation to other beers, never in isolation.

**Provenance and confidence knowledge.** Where a given fact came from, and how sure the product actually is of it. This is knowledge *about* the knowledge — and it's what lets the product be honestly uncertain instead of falsely confident.

**Freshness knowledge.** When a fact was last confirmed true. A price with no age attached is a fact pretending to be more permanent than it is.

**Availability knowledge.** Whether this is something a person can actually go buy, right now, somewhere real. Without this, everything else is trivia, not a decision aid.

This is the foundation catalog enrichment work should be measured against — not "how many fields are populated," but "how many of these seven categories does this beer's data genuinely satisfy."

---

## Part 6 — Trust

**Recommendations** always arrive with their reasoning attached, in the same breath, never as an afterthought. **Uncertainty** is shown, not hidden — a low-confidence answer should look visibly different from a high-confidence one, not identical with a smaller asterisk. **Explanations** are specific to what the person actually said, never generic boilerplate that could apply to any answer. **Confidence** is never collapsed into a single reassuring number — what's known and what's judged stay visibly separate. **Transparency about freshness** means a stale price is labeled stale, never presented as current just because it's the only figure available. **Mistakes** are handled by disclosure, not deflection — a wrong price or a data gap should be easy for a user to report and easy for them to see get corrected, never buried or quietly patched with no acknowledgment.

Trust compounds slowly and is lost instantly. One confidently wrong answer costs the product more than ten honestly uncertain ones.

---

## Part 7 — Delight

The moment the app says "these two are genuinely the same value — stop deliberating" and hands someone permission to just pick.

The moment a price check confirms a good deal, and the app is essentially high-fiving someone with facts instead of flattery.

The moment the "why" behind a recommendation names something specific a person actually said — proof the app was listening, not running a template.

The moment someone discovers a beer they'd never have picked is quietly better value than their usual — a small, evidence-backed act of discovery, not a sales pitch.

The quiet satisfaction of a product that never oversells itself, and is right more often precisely because it doesn't.

---

## Part 8 — Product North Star

*A one-page manifesto. Timeless — it should still describe ValueBrew if every line of code changed tomorrow.*

ValueBrew exists because a person standing in front of a shelf, or a screen, deserves an honest answer about their money — and almost nothing in that moment currently gives them one.

We are not building the biggest beer app, or the most entertaining one, or the one with the most beers listed. We are building the one that never lies to make itself look smarter. When we know something, we say it plainly. When we don't, we say that too. When two things are genuinely equal, we say so, even though a confident, made-up winner would feel more satisfying in the moment. That restraint is not a limitation of the product — it is the product.

Every answer ValueBrew gives carries its own reasoning, because an answer without a reason is just an opinion wearing a badge. Every number it shows carries its own confidence, because certainty that isn't earned is a debt that comes due the first time it's wrong. Every price it states is a fact, sourced from something real, never a guess dressed up to look like one.

We measure ourselves not by how impressive our engine sounds, but by whether a real person, standing in front of a real decision, trusted us enough to act on what we said — and came back the next time they needed to decide again. That is the only success that has ever mattered here, and it is the only one that ever will, no matter what this product looks like, runs on, or expands into next.

ValueBrew is not trying to be the loudest voice in the room. It is trying to be the one voice you'd still trust after checking it against everything else — every single time.
