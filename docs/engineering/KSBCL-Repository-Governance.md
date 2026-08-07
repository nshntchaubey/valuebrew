# KSBCL Pipeline — Repository Governance

### Not a new policy document. Every convention below was extracted from decisions the repository has already made, across Stages 1–4 and the Identity Decisions — nothing here is proposed, only observed and cited. Written for whoever drafts Stage 5, so that stage doesn't have to rediscover by trial what Stages 2–4 already established by repeated practice.

---

## 1. Master's field sketches are meant to be hardened, not re-litigated

**One sentence:** When master names an artifact and gives it a terse field list without full computation rules, the stage that actually produces that artifact is expected to fully specify it — this is normal, not an overreach.

**Demonstrated in:** Stage 2 (classification_audit.csv's five-column master sketch, §4.2, hardened into a full schema plus two persistent ledgers); Stage 3 (the Stage 3 field sketch, §4.3, hardened into exact extraction grammar); Stage 4 (item_code_canonical_map.csv and canonical_resolution_review.csv's sketches, §4.4, hardened into a complete resolution mechanism).

**Prevents:** every stage stalling on a master amendment before it can be built, or master having to anticipate implementation-level precision it was never meant to carry.

---

## 2. Explicit prior text is never silently overridden

**One sentence:** A stage's own architecture may fill a gap master left open, but it may never contradict something master (or an earlier recorded decision) already, explicitly decided — and where a decision does authorize a departure, the departure is scoped exactly to what that decision covers, never further.

