"""Deterministic, lawyer-first HTML views from canonical state."""
from __future__ import annotations

import html
import hashlib
import json
from pathlib import Path
from typing import Any


def dashboard(matter: Path, state: dict[str, Any]) -> Path:
    timeline = "".join(f"<li><b>{html.escape(item.get('date', {}).get('value', 'Fecha pendiente'))}</b> — {html.escape(item.get('type', 'Evento'))} <small>{html.escape(item['id'])}</small></li>" for item in state["timeline"]) or "<li>No hay eventos registrados todavía.</li>"
    deadlines = "".join(f"<li><b>Confirmación requerida</b> — {html.escape(item['id'])}: aún no se calcula una fecha cierta.</li>" for item in state["deadlines"]) or "<li>No hay plazos candidatos.</li>"
    facts = "".join(
        f"<li><b>{html.escape(item.get('status', 'unknown'))}</b> — {html.escape(item.get('statement', item['id']))} <small>{html.escape(item['id'])}</small></li>"
        for item in state["facts"]
    ) or "<li>No hay hechos registrados todavía.</li>"
    reviews = "".join(
        f"<li><b>{html.escape(item.get('next_review_on', 'Fecha pendiente'))}</b> — {html.escape(item.get('purpose', 'Revisión del asunto'))} <small>{html.escape(item['id'])}</small></li>"
        for item in state["scheduled_reviews"]
    ) or "<li>No hay revisiones programadas.</li>"
    counts = "".join(f"<li>{html.escape(kind)}: {count}</li>" for kind, count in state["counts"].items() if count)
    content = f"""<!doctype html><html lang=\"es-MX\"><meta charset=\"utf-8\"><title>AI LegalFlow MX — Estado del asunto</title><style>body{{font:18px/1.5 system-ui;margin:3rem auto;max-width:900px;color:#172033}}h1,h2{{color:#7f1d1d}}.warn{{background:#fff7ed;border-left:4px solid #c2410c;padding:1rem}}small{{color:#64748b}}</style><h1>Estado del asunto</h1><p>Esta vista se vuelve a crear desde los archivos del asunto. No sustituye revisión jurídica.</p><p class=\"warn\">Los plazos sólo se muestran como confirmados cuando existe evidencia y regla verificadas.</p><h2>Hechos y nivel de respaldo</h2><ul>{facts}</ul><h2>Línea de tiempo</h2><ul>{timeline}</ul><h2>Plazos</h2><ul>{deadlines}</ul><h2>Revisiones programadas</h2><ul>{reviews}</ul><h2>Objetos guardados</h2><ul>{counts}</ul><p><small>Huella del estado: {html.escape(state['state_hash'])}</small></p></html>"""
    target = matter / "outputs" / "current" / "dashboard.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def client_summary(matter: Path, state: dict[str, Any]) -> Path:
    """Create an intentionally data-minimized, client-safe operational view."""
    content = f"""<!doctype html><html lang="es-MX"><meta charset="utf-8"><title>AI LegalFlow MX — Resumen de seguimiento</title><style>body{{font:18px/1.5 system-ui;margin:3rem auto;max-width:800px;color:#172033}}h1,h2{{color:#7f1d1d}}.notice{{background:#eff6ff;border-left:4px solid #2563eb;padding:1rem}}</style><h1>Resumen de seguimiento</h1><p class="notice">Vista ilustrativa de avance. No contiene el texto de evidencia, no confirma conclusiones jurídicas y no sustituye la comunicación profesional.</p><h2>Actividad registrada</h2><ul><li>Hechos con nivel de respaldo: {len(state['facts'])}</li><li>Eventos en línea de tiempo: {len(state['timeline'])}</li><li>Plazos que requieren revisión: {len(state['open_items'])}</li><li>Revisiones programadas: {len(state['scheduled_reviews'])}</li><li>Desacuerdos abiertos: {len(state['open_disagreements'])}</li></ul><p>Solicita a tu abogada o abogado revisar los documentos, la regla aplicable y cualquier plazo antes de actuar.</p><p><small>Huella del estado: {html.escape(state['state_hash'])}</small></p></html>"""
    target = matter / "outputs" / "current" / "client-summary.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def render_visuals(matter: Path, state: dict[str, Any]) -> dict[str, Path]:
    """Build deterministic counsel and client views plus their visual contract."""
    counsel = dashboard(matter, state)
    client = client_summary(matter, state)
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (counsel, client)}
    manifest = {
        "schema": "legalflow/visual-contract/v1",
        "state_hash": state["state_hash"],
        "artifacts": hashes,
        "counsel_view": "dashboard.html",
        "client_view": "client-summary.html",
        "client_view_contains_evidence_text": False,
        "images_are_evidence": False,
    }
    manifest_path = matter / "outputs" / "current" / "visual-contract.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {"dashboard": counsel, "client_summary": client, "contract": manifest_path}


def verify_visuals(matter: Path, state: dict[str, Any]) -> list[str]:
    """Verify existing visual artifacts against the current canonical state."""
    manifest_path = matter / "outputs" / "current" / "visual-contract.json"
    if not manifest_path.is_file():
        return ["Missing visual contract; run legalflow dashboard"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["Visual contract is not valid JSON"]
    errors: list[str] = []
    if manifest.get("state_hash") != state["state_hash"]:
        errors.append("Visual contract does not match current state")
    if manifest.get("client_view_contains_evidence_text") is not False or manifest.get("images_are_evidence") is not False:
        errors.append("Visual contract has unsafe evidence flags")
    for filename, expected in manifest.get("artifacts", {}).items():
        path = matter / "outputs" / "current" / filename
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"Visual artifact changed or missing: {filename}")
    return errors
