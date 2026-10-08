# Dev loops: editor project, shipped exe, isolated test pack, logs

Versions: Brotato 1.1.15.4 (engine `3.7.dev.custom_build.74e86be54`, Mod Loader 6.2.0/6.3.0), Godot 3.7-dev1 official build, GDRE Tools v2.7.0. Checked 2026-10-08.

## Contents
- Loop A: decompiled project + Godot 3.7-dev1 editor
- Loop B: shipped game + Workshop item folder
- Loop C: shipped game + patched PCK copy (no Steam, own user dir)
- Why `mods-unpacked/` and `mods/` next to the exe do not work
- Logs and reading errors fast
- Faster restarts

## Loop A: decompiled project + Godot 3.7-dev1 editor

1. Decompile your own copy, outside the repo (never commit it):
   ```bash
   gdre_tools --headless --recover="C:/Program Files (x86)/Steam/steamapps/common/Brotato/Brotato.pck" --output="C:/dev/brotato-decompiled"
   gdre_tools --headless --list-bytecode-versions          # if detection fails: --force-bytecode-version=<commit or x.y.z>
   gdre_tools --headless --recover=... --scripts-only      # faster when you only need the scripts
   ```
   GDRE v2.7.0 still decompiles Godot 3.x (bytecode rev 13) although it no longer builds on 3.x. MIT alternative without GDRE: Combat Tracker's `tools/pck.py extract Brotato.pck reference/game "*.gd*"` + `tools/gdc.py` (token-table reconstruction of `.gdc`, loses comments only).
2. Editor: `Godot_v3.7-dev1_win64.exe` from `github.com/godotengine/godot-builds/releases/tag/3.7-dev1` (also `linux_headless.64`, `linux_server.64`, `x11.64`). It is the closest official build to the game's custom 3.7-dev; 3.6.3-stable also opens the project. Never open it with Godot 4.
3. Link the repo folder in (no copy step, edits land in git):
   ```bat
   mklink /J "C:\dev\brotato-decompiled\mods-unpacked\YourName-QoLPack" "C:\dev\qolpack\mods-unpacked\YourName-QoLPack"
   ```
   PowerShell: `New-Item -ItemType Junction -Path <project>\mods-unpacked\<Id> -Target <repo>\mods-unpacked\<Id>`; Linux/macOS: `ln -s`. Junctions need no admin rights. The editor writes `*.import` next to PNG/WAV inside the linked folder and cooked files into `<project>/.import/`: commit the `*.import` files only if you ship assets, and copy the cooked `<project>/.import/<prefix>*.stex` into the repo's `.import/` for `pack.py`.
4. Run: F5 in the editor (breakpoints, remote scene tree, profiler), or headless/windowed from a terminal:
   ```bash
   Godot_v3.7-dev1_win64.exe --path C:/dev/brotato-decompiled -w --resolution 1280x720 --position 0,0 --log-info
   Godot_v3.7-dev1_win64.exe --path C:/dev/brotato-decompiled --no-window --audio-driver Dummy -s res://mods/tests/run.gd
   ```
   Mod Loader reads `OS.get_cmdline_args()` in the editor project too, so `--log-debug`, `--disable-mods`, `--configs-path` work there.
5. Editor-only truths: it is a debug build (`assert`, override signature check `The function signature doesn't match the parent`, `bad comparison function` report, `SCRIPT ERROR` aborts the function). Deprecated Mod Loader calls are fatal asserts here and only warnings in the game. Steam-dependent vanilla code logs errors without Steam: ignore those, not yours. Never put zips in `res://mods/` of the editor project: loading any zip wipes the virtual `res://` and the unpacked mods vanish.
6. Keep the editor's save files out of your real profile: launch the editor project with `APPDATA` pointed elsewhere (`set APPDATA=C:\dev\brotato-appdata` in the same shell), or accept that `user://` is `%APPDATA%\Brotato` of the decompiled project name (same as the game if the project name is unchanged).

## Loop B: shipped game + Workshop item folder

