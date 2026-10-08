# Automated testing for Brotato mods

Checked 2026-10-08 against Brotato 1.1.15.4 / Mod Loader 6.3.0 source / Godot 3.x `main.cpp` / GUT `godot_3x` 7.4.3. Patterns come from Combat Tracker, FullMapCamera and mojimoon's mods (see sources.md); scripts below are rewritten and short.

## Contents
1. Smoke test: `tools/check_logs.py`
2. Headless runner in the decompiled project
3. Test pack against the real exe: `tools/build_testpack.py`, `tools/run_test.py`
4. In-game driver (autoload) for UI and screenshots
5. Two-process LAN test matrix
6. GUT for pure logic
7. What each layer proves

## 1. Smoke test: `tools/check_logs.py`

Run after any session in loops B or C. Exit 1 = do not ship.

```python
"""Fail if the last Brotato run logged errors from mods (Brotato's CrashReporter disables all mods next start).
Usage: python tools/check_logs.py <ModId> [logs_dir]"""
import os, re, sys

MOD_ID = sys.argv[1]
LOGS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get("APPDATA", os.path.expanduser("~/.local/share")), "Brotato", "logs")
ERR = re.compile(r"\b(SCRIPT ERROR|FATAL-ERROR|ERROR|Parse Error)\b")
bad = []
for name in ("godot.log", "modloader.log"):
    path = os.path.join(LOGS, name)
    if not os.path.isfile(path):
        bad.append("missing " + path)
        continue
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for i, line in enumerate(lines):
        pair = line + " " + (lines[i + 1] if i + 1 < len(lines) else "")
        if ERR.search(line) and ("mods-unpacked" in pair or MOD_ID in pair):
            bad.append("%s:%d %s" % (name, i + 1, pair.strip()))
        if "bad comparison function" in line:
            bad.append("%s:%d %s  (crashes the release build)" % (name, i + 1, line.strip()))
    if name == "modloader.log" and "Initializing -> " + MOD_ID not in "\n".join(lines):
        bad.append("no 'Initializing -> %s' in modloader.log (not loaded, or run without --log-info)" % MOD_ID)
print("\n".join(bad) or "logs clean")
sys.exit(1 if bad else 0)
```

Known harmless line that the script ignores (no `mods-unpacked` in it): `ERROR: Cannot load source code from file 'res://tests/partial_doubles/pd_player.gd'` - appears whenever any mod extends `player.gd`.

## 2. Headless runner in the decompiled project

Layout inside the decompiled project (never in the repo): `mods/tests/<Id>/run.gd` + suites; your mod junction-linked at `mods-unpacked/<Id>/`.

`tests/run_headless.sh` (Git Bash on Windows; `GODOT`, `PROJECT` as env vars):

```bash
#!/usr/bin/env bash
set -u
MOD=${MOD:-YourName-QoLPack}
GODOT=${GODOT:-/c/dev/godot/Godot_v3.7-dev1_win64.exe}
PROJECT=${PROJECT:-/c/dev/brotato-decompiled}
SANDBOX=$(mktemp -d); trap 'rm -rf "$SANDBOX"' EXIT
LOG="$SANDBOX/run.log"
cd "$PROJECT" || exit 2
APPDATA=$(cygpath -w "$SANDBOX") MOD_TEST=1 timeout 600 "$GODOT" --no-window --audio-driver Dummy --path . \
	-s "res://mods/tests/$MOD/run.gd" > "$LOG" 2>&1
STATUS=$?
# any ERROR line (or its At: line) naming the mod would make the game disable all mods next start
awk -v mod="$MOD" '/ERROR/ {cur=$0; if ((getline nxt) > 0 && (index(cur, mod) || index(nxt, mod))) {print cur; print nxt; found=1}} END {exit !found}' "$LOG" && STATUS=1
grep -q "bad comparison function" "$LOG" && { echo "bad comparison function (release build crashes)"; STATUS=1; }
grep -E "^(suite |  ran |FAIL |ALL TESTS PASSED|[0-9]+ checks)" "$LOG"
grep -q "ALL TESTS PASSED" "$LOG" || { STATUS=1; tail -40 "$LOG"; }
exit $STATUS
```

`mods/tests/<Id>/run.gd` - compiled before the autoloads exist, so no `RunData`/`ModLoader*` identifiers at class level:

