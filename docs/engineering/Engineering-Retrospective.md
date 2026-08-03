# ValueBrew — Engineering Retrospective

**Repository path:** `docs/engineering/Engineering-Retrospective.md`
**Status:** Closed — the permanent engineering record for the canonical rebuild, Home → Recommendation → Beer Detail → Price Verification, through Milestone 8.
**Relationship to the rest of this folder:** distinct from `Version-1-Architecture-Reference.md`, which describes *what was built*. This document describes *how it was built* — the engineering process, the decisions that survived, the ones that changed, and the mistakes the review process caught. Where the two overlap, the Architecture Reference is authoritative for current behavior; this document is authoritative for engineering history and is never updated to track new work.

---

## Architectural evolution

**The starting problem.** Before the canonical rebuild, this repository already contained a working app — a browse/filter/sort/search/favorites application with a profile-based recommendation engine (`recommendation/{models,policy,services,scoring}`). That code wasn't wrong, but it wasn't built against any Screen Contract, because no Screen Contracts existed yet. The rebuild's first job wasn't to add a feature — it was to give the product a governing layer the old code never had.

**`ValueBrewNavigator` (pre-session, extended throughout).** The first canonical commit introduced a navigator that owns every screen transition, one method per legal edge, resolved through a shared `GlobalKey<NavigatorState>` rather than `BuildContext`. This solved a problem the legacy code never had to solve, because it never had a Navigation Contract to be consistent with: once transitions are governed by a document, something has to be the single place that document's rules are actually enforced in code, or drift between "what the contract says" and "what the app does" becomes invisible. This established the convention every later milestone extended without exception — Beer Detail's edge (M3), Price Verification's edge (M4), the `isPlanning` flag (M6), and Price Verification's return edge (M8) all landed as one new method each, never a change to the pattern itself.

**Home + Recommendation domain (pre-session).** Home was built to do nothing but route, and `generate_recommendation.dart` was built as pure Dart with zero Flutter dependency. This solved the problem of keeping reasoning testable independent of rendering — a distinction the legacy `recommendation_engine.dart` blurred by mixing scoring logic with profile-provider state. Established convention: domain logic lives in its own file, under its own feature's `domain/` folder, importable and testable without pumping a widget.

**Milestone 3 — Beer Detail.** Solved the problem of a recommendation being a dead end: once `generateRecommendation` returned a SKU, there was nowhere to see its full facts. This is where `catalog_lookups.dart` was born as the sole lookup owner (`resolveBeer`, `resolveStyle`, later `resolveSku`) — a direct response to the legacy code's pattern of resolving IDs inline, differently, in more than one place. Established convention: one null-returning lookup function per relationship, owned in one file, never duplicated. Every later milestone (`resolveBenchmark` in M7) extended this file rather than inventing a second lookup owner.

**Milestone 4 — Price Verification.** Solved the problem of price-fairness being entirely unaddressed, despite being the single highest-confidence capability in the canon. This is where the shared loading/error convention (`ErrorStateView`, `SkeletonBox`) was proven a second time on a genuinely different screen, and where a real defect (a bare `Padding` risking overflow once a keyboard appears) was caught and fixed *before* the second commit of the same milestone — evidence the review discipline was already operating within a milestone, not only between milestones.

**Milestone 5 — Tie Disclosure.** Solved a problem the Recommendation Framework names directly: forcing an arbitrary pick when two SKUs are genuinely equal misrepresents what the engine actually knows. This is where `RecommendationOutcome` grew a fourth sealed subtype (`RecommendationTie`) rather than a boolean flag on the existing one — established the convention that a genuinely new *kind* of outcome gets its own type in the exhaustive switch, not a parameter bag on an existing type, so the compiler forces every renderer to handle it.

**Milestone 6 — Planning Mode.** Solved the problem of a provisional recommendation looking identical to a confident one. This is where a capability was added as a *flagged variant of an existing transition* (`isPlanning` on `homeToRecommendation`) rather than a new edge — directly citing the Home Screen Contract's own language ("not a fourth distinct destination"). Established the convention that not every new behavior earns a new navigator method; some earn a parameter on an existing one, and the difference is decided by the canon's own framing, not by implementation convenience.

