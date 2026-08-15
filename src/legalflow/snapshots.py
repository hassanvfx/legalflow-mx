"""Immutable milestone snapshots derived from a materialized matter state."""
from __future__ import annotations

import json
from pathlib import Path


def snapshot(matter: Path, state: dict, label: str) -> Path:
    """Persist a content-addressed copy of a state without changing it."""
    safe = "".join(char if char.isalnum() or char in "-_" else "-" for char in label)
    target = matter / "outputs" / "snapshots" / f"{safe}-{state['state_hash'][:12]}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return target
