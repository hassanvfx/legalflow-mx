"""Deterministic verification of canonical matter objects."""
from __future__ import annotations

from pathlib import Path
import hashlib
from datetime import date

from .objects import OBJECT_TYPES, load_objects
from .policy import audit_policy
from .security import security_audit


def verify_objects(matter: Path) -> list[str]:
    errors: list[str] = []
    objects = load_objects(matter)
    ids = {item["id"] for values in objects.values() for item in values if "id" in item}
    documents = {item["id"] for item in objects["document"]}
    for kind, values in objects.items():
        _, prefix = OBJECT_TYPES[kind]
        for item in values:
            if item.get("schema") != f"legalflow/{kind}/v1":
                errors.append(f"{item.get('id', 'unknown')}: invalid schema")
            if not str(item.get("id", "")).startswith(f"{prefix}-"):
                errors.append(f"{item.get('id', 'unknown')}: invalid ID prefix")
    for fact in objects["fact"]:
        support = fact.get("support", [])
        if not support:
            errors.append(f"{fact['id']}: a fact needs documentary support")
        for ref in support:
            if ref not in documents:
                errors.append(f"{fact['id']}: unknown document support {ref}")
        if fact.get("claim") and fact["claim"] not in {item["id"] for item in objects["claim"]}:
            errors.append(f"{fact['id']}: unknown claim {fact['claim']}")
    for act in objects["act"]:
        for ref in act.get("support", []):
            if ref not in documents:
                errors.append(f"{act['id']}: unknown document support {ref}")
    for deadline in objects["deadline"]:
        if deadline.get("status") == "DEADLINE_VERIFIED" and not deadline.get("trigger", {}).get("verified"):
            errors.append(f"{deadline['id']}: verified deadline has an unverified trigger")
        if deadline.get("status") == "DEADLINE_VERIFIED":
            if not deadline.get("authority") or deadline["authority"] not in {item["id"] for item in objects["authority"]}:
                errors.append(f"{deadline['id']}: verified deadline needs a locked authority")
            if not deadline.get("rule") or not deadline.get("candidate_date"):
                errors.append(f"{deadline['id']}: verified deadline needs a rule and date")
        if deadline.get("supersedes") and deadline["supersedes"] not in {item["id"] for item in objects["deadline"]}:
            errors.append(f"{deadline['id']}: deadline supersedes an unknown record")
    for authority in objects["authority"]:
        temporal = authority.get("temporal", {})
        start, end = temporal.get("effective_from"), temporal.get("effective_to")
        if start and end and end < start:
            errors.append(f"{authority['id']}: source temporal interval is reversed")
    proposals = {item["id"] for item in objects["proposal"]}
    actors = {item["id"] for item in objects["actor"]}
    membership_states: dict[str, str] = {}
    for membership in sorted(objects["membership"], key=lambda item: (item.get("created_at", ""), item["id"])):
        membership_states[membership.get("actor", "")] = membership.get("state", "")
    joined = {actor for actor, state in membership_states.items() if state == "joined"}
    disagreements = {item["id"] for item in objects["disagreement"]}
    for membership in objects["membership"]:
        if membership.get("actor") not in actors:
            errors.append(f"{membership['id']}: membership references unknown actor")
    for contribution in objects["contribution"]:
        if contribution.get("actor") not in joined:
            errors.append(f"{contribution['id']}: contribution is not from a joined actor")
    for disagreement in objects["disagreement"]:
        if disagreement.get("actor") not in joined:
            errors.append(f"{disagreement['id']}: disagreement is not from a joined actor")
        if disagreement.get("proposal") not in proposals:
            errors.append(f"{disagreement['id']}: disagreement references an unknown proposal")
    for decision in objects["decision"]:
        if decision.get("action") == "accept" and decision.get("object") not in proposals:
            errors.append(f"{decision['id']}: decision references an unknown proposal")
        if decision.get("action") == "resolve_disagreement" and decision.get("object") not in disagreements:
            errors.append(f"{decision['id']}: decision references an unknown disagreement")
        if decision.get("mode") == "governed" and decision.get("actor") not in joined:
            errors.append(f"{decision['id']}: governed decision is not from a joined actor")
    resolved = {item.get("object") for item in objects["decision"] if item.get("action") == "resolve_disagreement"}
    for decision in objects["decision"]:
        if decision.get("action") == "accept" and decision.get("mode") == "governed":
            if any(item.get("proposal") == decision.get("object") and item["id"] not in resolved for item in objects["disagreement"]):
                errors.append(f"{decision['id']}: accepted proposal has an unresolved disagreement")
    active_holds = {item["id"] for item in objects["legal_hold"] if item.get("state") == "active"}
    for hold in objects["legal_hold"]:
        if hold.get("state") == "active" and not hold.get("reason"):
            errors.append(f"{hold['id']}: legal hold needs a reason")
        if hold.get("state") == "released" and hold.get("releases") not in active_holds:
            errors.append(f"{hold['id']}: hold release references an unknown active hold")
    for review in objects["matter_review"]:
        if review.get("status") != "scheduled":
            errors.append(f"{review['id']}: matter review must be scheduled")
        try:
            date.fromisoformat(review.get("next_review_on", ""))
        except (TypeError, ValueError):
            errors.append(f"{review['id']}: matter review needs next_review_on in YYYY-MM-DD format")
        if not str(review.get("purpose", "")).strip():
            errors.append(f"{review['id']}: matter review needs a purpose")
    for access in objects["access_grant"]:
        if access.get("action") not in {"grant", "revoke"}:
            errors.append(f"{access['id']}: access event needs grant or revoke action")
        if access.get("permission") != "read":
            errors.append(f"{access['id']}: reviewer access must remain read-only")
        if not str(access.get("repository", "")).strip() or not str(access.get("handle", "")).strip():
            errors.append(f"{access['id']}: access event needs repository and reviewer handle")
    extractions = {item["id"] for item in objects["extraction"]}
    for redaction in objects["redaction"]:
        if redaction.get("document") not in documents or redaction.get("extraction") not in extractions:
            errors.append(f"{redaction['id']}: redaction has an unknown source")
            continue
        target = matter / redaction.get("output_path", "")
        if not target.is_file():
            errors.append(f"{redaction['id']}: redaction output is missing")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != redaction.get("sha256"):
            errors.append(f"{redaction['id']}: redaction output hash mismatch")
    for item in (matter / "objects").rglob("*.json") if (matter / "objects").exists() else ():
        if item.resolve().parents and matter.resolve() not in item.resolve().parents:
            errors.append(f"Object outside matter: {item}")
        text = item.read_text(encoding="utf-8")
        if '"../' in text or '"/' in text:
            errors.append(f"{item.relative_to(matter)}: cross-matter or absolute path is forbidden")
    errors.extend(audit_policy(matter))
    errors.extend(security_audit(matter)["errors"])
    return errors