**V1 readiness fixes.** Solved two problems that only became visible once enough milestones existed to compare against each other: `RecommendationScreen`'s loading/error handling had quietly diverged from the `ErrorStateView`/`SkeletonBox` convention established at M3–M4, and two doc comments described already-shipped behavior as unbuilt. Neither was wrong when written — both became wrong as the surrounding repository moved past them. This is where "a stale doc comment describing shipped behavior as unbuilt" was first named as a recurring pattern, one that recurred five more times before this retrospective.

**Version 1 release.** Solved the problem of pre-existing, never-tagged release artifacts describing a completely different application. This is where the project's discipline was tested against a genuinely ambiguous situation — the repository evidence alone couldn't say whether those artifacts were abandoned work or real prior release history, so the answer was asked rather than guessed. When commits were finally created, real `git diff` inspection revealed `value_brew_navigator.dart` and `recommendation_screen.dart` had accumulated changes from three or four different milestones in non-separable hunks, forcing the original 11-commit plan down to 7 — an architecture decision made from evidence encountered mid-execution, not from the plan as originally conceived.

**Milestone 7 — Style Benchmark.** Solved the problem of Beer Detail's own Screen Contract naming a MUST-clause requirement (Style Benchmark, "when available") that had never been built, using data (`Benchmark`, with `p25`/`p50`/`p75`) that had been sitting fully modeled and completely unused since before this session began. This is where a self-imposed architecture review caught the project inventing detail the canon never asked for — the original four-band design was rejected in favor of the smallest classification that still matched the canon's own worked example, using `p50` alone.

**Milestone 8 — Price Verification → Beer Detail.** Solved the last fully-specified, contradiction-free gap in the five-screen navigation graph. Notable not for what it built (the smallest milestone in the project, by lines changed) but for what its own kickoff caught: a stated premise ("Milestone 7 has already been... committed") that `git status` immediately proved false.

**Milestone 9 discovery.** Concluded, independently and for the first time, that no further milestone exists — every remaining canonical capability traces to a missing, contradictory, or explicitly deferred piece of canon, not to unfinished engineering. This is the point the architectural evolution described above stops, by design.

---

## Engineering principles demonstrated

**Ownership boundaries.** Every piece of logic has exactly one legitimate home: lookups in `catalog_lookups.dart`, formatting in `display_formatting.dart`, navigation in `ValueBrewNavigator`, domain judgments in each feature's own `domain/` file. Demonstrated concretely by `resolveBenchmark` and `StyleStandingFormatting` landing in the existing owners rather than new ones in M7, and by the M8 architecture review's explicit question — "could this be expressed more simply" — being answered "no" precisely because the existing owner already covered it. It mattered because the alternative, demonstrated by the *legacy* codebase's own `recommendation_engine.dart`/`recommendation_policy.dart` split, is logic that's technically separated but not actually ownable by any one reviewer.

**Vertical slices.** Every milestone shipped as domain + presentation + tests together, never a partial layer. Demonstrated by M3 through M8 uniformly, and by the M9 discovery process explicitly rejecting candidates (strength/size/brand preferences) specifically *because* they couldn't be completed as one slice without dragging in Trade-off Explanation. It prevented the kind of half-built capability that leaves a screen contract partially satisfied and a future contributor unsure what's real.

**Additive architecture.** No milestone required restructuring a prior milestone's files. Demonstrated by the fact that `catalog_lookups.dart`, `display_formatting.dart`, and `ValueBrewNavigator` all still contain every function/method they've ever contained, with new ones appended, never existing ones reshaped. It prevented the kind of churn where a later milestone's convenience becomes an earlier milestone's rework.

**Canon-first reasoning.** Every capability decision traced to a specific document and section before any code was written — never "this seems like a reasonable next feature." Demonstrated most sharply by the M7 band-count correction: the original four-band design was *plausible engineering* but had no citation, and was rejected the moment that was checked directly against the Lexicon, Beer Knowledge Model, and Screen Contract. It prevented scope invented from intuition rather than requirement.

**Repository-first reasoning.** Every acceptance review re-read the actual changed files, not a summary of them. Demonstrated by every commit acceptance review in this project reading all touched files fresh before answering a single question, and by the M8 kickoff's `git status` check overriding a stated claim. It prevented approving work based on a description of what was intended rather than what was typed.

