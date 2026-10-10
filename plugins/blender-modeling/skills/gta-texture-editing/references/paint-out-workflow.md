# Painting out doors/windows, the UV and patch alternatives, recolouring

Read when removing a painted-on door/window/sign from a facade, choosing between texture edit, UV
remap and patch plane, or recolouring. Tags as in SKILL.md.

## 1. Find exactly what draws the door

1. CodeWalker World view: click the building and note the entity's archetype, its `.ydr`, its `.ytyp`
   (`textureDictionary` field), and its `parentIndex`, which points to the LOD entity (often in a separate
   LOD/SLOD ymap).
2. Open the `.ydr` (RPF Explorer → double-click). Use **Material Editor** to list each geometry's shader name
   and sampler texture names (`DiffuseSampler`, `BumpSampler`, `SpecSampler`, …). "(embedded)" after
   a name means the texture is inside the drawable; otherwise it is resolved by name. [Src: ModelMatForm]
3. Resolution order for a non-embedded name: the archetype's `textureDictionary`, then its parent chain from
   `gtxd.ymt`/`gtxd.meta` (`CMapParentTxds`), then resident dictionaries such as `mapdetail`. [Src: CodeWalker
   GameFileCache/Renderer] If the texture lives in a **parent** txd, many buildings use it.
4. Check for an HD dictionary. `_manifest.ymf` `HDTxdAssetBindings` maps a txd to an HD txd (`+hi`).
   Embedded textures can have `+hidr/+hifr/+hidd` dictionaries. Tick "HD textures" in the CodeWalker model
   viewer and check that the door is in the HD copy too. [Src]
5. Find **every** representation of the door:
   - the HD drawable (diffuse, `_n`, `_s`);
   - the night/emissive geometry: materials whose shader is `emissivenight`, `emissivenight_geomnightonly`,
     `glass_emissivenight`, `decal_emissivenight_only` or `normal_spec_reflect_emissivenight` (the list comes from
     Sollumz/szio `Shaders.xml`) [Src];
   - the LOD and SLOD drawables (other archetypes and other txds; LOD txds are often shared by a whole
     block (verify)).
6. Decide whether the texture is **tiling** (UVs repeat, brick/plaster/panel pattern) or a **unique atlas**
   (a whole facade baked into one sheet with lighting and dirt). It decides the method.

## 2. Pick the method

| Situation | Best method | Why |
|---|---|---|
| Door is its own faces (frame geometry), and a plain wall area exists in the same texture | **UV remap** (§4) | No new texture, no extra memory, survives texture updates |
| Door is painted onto a large wall quad | Knife-cut the quad around the door, then **UV remap** | Same, after cutting |
| You must not replace the vanilla building model (vanilla exterior stays) | **Patch plane** (§5) | Leaves vanilla untouched; your MLO resource adds a small prop |
| Unique atlas with baked AO and dirt and no clean matching region | **Texture edit** (§3) | Only option that keeps the lighting continuous |
| Window glows at night | Delete the emissive faces in your copy, **or** black out the night texture | Diffuse edits do not remove emission |
| LOD/SLOD still shows the door | Remap or edit the LOD copy, or accept it if it is only a few pixels at that distance | LOD uses different models and textures |

Replacing the vanilla exterior with your own copy (map/ymap work) belongs to `fivem-mlo-creation`.
Making the new door functional belongs to `fivem-mlo-doors-windows`.

## 3. Texture edit: clean retouch

Setup:
- Export the textures as DDS (CodeWalker "Save all textures…"), then convert them to PNG at **full resolution**
  (`texconv -ft png -m 1`). Never edit a downscaled mip or a screenshot.
- Rename the copies at once: `<prefix>_<what>_d/_n/_s/_night` (lower case, ASCII). Keep the vanilla files
  untouched in a `vanilla/` folder.
- Use one layered work file per map, and the **same selection/mask and the same clone offsets** for diffuse,
  `_n`, `_s` and night. `paint_out.py` in automation.md does this automatically.

Tiling texture (bricks, panels, siding):
- Measure the repeat period in pixels (brick width and height, panel spacing). Clone or offset by **integer
  multiples of the period** in x and y, so mortar lines and panel seams continue. In the synthetic test,
  clone by one period gave an error of 7 (equal to the noise) versus 21 for Telea inpaint.
- Use GIMP Layer → Transform → Offset (wrap around, by half the size) to bring the texture edges into the middle.
  Check that the edit does not create a visible seam where the texture repeats.

Unique facade atlas:
- Clone first, then fix the low-frequency light. Use frequency separation: put a heavy Gaussian blur of the
  surroundings as the "low" layer and keep the cloned "high" detail. Baked AO, dirt streaks and the gradient
  under balconies must continue through the patch.
