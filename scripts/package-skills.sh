#!/usr/bin/env bash
# Baut pro Skill eine ZIP-Datei in dist/ zum Hochladen in claude.ai (Customize > Skills).
# Der Skill-Ordner liegt jeweils als oberster Eintrag im ZIP, so wie claude.ai es erwartet.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist="$repo_root/dist"

rm -rf "$dist"
mkdir -p "$dist"
for skill in "$repo_root"/plugins/*/skills/*/; do
  name="$(basename "$skill")"
  (cd "$(dirname "$skill")" && zip -qrX "$dist/$name.zip" "$name")
  echo "  + dist/$name.zip"
done
