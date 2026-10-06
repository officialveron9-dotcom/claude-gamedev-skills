# Externe Ressourcen: Unreal Engine 5, FiveM / Cfx.re, Claude-Skills

Stand: **2026-10-06**. Diese Datei enthält Links und eigene Kurzbeschreibungen. Übernommen
wurden bisher nur **quodsoler/unreal-engine-skills** (komplett, als Plugin `unreal-engine-reference`)
und aus **obra/superpowers** die Skills `systematic-debugging` und `verification-before-completion`
(Plugin `general-dev`), beide MIT, mit Lizenzdatei und `UPSTREAM.md`. Bei Repos ohne Lizenz gilt:
nur lesen, nicht übernehmen. Welche Skills sich übernehmen lassen, steht in `research/vendorable.md`.

**So wurde geprüft:**
- GitHub-Repos: per `git clone --depth 1` geklont. Daraus stammen das Datum des letzten Commits (Spalte „Letzte Aktivität“) und die Lizenzdatei im Repo-Root, notfalls der Lizenzhinweis im README. Sterne laut GitHub-Suche am 2026-10-06, gerundet.
- Nicht-GitHub-Seiten (dev.epicgames.com, docs.fivem.net, runtime.fivem.net, agentskills.io, luals.github.io) waren aus der Sandbox gesperrt. Sie sind über den Suchindex bzw. über Verweise in geprüften Repos belegt und mit „(Suchindex)“ markiert.
- „Verdikt“ ist meine Einschätzung für unseren Zweck: ein persönliches Skill-Repo für UE5 und FiveM, auch für FiveM auf GTA V Enhanced.

---

## Top-Empfehlungen: installierbare Skills und Plugins, nach Nutzen gerankt

Gerankt nach Nutzen für **dich**: UE5 mit C++/Blueprints, FiveM mit Lua, dazu allgemeines
Programmieren (Debugging, TDD, Code-Review, Refactoring, Planung). Sterne und letzte Aktivität
stammen vom 2026-10-06. Sterne sind nur ein Popularitätssignal. Bei sechsstelligen Werten ist
viel Hype dabei, Qualität bitte selbst prüfen.

**Vor dem Installieren:**
- Die Befehle gelten in einer lokalen Claude-Code-Session (Terminal, Desktop, VS Code). Statt `/plugin install …` geht im Terminal auch `claude plugin install …`.
- `claude-plugins-official` ist bereits registriert. Andere Marketplaces brauchst du nur einmal mit `/plugin marketplace add` hinzuzufügen.
- **In Cloud-Sessions (claude.ai/code) laden Plugins nicht.** Details in `research/claude-code-format.md`, Abschnitt 4.
- **Nicht alles auf einmal installieren.** Jede Skill-Beschreibung kostet in jeder Nachricht Kontext, und überlappende Sammlungen (z. B. Superpowers *und* Matt Pocock mit TDD/Debugging) konkurrieren um dieselben Auslöser. Empfohlener Start: Platz 1–5.

