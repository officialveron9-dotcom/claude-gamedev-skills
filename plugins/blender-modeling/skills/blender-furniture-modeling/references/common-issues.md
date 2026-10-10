# Common issues: symptom → cause → fix

Read when a piece looks wrong in Blender, GTA/FiveM or Unreal. Version tags: Blender 4.5.14/5.2.2 rows marked [V]
were reproduced headless; others are practice (verify). Add solved bugs here (exact message or symptom, version).

## Looks wrong

| Symptom | Cause | Fix |
|---|---|---|
| Furniture looks toy-like / chunky | boards 30–50 mm instead of 16–19 mm, legs too fat, no bevels, no reveals, one material | sizes from [dimensions.md](dimensions.md) §11, bevel 1–3 mm, 2–3 mm gaps, per-part materials |
| Looks like a CG block, edges razor sharp | no bevel, or Bevel modifier with default width 0.1 m disabled because it looked melted | width 0.001–0.003, 2 segments, Harden Normals, Weighted Normal [V defaults] |
| "Melted"/blobby edges after adding Bevel | default width **0.1 m** [V] | set width in metres (0.002) |
| Doors/drawers read as one slab | fronts modelled without gaps | 2–3 mm between fronts, gap/2 at outer edges |
| Wood grain runs across legs or doors | one global UV projection, islands not rotated | `uv_grain_project` (U along the long axis) or rotate islands 90° |
| Grain repeats identically on every board | all parts unwrapped to the same 0–1 square | world-scale box projection (object coordinates), offset per part |
| Chair back looks glued on with a gap | back post rotated about its back edge | rotate about the front-bottom edge so it sinks into the seat [V] |
| Painted metal frame looks like chrome | Metallic 1 on paint | Metallic 0, roughness 0.4–0.6 |
| Glass shelf invisible or black | single plane, no thickness, wrong shader | real thickness (6–12 mm), `glass` shader (GTA) / translucent non-Nanite mesh (UE) |

## Geometry and shading bugs

| Symptom | Cause | Fix |
|---|---|---|
| Flickering stripes where two parts meet (z-fighting) | coplanar same-facing faces of two parts overlap (post flush with seat side, crossing stretchers at one height, back panel flush in the outline) | offset 1–8 mm or stagger; test with `zfight_pairs()` [V] |
| Flicker on a tabletop item at distance (GTA) | rug/sticker/document 0–1 mm above the surface | ≥ 2–5 mm offset or a `decal` shader; never coplanar |
| Black or smeared shading on flat faces | no custom normals; Bevel without Harden Normals; flat face not planar | Bevel Harden Normals + Weighted Normal (Keep Sharp); flatten the face (`scenario-blender-hard-surface`) |
| Shading breaks after joining objects | one object had flat shading or different normals | smooth all faces, re-run `finalize` |
| Inverted/black faces in game, OK in Blender | flipped normals hidden by backface culling off | recalc outward per shell (`finalize`); check signed volume > 0 [V] |
| Bevel smaller than set on every edge | Clamp Overlap is object-wide: one thin part (3 mm back, glass, sight) limits all bevels: 2.0 → 1.5 mm [V 4.5.14, 5.2.2] | weight-limited bevel with thin parts weighted down (`finalize`), or put thin parts in another object |
| Non-manifold edges after "Merge by Distance" | merge welded touching boards whose corners coincide (2 edges on the bookcase) [V] | merge per island (`finalize`), never on the whole multi-part mesh |
| Non-manifold seam after Mirror | half-part closed at the mirror plane + merge → doubled inner face (8 edges) [V] | delete the plane face of each half before mirroring, merge + clipping on |
| Groove down the middle of a mirrored top | Mirror merge off: two halves get their own bevel | merge on with open halves, or model the top whole |
| Bevel artifacts around a boolean cut (pocket, handle recess) | cut after/below the bevel, cutter near an edge | EXACT boolean above the bevel, cutter clear of edges (`scenario-blender-hard-surface`) |
| Splayed leg pokes through the seat / wobbles | leg built as a rotated box | sheared box with level ends (`Parts.hexa`) [V] |
| Drawer box intersects the bottom panel | box built from the front's bottom edge | box bottom ≥ panel top + 3 mm [V] |
| Hidden faces waste triangles | closed shells touching | delete fully hidden contact faces on the final game copy only |

