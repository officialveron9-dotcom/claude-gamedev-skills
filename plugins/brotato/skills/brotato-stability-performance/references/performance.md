# Performance: FPS drops, stutter, memory growth

Godot 3.x only (1.1.7.1 logs show `v3.5.3`, 1.1.9.3 logs `v3.6.stable.custom_build`, builds since Feb 2026 a
custom `3.7.dev` per `brotato-modding`). Every API below exists in 3.5 and later 3.x. Brotato internals named here come from 1.1.14.x and may change.

## Contents
1. Budget and where the time goes
2. Measuring: editor profiler, monitors, in-game self-timing
3. Processing: `_process`, `_physics_process`, timers, time-slicing
4. Spawning: pooling vs instancing
5. Physics: Area2D counts, layers/masks, overlap queries
6. Hot-loop allocations, lookups, logging
7. Rendering: batching, particles, shader stutter, damage numbers
8. Memory: refcounting, cycles, orphans, pools

## 1. Budget and where the time goes

- At 60 FPS you get 16.6 ms per frame for everything, vanilla included. Late waves (and co-op, which raises
  enemy counts) already use most of it. Budget your mod at **≤ 1 ms per frame average, ≤ 3 ms worst frame**
  in a max-enemy wave on a mid-range PC (guidance, not an official number).
- **Physics steps multiply when FPS drops.** Godot 3 runs up to **8 physics steps per rendered frame**
  (hard-coded in `main.cpp`). At 30 FPS every `_physics_process` runs twice per frame. Expensive physics-tick
  code makes a slow frame slower (spiral). Keep non-physics work out of `_physics_process`.
- Vanilla already caps enemies: `EntitySpawner` compares `enemies.size()` with the wave's `max_enemies`
  (raised per extra co-op player) and kills the surplus (`enemies_removed_for_perf`). A mod that multiplies
  spawns (horde modes) must respect or raise that cap deliberately, and is then responsible for the frame rate.

## 2. Measuring

| Tool | Where | Use for |
|---|---|---|
| Debugger → Profiler, Network Profiler, Monitors, Video RAM | Recovered project run in the matching GodotSteam editor (setup: `brotato-modding`) | Per-function script time, physics/idle time, object/node/orphan counts, draw calls. The profiler does not count time spent waiting on servers (documented 3.x bug) |
| `Performance.get_monitor(Performance.X)` | Anywhere, including the shipped game | `TIME_PROCESS`, `TIME_PHYSICS_PROCESS` (seconds), `OBJECT_NODE_COUNT`, `OBJECT_ORPHAN_NODE_COUNT`, `OBJECT_COUNT`, `MEMORY_STATIC`, `RENDER_2D_ITEMS_IN_FRAME`, `RENDER_2D_DRAW_CALLS_IN_FRAME`, `PHYSICS_2D_ACTIVE_OBJECTS`, `PHYSICS_2D_COLLISION_PAIRS` |
| `OS.get_ticks_usec()` around a section | Your own code | Manual timing (official 3.x tip). Accumulate per second; never print per call |
| `rendering/batching/debug/diagnose_frame` | Editor project settings only | Prints batch breakdown; find what breaks batching |
| CLI `--print-fps`, `--debug-collisions`, `--frame-delay <ms>` | Only in debug export templates / editor | Unverified whether the shipped Brotato build accepts them; test before relying |

`Performance.add_custom_monitor()` does **not** exist in Godot 3 (4.x only). Keep your own counters.

### Frame-time logger a mod can ship (disabled by default via config)

