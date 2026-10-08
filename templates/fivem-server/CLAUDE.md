# <MeinServer> – FiveM-Server (Lua)

Vorlage aus `gamedev-skills/templates/fivem-server`. Platzhalter `<...>` ersetzen, Unzutreffendes löschen.
Dieses Repo ist der Ordner `server-data/` (Config + Resources). Artifacts, Datenbank und txAdmin-Daten liegen außerhalb.
Rechnerabhängige Pfade gehören in `CLAUDE.local.md` (gitignored, wird genauso geladen).

## Setup

- Plattform: FiveM **Legacy** (FXServer), Artifact **<35245 oder neuer, „Recommended“>** unter `<C:\FXServer\artifacts>`. <Oder: FiveM für GTAV Enhanced, `cfx-server`, siehe unten.>
- Game Build: `sv_enforceGameBuild <3889>` (nur beim Start gelesen; Änderung = Server-Neustart, Clients laden neu).
- Framework: **<ESX Legacy | QBCore | Qbox | standalone>** mit `ox_lib`, `oxmysql`, <`ox_inventory`, `ox_target`>. Nur APIs benutzen, die dieses Framework wirklich hat (Skill `fivem-frameworks`); nie `qb-core` und `qbx_core` gleichzeitig.
- OneSync: `on` (nicht `legacy`). Mit txAdmin wird OneSync dort eingestellt, nicht in `server.cfg`.
- Datenbank: MariaDB, Schema `<fivem>`, Zeichensatz `utf8mb4`/`utf8mb4_unicode_ci`; Verbindung über `mysql_connection_string` in `secrets.cfg`.
- Ordner: `server.cfg`, `secrets.cfg` (nicht im Repo, Vorlage `secrets.cfg.example`), `resources/[core]`, `[standalone]`, `[jobs]`, `[maps]`, `[vehicles]`.

## Starten, stoppen, neu laden

```bat
:: Windows ohne txAdmin (im Ordner server-data)
cd C:\FXServer\server-data
C:\FXServer\artifacts\FXServer.exe +exec server.cfg
```

```bash
# Linux ohne txAdmin
cd /opt/fxserver/server-data && bash /opt/fxserver/artifacts/run.sh +exec server.cfg
```

- Mit txAdmin: `FXServer.exe` bzw. `run.sh` **ohne** `+exec` starten, Web-UI `http://localhost:40120`; txAdmin übergibt `+exec <cfg>` und `+set onesync` selbst. Host-Einstellungen über `TXHOST_DATA_PATH`, `TXHOST_TXA_PORT`, `TXHOST_FXS_PORT`.
- Einzelne Resource: Server-Konsole `ensure <name>` (bei geänderter `fxmanifest.lua` vorher `refresh`). `start` meldet nichts, wenn schon gestartet – immer `ensure`.
- Server stoppen: `quit` in der Konsole (txAdmin: Stop-Button), nicht das Fenster schließen.

## `ensure`-Reihenfolge in `server.cfg`

`exec secrets.cfg` → `oxmysql` → `ox_lib` → Framework (`es_extended` | `qbx_core` | `qb-core`) → Framework-Abhängigkeiten (`ox_target`, `ox_inventory`) → `[standalone]` → `[jobs]` → `[maps]` → `[vehicles]`.
Convars, die eine Resource beim Start liest (`mysql_connection_string`, `inventory:framework`), stehen **vor** deren `ensure`. `#sv_master1` bleibt auskommentiert.

## Sicherheit (gilt immer)

1. Jeder Server-Event-Handler prüft `source`, Berechtigung, Zustand und Entfernung serverseitig und vertraut keinem Client-Wert (Geld, Items, Koordinaten, Preise).
2. `RegisterNetEvent` nur für Events, die Clients auslösen dürfen; Geschäftslogik nur in `server/`; keine `TriggerClientEvent(-1, ...)` mit Daten anderer Spieler; Rate-Limits für teure Events.
3. Secrets (`sv_licenseKey`, DB-Passwort, API-Keys, Webhooks) nur in `secrets.cfg`; nie in `server.cfg`, Lua, NUI oder Git.

