---
name: ue5-lighting-rendering
description: "Provides pitfalls, verified settings and fix tables for photoreal rendering in Unreal Engine 5.8 (current release): Lumen GI/reflections (HW vs SW ray tracing, Lumen Lite, leaks, noise, splotches, ghosting, emissive limits), MegaLights, physical light units, exposure (manual vs auto, EV100, physical camera, pumping, washed-out or dark images, local exposure), tonemapper/bloom/DOF/LUTs, Virtual Shadow Maps, reflections on glossy spheres, Substrate/clear-coat/cloth materials, TSR/DLSS/FSR/XeSS, Path Tracer reference. Use when setting up or debugging lighting, exposure, materials or image quality, e.g. a pool hall with glossy balls on felt. Triggers: Lumen, MegaLights, exposure, EV100, post process, Substrate, clear coat, VSM, TSR, path tracer, reflections, Beleuchtung, Belichtung, Grafik, Licht, Schatten, Reflexionen, Materialien, fotorealistisch, zu dunkel, ueberbelichtet."
---

# UE5 lighting & rendering: traps, settings, fixes (UE 5.8)

Scope: image quality for a photoreal interior (pool hall, close-ups of glossy balls on felt, characters at the table). Performance tuning lives in the `ue5-performance-optimization` skill.

## Version status that changes decisions (UE 5.8.x, Oct 2026)

| Feature | Status | Consequence |
|---|---|---|
| Lumen HWRT | Default/recommended path since 5.5; HWRT perf work in 5.6 | Prefer HWRT on RT-capable GPUs; SWRT is the fallback |
| Lumen Lite | New in 5.8, used at GI+Reflection quality **Medium** | Medium = irradiance-field GI **and no Lumen reflections (SSR fallback)** |
| MegaLights | Exp. 5.5-5.6, Beta 5.7, **Production-Ready 5.8** | Viable for many shadowed bar lights; HWRT recommended |
| Substrate | Exp. 5.2, Beta 5.5, **Production-Ready 5.7**; default for projects *created* in 5.7+ | Upgraded projects stay legacy until opted in |
| Nanite Tessellation | Experimental; 5.8 displacement regressions reported | Don't ship felt/wood detail on it; use normal maps |
| Dynamic Resolution on PC (DX12/Vulkan) | Enabled in 5.8 | Usable as a GPU-load safety net |

## Ten traps that ruin this scene

1. **Auto exposure left on while lighting.** Every intensity change gets "corrected" away. Light with fixed exposure (manual or Min EV100 = Max EV100), then decide on auto.
2. **Unphysical scale.** Ball 57.15 mm, 9-ft playfield 2.54 x 1.27 m. Wrong scale breaks inverse-square falloff, DOF, Lumen trace distances and VSM resolution.
3. **Thin or single-sided walls/ceiling** (< ~10 cm). Causes Lumen SWRT light and sky leaking. Close the room and give walls thickness.
4. **Lamp light from emissive meshes only.** Small, bright emissive surfaces cause Lumen noise and cast no proper shadows or highlights. Use real lights and let emissive only *look* bright.
5. **Medium scalability without reflection captures.** Lumen reflections are off at Reflection Quality <= Medium (5.8), so the balls fall back to SSR plus captures. With no capture placed, they reflect nothing off-screen.
6. **SWRT with characters around the table.** Software Lumen can't trace skinned meshes, so players only show up in ball reflections through screen traces. Use HWRT with skeletal meshes in RT.
7. **Coarse Nanite fallback meshes.** HWRT traces the fallback mesh, so round rails or balls look faceted in reflections and RT shadows. Lower *Fallback Relative Error* on hero meshes.
8. **Local exposure defaults flatten contrast.** 5.8 project templates write `r.DefaultFeature.LocalExposure.HighlightContrastScale/ShadowContrastScale=0.8`. Set them to 1.0 for faithful contrast, then dial back down if you want.
9. **DOF at real camera values too shallow for macro shots.** f/4 at 30 cm on full frame gives about 9 mm of focus depth. A ball does not fit, and the shot reads like a miniature.
10. **Judging the look in the editor viewport.** Viewport exposure ("Game Settings" unchecked), editor-only scalability and PIE overhead all mislead. Verify in Standalone at the target scalability, and against the Path Tracer.

