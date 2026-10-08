#!/usr/bin/env bash
# PostToolUse-Hook (Matcher "Edit|Write"): gdlint + gdformat --check auf die gerade geaenderte .gd-Datei.
# Ein Parse-Fehler ist in Brotato-Mods fast immer Godot-4-Syntax; die Meldung geht ueber Exit-Code 2 + stderr
# an Claude zurueck (nicht blockierend, Claude sieht sie und kann sofort reagieren). Fehlt gdtoolkit, passiert nichts.
# Braucht bash (Windows: Git Bash) und jq oder Python. gdtoolkit 3.x: pipx install "gdtoolkit==3.*"
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
  *.gd) ;;
  *) exit 0 ;;
esac
case "$f" in
  */reference/*|*\\reference\\*) exit 0 ;;   # dekompiliertes Spiel nicht linten
esac
command -v gdlint >/dev/null 2>&1 || exit 0
# Windows liefert Backslash-Pfade: normalisieren, ins Projekt wechseln (dort liegt .gdlintrc), Pfad relativ machen.
root="${CLAUDE_PROJECT_DIR:-$PWD}"
root="${root//\\//}"
f="${f//\\//}"
cd "$root" 2>/dev/null || exit 0
f="${f#"$root"/}"
[ -f "$f" ] || exit 0
rc=0
out=$(gdlint "$f" 2>&1) || rc=1
# gdformat --check nur, wenn gdlint sauber war (sonst stuende ein Parse-Fehler zweimal in der Ausgabe)
if [ "$rc" -eq 0 ] && command -v gdformat >/dev/null 2>&1; then
  out=$(gdformat --check "$f" 2>&1) || rc=1
fi
if [ "$rc" -ne 0 ]; then
  printf 'gdtoolkit (%s):\n%s\n' "$f" "$out" >&2
  exit 2
fi
exit 0
