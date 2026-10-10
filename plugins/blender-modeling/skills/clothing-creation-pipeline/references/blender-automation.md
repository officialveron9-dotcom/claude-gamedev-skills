# Automating the garment pipeline with Claude (bpy, MCP servers, MD API)

Contents: what Claude can and cannot automate · Blender MCP options · verified bpy snippets (Blender 5.2 LTS; operator and property identifiers read from the `blender-v5.2-release` source) · Marvelous Designer API · Substance Painter API · UE Python hand-off.

---

## 1. Split: Claude vs human

| Step | Claude | Human |
|---|---|---|
| Pattern drafting, drape art direction, fold placement | – | MD/CLO or sculpt |
| Import body, check scale/pose, report measurements | bpy | – |
| Shrinkwrap/Solidify/cleanup passes, merge by distance, normals | bpy | spot-check |
| Weight transfer + smooth/clean/limit/normalize, per-garment batch | bpy | fix joints |
| Pose test renders (import stroke FBX, screenshot worst frames) | bpy + viewport capture via MCP | judge |
| Body mask: find body faces hidden under the garment, write mask PNG | bpy | paint fixes |
| LOD decimation with protected groups, tri counts | bpy | check silhouette |
| Validation: units, tri budget, influences, non-manifold, UV range, missing vertex groups | bpy | – |
| Export FBX/USD with the correct options, naming | bpy | – |
| Substance export from a preset | Painter Python | painting |
| MD batch import/sim/export | MD Python API (license tier: see below) | design/fit |
| UE import settings, Dataflow graph assembly | UE Python / Editor Utility (`ue5-character-creation-clothing`) | review |

---

## 2. Driving Blender from Claude

| Option | Status (2026-10-09) | License | How |
|---|---|---|---|
| **Blender Lab official MCP** (`projects.blender.org/lab/blender_mcp`, docs `blender.org/lab/mcp-server`) | v1.0.0 27 Apr 2026, v1.0.3 11 Sep 2026; Blender **5.1+** extension `lab_blender_org/mcp` from extensions.blender.org; needs *Allow Online Access*; TCP bridge on `127.0.0.1:9876`; ~26 tools incl. code execution, scene summaries, screenshots | Not fetched (site blocked); Blender extensions are GPL-compatible by policy (verify) | Install the extension, start the bridge, run the MCP server over stdio (`uv tool run --from "git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp" blender-mcp`) |
| **mcp-for-blender** (ahujasid; formerly `blender-mcp`, 30 k stars) | Repo read directly: `pyproject` 2.1.9, add-on 1.8, `"blender": (3, 0, 0)`; last commit 2026-10-06; PyPI `mcp-for-blender` (old `blender-mcp` alias still works) | **MIT** (LICENSE read) | `claude mcp add blender uvx mcp-for-blender`; tools `get_scene_info`, `execute_blender_code`, `look` (viewport), `generate_3d`, `search_assets`, `import_asset`. Set `DISABLE_TELEMETRY=true` (anonymous usage ping is on by default; content telemetry is opt-in) and `BLENDER_MCP_SAFE_MODE=1`. Third-party, "not made by Blender" |
| Vendor bridges that expose a `bl_execute`-style tool | Session-specific | – | Same scripts; check the server's own Z-up/metres conventions |
| Headless `blender -b file.blend --python script.py` | Always available | – | For batch jobs; no viewport feedback |

Pick the official extension on Blender 5.1+; keep mcp-for-blender for 4.x or when the official one is unavailable. Either way the payload is plain `bpy`, so the snippets below apply to all three routes.

---

## 3. Verified bpy snippets (Blender 5.2; identifiers from source)

### 3.1 Transfer weights body → garment, then clean up

```python
import bpy

def transfer_weights(body_name, garment_name, max_dist=0.05, limit=8):
    body = bpy.data.objects[body_name]
    garment = bpy.data.objects[garment_name]
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)                 # source = selected
    garment.select_set(True)
    bpy.context.view_layer.objects.active = garment   # destination = active
    bpy.ops.object.data_transfer(
        data_type='VGROUP_WEIGHTS',
        use_create=True,
        vert_mapping='POLYINTERP_NEAREST',  # Nearest Face Interpolated
        layers_select_src='BONE_DEFORM',    # or 'ALL'
        layers_select_dst='NAME',
        use_object_transform=True,          # global space
        use_max_distance=True, max_distance=max_dist,
        mix_mode='REPLACE', mix_factor=1.0)
    bpy.ops.object.select_all(action='DESELECT')
    garment.select_set(True)
    bpy.context.view_layer.objects.active = garment
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=2, expand=0.0)
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.01, keep_single=True)
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=limit)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    arm = next((m.object for m in body.modifiers if m.type == 'ARMATURE'), None)
    if arm and not any(m.type == 'ARMATURE' for m in garment.modifiers):
        garment.modifiers.new("Armature", 'ARMATURE').object = arm
        garment.parent = arm

for g in ["SM_Shirt", "SM_Waistcoat", "SM_Trousers"]:
    transfer_weights("SK_Body", g)
```

