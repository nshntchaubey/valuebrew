# Development Philosophy

ValueBrew is built in small, reviewable milestones. A milestone is one feature, one refactor, or one architectural change — never a bundle of unrelated work — and it is not considered finished until it passes verification and has been explained, not just implemented.

Every milestone follows the same workflow, regardless of size:

1. **Understand the problem.** Read the relevant existing code and documentation before writing anything. If the task or the documentation is ambiguous or contradicts itself, stop and ask rather than guess — a wrong architectural assumption made silently is far more expensive to undo than a delayed answer.
2. **Design before implementing.** Decide the shape of the change — what new abstraction, if any, is actually needed — before touching files. If an abstraction is introduced, it should be possible to say why it exists and whether it's permanent or a placeholder for something not built yet.
3. **Implement one focused milestone.** Resist folding in adjacent cleanup, unrelated refactors, or "while I'm in here" changes. A bug fix doesn't need surrounding polish; a milestone doesn't need to solve the next one too.
4. **Keep commits small.** Each commit maps to one logical milestone (see [Commit Philosophy](#commit-philosophy)).
5. **Run `flutter analyze`.** Zero issues, not "just warnings."
6. **Run the full test suite.** Not just the tests touching the change — the whole suite, to catch anything the change affected indirectly.
7. **Review the architecture before committing.** Confirm the change fits where it was designed to fit, and that nothing was left half-finished, dead, or undocumented.

Nothing is committed automatically. A milestone's implementer verifies it end-to-end and reports what changed and why; the decision to commit — and when — belongs to whoever owns the project.

---

# Engineering Principles

**Simplicity over cleverness.** The simplest solution that fully satisfies the current milestone wins, even when a more general or more elegant one is available. Three similar lines are preferable to a shared abstraction built for a case that doesn't exist yet.

**Composition over inheritance.** Behavior is built by combining small, independent pieces — a scorer holding a map of strategies, an engine holding a policy — rather than by subclassing. There is no class hierarchy anywhere in the codebase that exists to share behavior; where variation is needed, it's expressed as a different object satisfying the same interface.

**Business logic outside widgets.** A widget's `build()` method renders values it's given; it doesn't compute them. Sorting, filtering, scoring, and explanation all live in providers or services, so they can be tested without a widget tree and reused wherever they're needed next.

**Testability first.** A design that can't be tested without spinning up the UI is treated as a design problem, not a testing problem. This is why the recommendation stack has no Flutter or Riverpod dependency at all — that was a design choice made for testability, not a coincidence.

**Single responsibility.** Each class does one job and knows nothing about the job above or below it. A similarity strategy scores one dimension; it doesn't know it's being combined with four others. A repository persists data; it doesn't know who reads it or why.

**Explicit dependencies.** Every service takes what it needs through its constructor, with a sensible production default. Nothing is reached for through a global, a singleton, or a static lookup — if a class needs something, that need is visible in its signature.

**Incremental evolution instead of rewrites.** When a design outgrows its original shape, the response is to extract or refactor toward the new shape while preserving external behavior — not to rewrite the surrounding system. A policy layer was extracted from an engine that used to hold its own rules; the engine's callers didn't need to change to benefit.

---

# Non-goals

Keeping a codebase maintainable is as much about what it refuses to do as what it does. ValueBrew intentionally avoids:

- **Unnecessary abstractions.** An interface, a base class, or a configuration layer is added when a second real case needs it, not because a third or fourth case might exist someday.
- **Premature optimization.** Performance work is justified by a measured or clearly anticipated cost, not by the possibility that something might be slow at a scale the app hasn't reached.
- **Clever code that reduces readability.** A terser or more idiomatic-looking solution is not preferred over a plainer one if the plainer one is easier for the next reader to verify correct.
- **Feature-driven architecture without clear boundaries.** A feature's needs are met within its own module and its own layer; they are not allowed to blur where recommendation logic, persistence, or UI rendering begin and end.
- **Large rewrites when incremental improvements are sufficient.** A design that has outgrown its shape is extended or refactored in place; it is not replaced wholesale, which would discard already-validated behavior and concentrate risk into one large change.
- **Adding infrastructure before there is a demonstrated need.** A remote-source interface can exist before a remote source is built, because a concrete near-term need (a documented future milestone) is already known — but speculative systems built for needs that aren't yet real are not.

Each of these is a way of spending complexity on a hypothetical instead of a demonstrated requirement. That complexity doesn't stay free once added — it has to be read, maintained, and reasoned about by everyone who touches the code afterward, whether or not the case it was built for ever arrives.

---

# Quality Standards

New code is expected to hold to the same bar as existing code, not a lighter one because it's "just one more feature":

- No duplicated business logic. If a comparison or a rule already exists somewhere, it's called, not re-derived.
- Providers own state. A widget doesn't hold business state in its own `State` object if that state needs to be shared, persisted, or tested independently.
- Widgets remain thin. A screen resolves and renders; it does not decide.
- Repositories isolate persistence. No widget or provider talks to `SharedPreferences`, a file, or a network client directly.
- Tests accompany meaningful behavior changes. A change that alters what the app does — not just how it's written — ships with tests proving the new behavior and, where relevant, the absence of regression in the old.
- A green analyzer before every commit. `flutter analyze` reporting anything short of "No issues found!" means the milestone isn't done.

---

# Commit Philosophy

Commits are intentionally small, and each one represents exactly one logical milestone: one feature added, one bug fixed, one refactor completed. A commit should be understandable from its message and diff alone, without needing the surrounding conversation for context.

This is a deliberate tradeoff against convenience. It would be faster to batch several related changes into one commit, but it would also make the history harder to review, harder to revert selectively, and harder to reason about later — for the same reason a milestone isn't allowed to bundle unrelated work, a commit isn't either. The git history is meant to read as a sequence of intentional, individually-justifiable decisions, not a changelog of "progress."

---

# Testing Philosophy

ValueBrew invests heavily in tests across four layers — unit, widget, provider, and repository — because the parts of the app doing the most consequential work (ranking, filtering, explaining a recommendation) are also the parts where a subtle bug is least likely to be visible just by looking at a screen. A ranking regression that reorders two results, or an explanation that no longer matches the score it's justifying, is exactly the kind of defect a manual pass over the UI would miss.

- **Unit tests** cover data models, utilities, and — most heavily — the recommendation stack, where many small numeric thresholds interact in ways worth pinning down explicitly.
- **Widget tests** confirm a screen renders and responds to interaction correctly, using fake dependencies injected through provider overrides — they are not where business logic is re-verified.
- **Provider tests** confirm that a provider is wired to and composes with its dependencies correctly, independent of whether the logic behind those dependencies is already covered elsewhere.
- **Repository tests** confirm persistence actually round-trips against the storage mechanism being used, including surviving being recreated from scratch.

Tests are written as part of designing a change, not appended afterward to satisfy a checklist. When a milestone changes an existing behavior on purpose, the existing test suite is what makes it possible to say — with evidence, not just confidence — whether anything else broke.

---

# Definition of Done

A milestone is complete only when all of the following are true:

- The feature behaves as intended, not merely as coded.
- Existing functionality has not regressed.
- `flutter analyze` reports no issues.
- The full test suite passes.
- Documentation is updated if the change affected architecture or design.
- The implementation has been reviewed, not just written.
- The Git commit represents one logical milestone.
- The feature is intentionally ready for users, not merely compiling.

None of these substitute for another — a milestone that passes every test but was never reviewed isn't done, and a milestone that's been reviewed but hasn't been re-tested isn't done either. Software quality here is measured by confidence, maintainability, and correctness — not by whether the code happens to run.

---

# Long-Term Vision

ValueBrew is intended to become an explainable beer recommendation platform, not merely a searchable price catalog. The distinction is deliberate: a catalog's job ends at showing accurate data; a recommendation platform's job includes being able to justify, in terms a user can read, why any given suggestion was made.

That direction is already reflected in what exists today — recommendations carry typed reasons alongside their scores, not just a ranked list — but personalization, recommendation profiles, and any use of user-specific signals remain future work, not built yet. Favorites is the first piece of user-generated data the app persists, and it exists in anticipation of that future work, not because personalization has been implemented. The vision is realistic about that gap: the architecture is shaped to make these features straightforward to add later, not to pretend they already exist.
