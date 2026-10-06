# Performance problems: symptom → diagnose → fix (UE 5.8)

Classify with `stat unit` first (SKILL.md). Measure in Standalone/packaged builds with VSync, frame cap and dynamic resolution off.

## GPU

| Symptom | Diagnose | Fix |
|---|---|---|
| GPU ≈ frame time, drops a lot at `r.ScreenPercentage 50` | Pixel-bound; `stat gpu` top passes | Lower internal res (TSR 67-75 %, upscaler plugin); then Lumen tier/post |
| Lumen GI + reflections > ~5 ms at 1440p | ProfileGPU: Lumen Screen Probe Gather / Reflections | GI/Reflection tier High; hit lighting Epic-only; Final Gather Quality 1; Max Roughness To Trace ~0.3 |
| Medium preset fast but balls look dead | Lumen reflections off at Medium (5.8) | Reflection captures; or Reflection Quality High with GI Medium |
| ShadowDepths/VSM > 2-3 ms | *Visualize > Virtual Shadow Map*: pages keep invalidating; count shadowed lights | Static invalidation behaviour on static props; remove WPO near table; Nanite; fewer shadowed lights; tighter radii; MegaLights for many lights |
| Shadow cost spikes when characters move | Skeletal meshes invalidate VSM pages | Expected; reduce shadowed lights touching characters; LOD bias at distance |
| Nanite raster high, overdraw view hot | Masked/WPO (programmable raster); stacked duplicate meshes | Opaque geometry; WPO disable distance; remove hidden duplicates |
| BasePass high | Shader Complexity / Quad Overdraw views | Simplify materials; Blendable Substrate GBuffer; fewer layers |
| Translucency high | Glass/bottle rows, haze cards | Fewer overlapping translucent layers; cheaper glass far from camera |
| PostProcessing high | DOF at Cine quality; Convolution bloom; motion blur | PostProcess tier Epic or lower in gameplay; Standard bloom |
| TSR high | History 200 % (Epic AA) at high output res | AA tier High; or upscaler plugin |
| Lights pass high | Many unshadowed overlapping lights / large radii | Tighter radii; merge fills; MegaLights |
| RT scene/BVH update high | Many skinned/WPO/dynamic meshes visible in RT | "Visible in Ray Tracing" off for clutter; `r.RayTracing.DynamicGeometry.MaxUpdatePrimitivesPerFrame` per tier |
| Volumetric fog high | Grid density with many lights | Coarser `r.VolumetricFog.GridPixelSize`/`GridSizeZ` on low tiers; fake haze |
| GPU time fine in editor, bad in game | Different scalability; editor-only exposure/viewport settings | Explicit `scalability N` in the measured session |

## CPU

| Symptom | Diagnose | Fix |
|---|---|---|
| Game ≈ frame | Insights CPU (`-trace=cpu,frame -statnamedevents`): Tick, Anim, Physics, BP | Reduce tick frequency; event-driven logic; anim URO/visibility ticking; physics substep budget |
| Game thread "slow" but mostly waiting | Insights shows waits on render thread/GPU | Not game-bound; fix the actual bottleneck |
| Draw (render thread) ≈ frame | `stat scenerendering`, `stat rhi`, `stat initviews` | Nanite; ISM/HISM; Merge Actors; fewer material sections; fewer shadowed lights on non-Nanite meshes |
| RHIT ≈ frame | Draw calls, PSO creation in Insights | Same as Draw; PSO caching |
| Spiky frame time every few seconds | Insights: GC, streaming, Blueprint events | GC settings/pooling; spread work; async loading |

## Hitches / stutter

| Symptom | Diagnose | Fix |
|---|---|---|
| Hitch the first time an effect/material/camera appears | Insights PSO scopes; repeats on cleared driver cache only | Bundled PSO cache + precaching; record with `-logPSO` |
| Objects appear a few frames late on first sight | PSO precache delays proxy creation (default strategy) | Precache earlier (loading screen); bundled cache |
| Hitch when entering a new area/level | Insights `loadtime`/`file` channels | Async loading, preload during menus, smaller packages |
| Hitch when changing graphics settings | Lumen path switch, shader/PSO compile | Apply settings in menus; expect re-convergence |
| Editor "Compiling Shaders" | DDC work | Shared DDC; not a runtime problem |

## Memory / streaming

| Symptom | Diagnose | Fix |
|---|---|---|
| "Texture streaming pool over budget", blurry felt/balls | `stat streaming`, `ListTextures` | Right-size textures; texture group LOD bias; raise pool per tier if VRAM allows; Build Texture Streaming |
| VRAM overflow / device lost on 8 GB GPUs | `memreport -full`, RHI memory | Pool size, VSM pages, Lumen atlas, TSR history %, fewer RT dynamic meshes |
| RAM grows over a session | Memory Insights snapshots | Find leaking assets/objects; unload unused levels |
| Long load times | Insights `loadtime`; package size | IoStore + compression; fewer hard references; smaller textures |

## Settings that don't seem to work

| Symptom | Cause | Fix |
|---|---|---|
| Quality menu doesn't change a CVar | CVar also set in DefaultEngine.ini/console. Log: "SetByScalability was ignored as it is lower priority than … SetByProjectSetting" | Move tier-dependent CVars to DefaultScalability.ini |
| New defaults ignored on your PC | Saved `GameUserSettings.ini` from older runs | Delete `Saved/Config/<Platform>/GameUserSettings.ini` when testing |
| Hit lighting toggle in PPV has no effect | `r.Lumen.HardwareRayTracing.HitLighting.Allowed=0` at High | Epic tier or override in DefaultScalability.ini |
| FPS capped at 60/refresh | VSync or `t.MaxFPS` | `r.VSync 0`, `t.MaxFPS 0` while measuring |

## Package / build

| Symptom | Diagnose | Fix |
|---|---|---|
| Package far larger than expected | Size Map, Asset Audit, cook log | Disable unused plugins; maps-to-cook list; exclude editor content; remove marketplace packs; Oodle compression; texture RDO |
| Cook takes very long | Shader permutations | Disable unused rendering features and RHIs; Blendable Substrate; shared DDC |
