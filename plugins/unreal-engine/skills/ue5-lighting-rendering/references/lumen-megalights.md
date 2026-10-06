# Lumen and MegaLights: settings, traps, fixes (UE 5.8)

Contents: HW vs SW decision · scalability tiers (what each tier really does) · PPV settings with recommended values · Lumen scene requirements · artifact table · emissive · MegaLights.

## HWRT vs SWRT decision

| Need | Choose | Why |
|---|---|---|
| Characters visible in reflections/GI | HWRT | SWRT traces distance fields; skinned meshes are not in them |
| Accurate reflections of lamps, other balls, glass | HWRT + Hit Lighting | SWRT reflections use low-res surface-cache lighting |
| Min-spec GPU without RT cores | SWRT (needs `r.GenerateMeshDistanceFields=1`) | SWRT runs on any SM6 GPU |
| Thin interior walls you can't rebuild | HWRT | Triangles instead of distance fields, so fewer leaks |

- SWRT detail: per-mesh distance fields are traced for the first ~2 m, then the merged Global Distance Field. Walls thinner than ~10 cm collapse in the SDF and leak.
- HWRT traces the **Nanite fallback mesh** of Nanite meshes. Hero curved meshes (rails, balls, lamp shades) need a fine fallback, or RT shadows and reflections look faceted.
- Skinned meshes in RT need the GPU skin cache (`r.SkinCache.CompileShaders=1`) and `r.RayTracing.Geometry.SkeletalMeshes=1`. BaseScalability sets the latter to 1 at GI High+ and 0 at Medium.

## What the scalability tiers actually set (5.8 BaseScalability, Lumen-relevant)

| Tier (sg level) | GI | Reflections | Notes |
|---|---|---|---|
| Low (0) | Lumen off (`r.Lumen.DiffuseIndirect.Allow=0`), DFAO off, `r.SkylightIntensityMultiplier=0.8` | Lumen off, SSR off | Needs captures and a sky light, or the interior goes flat |
| Medium (1) | **Lumen Lite**: `r.Lumen.FinalGatherMethod=0` (irradiance field gather), surface cache atlas 2048, no mesh-SDF tracing | **Lumen reflections off** → SSR (`r.SSR.Quality=2`) + reflection captures | 5.8 targets 60 fps on Switch 2 / mid PC; balls lose off-screen reflections |
| High (2) | Screen probe gather (`FinalGatherMethod=1`), `DownsampleFactor=32`, `HitLighting.Allowed=0` | Lumen, `r.Lumen.Reflections.DownsampleFactor=2` | Epic's 60 fps console target (~4 ms Lumen at 1080p) |
| Epic (3) | `DownsampleFactor=16`, mesh SDF tracing on, `HitLighting.Allowed=1` | Full res, front-layer translucency reflections allowed | 30 fps console target (~8 ms Lumen at 1080p) |
| Cinematic (4) | `DownsampleFactor=8`, radiance cache budget 350 | Front-layer translucency reflections enabled | For Movie Render Graph and screenshots |

Traps:
- "Hit Lighting for Reflections" in the PPV does nothing at High: `r.Lumen.HardwareRayTracing.HitLighting.Allowed=0` there. Use Epic, or override the CVar in your DefaultScalability.ini.
- If Medium is a target, place reflection captures and test Medium explicitly.
- Override tiers in `Config/DefaultScalability.ini` (same `[GlobalIlluminationQuality@2]` section names), never in engine Base files.

## Post Process Volume: Lumen settings for a hero interior

| Setting (PPV) | Default | Pool-hall hero value | Effect / trap |
|---|---|---|---|
| Lumen Scene Lighting Quality | 1 | 1-2 | Surface-cache lighting resolution; helps splotchy reflections |
| Lumen Scene Detail | 1 | 1-2 | Keeps smaller meshes (balls, bottles) in the Lumen scene; cost ↑ |
| Lumen Scene View Distance | 200 m | 20-50 m (interior) | Shorter is cheaper and plenty indoors |
| Lumen Scene Lighting Update Speed | 1 | 1-2 | Faster reaction to lamp toggles |
| Final Gather Quality | 1 | 1-2 (hero), 1 (gameplay) | Main noise vs cost knob; > 2 gets very expensive |
| Final Gather Lighting Update Speed | 1 | 1-2 | Less GI lag on moving objects |
| Max Trace Distance | — | room size | Cheaper; too short loses sky/large-scale occlusion |
| Diffuse Color Boost | 1 | **1** | > 1 inflates bounce, so the felt floods the scene green |
| Skylight Leaking | 0 | **0** | > 0 adds fake ambient, lifting blacks indoors |
| Reflections > Quality | 1 | 1-2 | Reflection rays per pixel |
| Max Roughness To Trace | 0.4 | 0.4 (balls ≤ 0.1 always traced) | Lowering to ~0.25 saves cost on rough wood/leather |
| Ray Lighting Mode | Surface Cache | Hit Lighting for Reflections (Epic) | HWRT only; big quality win for glossy balls |
| Max Reflection Bounces | — | 2 for hero shots | Ball-in-ball; needs hit lighting; costly |
| Max Refraction Bounces | 0 | 1-2 if glassware matters | Glass visible in reflections |
| High Quality Translucency Reflections | per project | on for glass bar items | Needs `r.Lumen.TranslucencyReflections.FrontLayer.EnableForProject=1` |
| Screen Traces | on | on | Turn off only to inspect the pure ray-traced result |

