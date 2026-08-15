---
type: Engineering Journal
title: "AI LegalFlow MX execution program"
description: "Master journal for the specification-driven Phase 0–5 delivery program."
tags: [ai-legalflow-mx, program, phases, legal-review]
status: draft
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Goal

Deliver AI LegalFlow MX against the canonical product specification through
verifiable phases. The first product flow is general Solo Counsel, local-first;
Legal Packs require their own Mexican legal review gates.

# Delivery model

- Phase 0: canonical objects, policies, materialization, verification, and Git.
- Phase 1: Solo Counsel workflow, ingestion, sources, deadlines, dashboard, OK.
- Phase 2: governed collaboration and safe sync.
- Phase 3: legal intelligence and security controls.
- Phase 4: visual and operational layer.
- Phase 5: reviewed Legal Packs.

# Rules

- A phase cannot be marked stable without its listed automated tests and release evidence.
- A Legal Pack cannot be marked released without the mandatory Mexican legal-review gate.
- User-facing documentation remains lawyer-first and states capability status truthfully.
- Remote storage remains opt-in and must verify private visibility before push.

# Active milestone

Foundation hardening and Windows-first onboarding — finish the public path from
ChatGPT/Codex to a local-first Demo while completing the remaining formal
Phase 0 and Phase 1 evidence.

# Progress evidence

- Added the versioned schema registry, immutable object writer, deterministic
  accepted-state materializer, object verification, and safe local Git wrapper.
- Added `init`, `ingest`, `status`, `timeline`, `dashboard`, `snapshot`, and
  `ok` CLI surfaces. Source resolution, remote sync, collaboration and pack
  behavior remain gated by their respective phases.
- Phase 0 tests prove reconstruction hash stability across filesystem recovery,
  block unsupported facts and cross-matter paths, and prohibit unsafe local Git
  actions through the product wrapper.
- Phase 1 now has a safe ingestion increment, untrusted-instruction detection,
  event/deadline candidates, source-plan objects, facts/claims, decisions,
  `ok/*` checkpoint tags, snapshots, and a reproducible dashboard.
- Phase 1 private sync is opt-in and fail-closed: it requires explicit consent,
  a passing local verification, and independently queried private visibility;
  clean-machine release evidence remains required before it is stable.
- Phase 2 now has a collaboration scaffold: joined actors have limited roles,
  contributions do not become accepted state automatically, and an unresolved
  disagreement blocks acceptance until the owner records a resolution.
- Phase 2 also has local access revocation and review bundles that exclude
  originals and journals by construction; remote enforcement is still gated.
- Phase 2 safe sync now fetches first, permits only collaboration-only
  fast-forwards, and blocks both divergence and material remote modifications.
- Phase 3 has begun with a deterministic local security audit and immutable
  legal holds; no deletion/retention automation is enabled.
- Phase 3 now also has derived redaction copies that preserve originals and
  record only selected-term hashes; they are never presented as self-validating.
- Phase 3 temporal evaluation now requires an official lock and reviewed
  interval, returning only a candidate applicability result.
- Phase 3 has a limited calendar-day deadline proposer; its output records
  limitations and cannot be treated as a confirmed deadline.
- Phase 3 has a local read-only MCP Legal MX for source locks and temporal
  candidates; web research and legal conclusions remain outside its scope.
- Scenario L now has executable local recovery: `legalflow recover` verifies
  preserved originals first, then reconstructs only the dashboard, client-safe
  view and a content-addressed recovery snapshot. A hash mismatch fails closed
  and leaves evidence untouched.
- Scenario H now has a non-destructive comparison command for `ok/*` snapshots;
  it reports the current delta and directs the lawyer to record a new decision,
  never to rewrite the matter history.
- Phase 4 now has canonical scheduled matter reviews. They are operational
  reminders, not legal deadline calculations, and remain tied to regenerated
  counsel and client-safe views.
- Phase 2 now enforces bundle-first review for personal repositories and a
  confirmed read-only Organization access route with an immutable audit event.
- Phase 3 now has a local encrypted conflict checker kept outside canonical
  matter content and remotes; it is deliberately exact-match and review-only.
- Phase 1 now has an executable synthetic local demonstration from matter
  creation through evidence-backed state, dashboard and an `ok/*` checkpoint.
- The shared acceptance matrix now traces every canonical Scenario A–L to its
  local automated evidence and names the gate still required before release.
- Phase 5 has a pack framework and validator; the repository contains no
  released pack because no Mexican legal-review evidence has been supplied.
- Phase 4 has begun with deterministic counsel/client views and a visual
  contract tied to canonical state; browser visual-regression gates remain open.
- Windows-first onboarding is tracked in the dedicated journal. It covers the
  verified PowerShell bootstrap, explicit-approval `onboard` flow, Codex Skill,
  real download-page capture, clearly labelled instructional illustrations,
  and the equivalent macOS route.
- ADRs 0001–0008 record the irreversible baseline decisions; Phase 2 and Phase
  5 ADRs are design decisions only until their gates have evidence.

# External blockers

- GitHub release publication, Pages deployment, and private-repository creation require account/network authority.
- Legal Pack release requires designated Mexican legal-review evidence.
- Lulu distribution requires publisher metadata and an external wrap cover.

# Workstream journals

- [Windows-first visual onboarding](onboarding-windows-visual.md)

# References

- [Canonical specification](../../LegalFlow_MX_Product_Vision_Technical_Spec_v0.1.html)
- [Foundation journal](legalflow-mx-foundation.md)
