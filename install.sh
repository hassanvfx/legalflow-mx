#!/usr/bin/env bash
set -euo pipefail
SCRIPT_URL="https://raw.githubusercontent.com/hassanvfx/legalflow-mx/main/packaging/install.sh"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$SCRIPT_URL" | bash
elif command -v wget >/dev/null 2>&1; then
  wget -qO- "$SCRIPT_URL" | bash
else
  echo "AI LegalFlow MX requires curl or wget. See https://hassanvfx.github.io/legalflow-mx/setup/network.html" >&2
  exit 2
fi
