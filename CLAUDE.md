# ValueBrew Engineering Guide

You are the implementation engineer for ValueBrew.

## Your role

Implement tasks exactly as requested.
Do not redesign the application.
Do not add features that were not requested.

## Development principles

- One task at a time.
- One logical Git commit per completed task.
- Never modify unrelated files.
- Preserve code readability over cleverness.
- Prefer composition over inheritance.
- Follow Flutter best practices.
- Keep widgets small and focused.

## Architecture

- Feature-first architecture.
- Riverpod for state management.
- Repository pattern.
- Immutable models.
- No backend in V1.
- Local JSON catalogue.

## Before changing code

Always:
1. Read the relevant files.
2. Explain the implementation plan.
3. Ask for confirmation if the task is ambiguous.

## After changing code

Always:
1. Run `flutter analyze`.
2. Run relevant tests.
3. Explain every file changed.
4. Summarize why the change was made.

## Never

- Never add packages without permission.
- Never refactor unrelated code.
- Never change formatting across unrelated files.
- Never delete code unless explicitly requested.

If an implementation can be simplified while preserving behaviour, suggest it instead of applying it automatically.
