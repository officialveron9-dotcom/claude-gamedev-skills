# Verified CVars: lighting and rendering (UE 5.8)

Only CVars with evidence for 5.8 are listed. Source tags:
- **[L]**: set or echoed in real UE 5.8.0-5.8.3 runtime/editor logs (see sources.md).
- **[S]**: present in Epic's engine `BaseScalability.ini` as shipped in 5.8-era builds. Values below are from it and match the 5.8 logs.
- **[D]**: named in current Epic documentation.
- **[R]**: named in the 5.8 release notes.

Value meanings marked "(verify)" are from long-standing engine behaviour, not re-confirmed for 5.8. Run `help <cvar>` in the console to confirm. Prefer Project Settings / PPV / scalability over raw CVars. Put permanent overrides in `DefaultEngine.ini [/Script/Engine.RendererSettings]` (project-level) or `DefaultScalability.ini` (tier-level), never in engine Base files.

## Project-level rendering features

| CVar | Use | Src |
|---|---|---|
| `r.DynamicGlobalIlluminationMethod` | 1 = Lumen (0 none, 2 SSGI — verify) | L |
| `r.ReflectionMethod` | 1 = Lumen, 2 = SSR, 0 = none (verify) | L |
| `r.RayTracing` | Support Hardware Ray Tracing (needs restart) | L |
| `r.Lumen.HardwareRayTracing` | Use HWRT for Lumen when available | L |
| `r.Lumen.HardwareRayTracing.LightingMode` | 0 = surface cache (template default); higher = hit lighting modes (verify) | L |
| `r.GenerateMeshDistanceFields` | Mesh SDFs; required for Lumen SWRT | L |
| `r.DistanceFields.DefaultVoxelDensity` | Global default SDF resolution | L |
| `r.AllowStaticLighting` | 0 for fully dynamic Lumen projects (also cuts permutations) | L |
| `r.Shadow.Virtual.Enable` | Virtual Shadow Maps on | L |
| `r.MegaLights.EnableForProject` | MegaLights (Production-Ready 5.8) | L |
| `r.PathTracing` | Compile path tracer shaders (needs `r.RayTracing`) | L |
| `r.ScreenPercentage.Default.PathTracer.Mode` | Screen-% mode while path tracing | L |
| `r.Substrate` | Substrate materials (restart; full recompile) | L |
| `r.Substrate.ProjectGBufferFormat` | Blendable vs Adaptive GBuffer | L |
| `r.Substrate.BytesPerPixel`, `r.Substrate.ClosuresPerPixel` | Substrate memory/closure budget | L |
| `r.Substrate.Glints`, `r.Substrate.RoughDiffuse`, `r.Material.RoughDiffuse` | Optional shading features | L |
| `r.ClearCoatNormal` | Enables the Clear Coat Bottom Normal output (legacy clear coat) | L |
| `r.VirtualTextures` | Streaming virtual texture support | L |
| `r.Lumen.TranslucencyReflections.FrontLayer.EnableForProject` | Allows high-quality translucency (glass) reflections | L |
| `r.Lumen.Reflections.HardwareRayTracing.Translucent.Refraction.EnableForProject` | HWRT refraction through translucency | L |
| `r.SkinCache.CompileShaders` | GPU skin cache; needed for skinned meshes in RT | L |
| `r.DefaultFeature.LightUnits` | Default unit for new lights (0 unitless, 1 candela, 2 lumen — verify) | L |
| `r.DefaultFeature.AutoExposure` | Project default auto exposure on/off | L |
| `r.DefaultFeature.AutoExposure.Method` | 0 = Histogram, 1 = Basic (verify) | L |
| `r.DefaultFeature.AutoExposure.Bias` | Default exposure bias (template 1.0) | L |
| `r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange` | EV100-based Min/Max (keep 1) | L |
| `r.DefaultFeature.LocalExposure.HighlightContrastScale` / `.ShadowContrastScale` | Templates write 0.8; 1.0 = no compression | L |
| `r.DefaultFeature.Bloom`, `.LensFlare`, `.MotionBlur` | Project defaults for those effects | L |

## Lumen (scalability-driven; override per tier in DefaultScalability.ini)

