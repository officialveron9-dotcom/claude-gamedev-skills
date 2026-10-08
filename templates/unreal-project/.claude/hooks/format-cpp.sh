#!/usr/bin/env bash
# PostToolUse-Hook (Matcher "Edit|Write"): formatiert die gerade geaenderte .cpp/.h mit clang-format.
# Laeuft nur, wenn im Projekt eine .clang-format liegt UND clang-format installiert ist; sonst passiert nichts.
# Input: Hook-JSON auf stdin (.tool_input.file_path). Braucht bash (Windows: Git Bash) und jq oder Python.
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
  *.cpp|*.h|*.hpp|*.inl) ;;
  *) exit 0 ;;
esac
[ -f "${CLAUDE_PROJECT_DIR:-.}/.clang-format" ] || exit 0
command -v clang-format >/dev/null 2>&1 || exit 0
clang-format -i --style=file "$f"
