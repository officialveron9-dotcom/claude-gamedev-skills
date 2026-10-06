---
name: ue5-performance-optimization
description: Provides profiling workflow, traps and fix tables for Unreal Engine 5.8 (current release) performance: stat unit/unitgraph/gpu, ProfileGPU, Unreal Insights, memreport, stat streaming; GPU- vs game-thread vs render-thread (Draw/RHI) bound; Nanite rules, Lumen/VSM/MegaLights cost controls, scalability groups, DefaultScalability.ini and device profiles, texture streaming pool, skeletal mesh LODs, draw calls, PSO precaching and shader stutter, memory and package size, frame budgets. Use when FPS is low, frames hitch, VRAM runs out, builds are too large, or when defining quality presets. Triggers: FPS, frame time, stat unit, GPU bound, ProfileGPU, Insights, Nanite, scalability, hitch, PSO, streaming pool over budget, Performance, Ruckeln, Ruckler, Stottern, Ressourcen sparen, Optimierung, Grafikeinstellungen, Speicher, VRAM, Ladezeiten.
---

# UE5 performance: measure → classify → fix (UE 5.8)

Scope: runtime performance and memory of a high-end interior (pool hall, close-up glossy balls, a few characters). Visual-quality settings live in the `ue5-lighting-rendering` skill. Build/C++ setup is covered elsewhere.

## Frame budgets

| Target | Budget | Plan for (≈ 10-15 % headroom) |
|---|---|---|
| 30 fps | 33.3 ms | ~29 ms |
| 60 fps | 16.67 ms | ~14.5 ms |
| 90 fps | 11.1 ms | ~9.5 ms |
| 120 fps | 8.33 ms | ~7.2 ms |
| 144 fps | 6.94 ms | ~6 ms |

- Epic's Lumen targets: about 4 ms for GI + reflections at High (60 fps console) and 8 ms at Epic (30 fps console), both at 1080p.
- A 60 fps PC target at 1440p with Epic Lumen and hit lighting leaves little room for anything else. Budget Lumen first.

## Measurement traps (fix these before trusting any number)

1. **Profiling in PIE/editor.** Editor overhead inflates the game and render threads. Use Standalone (`-game`) for iteration, and a packaged Development or Test build for decisions. `stat` commands are unavailable in Shipping.
2. **VSync or frame cap hides headroom.** Run `r.VSync 0` and `t.MaxFPS 0` while measuring. Both are verified in 5.8.
3. **Dynamic resolution masks GPU cost.** 5.8 enables it on PC (DX12/Vulkan). Disable it while profiling (`r.DynamicRes.OperationMode 0`) or read the resolution alongside the time.
4. **First-run noise.** PSO/shader compilation and streaming in the first seconds. Warm up, or measure the second run of the same shot. Profile first-run hitches separately.
5. **Average FPS.** Use frame time and its worst frames: `stat unitgraph`, Insights timeline. A 60 fps average with 80 ms spikes is a failing build.
6. **Inconsistent scalability.** Editor viewport scalability is separate from game settings. Set `sg.*` or `scalability <0-4>` explicitly in the session you measure.
7. **Moving camera.** Use fixed repro shots: (a) close-up break shot, (b) wide room with all characters, (c) menu/UI. Same resolution every time.

## Workflow

1. Launch a Standalone or packaged Test build at the target resolution and scalability, with VSync, frame cap and dynamic res off.
2. Run `stat unit` and `stat unitgraph`, then classify with the table below.
3. **GPU-bound:**
   - Set `r.ScreenPercentage 50`. If GPU time drops a lot, the cost is per-pixel (Lumen, VSM projection, post, translucency, base pass shading). If it barely moves, the cost is geometry or fixed (shadow depth, Nanite raster, Lumen scene update, RT BVH update).
   - Then use `stat gpu` / `ProfileGPU` (Ctrl+Shift+,) to find the top passes. Map pass to cause with [references/profiling.md](references/profiling.md).
4. **Game thread:** Unreal Insights with `-trace=cpu,frame,bookmark,log -statnamedevents`. Look for Tick, animation, physics (ball sim), Blueprint and UI.
5. **Render thread (Draw):** `stat scenerendering` and `stat rhi` (draw calls, primitives). Insights render-thread track. Usual causes: draw calls, primitive count, non-Nanite meshes with many sections, dynamic shadows of non-Nanite meshes.
6. **RHI thread:** draw-call and state submission. Same fixes as Draw, plus PSO behaviour.
7. **Memory/streaming:**
   - `stat streaming` (pool over budget = blurry textures and churn)
   - `memreport -full` (file in `Saved/Profiling/MemReports/`)
   - Memory Insights (`-trace=memory`)
8. **Hitches:** Insights timeline around the spike. Check for PSO compile, asset load, GC or a streaming burst. See [references/content-memory.md](references/content-memory.md).
9. Change one thing, re-measure the same shots, and keep a perf log (shot, scalability, Game/Draw/GPU ms, top 3 GPU passes).

## Classify with `stat unit`

