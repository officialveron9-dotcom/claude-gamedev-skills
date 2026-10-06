# Welche externen Skills dürfen wir ins private Repo kopieren („vendoren“)?

Stand: **2026-10-06**. Lizenzen und Commits wurden per `git clone --depth 1` direkt aus den
Repos gelesen: LICENSE-Datei im Root und, wo vorhanden, die LICENSE je Skill bzw. Plugin.
**Keine Rechtsberatung.** Das hier ist eine technische Einschätzung der gängigen Lizenzbedingungen.

Zugehörige Übersicht mit Installationsbefehlen: `docs/external-resources.md` („Top-Empfehlungen“).

---

## 1. Grundregeln je Lizenz

| Lizenz | Kopieren ins private Repo? | Pflichten |
| :- | :- | :- |
| **MIT** | Ja | Copyright-Zeile und MIT-Lizenztext mitkopieren (z. B. `LICENSE` im Skill-Ordner). Änderungen sind erlaubt. |
| **Apache-2.0** | Ja | Lizenztext beilegen, eine vorhandene `NOTICE`/`THIRD_PARTY_NOTICES` übernehmen, **geänderte Dateien als geändert kennzeichnen** (§4b). Für Markennamen gibt es kein Recht. |
| **CC BY-SA 4.0** | Ja, mit Auflage | Namensnennung, Link zur Lizenz, Änderungen angeben. **ShareAlike:** Wird die Bearbeitung je weitergegeben (auch an Dritte oder als öffentliches Repo), muss sie wieder unter CC BY-SA 4.0 stehen. Solche Skills daher in einem eigenen Unterordner mit eigener Lizenzdatei halten. |
| **Keine Lizenz** | **Nein** | Ohne Lizenz gilt das volle Urheberrecht. Nur lesen und verlinken. |
| **CC BY-NC-ND**, **PolyForm Noncommercial** | **Nein** | ND verbietet die Weitergabe von Bearbeitungen, NC jede kommerzielle Nutzung (ein RP-Server mit Einnahmen kann darunter fallen). |
| **Proprietär / „source-available“** | **Nein** | Betrifft z. B. die Anthropic-Skills `docx`, `pdf`, `pptx`, `xlsx`, `anthropics/claude-code` und `citizenfx/fivem` (Rockstar Creator Platform License). |

## 2. Empfohlene Ablage für übernommene Skills

```
plugins/<unser-plugin>/skills/<skill-name>/
├── SKILL.md            # ggf. angepasst; Frontmatter: name, description, license, metadata
├── LICENSE             # Original-Lizenztext (MIT/Apache/CC BY-SA) inkl. Copyright-Zeile
├── UPSTREAM.md         # Quelle, Commit, Lizenz, unsere Änderungen (s. Vorlage)
└── references/ ...     # nur mitkopieren, was der Skill wirklich referenziert
```

Ergänzung in der Frontmatter. Das Feld `metadata` ist spec-konform und auf claude.ai erlaubt, die Werte müssen Strings sein:

```yaml
license: MIT (see LICENSE; upstream obra/superpowers)
metadata:
  upstream: "https://github.com/obra/superpowers/tree/8ca22dba9a94/skills/verification-before-completion"
  upstream-license: "MIT"
  modified: "true"
```

Vorlage für `UPSTREAM.md`: Quelle (URL), Commit-SHA, Lizenz, Copyright-Inhaber, Datum der
Übernahme und eine Liste unserer Änderungen. Bei Apache-2.0 zusätzlich je geänderter Datei ein
Hinweis „Modified by <Name>, <Datum>“.

Hinweis: Viele Upstream-Skills nutzen Claude-Code-only-Frontmatter wie `argument-hint`,
`arguments`, `effort` oder `disable-model-invocation`. Für einen claude.ai-Upload müssen diese
Felder entfernt werden (siehe `research/claude-code-format.md`, Abschnitt 1.3).

---

## 3. Lizenz-Übersicht der geprüften Repos

