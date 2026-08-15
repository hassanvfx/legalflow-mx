# Knowledge Update Log

## YYYY-MM-DD

* **Initialization**: Created the ClineFlow OKF knowledge bundle.

## 2026-08-15

* **LegalFlow MX foundation**: Added the product bootstrap, CLI, plugin,
  matter template, documentation source, and booklet pipeline journal.
* **AI LegalFlow MX editorial reconstruction**: Migrated the public brand,
  created the full-bleed Mexican legal-tech title artwork, and expanded the
  booklet and Pages into an honest v0.1 capability guide.
* **AI LegalFlow MX execution program**: Opened the master program and Phase 0
  journals for specification-driven implementation with legal review gates.
* **Phase 0 first increment**: Added versioned canonical-object contracts,
  deterministic materialization, supported-fact verification, safe local Git
  checkpoints, and foundation regression tests.
* **Phase 1 first increment**: Added preservation-first ingestion, detection of
  untrusted embedded instructions, event/deadline candidates, source plans, and
  a deterministic lawyer-first dashboard.
* **Phase 0 reconstruction hardening**: Made accepted-state hashes independent
  of an absolute local path; added content-addressed snapshots and an auditable
  checkpoint record committed after each protected `ok/*` tag.
* **Phase 1 evidence increment**: Added CLI flows for positions and
  evidence-backed facts, visible fact-confidence labels in the dashboard, and
  source/decision/checkpoint coverage in the Solo Counsel journal.
* **Architecture decisions**: Recorded ADRs 0001–0008 for IDs, schemas, local
  Git, local-first privacy, sources, deadlines, collaboration and Legal Packs.
* **Phase 1 private-sync increment**: Added an explicit `sync-private` command
  that rejects absent consent, invalid matters, public/ambiguous remotes, and
  missing GitHub CLI credentials without transmitting data.
* **Phase 1 deadline increment**: Added immutable verified-deadline records
  that require an evidence trigger, a locked official source, reviewed rule,
  and confirmed date; unsupported certainty is rejected by verification.
* **Phase 2 collaboration scaffold**: Added actor, membership, contribution and
  disagreement records. A material disagreement blocks governed acceptance
  until an owner records its resolution; no ordering of shared records decides
  a legal conclusion.
* **Phase 2 external-review increment**: Added auditable local membership
  revocation and review bundles that include only selected canonical records,
  reconstructed views and a manifest, never originals or journals.
* **Phase 2 safe-sync increment**: Added divergence classification and a
  fail-closed fetch path: only non-material collaboration records can
  fast-forward; material remote changes and divergent history stay untouched.
* **Phase 2 offline-sync evidence**: Added an end-to-end local bare-remote
  test proving an offline peer contribution fast-forwards into the matter
  without history rewriting or external account access.
* **Phase 3 security increment**: Added remote/policy security audit and
  immutable legal-hold records. Local-only matters with remotes are blocked;
  hold release is an explicit auditable record and never triggers deletion.
* **Phase 3 redaction increment**: Added exact-term derived text copies that
  preserve originals, store term hashes rather than sensitive terms, and fail
  verification if their output hash changes.
* **Phase 5 framework increment**: Added Legal Pack manifest validation that
  blocks release until technical contents and dated Mexican legal-review
  evidence are present. No Legal Pack was added or announced as released.
* **Phase 4 visual increment**: Added deterministic counsel and data-minimized
  client views, plus a visual contract that binds artifact hashes to the
  canonical state and can be checked with `visual-verify`.
* **Phase 3 temporal-source increment**: Added official-source interval input
  and conservative temporal evaluation; it returns a candidate only and blocks
  unverified or temporally reversed source records.
* **Phase 3 deadline increment**: Added a generic calendar-day proposal that
  requires preserved trigger/source/rule context and records that it excludes
  inhábiles, suspension and jurisdiction-specific treatment.
* **Phase 3 MCP increment**: Added a local read-only MCP Legal MX server for
  stored source locks and temporal candidates; it has no network or mutation
  tool and passed plugin structural validation.
* **Acceptance Scenario L increment**: Replaced the recovery help-only command
  with a fail-closed local rebuild. It verifies originals before regenerating
  discardable views and a recovery snapshot; altered evidence blocks recovery.
