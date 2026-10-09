---
name: clothing-creation-pipeline
description: Guides creating photorealistic clothing that fits a specific character body before it reaches Unreal Engine 5.8. Covers tool choice with versions and licenses (Marvelous Designer/CLO 2026, Blender 5.2, Substance 3D, ZBrush, CC5, Daz, Fab, MetaHuman Outfit Assets), exporting the MetaHuman or Manny body as avatar, draping and fitting, skin weight transfer (Blender, Maya, UE), correctives, body masks, LODs, fabric materials and fuzz, FBX/USD export, bpy automation and Blender/MD MCP servers. Use when making or fitting garments, outfits or fabrics, or when clothes float, clip, snap or look plastic. German: Kleidung erstellen, fotorealistische Kleidung, Klamotten, passt nicht am Koerper, Stoff, Schnittmuster, Outfit.
---

# Clothing creation pipeline (DCC side, UE 5.8 handoff)

Scope: making a garment that fits *your* body (MetaHuman, Manny or a Fab/CC body) and looks real at billiards-table distance, then exporting it. Everything *inside* UE after import (Leader Pose, MetaHuman wardrobe assembly, Body Hidden Face Map, Chaos Cloth Dataflow, LODSync, import option names, licenses of Fab/Daz/Reallusion content) is in `ue5-character-creation-clothing`. Skin/cloth *shading* values live in `ue5-lighting-rendering`. Do not repeat those here.

Status checked 2026-10-09: UE 5.8, Marvelous Designer 2026.1, Blender 5.2 LTS, Substance 3D Painter 12.0.x, ZBrush 2026.2, Character Creator 5. Anything marked (verify) could not be confirmed from a primary source.

## Pick the pipeline (decision table)

| Need | Pipeline | Why / cost |
|---|---|---|
| Hero outfit, tailored look (shirt, waistcoat, trousers) seen in close-ups | **MD/CLO pattern + sim → retopo/cleanup in Blender → Substance → UE** (USD for MetaHuman, FBX otherwise) | Only pattern simulation gives believable seams, ease and folds. MD Personal 39 USD/mo or 280 USD/yr |
| Same, no MD budget | **Blender 5.2**: block out → Cloth sim with Pressure/Shrinkwrap → sculpt folds → retopo → Substance (or Blender paint) | Free. Folds are hand-made, 2–4× the time. Cloth sim is good enough for drape, not for tailoring |
| NPC / background outfit | **Buy on Fab** (MetaHuman parametric outfit or "Rigged to Epic skeleton") → refit only if it clips | Hours instead of days. Check license and skeleton before buying |
| Many body shapes from one garment (MetaHuman parametric bodies) | Author once → **Outfit Asset with several source bodies** (UE) | Resizing warps the garment per body. Needs ≥2 source bodies, better 4–6 |
| Characters from Reallusion | **CC5**: import OBJ/FBX garment → Transfer Skin Weights template → Conform → Hide Body Mesh → Auto Setup to UE | Fastest skinning of third-party garments. Auto Setup 2.0 lists UE 5.5–5.7; 5.8 unconfirmed |
| Daz characters | Daz dForce outfit → DazToUnreal or FBX | Interactive License per product. No 5.8 bridge build found |

Full comparison, versions, prices, license traps: [references/tools-and-sources.md](references/tools-and-sources.md).

## Top traps (read first)

