#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="${1:-$(sed -n 's/^version = "\([0-9][^"]*\)"/\1/p' "$root_dir/pyproject.toml")}"
out="$root_dir/output/release"
stage="$out/legalflow-mx-$version"
archive="$out/legalflow-mx-$version.tar.gz"

[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Release version must be semantic (x.y.z)." >&2; exit 2; }
[[ "$(sed -n 's/^version = "\([0-9][^"]*\)"/\1/p' "$root_dir/pyproject.toml")" == "$version" ]] || { echo "Release version differs from pyproject.toml." >&2; exit 2; }

rm -rf "$stage"
mkdir -p "$stage" "$out"
for path in src templates plugin docs packaging schemas fixtures legal-packs pyproject.toml README.md VERSION; do
  cp -R "$root_dir/$path" "$stage/"
done
tar -C "$out" -czf "$archive" "legalflow-mx-$version"
(cd "$out" && shasum -a 256 "$(basename "$archive")" > "legalflow-mx-$version.sha256")
for required in "legalflow-mx-$version/src/legalflow/cli.py" "legalflow-mx-$version/templates/matter/matter.yaml" "legalflow-mx-$version/packaging/install.ps1"; do
  tar -tzf "$archive" | grep -Fx "$required" >/dev/null || { echo "Release is missing $required" >&2; exit 1; }
done
echo "Wrote $archive and checksum"
