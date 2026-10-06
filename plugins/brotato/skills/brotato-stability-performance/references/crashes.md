# Crashes and script errors

Godot 3.x behavior, verified in the engine source (3.5 and 3.6 branches; newer Brotato builds use a custom
3.7.dev build, same GDScript runtime family). Brotato internals from 1.1.14.x.

## Contents
1. What a "crash" is in Brotato, and the CrashReporter
2. Freed instances
3. `yield` and coroutines
4. Signals
5. `get_node` and scene changes
6. Physics-flush and busy-parent errors
7. Script extensions, game updates, load order
8. Recursion and hard crashes
9. Saves and corrupt data
10. Error message → cause → fix

## 1. What a "crash" is

| Kind | What happens | Where you see it |
|---|---|---|
| GDScript runtime error (null call, bad index, freed instance, wrong arg count) | **Debug-enabled build** (editor, debug export template): error printed, the **current function aborts**. **Release build**: nothing printed, the failing operation yields null and the function **continues**. Either way the game keeps running with half-applied state: stuck wave, shop that never opens, soft-lock | Debug-enabled only: `godot.log` `SCRIPT ERROR:` + `at: func (res://path.gd:line)` |
| Parse error in a mod script | That script fails to load; its extension is not applied (ModLoader then errors on the null script) | Always printed: `SCRIPT ERROR: Parse Error: ...` + `at: GDScript::reload (res://...gd:line)` |
| Engine `ERR_*` errors (`Node not found`, physics flush, signal connect) and `push_error` | Operation skipped, function continues | Always printed as `ERROR:` + `at: ...` |
| Hard crash (process exits) | Native fault: unbounded recursion (no GDScript stack check without a debugger), out of memory, engine bug | Log simply ends; no script error |