## Scale, placement, pivot

| Symptom | Cause | Fix |
|---|---|---|
| Wrong size in UE (100× or 0.01×) | unit scale ≠ 1.0, scale not applied, FBX scale option | metres + `scale_length 1.0`, apply scale, `apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL'` (round trip verified [V]); compare with a 1 m cube |
| Wrong size in GTA | object scale not applied, or modelled in cm | `finalize` (applies rotation/scale to the data) [V]; Sollumz exports the evaluated mesh in metres |
| Object rotates around a strange point / snaps wrong | origin at the bbox centre or world origin | origin at the bottom centre of the footprint (`finalize`) |
| Furniture floats above or sinks into the floor | origin not at min z, or legs not on z = 0 | `finalize` sets min z = 0; splayed legs must have level feet [V] |
| Faces the wrong way after import | front not on −Y, or UE Force Front X Axis toggled | front −Y in Blender, default FBX axes, check once with an arrow mesh |
| Doors swing from the middle | door origin not on the hinge axis | `separate_doors=True` (origin at the outer back edge), `finalize(door, keep_origin=True)` [V] |
| Bed mattress placeholder misplaced after origin change | stored local coordinates not shifted | `finalize` shifts `footprint`, `col_boxes`, `mattress` [V] |

## Game-specific

| Symptom | Cause | Fix |
|---|---|---|
| GTA: prop invisible inside the MLO | placed through a normal ymap, or not attached to a room | MLO entity in a room (`fivem-mlo-creation`) |
| GTA: player walks through / gets stuck under a table | no bound, or one box down to the floor | top + leg boxes (`make_collision(obj, "SOLLUMZ")`), collision material set |
| GTA: furniture pops/vanishes at short distance | drawable lod distances or archetype lodDist too low/high, LOD meshes missing | set `lod_dist_*` and archetype `lod_dist` (Sollumz defaults 9998 / 200) [D]; add LOD1/LOD2 |
| GTA: shading faceted/hard after export | Mesh Domain "Vertex" averages the custom normals | keep Mesh Domain "Face Corner" (Sollumz default) [D] |
| GTA Enhanced: crash/`ERR_GFX_*` near many props | > 128 materials/geometries in one drawable | 1–4 materials per prop; split drawables (`fivem-mlo-creation`) |
| Textures blurry/missing in town | YTD over 16 MiB (oversized asset warning) | ≤ 1024–2048 px, BC1/BC3, split dictionaries (`gta-texture-editing`) |
| UE: glass parts render with the Nanite fallback / look wrong | translucent material on a Nanite mesh | glass in a separate non-Nanite mesh [S] |
| UE: collision is the full render mesh or missing | UCX names do not match the mesh name, or not exported together | `UCX_<MeshName>_NN`, same FBX, Combine Meshes on [V names] |
| UE: smoothing-group warning, faceted look | `mesh_smooth_type='OFF'` with no imported normals | `mesh_smooth_type='FACE'`, Import Normals and Tangents |
| Poly count too high | 3+ bevel segments, round parts with 32+ segments, hidden interiors | 1–2 segments for games (table 396–972 tris [V]), 16–24 segments on round parts, no hidden interiors, LODs |

## bpy errors seen while building the generators

| Message | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'bmesh'` (bpy wheel 4.5/5.2) | `import bmesh` before `import bpy` | import bpy first [V] |
| `TypeError: '<' not supported between instances of 'IDPropertyArray' and 'IDPropertyArray'` | sorting custom-property arrays | `sorted(list(x) for x in obj["doors"])` [V] |
| `AttributeError: Vector addition: (int + Vector) invalid type for this operation` | `sum()` over Vectors | `sum(vectors, Vector())` [V] |
| `KeyError: 'bpy_prop_collection[key]: key "Clearcoat" not found'` | pre-4.0 Principled names | `Coat Weight`, see `blender-python-pitfalls` [V 5.2.2] |
