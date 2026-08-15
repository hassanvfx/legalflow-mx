---
type: Architecture Decision Record
title: "ADR 0007: Colaboración gobernada y estado aceptado"
description: "Design for governed collaboration in Phase 2."
tags: [adr, phase-2, collaboration]
status: draft
generated:
  by: codex
  at: 2026-08-15T20:00:00Z
---

# ADR 0007: Colaboración gobernada y estado aceptado

Estado: aceptado; scaffold inicial implementado en Phase 2.

La colaboración separa notas privadas, contribuciones compartidas y estado
aceptado. Un desacuerdo material bloquea la aceptación automática; el orden de
un push nunca decide por sí mismo un criterio jurídico. El scaffold registra
actores, roles, adhesiones, contribuciones, desacuerdos y resoluciones; safe
sync y revocación continúan sujetos al gate de Phase 2.
