# Defensive patterns (Godot 3 GDScript)

Copy-ready helpers for a Brotato mod that must survive game updates, other mods and network hiccups.
Replace `Author-ModName` with your mod ID. Checked against the Godot 3.5/3.6 API (also valid on Brotato's newer 3.7.dev build) and Mod Loader 6.2.0/6.3.0.

## Contents
1. Guards at every boundary
2. Calling game methods that may not exist
3. Game-version gate
4. Feature flags and kill switch
5. Circuit breaker for risky features
6. Error log with context (rate-limited)
7. Crash-safe save
8. Detecting other mods

## 1. Guards at every boundary

Validate where data enters your code (vanilla callbacks, signals, timers, network messages, loaded files),
then trust it inside.

```gdscript
static func alive(o) -> bool:
	return is_instance_valid(o) and not (o is Node and o.is_queued_for_deletion())

func on_enemy_hit(enemy, damage) -> void:
	if not _enabled or not alive(enemy):
		return
	if typeof(damage) != TYPE_INT and typeof(damage) != TYPE_REAL:
		return
	_apply(enemy, int(damage))
```

- Re-entrancy guard for anything that can trigger itself (damage → on-hit → damage):
  `if _in_handler: return` … `_in_handler = true` … `_in_handler = false`.
- Clamp inputs from the network and from saves (`clamp()`, max list sizes, NaN check `x != x`).
  GDScript 3 has no `is_finite()`; compare against a sane range.

## 2. Calling game methods that may not exist

```gdscript
# Cached capability check (has_method per frame is wasteful)
var _caps := {}   # "instance_id:method" -> bool

func can_call(obj, method: String) -> bool:
	if not alive(obj):
		return false
	var key: String = "%d:%s" % [obj.get_instance_id(), method]
	if not _caps.has(key):
		_caps[key] = obj.has_method(method)
	return _caps[key]

func safe_call(obj, method: String, args: Array = [], fallback = null):
	if not can_call(obj, method):
		_warn_once("missing_" + method, "game method %s missing; feature degraded" % method)
		return fallback
	return obj.callv(method, args)
```

- Optional properties: `"x" in obj` or `obj.get("x")` (returns null when missing) instead of `obj.x`,
  which becomes a parse or runtime error after the member is renamed.
- Clear `_caps` on scene change (instance IDs are reused).
- `callv` hides arity errors until runtime; keep the call sites few and wrapped.
- Script extensions can't use this trick for the overridden method itself: a changed vanilla signature is a
  parse error in debug-enabled builds and a silently failing call in release builds ([crashes.md](crashes.md)
  section 7). Keep overrides minimal so a patch breaks one small file.

## 3. Game-version gate

ModLoader does not enforce `compatible_game_version`. Check it yourself at `_ready()` (not `_init()`, where
later autoloads are still null). In 1.1.14.x the version string is the constant `VERSION` on the
`ProgressData` and `CrashReporter` autoloads; read it with `get()` so a rename doesn't become a parse error.

```gdscript
const TESTED_GAME_VERSIONS := ["1.1.15.4"]          # versions you actually tested
const MIN_GAME_VERSION := "1.1.13.0"

static func version_tuple(v: String) -> Array:
	var out := []
	for part in v.split("."):
		out.append(int(part))
	return out

static func version_less(a: String, b: String) -> bool:
	var ta := version_tuple(a)
	var tb := version_tuple(b)
	for i in range(max(ta.size(), tb.size())):
		var x = ta[i] if i < ta.size() else 0
		var y = tb[i] if i < tb.size() else 0
		if x != y:
			return x < y
	return false

func _check_game_version() -> void:
	var pd = get_node_or_null("/root/ProgressData")
	var v = pd.get("VERSION") if pd else null
	if typeof(v) != TYPE_STRING:
		_set_mode("safe", "game version unreadable")
	elif version_less(v, MIN_GAME_VERSION):
		_set_mode("off", "game %s older than %s" % [v, MIN_GAME_VERSION])
	elif not (v in TESTED_GAME_VERSIONS):
		_set_mode("safe", "untested game version %s" % v)   # risky hooks off, QoL on
	else:
		_set_mode("full", "")
```

"safe" mode: keep low-risk QoL features, disable the features that override volatile vanilla methods
(combat, shop, wave flow) and online play. Tell the user once in the UI or log, not every frame.
Online: also put the game version and your protocol version into the lobby data and refuse mismatches
(`brotato-online-multiplayer`).

## 4. Feature flags and kill switch

```gdscript
const MOD_ID := "Author-ModName"
var flags := {"perf_log": false, "damage_meter": true, "online": true, "auto_shop": true}

func _load_flags() -> void:
	var cfg = ModLoaderConfig.get_current_config(MOD_ID)   # ModConfig or null
	if cfg != null and typeof(cfg.data) == TYPE_DICTIONARY:
		for key in flags:
			if cfg.data.has(key) and typeof(cfg.data[key]) == TYPE_BOOL:
				flags[key] = cfg.data[key]
	if "--author-modname-safe" in OS.get_cmdline_args():  # Steam launch option kill switch
		for key in flags:
			flags[key] = false
```

- Declare defaults in `manifest.json` under `extra.godot.config_schema` (ModLoader config; details in
  `brotato-modding`).
- Every risky feature checks its flag at its entry point, and the flag check is cheap (a bool member).
- Script extensions can't be uninstalled at runtime cheaply: put the flag check **inside** each override
  and fall through to `.method()` when off, so "off" really means vanilla behavior.

## 5. Circuit breaker

```gdscript
var _errors := {}            # feature -> count this session
const MAX_ERRORS := 5

func feature_failed(feature: String, detail: String) -> void:
	_errors[feature] = _errors.get(feature, 0) + 1
	log_event("warn", feature, detail)
	if _errors[feature] >= MAX_ERRORS and flags.get(feature, false):
		flags[feature] = false
		log_event("warn", feature, "disabled for this session after %d failures" % MAX_ERRORS)
```

Use it where a failure is detectable (lookup returned null, unexpected type, missing method). It turns a
per-frame error spam (lag + log flush + CrashReporter trigger) into one line and a disabled feature.

## 6. Error log with context

- Write your own file under `user://` (e.g. `user://author_modname/log.txt`); rotate at ~1 MB; keep 2 files.
- Every line: time, game version, mod version, scene, wave, online role (host/client/offline), feature, message.
- Rate-limit by key (same key at most once per 10 s, plus a counter of suppressed repeats).
- Keep a ring buffer of the last ~50 breadcrumbs in memory; dump it when an error is logged.
- `flush()` after warnings/errors only (a flush per line costs disk I/O).
- Do not route expected conditions through `push_error()`/`ModLoaderLog.error()`: each becomes an `ERROR:` line,
  is flushed to disk, and (with your `mods-unpacked` path in the text) can make Brotato's CrashReporter disable
  all mods next launch. Do not call `ModLoaderLog.*` in hot paths (it stores every entry in memory).

```gdscript
var _last_logged := {}       # key -> msec
var _suppressed := {}        # key -> count
var _crumbs := []            # ring buffer

func breadcrumb(text: String) -> void:
	_crumbs.append("%d %s" % [OS.get_ticks_msec(), text])
	if _crumbs.size() > 50:
		_crumbs.pop_front()

func log_event(level: String, key: String, msg: String) -> void:
	var now := OS.get_ticks_msec()
	if _last_logged.has(key) and now - _last_logged[key] < 10000:
		_suppressed[key] = _suppressed.get(key, 0) + 1
		return
	_last_logged[key] = now
	var line: String = "%s [%s] %s wave=%s scene=%s role=%s %s (suppressed %d)" % [
		Time.get_datetime_string_from_system(), level, key, _wave(), _scene_name(), _role(),
		msg, _suppressed.get(key, 0)]
	_suppressed[key] = 0
	_append_line(line, level != "info")
	if level == "error":
		for c in _crumbs:
			_append_line("  crumb " + c, false)
```

`_append_line(text, flush)` opens the file with `File.READ_WRITE` (or `File.WRITE` if it doesn't exist), calls
`seek_end()`, `store_line(text)`, `flush()` when asked, and keeps the `File` open between calls instead of
reopening per line. `_wave()`, `_scene_name()` and `_role()` must not throw: return `"?"` when unknown.

## 7. Crash-safe save

```gdscript
func save_json(path: String, data: Dictionary) -> bool:
	var tmp := path + ".tmp"
	var f := File.new()
	if f.open(tmp, File.WRITE) != OK:
		return false
	f.store_string(to_json(data))
	f.close()
	var check := File.new()                               # verify before replacing
	if check.open(tmp, File.READ) != OK:
		return false
	var parsed := JSON.parse(check.get_as_text())
	check.close()
	if parsed.error != OK:
		return false
	var dir := Directory.new()
	return dir.rename(tmp, path) == OK                    # Windows: target is deleted first

func load_json(path: String, defaults: Dictionary) -> Dictionary:
	for candidate in [path, path + ".tmp"]:               # .tmp survives a crash between delete and rename
		var f := File.new()
		if not f.file_exists(candidate) or f.open(candidate, File.READ) != OK:
			continue
		var parsed := JSON.parse(f.get_as_text())
		f.close()
		if parsed.error == OK and typeof(parsed.result) == TYPE_DICTIONARY:
			return _validated(parsed.result, defaults)    # per-key type checks, int() for numbers
	return defaults.duplicate(true)
```

- Add `"schema": N` to the file and migrate old schemas explicitly.
- Never save from `_process`; save on wave end, shop exit or config change.
- Don't call `OS.set_use_file_access_save_and_swap(true)` from a mod: it changes how the game writes its own files.

## 8. Detecting other mods

- `ModLoaderMod.is_mod_loaded("Other-ModId")` and `ModLoaderMod.get_mod_data_all()` (6.x) let you disable
  conflicting features instead of crashing. Declare known conflicts in `manifest.json`
  (`extra.godot.incompatibilities`) and order requirements with `dependencies`/`load_before`.
- For online sessions, compare the sorted `id@version` list between peers before the run starts.
