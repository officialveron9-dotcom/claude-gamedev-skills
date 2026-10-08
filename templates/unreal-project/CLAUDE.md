# <MeinSpiel> – Unreal Engine 5.8, C++

Vorlage aus `gamedev-skills/templates/unreal-project`. Platzhalter `<...>` ersetzen, Unzutreffendes löschen.
Rechnerabhängige Pfade (Engine-Ordner, Laufwerke) gehören in `CLAUDE.local.md` (gitignored, wird genauso geladen).

## Projekt

- Engine: Unreal Engine **5.8.x**, Launcher-Build unter `C:\Program Files\Epic Games\UE_5.8` (Source-Build: Pfad in `CLAUDE.local.md`).
- Projektdatei `<MeinSpiel>.uproject`, Hauptmodul `Source/<MeinSpiel>/`, Targets `<MeinSpiel>` (Game) und `<MeinSpiel>Editor`.
- Toolchain: Visual Studio 2022 17.14+ oder VS 2026, MSVC 14.38+/14.50, Windows SDK 10.0.26100 (Details: Skill `ue5-build-and-modules`, Abschnitt Toolchain).
- Plattform: Windows 64-bit. Dedicated Server: <nein | ja, Target `<MeinSpiel>Server`, braucht Source-Build>.
- Sprache: Deutsch im Chat; Code, Kommentare und Commit-Messages auf Englisch.

## Bauen (Windows, Eingabeaufforderung; `%UE%` = Engine-Ordner, in Befehlen ausschreiben)

```bat
:: Editor-Target (entspricht "Development Editor" in Visual Studio)
"%UE%\Engine\Build\BatchFiles\Build.bat" <MeinSpiel>Editor Win64 Development -Project="C:\Dev\<MeinSpiel>\<MeinSpiel>.uproject" -WaitMutex -FromMsBuild

:: Game-Target (Standalone; vor dem Packaging bauen, faengt WITH_EDITOR-Fehler ab)
"%UE%\Engine\Build\BatchFiles\Build.bat" <MeinSpiel> Win64 Development -Project="C:\Dev\<MeinSpiel>\<MeinSpiel>.uproject" -WaitMutex -FromMsBuild

:: Projektdateien neu erzeugen (nach Aenderungen an Build.cs, .uproject, .uplugin oder neuen Dateien)
"%UE%\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" -projectfiles -project="C:\Dev\<MeinSpiel>\<MeinSpiel>.uproject" -game -engine -progress

:: Cook + Package (Development, Win64)
"%UE%\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="C:\Dev\<MeinSpiel>\<MeinSpiel>.uproject" -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive -archivedirectory="C:\Dev\Builds"

:: compile_commands.json fuer clangd (Plugin clangd-lsp). Die Datei landet im Engine-Stammordner
:: (Launcher-Build: C:\Program Files\Epic Games\UE_5.8\compile_commands.json) und wird danach ins Projekt kopiert.
:: TODO pruefen: Befehl stammt aus Community-Threads zu UE 5.2-5.4, in 5.8 noch nicht getestet.
"%UE%\Engine\Build\BatchFiles\Build.bat" -mode=GenerateClangDatabase -project="C:\Dev\<MeinSpiel>\<MeinSpiel>.uproject" -game -engine <MeinSpiel>Editor Win64 Development
```

- Live Coding (Strg+Alt+F11 im Editor) nur für Funktionskörper in `.cpp`. Nach Änderungen an Headern, `UPROPERTY`/`UFUNCTION`, Basisklassen, Konstruktoren, `Build.cs`: Editor schließen, bauen, Editor neu starten.
- Bei Build-, Linker-, UHT- oder Packaging-Fehlern zuerst den Skill `ue5-build-and-modules` lesen (Fehlertext → Ursache → Fix).

## Logs

- Editor und Spiel: `Saved/Logs/<MeinSpiel>.log` (aktuell), ältere mit Zeitstempel daneben. Eigene Logs: `UE_LOG(LogTemp, Warning, TEXT("..."))` oder eigene Kategorie `DECLARE_LOG_CATEGORY_EXTERN`.
- Crashes: `Saved/Crashes/<Id>/` (`<MeinSpiel>.log`, `CrashContext.runtime-xml`, Minidump).
- Packaging/UAT: Konsolenausgabe; ab der **ersten** `Error:`-Zeile lesen, nicht beim letzten `BUILD FAILED`. Dateikopie unter `%APPDATA%\Unreal Engine\AutomationTool\Logs\<Engine-Pfad>\Log.txt` (TODO prüfen).
- Cook-Probleme: `Saved/Cooked/Win64/<MeinSpiel>/` fehlt etwas → Asset wird nicht referenziert (Asset Manager, "Maps to include").

