# Fabric and leather materials (Blender → GTA / UE)

Contents: Principled names per version · presets (`SF.FABRICS`) · velvet, cotton, linen, wool/bouclé, leather ·
micro detail · wear and variation · CC0 textures and licenses · GTA shader mapping · UE mapping.
Garment-side texturing (Substance layering, texel density maths, UE Substrate fuzz): `clothing-creation-pipeline`
→ `references/materials-realism.md`. Do not duplicate it here.

## 1. Principled BSDF inputs (read from bpy) [T]

| Input | 4.5.14 default | 5.2.2 default | Notes |
|---|---|---|---|
| `Sheen Weight` / `Sheen Roughness` / `Sheen Tint` | 0 / 0.5 / white | same | Since 4.0 (was `Sheen`, `Sheen Tint` float ≤ 3.6). 4.0: new microfiber sheen model, top layer above coat/emission [W, 4.0 release notes] |
| `Diffuse Roughness` | 0 | 0 | Present in 4.5 and 5.2 (not checked on 4.2); 0.5 for matte fibres |
| `Specular IOR Level` | 0.5 | 0.5 | was `Specular`; fabrics 0.3–0.4 |
| `Subsurface Scale` | **0.05** | **0.005** | Default changed between 4.5 and 5.2; set it explicitly if you use SSS on foam/felt |
| `Thin Wall` | — | False | 5.2 only; for sheer curtains (verify look) |
| `Coat Weight` / `Coat Roughness` | 0 / 0.03 | same | finished leather 0.1–0.2 / 0.3 |

Never `nodes["Principled BSDF"]` (localized names) — find by `bl_idname == "ShaderNodeBsdfPrincipled"`;
`mat.use_nodes = True` only below 5.0 (`blender-python-pitfalls` §6).

## 2. Presets (`SF.fabric_material(name, kind, color, coords="Object")`) [T: builds on 4.5.14 and 5.2.2]

| Kind | Roughness | Sheen W / R | Spec | Bump source (thread / scale) | Bump strength | Value variation |
|---|---|---|---|---|---|---|
| velvet | 0.90 | 1.0 / 0.30 | 0.3 | none (pile is the sheen) | 0 | ±4 % |
| cotton | 0.85 | 0.3 / 0.5 | 0.4 | 2 Wave textures, 3 mm | 0.15 | ±3 % |
| linen | 0.80 | 0.2 / 0.5 | 0.4 | 2 Wave textures, 4 mm | 0.25 | ±6 % (slubs) |
| wool / bouclé | 0.95 | 0.6 / 0.6 | 0.3 | 2 Wave textures, 6 mm (bouclé: Voronoi F1 bump instead) | 0.20 | ±5 % |
| leather | 0.45 | 0 / – | 0.5 | Voronoi Distance-to-Edge, scale 250 (≈ 4 mm cells) | 0.15 | ±5 % |

- Sheen Tint = dye colour lerped 40 % toward white (velvet highlights are lighter, same hue).
- Wave BANDS period = 2π / (20 · Scale) in the input coordinate units [S, Cycles `svm/wave.h`: `n = p.x * 20`]; for a
  thread period t in metres: Scale = 0.314 / t with Object coordinates (applied scale required).
- Bump node: Distance 0.001, Strength 0.1–0.25 (fabric; matches `scenario-blender-texturing-shading` notes).
- Object coordinates keep the weave physically sized and still bake onto any UV layout; use UV only when the UVs
  have a known texel density (stripes/plaids must follow the UVs → straightened UV islands).
- Rendered check (Cycles, 3 KNIFE pillows): velvet shows the grazing-angle sheen, linen the weave, leather the
  glossy grain [T, visual].

## 3. Per fabric notes

- **Velvet**: base colour dark and saturated (max channel 0.05–0.3 linear); all the "velvet" comes from Sheen 1.0
  at grazing angles. Crushed velvet: drive Sheen Weight 0.6–1.0 and a weak normal with a stretched Noise.
  Without Sheen it reads as felt or plastic.
- **Cotton/canvas**: visible weave only within ~1 m; beyond that rely on roughness variation.
- **Linen**: irregular slubs — Noise stretched along one axis (Mapping scale 1:10) multiplied into the bump and
  the value; slightly lighter at creases.