```gdscript
extends SceneTree

const MOD_ID := "YourName-QoLPack"
var _checks := 0
var _failures := []


func _initialize() -> void:
	yield(self, "idle_frame")
	yield(self, "idle_frame")  # autoloads + ModLoader are ready now
	if OS.get_environment("MOD_TEST") != "1":
		printerr("Refusing to run outside run_headless.sh (it isolates user://)")
		quit(2)
		return
	var mod = root.get_node_or_null("ModLoader/" + MOD_ID)
	_check(mod != null, "mod node exists")
	var ext_path := "res://mods-unpacked/%s/extensions/main.gd" % MOD_ID
	_check(ext_path in root.get_node("ModLoaderStore").script_extensions, "extension registered")
	if mod != null:
		var state = _suite(mod)
		if state is GDScriptFunctionState:
			yield(state, "completed")
	print("%d checks, %d failures" % [_checks, _failures.size()])
	for f in _failures:
		printerr("FAIL ", f)
	if _failures.empty():
		print("ALL TESTS PASSED")
	quit(0 if _failures.empty() else 1)


func _suite(mod) -> void:
	var run_data = root.get_node("RunData")
	run_data.reset()
	_check(mod.has_method("compute_share"), "api present")
	_check(mod.compute_share(100, 2) == 50, "compute_share halves")
	yield(create_timer(0.1), "timeout")  # exercise anything that needs a frame


func _check(ok: bool, msg: String) -> void:
	_checks += 1
	if not ok:
		_failures.append(msg)
```

Rules: `quit(code)` on every path; put a timeout in the shell (`timeout 600`); test through the mod node's public methods or by loading `res://mods-unpacked/<Id>/core/*.gd` with `load()`; never `extends "res://main.gd"` in a test file (it would get instanced by the game). A real battle can be driven from here too (`change_scene`, then poll `current_scene`), mojimoon's suites do it; expect vanilla headless noise from `progress_data.gd`/`cursor_manager.gd` and filter it.

## 3. Test pack against the real exe

`tools/build_testpack.py` (Godot 3 PCK format 1; derived from Combat Tracker/FullMapCamera, both MIT):

```python
"""Isolated copy of Brotato.pck for tests. Never ship, commit or share the output.
Usage: python tools/build_testpack.py "<game dir>" build/BrotatoTest.pck [tests_dir -> res://tests/]"""
import hashlib, os, struct, sys

OPTIONS_TRES = b"""[gd_resource type="Resource" load_steps=3 format=2]

[ext_resource path="res://addons/mod_loader/resources/options_current.gd" type="Script" id=1]
[ext_resource path="res://addons/mod_loader/options/profiles/default.tres" type="Resource" id=2]

[resource]
script = ExtResource( 1 )
current_options = ExtResource( 2 )
feature_override_options = {
}
"""


def read_pck(path):
    with open(path, "rb") as f:
        assert f.read(4) == b"GDPC", "not a Godot PCK"
        ver, major, minor, patch = struct.unpack("<4I", f.read(16))
        assert ver == 1, "only Godot 3 PCK format 1"
        f.read(64)
        index = []
        for _ in range(struct.unpack("<I", f.read(4))[0]):
            n = struct.unpack("<I", f.read(4))[0]
            name = f.read(n).rstrip(b"\0").decode()
            off, size = struct.unpack("<qq", f.read(16))
            f.read(16)
            index.append((name, off, size))
        data = {}
        for name, off, size in index:
            f.seek(off)
            data[name] = f.read(size)
    return (major, minor, patch), data


def write_pck(path, version, data):
    names = sorted(data)
    padded = {n: n.encode() + b"\0" * (-len(n.encode()) % 4) for n in names}
    header = b"GDPC" + struct.pack("<4I", 1, *version) + b"\0" * 64 + struct.pack("<I", len(names))
    offset = len(header) + sum(4 + len(padded[n]) + 32 for n in names)
    index = b""
    for n in names:
        index += struct.pack("<I", len(padded[n])) + padded[n] + struct.pack("<qq", offset, len(data[n])) + hashlib.md5(data[n]).digest()
        offset += len(data[n])
    with open(path, "wb") as f:
        f.write(header + index)
        for n in names:
            f.write(data[n])


def vstr(s):
    b = s.encode()
    return struct.pack("<II", 4, len(b)) + b + b"\0" * (-len(b) % 4)


def patch_project(blob, values):
    assert blob[:4] == b"ECFG"
    o, items = 8, []
    for _ in range(struct.unpack_from("<I", blob, 4)[0]):
        kl = struct.unpack_from("<I", blob, o)[0]; o += 4
        key = blob[o:o + kl].decode(); o += kl
        vl = struct.unpack_from("<I", blob, o)[0]; o += 4
        items.append([key, blob[o:o + vl]]); o += vl
    present = {k for k, _ in items}
    for item in items:
        if item[0] in values:
            item[1] = values[item[0]]
    items += [[k, v] for k, v in values.items() if k not in present]   # appended autoloads load last
    out = b"ECFG" + struct.pack("<I", len(items))
    for k, v in items:
        out += struct.pack("<I", len(k.encode())) + k.encode() + struct.pack("<I", len(v)) + v
    return out


game, out = sys.argv[1], sys.argv[2]
version, data = read_pck(os.path.join(game, "Brotato.pck"))
data["res://project.binary"] = patch_project(data["res://project.binary"], {
    "application/config/name": vstr("BrotatoModTests"),   # user:// -> %APPDATA%\BrotatoModTests
    "_custom_features": vstr(""),                          # no "steam" feature: local platform, ML default options
})
data["res://addons/mod_loader/options/options.tres"] = OPTIONS_TRES
if len(sys.argv) > 3:
    for root, _, files in os.walk(sys.argv[3]):
        for f in files:
            p = os.path.join(root, f)
            data["res://tests/" + os.path.relpath(p, sys.argv[3]).replace(os.sep, "/")] = open(p, "rb").read()
os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
write_pck(out, version, data)
print(out, len(data), "files")
```

