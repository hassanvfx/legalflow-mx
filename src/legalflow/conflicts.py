"""Local encrypted conflict-check registry; never part of the canonical matter."""

from __future__ import annotations

import json
import os
from pathlib import Path


def _normal(value: str) -> str:
    return " ".join(value.casefold().split())


def _fernet(key_env: str):
    try:
        from cryptography.fernet import Fernet
    except ImportError as error:
        raise ValueError("Falta el componente de cifrado. Reinstala AI LegalFlow MX desde una release verificada.") from error
    key = os.environ.get(key_env)
    if not key:
        raise ValueError(f"Falta la clave local en la variable de entorno {key_env}. No la escribas en el asunto ni en el comando.")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as error:
        raise ValueError(f"La variable {key_env} no contiene una clave de cifrado válida.") from error


def _path(matter: Path) -> Path:
    return matter / ".legalflow-local" / "conflicts.enc"


def _load(matter: Path, key_env: str) -> tuple[object, dict]:
    cipher = _fernet(key_env)
    path = _path(matter)
    if not path.is_file():
        return cipher, {"schema": "legalflow/conflict-registry/v1", "entries": []}
    try:
        return cipher, json.loads(cipher.decrypt(path.read_bytes()).decode("utf-8"))
    except Exception as error:
        raise ValueError("No se pudo abrir el registro local cifrado. No se modificó nada.") from error


def _save(matter: Path, cipher: object, registry: dict) -> None:
    path = _path(matter)
    path.parent.mkdir(parents=True, exist_ok=True)
    plaintext = json.dumps(registry, ensure_ascii=False, sort_keys=True).encode("utf-8")
    path.write_bytes(cipher.encrypt(plaintext))


def add_entity(matter: Path, entity: str, role: str, key_env: str = "LEGALFLOW_CONFLICT_KEY") -> dict:
    if role not in {"client", "adverse", "related"}:
        raise ValueError("El rol debe ser client, adverse o related.")
    if not entity.strip():
        raise ValueError("Escribe la persona u organización a revisar.")
    cipher, registry = _load(matter, key_env)
    normalized = _normal(entity)
    duplicate = any(item.get("normalized") == normalized and item.get("role") == role for item in registry["entries"])
    if not duplicate:
        registry["entries"].append({"entity": entity.strip(), "normalized": normalized, "role": role})
        registry["entries"].sort(key=lambda item: (item["normalized"], item["role"]))
        _save(matter, cipher, registry)
    return {"stored": not duplicate, "role": role, "count": len(registry["entries"])}


def check_entity(matter: Path, entity: str, key_env: str = "LEGALFLOW_CONFLICT_KEY") -> dict:
    if not entity.strip():
        raise ValueError("Escribe la persona u organización a revisar.")
    _, registry = _load(matter, key_env)
    normalized = _normal(entity)
    roles = sorted(item["role"] for item in registry["entries"] if item.get("normalized") == normalized)
    return {"match": bool(roles), "roles": roles, "registry_entries": len(registry["entries"]), "notice": "Coincidencia local: revisa el conflicto con criterio profesional antes de aceptar o rechazar un asunto."}
