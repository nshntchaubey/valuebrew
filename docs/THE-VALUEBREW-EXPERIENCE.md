# The ValueBrew Experience — Definitive End-to-End Specification

*Every interaction a person has with ValueBrew, from deciding to buy a beer to leaving the store, reconstructed from the shipped Version 1 app, the Canonical Architecture, the Product Brain, and the full history in Evolution of ValueBrew. Nothing here is invented — every screen, rule, and boundary traces to an existing canonical document or the actual V1 build. Gaps in what's currently built are named honestly, not papered over.*

---

## How This Document Is Organized

The journey branches at exactly one point — whether the person already has a specific beer in mind (**Anchor-Known**) or not (**No-Anchor**) — and reconverges at Beer Detail. Every step below carries the same eight-part analysis the brief asked for. Where a prior generation handled the same moment differently, that's named explicitly, not smoothed over.

---

## Before the App Opens: The Moment of Deciding to Check

A person is either standing at a shelf with beer already in front of them, or thinking ahead of a trip they haven't made yet. Either way, something has made them doubt their own instinct enough to reach for a second opinion — uncertainty about price, unfamiliarity with a brand, or just wanting to make sure before spending money.

**What the user is trying to achieve:** resolve a specific doubt, fast, before or during a purchase.
**What ValueBrew knows:** nothing yet — no prior session, no account, no memory of this person ever existing.
**What ValueBrew does not know:** who this is, what they bought last time, what they usually like, whether they've used the app before at all.
**What decision the product makes:** none yet — the app hasn't rendered anything.
**Why:** the canonical Product Definition Document's founding rejection of accounts means every session starts genuinely blank — this isn't a missing feature, it's the product refusing to assume continuity it hasn't earned.
**Trust principle exercised:** none yet is exercised more strongly than "never claim more than what's actually known" — the app would rather know nothing than guess who's opening it.
**What's withheld:** any greeting, any "welcome back," any assumption of prior context.
**Under uncertainty:** there is no uncertainty here — the app is simply, honestly, starting from zero, every time.

*Generational note: Generation 1 built Favorites specifically so a "welcome back" moment could eventually exist. That moment was never built, and the underlying signal it would have needed was removed entirely when accounts were rejected. A returning user gets no continuity today — a real, felt trade, made deliberately.*

---

## Step 1 — Home: Capturing Intent

The app opens to a single screen with one job: figure out, from what the person actually says, which of three paths they need — a recommendation, a specific beer they already have in mind, or a price to check.

**What the user is trying to achieve:** express what they need without having to know the app's internal categories first.
**What ValueBrew knows:** nothing about this person; only the fixed set of intents the canon recognizes.
**What ValueBrew does not know:** whether "I want something good under 200 rupees" means they have zero preference beyond budget, or whether they're about to name a specific brand.
**What decision the product makes:** Home performs zero reasoning of its own — it classifies the expressed intent and routes, nothing else.
**Why:** the ADR's own accepted decision is explicit — Home owns routing and nothing else, and is the only screen that never reaches a completed decision on its own.
**Trust principle exercised:** restraint — Home never guesses ahead of what's actually said, and never funnels someone toward a path they didn't ask for.
**What's withheld:** any recommendation content, any beer facts, any price — none of the sixteen canonical information objects belong on this screen.
**Under uncertainty:** if the expressed intent is ambiguous, exactly one clarifying question is asked — never zero, never a second one. If the intent is clearly outside what the app does at all, it says so plainly and names its four real capabilities, rather than forcing the person into the nearest-fitting path.

*Generational note: Generation 1's Home doubled as the search entry point itself — typing a beer name there went straight to results. Today's Home routes toward Recommendation and Price Verification cleanly, but the "I already know what I want, let me just find it" path — the thing Gen 1's fuzzy search already solved — has no screen to route to. This is the single most consequential gap in the entire journey, and it surfaces right here, at the very first screen.*

---

## Branch A — "I don't know what to buy yet": The Recommendation Journey

### Step 2A — The Budget Question

**What the user is trying to achieve:** get a specific answer without having to think in the app's own terms — they just want to say what they'd spend.
**What ValueBrew knows:** nothing about this person's taste yet; the full real catalog of SKUs, each with a real, government-verified price.
**What ValueBrew does not know:** style preference, whether this is for themselves or someone else, whether they'd trade a little more money for a specific style.
**What decision the product makes:** budget is asked first because it's a Hard Constraint — nothing that violates it can ever be shown, so it has to be known before anything else is worth asking.
**Why:** the Recommendation Screen Contract's own threshold rules — a question is only justified if its answer could actually change which candidate wins, and budget is the one input that eliminates the most candidates fastest.
**Trust principle exercised:** progressive disclosure — the app asks for exactly what it needs next, not a form up front.
**What's withheld:** every SKU's identity and price stays hidden until a real candidate set can be shown honestly.
**Under uncertainty:** if the number given could plausibly mean something other than budget (a size, for instance), this is one of the canon's own named open gaps — currently unresolved, not silently guessed at.

