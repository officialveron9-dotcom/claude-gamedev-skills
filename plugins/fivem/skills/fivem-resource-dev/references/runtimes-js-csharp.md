# JavaScript/TypeScript and C# resources - traps

Read when the resource is written in JS/TS or C#, or mixes runtimes.

## JavaScript / TypeScript

| Lua | JS |
|---|---|
| `AddEventHandler` | `on(name, fn)` |
| `RegisterNetEvent(name, fn)` | `onNet(name, fn)` |
| `TriggerEvent` | `emit` |
| `TriggerServerEvent` / `TriggerClientEvent` | `emitNet(name, ...)` / `emitNet(name, target, ...)` |
| `CreateThread` + `Wait(0)` loop | `setTick(fn)` / `clearTick(id)` |
| `Wait(ms)` | `await new Promise(r => setTimeout(r, ms))` (client: define a `Delay` helper) |
| `exports('n', fn)` | `exports('n', fn)` ; call `exports.res.n(...)` or `exports['res'].n(...)` |
| `source` | global `source` inside handler - copy it: `const src = source;` |

Traps:
- Server runs Node 16 by default; add `node_version '22'` (artifact >= 12913) for modern Node. Client JS is plain V8 with the ES2017 stdlib - no DOM, localStorage, IndexedDB, WebGL or Node APIs (do HTTP on the server).
- Thread affinity (server): callbacks from Node (fs, http, timers from libs, DB drivers) run on the libuv thread. Calling natives there -> `No current resource manager`. Wrap in `setImmediate(() => { ... })` before touching natives.
- `GetPlayers()` returns strings in JS too.
- `require` resolves from the resource's `node_modules`. The `yarn`/`webpack` builder resources run installs at start; they are slow, flaky on some artifacts (26261-27715 had Linux yarn issues) and "resources can no longer be builders" on GTA V Enhanced. Prefer bundling with esbuild/tsup in CI and shipping `dist/`.
- Sandbox: child processes and worker threads are blocked unless `add_unsafe_child_process_permission` / `add_unsafe_worker_permission` is set for the resource.
- Typings: `@citizenfx/client`, `@citizenfx/server`. Extend `CitizenExports` for typed exports. ox_lib/oxmysql publish `@overextended/ox_lib`, `@overextended/oxmysql`.
- Bundle TS to one plain JS file per side (CJS/IIFE, as the ox/Qbox templates do) instead of shipping raw ES-module output.

## C#

- Script files are `*.net.dll` listed in `client_script`/`server_script`; reference NuGet `CitizenFX.Core.Client` / `CitizenFX.Core.Server`. Template: `dotnet new -i CitizenFX.Templates` then `dotnet new cfx-resource`.
- `fx_version 'bodacious'`+ implies `clr_disable_task_scheduler`: after awaiting non-FiveM tasks you may be off the main thread - `await Delay(0)` (BaseScript) to get back before calling natives.
- Mono v2 runtime (`mono_rt2` manifest key, assemblies under `citizen/clr2/lib/mono/4.5/v2/`) is a preview; do not mix v1 and v2 assemblies.
- GTA V Enhanced replaced Mono with .NET (needs .NET 10 SDK) - C# resources need rework there.
- NUI callbacks: `RegisterNuiCallback("name", new Action<IDictionary<string, object>, CallbackDelegate>((data, cb) => { ...; cb(new { ok = true }); }));`

## Mixing runtimes

Exports and events work across Lua/JS/C# (msgpack serialisation). Functions passed across become function references (callable, async-ish); tables with holes or mixed keys may arrive as objects; Lua integers vs floats are preserved, JS numbers are doubles.