## Konventionen

- `fxmanifest.lua`: `fx_version 'cerulean'`, `game 'gta5'`, `lua54 'yes'`; Dateien in `client/`, `server/`, `shared/` (so wählen `.luacheckrc` und LuaLS die richtigen Globals).
- `CreateThread` statt `Citizen.CreateThread`; keine `Wait(0)`-Schleife ohne Abbruch; Distanz-Checks mit steigendem Sleep; Natives nicht jeden Frame neu abfragen (Skill `fivem-performance-debugging`).
- Natives auf docs.fivem.net/natives nachschlagen, nicht raten; Hashes mit `joaat('name')` schreiben (die Backtick-Syntax versteht `luacheck` nicht).
- Callbacks über `lib.callback` (ox_lib) bzw. Framework-Callback; State Bags statt eigener Sync-Events für Entity-Zustand.
- NUI: Nachrichten validieren, `SetNuiFocus` immer wieder freigeben, keine Secrets ins HTML.
- Deutsch im Chat; Code, Kommentare und Commit-Messages auf Englisch.

## Werkzeuge

- LuaLS mit `fivem-lls-addon`: `.luarc.json` (Pfad zum Addon anpassen). Lokal zeigt das Plugin `lua-lsp` Claude nach jedem Edit Typ- und Natives-Fehler.
- `luacheck` läuft nach jedem Edit automatisch (Hook `.claude/hooks/lint-lua.sh`); ganze Resource: `luacheck resources/[core]/<resource>`.
- Komplettprüfung mit LuaLS: `lua-language-server --check=resources/[core]/<resource> --checklevel=Warning --logpath=.lls-log` (Report im Log-Ordner; TODO prüfen: Dateiname `check.json`).
- Im Spiel: F8 `resmon 1` (ms pro Resource), `profiler record 500` → `profiler view`; Server-Konsole zeigt `SCRIPT ERROR` mit Stacktrace.

## Test-Checkliste vor „fertig“

- [ ] `luacheck` ohne Errors; Warnungen bewertet.
- [ ] Server-Start ohne `SCRIPT ERROR`, `Couldn't start resource`, `Could not find dependency`, `was not safe for net`.
- [ ] F8-Konsole ohne `SCRIPT ERROR`; `resmon 1`: eigene Resource im Leerlauf ≤ 0.05 ms.
- [ ] Mit zwei Clients getestet (Sync, Events, Entity-Ownership), nicht nur allein.
- [ ] Server-Events mit fehlenden/falschen Argumenten und fremder `source` aufgerufen → sauber abgelehnt, kein Crash.
- [ ] `ensure <resource>` zur Laufzeit hinterlässt nichts (Threads, Blips, Entities, NUI-Fokus).
- [ ] `git status`: keine `secrets.cfg`, keine `cache/`, keine Escrow-Dateien verändert.

## FiveM für GTAV Enhanced (falls genutzt)

- Enhanced-Server = `cfx-server` (eigener Artifact-Zweig). Legacy-Assets werden mit **Alchemist** (`AlchemistCli.exe <in> <out>`) ins Gen9-Format konvertiert und in `stream_enhanced/` abgelegt; Natives-Unterschiede, Breaking Changes und neue Convars stehen im Skill `fivem-gta5-enhanced`.
- Legacy und Enhanced getrennt betreiben (eigene `server-data`, eigener Port); nichts ungetestet zwischen beiden kopieren.

## Skills

`fivem-resource-dev` (fxmanifest, Events, State Bags, NUI), `fivem-frameworks`, `fivem-security`, `fivem-performance-debugging` (Konsolenfehler → Fix), `fivem-server-setup` (server.cfg, Artifacts, Streaming), `fivem-gta5-enhanced`; dazu `systematic-debugging` und `verification-before-completion`.

## Nie committen

`secrets.cfg`, `cache/`, `txData/`, `*.log`, DB-Dumps mit Spielerdaten, Escrow-Dateien (`*.fxap`) verändert, `CLAUDE.local.md`, `.claude/settings.local.json`.
