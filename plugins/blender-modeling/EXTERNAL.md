# Externe Ressourcen: Blender (Modellierung, bpy-Automatisierung, MCP)

Stand: **2026-10-10**. Eigene Bewertung für deinen Einsatz: MLO-Interiors mit Sollumz, GTA-Texturen,
Kleidung für Unreal Engine 5.8, möglichst viel per Skript oder MCP automatisiert.

**So wurde geprüft:**
- GitHub-Repos per `git clone --depth 1` gelesen: LICENSE im Root, letzter Commit, jede in Frage kommende `SKILL.md`.
- Blender-API-Fakten direkt im Blender-Quellcode (`github.com/blender/blender`, Release-Branches 2.80 bis 5.3) nachgesehen.
- `blender.org`, `developer.blender.org`, `docs.blender.org`, `projects.blender.org` und `extensions.blender.org` waren aus der Sandbox gesperrt. Was nur aus Suchergebnissen stammt, ist mit **(Suchindex)** markiert.
- Vendorbar sind nur MIT, Apache-2.0 und CC0 (siehe `research/vendorable.md`). Repos ohne LICENSE: nur lesen, nichts kopieren.

**Was schon in diesem Plugin steckt:** 8 übernommene Skills (Details und Commits in `UPSTREAM.md`) plus der eigene Skill `blender-python-pitfalls`. Sollumz, MLO-Aufbau und GTA-Texturen behandeln die Skills `fivem-mlo-creation`, `fivem-mlo-doors-windows` und `gta-texture-editing`.

---

## 1. Blender-Skills (Rangliste)

