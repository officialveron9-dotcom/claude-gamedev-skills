# Externe Ressourcen: Brotato-Modding (Godot 3, Godot Mod Loader 6.x)

Stand: **2026-10-06**. Eigene Kurzbewertungen für die Entwicklung einer Brotato-Mod (Online-Koop mit vielen QoL-Funktionen). Nichts davon ist in dieses Repo kopiert.

**So wurde geprüft:**
- GitHub-Repos wurden geklont oder ihre Dateien direkt gelesen (Lizenzdatei im Repo-Root, Datum des letzten Commits).
- Steam, Steam-Workshop, das Brotato-Wiki (brotato.wiki.spellsandguns.com), wiki.godotmodding.com und Patch-Note-Seiten waren aus der Sandbox gesperrt. Sie sind nur über Suchergebnisse belegt und mit **(Suchindex)** markiert.
- Repos **ohne Lizenzdatei**: nur lesen und daraus lernen, keinen Code übernehmen. **GPL**: Code nur übernehmen, wenn deine Mod auch GPL wird.

---

## Kernfakten in Kürze

- Brotato 1.1.15.4 läuft auf einem **eigenen Godot-3.7-dev-Build**, seit dem Update „Paws & Claws“ (Feb. 2026). Vorher lief es laut Mod-Beschreibungen auf Godot 3.5.x. Mods müssen also **GDScript 3** sein, Godot-4-Syntax geht nicht.
- Brotato bringt den **Godot Mod Loader 6.x** mit. Die Quellen widersprechen sich, ob es 6.2.0 oder 6.3.0 ist. Deshalb Code schreiben, der auf beiden läuft. Mod Loader 7 (Hooks, `extend_scene`) gibt es nur für Godot 4.
- Die Steam-Version lädt Mods als ZIP aus `steamapps/workshop/content/1942280/<Item-ID>/`.

---

## 1. Mod Loader und offizielle Doku

| Ressource | URL | Lizenz | Verdikt |
| :- | :- | :- | :- |
| Godot Mod Loader, Branch `3.x` (v6.3.0) | https://github.com/GodotModding/godot-mod-loader/tree/3.x | CC0 1.0 | **Pflichtlektüre.** Der Quellcode ist die zuverlässigste Doku: `addons/mod_loader/api/*.gd` und `resources/mod_manifest.gd`. Tag `v6.2.0` zum Vergleich. |
| Godot Mod Loader, Branch `4.x-dev` (v7.x) | https://github.com/GodotModding/godot-mod-loader | CC0 1.0 | **Nicht für Brotato.** Nur Godot 4. Hilft beim Erkennen, wenn Claude 7.x-APIs wie `add_hook` erfindet. |
| Godot Modding Wiki | https://wiki.godotmodding.com/ | – | Offizielle Doku (Manifest, Script-Extensions, Configs, CLI). Aus der Sandbox gesperrt. Die alten GitHub-Wiki-Seiten (bis 2025-02-19) stecken noch in der Git-Historie von `godot-mod-loader.wiki`. |
| Godot Modding Discord | https://discord.godotmodding.com/ | – | Support direkt von den Mod-Loader-Entwicklern. Gut bei Fragen zu Loader-Interna. |
| Godot Mod Tool (Editor-Plugin), Branch `3.x` | https://github.com/GodotModding/godot-mod-tool | MIT | Editor-Hilfen für Mods, z. B. „ModTool: Create Asset Overwrite“ (laut Mod-Loader-Wiki). Lohnt sich, wenn du im dekompilierten Projekt im Godot-3-Editor arbeitest. |

## 2. Brotato-spezifische Doku und Community