## Step-by-step: realistic indoor pool-hall setup

1. **Project settings** (Rendering):
   - Dynamic GI = Lumen (`r.DynamicGlobalIlluminationMethod=1`) and Reflections = Lumen (`r.ReflectionMethod=1`).
   - Support Hardware Ray Tracing (`r.RayTracing=1`) and Use HWRT when available (`r.Lumen.HardwareRayTracing=1`).
   - Generate Mesh Distance Fields on (`r.GenerateMeshDistanceFields=1`), which SWRT fallback needs.
   - Shadow Map Method = VSM (`r.Shadow.Virtual.Enable=1`).
   - AA = TSR (`r.AntiAliasingMethod=4`).
   - Path Tracing on (`r.PathTracing=1`) for reference renders.
   - Fully dynamic project: Allow Static Lighting off (`r.AllowStaticLighting=0`). This also cuts shader permutations.
   - Default Light Units = Candelas (`r.DefaultFeature.LightUnits=1`).
   - Extend default luminance range on (`r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=1`).
   - Upgraded project: decide on Substrate now (`r.Substrate=1`). Switching later recompiles everything.
2. **Geometry hygiene.** Real-world scale. Closed room with floor, ceiling and thick walls. No single-sided planes as walls. Check *Show > Visualize > Mesh Distance Fields* and *Lumen > Surface Cache* (pink = no coverage).
3. **Lock exposure first.** Use an unbound Post Process Volume: Exposure > Metering Mode = Manual, Exposure Compensation 0, Apply Physical Camera Exposure on. Start at ISO 800, f/2.8, 1/60 s (EV100 ~ 5.9, a typical dim bar photo). For a table-focused look, use ISO 400, f/4, 1/60 (EV100 ~ 7.9). See [references/exposure-post.md](references/exposure-post.md).
4. **Key lights: the table lamps.**
   - Use spot lights in candela, with an IES profile or barn-door rect lights sized to the shade/diffuser.
   - Set Source Radius (spot) or Source Width/Height (rect) to the real emitter size. This drives both the specular highlight shape on the balls and VSM penumbra softness.
   - Target: WPA spec is >= 520 lux uniform on the bed. Illuminance below a light is E = I·cos(theta)/d², so 520 lux at 1.0 m needs about 520 cd on-axis. Three overlapping shades at ~1 m: start at 250-400 cd each.
   - Inverse Squared Falloff must stay on; physical units need it.
5. **Practicals and ambience.**
   - Bar pendants: 60 W-equivalent bulb ~ 800 lm, 100 W-eq ~ 1600 lm.
   - Neon/signs: emissive mesh plus a matching rect/point light for the actual illumination.
   - Keep room ambience 1-3 stops below the table. Real bars are dark around a bright table.
6. **Sky/windows.**
   - Night interior: Sky Light low or off; check that it doesn't leak.
   - Daylight through windows: directional light in lux (sun ~ 100k lux) plus Sky Light. Expect blown-out windows at interior EV; tame them with local exposure, not by dimming the sun.
7. **Many lights?**
   - More than ~8-10 shadowed local lights overlapping on screen: enable MegaLights (`r.MegaLights.EnableForProject=1`, 5.8 production-ready) with HWRT.
   - Otherwise switch off shadows on fill lights and keep Attenuation Radius tight.
8. **Lumen quality for hero shots** (Post Process Volume):
   - Final Gather Quality 1-2, Lumen Scene Detail 1-2, Max Roughness To Trace 0.4 (default).
   - Ray Lighting Mode = Hit Lighting for Reflections when HWRT is available (Epic tier).
   - Details: [references/lumen-megalights.md](references/lumen-megalights.md).
