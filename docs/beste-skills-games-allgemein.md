# Die besten Claude-Skills für Spieleentwicklung (engine-übergreifend) und allgemeines Programmieren

Stand: **2026-10-08**. Ergänzt [external-resources.md](external-resources.md) (UE5, FiveM, Methodik-Sammlungen,
dort schon gerankt: obra/superpowers, mattpocock/skills, Anthropic-Plugins, trailofbits, wshobson/agents,
planning-with-files, brooks-lint, ponytail, awesome-gamedev-agent-skills, quodsoler) und
[../plugins/brotato/EXTERNAL.md](../plugins/brotato/EXTERNAL.md) (Godot-4-Skills, Verdikt: nicht für Brotato).
Diese Datei deckt ab: **Spiele** jenseits unserer drei Engines (engine-neutral, Unity, Godot 4, Shader, Netcode,
Game Design) und **allgemeine Programmier-Schwächen** von Claude.

**So wurde geprüft:** Alle GitHub-Repos per `git clone --depth 1` geklont und die `SKILL.md`-Dateien gelesen. Lizenz
aus der `LICENSE`-Datei im Repo. Sterne per Abruf der GitHub-Seite bzw. aus `external-resources.md` (2026-10-06);
„Installs“ stammen von Aggregatoren (skills.sh, Skillselion), sind also nur ein grobes Signal. Die GitHub-API war aus
der Sandbox gesperrt. Bewertet wurde **Inhalt**, nicht Sterne: konkret, versioniert, mit Falsch-vs-Richtig-Code und
Symptom → Ursache → Fix; reine Persona-Prompts („Du bist ein Veteran mit 15 Jahren Erfahrung“) wurden abgewertet.

**Web vs. lokal:** `/plugin install …` und `claude plugin …` wirken nur in lokalen Claude-Code-Sessions (Terminal,
Desktop, VS Code). Cloud-Sessions (claude.ai/code) laden **nur** `.claude/skills/` des Repos. Dort helfen
`npx skills add …` (schreibt in `.claude/skills/`, dann committen) oder unsere Kopie: `scripts/install-skills.sh <Projekt> gamedev-general`.

**Was wir übernommen haben:** 12 Skills als Plugin **`gamedev-general`** (`plugins/gamedev-general/`, Quelle, Lizenz und
Commit in dessen `UPSTREAM.md`). Bewusst **keine Godot-4- und keine Unity-Skills**, weil die Install-Skripte ganze
Plugins kopieren und ein Godot-4-Skill so im Brotato-Projekt (Godot 3) landen würde. Die sechs Spiele-Skills sind
engine-neutrale Methoden, ihre **Code-Beispiele sind aber Godot 4.7 / Unity 6.3**; jede betroffene `SKILL.md` trägt
direkt nach dem Frontmatter eine „Engine note“ mit der Godot-3- bzw. Unreal-Entsprechung. Für die Brotato-Mod gilt
trotzdem: `godot3-gdscript-pitfalls` immer mitinstallieren, und wenn Claude trotz Hinweis Godot-4-API vorschlägt,
`save-systems`/`game-feel` dort weglassen.

---

## A) Spiele: engine-neutral, Unity, Godot 4, Shader, Netcode, Game Design

