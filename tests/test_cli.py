from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import unittest
from pathlib import Path

from legalflow.cli import main
from legalflow.matter import create_matter, preserve_original, verify_matter
from legalflow.prerequisites import requirement_manifest


class LegalFlowTests(unittest.TestCase):
    def test_manifest_has_unique_public_routes(self) -> None:
        entries = list(requirement_manifest())
        self.assertEqual(len({entry["id"] for entry in entries}), len(entries))
        self.assertTrue(all(entry["url"].endswith(f"{entry['id']}.html") for entry in entries))

    def test_acceptance_matrix_covers_each_specification_scenario(self) -> None:
        matrix = json.loads((Path(__file__).resolve().parents[1] / "docs/content/acceptance-scenarios.json").read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in matrix], list("ABCDEFGHIJKL"))
        self.assertTrue(all({"today", "not_yet", "evidence"} <= set(item) for item in matrix))

    def test_matter_preserves_original(self) -> None:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            temp = Path(directory)
            root = create_matter(temp, "Caso-A")
            evidence = temp / "notificacion.txt"
            evidence.write_text("evidence", encoding="utf-8")
            record = preserve_original(root, evidence)
            self.assertTrue(record["sha256"])
            self.assertEqual(verify_matter(root), [])

    def test_setup_json_is_structured(self) -> None:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            previous = os.environ.get("LEGALFLOW_STATE_PATH")
            os.environ["LEGALFLOW_STATE_PATH"] = str(Path(directory) / "setup-state.json")
            try:
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    main(["setup", "--diagnose", "--json"])
                output = json.loads(capture.getvalue())
            finally:
                if previous is None:
                    os.environ.pop("LEGALFLOW_STATE_PATH", None)
                else:
                    os.environ["LEGALFLOW_STATE_PATH"] = previous
        self.assertIn("checks", output)
        self.assertTrue(all({"id", "status", "url"} <= set(item) for item in output["checks"]))

    def test_ok_creates_tag_snapshot_and_committed_audit_record(self) -> None:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            root = create_matter(Path(directory), "Caso-OK")
            main(["init", str(root)])
            exit_code = main(["ok", "ok/001-intake", "--matter", str(root)])
            self.assertEqual(exit_code, 0)
            checkpoints = list((root / "objects" / "checkpoints").glob("OK-*.json"))
            self.assertEqual(len(checkpoints), 1)
            self.assertTrue(list((root / "outputs" / "snapshots").glob("ok-001-intake-*.json")))
            self.assertEqual(
                subprocess.run(["git", "-C", str(root), "tag", "--list", "ok/001-intake"], text=True, capture_output=True, check=True).stdout.strip(),
                "ok/001-intake",
            )
            self.assertEqual(
                subprocess.run(["git", "-C", str(root), "status", "--porcelain"], text=True, capture_output=True, check=True).stdout.strip(),
                "",
            )

    def test_fact_recorded_by_cli_requires_preserved_document(self) -> None:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            temp = Path(directory)
            root = create_matter(temp, "Caso-Hecho")
            evidence = temp / "evidence.txt"
            evidence.write_text("evidence", encoding="utf-8")
            document = preserve_original(root, evidence)
            self.assertEqual(main(["record-claim", "La notificación fue recibida", "--matter", str(root)]), 0)
            self.assertEqual(main(["record-fact", "La notificación fue recibida", "--document", document["id"], "--matter", str(root)]), 0)
            self.assertEqual(verify_matter(root), [])

    def test_recover_rebuilds_views_from_a_copied_matter_without_changing_original(self) -> None:
        from tempfile import TemporaryDirectory
        import shutil

        with TemporaryDirectory() as directory:
            temp = Path(directory)
            root = create_matter(temp, "Caso-Recuperable")
            evidence = temp / "notificacion.txt"
            evidence.write_text("evidencia sintética", encoding="utf-8")
            record = preserve_original(root, evidence)
            restored = temp / "Equipo-Nuevo"
            shutil.copytree(root, restored)
            original = restored / record["original_path"]
            before = original.read_bytes()
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                exit_code = main(["recover", str(restored), "--json"])
            payload = json.loads(capture.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["recovered"])
            self.assertTrue(Path(payload["dashboard"]).is_file())
            self.assertTrue(Path(payload["snapshot"]).is_file())
            self.assertEqual(original.read_bytes(), before)

    def test_recover_fails_closed_when_an_original_was_altered(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            temp = Path(directory)
            root = create_matter(temp, "Caso-Alterado")
            evidence = temp / "notificacion.txt"
            evidence.write_text("original", encoding="utf-8")
            record = preserve_original(root, evidence)
            (root / record["original_path"]).write_text("alterado", encoding="utf-8")
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                exit_code = main(["recover", str(root), "--json"])
            payload = json.loads(capture.getvalue())
            self.assertEqual(exit_code, 22)
            self.assertFalse(payload["recovered"])
            self.assertTrue(any("Hash mismatch" in error for error in payload["errors"]))

    def test_remote_recover_requires_explicit_confirmation_and_new_destination(self) -> None:
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            exit_code = main(["recover", "--repository", "example/case", "--json"])
        payload = json.loads(capture.getvalue())
        self.assertEqual(exit_code, 22)
        self.assertFalse(payload["recovered"])
        self.assertIn("--confirm", payload["errors"][0])

    def test_compare_checkpoint_is_non_destructive_and_reports_current_changes(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            root = create_matter(Path(directory), "Caso-Comparar")
            main(["init", str(root)])
            self.assertEqual(main(["ok", "ok/001-intake", "--matter", str(root)]), 0)
            self.assertEqual(main(["record-claim", "Nueva posición", "--matter", str(root)]), 0)
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                exit_code = main(["compare-checkpoint", "ok/001-intake", "--matter", str(root), "--json"])
            payload = json.loads(capture.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["changed"])
            self.assertEqual(payload["count_changes"]["claim"], {"before": 0, "now": 1})
            self.assertTrue((root / "objects" / "claims").is_dir())

    def test_ingest_creates_a_semantic_local_ledger_commit(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            temp = Path(directory)
            root = create_matter(temp, "Caso-Ingesta")
            evidence = temp / "notificacion.txt"
            evidence.write_text("evidencia", encoding="utf-8")
            self.assertEqual(main(["ingest", str(evidence), "--matter", str(root)]), 0)
            log = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%s"], text=True, capture_output=True, check=True).stdout.strip()
            self.assertTrue(log.startswith("[evidence] Preserve DOC-"))

    def test_schedule_review_rejects_invalid_dates_and_records_valid_review(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            root = create_matter(Path(directory), "Caso-Revisión")
            self.assertEqual(main(["schedule-review", "no-fecha", "Revisar", "--matter", str(root)]), 22)
            self.assertEqual(main(["schedule-review", "2026-09-01", "Revisar faltantes", "--matter", str(root)]), 0)
            self.assertEqual(len(list((root / "objects" / "matter-reviews").glob("REVIEW-*.json"))), 1)

    def test_demo_runs_the_synthetic_solo_counsel_flow_without_git_arguments(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            self.assertEqual(main(["demo", "--workspace", str(workspace)]), 0)
            root = workspace / "Demo"
            self.assertEqual(verify_matter(root), [])
            self.assertTrue((root / "outputs" / "current" / "dashboard.html").is_file())
            self.assertTrue(list((root / "objects" / "facts").glob("FACT-*.json")))
            self.assertEqual(subprocess.run(["git", "-C", str(root), "tag", "--list", "ok/001-demo"], text=True, capture_output=True, check=True).stdout.strip(), "ok/001-demo")

    def test_onboard_shows_a_no_write_plan_until_confirmed(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            workspace = Path(directory) / "Legal-IA"
            self.assertEqual(main(["onboard", "--workspace", str(workspace), "--demo"]), 0)
            self.assertFalse(workspace.exists())

    def test_onboard_creates_the_selected_local_only_first_matter_after_confirmation(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            workspace = Path(directory) / "Asuntos"
            self.assertEqual(main(["onboard", "--workspace", str(workspace), "--matter", "Primer-Asunto", "--confirm"]), 0)
            root = workspace / "Primer-Asunto"
            self.assertTrue((root / "matter.yaml").is_file())
            self.assertNotIn("github.com", (root / ".git" / "config").read_text(encoding="utf-8"))

    def test_onboard_confirmed_json_has_no_human_output(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                self.assertEqual(main(["onboard", "--workspace", str(Path(directory) / "Legal-IA"), "--demo", "--confirm", "--json"]), 0)
            payload = json.loads(capture.getvalue())
            self.assertTrue(payload["completed"])
            self.assertTrue(payload["local_only"])

    def test_windows_bootstrap_requires_integrity_and_never_handles_secrets(self) -> None:
        script = (Path(__file__).resolve().parents[1] / "packaging" / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("Get-FileHash", script)
        self.assertIn("SHA256", script)
        self.assertIn("$env:LOCALAPPDATA", script)
        self.assertIn("setup --resume", script)
        self.assertNotIn("gh auth login", script)
        self.assertIn("no solicita credenciales de GitHub", script)

    def test_release_builder_contains_the_runtime_template_and_windows_bootstrap(self) -> None:
        builder = (Path(__file__).resolve().parents[1] / "scripts" / "build_release.sh").read_text(encoding="utf-8")
        self.assertIn("schemas fixtures legal-packs", builder)
        self.assertIn("tar -tzf", builder)
        self.assertIn("legalflow/cli.py", builder)

    def test_windows_ci_exercises_bootstrap_checksum_launcher_and_demo(self) -> None:
        workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("Install a verified local release", workflow)
        self.assertIn("LEGALFLOW_RELEASE_BASE", workflow)
        self.assertIn("legalflow.cmd", workflow)
        self.assertIn("onboard --workspace", workflow)
        self.assertIn("Bootstrap accepted a corrupt checksum", workflow)
