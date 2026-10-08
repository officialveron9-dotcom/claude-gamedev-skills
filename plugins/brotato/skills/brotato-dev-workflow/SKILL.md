---
name: brotato-dev-workflow
description: Sets up and runs a fast, reliable Brotato mod dev loop (Godot 3.7-dev custom build, Mod Loader 6.x) - editor loop in a decompiled project vs shipped Brotato.exe with isolated test packs, verified Godot and Mod Loader CLI flags, log locations and error scanning, headless and in-game automated tests, two-process LAN tests, gdtoolkit 3.x lint and format, repo template with pack.py, manifest validator, CI, pre-commit and CLAUDE.md, Workshop shipping via GodotWorkshopUtility or SteamCMD, re-testing after game patches. Use for "Brotato mod testen", "dev loop", "schneller entwickeln", "Mod packen", zip, "hochladen", Workshop, SteamCMD, Tests, CI, GitHub Actions, gdlint, gdformat, headless, modloader.log.
---

# Brotato mod dev workflow (Brotato 1.1.15.x, Godot 3.7-dev, Mod Loader 6.x; checked 2026-10-08)

Scope: iterate, test, lint, package, ship. Not here: mod code and Mod Loader API (`brotato-modding`), Godot 3 syntax (`godot3-gdscript-pitfalls`), netcode (`brotato-online-multiplayer`), lag/crash rules and the release checklist (`brotato-stability-performance`), options menus and HUD (`brotato-ui-qol`).

## 1. Pick the loop

| Loop | Use for | Restart | Catches | Misses |
|---|---|---|---|---|
| **A** decompiled project in the `Godot_v3.7-dev1` editor, repo folder junction-linked into `mods-unpacked/` | writing code, breakpoints | F5, ~5 s | parse errors, override signature mismatch, `bad comparison function`, asserts (debug build) | release-only behaviour, Steam, zip layout |
| **B** shipped `Brotato.exe` + zip in the Workshop item folder | final manual test, Steam/online | full restart | what players get | nothing automated |
| **C** shipped `Brotato.exe --main-pack <patched copy> --mods-path <dir> --script res://tests/x.gd` | automated regression, 2-4 process LAN tests, any machine with the game installed | 20-60 s | load/runtime errors, screenshots, exit codes | signature mismatch (release build) |

Code in A, run C before every commit that touches game hooks, run B before every release. Setup and commands: [references/dev-loops.md](references/dev-loops.md).

Pitfalls that cost days:
- A real `mods-unpacked/` folder next to `Brotato.exe` is never read: the shipped game enumerates `res://mods-unpacked/` inside the PCK. Junctions only work in the editor project; the exe needs a zip.
- The Steam build runs Mod Loader in Workshop mode: `<game>/mods/*.zip` and `--mods-path` are ignored unless the `steam` feature tag is removed in a patched PCK copy (loop C).
- Editor = debug build, game = release build: signature checks, `assert`, sort validation and `SCRIPT ERROR` aborts exist only in A. "Works in the editor" proves nothing about the exe.

## 2. Verified CLI flags

Godot 3.x engine (branch `3.x` `main.cpp`): `--path <dir>`, `--main-pack <file.pck>`, `-s`/`--script <res://x.gd>` (script must `extends SceneTree`), `--check-only` (with `-s`: parse only, exit code 0/1), `--no-window`, `-q`/`--quit`, `-d`/`--debug`, `--remote-debug <host:port>`, `--audio-driver Dummy`, `--video-driver GLES2`, `-w`, `--resolution 1280x720`, `--position 0,0`, `--fixed-fps <n>`, `--time-scale <f>`, `--frame-delay <ms>`, `--print-fps`, `--disable-crash-handler`, `-v`/`--verbose`. Unknown `--my-arg=value` are passed through to `OS.get_cmdline_args()`.