| Rang | Skill / Sammlung | URL | Lizenz | Sterne / Signal | Letzte Aktivität | Welche Claude-Schwäche es behebt | Installation | Verdikt |
| :- | :- | :- | :- | :- | :- | :- | :- | :- |
| 1 | **gamedev-skills/awesome-gamedev-agent-skills**: 74 Skills + Router; Disziplinen (Performance, Shader, Physik, Saves, Game Feel, Audio, Input, Kamera, KI, ProcGen), Genres, Workflows (Steam, itch) | https://github.com/gamedev-skills/awesome-gamedev-agent-skills | Apache-2.0 + NOTICE | ~1,3k★; skills.sh: `shader-programming` ~600 Installs, `godot-shaders` ~530, `unity-csharp-scripting` ~520 | 2026-09-27 | Claude rät bei Spiel-Problemen („ruckelt“, „Objekte fallen durch Wände“, „Save kaputt“) statt zu messen; mischt GLSL/HLSL; vergisst Fixed Timestep, atomare Saves, Schema-Version, Hit-Stop mit Realzeit | **Im Repo als Plugin `gamedev-general`** (6 Skills: `performance-optimization`, `shader-programming`, `physics-tuning`, `save-systems`, `game-feel`, `steam-publish`). Rest: `npx skills add gamedev-skills/awesome-gamedev-agent-skills` oder `claude plugin marketplace add gamedev-skills/awesome-gamedev-agent-skills` + `claude plugin install router@awesome-gamedev-agent-skills` | **Beste engine-übergreifende Sammlung.** Jeder Skill: Workflow, Falsch-vs-Richtig-Code, Pitfalls als Symptom → Ursache → Fix, Primärquellen, versioniert (Godot 4.7, Unity 6.3 LTS, UE 5.8, `docs/VERSION-SUPPORT.md`). Engine-Skills `godot/*` sind **Godot 4.7: nicht in Brotato**. Die 6 UE-Skills sind flacher als quodsoler. |
| 2 | **Donchitos/Claude-Code-Game-Studios** (CCGS): 74 Skills, 49 Agents, 12 Hooks; Studio-Prozess (GDD, Balance-Check, Perf-Profile, QA, Release) | https://github.com/Donchitos/Claude-Code-Game-Studios | MIT | ~25,9k★ | 2026-10-08 | Fehlende Struktur: kein Design-Review, keine QA, „Report ohne Daten“. Gute Idee: `NOT ASSESSED — NO DATA` statt erfundener Ergebnisse; `test-flakiness` kennt GdUnit4-, Unity- und UE-Automation-Logs; `docs/engine-reference/unreal|godot|unity` listet Breaking Changes und veraltete APIs | Repo klonen und `.claude/` als Projektvorlage übernehmen (kein Plugin, kein `npx`) | **Stark, aber ein Framework.** Skills hängen an `hooks/yaml-helper.sh`, `project.yaml` und Claude-Code-only-Frontmatter (`argument-hint`, `model`, `!`-Injektion); einzeln nicht übernehmbar. Engine-Referenz ist UE 5.7 / Godot 4.6, also leicht hinter uns. Nur für ein neues Projekt als Ganzes. |
| 3 | **Unity-Technologies/unity-agent-plugin** (offiziell): 32 Skills (URP, Shader Graph Custom Node, Physik, UI Toolkit/UGUI, Addressables/Packages, Audio, TMP, Web-Build, Localization, Multiplayer Services) + `unity-cli` + MCP | https://github.com/Unity-Technologies/unity-agent-plugin | **Unity Companion License** (nicht vendorbar) | 393★, offiziell, im Marketplace `claude-plugins-official` | 2026-10-06 | Veraltetes Unity-Wissen (BIRP statt URP, alte Input/UI-APIs); Skills wie `optimize-text-mesh-pro` arbeiten mit Symptom-Triage-Tabellen | `/plugin install unity@claude-plugins-official` (oder `/plugin marketplace add Unity-Technologies/unity-agent-plugin`, dann `/plugin install unity@unity-agent-plugin`) | **Erste Wahl für Unity 6**, nur dort installieren. Beta (0.1.8). Lizenz erlaubt Nutzung nur mit Unity, daher nicht kopieren. |
| 4 | **jame581/GodotPrompter**: 56 Skills, GDScript + C#, Godot 4.3+ mit 4.5–4.7-Zusätzen (`gdscript-patterns`, `multiplayer-sync` mit Interpolation/Prediction, `godot-code-review`, `godot-debugging`, LimboAI/Beehave) | https://github.com/jame581/GodotPrompter | MIT | ~790★ | 2026-10-06 | Godot-4-Fehler: falsche Signal-/Await-Syntax, fehlendes Static Typing, `MultiplayerSynchronizer` falsch konfiguriert | `claude plugins marketplace add jame581/skillsmith` + `claude plugins install godot-prompter@skillsmith` | **Beste Godot-4-Sammlung** (tief, 200–500 Zeilen je Skill, mit 4.7-Migrationshinweisen). Baut auf Superpowers auf. **Nicht für Brotato (Godot 3).** |
| 5 | **thedivergentai/gd-agentic-skills**: 99 Godot-4-Skills, darunter Experten-Skills wie `godot-shaders-basics` (NEVER-Listen mit Quellen, fertige `.gdshader`-Dateien: Instance Uniforms, Alpha Scissor, Reversed-Z) | https://github.com/thedivergentai/gd-agentic-skills | **LGPL-3.0** (nicht vendorbar) | 814★; skills.sh ~4,7k Installs gesamt | 2026-09-09 | Shader-Fehler, die Batching oder Depth-Prepass zerstören; `discard` als „Optimierung“ | `npx skills add thedivergentai/gd-agentic-skills` | Inhaltlich sehr gut, aber LGPL und Godot 4. Zum Lesen für Shader-Fallen. **Nicht für Brotato.** |
| 6 | **MiniMax-AI/skills `shader-dev`**: 36 GLSL-Techniken (Raymarching, SDF, Noise, Fluid, Post-Processing) mit Technique- und Reference-Dateien, ShaderToy/WebGL2 | https://github.com/MiniMax-AI/skills | MIT | ~13,7k★ (Repo) | 2026-04-18 | Claude schreibt kaputtes oder zu teures GLSL für Effekte; kennt SDF-Operatoren und Noise-Varianten nur grob | `npx skills add MiniMax-AI/skills --skill shader-dev` | Gut für eigenständige GLSL-Effekte und Prototypen. Nicht für Engine-Material-Pipelines (UE Material Graph, Godot `canvas_item`). Ergänzt `shader-programming`. |
| 7 | **wshobson/agents `game-development`**: `godot-gdscript-patterns`, `unity-ecs-patterns` (DOTS/Jobs/Burst) + Agents `unity-developer`, `minecraft-bukkit-pro` | https://github.com/wshobson/agents | MIT | ~40k★ (Repo); Skillselion: `godot-gdscript-patterns` ~13,6k Installs (meistinstallierter Gamedev-Skill) | 2026-10-04 | Generische Godot-4-/ECS-Muster | `/plugin marketplace add wshobson/agents` + `/plugin install game-development@claude-code-workflows` | **Populär, aber flach**: 60–80 Zeilen `SKILL.md` plus lange Referenz ohne Pitfall-Struktur. Nur, wenn man Unity DOTS braucht. Godot-Teil ist Godot 4. |
| 8 | **omer-metin/skills-for-antigravity**: u. a. `game-networking` (Rollback, Prediction, Lag Compensation), `shader-programming`, `game-design-core`, `error-handling` | https://github.com/omer-metin/skills-for-antigravity | Apache-2.0 | 162★ | 2026-01-22 | Netcode-Fehler: Client-Position vertrauen, Hit-Detection auf dem Client | `npx skills add omer-metin/skills-for-antigravity --skill game-networking` | **Persona-Prompt** („veteran with 15+ years“) in der `SKILL.md`; Substanz nur in `references/sharp_edges.md` (TypeScript-Beispiele, 800+ Zeilen). Als Lektüre für Netcode-Fallen brauchbar, als Skill nicht empfohlen. |
| 9 | **Jeffallan/claude-skills `game-developer`** | https://github.com/Jeffallan/claude-skills | MIT | ~12k★ | 2026-10-03 | Allgemeine Checkliste (60 FPS, Pooling, LOD) | `/plugin marketplace add jeffallan/claude-skills` + `/plugin install fullstack-dev-skills@fullstack-dev-skills` | Spec-konformes Frontmatter, inhaltlich generisch. Nicht nötig neben Rang 1. |
| 10 | **EpicGames-Plugin, quodsoler, ibrews/ue5-mcp** | siehe [external-resources.md](external-resources.md) | MIT | – | – | UE-spezifisch | siehe dort | Bereits gerankt, hier nur der Vollständigkeit halber. |

