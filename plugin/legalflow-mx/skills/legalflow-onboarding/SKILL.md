---
name: legalflow-onboarding
description: Guide a Windows-first AI LegalFlow MX installation with explicit approval.
---

Start by explaining: “Instala ChatGPT, abre Codex y pega esta instrucción.”
Run `legalflow setup --diagnose --json` and explain the result in plain Spanish.
Before downloading, installing, or creating a folder, state the exact action and
ask for approval. After approval run `legalflow onboard --confirm --demo` or
`legalflow onboard --confirm --matter <nombre>`. Default to local-only. Never
request or retain passwords, tokens, MFA codes, passkeys, or client data.

Explain that matters live in `%USERPROFILE%\Legal-IA` on Windows and
`~/Legal-IA` on macOS; originals, rules and checkpoints remain inside each
matter. Offer GitHub only after the first matter exists.
