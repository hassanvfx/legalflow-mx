"""Friendly command-line interface for AI LegalFlow MX."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path

from . import BRAND, __version__
from .git import checkpoint, commit_audit_record, commit_semantic, initialize
from .github import PrivateRemoteError, clone_verified_private, reviewer_access, sync_private
from .decisions import accept_solo, propose
from .collaboration import accept_proposal, contribute, disagree, invite, join, resolve_disagreement, revoke, review_bundle
from .ingest import ingest as ingest_document
from .matter import create_matter, preserve_original, verify_matter
from .migrate import migrate_matter
from .objects import materialize
from .prerequisites import platform_summary, run_checks
from .render import dashboard as render_dashboard, render_visuals, verify_visuals
from .sources import lock_source, temporal_status
from .snapshots import snapshot as create_snapshot
from .security import place_legal_hold, release_legal_hold, security_audit
from .redaction import redact_document
from .packs import list_packs, validate_pack
from .deadlines import propose_calendar_deadline
from .conflicts import add_entity as add_conflict_entity, check_entity as check_conflict_entity
from .review import compare_checkpoint


def _credit() -> None:
    print(f"{BRAND} · Hassan Uriostegui y Aurora Cotne")


def _save_state(checks: list[dict[str, str]]) -> None:
    state_path = Path(os.environ.get("LEGALFLOW_STATE_PATH", str(Path.home() / ".legalflow" / "setup-state.json")))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"version": __version__, "checks": checks}, indent=2) + "\n", encoding="utf-8")


def _show_checks(as_json: bool) -> int:
    checks = [result.as_dict() for result in run_checks()]
    _save_state(checks)
    if as_json:
        print(json.dumps({"platform": platform_summary(), "checks": checks}, indent=2))
    else:
        labels = {"ready": "LISTO", "attention": "ATENCION REQUERIDA", "optional": "OPCIONAL", "blocked": "BLOQUEADO"}
        for check in checks:
            print(f"[{labels[check['status']]}] {check['title']}")
            if check["status"] != "ready":
                print(f"  Por que importa: {check['why']}")
                print(f"  Que hacer: {check['action']}")
                print(f"  Guia: {check['url']}")
                print(f"  Alternativa segura: {check['fallback']}")
                print("  Reanudar: legalflow setup --resume")
        print()
        _credit()
    return 0 if all(item["status"] != "blocked" for item in checks) else 2


def _default_workspace() -> Path:
    """Return the familiar local workspace for the current operating system."""
    if os.name == "nt" or platform.system() == "Windows":
        return Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Legal-IA"
    return Path.home() / "Legal-IA"


def _onboarding_plan(workspace: Path, content: str | None) -> list[str]:
    first = "una demostración segura" if content == "demo" else f"el asunto “{content}”"
    return [
        "1. Revisar los requisitos de esta computadora.",
        f"2. Crear la carpeta local de asuntos: {workspace}",
        f"3. Crear {first} sin enviar información a GitHub.",
        "4. Explicar dónde quedan los originales, las reglas y los puntos seguros.",
    ]


def _run_demo(workspace: Path, name: str, *, emit: bool = True) -> int:
    """Create the synthetic first matter used by both `demo` and onboarding."""
    from .objects import write_object

    workspace.mkdir(parents=True, exist_ok=True)
    root = create_matter(workspace, name)
    initialize(root)
    fixture = Path(__file__).with_name("fixtures") / "notificacion.txt"
    record = ingest_document(root, fixture)
    commit_semantic(root, "evidence", f"Preserve {record['document']['id']}")
    claim_record = write_object(root, "claim", {"statement": "La notificación sintética fue recibida.", "status": "reported", "support": [record["document"]["id"]]})
    write_object(root, "fact", {"statement": "La notificación sintética fue recibida.", "status": "documented", "support": [record["document"]["id"]], "claim": claim_record["id"]})
    write_object(root, "act", {"type": "recepción de notificación sintética", "date": {"value": "2026-08-15", "confidence": "documented"}, "status": "DOCUMENTED", "support": [record["document"]["id"]]})
    errors = verify_matter(root)
    if errors:
        print("DEMO BLOQUEADA", *[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
        return 22
    state = materialize(root)
    dashboard_path = render_visuals(root, state)["dashboard"]
    commit = checkpoint(root, "ok/001-demo", "Synthetic Solo Counsel demonstration")
    checkpoint_record = write_object(root, "checkpoint", {"git_tag": "ok/001-demo", "git_commit": commit, "summary": "Synthetic Solo Counsel demonstration", "state_hash": state["state_hash"]})
    snapshot_path = create_snapshot(root, state, "ok/001-demo")
    commit_audit_record(root, f"Record {checkpoint_record['id']} for ok/001-demo")
    if emit:
        print(f"Demo local lista: {root}")
        print(f"Vista para revisión: {dashboard_path}")
        print(f"Punto seguro creado: ok/001-demo; fotografía: {snapshot_path.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="legalflow", description="AI LegalFlow MX setup and matter workflow")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("setup", help="Check prerequisites and save resumable state")
    setup.add_argument("--resume", action="store_true")
    setup.add_argument("--diagnose", action="store_true")
    setup.add_argument("--json", action="store_true")
    doctor = sub.add_parser("doctor", help="Run setup diagnostics")
    doctor.add_argument("--json", action="store_true")
    onboard = sub.add_parser("onboard", help="Guide the approved local setup for the first matter")
    onboard.add_argument("--workspace", type=Path, default=_default_workspace())
    first_content = onboard.add_mutually_exclusive_group()
    first_content.add_argument("--demo", action="store_true", help="Create the synthetic local demonstration")
    first_content.add_argument("--matter", help="Create the named first local matter")
    onboard.add_argument("--confirm", action="store_true", help="Approve creating the local workspace and selected first content")
    onboard.add_argument("--json", action="store_true", help="Print the plan in a stable machine-readable format")
    create = sub.add_parser("create-matter", help="Create a local-only matter")
    create.add_argument("name")
    create.add_argument("--workspace", type=Path, default=Path.home() / "Legal-IA")
    demo = sub.add_parser("demo", help="Create a complete synthetic Solo Counsel demonstration locally")
    demo.add_argument("--name", default="Demo")
    demo.add_argument("--workspace", type=Path, default=Path.home() / "Legal-IA")
    init = sub.add_parser("init", help="Initialize a local matter and its safe Git ledger")
    init.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    ingest = sub.add_parser("ingest", help="Preserve one document as evidence")
    ingest.add_argument("source", type=Path)
    ingest.add_argument("--matter", type=Path, default=Path.cwd())
    claim = sub.add_parser("record-claim", help="Record a reported position that still needs review")
    claim.add_argument("statement")
    claim.add_argument("--matter", type=Path, default=Path.cwd())
    fact = sub.add_parser("record-fact", help="Record a statement backed by a preserved document")
    fact.add_argument("statement")
    fact.add_argument("--document", required=True)
    fact.add_argument("--claim")
    fact.add_argument("--status", choices=("documented", "reported", "inferred"), default="documented")
    fact.add_argument("--matter", type=Path, default=Path.cwd())
    act = sub.add_parser("record-act", help="Record an evidence-backed event for the timeline")
    act.add_argument("type")
    act.add_argument("date")
    act.add_argument("--document", required=True)
    act.add_argument("--matter", type=Path, default=Path.cwd())
    deadline = sub.add_parser("record-deadline", help="Record a deadline candidate; it is not a confirmed date")
    deadline.add_argument("--document", required=True)
    deadline.add_argument("--matter", type=Path, default=Path.cwd())
    confirm_deadline = sub.add_parser("confirm-deadline", help="Record a human-confirmed deadline with its source rule")
    confirm_deadline.add_argument("deadline", help="Candidate deadline ID")
    confirm_deadline.add_argument("--authority", required=True, help="Locked authority ID")
    confirm_deadline.add_argument("--rule", required=True, help="Rule reviewed by the lawyer")
    confirm_deadline.add_argument("--due", required=True, help="Confirmed due date, YYYY-MM-DD")
    confirm_deadline.add_argument("--matter", type=Path, default=Path.cwd())
    calculate_deadline = sub.add_parser("calculate-deadline", help="Propose a calendar-day deadline; requires human confirmation")
    calculate_deadline.add_argument("--document", required=True)
    calculate_deadline.add_argument("--authority", required=True)
    calculate_deadline.add_argument("--start", required=True, help="Fecha de inicio revisada, YYYY-MM-DD")
    calculate_deadline.add_argument("--days", required=True, type=int, help="Días calendario de la regla revisada")
    calculate_deadline.add_argument("--rule", required=True, help="Regla revisada por la persona profesional")
    calculate_deadline.add_argument("--matter", type=Path, default=Path.cwd())
    source_plan = sub.add_parser("source-plan", help="Create the official-source research plan for this matter")
    source_plan.add_argument("--matter", type=Path, default=Path.cwd())
    source_resolve = sub.add_parser("source-resolve", help="Fija una fuente y conserva su huella")
    source_resolve.add_argument("url")
    source_resolve.add_argument("title")
    source_resolve.add_argument("--effective-from", help="Inicio de vigencia revisado, YYYY-MM-DD")
    source_resolve.add_argument("--effective-to", help="Fin de vigencia revisado, YYYY-MM-DD")
    source_resolve.add_argument("--authority-type", default="unknown", help="Ej. ley, reglamento, jurisprudencia")
    source_resolve.add_argument("--matter", type=Path, default=Path.cwd())
    temporal = sub.add_parser("source-temporal", help="Explica si una fuente podría aplicar en una fecha")
    temporal.add_argument("authority")
    temporal.add_argument("date")
    temporal.add_argument("--matter", type=Path, default=Path.cwd())
    proposal = sub.add_parser("propose", help="Registra una posición para revisión")
    proposal.add_argument("issue")
    proposal.add_argument("position")
    proposal.add_argument("--depends-on", action="append", default=[])
    proposal.add_argument("--matter", type=Path, default=Path.cwd())
    decision = sub.add_parser("decide", help="Acepta una propuesta en modo Solo Counsel")
    decision.add_argument("proposal")
    decision.add_argument("reason")
    decision.add_argument("--matter", type=Path, default=Path.cwd())
    status = sub.add_parser("status", help="Rebuild and show current matter state")
    status.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    status.add_argument("--json", action="store_true")
    timeline = sub.add_parser("timeline", help="Show evidence-backed events")
    timeline.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    timeline.add_argument("--json", action="store_true")
    dashboard = sub.add_parser("dashboard", help="Rebuild a deterministic dashboard")
    dashboard.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    visual_verify = sub.add_parser("visual-verify", help="Verify visual outputs against canonical state")
    visual_verify.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    visual_verify.add_argument("--json", action="store_true")
    schedule_review = sub.add_parser("schedule-review", help="Record a human review date; it is not a legal deadline")
    schedule_review.add_argument("date", help="Fecha de revisión, YYYY-MM-DD")
    schedule_review.add_argument("purpose", help="Qué debe revisarse")
    schedule_review.add_argument("--matter", type=Path, default=Path.cwd())
    snapshot = sub.add_parser("snapshot", help="Materialize the current state")
    snapshot.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    ok = sub.add_parser("ok", help="Create a verified local checkpoint")
    ok.add_argument("tag")
    ok.add_argument("--message", default="Legal checkpoint")
    ok.add_argument("--matter", type=Path, default=Path.cwd())
    compare = sub.add_parser("compare-checkpoint", help="Compare a current matter with a point-safe snapshot without restoring history")
    compare.add_argument("tag", help="Existing local checkpoint tag, for example ok/001-intake")
    compare.add_argument("--matter", type=Path, default=Path.cwd())
    compare.add_argument("--json", action="store_true")
    sync = sub.add_parser("sync-private", help="Sync only to a GitHub repository proved private")
    sync.add_argument("repository", help="GitHub owner/repository")
    sync.add_argument("--confirm", action="store_true", help="Confirm that this matter may leave this Mac")
    sync.add_argument("--create-private", action="store_true", help="Create the named GitHub repository as private if missing")
    sync.add_argument("--matter", type=Path, default=Path.cwd())
    invite_actor = sub.add_parser("invite", help="Invite a collaborator with a limited role")
    invite_actor.add_argument("handle")
    invite_actor.add_argument("role", choices=("owner", "counsel", "reviewer", "observer"))
    invite_actor.add_argument("--matter", type=Path, default=Path.cwd())
    join_actor = sub.add_parser("join", help="Record that an invited collaborator joined this matter")
    join_actor.add_argument("actor")
    join_actor.add_argument("--matter", type=Path, default=Path.cwd())
    contribution = sub.add_parser("contribute", help="Record a shared contribution without accepting it")
    contribution.add_argument("actor")
    contribution.add_argument("summary")
    contribution.add_argument("--matter", type=Path, default=Path.cwd())
    disagreement = sub.add_parser("disagree", help="Record a material disagreement about a proposal")
    disagreement.add_argument("proposal")
    disagreement.add_argument("actor")
    disagreement.add_argument("reason")
    disagreement.add_argument("--matter", type=Path, default=Path.cwd())
    accept = sub.add_parser("accept-proposal", help="Accept a proposal only when no disagreement remains")
    accept.add_argument("proposal")
    accept.add_argument("actor")
    accept.add_argument("reason")
    accept.add_argument("--matter", type=Path, default=Path.cwd())
    resolve = sub.add_parser("resolve-disagreement", help="Record an owner's resolution of a disagreement")
    resolve.add_argument("disagreement")
    resolve.add_argument("actor")
    resolve.add_argument("reason")
    resolve.add_argument("--matter", type=Path, default=Path.cwd())
    revoke_actor = sub.add_parser("revoke", help="Revoke a collaborator's local matter access")
    revoke_actor.add_argument("actor")
    revoke_actor.add_argument("owner")
    revoke_actor.add_argument("reason")
    revoke_actor.add_argument("--matter", type=Path, default=Path.cwd())
    bundle = sub.add_parser("review-bundle", help="Create a limited bundle for an external reviewer")
    bundle.add_argument("--include", action="append", required=True, help="Canonical record ID to include; originals are never included")
    bundle.add_argument("--matter", type=Path, default=Path.cwd())
    reviewer_access_cmd = sub.add_parser("reviewer-access", help="Grant or revoke read-only reviewer access through a private GitHub Organization")
    reviewer_access_cmd.add_argument("repository", help="GitHub owner/repository")
    reviewer_access_cmd.add_argument("handle", help="GitHub handle of the reviewer")
    reviewer_access_cmd.add_argument("--revoke", action="store_true", help="Revoke instead of grant")
    reviewer_access_cmd.add_argument("--confirm", action="store_true", help="Confirm the remote access change")
    reviewer_access_cmd.add_argument("--matter", type=Path, default=Path.cwd())
    hold = sub.add_parser("legal-hold", help="Record a legal hold; no deletion workflow is automated")
    hold.add_argument("reason")
    hold.add_argument("--matter", type=Path, default=Path.cwd())
    release_hold = sub.add_parser("release-legal-hold", help="Record a reviewed release of a legal hold")
    release_hold.add_argument("hold")
    release_hold.add_argument("reason")
    release_hold.add_argument("--matter", type=Path, default=Path.cwd())
    audit = sub.add_parser("security-audit", help="Audit remotes, secrets policy and legal holds")
    audit.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    audit.add_argument("--json", action="store_true")
    redact = sub.add_parser("redact", help="Create a derived text copy using exact human-selected terms")
    redact.add_argument("document")
    redact.add_argument("--replace", action="append", required=True, help="Exact text to replace; it is not stored in the redaction record")
    redact.add_argument("--matter", type=Path, default=Path.cwd())
    conflict_add = sub.add_parser("conflict-add", help="Add an entity to the encrypted local conflict registry")
    conflict_add.add_argument("entity", help="Persona u organización; se cifra localmente")
    conflict_add.add_argument("--role", choices=("client", "adverse", "related"), required=True)
    conflict_add.add_argument("--key-env", default="LEGALFLOW_CONFLICT_KEY")
    conflict_add.add_argument("--matter", type=Path, default=Path.cwd())
    conflict_check = sub.add_parser("conflict-check", help="Check an entity against the encrypted local conflict registry")
    conflict_check.add_argument("entity", help="Persona u organización a revisar")
    conflict_check.add_argument("--key-env", default="LEGALFLOW_CONFLICT_KEY")
    conflict_check.add_argument("--matter", type=Path, default=Path.cwd())
    pack_list = sub.add_parser("pack-list", help="List Legal Packs and whether their review gate is satisfied")
    pack_list.add_argument("--json", action="store_true")
    pack_validate = sub.add_parser("pack-validate", help="Validate a Legal Pack manifest and legal-review evidence")
    pack_validate.add_argument("manifest", type=Path)
    pack_validate.add_argument("--json", action="store_true")
    migrate = sub.add_parser("migrate", help="Check and apply compatible matter schema migrations")
    migrate.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    migrate.add_argument("--json", action="store_true")
    verify = sub.add_parser("verify", help="Verify matter structure and preserved originals")
    verify.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    recover = sub.add_parser("recover", help="Verify and rebuild safe local matter views after recovery")
    recover.add_argument("matter", type=Path, nargs="?", default=Path.cwd())
    recover.add_argument("--repository", help="Optional GitHub owner/repository to clone after private visibility is proved")
    recover.add_argument("--destination", type=Path, help="New local folder for a verified private clone")
    recover.add_argument("--confirm", action="store_true", help="Confirm that the approved private repository may be cloned to this Mac")
    recover.add_argument("--json", action="store_true")
    sub.add_parser("update", help="Show safe update instructions")
    args = parser.parse_args(argv)
    if args.command in {"setup", "doctor"}:
        return _show_checks(args.json)
    if args.command == "onboard":
        content = "demo" if args.demo or not args.matter else args.matter
        plan = _onboarding_plan(args.workspace, content)
        checks = [result.as_dict() for result in run_checks()]
        payload = {"workspace": str(args.workspace), "local_only": True, "content": content, "plan": plan, "checks": checks, "confirmed": args.confirm}
        if not args.confirm:
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print("PLAN DE INICIO (no se creó ni modificó nada)")
                print(*[f"{item}" for item in plan], sep="\n")
                print("\nCuando estés listo, aprueba este plan con:")
                print(f"  legalflow onboard --confirm --workspace \"{args.workspace}\" {'--demo' if content == 'demo' else f'--matter \"{content}\"'}")
                print("El inicio es local: no se conectará GitHub ni se pedirá ninguna contraseña, token o código.")
                _credit()
            return 0
        if content == "demo":
            exit_code = _run_demo(args.workspace, "Demo", emit=not args.json)
        else:
            args.workspace.mkdir(parents=True, exist_ok=True)
            root = create_matter(args.workspace, content)
            initialize(root)
            if not args.json:
                print(f"Asunto local creado: {root}")
                print("Guarda los documentos originales en este asunto. Cada punto seguro y regla queda dentro de su propia carpeta.")
            exit_code = 0
        if args.json:
            payload.update({"completed": exit_code == 0})
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        elif exit_code == 0:
            print("Tu inicio quedó en modo local. GitHub sólo se ofrece después, cuando tú decidas compartir.")
            _credit()
        return exit_code
    if args.command == "create-matter":
        args.workspace.mkdir(parents=True, exist_ok=True)
        root = create_matter(args.workspace, args.name)
        initialize(root)
        print(f"Matter created locally: {root}")
        _credit()
        return 0
    if args.command == "demo":
        exit_code = _run_demo(args.workspace, args.name)
        if exit_code:
            return exit_code
        _credit()
        return 0
    if args.command == "init":
        initialize(args.matter)
        print(f"Matter ledger initialized: {args.matter}")
        _credit()
        return 0
    if args.command == "ingest":
        # A manually created matter may not have its ledger yet. Create the
        # baseline before touching evidence so the import gets its own event.
        if not (args.matter / ".git").exists():
            initialize(args.matter)
        record = ingest_document(args.matter, args.source)
        commit = commit_semantic(args.matter, "evidence", f"Preserve {record['document']['id']}")
        outcome = "Documento ya preservado" if record["duplicate"] else "Documento preservado"
        message = f"{outcome}: {record['document']['id']}; extracción: {record['extraction']['id']}"
        if commit:
            message += f"; registro local: {commit[:12]}"
        print(message)
        _credit()
        return 0
    if args.command == "record-claim":
        from .objects import write_object
        record = write_object(args.matter, "claim", {"statement": args.statement, "status": "reported", "support": []})
        print(f"Posición registrada para revisión: {record['id']}. Aún no es un hecho confirmado.")
        _credit()
        return 0
    if args.command == "record-fact":
        from .objects import write_object
        payload = {"statement": args.statement, "status": args.status, "support": [args.document]}
        if args.claim:
            payload["claim"] = args.claim
        record = write_object(args.matter, "fact", payload)
        print(f"Hecho registrado: {record['id']}. Revisa siempre el documento de respaldo antes de usarlo.")
        _credit()
        return 0
    if args.command == "record-act":
        from .objects import write_object
        record = write_object(args.matter, "act", {"type": args.type, "date": {"value": args.date, "confidence": "documented"}, "status": "DOCUMENTED", "support": [args.document]})
        print(f"Evento registrado: {record['id']}")
        _credit()
        return 0
    if args.command == "record-deadline":
        from .objects import write_object
        record = write_object(args.matter, "deadline", {"trigger": {"act": args.document, "verified": False}, "status": "DEADLINE_CANDIDATE", "support": [args.document], "candidate_date": None})
        print(f"Plazo candidato registrado: {record['id']}. Confirma documento y regla antes de usar una fecha.")
        _credit()
        return 0
    if args.command == "calculate-deadline":
        try:
            record = propose_calendar_deadline(args.matter, args.document, args.authority, args.start, args.days, args.rule)
        except ValueError as error:
            print(f"PLAZO BLOQUEADO: {error}", file=sys.stderr)
            return 22
        print(f"Plazo candidato calculado: {record['candidate_date']}. No considera inhábiles ni suspensión; confírmalo antes de usarlo.")
        _credit()
        return 0
    if args.command == "confirm-deadline":
        from .objects import load_objects, write_object
        objects = load_objects(args.matter)
        candidate = next((item for item in objects["deadline"] if item["id"] == args.deadline), None)
        authority = next((item for item in objects["authority"] if item["id"] == args.authority), None)
        if candidate is None or authority is None:
            print("PLAZO BLOQUEADO: falta el plazo candidato o la fuente fijada.", file=sys.stderr)
            return 22
        if authority.get("verification", {}).get("status") != "verified_official":
            print("PLAZO BLOQUEADO: la fuente debe estar verificada como oficial.", file=sys.stderr)
            return 22
        record = write_object(args.matter, "deadline", {"trigger": {**candidate.get("trigger", {}), "verified": True}, "status": "DEADLINE_VERIFIED", "support": candidate.get("support", []), "candidate_date": args.due, "authority": args.authority, "rule": args.rule, "supersedes": candidate["id"]})
        print(f"Plazo confirmado por revisión humana: {record['id']}. Fecha registrada: {args.due}.")
        _credit()
        return 0
    if args.command == "source-plan":
        from .objects import write_object
        record = write_object(args.matter, "source_plan", {"jurisdiction": "MX", "required": [{"source": source, "status": "MISSING"} for source in ("constitution", "substantive_code", "procedural_code", "jurisprudence")]})
        print(f"Plan de fuentes creado: {record['id']}. Consulta sólo fuentes oficiales antes de afirmar vigencia.")
        _credit()
        return 0
    if args.command == "source-resolve":
        try:
            record = lock_source(args.matter, args.url, args.title, effective_from=args.effective_from, effective_to=args.effective_to, authority_type=args.authority_type)
        except ValueError as error:
            print(f"FUENTE BLOQUEADA: {error}", file=sys.stderr)
            return 22
        print(f"Fuente fijada: {record['id']}. Estado: {record['verification']['status']}")
        _credit()
        return 0
    if args.command == "source-temporal":
        from .objects import load_objects
        authority = next((item for item in load_objects(args.matter)["authority"] if item["id"] == args.authority), None)
        if authority is None:
            print("Fuente no encontrada.", file=sys.stderr)
            return 21
        result = temporal_status(authority, args.date)
        print(f"{result['status']}: {result['reason']}")
        _credit()
        return 22 if result["status"] == "review_required" else 0
    if args.command == "propose":
        record = propose(args.matter, args.issue, args.position, args.depends_on)
        print(f"Propuesta registrada: {record['id']}")
        _credit()
        return 0
    if args.command == "decide":
        record = accept_solo(args.matter, args.proposal, args.reason)
        print(f"Decisión Solo Counsel registrada: {record['id']}")
        _credit()
        return 0
    if args.command in {"status", "timeline", "dashboard", "snapshot"}:
        state = materialize(args.matter)
        dashboard_path = render_visuals(args.matter, state)["dashboard"] if args.command == "dashboard" else None
        snapshot_path = create_snapshot(args.matter, state, "snapshot") if args.command == "snapshot" else None
        if args.command == "timeline":
            output = state["timeline"]
        else:
            output = state
        if getattr(args, "json", False):
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(f"Estado reconstruido: {state['state_hash']}")
            print(f"Objetos: {state['counts']}")
            if dashboard_path:
                print(f"Vista para revisión: {dashboard_path}")
            if snapshot_path:
                print(f"Fotografía guardada: {snapshot_path}")
            _credit()
        return 0
    if args.command == "visual-verify":
        errors = verify_visuals(args.matter, materialize(args.matter))
        if args.json:
            print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        else:
            print("VISTA VERIFICADA" if not errors else "VISTA BLOQUEADA")
            for error in errors:
                print(f"- {error}")
            _credit()
        return 0 if not errors else 22
    if args.command == "schedule-review":
        from datetime import date
        from .objects import write_object
        try:
            date.fromisoformat(args.date)
        except ValueError:
            print("REVISIÓN BLOQUEADA: usa una fecha con formato YYYY-MM-DD.", file=sys.stderr)
            return 22
        record = write_object(args.matter, "matter_review", {"next_review_on": args.date, "purpose": args.purpose, "status": "scheduled"})
        print(f"Revisión programada: {record['id']} para {args.date}. No es un plazo legal.")
        _credit()
        return 0
    if args.command == "ok":
        errors = verify_matter(args.matter)
        if errors:
            print("OK BLOQUEADO", *[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
            return 22
        state = materialize(args.matter)
        commit = checkpoint(args.matter, args.tag, args.message)
        from .objects import write_object
        checkpoint_record = write_object(args.matter, "checkpoint", {"git_tag": args.tag, "git_commit": commit, "summary": args.message, "state_hash": state["state_hash"]})
        snapshot_path = create_snapshot(args.matter, state, args.tag)
        audit_commit = commit_audit_record(args.matter, f"Record {checkpoint_record['id']} for {args.tag}")
        print(f"Checkpoint creado: {args.tag} ({commit[:12]}) estado {state['state_hash'][:12]}; registro {audit_commit[:12]}; fotografía: {snapshot_path.name}")
        _credit()
        return 0
    if args.command == "compare-checkpoint":
        try:
            result = compare_checkpoint(args.matter, args.tag, materialize(args.matter))
        except ValueError as error:
            print(f"COMPARACIÓN BLOQUEADA: {error}", file=sys.stderr)
            return 22
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"COMPARACIÓN CON {result['checkpoint']}")
            print("Hay cambios desde el punto seguro." if result["changed"] else "No hay cambios desde el punto seguro.")
            for kind, change in result["count_changes"].items():
                print(f"- {kind}: {change['before']} → {change['now']}")
            print(result["instruction"])
            _credit()
        return 0
    if args.command == "sync-private":
        if not args.confirm:
            print("SYNC BLOQUEADO: usa --confirm sólo después de autorizar que este asunto se sincronice a un repositorio privado.", file=sys.stderr)
            print("Guía: https://hassanvfx.github.io/legalflow-mx/setup/github-auth.html", file=sys.stderr)
            return 22
        errors = verify_matter(args.matter)
        if errors:
            print("SYNC BLOQUEADO: el asunto no superó verify.", *[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
            return 22
        try:
            result = sync_private(args.matter, args.repository, args.create_private)
        except PrivateRemoteError as error:
            print(f"SYNC BLOQUEADO: {error}", file=sys.stderr)
            print("Alternativa segura: continúa en local-only. Guía: https://hassanvfx.github.io/legalflow-mx/setup/github-auth.html", file=sys.stderr)
            return 22
        direction = {"equal": "sin cambios", "local-ahead": "cambios locales enviados", "remote-ahead": "contribuciones no materiales integradas"}[result["direction"]]
        print(f"Sincronización privada comprobada: {result['url']} ({direction}).")
        _credit()
        return 0
    if args.command in {"invite", "join", "contribute", "disagree", "accept-proposal", "resolve-disagreement", "revoke"}:
        try:
            if args.command == "invite":
                record = invite(args.matter, args.handle, args.role)
            elif args.command == "join":
                record = join(args.matter, args.actor)
            elif args.command == "contribute":
                record = contribute(args.matter, args.actor, args.summary)
            elif args.command == "disagree":
                record = disagree(args.matter, args.actor, args.proposal, args.reason)
            elif args.command == "accept-proposal":
                record = accept_proposal(args.matter, args.actor, args.proposal, args.reason)
            elif args.command == "resolve-disagreement":
                record = resolve_disagreement(args.matter, args.actor, args.disagreement, args.reason)
            else:
                record = revoke(args.matter, args.owner, args.actor, args.reason)
        except (ValueError, PermissionError) as error:
            print(f"COLABORACIÓN BLOQUEADA: {error}", file=sys.stderr)
            return 22
        print(f"Registro de colaboración creado: {record['id']}. No cambia el estado aceptado sin una decisión válida.")
        _credit()
        return 0
    if args.command == "review-bundle":
        try:
            path = review_bundle(args.matter, args.include)
        except ValueError as error:
            print(f"BUNDLE BLOQUEADO: {error}", file=sys.stderr)
            return 22
        print(f"Bundle de revisión creado: {path}. No contiene originales ni journals.")
        _credit()
        return 0
    if args.command == "reviewer-access":
        try:
            result = reviewer_access(args.repository, args.handle, "revoke" if args.revoke else "grant", args.confirm)
        except PrivateRemoteError as error:
            print(f"ACCESO BLOQUEADO: {error}", file=sys.stderr)
            return 22
        if result["mode"] == "bundle-first":
            print("ACCESO REMOTO NO CAMBIADO: un repositorio personal no ofrece un control verificable de sólo lectura. Usa review-bundle o una GitHub Organization privada.")
            _credit()
            return 0
        from .objects import write_object
        record = write_object(args.matter, "access_grant", {"action": result["action"], "repository": result["repository"], "handle": result["handle"], "permission": "read", "visibility": result["visibility"], "mode": result["mode"]})
        action = "revocado" if result["action"] == "revoke" else "otorgado"
        print(f"Acceso de sólo lectura {action}: {record['id']}. Revisa el resultado en GitHub antes de compartir evidencia adicional.")
        _credit()
        return 0
    if args.command in {"legal-hold", "release-legal-hold"}:
        try:
            record = place_legal_hold(args.matter, args.reason) if args.command == "legal-hold" else release_legal_hold(args.matter, args.hold, args.reason)
        except ValueError as error:
            print(f"LEGAL HOLD BLOQUEADO: {error}", file=sys.stderr)
            return 22
        print(f"Registro de legal hold creado: {record['id']}. No se automatiza ninguna eliminación.")
        _credit()
        return 0
    if args.command == "security-audit":
        report = security_audit(args.matter)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("AUDITORÍA DE SEGURIDAD")
            for message in report["errors"] or ["Sin incumplimientos detectados."]:
                print(f"- {message}")
            for message in report["warnings"]:
                print(f"- Atención: {message}")
            _credit()
        return 22 if report["errors"] else 0
    if args.command == "redact":
        try:
            result = redact_document(args.matter, args.document, args.replace)
        except ValueError as error:
            print(f"REDACCIÓN BLOQUEADA: {error}", file=sys.stderr)
            return 22
        print(f"Copia derivada creada: {result['path']}. Revisa la copia antes de compartirla; el original no cambió.")
        _credit()
        return 0
    if args.command in {"conflict-add", "conflict-check"}:
        try:
            if args.command == "conflict-add":
                result = add_conflict_entity(args.matter, args.entity, args.role, args.key_env)
                message = "Entidad añadida al registro local cifrado." if result["stored"] else "La entidad ya estaba en el registro local cifrado."
            else:
                result = check_conflict_entity(args.matter, args.entity, args.key_env)
                message = "POSIBLE CONFLICTO: revisa antes de continuar." if result["match"] else "Sin coincidencia local. Esto no sustituye una revisión de conflicto profesional."
        except ValueError as error:
            print(f"CONFLICTO BLOQUEADO: {error}", file=sys.stderr)
            return 22
        print(message)
        _credit()
        return 0
    if args.command == "pack-list":
        packs = list_packs()
        if args.json:
            print(json.dumps({"packs": packs}, ensure_ascii=False, indent=2))
        else:
            for pack in packs or [{"id": "ninguno", "released": False}]:
                label = "LISTO PARA RELEASE" if pack["released"] else "NO LIBERADO"
                print(f"[{label}] {pack['id']}")
            _credit()
        return 0
    if args.command == "pack-validate":
        errors = validate_pack(args.manifest)
        if args.json:
            print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        else:
            print("PACK VALIDADO" if not errors else "PACK BLOQUEADO")
            for error in errors:
                print(f"- {error}")
            _credit()
        return 0 if not errors else 22
    if args.command == "migrate":
        messages = migrate_matter(args.matter)
        print(json.dumps({"messages": messages}, ensure_ascii=False) if args.json else "\n".join(messages))
        if not args.json:
            _credit()
        return 0
    if args.command == "verify":
        errors = verify_matter(args.matter)
        if errors:
            print("VERIFY FAILED", *[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
            return 1
        print("VERIFY PASSED: canonical structure and originals are intact.")
        _credit()
        return 0
    if args.command == "recover":
        if args.repository:
            if not args.confirm or args.destination is None:
                message = "RECUPERACIÓN BLOQUEADA: para clonar debes usar --repository, una --destination nueva y --confirm."
                if args.json:
                    print(json.dumps({"recovered": False, "errors": [message], "guide": "https://hassanvfx.github.io/legalflow-mx/setup/recovery.html"}, ensure_ascii=False, indent=2))
                else:
                    print(message, file=sys.stderr)
                return 22
            try:
                clone_verified_private(args.repository, args.destination)
            except PrivateRemoteError as error:
                message = f"RECUPERACIÓN BLOQUEADA: {error}"
                if args.json:
                    print(json.dumps({"recovered": False, "errors": [message], "guide": "https://hassanvfx.github.io/legalflow-mx/setup/recovery.html"}, ensure_ascii=False, indent=2))
                else:
                    print(message, file=sys.stderr)
                return 22
            args.matter = args.destination
        # Recovery deliberately rebuilds only discardable outputs from canonical
        # records.  It never copies, deletes, edits, resets, or pushes evidence.
        errors = verify_matter(args.matter)
        if errors:
            payload = {
                "recovered": False,
                "errors": errors,
                "next_step": "Keep originals intact; resolve verification errors before rebuilding views.",
                "guide": "https://hassanvfx.github.io/legalflow-mx/setup/recovery.html",
            }
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print("RECUPERACIÓN BLOQUEADA: no se modificó ningún original.")
                for error in errors:
                    print(f"- {error}")
                print(f"Guía: {payload['guide']}")
                _credit()
            return 22
        state = materialize(args.matter)
        views = render_visuals(args.matter, state)
        recovered_snapshot = create_snapshot(args.matter, state, "recovered")
        payload = {
            "recovered": True,
            "matter": str(args.matter),
            "state_hash": state["state_hash"],
            "dashboard": str(views["dashboard"]),
            "client_summary": str(views["client_summary"]),
            "snapshot": str(recovered_snapshot),
            "guide": "https://hassanvfx.github.io/legalflow-mx/setup/recovery.html",
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("RECUPERACIÓN COMPLETA: se verificaron originales y se reconstruyeron vistas locales.")
            print(f"Estado reconstruido: {state['state_hash']}")
            print(f"Vista para revisión: {views['dashboard']}")
            print(f"Fotografía de recuperación: {recovered_snapshot}")
            _credit()
        return 0
    print("Updates must use a verified release. Consult https://hassanvfx.github.io/legalflow-mx/setup/update.html")
    _credit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
