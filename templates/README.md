# Vorlagen für die Spielprojekte (`CLAUDE.md`, Hooks, Linter-Configs)

Stand: **2026-10-08**, geprüft gegen die Claude-Code-Doku (code.claude.com/docs: `memory`, `settings`,
`permissions`, `hooks`, `hooks-guide`, `mcp`, `plugins/code-intelligence`, `cloud-environments`) und die
Quell-Repos der Werkzeuge (siehe `docs/tools-und-sdks.md`). Alles, was nicht belegt ist, steht in den Dateien
als `TODO prüfen`.

Die Vorlagen ergänzen die Skills: Skills sagen Claude, *wie* man in UE5, FiveM und Brotato richtig arbeitet;
die `CLAUDE.md` sagt Claude, *was dein Projekt ist* (Engine-Version, Build-Befehle, Pfade, Regeln), und die
Hooks lassen Linter nach jedem Edit automatisch laufen.

## Was in welchem Ordner liegt

| Datei | Zweck |
|---|---|
| `CLAUDE.md` | Projektgedächtnis: wird in jeder Session geladen (lokal und Cloud). Deutsch mit englischen Befehlen. Platzhalter `<...>` ersetzen, Unzutreffendes löschen, unter ~200 Zeilen halten. Rechnerabhängiges in `CLAUDE.local.md` (wird genauso geladen, steht in `.gitignore`). |
| `.claude/settings.json` | Geteilte Projekteinstellungen: `permissions.allow/ask/deny` (was Claude ohne Nachfrage darf, was es nie lesen soll) und `hooks` (automatische Befehle). Wird mit dem Repo committet. Persönliche Abweichungen in `.claude/settings.local.json`. |
| `.claude/hooks/*.sh` | Die Hook-Skripte: `format-cpp.sh` (clang-format), `lint-lua.sh` (luacheck), `lint-gd.sh` (gdlint + gdformat). Lesen den Hook-Input (JSON mit `tool_input.file_path`) von stdin, prüfen nur die eine geänderte Datei und beenden sich still, wenn das Werkzeug fehlt. |
| `.mcp.json` (nur Unreal) | Projektweite MCP-Server: `unreal-api` (API-Datenbank über `uvx unreal-api-mcp`, läuft ohne Editor) und `unreal-mcp` (Epics Editor-MCP auf `http://127.0.0.1:8000/mcp`). Claude Code fragt beim ersten Start einmal, ob die Server erlaubt sind. |
| `.luarc.json`, `.luacheckrc` (FiveM) | LuaLS mit `fivem-lls-addon` (Typen für Natives und Runtime) und luacheck mit Cfx-Globals. |
| `.gdlintrc`, `.editorconfig`, `tools/build_zip.py` (Brotato) | gdlint-Regeln für Godot 3, Tabs für `.gd`, Zip-Builder mit korrektem `mods-unpacked/`-Root. |
| `.gitignore`, `secrets.cfg.example`, `.clang-format.example` | Nie-committen-Listen, Vorlage für Secrets, optionaler clang-format-Stil (erst nach Umbenennen aktiv). |

## Kopieren

`scripts/install-skills.ps1` kopiert nur die **Skills** nach `.claude/skills/`. Die Vorlagen kopierst du von Hand,
weil du sie danach anpasst (Platzhalter, Pfade). Versteckte Dateien (`.claude`, `.gitignore`, `.luarc.json`) nicht vergessen.

```powershell
# Windows PowerShell, im Ordner dieses Repos
Copy-Item -Recurse -Force .\templates\unreal-project\* C:\Dev\MeinSpiel\
Copy-Item -Recurse -Force .\templates\unreal-project\.* C:\Dev\MeinSpiel\ -Exclude .,..
Copy-Item -Recurse -Force .\templates\fivem-server\*  C:\FXServer\server-data\
Copy-Item -Recurse -Force .\templates\fivem-server\.* C:\FXServer\server-data\ -Exclude .,..
Copy-Item -Recurse -Force .\templates\brotato-mod\*   C:\Dev\MeineBrotatoMod\
Copy-Item -Recurse -Force .\templates\brotato-mod\.*  C:\Dev\MeineBrotatoMod\ -Exclude .,..
```

```bash
# Linux / macOS / Git Bash (cp -r mit Punkt-Dateien)
cp -r templates/unreal-project/. ~/MeinSpiel/
cp -r templates/fivem-server/.   ~/server-data/
cp -r templates/brotato-mod/.    ~/MeineBrotatoMod/
```

