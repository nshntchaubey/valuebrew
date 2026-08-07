# KSBCL Pipeline — Engineering Process Retrospective

### This is not a summary of Stage 4. It is the workflow that Stages 2, 3, and 4 each independently, repeatedly followed — extracted from what their own documents actually record, not from any stated methodology. Written for whoever writes Stage 5.

---

## 1. The sequence a successful stage author repeatedly followed

Every stage's own §0 ("Sources consulted") records the same opening move: master read in full, every already-frozen prior stage's contract read in full, before a single sentence of new architecture was drafted. Stage 3's §0 names Stage 1 and Stage 2's frozen documents specifically; Stage 4's names Stage 3's, plus the Identity Decisions once those existed. Nothing was drafted from memory of what an earlier stage "probably said."

Immediately after that reading pass, the real output already sitting on disk from the prior stage's actual run was pulled and used as the only source of examples from that point forward — Stage 3 cites real rows from `structured_rows.csv`/`classification_audit.csv`; Stage 4 cites real rows from `normalized_rows.csv`. Every "must extract" or "must attach" example in both documents traces to a specific, named `item_code`.

Only then was the mechanism drafted — and the draft was immediately followed by an independent adversarial pass explicitly described as having "no attachment to the design" (Stage 2 §14) or being "a cold read, as an implementer with no ability to ask questions" (Stage 2 §15). This did not happen once. Stage 2 went through four distinct rounds before its own final categorization table showed nothing left uncategorized. Stage 4's equivalent of this repeated-round pattern was the extended adversarial sequence this whole review consisted of.

## 2. What always happened before a stage froze

Three things, without exception, across all three stages:

- Every remaining open item was sorted into a closed, named set of categories — never left as an unlabeled loose end. Stage 2's §17 table is the sharpest example: every item ever raised across four review rounds is assigned exactly one of "resolved into frozen architecture," "configuration," "product decision required," or "future implementation work," with a closing line stating explicitly that nothing remains unclassified.
- The mechanism was run against the real, full dataset and its actual output inspected before anyone was willing to call it correct — not just reasoned about on paper. Stage 3's freeze followed a real 1,714-row run; Stage 4's real-data validation used the actual June 2026 output before either Identity Decision was finalized.
- A status line was written declaring the document frozen, and it appeared only after the first two conditions were already true — never before.

## 3. Mistakes that repeatedly appeared in early drafts

The same handful of mistake shapes recur, independent of which stage or which author:

- **Reusing a mechanism built for one problem to solve a different one it wasn't designed for.** Stage 3's first pass reused Stage 2's vocabulary-boundary matcher for a structured pack-size grammar; Stage 4's first pass reused master's supplier-included merge gate for a configuration the supplier decision had made newly possible, without re-deriving whether the gate's original reasoning still applied there.
- **Silently narrowing or dropping something an upstream document had already, explicitly required**, without checking it against that upstream text first. Stage 2 dropped a master-specified condition once; Stage 3 nearly internalized a field master's own §4.4 required for a later stage's key.
- **Asserting a guarantee or a rule existed without actually defining it.** Stage 2 claimed a tie-break existed for multi-keyword matches before one was ever specified; a claim of "never a gate" was made and didn't survive being checked against what actually happens on a silent no-match row.
- **Adding a field or mechanism with no confirmed consumer**, justified by what seemed like reasonable foresight rather than a cited, real need.
- **Leaving cross-run or ordering behavior unspecified the first time a persistent, stateful ledger was introduced** — within-run processing order and out-of-order-rerun handling were both found missing from Stage 2's first draft of its own persistent ledger, not from a hypothetical one.
- **A correction applied in one place not being checked against every other document that describes the thing being corrected** — the single largest source of extra review cycles in Stage 4's own history, most visibly when a corrected computation rule made an already-frozen, previously-accurate statement in a different document quietly false.

## 4. Review activities that consistently found genuine defects

- **An independent, zero-context reviewer, explicitly told to try to break the document rather than summarize it.** Every genuine architecture blocker actually corrected in this whole process — Stage 2's dropped condition, Stage 3's suffix-position assumption, Stage 4's over-broad merge-gate removal — was surfaced this way, not by the original author re-reading their own draft.
- **Checking a rule against a specific, named, real row, not a hypothetical one.** Stage 3's suffix-stripping bug and Stage 4's Budweiser Magnum/Kingfisher findings were both found by querying actual extracted data, not by inspecting the rule in the abstract.
- **Checking a proposed simplification or removal against every other document that might depend on it, not just the stage's own text.** This is what caught the `pack_count` near-miss and, later, exposed exactly what a corrected `item_status` rule required elsewhere.
- **Applying the literal test "would two competent engineers implement this differently" to every remaining ambiguity**, rather than accepting that a rule sounds reasonable.

## 5. Review activities that consistently produced false positives