**Avoiding speculative abstractions.** Nothing was built ahead of a second, let alone third, real consumer. Demonstrated by the repeated "not worth doing" verdicts on extracting shared test fixtures at two call sites, and by `ValueBrewNavigator`'s own doc comment stating outright that a route table "isn't earned yet" even after four methods. It prevented infrastructure existing to serve a need that was assumed rather than demonstrated.

**Preserving reviewability.** Commits were sized so each one told exactly one story, and stress-tests actively tried to eliminate every new element before accepting it. Demonstrated by the M8 stress test trying, and failing, to eliminate the navigator method, the button, and the `navigatorKey` test wiring individually, with a stated reason for each survival. It prevented "it's approved because nothing obviously broke" from substituting for "each piece was checked and is necessary."

**Implementation only after architecture convergence.** Every milestone had a distinct "freeze" step before any code was written, and the M9 discovery explicitly declined to implement anything once no candidate survived. It prevented building against a plan that was still moving.

**Documentation accuracy.** Doc comments were held to the same evidentiary standard as behavior — a claim that something is "not yet built" was checked against whether it actually still wasn't, repeatedly, and corrected when it wasn't true (`rootNavigatorKey`, `generate_recommendation.dart` twice, `recommendation_result.dart`, and three more found in a full-repository audit). It prevented a future reader trusting a comment that had quietly become fiction.

**Evidence over assumption.** The single most repeated pattern in this project: every "the canon says X" claim was followed by a direct quote and citation, every "this file does Y" claim was followed by actually reading it, and every "this is already committed" claim was checked against `git status` rather than accepted. It's the reason the M7 band-count issue, the M8 uncommitted-milestone issue, and a later full-repository audit's findings were all caught at all.

---

## Architectural decisions that proved correct

