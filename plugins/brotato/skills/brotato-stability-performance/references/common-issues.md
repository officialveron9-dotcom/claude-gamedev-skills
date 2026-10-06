# Common issues: symptom → cause → fix

Brotato 1.1.x on Godot 3.x (3.5.3 → 3.6 → custom 3.7.dev). Add a row here when a bug is solved (exact symptom or message, cause, fix,
game version). Error-message lookups: [crashes.md](crashes.md) section 10.

## Lag and FPS

| Symptom | Likely cause | Fix |
|---|---|---|
| FPS fine early, drops late in a wave (worse in co-op) | Mod work scales with enemy/projectile/pickup count: per-frame loops over all enemies, `get_nodes_in_group()`, Area2D masking enemies or gold, per-enemy `_process` | Event-driven hooks; time-slice loops at 4-10 Hz; narrow collision masks; measure with the perf probe ([performance.md](performance.md) section 2) |
| Stutter spike when many enemies die at once / at wave end | Per-death `instance()`/`queue_free()` of mod effects, per-death logging, per-death signal handlers doing heavy work, freeing big Dictionaries at once | Pool effects via `Main`'s pool; cap effects per frame; no logging per death; defer bulk cleanup over frames |
| Stutter the first time a mod effect appears, then smooth | Synchronous shader compilation (logs: `Async. shader compilation: OFF`) for a new material/shader or `Particles2D` | Pre-warm materials at load; use `CPUParticles2D`; share one material instance |
| FPS drop only while a mod UI/meter is visible | Label text set every frame, `_draw()`/`update()` every frame, many Controls | Update at 4-10 Hz and only on change; one `Label` per value, no rebuilds |
| Slow frames get even slower (spiral) | Heavy `_physics_process` code; Godot 3 runs up to 8 physics steps per frame when FPS drops | Move non-physics work to `_process` or a low-rate tick |
| Per-frame cost doubled after adding an extension | Extension calls `._physics_process(delta)`/`._process(delta)`; Godot 3 already calls the vanilla callback | Remove the explicit parent call for virtual callbacks |
| Lag spikes every few seconds, log file grows fast | Error/print spam: errors always flush the log to disk; `ModLoaderLog` calls store entries in memory | Fix the error source; rate-limit logs; no `ModLoaderLog.debug` in hot paths |
| Draw calls jump with the mod | Unique textures/materials per node, custom shader per enemy, 2D lights | Atlas textures, shared material, avoid per-node `ShaderMaterial` and lights |
| Horde/multiplier mod: enemies vanish or FPS collapses | Vanilla `max_enemies` cap kills extra enemies (`enemies_removed_for_perf`); raising it removes the safety net | Raise the cap deliberately and test frame time at the worst wave; keep a hard cap |
| Effects visible on one PC, missing on another | `Particles2D` on the GLES2 fallback (Brotato has `fallback_to_gles2=true`) | `CPUParticles2D` |

## Memory

| Symptom | Likely cause | Fix |
|---|---|---|
| Memory (`MEMORY_STATIC`, `OBJECT_COUNT`) grows every wave | Mod Dictionary/Array keyed by enemies never cleared; `Reference` cycles; nodes removed but never freed; `yield` states that never resume | Clear per-wave data on wave end; `weakref` for back-references; `queue_free` what you remove; replace waits on signals that may never fire |
| Orphan count high from wave 1 but stable | Brotato's pool keeps pooled nodes out of the tree | Normal; watch the trend, not the value |
| Memory grows in long online sessions | Unbounded message logs, resend queues, interpolation buffers | Cap every buffer (size and age) |
| Memory grows with a mod that logs a lot | `ModLoaderLog` stores every entry (and repeats) in `ModLoaderStore` | Own rate-limited file logger for frequent events |

## Crashes and errors

| Symptom | Likely cause | Fix |
|---|---|---|
| Crash/errors at run end, quit to menu or restart | Mod references to nodes freed by the scene change (`Main` frees all pooled nodes on exit); timers/yields resuming after the scene is gone; cleanup order | Clear caches on scene exit; `alive()` at every callback; connect timers to `self` (auto-disconnect on free) instead of `yield` |
| Crash or broken feature right after a Brotato update | Overridden method signature changed (`Parse Error: The function signature doesn't match the parent...` in debug-enabled builds; silent failed calls in release); renamed members (`isn't declared in the current scope`); removed methods (`Nonexistent function`) | Diff the hooked vanilla scripts; update signatures; version gate + safe mode ([defensive-patterns.md](defensive-patterns.md)) |
| All mods disabled at startup after a session with errors | CrashReporter (1.1.14.x) found an `ERROR:`/`SCRIPT ERROR:` line mentioning `mods-unpacked` in the previous log | Fix the script error; never push expected warnings as errors with your mod path |
| Game closes with no error | Infinite recursion (override calls itself instead of `.method()`, signal ping-pong); no stack check without a debugger | Re-entrancy guards; review overrides; reproduce in the editor to get `Stack Overflow` |
| Effect/handler runs twice | Duplicate `connect`, extension calling a virtual callback's parent, two mods extending the same method both re-applying an effect | `is_connected` guards; don't call parent for virtual callbacks; idempotent effects |
| Works alone, breaks with another mod | Another mod overrides the same method without calling `.method()`, or replaces the scene/node you hook; unspecified load order | `load_before`/`dependencies`; `ModLoaderMod.is_mod_loaded()` to adapt; call the parent in every override |
| Errors only on second run in a session | State kept in an autoload/static from the previous run; pooled node state not reset | Reset on run start; reset pooled-node fields in the re-init hook |
| Errors right at game start (null singleton) | Game singletons accessed in `mod_main._init()`, before later autoloads exist | Only install extensions in `_init()`; touch singletons from `_ready()` or later |
| `Can't change this state while flushing queries...` | Changing Area2D/shape state inside a physics callback | `set_deferred` / `call_deferred` |
| Wave never ends / shop never opens (no crash) | A script error in the code that advances the flow: debug-enabled builds abort that function, release builds continue silently with null | Find the first `SCRIPT ERROR` in `godot.log` (debug-enabled) or reproduce in the editor; guard that path |
| Mod settings/save lost or reset | Crash during a direct write (no temp+rename); JSON numbers read as floats; invalid data not validated | Crash-safe save; validate and convert types on load |

## Online

| Symptom | Likely cause | Fix |
|---|---|---|
| Freeze when host opens the shop | One huge reliable state message built and sent in one frame, or a phase message lost during the scene change | Chunk and spread; epoch + ack + resend ([online-stability.md](online-stability.md)) |
| Client disconnects after N minutes | No heartbeat / net node paused / main-thread stalls longer than the timeout / send queue never drains | Heartbeat on `PAUSE_MODE_PROCESS` node; keep stalls short; cap and drain queues |
| Everyone freezes when host alt-tabs | Native pause on focus loss stops the tree and network processing | Override auto-pause online; network nodes `PAUSE_MODE_PROCESS` |
| Client FPS fine offline, bad online | Per-message GDScript work, JSON encode/decode per tick, polling every frame at uncapped FPS | Binary encoding, message caps per frame, poll throttle |
| Positions drift apart over a run | Desync (client-side gameplay code or RNG) | Host authority; state hash at wave start/shop; resync (`brotato-online-multiplayer`) |
| Errors on the client just after a scene change | Stale messages for the previous scene | Scene epoch; drop stale |