**Netcode (Rollback, Client Prediction, Determinismus):** Es gibt **keinen** guten engine-neutralen Skill. Vorhanden sind nur
engine-gebundene (`godot-multiplayer` und `roblox-networking` in Rang 1, `multiplayer-sync`/`multiplayer-basics` in GodotPrompter,
beides Godot 4) und die Persona-Variante von Rang 8. Für UE bleibt `ue5-multiplayer`/`ue-networking-replication`, für Brotato
`brotato-online-multiplayer`. Siehe Lücken unten.

**Steamworks-API im Spiel (Achievements, Cloud, Lobbys):** nur `steam-publish` (SteamPipe, Depots, Store-Review, Release-Checkliste;
übernommen). Ein `steam-sdk`-Skill in `a5c-ai/babysitter` ist ein Platzhalter. Lücke.

**Game Design / Balancing:** CCGS `balance-check` (Rang 2, nur im Framework), `tower-defense/references/balancing.md` in Rang 1,
`game-design-core` bei Rang 8 (Persona). Kein eigenständiger, konkreter Balancing-Skill gefunden. Lücke.

**Audio (FMOD/Wwise):** `audio-design` in Rang 1 (Buses, dB, Ducking, adaptive Musik; engine-neutral, Godot-4-Beispiele) ist gut,
behandelt aber keine Middleware-APIs. Installierbar: `npx skills add https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/main/skills/disciplines/audio-design`.

