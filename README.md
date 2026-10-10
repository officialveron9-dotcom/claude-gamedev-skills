# Gamedev-Skills für Claude

Skills, die Claude beim Programmieren für **Unreal Engine 5** (Billard-Spiel mit hoher Grafik),
**FiveM**, **FiveM für GTA V Enhanced**, **Brotato-Mods** (Godot) und **Web-Projekte** fehlendes Wissen geben: Entwicklungsfallen,
Fehlermeldung → Ursache → Lösung, richtige Code-Muster und Checklisten. Hintergrundwissen,
das Claude ohnehin kennt, ist bewusst weggelassen.

Stand der Recherche: **2026-10-06** (Unreal Engine 5.8, FiveM Legacy und FiveM für GTAV Enhanced im Early Access,
Brotato 1.1.15.x auf einem eigenen Godot-3-Build mit Godot Mod Loader 6.x).
Die Skill-Inhalte sind auf Englisch, weil Doku, APIs und Fehlermeldungen englisch sind.
Claude versteht trotzdem deine deutschen Fragen; die Beschreibungen enthalten auch deutsche Stichwörter.

## Was drin ist

| Plugin | Skills | Herkunft |
|---|---|---|
| `unreal-engine` | 11 | eigene Recherche |
| `unreal-engine-reference` | 31 | [quodsoler/unreal-engine-skills](https://github.com/quodsoler/unreal-engine-skills), MIT |
| `fivem` | 6 | eigene Recherche |
| `brotato` | 7 | eigene Recherche |
| `blender-modeling` | 12 (wird auf 13 erweitert) | eigene Recherche + [luckyfried/code-tools](https://github.com/luckyfried/code-tools), [scenario-labs/skills](https://github.com/scenario-labs/skills) (MIT) |
| `general-dev` | 2 | [obra/superpowers](https://github.com/obra/superpowers), MIT |
| `gamedev-general` | 12 | [awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) (Apache-2.0), [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), [fvadicamo/dev-agent-skills](https://github.com/fvadicamo/dev-agent-skills) (MIT) |
| `web-dev` | 12 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), [pproenca/dot-skills](https://github.com/pproenca/dot-skills), [addyosmani](https://github.com/addyosmani/web-quality-skills), [anthropics/skills](https://github.com/anthropics/skills), [testdino-hq](https://github.com/testdino-hq/playwright-skill), [supabase/agent-skills](https://github.com/supabase/agent-skills), [mcollina/skills](https://github.com/mcollina/skills) u. a. (MIT/Apache-2.0) |

### `unreal-engine` (eigene Skills)

| Skill | Wofür |
|---|---|
| `ue5-cpp-core` | UObject/Garbage Collection, Reflection-Makros, Delegates, Blueprint↔C++, Core Redirects |
| `ue5-build-and-modules` | Build.cs, Linker-Fehler (LNK2019), Live Coding, UBT/UHT, Packaging-Fehler |
| `ue5-multiplayer` | Replikation, RPCs, Ownership, „RPC feuert nicht“, „Variable repliziert nicht“ |
| `ue5-gameplay-systems` | Enhanced Input, Gameplay Ability System, Gameplay Tags, Subsystems, Asset Loading, UI |
| `ue5-version-notes` | Was sich von UE 5.0 bis 5.8 geändert hat, bekannte Engine-Bugs |
| `ue5-lighting-rendering` | Lumen, Belichtung, Licht im Innenraum, Reflexionen, Materialien (Filz, Kugeln), Path Tracer |
| `ue5-performance-optimization` | Profiling, CPU/GPU-Engpässe, Nanite, Scalability, Shader-Ruckler, Speicher sparen |
| `ue5-animation-characters` | Animation Blueprints, Motion Matching, Control Rig/IK, Retargeting, MetaHuman |
| `ue5-character-creation-clothing` | Charaktere aus MetaHuman, Fab, CC4, Daz, Mixamo; Kleidung anziehen ohne Durchstechen; Stoffsimulation |
| `ue5-npc-ai` | StateTree/Behavior Tree, NavMesh, Wahrnehmung, Smart Objects, Zuschauer-NPCs, KI-Gegner |
| `billiards-game-dev` | Kugelphysik (eigene Simulation statt Chaos), Effet, Banden, Zielhilfe, Multiplayer-Sync |

### `fivem` (eigene Skills)

| Skill | Wofür |
|---|---|
| `fivem-resource-dev` | fxmanifest, Events, Callbacks, Exports, State Bags, NUI, OneSync-Entities |
| `fivem-frameworks` | ESX Legacy, QBCore, Qbox, ox_lib/ox_inventory/ox_target, oxmysql, Bridges |
| `fivem-security` | Server-Events absichern, Exploits, Entity Lockdown, ACE, Secrets |
| `fivem-performance-debugging` | resmon, Profiler, teure Loops, Konsolenfehler mit Lösung |
| `fivem-server-setup` | server.cfg, Game Build, txAdmin, Artifacts, Datenbank, Streaming von Autos/MLOs/Kleidung |
| `fivem-gta5-enhanced` | Was auf FiveM für GTAV Enhanced anders ist: `cfx-server`, Breaking Changes, `stream_enhanced`, Alchemist |

### `blender-modeling` (alles fürs Modellieren in Blender)

| Skill | Wofür |
|---|---|
| `gta-texture-editing` | GTA-Texturen bearbeiten: aufgemalte Türen/Fenster wegretuschieren (auch `_n`, `_s`, Nacht-Maps, LODs), Farben ändern, DDS-Formate, `.ytd` packen; getestete Python-Scripts |
| `fivem-mlo-doors-windows` | Echte Türen, Garagentore (Keypad, PIN, Fernbedienung) und Glasfenster mit Durchsicht für MLOs; Portale, Glas-Shader, Türsystem-Lua, ox_doorlock |
| `clothing-creation-pipeline` | Fotorealistische Kleidung erstellen und an den Körper anpassen: Marvelous Designer/CLO, Blender, Substance-Stoffe, Weight-Transfer, Export nach UE |
| `blender-python-pitfalls` | bpy-Änderungen von Blender 2.8 bis 5.x, exakte Fehlermeldungen → Ursache → Lösung; damit Claudes Blender-Scripts laufen |
| `blender-current-api`, `blender-game-export`, `blender-verify` | Aktuelle API, Export für Game-Engines, Ergebnisse prüfen (übernommen, MIT) |
| `scenario-blender-expert`, `-hard-surface`, `-retopology`, `-uv-baking`, `-rigging` | Modellieren, Retopologie, UV und Baking, Rigging mit Python-Scripts, getestet auf Blender 5.2 (übernommen, MIT) |

Blender-MCP, Sollumz und hilfreiche Addons: [plugins/blender-modeling/EXTERNAL.md](plugins/blender-modeling/EXTERNAL.md).

### `brotato` (eigene Skills)

| Skill | Wofür |
|---|---|
| `brotato-modding` | Godot Mod Loader 6.x, `manifest.json`, `mod_main.gd`, Script-Extensions, Brotato-Interna, Workshop, Fehler → Lösung |
| `godot3-gdscript-pitfalls` | Verhindert Godot-4-Syntax in Godot-3-Code (`export`, `yield`, `connect`, `.method()` …), Engine-Fallen |
| `brotato-online-multiplayer` | Online-Koop über Steam-Lobbys und P2P: Host-Autorität, Zufall synchronisieren, Snapshots, Desync-Fixes |
| `brotato-stability-performance` | Gegen Lag, Abstürze und Verbindungsabbrüche: Pooling, freigegebene Nodes, CrashReporter, Release-Checkliste |
| `brotato-ui-qol` | Optionsmenü-Tabs, Mod-Einstellungen (`ModLoaderConfig`), Tastenbelegung im Koop, HUD-Overlays, Übersetzungen, sicheres Speichern |
| `brotato-dev-workflow` | Schneller Entwicklungskreislauf: Editor vs. echtes Spiel, Mod-Loader-Flags, Tests ohne Spiel-Fenster, `gdlint`/`gdformat`, Packen, Workshop-Upload, CI |
| `brotato-anticheat-trust` | Gegenseitige Kontrolle im Koop, auch des Hosts: Commit-Reveal-Seed, Clients prüfen Shop/Drops/Schaden nach, Hash-Vergleich unter allen, Steam-Auth-Tickets; bei Abweichung ist der Run ungültig (kein Kick); Ranking ohne Server über lokale, von Mitspielern signierte Run-Historie |

Brotato läuft auf **Godot 3**. Installiere keine Godot-4-Skills zusammen mit diesen, sonst schreibt Claude
wieder Godot-4-Code. Externe Tools und Beispiel-Mods: [plugins/brotato/EXTERNAL.md](plugins/brotato/EXTERNAL.md).

### `gamedev-general` (übernommen, engine-neutral)

| Skill | Wofür |
|---|---|
| `performance-optimization`, `shader-programming`, `physics-tuning`, `save-systems`, `game-feel`, `steam-publish` | Engine-neutrale Spielentwicklung mit Workflow, Falsch-vs-Richtig-Code und Fehlertabellen; Beispiele in Godot 4/Unity, jede Datei nennt die Godot-3- und Unreal-Entsprechung |
| `tdd`, `code-review`, `codebase-design`, `grilling`, `writing-for-agents` | Allgemeine Coding-Disziplin: erst Test, dann Code; Review-Checkliste; Architektur; Pläne vor großen Features durchfragen; gute `CLAUDE.md` schreiben |
| `git-commit` | Saubere, kleine Commits mit guten Nachrichten |

Passt zu allen drei Projekten. Die gerankte Gesamtliste mit weiteren Empfehlungen und Lücken: [docs/beste-skills-games-allgemein.md](docs/beste-skills-games-allgemein.md).

### `web-dev` (übernommen, für Websites und Web-Apps)

| Skill | Wofür |
|---|---|
| `vercel-react-best-practices`, `react-19-best-practices`, `nextjs-16-app-router`, `tailwind-v4-best-practices` | Aktuelle Framework-Versionen statt veralteter APIs: Server/Client Components, Hydration, Wasserfälle, Bundle-Größe, Tailwind v4 |
| `wcag-accessibility`, `core-web-vitals`, `security-and-hardening` | Barrierefreiheit (WCAG 2.2), Ladezeit-Metriken, OWASP-Sicherheit (XSS, CSRF, Auth, Secrets) |
| `webapp-testing`, `playwright-core` | Web-Apps im Browser testen, flaky Tests vermeiden |
| `dependency-verification` | Erfundene npm-Pakete erkennen, bevor sie installiert werden |
| `supabase-postgres-best-practices`, `nodejs-best-practices` | Datenbank-Schema und Abfragen, Node.js-Backend |

Nur für Web-Projekte installieren. Gerankte Gesamtliste mit weiteren Empfehlungen und Lücken: [docs/beste-skills-web.md](docs/beste-skills-web.md).

### `unreal-engine-reference` und `general-dev` (übernommen)

- **`unreal-engine-reference`**: 31 tiefe UE-5.8-C++-Skills von quodsoler, z. B. GAS, Replikation,
  Actor-Lifecycle, Niagara, UMG/Slate, Savegames, Testing. Der Skill `ue-project-context` legt in
  deinem Spielprojekt `.agents/ue-project-context.md` an, das die anderen Skills lesen. Den solltest du zuerst ausführen.
- **`general-dev`**: `systematic-debugging` (erst Ursache finden, dann fixen) und
  `verification-before-completion` (erst prüfen, dann „fertig“ sagen) aus der bekanntesten Skill-Sammlung.

## So benutzt du die Skills

**Nicht alles in jedes Projekt packen.** Jede Skill-Beschreibung kostet Claude in jeder Nachricht etwas Kontext.

| Projekt | Plugins |
|---|---|
| Unreal-Spiel | `unreal-engine`, `unreal-engine-reference`, `general-dev`, `gamedev-general` |
| FiveM-Server (Legacy oder Enhanced) | `fivem`, `general-dev` |
| Brotato-Mod | `brotato`, `general-dev`, `gamedev-general` |
| Website / Web-App | `web-dev`, `general-dev` |
| Blender (GTA-MLOs, Kleidung, Modelle) | `blender-modeling`, `general-dev` |

### A) Claude Code im Web (claude.ai/code)

Cloud-Sessions laden **nur** Skills aus dem Ordner `.claude/skills/` des Repos, an dem gearbeitet wird.
Plugins und Marketplaces werden dort nicht geladen. Deshalb kopierst du die Skills einmal in dein Spiel-Repo:

- **Am einfachsten:** Starte eine Session mit deinem Spiel-Repo **und** diesem Repo und schreib:
  „Kopiere die Unreal-Skills aus gamedev-skills nach `.claude/skills/` in meinem Spiel-Repo und pushe.“
- **Oder selbst auf deinem PC** (danach `.claude/skills/` committen und pushen):

  ```powershell
  # Windows PowerShell, im Ordner dieses Repos
  .\scripts\install-skills.ps1 -Project C:\Pfad\zu\MeinSpiel -Plugin unreal-engine, unreal-engine-reference, general-dev
  .\scripts\install-skills.ps1 -Project C:\Pfad\zu\server-data -Plugin fivem, general-dev
  .\scripts\install-skills.ps1 -Project C:\Pfad\zu\MeineBrotatoMod -Plugin brotato, general-dev
  ```

  ```bash
  # Linux / macOS / Git Bash
  scripts/install-skills.sh ~/MeinSpiel unreal-engine unreal-engine-reference general-dev
  scripts/install-skills.sh ~/server-data fivem general-dev
  scripts/install-skills.sh ~/MeineBrotatoMod brotato general-dev
  ```

Wenn du hier Skills änderst, kopierst du sie danach erneut in deine Projekte.

### B) Claude Code lokal (Terminal, Desktop-App, VS Code)

Dieses Repo ist ein Plugin-Marketplace. Weil es privat ist, muss git auf deinem PC bei GitHub
angemeldet sein (z. B. `gh auth login` und danach `gh auth setup-git`).

```text
/plugin marketplace add <dein-github-name>/<dieses-repo>
/plugin install unreal-engine@gamedev-skills
/plugin install unreal-engine-reference@gamedev-skills
/plugin install fivem@gamedev-skills
/plugin install blender-modeling@gamedev-skills
/plugin install brotato@gamedev-skills
/plugin install general-dev@gamedev-skills
/plugin install gamedev-general@gamedev-skills
/plugin install web-dev@gamedev-skills
```

Alternativ für alle Projekte auf einmal: `.\scripts\install-skills.ps1 -Personal -Plugin ...` kopiert
die Skills nach `~/.claude/skills/`.

### C) claude.ai (Chat)

1. Unter **Settings → Capabilities** muss „Code execution and file creation“ an sein.
2. ZIP-Dateien bauen: `.\scripts\package-skills.ps1` (Windows) oder `scripts/package-skills.sh`.
   Danach liegt pro Skill eine ZIP in `dist/`.
3. In claude.ai: **Customize → Skills → „+“ → Upload a skill** und die ZIP hochladen.

Falls ein Upload wegen zu langer Beschreibung abgelehnt wird, lass Claude die `description` im
jeweiligen `SKILL.md` kürzen.

## Projekt-Vorlagen und Tools

- **[templates/](templates/README.md)**: fertige `CLAUDE.md`, `.claude/settings.json` mit Hooks (Lint nach jeder Änderung),
  Linter-Configs und `.gitignore` für ein Unreal-Projekt, einen FiveM-Server und eine Brotato-Mod. Einmal ins
  Projekt kopieren, dann kennt Claude dort Befehle, Regeln und Prüfungen.
- **[docs/tools-und-sdks.md](docs/tools-und-sdks.md)**: geprüfte Tools und SDKs gegen Lag, Abstürze und Desync,
  mit Installationsbefehlen und der Angabe, ob sie in Cloud-Sessions oder nur lokal funktionieren.

## Empfohlene Plugins zusätzlich (lokal)

Gut bewertete Sammlungen, die man besser installiert als kopiert. Die volle, gerankte Liste mit
Sternen, Lizenzen und Begründung steht in [docs/external-resources.md](docs/external-resources.md).

```text
/plugin install superpowers@claude-plugins-official                          # Debugging, TDD, Planen, Review
/plugin install unreal-engine-skills-for-claude-code@claude-plugins-official # Epics offizielles UE-Plugin (Editor-Steuerung, UE 5.8)
/plugin install lua-lsp@claude-plugins-official                              # Lua-Fehler sofort sehen (FiveM, mit fivem-lls-addon)
/plugin install clangd-lsp@claude-plugins-official                           # C++-Fehler sofort sehen (UE, braucht compile_commands.json)
/plugin install code-review@claude-plugins-official                          # Code-Review
```

Wenn du `superpowers` komplett installierst, brauchst du `general-dev` aus diesem Repo nicht zusätzlich.

## Neue Probleme eintragen

Claude weiß nicht alles. Wenn ihr einen Fehler gelöst habt, der nicht in den Skills stand,
sag Claude in einer Session mit diesem Repo:

> „Trag diesen Fehler und die Lösung in den passenden Skill ein.“

Jeder Skill hat unter `references/` eine Tabelle mit bekannten Problemen
(`common-errors.md`, `common-issues.md`, `troubleshooting.md` oder `known-issues.md`). Dort kommt eine
neue Zeile rein: **Fehlermeldung bzw. Symptom → Ursache → Lösung**.

## Aufbau

```text
.claude-plugin/marketplace.json     Marketplace "gamedev-skills"
plugins/<plugin>/skills/<skill>/    SKILL.md + references/ (Details, Fehlertabellen, Quellen)
plugins/<plugin>/UPSTREAM.md        bei übernommenen Skills: Quelle, Lizenz, Commit
scripts/                            Skills in Projekte kopieren, ZIPs für claude.ai bauen, Skills prüfen
templates/                          CLAUDE.md, .claude/settings.json mit Hooks, Linter-Configs je Projekt (siehe templates/README.md)
docs/external-resources.md          gerankte externe Skills, MCP-Server und Tools
docs/tools-und-sdks.md              geprüfte Tool-/SDK-Tabellen je Projekt (Lag, Crashes, Desync, Claude-Code-Plugins)
research/                           Format der Skills/Plugins, welche fremden Skills man übernehmen darf
```

Jede eigene Skill hat `references/sources.md` mit den Quellen. Was nicht direkt aus einer
Primärquelle belegt ist, ist dort markiert. Vor allem bei Unreal 5.8 und FiveM für GTAV Enhanced
ändert sich viel. Prüf bei Versions-Updates die Datei `ue5-version-notes` bzw. `fivem-gta5-enhanced`.

## Lizenzen

Übernommene Skills stehen unter ihrer Originallizenz (MIT). Die Lizenzdatei liegt in jedem Skill-Ordner,
die Quelle samt Commit steht in `UPSTREAM.md`.
