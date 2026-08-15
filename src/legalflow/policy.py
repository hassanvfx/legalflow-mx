"""Deterministic, local policy checks; no legal rule lives only in prompts."""
from __future__ import annotations

import re
from pathlib import Path

SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|password|ghp_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)")


def storage_mode(matter: Path) -> str:
    policy = matter / ".legalflow" / "policy.yaml"
    if not policy.is_file():
        return "local-only"
    lines = policy.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "storage:":
            for nested in lines[index + 1 :]:
                if nested and not nested.startswith((" ", "\t")):
                    break
                if nested.strip().startswith("mode:"):
                    return nested.split(":", 1)[1].strip()
        if line.strip().startswith("storage_mode:"):
            return line.split(":", 1)[1].strip()
    return "local-only"


def audit_policy(matter: Path) -> list[str]:
    errors: list[str] = []
    mode = storage_mode(matter)
    if mode not in {"local-only", "github-private", "restricted"}:
        errors.append(f"Unknown storage mode: {mode}")
    for path in matter.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name.endswith(".png"):
            continue
        if path.stat().st_size > 2_000_000:
            continue
        try:
            if SECRET_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
                errors.append(f"Potential secret in {path.relative_to(matter)}")
        except OSError:
            errors.append(f"Cannot inspect {path.relative_to(matter)}")
    return errors


def require_remote_opt_in(matter: Path) -> None:
    if storage_mode(matter) == "local-only":
        raise PermissionError("Cloud sync is blocked: this matter is local-only")


def set_storage_mode(matter: Path, mode: str) -> None:
    """Change only the declared storage mode after an explicit verified opt-in."""
    if mode not in {"local-only", "github-private", "restricted"}:
        raise ValueError(f"Unsupported storage mode: {mode}")
    path = matter / ".legalflow" / "policy.yaml"
    if not path.is_file():
        raise FileNotFoundError(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = False
    for index, line in enumerate(lines):
        if line.strip() == "storage:":
            for nested_index in range(index + 1, len(lines)):
                nested = lines[nested_index]
                if nested and not nested.startswith((" ", "\t")):
                    break
                if nested.strip().startswith("mode:"):
                    indent = nested[: len(nested) - len(nested.lstrip())]
                    lines[nested_index] = f"{indent}mode: {mode}"
                    changed = True
                    break
            break
    if not changed:
        raise ValueError("Policy does not contain storage.mode")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
