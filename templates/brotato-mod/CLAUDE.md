# <Namespace-ModName> – Brotato-Mod (Godot 3, GDScript 3)

Vorlage aus `gamedev-skills/templates/brotato-mod`. Platzhalter `<...>` ersetzen, Unzutreffendes löschen.
Rechnerabhängige Pfade (Steam-Ordner, Workshop-Item-ID, dekompiliertes Projekt) gehören in `CLAUDE.local.md` (gitignored).

## Nicht verhandelbar

- Brotato **1.1.15.x** läuft auf einem eigenen **Godot-3.x**-Build (3.7-dev). Nur **GDScript 3**: `export`, `onready`, `yield`, `connect("sig", self, "_m")`, `.method()` für den Elternaufruf. Kein `@export`, `await`, `super()`, `signal.connect(...)`, kein `Callable`. Vor jedem GDScript den Skill `godot3-gdscript-pitfalls` lesen; ein einziges Godot-4-Token ist ein Parse-Fehler, der die ganze Mod abschaltet.
- Godot Mod Loader **6.x** (6.2.0 oder 6.3.0, Code muss auf beiden laufen). Keine 7.x-APIs (`add_hook`, `install_script_hooks`, `extend_scene`, `refresh_scene`).
- Mod-ID `<Namespace-ModName>` = Ordnername unter `mods-unpacked/` = Konstante `MOD_ID`; `namespace`/`name` nur `[A-Za-z0-9_]`, mindestens 3 Zeichen.
- Script-Extensions nur in `mod_main.gd` `_init()` installieren; Signaturen exakt aus dem dekompilierten Spiel kopieren; `.method()` aufrufen und zurückgeben; nie `._ready()`/`._process()` aus einer Extension aufrufen.
- 1.1.14+: Hash-Keys und `player_index` (`Utils.get_stat(Keys.stat_armor_hash, player_index)`), danach `Utils.reset_stat_cache(player_index)`.
- Spielcode nie committen oder veröffentlichen. Das dekompilierte Projekt liegt in `reference/` (gitignored) und dient nur zum Nachschlagen.

## Layout

```text
mods-unpacked/<Namespace-ModName>/
├── manifest.json              # name, namespace, version_number, extra.godot.* (siehe Skill brotato-modding)
├── mod_main.gd                # _init(): install_script_extension(...); _ready(): Logging, call_deferred-Setup
├── extensions/<pfad wie im Spiel>.gd   # extends "res://..." (Pfad spiegeln, z. B. extensions/main.gd)
└── assets/ translations/      # optional; Assets mit Präfix <modname>_ und .import daneben
dist/                          # gebaute Zips (gitignored)
tools/build_zip.py             # Zip mit Root mods-unpacked/ (+ .import/) erzeugen
reference/                     # dekompiliertes Brotato, nur lokal (gitignored)
```

## Befehle

```powershell
# Lint und Format (gdtoolkit 3.x, Tabs). Python >= 3.12 braucht zusaetzlich: pipx inject gdtoolkit "setuptools<80"
gdlint mods-unpacked/<Namespace-ModName>
gdformat --check mods-unpacked/<Namespace-ModName>      # ohne --check formatiert es die Dateien

# Zip bauen; Version = version_number aus manifest.json; optional 3. Argument = Asset-Praefix fuer .import/
python tools/build_zip.py <Namespace-ModName> 1.0.0      # -> dist/<Namespace-ModName>-1.0.0.zip
python -m zipfile -l dist/<Namespace-ModName>-1.0.0.zip  # Eintraege muessen mit mods-unpacked/ beginnen, "/" als Trenner

# Testen: Zip in den Ordner des eigenen (versteckten) Workshop-Items legen, genau ein Zip dort, Spiel neu starten
Copy-Item dist/<Namespace-ModName>-1.0.0.zip "C:\Program Files (x86)\Steam\steamapps\workshop\content\1942280\<ItemId>\" -Force

# Logs nach dem Lauf (Shop, Welle, Endscreen, Beenden)
Get-Content "$env:APPDATA\Brotato\logs\modloader.log" -Tail 80
Select-String -Path "$env:APPDATA\Brotato\logs\godot.log" -Pattern "SCRIPT ERROR|Parse Error|ERROR:" | Select-String "<Namespace-ModName>"
```

- Steam-Startoptionen zum Debuggen: `--log-debug` (mehr ModLoader-Ausgabe), `--disable-mods` (sauber starten).
- Decompile nur für den eigenen Rechner: GDRE Tools → *Recover project* auf `Brotato.pck` nach `reference/`. Im Godot-**3.6**-Editor öffnen, nie mit Godot 4 (der Konverter zerstört das Projekt).
- Upload: `GodotWorkshopUtility.exe` aus dem Spielordner (Titel = Zip-Name, Workshop-ID für Updates eintragen) oder SteamCMD `workshop_build_item` mit `.vdf` (appid 1942280).

## Skills

`brotato-modding` (Mod Loader API, Manifest, Interna, Fehler → Lösung), `godot3-gdscript-pitfalls` (immer vor GDScript), `brotato-online-multiplayer` (Steam-Lobbys, Host-Autorität, Desync), `brotato-anticheat-trust` (Host und Clients gegenseitig prüfen, Commit-Reveal, Kick), `brotato-stability-performance` (Pooling, Crashes, Release-Checkliste), `brotato-ui-qol` (Menüs, Einstellungen, Tasten, Übersetzungen), `brotato-dev-workflow` (Dev-Loops, Mod-Loader-Flags, Headless-Tests, Lint, Packen, Upload); dazu `systematic-debugging` und `verification-before-completion`.

## Vor „fertig“

- [ ] `gdlint` und `gdformat --check` ohne Befund (Parse-Fehler = fast immer Godot-4-Syntax).
- [ ] `namespace-name` == Ordner == `MOD_ID`; `version_number` erhöht; `compatible_game_version`/`compatible_mod_loader_version` stimmen.
- [ ] Jede Override-Signatur aus dem aktuellen dekompilierten Spiel kopiert; jedes Override ruft `.method()` auf (außer bewusst ersetzt).
- [ ] Hash-Keys und `player_index` überall; solo und mit 2+ lokalen Spielern getestet (bei Online-Features auf zwei Rechnern).
- [ ] Zip gebaut, in den Workshop-Ordner kopiert, voller Lauf; `godot.log`/`modloader.log` ohne `SCRIPT ERROR`/`ERROR` zur Mod.
- [ ] `git status`: nur `mods-unpacked/<Namespace-ModName>/`, `tools/`, Doku; keine Spieldateien, keine Zips.

## Nie committen

`reference/` (dekompiliertes Spiel), `*.pck`, `Brotato*.exe`, `dist/`, `*.zip`, Logs, `CLAUDE.local.md`, `.claude/settings.local.json`.
