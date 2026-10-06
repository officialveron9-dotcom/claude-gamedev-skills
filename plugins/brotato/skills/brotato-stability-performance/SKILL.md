---
name: brotato-stability-performance
description: Prevents and fixes lag, FPS drops, stutter, crashes, memory leaks and online disconnects in Brotato mods (Godot 3.x GDScript, Mod Loader) - Brotato's node pool, per-frame cost, Area2D/physics, batching, particles, profiling and self-timing, freed-instance and yield errors, script extensions breaking after game updates, CrashReporter disabling mods, crash-safe saves, heartbeats and timeouts, symptom tables and a pre-release checklist. Use for Brotato mod lag, FPS, performance, object pooling, crash, freed instance, memory leak, disconnect, timeout, or German "Lag", "ruckelt", "Absturz", "stürzt ab", "Verbindungsabbruch", "Performance", "FPS".
---

# Brotato mods: no lag, no crash, no disconnect

Baseline (checked 2026-10-06; re-check after every game patch):
- Brotato 1.1.x runs a custom **Godot 3.x** build: `v3.5.3` in 1.1.7.1 logs, `v3.6.stable` in 1.1.9.3 logs, and
  `3.7.dev` since the Feb 2026 update according to `brotato-modding`. Line 1 of `godot.log` tells you. Write
  Godot 3 GDScript only (`yield`, `.method()`, `connect("sig", self, "m")`, `pause_mode`). Every API used here
  exists in 3.5 and later 3.x versions.
- The shipped game is most likely a **release** build: vanilla gates its F2 debug menu on `OS.is_debug_build()`,
  and `brotato-modding` reports the same. Godot 3 release builds skip runtime script-error checks, signature
  checks and sort validation. Log `OS.is_debug_build()` once at startup to confirm.
- Related skills: `brotato-modding` (Mod Loader, script extensions, decompiling, internals),
  `godot3-gdscript-pitfalls` (Godot 3 vs 4 syntax), `brotato-online-multiplayer` (netcode, sync, desync).
  This skill only covers stability and performance.

## 1. Lag rules

1. **Budget**: aim for ≤ 1 ms/frame average and no new spikes in a max-enemy wave. Late waves and co-op
   already use most of the 16.6 ms.
2. **No per-frame scans** over enemies, projectiles or pickups. Hook the vanilla event (death, hit, wave
   end) or tick at 4-10 Hz and time-slice. `get_nodes_in_group()` and `get_overlapping_*()` allocate arrays.
3. **No per-entity `_process`** for mod logic. Use one manager node. Turn processing off when idle.
4. **Keep `_physics_process` lean.** Godot 3 runs up to 8 physics steps per frame when FPS drops, so physics-tick
   cost multiplies exactly when the game is already slow.
5. **Pool, don't churn.** Reuse Brotato's `Main.get_node_from_pool(id, parent)` / `add_node_to_pool(node, id)`
   for mod effects and texts. Pooled nodes keep state, and `_ready()` doesn't run again, so reset in the re-init hook.
6. **Narrow collision masks.** Mod `Area2D`s that mask enemies (layer 3) or gold (layer 7) pair with hundreds of
   bodies. Set `monitorable = false` when nothing detects the area. Toggle physics state with `set_deferred`.
7. **No logging in hot paths.** Errors always flush the log to disk, and every `ModLoaderLog.*` call is hashed and
   stored in memory before the verbosity check. Rate-limit everything.
8. **Rendering**: one atlas, one shared material, `CPUParticles2D` (GPU particles don't render on Brotato's GLES2
   fallback), pre-warm shaders (logs show `Async. shader compilation: OFF`), and update HUD labels only on change.
9. **Respect the vanilla enemy cap** (`max_enemies`, `enemies_removed_for_perf`). Mods that raise it own the frame rate.

## 2. Crash rules

1. **Validate every stored reference** before use. In Godot 3, freed objects are not null:
   `is_instance_valid(o) and not o.is_queued_for_deletion()`. Pooled nodes can be valid but a *different* enemy.
