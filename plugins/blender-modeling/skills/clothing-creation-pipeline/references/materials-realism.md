# Photorealistic fabric: geometry, textures, materials

Contents: reference · texel density · UDIM vs atlas · bakes from MD/high-poly · material layering · fuzz/sheen in UE · seams and stitches · asymmetry · per-fabric starting values · fake-vs-real checklist.

Material node setup and project-wide Substrate decisions: `ue5-lighting-rendering` (felt example values live there). This file is about *authoring* the garment so those materials have something to show.

---

## 1. Reference first

- 3+ photos per garment type: full front/back/side, seams at 20 cm, fabric at 5–10 cm with a ruler. Note fabric weight (a 120 g/m² shirt drapes differently from 400 g/m² wool), construction (yoke, darts, plackets, cuffs, hems), where it creases when the wearer bends.
- Shoot your own fabric swatches flat under diffuse light for Sampler/photogrammetry textures. A scan beats any procedural weave for close-ups.

---

## 2. Texel density

- 1 px/cm = 100 px/m. Guidance from current density guides: third-person 512–1024 px/m (5–10 px/cm), first-person/close-up 1024–2048 px/m (10–20 px/cm), cinematic 2048–4096 px/m.
- A 4K map over a 2 m × 2 m UV space ≈ 20 px/cm. A shirt (≈1.2 m² of surface) on one 4K tile reaches ~15–18 px/cm with good packing.
- Targets for this project: player/opponent garments **10–20 px/cm** (camera gets within 50 cm at the table); named NPCs 8–10; background NPCs ~5. Keep the garment within ±25 % of the body/skin density, or the seam between skin and sleeve reads wrong.
- Measure in Blender (Texel Density Checker add-on or `bpy` area math) or Substance Painter's texel density display before baking.

---

## 3. UDIM vs single UV set

| | Use | Notes |
|---|---|---|
| **UDIM** (1001 shirt front/back, 1002 sleeves+collar, 1003 trousers, ...) | Hero outfits, Substance painting | UE imports UDIMs as Virtual Textures (enable *Virtual Texture Support*); each tile is a VT. MD can lay patterns on the UDIM grid before export |
| **Single atlas** (one 2K/4K per garment) | NPCs, Fab-style modular pieces | Simplest for Leader Pose/merge; one material = one draw call |
| **Tiled detail + unique mask** | Both | Unique 2K for wear/AO/ID + a tiled 1K weave normal/roughness at 10–30 tiles/m. Gives micro detail at any distance without 8K maps |

Straighten UV islands where the weave direction matters (stripes, denim twill); MD's UV editor keeps pattern grain, Blender *Follow Active Quads* or *UV Squares* add-on for rectangles.

---

## 4. Bakes from MD / high-poly

- MD triangles are too fine for direct use but perfect as a **bake source**: export *Thick* (or the welded thin sim mesh) at 5 mm particle distance as the high mesh; bake to the retopo'd game mesh.
- Bake set: normal (**DirectX, green down** for UE), ambient occlusion, curvature, thickness, position/world normal, ID per pattern panel (MD can export pattern colors as ID). Bake at 2× the target resolution and downsample.
- Normal map sanity: folds must be visible in the *geometry* at silhouette scale; the normal map carries medium folds (1–3 cm) and seams; a tiled detail normal carries the weave. A strong baked normal on a flat mesh is the classic "painted-on folds" look.
- Cage/distance: set max ray distance to the garment thickness + 5 mm, or sleeves bake the torso.

---

## 5. Material layering (Substance Painter or UE material layers)

Bottom to top:
1. **Base fabric**: tiled weave albedo + normal + roughness (Assets library, Sampler scan, Designer). Albedo of dyed cotton/wool: max channel ≈ 0.1–0.45 linear; black fabric never 0.
2. **Colour variation**: subtle per-panel hue/value noise ±3 %, sun/wash fade on shoulders.
3. **Seams and stitching**: seam height/normal + thread stamp along pattern borders (Painter *Stitches* alpha on a path); seam AO.
4. **Wear**: roughness lowered on edges that rub (cuffs, collar fold, pocket mouths, elbows) using curvature + AO masks; pilling on knits; shine on worn wool (waistcoat back, trouser seat) = roughness 0.35–0.5 islands.
5. **Dirt/dust**: in crease AO and at hems; chalk dust on the cue hand's cuff for a billiards player.
6. **Fuzz/sheen mask**: strong on wool/felt/velvet/cotton, weak on silk/satin/leather; store as a grayscale channel.
7. **Opacity/thickness**: for lace, mesh, thin cotton edges (Substrate thin-film/translucency or masked).