| Rang | Was | Sterne / Signal | Letzte Aktivität | Lizenz | Installation | Warum für dich |
| :- | :- | :- | :- | :- | :- | :- |
| 1 | **obra/superpowers**: Skills für Debugging, TDD, Planen, Code-Review, Verifikation | ~296k★, im offiziellen Marketplace | 2026-09-25 | MIT | `/plugin install superpowers@claude-plugins-official` | Die bekannteste Methodik-Sammlung. Stark bei systematischem Debugging, TDD, Plan schreiben und ausführen sowie „verification-before-completion“. Sprachunabhängig, also auch für C++ und Lua. |
| 2 | **Epic Games: unreal-engine-skills-for-claude-code** | ~320★, offiziell von Epic | 2026-09-17 | MIT | `/plugin install unreal-engine-skills-for-claude-code@claude-plugins-official` | Offizielle Editor-Steuerung über Unreal MCP (UE 5.8, experimentell). Pflicht für UE-Arbeit, siehe 1.1. |
| 3 | **lua-lsp** und **clangd-lsp** (Anthropic, LSP-Plugins) | offizieller Marketplace (~37k★ Repo) | 2026-10-05 | Apache-2.0 | `/plugin install lua-lsp@claude-plugins-official` und `/plugin install clangd-lsp@claude-plugins-official` | Claude sieht nach jedem Edit echte Compiler- und Typfehler. Für FiveM kommt **fivem-lls-addon** über `.luarc.json` dazu (siehe 2.2). Für UE braucht clangd eine `compile_commands.json`. Voraussetzung: `lua-language-server` bzw. `clangd` sind installiert. |
| 4 | **Anthropic-Workflow-Plugins**: `code-review`, `pr-review-toolkit`, `feature-dev`, `code-simplifier`, `security-guidance` | offizieller Marketplace, von Anthropic gepflegt | 2026-10-05 | Apache-2.0 | `/plugin install code-review@claude-plugins-official` (analog für `pr-review-toolkit`, `feature-dev`, `code-simplifier`, `security-guidance`) | Review mit mehreren Agents, Feature-Workflow (explore, architect, review) und Vereinfachen von Code. Gut gepflegt und gering riskant. Wähle 1–2 davon, nicht alle. |
| 5 | **mattpocock/skills**: `grill-me`, `tdd`, `diagnosing-bugs`, `code-review`, `to-spec`, `improve-codebase-architecture` | ~278k★, im offiziellen Marketplace | 2026-10-06 | MIT | `/plugin install mattpocock-skills@claude-plugins-official` | Kurze, präzise Skills (TDD hat z. B. 38 Zeilen). `grill-me` ist sehr gut zum Durchfragen von Plänen vor großen Features. **Alternative zu Platz 1**, nicht zusätzlich, falls dir Superpowers zu „schwer“ ist. |
| 6 | **trailofbits/skills**: `modern-cpp`, `c-review`, `differential-review`, `static-analysis` | ~7,4k★, Security-Firma Trail of Bits | 2026-09-28 | **CC BY-SA 4.0** | `/plugin marketplace add trailofbits/skills`, dann `/plugin install modern-cpp@trailofbits` und `/plugin install c-review@trailofbits` | Die besten C++-spezifischen Skills, die ich gefunden habe: moderne Idiome (C++20/23) und Security-Review für C/C++ (Speicherfehler, Integer-Overflows). Für UE-C++ teilweise anpassen, weil UE eigene Container und Smart Pointer nutzt. |
| 7 | **quodsoler/unreal-engine-skills**: 31 UE-C++-Skills | ~360★ | 2026-09-28 | MIT | **Schon in diesem Repo** als Plugin `unreal-engine-reference`. Original: `npx skills add quodsoler/unreal-engine-skills` | Inhaltlich die tiefsten UE-Skills (GAS, Replikation, Actor-Lifecycle …), gegen UE 5.8 geprüft. Nur die Skills nehmen, die du brauchst. |
| 8 | **wshobson/agents**: Marketplace `claude-code-workflows` (~95 Plugins) | ~40k★ | 2026-10-04 | MIT | `/plugin marketplace add wshobson/agents`, dann z. B. `/plugin install systems-programming@claude-code-workflows` (enthält Agent `cpp-pro`), `debugging-toolkit@claude-code-workflows`, `code-refactoring@claude-code-workflows` | Riesiger Baukasten aus vielen Subagents. Nur gezielt einzelne Plugins installieren. Viel Überlappung mit Platz 1, 4 und 5. |
| 9 | **OthmanAdi/planning-with-files** | ~27k★ | 2026-10-06 | MIT | `/plugin marketplace add OthmanAdi/planning-with-files`, dann `/plugin install planning-with-files@planning-with-files` | Pläne liegen als Dateien auf der Platte und überstehen `/clear` und Kompaktierung. Gut für lange UE-Refactorings. Achtung: arbeitet mit Hooks, die in jeder Runde laufen. |
| 10 | **hyhmrright/brooks-lint** | ~1,5k★, auch im Community-Marketplace | 2026-10-05 | MIT | `/plugin marketplace add hyhmrright/brooks-lint`, dann `/plugin install brooks-lint@brooks-lint-marketplace` | Code-Review und Tech-Debt-Diagnose, begründet mit Klassikern (Fowler, Feathers, Ousterhout …). Nützlich für Refactoring-Entscheidungen. |
| 11 | **FiveM: matiaspalmac/fivem-security-audit** und **hamchowderr/fivem-kit** | jung, < 10★ | 2026-09-04 / 2026-08-11 | MIT | Security-Audit: `npx fivem-security-audit`. Kit: `/plugin marketplace add hamchowderr/fivem-kit`, dann `/plugin install fivem@fivem-kit` | Es gibt keine etablierte, hoch bewertete FiveM-Sammlung. Diese beiden sind die brauchbarsten Ansätze (Dupe- und Backdoor-Audit bzw. Natives und Frameworks). **Vor Nutzung lesen** und gezielt in eigene Skills überführen. |
| 12 | **DietrichGebert/ponytail**: YAGNI, „die faulste Lösung, die funktioniert“ | ~157k★, auch im Community-Marketplace | 2026-10-05 | MIT | `/plugin marketplace add DietrichGebert/ponytail`, dann `/plugin install ponytail@ponytail` | Optional. Hilft gegen Over-Engineering, kann aber mit eigenen Architektur-Vorgaben kollidieren. |

**Bewusst nicht empfohlen:**
- `gsd-build/get-shit-done` (~64k★) ist seit 2026 **archiviert**.
- `SuperClaude-Org/SuperClaude_Framework` (~24k★, MIT) ist ein Framework-Installer statt Plugin und greift tief in die Konfiguration ein.
- `alirezarezvani/claude-skills` (~28k★, MIT) hat über 380 Skills, überwiegend Business- und Marketing-Themen.
- `Jeffallan/claude-skills` (~12k★, MIT; `/plugin marketplace add jeffallan/claude-skills`, dann `/plugin install fullstack-dev-skills@fullstack-dev-skills`) ist ein einziges Bündel mit 67 Skills. Besser den Skill `cpp-pro` einzeln übernehmen, siehe `research/vendorable.md`.
- „everything-claude-code“-Kopien: Herkunft unklar, das Original-Repo ist per GitHub-Suche nicht mehr auffindbar.
- `Egonex-AI/Understand-Anything` (~85k★, MIT, Codebase-Wissensgraph) ist optional, um sich in große fremde Codebasen einzulesen. Für den Alltag nicht nötig.

