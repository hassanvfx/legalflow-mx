"""Narrow Git wrapper that never exposes destructive history rewriting."""
from __future__ import annotations

import subprocess
from pathlib import Path


def run_git(matter: Path, *args: str) -> str:
    forbidden = {"push", "reset"}
    if args and args[0] in forbidden:
        raise PermissionError(f"AI LegalFlow MX does not allow git {args[0]} through this wrapper")
    completed = subprocess.run(["git", "-C", str(matter), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def initialize(matter: Path) -> None:
    if not (matter / ".git").exists():
        run_git(matter, "init", "-b", "main")
        subprocess.run(["git", "-C", str(matter), "config", "user.name", "AI LegalFlow MX (local ledger)"], check=True, text=True, capture_output=True)
        subprocess.run(["git", "-C", str(matter), "config", "user.email", "local-ledger@ai-legalflow.invalid"], check=True, text=True, capture_output=True)
        run_git(matter, "add", ".")
        subprocess.run(["git", "-C", str(matter), "commit", "-m", "[init] Initialize AI LegalFlow MX matter"], check=True, text=True, capture_output=True)


def checkpoint(matter: Path, tag: str, message: str) -> str:
    if not tag.startswith(("ok/", "filed/", "hearing/", "closed/")):
        raise ValueError("Checkpoint tags must be immutable legal tags")
    run_git(matter, "add", ".")
    subprocess.run(["git", "-C", str(matter), "commit", "--allow-empty", "-m", f"[state] {message}"], check=True, text=True, capture_output=True)
    subprocess.run(["git", "-C", str(matter), "tag", "-a", tag, "-m", message], check=True, text=True, capture_output=True)
    return run_git(matter, "rev-parse", "HEAD")


def commit_audit_record(matter: Path, message: str) -> str:
    """Commit a new canonical audit record after its checkpoint tag is fixed."""
    run_git(matter, "add", "objects/checkpoints", "outputs/snapshots")
    subprocess.run(
        ["git", "-C", str(matter), "commit", "--allow-empty", "-m", f"[checkpoint] {message}"],
        check=True,
        text=True,
        capture_output=True,
    )
    return run_git(matter, "rev-parse", "HEAD")


def commit_semantic(matter: Path, category: str, message: str) -> str | None:
    """Commit an ordinary matter event without exposing Git to the lawyer."""
    if not (matter / ".git").exists():
        initialize(matter)
        return run_git(matter, "rev-parse", "HEAD")
    run_git(matter, "add", ".")
    if not run_git(matter, "status", "--porcelain"):
        return None
    subprocess.run(
        ["git", "-C", str(matter), "commit", "-m", f"[{category}] {message}"],
        check=True,
        text=True,
        capture_output=True,
    )
    return run_git(matter, "rev-parse", "HEAD")