Export: Base Color, Normal (DirectX), ORM (R=AO G=Roughness B=Metallic, metallic 0 except buttons/buckles), Fuzz mask, optional Opacity, optional Height (for POM on heavy knits only).

---

## 6. Fuzz and sheen in UE 5.8

- Substrate **Slab** inputs: `FuzzAmount` (how much fuzz layer on top), `FuzzColor` (tint; usually a lighter version of the base), `FuzzRoughness`. Cotton 0.3–0.6, wool/felt 0.5–0.8, velvet 0.8–1.0, silk 0.05–0.15, leather 0. Scale by your fuzz mask.
- Legacy pipeline: *Cloth* shading model with Fuzz Color + Cloth amount.
- Fuzz brightens grazing angles: with lights behind the opponent (pool-hall lamps), too much fuzz halos the whole silhouette. Check it against the table lamp setup, not in the material preview.
- Two-sided fabric: enable two-sided and feed a flipped normal for backfaces, or add inner-surface geometry for open jackets.

---

## 7. Seams, stitches, hems: geometry or texture?

| Element | Hero (camera < 1 m) | NPC |
|---|---|---|
| Seam ridge | Geometry (1 extra loop, 1–2 mm raise) + normal | Normal only |
| Topstitch | Geometry strip or alpha-card for pockets/plackets; normal elsewhere | Normal |
| Hem/collar/cuff thickness | Solidify 2–4 mm on the edge loops only, rim faces kept | Solidify 2 mm or double-sided material |
| Buttons/buckles/zips | Separate low-poly meshes, metal material, their own LOD | Baked into normal + albedo |
| Fraying/rips (MD 2026.1 Seamline Rip) | Only for a worn NPC look; export as geometry + opacity | Skip |

---

## 8. Asymmetry and story

Mirror the block-out, then break it: slightly different fold set on each sleeve, collar sits 2–3 mm lower on one side, one cuff rolled, waistcoat pulled by the bridge arm, chalk on the cue hand side, worn seat on a bar-fly NPC. Symmetric folds are the single biggest giveaway after flat roughness.

---

## 9. Per-fabric starting values (UE, linear albedo, Substrate roughness)

| Fabric | Albedo max channel | Roughness | Fuzz | Notes |
|---|---|---|---|---|
| Cotton shirt | 0.3–0.8 (white 0.75–0.8) | 0.65–0.85 | 0.3–0.5 | Visible weave normal 15–25 tiles/m |
| Worsted wool (waistcoat/trousers) | 0.03–0.25 | 0.7–0.9 (worn 0.4) | 0.5–0.8 | Tiny twill normal; sheen on worn spots |
| Felt (table) | see `ue5-lighting-rendering` | 0.8–1.0 | 0.3–0.8 | |
| Denim | 0.05–0.3 | 0.75–0.9 | 0.3–0.5 | Twill at 45°; wear on seams |
| Silk/satin | 0.1–0.6 | 0.2–0.4 | 0.05–0.15 | Anisotropy if available |
| Leather (shoes, belt) | 0.02–0.2 | 0.3–0.5 (polished 0.15) | 0 | Clear coat on patent |
| Knit (sweater) | 0.05–0.5 | 0.85–1.0 | 0.6–0.9 | Needs geometry/height for the knit; fuzz hides a flat mesh |

Values are starting points from practice, not measured data; grade them against reference photos in the actual pool-hall lighting.

---

## 10. Fake vs real checklist

- [ ] Silhouette: thickness on every visible edge, no razor hems.
- [ ] Folds at three scales (geometry, baked normal, tiled weave).
- [ ] Roughness varies across the garment and per panel.
- [ ] Fuzz on fibrous fabrics; none on leather/metal.
- [ ] Seams raised and stitched where the camera can see them.
- [ ] Wear/dirt only where physics would put it (contact points, creases, hems).
- [ ] Asymmetry present; mirrored UVs not used on hero garments (mirrored dirt is obvious).
- [ ] Skin-to-cloth contact: AO in collars/cuffs, no floating gap, no z-fighting.
- [ ] Texel density consistent with the face/hands.
- [ ] Checked under the table lamp + ambient, from the gameplay camera, at LOD0 and LOD1.