### Step 2B — The Optional Style Question

**What the user is trying to achieve:** narrow toward something they'd actually enjoy, without being forced to answer if they don't care.
**What ValueBrew knows:** the budget-filtered candidate set.
**What ValueBrew does not know:** whether narrowing by style would actually change the outcome yet — this determines whether the question is even asked.
**What decision the product makes:** the question fires only if two or more candidates remain genuinely indistinguishable on everything already known, and the answer would actually separate them. If one candidate already dominates, this question is skipped entirely — asking it anyway would be a delay dressed as diligence.
**Why:** the Decision Engine Model's own forbidden case — "the question would touch an input already unnecessary" — asking a question that can't change the outcome is explicitly disallowed.
**Trust principle exercised:** never asking more than is needed to answer honestly.
**What's withheld:** nothing yet — this is genuinely the last gate before an answer.
**Under uncertainty:** if the person doesn't answer or explicitly declines, the app proceeds with what it has rather than blocking.

### Step 3A — The Outcome: A Clean Winner

**What the user is trying to achieve:** a confident, specific answer.
**What ValueBrew knows:** exactly one SKU dominates on every known Hard and Strong input.
**What ValueBrew does not know:** anything about taste dimensions never asked about (occasion, exact flavor preference) — deliberately never inferred.
**What decision the product makes:** show the winning SKU, its Explanation, and its Confidence — together, in the same moment, never one before the other.
**Why:** the ADR's Accepted decision that Explanation always accompanies Recommendation, with no exception, and that Confidence is never collapsed into a single blended figure.
**Trust principle exercised:** explainability and confidence honesty simultaneously — the answer states which inputs it's certain about (price, ABV — Verified/Computed Facts) separately from anything resting on stated preference.
**What's withheld:** no numeric score, no percentage, no "94% match" — the Lexicon forbids exactly this kind of false-precision language.
**Under uncertainty:** not applicable here — this is the confident-outcome path by definition.

### Step 3B — The Outcome: A Genuine Tie

**What the user is trying to achieve:** still wants an answer, even if the honest one isn't a single winner.
**What ValueBrew knows:** two or more candidates are equal on everything the person actually stated as mattering.
**What ValueBrew does not know:** which of the tied candidates they'd prefer on a dimension nobody asked about or that isn't tracked at all (packaging aesthetics, brand loyalty).
**What decision the product makes:** disclose the tie plainly, as a complete, legitimate answer — never manufacture a winner to avoid an unsatisfying-feeling response.
**Why:** the ADR's Accepted decision that ties are accepted as legitimate, complete outcomes, directly citing the Recommendation Framework's rejection of forcing an arbitrary tiebreak.
**Trust principle exercised:** this is the single clearest, most concrete demonstration of "silence is better than a guess" in the whole product — the honest answer here costs the product a moment of feeling less decisive, and it takes that cost on purpose.
**What's withheld:** any invented tiebreaker, any "we'd slightly recommend X" hedge that isn't actually backed by anything the person said.
**Under uncertainty:** this *is* the uncertainty made visible — the tie itself is the honest representation of it, not a failure state requiring further probing.

*Generational note: Generation 1's `RecommendationEngine` had no tie concept at all — `similarBeers`/`betterValueAlternatives` always returned a ranked list, and `BeerDetailScreen` always surfaced a single highest-value SKU as "the" pick. Today's Tie Disclosure is a genuine improvement over Generation 1, not a lateral change — it's the product refusing to do something Generation 1 did unquestioningly.*

### Step 3C — The Outcome: No Recommendation Exists

**What the user is trying to achieve:** an answer, even a disappointing one.
**What ValueBrew knows:** either nothing satisfies the stated budget at all, or too little is known to meaningfully distinguish among a large field.
**What ValueBrew does not know:** whether relaxing the budget or answering more questions would resolve it — this is exactly what Recovery is for.
**What decision the product makes:** two distinct Recovery conditions, never merged — Conflicting Constraints (a stated Hard Constraint and Strong Preference together exclude everything, both named plainly) versus Low-Confidence Response (too little is known, so the app asks for the single most useful next input or offers a clearly labeled provisional answer).
**Why:** the Recommendation Screen Contract's own precise definition of when a recommendation does not yet exist — two distinct failure shapes, each requiring a different honest response.
**Trust principle exercised:** graceful degradation under uncertainty rather than either forcing a bad answer or going silent.
**What's withheld:** a manufactured "close enough" pick that quietly violates the stated budget.
**Under uncertainty:** this entire step *is* the product's uncertainty-handling mechanism made visible to the user.