To add an in-game driver autoload, extend the `patch_project` dict with `"autoload/ModTestDriver": vstr("*res://tests/driver.gd")`.

`tools/run_test.py` (orchestration; adapt paths):

```python
import os, shutil, subprocess, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.environ.get("BROTATO_GAME_DIR", r"C:\Program Files (x86)\Steam\steamapps\common\Brotato")
MOD_ID = "YourName-QoLPack"
build = os.path.join(REPO, "build")
zip_path = subprocess.run([sys.executable, "tools/pack.py"], cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines()[0]
mods = os.path.join(build, "testmods"); shutil.rmtree(mods, ignore_errors=True); os.makedirs(mods)
shutil.copy(zip_path, mods)
for extra in sys.argv[1:]:                      # e.g. the BrotatoOnline zip from the Workshop folder
    shutil.copy(extra, mods)
pack = os.path.join(build, "BrotatoTest.pck")
subprocess.run([sys.executable, "tools/build_testpack.py", GAME, pack, os.path.join(REPO, "tests")], cwd=REPO, check=True)
cmd = [os.path.join(GAME, "Brotato.exe"), "--main-pack", pack, "--mods-path", mods, "--script", "res://tests/smoke.gd",
       "--no-window", "--audio-driver", "Dummy", "--video-driver", "GLES2", "--log-info",
       "--qol-test-out=" + os.path.join(build, "result.json").replace("\\", "/")]
t0 = time.time()
with open(os.path.join(build, "stdout.log"), "w", encoding="utf-8", errors="replace") as log:
    proc = subprocess.Popen(cmd, cwd=GAME, stdout=log, stderr=subprocess.STDOUT)
    try:
        code = proc.wait(timeout=120)
    except subprocess.TimeoutExpired:
        proc.kill(); code = "timeout"
print("exit", code, "after %.0fs" % (time.time() - t0))
logs = os.path.join(os.environ["APPDATA"], "BrotatoModTests", "logs")
check = subprocess.run([sys.executable, "tools/check_logs.py", MOD_ID, logs], cwd=REPO)
os.remove(pack)                                 # the patched pack is the whole game: do not keep it around
sys.exit(0 if code == 0 and check.returncode == 0 else 1)
```

`tests/smoke.gd` is the SceneTree runner from section 2 with two changes: read your output path from `OS.get_cmdline_args()` (`arg.begins_with("--qol-test-out=")`) and write JSON with `File` (`File.WRITE`, `to_json(results)`). Refuse to run unless `OS.get_user_data_dir()` contains `BrotatoModTests` so a mistake never touches real saves.

## 4. In-game driver (autoload) for UI and screenshots

Combat Tracker's pattern for things a `SceneTree` script cannot do well: an autoload `Node` added via `patch_project`, `pause_mode = PAUSE_MODE_PROCESS`, in `_ready()` set `DebugService.disable_saving = true`, `no_fullscreen_on_launch = true`, `custom_wave_duration = <s>`, `nb_enemies_mult`, then `call_deferred("_run")`. `_run()` yields on `create_timer`, starts a run with a fixed character/weapons/items (`RunData.add_character/add_weapon/add_item`, `change_scene` to the difficulty/game scene), waits, inspects your nodes, takes screenshots (`get_viewport().get_texture().get_data()`, `flip_y()`, `save_png("user://shots/1.png")`), drives clicks with `Input.parse_input_event(InputEventMouseButton)` so the engine's real input path is tested, writes `user://results.json`, and `get_tree().quit()`. Parameterise through environment variables (`OS.get_environment("QOL_TEST_WAVE")`), not source edits. Run without `--no-window` for these.

