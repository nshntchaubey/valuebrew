# ValueBrew Architecture

**Version:** 1.0  
**Status:** Frozen for External Review  
**Last Updated:** July 2026

---

## Overview

This directory contains the canonical architecture for ValueBrew.

The architecture defines **what the product is**, **why it exists**, and **how it should behave**.

It intentionally does **not** define implementation details, technologies, APIs, databases, or UI styling.

The objective is to ensure that every designer, engineer, reviewer, or AI assistant builds the same product from a single source of truth.

---

## Principles

The architecture is:

- Behavior-first
- Platform independent
- Technology agnostic
- User-centric
- Deterministic
- Internally consistent

---

## Repository Structure

```text
architecture/
│
├── README.md
├── INDEX.md
├── CHANGELOG.md
│
├── current/
│   ├── 00-Architecture-Review-Guide.md
│   ├── ...
│   └── 19-Architectural-Decisions-Record.md
│
└── archive/
```

---

## Reading Order

New readers should begin with:

1. Architecture Review Guide
2. Behavioral Hypothesis Model
3. Product Definition Document

Continue following the sequence described in **INDEX.md**.

---

## Versioning

The `current/` directory contains the latest approved architecture.

Major versions are archived under `archive/`.

Minor revisions are documented in `CHANGELOG.md`.

---

## Status

Version 1.0 is considered feature complete and frozen pending external architectural review.