| CVar | Low / Med / High / Epic / Cine | Src |
|---|---|---|
| `r.Lumen.DiffuseIndirect.Allow` | 0 / 1 / 1 / 1 / 1 | S, L |
| `r.Lumen.FinalGatherMethod` | – / **0 (irradiance field = Lumen Lite)** / 1 / 1 / 1 | S, L |
| `r.Lumen.Reflections.Allow` | 0 / **0** / 1 / 1 / 1 | S, L |
| `r.Lumen.HardwareRayTracing.HitLighting.Allowed` | – / 0 / 0 / 1 / 1 | S, L |
| `r.Lumen.TraceMeshSDFs` / `.Allow` | Allow: – / 0 / 0 / 1 / 1 | S, L |
| `r.Lumen.ScreenProbeGather.DownsampleFactor` | – / – / 32 / 16 / 8 | S, L |
| `r.Lumen.ScreenProbeGather.TracingOctahedronResolution` | – / – / 8 / 8 / 16 | S, L |
| `r.Lumen.ScreenProbeGather.RadianceCache.ProbeResolution` | – / – / 16 / 32 / 32 | S, L |
| `r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor` | – / 1 / 2 / 1 / 1 | S, L |
| `r.Lumen.Reflections.DownsampleFactor` | – / – / 2 / 1 / 1 | S, L |
| `r.Lumen.TranslucencyReflections.FrontLayer.Allow` | – / – / 0 / 1 / 1 | S, L |
| `r.Lumen.TranslucencyReflections.FrontLayer.Enable` | – / – / 0 / 0 / 1 | S, L |
| `r.LumenScene.SurfaceCache.AtlasSize` | – / 2048 / 3584 / 4096 / 4096 | S, L |
| `r.LumenScene.SurfaceCache.CardTexelDensityScale` | – / 50 / 100 / 100 / 100 | S, L |
| `r.RayTracing.Geometry.SkeletalMeshes` | – / 0 / 1 / 1 / 1 | S, L |
| `r.MeshCardRepresentation.SkeletalMesh` | – / 0 / 1 / 1 / 1 | S, L |
| `r.SkylightIntensityMultiplier` | 0.8 / 1 / 1 / 1 / 1 | S, L |
| `r.SSR.Quality` (Reflection tier) | 0 / 2 / 2 / 3 / 4 | S, L |

Example override, keeping hit-lit reflections at High:
```ini
; Config/DefaultScalability.ini
[ReflectionQuality@2]
r.Lumen.Reflections.DownsampleFactor=1
[GlobalIlluminationQuality@2]
r.Lumen.HardwareRayTracing.HitLighting.Allowed=1
```

## MegaLights

| CVar | Note | Src |
|---|---|---|
| `r.MegaLights.NumSamplesPerPixel` | Shadow rays per pixel (Epic tier 4); fewer = noisier | S, L, D |
| `r.MegaLights.DownsampleMode` | Epic tier 2 | S, L |
| `r.MegaLights.ScreenTraces.Quality` | Epic tier 1 | S, L |

## Shadows

| CVar | Note | Src |
|---|---|---|
| `r.Shadow.Virtual.Cache` | 0 disables VSM caching (debug only) | D |
| `r.Shadow.Virtual.MaxPhysicalPages` | Page pool (Epic tier 4096) | S, L |
| `r.Shadow.Virtual.ResolutionLodBiasLocal` / `...LocalMoving` | Epic 0.0 / 1.0; lower = sharper local shadows, more pages | S, L |
| `r.Shadow.Virtual.ResolutionLodBiasDirectional` | Epic -1.5 | S, L |
| `r.Shadow.Virtual.SMRT.RayCountLocal` / `SamplesPerRayLocal` | Soft-shadow quality (Epic 8 / 4) | S, L |
| `r.Shadow.Virtual.DeferredInvalidationBudget` | 5.8: budget for LOD-delta invalidations | R |
| `r.Shadow.Virtual.PrefilteredDistant.ProjectEnable` | 5.8: gate for prefiltered distant shadows | R |
| `r.ContactShadows` | Global contact shadow toggle (per-light length still required) | L |

## Post, AA, exposure

| CVar | Note | Src |
|---|---|---|
| `r.AntiAliasingMethod` | 4 = TSR, 2 = TAA, 0 = none (verify) | L |
| `r.ScreenPercentage` | Internal render % (testing; ship via resolution quality) | L |
| `r.TSR.History.ScreenPercentage` | Low–High 100, Epic/Cine 200 | S, L |
| `r.TSR.History.UpdateQuality` | 0/1/2/3/3 | S, L |
| `r.TSR.ShadingRejection.Flickering` | 0/0/1/1/1, reduces specular flicker | S, L |
| `r.TSR.ThinGeometryDetection` | Helps cue sticks/thin wires | L |
| `r.DynamicRes.OperationMode` | Dynamic resolution (PC DX12/Vulkan support in 5.8) | L, R |
| `r.EyeAdaptationQuality` | Auto exposure quality (Epic 2) | S, L |
| `r.LocalExposure` | Local exposure on/off | L |
| `r.Tonemapper.Quality` | Epic/Cine 5 | S, L |
| `r.Tonemapper.Sharpen` | Post sharpening (0.25-0.5 useful with TSR) | L |
| `r.LUT.Size` | Grading LUT res (Epic 32, Cine 64) | S, L |
| `r.BloomQuality` | Epic 5 | S, L |
| `r.LensFlareQuality`, `r.SceneColorFringeQuality`, `r.MotionBlurQuality` | Per PostProcess tier | S, L |
| `r.DepthOfFieldQuality` | Epic 2, Cine 4 (full-res gather) | S, L |
| `r.DOF.Gather.ResolutionDivisor` | Epic 2, Cine 1 | S, L |
| `r.ReflectionCaptureResolution` | Capture cubemap size (fallback reflections) | L |
| `r.AnisotropicMaterials` | Anisotropy support (ShadingQuality High+) | S, L |
| `r.VT.MaxAnisotropy` | VT filtering | S, L |

## Not listed on purpose

PPV-only settings (Final Gather Quality, Lumen Scene Detail, Max Roughness To Trace, Ray Lighting Mode, Max Reflection Bounces, Diffuse Color Boost, Skylight Leaking) are set in the Post Process Volume. Their CVar twins were not verifiable for 5.8 here, so don't type guessed names.
