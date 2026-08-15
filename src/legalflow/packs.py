"""Legal Pack framework; a pack is unavailable until review evidence validates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACK_ROOT = Path(__file__).resolve().parents[2] / "legal-packs"
REQUIRED = ("id", "version", "schema_version", "skills", "sources", "deadline_rules", "taxonomy", "fixtures", "examples", "disclaimers", "legal_review")


def load_pack(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_pack(path: Path) -> list[str]:
    """Validate technical content and mandatory Mexican legal-review evidence."""
    errors: list[str] = []
    try:
        pack = load_pack(path)
    except (OSError, json.JSONDecodeError) as error:
        return [f"Cannot read pack manifest: {error}"]
    for field in REQUIRED:
        if field not in pack or pack[field] in (None, "", []):
            errors.append(f"Missing required pack field: {field}")
    review = pack.get("legal_review", {})
    if review.get("status") != "approved":
        errors.append("Mexican legal review is not approved")
    for field in ("approved_by", "approved_at", "evidence"):
        if not review.get(field):
            errors.append(f"Legal review missing: {field}")
    if not str(pack.get("id", "")).startswith("mx-"):
        errors.append("Pack id must start with mx-")
    return errors


def list_packs(root: Path = PACK_ROOT) -> list[dict[str, str | bool]]:
    result: list[dict[str, str | bool]] = []
    for path in sorted(root.glob("*/pack.json")) if root.exists() else ():
        try:
            pack = load_pack(path)
        except (OSError, json.JSONDecodeError):
            result.append({"path": str(path), "id": "invalid", "released": False})
            continue
        errors = validate_pack(path)
        result.append({"path": str(path), "id": str(pack.get("id", "unknown")), "released": not errors})
    return result
