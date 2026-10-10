# Symptom → cause → fix (garment creation and fitting, DCC side)

Work top to bottom inside each group. In-UE symptoms after import (Leader Pose, LODSync, Chaos Cloth jitter, grooms) are in `ue5-character-creation-clothing/references/common-issues.md`.

## Marvelous Designer / CLO

| Symptom | Likely cause | Fix |
|---|---|---|
| Garment explodes, flies away or vibrates on *Simulate* | Patterns overlap at arrangement; particle distance too small for the first drape; wrong *Layer* order; avatar self-intersecting (hands in pockets pose); sewing crossed | Reset 2D arrangement, place with arrangement points, particle distance 20 mm for the first drape then 5–10 mm, fix layers inner→outer, check sewing lines for crossing (red), pause and *Reset* the garment |
| Cloth sinks into the avatar | *Skin Offset* 0 or collision off; particle distance larger than the gap | Skin Offset 2–3 mm; smaller particle distance; *Simulate (Complete)* for the final |
| Clothes float visibly above the skin | Skin Offset too high; fabric *Thickness - Collision* too high | Skin Offset 2–3 mm, collision thickness ≤ 2.5 mm |
| Avatar imports tiny or huge | FBX import unit mm vs cm | Re-import with unit cm; check height in the measure tool |
| "No matching avatar" when applying `Apose`/`Default_Pose` | MD older than 2024.0.173 | Update MD |
| USD garment misaligned on the MetaHuman in UE | Exported in `Apose`, not `Default_Pose` (arms bent) | Apply `Default_Pose`, re-export |
| Chaos Cloth data missing after USD import | MD < 2025.2 with UE 5.6+, or UE 5.5 | MD 2025.2+ and UE 5.6+ |
| Remeshed/retopologised garment "falls apart", sewing gone | MD retopology removes sewing | Remesh last on a copy; keep the triangle project; *Remesh All (Replace)* |
| Exported FBX has split seams / shading lines | *Unweld* export | *Weld*; or merge by distance in Blender |
| Normals inverted/black panels in UE | Pattern faces flipped in MD | *Flip Normal* on the pattern in MD, or *Recalculate Outside* in Blender; two-sided material as fallback |
| Thickness exported as a second shell with bad normals | *Thick* export of a triangle mesh | Export *Thin*; add thickness with Solidify on edge loops |
| Textures from MD look flat in UE | MD fabric textures are preview-grade | Re-texture in Substance; use MD only for normal/height bakes |

## Blender fitting and simulation

| Symptom | Likely cause | Fix |
|---|---|---|
| Cloth sits 1.5 cm above the body | Default object collision `distance_min` 0.015 m | 0.003–0.005 m; body collision thickness outer 0.001–0.003 |
| Cloth passes through the body | Body has no *Collision* physics or it is on the wrong copy; `collision_quality` too low; cloth starts intersecting | Add Collision to the evaluated body copy; quality 4–6; start outside, settle |
| Shrinkwrap pulls the sleeve into the torso | `NEAREST_SURFACEPOINT` picks the torso | `PROJECT` along normals, limit with a vertex group, or fit sleeves separately |
| Shrinkwrap flattens folds | Wrap mode `ON_SURFACE` | `OUTSIDE_SURFACE`/`ABOVE_SURFACE` with offset; exclude fold regions via vertex group |
| Surface Deform bind fails ("target has edges with more than two polygons", "concave polygons") | Dirty body target | Bind to a clean body copy (apply modifiers, triangulate n-gons, remove non-manifold) |
| Garment moves when the armature is parented | Garment had unapplied transforms | `Ctrl+A` all transforms before parenting/transfer |
| Fit changes after export | Modifiers (Shrinkwrap/Solidify) applied by the exporter in a different order | Apply modifiers manually in order before export |

## Skin weights