1. Publish once as hidden (see shipping.md), subscribe. The item folder is `<SteamLibrary>/steamapps/workshop/content/1942280/<item_id>/`.
2. `tools/sync.py`: run `pack.py`, delete every `*.zip` in that folder, copy the new one (mojimoon's `pack_mod.py` does exactly this). Two zips = two versions loaded.
3. Steam launch options: `--log-info` (or `--log-debug` while hunting a load problem), `-w --resolution 1280x720 --position 0,0` for a small window beside the editor, `--disable-mods` to prove a crash is not mod-related.
4. Restart the game: mods load only at startup; the in-game Mods menu toggle also needs a restart.
5. Read `godot.log` + `modloader.log` (below). Steam's "Verify integrity" and item updates overwrite your zip with the published one.

## Loop C: shipped game + patched PCK copy

What Combat Tracker and FullMapCamera do (both MIT, both verified on 1.1.15.4):

- Copy `Brotato.pck` and patch only the copy (`tools/build_testpack.py` in testing.md):
  - `res://project.binary` (binary `ECFG` key/value list): `application/config/name = "BrotatoModTests"` (user dir becomes `%APPDATA%\BrotatoModTests`, saves/profile/logs isolated) and `_custom_features = ""` (drops the `steam` feature tag: the game runs its local platform instead of GodotSteam, and Mod Loader's `steam` feature override no longer switches Workshop mode on, so `--mods-path` and `<exe dir>/mods/*.zip` work). Combat Tracker instead sets `application/config/use_custom_user_dir` + `custom_user_dir_name` and remaps `res://singletons/platforms/platform.gd` to a `LocalPlatform` wrapper; same effect, more game-specific.
  - Replace `res://addons/mod_loader/options/options.tres` with a resource that points at `profiles/default.tres` and has no `feature_override_options` (belt and braces).
  - Optional: add an autoload `autoload/TestDriver = "*res://tests/driver.gd"` and overlay `res://tests/*.gd` into the pack for in-game UI tests; or overlay your unpacked mod at `res://mods-unpacked/<Id>/` to test without a zip.
- Run from the game directory (Steam DLL next to the exe):
  ```bash
  Brotato.exe --main-pack build/BrotatoTest.pck --mods-path build/testmods --script res://tests/smoke.gd --no-window --audio-driver Dummy --video-driver GLES2 --my-mod-test-out=C:/dev/qolpack/build/result.json
  ```
  `--no-window` + `--audio-driver Dummy` for script tests; drop `--no-window` and keep a real window for screenshots and `Input.parse_input_event` UI tests (Combat Tracker sets `OS.window_size`, mutes the Master bus, uses `DebugService` to start on a chosen wave).
- Results: `%APPDATA%\BrotatoModTests\logs\godot.log` + `modloader.log`, plus whatever your script writes (`user://` or the absolute path from your `--...-out=` arg). Always `proc.wait(timeout=...)` then `kill()`.
- Legal/hygiene: the patched pack contains the whole game. Keep it in `build/` or `.local/` (gitignored), delete it after the run, never upload it.

## Why `mods-unpacked/` and `mods/` next to the exe do not work

- Mod Loader lists `res://mods-unpacked/` with `Directory`; in an exported game that is the PCK, not the disk. A folder beside `Brotato.exe` is invisible. Unpacked mods are an editor-only feature.
- `_load_mod_zips()` is either/or: `steam_workshop_enabled` -> `<steamapps>/workshop/content/<app_id>/*/` (app id from `steam_data.json` beside the exe), else `<exe dir>/mods/` or `--mods-path`. The Steam build has Workshop mode on, so `mods/` loads nothing there - which is why reports disagree.

## Logs and reading errors fast

| File | Content |
|---|---|
| `%APPDATA%\Brotato\logs\godot.log` | engine + GDScript: `SCRIPT ERROR: <func>: <msg>` + `At: res://...gd:<line>`, `ERROR: <msg>` + `At: <file>:<line>`, Mod Loader `push_error`s |
| `%APPDATA%\Brotato\logs\modloader.log` | Mod Loader only, rotated each start (`modloader_<date>.log` backups): zip scan (`Checking workshop items, with path:`, `<zip> loaded.`), manifest problems (`FATAL-ERROR`), `mod_load_order -> 1) <Id>`, `Initializing -> <Id>`, `DONE: Installed all script extensions` |
| stdout of the process (loops A/C) | same as `godot.log` plus your `print()`s; capture it to a file in test runners |

```bash
# bash / Git Bash: first error with its At: line, then live tail
grep -n -A1 -m1 -E "Parse Error|SCRIPT ERROR|FATAL-ERROR" "$APPDATA/Brotato/logs/godot.log" "$APPDATA/Brotato/logs/modloader.log"
tail -f "$APPDATA/Brotato/logs/godot.log"
```

Read order: `modloader.log` first `FATAL-ERROR` (manifest/zip) -> `godot.log` first `Parse Error` (your script did not compile; the following `set_meta ... null instance` line is a consequence) -> first `SCRIPT ERROR` (runtime). Levels in `modloader.log` need the launch flag: `WARNING` needs `--log-warning`, `INFO`/`SUCCESS` need `--log-info`, `DEBUG` needs `--log-debug`.

## Faster restarts

- No verified "skip intro" flag exists. What is verified: a dev-only driver or test mod can set `DebugService.disable_saving = true`, `DebugService.no_fullscreen_on_launch = true`, `DebugService.custom_wave_duration = 20`, `DebugService.nb_enemies_mult = 2.0` in `_ready()` (fields used by Combat Tracker's driver on 1.1.15.4; `brotato-stability-performance` also uses `starting_wave`, `invulnerable` - guard with `if "field" in DebugService`). Keep that mod out of the release zip.
- Engine flags: `--time-scale 3` speeds the simulation, `--fixed-fps 30` makes runs deterministic-ish, `-w --resolution 1280x720` avoids the fullscreen switch, `--audio-driver Dummy` skips audio init.
- Loop A restarts in seconds; use it for everything that does not need Steam or the release build. Reserve loop B for the final pass.
