---
type: Engineering Journal
title: "Phase 3 - Legal intelligence and security"
description: "Sources, deadlines, redaction, audit, and MCP Legal MX."
tags: [ai-legalflow-mx, phase-3, security, sources]
status: draft
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Gate

Adversarial documents, ambiguous deadlines, remote visibility, and cross-matter
access all fail closed with deterministic evidence.

# Progress

- Added `security-audit`: a local-only matter with a configured remote fails
  verification; private mode only permits approved GitHub URL forms.
- Added immutable legal-hold and hold-release records. The audit shows active
  holds and explicitly states that no deletion is automated.
- Added exact-term derived redactions from extracted text. Original evidence is
  unchanged; the redaction object stores only term hashes and verifies the
  derived-output hash. Human visual review remains required.
- Extended the temporal resolver: it accepts a human-reviewed effective
  interval only on an official locked source, returns candidate applicability,
  and rejects reversed intervals or unverified sources.
- Added a generic calendar-day deadline proposal. It requires a preserved
  trigger, official source and reviewed rule, records its limitations, and
  remains a candidate until a human separately confirms it.
- Added a local read-only MCP Legal MX surface for stored source locks and
  temporal checks. It has no network, write, or legal-conclusion tool.
- Added an encrypted local conflict registry. It accepts exact normalized
  entities, never enters canonical objects or sync, and requires a user-held
  environment key. A match is a human-review prompt, never a legal conclusion.

# Open work

- Jurisprudence workflow, robust temporal resolver, entity resolution beyond
  exact matching, audience policies, retention engine, redaction workflow,
  and the full adversarial Phase 3 gate.
