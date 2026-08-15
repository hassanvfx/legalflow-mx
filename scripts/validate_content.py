"""Ensure every documented setup item has a generated GitHub Pages route."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    entries = json.loads((ROOT / "docs/content/setup-manifest.json").read_text(encoding="utf-8"))
    missing = [entry["id"] for entry in entries if not (ROOT / "docs-site/setup" / f"{entry['id']}.html").is_file()]
    if missing:
        print("Missing GitHub Pages guides:", ", ".join(missing))
        return 1
    print(f"PASS: {len(entries)} setup routes exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