```gdscript
# perf_probe.gd: add as a child of your mod_main node when config "perf_log" is true
extends Node

const REPORT_MSEC := 5000
const SPIKE_USEC := 33000                # longer than two 60 FPS frames

var _last_usec := 0
var _window_start := 0
var _frames := 0
var _worst_usec := 0
var _spikes := 0
var _sections := {}                      # section name -> accumulated usec

func _ready() -> void:
	pause_mode = Node.PAUSE_MODE_PROCESS
	_last_usec = OS.get_ticks_usec()
	_window_start = OS.get_ticks_msec()

func begin() -> int:
	return OS.get_ticks_usec()

func end(section: String, start_usec: int) -> void:
	_sections[section] = _sections.get(section, 0) + (OS.get_ticks_usec() - start_usec)

func _process(_delta: float) -> void:
	var now := OS.get_ticks_usec()
	var dt := now - _last_usec
	_last_usec = now
	_frames += 1
	if dt > _worst_usec:
		_worst_usec = dt
	if dt > SPIKE_USEC:
		_spikes += 1
	if OS.get_ticks_msec() - _window_start < REPORT_MSEC:
		return
	var parts := PoolStringArray()
	for key in _sections:
		parts.append("%s=%.2fms/f" % [key, _sections[key] / 1000.0 / max(_frames, 1)])
	print("[MyMod perf] fps=%d worst=%.1fms spikes=%d nodes=%d orphans=%d static_mb=%.1f draws=%d %s" % [
		Engine.get_frames_per_second(), _worst_usec / 1000.0, _spikes,
		Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
		Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT),
		Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0,
		Performance.get_monitor(Performance.RENDER_2D_DRAW_CALLS_IN_FRAME),
		parts.join(" ")])
	_frames = 0
	_worst_usec = 0
	_spikes = 0
	_sections.clear()
	_window_start = OS.get_ticks_msec()
```

Usage in a hot function: `var t = probe.begin()` … `probe.end("aura", t)`. One line every 5 s is fine; one
line per frame is not (see section 6). Compare runs with and without your mod on the same seed, wave and character.

Orphan count caveat: Brotato's `Main` pool calls `remove_child()` on pooled nodes, so pooled enemies,
projectiles and floating texts count as orphans. A high but **stable** orphan count is normal; a count that
grows wave after wave is a leak.

## 3. Processing

| Wrong | Right |
|---|---|
| `_process` on every entity your mod adds, checking a condition that rarely changes | Event-driven: connect to the vanilla signal (died, took_damage, wave end) or override the vanilla method that fires once |
| Polling `is_instance_valid(x)` every frame to detect death | `x.connect("tree_exiting", self, "_on_x_gone", [], CONNECT_ONESHOT)` |
| One `Timer` node or `create_timer()` per entity per tick | One manager node that iterates a list on a shared timer |
| Scanning all enemies every frame for a 0.5 s aura effect | Time-slice: process `enemies.size() / 10` per frame, or tick every 0.1-0.25 s |
| Work in `_physics_process` that is not physics | `_process`, or a lower-rate tick (see 8-step multiplier above) |
| Leaving processing on for hidden/idle helper nodes | `set_process(false)` / `set_physics_process(false)` until needed |

- In Godot 3, `_process`, `_physics_process`, `_ready`, `_enter_tree`, `_exit_tree` and the `_input` callbacks run
  on **every level** of a script-extension chain automatically. Calling `._physics_process(delta)` from an
  extension runs the vanilla body **twice per frame** (double cost, double effects). Details in [crashes.md](crashes.md).
- `SceneTree.create_timer(time, pause_mode_process = true)`: the default keeps running while the tree is paused
  (shop, pause menu). Pass `false` for gameplay timers.
- `VisibilityNotifier2D` (`screen_entered`/`screen_exited`) and `VisibilityEnabler2D` (`process_parent`,
  `physics_process_parent`, `pause_animations`, `pause_particles`, `pause_animated_sprites`, `freeze_bodies`)
  exist in 3.x. Use them only for **cosmetic** mod nodes: enemies off-screen must keep simulating, and in online
  play each peer's screen differs, so visibility-gated gameplay desyncs.

## 4. Spawning: pooling vs instancing