| Repo | Lizenz (geprüft) | Commit | Vendorbar? |
| :- | :- | :- | :- |
| obra/superpowers | MIT (© 2025 Jesse Vincent) | `8ca22dba9a94` | **Ja** |
| mattpocock/skills | MIT (© 2026 Matt Pocock) | `6fd947921b93` | **Ja** |
| anthropics/claude-plugins-official, Anthropic-eigene Plugins unter `plugins/` | Apache-2.0 (eine LICENSE je Plugin) | `d4226d062928` | **Ja.** Fremd-Plugins dort haben eigene Lizenzen. |
| anthropics/skills | Apache-2.0 je Skill (`LICENSE.txt`), plus `THIRD_PARTY_NOTICES.md` | `683bc88e56f3` | **Ja** außer `docx`/`pdf`/`pptx`/`xlsx` (proprietär) |
| trailofbits/skills | **CC BY-SA 4.0** | `82fe82262526` | **Bedingt** (ShareAlike, separat halten) |
| Jeffallan/claude-skills | MIT | `1be15d8064f8` | **Ja** |
| wshobson/agents | MIT (© 2024 Seth Hobson) | `46891e7e60da` | **Ja** |
| quodsoler/unreal-engine-skills | MIT (© 2025 quodsoler) | `f3742d7b6886` | **Ja** |
| EpicGames/unreal-engine-skills-for-claude-code-plugin | MIT (© 2026 Epic Games) | `a6aa73ada02a` | Ja, aber **besser installieren** (wird von Epic gepflegt und hängt an der Engine-Version) |
| gamedev-skills/awesome-gamedev-agent-skills | Apache-2.0 + `NOTICE` | `d4b0e35550c5` | **Ja** (NOTICE übernehmen) |
| ABostrom/ushell-skill | MIT | `2a527cbaf8c5` | **Ja** |
| matiaspalmac/fivem-security-audit | MIT | `193249ee40c7` | **Ja** |
| matiaspalmac/fivem-resource-builder | MIT | `d34ea3075362` | **Ja** |
| hyhmrright/brooks-lint | MIT | `b6ef8a19df6e` | **Ja** |
| OthmanAdi/planning-with-files | MIT | (nicht gepinnt) | Ja, aber hook-basiert, daher besser installieren |
| DietrichGebert/ponytail | MIT | (nicht gepinnt) | Ja (Geschmackssache) |
| hamchowderr/fivem-kit, B7Kompirine/muto-atlas | MIT | (nicht gepinnt) | Ja, inhaltlich aber erst prüfen |
| ibrews/ue5-mcp | MIT laut README, **keine LICENSE-Datei** | `8e3aed4beb16` | Grauzone. Vor dem Kopieren beim Autor eine LICENSE-Datei anfragen. |
| HeyyCzer/fivem-natives-skill, Johan-p/unreal-claude-template, Sophriel/Claude-Code-Skill-for-Unreal-Engine | keine Lizenz | – | **Nein** |
| TMHSDigital/CFX-Developer-Tools, TMHSDigital/cfx-mcp, hesreallyhim/awesome-claude-code | CC BY-NC-ND 4.0 | – | **Nein** |
| mysbryce/5m-mcp | PolyForm Noncommercial 1.0 | – | **Nein** |
| citizenfx/natives, citizenfx/fivem-docs, alloc8or/gta5-nativedb-data | keine LICENSE-Datei bzw. „educational only“ | – | **Nein.** Nur nachschlagen und verlinken, keine Natives-Dumps ins Repo. |
| citizenfx/fivem | Rockstar Games Creator Platform License (proprietär) | – | **Nein** |

---

## 4. Konkrete Skills, deren Übernahme sich lohnt

Auswahlkriterien: hilft bei UE5-C++ und FiveM-Lua, ist nicht schon durch ein offizielles
Plugin abgedeckt, das wir ohnehin installieren, ist eigenständig (wenige Querverweise) und
passt in unsere Skill-Größe (`SKILL.md` unter 500 Zeilen).

### 4.1 Allgemeines Programmieren

