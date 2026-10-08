#!/usr/bin/env bash
# PostToolUse-Hook (Matcher "Edit|Write"): luacheck auf die gerade geaenderte .lua-Datei.
# Meldet luacheck etwas, geht die Ausgabe ueber Exit-Code 2 + stderr an Claude zurueck (dokumentiertes
# Verhalten fuer PostToolUse: nicht blockierend, aber Claude sieht die Meldung und kann reagieren).
# Fehlt luacheck, passiert nichts. Braucht bash (Windows: Git Bash) und jq oder Python.
set -u
if command -v jq >/dev/null 2>&1; then
  f=$(jq -r '.tool_input.file_path // empty')
elif command -v python3 >/dev/null 2>&1; then
  f=$(python3 -c "import sys,json;print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")
elif command -v python >/dev/null 2>&1; then
  f=$(python -c "import sys,json;print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")
else
  exit 0
fi
[ -n "$f" ] || exit 0
case "$f" in
  *.lua) ;;
  *) exit 0 ;;
esac
command -v luacheck >/dev/null 2>&1 || exit 0
# Windows liefert Backslash-Pfade: erst normalisieren, dann ins Projekt wechseln und den Pfad relativ machen,
# damit die files[...]-Muster der .luacheckrc greifen.
root="${CLAUDE_PROJECT_DIR:-$PWD}"
root="${root//\\//}"
f="${f//\\//}"
cd "$root" 2>/dev/null || exit 0
f="${f#"$root"/}"
[ -f "$f" ] || exit 0
out=$(luacheck --no-color --codes "$f" 2>&1)
rc=$?
if [ "$rc" -ne 0 ]; then
  printf 'luacheck (%s):\n%s\n' "$f" "$out" >&2
  exit 2
fi
exit 0
