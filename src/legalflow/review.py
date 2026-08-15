"""Safe comparison of a current matter against an immutable checkpoint view."""

from __future__ import annotations

import json
from pathlib import Path


def _snapshot_for_tag(matter: Path, tag: str) -> Path:
    safe = "".join(char if char.isalnum() or char in "-_" else "-" for char in tag)
    matches = sorted((matter / "outputs" / "snapshots").glob(f"{safe}-*.json"))
    if not matches:
        raise ValueError(f"No local snapshot exists for checkpoint {tag}")
    return matches[-1]


def compare_checkpoint(matter: Path, tag: str, current: dict) -> dict:
    """Report a non-destructive comparison; it never changes Git or objects."""
    snapshot_path = _snapshot_for_tag(matter, tag)
    previous = json.loads(snapshot_path.read_text(encoding="utf-8"))
    changed_counts = {
        kind: {"before": previous.get("counts", {}).get(kind, 0), "now": current.get("counts", {}).get(kind, 0)}
        for kind in sorted(set(previous.get("counts", {})) | set(current.get("counts", {})))
        if previous.get("counts", {}).get(kind, 0) != current.get("counts", {}).get(kind, 0)
    }
    return {
        "checkpoint": tag,
        "checkpoint_state_hash": previous.get("state_hash"),
        "current_state_hash": current["state_hash"],
        "changed": previous.get("state_hash") != current["state_hash"],
        "count_changes": changed_counts,
        "instruction": (
            "Esta comparación no restaura ni borra nada. Revisa los cambios y registra una nueva propuesta o decisión "
            "basada en la evidencia actual."
        ),
    }
