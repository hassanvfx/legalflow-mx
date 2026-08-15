"""Conservative arithmetic proposals for deadlines; never legal conclusions."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from .objects import load_objects, write_object
from .sources import temporal_status


def propose_calendar_deadline(matter: Path, document_id: str, authority_id: str, start_date: str, days: int, rule: str) -> dict:
    """Record a calendar-day proposal that requires subsequent human confirmation."""
    if days < 0 or days > 3650:
        raise ValueError("El número de días debe estar entre 0 y 3650")
    start = date.fromisoformat(start_date)
    if not rule.strip():
        raise ValueError("Describe la regla que revisaste antes de calcular")
    objects = load_objects(matter)
    if document_id not in {item["id"] for item in objects["document"]}:
        raise ValueError("No existe el documento desencadenante preservado")
    authority = next((item for item in objects["authority"] if item["id"] == authority_id), None)
    if authority is None or temporal_status(authority, start_date)["status"] != "candidate_applicable":
        raise ValueError("La fuente oficial no tiene vigencia candidata para la fecha de inicio")
    proposed_due = (start + timedelta(days=days)).isoformat()
    return write_object(matter, "deadline", {
        "trigger": {"act": document_id, "verified": False},
        "status": "DEADLINE_CANDIDATE",
        "support": [document_id],
        "candidate_date": proposed_due,
        "authority": authority_id,
        "rule": rule,
        "calculation": {"method": "calendar_days", "start_date": start_date, "days": days, "proposed_due": proposed_due, "limitations": ["No considera días inhábiles", "No considera suspensión de plazos", "Requiere confirmación humana"]},
    })
