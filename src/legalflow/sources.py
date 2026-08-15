"""Official-first sources, locks, and conservative temporal evaluation."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from .objects import write_object

OFFICIAL_SUFFIXES = ("dof.gob.mx", "scjn.gob.mx", "diputados.gob.mx", "gob.mx", "poderjudicialcdmx.gob.mx")


def is_official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_SUFFIXES)


def lock_source(matter: Path, url: str, title: str, content: bytes | None = None, cache_root: Path | None = None, effective_from: str | None = None, effective_to: str | None = None, authority_type: str = "unknown") -> dict:
    if not url.startswith("https://"):
        raise ValueError("Las fuentes remotas deben usar HTTPS")
    for value in (effective_from, effective_to):
        if value:
            date.fromisoformat(value)
    if effective_from and effective_to and effective_to < effective_from:
        raise ValueError("El fin de vigencia no puede ser anterior al inicio")
    if content is None:
        with urlopen(url, timeout=15) as response:  # nosec B310: explicit user command; HTTPS required
            content = response.read(10_000_000)
    digest = hashlib.sha256(content).hexdigest()
    root = cache_root or Path(os.environ.get("LEGALFLOW_SOURCE_CACHE", str(Path.home() / ".legalflow" / "source-cache")))
    cache = root / "sha256" / digest[:2] / digest[2:]
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        cache.write_bytes(content)
    authority = write_object(matter, "authority", {
        "title": title, "authority_type": authority_type, "source": {"url": url, "publisher": urlparse(url).hostname},
        "official_status": "official" if is_official(url) else "unverified", "retrieved_at": datetime.now(UTC).isoformat(),
        "sha256": digest, "verification": {"status": "verified_official" if is_official(url) else "review_required"},
        "temporal": {"effective_from": effective_from, "effective_to": effective_to, "recorded_by": "human_review" if effective_from else "unknown"},
    })
    locks = matter / ".legalflow" / "source-lock.json"
    current = json.loads(locks.read_text(encoding="utf-8")) if locks.exists() else {}
    current[authority["id"]] = {"url": url, "sha256": digest, "retrieved_at": authority["retrieved_at"], "official": is_official(url)}
    locks.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return authority


def temporal_status(authority: dict, relevant_date: str | None) -> dict[str, str]:
    temporal = authority.get("temporal", {})
    if authority.get("verification", {}).get("status") != "verified_official":
        return {"status": "review_required", "reason": "La fuente no está verificada como oficial."}
    if not relevant_date or not temporal.get("effective_from"):
        return {"status": "review_required", "reason": "Falta fecha relevante o inicio de vigencia verificable."}
    if relevant_date < temporal["effective_from"]:
        return {"status": "not_effective", "reason": "La fecha es anterior a la vigencia registrada."}
    if temporal.get("effective_to") and relevant_date > temporal["effective_to"]:
        return {"status": "superseded", "reason": "La fecha es posterior al fin de vigencia registrado."}
    return {"status": "candidate_applicable", "reason": "Coincide con el intervalo registrado; requiere revisión jurídica."}
