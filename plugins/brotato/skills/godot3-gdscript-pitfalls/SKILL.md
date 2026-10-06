---
name: godot3-gdscript-pitfalls
description: Stops Godot 4 syntax from leaking into Godot 3.x GDScript (3.5/3.6/3.7-dev, e.g. Brotato mods) - wrong-vs-right table for export/onready/yield/connect/super/setget/tool/instance/KinematicBody2D/Pool*Array/File/JSON, Godot 3 multilevel lifecycle callbacks, yield and signals, safe freeing, typing and parse errors, deferred calls, performance with many enemies/projectiles, debug-vs-release differences. Use whenever writing or reviewing GDScript for a Godot 3 project or mod, or on errors like "Unexpected '@'" or "Parse Error"; German triggers "Godot Fehler", "GDScript 3", "Godot 3 Syntax", "Script erweitern".
---

# Godot 3 GDScript pitfalls (for Godot 3.5-3.7-dev projects such as Brotato)

Default training data mixes Godot 3 and 4. In a Godot 3 project **one** Godot 4 token makes the whole script fail to parse, and in a mod that kills the mod. Brotato 1.1.15.x runs a custom Godot 3.7-dev build: everything below applies.

## Identify the version before writing code

| Evidence | Godot 3 | Godot 4 |
|---|---|---|
| `project.godot` | `config_version=4` | `config_version=5` |
| `.tscn`/`.tres` header | `format=2` | `format=3` |
| Scripts in the project | `onready var`, `yield(`, `.method(` | `@onready`, `await`, `super.` |
| Runtime | `Engine.get_version_info().major == 3` | `== 4` |

## Wrong (Godot 4) -> right (Godot 3)

| Topic | Godot 4 (wrong here) | Godot 3 (write this) |
|---|---|---|
| Export | `@export var speed := 5.0` | `export var speed := 5.0` |
| Export hints | `@export_range(0, 10) var n: int` | `export(int, 0, 10) var n = 0` |
| Enum/file export | `@export_enum("A","B")`, `@export_file("*.json")` | `export(int, "A", "B") var mode`, `export(String, FILE, "*.json") var path` |
| Onready | `@onready var label = $Label` | `onready var label = $Label` |
| Tool script | `@tool` | `tool` (first line) |
| Parent call | `super()`, `super.method(x)` | `.method(x)`; constructor args: `func _init(a).(a):` |
| Wait for signal | `await get_tree().create_timer(1.0).timeout` | `yield(get_tree().create_timer(1.0), "timeout")` |
| Next frame | `await get_tree().process_frame` | `yield(get_tree(), "idle_frame")` |
| Wait for coroutine | `await my_func()` | `yield(my_func(), "completed")` (only if it actually yielded) |
| Connect | `btn.pressed.connect(_on_pressed)` | `btn.connect("pressed", self, "_on_pressed")` |
| Connect with args | `sig.connect(f.bind(x))` | `obj.connect("sig", self, "_f", [x])` (binds appended after signal args) |
| One-shot | `sig.connect(f, CONNECT_ONE_SHOT)` | `obj.connect("sig", self, "_f", [], CONNECT_ONESHOT)` |
| Emit | `died.emit(self)` | `emit_signal("died", self)` |
| Signal check | `sig.is_connected(f)` | `obj.is_connected("sig", self, "_f")` |
| Callables / lambdas | `func(x): return x * 2`, `Callable(self, "f")` | not available: named method + `funcref(self, "f")`, `call("f")` |
| Deferred | `f.call_deferred(a)` | `call_deferred("f", a)` |
| Properties | `var hp: int: set = _set_hp, get = _get_hp` | `var hp: int setget _set_hp, _get_hp` |
| Typed arrays | `var a: Array[int]` | `var a: Array` (no element types) |
| Packed arrays | `PackedStringArray`, `PackedVector2Array` | `PoolStringArray`, `PoolVector2Array` (value-copied on assignment) |
| Instance scene | `scene.instantiate()` | `scene.instance()` |
| Change scene | `change_scene_to_file(p)`, `change_scene_to_packed(s)` | `get_tree().change_scene(p)`, `change_scene_to(s)` |
| Body 2D | `CharacterBody2D`, `velocity` prop + `move_and_slide()` | `KinematicBody2D`, `velocity = move_and_slide(velocity)` |
| Pause behaviour | `process_mode = PROCESS_MODE_ALWAYS` | `pause_mode = PAUSE_MODE_PROCESS` |
| Files | `FileAccess.open(p, FileAccess.READ)` | `var f = File.new(); if f.open(p, File.READ) == OK: ...; f.close()` |
| Directories | `DirAccess.open(p)` | `var d = Directory.new(); d.open(p)`; `d.list_dir_begin(true, true)` |
| JSON | `JSON.stringify(d)`, `JSON.parse_string(s)` | `JSON.print(d)` / `to_json(d)`; `var r = JSON.parse(s); if r.error == OK: r.result` |
| Paths | `dir.path_join("x")` | `dir.plus_file("x")` |
| Random | `randf_range(a, b)`, `randi_range(a, b)` | `rand_range(a, b)`, `a + randi() % (b - a + 1)` |
| Math renames | `deg_to_rad`, `snapped`, `str_to_var`, `var_to_str` | `deg2rad`, `stepify`, `str2var`, `var2str` |
| Empty checks | `arr.is_empty()`, `s.is_empty()` | `arr.empty()`, `s.empty()` |
| Array ops | `remove_at(i)`, `reverse()`, `slice(a, b)` end-exclusive | `remove(i)`, `invert()`, `slice(a, b)` **end-inclusive**, `end` required |
| Sorting | `arr.sort_custom(func(a, b): return a < b)` | `arr.sort_custom(self, "_cmp")` with `func _cmp(a, b) -> bool: return a < b` |
| Strings | `"%s" % x` (same), `String.num(x)` | `"%s" % x`, `str(x)`, `"%.2f" % x` |
| Time | `Time.get_ticks_msec()` (3.5+ also has `Time`) | `OS.get_ticks_msec()`, `OS.get_unix_time()` |
| Window | `DisplayServer.window_get_size()` | `OS.window_size`, `get_viewport().size` |
| Networking | `@rpc("any_peer")`, `multiplayer.get_remote_sender_id()`, `ENetMultiplayerPeer` | `remote func`/`master`/`puppet`/`remotesync`, `get_tree().get_rpc_sender_id()`, `NetworkedMultiplayerENet`, `get_tree().network_peer`, `is_network_master()` |
| Node name lookup | `get_node("%Unique")` | same (`%Unique` works since 3.5) |
| Tween | `create_tween().tween_property(...)` | same in 3.5+ (`SceneTreeTween`); the old `Tween` node also exists |