1. **Draping on the wrong body.** Always export the *final game body* (MetaHuman: *Export Combined Skel Mesh* → FBX; Manny: `SK_Mannequin`) and drape on it. A garment made on MD's default avatar never fits a MetaHuman at the shoulders, chest and crotch.
2. **Units.** UE = cm. MD import/export dialogs may default to **mm**; Blender scene = m. A 1.8 m garment that imports at 18 000 or 1.8 units is a unit mistake, never fix it with actor scale. Blender export: `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_ALL'`.
3. **Exporting MD's simulation mesh as the game mesh.** MD triangles (particle distance 5–20 mm) are uneven, unwelded, and have no clean loops. Retopo or at least *Remesh (quad) + Weld* and clean the result in Blender. MD's retopology deletes sewing, so do it last on a copy.
4. **Zero thickness.** Thin single-sided cloth reads as paper. Model hems, collars, cuffs and plackets with thickness (MD *Thick* export or Blender Solidify 2–4 mm on edges only), keep the body panels single-sided with a two-sided material.
5. **Weights transferred from the wrong source or wrong mapping.** Transfer from the *body skeletal mesh* (not from another garment), garment and body in the same bind pose at identity transforms, mapping *Nearest Face Interpolated*, then smooth, clean and limit influences (UE default 8). Nearest-vertex mapping on a thick collar grabs the inner surface and snaps.
6. **Pose mismatch for USD → MetaHuman.** For the MD/CLO → USD → Outfit Asset path, CLO's doc says the body must be in its `Default_Pose` (arms bent) on export or the UE USD import misaligns. Fit in `Apose`, switch to `Default_Pose`, export.
7. **Testing only in the A-pose.** A billiards character bends over the rail and pulls the cue arm back. Pose the body (Blender: import a stroke animation FBX) and fix the armpit, elbow and hip before export, not in UE.
8. **One roughness for the whole garment.** Fabric realism is 80 % material: weave-scale normal + roughness variation, fuzz/sheen, wear on edges, dirt in creases, slightly different roughness per panel.
9. **Skipping the body mask.** Any opaque garment needs the body faces under it removed (DCC delete per outfit variant, or a Body Hidden Face Map for MetaHuman). Without it, every pose shows skin.
10. **Buying "MetaHuman clothing" that is fixed-size.** Fixed garments fit one of the 18 compatibility bodies only. Parametric ones carry an Outfit Asset. Read the listing.

## Workflow A: Marvelous Designer / CLO → UE (hero garments)

