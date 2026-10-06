# Profiling toolkit (UE 5.8)

Contents: console commands · view modes · GPU pass → cause table · Unreal Insights recipes · memory tools · repeatable capture protocol.

## Console commands

| Command | Shows | Gotcha |
|---|---|---|
| `stat fps` / `stat unit` | FPS; Frame, Game, Draw (render thread), RHIT, GPU ms | Read max-of-threads, not the sum |
| `stat unitgraph` | Rolling graph of the same | Best for spotting hitches and oscillation |
| `stat gpu` | Per-pass GPU timings | 5.6+: same data stream as ProfileGPU and Insights; split into Graphics/Compute (async compute overlaps) |
| `ProfileGPU` (Ctrl+Shift+,) | One-frame GPU capture; GPU Visualizer in editor; table in the log (5.6+) | Single frame: capture 2-3 times |
| `stat rhi` | Draw calls, primitives, RHI memory | Includes all passes (shadows, depth) |
| `stat scenerendering` | Mesh draw calls, visibility, render-thread costs | Render-thread suspects |
| `stat initviews` | Culling/visibility cost and counts | Many small actors = high cost |
| `stat game` / `stat engine` | Tick groups, world/actor/component tick | Game-thread triage before Insights |
| `stat foliage` | ISM/HISM instance and triangle counts | Instanced props, not only foliage |
| `stat streaming` | Texture streaming pool, over-budget, wanted vs resident mips | "Over budget" = blurry textures and churn |
| `stat memory` | High-level memory categories | Use memreport for detail |
| `stat levels` | Loaded/visible streaming levels | Level streaming hitches |
| `stat none` | Clears overlays | Overlays cost a bit themselves |
| `memreport -full` | Full memory dump to `Saved/Profiling/MemReports/` | Compare between scalability tiers |
| `ListTextures` | Every texture with size/format/mips | Sort to find 4K/8K offenders |
| `obj list class=Texture2D` | Loaded objects of a class | Also StaticMesh, SkeletalMesh, SoundWave |
| `r.ScreenPercentage 50` | Pixel-bound test | Restore afterwards |
| `scalability 0..4` | Sets all sg groups at once | Then override single `sg.*` |
| `Trace.Start` / `Trace.Stop` | Start/stop Insights tracing at runtime | Capture only the interesting window |

Optional: the CSV profiler (`csvprofile start` / `csvprofile stop`) gives per-frame stat CSVs for long runs and regressions.

## View modes for performance

- *Optimization Viewmodes*: Shader Complexity, Quad Overdraw, Light Complexity, Texture Streaming Accuracy.
- *Nanite Visualization*: Overdraw, Triangles, Clusters, programmable-raster-related views. Look for masked/WPO areas.
- *Lumen*: Surface Cache, Card Placement, Lumen Scene. Huge single meshes and pink coverage gaps cost quality and time.
- *Virtual Shadow Map*: cached vs invalidated pages. Steady pages that keep turning "dirty" mean WPO, skinned or moving primitives.
- *Show > Visualize > HDR*, buffer visualizations: not perf, but rule out exposure-related "dark = noisy" Lumen issues first.

## GPU pass → likely cause → fix

| Pass family (stat gpu / ProfileGPU) | Likely cause | Fix |
|---|---|---|
| Lumen Screen Probe Gather / final gather | Tier too high; Final Gather Quality > 1 | GI tier High; FG Quality 1; screen % |
| Lumen Reflections | Many glossy pixels; hit lighting; Reflection Quality > 1 | Max Roughness To Trace lower for rough wood; hit lighting Epic-only; Quality 1 |
| Lumen scene update / surface cache lighting | Many moving lights/objects; Lumen Scene Lighting Quality ↑ | Defaults; fewer moving shadowed lights |
| ShadowDepths / VSM page rendering | Invalidations (WPO, skinned, moving lights); non-Nanite high-poly | Static invalidation behaviour on static props; Nanite; no WPO near table |
| Shadow projection (VSM SMRT) / lights | Many shadowed local lights, large radii | Shadows off on fills; tighter radii; MegaLights |
| Nanite VisBuffer / raster | Programmable raster (masked, WPO, PDO), overdraw of stacked geometry | Opaque where possible; WPO disable distance; inspect Nanite Overdraw |
| BasePass | Expensive materials; non-Nanite overdraw; Substrate Adaptive with many layers | Simplify materials; Blendable GBuffer; fewer closures |
| Translucency | Glassware, particles, haze cards | Fewer layers near camera; lower res translucency; avoid full-screen sheets |
| PostProcessing (DOF, Bloom, MotionBlur) | Cinematic DOF, Convolution bloom | DOF quality per tier; Standard bloom in gameplay |
| TSR | History 200 % at Epic | AA tier High (history 100 %) on lower presets |
| Ray tracing scene / BVH update | Many skinned/WPO meshes in RT | Exclude unneeded actors from RT ("Visible in Ray Tracing" off) |
| Volumetric fog | Grid density | `r.VolumetricFog.GridPixelSize` / `GridSizeZ` per tier |
| SSS / hair strands | Skin/hair on close characters | Groom LOD/cards at distance; SSS only on close characters |

## Unreal Insights recipes

- Start `UnrealInsights.exe` (`Engine/Binaries/<Platform>/`). It launches the trace server; the game connects automatically on the same machine.
- Typical game launch arguments:
  - CPU/GPU frame analysis: `-trace=cpu,gpu,frame,bookmark,log -statnamedevents`
  - Loading/hitch analysis: add `loadtime,file`
  - Memory: `-trace=memory` (heavier; run separately)
- Without `-statnamedevents`, many engine scopes are missing. With it, the game thread runs slower: compare ratios, not absolutes.
- Read the Timing view:
  - Frames track first; select a spike.
  - GameThread: if it shows a long *wait* on the render thread or GPU, the game thread is **not** the bottleneck.
  - RenderThread / RHIThread / GPU tracks: the longest bar on the critical path wins.
- Hitch triage: PSO compile scopes, async loading and "Flush", GC (`CollectGarbage`), `UpdateStreaming`, or a big Blueprint event.
- Bookmark state changes (shot start, break, menu open) through gameplay code or `Trace.Bookmark` so captures are navigable.

## Memory tools

| Question | Tool |
|---|---|
| What uses RAM/VRAM overall? | `memreport -full` (per tier), `stat memory` |
| Which textures are big/unneeded? | `ListTextures`, Size Map in the Content Browser, `stat streaming` |
| Leak or growth over time? | Memory Insights (`-trace=memory`), compare snapshots |
| Per-system budget (LLM tags) | `-llm` launch argument + `stat llm` / `stat llmfull` |

## Repeatable capture protocol

1. Same build type (Test or Development), resolution, `scalability N`, VSync/cap off, dynamic res off.
2. Load the map, wait ~10 s for streaming and PSO warm-up, then run each repro shot for ~10 s.
3. Record: average and max frame time, Game/Draw/RHIT/GPU, top 5 GPU passes, `stat streaming` pool state.
4. Store traces with the build ID. Re-run the same protocol after each change. Never compare editor numbers with packaged numbers.
