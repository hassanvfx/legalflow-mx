"""Safe evidence ingestion: preserve first, treat document text as untrusted."""
from __future__ import annotations

import mimetypes
import re
import hashlib
from pathlib import Path
from typing import Any

from .matter import preserve_original
from .objects import write_object

MAX_BYTES = 50 * 1024 * 1024
INJECTION = re.compile(r"(?i)(ignore (?:all |previous )?instructions|system prompt|you are chatgpt|execute this command)")


def _extract(source: Path) -> tuple[str, str]:
    if source.suffix.lower() in {".txt", ".md", ".csv"}:
        return source.read_text(encoding="utf-8", errors="replace")[:200_000], "text"
    if source.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader  # optional dependency
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(source)).pages)[:200_000], "pdf"
        except Exception:
            return "", "pdf-unavailable"
    return "", "unsupported"


def ingest(matter: Path, source: Path) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.stat().st_size > MAX_BYTES:
        quarantine = matter / "quarantine" / source.name
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        quarantine.write_bytes(source.read_bytes())
        raise ValueError("Document exceeds 50 MiB and was placed in quarantine")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    duplicate = (matter / "objects" / "documents" / f"DOC-{digest[:20].upper()}.json").is_file()
    document = preserve_original(matter, source)
    text, method = _extract(source)
    extraction = write_object(matter, "extraction", {
        "document": document["id"], "method": method,
        "text": text, "confidence": "low" if not text else "unreviewed",
        "untrusted_instructions_detected": bool(INJECTION.search(text)),
        "mime_type": mimetypes.guess_type(source.name)[0] or "application/octet-stream",
    })
    return {"document": document, "extraction": extraction, "duplicate": duplicate}