- **Wool/bouclé**: very rough, strong sheen; bouclé loops = Voronoi F1 bump at 3–5 mm or real geometry for hero.
- **Leather**: roughness 0.35–0.5 with a roughness map (worn areas glossier 0.25–0.3), grain bump, creases as
  geometry/normal at seat fronts and arm tops, Coat 0.1–0.2 for finished/aniline-dyed, Sheen 0.

## 4. Micro detail, wear, variation (what removes the CG look)

| Scale | Carrier |
|---|---|
| Folds 2–20 cm | Geometry (sim/sculpt) |
| Wrinkles 3–20 mm | Baked normal from the high/sculpt |
| Weave, grain 1–5 mm | Tiled detail normal (GTA `normal_spec_detail` DetailSampler / UE detail texture) |
| Colour | ±3–6 % value noise, fade on sun-facing tops, darker dirt in creases (AO-masked), lighter seat fronts |
| Roughness | per-panel ±0.05, worn areas glossier (leather) or fuzzier (fabric pilling) |

## 5. CC0 sources and licenses

| Source | License | Use |
|---|---|---|
| Poly Haven (polyhaven.com) textures/models | CC0 [W, quoted on a mirror; site blocked here] | fabric/leather PBR sets, sofa/pillow models as reference or base |
| ambientCG (ambientcg.com) | CC0 [W] | Fabric, Leather categories |
| Fab (fab.com) | Standard License: commercial use and modification allowed, no standalone redistribution; Personal tier < 100 k USD revenue / 12 months; NoAI tag only on Standard-licensed assets [W, Epic docs summary] | check each listing; CC-BY assets need attribution |
| Sketchfab free | per model (often CC-BY) | attribution in your credits |

Packaging a texture inside a FiveM resource or a UE game is not "standalone redistribution"; reselling the raw
files is. Keep a license log per asset (`clothing-creation-pipeline` does the same for garments).

## 6. GTA V (Sollumz) mapping

- Principled materials do not export; convert (Sollumz *Convert to Shader Material*): with a normal **and** a
  specular image node it picks `normal_spec.sps`, normal only → `normal.sps`, spec only → `spec.sps`, else
  `default.sps` [S, Sollumz `ydr/operators/materials.py`].
- `normal_spec` samplers: Diffuse, Bump, Spec; defaults `bumpiness` 1, `specularIntensityMult` 1,
  `specularFalloffMult` 100, `specularFresnel` 0.75, `specMapIntMask` (1,0,0) [S, szio 1.4.0.dev1 `Shaders.xml`].
  Fabric: dark spec R (0.05–0.15), low gloss (spec alpha × falloff); leather: spec R 0.2–0.35, higher alpha.
- `normal_spec_detail` adds `DetailSampler` + `detailSettings` (default 1.35, 0, 7.5, 8) [S]. In CodeWalker's
  decompiled shader the detail normal is sampled at UV × `detailSettings.zw` (and × 3.17 again), scaled by
  `detailSettings.y`, and masked by the spec map alpha [S, CodeWalker `BasicPS.hlsl`]. So: weave tiling = z, w;
  set **y > 0** (default 0 = no detail, verify in game); spec alpha also gates the detail.
- `*_tnt` variants (`normal_spec_tnt`, `normal_spec_detail_tnt`) for colour variants of one sofa via a palette
  (column = vertex colour0 blue, row = entity `tintValue`; `gta-texture-editing`).
- `cloth_*` shaders (`cloth_default`, `cloth_normal_spec`, …) carry `IS_CLOTH` — simulated env cloth only [S].
- Textures: power of two DDS, BC1 (opaque) / BC3 (spec with alpha); 512–1024 per prop, share one fabric detail map
  across all soft props of an MLO; commands in `gta-texture-editing`.

## 7. Unreal Engine 5.8 mapping

- Bake: Base Color, Normal (DirectX, green down), ORM (AO, Roughness, Metallic 0), optional Sheen/Fuzz mask.
- Substrate Slab fuzz for velvet/wool/cotton (FuzzAmount 0.3–1.0, FuzzColor ≈ Sheen Tint), 0 for leather —
  values and pitfalls in `clothing-creation-pipeline` (materials-realism §6) and `ue5-lighting-rendering`.
- Detail normal tiled via a second texture coordinate (10–30 tiles/m) masked by distance.