9. **Reflection fallback.** Place one Sphere Reflection Capture centred above the table at ball height, plus room captures. Lower tiers use them.
10. **Materials.** Ball, felt, wood, metal and leather recipes are in [references/materials.md](references/materials.md). Validate albedo/roughness ranges in *Buffer Visualization*.
11. **Post.**
    - Tonemapper Film defaults.
    - Bloom low (Standard, not Convolution, for gameplay).
    - Vignette and grain subtle.
    - Colour grade with white balance first, LUT last.
    - DOF via CineCamera with real f-stops (f/5.6-f/11 for close-ups).
12. **AA.** TSR at Epic AA quality (history 200 %). Thin geometry detection helps cue sticks (`r.TSR.ThinGeometryDetection`).
13. **Ground truth.** Switch the viewport to *Path Tracing* (same exposure) and compare light levels, felt colour bleed, reflection content and contact darkening. Fix lights and materials first, Lumen settings last.
14. **Verify in Standalone** at each scalability level (Epic/High/Medium). Pay particular attention to Medium (Lumen Lite + SSR).

## Exposure: symptom → cause → fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Image greyish/washed out, blacks lifted | Auto exposure pushes dark bar to middle grey; local exposure < 1; bloom/haze; Lumen *Skylight Leaking* > 0 | Manual exposure; LocalExposure contrast scales 1.0; bloom down; Skylight Leaking 0 |
| Everything near-black after switching to physical units | Exposure still at a daylight-ish EV, or lights still in old unitless values | EV100 ~6-8 for interior; re-enter intensities in cd/lm |
| Brightness "pumps" when camera moves from felt to lamp | Wide Min/Max EV100 range, fast adaptation, highlight-dominated histogram | Lock EV (Min = Max) or narrow to ±1 EV; slower Speed Up/Down; metering mask; Manual for gameplay |
| Editor looks right, game doesn't | Viewport exposure override; camera's own PP settings; volume not unbound; different scalability | Lit menu > Exposure "Game Settings"; check camera PP weight; Infinite Extent (Unbound) |
| Physical camera f-stop has no effect on brightness | Apply Physical Camera Exposure is only honoured in Manual metering | Use Manual + Apply Physical Camera Exposure |
| Neon/bulb meshes look dull grey | Emissive too low for physical EV | Raise emissive until it clips slightly at the target EV; check *Visualize > HDR (Eye Adaptation)* |
| Old project: Min/Max "Brightness" behave oddly | Extend default luminance range off (values in cd/m², not EV100) | Enable `r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=1`, re-enter values |

Full formulas, EV tables and PPV values: [references/exposure-post.md](references/exposure-post.md).

## Lumen: fast triage

| Symptom | First thing to check | Typical fix |
|---|---|---|
| Light/sky leaking at wall-ceiling seams | Wall thickness, single-sided meshes, SWRT | Thicken (>= 10 cm), close geometry, HWRT, raise mesh Distance Field Resolution Scale |
| Blotchy/splotchy GI in corners | Surface cache coverage (pink), Final Gather Quality | Fix cards (split huge meshes, Max Lumen Mesh Cards), Final Gather Quality 2 |
| Crawling noise in dim areas | Lit mostly by bounce or small emissive | Add real fill lights; Final Gather Quality ↑; avoid tiny bright emissive |
| Lighting lags or ghosts after a lamp toggles or balls move | Temporal accumulation | Raise Lumen Scene Lighting Update Speed / Final Gather Lighting Update Speed (cost ↑) |
| Players missing in ball reflections | SWRT (no skinned meshes) | HWRT + skeletal meshes in RT (`r.RayTracing.Geometry.SkeletalMeshes=1`) + skin cache |
| Reflections dull or flat-lit | Surface-cache lighting in reflections | Ray Lighting Mode = Hit Lighting for Reflections (HWRT) |
| Green felt over-tints everything | Diffuse Color Boost > 1 or felt albedo too high | Diffuse Color Boost 1; felt albedo per materials reference |

Deep dive with all settings and 5.8 Lumen Lite/MegaLights pitfalls: [references/lumen-megalights.md](references/lumen-megalights.md).

## Reflections on glossy balls

- Highlights from lights are analytic: their shape and size come from Source Radius / rect size, not Lumen. Size them to the real lamp opening, or the balls get pin-point CG highlights.
- Environment reflections come from Lumen: screen traces first, then the ray-traced Lumen scene.
  - SWRT: distance fields + surface cache, no skinned meshes, small meshes culled.
  - HWRT: triangles. With Hit Lighting, materials and lights are evaluated at the hit point.