### The Planning-Mode Variant

**What the user is trying to achieve:** the same recommendation, but they're not standing in a store yet — they're getting ready to go.
**What ValueBrew knows:** the same candidate data, but with an explicit signal that prices may have shifted by the time this is actually acted on.
**What ValueBrew does not know:** the exact price at the moment of purchase, which hasn't happened yet.
**What decision the product makes:** the same recommendation flow, with a standing caveat present from the very first response through every subsequent one — never collapsed into a one-time disclaimer that's easy to forget.
**Why:** the Home Screen Contract's own framing — Planning is a flagged variant of the same transition, not a fourth destination, and the caveat's persistence is an explicit Acceptance Criterion.
**Trust principle exercised:** honest time-boundedness — the app never implies more certainty about the future than it has.
**What's withheld:** nothing extra — the same information, with its confidence honestly qualified by time.
**Under uncertainty:** the entire mode *is* the uncertainty being honestly carried forward, not resolved away.

---

## Branch B — "I already know what I want": The Anchor-Known Journey

**What the user is trying to achieve:** confirm or learn about a specific beer they're already holding or have already decided on.
**What ValueBrew knows:** once identified, everything the catalog has on that exact SKU.
**What ValueBrew does not know, right now, structurally:** *how the person actually gets to that SKU in the first place.* This is the one honest, acknowledged gap in the entire journey — Search/Browse Results, the screen that would let someone type or browse toward a specific beer, has no canonical Screen Contract at all. It's the single Open, non-Accepted decision in the entire Architectural Decisions Record.
**What decision the product makes:** none — there is no decision to make, because there is no built path here today. In the current shipped app, the only way to reach a specific beer's detail is by way of a Recommendation's own hand-off (tapping through from a recommended or tied SKU).
**Why this gap exists rather than being resolved:** it's explicitly, honestly named in the canon as "a sequencing gap in how the canon was built," not a deliberate removal.
**Trust principle exercised, even in the gap:** the product doesn't paper over this with a fake search box that silently does something else — it simply doesn't claim a capability it doesn't have.
**What's withheld:** nothing is hidden here — the gap itself is the honest state.
**Under uncertainty:** there's no mechanism to be uncertain within yet, because the screen doesn't exist.

*Generational note: this is the sharpest instance in the whole journey of Evolution of ValueBrew's central finding — Generation 1 already had a working, tested, fuzzy-match search screen. It was cut for MVP discipline, then never re-specified when everything else was rebuilt more rigorously. Anyone building this gap closed should treat Generation 1's implementation as a working reference, not a blank page.*

### Step 4 — Beer Detail: The Full Picture

However the person arrives here (today, always by way of a Recommendation hand-off), this is the screen that has to answer everything knowable about one specific beer.

**What the user is trying to achieve:** understand exactly what they're looking at, completely, before deciding anything further.
**What ValueBrew knows:** Beer Identity, Legal Price, Alcohol Content, Size, Alcohol-Adjusted Value, and — where a benchmark exists for this style — Style Benchmark standing (better/typical/worse than peers).
**What ValueBrew does not know:** whether the person already likes this beer, whether they're comparing it against something else in their head, or what the shop actually charges (that's a separate, explicit request away).
**What decision the product makes:** show everything on this list, at uniformly high confidence, and nothing beyond it — no Soft-preference-driven content ever appears here, because none of it is Recommendation's business.
**Why:** the Beer Detail Screen Contract's own composition — every fact here is Verified or Computed, never a judgment call, which is why this screen's confidence never needs the Hard/Strong/Soft split Recommendation requires.
**Trust principle exercised:** completeness without overreach — this screen answers "what is this" exhaustively, and refuses to answer "should I buy it" (that belongs to Confirm-as-Is, discussed next) or "is this a good deal right now" (Price Verification).
**What's withheld:** Observed/Charged Price never appears here, under any condition — that number only ever exists inside Price Verification, by design.
**Under uncertainty:** if the Style Benchmark isn't available for this beer's style yet, it's simply, gracefully omitted — never treated as an error, never a placeholder that implies something's broken.

### Confirm-as-Is — What Would Happen, and Why It Doesn't Yet

