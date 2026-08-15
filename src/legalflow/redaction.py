"""Create explicit, derived text redactions without altering evidence."""
from __future__ import annotations

import hashlib
from pathlib import Path

from .objects import load_objects, write_object


def redact_document(matter: Path, document_id: str, terms: list[str]) -> dict:
    """Replace only exact terms supplied by a human reviewer in extracted text."""
    cleaned = [term for term in terms if len(term.strip()) >= 3]
    if not cleaned or len(cleaned) != len(terms):
        raise ValueError("Cada término de redacción debe tener al menos 3 caracteres")
    objects = load_objects(matter)
    if document_id not in {item["id"] for item in objects["document"]}:
        raise ValueError("Documento preservado no encontrado")
    extraction = next((item for item in reversed(objects["extraction"]) if item.get("document") == document_id and item.get("text")), None)
    if extraction is None:
        raise ValueError("No hay texto extraído para este documento; no se puede redactar automáticamente")
    original = extraction["text"]
    derived = original
    count = 0
    for term in cleaned:
        occurrences = derived.count(term)
        if not occurrences:
            raise ValueError("Un término indicado no aparece en el texto extraído; revisa la selección")
        derived = derived.replace(term, "[REDACTADO]")
        count += occurrences
    digest = hashlib.sha256(derived.encode("utf-8")).hexdigest()
    target = matter / "outputs" / "redactions" / f"{document_id}-{digest[:12]}.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(derived, encoding="utf-8")
    term_hashes = [hashlib.sha256(term.encode("utf-8")).hexdigest() for term in cleaned]
    record = write_object(matter, "redaction", {
        "document": document_id,
        "extraction": extraction["id"],
        "output_path": str(target.relative_to(matter)),
        "sha256": digest,
        "term_hashes": term_hashes,
        "replacement_count": count,
        "review_required": True,
    })
    return {"record": record, "path": target}