- Ball-in-ball inter-reflections need HWRT hit lighting. Raise *Max Reflection Bounces* (PPV) only for hero shots.
- Glass and bottles in reflections: *Max Refraction Bounces*, plus Front Layer Translucency Reflections (`r.Lumen.TranslucencyReflections.FrontLayer.EnableForProject`).
- Reflection captures are ignored while Lumen reflections run. They are the fallback for Medium/Low. Capture resolution: `r.ReflectionCaptureResolution`.
- Specular shimmer on ball edges in motion:
  - TSR flicker rejection: `r.TSR.ShadingRejection.Flickering=1` (on at High+).
  - Roughness floor ≥ ~0.02.
  - Normal-map roughness composite (texture *Composite Texture*) for specular AA.

## Shadows (VSM)

- Static room and table: set *Shadow Cache Invalidation Behavior = Static*.
- Balls and cue (no WPO): Rigid/Auto.
- Any WPO or Pixel Depth Offset material invalidates cached pages every frame. Keep both off on everything near the table.
- Penumbra comes from light source size (SMRT). Hard, CG-looking ball shadows mean Source Radius is too small.
- VSM contact precision is usually enough for ball-on-felt. Use per-light *Contact Shadow Length* (`r.ContactShadows` must be on) for hair, cloth folds and fingers. Keep it small; it is screen-space and can halo.
- Debug views: *Show > Visualize > Virtual Shadow Map* (cached vs invalidated pages). `r.Shadow.Virtual.Cache 0` only for A/B testing.
- Non-Nanite high-poly meshes are expensive to render into VSM pages. Make static props Nanite.

## Materials (summary; full recipes in references)

| Surface | Model | Key values (linear) |
|---|---|---|
| Phenolic ball | Substrate slab + coat (*Substrate Simple Clear Coat* / vertical layer) or legacy Clear Coat | coat roughness 0.02-0.06, base roughness 0.15-0.3, white ball albedo ≤ 0.8 |
| Worsted felt | Substrate slab with Fuzz, or legacy Cloth | roughness 0.8-1.0, fuzz amount 0.3-0.8, albedo dark-mid (max channel ~0.1-0.25) |
| Lacquered wood | Slab + coat / legacy Clear Coat | coat 0.05-0.15, base 0.4-0.6 |
| Chrome/brass fittings | Metallic 1 | chromium ~0.55 grey, roughness 0.05-0.2 |

Traps:
- Saturated, bright felt albedo plus Lumen equals a green room.
- Specular input left at 0 or 1 on dielectrics. Keep 0.5, i.e. 4 % F0.
- Upgraded projects silently stay non-Substrate.

## AA and upscaling

- TSR is the default. Quality comes from `sg.AntiAliasingQuality`: Epic sets `r.TSR.History.ScreenPercentage=200`.
- Close-ups of ball numbers and felt weave: keep the internal resolution ≥ 66 %.
- DLSS/FSR/XeSS are vendor plugins (not bundled). Check each plugin's release supports 5.8. Enable only one, keep TSR as fallback, and re-check ghosting on fast balls.

## Reference files (read when needed)

- [references/lumen-megalights.md](references/lumen-megalights.md): read when tuning Lumen quality, fixing leaks/noise/ghosting, choosing HW vs SW RT, or enabling MegaLights / Lumen Lite.
- [references/exposure-post.md](references/exposure-post.md): read when setting exposure, physical camera, local exposure, tonemapper, bloom, DOF or LUT grading.
- [references/materials.md](references/materials.md): read when authoring ball/felt/wood/metal materials, deciding on Substrate, texel density or virtual textures.
- [references/common-issues.md](references/common-issues.md): read when a visual artifact must be diagnosed (full symptom → cause → fix table).
- [references/cvars.md](references/cvars.md): read before typing any CVar; lists only CVars verified for 5.8 with source tags.
- [references/sources.md](references/sources.md): provenance of every claim.
