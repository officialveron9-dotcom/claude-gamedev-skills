# Topology, shading and game-readiness rules (no-bugs pass)

Read before exporting, or when a piece shades badly, flickers, floats or has the wrong size in game. [V] = verified
headless in this skill's tests on bpy 5.2.2 and 4.5.14; [D] = read in source; [N] = practice (verify).

## 1. Rules

| # | Rule | Check |
|---|---|---|
| 1 | Scene metric, `unit_settings.scale_length = 1.0`, model in metres | a 1.75 m reference box next to the piece |
| 2 | Rotation and scale applied (`finalize` does it on the data, keeping the world placement) [V] | `obj.matrix_basis.to_3x3() == Identity` |
| 3 | Origin = bottom centre of the footprint (floor contact); front faces −Y; Z up | min z of the mesh = 0; footprint centred on 0,0 [V] |
| 4 | Every part a closed shell with outward normals | non-manifold edges = 0; signed volume per island > 0 [V] |
| 5 | No coplanar same-facing overlapping faces between parts (z-fighting) | `zfight_pairs()` in the tests [V] |
| 6 | Merge by distance **per part** (island); never on the whole multi-part mesh | a global merge welded the bookcase into 2 non-manifold edges [V] |
| 7 | No loose verts/edges, no degenerate faces | `finalize` deletes them |
| 8 | Smooth shading + Bevel (Harden Normals) + Weighted Normal instead of subdivision | evaluated mesh `has_custom_normals` [V] |
| 9 | One bevel width/segment count per asset; thin parts weighted down so Clamp Overlap does not shrink every bevel | top keeps 2.00 mm next to a 3 mm back panel [V] |
| 10 | N-gons only on flat caps (round seat tops); triangulate for export (modifier with Keep Normals) | `finalize(triangulate=True)` keeps custom normals [V] |
| 11 | Mirror/Array: open the half-part at the mirror plane before merging (§2); apply before UV/tests if anything reads `obj.data`; exporters (FBX `use_mesh_modifiers`, Sollumz) use the evaluated mesh [D] | non-manifold = 0 on the evaluated mesh [V] |
| 12 | Glass, emissive and decal parts as separate geometry/material (GTA alpha bucket, UE non-Nanite) | – |
| 13 | Collision = a few boxes, never the render mesh | UCX/box bounds from `col_boxes` [V] |
| 14 | LODs: LOD0 bevelled, LOD1 = same parts unbevelled, LOD2 = boxes | tris 972 > 108 > 60 for the table [V] |

## 2. Modifier defaults that bite (read on 5.2.2) [V]

| Modifier | Default | Use for furniture |
|---|---|---|
| Bevel | width **0.1 m**, segments 1, limit Angle 30°, profile 0.5, Harden Normals **off**, Clamp Overlap on, Miter Outer Sharp, `edge_weight = "bevel_weight_edge"` | width 0.001–0.003, segments 1–2 (game) / 3 (render), Harden Normals on, Miter Outer Arc; limit Weight when thin parts share the object |
| Weighted Normal | mode Face Area, weight 50, threshold 0.01, Keep Sharp off | Keep Sharp on; place last (before Triangulate) |
| Solidify | thickness 0.01, offset −1, even thickness off | prefer real boxes; for curved panels set even thickness on |
| Array | relative offset (1,0,0), merge off (merge threshold 0.01) | slats/shelves: constant offset in metres, merge off (parts must not weld) |
| Mirror | X axis, merge on (0.001), clipping off | delete each half-part's face lying on the mirror plane, then merge on + clipping on. Closed half-boxes + merge left a doubled inner face (8 non-manifold edges on a half table); merge off keeps two halves whose bevel cuts a groove down the middle [V] |
| Boolean | solver EXACT (`FLOAT` = old Fast, `MANIFOLD` 4.5+), self off | EXACT; cut before the bevel (see `scenario-blender-hard-surface`) |
| Triangulate | Beauty / Shortest Diagonal, Keep Normals off | Keep Normals **on** after Weighted Normal |

Harden Normals needs custom normals; Blender creates them automatically (manual [S]). Blender 4.1+ has no Auto Smooth:
`shade_auto_smooth` adds a "Smooth by Angle" GN modifier, and Bevel/Weighted Normal work without it
(`blender-python-pitfalls` §5).

```python
bev = obj.modifiers.new("Bevel", "BEVEL")
bev.width, bev.segments, bev.profile = 0.002, 2, 0.5
bev.limit_method = "ANGLE"            # or "WEIGHT" + bevel_weight_edge attribute (finalize does this)
bev.harden_normals = True
bev.miter_outer = "MITER_ARC"
wn = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
wn.keep_sharp = True
obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
```

### The Clamp Overlap trap (verified)

