---
type: Architecture Decision Record
title: "ADR 0002: Compatibilidad de schemas y migraciones"
description: "Explicit compatible schema evolution."
tags: [adr, phase-0, schemas]
status: accepted
generated:
  by: codex
  at: 2026-08-15T20:00:00Z
---

# ADR 0002: Compatibilidad de schemas y migraciones

Estado: aceptado

Cada objeto declara `legalflow/<tipo>/vN`. Una versión mayor exige migración
explícita, idempotente y probada; v1 se conserva sin transformación. Nunca se
actualiza un archivo de evidencia para aparentar compatibilidad.
