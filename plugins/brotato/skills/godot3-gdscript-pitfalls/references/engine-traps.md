# Godot 3 engine traps (verified against the 3.x branch source, version 3.7-dev)

## Contents
- Script inheritance and callbacks
- Autoload start-up order
- yield / coroutines
- Signals
- Freeing, pooling, references
- Deferred calls and physics
- Pause
- Input and UI
- Threads
- Performance checklist for swarms

## Script inheritance and callbacks

Engine callbacks are dispatched with `call_multilevel` / `call_multilevel_reversed`, i.e. on every script in the `extends` chain that defines the function:

| Callback | Dispatch | Order |
|---|---|---|
| `_ready`, `_enter_tree`, `_draw` | `call_multilevel_reversed` | base script first, then child |
| `_process`, `_physics_process`, `_exit_tree` | `call_multilevel` | child first, then base |
| `_input`, `_unhandled_input`, `_unhandled_key_input` | `SceneTree._call_input_pause` -> `call_multilevel` | child first, then base |
| `_gui_input` | `Viewport` -> `call_multilevel` | child first, then base |
| `_notification(what)` | `GDScriptInstance::notification` loops all levels | child first, then base |
| `_init` | constructor chain | base first; pass args with `func _init(x).(x):` |

Consequences:
- `._ready()`/`._process(delta)` inside an override executes the base a second time.
- You cannot suppress the base callback by overriding it. To change base behaviour, override the ordinary method the callback calls (e.g. the base `_process` calls `_update_x()`; override `_update_x`), or toggle `set_process(false)` and re-implement deliberately.
- `onready` vars initialise per level right before that level's `_ready`: base `onready` -> base `_ready` -> child `onready` -> child `_ready`.
- Ordinary methods and signal handlers are virtual: only the most-derived version runs unless you call `.method()`.
- Methods connected by name in a `.tscn` (`[connection signal="timeout" from="WaveTimer" to="." method="_on_WaveTimer_timeout"]`) resolve at emit time, so an extension override of `_on_WaveTimer_timeout` is called.
- Overriding a method that vanilla calls with `call_deferred("m")` or `connect(..., "m")` also works (string lookup).
- Override signature check (`The function signature doesn't match the parent...`) runs only in debug builds; it compares static-ness, return type, argument count/types and default count.

## Autoload start-up order

`main.cpp`: every autoload is first instanced in project order (its `_init` runs, its global name is set right after), then all are added to `/root` in the same order.

