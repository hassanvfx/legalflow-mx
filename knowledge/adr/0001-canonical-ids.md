---
type: Architecture Decision Record
title: "ADR 0001: IDs y objetos canónicos inmutables"
description: "Immutable file-backed object identity."
tags: [adr, phase-0, ids]
status: accepted
generated:
  by: codex
  at: 2026-08-15T20:00:00Z
---

# ADR 0001: IDs y objetos canónicos inmutables

Estado: aceptado

Los objetos del asunto usan IDs con prefijo estable y se escriben una sola vez
en archivos JSON canónicos. Un intento de reescribir un ID con contenido
distinto falla. Las vistas y los índices se regeneran desde esos objetos.
