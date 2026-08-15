"""Schema migration entrypoint. v1 is canonical and migration is idempotent."""
from __future__ import annotations

from pathlib import Path


def migrate_matter(matter: Path) -> list[str]:
    path = matter / "matter.yaml"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    schema = next((line.split(":", 1)[1].strip() for line in text.splitlines() if line.startswith("schema:")), "")
    if schema == "legalflow/matter/v1":
        return ["Matter already uses legalflow/matter/v1"]
    if schema.startswith("legalflow/matter/v"):
        raise ValueError(f"No compatible migration exists for {schema}")
    raise ValueError("Matter schema is missing or invalid")