**What the user is trying to achieve:** a quick reassurance that a beer they've already chosen is actually a solid pick, without going through the full Recommendation flow again.
**What ValueBrew knows, in principle:** the same facts as the rest of Beer Detail.
**What ValueBrew does not know:** the exact rule that would determine *when* this judgment should even surface — this is itself a named, unresolved canonical gap.
**What decision the product makes today:** none — this feature is not built. It's blocked on two things at once: the anchor-known entry path (the same Search/Browse gap above) doesn't exist to trigger it, and even if it did, surfacing it via a Recommendation hand-off would duplicate content the Recommendation itself already stated, violating the canon's own anti-duplication rule.
**Why the canon still describes it:** it's a real, specified Feature belonging to the Recommendation Module's logic — deliberately demoted from ever having its own independent entry point, per an early Feature Inventory correction the ADR records explicitly.
**Trust principle exercised:** the same restraint principle as everywhere else — rather than build a rough version of this that would need to guess at its own trigger condition, the product simply doesn't build it until the trigger is genuinely known.
**What's withheld:** the confirming judgment itself, entirely, for now.
**Under uncertainty:** the uncertainty here isn't about the answer — it's about *when to even ask the question*, and that's exactly what remains unresolved.

### Step 5 — Leaving Beer Detail: Two Legitimate Endings

**What the user is trying to achieve:** either move on to check a price or compare, or simply be done, satisfied with what they now know.
**What ValueBrew knows:** the person has seen everything the screen has to offer.
**What ValueBrew does not know:** whether "done" means "I'll buy this" or "I've decided against it" — and it doesn't need to know, because it never asks.
**What decision the product makes:** Decision Complete is reached either way — through an explicit next action, or simply by the person walking away satisfied. Both are treated as legitimate, not one as a "real" completion and the other as an abandoned flow.
**Why:** the Beer Detail Screen Contract explicitly names both paths as valid — "the lighter completion path, legitimate in its own right."
**Trust principle exercised:** the product doesn't demand a closing action to consider itself successful — it doesn't need a "conversion event" to have done its job.
**What's withheld:** any prompt, nudge, or "are you sure?" interruption on the way out.
**Under uncertainty:** there's no ambiguity here to resolve — both endings are equally honest.

---

## Step 6 — The Fairness Check: Price Verification

Reached only by explicit request, from Beer Detail, never automatically — this is the single highest-trust capability in the entire product.

**What the user is trying to achieve:** find out, plainly, whether what they're about to pay (or already paid) is fair.
**What ValueBrew knows:** the SKU's government-published Legal Price, sourced from KSBCL, the one number in the entire product with the strongest evidentiary grounding.
**What ValueBrew does not know:** the actual price the retailer will charge or has charged — that has to come from the person, entered explicitly, every time.
**What decision the product makes:** classify the entered charged price as below, at, or above the legal reference — a clean, three-way, unambiguous verdict.
**Why:** the ADR's own Accepted decision — Price Verification stays isolated and never escalates, even following an overcharge finding, precisely to keep this one answer uncontaminated by any upsell impulse.
**Trust principle exercised:** "price is a fact, not a feeling" — this is the one place in the product where a number is never softened, estimated, or blended with anything else.
**What's withheld:** any recommendation, any comparison, any suggestion of an alternative — even when the answer is "you were overcharged," the product doesn't pivot to "here's what you should buy instead" unless explicitly asked, separately, afterward.
**Under uncertainty:** the Screen Contract's own flagged, still-open gap — how an imprecise or approximate charged price should be handled — is explicitly not resolved by inference. The current build does not silently round or guess; this remains a named limitation, not a hidden one.

*Generational note: Generation 1's Beer Detail carried a visible provenance strip — "price confirmed 2 days ago by 3 people" — a freshness signal shown directly to the user. The current Price Verification has no equivalent freshness indicator at all; the Legal Price is treated as simply, unconditionally current. This is a real difference in trust model, not just a feature gap — Generation 1 leaned on visible, crowd-sourced recency; the current generation leans on a single authoritative government source with no visible age. Whether that source's own freshness should ever be surfaced to the user the way Generation 1 surfaced it is a genuinely open question worth deciding on purpose, not by default.*

### Returning to Beer Detail

**What the user is trying to achieve:** see the broader context again after checking a price.
**What decision the product makes:** the hand-off carries only the SKU identity forward — the charged price the person just entered is never carried with it, by explicit rule.
**Why:** the Navigation Contract's own stated principle — a fact is referenced across a screen boundary, never re-hosted, and Observed/Charged Price specifically is never persisted or displayed outside Price Verification under any condition.
**Trust principle exercised:** minimal, deliberate forgetting — the product doesn't accumulate a shadow history of what someone paid, even within one session.

