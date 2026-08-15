from __future__ import annotations

import json
import unittest
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]


class PluginContractTests(unittest.TestCase):
    def test_manifest_and_skills_are_present(self) -> None:
        plugin = ROOT / "plugin/legalflow-mx"
        manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "legalflow-mx")
        self.assertTrue((plugin / manifest["skills"]).is_dir())
        self.assertGreater(len(list((plugin / "skills").glob("*/SKILL.md"))), 0)

    def test_manifest_has_no_unsupported_hook_field(self) -> None:
        manifest = json.loads((ROOT / "plugin/legalflow-mx/.codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("hooks", manifest)

    def test_legal_mx_mcp_is_read_only_and_lists_local_source_locks(self) -> None:
        from legalflow.matter import create_matter
        from legalflow.sources import lock_source
        from legalflow.mcp_legal_mx import handle_request
        with tempfile.TemporaryDirectory() as directory:
            root = create_matter(Path(directory), "Demo")
            authority = lock_source(root, "https://www.dof.gob.mx/example", "Fuente sintética", b"version", Path(directory) / "cache", "2025-01-01")
            response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "legalflow_sources", "arguments": {"matter": str(root)}}})
            self.assertIn(authority["id"], response["result"]["content"][0]["text"])
            self.assertTrue((root / "objects" / "authorities" / f"{authority['id']}.json").is_file())