Full rename list (classes, methods, constants): [references/godot3-vs-godot4-api.md](references/godot3-vs-godot4-api.md) - read when an API name is not in this table.

## Exact parse errors that mean "Godot 4 syntax" or "reserved name"

| Message (Godot 3) | Cause |
|---|---|
| `Unexpected '@'` | any annotation |
| `Expected end of statement after expression, got Identifier instead.` / `The identifier "await" isn't declared in the current scope.` | `await`, lambda, Godot 4 statement |
| `Expected an identifier for the local variable name.` (`...member variable name.`, `...for an argument.`) | name equals a built-in function: `range`, `min`, `max`, `sign`, `str`, `len`, `abs`, `clamp`, `lerp`, `hash`, `load`, `print`, `char`, `ord`, `step_decimals`, `round`, `floor`, `seed`, `wrapi`, `ease`, `convert` |
| `Mixed tabs and spaces in indentation.` / `Unindent does not match any outer indentation level.` | indentation |
| `The function signature doesn't match the parent. Parent signature is: "..."` | override differs (debug builds only) |
| `The assigned value doesn't have a set type; the variable type can't be inferred.` | `:=` on a Variant (`dict["k"]`, `node.get("x")`, untyped call) - use `=` or an explicit type |
| `Couldn't fully preload the script, possible cyclic reference or compilation error.` | `preload` cycle -> `load()` |

## Lifecycle: Godot 3 calls callbacks on EVERY script level

Verified in the 3.x engine source (`call_multilevel`): for a script that `extends` another script, the engine itself runs the parent's and the child's version.

| Callback | Order | Consequence |
|---|---|---|
| `_init` | base -> child (constructor chain) | never call `._init()` |
| `_enter_tree`, `_ready`, `_draw` | base -> child | never call `._ready()`; base `onready` vars and base `_ready` already ran when yours runs |
| `_process`, `_physics_process`, `_exit_tree`, `_input`, `_unhandled_input`, `_unhandled_key_input`, `_gui_input`, `_notification` | child -> base | never call `._process(delta)`; you **cannot** stop the base from running by not calling it |

Ordinary methods (`func take_damage(...)`) are normal overrides: the parent runs only if you call `.take_damage(...)`. Details, `yield` and freeing rules: [references/engine-traps.md](references/engine-traps.md).

## yield and signals

- A function containing `yield` returns a `GDScriptFunctionState` at the first yield; the caller continues immediately. `.parent_method()` that yields behaves the same way.
- `yield(f(), "completed")` errors (`First argument of yield() is null.` / `... not of type object.`) if `f()` returned without yielding on that path - make every path yield or check `if r is GDScriptFunctionState`.
- A node freed while yielding gives `Resumed function 'f()' after yield, but class instance is gone.` Use a child `Timer` node or a one-shot connection for delays in nodes that can be freed (enemies, projectiles, scenes).
- `get_tree().create_timer(t)` keeps running while the tree is paused (`pause_mode_process` defaults to `true`). Pass `false` for gameplay delays: `get_tree().create_timer(t, false)`.
- `connect` is string-based: typos show only at emit time (`Error calling method from signal ...: Method not found.`). Connecting twice errors (`... is already connected to given method ...`); guard with `is_connected`.
- `connect()` returns an `int` error code; assign it (`var _err = obj.connect(...)`) to silence the unused-return warning.

