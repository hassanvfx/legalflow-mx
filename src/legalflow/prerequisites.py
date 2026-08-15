"""Deterministic setup checks and their shared documentation contract."""

from __future__ import annotations

import os
import platform
import shutil
import socket
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

DOCS_BASE = "https://hassanvfx.github.io/legalflow-mx/setup"


@dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    severity: str
    why: str
    action: str
    fallback: str

    @property
    def url(self) -> str:
        return f"{DOCS_BASE}/{self.id}.html"


REQUIREMENTS = (
    Requirement("codex", "ChatGPT Codex", "required", "AI LegalFlow MX uses Codex for guided matter work.", "Install or update Codex, then run legalflow setup --resume.", "The CLI and template can be installed now; guided work waits for Codex."),
    Requirement("git", "Git", "required", "Git preserves evidence history and checkpoints.", "Install Git using the command for your operating system.", "Choose another machine or complete this step later."),
    Requirement("github-cli", "GitHub CLI", "optional", "GitHub CLI is used only for private cloud synchronization.", "Install gh, or continue in local-only mode.", "Continue in local-only mode without cloud synchronization."),
    Requirement("github-auth", "GitHub authentication", "optional", "Authentication is needed only to create or sync a private repository.", "Run gh auth login and complete the browser flow directly with GitHub.", "Continue in local-only mode. No credential is needed by AI LegalFlow MX."),
    Requirement("network", "Network connection", "optional", "Network access is needed for releases, official sources, and cloud sync.", "Check DNS, proxy, captive portal, or try again later.", "Use already installed local functionality and retry safely later."),
    Requirement("permissions", "Writable workspace", "required", "AI LegalFlow MX must create only the selected matter and local setup state.", "Choose a writable folder such as ~/Legal-IA.", "Do not grant broad administrator access; pick another folder."),
)


@dataclass
class CheckResult:
    id: str
    status: str
    title: str
    why: str
    action: str
    fallback: str
    url: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _result(requirement: Requirement, status: str) -> CheckResult:
    return CheckResult(requirement.id, status, requirement.title, requirement.why, requirement.action, requirement.fallback, requirement.url)


def run_checks(home: Path | None = None) -> list[CheckResult]:
    """Run only local, non-interactive checks. Never access credentials."""
    home = home or Path.home()
    checks: list[CheckResult] = []
    codex = shutil.which("codex") or shutil.which("chatgpt")
    checks.append(_result(REQUIREMENTS[0], "ready" if codex else "attention"))
    checks.append(_result(REQUIREMENTS[1], "ready" if shutil.which("git") else "blocked"))
    gh = shutil.which("gh")
    checks.append(_result(REQUIREMENTS[2], "ready" if gh else "optional"))
    checks.append(_result(REQUIREMENTS[3], "ready" if gh and _gh_authenticated() else "optional"))
    checks.append(_result(REQUIREMENTS[4], "ready" if _network_available() else "optional"))
    checks.append(_result(REQUIREMENTS[5], "ready" if os.access(home, os.W_OK) else "blocked"))
    return checks


def _gh_authenticated() -> bool:
    # Do not invoke gh: it may prompt or expose account details. Setup can ask later.
    return bool(os.environ.get("LEGALFLOW_GITHUB_AUTHENTICATED"))


def _network_available() -> bool:
    try:
        socket.getaddrinfo("github.com", 443, type=socket.SOCK_STREAM)
        return True
    except OSError:
        return False


def platform_summary() -> dict[str, str]:
    return {"system": platform.system(), "machine": platform.machine(), "python": platform.python_version()}


def requirement_manifest() -> Iterable[dict[str, str]]:
    for requirement in REQUIREMENTS:
        yield {**asdict(requirement), "url": requirement.url}