| Ressource | URL | Lizenz | Verdikt |
| :- | :- | :- | :- |
| Brotato Wiki: Modding, Modding Notes, Mods Archive | https://brotato.wiki.spellsandguns.com/Modding | – | **(Suchindex)** Einstieg und Liste bekannter Mods. Technische Details eher dünn und teils veraltet (Stand 1.0/1.1). |
| Steam-Guide „Modding Guide for Brotato“ | https://steamcommunity.com/sharedfiles/filedetails/?id=2931079751 | – | **(Suchindex, Verweis im Mod-Loader-Wiki)** Schritt für Schritt: Dekompilieren und erste Mod. Älter als die Hash- und Koop-Umbauten, also Code-Beispiele gegen 1.1.15 prüfen. |
| Brotato Steam-Diskussionen / Patch Notes | https://steamcommunity.com/app/1942280/discussions/ | – | **(Suchindex)** Hier tauchen Bruchstellen nach Updates zuerst auf, z. B. „Unexpected error in mod … Mods have been temporarily disabled.“ |
| Godot Workshop Utility (Uploader von Blobfish) | https://github.com/Blobfish-Games/godot-workshop-utility | CC0 1.0 | Erklärt, wie der mitgelieferte `GodotWorkshopUtility.exe` funktioniert (`steam_data.json`, Beta-Branch „modding“). Der Uploader setzt den Titel aus dem ZIP-Namen. |

Einen öffentlichen, dedizierten Brotato-Modding-Discord konnte ich nicht verifizieren. Die Links laufen meist über den Godot-Modding-Discord und die Workshop-Seiten der Mods.

## 3. Werkzeuge

| Ressource | URL | Lizenz | Verdikt |
| :- | :- | :- | :- |
| GDRE Tools (gdsdecomp), v2.7.0 | https://github.com/GDRETools/gdsdecomp | MIT | **Pflicht** zum Nachschlagen der Spielskripte: „Recover project“ auf `Brotato.pck` stellt Skripte und Projekt wieder her. Nur lokal nutzen. Spielcode **nie** veröffentlichen oder in ein Repo committen. |
| GodotPCKExplorer | https://github.com/DmitriySalnikov/GodotPCKExplorer | MIT | Schneller PCK-Browser und -Extractor. Gut, um gezielt einzelne Dateien zu ziehen, wenn GDRE zu schwer ist. |
| Godot 3.6 stable / 3.x-dev-Builds | https://godotengine.org/download/archive/ | MIT | Editor für das dekompilierte Projekt. Mod-Autoren nutzen `Godot_v3.7-dev1`. **Niemals mit Godot 4 öffnen**, der Konverter zerstört das Projekt. |
| SteamCMD | https://developer.valvesoftware.com/wiki/SteamCMD | proprietär (Valve) | Alternative zum Uploader. Titel, Beschreibung und Changenote bleiben stabil, siehe `publish-steamcmd.sh` in brotato-synergies. |

## 4. Beispiel-Mods mit Quellcode (zum Lernen)

