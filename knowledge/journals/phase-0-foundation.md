---
type: Engineering Journal
title: "Phase 0 - Foundation"
description: "Canonical file-backed legal objects and deterministic verification."
tags: [ai-legalflow-mx, phase-0, schemas, verification]
status: draft
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Goal

Make a matter reconstructible from canonical files and local Git, without a
hidden mutable database.

# Acceptance evidence

- Schemas and fixtures validate.
- Objects are immutable and IDs are stable.
- Materialized state is regenerated from objects.
- Verify rejects unsupported facts, altered originals, cross-matter references,
  forbidden policy states, and unsafe Git history operations.

# Next actions

- [x] Define schema registry and immutable object store.
- [x] Implement materializer, deterministic object verify, and safe local Git wrapper.
- [x] Add first Phase 0 fixtures and regression tests.
- [x] Add baseline policy engine, cross-matter guard, v1 migration guard, and Git-history regression cases.
- [x] Prove state hash survives recovery to another filesystem location.
- [ ] Expand contract coverage for every schema field and run the formal Phase 0 release gate.