- `PackedScene.instance()` + `add_child()` + `queue_free()` for every projectile, pickup or label causes
  allocation churn and stutter when many die at once (end of wave, explosions).
- Brotato already pools: `Main.get_node_from_pool(pool_id, parent)` returns a recycled node (or `null` when the
  pool is empty) and `Main.add_node_to_pool(node, pool_id)` returns it; vanilla floating texts use
  `pool_id = Keys.generate_hash(scene.resource_path)` (1.1.14.x). Reuse this API for your own scenes instead of
  writing a second pool, and guard it as shown in [crashes.md](crashes.md) (stale entries, freed parents).
- **Pooled nodes keep state.** `_ready()` does not run again on reuse, but `_enter_tree()` does. Reset every
  field, meta, tween, timer and signal connection your mod adds; hook the re-init path (`init(...)` on units,
  or the pooled `enemy_respawned` signal listed in `brotato-modding`) rather than `_ready()`. Online: assign a fresh network ID on every reuse (see `brotato-online-multiplayer`).
- Pre-warm your own pool during wave start (spread over a few frames), not at the first explosion.
- Pools die with `Main`: vanilla frees all pooled nodes in `Main._exit_tree()`. Never keep pooled nodes across
  scene changes.

## 5. Physics

- Brotato's 2D layers (1.1.14.x project): 1 neutral, 2 player, 3 enemies, 4 player_projectiles,
  5 enemy_projectiles, 6 items, 7 gold, 8 obstacles, 9 bonus_gold, 10 pets, 11 pet_projectiles, 12 structures.
  Broadphase is the hash grid (`physics/2d/use_bvh=false`).
- Every mod `Area2D` that masks layer 3 (enemies) or 7 (gold) creates pairs with hundreds of bodies. Use the
  narrowest mask, a small shape, and `monitorable = false` when nothing needs to detect it.
- A large pickup-magnet area masking gold/items during a 300-material wave is a classic FPS drop. Prefer a
  distance check on a vanilla-maintained list at a low tick rate.
- `get_overlapping_bodies()`/`get_overlapping_areas()` allocate an Array and are only refreshed once per physics
  step. Use `body_entered`/`body_exited` signals and keep your own set.
- Toggling `monitoring`, `disabled` on shapes or adding/removing collision nodes inside a physics callback fails
  with `Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead.`
  Use `set_deferred("monitoring", false)` / `call_deferred(...)`.
- Prefer `Physics2DDirectSpaceState.intersect_point/intersect_shape` once per tick over spawning temporary areas.

## 6. Hot-loop allocations, lookups, logging

```gdscript
# WRONG: per frame, per enemy
func _process(_delta):
	for e in get_tree().get_nodes_in_group("enemies"):       # new Array every call
		var p = get_node("/root/Main/Players").get_child(0)     # path lookup every iteration
		var info = {"hp": e.current_stats.health, "pos": e.global_position}   # Dictionary per enemy
		print("enemy " + str(e.name) + " hp " + str(info.hp))   # string building + log I/O

# RIGHT: cache refs once per scene, reuse containers, no logging in the loop
var _player: Node = null
var _scratch := []

func on_wave_started(player: Node) -> void:   # called from your hook, not every frame
	_player = player

func _tick() -> void:                         # 4-10 Hz, not every frame
	if not is_instance_valid(_player):
		return
	_scratch.clear()
	for e in _enemies_source():               # vanilla-maintained list, see below
		if is_instance_valid(e) and not e.is_queued_for_deletion():
			_scratch.append(e)
```

- Prefer vanilla-maintained lists (e.g. the `enemies` array on `EntitySpawner` in 1.1.14.x) over
  `get_nodes_in_group()`. Don't mutate them; iterate a copy (`duplicate()`) if your loop can kill or free entries.
- Cache `has_method()`/`has_signal()` results per object (BrotatoOnline keeps a per-instance cache) instead of
  checking per frame.
