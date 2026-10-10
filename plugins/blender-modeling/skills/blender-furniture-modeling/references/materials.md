# Furniture materials: Principled values, textures, GTA shaders, Unreal

Read when assigning materials or textures. Tags: [V] verified headless (bpy 5.2.2 and 4.5.14), [D] read in source,
[S] search snippet, [N] practice (verify).

## 1. Principled BSDF values (Blender 4.0+ socket names) [N values, V names]

| Material | Base colour (linear) | Roughness | Metallic | Coat Weight / other | Notes |
|---|---|---|---|---|---|
| Oiled/matte wood | wood texture, never > 0.8 | 0.45–0.65 | 0 | 0 | grain along the part (see construction.md §4) |
| Lacquered wood | wood texture | 0.35–0.5 base | 0 | Coat 0.3–1.0, Coat Roughness 0.03–0.1 | the coat gives the sharp highlight |
| Painted/lacquered MDF | flat colour 0.05–0.85 | 0.2–0.35 gloss, 0.4–0.6 satin | 0 | – | |
| Melamine / laminate | texture or flat | 0.35–0.55 | 0 | – | slight normal texture |
| Brushed steel / aluminium | 0.55–0.75 grey | 0.25–0.4 | 1 | Anisotropic 0.3–0.7 (render only) | |
| Chrome | 0.8–0.95 | 0.02–0.1 | 1 | – | needs reflections to read |
| Powder-coated / painted metal | colour | 0.4–0.6 | **0** | – | paint is a dielectric: metallic 1 makes it look like bare metal |
| Brass | (0.9, 0.7, 0.35) | 0.2–0.4 | 1 | – | |
| Glass | (0.85–0.95) slight green | 0–0.05 | 0 | Transmission Weight 1, IOR 1.52 | model real thickness; edges look green through it |
| Polished marble / stone | texture | 0.05–0.2 (honed 0.4–0.6) | 0 | – | |
| Leather, fabric, felt | → `blender-soft-furniture` (billiard felt: roughness ~0.9, Sheen) | | | | |

Socket names that old memory gets wrong (checked on 5.2.2: `Base Color, Metallic, Roughness, IOR, Alpha, Thin Wall,
Normal, Weight, Diffuse Roughness, Subsurface Weight/Radius/Scale/IOR/Anisotropy, Specular IOR Level, Specular Tint,
Anisotropic, Anisotropic Rotation, Tangent, Transmission Weight, Coat Weight/Roughness/IOR/Tint/Normal, Sheen
Weight/Roughness/Tint, Emission Color, Emission Strength, Thin Film Thickness, Thin Film IOR`) [V]:
`Clearcoat` → `Coat Weight`, `Specular` → `Specular IOR Level`, `Transmission` → `Transmission Weight`,
`Emission` → `Emission Color`. `mat.use_nodes = True` only below 5.0 (`blender-python-pitfalls`).

## 2. Textures

| Source | Licence | Use |
|---|---|---|
| Poly Haven (polyhaven.com) | CC0, commercial use, no attribution required (FAQ) [S] | wood, metal, marble, fabric sets with roughness/normal/AO |
| ambientCG (ambientcg.com) | CC0 / public domain per third-party guides [S]; check the asset page | large PBR library |
| FreePBR | personal use free, commercial paid [S] | avoid for a server/game |

- Texel density: pick one value per project and keep it. 512 px/m is a common prop baseline; 1024 px/m for furniture
  the player sees up close in first person [S, forum practice]. With the generators' world-scale UVs,
  `meters_per_uv = texture_px / density` (2048 px at 1024 px/m → `meters_per_uv=2.0`) [V: UV span = size / meters_per_uv].
- GTA: textures power of two, ≤ 2048 (1024 typical for props), DDS with mipmaps, keep every YTD well under 16 MiB
  (`gta-texture-editing`, `fivem-mlo-creation`).
- Colour textures sRGB; roughness/normal/metal/AO Non-Color.
- Tiling wood on big tops is fine; avoid visible repeats by using a 2 × 1 m texture or a detail map
  (`normal_spec_detail` in GTA).

## 3. GTA V / Sollumz shader mapping

Shader names and texture slots read in Sollumz/szio `Shaders.xml` (2026-10-10) [D]:

| Furniture surface | Shader | Slots |
|---|---|---|
| Wood, laminate, lacquer, painted parts, fabric | `normal_spec` | DiffuseSampler, BumpSampler, SpecSampler |
| Same with a tiling detail grain | `normal_spec_detail` | + DetailSampler |
| Colour variants of one prop (tint palette) | `normal_spec_tnt` | + TintPaletteSampler (palette row per entity tint, verify) |
| Polished stone, chrome, glossy lacquer with reflections | `normal_spec_reflect` / `spec_reflect` | + EnvironmentSampler |
| Stickers, labels, worn spots on top of a surface | `normal_spec_decal` / `decal` | alpha; offset ≥ 1–2 mm from the base face |
| Glass doors, glass tops, vitrines | `glass` family (see `fivem-mlo-doors-windows` §7) | separate geometry/entity, alpha bucket |
| Mirror | `mirror_default` | needs vanilla-style setup (verify) |
| Lamp shade glow, bulbs | `emissive`, `emissivenight` | |
| Diffuse only, no normal | `default` | |

- GTA spec maps are not roughness: `SpecSampler` intensity = dot(RGB, `specMapIntMask`) (default R) and A ×
  `specularFalloffMult` = gloss (`gta-texture-editing` [D]). Rough conversion: R ≈ specular amount
  (0.1–0.3 wood, 0.5–1 metal), A ≈ 1 − roughness (verify visually in game).
- Generators name slots `sz_<shader>.<kind>` (`sz_normal_spec.wood`, `sz_glass.glass`), the same convention as the
  doors skill, so `sz_apply_shaders()` from `fivem-mlo-doors-windows` converts them (not executed: Sollumz cannot load
  in the bpy wheel).
- Sollumz exports the **evaluated** mesh (modifiers applied, bmesh-triangulated) and reads face-corner normals, so the
  Bevel/Weighted Normal custom normals reach the `.ydr` with the default Mesh Domain "Face Corner"; "Vertex" averages
  them [D: `ydr/ydrexport.py` `create_model`, `vertex_buffer_builder.py`, commit 07d6a49]. Not tested in game.
- Gen9 (Enhanced): ≤ 128 materials/geometries per drawable (`fivem-mlo-creation`). One furniture prop should use 1–4.

## 4. Unreal Engine 5.8

- One master material with instances per wood/metal/stone; pack ORM (AO, Roughness, Metallic) into one texture.
- FBX keeps only a simple material description: rebuild materials in UE (`blender-game-export`).
- Nanite: fine for opaque furniture, even with real bevel geometry. Translucent glass is not drawn by Nanite (falls
  back) [S]: keep glass parts in a separate non-Nanite static mesh. Masked materials: supported with extra cost in
  recent versions (verify for 5.8).
- Import normals (Normal Import Method: Import Normals and Tangents) so the Weighted Normal result survives.
- Lumen/reflections: glossy lacquer and chrome need roughness ≥ ~0.05 to avoid noisy reflections (N).
