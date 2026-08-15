"""Create and verify file-backed AI LegalFlow MX matters."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from .objects import write_object
from .verify import verify_objects

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "matter"


def create_matter(destination: Path, name: str) -> Path:
    root = destination / name
    if root.exists():
        raise FileExistsError(f"Matter already exists: {root}")
    shutil.copytree(TEMPLATE_ROOT, root)
    matter_yaml = root / "matter.yaml"
    matter_yaml.write_text(
        "schema: legalflow/matter/v1\n"
        f"id: MATTER-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}\n"
        f"name: {name}\n"
        "storage_mode: local-only\n"
        "approval_mode: solo\n",
        encoding="utf-8",
    )
    return root


def preserve_original(matter: Path, source: Path) -> dict[str, str | int]:
    if not source.is_file():
        raise FileNotFoundError(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    document_id = f"DOC-{digest[:20].upper()}"
    existing_record = matter / "objects" / "documents" / f"{document_id}.json"
    if existing_record.is_file():
        # Same content is already a preserved original. Keep the first immutable
        # provenance record rather than writing a conflicting second document.
        return json.loads(existing_record.read_text(encoding="utf-8"))
    target = matter / "originals" / f"{digest[:16]}-{source.name}"
    if not target.exists():
        shutil.copy2(source, target)
    record = {
        "id": document_id,
        "schema": "legalflow/document/v1",
        "sha256": digest,
        "size_bytes": source.stat().st_size,
        "original_path": str(target.relative_to(matter)),
        "source": "user_import",
        "received_at": datetime.now(UTC).isoformat(),
    }
    return write_object(matter, "document", record)


def verify_matter(matter: Path) -> list[str]:
    errors: list[str] = []
    required = ("matter.yaml", "AGENTS.md", ".legalflow/policy.yaml", "objects", "originals", "knowledge/journals")
    for item in required:
        if not (matter / item).exists():
            errors.append(f"Missing required matter path: {item}")
    for record_path in (matter / "objects" / "documents").glob("*.json") if (matter / "objects" / "documents").exists() else ():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        original = matter / record["original_path"]
        if not original.is_file():
            errors.append(f"Missing original for {record['id']}")
        elif hashlib.sha256(original.read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"Hash mismatch for {record['id']}")
    errors.extend(verify_objects(matter))
    return errors