Which build is Brotato? Most likely **release**: vanilla opens its F2 debug menu only when
`OS.is_debug_build()` is true (a "DebugLoader" mod exists to unlock it), and mod authors cited in
`brotato-modding` test on the assumption that the shipped game is release. Counter-evidence: search snippets of
player logs on Steam show runtime `SCRIPT ERROR`s such as `Invalid call. Nonexistent function 'remove_effect' in
base 'Nil'`, which Godot 3 prints only in debug-enabled builds. Log `OS.is_debug_build()` once to confirm, and
write mod code that is correct under both behaviors (guard; don't rely on aborts or on errors being visible).

Logs (Windows): `%APPDATA%\Brotato\logs\godot.log` (+ up to 4 rotated `godot<timestamp>.log`),
`%APPDATA%\Brotato\logs\modloader.log`, and Brotato's own `%APPDATA%\Brotato\<steam_id>\log.txt`. The first
log line shows the engine version, the fifth the game version (`Brotato v1.1.x`).

**Brotato's CrashReporter (1.1.14.x)** is the first autoload. At startup it reads the previous session's
engine log. If any line containing `ERROR:` (this includes `SCRIPT ERROR:`), or the line after it, contains
`mods-unpacked`, or a line contains a mod-zip unzip error, it treats the last run as a mod crash, remembers the
mod folder name and **disables mods for that launch**. Consequences:
- A parse error in your mod (any build), or a runtime error in your script on a debug-enabled build (its `at:`
  line names `res://mods-unpacked/Author-Mod/...`), during a session = all mods off next start, reported as a
  crash of your mod.
- Never `push_error()`/`ModLoaderLog.error()` messages that contain your `mods-unpacked` path for non-fatal
  conditions. Use `print()` or a warning to your own file for expected situations.
- Fix every `SCRIPT ERROR` that names your files before release, even "harmless" ones.

## 2. Freed instances

Godot 3: a variable pointing at a freed Object is **not** set to null. Debug builds call it `previously freed
instance`; `is_instance_valid()` returns false for it in all builds. `queue_free()` frees at the end of the
frame, so a node can be valid but queued.

```gdscript
# Use one helper everywhere (order matters: `is` on a freed object is itself an error)
static func alive(o) -> bool:
	return is_instance_valid(o) and not (o is Node and o.is_queued_for_deletion())

# WRONG
func _on_timer() -> void:
	_target.take_damage(10)             # target died 0.3 s ago: SCRIPT ERROR, function aborts

# RIGHT
func _on_timer() -> void:
	if not alive(_target):
		_target = null
		return
	_target.take_damage(10)
```

- Store `weakref(node)` (or `get_instance_id()` + `instance_from_id(id)`) for references that may outlive the
  target, and check the result each use. `wr.get_ref()` returns null once the object is freed.
- Pooled nodes are worse than freed ones: the reference stays valid but now points at a **different** enemy
  (Brotato reuses enemies, projectiles, pickups and floating texts). Re-validate identity with your own ID or
  meta set on (re)init, and clear your references when the node returns to the pool.
- Freeing inside a signal emitted by that object: `Attempted to free a locked object (calling or emitting).`
  Use `queue_free()` (or `call_deferred("free")`).
- Freed while iterating: `for e in list` where `list` is modified during the loop skips elements. Iterate
  backwards by index or over `list.duplicate()`.

Patterns seen in a released online mod (BrotatoOnline, Brotato 1.1.15.4) and why they were needed:
- Vanilla `Main._exit_tree()` frees every pool entry; stale/queued nodes left in `_pool` crash it. Prune
  invalid entries before calling the parent.
- `get_node_from_pool(id, parent)` calls `parent.add_child()`; during end-of-wave cleanup the parent
  (e.g. the enemy-projectile container) can already be queued. Check the parent before calling the parent method.
- Player cleanup called `stop()` on a `CPUParticles2D` already freed by `die()`; a pet kept a freed owner and
  crashed in `_physics_process` on `global_position`; the focus emulator emitted a signal with a freed Control.
  Same fix every time: `alive()` checks at the boundary, then defer to vanilla.

## 3. `yield` and coroutines

```gdscript
# WRONG: resumes on a node that was freed during the wait
func flash() -> void:
	modulate = Color.red
	yield(get_tree().create_timer(0.2), "timeout")
	modulate = Color.white   # ERROR: Resumed function 'flash()' after yield, but class instance is gone.

# RIGHT: callback on self; Godot removes the connection when self is freed
func flash() -> void:
	modulate = Color.red
	get_tree().create_timer(0.2, false).connect("timeout", self, "_end_flash", [], CONNECT_ONESHOT)

func _end_flash() -> void:
	modulate = Color.white
```

- `yield(obj, "signal")` where `obj` is freed or never emits: the function never resumes, its
  `GDScriptFunctionState` leaks, and any logic after the yield (wave end, unlocking input) never runs.
- `yield(null_or_freed, ...)`: `First argument of yield() is null.` / `... is a previously freed instance.`
- A caller that does `yield(my_coroutine(), "completed")` breaks if `my_coroutine()` returns without yielding
  on some path. Keep coroutine control flow simple; prefer signals and state machines in mod code.
- `create_timer(t)` defaults to `pause_mode_process = true`: it fires while the shop or pause menu is open.

## 4. Signals

- `connect()` twice: `Signal 'x' is already connected to given method 'y' in that object.` Guard with
  `if not a.is_connected("x", self, "y"):`. Pooled nodes are the usual source (connect in `init()` each reuse).
- `disconnect()` of a missing connection: `Attempt to disconnect a nonexistent connection ...`. Guard with
  `is_connected()`.
- `Error calling method from signal 'x': ...` usually means the callback signature changed (game update added
  an argument). Accept extra arguments with defaults, or connect with `binds` that match.
- Connections are removed automatically when **either** object is freed, but your own arrays/dicts are not.
- `CONNECT_DEFERRED` callbacks run after the current frame's processing; validate `alive()` inside them.

## 5. `get_node` and scene changes

- `get_node("path")` on a missing node logs `Node not found: "path" (relative to "...")` and returns null; the
  next call on it aborts your function. Use `get_node_or_null()` and handle null.
- Paths into vanilla scenes (`/root/Main/...`) break when Brotato renames or restructures nodes in an update.
  Resolve them in one place, with a null check and a single warning (not per frame).
- `get_tree().change_scene()` is deferred: `current_scene` still reports the old scene for a moment, and the old
  scene's nodes are freed at the swap. Cached references from the old scene become invalid; timers, tweens and
  network messages addressed to it must be dropped (scene epoch, see `brotato-online-multiplayer`).
- Run end / quit to menu frees `Main` and every pooled node. Clear all mod caches on scene exit
  (`tree_exiting` of `Main`, or `SceneTree` `node_removed` filtered to the scene root).

## 6. Physics-flush and busy-parent errors

| Message | Cause | Fix |
|---|---|---|
| `Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead.` | Toggling `monitoring`/`monitorable`, shape `disabled`, or adding/removing collision objects inside `body_entered`/`area_entered` or other physics callbacks | `set_deferred("monitoring", false)`, `call_deferred("add_child", n)` |
| `Parent node is busy setting up children, add_node() failed. Consider using call_deferred("add_child", child) instead.` | `add_child()` during the parent's `_ready()`/`_enter_tree()` | `call_deferred("add_child", child)` |
| `Can't add child 'X' to 'Y', already has a parent 'Z'.` | Re-adding a pooled/reused node without removing it, or double `add_child` | `if n.get_parent(): n.get_parent().remove_child(n)` first |
| `Message queue out of memory. Try increasing 'memory/limits/message_queue/max_size_...'` | Thousands of `call_deferred`/`set_deferred`/deferred signals per frame | Batch deferred work into one deferred call per frame; a mod cannot raise the project setting |

## 7. Script extensions, game updates, load order

Extension mechanics belong to `brotato-modding`; these are the parts that cause crashes or lag:

1. **Virtual callbacks run on every level (Godot 3).** `_ready`/`_enter_tree` run base first, then your
   extension; `_process`/`_physics_process`/`_exit_tree` run your extension, then the base. You cannot skip
   the vanilla body by returning early, and calling `._ready()` or `._physics_process(delta)` runs vanilla
   **twice**. (BrotatoOnline documents the doubled `Main._ready()` duplicating `EntitySpawner.init()`.) To change
   vanilla per-frame behavior, override a regular method that the callback calls.
2. **Always chain regular overrides**: `return .method(args)` (keep the return value). Not calling the parent
   silently breaks every other mod extending the same method (ModLoader chains extensions: the second mod's
   script extends the first's).
3. **Infinite recursion**: writing `method(args)` instead of `.method(args)` inside the override calls itself.
   No stack-overflow error without a debugger attached; the process just dies.
4. **Game update changed a signature.** Debug-enabled builds (and the editor) reject the extension:
   `Parse Error: The function signature doesn't match the parent. Parent signature is: "..."` (this check is
   compiled only with `DEBUG_ENABLED`). Release builds load it, and vanilla's calls with the new arity then fail
   (`Invalid call to function 'x' ... Expected N arguments.` in debug-enabled builds, silently in release).
   Renamed or removed members referenced in your script → `The identifier "x" isn't declared in the current
   scope.` in every build; calls to removed methods → `Invalid call. Nonexistent function 'x' in base 'Y'.`
   A parse failure means **none** of that file's overrides apply. Keep one small extension file per vanilla
   script, and re-diff hooked methods after every patch. Test in the editor (debug) to catch mismatches early.
5. **Load order**: ModLoader 6.x sorts by "importance" (number of mods depending on you) only, with a
   non-stable sort. Without `dependencies`/`load_before` in `manifest.json`, assume no particular order.
6. **Too early**: ModLoader is an autoload that runs mods' `mod_main._init()` while autoloads listed after it
   (`ProgressData`, `RunData`, `ItemService`, ...) are still null. In `_init()` only install extensions and
   translations; touch game singletons from `_ready()` or later, and game state only after it is initialized
   (e.g. on the first relevant signal or scene).
7. ModLoader stores `compatible_game_version` from the manifest but does **not** enforce it; check the version
   yourself ([defensive-patterns.md](defensive-patterns.md)).

## 8. Recursion and hard crashes

- GDScript checks call depth (`Stack Overflow (Stack Size: 1024)`) only when a script debugger is attached
  (editor runs). In the shipped game, unbounded recursion crashes the process without a script error.
- Common sources: override calling itself (above), a signal handler that triggers the same signal (e.g. your
  `on_damage_taken` deals damage), stat recalculation that calls itself through a setter. Add a re-entrancy
  guard: `if _busy: return` / `_busy = true` … `_busy = false`.
- `Array.sort_custom(obj, "cmp")` with an inconsistent comparator (`<=`, randomness, values that change during
  the sort): debug builds print `bad comparison function; sorting will be broken`, release builds skip the check
  and can read out of bounds and crash. Comparators must be strict (`a < b`) and deterministic.
- Out-of-memory: unbounded arrays/dicts (per-hit history, logs kept in memory), mass instancing with no cap.

## 9. Saves and corrupt data

- Godot 3 `File.open(path, File.WRITE)` truncates in place unless save-and-swap is enabled globally (it is off by
  default). A crash mid-write leaves an empty or partial file. Write `path + ".tmp"`, `close()`, then
  `Directory.rename(tmp, path)` (on Windows Godot deletes the target first, so also try `.tmp` on load).
- On load: `File.file_exists`, `JSON.parse(text)` → check `result.error == OK` and `typeof(result.result) ==
  TYPE_DICTIONARY`, then validate every key and type; fall back to defaults (and keep the bad file as `.bad`).
- JSON turns every number into float: `Array.has(5)` fails on `[5.0]`, and dictionary keys become strings.
  Convert with `int()` on load. Large ints (Steam IDs) lose precision; store them as strings.
- Never put Objects, Resources or node references in data you save or put into Brotato's run state;
  `to_json()` writes `"[Object:1234]"` and the next load breaks. Store `my_id` strings.
- Brotato writes `user://<steam_id>/save_v2.json` plus rotating `.bak` backups (1.1.7-1.1.9 logs). Keep your
  mod's data in its own file; if you must extend the vanilla run state, add one namespaced key and make the
  game tolerate its absence (players load saves without your mod).
- Save only on events (wave end, shop exit, config change), never per frame.

## 10. Error message → cause → fix

| Message (Godot 3.x text) | Cause | Fix |
|---|---|---|
| `Attempt to call function 'x' in base 'previously freed instance' on a null instance.` / `Invalid get index 'x' (on base: 'previously freed instance').` | Stored reference to a freed node | `alive()` check; weakref; clear refs on `tree_exiting` |
| `Invalid get index 'x' (on base: 'Nil').` / `Invalid call. Nonexistent function 'x' in base 'Nil'.` | Null from `get_node`, a missing singleton (used in `_init`), or a failed lookup | `get_node_or_null` + guard; move code out of `_init` |
| `Invalid call. Nonexistent function 'x' in base 'Y'.` | Method removed/renamed by a game update or another mod | `has_method` guard at the boundary; update hooks |
| `Invalid call to function 'x' in base 'Y'. Expected N arguments.` | Signature changed (update) | Match the new signature; defaults for new args |
| `Parse Error: The function signature doesn't match the parent. Parent signature is: "..."` (debug-enabled builds/editor only) | Your override's arguments differ from the vanilla method after an update | Copy the new signature exactly |
| `Parse Error: The identifier "x" isn't declared in the current scope.` | Vanilla variable/class removed or renamed, or a DLC-only class | Update; use `get()`/`"x" in obj` for optional members |
| `Resumed function 'f()' after yield, but class instance is gone.` | `yield` outlived its node | Timer/signal callbacks instead of yield |
| `Left operand of 'is' was already freed.` | `x is Type` on a freed object | `is_instance_valid(x)` first |
| `Trying to assign value of type 'Nil' to a variable of type 'int'.` (and similar) | Typed var receives null from a failed call | Check before assigning; untyped temp |
| `Invalid type in function 'x' in base 'Y'. Cannot convert argument 1 from float to int.` | JSON/network numbers are floats | `int()` conversion at the boundary |
| `Signal 'x' is already connected to given method 'y' in that object.` | Double connect (pooled node, re-entered scene) | `is_connected()` guard |
| `Attempted to free a locked object (calling or emitting).` | `free()` inside the object's own signal | `queue_free()` |
| `Error calling deferred method: ...` | Deferred call to a freed or changed target | Validate in the callee; pass IDs not nodes |
| `Message queue out of memory ...` | Deferred-call flood | One deferred batch per frame |
| Mods disabled on startup ("Unexpected error in mod X. Mods have been temporarily disabled.", text as reported in `brotato-modding`) | CrashReporter found an `ERROR:` line with `mods-unpacked` in the last log | Fix the error; don't push errors with your path for expected cases |
| Game closes with no error, log just ends | Infinite recursion or native crash | Re-entrancy guards; bisect with feature flags; run in the editor to get `Stack Overflow` |
| Wrong values / soft-lock but **no** error in the log | Release build: runtime errors are silent and execution continues with null | Reproduce in the editor (debug) or add guards + your own log at the suspected boundary |
