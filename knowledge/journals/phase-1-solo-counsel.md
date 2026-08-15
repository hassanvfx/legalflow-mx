---
type: Engineering Journal
title: "Phase 1 - Solo Counsel MVP"
description: "Evidence ingestion, sources, decisions, dashboard, and checkpoints."
tags: [ai-legalflow-mx, phase-1, solo-counsel]
status: draft
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Gate

Clean-machine E2E: install, create Demo, ingest synthetic evidence, build an
evidence-backed timeline/dashboard, make a verified OK checkpoint, and opt in
to a verified private remote without Git commands.

# Dependencies

Phase 0 schemas, materializer, policy checks, and Git wrapper must be stable.

# Progress

- Safe text/PDF ingestion preserves originals before extraction and flags
  embedded instructions as untrusted data.
- Events, deadline candidates, source plans, and a deterministic HTML dashboard
  have initial local implementations.
- Claims, evidence-backed facts, source locks, conservative temporal review,
  Solo Counsel decisions, `ok/*` tags, checkpoint records, and immutable
  snapshots now have initial local implementations.
- `sync-private` now requires an explicit consent flag, a clean `verify`, and
  GitHub proof of private visibility immediately before transfer; it fails
  closed and otherwise preserves local-only mode.
- A deadline can only be marked verified when an evidence trigger, an official
  locked authority, the human-reviewed rule, and a confirmed date are all kept
  in the immutable record. Otherwise it remains a candidate.
- `compare-checkpoint` compares the current reconstructed state against a
  local `ok/*` snapshot without reset, restoration or deletion. It supports a
  new reviewed decision instead of history rewriting.
- CLI ingestion now creates a local semantic evidence commit automatically;
  the lawyer sees the preservation result rather than a Git command.
- Recovery can now clone an explicitly approved private GitHub repository into
  a new folder only after a fresh visibility proof, then runs normal hash
  verification and local view reconstruction. It cannot overwrite a folder.
- Re-importing byte-identical evidence now reuses the immutable document record
  instead of creating a conflicting copy; the import result makes the duplicate
  status explicit while preserving a new extraction record for auditability.
- `legalflow demo` now executes a full synthetic Solo Counsel path locally:
  matter, preserved synthetic notice, evidence-backed claim/fact/act,
  regenerated dashboard, verified `ok/001-demo` tag and snapshot.
- OCR quality, source adapters, clean-machine E2E, and collaboration-safe sync
  remain open.
