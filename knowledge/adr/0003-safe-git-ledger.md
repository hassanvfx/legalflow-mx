---
type: Architecture Decision Record
title: "ADR 0003: Ledger Git local y no destructivo"
description: "No destructive history operations through product flows."
tags: [adr, phase-0, git]
status: accepted
generated:
  by: codex
  at: 2026-08-15T20:00:00Z
---

# ADR 0003: Ledger Git local y no destructivo

Estado: aceptado

El producto inicializa un ledger Git local sin exponer comandos Git al abogado.
El wrapper rechaza `reset` y `push`; los puntos seguros usan etiquetas legales
inmutables y un registro de auditoría posterior. La recuperación parte de
objetos y del historial, nunca de una base de datos oculta.