## Konventionen (je eine Zeile)

- Namen: Präfixe `A`/`U`/`F`/`E`/`I`/`T`, PascalCase, bool mit `b` (`bIsReady`), Dateiname = Klassenname ohne Präfix.
- Keine STL-Container und keine Exceptions im Gameplay-Code: `TArray`/`TMap`/`TSet`, `FString`/`FName`/`FText`, `TOptional`; `check()`/`ensure()` statt `throw`.
- UObjects nie mit `new`/`delete`: `NewObject`, `CreateDefaultSubobject` (nur im Konstruktor), `SpawnActor`; Zeiger auf UObjects als `UPROPERTY()` `TObjectPtr<T>`, sonst räumt der GC sie weg.
- `UPROPERTY`: `EditDefaultsOnly`/`EditAnywhere` plus `BlueprintReadOnly` als Standard, `BlueprintReadWrite` nur mit Grund; immer `Category`; `VisibleAnywhere` für Komponenten; `Transient` für Laufzeitdaten.
- `UFUNCTION(BlueprintCallable)` nur für Funktionen, die Blueprints wirklich brauchen; reine Abfragen `BlueprintPure` und `const`.
- Includes: eigener Header zuerst, modul-relative Pfade (`GameFramework/Character.h`), `*.generated.h` als letztes Include im Header, Forward-Declarations statt Includes im Header.
- Neue Engine-Module in `Build.cs` (Private, wenn nur in `.cpp` genutzt) und Plugins im `.uproject` eintragen, sonst LNK2019.
- Multiplayer: Server-autoritativ, `DOREPLIFETIME`, `WithValidation` für Client-RPCs (Skill `ue5-multiplayer`).
- `.uasset`/`.umap` nie als Text bearbeiten; Blueprint- und Asset-Änderungen über den Editor (Unreal MCP) oder als Anleitung beschreiben.
- Keine Blueprint-Abhängigkeiten in C++ (`FindObject<UClass>("/Game/...")` nur über `TSoftClassPtr`/`UPROPERTY`-Referenzen).

## Skills und MCP

- Einmal zu Beginn: `/ue-project-context` ausführen, damit `.agents/ue-project-context.md` existiert (die `ue-*`-Referenz-Skills lesen sie).
- Compile/Link/Package: `ue5-build-and-modules`. UObject, GC, Delegates, Reflection: `ue5-cpp-core`. Replikation: `ue5-multiplayer`. Lumen, Licht, Materialien: `ue5-lighting-rendering`. FPS/Hitches: `ue5-performance-optimization`. Billard-Physik: `billiards-game-dev`.
- Bugs: `systematic-debugging` (erst Ursache, dann Fix). Vor „fertig“: `verification-before-completion`.
- MCP `unreal-api` (API-Datenbank, braucht keinen Editor, geht auch in Cloud-Sessions): vor jedem Engine-Aufruf, der in dieser Sitzung noch nicht benutzt wurde, `get_function_signature`; vor einem `#include` `get_include_path`; bei älteren Beispielen `get_deprecation_warnings`. Keine Signaturen raten.
- MCP `unreal-mcp` (Editor-Steuerung, nur lokal bei laufendem Editor): vorher speichern und committen; Ablauf `list_toolsets` → `describe_toolset` → `call_tool`; keine Massenänderungen ohne Rückfrage; Ergebnis jedes Aufrufs prüfen. Konfiguration erzeugt die Editor-Konsole mit `ModelContextProtocol.GenerateClientConfig ClaudeCode`.

## Vor „fertig“

1. Editor-Target baut (Befehl oben) ohne neue Warnungen in geänderten Dateien.
2. Header geändert? Editor war geschlossen, Build lief, Editor startet ohne „could not be compiled“.
3. Game-Target baut (`WITH_EDITOR`-/`WITH_EDITORONLY_DATA`-Fehler zeigen sich erst hier).
4. Automation-Tests (falls vorhanden): `"%UE%\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "C:\Dev\<MeinSpiel>\<MeinSpiel>.uproject" -ExecCmds="Automation RunTests <MeinSpiel>; Quit" -unattended -nopause -nullrhi -log` – Ergebnis in `Saved/Logs/`.
5. `Saved/Logs/<MeinSpiel>.log` nach `Error`/`Warning` mit eigenen Klassennamen durchsuchen.
6. `git status`: nur Quell-, Config- und Content-Dateien; nichts aus der Liste unten.

## Nie committen

`Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/`, `*.sln`, `*.VC.db`, `Plugins/*/Binaries/`, `Plugins/*/Intermediate/`, `compile_commands.json` (enthält lokale Pfade), `CLAUDE.local.md`, `.claude/settings.local.json`. Große Binärdateien (`.uasset`, `.umap`) über Git LFS.