| Skill | Quelle (Pfad @ Commit) | Lizenz | Größe | Warum übernehmen | Nötige Anpassung |
| :- | :- | :- | :- | :- | :- |
| `verification-before-completion` | obra/superpowers `skills/verification-before-completion` @ `8ca22dba9a94` | MIT | 120 Zeilen, 1 Datei | Zwingt dazu, vor „fertig“ wirklich zu bauen und zu testen. Besonders wertvoll bei UE (kompiliert es?) und FiveM (startet die Resource?). | Prüfbefehle für UBT/UAT bzw. `refresh; ensure <res>` und txAdmin-Logs ergänzen. |
| `systematic-debugging` | obra/superpowers `skills/systematic-debugging` @ `8ca22dba9a94` | MIT | 283 Zeilen + 10 Dateien | Bewährte Debugging-Methodik (Root Cause vor Fix). | 2 Verweise `superpowers:…` umschreiben. Die TS-Beispiel-Datei und die `test-pressure-*.md` weglassen. Abschnitte für UE-Crashlogs/Callstacks und FiveM-F8/Serverkonsole ergänzen. |
| `writing-plans` | obra/superpowers `skills/writing-plans` @ `8ca22dba9a94` | MIT | 204 Zeilen | Saubere Implementierungspläne vor großen Features. | 4 Verweise `superpowers:…` entfernen bzw. ersetzen. |
| `grill-me` | mattpocock/skills `skills/productivity/grill-me` @ `6fd947921b93` | MIT | 7 Zeilen | Winziger, sehr effektiver Skill: Claude fragt einen Plan gründlich durch. | Kaum Anpassung nötig. `disable-model-invocation` entfernen, falls er auf claude.ai hochgeladen werden soll. |
| `diagnosing-bugs` | mattpocock/skills `skills/engineering/diagnosing-bugs` @ `6fd947921b93` | MIT | 138 Zeilen + Skript-Template | Kompakte Alternative zu `systematic-debugging`, mit Perf-Regressionen. | Nur **eins** von beiden übernehmen. `agents/openai.yaml` weglassen. |
| `tdd` | mattpocock/skills `skills/engineering/tdd` @ `6fd947921b93` | MIT | 38 Zeilen + `tests.md`, `mocking.md` | Kurzer Red-Green-Refactor-Leitfaden. | Beispiele sind TypeScript. Auf UE Automation Tests (`IMPLEMENT_SIMPLE_AUTOMATION_TEST`) bzw. Lua-Tests umschreiben, dabei ggf. quodsoler `ue-testing-debugging` einbeziehen. |
| `brooks-review` | hyhmrright/brooks-lint `skills/brooks-review` @ `b6ef8a19df6e` | MIT | 40 Zeilen + Dateien in `skills/_shared/` (4 Verweise) | Review mit Begründung aus Klassikern, gut für Refactoring-Entscheidungen. | Hängt an `skills/_shared/`. Entweder mitnehmen oder lieber als Plugin installieren. |

**Nicht kopieren, sondern installieren:** Superpowers als Ganzes (die Skills verweisen
aufeinander), Anthropics `code-review`, `pr-review-toolkit`, `feature-dev` und `skill-creator`
(gepflegt, Apache-2.0, Updates kommen automatisch) sowie `planning-with-files` (hook-basiert).

### 4.2 C++ / Unreal Engine

| Skill | Quelle | Lizenz | Größe | Warum übernehmen | Nötige Anpassung |
| :- | :- | :- | :- | :- | :- |
| `ue-project-context` | quodsoler/unreal-engine-skills `skills/ue-project-context` @ `f3742d7b6886` | MIT | 290 Zeilen | Basis-Skill, der Module, Plattformen und Konventionen des Projekts erfasst. Die anderen quodsoler-Skills lesen dessen Ausgabe. | An unser Projekt anpassen oder durch eine projektspezifische `CLAUDE.md` ersetzen. |
| `ue-cpp-foundations` | quodsoler `skills/ue-cpp-foundations` | MIT | 499 Zeilen + 3 Dateien | UCLASS/UPROPERTY, TObjectPtr, GC und Reflection, gegen UE 5.8 geprüft. Der wichtigste UE-Skill. | Liegt knapp an der 500-Zeilen-Grenze. Ggf. nach `references/` auslagern und um unsere Namenskonventionen ergänzen. |
| `ue-module-build-system` | quodsoler `skills/ue-module-build-system` | MIT | 481 Zeilen | Build.cs, Target.cs, Module und Plugins, die häufigste Fehlerquelle beim Kompilieren. | Unsere Targets und Plattformen eintragen. |
| `ue-networking-replication` | quodsoler `skills/ue-networking-replication` | MIT | 486 Zeilen | Replikation und RPCs, nur bei Multiplayer relevant. | Nur bei Bedarf übernehmen. |
| `ue-testing-debugging` | quodsoler `skills/ue-testing-debugging` | MIT | 498 Zeilen | Automation Tests, Logging, Debug-Tools. Ergänzt den TDD-Skill. | Unsere Testkommandos ergänzen. |
| `ue-gameplay-abilities`, `ue-blueprint-cpp-interop`, `ue-async-threading` | quodsoler | MIT | jeweils 440–500 Zeilen | Nur übernehmen, wenn das Projekt GAS, viel BP-C++-Interop oder Threading nutzt. | Auswahl nach Bedarf. |
| `ushell` | ABostrom/ushell-skill `skills/ushell` @ `2a527cbaf8c5` | MIT | 187 Zeilen + 9 Dateien | Build, Cook, Stage, Package über Epics `ushell` (UAT/BuildGraph). | Nur wenn wir `ushell` nutzen. Pfade anpassen. |
| `modern-cpp` | trailofbits/skills `plugins/modern-cpp/skills/modern-cpp` @ `82fe82262526` | **CC BY-SA 4.0** | 187 Zeilen + 6 Referenzen | Moderne C++20/23-Idiome und Anti-Patterns. | **UE-Konflikt:** UE nutzt TArray/TMap/TUniquePtr statt STL, keine Exceptions, kein RTTI usw. Lieber eine eigene „UE-C++-Stil“-Notiz schreiben und den Skill als **Plugin installieren** statt kopieren. Wenn doch kopiert wird: eigener Ordner mit CC-BY-SA-Lizenz. |
| `c-review` | trailofbits/skills `plugins/c-review/skills/c-review` @ `82fe82262526` | **CC BY-SA 4.0** | 203 Zeilen | Security-Review für C/C++. | Nutzt `allowed-tools: Workflow …`, ist also Claude-Code-spezifisch. Besser installieren als kopieren. |
| `cpp-pro` | Jeffallan/claude-skills `skills/cpp-pro` @ `1be15d8064f8` | MIT | 120 Zeilen + 5 Referenzen | Allgemeiner Modern-C++-Experte mit spec-konformer Frontmatter (`license`, `metadata`). Leicht anzupassen. | Wie oben auf UE-Besonderheiten hinweisen. Konkurriert mit `modern-cpp`, nur eins von beiden nehmen. Wegen MIT ist `cpp-pro` der bessere Kandidat zum Kopieren. |