* **Acceptance Scenario H increment**: Added `compare-checkpoint` for a
  non-destructive comparison with an immutable `ok/*` snapshot. It exposes the
  delta for a new reviewed decision and never performs reset or restoration.
* **Acceptance Scenario C increment**: CLI ingestion now writes a semantic
  local evidence commit after preservation and extraction, without requiring a
  visible Git command from the lawyer.
* **Acceptance traceability**: Added a lawyer-first A–L acceptance matrix to
  Pages source. Each scenario names what is automated today, what is still
  required, and the regression test that supplies the current evidence.
* **Acceptance Scenario L remote increment**: Added explicit-confirmation
  recovery cloning. It only proceeds after GitHub proves private visibility,
  requires a new destination, checks the resulting origin, then verifies and
  rebuilds the recovered matter.
* **Phase 4 review increment**: Added canonical scheduled reviews with a
  purpose and ISO date. Regenerated views show them as reminders, never as
  legal deadlines.
* **Phase 1 ingestion deduplication**: Byte-identical imports now reuse their
  existing immutable document record and report that result; this prevents
  duplicate originals while retaining the preservation-first workflow.
* **Phase 2 reviewer-access increment**: Personal repositories now fall back
  to limited review bundles. Private Organizations can grant or revoke a
  reviewer’s read-only access only after confirmation and visibility proof,
  then record the event locally.
* **Phase 3 conflict increment**: Added an encrypted local conflict registry
  keyed only through a user environment variable. It never joins matter
  objects or sync and returns a human-review signal rather than a conclusion.
* **Phase 1 Demo increment**: Added `legalflow demo`, a synthetic end-to-end
  local Solo Counsel exercise that creates evidence-backed state, a dashboard,
  snapshot and protected OK checkpoint without GitHub or client data.
* **Phase 5 pack journals**: Added the eight practice-pack draft manifests and
  per-pack journals. They remain unreleased until individual Mexican legal
  review, ADR, source/rule content and regression evidence exist.
* **Windows-first onboarding plan**: Opened the visual onboarding journal for
  the verified PowerShell bootstrap, Codex-guided approval flow, educational
  visuals and cross-platform acceptance evidence.
* **Windows-first onboarding increment**: Added `legalflow onboard`, a
  verified PowerShell bootstrap, Codex onboarding Skill, four clearly labelled
  ImageGen reference illustrations, and the Windows-first Pages/README/booklet
  route. Product regression tests and OKF validation passed.
* **Onboarding editorial verification**: Captured the official OpenAI download
  page with source metadata and SHA-256; corrected the booklet renderer so it
  renders Markdown images and prompt blocks rather than printing their syntax.
  The rebuilt 14-page Lulu interior passed preflight and visual inspection.
* **Onboarding QR completion**: Added the missing prompt and macOS reference
  illustrations to the booklet and a live-guide QR after every onboarding
  visual. The 17-page interior passed preflight and visual inspection.
* **Windows onboarding CI increment**: Added a Windows GitHub Actions job that
  parses the PowerShell bootstrap and exercises CLI contracts, plus a local
  integrity/no-credentials test. Public Pages generation now excludes the
  internal capability and acceptance reports.
* **Release artifact hardening**: The release builder now packages the complete
  runtime contract, validates its required paths and verifies its emitted
  SHA-256 checksum; CI runs the same build-and-verify sequence.
* **Onboarding JSON contract**: Confirmed onboarding now suppresses human
  messages under `--json`; an automated test proves the result parses as one
  machine-readable local-only completion record.
* **Windows clean-run CI**: Added a Windows runner integration path that builds
  a release, serves it locally, invokes the verified PowerShell bootstrap and
  proves the launcher can create the local-only Demo.
* **Windows checksum adversarial test**: The Windows integration path now
  proves that a corrupted SHA-256 fails before a product release is written,
  then restores the checksum for the successful Demo path.
* **Publication check**: GitHub CLI credentials for the available accounts are
  invalid, API access failed, no remote is configured and the worktree is
  entirely untracked. Release and Pages publication require owner authentication
  and authorization.