## Lumen scene requirements checklist

- [ ] Real-world scale. Walls, floor and ceiling closed and ≥ ~10 cm thick. No single-sided walls.
- [ ] Large meshes split (an entire room as one mesh gets poor card coverage). Check *Visualize > Lumen > Surface Cache*: pink = no coverage, so fix the mesh or raise *Max Lumen Mesh Cards* (Static Mesh build settings).
- [ ] *Visualize > Mesh Distance Fields*: thin parts present? Raise *Distance Field Resolution Scale* per mesh, or use HWRT.
- [ ] Lights Movable (fully dynamic project, `r.AllowStaticLighting=0`).
- [ ] Hidden-in-game or editor helper meshes not polluting the Lumen scene (Affect Distance Field Lighting / Visible in Ray Tracing flags).
- [ ] Characters: HWRT + skin cache + skeletal meshes in RT (see above).

## Lumen artifact table

| Symptom | Cause | Fix |
|---|---|---|
| Bright seams/leaks along wall-ceiling joints | SWRT SDF of thin or open walls | Thicken and close; Distance Field Resolution Scale ↑; HWRT |
| Sky light glowing inside a closed room | Sky occlusion leaking through thin geometry; Skylight Leaking > 0 | Fix geometry; Skylight Leaking 0; sky light off for night scenes |
| Splotches / low-frequency blobs in corners | Too few screen probes; poor surface cache | Final Gather Quality ↑; fix cards; Lumen Scene Lighting Quality ↑ |
| Speckle noise in dark areas lit by bounce | Few rays vs dim indirect; tiny bright emissive | Add real fill lights; Final Gather Quality ↑; enlarge or dim the emissive |
| Ghost trails behind rolling balls/cue | Temporal accumulation of GI/reflections; low-res TSR input | Update Speed ↑; screen % ↑; check TSR settings |
| Black/missing objects in reflections | Object outside Lumen scene (too small, culled) or skinned (SWRT) | Lumen Scene Detail ↑; HWRT; "Visible in Ray Tracing" on |
| Reflections lit wrongly (too dark/flat) | Surface-cache lighting | Hit Lighting for Reflections (HWRT, Epic tier or CVar override) |
| Reflections disappear on Medium settings | 5.8 Medium = Lumen Lite, reflections fall back to SSR | Reflection captures; or keep Reflection Quality ≥ High |
| GI too weak vs path tracer | Lumen Scene too coarse; emissive-only lighting | Real lights; Lumen Scene Lighting Quality ↑ |
| Dark halo/AO under balls too strong or missing | Short-range AO / screen traces | Compare with path tracer; ShortRangeAO CVars are scalability-tier controlled |
| Translucent glass dark/flat | Translucency volume is low-res | Front-layer translucency reflections; Max Refraction Bounces |

## Emissive limits

- Emissive feeds Lumen GI at no extra light cost, but small and very bright emissive areas create noise. Lumen finds them by chance, not by sampling them as lights.
- Emissive gives no analytic specular highlight on balls and no sharp shadows. Every lamp needs a real light; the emissive mesh is only the visible bulb/shade.
- Neon signs: emissive tube plus a rect light along it (shadows often off) for clean illumination.

## MegaLights (Production-Ready in 5.8)

- Enable: Project Settings > Rendering > Direct Lighting > MegaLights (`r.MegaLights.EnableForProject=1`). The editor prompts to enable Support Hardware Ray Tracing (recommended).
- How it works: a fixed number of shadow rays per pixel (`r.MegaLights.NumSamplesPerPixel`, Epic tier = 4), importance-sampled over lights. Cost is roughly flat in light count, and noise grows with the number of significant overlapping lights.
- Per-light *MegaLights Shadow Method*: Ray Tracing (default, correct area shadows, no per-light cost) or Virtual Shadow Maps.
- 5.8 additions: less noise; lighting channels; IES for volumetrics and translucency; transmission (SSS); froxel translucency; front-layer translucency lighting; light finder and ray visualizer tools.
- Traps:
  - With few lights (one table, 3 lamps) MegaLights adds noise for little gain. Use classic VSM lights.
  - Use it when a bar full of practicals needs shadows.
  - Directional light + MegaLights RT shadows: volumetric clouds can't receive opaque shadows (no VSM exists). Irrelevant indoors, relevant for exterior shots.
  - Deferred renderer only. Not for forward/VR/mobile.
  - Compare noise in motion in Standalone; temporal denoising looks better in a still editor viewport.
