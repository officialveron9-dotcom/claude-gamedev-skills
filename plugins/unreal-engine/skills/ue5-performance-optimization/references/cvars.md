# Verified CVars: performance (UE 5.8)

Source tags:
- **[L]**: set or echoed in real UE 5.8.0-5.8.3 logs.
- **[S]**: in Epic's 5.8-era `BaseScalability.ini` (values quoted are Low/Med/High/Epic/Cine).
- **[S\*]**: the scalability group section exists in BaseScalability; the `sg.<Group>` name follows the convention verified in logs for the other ten groups.
- **[D]**: named in current Epic docs.
- **[R]**: 5.8 release notes.

`stat …`, `ProfileGPU`, `memreport`, `ListTextures`, `Trace.Start/Stop` and `scalability N` are console *commands*, not CVars; see profiling.md. Confirm semantics with `help <cvar>`. Tier-dependent CVars belong in DefaultScalability.ini or device profiles, never DefaultEngine.ini. Otherwise scalability is silently overridden (priority warning seen in 5.8 logs).

## Measurement hygiene

| CVar | Use | Src |
|---|---|---|
| `r.VSync` | 0 while profiling | L |
| `t.MaxFPS` | 0 = uncapped while profiling; cap for battery/thermals | L |
| `r.DynamicRes.OperationMode` | 0 while profiling (5.8 enables dynamic res on PC DX12/Vulkan) | L, R |
| `r.ScreenPercentage` | 50 = pixel-bound test | L |

## Scalability groups

| CVar | Src |
|---|---|
| `sg.ViewDistanceQuality`, `sg.AntiAliasingQuality`, `sg.ShadowQuality`, `sg.GlobalIlluminationQuality`, `sg.ReflectionQuality`, `sg.PostProcessQuality`, `sg.TextureQuality`, `sg.EffectsQuality`, `sg.FoliageQuality`, `sg.LandscapeQuality` | L |
| `sg.ResolutionQuality`, `sg.ShadingQuality` | S\* |

## Lumen / lighting cost (tier-controlled)

| CVar | Low / Med / High / Epic / Cine | Src |
|---|---|---|
| `r.Lumen.DiffuseIndirect.Allow` | 0 / 1 / 1 / 1 / 1 | S, L |
| `r.Lumen.FinalGatherMethod` | – / 0 (Lumen Lite) / 1 / 1 / 1 | S, L |
| `r.Lumen.Reflections.Allow` | 0 / 0 / 1 / 1 / 1 | S, L |
| `r.Lumen.HardwareRayTracing.HitLighting.Allowed` | – / 0 / 0 / 1 / 1 | S, L |
| `r.Lumen.ScreenProbeGather.DownsampleFactor` | – / – / 32 / 16 / 8 | S, L |
| `r.LumenScene.SurfaceCache.AtlasSize` | – / 2048 / 3584 / 4096 / 4096 | S, L |
| `r.RayTracing.DynamicGeometry.MaxUpdatePrimitivesPerFrame` | – / 1000 / -1 / -1 / -1 | S, L |
| `r.MegaLights.NumSamplesPerPixel` | 2 / 2 / 4 / 4 / 4 | S, L |

## Shadows

| CVar | Low / Med / High / Epic / Cine | Src |
|---|---|---|
| `r.Shadow.Virtual.MaxPhysicalPages` | 512 / 512 / 2048 / 4096 / 8192 | S, L |
| `r.Shadow.Virtual.ResolutionLodBiasLocal` | 1.0 / 1.0 / 0.0 / 0.0 / 0.0 | S, L |
| `r.Shadow.Virtual.SMRT.RayCountLocal` | 0 / 4 / 4 / 8 / 16 | S, L |
| `r.Shadow.Virtual.Cache` | 0 = caching off (A/B test only) | D |
| `r.Shadow.Virtual.DeferredInvalidationBudget` | 5.8 budget for LOD-delta invalidations | R |

## Textures / streaming / VT

| CVar | Low / Med / High / Epic / Cine | Src |
|---|---|---|
| `r.Streaming.PoolSize` (MB) | 400 / 600 / 800 / 1000 / 3000 | S, L |
| `r.Streaming.LimitPoolSizeToVRAM` | 1 / 1 / 1 / 0 / 0 | S, L |
| `r.Streaming.MipBias` | 16 / 1 / 0 / 0 / 0 | S, L |
| `r.Streaming.Boost` | 0.3 / 1 / 1 / 1 / 1 | S, L |
| `r.MaxAnisotropy` | 1 / 2 / 4 / 8 / 8 | S, L |
| `r.VT.MaxAnisotropy` | 4 / 4 / 8 / 8 / 8 | S, L |
| `r.TextureStreaming` | Streaming on/off (keep on) | L |
| `r.VirtualTextures` | Streaming VT support | L |

## Geometry / characters

| CVar | Note | Src |
|---|---|---|
| `r.Nanite.ProjectEnabled` | Nanite project toggle | L |
| `r.Nanite.Foliage` | Nanite foliage (experimental 5.7+) | L |
| `r.SkeletalMeshLODBias` | 2 / 1 / 0 / 0 / 0 by ViewDistance tier | S, L |
| `r.ViewDistanceScale` | 0.4 / 0.6 / 0.8 / 1.0 / 10 | S, L |
| `r.SkinCache.CompileShaders` | Needed for skinned meshes in HWRT | L |
| `r.MeshStreaming` | Mesh LOD streaming | L |

## Post / AA / effects

| CVar | Low / Med / High / Epic / Cine | Src |
|---|---|---|
| `r.TSR.History.ScreenPercentage` | 100 / 100 / 100 / 200 / 200 | S, L |
| `r.DepthOfFieldQuality` | 0 / 1 / 2 / 2 / 4 | S, L |
| `r.MotionBlurQuality` | 0 / 3 / 3 / 4 / 4 | S, L |
| `r.BloomQuality` | 4 / 4 / 5 / 5 / 5 | S, L |
| `r.VolumetricFog.GridPixelSize` / `GridSizeZ` | Epic 8 / 128 | S, L |
| `fx.Niagara.QualityLevel` | Epic 3 | S, L |
| `r.MaterialQualityLevel` | Epic 1 (High) | S, L |

## PSO / shaders / features (project-level)

| CVar | Note | Src |
|---|---|---|
| `r.PSOPrecaching` | PSO precaching (default on since 5.3) | D |
| `r.PSOPrecache.ProxyCreationStrategy` | What happens while PSOs compile (delay draw by default) | L, D |
| `r.PSOPrecache.GlobalShaders` | Precache global shader PSOs | L |
| `r.PSOPrecache.KeepInMemoryForActiveMaterials` | Precache memory behaviour | L |
| `r.ShaderPipelineCache.Enabled` | Use bundled PSO cache | D |
| `r.AllowStaticLighting` | 0 in fully dynamic projects (fewer permutations) | L |
| `r.SupportSkyAtmosphere`, `r.VolumetricCloud.Support`, `r.SupportLocalFogVolumes`, `r.SupportStationarySkylight` | Disable unused features → fewer shaders | L |