| Rang | Skill / Repo | Lizenz | Letzter Commit | Inhalt | Verdikt |
| :- | :- | :- | :- | :- | :- |
| 1 | **scenario-labs/skills**, Familie `skills/dcc/blender/scenario-blender-*` (13 Skills) – https://github.com/scenario-labs/skills | MIT | 2026-10-10 | Aus ~200 Experten-Videos destilliert, jede Aussage mit Quelle oder „verified in 5.2.1“. Je Skill ein getestetes Python-Modul (`bx_*.py`), messbare Gates, Review-Renderings. Dazu `blender-5.2-deltas.md` (was alte Tutorials falsch machen) und `bpy-reliability.md`. | **Übernommen:** `expert`, `hard-surface`, `retopology`, `uv-baking`, `rigging`. **Optional installieren:** `texturing-shading` (PBR, Grunge, Decals), `sculpting`, `geometry-nodes`, `lighting-rendering`: `npx skills add scenario-labs/skills --skill scenario-blender-texturing-shading` |
| 2 | **luckyfried/code-tools**, `skills/blender-*` – https://github.com/luckyfried/code-tools | MIT | 2026-09-30 | Aktuelle API für 5.2 mit Alt→Neu-Tabelle nach Release-Notes, Export nach UE/Unity/Godot/three.js, Prüfschleife über den offiziellen MCP oder headless. | **Übernommen:** `blender-current-api`, `blender-game-export`, `blender-verify`. `blender-animation-rigging` und `blender-compositing-nodes` bei Bedarf. |
| 3 | **majidmanzarpour/blender-game-skills**, `blender-image-to-3d` – https://github.com/majidmanzarpour/blender-game-skills | MIT | 2026-09-23 | Aus Referenzfotos ein Game-Asset bauen, in Phasen mit Silhouetten-Messung, Validierung, Bake, GLB/FBX-Export und Reimport. Bis 5.2 getestet. | **Empfohlen** für Props nach Foto (Möbel, Deko fürs MLO): `npx skills add majidmanzarpour/blender-game-skills --skill blender-image-to-3d`. Nicht kopiert, weil Rang 1/2 die Grundlagen schon abdecken. |
| 4 | **jmhobbs/agent-skills**, `blender-lod-pipeline` – https://github.com/jmhobbs/agent-skills | MIT | 2026-09-10 | LOD-Kette per Decimate, kaputte Texturpfade reparieren, FBX je LOD, PBR-Maps trennen, AO backen. Läuft über einen Blender-MCP. | Nützlich für UE-Props. GTA-LODs macht Sollumz. |
| 5 | **Impertio-Studio/Blender-Bonsai-ifcOpenshell-Sverchok-Claude-Skill-Package**, `skills/blender/*` (26 Skills) – https://github.com/Impertio-Studio/Blender-Bonsai-ifcOpenshell-Sverchok-Claude-Skill-Package | MIT | 2026-03-30 | Sehr ausführliche API-Skills für 3.x bis 5.1, z. B. `blender-errors-context`, `blender-core-versions`. | Gut zum Nachschlagen, aber älter als 5.2 und sehr lang. Die Frontmatter enthält `dependencies` (nicht portabel). Nicht übernommen, weil `blender-current-api` und `blender-python-pitfalls` dasselbe aktueller abdecken. |
| 6 | **devanshutak25/agent-skills**, `blender-python` – https://github.com/devanshutak25/agent-skills | MIT | 2026-03-26 | API-Referenz für 5.0/5.1 mit Routing-Tabelle. | Brauchbar, aber 5.2 fehlt. |
| 7 | **MAX-786/claude-3d-harness** – https://github.com/MAX-786/claude-3d-harness | MIT (Bibliotheken mit eigener Lizenz, siehe dort `THIRD_PARTY.md`) | 2026-09-21 | Plugin mit Registry über 58 Fremd-Skills (RobLe3, Gaius114, kevinbadi, jithinolickal, newo-ether) und einem gepinnten MCP-Server mit SHA-256-Prüfung. Sicherheits-Review der importierten Skripte. Auf Windows 11 getestet. | Interessant für filmische Renderings. Für MLO und Kleidung zu breit. Die Bibliothek `kb` hat upstream keine LICENSE (Lizenz nur per Aussage des Autors). |
| 8 | **RobLe3/cc-blender-skill** – https://github.com/RobLe3/cc-blender-skill | MIT | 2026-05-01 | 30 Skills, auf 5.1.1 validiert, Props und Szenen. | **Vorsicht:** Das FBX-Rezept setzt `bake_space_transform=True` als „critical“. Das FBX-Add-on selbst nennt die Option experimentell und „known to be broken with armatures/animations“. |
| 9 | **arjun988/blender-skills** – https://github.com/arjun988/blender-skills | MIT | 2026-07-10 | 94 Rollen- und Stil-Checklisten, kaum bpy-Code. | Nur als Ideensammlung, z. B. für Seams, Texel-Dichte und UCX-Namen. |
| 10 | ra100/blender-claude-plugin, TerminalSkills/skills (Apache-2.0), afovea/game-dev-skills, TraX22/HydraOps-Skills (Apache-2.0), Mindrally/skills (Apache-2.0), MartinRapcan/blender-claude-skill, ozanzeng/blender-LPM-skill, clawic/skills, dcc-mcp/dcc-mcp-blender (Skills) | MIT oder Apache-2.0 | 2026 | Allgemeine bpy-Anleitungen, teils veraltet. Beispiele: `context.copy()` als Tipp, EEVEE-Kennung nur für 4.2, `bl_info` statt Manifest. | Nicht empfohlen. |
| – | SFKislev/Flue, Skill `blender` – https://github.com/SFKislev/flue | MIT | 2026-09-01 | Shell-Brücke zu bpy ohne MCP. Laut Suchindex der meistinstallierte Blender-Skill (~2 300). Der Skill-Text enthält einen fest verdrahteten Pfad (`C:\Users\fredd\...`). | Nur als Alternative zum MCP. |

**Abgelehnt** (Lizenz): TMHSDigital/Blender-Developer-Tools (CC BY-NC-ND 4.0), LevyBytes/AI-SKILL-blender (AGPL-3.0). Ohne LICENSE: edemaistre/blender-expert-skills (gleicher Inhalt wie Rang 1, dort unter MIT), kevinbadi/blender-skills, Seretos/blender-helper, itgoyo/hermes-skills, remiehneppo/blender-skills, fandhe-ai/agent-reference-skills, ptrthomas/blender-agent, AndreiFlau/blender-mcp-skill.

---

## 2. MCP-Server und Brücken

Alle laufen **lokal**: Das Blender-Add-on öffnet eine TCP-Brücke auf `127.0.0.1:9876`, und der MCP-Server läuft auf deinem Rechner. Der Code von Claude läuft ohne Sandbox in deiner offenen Datei. Deshalb vorher eine Kopie speichern und nur in Projekten ohne sensible Daten arbeiten. Blender Lab empfiehlt laut `blender-verify` eine VM.