- **Proposing a new persistent entity to explain an observed gap without first checking whether the underlying fact was already recoverable from data that already persists.** Every "missing entity" candidate raised during this process was eventually shown to be a missing *rule* over already-available data, not missing storage.
- **Reasoning from a sibling stage's precedent or from a field's name, instead of checking the specific document's own words.** The clearest example collapsed an entire finding the moment that borrowed reasoning was disallowed and the document's own text was read in isolation.
- **Reading a phrase like "audited action" as requiring a full, dedicated mechanism, without first checking whether an existing, weaker signal already satisfies it.**
- **Generalizing from what a reviewer did repeatedly, rather than from what the frozen documents themselves repeatedly demonstrate**, when searching for a governance principle. A candidate that felt earned by the review's own habits collapsed once the standard was correctly applied only to the documents, not to the review process that produced them.

## 6. When Product Decisions entered the process

Twice, in two different shapes. Master itself already carried three Product Decisions before any stage architecture existed — settled once, at the very top of the pipeline, and never revisited.

Within an individual stage, Product Decisions arrived at opposite ends of the process depending on how they surfaced. Where a stage's central question was recognized up front as inherently value-laden — no amount of analysis would resolve it, only a stance would — architecture drafting stopped before it started, and the question was settled first, in its own dedicated document, using real data as evidence but never as the decider. Where a stage's mechanism was already drafted and a freeze review discovered a new ambiguity the mechanism genuinely could not resolve on its own, the decision arrived late, as the last thing standing after everything else had already been sorted into architecture or configuration.

## 7. When Repository Governance was actually useful

Not during Stages 2 through 4's own drafting — it didn't exist yet, and nothing in those three stages' own text cites it as authority, because it couldn't have. Its usefulness is entirely prospective. It became relevant at exactly one moment: once a stage's own defects were exhausted and the review's remaining question shifted from "is this stage correct" to "was the process that produced it repeatable" — at which point the value stopped being about verifying Stage 4 and started being about not making whoever writes Stage 5 rediscover, by trial, the same handful of mistake shapes listed above.

## 8. What could have been done earlier to avoid a later review cycle

- Querying the real dataset *before* drafting a mechanism, not only after a freeze review asked for validation — several corrections were things a direct data query would have surfaced at draft time rather than at review time.
- Checking a proposed change against every other document that describes the thing being changed *at the moment the change is agreed*, not in a separate, later pass dedicated to synchronization. The gap between "corrected here" and "checked everywhere this is described" was itself the source of an entire additional review round.
- Applying the full evidentiary bar for a governance claim — independent demonstration in at least three places — from the first time a pattern was noticed, rather than accepting a convention on thinner evidence and having to recheck it later.
- Writing an agreed conclusion into the actual document in the same session it was agreed, rather than treating "concluded in discussion" as equivalent to "resolved" — the largest single gap found in this entire process was a confirmed, undisputed conclusion that was never propagated into the text it concerned.

## 9. The workflow Stage 5 should follow, blank page to frozen architecture — extracted, not invented

1. Read master, every frozen prior stage, every recorded Product Decision, and Repository Governance in full before writing anything.
2. Pull the real, actual output already on disk from the immediately preceding stage's real run. Use nothing else as a source of examples from this point forward.
3. Before drafting any mechanism, sort the stage's open questions into value-laden (no amount of analysis closes the gap) versus mechanical (an answer is derivable from something already stated). For any value-laden question, stop and settle it first, in its own document, before architecture proceeds.
4. Draft the architecture. Where it fills a gap master left open, that's expected. Where it departs from something master or a recorded decision already, explicitly settled, cite the specific authority and scope the departure exactly to what that authority covers — never further.
5. Ground every rule and edge case in a specific, named, real row. Mark anything hypothetical as exactly that.
6. Run an independent, zero-context adversarial review, explicitly instructed to try to break the document, not summarize it.
7. For every finding: check it against master and every other frozen document before accepting it as real. Never accept a finding on the reviewer's word alone.
8. For every proposed simplification or removal: check every other document in the repository that might depend on the thing being removed, not just the stage's own text.
9. Repeat 6–8 with a fresh reviewer each time until a full pass produces nothing new.
10. Sort every remaining open item into exactly one of: resolved into the frozen text, configuration/vocabulary, Product Decision required (name every acceptable option, pick none), or explicitly a later stage's responsibility. Nothing may remain unsorted.
11. Declare the architecture frozen once every item has a category — not once every item has an answer.
12. Implement exactly what the frozen text says. No simplifications, no additions.
13. Run against the real, full dataset and produce every output artifact the architecture itself defines.
14. Run a separate, independent implementation review, checking the code against the frozen text, not against what seems reasonable.
15. For any Product Decision reached along the way, record it in a dedicated decision document with the options, the accepted trade-off, and the rationale — never fold it silently into the architecture text.
16. The moment any correction or decision is agreed — architecture fix, Product Decision, or governance calibration — apply it to the document in the same pass, and check every other already-frozen document that describes the thing being changed, since a correction in one place can make an already-correct statement elsewhere false.
17. Produce a closure record of what was found, fixed, rejected, and left open, so the next stage's author never has to rediscover any of it.