2. **Don't `yield` across lifetimes.** Use `create_timer(t, false).connect("timeout", self, "_m", [], CONNECT_ONESHOT)`.
   Godot removes the connection when `self` is freed. `yield` resumes into
   `Resumed function '...' after yield, but class instance is gone`.
3. **Virtual callbacks run on every extension level.** Never call `._ready()`, `._process(d)` or
   `._physics_process(d)` from an extension. That runs vanilla twice, and an early `return` can't skip vanilla.
4. **Always chain regular overrides**: `return .method(args)`. If you skip it, other mods' extensions break. If you
   write `method(args)` instead, it recurses forever and the game closes without a stack-overflow message.
5. **Game updates break signatures.** In debug-enabled builds a mismatched override is a parse error, and the
   whole extension file is dropped. In release builds it loads, and calls with the new arity then fail silently.
   Renamed members are parse errors in both. Keep one small file per vanilla script, gate on the game version,
   and ship a safe mode.
6. **`mod_main._init()` runs before `ProgressData`, `RunData` and the other later autoloads exist.** Only
   install extensions there.
7. **Physics-callback changes** use `set_deferred()`/`call_deferred()`
   (`Can't change this state while flushing queries...`).
8. **Saves**: write `.tmp`, verify, rename. Validate types on load, because JSON numbers come back as floats.
   Never save Objects.
9. **Brotato's CrashReporter** (1.1.14.x) disables all mods for the next launch ("Mods have been temporarily
   disabled") if the previous `godot.log` has an `ERROR:`/`SCRIPT ERROR:` line mentioning `mods-unpacked`.
   Parse errors always qualify. Ship with zero script errors, and never `push_error()` expected conditions that
   contain your mod path.
10. **A GDScript runtime error never closes the game.** Release builds print nothing and continue with null.
    Debug-enabled builds (the editor) print `SCRIPT ERROR` and abort the current function. Either way the result is
    wrong state or a soft-lock (wave never ends, shop never opens). Some player logs on Steam do show runtime
    `SCRIPT ERROR`s, so design for both behaviors. Reproduce in the editor to see the first error. A bad
    `sort_custom` comparator is only reported in debug builds, and in release builds it can crash.

## 3. Wrong vs right

```gdscript
# WRONG: per-frame scan + allocation + log spam
func _process(_d):
	for e in get_tree().get_nodes_in_group("enemies"):
		if e.global_position.distance_to(_player.global_position) < 200:
			ModLoaderLog.debug("near " + str(e), MOD_ID)
# RIGHT: low-rate tick, cached refs, squared distance, no logging in the loop
var _acc := 0.0
func _process(delta):
	_acc += delta
	if _acc < 0.2 or not alive(_player):
		return
	_acc = 0.0
	var p: Vector2 = _player.global_position
	for e in _enemy_list():                 # vanilla-maintained list, iterate a copy if you may free entries
		if alive(e) and e.global_position.distance_squared_to(p) < 40000.0:
			_near_count += 1
```

```gdscript
# WRONG: extension of a vanilla per-frame callback
func _physics_process(delta):
	if not _enabled:
		return                    # vanilla still runs (Godot 3 calls every level)
	._physics_process(delta)      # ...and now vanilla runs a second time
	_extra_logic()
# RIGHT: only add your logic; to change vanilla, override the regular method it calls
func _physics_process(_delta):
	if _enabled:
		_extra_logic()
```

```gdscript
# WRONG: crashes after a death/scene change
var _target
func _on_tick():
	_target.take_damage(5)
# RIGHT
func _on_tick():
	if not alive(_target):
		_target = null
		return
	_target.take_damage(5)

static func alive(o) -> bool:
	return is_instance_valid(o) and not (o is Node and o.is_queued_for_deletion())
```

## 4. Measure, don't guess

- Editor (recovered project in the matching GodotSteam editor, see `brotato-modding`): Profiler, Monitors
  (objects, nodes, orphans, draw calls, physics pairs).
- Shipped game: `Performance.get_monitor(...)` plus `OS.get_ticks_usec()` section timing, aggregated and printed
  once per 5 s behind a config flag. `Performance.add_custom_monitor` does not exist in Godot 3.
  Copy-ready probe: [references/performance.md](references/performance.md) section 2.
