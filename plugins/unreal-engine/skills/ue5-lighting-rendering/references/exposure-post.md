# Exposure, physical camera and post process (UE 5.8)

Contents: exposure math · real-world targets · three exposure setups · local exposure · debug tools · tonemapper/grading/LUT · bloom/lens · DOF table.

## Exposure math (Epic Auto Exposure docs)

- Apply Physical Camera Exposure **on** (Manual metering only): `EV100 = log2(N² / t × 100 / ISO)` (N = f-stop, t = shutter seconds).
- Off: `Exposure = 1 / 2^(EV100 + Exposure Compensation)`.
- With *Extend default luminance range* on (default for new projects), the Min/Max fields are **EV100**. Off (old projects), they are luminance (cd/m²), so values copied between projects break.

| ISO | f-stop | Shutter | EV100 | Use |
|---|---|---|---|---|
| 1600 | 2.0 | 1/50 | ~3.6 | Very dark bar corner |
| 800 | 2.8 | 1/60 | ~5.9 | Typical dim bar photo |
| 400 | 4 | 1/60 | ~7.9 | Exposed for the bright table |
| 100 | 4 | 1/125 | ~11 | Bright retail/gallery |
| 100 | 16 | 1/125 | ~15 | Sunny exterior |

Real-world reference (photographic EV100 tables): home interiors 5-7, offices 7-8, galleries 8-11, night street/shop windows 7-8, floodlit buildings 3-5.

## Photometric helpers for lights

- Illuminance from a point/spot light: `E [lux] = I [cd] · cos(theta) / d²`. 520 lux at 1.0 m needs ~520 cd on-axis; at 1.65 m about 1400 cd.
- Isotropic point light: `I = Phi / (4π)`. An 800 lm bulb is ~64 cd; 1600 lm is ~127 cd.
- WPA table spec: ≥ 520 lux (48 fc) at every point of bed and rails. Fixture ≥ 40 in (1.02 m) above the bed if it can be moved aside, ≥ 65 in (1.65 m) if fixed. A reflector or screen keeps the centre from being noticeably brighter than the rails.
- Units: directional = lux; sky light/emissive = cd/m² luminance; point/spot/rect = candela, lumen or unitless. All of these require Inverse Squared Falloff.
- Prefer **candela** for spots and IES lights. It is the native IES quantity and stays stable when you change the cone angle.
- IES: assign the profile. With *Use IES Brightness* the file's candela values drive intensity; scale with *IES Intensity Scale*.

## Three exposure setups

**A. Locked (recommended while lighting, and for most of gameplay)**
- Metering Mode = Manual, Apply Physical Camera Exposure = on, set ISO/shutter/aperture from the table above, Exposure Compensation 0.
- Alternative: keep Auto Exposure Histogram with Min EV100 = Max EV100 = target. This behaves as fixed.
- Project-wide default: `r.DefaultFeature.AutoExposure=0` (5.8 logs show many projects ship this way).

**B. Guard-railed auto (walking from the dark bar to the bright table)**
- Auto Exposure Histogram (`r.DefaultFeature.AutoExposure.Method=0`).
- Min/Max EV100 = target ±1-1.5. Never the full default range indoors.
- Moderate Speed Up and slower Speed Down so the eye adapts naturally without pumping.
- Use a Metering Mask (centre-weighted texture) so the lamp housing at the frame edge doesn't drive exposure.
- Use the *Exposure Compensation Curve* (compensation as a function of average scene EV100) to keep dark scenes dark instead of lifting them to middle grey.

**C. Cinematic**
- Manual, with the physical camera matching the CineCamera's real f-stop (DOF and exposure stay consistent).
- Per-shot compensation keyframed in Sequencer.

Traps:
- A camera component's own Post Process settings override the level volume at blend weight 1. Check both.
- `r.DefaultFeature.AutoExposure.Bias` (template value 1.0) shifts auto exposure. Don't stack it with large PPV compensation.
- The Physical Camera aperture changes **brightness only in Manual + Apply Physical Camera Exposure**. It always changes DOF.

