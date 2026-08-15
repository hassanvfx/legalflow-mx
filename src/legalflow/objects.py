"""Canonical immutable matter objects and deterministic materialization."""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

OBJECT_TYPES = {
    "document": ("documents", "DOC"), "claim": ("claims", "CLAIM"),
    "fact": ("facts", "FACT"), "act": ("acts", "ACT"),
    "authority": ("authorities", "AUTH"), "proposal": ("proposals", "PROP"),
    "decision": ("decisions", "DEC"), "deadline": ("deadlines", "DEADLINE"),
    "checkpoint": ("checkpoints", "OK"), "source_plan": ("source-plans", "SOURCEPLAN"),
    "extraction": ("extractions", "EXT"),
    "actor": ("actors", "ACTOR"), "membership": ("memberships", "MEMBER"),
    "contribution": ("contributions", "CONTRIB"), "disagreement": ("disagreements", "DISAGREE"),
    "legal_hold": ("legal-holds", "HOLD"),
    "redaction": ("redactions", "REDACT"),
    "matter_review": ("matter-reviews", "REVIEW"),
    "access_grant": ("access-grants", "ACCESS"),
}


def new_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}-{secrets.token_hex(4).upper()}"


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def object_path(matter: Path, kind: str, object_id: str) -> Path:
    directory, _ = OBJECT_TYPES[kind]
    return matter / "objects" / directory / f"{object_id}.json"


def write_object(matter: Path, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    if kind not in OBJECT_TYPES:
        raise ValueError(f"Unknown object type: {kind}")
    directory, prefix = OBJECT_TYPES[kind]
    data = {"schema": f"legalflow/{kind}/v1", "id": payload.get("id", new_id(prefix)), "created_at": payload.get("created_at", datetime.now(UTC).isoformat()), **payload}
    if not str(data["id"]).startswith(f"{prefix}-"):
        raise ValueError(f"Invalid {kind} ID: {data['id']}")
    target = matter / "objects" / directory / f"{data['id']}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = canonical_json(data)
    if target.exists():
        if target.read_text(encoding="utf-8") != encoded:
            raise FileExistsError(f"Immutable object already exists: {data['id']}")
        return data
    target.write_text(encoded, encoding="utf-8")
    return data


def load_objects(matter: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {kind: [] for kind in OBJECT_TYPES}
    for kind, (directory, _) in OBJECT_TYPES.items():
        for path in sorted((matter / "objects" / directory).glob("*.json")) if (matter / "objects" / directory).exists() else ():
            result[kind].append(json.loads(path.read_text(encoding="utf-8")))
    return result


def matter_id(matter: Path) -> str:
    """Read the stable matter identifier without requiring a YAML dependency."""
    matter_file = matter / "matter.yaml"
    if not matter_file.is_file():
        raise FileNotFoundError(f"Missing matter.yaml: {matter_file}")
    for line in matter_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("id:"):
            identifier = line.partition(":")[2].strip()
            if identifier.startswith("MATTER-"):
                return identifier
            break
    raise ValueError("matter.yaml must contain a MATTER-* id")


def materialize(matter: Path) -> dict[str, Any]:
    objects = load_objects(matter)
    acts = sorted(objects["act"], key=lambda item: (item.get("date", {}).get("value", "9999-12-31"), item["id"]))
    facts = sorted(objects["fact"], key=lambda item: item["id"])
    deadlines = sorted(objects["deadline"], key=lambda item: item["id"])
    superseded_deadlines = {item.get("supersedes") for item in deadlines if item.get("supersedes")}
    resolved_disagreements = {item.get("object") for item in objects["decision"] if item.get("action") == "resolve_disagreement"}
    open_disagreements = [item for item in objects["disagreement"] if item["id"] not in resolved_disagreements]
    released_holds = {item.get("releases") for item in objects["legal_hold"] if item.get("state") == "released"}
    scheduled_reviews = sorted(
        [item for item in objects["matter_review"] if item.get("status") == "scheduled"],
        key=lambda item: (item.get("next_review_on", "9999-12-31"), item["id"]),
    )
    state = {
        "schema": "legalflow/accepted-state/v1",
        "matter": matter_id(matter),
        "generated_at": datetime.now(UTC).isoformat(),
        "counts": {kind: len(items) for kind, items in objects.items()},
        "timeline": acts,
        "facts": facts,
        "deadlines": deadlines,
        "accepted_decisions": [item for item in objects["decision"] if item.get("action") == "accept" and item.get("object") not in {row.get("proposal") for row in open_disagreements}],
        "shared_contributions": sorted(objects["contribution"], key=lambda item: item["id"]),
        "open_disagreements": open_disagreements,
        "active_legal_holds": [item for item in objects["legal_hold"] if item.get("state") == "active" and item["id"] not in released_holds],
        "scheduled_reviews": scheduled_reviews,
        "remote_access_events": sorted(objects["access_grant"], key=lambda item: item["id"]),
        "open_items": [item["id"] for item in deadlines if item.get("status") != "DEADLINE_HUMAN_CONFIRMED" and item["id"] not in superseded_deadlines],
    }
    digest_input = {key: value for key, value in state.items() if key != "generated_at"}
    state["state_hash"] = hashlib.sha256(canonical_json(digest_input).encode()).hexdigest()
    target = matter / "outputs" / "current" / "accepted-state.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(canonical_json(state), encoding="utf-8")
    return state