Mod Loader 6.2/6.3 (`mod_loader_store.gd`, `internal/cli.gd`): `--disable-mods`, `--mods-path="C:/dir"` (or `--mods-path "C:/dir"`), `--configs-path="C:/dir"`, `-v`/`--log-warning`, `-vv`/`--log-info`, `-vvv`/`--log-debug`, `--log-ignore=Name1,Name2:*`. Nothing else exists (`--enable-mods` is a no-op unless the game was built with `REQUIRE_CMD_LINE`; `--only-setup`, `--setup-create-override-cfg`, `--exe-name`, `--pck-name` belong to the loader's self-install tool, not to mods). Steam launch options take the same flags. Use `--log-info` not `-v`: `-v` is also Godot's `--verbose`.

## 3. Logs: read them first, every time

| What | Where |
|---|---|
| Godot (parse errors, `SCRIPT ERROR`, `ERROR:` + `At:` line) | `%APPDATA%\Brotato\logs\godot.log`; macOS `~/Library/Application Support/Brotato/logs/`; Linux `~/.local/share/Brotato/logs/` |
| Mod Loader (`<time> <LEVEL> <LogName>: msg`; rotated per start to `modloader_<date>.log`) | same folder, `modloader.log`; `Initializing -> <ModId>` and `mod_load_order` need `--log-info` |
| Isolated test packs | `%APPDATA%\<patched project name>\logs\` |

```powershell
Select-String "$env:APPDATA\Brotato\logs\godot.log" -Pattern "SCRIPT ERROR|ERROR:|Parse Error" -Context 0,1 | Select -First 20
Get-Content "$env:APPDATA\Brotato\logs\godot.log" -Wait -Tail 20     # live tail while playing
```

The first `Parse Error`/`FATAL-ERROR`/`SCRIPT ERROR` is the cause; later lines are consequences. Any `ERROR:`/`SCRIPT ERROR:` line (or its `At:` line) mentioning `mods-unpacked` makes Brotato's CrashReporter disable all mods on the next start, so a release with one logged error is a broken release.

## 4. Automated tests (details and scripts: [references/testing.md](references/testing.md))

1. **Smoke test** (minimum, every build): `python tools/pack.py` -> start the game with the zip and `--log-info` -> play menu, wave, shop, quit -> `python tools/check_logs.py <ModId>`: fails on `ERROR`/`SCRIPT ERROR`/`Parse Error` lines mentioning `mods-unpacked`, on `bad comparison function`, and if `Initializing -> <ModId>` is missing.
2. **Headless runner** in the decompiled project: `Godot_v3.7-dev1_win64.exe --no-window --audio-driver Dummy --path <project> -s res://mods/tests/run.gd` with `APPDATA` pointed at a temp dir; the script `extends SceneTree`, waits two `idle_frame`s (autoloads and ModLoader exist then), runs checks, `quit(0 or 1)`. Reference game singletons only via `root.get_node("RunData")` - the script compiles before autoloads exist.
3. **Test pack against the real exe**: copy `Brotato.pck`, patch `project.binary` (new `application/config/name` = separate user dir, `_custom_features = ""` = no Steam, optional `autoload/TestDriver`), replace Mod Loader `options.tres` with the default profile, run `Brotato.exe --main-pack build/BrotatoTest.pck --mods-path build/testmods --script res://tests/x.gd --no-window --audio-driver Dummy --video-driver GLES2`, `wait(timeout)`, kill, scan logs. Patched packs stay in `build/` (gitignored) and are deleted after the run.
4. **Online**: 2-4 copies of loop C in separate exe directories (own `mods/` each), one `--role=host`, others `--role=client` joining `127.0.0.1:<port>`, each writes a JSON result and exits 0/1. Host-only and client-only installs are separate cases.
5. **GUT 7.4.3 (`godot_3x`)** only for pure-logic scripts (no `extends "res://..."` game script, no autoload use), run with the headless Linux build in CI.

## 5. Lint and format

```bash
pip install "gdtoolkit==3.*" "setuptools<81"     # 3.6.0 (2024-10-20) is the Godot 3 line; it imports pkg_resources
gdlint -d                                       # writes ./gdlintrc (read from cwd upwards, also .gdlintrc)
gdlint mods-unpacked && gdformat --check mods-unpacked
```

| Check | Godot 4 token (`@export`, `await`, `super()`) | Space-indented lines | Builtin shadowing (`var range`) | Signature mismatch |
|---|---|---|---|---|
| `gdlint` | parse error, exit 1 | **silent** | **silent** | no |
| `gdformat --check` | parse error | exit 1 (would rewrite to tabs) | no | no |
| Godot editor / headless run (A) | yes | yes | yes | yes (debug build only) |

So the gate is `gdlint` + `gdformat --check` + one run in loop A. gdformat 3.6 writes tabs and keeps `.method()`, `yield`, `export(int, 0, 10)`, `setget`, `func _init(a).(a)` unchanged (tested). Silence a rule on one line with `# gdlint:ignore = class-definitions-order`. Pre-commit, `gdlintrc` tweaks and CI: [references/template.md](references/template.md).

## 6. Repo template (full files: [references/template.md](references/template.md))

```
mods-unpacked/<Namespace>-<Name>/   # the only folder that ships (manifest.json, mod_main.gd, extensions/, core/, game/)
tests/        # run.gd (headless), driver.gd (test pack), test_*.gd (GUT) - never packed
tools/        # pack.py, validate_manifest.py, check_logs.py, build_testpack.py, run_test.py, sync.py
docs/workshop/ (description.txt, changenotes/vX.Y.Z.txt, preview.png)   .github/workflows/check.yml, release.yml
CLAUDE.md  CHANGELOG.md  gdlintrc  .pre-commit-config.yaml  .gitignore (build/ dist/ .local/ reference/ *.pck *.zip)
```

Keep the real folder name `mods-unpacked/<Id>/` at the repo root (not `src/`): extension paths must contain `res://mods-unpacked/<Id>/`, the junction into the editor project then needs no copy step, and every reference mod uses it. `pack.py` zips exactly that folder (plus `.import/<prefix>*` for cooked assets), reads the version from `manifest.json`, refuses a mismatch with the in-code `VERSION` const or a `vX.Y.Z` tag, uses fixed timestamps (reproducible sha256).

## 7. Shipping (details: [references/shipping.md](references/shipping.md))

- First upload hidden, subscribe, confirm `steamapps/workshop/content/1942280/<id>/<zip>` matches `dist/` byte for byte, test from the downloaded item, then set public.
- `GodotWorkshopUtility.exe` (game folder, via Steam beta branch `modding` or `steam_appid.txt`): title = zip filename, no changenote, blank ID = new item. `SteamCMD +workshop_build_item item.vdf` keeps title/description/changenote in a file (absolute paths, `contentfolder` holds only the zip, `publishedfileid 0` creates and prints the id). A changenote is only recorded when the uploaded files changed.
- Updates: bump `version_number` + `VERSION` const, CHANGELOG line, never rename namespace/name (new mod ID = players lose their enable state and configs), keep `config_schema` backwards compatible, bump the network protocol version when messages change.
- After every Brotato patch: re-decompile, diff the scripts you extend, run loops A and C, update `compatible_game_version`, log one warning when the game version is untested.

## 8. Claude: definition of done

Before claiming a change works, run and report: `gdlint` + `gdformat --check` clean; `validate_manifest.py` OK; `pack.py` built and `python -m zipfile -l dist/*.zip | head` shows `mods-unpacked/<Id>/...`; if the game is on this machine, `run_test.py` or a manual run followed by `check_logs.py` clean; headless `run.gd` passed if the decompiled project exists. State explicitly which steps could not run here (no game, no project). Never commit `reference/`, decompiled scripts, `*.pck`, `build/`, `dist/`, `.local/`, logs. CLAUDE.md snippet for the mod repo: [references/template.md](references/template.md#claudemd-for-the-mod-repo).

## 9. Symptom -> cause -> fix (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Mod missing from the Mods menu, `modloader.log` has no `Initializing -> <Id>` | zip not in a Workshop item folder, two zips, or run without `--log-info` so the line is hidden | one zip in `workshop/content/1942280/<id>/`; `--log-info` |
| `The mod zip at path "..." does not have the correct file structure.` | zip root is the mod folder, an extra top folder, or backslash entry names (Windows PowerShell 5 `Compress-Archive`) | `pack.py`; check `python -m zipfile -l` |
| "Unexpected error in mod X. Mods have been temporarily disabled." | previous `godot.log` had `ERROR`/`SCRIPT ERROR` mentioning `mods-unpacked` | fix it, re-enable mods; `check_logs.py` before every release |
| Passes in the editor, breaks in the exe | release build: `.import`-less assets, case-sensitive zip paths, `bad comparison function` crash, unpacked folder not read, Steam code paths | test the zip in loop B/C; ship `.import` + `.stex`; strict `<` comparators |
| Passes in the exe, parse error in the editor | debug-only checks: signature mismatch, deprecated ML API `assert`, `preload` cycle | copy vanilla signature; `ModLoaderMod.*`; `load()` |
| Workshop item does not update for players | upload failed silently (no `steam_appid.txt`), new item created (blank ID), files unchanged, Steam cache | check the item page's change notes; paste the item id; unsubscribe/resubscribe |
| `Parse Error: Mixed tabs and spaces in indentation.` | editor/AI inserted spaces; gdlint does not see it | `gdformat mods-unpacked`; `.editorconfig` `indent_style = tab` |
| `ModuleNotFoundError: No module named 'pkg_resources'` from gdlint | gdtoolkit 3.6.0 needs setuptools < 81 (removed `pkg_resources`); Python 3.12+ venvs ship none | `pip install "setuptools<81"` (also in pre-commit `additional_dependencies`) |
| `--mods-path` ignored, `Checking workshop items, with path:` in the log | Steam Workshop mode on (Steam build) | patched test pack without the `steam` feature, or the Workshop folder loop |
| `Can't load the script "res://tests/x.gd" as it doesn't inherit from SceneTree or MainLoop.` | `-s` script extends Node | `extends SceneTree`; use an autoload driver for in-game UI tests |
| Headless run never exits | no `quit()`, or a `yield` on a signal that never fires | `quit(code)` on every path, `_idle` timeout, `proc.wait(timeout=)` + kill |

## References

- [references/dev-loops.md](references/dev-loops.md) - loops A/B/C step by step, junctions, decompiling, log reading, fast-restart flags. Read when setting up a machine or when iteration feels slow.
- [references/testing.md](references/testing.md) - `check_logs.py`, headless runner, test pack builder, in-game driver, LAN matrix, GUT. Read before writing or running any test.
- [references/template.md](references/template.md) - repo layout, `pack.py`, `validate_manifest.py`, `gdlintrc`, pre-commit, GitHub Actions, `.gitignore`, CHANGELOG, CLAUDE.md. Read when creating or restructuring the repo.
- [references/shipping.md](references/shipping.md) - GodotWorkshopUtility vs SteamCMD vs Steamworks script, vdf, first upload, update rules, after-patch procedure. Read before any upload.
- [references/common-issues.md](references/common-issues.md) - symptom -> cause -> fix for tooling, tests, packaging, Workshop.
- [references/sources.md](references/sources.md) - what each fact is based on, direct reads vs search snippets.