**Nicht kopieren:** Epics `unreal-mcp`-Skill. Er ist an die MCP-Version gekoppelt und kommt
mit dem Plugin.

### 4.3 FiveM / Lua

| Skill | Quelle | Lizenz | Größe | Warum übernehmen | Nötige Anpassung |
| :- | :- | :- | :- | :- | :- |
| `fivem-security-audit` | matiaspalmac/fivem-security-audit (Repo-Root `SKILL.md` + `checks/`) @ `193249ee40c7` | MIT | 338 Zeilen + ~25 Check-Dateien | Audit auf Backdoors, Dupes, Event-Exploits, NUI-Lücken und Crash-Vektoren. Deckt Legacy und Enhanced sowie ESX/QBCore/Qbox/ox ab. | Frontmatter enthält Claude-Code-only-Felder (`argument-hint`, `arguments`, `effort`). Vor einem claude.ai-Upload entfernen. Auf unser Framework zuschneiden. Checks gegen docs.fivem.net gegenprüfen. |
| `fivem-resource-builder` | matiaspalmac/fivem-resource-builder (Root `SKILL.md` + `examples/`) @ `d34ea3075362` | MIT | 145 Zeilen + Beispiele | Scaffolding sicherer Resources (fxmanifest, Client/Server/Shared, ACE, Anti-Dupe). | Auf unser Framework und unsere Ordnerkonventionen reduzieren. `WebFetch` in `allowed-tools` prüfen. |
| Teile aus `fivem-kit` / `muto-atlas` | hamchowderr/fivem-kit, B7Kompirine/muto-atlas | MIT | groß | Ideen für Natives-Lookup und Daten-zuerst-Arbeitsweise. | Nicht 1:1 übernehmen. Erst Qualität prüfen (jung, wenige Nutzer). |

**Nicht kopieren:** Natives-Daten selbst (citizenfx/natives, `ext/native-decls`, alloc8or).
Stattdessen schreibt unser FiveM-Natives-Skill, **wie** man nachschlägt (docs.fivem.net,
`runtime.fivem.net/doc/natives*.json`, `natives_gen9.json` für Enhanced) und wie man die
LuaLS-Typen aus **overextended/fivem-lls-addon** (MIT, als Werkzeug installiert, nicht vendored)
einbindet.

---

## 5. Empfohlenes Vorgehen

1. **Installieren statt kopieren** für alles, was gepflegt wird und Querverweise hat: Superpowers, Anthropic-Plugins, Epic-Plugin, trailofbits (CC BY-SA).
2. **Kopieren mit Attribution** für kleine, eigenständige MIT/Apache-Skills, die wir anpassen wollen. Startliste: `verification-before-completion`, `grill-me`, ein Debugging-Skill (`systematic-debugging` **oder** `diagnosing-bugs`), `ue-cpp-foundations`, `ue-module-build-system`, `fivem-security-audit`, `fivem-resource-builder`.
3. Jede Kopie bekommt `LICENSE` + `UPSTREAM.md` und den Commit-Pin. Updates ziehen wir bewusst manuell per Diff gegen den neuen Upstream-Commit.
4. Vor einem claude.ai-Upload die Frontmatter auf die sechs erlaubten Felder reduzieren.