### Domänen-Kurzfassung (Details in den Abschnitten unten)

| Bereich | Wichtigste Ressourcen |
| :- | :- |
| UE5 Editor | Epic Unreal MCP (UE 5.8) und Epics Plugin (Rang 2). Alternativen: ChiR24/Unreal_mcp, tumourlove/monolith |
| UE5 Doku/API | Codeturion/unreal-api-mcp (offline, MIT) |
| UE5 Skills | quodsoler/unreal-engine-skills, ibrews/ue5-mcp (Gotchas), ABostrom/ushell-skill (Build/Cook) |
| FiveM Natives | docs.fivem.net/natives, citizenfx/natives, `citizenfx/fivem` `ext/native-decls`, `runtime.fivem.net/doc/natives*.json`, alloc8or `natives_gen9.json` (Enhanced) |
| FiveM Lua-Tooling | LuaLS + overextended/fivem-lls-addon + `lua-lsp`-Plugin |
| FiveM Live-Test | ziyacivan/fivem-mcp, nimoalr/lavender-mcp-server (unterstützt laut Beschreibung Enhanced). Nur auf Dev-Servern |
| Skill-Authoring | anthropics/skills, `skill-creator@claude-plugins-official`, agentskills/agentskills (`skills-ref validate`) |

---

## 1. Unreal Engine

### 1.1 Offiziell von Epic

**Unreal MCP in Unreal Editor (Epic-Dokumentation)**
- URL: https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor (Suchindex). API-Referenz: https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ModelContextProtocol (Suchindex)
- Lizenz: Teil der Engine (Unreal Engine EULA)
- Funktion: Ein experimentelles Editor-Plugin („Unreal MCP“ / `ModelContextProtocol`, dazu `AllToolsets`/ToolsetRegistry) startet einen MCP-Server im Editor-Prozess, standardmäßig `http://127.0.0.1:8000/mcp`. Es gibt keine Authentifizierung, das Plugin ist nicht für Remote-Nutzung gedacht, und Tool-Aufrufe laufen seriell auf dem Game-Thread. Erschienen mit UE 5.8 (Juni 2026).
- Wartung: aktiv, aber „Experimental“ (APIs können sich ändern)
- Verdikt: **Erste Wahl** für die Editor-Anbindung, sobald das Projekt auf UE 5.8 läuft. Laut einer Community-Quelle (ibrews/ue5-mcp) braucht es evtl. einen Source-Build der Engine. Bitte selbst prüfen.

**EpicGames/unreal-engine-skills-for-claude-code-plugin**
- URL: https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin
- Lizenz: MIT (© 2026 Epic Games). Version 3.1.1
- Funktion: Offizielles Claude-Code-Plugin im Marketplace `claude-plugins-official`. Es enthält die Skills `unreal-mcp`, `create-toolset` und `unreal-skill` sowie einen SessionStart-Hook, der UE-Konventionen setzt (der Hook braucht bash bzw. Git Bash unter Windows). Die MCP-Konfiguration erzeugt man im Editor mit `ModelContextProtocol.GenerateClientConfig ClaudeCode`. „Tool search“ (nur 3 Meta-Tools) spart Kontext. Installation: `/plugin install unreal-engine-skills-for-claude-code@claude-plugins-official`
- Wartung: letzter Commit 2026-09-17, ca. 320★, aktiv
- Verdikt: **Unbedingt nutzen, nicht nachbauen.** Unsere eigenen UE-Skills sollen dieses Plugin ergänzen (Projektkonventionen, Build/Cook, C++-Stil), nicht ersetzen. Die Sicherheitshinweise im README beachten: `execute_tool_script` führt beliebiges Python im Editor aus.

