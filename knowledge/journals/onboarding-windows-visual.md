---
type: Engineering Journal
title: "Windows-first visual onboarding"
description: "A lawyer-first path from ChatGPT and Codex to the first local AI LegalFlow MX matter."
tags: [ai-legalflow-mx, onboarding, windows, codex, accessibility]
status: active
generated:
  by: codex
  at: 2026-08-15T14:00:00Z
---

# Objective

Make the first experience understandable without Terminal, Git, GitHub or
programming knowledge: download ChatGPT, open Codex, paste one instruction,
approve each local change, and create a Demo or first matter in
`%USERPROFILE%\Legal-IA`.

# Scope and sequence

1. Publish the Windows three-step route in the README, Pages and Lulu booklet;
   present macOS immediately after it only where the application, path or
   command differs.
2. Implement a verified PowerShell bootstrap: platform/preflight checks,
   SHA-256 verification with `Get-FileHash`, versioned extraction beneath
   `%LOCALAPPDATA%\AI-LegalFlow-MX`, a user launcher, and resumable setup.
3. Implement `legalflow onboard`: show its plan first; create a workspace only
   with `--confirm`; offer `--demo` or `--matter`; remain local-only by default.
4. Complete the `legalflow-onboarding` Codex Skill. It diagnoses first and
   asks for an explicit approval before every download, installation, folder
   creation or cloud configuration. It never asks for or stores secrets.
5. Capture the current official ChatGPT download page with capture date, URL
   and checksum. Generate four clearly-labelled reference illustrations for
   the Codex steps; they must not impersonate official screenshots.
6. Place the visual sequence in Pages and the booklet, with accessible alt
   text, transcripts, high-contrast treatment, captions and live-page QR.

# Evidence required to close

- Windows 10/11 clean-machine simulation: bootstrap, checksum, launcher,
  diagnosis, approval, workspace and Demo.
- Cancellation tests before download, folder creation and cloud setup: no
  unapproved change and no lost progress.
- Platform-default and custom/existing-workspace tests on Windows and macOS.
- Real-link verification; recorded capture metadata; rendered PDF/Pages visual
  review for legibility, alt text, correct labels and no client data.
- CLI and Skill tests confirm local-only default and no request for passwords,
  tokens, MFA codes or client information.

# Current evidence

- README starts the Windows three-step promise and uses the official ChatGPT
  download link.
- `legalflow onboard` now prints a no-write plan, requires `--confirm`, keeps
  local-only as the default, and creates either the synthetic Demo or a named
  first matter. Its cancellation and local-matter tests pass.
- A first `legalflow-onboarding` Skill structure exists and directs Codex to
  diagnose, explain and request approval before any local change.
- `packaging/install.ps1` now implements prereq checks, release download,
  `Get-FileHash` validation, versioned extraction, a user launcher and
  resumable setup without GitHub authentication.
- Four ImageGen educational illustrations are versioned for the Windows and
  macOS sequence and are placed in the Pages source and Lulu manuscript.
- Captured the live public OpenAI download page on 2026-08-15, with its source
  URL, capture time and SHA-256 in `docs-site/assets/official/`; it is clearly
  captioned as a real capture rather than an illustration.
- Rebuilt and visually inspected the onboarding pages in the 6.25 × 9.25 in
  full-bleed booklet. The PDF preflight passes with embedded fonts and title
  art at 300 ppi or better.
- The booklet now includes all four instructional illustrations and a
  scannable QR route after each visual step. The 17-page rebuilt interior was
  visually checked again after that addition.
- The complete regression suite passes (53 tests); OKF validation passes.
- CI now has a Windows runner that parses `install.ps1` without executing it
  and runs the onboarding/CLI contracts on Windows. The local suite now has
  54 passing tests, including the bootstrap integrity and no-credentials
  contract.
- The documentation generator removes internal capability and acceptance pages
  rather than recreating them in public Pages.
- The release builder now derives the product version from `pyproject.toml`,
  packages the runtime, templates, schemas, fixtures, packs and Windows
  bootstrap, asserts required archive paths, and emits the exact SHA-256 file
  consumed by both bootstrap scripts. Its archive verification passes locally.
- `legalflow onboard --json --confirm` now remains a strict JSON contract even
  while creating the Demo, so Codex can consume it without mixed human output.
  The suite has 56 passing tests.
- The Windows CI integration now deliberately serves a corrupted SHA-256 file
  first and asserts the bootstrap exits without writing a release; it then
  restores the checksum and executes the verified Demo path. The suite has 57
  passing tests.

# Open work

- Publish the prepared repository and observe the Windows CI clean-run result:
  it builds a release, serves it locally, runs the bootstrap with its checksum
  check, verifies the launcher, and creates the Demo in local-only mode. Add
  adverse corrupt-download and permissions cases after the happy-path run is
  green.
- Publish GitHub Pages and review the live site.

# External publication blocker

On 2026-08-15, the local GitHub CLI reported invalid credentials for the
available `hassanvfx` account and could not reach the GitHub API. The worktree
also has no configured remote and all repository contents are untracked.
Publishing, creating the private/public remote, release upload and Pages
deployment therefore require the repository owner to authenticate GitHub and
explicitly authorize the external changes.

## Publication resumed

The repository owner completed GitHub device authentication. On 2026-08-15,
the initial product commit was pushed to the new public repository
`https://github.com/hassanvfx/legalflow-mx`. GitHub Pages deployment is now
configured from the `docs-site/` artifact; release publication and remote CI
evidence are the next actions.

The first remote run exposed two defects: a PowerShell launcher string used an
invalid quote escape, and the public content verifier still required an
intentionally removed internal status page. Both were corrected; the Pages
workflow now requests explicit Pages enablement before deployment.

A subsequent remote run showed that the Windows workflow itself used Bash
environment syntax; it was replaced with PowerShell assignment. GitHub Actions
cannot create the Pages site under this repository policy, so the authenticated
owner account must create the Pages configuration once; deployments can then
use the workflow token.
