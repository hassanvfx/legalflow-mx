"""Fail-closed private GitHub synchronization for an explicitly opted-in matter."""
from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from .policy import set_storage_mode

REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
Runner = Callable[[list[str], Path | None], str]


class PrivateRemoteError(RuntimeError):
    """An external remote did not meet the privacy proof required for sync."""


def sync_direction(counts: str) -> str:
    """Classify `git rev-list --left-right --count main...origin/main` output."""
    try:
        local_ahead, remote_ahead = (int(value) for value in counts.split())
    except ValueError as error:
        raise PrivateRemoteError("Git no devolvió un diagnóstico de divergencia legible.") from error
    if local_ahead and remote_ahead:
        return "diverged"
    if local_ahead:
        return "local-ahead"
    if remote_ahead:
        return "remote-ahead"
    return "equal"


def _changed_remote_paths(matter: Path, runner: Runner) -> list[str]:
    output = runner(["git", "diff", "--name-only", "main..origin/main"], matter)
    return [line for line in output.splitlines() if line]


def _is_collaboration_only(path: str) -> bool:
    return path.startswith((
        "objects/actors/", "objects/memberships/", "objects/contributions/",
        "objects/disagreements/", "knowledge/journals/",
    ))


def safe_sync(matter: Path, repository: str, runner: Runner | None = None) -> dict[str, str]:
    """Fetch then fast-forward only non-material remote collaboration records.

    It deliberately refuses divergence and remote material changes. Those cases
    require an explicit bundle/review workflow so no conclusion is accepted by
    an implicit merge or push order.
    """
    runner = runner or _run
    if runner(["git", "status", "--porcelain"], matter):
        raise PrivateRemoteError("Hay cambios locales sin registrar; crea un checkpoint antes de sincronizar.")
    proof = private_repository(repository, runner)
    runner(["git", "fetch", "origin"], matter)
    direction = sync_direction(runner(["git", "rev-list", "--left-right", "--count", "main...origin/main"], matter))
    if direction == "diverged":
        raise PrivateRemoteError("Las historias local y remota divergen. Se preservaron ambas; revisa un bundle, no se hizo merge.")
    if direction == "remote-ahead":
        changed = _changed_remote_paths(matter, runner)
        material = [path for path in changed if not _is_collaboration_only(path)]
        if material:
            raise PrivateRemoteError("El remoto contiene cambios materiales; no se integró automáticamente. Revisa un bundle antes de decidir.")
        # A fast-forward cannot rewrite local shared history.
        runner(["git", "merge", "--ff-only", "origin/main"], matter)
        return {"repository": repository, "visibility": proof["visibility"], "url": proof["url"], "direction": direction}
    if direction == "local-ahead":
        # Privacy is checked a second time immediately before the only upload.
        private_repository(repository, runner)
        runner(["git", "push", "--set-upstream", "origin", "main"], matter)
    return {"repository": repository, "visibility": proof["visibility"], "url": proof["url"], "direction": direction}