| Rang | Server | Lizenz | Status | Einrichtung (3 Zeilen) | Hinweis |
| :- | :- | :- | :- | :- | :- |
| 1 | **Blender Lab, offizieller MCP** (`blender_mcp`) – https://projects.blender.org/lab/blender_mcp, Doku https://www.blender.org/lab/mcp-server/ | GPL-3.0-or-later (laut README von NousResearch/hermes-plugin-blender; die Seite selbst war gesperrt) | v1.0.0 am 27.04.2026, v1.0.3 am 11.09.2026 **(Suchindex)**. Braucht **Blender 5.1+**. In Claude Desktop heißt er Connector „Blender“ (Blender Lab). | 1. Blender 5.2 LTS: *Preferences › Get Extensions › Repositories* → `https://lab.blender.org/` hinzufügen, Add-on „MCP“ installieren, *Allow Online Access* einschalten. 2. In den Add-on-Einstellungen *Start MCP Bridge Server* klicken (*Auto Start* an). 3. `pip install "git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp"`, dann `claude mcp add blender -- blender-mcp` | **Erste Wahl.** Tools: `execute_blender_code` (Rückgabe über die Variable `result`), Szenen- und Objekt-Zusammenfassungen, fehlende Dateien, Screenshots, `search_api_docs`, dazu `_for_cli`-Varianten für Hintergrundprozesse. Achtung: `blender-mcp` auf PyPI ist ein **anderer** Server. |
| 2 | **mcp-for-blender** (ahujasid, früher `blender-mcp`) – https://github.com/ahujasid/mcp-for-blender | MIT | Commit 2026-10-06, Paket 2.1.9, Add-on 1.8, ab Blender 3.0 | 1. uv installieren (offizieller Installer, nicht `pip install uv`). 2. `uvx mcp-for-blender install-addon`, in Blender im N-Panel *BlenderMCP* verbinden. 3. `claude mcp add blender uvx mcp-for-blender` (env `DISABLE_TELEMETRY=true`, `BLENDER_MCP_SAFE_MODE=1`) | Für Blender 4.x oder wenn der offizielle nicht läuft. Standardmäßig wird ein anonymer Nutzungsdatensatz gesendet (Tool-Name, Dauer, Versionen); Inhalte nur nach Opt-in. Poly Haven, Sketchfab, Hyper3D und Hunyuan3D sind externe Dienste. „Not made by Blender.“ |
| 3 | newo-ether/blender-mcp – https://github.com/newo-ether/blender-mcp | MIT (© Siddharth Ahuja, Fork) | Commit 2026-09-21 | per claude-3d-harness (gepinnte Wheel-URL) | Nur über den Harness getestet, nicht einzeln geprüft. |
| 4 | dcc-mcp/dcc-mcp-blender – https://github.com/dcc-mcp/dcc-mcp-blender | MIT | Commit 2026-10-09 | siehe README | Typisierter Adapter mit ~40 Mini-Skills. Nicht im Produktiveinsatz geprüft. |
| – | Headless `blender -b datei.blend --factory-startup --python-exit-code 1 -P skript.py -- args` | – | immer verfügbar | – | Für Batch-Jobs (Export, Validierung, LODs). Ohne Netz, ohne Viewport. Siehe `blender-python-pitfalls` §8. |
| – | Higgsfield Bridge (`bl_*`-Tools), in Claude-Sitzungen mit diesem Connector sichtbar | nicht geprüft | – | – | Herstellerbrücke mit kostenpflichtiger KI-Generierung. Nur nutzen, wenn ohnehin verbunden. Die bpy-Regeln gelten dort genauso. |

**Empfehlung:** Blender **5.2 LTS** plus offizieller MCP für interaktive Arbeit, `blender -b` für Batch-Jobs. Sollumz verlangt mindestens Blender 4.2 und nennt keine Obergrenze. Ob 5.2 im Alltag fehlerfrei läuft, wurde hier nicht getestet; vor jedem Blender-Update die Sollumz-Releases prüfen.

---

## 3. Add-ons für deinen Workflow