- Grow the mask 2–4 px past the door, so frame shadows and AO rims are covered.
- Repeating dirt from cloning is the giveaway. Clone from 2–3 different sources and break up repeats with a
  soft brush.

Per map:

| Map | What to do | Check |
|---|---|---|
| Diffuse | Clone/heal as above; keep alpha unchanged unless the alpha has a door shape | Compare with the original at 25% zoom (mip view) |
| Normal `_n` | **Same clone offset as diffuse.** For smooth plaster, fill flat `R=128,G=128` (B is ignored; Z is rebuilt from R,G) [Src: CodeWalker decompiled shader] | No leftover door-panel bevels; no non-unit vectors (renormalise R,G) |
| Specular `_s` | Paint **R** (intensity, default `specMapIntMask = 1,0,0`) and **A** (gloss × `specularFalloffMult`) to the wall's values [Src] | Glass and metal of the door no longer shine |
| Night / emissive | Fill the masked area black (assumed to be no emission (verify)), or delete the emissive faces | Test at 22:00 game time |
| Detail (`DetailSampler`) | Do not touch. It is a global tiling detail from `mapdetail` | — |
| LOD/SLOD textures | Same edit on the small texture; usually a simple colour fill is enough | View from 150–500 m |

Seams and mips:
- If the edit touches a **UV island border** in an atlas, extend (dilate) the fill 4–8 px beyond the island.
  Lower mips average neighbouring pixels, so an unpadded edge shows a coloured seam at a distance.
- Never resize or crop the canvas. UVs are normalised, so a different aspect ratio shifts everything.

AI options (all as a first pass; then hand-retouch): `cv2.inpaint` for small or noisy areas; LaMa
(IOPaint `iopaint start --model=lama --device=cpu --port=8080`) for irregular areas; SD inpainting or Photoshop
Generative Fill for unique facades. All of them blur or invent regular patterns, so clone those. Run them on
the diffuse only; apply clone/flat fills to `_n`/`_s` with the same mask. Licences: formats-and-tools.md.

## 4. UV remap instead of editing (Blender + Sollumz)

1. Import your **copy** of the building `.ydr` (Sollumz). Sollumz flips V: Blender `v = 1 - v_game`. [Src]
2. Edit Mode → select the door faces (knife-cut first with `K` if the door is part of a larger face).
3. UV Editor: move the island onto a plain wall region of the **same** texture. Keep the texel density: scale
   the island so it covers the same pixels per metre as the neighbouring wall faces. For tiling textures,
   offsets by whole UV units are free (the sampler wraps).
4. Copy the neighbours' **vertex colours** to the remapped faces. Colour0 R/G scale ambient light (baked
   AO) [Src: CodeWalker decompiled shader]. Door faces often carry darker AO, so the patch would look dirty.
5. The `_n` and `_s` maps follow automatically (same UVs). Do the same on the LOD copy if it is visible.
6. Export Gen8 and Gen9 (Sollumz 2.8.0+) or export Gen8 and convert with Alchemist. See repack-and-stream.md.

## 5. Patch plane (vanilla building untouched)

- Add a thin plane 1–2 cm in front of the facade in your MLO ymap/ytyp, covering the painted door.
  Texture it with a crop of the wall copied into **your** small YTD (or embedded). Choose a power-of-two
  crop.
- Shader: `normal_spec` (opaque) or a decal variant (`normal_spec_decal`, `decal`) when you need soft alpha
  edges. Decal alpha is multiplied by vertex colour0 alpha [Src: CodeWalker shader]. No collision.
- Problems: Z-fighting if closer than about 1 cm; shadows and specular may differ from the wall;
  the vanilla LOD still shows the door at distance; night windows of the vanilla model still glow (cover them,
  or hide the vanilla model as in `fivem-mlo-creation`).

## 6. Recolouring

| Want | Do | Avoid |
|---|---|---|
| Different paint colour on a `_tnt` shader | Set the entity's `tintValue` in the ymap (palette **row**), or edit the `TintPaletteSampler` palette. The column comes from vertex colour0 **blue** (colour1 for `trees_*_tnt`) [Src: Sollumz tint preview] | Editing the diffuse of a tinted material, since it is multiplied by the palette |
| Recolour a normal diffuse | Hue/Saturation or Curves on a **16-bit sRGB** copy, then 8-bit with dithering; texconv `-bc d` or BC7 for smooth gradients | 8-bit HSL on gradients (banding), "convert to linear", recolouring `_n`/`_s` |
| Darken or lighten areas | Diffuse curves, or vertex colour0 R/G (ambient) in your model copy | Clipping to pure black or white; changing contrast of `_n` |
| Same colour everywhere | Change one shared texture copy that all your parts reference | Overriding vanilla names |

After recolouring, check in game under day, night and rain (wetness darkens), because the in-game tone
mapping differs from Photoshop.