Property names (`data_type`, `vert_mapping`, `layers_select_src/dst`, `use_max_distance`, `max_distance`, `ray_radius`, `islands_precision`, `mix_mode`, `mix_factor`, `use_object_transform`) and enum values (`VGROUP_WEIGHTS`; `TOPOLOGY`/`NEAREST`/`EDGE_NEAREST`/`EDGEINTERP_NEAREST`/`POLY_NEAREST`/`POLYINTERP_NEAREST`/`POLYINTERP_VNORPROJ`; `ACTIVE`/`ALL`/`BONE_SELECT`/`BONE_DEFORM`; `ACTIVE`/`NAME`/`INDEX`; `REPLACE`/`ABOVE_THRESHOLD`/`BELOW_THRESHOLD`/`MIX`/`ADD`/`SUB`/`MUL`) were read from `object_data_transfer.cc` and `rna_modifier.cc`. `vertex_group_smooth(factor, repeat, expand)`, `vertex_group_clean(limit, keep_single)`, `vertex_group_limit_total(limit)` from `object_vgroup.cc`. `group_select_mode` is a runtime enum; `'ALL'` and `'ACTIVE'` are standard, `'BONE_DEFORM'` exists when an armature is present.

### 3.2 Shrinkwrap pass with offset and protected vertex group

```python
def shrinkwrap(garment_name, body_name, offset=0.006, exclude_group=None):
    g = bpy.data.objects[garment_name]
    m = g.modifiers.new("Fit", 'SHRINKWRAP')
    m.target = bpy.data.objects[body_name]
    m.wrap_method = 'NEAREST_SURFACEPOINT'   # or 'PROJECT' for sleeves
    m.wrap_mode = 'OUTSIDE_SURFACE'          # keep outside, push out only
    m.offset = offset                        # metres
    if exclude_group:
        m.vertex_group = exclude_group
        m.invert_vertex_group = True
    bpy.context.view_layer.objects.active = g
    bpy.ops.object.modifier_apply(modifier=m.name)
```

### 3.3 Edge thickness only (Solidify on a vertex group)

```python
def thicken_edges(garment_name, group="Hems", thickness=0.003):
    g = bpy.data.objects[garment_name]
    m = g.modifiers.new("Thick", 'SOLIDIFY')
    m.thickness = thickness; m.offset = -1.0   # grow inward
    m.use_even_offset = True; m.use_rim = True
    m.vertex_group = group; m.thickness_vertex_group = 0.0
    bpy.context.view_layer.objects.active = g
    bpy.ops.object.modifier_apply(modifier=m.name)
```

### 3.4 LOD chain with protected seams

```python
def make_lods(garment_name, ratios=(0.5, 0.25, 0.1), protect="Protect"):
    src = bpy.data.objects[garment_name]
    out = []
    for i, r in enumerate(ratios, start=1):
        lod = src.copy(); lod.data = src.data.copy()
        lod.name = f"{garment_name}_LOD{i}"
        bpy.context.collection.objects.link(lod)
        m = lod.modifiers.new("Decimate", 'DECIMATE')
        m.decimate_type = 'COLLAPSE'; m.ratio = r
        m.use_collapse_triangulate = True; m.use_symmetry = False
        if protect in lod.vertex_groups:
            m.vertex_group = protect; m.invert_vertex_group = True; m.vertex_group_factor = 10.0
        bpy.context.view_layer.objects.active = lod
        bpy.ops.object.modifier_apply(modifier=m.name)   # weights survive
        out.append(lod)
    return out
```

UE reads LODs from one FBX only via the legacy `LOD0/LOD1` group naming or separate imports; the usual route is to import LOD0 and then *Import LOD* per level, or let UE reduce. Keep DCC LODs when the silhouette matters (hero).

### 3.5 Validation report

```python
import bmesh
def validate(garment_name, tri_budget=40000, max_infl=8):
    o = bpy.data.objects[garment_name]; me = o.data
    bm = bmesh.new(); bm.from_mesh(me)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    nonmanifold = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
    ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
    bm.free()
    over = sum(1 for v in me.vertices if len([g for g in v.groups if g.weight > 0.0]) > max_infl)
    unnorm = sum(1 for v in me.vertices if abs(sum(g.weight for g in v.groups) - 1.0) > 0.01)
    dims = o.dimensions   # metres; a shirt ~0.5-0.8 m tall
    uv_out = 0
    if me.uv_layers.active:
        uv_out = sum(1 for l in me.uv_layers.active.data if not (0.0 <= l.uv.x <= 10.0 and 0.0 <= l.uv.y <= 10.0))
    return dict(tris=tris, over_budget=tris > tri_budget, nonmanifold=nonmanifold, ngons=ngons,
                over_influences=over, unnormalized=unnorm, dims_m=tuple(round(d, 3) for d in dims),
                uv_outside_udim_range=uv_out, scale=tuple(o.scale), rot=tuple(o.rotation_euler))
```

### 3.6 Body faces hidden under the garment (mask helper)

