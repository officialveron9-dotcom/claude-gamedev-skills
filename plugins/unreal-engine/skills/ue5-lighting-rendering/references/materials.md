# Materials for a photoreal pool hall (UE 5.8)

Contents: Substrate decision and traps · PBR value ranges · recipes (balls, felt, wood, metal, leather, chalk, glass) · specular aliasing · texel density · virtual textures.

## Substrate: decide once, early

- Status: Production-Ready since 5.7. **Enabled by default only for projects created in 5.7+**. Projects upgraded from older versions stay on the legacy path until *Project Settings > Rendering > Substrate* (`r.Substrate=1`) is enabled and the editor restarted.
- Enabling converts legacy materials automatically (each root node maps to a Slab). Toggling later means a full shader recompile and a visual re-check of every material. Decide before content production.
- GBuffer format (Project Settings, `r.Substrate.ProjectGBufferFormat`):
  - **Blendable**: fixed memory, performance on par with legacy, for 60 Hz.
  - **Adaptive**: richer layering, cost depends on on-screen material complexity, ~15 % longer cooks.
  - Pick Blendable unless you need multi-layer materials everywhere.
- Related knobs (in 5.8 logs): `r.Substrate.BytesPerPixel`, `r.Substrate.ClosuresPerPixel`, `r.Substrate.Glints`, `r.Substrate.RoughDiffuse`.
- 5.8 adds Substrate Toon (experimental) and AxF measured-material import. Neither is needed here.
- Convert a legacy material manually: right-click the root node > *Convert to Substrate*. This creates a Slab wired into Front Material.

## PBR value guardrails (linear values; check in Buffer Visualization)

| Quantity | Range | Trap |
|---|---|---|
| Dielectric albedo | ~0.02 (charcoal) … ~0.8 (fresh snow); most materials 0.05-0.6 | Albedo > 0.8 or pure-saturated colours make Lumen bounce explode |
| Metal base colour | 0.5-1.0 (chromium ~0.55, aluminium ~0.91, gold 1.0/0.77/0.34, copper 0.96/0.64/0.54) | Dark "metal" (< 0.4) looks like plastic |
| Specular (legacy input) | 0.5 (= 4 % F0) | Don't use it to fake glossiness; use roughness |
| Roughness | > ~0.02 floor for anything visible in motion | 0.0 produces sparkling aliasing and noisy Lumen reflections |
| Metallic | 0 or 1 (blend only at transitions) | 0.5 everywhere = wrong energy |

## Recipes

**Billiard ball (phenolic resin, 57.15 mm)**
- Model:
  - Substrate: Slab (base colour, roughness 0.15-0.3) under a clear coat. Use the *Substrate Simple Clear Coat* node, or Vertical Layer with a thin coat slab.
  - Legacy alternative: Clear Coat shading model (Clear Coat 1.0, Clear Coat Roughness 0.02-0.06).
- Coat roughness variation is what sells realism: a subtle smudge/micro-scratch mask, 0.02 → 0.1. Add chalk transfer on the cue ball (light blue, rough, low opacity).
- Albedo:
  - White cue ball ≤ ~0.8. A 1.0 white blows out under 500+ lux at physical exposure.
  - Black 8-ball ~0.02-0.04; the highlights carry it.
- Texture: 2K is ample (circumference ~18 cm, so ~110 px/cm). Use a cube-sphere UV or triplanar numbers to avoid pole pinching. Numbers are part of the albedo, not a separate decal mesh.
- Highlights come from light source size (Source Radius/Rect), not the material. See SKILL.md.

**Table cloth (worsted wool felt)**
- Substrate Slab: roughness 0.8-1.0, Fuzz Amount 0.3-0.8, Fuzz Color slightly lighter/desaturated than base, Fuzz Roughness 0.5-0.8.
- Legacy alternative: Cloth shading model (Fuzz Color + Cloth 1).
- Albedo: dark-mid green/blue, max channel ~0.1-0.25. Tournament cloth is not neon. Bright felt plus Lumen tints players and walls.
- Detail: tiling weave normal map (fine) plus a large-scale macro variation mask (wear paths, slight brightness drift, chalk dust near pockets). This kills visible tiling in wide shots.
- Don't use Nanite Tessellation for weave (experimental; 5.8 displacement regressions reported).

**Rails and cabinet (lacquered wood)**
- Base wood albedo 0.05-0.35 (dark stains low), base roughness 0.4-0.6, under a coat of roughness 0.05-0.15 (gloss lacquer) or 0.2-0.3 (satin).
- Anisotropy needs `r.AnisotropicMaterials=1` (on at ShadingQuality High+). Optional for brushed metal, rarely needed for wood.

**Fittings (chrome corner caps, brass lamp hardware)**
- Metallic 1, roughness 0.05-0.2, base colour from the metal list.
- Add fingerprint/smudge roughness variation, or they look like CG chrome.

**Leather pockets, cue grip, bar stools**
- Roughness 0.4-0.7, albedo low.
- Substrate fuzz small, or none.

**Chalk cube**
- Rough (0.9), albedo ~0.3-0.5 blue.
- Rough-diffuse response: `r.Material.RoughDiffuse` / `r.Substrate.RoughDiffuse` (both in 5.8 logs; project-level).

**Glassware/bottles**
- Translucent. Keep the count small near the camera (translucency cost, no Nanite).
- Enable front-layer translucency reflections for crisp glass (see lumen reference).
- Refraction through glass in reflections needs Max Refraction Bounces ≥ 1.

## Specular aliasing on glossy curved surfaces

- Ball silhouettes and lacquered rail edges shimmer under TSR in motion. Fixes, in order:
  1. Roughness floor ~0.02-0.03 on the coat.
  2. Enable *Composite Texture* on roughness maps, using the normal map to add normal variance to roughness.
  3. `r.TSR.ShadingRejection.Flickering=1` (default at AA quality High+).
  4. Higher internal resolution for hero shots.

## Texel density (convention, not engine rule)

| Asset class | Target | Why |
|---|---|---|
| Table bed, rails, balls (hero close-ups) | ≥ 10.24 px/cm (1024 px/m), more for macro shots | Camera sits 0.3-1 m from them |
| Characters' hands/cue | ≥ 10 px/cm | In frame during shots |
| Room props, bar | ~5 px/cm | Mid distance |
| Walls/ceiling/floor | 2.5-5 px/cm + detail tiling | Mostly dark, out of focus |

- Check with *Optimization Viewmodes > Texture Streaming Accuracy* (Mesh UV Densities, Material Texture Scales, Required Texture Resolution).
- Higher density than the screen can show only costs memory. Streaming drops the mips anyway.

## Virtual textures

- Streaming Virtual Textures (SVT): enable `r.VirtualTextures=1`, then convert large unique textures (4K-8K wood panels, wall murals) to VT.
  - Pays off with many large textures. Adds a VT feedback pass and VT sampling cost.
  - Keep small and tiling textures (felt weave, ball atlases) as regular streamed textures.
- Runtime Virtual Textures are a landscape/decal-blending tool, not useful in this interior.
- VT anisotropy follows `r.VT.MaxAnisotropy` (TextureQuality tiers: 4/4/8/8).
