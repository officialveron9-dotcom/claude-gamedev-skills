# Rendering cost controls (UE 5.8)

Contents: Nanite rules · Lumen cost knobs · VSM · MegaLights · ray tracing scene · translucency/fog · post/AA · resolution strategy.

## Nanite: do / don't

| Asset | Nanite? | Reason / trap |
|---|---|---|
| Room shell, bar, table body, rails, chairs, bottles (opaque), props | **Yes** | Cheap raster, best VSM caching and performance, fewer draw calls |
| Balls, cue (movable, low-poly) | Yes (fine) or no | Nanite supports movable meshes. No WPO, so cheap. Keep the fallback mesh fine for HWRT reflections |
| Masked materials (grilles, lace curtains) | Yes, but costs | Programmable raster. Keep masked areas small or use real geometry |
| WPO/PDO materials | Avoid near the table | Programmable raster plus VSM invalidation every frame. Set *World Position Offset Disable Distance*; disable *Evaluate WPO* where unused |
| Translucent glass, liquids | No | Translucency is not Nanite-rendered; keep these meshes simple |
| Skeletal meshes (characters) | No (Nanite skinning is experimental) | Use classic LODs |
| Nanite Tessellation/displacement | No for shipping | Experimental; 5.8 regressions reported. Use normal maps |
| Nanite Foliage (voxels/assemblies) | n/a here | Experimental (5.7) |

Settings that matter:
- *Fallback Relative Error* / *Fallback Target*: the fallback is used for HWRT, collision and non-Nanite paths. Fine on hero curved meshes, coarse elsewhere.
- *Keep Triangle Percent* / *Trim Relative Error*: reduce disk and memory for over-detailed scans.
- Project toggle: `r.Nanite.ProjectEnabled` (in 5.8 logs).
- Debug: *Nanite Visualization > Overdraw* for stacked/overlapping geometry. Overlapping copies of the same mesh, e.g. kitbashed rails, cost real raster time.

## Lumen cost knobs (biggest first)

1. **Scalability tier** (`sg.GlobalIlluminationQuality`, `sg.ReflectionQuality`):
   - Epic → High saves the most: screen probe downsample 16→32, no hit lighting, no mesh-SDF tracing, half-res reflections.
   - Medium = Lumen Lite in 5.8 (~2x faster than High per Epic) but **no Lumen reflections**.
2. **Hit Lighting for Reflections**: only allowed at Epic (`r.Lumen.HardwareRayTracing.HitLighting.Allowed`). Big cost on glossy-heavy frames.
3. **PPV Final Gather Quality / Reflections Quality**: >1 is expensive. Use only in cinematics.
4. **Max Roughness To Trace** (PPV, default 0.4): lowering it to ~0.25-0.3 skips traced reflections on rough wood/leather. Balls (≤ 0.1) unaffected.
5. **Lumen Scene View Distance / Max Trace Distance**: shorten to the room size indoors.
6. **Lumen Scene Lighting Quality / Update Speed**: leave at 1 for gameplay.
7. **Translucency volume**: GI on translucency/fog is tier-controlled (`r.Lumen.TranslucencyVolume.*` in BaseScalability). Rarely worth hand-tuning.
8. **Async compute**: Lumen overlaps other work. A pass that looks big in `stat gpu` Compute may not be on the critical path; check the total.

## Virtual Shadow Maps

- Cost drivers:
  - Number of shadowed lights × screen coverage.
  - Page invalidations: moving lights, WPO/PDO, skinned meshes, moving actors.
  - Non-Nanite geometry rendered into pages.
- Per-primitive *Shadow Cache Invalidation Behavior*: room/table = Static, balls/cue = Rigid/Auto.
- Tier knobs (Epic values): `r.Shadow.Virtual.MaxPhysicalPages=4096`, `ResolutionLodBiasLocal=0.0` (Moving 1.0), `ResolutionLodBiasDirectional=-1.5`, SMRT ray count 8 / samples 4.
  - Raise `ResolutionLodBias*` (blurrier) and lower SMRT counts on Medium/Low.
- `r.Shadow.Virtual.Cache 0` disables caching. Only for A/B testing how much caching saves.
- 5.7 improved caching for non-Nanite meshes. 5.8 adds throttled LOD-delta invalidation (`r.Shadow.Virtual.DeferredInvalidationBudget`) and `r.Shadow.Virtual.PrefilteredDistant.ProjectEnable` for bandwidth-limited platforms.
- Light attenuation radius is a shadow-cost multiplier. Size it to where the light is visibly contributing.

## MegaLights (Production-Ready 5.8)

- When: many (> ~10) shadowed local lights overlap on screen (bar practicals, neon, wall sconces).
  - Cost is roughly fixed per pixel (`r.MegaLights.NumSamplesPerPixel`, Epic 4) instead of per light.
  - HWRT recommended.
- When not: a handful of lights (table lamps only). Classic VSM lights are cleaner and can be cheaper.
- Profile in motion. Noise and denoiser cost show up when many lights compete per pixel.

## Ray tracing scene (HWRT Lumen, path tracer)

- Every RT-visible movable, skinned or WPO mesh updates the BVH each frame. Exclude helper meshes, distant clutter and invisible proxies ("Visible in Ray Tracing" off).
- Skeletal meshes in RT need the skin cache. Tier knob: `r.RayTracing.Geometry.SkeletalMeshes` (0 at Medium).
- `r.RayTracing.DynamicGeometry.MaxUpdatePrimitivesPerFrame` (BaseScalability: 1000 at Medium, -1 above) caps dynamic BVH updates.

## Translucency, fog, particles

- Translucency is shaded per layer per pixel (overdraw) and is not Nanite-rendered. Rows of glasses and bottles behind the bar, seen through each other, can cost more than all the opaque geometry.
- Volumetric fog/haze: `r.VolumetricFog.GridPixelSize` (Epic 8) / `GridSizeZ` (Epic 128). Coarser on lower tiers. A light "smoky bar" haze from a large translucent card is often cheaper than volumetric fog with many lights.
- Niagara: GPU sim for chalk dust; cap spawn counts per tier (`fx.Niagara.QualityLevel`).

## Post and AA

| Feature | Cost trap | Control |
|---|---|---|
| Cinematic DOF | Full-res gather at Cine (`r.DOF.Gather.ResolutionDivisor=1`) | PostProcessQuality tier; Epic uses divisor 2 |
| Bloom | Convolution (FFT) | Standard bloom in gameplay (`r.BloomQuality` tier) |
| Motion blur | Full-res gather at Epic | `r.MotionBlurQuality` tier |
| TSR | History 200 % at Epic AA tier | AA tier High (100 %) for lower presets |
| Local exposure / eye adaptation | Small | Leave on |
| Lens flare (image-based) | Small-medium | Off by default in new projects |

## Resolution strategy

- Prefer lowering internal resolution (TSR/DLSS/FSR/XeSS) before cutting lighting tiers. Lumen and post are largely per-pixel.
- Ship *Resolution Quality* presets (BaseScalability: Performance 50 %, Balanced ~58 %, Quality ~67 %, Native 100 %). Keep ≥ ~67 % for close-up ball shots.
- Dynamic resolution (PC DX12/Vulkan in 5.8) as a safety net against GPU spikes; set min/max screen % bounds.
- Disable it while profiling.
