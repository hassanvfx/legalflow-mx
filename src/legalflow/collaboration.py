"""Governed collaboration records; shared activity never accepts itself."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from .objects import load_objects, materialize, object_path, write_object

ROLES = {"owner", "counsel", "reviewer", "observer"}


def invite(matter: Path, handle: str, role: str) -> dict:
    if role not in ROLES:
        raise ValueError(f"Unsupported role: {role}")
    if not handle or any(char.isspace() for char in handle):
        raise ValueError("Actor handle must be a non-empty single identifier")
    return write_object(matter, "actor", {"handle": handle, "role": role, "state": "invited"})


def join(matter: Path, actor_id: str) -> dict:
    objects = load_objects(matter)
    if actor_id not in {actor["id"] for actor in objects["actor"]}:
        raise ValueError("Unknown invited actor")
    return write_object(matter, "membership", {"actor": actor_id, "state": "joined"})


def membership_states(matter: Path) -> dict[str, str]:
    """Return the last immutable membership event for each actor."""
    states: dict[str, str] = {}
    for entry in sorted(load_objects(matter)["membership"], key=lambda item: (item.get("created_at", ""), item["id"])):
        states[entry.get("actor", "")] = entry.get("state", "")
    return states


def active_actor(matter: Path, actor_id: str) -> dict:
    objects = load_objects(matter)
    actor = next((item for item in objects["actor"] if item["id"] == actor_id), None)
    if actor is None or membership_states(matter).get(actor_id) != "joined":
        raise ValueError("Actor has not joined this matter")
    return actor


def contribute(matter: Path, actor_id: str, summary: str) -> dict:
    active_actor(matter, actor_id)
    return write_object(matter, "contribution", {"actor": actor_id, "summary": summary, "layer": "shared"})


def disagree(matter: Path, actor_id: str, proposal_id: str, reason: str) -> dict:
    active_actor(matter, actor_id)
    if proposal_id not in {item["id"] for item in load_objects(matter)["proposal"]}:
        raise ValueError("Unknown proposal")
    return write_object(matter, "disagreement", {"actor": actor_id, "proposal": proposal_id, "reason": reason, "state": "open"})


def accept_proposal(matter: Path, actor_id: str, proposal_id: str, reason: str) -> dict:
    actor = active_actor(matter, actor_id)
    if actor["role"] not in {"owner", "counsel"}:
        raise PermissionError("Only owner or counsel may accept a proposal")
    objects = load_objects(matter)
    if proposal_id not in {item["id"] for item in objects["proposal"]}:
        raise ValueError("Unknown proposal")
    resolved = {item.get("object") for item in objects["decision"] if item.get("action") == "resolve_disagreement"}
    open_disagreements = [item for item in objects["disagreement"] if item.get("proposal") == proposal_id and item.get("state") == "open" and item["id"] not in resolved]
    if open_disagreements:
        raise PermissionError("A material disagreement is open; acceptance is blocked")
    return write_object(matter, "decision", {"action": "accept", "object": proposal_id, "actor": actor_id, "mode": "governed", "reason": reason})


def resolve_disagreement(matter: Path, actor_id: str, disagreement_id: str, reason: str) -> dict:
    actor = active_actor(matter, actor_id)
    if actor["role"] != "owner":
        raise PermissionError("Only owner may resolve a material disagreement")
    if disagreement_id not in {item["id"] for item in load_objects(matter)["disagreement"]}:
        raise ValueError("Unknown disagreement")
    return write_object(matter, "decision", {"action": "resolve_disagreement", "object": disagreement_id, "actor": actor_id, "mode": "governed", "reason": reason})


def revoke(matter: Path, owner_id: str, actor_id: str, reason: str) -> dict:
    owner = active_actor(matter, owner_id)
    if owner["role"] != "owner":
        raise PermissionError("Only owner may revoke access")
    if actor_id == owner_id:
        raise PermissionError("An owner cannot revoke their own access")
    active_actor(matter, actor_id)
    return write_object(matter, "membership", {"actor": actor_id, "state": "revoked", "by": owner_id, "reason": reason})


def review_bundle(matter: Path, record_ids: list[str]) -> Path:
    """Create a minimal reviewer bundle that never includes originals or journals."""
    objects = load_objects(matter)
    index = {item["id"]: kind for kind, rows in objects.items() for item in rows}
    unknown = sorted(set(record_ids) - set(index))
    if unknown:
        raise ValueError(f"Unknown canonical record(s): {', '.join(unknown)}")
    state = materialize(matter)
    dashboard = matter / "outputs" / "current" / "dashboard.html"
    if not dashboard.exists():
        from .render import dashboard as render_dashboard
        render_dashboard(matter, state)
    manifest = {
        "schema": "legalflow/review-bundle/v1",
        "matter": state["matter"],
        "state_hash": state["state_hash"],
        "records": sorted(record_ids),
        "contains_originals": False,
        "contains_journals": False,
        "review_notice": "Contenido para revisión. No es una aceptación automática ni sustituye revisión jurídica.",
    }
    fingerprint = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:12]
    target = matter / "outputs" / "review-bundles" / f"review-{fingerprint}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("bundle.json", json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        archive.write(matter / "outputs" / "current" / "accepted-state.json", "accepted-state.json")
        archive.write(dashboard, "dashboard.html")
        for record_id in sorted(record_ids):
            path = object_path(matter, index[record_id], record_id)
            archive.write(path, f"objects/{path.name}")
    return target