- Strings: `str()`, `+`, `%` and `to_json()` allocate. Build strings only when you actually log or send.
- Network snapshots: don't build one Dictionary per entity per tick; reuse a `StreamPeerBuffer` (details in
  `brotato-online-multiplayer`).
- **Logging cost** (verified in Godot 3.5/3.6 source):
  - Errors (`push_error`, `printerr`, script errors) always flush the log file to disk. `print()` flushes on every
    line when `application/run/flush_stdout_on_print` is on (default on for debug builds).
  - `ModLoaderLog.*` (6.2.0/6.3.0) stores every call in `ModLoaderStore` (MD5 of the entry, plus a growing
    `stack` array for repeated messages) and emits `ModLoader.logged` **before** checking verbosity. A
    `ModLoaderLog.debug()` per frame costs CPU and grows memory even when debug logging is off. Each line that
    is written opens, seeks and closes `user://logs/modloader.log`.
  - Rule: no logging in per-frame or per-entity paths. Rate-limit (once per key per N seconds) everything else.

## 7. Rendering

- Brotato renders with GLES3 and has `fallback_to_gles2=true`. Logs show `Async. shader compilation: OFF`.
- **Batching (3.x 2D batching) breaks on**: texture change, material change, primitive type change; custom
  shaders that read/write `COLOR`/`MODULATE` or read `VERTEX` disable vertex baking; 2D lights add a pass per
  light. Use one atlas texture for all your mod sprites, share one `Material` instance (don't `duplicate()` per
  node), and avoid a unique `ShaderMaterial` per enemy (e.g. per-enemy outline/flash shaders).
- Watch `RENDER_2D_DRAW_CALLS_IN_FRAME` with and without your mod in the same scene.
- **Particles**: use `CPUParticles2D`. `Particles2D` (GPU) does not render on the GLES2 fallback, compiles a
  shader on first use and is slower on macOS. Keep `amount` small, `one_shot` for bursts, and pool emitters
  instead of instancing one per hit.
- **Shader compilation stutter**: with synchronous compilation, the first frame that draws a new shader or
  material variant blocks. Pre-warm at load: draw each mod material once (one tiny sprite at alpha 0.01,
  on-screen for 1-2 frames, during wave start or menu), then remove it. Don't create materials at runtime.
- **Damage numbers / labels**: vanilla floating text is pooled through `Main`'s pool. Mod text
  (extra damage numbers, DPS meters) must use the same pool or a capped pool; `Label` text changes re-shape
  text and re-layout. Update HUD labels at 4-10 Hz, not per frame, and only when the value changed.
- `_draw()`/`update()`: call `update()` only when the drawing changes; each `draw_*` call is a command.

## 8. Memory

- `Reference`/`Resource` are refcounted: freed when the last reference goes away, no GC pass. Two References
  that point at each other never free; break cycles with `weakref(obj)` and `wr.get_ref()`.
- `Node`/`Object` (not Reference) never free themselves: `remove_child()` without `queue_free()` leaks an orphan.
  `Object.new()` helpers must be `free()`d.
- Typical mod leaks: per-enemy entries in a mod Dictionary never erased (keyed by node or instance ID); signal
  connections from long-lived autoloads to short-lived nodes (auto-removed when the node is freed, but the
  autoload-side arrays aren't); `GDScriptFunctionState` from `yield` on a signal that never fires.
- Leak test: log `OBJECT_COUNT`, `OBJECT_NODE_COUNT`, `OBJECT_ORPHAN_NODE_COUNT`, `MEMORY_STATIC` at every wave
  start for 20+ waves (endless). Flat is good; a staircase is a leak. `Node.print_stray_nodes()` lists orphans
  (debug builds only).
- `ObjectDB instances leaked at exit` and `Resources still in use at exit` also appear in vanilla logs without
  mods; they are not proof of a mod leak.