**Demonstrated in:** Stage 2 (a compound-phrase veto guard was removed after being found to contradict master §6.1's unqualified "never veto a style-keyword match"; the unfamiliar-supplier demotion was restored after silently dropping a master §6.2 requirement); Stage 3 (an attempt to internalize `pack_count` was reversed on finding master §4.4 still required it); Stage 4 (an initial, over-broad removal of the price/date review gate was corrected to apply only to the cross-supplier configuration the Identity Decision actually addresses).

**Prevents:** architecture quietly drifting away from decisions that were deliberately made, without anyone noticing.

---

## 3. Architectural decisions vs. Product Decisions have a consistent, evidenced boundary

**One sentence:** A question is resolved by architecture when an answer is derivable from something already stated in the repository and doesn't change what the product promises; it requires an explicit Product Decision when no amount of further analysis closes the gap because the disagreement is about values or risk tolerance, not facts.

**Demonstrated in:** architecture-resolved — word-boundary matching mechanics, `classification_config_version`'s computation, declaration-order tie-breaks (Stage 2); `pack_size_ml` grammar, `container_type` priority order, removal of unconsumed fields (Stage 3); `item_status`'s semantic definition, the exact scope of a merge-mechanism departure (Stage 4). Escalated to Product Decision — multi-word vocabulary punctuation matching (Stage 2, §17); `supplier_code`'s place in canonical identity, and multi-candidate identity ambiguity handling (the Identity Decisions); Duty-Free exclusion, implementation language, and the original auto-merge confidence bar (Master §12, each explicitly attributed to "the product owner").

**Prevents:** engineers making business-value calls they have no standing to make, and business decisions being needlessly escalated when a derivable engineering answer already exists.

---

## 4. Confirm, then extend — never build for an unconfirmed hypothetical

**One sentence:** A rule, exception, or vocabulary entry is added to a deterministic mechanism only after a real, confirmed instance appears in actual data — never pre-emptively for a risk that might exist.

**Demonstrated in:** Stage 2 (§4.7's confirm-then-allowlist policy for misspellings and abbreviations; the "Root Beer"/"Ginger Beer" risk left explicitly unmitigated pending real evidence); Stage 3 (the bare-`l` unit left unhandled absent a confirmed real row, citing Stage 2's own posture as precedent).

**Prevents:** speculative machinery built for failure modes that never materialize, and the false confidence that comes with defending against an imagined case instead of an observed one.

---

## 5. Under genuine uncertainty, the default favors under-action over over-action

**One sentence:** Where the architecture must choose a default without full information, it consistently prefers the option that fails toward exclusion or non-merging rather than inclusion or merging, because a false negative is cheaply corrected later while a false positive silently corrupts the catalogue.

**Demonstrated in:** Stage 2 (§4.6, Low-confidence rows excluded by default); Stage 4 (master's own "exact match only, never fuzzy" auto-merge bar; the Identity Decision's Option F preserving ambiguity rather than auto-resolving it).

**Prevents:** an error that's invisible and hard to undo, in exchange for one that's visible, bounded, and recoverable.

---

## 6. Never invent a fact the source doesn't state

**One sentence:** A field is populated only from what the source data actually and confirmably shows; where information is genuinely absent, the field is left null or unknown rather than guessed, defaulted, or inferred from a different, less direct signal.

**Demonstrated in:** Stage 1 (§9's invariants — raw fields are never reinterpreted, no case size is ever assumed for a bare-volume row); Stage 3 (`pack_count`/`container_type` left null/unknown rather than guessed); Stage 4 (`item_status` grounded in confirmed source presence rather than a downstream, filtered signal that could make a still-published item look delisted).

**Prevents:** the pipeline asserting a real-world fact it cannot actually support, which then propagates as false certainty into every feature built on top of it.

---

## 7. Every stage produces an audit artifact, not just a clean output

**One sentence:** Rows that are rejected, excluded, or flagged are always preserved with a reason, never silently dropped, so any decision the pipeline made is reconstructable without re-reading the original source.

**Demonstrated in:** Stage 1 (`rejected_rows.csv`); Stage 2 (`classification_audit.csv`, the persistent review queue); Stage 3 (aggregate rate tracking for malformed/incomplete cases); Stage 4 (`canonical_resolution_review.csv`).

**Prevents:** an unattended, monthly-run pipeline becoming an unauditable black box over time.

---

## 8. Correctness means determinism, not a fabricated accuracy number

**One sentence:** Since no ground-truth label exists for questions like "is this really beer" or "is this really the same product," correctness is defined as determinism, explainability, and non-regression — never as an accuracy percentage measured against a target nobody could actually verify.

**Demonstrated in:** Stage 2 (§9); Stage 3 (§5); Stage 4 (§8).

**Prevents:** manufacturing false precision from a number that looks rigorous but isn't checkable.

---

## 9. Freeze requires a deterministic, implementable text — not the resolution of every question

**One sentence:** A stage may freeze with a genuine question still open, provided the frozen text already gives that question one explicit, fully-implementable, deterministic answer every compliant implementer would arrive at today, even if a later decision might revise that answer.

**Demonstrated in:** Stage 1 (validation thresholds left unset, tunable, inert until configured); Stage 2, stated directly in its own text: "architecture is complete once a decision like this is identified and correctly routed, not only once every decision has been made" — frozen with its punctuation-matching Product Decision still open; Stage 4 (`pack_count`'s retention, null/`unknown` matching, cross-run tracking, and audit-field completeness all left open at freeze, each with a stated, working default).

**Prevents:** a stage that can never freeze because some genuinely irreducible or evidence-pending questions cannot be resolved in advance — while still preventing ambiguity from being smuggled through as if it had been resolved.

---

## 10. Review history — including reversed mistakes — is disclosed, not erased

**One sentence:** When an adversarial review finds a defect, or an earlier draft turns out to have been wrong, the document records what was tried, what was found, and why it changed, rather than presenting a clean text as if the mistake never happened.

**Demonstrated in:** Stage 2 (§14–§17, including explicitly noting that an earlier, non-independent "review" was discarded and redone honestly); Stage 3 (§12.2's disclosure of the `pack_count` internalization near-miss).

**Prevents:** false confidence from a document whose polish comes from erasing its own history rather than surviving scrutiny.

---

## 11. Every rule is grounded in real, confirmed data — and illustrative examples are labeled as such

**One sentence:** An edge case, rule, or validation is written into an architecture document only after being checked against actual extracted rows from the real dataset, and a hypothetical example is always explicitly marked as illustrative rather than presented as if it were confirmed.

**Demonstrated in:** Stage 2 (explicitly separating confirmed KSBCL evidence from a different, non-KSBCL research corpus used only illustratively); Stage 3 (every "must extract" rule cites a real item_code); Stage 4 (the Kingfisher multi-supplier group and the Budweiser Magnum pair, both confirmed against the real 2026-06 run before being used to justify a mechanism).

**Prevents:** architecture built around a plausible-sounding but unconfirmed assumption about what the data actually contains.

---

## Reading this before writing Stage 5

None of the eleven conventions above are stated as a single, standalone repository policy anywhere — each was demonstrated by repeated, consistent practice across Stages 2 through 4, not written down in advance. Stage 5 inherits them the same way Stage 4 inherited Stage 2 and 3's precedent: by following the same discipline, not by finding a rule to cite. Where Stage 5 encounters a genuinely new kind of question none of the above quite covers, the correct move — demonstrated every time it has come up — is to name the question precisely, determine which side of convention 3's boundary it falls on, and either resolve it architecturally with cited justification or route it explicitly for a Product Decision. Guessing silently is the one thing no stage in this repository has ever been allowed to do.