### 1.2 Community-MCP-Server für den Editor

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| ChiR24/Unreal_mcp | https://github.com/ChiR24/Unreal_mcp | MIT | 2026-10-05 (~900★) | TypeScript-Server und C++-„Automation Bridge“-Plugin. Rund 400 Fähigkeiten hinter einem einzigen Tool `unreal`: PIE, Screenshots, Logs, Python, Packaging. | Stärkste Community-Alternative, falls Epics MCP nicht reicht oder UE < 5.8 im Einsatz ist. |
| tumourlove/monolith | https://github.com/tumourlove/monolith | MIT | 2026-09-10 (~320★) | Natives C++-Plugin für UE 5.7/5.8 mit über 1.400 Aktionen (Blueprints, Materials, Niagara, GAS, UI, Audio) und C++-Lookups (Includes, Signaturen). | Sehr umfangreich und aktiv. Interessant für tiefe Blueprint/GAS-Arbeit. |
| db-lyon/ue-mcp | https://github.com/db-lyon/ue-mcp | MIT | 2026-10-06 (~380★) | C++-Bridge über WebSocket mit 26 Kategorie-Tools. Bindet auf UE 5.8+ zusätzlich Epics native Toolsets ein. Enthält auch 6 Skills. | Aktiv, aber viele offene Issues (87). Beobachten. |
| flopperam/unreal-engine-mcp | https://github.com/flopperam/unreal-engine-mcp | MIT (laut README, keine LICENSE-Datei) | 2026-06-26 (~1,1k★) | Blueprint-Authoring und Weltbau für UE 5.5–5.7. Das Projekt gehört inzwischen zum kommerziellen Anbieter „Aura“. | Populär, aber kommerziell ausgerichtet. Mit Vorsicht einsetzen. |
| chongdashu/unreal-mcp | https://github.com/chongdashu/unreal-mcp | MIT (README-Badge, keine LICENSE-Datei) | 2025-04-22 (~2,1k★) | Das Pionier-Projekt: Python-MCP plus C++-Plugin für UE 5.5, als „Experimental“ markiert. | **Veraltet.** Nur historisch interessant. |
| runreal/unreal-mcp | https://github.com/runreal/unreal-mcp | MIT | 2025-06-06 (~120★) | Nutzt die eingebaute Python Remote Execution von UE und braucht kein eigenes Plugin (UE 5.4+). | Schlank, aber seit über einem Jahr ohne Commit. |
| kvick-games/UnrealMCP | https://github.com/kvick-games/UnrealMCP | MIT (README) | 2025-06-21 (~610★) | Frühes MCP-Plugin, getestet mit UE 5.5. | Veraltet. |

### 1.3 Doku- und API-Suche

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| Codeturion/unreal-api-mcp | https://github.com/Codeturion/unreal-api-mcp | MIT | 2026-07-19 (~100★) | MCP-Server mit vorgebauter UE-C++-API-Datenbank, Version per `UNREAL_VERSION` wählbar. Braucht keine UE-Installation. | **Empfohlen** gegen erfundene Signaturen und Includes. Funktioniert auch in Cloud-Sessions ohne Editor. |
| remiphilippe/mcp-unreal | https://github.com/remiphilippe/mcp-unreal | Apache-2.0 | 2026-02-19 (~75★) | Einzelnes Go-Binary für UE 5.7: headless Build/Tests, Editor über Remote Control API und lokaler Doku-Index (`--build-index`). | Gute Idee (Build und Tests aus Claude), aber seit 8 Monaten still. |
| daniel-eder/unreal-engine-assistant-mcp | https://github.com/daniel-eder/unreal-engine-assistant-mcp | CC0/MIT/Apache (REUSE, Ordner `LICENSES/`) | 2026-03-28 | Fragt per Puppeteer Epics Web-„Unreal AI Assistant“ ab. | Fragil und rechtlich heikel (Web-Automation eines fremden Dienstes). **Nicht empfohlen.** |

### 1.4 Skills und CLAUDE.md-Vorlagen

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| quodsoler/unreal-engine-skills | https://github.com/quodsoler/unreal-engine-skills | MIT | 2026-09-28 (~360★) | 31 Agent-Skills für UE-C++ (Actor-Lifecycle, GAS, Replikation, Niagara, UMG, Mass, StateTree …), gegen die UE-5.8-Header geprüft. Ein Basis-Skill schreibt den Projektkontext. | **Beste inhaltliche Vorlage.** Struktur ansehen und eigene, projektbezogene Skills schreiben. |
| gamedev-skills/awesome-gamedev-agent-skills | https://github.com/gamedev-skills/awesome-gamedev-agent-skills | Apache-2.0 | 2026-09-27 (~1,3k★) | 74 Gamedev-Skills für viele Engines, darunter 6 Unreal-Skills (Blueprints, C++, Enhanced Input, Niagara, Packaging, BTs). Mit `marketplace.json`. | Gute Breite, aber weniger tief als quodsoler. |
| ibrews/ue5-mcp | https://github.com/ibrews/ue5-mcp | MIT (README) | 2026-08-09 | Server-unabhängiger Skill mit UE5-Fallstricken bei MCP-Arbeit (Niagara, Lumen, MetaSound, UMG; Unterschiede UE 5.7 vs. 5.8). | Nützliche Gotcha-Sammlung als Ergänzung zu Epics Plugin. |
| ABostrom/ushell-skill | https://github.com/ABostrom/ushell-skill | MIT | 2026-05-14 | Skill für Epics CLI `ushell` (UAT, BuildGraph, Build/Cook-Kanäle). Als Plugin mit Marketplace aufgebaut. | Relevant für Build- und Cook-Automatisierung. |
| MRCalderon3D/everything-game-dev-code | https://github.com/MRCalderon3D/everything-game-dev-code | MIT | 2026-08-20 (~90★) | Großes Multi-Engine-Gerüst mit 42 Agents, 51 Commands und 86+ Skills. | Zu breit für uns. Höchstens als Ideensteinbruch. |
| Johan-p/unreal-claude-template | https://github.com/Johan-p/unreal-claude-template | **keine Lizenz** | 2026-08-18 | Claude-Code-Gerüst für UE-Projekte (`.claude/skills`, Subagents, Spec-Pipeline). | Nur als Anschauung für den Aufbau einer `CLAUDE.md` und `.claude/` in UE-Projekten. **Nichts übernehmen.** |
| Sophriel/Claude-Code-Skill-for-Unreal-Engine | https://github.com/Sophriel/Claude-Code-Skill-for-Unreal-Engine | **keine Lizenz** („as-is“) | 2026-08-14 | Ein UE-C++-Skill mit Referenzdateien. | Nur lesen. |

