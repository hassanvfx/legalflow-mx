"""Local security audit and immutable legal-hold records."""
from __future__ import annotations

import subprocess
from pathlib import Path

from .objects import load_objects, write_object
from .policy import storage_mode


def remote_urls(matter: Path) -> dict[str, list[str]]:
    if not (matter / ".git").exists():
        return {}
    remotes = subprocess.run(["git", "-C", str(matter), "remote"], text=True, capture_output=True, check=False)
    if remotes.returncode:
        return {}
    result: dict[str, list[str]] = {}
    for name in remotes.stdout.splitlines():
        urls = subprocess.run(["git", "-C", str(matter), "remote", "get-url", "--all", name], text=True, capture_output=True, check=False)
        if urls.returncode == 0:
            result[name] = [url for url in urls.stdout.splitlines() if url]
    return result


def security_audit(matter: Path) -> dict[str, list[str] | dict[str, list[str]]]:
    """Report remote and legal-hold state without changing the matter."""
    errors: list[str] = []
    warnings: list[str] = []
    urls = remote_urls(matter)
    mode = storage_mode(matter)
    if mode == "local-only" and urls:
        errors.append("A local-only matter has a configured Git remote")
    for name, values in urls.items():
        for url in values:
            allowed = url.startswith("https://github.com/") or url.startswith("git@github.com:")
            if mode == "github-private" and not allowed:
                errors.append(f"Remote {name} is not an approved GitHub URL")
            if url.startswith("http://"):
                errors.append(f"Remote {name} uses insecure HTTP")
    objects = load_objects(matter)
    released = {item.get("releases") for item in objects["legal_hold"] if item.get("state") == "released"}
    active = [item["id"] for item in objects["legal_hold"] if item.get("state") == "active" and item["id"] not in released]
    if active:
        warnings.append(f"Active legal hold(s): {', '.join(active)}. Automatic deletion remains disabled.")
    return {"errors": errors, "warnings": warnings, "remotes": urls, "active_holds": active}


def place_legal_hold(matter: Path, reason: str) -> dict:
    if not reason.strip():
        raise ValueError("A legal hold needs a reason")
    return write_object(matter, "legal_hold", {"state": "active", "reason": reason})


def release_legal_hold(matter: Path, hold_id: str, reason: str) -> dict:
    holds = {item["id"] for item in load_objects(matter)["legal_hold"] if item.get("state") == "active"}
    if hold_id not in holds:
        raise ValueError("Unknown active legal hold")
    if not reason.strip():
        raise ValueError("A hold release needs a reason")
    return write_object(matter, "legal_hold", {"state": "released", "releases": hold_id, "reason": reason})