1. **Body out of UE.** Combined Skel Mesh (MetaHuman) or `SK_Mannequin` → right-click → *Asset Actions > Export* → FBX. Keep the file; it is also the weight source later.
2. **Avatar into MD.** *File > Import > FBX*, Object Type **Avatar**, unit **cm**, Y-up. Check the avatar is ~175–185 cm in MD's measure tool. Load an A-pose if the mesh comes in T-pose. Set the avatar's *Skin Offset* ≈ 2–3 mm (verify your version's default).
3. **Patterns.** Trace real patterns (reference photos of the actual garment type: shirt yoke, trouser rise, waistcoat darts). Particle distance 20 mm for the first drape, 5–10 mm for the final. Fabric presets per panel (cotton for the shirt, wool for the waistcoat), not one preset for all.
4. **Fit.** Ease: 2–6 cm at the chest for a shirt, close to 0 for a waistcoat. Use *Layer* for stacked garments (shirt 0, waistcoat 1, jacket 2). Strengthen tight regions rather than raising global stiffness. Add *Pinching* / *Brush Pinching* (2026.1) folds only where photos show them.
5. **Export the sim result** (for UE Chaos Cloth): *USD* (carries sim + render mesh, panels, attributes; MD 2025.2+ for UE 5.6+). **Export the game mesh** (for skinned garments): FBX/OBJ, *Thin*, *Weld*, *Unified UV* (single texture per garment) or *Multiple Objects* when you need a material per panel, unit cm. Export a second copy *Thick* only for bake/preview.
6. **Blender cleanup.** Merge by distance, fix normals, retopo (manual for hero, Quad Remesher/Instant Meshes for NPC), re-project MD detail as normal/height bake from the thick/high mesh, UDIM or atlas UVs, Solidify on edges, body mask faces.
7. **Weights, correctives, LODs**: [references/fit-and-weights.md](references/fit-and-weights.md).
8. **Materials**: [references/materials-realism.md](references/materials-realism.md).
9. **Export to UE**: table below, then continue in `ue5-character-creation-clothing` (import options, Leader Pose, Cloth Asset, Outfit Asset, LODSync).

MD/CLO → MetaHuman USD specifics (versions, folder rules, Dataflow nodes, parametric sizes): [references/tools-and-sources.md](references/tools-and-sources.md#marvelous-designer--clo).

## Workflow B: Blender only (no MD)

1. Import the game body FBX (cm → Blender applies 0.01, mesh ends up 1.8 m). Do not rotate or scale the armature.
2. Block the garment as a low-poly shell: duplicate body region → delete unwanted faces → *Shrinkwrap* (Nearest Surface Point, Offset 0.004–0.008 m) → add seams/loops by hand. Keep quads, loops follow seams.
3. Drape: Cloth modifier on the garment, body has *Collision* physics. Settings for a tight fit: cloth *Quality* 8–12, *Collision Quality* 4–6, object collision *Distance* 0.003–0.005 m (default 0.015 m floats the cloth 1.5 cm), self-collision distance 0.003, pin group at waist/shoulders, *Pressure* for puffy sleeves. Settle 40–80 frames, then *Apply as Shape Key* or apply the modifier.
4. Sculpt folds (Cloth brush, Dam Standard, Pinch) on a multires/high copy. Bake normal + AO + curvature to the game mesh.
5. Retopo if the sculpt changed topology; otherwise keep the block-out as the game mesh.
6. Weights, correctives, LODs, export: same as Workflow A.

Blender 5.2 LTS adds experimental node-based cloth in Geometry Nodes; stay on the classic Cloth modifier for production.

## Fit to a specific body: minimum rules

- Same bind pose, same scale, identity transforms on garment and body before any transfer (`Ctrl+A` apply all; parent to the armature with *Empty Groups*).
- Offset from skin: 3–5 mm for tight knits, 8–15 mm for shirts, more for coats. Below 3 mm the UE skinning jitter shows skin.
- Weights: `Data Transfer` (Vertex Groups, *Nearest Face Interpolated*, *Only Neighbor Geometry* ~5 cm) → `Smooth` 2–3 iterations ×0.5 → `Clean` 0.01 → `Limit Total` 8 → `Normalize All`. Hard-lock collar/cuff/waistband rows to the body's weights.
- Thick parts (collar, cuffs): transfer from the *outer* surface only, then copy to inner loops (Blender: transfer with a vertex group mask, or `Copy Vertex Group to Selected`).
- Correctives: pose the body through the stroke/bridge/sit poses; where skin shows, add a shape key per pose driven by the same curve or bone rotation as the body's corrective, or push the garment out locally. Never inflate the whole mesh.
- Multiple MetaHuman bodies: author on one body, build an Outfit Asset with several source bodies in UE (Epic: at least 2, suggests 4–6). For a fixed cast, just refit per character and skip resizing.
- LODs: same count and screen sizes as the body. Blender *Decimate* (Collapse, Symmetry, vertex group protecting seams and silhouette edges) at 50 % / 25 % / 10 %, or let UE reduce with the body's settings.

Settings, Maya and UE alternatives, body mask authoring, armpit/crotch/elbow fixes: [references/fit-and-weights.md](references/fit-and-weights.md).

## Photorealism: what makes clothes fake

| Fake | Real |
|---|---|
| One roughness value, flat albedo | Roughness map with weave + wear; albedo with slight per-thread variation, dirt in creases |
| No fuzz | Substrate Slab *Fuzz Amount/Color/Roughness* (legacy: Cloth shading model) for cotton, wool, felt; near 0 for silk/leather |
| Paper-thin hems and collars | Geometry thickness on every visible edge; two-sided material on panels |
| Seams painted only in albedo | Seam/topstitch in normal + height (+ small AO), stitch geometry on hero garments where the camera is within ~1 m |
| Perfect symmetry | Mirror only in block-out; asymmetric folds, one rolled cuff, collar sits unevenly |
| Normal map noise instead of folds | Large folds in geometry/sim, medium in baked normal, weave in tiled detail normal |
| Texture blur at 1 m | Texel density: hero garments 10–20 px/cm (4K over a shirt), NPCs ~5 px/cm; UDIM for hero outfits, atlas for NPCs |
| Garment floats / hovers | Skin offset 3–5 mm, AO/contact shadow in creases, body mask |

Texel density math, UDIM vs atlas, material layering, Substance setup, baking from MD, fabric scans: [references/materials-realism.md](references/materials-realism.md).

## Export settings to UE (FBX, Blender 5.2 `bpy.ops.export_scene.fbx`)

| Option | Value | Why |
|---|---|---|
| `object_types` | `{'ARMATURE','MESH'}` | No cameras/lights/empties |
| `use_selection` | `True` (garment + armature only) | Never export the body with the garment |
| `apply_unit_scale` / `apply_scale_options` | `True` / `'FBX_SCALE_ALL'` | Scene in metres → UE cm with root scale 1 |
| `add_leaf_bones` | `False` | Default is True and adds `_end` bones |
| `use_armature_deform_only` | `True` | Drops control bones |
| `mesh_smooth_type` | `'OFF'` (normals only) + `use_tspace=True` | UE imports normals/tangents; smoothing groups are legacy |
| `colors_type` | `'SRGB'` default; `'LINEAR'` when vertex colors are masks (verify UE import matches) | Masks must not be gamma-shifted |
| `bake_anim` | `False` | Mesh export only |
| `use_mesh_modifiers` | `True` (and no unapplied Solidify you still want editable) | Modifiers are applied in the file |
| `bake_space_transform` | `False` | Marked experimental/broken with armatures in Blender's own source |
| Armature object name | `root` (Manny/MetaHuman) | Else an extra `Armature` bone |

USD from Blender (`bpy.ops.wm.usd_export`): `export_armatures=True`, `only_deform_bones=True`, `export_shapekeys=True`, `convert_scene_units='CENTIMETERS'` (verify against your UE USD import units), `convert_orientation=True`, `export_global_forward_selection='X'`, `export_global_up_selection='Z'`. UE import option names and the skeleton choice: `ue5-character-creation-clothing` (import table).

Triangle budgets (starting points, not Epic figures): hero garment 20–40 k tris at LOD0, whole hero outfit ≤ 100 k; named NPC outfit ≤ 30 k; background NPC outfit ≤ 12 k. Cloth sim mesh (Chaos) 2–8 k tris per simulated region.

## Automation with Claude

- Blender: everything in Workflow B after the artistic steps is scriptable in `bpy` (Blender 4.x/5.x API): batch weight transfer, Shrinkwrap/Solidify passes, decimated LODs, validation (scale, tri count, influences, non-manifold), FBX/USD export. Verified snippets: [references/blender-automation.md](references/blender-automation.md).
- Drive Blender live via MCP: the official **Blender Lab MCP** extension (Blender 5.1+, port 9876) or the community **mcp-for-blender** (MIT, formerly `blender-mcp`). If this session already exposes a Blender bridge tool that executes Python (e.g. a `bl_execute`-style tool), use it directly.
- Marvelous Designer: has an in-app **Python API** (since the 2025.1/Linux release; plug-ins registered via *Plug-in Manager*). Reported as Enterprise-tier at launch; a community MCP runs it on Windows MD 2026.0.315 (tier unverified). Pattern design and fitting stay manual; use scripts for batch import/sim/export only.
- Substance 3D Painter: in-app Python API for export (`substance_painter.export`). CLO/ZBrush: no path for Claude; ZBrush is ZScript only.
- Existing community skills and MCPs with licenses and verdicts: [references/external-skills.md](references/external-skills.md).

## Fast triage (full table in common-issues.md)

| Symptom | First check |
|---|---|
| Garment explodes or vibrates in MD | Patterns intersect at arrangement, particle distance too small for the first drape, layers wrong, avatar colliding with itself |
| Clothes float above the skin | Blender collision *Distance* 0.015 default; MD skin offset; Shrinkwrap offset too big |
| 100× wrong size in UE/MD | mm vs cm (MD), FBX scale options (Blender) |
| Vertices snap or stretch when posing | Nearest-vertex mapping on thick parts; transfer done off-pose; influences >8; garment weighted to bones the body lacks |
| Visible seams / shading lines on the garment | Unwelded MD export; normals recomputed on import; UV seam on a texture border |
| Cloth looks like plastic | Uniform roughness, no fuzz, DirectX/OpenGL normal flip, normal map too strong |
| LOD popping | Decimate changed silhouette/normals; screen sizes differ from the body |
| MetaHuman outfit fits in Creator, clips after body change | Fixed garment on a parametric body; add a source size or use Source Size Override |
| USD garment misaligned in UE | Exported in A-pose instead of `Default_Pose`; unit mismatch |

[references/common-issues.md](references/common-issues.md)

## Checklist: reference photo → game-ready garment

- [ ] Reference set: 3+ photos of the real garment type (front/back/side, close-up of seams, fabric at 10 cm). Note fabric, weight, ease, where it wrinkles.
- [ ] Game body exported from UE in the final shape (MetaHuman body sliders locked, or compatibility body chosen). Height checked in the DCC.
- [ ] Garment built on that body at cm scale, A-pose. Stacked garments layered inner → outer.
- [ ] Fit checked in bridge stance, full stroke, sitting, walking (posed body or animation import). Skin offset ≥ 3 mm everywhere.
- [ ] Game mesh: welded, clean quads/tris, loops along seams, thickness on visible edges, body faces under opaque cloth removed (or mask painted), tri budget met, no n-gons, no non-manifold edges except intended open borders.
- [ ] UVs: hero = UDIM or 2×4K, NPC = one 2K atlas; texel density consistent with the body; seams hidden; straightened where the weave must stay aligned.
- [ ] Bakes from the high/sim mesh: normal (DirectX/green-down for UE), AO, curvature, height, thickness/ID.
- [ ] Material: base fabric (weave normal + roughness) → wear layer (edges, curvature) → dirt (crease AO) → fuzz parameter; two-sided where needed; per-panel roughness variation.
- [ ] Skin weights transferred from the body, smoothed, cleaned, ≤ 8 influences, normalized; collar/cuff/waist rows match the body exactly.
- [ ] Correctives for armpit/elbow/hip (shape keys) if the stroke pose showed skin.
- [ ] LODs match the body (count, screen sizes); sim mesh separate for Chaos Cloth parts.
- [ ] Exported with the settings above (FBX) or USD for MetaHuman Outfit Assets; file named `SK_<Character>_<Garment>`; skeleton = body skeleton on import.
- [ ] Licenses logged: MD Personal/Enterprise terms for your situation, Substance assets, Fab/CC/Daz content (`ue5-character-creation-clothing`).
- [ ] Continue with the in-UE checklist in `ue5-character-creation-clothing`.

## References

- [references/tools-and-sources.md](references/tools-and-sources.md): read when choosing tools or buying garments. Versions, prices, licenses, MD/CLO ↔ MetaHuman USD, CC5, Daz, Fab, MetaHuman Outfit Assets.
- [references/fit-and-weights.md](references/fit-and-weights.md): read when fitting, transferring weights, authoring masks, correctives and LODs.
- [references/materials-realism.md](references/materials-realism.md): read when the garment looks fake. Texel density, UDIM, layering, fuzz, seams, baking, Substance.
- [references/blender-automation.md](references/blender-automation.md): read before writing bpy scripts or wiring a Blender/MD MCP.
- [references/external-skills.md](references/external-skills.md): community skills and MCP servers, licenses, verdicts.
- [references/common-issues.md](references/common-issues.md): symptom → cause → fix.
- [references/sources.md](references/sources.md): URLs, what each backed up, verification level.