**`ValueBrewNavigator`, one method per transition.** Survived four additions (M3, M4, M6's parameter, M8) without its shape changing. Strengthened, not weakened, by later work — M8's stress test specifically confronted the temptation to merge two identical-bodied methods (`recommendationToBeerDetail`, `priceVerificationToBeerDetail`) and held the line because the Navigation Contract treats them as distinct edges. This decision would be made the same way again today; the identical-body case is exactly the scenario that would tempt a "smarter" design, and the discipline held under that exact temptation.

**`catalog_lookups.dart` as sole lookup owner.** Survived four additions (`resolveBeer`, `resolveStyle`, `resolveSku`, `resolveBenchmark`) with zero duplicate resolution logic appearing anywhere else in the canonical tree. Strengthened by each addition following the exact same null-returning, single-loop shape. Would be made the same way again; the alternative, visible in the legacy tree's own scattered resolution logic, is strictly worse.

**`display_formatting.dart` as sole formatting owner.** Survived three additions (`ValueVerdictFormatting`, `PriceVerificationVerdictFormatting`, `StyleStandingFormatting`) with the explicit rule "domain returns enums, formatting owns strings" holding without exception — `classifyStyleStanding` returning only an enum, never text, was checked and confirmed directly in the M7 acceptance review. Would be made the same way again.

**Domain-layer separation.** Every judgment (`verifyPrice`, `generateRecommendation`, `classifyStyleStanding`) is pure Dart, testable without a widget. Survived Beer Detail gaining its *first* domain file in M7 without disturbing the "purely presentational" framing anywhere it was still true — only the one sentence that became false was corrected. Would be made the same way again.

**`RecommendationOutcome` as a sealed type with an exhaustive switch.** Survived a fourth subtype (`RecommendationTie`) being added in M5 without any renderer silently ignoring it — the compiler forced the new case everywhere. This is the strongest evidence in the whole project that the original design choice was correct: it wasn't just convenient, it caught something at compile time that a boolean flag would have let slip past at runtime. Would be made the same way again, more confidently than when it was made.

**Widget-local transient state.** `_result`, `_chargedPriceController`, `_error` on `PriceVerificationScreen` were never lifted into a provider. Survived M8's navigation edge relying on exactly this property — state preservation across the Beer Detail round trip worked for free, because `MaterialPageRoute` keeps the state object mounted, with zero code written to make it happen. Would be made the same way again; it's the clearest example in the project of an architectural choice paying for itself later without anyone planning for that payoff in advance.

---

## Architectural decisions that changed

**Recommendation's loading/error handling.** Originally a bare `CircularProgressIndicator` and raw exception text. Changed during the V1-readiness pass to the shared `ErrorStateView`/`SkeletonBox` convention. Forced by direct comparison against Beer Detail and Price Verification, which had already established that convention — the divergence was only visible once enough sibling screens existed to compare against. Unambiguously improved the repository; it removed the one place a person could see a raw `Exception` object on screen.

**Style Benchmark's classification shape.** Originally proposed as four bands using `p25`/`p50`/`p75`. Changed to three states using `p50` alone, one review turn before implementation began. Forced by a direct, narrowly-scoped rereading of every document that defines "Style Benchmark," which turned up no citation for any specific band count — only the comparison concept and one worked example ("better value than typical"), itself a two-sided comparison against a midpoint. Unambiguously improved the repository: it shipped exactly what was specified, nothing invented, and left `p25`/`p75` available, unused, for whichever future milestone might actually need them.

**Release documentation.** Originally, `CHANGELOG.md`, `README.md`, `privacy_policy.md`, and three other files described the pre-canon browse/filter/favorites application, with a pre-existing but never-tagged `1.0.0` entry. Changed to describe only the canonical rebuild. Forced by discovering, while attempting to write a release plan, that these artifacts already existed and disagreed with the repository — resolved by asking rather than guessing, since repository evidence alone couldn't determine whether they were abandoned drafts or real history. Improved the repository, conditioned on a judgment call that had to come from outside the repository itself.

**Commit strategy.** Originally an 11-commit plan, one per milestone-sub-step, drafted before any of the actual `git diff` output existed. Changed to 7 commits once the real diffs were inspected and `value_brew_navigator.dart`/`recommendation_screen.dart` proved to carry non-separable changes from three-plus milestones each. Forced by evidence only available at execution time — the original plan couldn't have known this without the literal file states in hand. Improved the repository's honesty about its own history: a synthetic 11-commit split reconstructing states that were never actually built and tested independently would have been less truthful than 7 commits that are.

---

## Mistakes caught by the review process

**Style-lookup inconsistency (M3).** An inline style resolution alongside an already-extracted local variable, in the same file. Discovered during the post-implementation review conducted *before* Milestone 4 began — a dedicated checkpoint separate from the implementation itself. Missed during implementation because the two forms did the same thing and both passed tests; only a direct, deliberate re-read for consistency (not correctness) caught it. The review process worked because that re-read was a separate, later pass, not a hope that implementation would self-catch it.

**Bare `Padding` risking overflow (M4).** `PriceVerificationScreen` used `Padding` instead of `SingleChildScrollView`, a real risk once the keyboard appears. Caught during the Commit 1 implementation review, before Commit 2 of the same milestone began. Missed initially because it only manifests with a keyboard visible, a state the initial build-and-glance didn't exercise. The process worked because "implementation review" wasn't treated as a formality between commits — it was a real checkpoint even within one milestone.

**Test collisions from mounted prior routes (M5, M6).** `find.text(...)` matched buttons on more than one screen because `MaterialPageRoute` keeps the previous route mounted underneath. Caught by literally running the tests and reading the failure, not by inspection. Missed initially because it's a Flutter framework behavior, not a repository defect — invisible until exercised. The process worked because running tests was never treated as a formality either.

**RecommendationScreen's stale loading/error handling and two stale doc comments (V1 readiness).** Both true when written, both false by the time three more milestones had passed. Caught by a dedicated pre-release readiness audit whose entire purpose was comparing every screen against every other screen and every comment against the current code. Missed earlier because no milestone's own review scope included comparing itself against siblings that didn't exist yet when it shipped. The process worked because a pre-release audit was run at a wider scope than any single milestone's own review.

**Pre-existing legacy release artifacts (release prep).** An entire set of already-written, never-tagged release documents describing a different product. Caught while attempting to *write* new release documentation and finding files that already existed and disagreed. Missed by every prior review because none of them had reason to look at `CHANGELOG.md`/`store_listing.md`/etc. until release work actually began. The process worked because the ambiguity was surfaced and asked about rather than silently resolved either direction.

**`recommendation_result.dart`'s stale "genuine tie" claim, and a date discrepancy across two release documents (Final Repository Verification).** Both caught by a review explicitly instructed not to assume prior reviews were correct — a full, independent re-derivation, not a checklist re-run. Missed by the reviews that produced the surrounding work because Tie Disclosure and the release-doc dates were each accurate when their own milestone shipped them, and only drifted afterward.

**Milestone 7's over-specified four-band design.** Caught by a review scoped to exactly one question — "is the band count actually specified, or did I invent it" — asked one turn before implementation, not after. Missed by the original discovery because that discovery was answering "does this capability exist," a coarser question than "is every detail of my proposed implementation actually cited." The process worked because a narrower, more skeptical follow-up question was asked deliberately, rather than treating the first "yes, viable" answer as final.

**Milestone 7 stated as committed when it wasn't (M8 kickoff).** Caught by running `git status` as the very first action of the next turn, before doing anything else. Missed by nothing prior — this was a new claim in a new message, not a carried-forward error — but it's the clearest single demonstration in the project that a stated premise is not evidence, however confidently or specifically stated.

**The unreachable legacy codebase and several further stale doc comments (Repository Stewardship Audit).** All present since before the canonical rebuild session began, none previously flagged. Caught by an audit explicitly scoped to the *entire* repository, with instructions not to inherit any prior turn's scope boundaries. Missed by every earlier review because every earlier review was scoped to "what this milestone touches" or "what the canonical tree contains" — reasonable scopes for their own purposes, but none of them was ever "everything in `lib/`." The process worked because a wider-scoped audit was eventually run at all, not because any narrower review should have caught it.

---

## Review methodology

**Implementation and review stayed separate, every time, without exception — including for a three-file, sixty-line milestone (M8).** This wasn't caution for caution's sake; it's what let the M8 architecture review find and justify the "identical method bodies, distinct canonical edges" question *before* code existed to defend, rather than after code existed to rationalize.

**Acceptance reviews repeatedly re-read the repository instead of trusting the implementation summary, because the summary describes intent, and intent is not what shipped.** This is the reason the M7 and M8 acceptance reviews could each independently confirm things like "no callback prop was introduced" — by reading the actual `onPressed` closure, not by recalling that none was planned.

**Fresh verification mattered because plans age faster than they're remembered to have aged.** The clearest proof is M8's opening move: a stated fact ("Milestone 7 has already been... committed") that was one `git status` call away from being disproven. Nothing about the claim was suspicious on its face; it was simply false, and the only way to know that was to check, not to reason about plausibility.

**Repository evidence consistently beat memory because memory compresses, and compression is where invented detail creeps in.** The M7 band-count correction is the sharpest example: nothing about "four bands feels reasonable" is wrong reasoning in the abstract, but it was never what the canon said, and only a literal re-read of the Lexicon's "Outputs: a value percentile" line and the Beer Knowledge Model's one worked example revealed that the canon had specified less than what memory had quietly filled in.

**Architecture discovery eventually concluding "no milestone exists" is the methodology's proof of health, not a failure of it.** A discovery process that always finds something to build is indistinguishable from one that manufactures work; a discovery process that sometimes concludes there's nothing, and can show its work for why every candidate failed independently, is one that was actually testing against real constraints. This happened more than once in this project (Milestone 9's conclusion, and Comparison/Confirm-as-Is being independently re-rejected in multiple separate discovery passes with the same evidence each time) — consistency across independent re-derivations is itself evidence the rejections were real, not arbitrary.

---

## Repository maturity

**Architectural maturity: high.** Eight milestones shipped without a single one requiring a change to an established pattern — `ValueBrewNavigator`'s shape, `catalog_lookups.dart`'s convention, `display_formatting.dart`'s ownership rule, and the domain/presentation split all absorbed every addition without bending.

**Repository maturity: mixed, and honestly so.** The canonical tree (`discovery/`, `recommendation/domain`+`presentation`, `beer_detail/domain`+`presentation`, `price_verification/`, `shared/`, `navigation/`) is clean and fully accounted for. A substantial unreachable legacy tree still exists alongside it, catalogued in a dedicated stewardship audit but not acted on — this is a real maturity gap, not a hidden one.

**Documentation maturity: strong at the canon layer, catalogued-imperfect at the engineering layer.** Twenty frozen canon documents plus an Architectural Decisions Record give this project a documentation floor few repositories have. The engineering-facing documents (README, CHANGELOG, VERSION, the Architecture Reference) had a known, small, fully-itemized set of staleness issues, addressed in the same documentation pass that produced this retrospective.

**Testing maturity: strong, with one known naming defect.** 571 tests as of Milestone 8, consistent unit/widget conventions throughout the canonical tree, one confirmed basename collision between a legacy and canonical test file.

**Maintainability: high.** Every ownership boundary is independently checkable by grep, not by convention alone — demonstrated repeatedly by this project's own audits succeeding at exactly that.

**Extensibility: high within canon-authorized bounds, and deliberately not beyond them.** This is a design property, evidenced by the fact that the project's own discovery process is *built* to refuse extension the canon doesn't authorize, and did so, repeatedly, correctly.

**Engineering discipline: the repository's strongest asset.** Its clearest evidence is negative: the number of times this project concluded "nothing to build" or "this isn't specified, don't invent it" rather than producing more code.

---

## Guidance for future contributors

**Never:**
- Never invent a trigger rule, threshold, band count, or classification the canon doesn't specify — cite the smallest thing that's actually written down, not the most detailed thing that seems plausible.
- Never trust a stated claim about repository state — a commit happened, a file exists, a count is current — without checking it directly first.
- Never let an implementation summary substitute for reading the actual diff during review.
- Never restructure or refactor a file as an incidental side effect of an unrelated change.
- Never resolve a documented, open canonical gap locally, however small the resolution seems — name it, don't close it.

**Always:**
- Always trace a new capability to a specific document and section before writing any code.
- Always check whether a new file, method, or widget can be eliminated before defending it as necessary.
- Always keep implementation and review as genuinely separate passes, regardless of how small the change is.
- Always verify the exact file set with `git status`/`git diff --stat` before staging or committing.
- Always classify a repository finding (real defect, self-documented deferral, historical artifact) before deciding whether it's actionable.

**How to begin a new feature:** read the governing Screen Contract(s) and Navigation Contract fresh, not from memory; read the actual files that would be touched and what currently imports them; test the candidate independently against every rejection criterion this project used (fully specified, independently reachable, no invented behavior/thresholds/inputs, no unresolved navigation or architecture, no dependency on another missing capability); only then propose an architecture, and expect it to be stress-tested before any code is written.

**How to determine whether something belongs in the repository or the canon:** if the question is "what should this do, and under what conditions," and no cited document answers it, it's a canon question — do not answer it in code, however small the gap seems. If the question is "how should this already-specified behavior be built," it's a repository question, and the answer should follow this project's existing ownership conventions rather than invent a new one.

**When to stop implementing:** the moment you notice you're filling in a detail the canon left unspecified. Stop, find the smallest version that's actually citable, and build that instead — this is the single most concrete, repeatable lesson this project produced.

**When to stop reviewing:** once a fresh, independently-derived pass — not a re-run of the same checklist against the same assumptions — turns up nothing new. Not before that, regardless of how confident the implementation felt going in.

---

## Final conclusion

1. **Is this repository a successful example of architecture-first engineering?** Yes — eight shipped milestones, each traceable to a specific canon citation, zero required refactors across them, and a discovery process that repeatedly concluded no further work existed rather than manufacturing it.
2. **Did the review process materially improve the codebase?** Yes — a concrete, itemized list of real defects were caught before or shortly after shipping (M3's lookup inconsistency, M4's overflow risk, six stale doc comments across the project's life, an over-specified classification design in M7, an uncommitted milestone in M8) and none of them would have been caught by implementation alone.
3. **Did the repository converge naturally, or was convergence forced?** Naturally — the clearest evidence is that the discovery process rejected candidates independently, with different reasoning each time, and arrived at "nothing survives" through actual constraint-checking, not through a process built to always produce that answer or always avoid it.
4. **Is the repository now primarily constrained by engineering or by product definition?** By product definition. Every currently blocked capability traces to missing, contradictory, or explicitly deferred canon — none traces to a repository limitation.
5. **What is the single biggest lesson?** A canon gap is never resolved by inventing an answer at implementation time — it is named and left alone. This is the one thread connecting Comparison's unresolved 3+-candidate scaling, Confirm-as-Is's undefined trigger, the Home/Price-Verification contradiction, and Style Benchmark's unspecified band count — and it's the reason this repository can be handed to a future contributor with confidence that what's built is exactly what was actually specified, nothing more.

---

## Recommendation

This document closes the engineering record for the current canon. No further architecture discovery, milestone discovery, reopening of settled decisions, or invented implementation work follows from here. Future work resumes only when the canon changes or the repository materially changes — and when it does, it begins from first principles, not from this document's conclusions carried forward as assumptions.
