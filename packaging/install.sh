#!/usr/bin/env bash
set -euo pipefail

REPO="hassanvfx/legalflow-mx"
VERSION="${LEGALFLOW_VERSION:-0.1.0}"
ROOT="${LEGALFLOW_HOME:-$HOME/.legalflow/releases/$VERSION}"

info() { printf '\n[AI LegalFlow MX] %s\n' "$1"; }
fail() { printf '[AI LegalFlow MX] ERROR: %s\n' "$1" >&2; exit 1; }

info "Hassan Uriostegui y Aurora Cotne"
command -v python3 >/dev/null 2>&1 || fail "Python 3 is needed for this bootstrap. See https://hassanvfx.github.io/legalflow-mx/setup/python.html"
if [ ! -d "$ROOT" ]; then
  info "Downloading verified product release $VERSION"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  archive="$tmp/legalflow-mx.tar.gz"
  checksum="$tmp/legalflow-mx.sha256"
  base="https://github.com/$REPO/releases/download/v$VERSION"
  curl -fsSL "$base/legalflow-mx-$VERSION.tar.gz" -o "$archive" || fail "Release download failed. See https://hassanvfx.github.io/legalflow-mx/setup/network.html"
  curl -fsSL "$base/legalflow-mx-$VERSION.sha256" -o "$checksum" || fail "Release checksum download failed."
  (cd "$tmp" && shasum -a 256 -c "$checksum") || fail "Checksum verification failed; nothing was installed."
  mkdir -p "$ROOT"
  tar -xzf "$archive" -C "$ROOT" --strip-components=1
fi
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m legalflow.cli setup "$@"