## 5. Two-process LAN test matrix

FullMapCamera's design, verified with 2 and 4 processes on one machine:

- One **separate exe directory per process** (`build/runtime-host/`, `build/runtime-client1/`...) containing copies of `Brotato.exe` + `steam_api64.dll` and its own `mods/` folder - this is how "host has the mod, client does not" is tested without leaking the real `mods` folder. Each process gets its own patched pack with its own `application/config/name` (`BrotatoModTests-host`, `...-client1`) so user dirs and logs do not collide.
- Start all with `--main-pack <pack> --script res://tests/lan.gd --no-window --audio-driver Dummy --video-driver GLES2 --lan-role=host|client --lan-players=2 --lan-out=<abs json>`; on Windows pass `creationflags=0x08000000` (no console window). `wait(timeout=30)` per process, kill the rest on failure, delete the packs in `finally`.
- `tests/lan.gd` (`extends SceneTree`): parse the `--lan-*` args, assert the isolated project name and user dir, disable your netcode's Steam transport (set the transport node's handles to null so it reports unavailable; never call `steamInit`), host -> `create_session`, client -> `join_lan("127.0.0.1", <your port>)`, poll until `member_count >= players`, host configures characters/weapons and goes through the real difficulty -> prepare/ack -> commit path, every process polls until `current_scene.filename == game scene`, then runs 20+ samples of its assertions and writes `{"role", "checks", "failures", "session_id", "local_player_indices", ...}`; `_idle()` enforces a 20 s timeout. Exit 0 only with zero failures.
- Python asserts: all exit codes 0, one shared `session_id`, union of `local_player_indices` == `range(players)`, per-role expectations (mod installed vs absent).
- Cases to keep: both installed, host-only, client-only, four players. Re-run on every netcode change and after every Brotato or BrotatoOnline update. Real Steam P2P, two machines and internet latency still need a manual pass (`brotato-online-multiplayer`).

## 6. GUT for pure logic

GUT 7.4.3 (`bitwes/Gut` branch `godot_3x`, last change 2024-02-29) runs on Godot 3.x. It cannot load scripts that `extends "res://main.gd"` or touch autoloads outside the game project, so keep testable logic in plain `Reference`/`Node` scripts (`core/`), like Combat Tracker, and forbid game globals there:

```bash
grep -rnE "\b(RunData|ItemService|ProgressData|Utils|Keys|ModLoader[A-Za-z]*)\b" mods-unpacked/YourName-QoLPack/core && echo "core/ touches the game" && exit 1
```

Setup: a `project.godot` at the repo root (`config_version=4`, `[application] config/name="QoLPack tests"`) makes `res://mods-unpacked/<Id>/core/x.gd` resolvable; `addons/gut/` vendored or gitignored; tests in `tests/unit/test_*.gd` (`extends "res://addons/gut/test.gd"`, `assert_eq(load("res://mods-unpacked/YourName-QoLPack/core/share.gd").new().half(101), 50)`).

```bash
Godot_v3.7-dev1_win64.exe --no-window --audio-driver Dummy --path . -s addons/gut/gut_cmdln.gd -gdir=res://tests/unit -ginclude_subdirs -gexit -glog=1
# CI (Linux): Godot_v3.7-dev1_linux_headless.64 or Godot_v3.6.3-stable_linux_headless.64, same arguments; add -gjunit_xml_file=res://build/gut.xml
```

Exit code 0 = all passed, 1 = a failure (pending tests do not fail). Options take `-gname=value` without spaces; `.gutconfig.json` at `res://` holds defaults.

## 7. What each layer proves

| Layer | Proves | Blind spot |
|---|---|---|
| gdlint + gdformat --check | no Godot 4 tokens, consistent indentation, naming | runtime, signatures, builtin shadowing |
| validate_manifest.py | manifest passes Mod Loader's rules, folder name matches | nothing about code |
| headless run (loop A) | compiles in a debug build, extension installed, logic | release-only behaviour, Steam |
| GUT | pure logic with fixtures | anything touching the game |
| test pack (loop C) | loads and runs in the shipped release build, zip layout, other mods alongside | signature mismatch (silent in release), real Steam |
| LAN matrix | netcode across processes, install combinations | internet latency, Steam P2P |
| Workshop download + manual run (loop B) | what players get | - |