One mesh with a 25 mm slab and a separate 3 mm panel, Bevel 2 mm/Angle/Clamp Overlap on: the slab's bevel drops to
**1.5 mm** (the thin panel's limit is applied object-wide); with clamp off it stays 2.0 mm; with a weight-limited
bevel where the thin panel's edges get weight 0 (or ≤ t/(2.5·width)) it stays 2.0 mm with clamp on. Same result on
5.2.2 and 4.5.14 [V]. `finalize()` writes `bevel_weight_edge` = 1 on edges ≥ 30° and scales it down on parts thinner
than 2.5 × width.

## 3. Budgets (practice, verify per project) [N]

| Item | GTA prop LOD0 tris | UE non-Nanite LOD0 | Generator result, 2 / 1 bevel segments [V] |
|---|---|---|---|
| Chair | 500–2 000 | 1 000–4 000 | 1 620 / 660 |
| Bar stool | 400–1 500 | 800–3 000 | 1 148 / 540 |
| Dining table | 300–1 500 | 800–3 000 | 972 / 396 |
| Bookcase, wardrobe, kitchen unit | 500–3 000 | 1 000–5 000 | 1 188–1 512 / 484–616 |
| Dresser (no drawer boxes) | 800–3 000 | 1 500–5 000 | 2 376 / 968 |
| Bed frame (18 slats) | 1 000–3 500 | 2 000–6 000 | 3 240 / 1 320 |
| Pool table | 3 000–8 000 | 5 000–15 000 | 5 016 / 2 328 |

- Sollumz splits any geometry above 65 535 vertices (16-bit indices) on export [D: `split_vert_buffers`]; furniture
  never gets close, so the limit that matters is draw calls: keep 1–4 materials per prop.
- FiveM warns per streamed asset above 16 MiB (textures dominate, not triangles): `fivem-mlo-creation`,
  `gta-texture-editing`.
- Unreal Nanite: triangles stop mattering for opaque meshes; keep the real bevels, skip LODs, but put glass in a
  separate non-Nanite mesh.
- Optional on the final game copy only: delete faces that are fully covered by a touching part (leg tops under a
  table, panel ends against sides). Saves ~15–25 % but breaks closed shells, so do it after collision/LOD generation.

## 4. Collision

| Target | How | Generator |
|---|---|---|
| Unreal | `UCX_<MeshName>_NN` convex boxes in the same FBX (or Simple Collision in the Static Mesh editor) | `make_collision(obj, "UE")` → top + 4 legs for a table, seat + back for a chair [V] |
| GTA/FiveM (Sollumz) | Drawable empty > `.model` + Bound Composite `.col` > Box bounds (embedded in the `.ydr`) | `make_collision(obj, "SOLLUMZ")` returns the asset dict `sz_convert()` (doors skill) expects [V layout, Sollumz not executed] |

- Collision material: `WOOD_SOLID_MEDIUM`/`WOOD_SOLID_POLISHED` wood, `METAL_SOLID_MEDIUM` metal, `MARBLE`/`STONE`,
  `GLASS_*` (names/indices in `fivem-mlo-creation` collision table). Composite flags: copy from a vanilla prop of the
  same kind (verify); the MLO-shell flag preset "General (Default)" is for map geometry.
- Leave walk space: a table needs top + leg boxes, not one box down to the floor (peds and the player clip around it).
- Interior props live in the MLO entity list (attached to a room); a prop placed through a normal ymap inside an MLO is
  culled (`fivem-mlo-creation`).

## 5. LODs and distances

- GTA: Sollumz LOD slots high/medium/low/very_low on the model (`model.sz_lods`). Drawable `lod_dist_high/med/low/vlow`
  default to 9998 and the archetype `lod_dist` to 200 (Sollumz properties [D]). For small interior furniture set
  realistic values (e.g. high 15–25 m, medium 40 m, archetype 50–100 m) (verify in game).
- UE: import LODs or use auto LOD reduction; Nanite meshes need none.

## 6. Export checklists

**GTA V / FiveM (Sollumz 2.9)**
- [ ] `finalize()` done; modifiers left live (Sollumz exports the evaluated mesh) or applied; Mesh Domain Face Corner.
- [ ] Hierarchy: Drawable `<prefix>_<name>` > `.model` (identity) + `.col` box bounds; names lowercase, unique, no `.001`.
- [ ] Shaders converted from the `sz_*` placeholders (`sz_apply_shaders`), textures power of two, YTD < 16 MiB.
- [ ] Collision material + flags (copied from a vanilla prop), archetype in a `.ytyp` with lodDist set; Static flag
      for immovable furniture (verify), Dynamic only for physics props.
- [ ] Placed as an MLO entity in a room; Gen9 copy in `stream_enhanced/` (`fivem-mlo-creation`).

**Unreal Engine 5.8 (FBX)**
- [ ] `finalize(triangulate=True)`; `UCX_` boxes next to the mesh; selection = mesh + UCX.
- [ ] FBX: `apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
      use_mesh_modifiers=True, mesh_smooth_type='FACE', use_tspace=True` (`blender-python-pitfalls` §9). A Blender
      round trip of the table with these settings returned 1.6 × 0.9 × 0.75 m and the 5 UCX objects [V]; check the
      size in UE against a 1 m cube.
- [ ] UE import: Import Normals and Tangents, Combine Meshes on, collision from UCX, Nanite on for opaque meshes.