def _run(command: list[str], cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
    except FileNotFoundError as error:
        raise PrivateRemoteError("GitHub CLI no está instalado. Continúa local-only o consulta la guía de instalación.") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or "comando externo sin detalle"
        raise PrivateRemoteError(detail) from error
    return completed.stdout.strip()


def _validate_repository(repository: str) -> None:
    if not REPOSITORY.fullmatch(repository):
        raise PrivateRemoteError("El repositorio debe escribirse como propietario/repositorio.")


def private_repository(repository: str, runner: Runner = _run) -> dict[str, str]:
    """Return independently queried visibility data, or fail without a remote action."""
    _validate_repository(repository)
    try:
        data = json.loads(runner(["gh", "repo", "view", repository, "--json", "visibility,url"], None))
    except (json.JSONDecodeError, TypeError) as error:
        raise PrivateRemoteError("GitHub no devolvió una verificación de visibilidad legible.") from error
    if data.get("visibility") != "PRIVATE" or not str(data.get("url", "")).startswith("https://github.com/"):
        raise PrivateRemoteError("El remoto no está comprobado como privado; no se configuró ni se envió información.")
    return {"visibility": data["visibility"], "url": data["url"]}


def clone_verified_private(repository: str, destination: Path, runner: Runner = _run) -> dict[str, str]:
    """Clone only a GitHub repository that was just independently proved private."""
    _validate_repository(repository)
    if destination.exists():
        raise PrivateRemoteError("La carpeta de recuperación ya existe; elige una carpeta nueva para no sobrescribir información.")
    proof = private_repository(repository, runner)
    expected = f"https://github.com/{repository}.git"
    runner(["git", "clone", expected, str(destination)], None)
    origin = runner(["git", "remote", "get-url", "origin"], destination)
    if origin != expected:
        raise PrivateRemoteError("La copia recuperada no conserva el remoto privado que se comprobó; no se continuó con la reconstrucción.")
    return {**proof, "destination": str(destination)}


def reviewer_access(repository: str, handle: str, action: str, confirmed: bool, runner: Runner = _run) -> dict[str, str]:
    """Use a private GitHub Organization for read-only reviewer access.

    Personal repositories intentionally fall back to a limited review bundle:
    GitHub's collaborator model is not a verifiable read-only control there.
    """
    _validate_repository(repository)
    if not handle or any(char.isspace() for char in handle):
        raise PrivateRemoteError("El identificador del revisor debe ser una sola palabra.")
    if action not in {"grant", "revoke"}:
        raise PrivateRemoteError("La acción de acceso debe ser grant o revoke.")
    proof = private_repository(repository, runner)
    try:
        owner = json.loads(runner(["gh", "repo", "view", repository, "--json", "owner"], None)).get("owner", {})
    except (json.JSONDecodeError, TypeError) as error:
        raise PrivateRemoteError("GitHub no devolvió el tipo de propietario del repositorio.") from error
    if owner.get("__typename") != "Organization":
        return {"mode": "bundle-first", "repository": repository, "handle": handle, "visibility": proof["visibility"]}
    if not confirmed:
        raise PrivateRemoteError("Confirma explícitamente antes de cambiar el acceso de un revisor.")
    endpoint = f"repos/{repository}/collaborators/{handle}"
    if action == "grant":
        runner(["gh", "api", "--method", "PUT", endpoint, "-f", "permission=pull"], None)
        try:
            permission = json.loads(runner(["gh", "api", f"{endpoint}/permission"], None)).get("permission")
        except (json.JSONDecodeError, TypeError) as error:
            raise PrivateRemoteError("GitHub no devolvió una prueba legible del permiso del revisor.") from error
        if permission not in {"read", "pull"}:
            raise PrivateRemoteError("El permiso del revisor no se comprobó como sólo lectura.")
    else:
        runner(["gh", "api", "--method", "DELETE", endpoint], None)
    return {"mode": "organization-read-only", "repository": repository, "handle": handle, "visibility": proof["visibility"], "action": action, "permission": "read"}


def _origin(matter: Path, runner: Runner) -> str | None:
    try:
        value = runner(["git", "remote", "get-url", "origin"], matter)
    except PrivateRemoteError:
        return None
    return value or None


def sync_private(matter: Path, repository: str, create_private: bool = False, runner: Runner = _run) -> dict[str, str]:
    """Sync main only after GitHub proves that the intended remote is private."""
    _validate_repository(repository)
    try:
        proof = private_repository(repository, runner)
    except PrivateRemoteError:
        if not create_private:
            raise
        runner(["gh", "repo", "create", repository, "--private", "--confirm"], None)
        proof = private_repository(repository, runner)
    expected = f"https://github.com/{repository}.git"
    origin = _origin(matter, runner)
    if origin and origin != expected:
        raise PrivateRemoteError("El remoto origin no coincide con el repositorio privado confirmado; no se envió información.")
    if origin is None:
        runner(["git", "remote", "add", "origin", expected], matter)
    set_storage_mode(matter, "github-private")
    runner(["git", "add", ".legalflow/policy.yaml"], matter)
    runner(["git", "commit", "--allow-empty", "-m", "[privacy] Enable verified private sync"], matter)
    return safe_sync(matter, repository, runner)