### 1.5 Code-Intelligenz für UE-C++

- **clangd-lsp** (offizielles Anthropic-Plugin): https://github.com/anthropics/claude-plugins-official/tree/main/plugins/clangd-lsp (Apache-2.0, Repo aktiv 2026-10-05). Startet `clangd --background-index`, damit Claude C++-Diagnosen und Symbolnavigation bekommt. Für UE wird eine `compile_commands.json` gebraucht, die UnrealBuildTool erzeugen kann. Das ist ungetestet. Verdikt: lohnt sich bei großen C++-Codebasen.

---

## 2. FiveM / Cfx.re (inkl. GTA V Enhanced)

Kontext: „FiveM for GTA V Enhanced“ ist seit dem 21.07.2026 im Early Access, mit eigenem
Launcher neben FiveM Legacy und neuem OneSync (Quelle: Presse und Hoster-Artikel im
Suchindex, z. B. https://rockstarintel.com/fivem-for-gta-v-enhanced-gets-development-update/).
Natives-Unterschiede zwischen Legacy und Enhanced (gen9) sind bisher nur in alloc8ors
`natives_gen9.json` maschinenlesbar greifbar, siehe 2.1.

### 2.1 Offizielle bzw. primäre Datenquellen für Natives

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| FiveM Natives Reference | https://docs.fivem.net/natives/ (Suchindex) | – | – | Offizielle Native-Referenz (GTA V und CFX). | Kanonische Quelle für Links in unseren Skills. |
| Natives als JSON | https://runtime.fivem.net/doc/natives.json und https://runtime.fivem.net/doc/natives_cfx.json (in mehreren geprüften Repos referenziert) | – | – | Maschinenlesbare Gesamtdumps (ca. 5 MB). Diese Dateien nutzen die meisten Natives-MCPs. | Gut, um ein eigenes Nachschlage-Skript zu bauen. **Nicht** komplett in einen Skill packen, das ist zu groß. |
| citizenfx/natives | https://github.com/citizenfx/natives | **keine LICENSE-Datei** | 2026-08-17 (~600★) | Quell-Repo der GTA-V-Native-Doku hinter docs.fivem.net. Enthält nur GTA-Natives. | Primärquelle. Verlinken, nicht kopieren. |
| citizenfx/fivem (`ext/native-decls`) | https://github.com/citizenfx/fivem/tree/master/ext/native-decls | Rockstar Games Creator Platform License (proprietär) | 2026-09-30 (~4,3k★) | Hauptrepo von FiveM/RedM/FXServer. `ext/native-decls` enthält rund 860 Markdown-Deklarationen der **CFX-eigenen** Natives. | Primärquelle für CFX-Natives. Nur verlinken. |
| citizenfx/fivem-docs | https://github.com/citizenfx/fivem-docs | keine LICENSE-Datei | 2026-10-01 | Quelle von docs.fivem.net (Scripting-Handbuch, fxmanifest, Events, OneSync). | Primärquelle für Konzepte. Nur verlinken. |
| alloc8or/gta5-nativedb-data | https://github.com/alloc8or/gta5-nativedb-data | keine Lizenz („strictly for educational purposes“) | 2026-09-15 (~265★) | `natives.json` und **`natives_gen9.json`** (Enhanced), die Datenbasis von https://alloc8or.re/gta5/nativedb/ | Einzige maschinenlesbare Enhanced-Natives-Quelle, die ich gefunden habe. Nur als Referenz/Lookup nutzen, nicht weiterverteilen. |

### 2.2 Lua Language Server und Typdefinitionen

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| overextended/fivem-lls-addon | https://github.com/overextended/fivem-lls-addon | MIT | 2026-07-26 | LuaLS-Addon „CfxLua“ mit Typen für FiveM/RedM-Natives und Runtime-Globals (CreateThread, Statebags, Vektoren). Einrichtung über `.luarc.json` mit `workspace.userThirdParty`. | **Empfohlen.** Der Standard für FiveM-Lua-IntelliSense. |
| LuaLS/lua-language-server | https://github.com/LuaLS/lua-language-server | MIT | 2026-09-22 | Der Lua-Language-Server selbst (früher „sumneko“). | Voraussetzung für Addon und Plugin. |
| lua-lsp (offizielles Claude-Code-Plugin) | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/lua-lsp | Apache-2.0 | 2026-10-05 | Bindet `lua-language-server` in Claude Code ein, sodass Claude nach jedem Edit Diagnosen bekommt. | **Empfohlen** in Kombination mit fivem-lls-addon. Installation: `/plugin install lua-lsp@claude-plugins-official` |
| overextended/cfxlua-vscode | https://github.com/overextended/cfxlua-vscode | MIT | 2026-04-25 | VS-Code-Extension „CfxLua IntelliSense“, laut README **eingestellt**. | Nicht mehr nutzen, stattdessen fivem-lls-addon. |
| Qbox-project/qbx-lua | https://github.com/Qbox-project/qbx-lua | GPL-3.0 | 2026-10-01 (neu seit 09/2026) | In Rust geschriebener Linter (`qbx-lint`), Formatter und Language-Server speziell für CfxLua. | Vielversprechend, aber sehr jung und GPL. Beobachten. |

### 2.3 Linter

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| GoatG33k/fivem-lua-lint-action | https://github.com/GoatG33k/fivem-lua-lint-action | MIT-artig (LICENSE.md) | 2022-02-08 | GitHub Action, die Luacheck mit FiveM-Globals ausführt. | Veraltet, aber das Prinzip (luacheck plus Cfx-Globals) ist weiter brauchbar. |
| Qbox-project/qbx-lua | siehe 2.2 | GPL-3.0 | 2026-10-01 | `qbx-lint` | Siehe oben. |
| LuaLS-Diagnosen | siehe 2.2 | MIT | – | `lua-language-server --check` als CLI-Diagnose. | In Kombination mit dem Addon der praktischste „Linter“. Ein CI-Einsatz ist ungetestet. |

### 2.4 MCP-Server für FiveM

Alle sind jung (2026) und haben nur wenige Sterne. **Sicherheit:** Viele erlauben
Code-Ausführung auf Server bzw. Client. Nur lokal auf Dev-Servern betreiben, nie auf
Produktion.

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| ziyacivan/fivem-mcp | https://github.com/ziyacivan/fivem-mcp | MIT | 2026-09-04 | Bauen, Starten und Live-Testen eines FXServers über RCON, Client-F8-Konsole (devcon), Fenster-Automation, Screenshots und eine In-Game-Bridge für Natives/Exports/NUI. Getestet gegen den **Legacy**-Client. | Bester Kandidat für „hat es im Spiel funktioniert?“-Schleifen. Enhanced-Support unklar. |
| nimoalr/lavender-mcp-server | https://github.com/nimoalr/lavender-mcp-server | MIT | 2026-08-26 | Läuft als FiveM-Resource (Streamable HTTP, localhost und Bearer-Token). Kann Server inspizieren, Resources verwalten, Konsole lesen und JS/Lua auf Server/Client ausführen. Laut Beschreibung für FiveM, **FiveM for GTA V Enhanced** und RedM. | Interessant wegen expliziter Enhanced-Unterstützung. Erfordert Artifact ≥ 25943. |
| hamchowderr/fivem-kit | https://github.com/hamchowderr/fivem-kit | MIT | 2026-08-11 | Claude-Code-Plugin (Skills, Subagents, Hooks) plus MCP-Server `fivem-mcp` (npx) mit Natives-DB, Framework-APIs (ox/ESX/QBCore/Qbox), Security-Audit und Stack-Erkennung. | Als Plugin-Beispiel gut. Inhaltlich prüfen, bevor man sich darauf verlässt. |
| B7Kompirine/muto-atlas | https://github.com/B7Kompirine/muto-atlas | MIT | 2026-09-13 | Claude-Code-Plugin mit eigenem Marketplace und read-only MCP. Baut 24 Offline-Datenschichten aus der **eigenen** GTA-V-Installation (z. B. ytyp/Asset-Daten). | Kreativer Ansatz („erst Daten prüfen, dann coden“). Vor Nutzung die Skripte prüfen. |
| TMHSDigital/cfx-mcp | https://github.com/TMHSDigital/cfx-mcp | **CC BY-NC-ND 4.0** | 2026-05-24 | Read-only Native-Lookup (Name/Hash) aus runtime.fivem.net. | Lizenz verbietet Bearbeitungen und kommerzielle Nutzung. Nur als Inspiration. |
| mysbryce/5m-mcp | https://github.com/mysbryce/5m-mcp | **PolyForm Noncommercial 1.0** | 2026-05-29 | Resources live bauen, starten und debuggen. | Nicht-kommerzielle Lizenz, für einen RP-Server mit Einnahmen ungeeignet. |

### 2.5 FiveM-Skills

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| matiaspalmac/fivem-security-audit | https://github.com/matiaspalmac/fivem-security-audit | MIT | 2026-09-04 | Claude-Code-Skill für Security-Reviews von Resources (Dupes, Backdoors, Crash-Vektoren, Supply-Chain). Abdeckung: Legacy, Enhanced, ESX/QBCore/Qbox/ox. | Gute Idee für einen eigenen Review-Skill. Inhalt prüfen. |
| matiaspalmac/fivem-resource-builder | https://github.com/matiaspalmac/fivem-resource-builder | MIT | 2026-09-04 | Skill zum „secure by default“-Scaffolding von Resources inkl. React-NUI. | Brauchbar als Vorlage für unseren Scaffolding-Skill. |
| HeyyCzer/fivem-natives-skill | https://github.com/HeyyCzer/fivem-natives-skill | **keine Lizenz** | 2026-03-25 | Natives-Referenz nach Namespace (aus cfxnatives.dev), automatisch aktualisiert. | Zeigt, wie man Natives auf Referenzdateien verteilt (Progressive Disclosure). **Nicht übernehmen.** |
| TMHSDigital/CFX-Developer-Tools | https://github.com/TMHSDigital/CFX-Developer-Tools | **CC BY-NC-ND 4.0** | 2026-10-03 | Cursor-Plugin mit 9 Skills, MCP-Tools, Natives, Events und Templates. | Restriktive Lizenz. Nur ansehen. |

---

## 3. Allgemein: Claude-Skills und Plugins

### 3.1 Offizielle Quellen, Spezifikation und Listen

| Name | URL | Lizenz | Letzte Aktivität | Was es tut | Verdikt |
| :- | :- | :- | :- | :- | :- |
| anthropics/skills | https://github.com/anthropics/skills | Apache-2.0 für die meisten Skills. docx/pdf/pptx/xlsx nur „source-available“ | 2026-10-05 (~180k★) | Offizielle Beispiel-Skills plus `.claude-plugin/marketplace.json`, das Skills über `"source": "./"` und `"skills": [...]` zu Plugins bündelt. | **Formatreferenz Nr. 1.** Struktur übernehmen, Inhalte nur unter Apache-2.0. |
| anthropics/claude-plugins-official | https://github.com/anthropics/claude-plugins-official | Apache-2.0 | 2026-10-05 | Offizieller Marketplace (`claude-plugins-official`, über 300 Plugins), u. a. Epics Unreal-Plugin, `lua-lsp`, `clangd-lsp`, `skill-creator`, `plugin-dev`, `superpowers`. | Standardquelle für Plugins, wird automatisch registriert. |
| anthropics/claude-plugins-community | https://github.com/anthropics/claude-plugins-community | Apache-2.0 | 2026-10-05 | Community-Marketplace `claude-community` (über 2.000 eingereichte Plugins). Kein FiveM-Plugin gefunden. | Zum Stöbern. Plugins sind nicht von Anthropic geprüft. |
| anthropics/claude-code (`plugins/`) | https://github.com/anthropics/claude-code/tree/main/plugins | proprietär (Anthropic Commercial Terms) | 2026-10-06 | Demo-Marketplace `claude-code-plugins` und CHANGELOG. | Nur als Beispiel. CHANGELOG nützlich, um Formatänderungen zu verfolgen. |
| agentskills/agentskills | https://github.com/agentskills/agentskills (Seite: https://agentskills.io) | Apache-2.0 | 2026-08-09 | Offene Agent-Skills-Spezifikation und Validator `skills-ref`. | **Pflichtlektüre.** `skills-ref validate` in die CI aufnehmen. |
| skill-creator (Plugin) | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator | Apache-2.0 | 2026-10-05 | Skills erstellen, verbessern und mit Evals messen (inkl. Trigger-Tests für die Description). | Empfohlen beim Schreiben unserer Skills. |
| obra/superpowers | https://github.com/obra/superpowers | MIT | 2026-09-25 | Bekannte Skill-Sammlung für Workflows (Brainstorming, TDD, systematisches Debugging, Skill-Authoring). Auch im offiziellen Marketplace. | Gutes Vorbild für prozessorientierte Skills. |
| VoltAgent/awesome-agent-skills | https://github.com/VoltAgent/awesome-agent-skills | MIT | 2026-10-06 (~35k★) | Kuratierte Liste mit über 1.000 Skills offizieller Teams und der Community. | Gute Discovery-Liste, sehr aktiv. |
| hesreallyhim/awesome-claude-code | https://github.com/hesreallyhim/awesome-claude-code | CC BY-NC-ND 4.0 | 2026-10-06 (~55k★) | Kuratierte Liste zu Claude Code (Skills, Hooks, Plugins, Tools). | Zum Finden gut. Liste nicht weiterverarbeiten (ND-Lizenz). |
| ComposioHQ/awesome-claude-skills | https://github.com/ComposioHQ/awesome-claude-skills | Apache-2.0 (laut README, keine LICENSE-Datei) | 2026-07-24 (~77k★) | Große Liste plus Sammlung (über 860 SKILL.md), stark auf Composio-Integrationen ausgerichtet. | Masse statt Klasse. Nur gezielt suchen. |
| travisvn/awesome-claude-skills | https://github.com/travisvn/awesome-claude-skills | keine Lizenzangabe gefunden | 2026-04-28 (~15k★) | Kuratierte Skill-Liste. | Seit Monaten wenig Bewegung. Zweitrangig. |

---

### 3.2 Allgemeine Programmier-Sammlungen im Detail

| Name | URL | Lizenz | Letzte Aktivität | Inhalt (relevante Skills) | Verdikt |
| :- | :- | :- | :- | :- | :- |
| obra/superpowers | https://github.com/obra/superpowers (eigener Marketplace: https://github.com/obra/superpowers-marketplace, MIT, 2026-09-08) | MIT | 2026-09-25 (~296k★) | `systematic-debugging`, `test-driven-development`, `writing-plans`, `executing-plans`, `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, `using-git-worktrees`, `writing-skills` u. a. (15 Skills) | **Top.** Skills verweisen aufeinander (`superpowers:…`). Deshalb besser als Plugin installieren als einzeln kopieren. |
| mattpocock/skills | https://github.com/mattpocock/skills | MIT | 2026-10-06 (~278k★) | `tdd`, `diagnosing-bugs`, `code-review`, `grill-me`, `to-spec`, `to-tickets`, `improve-codebase-architecture`, `domain-modeling` u. a. (38 Skills) | Sehr kompakt und praxisnah. Viele Skills sind TypeScript-lastig, die Methodik ist aber übertragbar. |
| Anthropic-Plugins in `claude-plugins-official` | https://github.com/anthropics/claude-plugins-official/tree/main/plugins | Apache-2.0 (je Plugin eine LICENSE) | 2026-10-05 | `code-review`, `pr-review-toolkit` (6 Review-Agents), `feature-dev`, `code-simplifier`, `security-guidance`, `hookify`, `claude-md-management`, `skill-creator`, `plugin-dev`, LSP-Plugins | Offiziell gepflegt, sichere Basis. |
| trailofbits/skills | https://github.com/trailofbits/skills | CC BY-SA 4.0 | 2026-09-28 (~7,4k★) | `modern-cpp`, `c-review`, `differential-review`, `static-analysis` (CodeQL/Semgrep), `property-based-testing`, `mutation-testing`, Fuzzing-Skills (libFuzzer, AFL++, ASan) | Beste C/C++-Skills. ShareAlike-Lizenz beachten. |
| wshobson/agents | https://github.com/wshobson/agents | MIT | 2026-10-04 (~40k★) | ~95 Plugins, u. a. `systems-programming` (Agents `c-pro`, `cpp-pro`), `debugging-toolkit`, `error-debugging`, `tdd-workflows`, `code-refactoring`, `comprehensive-review`, `game-development` (nur Unity/Minecraft) | Breit, aber eher Agent-Personas als Methodik. Selektiv nutzen. |
| Jeffallan/claude-skills | https://github.com/Jeffallan/claude-skills | MIT | 2026-10-03 (~12k★) | 67 Skills, u. a. `cpp-pro`, `game-developer` (Unity/Unreal allgemein), `debugging-wizard`, `code-reviewer`, `test-master`, `legacy-modernizer` | Saubere, spec-konforme Frontmatter (inkl. `license`/`metadata`). Gute Einzelstücke zum Übernehmen. |
| OthmanAdi/planning-with-files | https://github.com/OthmanAdi/planning-with-files | MIT | 2026-10-06 (~27k★) | Planungsdateien auf der Platte (`task_plan.md`, `findings.md`, `progress.md`) plus Hooks | Gut für lange Aufgaben. Ein deutscher Skill (`planning-with-files-de`) ist vorhanden. |
| hyhmrright/brooks-lint | https://github.com/hyhmrright/brooks-lint | MIT | 2026-10-05 (~1,5k★) | `brooks-review`, `brooks-audit`, `brooks-debt`, `brooks-health`, `brooks-sweep` | Gut für Refactoring- und Tech-Debt-Reviews. |
| DietrichGebert/ponytail | https://github.com/DietrichGebert/ponytail | MIT | 2026-10-05 (~157k★) | `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt` | Geschmackssache (radikales YAGNI). |
| Egonex-AI/Understand-Anything | https://github.com/Egonex-AI/Understand-Anything | MIT | 2026-10-06 (~85k★) | Interaktiver Wissensgraph einer Codebasis | Optional zum Einarbeiten in große Codebasen. |
| C++/Lua-spezifisch sonst | – | – | – | Weitere hoch bewertete C++-Skill-Sammlungen habe ich nicht gefunden; Lua-Skills bisher nur für Nischen (Aseprite, REAPER, WezTerm). | Für Lua gilt: LSP (`lua-lsp` + fivem-lls-addon) plus eigene FiveM-Skills. |

---

## 4. Was wir daraus für unser Repo ableiten

- **Nicht nachbauen, was offiziell existiert:** Für die Editor-Steuerung nutzen wir Epics Plugin bzw. Unreal MCP. Unsere UE-Skills decken Projektkonventionen, Build/Cook/Packaging, C++-Stil und UE-5.8-Fallstricke ab.
- **FiveM-Natives nicht in Skills kopieren:** Der Skill erklärt, *wie* man nachschlägt (docs.fivem.net, `runtime.fivem.net/doc/*.json`, `natives_gen9.json` für Enhanced, LuaLS-Typen). Optional gibt es ein kleines Lookup-Skript unter `scripts/`.
- **Lizenzen beachten:** Mehrere FiveM-Projekte sind NC/ND-lizenziert (CC BY-NC-ND, PolyForm NC) oder ganz ohne Lizenz. Daraus nichts übernehmen.
- **Sicherheit:** Editor- und FiveM-MCPs mit Code-Ausführung nur lokal betreiben. Den Modus „skip permissions“ dabei meiden. Vor langen MCP-Sessions committen.
- **Cloud-Sessions (claude.ai/code):** Plugins aus `.claude/settings.json` laden dort nicht (siehe `research/claude-code-format.md`, Abschnitt 4). MCP-Server, die einen laufenden Editor oder Spiel-Client brauchen, funktionieren in der Cloud-VM ohnehin nicht. Reine Doku-MCPs wie Codeturion/unreal-api-mcp schon, sofern sie über die projektweite `.mcp.json` eingebunden sind und das Netzwerk sie erlaubt.