```python
from mathutils.bvhtree import BVHTree
def hidden_body_faces(body_name, garment_name, depth=0.012):
    """Select body faces whose centre lies inside/under the garment within `depth` metres."""
    body = bpy.data.objects[body_name]; garment = bpy.data.objects[garment_name]
    dg = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(garment, dg)
    inv = garment.matrix_world.inverted()
    hidden = []
    for p in body.data.polygons:
        c_world = body.matrix_world @ p.center
        n_world = (body.matrix_world.to_3x3() @ p.normal).normalized()
        loc, nrm, idx, dist = bvh.find_nearest(inv @ c_world, depth)
        if loc is not None:
            to_cloth = (garment.matrix_world @ loc) - c_world
            if to_cloth.dot(n_world) > 0:      # cloth is outside the skin here
                hidden.append(p.index)
    for p in body.data.polygons: p.select = p.index in set(hidden)
    return hidden
```

Bake the selection to a black/white UV image (*Bake > Emit* with a per-face material, or paint via `bpy.ops.paint.vertex_color_set` then bake vertex color to the body UVs) and export it as the MetaHuman Body Hidden Face Map. Review visually; the heuristic over-selects at open edges.

### 3.7 Export FBX / USD for UE

```python
def export_fbx(garment_names, armature_name, path):
    bpy.ops.object.select_all(action='DESELECT')
    for n in garment_names: bpy.data.objects[n].select_set(True)
    bpy.data.objects[armature_name].select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=False,            # flagged broken with armatures in the add-on
        use_mesh_modifiers=True, mesh_smooth_type='OFF', use_tspace=True,
        colors_type='SRGB',                    # 'LINEAR' for numeric masks (verify in UE)
        add_leaf_bones=False, use_armature_deform_only=True,
        primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL',
        bake_anim=False, path_mode='COPY', embed_textures=False,
        axis_forward='-Z', axis_up='Y')

def export_usd(path):
    bpy.ops.wm.usd_export(
        filepath=path, selected_objects_only=True,
        export_armatures=True, only_deform_bones=True, export_shapekeys=True,
        export_uvmaps=True, export_normals=True, export_materials=True,
        convert_orientation=True, export_global_forward_selection='X', export_global_up_selection='Z',
        convert_scene_units='CENTIMETERS',     # verify against your UE USD import
        triangulate_meshes=False)
```

Option names were read from `io_scene_fbx/__init__.py` (add-on 5.15.0) and `io_usd.cc` in the 5.2 branch. Defaults to remember: `add_leaf_bones=True`, `mesh_smooth_type='OFF'`, `use_tspace=False`, `colors_type='SRGB'`, `apply_scale_options='FBX_SCALE_NONE'`.

### 3.8 Pose test

Import a stroke animation (`bpy.ops.import_scene.fbx(filepath=..., use_anim=True, automatic_bone_orientation=False)`) onto the body armature, set `scene.frame_set(f)` at the worst frames, and capture the viewport through the MCP (`look` / screenshot tool) or `bpy.ops.render.opengl(write_still=True)`. Compare garment vs body intersections with the BVH helper above (count body faces whose centre is *outside* the garment).

---

## 4. Marvelous Designer API

- Official docs: `developer.marvelousdesigner.com` (Changelog, Environment Setup, API Scenario, API List, ApiTypes, Python API). Runs **inside** MD (Python plug-ins registered in *Plugins > Plug-in Manager*; `.py` on Windows). Documented capabilities: batch import/export (ZPRJ/OBJ/FBX/Alembic), create patterns, run N simulation steps, adjust simulation and fabric properties, read pattern topology. No documented interrupt for a running simulation.
- Tier: coverage at the Linux launch (Sept/Oct 2025) says Enterprise plan only. Community MCP `Laboon2501/MarvelousDesigner-MCP` (MIT) verified on Windows MD 2026.0.315 with Python plug-ins; its latest documented API changelog was 2025.1.201. Whether a Personal subscription exposes the plug-in API is **(verify)** with CLO sales.
- What Claude can do with it: open a project, swap the avatar, run bounded sim steps, export OBJ/FBX/USD with explicit paths and units, read measurements. What it cannot do: draft patterns, judge fit, place folds.
- CLO: GUI tool; its plug-in API also runs in-app (no headless path). ZBrush: ZScript only.

---

## 5. Substance 3D Painter API

In-app Python (`substance_painter` module): `substance_painter.export.export_project_textures(config)` with a JSON export config (preset name, output path, formats, size), plus baking and layer-stack access. Use it to re-export all garments with the ORM + Fuzz output template after changes.

---

## 6. UE hand-off scripts

Import automation (Interchange/FBX import options, skeleton assignment, LOD import, Cloth Asset Dataflow) belongs to the UE side; see `ue5-character-creation-clothing` and `ue5-animation-characters`. Minimal hint: `unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])` with `unreal.FbxImportUI` → `skeletal_mesh_import_data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS`, `import_morph_targets = True`, `ui.skeleton = <body skeleton>`.
