#!/usr/bin/env bash
# Kopiert die Skills in den .claude/skills-Ordner eines Projekts (oder nach ~/.claude/skills).
# Aufruf:
#   scripts/install-skills.sh <projektordner> [all|<plugin> ...]
#   scripts/install-skills.sh --personal [all|<plugin> ...]
# Plugins: unreal-engine, unreal-engine-reference, fivem, brotato, general-dev, gamedev-general, web-dev (Ordner unter plugins/).
# Gleichnamige Skills im Ziel werden ueberschrieben.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() { sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 1; }

[ $# -ge 1 ] || usage
if [ "$1" = "--personal" ]; then
  target="$HOME/.claude/skills"
else
  [ -d "$1" ] || { echo "Projektordner nicht gefunden: $1" >&2; exit 1; }
  target="$(cd "$1" && pwd)/.claude/skills"
fi

shift
if [ $# -eq 0 ] || [ "$1" = "all" ]; then
  plugins=()
  for dir in "$repo_root"/plugins/*/; do plugins+=("$(basename "$dir")"); done
else
  plugins=("$@")
  for plugin in "${plugins[@]}"; do
    [ -d "$repo_root/plugins/$plugin/skills" ] || { echo "Unbekanntes Plugin: $plugin" >&2; usage; }
  done
fi

mkdir -p "$target"
for plugin in "${plugins[@]}"; do
  for skill in "$repo_root/plugins/$plugin/skills"/*/; do
    name="$(basename "$skill")"
    rm -rf "${target:?}/$name"
    cp -R "$skill" "$target/$name"
    echo "  + $name"
  done
done
echo "Skills installiert nach: $target"