## Freeing and references

- `queue_free()` deletes at the end of the frame; the node stays valid and in the tree until then (`is_queued_for_deletion()`). `free()` is immediate - never on a node currently processing or in a physics callback.
- A freed object is **not** `null`: `if obj:` is unreliable and calls fail with `... in base 'previously freed instance' ...`. Always `is_instance_valid(obj)`.
- `Reference`/`Resource` are refcounted; plain `Object.new()` leaks unless you call `free()`.
- `add_child`/`remove_child` while the parent is in `_ready` setup or a physics callback: use `call_deferred("add_child", n)` and `set_deferred("monitoring", false)` (`Parent node is busy setting up children...`, `Can't change this state while flushing queries...`).
- Resources from `load()` are cached and shared. Mutating one affects every user; `duplicate()` (shallow) or `duplicate(true)` before per-instance edits.

## Typing traps

- `5 / 2 == 2` (int division); use `5 / 2.0`. `"%d" % 3.9` -> `3`; `int(3.9)` -> 3 (truncates, use `round()`).
- Typed vars convert silently in places (`var i: int = 2.7` -> 2 with a narrowing warning).
- `Dictionary` keys: `1` and `1.0` are different keys; JSON numbers parse as `float` -> cast ids with `int()`.
- `{"a": 1} == {"a": 1}` is **false** in Godot 3 (dictionaries compare by reference; arrays compare by value). Use `deep_equal(a, b)` (3.5+).
- `PoolStringArray`/`PoolIntArray` are copied on assignment and when passed: `arr.append()` on a copy does not change the original.
- `for i in 3` and `for i in range(3)` both work; `range()` builds an array (avoid in hot loops with huge counts).
- `assert()` is stripped from release builds - never put side effects inside it.
- Use the enum constant, not literals: `PROPERTY_USAGE_SCRIPT_VARIABLE` is 8192 in Godot 3 (4096 in Godot 4), likewise `PAUSE_MODE_PROCESS`, `CONNECT_ONESHOT`.

## Performance with many enemies and projectiles

- No per-entity `_process` in mod code; react to signals (spawn, damage, death) or run one manager that iterates a cached list. `set_process(false)` when idle.
- Cache lookups: no `get_node`, `get_tree().get_nodes_in_group()`, `find_node()` or string building per frame; store references in `onready`/on spawn and validate with `is_instance_valid`.
- Hash/compute keys once (e.g. Brotato `Keys.generate_hash`) and keep them in member vars.
- `distance_squared_to` over `distance_to`; avoid allocating arrays/dictionaries every frame.
- `print`/`push_error`/logging per frame stalls the game (file I/O). Throttle with a counter.
- Respect pooling: if the game reuses enemies/projectiles, never `queue_free` them yourself, and reset per-entity state on reuse.
- Prefer one `_draw()` node over hundreds of `Label`s for overlays; update at 5-10 Hz, not every frame.

## Debug vs release (exported games are release builds)

| Check | Editor/debug | Shipped release game |
|---|---|---|
| Override signature mismatch | parse error | accepted; fails later on wrong arg count |
| `assert(cond)` | stops | removed |
| `sort_custom` bad comparator | `bad comparison function; sorting will be broken` | no check, may crash |
| "method isn't declared" on typed base | parse error | runtime `Invalid call. Nonexistent function ...` |

Test in the real game, not only in the editor.

## Checklist before handing over Godot 3 code

- [ ] No `@`, `await`, `super`, `func(` lambdas, `Array[T]`, `Packed*Array`, `instantiate`, `FileAccess`, `.connect(callable)`.
- [ ] Engine callbacks never call their `.` parent; normal overrides call `.method()` and return its value.
- [ ] Every `connect` method name exists; repeated connects guarded with `is_connected`.
- [ ] Nodes that may be freed are checked with `is_instance_valid`; no `yield` on timers inside short-lived nodes.
- [ ] No variable/argument named like a built-in function; tabs only.
- [ ] No per-frame lookups/allocations/logging in code that runs for every enemy or projectile.

## References

- [references/godot3-vs-godot4-api.md](references/godot3-vs-godot4-api.md) - extended Godot 3 <-> 4 rename table (classes, methods, constants, project/scene formats).
- [references/engine-traps.md](references/engine-traps.md) - lifecycle internals, yield/coroutines, signals, freeing, physics, input, UI, autoload order.
- [references/sources.md](references/sources.md) - sources and what was verified directly in engine source.