- Brotato's pool keeps pooled nodes out of the tree, so the orphan count is high by design. Watch the trend
  across waves, not the absolute value.
- Always compare with and without the mod on the same character, wave and build.

## 5. Online (details: `brotato-online-multiplayer`)

- Every network node: `pause_mode = Node.PAUSE_MODE_PROCESS`. Brotato pauses on focus loss, and a paused
  receive loop means timeouts.
- App-level heartbeat (1-2 s, timeout ~8-15 s) plus host-gone handling (back to menu cleanly).
- Main-thread stalls longer than the transport timeout drop peers. ENet defaults: 5 s minimum, 30 s maximum.
- Unreliable, small snapshots. Reliable only for events. Chunk big payloads across frames. Cap the messages
  handled per frame. Throttle polling at uncapped FPS.
- Tag messages with a scene epoch, and drop stale ones after scene changes.
- Test with 2-4 real players under 100-150 ms latency and 2-5 % loss.
  Table and reference numbers: [references/online-stability.md](references/online-stability.md).

## 6. Top symptoms (full list: [references/common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| FPS drops late in a wave | Mod cost scales with entity count (scans, groups, wide Area2D masks) | Events + low-rate tick + narrow masks |
| Stutter when many enemies die | Per-death instancing, logging or heavy handlers | Pool, cap per frame, no per-death logs |
| Hitch the first time an effect shows | Synchronous shader compile | Pre-warm materials; `CPUParticles2D` |
| Memory grows each wave | Per-enemy dict entries never cleared, Reference cycles, never-resumed `yield` | Clear on wave end, `weakref`, signals instead of yield |
| Crash at run end / quit to menu | Refs into freed `Main`/pool nodes, timers resuming after scene change | Clear caches on scene exit, `alive()` checks, timers connected to `self` |
| Crash after a game update | Changed signatures/renamed members in hooked scripts | Diff hooked scripts, fix signatures, version gate + safe mode |
| All mods disabled on next start | CrashReporter saw an error mentioning `mods-unpacked` | Fix the script error; no expected errors via `push_error` |
| Freeze when host opens shop | Huge reliable blob in one frame, or a phase message lost during the scene change | Chunk, epoch, ack/resend |
| Client disconnects after N minutes | No heartbeat, paused net node, stalls, growing send queue | Heartbeat on PROCESS node, short stalls, capped queues |
| Game closes without error | Infinite recursion (override calls itself, signal ping-pong) | `.method()`, re-entrancy guard |

## 7. Pre-release checklist (full: [references/release-checklist.md](references/release-checklist.md))

- [ ] Max-enemy wave (endless 25+ or a dev-only `DebugService` stress setup) with vs without the mod: ≤ 1 ms avg, no new spikes.
- [ ] 20+ waves: object, node and memory counts flat.
- [ ] Online: 2-4 players with simulated latency and loss, plus host/client pause, alt-tab, quit and reconnect.
- [ ] Current Brotato version: hooked scripts re-diffed, no `Parse Error`, full smoke path through run end.
- [ ] `godot.log`/`modloader.log`: zero errors naming your mod. No repeated warnings.
- [ ] Manifest versions bumped. Perf/debug flags off. The Workshop zip is tested on a clean profile and with popular mods.

## References

- [references/performance.md](references/performance.md): budgets, profiling and the probe, processing,
  pooling, physics, allocations and logging cost, rendering, memory. Read when optimizing or measuring.
- [references/crashes.md](references/crashes.md): crash kinds, CrashReporter, freed instances, yield, signals,
  scene changes, extensions/updates/load order, recursion, saves, and an error message → fix table. Read for any error.
- [references/defensive-patterns.md](references/defensive-patterns.md): guards, safe calls, version gate,
  feature flags/kill switch, circuit breaker, context logger, crash-safe save, mod detection.
- [references/online-stability.md](references/online-stability.md): disconnect/net-lag causes, reference numbers, test plan.
- [references/common-issues.md](references/common-issues.md): symptom → cause → fix for lag, memory, crashes, online.
- [references/release-checklist.md](references/release-checklist.md): per-release checklist.
- [references/sources.md](references/sources.md): where each fact comes from.
