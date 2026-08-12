# ValueBrew — Collaboration Governance

**Status: DRAFT — first pass, not yet reviewed by everyone it governs, not frozen.**

### Governs how decisions get made and preserved across everyone working on this project — currently the founder, an engineering-side AI collaborator (Claude) with direct repository access, and a product-side AI collaborator (ChatGPT) without it. Named after the roles, not the specific tools, since tools are expected to change and the governance shouldn't need renaming when they do.

---

## Purpose

The purpose of this document is to ensure that important decisions become explicit, reviewable, version-controlled, and discoverable — rather than remaining dependent on a conversation, an individual's memory, or a specific AI tool. Every rule below exists to serve that purpose. A rule that doesn't help preserve important knowledge, or that trades preservation for convenience, doesn't belong here.

## Where this came from

This document was not designed in advance — it was extracted, the same way `KSBCL-Repository-Governance.md` was, after enough real decisions had accumulated across an actual three-way exchange (founder, Claude, ChatGPT) that a repeatable pattern became visible. Every convention below was demonstrated in that exchange before being written down here, including the exchange finding and correcting its own violations of these same principles while they were still being drafted (see §1.3's worked example).

## Scope

This document governs collaboration and decision preservation across the ValueBrew project. It does not replace the Product Canon (`docs/architecture/current/`), the Architectural Decisions Record, `KSBCL-Repository-Governance.md`, or any future engineering-side or product-side governance document. Instead, it defines how those artifacts get created, challenged, and maintained together, and how authority is divided across the people and tools doing that work. If a rule here would duplicate or override something already decided in one of those documents, that document wins — this one is about process, not product or engineering truth.

---

## Part 1 — Governance (timeless; should change rarely)

### 1.1 Sources of authority

| Domain | Authority |
|---|---|
| Vision — what kind of company/product this is trying to be | The founder |
| Product truth — what the app does, why, for whom | The Product Canon (`docs/architecture/current/`) |
| Engineering truth — what's built, what's tested, what the code does | The repository itself (code, tests, engineering docs) |
| Decision reasoning — why a specific choice was made | ADRs, governance documents, decision records, closure reports |
| Product reasoning — trade-offs, prioritization, interpretation of customer psychology, strategy, and judgment about what to build next | Product-side discussion — always provisional until checked against evidence |
| Reality | Users, experiments, production data, real repository state |

No conversation is authoritative on its own, in any domain. A conversation is where reasoning is discovered; a document in the repository is where it's preserved. If something important was only ever said, not written down, it does not yet exist for the purposes of this project.

### 1.2 Claim classification

Every important claim, from any participant, must be classifiable as exactly one of:

- **Evidence** — directly observed: a real file's actual content, a real test result, real production data.
- **Inference** — a conclusion drawn from evidence, stated with its reasoning visible.
- **Hypothesis** — an untested belief about what would be true or would work, explicitly flagged as untested.
- **Opinion** — a value judgment or preference, not a factual claim at all.

A claim presented as Evidence must be checkable by someone else against the actual repository, actual data, or actual users — not taken on the claimant's word, regardless of which participant (founder, Claude, or ChatGPT) made it.

**Classification is not permanent — it changes as evidence accumulates, and that's expected, not a failure of the earlier classification.** An Opinion can be tested and become a Hypothesis; a Hypothesis can be checked against real data and become Evidence; Evidence can be re-examined and turn out to be wrong, dropping back to a corrected Opinion or a discarded claim. The KSBCL pipeline's own review history is full of exactly this: a suspected defect started as a Hypothesis, was checked against real data, and either hardened into confirmed Evidence of a real bug or collapsed under scrutiny and was discarded. Recording which one happened, and why, is more valuable than getting the classification right on the first attempt.

### 1.3 Challenge protocol

No participant accepts an important claim from another participant solely because that participant asserted it — including when the other participant is an AI that sounds confident, and including when accepting it would be the path of least friction. Every important claim is either:

- verified directly against the repository (for engineering/product-truth claims), or
- verified against users or real data (for product-reasoning claims), or
- explicitly labeled as Inference, Hypothesis, or Opinion if it can't be verified right now.

**Worked example, from this document's own drafting:** a claim that a five-second decision window was already part of ValueBrew's product canon was checked directly against `docs/architecture/current/01-Behavioral-Hypothesis-Model.md` and `02-Product-Definition-Document.md` — it wasn't there. The claim was reclassified from something stated with the confidence of Product Truth down to Opinion, on the record, by the person who made it. That correction is the protocol working, not a failure of it.

### 1.4 Roles and responsibilities

This section was originally titled "Ownership," which conflated two different things: who is accountable for verifying correctness in a domain (a responsibility, currently held by whoever is capable of it), and who has final, non-delegable decision authority (the founder, permanently). Naming it "Roles and Responsibilities" instead makes that distinction visible rather than hiding it under one word.

Every role here is assigned to a **role**, not a tool — the same reason this document's title doesn't name Claude or ChatGPT. Tools filling these roles can change; the roles and what they're accountable for should not need rewriting when that happens.

- **Engineering correctness** is the responsibility of whoever can directly verify repository-derived claims against the actual repository. At the time of writing, this role is fulfilled by Claude.
- **Product reasoning** is the responsibility of whoever is acting as product partner. At the time of writing, this role is fulfilled by ChatGPT. Holding this responsibility is never the same as holding *truth* — product reasoning begins as Hypothesis or Opinion until supported or rejected by evidence, regardless of who's holding the role.
- **Vision and final judgment** are the founder's decision authority, always — this is not a role that gets filled by a tool and is not expected to change. Neither AI collaborator becomes the authority on anything the founder is the actual authority over.

### 1.5 Repository primacy

If it's important, it lives in the repository — not in a chat thread, not in a specific person's or AI's memory, and not in a document deliberately kept outside version control on the theory that it's "not ready yet." The repository should preserve conclusions, not conversations — not every discussion deserves to be preserved, only the durable outcome it produced, or the repository eventually becomes just another chat log. A draft, explicitly labeled as a draft with disclosed open questions, belongs in the repository more than a polished idea that only exists in conversation. This document itself is the test case: it exists as a versioned file, in draft status, rather than as an unwritten agreement everyone privately holds.

### 1.6 Governance evolves by extraction, not invention

New governance rules should be extracted from recurring, demonstrated practice, not introduced speculatively because they sound reasonable. A single incident may reveal a problem; only a recurring pattern justifies turning it into governance. This is how `KSBCL-Repository-Governance.md` came to exist, and it's how this document came to exist — every rule above traces to something that actually happened, not to a guess about what might someday be useful.

---

## Part 2 — Workflow (changeable; expected to evolve as tools and process change)

### 2.1 How a document gets drafted

Whoever can directly verify the claims being written should draft the first version — not whoever has the best writing, but whoever can check their own claims. This is about verification capability, not access for its own sake: an engineering-grounded document is drafted by whoever can check it against the actual repository; a product-vision document is drafted by whoever owns that reasoning, with the founder's direct input, since vision has only one real owner.

### 2.2 How review happens

The pattern already proven across the KSBCL pipeline work: draft → independent, skeptical review (ideally from someone/something with no attachment to the draft) → revise what survives scrutiny, discard what doesn't, on the record → disclose the revision history in the document itself rather than presenting a clean final version as if no correction ever happened.

### 2.3 How cross-tool relay currently works

As of this document's drafting, ChatGPT has no direct access to this repository. Every exchange between the engineering side and the product side currently flows through the founder manually relaying content in both directions. This is a real, disclosed limitation of the current workflow, not a solved problem — "we'll review each other's work directly" is aspirational until that access gap closes. This section should be updated the moment that changes.

### 2.4 How disagreements get resolved

Check the repository, check real data, or check with users. If none of those settle it, the disagreement is recorded as an open question with each side's position labeled by claim type (§1.2) — never silently resolved by whichever participant asserted their position more confidently.

---

## Status

Draft, revised twice. First pass drafted by Claude; reviewed by ChatGPT, who found the draft's ownership language tied specific rules to specific tools in a way that contradicted the document's own title and philosophy, found one term used loosely enough to introduce a real inconsistency risk on its own first revision, and proposed the Scope section, the broader definition of product reasoning, the dynamic-classification note, and the extraction-not-invention principle — all adopted. One suggestion (a worked example for dynamic classification) was corrected before being adopted: it used "Engineering Truth" as if it were a claim classification, but §1.2 defines only four (Evidence, Inference, Hypothesis, Opinion) — "Engineering Truth" is a domain from §1.1, not a classification, so the example was rewritten using only the four actual categories.

Second review, also from ChatGPT: found that §1.4 ("Ownership") still mixed two different things under one word — responsibility for verifying correctness in a domain, versus the founder's non-delegable decision authority — and proposed renaming it. Adopted, retitled "Roles and Responsibilities," with the distinction stated explicitly in the section itself rather than left implicit. Also adopted two smaller tightenings: a more precise sentence on when product reasoning resolves into supported or rejected evidence, and an explicit statement in §1.5 that the repository preserves conclusions, not conversations.

Still not yet reviewed by the founder directly. Revise this section, with the revision disclosed, the next time something here changes.