| Symptom | Likely cause | Fix |
|---|---|---|
| Vertices snap/stretch when posing (collar, cuffs) | `NEAREST` vertex mapping on thick parts; inner shell took weights from inside the neck/arm | `POLYINTERP_NEAREST`; transfer from outer shell only; copy to inner loops |
| Sleeve hem pulled toward the torso | No distance limit in the transfer | `use_max_distance=True`, `max_distance=0.05` |
| Garment distorts in UE but is fine in Blender | >8 influences or un-normalized weights; weights on non-deform bones | Limit Total 8, Normalize All, delete non-deform groups |
| Hem swims against the leg | Garment weights smoother than the body's | Less smoothing near hems; copy the body's rows |
| Garment weighted to bones the body skeleton lacks | Transferred from a different body/armature | Transfer from the exact game body; `use_armature_deform_only` on export |
| Extra `Armature` bone / skeleton mismatch in UE | Armature object exported as a node | Name the armature object `root` to match Manny/MetaHuman, or re-import onto the body skeleton |

## Scale, axes, import

| Symptom | Likely cause | Fix |
|---|---|---|
| Garment 100× too big/small in UE | Blender `apply_scale_options='FBX_SCALE_NONE'` with metres; MD mm export | `FBX_SCALE_ALL` + `apply_unit_scale=True`; MD unit cm |
| Garment lying on its side | Axis conversion or `bake_space_transform` | Keep `axis_forward='-Z'`, `axis_up='Y'`, `bake_space_transform=False`; let UE convert |
| USD garment in metres inside UE | `convert_scene_units` left at metres | `CENTIMETERS` (verify UE import setting) |
| Vertex-color masks wrong in UE | sRGB/linear mismatch (`colors_type`) | Export `'LINEAR'` for numeric masks, check UE vertex color import option |

## Look

| Symptom | Likely cause | Fix |
|---|---|---|
| Cloth looks like plastic | Uniform roughness, no fuzz, normal too strong, no weave detail | Roughness map with wear; Substrate fuzz; weave detail normal; normal strength ≤ 1 |
| Folds look painted on | Folds only in the normal map | Large folds in geometry/sim; bake medium folds; weave tiled |
| Lighting seams along panels | Normals recomputed on import; UV island borders on a texture edge; MD unweld | *Import Normals and Tangents* in UE; padding ≥ 16 px; weld |
| Normal map lighting inverted | OpenGL (green-up) map in UE | DirectX (green-down) in Painter project, or flip green on import |
| Texture blurry at the table | Texel density below 10 px/cm on hero garments | UDIM or 4K; measure density |
| Mirrored dirt/wear | Mirrored UVs on hero garments | Unique UVs for hero garments |
| Garment halos at grazing angles | Fuzz too high / fuzz colour too bright | Lower FuzzAmount, darker FuzzColor, check under table lamps |

## LODs and masks

| Symptom | Likely cause | Fix |
|---|---|---|
| LOD popping | Decimate changed silhouette/normals; LOD screen sizes differ from the body | Protect silhouette/seam groups; match the body's screen sizes |
| Skin pokes through at mid distance only | Body faces under the garment not removed in lower LODs; body/garment reduced independently | Remove in all LODs; same reduction settings |
| MetaHuman body fully visible after assembly | Hidden Face Map fully black (bug) or set after assembly; two masks | Keep some white; set before assembly; merge masks |
| Gap at the garment edge after LOD reduction | Mask boundary exactly at the garment edge | Keep 1–2 loops of body overlap under the edge |

## MetaHuman outfits

| Symptom | Likely cause | Fix |
|---|---|---|
| Fits in Creator, clips after changing the body | Fixed garment on a parametric body; no source size near that body | Parametric Outfit Asset with more source bodies; *Source Size Override*; or compatibility body |
| Outfit Asset validation fails | Not under `/Game/Outfits/<Name>/` with the matching subfolder; MetaHuman Creator Core Data missing | Fix the folder structure; install Core Data |
| Transfer Skin Weights node gives garbage | Target not set to render mesh; wrong source mesh; unit mismatch between USD and body | Target = render mesh, transfer type = skeletal mesh, source = combined skeletal mesh; fix units |
| Resized outfit looks warped | Too few interpolation points or body far from all sources | Raise interpolation points; add a size |
