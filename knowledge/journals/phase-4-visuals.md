---
type: Engineering Journal
title: "Phase 4 - Visual and operational layer"
description: "Deterministic dashboard, snapshots, client-safe outputs, and review cadence."
tags: [ai-legalflow-mx, phase-4, visuals]
status: draft
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Gate

Every published snapshot is regenerated from canonical objects and passes visual regression.

# Progress

- Added a deterministic visual contract containing the state hash and content
  hashes for the counsel dashboard and client-safe summary.
- The client summary is data-minimized: it excludes fact/evidence text and
  explicitly states it is illustrative, not a legal conclusion.
- `visual-verify` blocks a changed/missing artifact or a contract that no
  longer represents the current canonical state.
- `schedule-review` records a human review date and purpose as a canonical,
  reconstructible record. Counsel and client-safe views expose its count or
  date while clearly distinguishing it from a legal deadline.

# Open work

- Browser accessibility audit, rendered visual snapshots, client template
  choices, and the full Phase 4 gate.
