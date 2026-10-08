# Workflow problems: symptom -> cause -> fix

Mod code and Mod Loader errors (manifest messages, extension failures, runtime errors) are in `brotato-modding` `references/troubleshooting.md`. This table covers tooling, tests, packaging and the Workshop. Versions: Brotato 1.1.15.4, Mod Loader 6.2.0/6.3.0, Godot 3.7-dev, gdtoolkit 3.6.0, GDRE 2.7.0, GUT 7.4.3 (checked 2026-10-08).

## Loading and dev loops

| Symptom | Cause | Fix |
|---|---|---|
| Mod missing from the Mods menu; `modloader.log` shows `Checking workshop items, with path:` but never your zip | zip not in `steamapps/workshop/content/1942280/<id>/`, or the Steam download is pending | `tools/sync.py` into the item folder; check `<zip> loaded.` lines with `--log-info` |
| Old version keeps running after `sync.py` | two zips in the item folder, or Steam restored the published zip (verify integrity, item update) | delete every `*.zip` before copying; log `loaded v<VERSION>` in `_ready()` |
| `mods-unpacked/<Id>/` placed next to `Brotato.exe` does nothing | exported game enumerates `res://mods-unpacked/` inside the PCK only | junction into the editor project; zip for the exe |
| `<game>/mods/x.zip` ignored on the Steam build | Workshop mode: zips come only from Workshop folders | Workshop item folder, or a patched pack without the `steam` feature |
| `--mods-path` ignored | same: `override_path_to_mods` is read only when `steam_workshop_enabled` is false | loop C pack (`_custom_features = ""` + default `options.tres`) |
| `Can't open workshop folder .../workshop/content/1942280` when running `Brotato.exe` from a copied directory | ML derives the Workshop path from the exe location (`../../workshop/content/<app_id>`) | run from the Steam install dir, or use the patched pack with `--mods-path` |
| `The steam_data file does not contain an app ID` / `Can't open steam_data file` | `steam_data.json` missing beside the exe copy | copy it along with `Brotato.exe` and `steam_api64.dll`, or patch the pack |
| `-v` makes the console extremely noisy | `-v` is Godot `--verbose` as well as ML `--log-warning` | `--log-info` / `--log-debug` |
| Editor project: unpacked mods vanish after adding a zip to `res://mods/` | Godot bug: loading a zip replaces the virtual `res://` | editor = unpacked mods only |
| Editor opens, every `.tres` is rewritten, scripts show Godot 4 errors | opened with Godot 4 (converter ran) | delete, re-decompile, use `Godot_v3.7-dev1` |
| GDRE `--recover` output has empty or wrong `.gd` files | bytecode version misdetected for the custom 3.7 build | `--list-bytecode-versions`, then `--force-bytecode-version=<3.6 commit or x.y.z>`; or Combat Tracker's `pck.py` + `gdc.py` |
| Breakpoints never hit in the editor for extension code | the running script is the vanilla path (`take_over_path`); breakpoints must be set in the extension file under `res://mods-unpacked/` | set them in your file, confirm with `print(get_script().resource_path)` |
| `Parse Error: The function signature doesn't match the parent.` in the editor, fine in the game | debug-only check; the release game loads the mismatch and fails later with wrong-argument-count errors | copy the exact vanilla signature |
| Game ignores `DebugService` tweaks from your driver | set before `DebugService` existed, or field renamed | set in `_ready()`/deferred; guard `if "field" in DebugService` |

## Tests

| Symptom | Cause | Fix |
|---|---|---|
| `Can't load the script "res://tests/x.gd" as it doesn't inherit from SceneTree or MainLoop.` | `-s` script extends Node | `extends SceneTree` (use an autoload driver for in-game UI tests) |
| `-s` script: `Parse Error: The identifier "RunData" isn't declared in the current scope` or null autoloads | runner compiles before autoloads exist | `root.get_node("RunData")`, two `idle_frame` yields first |
| Headless run never exits / CI job hangs | no `quit()` path, `yield` on a signal that never fires, modal error dialog | `quit(code)` everywhere, `_idle()` timeout, `timeout`/`proc.wait(timeout=)` + kill, `--no-window` |
| Headless run exits 0 although checks failed | `quit()` without code, or `OS.exit_code` set and then overwritten | `quit(1)`; grep stdout for `ALL TESTS PASSED` as a second gate |
| Test pack: `Brotato.exe` starts but no mods load, no `modloader.log` | wrong `--main-pack` path (relative to cwd), or options.tres not replaced and Workshop path invalid | absolute pack path, cwd = game dir, replace `options.tres`, `--log-info` |
| Test pack writes into the real `%APPDATA%\Brotato` | `application/config/name` unchanged in `project.binary` | patch the name (or `use_custom_user_dir` + `custom_user_dir_name`); assert `OS.get_user_data_dir()` in the script |
| Test pack: Steam overlay/achievements fire, `steamInit` errors | `steam` feature still present | `_custom_features = ""` (or remap `platform.gd` to a local platform) |
| `ERROR: Cannot load source code from file 'res://tests/partial_doubles/pd_player.gd'` in every run | any extension of `player.gd` makes ML reload a dev test class missing from the pack | harmless; `check_logs.py` ignores it (no `mods-unpacked` in the line) |
| LAN test: client never joins | both processes share one user dir / port, Steam transport still active, host not yet listening | separate exe dirs + project names, disable the Steam transport, client waits ~1 s before `join_lan` |
| LAN test: "host-only" case shows the mod on the client too | client process used the real game folder with your Workshop subscription | per-role exe directories with their own `mods/` |
| GUT: `Cannot load source code` / `Parse Error` loading `extensions/*.gd` | `extends "res://main.gd"` cannot resolve outside the game project | test `core/` only; keep game access in `game/` |
| GUT runs 0 tests | `-gdir` path wrong, files not `test_*.gd`, option written with a space (`-gdir res://...`) | `-gdir=res://tests/unit -ginclude_subdirs` |
| Combat/stat numbers differ between runs | wave RNG and pooled nodes | seed what you can, assert invariants (conservation, >0) not exact values; stability skill for determinism limits |

