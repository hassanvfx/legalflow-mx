"""Generate GitHub Pages troubleshooting pages from the shared manifest."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/content/setup-manifest.json"
OUT = ROOT / "docs-site/setup"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in entries:
        steps = "".join(f"<li>{html.escape(step)}</li>" for step in entry["steps"])
        page = f"""<!doctype html><html lang=\"es-MX\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{html.escape(entry['title'])} | AI LegalFlow MX</title><link rel=\"stylesheet\" href=\"../style.css\"></head><body><main><p class=\"eyebrow\">AI LEGALFLOW MX · SETUP</p><h1>{html.escape(entry['title'])}</h1><p>{html.escape(entry['summary'])}</p><h2>Pasos</h2><ol>{steps}</ol><h2>Alternativa segura</h2><p>{html.escape(entry['fallback'])}</p><p><code>legalflow setup --resume</code></p><p><a href=\"../index.html\">Volver a la guía</a></p><footer>AI LegalFlow MX · Hassan Uriostegui y Aurora Cotne</footer></main></body></html>"""
        (OUT / f"{entry['id']}.html").write_text(page, encoding="utf-8")
    # Capability matrices and acceptance evidence are internal engineering
    # material. Never regenerate them into the commercial GitHub Pages site.
    for internal_page in (ROOT / "docs-site/capabilities.html", ROOT / "docs-site/acceptance.html"):
        internal_page.unlink(missing_ok=True)
    print(f"Built {len(entries)} setup pages in {OUT}")


if __name__ == "__main__":
    main()