---

## Where the Journey Would Continue, If Built: Comparison

If the person instead wants to weigh two specific beers against each other rather than check one — a real, frequent moment ("Priya the Host," dating back to Generation 1's earliest personas, still holds) — this is where Comparison belongs. It is fully specified. It is not yet built into the shipped app.

**What the user would be trying to achieve:** a direct answer between two named options, not a fresh search.
**What ValueBrew would know:** exactly the candidates handed to it — never more, since Comparison never searches the catalog on its own.
**What ValueBrew would not know:** anything about a beer not named in the comparison — and it would never claim to.
**What the product would decide:** a winner, a Trade-off Explanation, or a Tie Disclosure — with per-candidate and result-level confidence kept as two distinct, never-merged layers.
**Why:** the Comparison Screen Contract's own validation rule — Comparison can conclude Beer A is better than Beer B; it can never claim to have found the best beer in existence, because it never looked past the two it was handed.
**Trust principle that would be exercised:** the same restraint as Recommendation's tie-handling, applied to a bounded, explicitly-scoped question instead of an open-ended one.
**What would be withheld:** any implication that the comparison result generalizes beyond the named candidates.
**Under uncertainty:** at most one clarifying question, ever — if that doesn't resolve it, a genuine Trade-off or Tie is the honest answer, never further probing.

*Generational note: Generation 1's Compare screen already existed — simple, read-only, no scoring. The canonical Comparison specification is a genuine improvement over it, not a lateral rebuild: it adds Trade-off Explanation and Tie Disclosure, both ideas Generation 1 never had anywhere in its own Compare screen. This is the clearest case in the whole product's history of a rebuilt idea actually getting better, not just getting rebuilt.*

---

## Leaving the Store: What ValueBrew Carries Forward

**What the user is trying to achieve:** nothing further from the app — the decision is made, the purchase is done.
**What ValueBrew knows, at this final moment:** exactly what it knew when the session started, plus nothing — no record of what was recommended, what was verified, what was compared, or what was decided.
**What ValueBrew does not know, permanently, by design:** who this person is the next time they open the app.
**What decision the product makes:** none — the session simply ends, and nothing is written anywhere that persists it.
**Why:** the Product Definition Document's founding rejection of accounts, carried through every generation of the canon without exception, and directly responsible for the removal of Generation 1's Favorites feature.
**Trust principle exercised:** the same one that opened this entire document — never claim more than what's actually known, applied to the product's own memory of the person, not just its claims about beer.
**What's intentionally withheld:** everything. There is no purchase history, no favorite list, no "last time you checked this beer" — not because it wasn't thought of, but because Generation 1 built exactly that anticipatory signal once, and it was deliberately, permanently removed.
**What happens when the product is uncertain about whether this trade-off is worth it:** it isn't uncertain — this is one of the few genuinely settled, permanent decisions in the entire history, revisited and reaffirmed rather than questioned every time it comes up.

---

## The Full Journey, End to End

```
Decide to check (no memory of you exists)
        │
        ▼
      Home ── one clarifying question, at most, if ambiguous
   ┌────┴────┐
   │         │
No anchor   Anchor known
   │         │        (Search/Browse gap — no screen exists yet)
   ▼         ▼
Budget    [today: unreachable directly —
 │         only reached via a Recommendation hand-off]
 ▼
Style (only if it would change the outcome)
 │
 ▼
┌─────────────────────────────────────────┐
│ Winner · Tie · No-match (Conflicting /    │
│ Low-Confidence) · Planning-mode variant   │
└──────────────────┬────────────────────────┘
                    ▼
              Beer Detail ── Full Picture, uniformly high confidence
                    │            (Confirm-as-Is: specified, not built)
        ┌───────────┼───────────────┐
        ▼           ▼               ▼
  Price Verification  [Comparison:   Leave, satisfied
  (explicit request     specified,    (equally legitimate
   only, never auto)    not built]    ending)
        │
        ▼
  Below / At / Above verdict
  (charged price never carried forward)
        │
        ▼
  Back to Beer Detail, or done
                    │
                    ▼
          Leaves the store —
    everything the app knew is gone
```

---

## What This Document Is Not Claiming

Two gaps run through this entire journey honestly, not hidden: **Search/Browse Results** has no canonical screen at all, which means the Anchor-Known path only exists today as a hand-off destination, never a true entry point — and **Comparison** and **Confirm-as-Is** are fully specified but not yet built into the shipped app. None of these are failures of this document or of the product — they're the same honest, disclosed limitations the canon itself has always named, carried through faithfully here rather than smoothed over to make the journey read more complete than it currently is.