## Local exposure (window/lamp highlight control)

- PPV Local Exposure: Highlight Contrast Scale, Shadow Contrast Scale, Detail Strength, Blurred Luminance Blend.
- 5.8 project templates write `r.DefaultFeature.LocalExposure.HighlightContrastScale=0.8` and `...ShadowContrastScale=0.8`, so contrast is compressed by default. For a moody bar, start at 1.0/1.0. Lower highlights to ~0.6-0.8 only when windows or lamp shades blow out.
- Too much local exposure looks like HDR-photo haloing around lamps and silhouettes.

## Debug tools

- Level viewport *Lit > Exposure*: "Game Settings" uses the PPV; unchecked, it uses a manual EV100 slider. Many "wrong brightness" reports are this toggle.
- *Show > Visualize > HDR (Eye Adaptation)*: histogram, current and target exposure.
- *Window > Pixel Inspector*: scene colour/luminance per pixel. Compare felt vs lamp vs wall ratios with the Path Tracer.
- *Buffer Visualization > Base Color / Roughness*: catch out-of-range albedo before blaming exposure.

## Tonemapper, grading, LUT

- Leave Film (Slope/Toe/Shoulder/Black Clip/White Clip) at defaults until lights and exposure are final. Bending the curve to hide wrong light ratios breaks HDR output and the path-traced reference.
- Grade in this order: White Balance (Temp/Tint) → Global/Shadows/Midtones/Highlights → LUT last.
- LUT: grade a screenshot taken with a neutral LUT and *all other grading neutral*, otherwise the grade is applied twice.
  - Import the strip with Texture Group = ColorLookupTable.
  - Internal LUT resolution follows `r.LUT.Size` (32 at Epic, 64 at Cinematic PostProcessQuality).
- An SDR-authored LUT does not translate to HDR output. Prefer PPV colour wheels if HDR is a target.
- `r.Tonemapper.Sharpen`: 0.25-0.5 counters TSR softness. Higher rings around ball highlights.

## Bloom, lens, motion blur

- Bloom Method: Standard (cheap; gameplay) vs Convolution (FFT kernel; realistic glare, expensive, use for cinematics/screens).
- Many small specular highlights on glossy balls means bloom adds halos. Keep intensity low.
- Lens flares are off in new-project defaults (`r.DefaultFeature.LensFlare=0`). Don't enable them for an interior unless stylised.
- Chromatic aberration (Scene Color Fringe), vignette and film grain: subtle (vignette ≤ ~0.4). Grain can mask Lumen noise but also hides texture detail on the felt.
- Motion blur on rolling balls reads well at 30 fps cinematics. In gameplay it smears ball numbers; consider lower amount or max distortion.

## Depth of field (Cinematic DOF)

- Driven by Focal Distance, Aperture (f-stop) and sensor width (CineCamera Filmback). Number of diaphragm blades and Maximum Aperture shape the bokeh.
- Quality via `r.DepthOfFieldQuality` / PostProcessQuality (Cinematic gathers at full res, so it costs a lot more).
- CineCamera *Focus Method = Tracking* on the cue ball keeps focus during shots.
- "Depth Blur km for 50%" is not used by Cinematic DOF; ignore it.

Approximate total depth of field, 50 mm lens, full-frame (circle of confusion 0.03 mm):

| Focus distance | f/2.8 | f/5.6 | f/11 |
|---|---|---|---|
| 0.3 m | ~6 mm | ~12 mm | ~24 mm |
| 0.5 m | ~17 mm | ~34 mm | ~66 mm |
| 1.0 m | ~67 mm | ~134 mm | ~264 mm |

- A 35 mm lens roughly doubles these values at the same distance.
- A 57 mm ball fully sharp at 0.3-0.5 m needs about f/11-f/16, or step back with a longer lens.
- Shallow DOF on real-scale objects is what makes renders look like miniatures (tilt-shift effect).