## Lint, format, packaging

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pkg_resources'` from gdlint/gdformat/gdparse | gdtoolkit 3.6.0 imports `pkg_resources`; setuptools >= 81 removed it and Python 3.12+ venvs ship no setuptools | `pip install "setuptools<81"`; pre-commit `additional_dependencies: ["setuptools<81"]` |
| gdlint prints `Unexpected token Token(AT, '@')` | Godot 4 syntax in a file | Godot 3 syntax (`godot3-gdscript-pitfalls`) |
| gdlint passes but the game says `Mixed tabs and spaces in indentation.` / `Unindent does not match` | gdlint 3.6 does not flag space-indented lines | `gdformat --check` fails on them; `gdformat <dir>` rewrites to tabs; `.editorconfig` |
| gdlint passes, game: `Expected an identifier for the local variable name.` | builtin name as identifier (`range`, `min`, `max`, `sign`, `str`, `len`, `hash`, `load`, `char`) - not a gdlint rule | rename; loop A catches it |
| gdlint `class-definitions-order` on a vanilla-style file | vars after funcs, `onready` before `export` | reorder, or `# gdlint:ignore = class-definitions-order` on that line |
| gdlint `function-name` on an override | vanilla name has capitals (`_on_EntitySpawner_...` passes, others may not) | `# gdlint:ignore = function-name`; never rename an override |
| gdformat changed semantics / corrupted a file | rare 3.x formatter bug (multi-line expressions, comments inside calls) | run on a clean git tree, review the diff, `--diff` first; exclude the file via `excluded_directories` if needed |
| gdlint walks `build/`, `reference/`, the vendored `addons/gut` | default `excluded_directories` is only `.git` | extend `excluded_directories` in `gdlintrc` |
| `The mod zip at path "..." does not have the correct file structure.` | zip root is `<Id>/` or `qolpack/mods-unpacked/`; or entry names use `\` (Windows PowerShell 5.1 `Compress-Archive`) | `pack.py`; verify with `python -m zipfile -l` |
| `No loader found for resource: res://mods-unpacked/.../x.png` only in the exe | raw asset without `.import` + cooked `.import/*.stex` in the zip | `.import/qolpack_*` from the editor project + `*.import` files; or load bytes (`brotato-modding`) |
| `x.zip failed to load.` | unsupported compression (bzip2/lzma), encrypted, or truncated | `ZIP_STORED`/`ZIP_DEFLATED` only |
| Works unpacked in the editor, extension path not found in the zip | case mismatch (`Extensions/` vs `extensions/`), zip paths are case-sensitive | lower-case folder names, build paths from `ModLoaderMod.get_unpacked_dir()` |
| `pack.py`: `version mismatch` | `manifest.json` and `VERSION` const differ | bump both; it is the point of the check |
| Release workflow fails on `gh release create` | tag already has a release, or missing `contents: write` | delete the draft, keep `permissions`, re-run with `workflow_dispatch` |

## Workshop

| Symptom | Cause | Fix |
|---|---|---|
| GodotWorkshopUtility stuck at `creating new workshop item...`; log `Steam could not initialize: ... No appID found` | started outside Steam without `steam_appid.txt` | beta branch `modding` launch option, or `steam_appid.txt` = `1942280` beside it |
| Every upload creates another item | Workshop ID blank / `publishedfileid 0` left in the vdf | paste the id after the first upload; commit it |
| Title changed to the zip filename | GodotWorkshopUtility sets title = filename every time | name the zip like the title, or upload with SteamCMD/Steamworks script |
| Item page shows no change note for the update | files unchanged in that submit (changenotes are only recorded with file changes), or GodotWorkshopUtility (no changenote field) | upload the new zip and the note in one submit; edit on the changelog page afterwards |
| Subscribers still get the old version | upload failed (watch for `EResult` != 1), item hidden, Steam cache | check the item's "Change Notes" page; unsubscribe/resubscribe; `sha256` the downloaded zip |
| Item invisible to other people | hidden visibility, legal agreement not accepted, account < USD 5 | item page visibility; `needs_agreement` flag; account |
| SteamCMD: `ERROR! Failed to ... (File Not Found)` / `Invalid Param` | relative `contentfolder`/`previewfile`, preview >= 1 MB, wrong appid | absolute paths in the generated vdf, preview < 1 MB |
| SteamCMD: `Access Denied` / `EResult 15` | logged-in account does not own Brotato or the item | log in as the item's author |
| SteamCMD hangs at login | Steam Guard code expected | run once interactively; later runs reuse the cached login |
| Uploader or game crashes in a folder with `override.cfg` | a mod used `register_global_classes_from_array` | delete `override.cfg` before uploading |
