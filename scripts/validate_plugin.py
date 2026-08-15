"""Portable structural validation for the AI LegalFlow MX Codex plugin."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "plugin/legalflow-mx")
    manifest_path = root / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        print("FAIL: missing plugin manifest")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    if manifest.get("name") != root.name:
        errors.append("plugin name must match its directory")
    if not manifest.get("interface", {}).get("displayName", "").startswith("AI LegalFlow MX"):
        errors.append("plugin display name must use the public brand")
    if "hooks" in manifest:
        errors.append("unsupported hooks field in plugin manifest")
    if not (root / "skills").is_dir() or not list((root / "skills").glob("*/SKILL.md")):
        errors.append("no plugin skills found")
    if errors:
        print("FAIL:", *errors, sep="\n")
        return 1
    print("PASS: AI LegalFlow MX plugin manifest and Skills are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
