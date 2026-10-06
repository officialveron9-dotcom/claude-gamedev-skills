# Visual issues: symptom → cause → fix (UE 5.8)

Always isolate first. Freeze exposure (manual), compare against *View Mode > Path Tracing*, and toggle the suspect feature with its show flag or CVar.

## Lighting / GI

| Symptom | Cause | Fix |
|---|---|---|
| Light bleeds through wall/ceiling seams | SWRT distance field too coarse; walls < ~10 cm; single-sided meshes | Thicken, close room, Distance Field Resolution Scale ↑, or HWRT |
| Interior glows with sky light at night | Sky Light on; Skylight Leaking > 0; sky occlusion leaking through gaps | Sky light off/low; Skylight Leaking 0; seal geometry |
| Blotchy GI | Screen probe undersampling; missing surface cache | Final Gather Quality ↑; fix pink areas in *Lumen > Surface Cache* view |
| Noise in shadowed bar areas | Indirect-only lighting; tiny bright emissives | Add real fill lights; enlarge/dim emissive; Final Gather Quality ↑ |
| GI lags 0.5-1 s after lamp switch | Lumen temporal accumulation | Lumen Scene Lighting Update Speed and Final Gather Lighting Update Speed ↑ (cost) |
| Whole scene tinted green | Felt albedo too bright/saturated; Diffuse Color Boost > 1 | Felt max channel ≤ ~0.25; Diffuse Color Boost 1 |
| Lighting changes between Epic and Medium | Medium = Lumen Lite irradiance field + SSR (5.8) | Expected; tune Medium separately, add reflection captures |
| Lights ignore physical values / editor shows "unitless" | Inverse Squared Falloff off, or light still in Unitless | Enable falloff; Intensity Units = Candelas |
| Lighting channel set but bounce still appears | Lighting channels gate direct lighting; GI from the lit surface still propagates | Use channels for direct rim/kicker lights only; verify the GI result in the path tracer |
| "Lighting needs to be rebuilt" in a Lumen project | Static/stationary lights with static lighting allowed | Movable lights; `r.AllowStaticLighting=0` |

## Reflections

| Symptom | Cause | Fix |
|---|---|---|
| Characters invisible in ball reflections when off-screen | SWRT; skinned meshes not in RT | HWRT; skin cache; `r.RayTracing.Geometry.SkeletalMeshes=1` |
| Reflections flat/dark vs path tracer | Surface-cache lighting | Ray Lighting Mode = Hit Lighting for Reflections + `r.Lumen.HardwareRayTracing.HitLighting.Allowed=1` (Epic tier) |
| Balls reflect nothing on Medium | Lumen reflections off at Reflection Quality ≤ 1 → SSR only | Sphere reflection capture over the table; room captures |
| Faceted reflections of rails/balls | HWRT traces the Nanite fallback mesh | Lower Fallback Relative Error on hero meshes |
| Reflections smear when the ball rolls | Temporal reflection history; low internal res | Higher screen %; Reflections Quality ↑; check TSR |
| Rough wood reflections noisy | Traced up to Max Roughness To Trace 0.4 | Lower to ~0.25-0.3 (rough falls back to GI-based specular) |
| Highlights on balls are tiny dots | Light Source Radius / rect size 0 | Set emitter size to the real shade opening |
| Glass missing in reflections | Max Refraction Bounces 0 | Set to 1-2 (hero shots) |

## Shadows

| Symptom | Cause | Fix |
|---|---|---|
| Ball shadows razor-sharp, CG look | Source Radius 0 | Real emitter size → SMRT soft shadows |
| Shadows shimmer/blocky when camera moves | VSM page invalidation; ResolutionLodBias too high | Reduce WPO/PDO near table; check *Visualize > Virtual Shadow Map*; tier settings |
| Shadow "pops" on characters | Non-Nanite/skeletal pages re-rendering; LOD switches | Expected cost; keep LOD0 at close range; contact shadows for fine detail |
| Light peeks under the ball (no contact) | Shadow bias at tiny scale | Contact Shadow Length (small) on key lights; verify with path tracer |
| Contact shadows halo around fingers/cue | Screen-space contact shadow too long | Shorten Contact Shadow Length; use world-space units option |

## Exposure / tone

| Symptom | Cause | Fix |
|---|---|---|
| Washed out, no blacks | Auto exposure to middle grey; local exposure 0.8 defaults; bloom | Manual EV; LocalExposure contrast 1.0; less bloom |
| Pumping | Wide EV range, histogram dominated by lamp | Lock or narrow EV; metering mask; slower speeds |
| Different brightness in PIE vs viewport | Viewport exposure override; camera PP | Lit > Exposure "Game Settings"; inspect camera post-process |
| Banding in dark gradients (walls) | 8-bit output after grading; heavy LUT | Film grain small; less extreme grade; HDR output if available |

## Anti-aliasing / temporal

| Symptom | Cause | Fix |
|---|---|---|
| Cue stick breaks up/flickers | Sub-pixel thin geometry | `r.TSR.ThinGeometryDetection=1`; higher screen %; slightly thicker cue tip mesh |
| Ghost trail behind fast balls | Low internal resolution; disocclusion | Screen % ≥ 66; AA quality High+ (TSR history settings) |
| Specular sparkle on lacquer/ball edges | Too low roughness; no specular AA | Roughness floor; Composite Texture on roughness; flicker rejection |
| Soft/blurry image overall | Upscaling from low %, TSR history 100 % | Epic AA tier (history 200 %); `r.Tonemapper.Sharpen` 0.25-0.5 |
| Upscaler plugin ghosting | DLSS/FSR/XeSS mode/preset | Try another preset; compare to TSR; re-test after plugin update |

## Materials

| Symptom | Cause | Fix |
|---|---|---|
| Felt looks like plastic | No fuzz/sheen, roughness too low | Fuzz (Substrate) or Cloth model; roughness 0.8-1.0 |
| Balls look like CG spheres | Perfect uniform coat; no roughness variation; point highlights | Smudge/scratch roughness mask; emitter sizes; chalk marks |
| Visible felt tiling in wide shots | Single tiling normal map | Macro variation mask; second detail scale |
| Upgraded project ignores Substrate nodes | Substrate disabled (legacy path) | Enable `r.Substrate=1`, restart, re-check all materials |
| Material costs explode with Substrate | Adaptive GBuffer + many layers | Blendable format; fewer closures (`r.Substrate.ClosuresPerPixel`) |