- During an early autoload's `_init`, later autoload globals are `null`.
- When an early autoload enters the tree, its `_ready` (and its children's) runs before later autoloads are in the tree; they exist as objects but their `_ready` has not run.
- Mods loaded by an early autoload (Godot Mod Loader) must therefore defer game-state access: `call_deferred("_setup")` or `yield(get_tree(), "idle_frame")` from `_ready`.
- `get_tree()` on a node not in the tree prints `Condition "!data.tree" is true. Returned: nullptr` and returns `null`.

## yield / coroutines

- `yield(obj, "signal")` suspends and returns a `GDScriptFunctionState` to the caller immediately; the caller does not wait. `yield()` without args suspends until someone calls `state.resume()`.
- To wait for another coroutine: `var s = f(); if s is GDScriptFunctionState: yield(s, "completed")`.
- Errors: `First argument of yield() is null.`, `First argument of yield() not of type object.`, `First argument of yield() is a previously freed instance.`, `Error connecting to signal: X during yield().`, `Resumed function 'f()' after yield, but class instance is gone.`
- A yield inside `_ready` ends `_ready` early from the engine's view; code after the yield runs later, after the parent and siblings already continued.
- Signals emitted before you start the `yield` are missed (no buffering).
- `get_tree().create_timer(sec, pause_mode_process := true)`: by default the timer ticks while the tree is paused. Use `create_timer(sec, false)` for gameplay delays.
- Yielding per entity (hundreds of suspended coroutines) is costly and dangerous with pooling; use one Timer or a manager.

## Signals

- `connect(signal, target, method, binds := [], flags := 0)` returns `OK` or an error code. Binds are appended after the signal's own arguments: handler signature = signal args + binds.
- Flags: `CONNECT_DEFERRED` (call at idle time), `CONNECT_PERSIST` (saved in scenes), `CONNECT_ONESHOT` (auto-disconnect after first emit), `CONNECT_REFERENCE_COUNTED`.
- Errors: `In Object of type 'X': Attempt to connect nonexistent signal 'y' to method 'Z.w'.`, `Signal "y" from "X" is already connected to given method "w" in "Z".`, `Disconnecting nonexistent signal 'y' ...`, at emit time `Error calling method from signal 'y': ...: Method not found.` or wrong argument count.
- Freed targets are disconnected automatically; freed emitters take their connections with them.
- The handler must accept signal args + binds; fewer parameters fail at emit time. For signals whose arity may change between game versions, add trailing parameters with defaults: `func _on_x(a, b = null, c = null):`.

## Freeing, pooling, references

- `queue_free()` is processed at the end of the frame; `free()` is immediate and unsafe during the object's own callbacks or physics.
- After freeing, variables still hold the object: `is_instance_valid(obj)` is the only safe test (`obj != null` is true for a freed object). Calls fail with `Attempt to call function 'f' in base 'previously freed instance' on a null instance.`
- `Object.new()` (non-`Reference`) leaks unless freed; `Node`s not added to the tree leak too (`print_stray_nodes()` lists them).
- Games with pools (Brotato reuses enemies and drops) keep nodes alive and re-emit spawn/respawn signals. Store per-entity data in a `Dictionary` keyed by `get_instance_id()` and clear it on despawn/respawn, or in `set_meta()` that you reset.
- `remove_child()` does not free; free it or add it elsewhere (`Can't add child 'x' to 'y', already has a parent 'z'.`).

## Deferred calls and physics

- During `_ready` chains: `Parent node is busy setting up children, add_node() failed. Consider using call_deferred("add_child", child) instead.`
- In physics callbacks (`body_entered`, `area_entered`) changing collision/monitoring: `Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead.` -> `set_deferred("monitoring", false)`, `call_deferred("queue_free")` is not needed (queue_free is already deferred).
- `Space state is inaccessible right now, wait for iteration or physics process notification.` -> do `direct_space_state` queries in `_physics_process`.

## Pause

- `get_tree().paused = true` stops nodes with `pause_mode = PAUSE_MODE_STOP` (and `INHERIT` under them). UI that must work in pause needs `PAUSE_MODE_PROCESS` on its root.
- `SceneTreeTimer` ignores pause by default (see yield section); `Timer` nodes respect `pause_mode`.

## Input and UI

- Input order per event: `_input` (reverse tree order) -> GUI (`_gui_input` on the control under the mouse / focus) -> `_unhandled_input` -> `_unhandled_key_input`.
- Stop propagation: `get_tree().set_input_as_handled()` (Godot 3) - not `get_viewport().set_input_as_handled()` (Godot 4).
- `_input` of later siblings runs first; a `CanvasLayer` added last under `/root` sees events before the current scene.
- Mouse picking for GUI ignores `CanvasLayer.layer` ordering in Godot 3 (tree order decides). Full-screen `Control`s with `mouse_filter = STOP` block clicks to anything behind; set `MOUSE_FILTER_IGNORE` on decorative containers.
- Controls with focus capture keyboard/gamepad navigation; overlay buttons in a gamepad-driven game should use `focus_mode = FOCUS_NONE`.
- `%UniqueName` (3.5+) only resolves inside the same scene owner.

## Threads

- `var t = Thread.new(); t.start(self, "_worker", userdata)`; the worker takes exactly one argument (`func _worker(userdata):`). Always `t.wait_to_finish()` before the object is freed.
- Never touch the scene tree from a thread; send results back with `call_deferred`. Guard shared data with `Mutex`.

## Performance checklist for swarms (hundreds of enemies/projectiles)

- No `_process` per spawned object added by your code; one manager node with a cached array.
- No `get_nodes_in_group`, `get_node`, `find_node`, `get_children()` scans per frame; maintain lists via spawn/despawn signals.
- Precompute keys, colors, fonts, strings; avoid `"%s" %` formatting and `str()` in per-frame paths.
- Prefer `distance_squared_to`; avoid `sqrt`, `atan2` per pair; never O(n^2) loops over all enemies x all projectiles in GDScript.
- Throttle UI updates (5-10 Hz) and redraws (`update()` only when data changed).
- Logging per frame (`print`, `push_warning`) is disk I/O; aggregate.
