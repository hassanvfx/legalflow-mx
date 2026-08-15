# AI LegalFlow MX

AI LegalFlow MX is a Codex-first, file-backed workflow for Mexican legal matters.
This repository is the product source: it ships the CLI, Codex plugin, matter
template, setup guidance, GitHub Pages source, and printable reference guide.

## Empieza en tres pasos en Windows

1. Descarga [ChatGPT para Windows](https://chatgpt.com/download).
2. Abre Codex en ChatGPT.
3. Pega esta instrucción en una conversación nueva:

```text
Quiero instalar AI LegalFlow MX en esta computadora Windows.

Guíame paso a paso. Revisa primero mi equipo. Después instala AI LegalFlow MX
con el método oficial, crea mi carpeta de asuntos en %USERPROFILE%\Legal-IA y
ayúdame a ejecutar una demostración o crear mi primer asunto.

No me pidas ni guardes contraseñas, tokens, códigos de verificación ni
información de clientes. Antes de descargar, instalar, crear carpetas o
configurar nube, explícame qué harás y pide mi aprobación.
```

En macOS sigue la misma secuencia y usa `~/Legal-IA`. Si algo falta, deja que Codex te guíe.

Prefieres instalar desde Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/hassanvfx/legalflow-mx/main/install.sh | bash
```

The installer is safe to run again. It reports missing requirements in plain
language, links to the matching GitHub Pages guide, and always keeps a
`local-only` path available.

## Development

```bash
python3 -m pip install -e .
PYTHONPATH=src python3 -m unittest discover -s tests
legalflow setup --diagnose --json
```

Generated website and book artifacts are intentionally excluded from Git.

---

AI LegalFlow MX is created by **Hassan Uriostegui** and **Aurora Cotne**.

The public brand is AI LegalFlow MX. The `legalflow` command, package name,
repository slug, and public documentation URLs remain compatibility interfaces.
