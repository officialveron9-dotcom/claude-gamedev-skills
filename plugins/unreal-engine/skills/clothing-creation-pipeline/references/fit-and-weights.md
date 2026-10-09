# Fit to a specific body, weights, masks, correctives, LODs

Contents: body export · avatar import (MD, Blender) · fitting methods · weight transfer (Blender, Maya, UE) · multi-layer garments · body hiding masks · correctives · fitting one garment to many bodies · LODs · poses to test.

---

## 1. Get the game body out of UE

| Body | Export | Scale / pose |
|---|---|---|
| MetaHuman (5.6+) | MetaHuman Character → MetaHuman Creator menu → **Export Combined Skel Mesh** → Content Browser → right-click → *Asset Actions > Export* → FBX | cm, A-pose, extended Manny skeleton. Lock the body sliders first; a later body change = refit |
| Manny / Quinn | `SK_Mannequin` / `SK_Mannequin_Female` → Export FBX | cm, A-pose |
| CC5 / Daz / Fab body | Export the skeletal mesh you actually use | Check the bind pose (CC: UE5/MetaHuman preset) |

Also export the body's **skin weights** (they are in the same FBX) and one or two **animations** (bridge stance, stroke, sit) as FBX with skin for pose testing.

Which parts of the body to keep in the DCC: full body for fitting; for the mask step keep the UV layout intact (don't merge or re-unwrap the body).

---

## 2. Bring the body into the DCC

**Marvelous Designer**
- *File > Import > FBX*. Object Type **Avatar**, Scale **cm** (not mm), Axis Y-up (default). Confirm the height in the measure tool (MetaHuman male default ≈ 181 cm).
- If it arrives in T-pose, import an A-pose or apply the CLO/MD `Apose` pose. For the USD → Outfit Asset path, switch to `Default_Pose` before export.
- Avatar *Skin Offset*: 2–3 mm. Larger values float every garment.
- Keep the imported avatar; you need the same file in UE as the Transfer Skin Weights source.

**Blender 5.2**
- *File > Import > FBX*, defaults (`global_scale=1.0`, `apply_unit_scale`). The 180 cm body becomes 1.8 m. Scene units stay **metres**.
- Keep **Automatic Bone Orientation off** and the armature object unchanged; you will export the garment with this armature later. Rename the armature object to `root` only if you are rebuilding the hierarchy; otherwise re-export with the same object and let UE match bones by name.
- Apply nothing to the body. Make a *copy* for collision/fitting (apply modifiers on the copy only).

---

## 3. Fitting methods (Blender)

| Method | When | Settings |
|---|---|---|
| **Shrinkwrap** | Pull a block-out or a bought garment onto the body | `wrap_method='NEAREST_SURFACEPOINT'`, `wrap_mode='OUTSIDE_SURFACE'` or `'ABOVE_SURFACE'`, `offset` 0.004–0.012 m. Use a vertex group to exclude hems, collars, loose parts. `PROJECT` along normals for sleeves (nearest point grabs the torso) |
| **Surface Deform** | Transfer a fit from body A to body B (same topology bodies, e.g. two MetaHuman shapes) | Bind garment to body A copy (`surfacedeform_bind`), swap target shape via shape key on the body, apply. Bind fails on non-manifold or concave n-gon targets: use a clean, modifier-applied body copy |
| **Cloth sim** | Drape soft garments, settle after Shrinkwrap | Garment: Cloth, `quality` 8–12, `collision_quality` 4–6, object collision `distance_min` 0.003–0.005, `use_self_collision`, `self_distance_min` 0.003, pin group. Body copy: Collision physics, thickness outer 0.001–0.003, single-sided off. Bake 40–80 frames then *Apply as Shape Key* |
| **Lattice / proportional edit** | Local pushes at the armpit or crotch | Proportional size 5–10 cm, *Connected only* |
| **Sculpt Cloth brush** | Fold art direction | Low strength, on a duplicate without modifiers |

Rules: garment and body at identity transforms (apply scale/rotation), same origin; fit in the bind pose; offset from skin 3–5 mm minimum (tight knits), 8–15 mm (shirts), 20 mm+ (coats). Inner layers get *less* offset than outer layers and the outer layer is shrink-wrapped to the inner one, not to the body.

---

## 4. Skin weight transfer

### Blender (verified operator names, 5.2)

Order: select the **body** (source), then the **garment** (active, destination) → `bpy.ops.object.data_transfer(...)` or the modifier. Mapping: `vert_mapping='POLYINTERP_NEAREST'` (Nearest Face Interpolated). Layers: `layers_select_src='BONE_DEFORM'` or `'ALL'`, `layers_select_dst='NAME'`, `use_create=True`. Only-neighbour filter: `use_max_distance=True, max_distance=0.05` (5 cm) so a sleeve cannot pull weights from the torso. Thick garments: transfer with the garment's **outer shell only** (mask vertex group), then copy to the inner loops.

Then, on the garment: `vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=2)` → `vertex_group_clean(group_select_mode='ALL', limit=0.01)` → `vertex_group_limit_total(group_select_mode='ALL', limit=8)` → `vertex_group_normalize_all(lock_active=False)`. Add the Armature modifier pointing at the body's armature; delete vertex groups that are not deform bones.

Where the garment touches skin (collar, cuffs, waistband, trouser hem over socks) the weights must **equal** the body's: transfer those rows with `use_max_distance` 0.5 cm and no smoothing, or hand-copy the body's weights on the matching loop.

Influence count: UE's default limit is 8 per vertex, with a project setting for more/unlimited (verify for 5.8); extra influences are dropped on import and the mesh changes shape.

### Maya (standard option names; not re-verified this round)
Copy Skin Weights: *Surface Association* = Closest Point on Surface, *Influence Association* = Name (fallback One to One), sample space World, then *Smooth Skin Weights* and *Prune Small Weights* 0.01, max influences 8.

### Unreal (details in `ue5-character-creation-clothing`)
- Skeletal Mesh Editing Tools plugin: weight transfer from a source skeletal mesh and painting.
- Geometry Script `TransferBoneWeightsFromMesh` (static → skeletal garment).
- Cloth Dataflow `TransferSkinWeights` node (body → sim/render mesh). This is the right place for Chaos Cloth garments; for skinned garments transfer in the DCC where you can smooth and inspect.

### Common weight failures
| Symptom | Cause | Fix |
|---|---|---|
| Collar flips inside when the head turns | Inner collar loops got neck weights from the inner surface, outer got shoulder weights | Transfer from the outer shell, copy inward; or smooth across the thickness |
| Sleeve hem stretches toward the torso | Nearest mapping or no distance limit | `POLYINTERP_NEAREST` + `max_distance` 5 cm; re-transfer |
| Garment explodes on first pose in UE | Un-normalized weights, >8 influences, or weights on non-deform bones | Clean → limit → normalize; delete non-deform groups |
| Hem swims against the leg | Garment weights smoother than the body's at the knee | Less smoothing on hems; match the body rows |

---

## 5. Multi-layer outfits (shirt + waistcoat + jacket)

- Fit inner to body, outer to inner (Shrinkwrap target = the inner garment), 2–4 mm between layers.
- Delete inner-layer faces that are never visible (shirt under a closed waistcoat) and give the outer layer the inner layer's weights where they overlap (transfer from the inner garment, not from the body, for the overlap region only).
- Keep each layer a separate mesh/section so UE can hide pieces per outfit variant. Merge for NPCs.

---

## 6. Body hiding masks

| Target | How to author |
|---|---|
| Fixed outfit (NPC, Manny, CC) | Delete body faces under opaque cloth in the DCC (keep a body variant per outfit). Leave 1–2 loops of overlap under the garment edge so LOD reduction never opens a gap |
| MetaHuman wardrobe item | **Body Hidden Face Map**: texture in the MetaHuman body UV layout, white = keep, black = remove. In Blender: select body faces within ~1 cm *inside* the garment (script in `blender-automation.md`), bake selection → vertex color or paint to a UV image, export PNG. One mask per character (merge shirt + gloves masks), never fully black |
| CC5 | *Hide Body Mesh* tool on the garment; *Delete Hidden Mesh* on export (irreversible; keep the CC project) |
| Runtime toggling | Material opacity mask on the skin: last resort (cost, shadows) |

Test masks at all LODs: a body LOD that merges vertices across the mask boundary pokes through.

---

## 7. Correctives (armpit, crotch, elbow, shoulder)

1. Import the stroke / bridge / sit clips onto the body in the DCC. Scrub to the worst frames.
2. Where skin shows: first increase local offset (sculpt/proportional edit on the garment in bind pose, 2–5 mm), then fix weights (garment weights at the joint should match the body's a little *more* on the outer side so the cloth travels with the limb), then add a **shape key** per problem pose.
3. Drive the shape key like the body's corrective: UE morph target with the same name as a MetaHuman corrective curve (so Leader Pose curves drive it) or a bone-rotation driver re-created in the AnimBP. MetaHuman body correctives deform the body only; garments need their own.
4. Crotch/hips: raise the trouser rise and add ease instead of correctives; a tight trouser on a bent hip always clips.
5. Elbows/knees: add 2–3 edge loops across the joint on the outside, keep the inside sparse.

---

## 8. One garment, many bodies

| Situation | Approach |
|---|---|
| Fixed cast (player, 6 opponents, 10 NPCs) | Refit per body: Surface Deform from the authoring body to each target body (same topology MetaHuman bodies), apply, re-check offset, re-transfer weights. One mesh per character. Simplest and most robust |
| Player body customisation | MetaHuman **Outfit Asset** with source bodies: author on body A, add sizes for bodies that resize badly. Epic: at least 2 source bodies; 4–6 in practice (one height row). Each source body is one combined body+head mesh; the garment must be the same mesh/representation per size |
| Manny-based characters with different proportions | Keep one body scale; vary clothing instead. Scaling bones breaks fit quickly |

---

## 9. LODs matched to the body

- Same LOD count and screen sizes as the body (MetaHuman UE Optimized: check the body's LOD settings in UE and copy them).
- Blender Decimate per LOD: `decimate_type='COLLAPSE'`, `ratio` 0.5 / 0.25 / 0.1, `use_symmetry=True` where the garment is symmetric, `vertex_group` = "protect" (seams, silhouette edges, mask boundary) with `invert_vertex_group=True` and `vertex_group_factor` high, `use_collapse_triangulate=True`. Decimate **after** weight transfer; the modifier keeps weights.
- Or let UE generate skeletal LODs with the same reduction settings as the body. Do not mix (DCC LODs on the body, auto-LODs on the garment) without checking the switch distances.
- Remove body faces under the garment in **every** LOD, or the body's lower LOD shows through the garment's lower LOD.
- Cloth-simulated garments: separate low-res sim mesh (2–8 k tris); LOD1+ falls back to skinned, so the skinned fallback must already look right.

---

## 10. Poses to test before export (billiards)

Bridge stance (torso folded over the rail, left arm extended), full back-swing and follow-through of the cue arm, chalking (elbow bent >120°), sitting on a bar stool, walking, leaning on the cue. Skin showing in any of these = fix in the DCC now.