| Pattern | Bound | Go to |
|---|---|---|
| GPU ≈ Frame, Game/Draw clearly lower | GPU | `stat gpu`, ProfileGPU, Insights GPU track (5.6+: one unified GPU profiler for all three) |
| GPU drops with `r.ScreenPercentage 50` | GPU, pixel-bound | Lumen tier, screen %, post (DOF/bloom), translucency, VSM projection |
| GPU unchanged at 50 % | GPU, geometry/fixed | Shadow depths, Nanite raster (masked/WPO), RT/BVH update, Lumen scene, many lights |
| Game ≈ Frame | Game thread | Insights CPU: tick, anim, physics, BP, UI |
| Draw ≈ Frame | Render thread | `stat scenerendering`, `stat rhi`: draw calls, primitives, visibility |
| RHIT ≈ Frame | RHI thread | Draw calls, PSO creation, driver |
| Frame spikes, all averages fine | Hitch | Insights timeline; PSO/streaming/GC |

## Traps that waste the most frame time (this game type)

1. **Every light shadowed with a huge Attenuation Radius.** Each VSM-shadowed local light costs page rendering and projection. Bar practicals: shadows off on fill lights, tight radii, or MegaLights for many shadowed lights (5.8 Production-Ready, cost ~flat in light count).
2. **WPO/PDO materials near the table** (swaying signs, animated cloth via WPO). They invalidate VSM cache pages every frame and force Nanite programmable raster.
3. **Non-Nanite high-poly static props.** Expensive in VSM and on the render thread. Make static opaque props Nanite.
4. **Lumen Epic + Hit Lighting + Cine DOF as the only preset.** Build tiers. See [references/scalability.md](references/scalability.md).
5. **Translucent glassware and haze everywhere.** Translucency and volumetric fog are per-pixel. Keep glass near the camera few, and fog grid at tier defaults.
6. **8K textures on small props.** The streaming pool overflows and the hero felt goes blurry (see [references/content-memory.md](references/content-memory.md)).
7. **Characters at LOD0 everywhere, with strand hair and animation ticking off-screen.** Use LODs, LOD bias per tier, visibility-based anim ticking, and cards/LOD for grooms at distance.
8. **No PSO strategy.** The first break shot hitches. Precaching is on by default since 5.3, but still ship a bundled cache for the gaps.
9. **Unused plugins and rendering features enabled.** Shader permutations, cook time, package size and memory all grow.
10. **Fixing by intuition.** Always rank by measured ms. Don't optimize anything under ~0.3 ms while a 4 ms pass exists.

## Prioritized optimization checklist

1. [ ] Repro shots, Test build, VSync/cap/dynres off. Baseline numbers recorded.
2. [ ] Bound classified (table above).
3. [ ] GPU top pass addressed. Usual order for this scene: Lumen (tier, Final Gather, hit lighting, reflections) → shadows (light count/radius, invalidations, Nanite) → post (DOF quality, bloom method, TSR history %) → translucency → base pass (material cost, overdraw).
4. [ ] Internal resolution strategy: TSR at 66-75 % for High/Medium; Epic native or ~75 % + history 200 %. Optional DLSS/FSR/XeSS plugin.
5. [ ] Static opaque meshes Nanite. Masked/WPO only where needed, with WPO disable distance.
6. [ ] Characters: LODs set and tested, `r.SkeletalMeshLODBias` per tier, anim off-screen behaviour, groom LOD.
7. [ ] Streaming pool fits per tier (`stat streaming` shows no over-budget). Texture sizes and compression fixed at the source.
8. [ ] PSO: precaching verified in a packaged build plus bundled PSO cache recorded. First-run hitch test with a cleared driver shader cache.
9. [ ] Scalability tiers (Low-Epic) defined in DefaultScalability.ini, with auto-detect for first launch.
10. [ ] Memory: memreport per tier; VRAM headroom on min-spec GPU.
11. [ ] Package: unused plugins/content removed, maps-to-cook list set, compression and Oodle settings checked.
12. [ ] Re-test min-spec and target-spec hardware; record the final perf log.

## Common problems (short; full table in references)

| Problem | Diagnose | Fix |
|---|---|---|
| 40-50 fps on a strong GPU, GPU ≈ frame | ProfileGPU: Lumen passes 6-10 ms | High tier for Lumen, Hit Lighting off, screen % 66-75 |
| Shadow depths 3+ ms | *Visualize > Virtual Shadow Map*, light count | Fewer shadowed lights, tighter radii, Nanite, no WPO near table, MegaLights |
| Hitch on first shot/effect | Insights: PSO compile events | Bundled PSO cache, precache validation |
| Blurry felt/ball textures | `stat streaming`: pool over budget | Lower oversized textures, raise pool per tier, VT for huge unique textures |
| Draw ≈ frame | `stat rhi` draw calls high | Nanite, merge/instance, fewer material sections |
| VRAM overflow on 8 GB GPUs | memreport, Insights memory | Pool size, texture LOD bias per tier, VSM pages, Lumen surface cache atlas |

## Reference files (read when needed)

- [references/profiling.md](references/profiling.md): read when capturing or reading stat/ProfileGPU/Insights/memreport data; has the GPU pass → cause table.
- [references/rendering-costs.md](references/rendering-costs.md): read when a rendering feature (Nanite, Lumen, VSM, MegaLights, translucency, post, AA) dominates the GPU.
- [references/scalability.md](references/scalability.md): read when building quality presets, per-platform/device profiles or auto-detect.
- [references/content-memory.md](references/content-memory.md): read for texture streaming, LODs/HLOD, draw calls, PSO/shader stutter, memory and package size.
- [references/common-issues.md](references/common-issues.md): read for the full problem → diagnose → fix table.
- [references/cvars.md](references/cvars.md): read before typing any CVar; only 5.8-verified CVars with sources.
- [references/sources.md](references/sources.md): provenance.