Danach:
1. `CLAUDE.md` öffnen, alle `<...>` ersetzen, Abschnitte streichen, die nicht zutreffen.
2. Pfade in `.claude/settings.json` (Unreal: Engine-Pfad in den `Read(//c/...)`-Regeln) und `.luarc.json` anpassen.
3. Skills dazu: `.\scripts\install-skills.ps1 -Project <Ordner> -Plugin ...` (siehe Haupt-README).
4. Claude Code im Projektordner starten, dem Ordner vertrauen (erst dann gelten `permissions.allow`, `env` und Marketplaces aus der Datei; `deny`/`ask` und Hooks gelten nach dem Vertrauen ebenfalls), `.mcp.json`-Server einmal bestätigen.

## Regel für Hooks: Sie laufen auf deinem Rechner

Ein Hook ist ein Shell-Befehl, den Claude Code **auf dem Rechner der Session** ausführt. Alles, was der Befehl
braucht, muss dort installiert sein, sonst passiert nichts (die Skripte prüfen das und beenden sich still) oder
Claude Code zeigt `hook error`:

| Projekt | Lokal nötig (Windows) |
|---|---|
| alle | **Git for Windows** (Git Bash: Claude Code führt `command`-Hooks unter Windows mit bash aus, wenn Git Bash installiert ist, sonst mit PowerShell), **jq** (`winget install jqlang.jq`; Fallback in den Skripten: Python) |
| Unreal | `clang-format` aus LLVM (`winget install LLVM.LLVM`, bringt auch `clangd` für das Plugin `clangd-lsp`), plus eine `.clang-format` im Projekt |
| FiveM | `luacheck` (Windows-Binary von den GitHub-Releases oder `luarocks install luacheck`), `lua-language-server` (`winget install -e --id LuaLS.lua-language-server`) für das Plugin `lua-lsp` |
| Brotato | Python 3 + `pipx install "gdtoolkit==3.*"`; bei Python ≥ 3.12 zusätzlich `pipx inject gdtoolkit "setuptools<80"` (sonst `ModuleNotFoundError: No module named 'pkg_resources'`, hier nachgestellt) |

- **Cloud-Sessions (claude.ai/code):** Hooks, `permissions` und `.mcp.json` aus dem Repo laufen dort auch, aber nur in Sessions mit **einem** Repo. Die VM (Ubuntu 24.04) hat `jq`, Python, `uv`, Clang und `clang-format`; `luacheck` und `gdtoolkit` fehlen und müssten über einen SessionStart-Hook oder das Setup-Script der Cloud-Umgebung installiert werden (`apt-get install lua-check`, `pip install "gdtoolkit==3.*" "setuptools<80"`). Ohne sie sind die Hooks dort wirkungslos, nicht kaputt. Plugins (`lua-lsp`, `clangd-lsp`, Epics UE-Plugin) laden in der Cloud nie.
- Ein Hook lässt sich ohne Claude testen: `echo '{"tool_input":{"file_path":"resources/[core]/x/client/main.lua"}}' | bash .claude/hooks/lint-lua.sh; echo $?` (Exit 2 = Befund auf stderr, 0 = sauber oder Werkzeug fehlt).
- Unter Windows liefert Claude Code `file_path` mit Backslashes; die Skripte normalisieren das. Pfade mit Leerzeichen sind in Ordnung.
- Hooks aus `.claude/settings.json` übernimmt Claude Code bei Änderung sofort (`/hooks` zeigt sie an). Alle abschalten: `"disableAllHooks": true` in `settings.local.json`.
- Der clang-format-Hook ist absichtlich inaktiv, bis du `.clang-format.example` nach `.clang-format` umbenennst: Auf bestehendem Code erzeugt der erste Lauf einen großen Diff, den du bewusst in einem eigenen Commit machen solltest.

## Was `TODO prüfen` bedeutet

An diesen Stellen gab es keine Primärquelle oder keinen Test in UE 5.8 / auf Windows: der `GenerateClangDatabase`-Befehl
(Community-Threads zu UE 5.2–5.4), der UAT-Logpfad, der Dateiname des LuaLS-`--check`-Reports, das
`113/[A-Z]...`-Ignore-Muster in `.luacheckrc` unter Windows-Pfaden, die `Read(//c/Program Files/...)`-Regeln mit Leerzeichen im Pfad (Syntax laut Doku, nicht unter Windows getestet), der clang-format-Beispielstil. Wenn etwas bei dir
funktioniert oder nicht, sag es Claude in einer Session mit diesem Repo, dann wird die Vorlage korrigiert.