| Mod | URL | Lizenz | Letzte Aktivität | Verdikt |
| :- | :- | :- | :- | :- |
| Brotato Combat Tracker (DPS-Meter) | https://github.com/DPS-Love/brotato-combat-tracker | MIT | 2026-10-01 | **Bestes Vorbild.** Hookt über Signale statt Extensions und ist robust gegen Updates. Dazu automatisierte Tests mit `Brotato.exe`, ein Workshop-Upload-Skript und eine sehr gute `DEVELOPMENT.md` (chinesisch). Bindet die Mod-API von BrotatoOnline an. |
| FullMapCamera | https://github.com/L1SC/brotato-full-map-camera | MIT | 2026-09-17 | Saubere einzelne Extension (`my_camera.gd`), kompatibel mit BrotatoOnline. Starke Testmethodik mit echten LAN-Prozessen. |
| auto-brotato | https://github.com/64922/auto-brotato | MIT | 2026-10-06 | `docs/protocol.md` §8 listet viele interne Felder von Main, Shop und Menüs. Sehr nützlich als Landkarte, aber manche Aussagen zur Engine sind ungenau. |
| Brotatogether | https://github.com/boardengineer/Brotatogether | MIT | 2026-05-20 | Älterer Multiplayer-Mod. Zeigt Netzwerk-Architektur und Client-Main, viele Interna allerdings aus älteren Spielversionen. |
| BrotatoOnline | https://github.com/xx666zz/BrotatoOnline | **GPL-3.0** | 2026-09-26 | Der aktuelle Online-Koop-Mod (Workshop 3741034628). Wichtig für Kompatibilität mit deiner Mod. Wegen der GPL nur lesen, außer deine Mod wird ebenfalls GPL. |
| Co-op Synergies | https://github.com/hhoangg/brotato-synergies | MIT (Code), CC BY 4.0 (Assets) | 2026-09-05 | Gute „House Rules“ zu GDScript-3-Fallen (Tabs, Builtin-Namen, `:=`), PNGs ohne Import laden, Upload per SteamCMD. |
| Extended Coop 8 | https://github.com/MattieTK/brotato-extended-coop-8 | keine | 2026-08-31 | Koop-Gerätezuordnung und Uploader-Anleitung. Nur lesen. |
| Share Money | https://github.com/CommanderAstern/brotato-share-money | keine | 2026-08-23 | Kleine, saubere Koop-Shop-Extension mit Python-Tests fürs Manifest. Nur lesen. |
| Oudstand-Mods (DamageMeter, ModOptions, QuickEquip) | https://github.com/Oudstand/Brotato-Mods | keine | 2026-09-21 | Eigene ModOptions-UI und Translations-Einbindung. Nur lesen. |
| mojimoon BrotatoMods | https://github.com/mojimoon/BrotatoMods | keine | 2026-10-05 | Headless-Testrunner im dekompilierten Projekt, Laufzeit-CSV-Übersetzungen, Packer-Skript. Nur lesen. |
| Balance Mod | https://github.com/DarkTwinge/Brotato-BalanceMod | keine | 2026-08-24 | Die Git-Historie zeigt, was bei jedem Spiel-Update brach (Hash-Umstellung Jan. 2026). Nur lesen. |
| Yoko-NewContentLoader | https://github.com/CYoJkoY/Yoko-NewContentLoader | **eingeschränkte Eigenlizenz** | 2026-10-02 | Content-Framework für Items, Waffen und Charaktere, ausgelegt auf 1.1.15.4. Gute Doku (`docs/USAGE.en.md`). Als Abhängigkeit nutzbar, Code nicht übernehmen. |
| ContentLoader + Brotils | https://github.com/BrotatoMods/Brotato-ContentLoader | keine | 2025-11-30 | Der Klassiker, zuletzt für 1.1.13.1 getestet. Für neue Content-Mods eher NCL prüfen. |

## 5. Vorhandene Godot-Skills für Claude

Ergebnis: **Keiner der gefundenen Skills zielt auf Godot 3.** Fast alle sind für Godot 4 geschrieben und würden Claude zu `@export`, `await` und `super()` verleiten. Für Brotato daher **nicht** zusammen mit den Brotato-Skills installieren.

| Skill | URL | Lizenz | Godot-Version | Verdikt |
| :- | :- | :- | :- | :- |
| GodotPrompter (56 Skills, ~790★) | https://github.com/jame581/GodotPrompter | MIT | 4.3+ | Die beste allgemeine Godot-Sammlung, aber nur Godot 4. Für Brotato schädlich. Für ein späteres Godot-4-Projekt empfehlenswert. |
| godot-game-dev-studio | https://github.com/bgrenat/godot-game-dev-studio | LGPL | 4.7+ | Umfangreich, nur Godot 4. Nicht für Brotato. |
| godot-4-development | https://github.com/Henzen3d/godot-4-development | MIT | 4.x | Nur Godot 4. Nicht für Brotato. |
| godot-code-style | https://github.com/mjasnikovs/godot-code-style | MIT | 4.7 | Strikter, typisierter Godot-4-Stil. Nicht für Brotato. |
| Godot-Skills (fenixnix) | https://github.com/fenixnix/Godot-Skills | MIT | unklar | Kurz, chinesisch, kaum versionsspezifisch. Wenig Mehrwert. |
| godot-skill (BangRocket) | https://github.com/BangRocket/godot-skill | keine gefunden | 4.x (enthält 3→4-Porting) | Nur als Lektüre zur Abgrenzung 3 vs. 4. Ohne Lizenz nicht übernehmen. |
| godot-gdscript-to-csharp | https://github.com/gxrsprite/godot-gdscript-to-csharp | keine gefunden | Godot 3 → Godot 4 C# | Portiert GDScript 3 nach C#. Für Brotato-Mods irrelevant. |

**Empfehlung:** Für Brotato nur die eigenen Skills `brotato-modding` und `godot3-gdscript-pitfalls` (plus `brotato-online-multiplayer`) nutzen. Godot-4-Skills nur in Godot-4-Projekten aktivieren.