---

## B) Allgemeines Coding: Claude-Schwächen und die besten Gegenmittel

| Rang | Skill / Sammlung | URL | Lizenz | Sterne / Signal | Letzte Aktivität | Welche Claude-Schwäche es behebt | Installation | Verdikt |
| :- | :- | :- | :- | :- | :- | :- | :- | :- |
| 1 | **mattpocock/skills `writing-for-agents`** (+ `SKILL-MECHANICS.md`) | https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents | MIT | ~278k★ (Repo) | 2026-10-08 | Aufgeblähte, vage `CLAUDE.md`/Skills: erklärt Context Pointer, Progressive Disclosure, Completion Criteria, „Leading Words“, Negations-Falle („don't think of an elephant“) | **Im Repo (`gamedev-general`)**; sonst `/plugin install mattpocock-skills@claude-plugins-official` | **Bester Skill zu Context Engineering**, den ich gefunden habe. Kurz (81 Zeilen), jede Regel begründet. |
| 2 | **mattpocock/skills `tdd`** (+ `tests.md`, `mocking.md`) und **`codebase-design`** (+ `DEEPENING.md`, `DESIGN-IT-TWICE.md`) | https://github.com/mattpocock/skills/tree/main/skills/engineering | MIT | ~278k★ | 2026-10-08 | Tests gegen Interna, tautologische Asserts, „alle Tests zuerst, dann Code“; flache Module, Seam an der falschen Stelle, Mocks überall | **Im Repo (`gamedev-general`)** | `tdd` zwingt zu vorher vereinbarten Seams und vertikalen Slices; `codebase-design` liefert das Vokabular (Deep Module, Seam, Adapter) für sichere Refactorings. Beispiele TypeScript, Methode übertragbar auf C++/Lua/GDScript. |
| 3 | **mattpocock/skills `code-review`** | https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review | MIT | ~278k★ | 2026-10-08 | Reviews, die Stil und Spec vermischen; Scope Creep unbemerkt; keine Smell-Checkliste | **Im Repo (`gamedev-general`)**, Tracker-Zeile angepasst | Zwei-Achsen-Review (Standards vs. Spec) in parallelen Sub-Agents, Fowler-Smell-Baseline. Braucht git + Sub-Agents (lokal am besten). Alternative zum Installieren: `/plugin install code-review@claude-plugins-official`. |
| 4 | **mattpocock/skills `grilling`** (Alias `grill-me`) | https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling | MIT | ~278k★ | 2026-10-08 | Claude baut los, bevor Anforderungen klar sind; fragt nach Fakten, die es selbst nachschlagen könnte | **Im Repo (`gamedev-general`)** | Design-Tree in Runden, Empfehlung pro Frage, Fakten sucht Claude selbst. Vor jedem größeren Feature. |
| 5 | **Anthropic `claude-md-management`** (Skill `claude-md-improver`) | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management | Apache-2.0 | offizieller Marketplace | 2026-10-08 | Veraltete oder lückenhafte `CLAUDE.md` (Befehle, Architektur, Gotchas fehlen) | `/plugin install claude-md-management@claude-plugins-official` | Audit mit Bewertungsraster, Report vor Änderung. Nicht übernommen: Name enthält „claude“ (im Skill-Namen verboten) und Frontmatter-Key `tools`. Ergänzt Rang 1. |
| 6 | **fvadicamo/dev-agent-skills `git-commit`** (+ `github-pr-review`, `github-pr-creation`, `decision-records`) | https://github.com/fvadicamo/dev-agent-skills | MIT | 72★ | 2026-09-11 | Generische Commit-Messages („update code“), kein Scope, Vergangenheitsform, mehrere Themen in einem Commit | **`git-commit` im Repo (`gamedev-general`)**; Rest: `npx skills add fvadicamo/dev-agent-skills --skill github-pr-review` | Kompakt (56 Zeilen + 300 Zeilen Gut/Schlecht-Beispiele), Conventional Commits, liest Konventionen aus `CLAUDE.md`. Kleine Nutzerbasis, Inhalt solide. |
| 7 | **Anthropic `commit-commands`** (`/commit`, `/commit-push-pr`, `/clean_gone`) | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands | Apache-2.0 | offizieller Marketplace | 2026-10-08 | Commit/Push/PR-Routine | `/plugin install commit-commands@claude-plugins-official` | Commands, keine Skills; nur lokal. Gut mit Rang 6 kombinierbar. |
| 8 | **obra/superpowers `finishing-a-development-branch`, `using-git-worktrees`, `requesting-code-review`** | https://github.com/obra/superpowers | MIT | ~296k★ | 2026-09-25 | Branch „fertig“ ohne grüne Tests, kein Merge-/Cleanup-Plan; parallele Arbeit im selben Tree | `/plugin install superpowers@claude-plugins-official` | Gut, aber die Skills verweisen aufeinander (`superpowers:…`); besser als Plugin als einzeln kopiert. |
| 9 | **Anthropic `security-guidance`** (Hooks, Diff-Review) und **`claude-security`** (tiefer Scan mit Verifikations-Panel) | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance | security-guidance: Apache-2.0; claude-security: **proprietär** („All rights reserved“, nur Nutzung) | offizieller Marketplace | 2026-10-08 | Injection, Secrets, SSRF, unsichere Deserialisierung in Claude-generiertem Code | `/plugin install security-guidance@claude-plugins-official`; `/plugin install claude-security@claude-plugins-official` | Ergänzt trailofbits (C/C++). Nur installieren, nicht kopieren. Für FiveM bleibt `fivem-security` unsere Hauptquelle. |
| 10 | **Jeffallan/claude-skills `security-reviewer`, `code-reviewer`, `test-master`, `debugging-wizard`, `legacy-modernizer`** | https://github.com/Jeffallan/claude-skills | MIT | ~12k★ | 2026-10-03 | Fehlende Review-/Audit-Struktur; Legacy-Migration ohne Characterization Tests | `/plugin marketplace add jeffallan/claude-skills` + `/plugin install fullstack-dev-skills@fullstack-dev-skills` (67 Skills auf einmal) | Spec-konform, saubere Workflows mit Referenz-Tabellen, aber Web-Stack-lastig (Semgrep, npm audit, Jest). Brauchbarer Ersatz, wenn man die Anthropic-Plugins nicht will. |
| 11 | **patricio0312rev/skills `flaky-test-detective`** (155 Skills, u. a. `structured-logging-standardizer`, `observability-setup`, `error-handling-standardizer`) | https://github.com/patricio0312rev/skills | MIT | 62★ | 2026-01-11 | Flaky Tests: Timing, geteilter Zustand, Zufall, Netz | `npx skills add patricio0312rev/skills --skill flaky-test-detective` | Ursachen-Katalog ok, aber komplett TypeScript/React/Jest, dazu fragwürdige Regex-„Auto-Fixes“. Für UE Automation Tests oder GUT/Godot-Tests nur die Checkliste nutzen. |
| 12 | **openai/skills `security-best-practices`, `security-threat-model`** | https://github.com/openai/skills | Apache-2.0 (je Skill `LICENSE.txt`) | offizielle OpenAI-Skills | 2026-06-23 | Sprachspezifische Security-Reviews | `npx skills add openai/skills --skill security-best-practices` | Nur Python, JavaScript/TypeScript, Go. Für C++/Lua/GDScript ohne Nutzen. |
| 13 | **trailofbits/skills, brooks-lint, planning-with-files, ponytail** | siehe [external-resources.md](external-resources.md) | CC BY-SA / MIT | – | – | – | siehe dort | Bereits gerankt. |

---

## Bewusst nicht aufgenommen

| Was | Grund |
| :- | :- |
| Godot-4-Skills in `gamedev-general` (`godot-gdscript`, `godot-multiplayer` aus Rang A1; GodotPrompter; gd-agentic-skills) | Brotato läuft auf Godot 3. `scripts/install-skills.*` kopieren ganze Plugins, ein Godot-4-Skill würde im Brotato-Projekt landen und Claude zu `@export`/`await`/`FileAccess` verleiten. Für ein künftiges Godot-4-Projekt: GodotPrompter installieren (A4). |
| Unity-Skills in `gamedev-general` | Kein Unity-Projekt. Unitys offizielles Plugin (A3) ist besser und darf wegen Companion License ohnehin nicht kopiert werden. |
| thedivergentai/gd-agentic-skills | LGPL-3.0, laut `research/vendorable.md` nicht vendorbar (nur MIT/Apache-2.0/CC0). |
| Donchitos/Claude-Code-Game-Studios (einzelne Skills) | MIT, aber jede `SKILL.md` ruft `hooks/yaml-helper.sh` auf, liest `project.yaml` und nutzt nicht-portable Frontmatter-Keys (`argument-hint`, `user-invocable`, `model`). Einzeln herausgelöst funktionieren sie nicht. Als komplette Projektvorlage für ein neues Spiel brauchbar. |
| omer-metin/skills-for-antigravity | `SKILL.md` ist ein Persona-Prompt ohne Inhalt; Substanz nur in TypeScript-lastigen Referenzen. Zum Lesen ja, als Skill nein. |
| wshobson `godot-gdscript-patterns`, `unity-ecs-patterns` | Meistinstalliert, aber generisch (Konzept-Listen, kaum Pitfalls). Godot 4. |
| awesome-gamedev `router` | Routet zwischen allen 74 Skills; mit 6 kopierten Skills nutzlos. |
| awesome-gamedev `procedural-gen`, `audio-design`, `ai-behavior-trees-utility-ai`, `input-systems`, `camera-systems` | Gut, aber für unsere Projekte zweitrangig bzw. durch eigene Skills (`ue5-npc-ai`, `brotato-online-multiplayer` für Seed-Sync) abgedeckt. Einzeln installierbar: `npx skills add https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/main/skills/disciplines/<skill>`. |
| Anthropic `claude-md-improver`, `claude-security`, `code-modernization` | Skill-Name mit „claude“ bzw. proprietäre Lizenz bzw. großes Hook-/Agent-Plugin. Installieren statt kopieren. |
| openai `security-best-practices` | Nur Python/JS/Go. |
| mattpocock `grill-me`, `grill-with-docs`, `wayfinder`, `research` | `grill-me` ist nur ein Alias auf `grilling` (mit nicht-portablem `disable-model-invocation`); `wayfinder`/`research` brauchen Issue-Tracker bzw. Hintergrund-Agents aus `/setup-matt-pocock-skills`. |
| Aggregator-Skills ohne auffindbares GitHub-Repo („strict-api“, „check-the-docs“, „async-concurrency-correctness“ auf claudskills.com, `majiayu000/claude-skill-registry`) | Herkunft und Lizenz nicht prüfbar; Registry-Massenware. |
| garrytan `review`/`investigate`/`cso` (officialskills.sh) | Repo aus der Sandbox nicht klonbar, Inhalt und Lizenz **ungeprüft**. |
| github/awesome-copilot `dotnet-timezone`, mjunaidca `datetime-timezone`, flutter `handling-concurrency`, eduardo-sl `go-agent-skills` | Technologiegebunden (.NET, Web, Dart, Go), für UE-C++/Lua/GDScript nicht übertragbar. |

---

## Bekannte Schwächen ohne guten Skill (Lücken, lohnen sich selbst zu schreiben)

| Schwäche | Was es gibt | Was fehlt |
| :- | :- | :- |
| **Erfundene APIs / Pakete; Doku-Abgleich vor dem Coden** | mattpocock `research` (12 Zeilen, Hintergrund-Agent); MCPs: Codeturion/unreal-api-mcp (UE), Context7 (Web-Libs), unsere FiveM-Natives-Anleitung | Ein kurzer Skill „erst Header/Natives-Dump/Godot-Klassenreferenz prüfen, dann schreiben; Signatur zitieren“ für UE 5.8 (`Engine/Source`), FiveM (`natives.json`/`natives_gen9.json`), Godot 3 (`doc/classes`). Höchste Priorität. |
| **Netcode engine-neutral**: Rollback, Client Prediction + Reconciliation, Lockstep, Determinismus, Seed-Sync | Godot-4-Skills, omer-metin-Referenzen (Persona, TS) | Engine-neutraler Skill mit Entscheidungsbaum (Rollback vs. Server-Authority vs. Lockstep), Desync-Debugging (Hash pro Tick, Replay), Float-Determinismus. Für Billard-Sync und Brotato-Koop direkt nutzbar. |
| **Gleitkomma / Determinismus** | Nur Randnotizen (physics-tuning, procedural-gen: Seeds) | `==` auf Floats, Akkumulationsfehler, FMA/Compiler-Flags, Fixed-Point für Lockstep, `float` vs. `double` in UE, Godot-`real_t`. |
| **Nebenläufigkeit / Race Conditions** in C++ (UE Game Thread vs. Render/Async), Lua-Threads (FiveM `CreateThread`, `Wait`), GDScript-Threads | quodsoler `ue-async-threading` (UE-spezifisch); Rest nur Go/Swift/Dart | Engine-übergreifender Skill: Game-Thread-Regeln, `AsyncTask`/`TGraphTask`, FiveM-Scheduler-Fallen (Event-Reihenfolge, `Citizen.Await`), Godot `Thread`/`Mutex`. |
| **Fehlerbehandlung** in C++ ohne Exceptions (UE), Lua `pcall`/Fehler-Objekte, GDScript ohne Exceptions | omer-metin `error-handling` (TS-Persona) | Sprachspezifische Falsch-vs-Richtig-Muster: `check()`/`ensure()`, `TOptional`/`TValueOrError`, `pcall` + Logging in FiveM, `push_error`/Rückgabewerte in GDScript 3. |
| **Datum/Zeit/Zeitzonen** | Nur .NET/Web-Skills | Spielrelevant: Serverzeit vs. Clientzeit (FiveM `os.time` auf Server, `GetGameTimer`), UTC in Savegames/Leaderboards, Sommerzeit. Niedrige Priorität. |
| **Logging / Observability für Spiele** | patricio `structured-logging-standardizer` (Backend), Jeffallan `monitoring-expert` (Web) | UE `UE_LOG`-Kategorien/Verbosity, `Saved/Logs`, Unreal Insights-Traces; FiveM `print`-Disziplin, `resmon`, txAdmin-Logs; Godot `print_debug`, CrashReporter. Teilweise in unseren eigenen Skills, aber kein Querschnitts-Skill. |
| **Große fremde Codebasen lesen** | Egonex-AI/Understand-Anything (Tool), mattpocock `wayfinder` (Planung) | Skill: Einstiegspunkte finden (`*.uproject`, `fxmanifest.lua`, `project.godot`), Abhängigkeitsgraph skizzieren, erst lesen, dann ändern. |
| **Performance-Profiling allgemein** (außerhalb von Spielen) | `performance-optimization` (Spiele, übernommen), omer-metin `performance-hunter` (Persona) | Für Server-Lua (FiveM) und Build-Zeiten (UBT) ein kurzer „erst messen“-Skill. Teilweise in `fivem-performance-debugging`. |
| **Steamworks-API im Spiel** | `steam-publish` (nur Veröffentlichung) | Achievements, Stats, Cloud Saves, Lobbys/P2P (`ISteamNetworkingMessages`), Overlay; GodotSteam (Godot 3 und 4), UE OnlineSubsystemSteam. Für Billard und Brotato-Koop relevant. |
| **Game Balancing / Ökonomie** | CCGS `balance-check` (nur im Framework) | Eigenständiger Skill: Spreadsheets/Formeln, Progressionskurven, degenerierte Strategien, Simulation statt Bauchgefühl. |
| **FMOD / Wwise** | `audio-design` (Buses, Ducking, adaptive Musik, engine-neutral) | Middleware-APIs, Bank-Loading, Parameter/RTPC, Memory. |

Für die Lücken gilt die Hausregel aus `CLAUDE.md`: nur schreiben, was Claude falsch macht (Fallen, Falsch-vs-Richtig,
Fehlermeldung → Ursache → Fix), versionsspezifisch markieren, Quellen in `references/sources.md`.