| Zweck | Add-on | Lizenz / Preis | Stand | Verdikt |
| :- | :- | :- | :- | :- |
| GTA V / FiveM | **Sollumz** – https://github.com/Sollumz/Sollumz | GPL-3.0-or-later, kostenlos | `main` am 2026-10-10: Version 2.9.0-dev als Extension (`blender_manifest.toml`, `blender_version_min = "4.2.0"`) | Pflicht für YDR/YBN/YTYP. Details in `fivem-mlo-creation`. |
| Retopo (eingebaut) | QuadriFlow (`object.quadriflow_remesh`), Voxel Remesh, Shrinkwrap und Retopology-Overlay, Poly Build | GPL, kostenlos | in 5.2 headless getestet (laut scenario-Skill) | Für statische Props reicht oft QuadriFlow mit anschließendem Aufräumen. Für Kleidung `scenario-blender-retopology` nutzen. |
| Retopo | **RetopoFlow 4** (Orange Turbine) – https://superhivemarket.com/products/retopoflow | GPL-Quellcode. Einzellizenz **85,99 $** auf Superhive, Teams ab ~152 $ **(Suchindex)**. Kostenlose Builds auf GitHub, laut Artikeln 2025 aber nicht aktuell | Version 4.1.9 vom 25.06.2026 „Blender 5.2 compatibility“ **(Suchindex)** | Bestes manuelles Retopo-Werkzeug (Kleidung, Charaktere). Interaktiv, nicht per Skript steuerbar. |
| Retopo (Auto) | **Quad Remesher** (Exoside) – https://exoside.com/quadremesher/ | proprietär. Indie 59,90 $ (nicht kommerziell), Pro 109,90 $ (unbefristet, kommerziell), Abo 15,99 $ pro 3 Monate, je ohne MwSt. **(Suchindex, Preisseite undatiert)** | – | Beste Auto-Quads für Props und gescannte Meshes. Für einen RP-Server mit Einnahmen die **Pro**-Lizenz nehmen. |
| Retopo (Auto) | Instant Meshes – https://github.com/wjakob/instant-meshes | BSD-artig (LICENSE gelesen), kostenlos | letzter Commit 2019, eigenständige Anwendung | Kostenlose Alternative zu Quad Remesher. Export als OBJ, dann Import in Blender. |
| UV (eingebaut) | Minimum Stretch/SLIM-Unwrap (4.3+), `uv.pack_islands` mit Pixel-Margin, `uv.arrange_islands` (5.0+) | GPL, kostenlos | 5.2 | `uv.unwrap` immer mit `method=` aufrufen, denn der Standard ist CONFORMAL. Siehe `scenario-blender-uv-baking`. |
| UV-Packen | **UVPackmaster** (3Coords) – https://superhivemarket.com/products/uvpackmaster | proprietär. Preis nicht gefunden. v3 mit Blender-5-Support seit 14.01.2026, v4 auf Superhive **(Suchindex)** | – | Lohnt sich nur bei vielen Assets bzw. Atlas/Trim-Sheets für MLOs. |
| UV-Werkzeuge | **Zen UV** – https://superhivemarket.com/products/zen-uv | proprietär. Auf einer Sale-Seite 29,25–374,25 $ je nach Lizenzstufe **(Suchindex)** | v5.3.3 **(Suchindex)** | Komfort für Seams, Trim-Sheets und Texel-Dichte. Optional. |
| UV-Werkzeuge | TexTools – https://github.com/franMarz/TexTools-Blender | GPL (LICENSE gelesen), kostenlos | letzter Commit 2024-12-02, also vor Blender 5.0 | Kostenlose Texel-Dichte- und Bake-Helfer. Unter 5.x wahrscheinlich teilweise defekt, erst testen. |
| Eingebaut seit 5.2 | LoopTools-Funktionen Circle/Flatten/Space (`mesh.circularize`, `mesh.flatten`, `mesh.space_edge_loops_evenly`) | GPL | 5.2 | Das LoopTools-Add-on wird dafür nicht mehr gebraucht (Relax fehlt weiterhin). |

---

## Quellen dieser Datei

- D: geklonte Repos aller Skills und Server oben (Commit-Daten in der Tabelle), `NousResearch/hermes-plugin-blender` README (offizieller MCP: GPL-3.0-or-later, Blender 5.1+, Port 9876, gepinnter Commit `2cea8d56`), `psiQAQ/blender_mcp-setup-guide` README, `MAX-786/claude-3d-harness/THIRD_PARTY.md`.
- S: https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026 (Versionen des offiziellen MCP, von einem Konkurrenten), https://www.cgchannel.com/?p=171061 und https://superhivemarket.com/products/retopoflow/versions (RetopoFlow 4), https://exoside.com/quadremesher/quadremesher-buy/ (Quad Remesher), https://superhivemarket.com/products/uvpackmaster/ und https://glukoz.gumroad.com (UVPackmaster), https://agentskill.sh/blog/best-blender-skills-for-ai-agents und https://skillselion.com/skills/sfkislev/flue/blender (Installationszahlen).
