---
type: Architecture Decision Record
title: "ADR 0004: Local-first y GitHub privado por decisión expresa"
description: "Cloud sync stays off until a user opts in."
tags: [adr, privacy, github]
status: accepted
generated:
  by: codex
  at: 2026-08-15T20:00:00Z
---

# ADR 0004: Local-first y GitHub privado por decisión expresa

Estado: aceptado

Todo asunto inicia en `local-only`. GitHub sólo puede habilitarse después de una
decisión explícita y la verificación de visibilidad privada. Contraseñas,
tokens, passkeys y códigos MFA no entran al producto ni a sus journals.
