---
type: Engineering Journal
title: "Phase 2 - Collaboration"
description: "Actors, proposals, safe sync, and external access governance."
tags: [ai-legalflow-mx, phase-2, collaboration]
status: draft
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Gate

Disjoint offline work integrates without force-push; conflicts preserve both
positions and cannot change accepted state automatically.

# Progress

- Added immutable actor, membership, contribution, and disagreement records.
- An actor must join the matter before contributing; owner and counsel are the
  only roles that can accept a proposal.
- An open disagreement blocks governed acceptance. An owner must leave a
  separate auditable resolution before a proposal can become accepted.
- The owner can revoke local membership. Reviewer bundles include only selected
  canonical records plus reconstructed views, never originals or journals.
- Safe sync fetches first and can fast-forward only collaboration-only remote
  records. It blocks local/remote divergence and any remote material change,
  preserving both histories for explicit review.
- A local bare-remote regression test proves a peer contribution can be
  fetched and fast-forwarded without GitHub, force-push, or a merge commit.
- Reviewer access now uses bundle-first for a private personal repository.
  For a private GitHub Organization, it can grant or revoke read-only access
  only after confirmation, private visibility proof and a read-only permission
  check; the result becomes an immutable local access event.

# Open work

- Offline multi-machine tests, organization access E2E, and the Phase 2 gate.
