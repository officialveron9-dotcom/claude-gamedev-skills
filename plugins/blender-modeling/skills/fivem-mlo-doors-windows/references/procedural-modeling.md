# Procedural modelling: doors, garage doors, windows, wall openings (bpy)

Read when building an MLO door, double door, garage door, window or wall opening **from scratch** in Blender.
Vanilla props are **reference only**: use them for dimensions, archetype flags/special attribute and behaviour.
Never ship their meshes.

**Status.** Every generator below ran headless on 2026-10-10 with the `bpy` wheels **5.2.2** (Blender 5.2 LTS,
Python 3.13) and **4.2.0** (Blender 4.2 LTS, Python 3.11). Both passed all 51 checks of the test harness at the end
of this file. The Sollumz steps (`sz_*` functions) were **not executed**, because Sollumz cannot load in the bpy
wheel. Their operator ids and property names were read from the Sollumz source (`07d6a49`, 2026-10-10), and each step
is guarded with `hasattr`, so it is skipped without Sollumz.

## Conventions the generators follow

| Item | Convention | Why |
|---|---|---|
| Units / axes | metres; X = width, Y = wall normal (exterior on −Y by default), Z = up | GTA/Blender Z-up |
| Swing door origin | on the **hinge axis**, **mid-height** of the leaf, mid-thickness | official Cfx "hinge point (side center)"; vanilla `v_ilev_247door` entity sits at z = 1.15 (half its height) |
| Swing door axes | leaf extends along local **−X** from the hinge, thickness on Y | matches the vanilla 24/7 layout: both leaves point −X, the left one is rotated 180°. Compare against the template's bounding box (verify) |
| Hinge position | axis inset `gap + t/2` from the jamb, with a half-round **hinge barrel** (radius t/2) | closed gap = `gap` on both edges, and ±90° swing never crosses the jamb (tested) |
| Door bound | one box from the free edge **to the hinge axis** (not past it) | the box corners sweep radius t/2 and never hit the frame (tested) |
| Double door | `<name>_r` hinge on +X, rotation 0; `<name>_l` Y-mirrored model, hinge on −X, rotated 180° | vanilla `v_ilev_247door` / `_r`; mirrored pivots without negative scale |
| Garage door | **one rigid mesh**, panels only as grooves; origin **bottom centre**; mounted on the interior face, overlapping the opening by 5 cm | the door system moves one object; official Cfx origin for Garage Door (5) |
| Window | static frame + mullions object; **separate glass drawable** with two opposite faces 6 mm apart, running 1 cm into the frame | glass needs its own alpha shader/entity; no coplanar faces means no z-fighting (tested) |
| Wall | closed manifold slab with the hole and generated reveal faces (jambs, head, sill) | clean collision source; volume and manifold tested |
| Materials | placeholder slots named `sz_<shader>.<label>` (e.g. `sz_normal_spec.door_leaf`, `sz_glass.window_glass`) | `sz_apply_shaders()` swaps them for real Sollumz shaders |
| UV | `UVMap 0`, world-scale box projection, `meters_per_uv` (default 1 m per UV tile) | Sollumz UV name; the same texel density on every part (tested) |
| Vertex colour | `Color 1`, BYTE_COLOR, face corner, green `(0,1,0,1)` for interior | Sollumz attribute name; Cfx docs: green = interior, red = exterior |
| Hierarchy | `<name>` (empty = Drawable) > `<name>.model` (mesh, identity local) + `<name>.col` (composite) > `<name>.col.box0` (box bound centred on its own origin) | the Sollumz Drawable layout; the drawable origin = pivot |
| LOD | `<name>.model.lod_med` mesh (simple box), assigned to `sz_lods.medium` when Sollumz is loaded | Sollumz LOD slots `very_high/high/medium/low/very_low` |

### Default dimensions (all parameters)

| Element | Defaults | Typical range |
|---|---|---|
| Swing door, clear opening | 0.90 × 2.10 m, leaf 45 mm, gaps 3 mm sides/top, 10 mm floor, frame 60 mm, handle at 1.0 m | 0.8–1.0 × 2.0–2.2 |
| Double door | 1.80 × 2.10 m, 6 mm centre gap | 1.5–2.0 |
| Garage door, clear opening | 2.75 × 2.30 m, slab 45 mm, 4 panels, 50 mm overlap | 2.5–3.0 × 2.2–2.5 (trucks: wider/taller) |
| Window | 1.20 × 1.40 m, sill 0.90 m, frame 60 × 80 mm, 1 vertical mullion, glass 6 mm | |
| Wall | 0.20 m thick | 0.15–0.30 |

### Archetype naming

- `<prefix>_<mlo>_<kind>_<nn>[_l|_r|_glass]`, lowercase `a-z0-9_`. Examples: `vx_bennys_door_01`,
  `vx_bennys_ddoor_01_l` / `_r`, `vx_bennys_gar_01`, `vx_bennys_win_01_glass`. Use a project prefix so names
  never clash with vanilla or other resources (file names must be unique across all running resources).
- Archetype name = Drawable object name = `.ydr` name (= `.ytd` name if not shared). Blender's `.001` suffixes break
  this, so check the names before export.

## Public API

| Function | Returns | ytyp afterwards |
|---|---|---|
| `make_wall_with_opening(name, wall_w, wall_h, wall_t, open_w, open_h, sill, open_x)` | wall object, `["opening"] = (x0, x1, z0, z1)` | shell/static |
| `make_door(name, open_w, open_h, leaf_t, gap, floor_gap, hinge="RIGHT"/"LEFT", ...)` | dict: `drawable, model, composite, bounds, lods, frame, leaf_size, hinge_x, wall_opening` | Special Attribute **7**, Dynamic + Enable Door Physics |
| `make_double_door(name, open_w, ...)` | `{"left", "right", "frame", "wall_opening"}` | 7 on both |
| `make_garage_door(name, open_w, open_h, panels, style="SECTIONAL"/"ROLLER"/"FLAT", inside_dir=+1)` | dict incl. `slab_size, wall_opening` | **5**, Dynamic + Enable Door Physics |
| `make_sliding_door(name, open_w, open_h)` | same, origin at the **bottom corner** | **8** (slide direction: test in game) |
| `make_window(name, open_w, open_h, sill, mullions_v, mullions_h, glass_shader="glass")` | glass asset dict + `["frame"]`, `glass_area, wall_opening` | glass: none (0); frame: static |
| `portal_corners(x0, x1, z0, z1, y, outside_dir=-1)` | 4 corners, vanilla order (c1 bottom-right ... as seen from outside) | Sollumz portal from verts; arrow outward (tested) |
| `attach_to_template_bone(model, armature, bone)` | Copy Transforms constraint | official Cfx template-skeleton path |
| `sz_convert(asset)`, `sz_apply_shaders(obj)`, `sz_add_archetype(drawable, "IS_NORMAL_DOOR")` | Sollumz tagging (guarded; not executed) | |
| `build_demo()` | 4 walls with door, double door, garage, window | |

`wall_opening` is the hole to cut for the part: frame outer size for doors, clear size for windows and garages. Pass
it straight to `make_wall_with_opening` (fit is tested).

## Sollumz integration (names verified in the source, calls not executed)

- Object types: `obj.sollum_type = "sollumz_drawable"` (empty), `"sollumz_drawable_model"` (mesh),
  `"sollumz_bound_composite"` (empty), `"sollumz_bound_box"` (mesh; size and centre come from the object's bbox).
- LODs: `model.sz_lods.high.mesh = model.data`, `.medium/.low/.very_low.mesh = lod_mesh`,
  `model.sz_lods.active_lod_level = "sollumz_high"`.
- Shaders: `bpy.ops.sollumz.createshadermaterial(shader_index=i)` appends a material to every **selected** mesh.
  Find `i` in `window_manager.sz_shader_materials` (item `.name` is the upper-case shader name such as `GLASS`, plus
  `.index`). `bpy.ops.sollumz.change_shader(shader_index=i)` changes the active material (it must already be a
  Sollumz shader).
- Collision material: set `window_manager.sz_collision_material_index` (look it up in `wm.sz_collision_materials` by
  name, e.g. `WOOD_SOLID_MEDIUM`, `METAL_GARAGE_DOOR`, `GLASS_BULLETPROOF`), then
  `bpy.ops.sollumz.clearandcreatecollisionmaterial()` on the selected bounds.
- Bound flags: the UI path `bpy.ops.sollumz.createbound()` (with `scene.create_bound_type`) applies the default flag
  preset. The generators create bounds directly, so **copy `composite_flags1/2` from the imported template's bound**
  (Flags panel) (verify which flags vanilla doors use).
- Archetype: `bpy.ops.sollumz.createytyp()`, then `ytyp = scene.ytyps[scene.ytyp_index]`, `arch = ytyp.new_archetype()`,
  `arch.asset = drawable` (fills asset type and physics dictionary), `arch.special_attribute = "IS_NORMAL_DOOR"`
  (`IS_GARAGE_DOOR`, `IS_SLIDING_DOOR`, ...), `arch.flags.flag18 = True` (Dynamic), `arch.flags.flag27 = True`
  (Enable Door Physics), `arch.lod_dist = 100`.
- Export space: by default Sollumz writes model vertices **relative to the Drawable** (`get_export_transforms_to_apply`).
  So a door may sit at its real place and rotation in the scene, and the entity transform comes from the object.
  **Keep "Apply Parent Transforms" OFF**: when it is on, the Drawable's rotation is baked into the mesh, and the
  180°-rotated left leaf would be exported pointing the wrong way.
- Skeleton: the official Cfx workflow keeps the **template's armature** and adds Copy Transforms to its door bone
  (`attach_to_template_bone`; delete the template mesh). Whether a skeleton-less custom drawable behaves as a door is
  unverified, so test it or use the template armature.

## Workflow

1. In Blender, `exec(open(".../mlo_openings.py").read())`, or run `blender -b file.blend -P mlo_openings.py`.
2. Call the generator with the measured opening, for example `d = make_door("vx_shop_door_01", open_w=0.95)`. Cut
   the wall with `make_wall_with_opening(..., *d["wall_opening"])`, or cut your existing shell to the same size
   (shell workflow: `fivem-mlo-creation`).
3. Move the **drawable** (not the model) into place in the shell. The model keeps an identity local transform.
4. With Sollumz loaded, run `sz_convert(d)`, then `sz_add_archetype(d["drawable"], "IS_NORMAL_DOOR")`. Assign
   textures, export (Gen8 and/or Gen9), and add the door as an MLO entity attached to the doorway portal.
5. Create the portal with `portal_corners(...)` (4 verts, then Sollumz "Create From Verts") and check that the arrow
   points outward.

## Test results (2026-10-10)

`bpy 5.2.2` and `bpy 4.2.0`: **51/51 passed** each. They cover the wall manifold, volume, bbox and reveal faces (door and window);
hierarchy and identity model transform; pivot on the hinge axis at mid-height; the leaf spanning −X; floor/head/jamb
gaps; a ±90° swing of leaf and bound staying 3 mm off the jamb (single right, single left, both double leaves); the
bound ending at the axis; the LOD being simpler; material slot names; frame/garage/window fitting their wall hole;
the double door's mirrored pivots and 6 mm centre gap; the garage being a single rigid mesh with its origin at the
bottom centre behind the wall, plus the roller variant; the sliding door having its origin at the bottom corner while still
covering the opening; glass having 2 opposite faces, no coplanar planes with the
frame, and running 1 cm into it; the portal arrow pointing outward for both exterior sides; UV span = size /
`meters_per_uv`; the template-armature constraint; and the Sollumz guards. Bug found while testing:
`obj.matrix_world` is **stale** after setting `obj.location` until `view_layer.update()`, so the generators read
`matrix_basis` instead (see `blender-python-pitfalls`).

Re-run: `uv venv --python 3.13 venv && uv pip install --python venv/bin/python bpy==5.2.2` (or Python 3.11 + `bpy==4.2.0`), save the two code blocks
as `gen/mlo_openings.py` and `tests/test_generators.py`, then run `venv/bin/python tests/test_generators.py`.

## Generator: save as `mlo_openings.py`

```python
"""MLO door / garage door / window generators for Blender 4.2+ / 5.x (tested headless with bpy 5.2.2).

Pure bpy + bmesh. Sollumz-specific steps live in the `sz_*` functions and are skipped when Sollumz is not
loaded (hasattr checks), so the geometry part also runs in `blender -b` or the `bpy` wheel.
Units: metres. Axes: X = width, Y = wall normal (exterior = -Y by default), Z = up.
"""
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

EPS = 1e-6
INTERIOR_VC = (0.0, 1.0, 0.0, 1.0)   # Cfx docs: vertex colour green = interior, red = exterior


# --------------------------------------------------------------------------- generic helpers
def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def placeholder_material(shader, label, rgba=(0.8, 0.8, 0.8, 1.0)):
    """Material named 'sz_<shader>.<label>'; sz_apply_shaders() swaps it for a real Sollumz shader."""
    name = f"sz_{shader}.{label}"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    return mat


def add_box(bm, mn, mx, mat_index=0):
    """Axis-aligned box from min to max corner, outward normals, given material slot."""
    mn, mx = Vector(mn), Vector(mx)
    size = mx - mn
    assert min(size) > EPS, f"degenerate box {mn} {mx}"
    m = Matrix.LocRotScale((mn + mx) / 2, None, size)
    verts = bmesh.ops.create_cube(bm, size=1.0, matrix=m)["verts"]
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = mat_index


def add_cylinder_z(bm, center, radius, height, segments=12, mat_index=0):
    m = Matrix.Translation(Vector(center))
    verts = bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius,
                                  radius2=radius, depth=height, matrix=m)["verts"]
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = mat_index


def add_quad(bm, corners, mat_index=0):
    """corners in counter-clockwise order seen from the side the normal should face."""
    f = bm.faces.new([bm.verts.new(c) for c in corners])
    f.material_index = mat_index
    return f


def uv_box_project(bm, meters_per_uv=1.0, layer_name="UVMap 0"):
    """World-scale box projection in object space: same texel density on every object."""
    uv = bm.loops.layers.uv.get(layer_name) or bm.loops.layers.uv.new(layer_name)
    bm.normal_update()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        u_i, v_i = {0: (1, 2), 1: (0, 2), 2: (0, 1)}[ax]
        for loop in f.loops:
            co = loop.vert.co
            loop[uv].uv = (co[u_i] / meters_per_uv, co[v_i] / meters_per_uv)


def bm_to_object(bm, name, coll, materials, meters_per_uv=1.0, vertex_color=INTERIOR_VC):
    uv_box_project(bm, meters_per_uv)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mat in materials:
        me.materials.append(mat)
    attr = me.color_attributes.new("Color 1", "BYTE_COLOR", "CORNER")   # Sollumz name for colour set 0
    attr.data.foreach_set("color", list(vertex_color) * len(me.loops))
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    return obj


def lod_mesh_from_boxes(name, boxes, materials):
    """Low-poly LOD mesh datablock (boxes = [(min, max, slot)])."""
    bm = bmesh.new()
    for mn, mx, slot in boxes:
        add_box(bm, mn, mx, slot)
    uv_box_project(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mat in materials:
        me.materials.append(mat)
    attr = me.color_attributes.new("Color 1", "BYTE_COLOR", "CORNER")
    attr.data.foreach_set("color", list(INTERIOR_VC) * len(me.loops))
    me.use_fake_user = True
    return me


def make_asset(name, model_obj, bound_boxes, coll, lods=(), collision_material="WOOD_SOLID_MEDIUM"):
    """Drawable hierarchy (Sollumz layout): <name> (empty) > <name>.model (mesh)
    + <name>.col (composite empty) > <name>.col.box<i> (box bound, centred on its own origin).
    The empty takes the model's transform (pivot); children keep identity local transforms."""
    assert model_obj.parent is None
    drawable = bpy.data.objects.new(name, None)
    coll.objects.link(drawable)
    drawable.matrix_world = model_obj.matrix_basis.copy()   # NOT matrix_world: stale until view_layer.update()
    model_obj.name = f"{name}.model"
    model_obj.parent = drawable
    model_obj.matrix_parent_inverse = Matrix.Identity(4)
    model_obj.matrix_basis = Matrix.Identity(4)
    comp = bpy.data.objects.new(f"{name}.col", None)
    coll.objects.link(comp)
    comp.parent = drawable
    bounds = []
    for i, (mn, mx) in enumerate(bound_boxes):
        mn, mx = Vector(mn), Vector(mx)
        bm = bmesh.new()
        add_box(bm, (mn - mx) / 2, (mx - mn) / 2)
        me = bpy.data.meshes.new(f"{name}.col.box{i}")
        bm.to_mesh(me)
        bm.free()
        b = bpy.data.objects.new(f"{name}.col.box{i}", me)
        coll.objects.link(b)
        b.parent = comp
        b.location = (mn + mx) / 2
        b.display_type = "WIRE"
        bounds.append(b)
    model_obj["sz_lods"] = [m.name for m in lods]          # plain record; Sollumz uses obj.sz_lods
    drawable["sz_collision_material"] = collision_material
    bpy.context.view_layer.update()
    return {"drawable": drawable, "model": model_obj, "composite": comp, "bounds": bounds, "lods": list(lods)}


# --------------------------------------------------------------------------- wall with opening + reveal
def make_wall_with_opening(name="mlo_wall_01", wall_w=4.0, wall_h=3.0, wall_t=0.2,
                           open_w=1.0, open_h=2.1, sill=0.0, open_x=0.0, coll=None,
                           material=None, meters_per_uv=1.0):
    """Closed manifold wall slab with a rectangular opening; the reveal (jambs, head, sill)
    is generated automatically. Origin: wall bottom centre, wall centred on Y=0."""
    coll = coll or bpy.context.scene.collection
    material = material or placeholder_material("normal_spec", "wall")
    x0, x1 = open_x - open_w / 2, open_x + open_w / 2
    z0, z1 = sill, sill + open_h
    assert -wall_w / 2 + EPS < x0 and x1 < wall_w / 2 - EPS, "opening must not touch the wall sides"
    assert -EPS <= z0 and z1 < wall_h - EPS, "opening must stay below the wall top"
    xs = sorted({-wall_w / 2, x0, x1, wall_w / 2})
    zs = sorted({0.0, z0, z1, wall_h})
    ix0, ix1, iz0, iz1 = xs.index(x0), xs.index(x1), zs.index(z0), zs.index(z1)
    bm = bmesh.new()
    vf = {(i, j): bm.verts.new((x, -wall_t / 2, z)) for i, x in enumerate(xs) for j, z in enumerate(zs)}
    vb = {(i, j): bm.verts.new((x, wall_t / 2, z)) for i, x in enumerate(xs) for j, z in enumerate(zs)}
    front = []
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            if ix0 <= i < ix1 and iz0 <= j < iz1:
                continue                                   # the hole
            front.append(bm.faces.new((vf[i, j], vf[i + 1, j], vf[i + 1, j + 1], vf[i, j + 1])))   # normal -Y
            bm.faces.new((vb[i, j + 1], vb[i + 1, j + 1], vb[i + 1, j], vb[i, j]))                  # normal +Y
    # every front boundary edge becomes a rim face (outer sides) or a reveal face (opening)
    lookup = {v: k for k, v in vf.items()}
    for e in [e for e in bm.edges if len(e.link_faces) == 1 and all(v in lookup for v in e.verts)]:
        a, b = e.verts
        bm.faces.new((a, b, vb[lookup[b]], vb[lookup[a]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = bm_to_object(bm, name, coll, [material], meters_per_uv)
    obj["opening"] = (x0, x1, z0, z1)
    return obj


# --------------------------------------------------------------------------- swing doors
def _leaf_geometry(bm, w, h, t, handle_h, slot_leaf=0, slot_handle=1, mirror_y=False):
    """Leaf in local space: hinge axis = local Z through origin, leaf along -X, thickness on Y,
    origin at mid-height of the hinge edge (vanilla door origin height = half the leaf)."""
    add_box(bm, (-w, -t / 2, -h / 2), (0.0, t / 2, h / 2), slot_leaf)
    add_cylinder_z(bm, (0.0, 0.0, 0.0), t / 2, h, 12, slot_leaf)      # hinge barrel: tight gap, full swing
    hz = handle_h - h / 2
    hx = -w + 0.07
    for side in (-1, 1):                                               # handle placeholder on both faces
        y_in = side * (t / 2 - 0.001)
        y_out = side * (t / 2 + 0.06)
        add_box(bm, (hx - 0.06, min(y_in, y_out), hz - 0.015), (hx + 0.06, max(y_in, y_out), hz + 0.015), slot_handle)
    if mirror_y:
        bmesh.ops.scale(bm, vec=(1, -1, 1), verts=bm.verts)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)


def make_door(name="mlo_door_01", open_w=0.9, open_h=2.1, leaf_t=0.045, gap=0.003, floor_gap=0.01,
              hinge="RIGHT", wall_t=0.2, frame_w=0.06, handle_h=1.0, coll=None, mirror_y=False,
              leaf_w=None, hinge_x=None, with_frame=True, meters_per_uv=1.0,
              collision_material="WOOD_SOLID_MEDIUM"):
    """Single swing door (+ static frame) for a clear opening open_w x open_h (frame inner size).
    hinge='RIGHT': hinge on the +X jamb, leaf points -X, rotation 0.
    hinge='LEFT' : hinge on the -X jamb, object rotated 180 deg about Z (vanilla v_ilev_247door layout).
    ytyp: Special Attribute 7 (Normal Door), flags Dynamic + Enable Door Physics."""
    coll = coll or get_collection(name)
    w = leaf_w if leaf_w is not None else open_w - 2 * gap - leaf_t / 2   # `gap` at both jambs
    h = open_h - gap - floor_gap
    mats = [placeholder_material("normal_spec", "door_leaf", (0.45, 0.3, 0.2, 1)),
            placeholder_material("normal_spec", "door_handle", (0.7, 0.7, 0.7, 1))]
    bm = bmesh.new()
    _leaf_geometry(bm, w, h, leaf_t, handle_h - floor_gap, 0, 1, mirror_y)
    model = bm_to_object(bm, f"{name}.tmp", coll, mats, meters_per_uv)
    sign = 1 if hinge == "RIGHT" else -1
    if hinge_x is None:
        hinge_x = sign * (open_w / 2 - gap - leaf_t / 2)   # barrel (radius t/2) stays `gap` off the jamb
    model.matrix_world = Matrix.LocRotScale((hinge_x, 0.0, floor_gap + h / 2),
                                            None if sign == 1 else Matrix.Rotation(math.pi, 3, "Z"), None)
    lod = lod_mesh_from_boxes(f"{name}.model.lod_med",
                              [((-w, -leaf_t / 2, -h / 2), (0, leaf_t / 2, h / 2), 0)], mats[:1])
    # the bound ends AT the hinge axis: its corners sweep radius t/2 and never cross the jamb plane
    door = make_asset(name, model, [((-w, -leaf_t / 2, -h / 2), (0.0, leaf_t / 2, h / 2))], coll, [lod],
                      collision_material)
    door["frame"] = make_frame(f"{name}_frame", open_w, open_h, wall_t, frame_w, coll=coll,
                               meters_per_uv=meters_per_uv) if with_frame else None
    door["leaf_size"] = (w, leaf_t, h)
    door["hinge_x"] = hinge_x
    door["wall_opening"] = (open_w + 2 * frame_w, open_h + frame_w, 0.0)   # hole for make_wall_with_opening
    return door


def make_frame(name, open_w, open_h, wall_t, frame_w=0.06, sill_h=0.0, has_sill=False, coll=None,
               meters_per_uv=1.0, material=None):
    """Static frame lining the reveal; inner edge = clear opening. Origin: opening bottom centre."""
    coll = coll or bpy.context.scene.collection
    material = material or placeholder_material("normal_spec", "frame", (0.9, 0.9, 0.9, 1))
    d = wall_t / 2 + 0.01                                   # 1 cm proud of each wall face (casing)
    x0, x1, z0, z1 = -open_w / 2, open_w / 2, sill_h, sill_h + open_h
    bm = bmesh.new()
    add_box(bm, (x0 - frame_w, -d, z0), (x0, d, z1 + frame_w))       # left jamb
    add_box(bm, (x1, -d, z0), (x1 + frame_w, d, z1 + frame_w))       # right jamb
    add_box(bm, (x0, -d, z1), (x1, d, z1 + frame_w))                 # head
    if has_sill:
        add_box(bm, (x0, -d, z0 - frame_w), (x1, d, z0))             # sill
    return bm_to_object(bm, name, coll, [material], meters_per_uv)


def make_double_door(name="mlo_ddoor_01", open_w=1.8, open_h=2.1, leaf_t=0.045, gap=0.003,
                     floor_gap=0.01, wall_t=0.2, coll=None, **kw):
    """Two leaves with mirrored pivots (vanilla v_ilev_247door / _r layout):
    <name>_r: hinge on the +X jamb, rotation 0; <name>_l: Y-mirrored model, hinge on the -X jamb, rotated 180.
    Gaps: `gap` at each jamb, 2*gap in the middle. One shared static frame."""
    coll = coll or get_collection(name)
    leaf_w = open_w / 2 - 2 * gap - leaf_t / 2
    hx = open_w / 2 - gap - leaf_t / 2
    common = dict(open_w=open_w, open_h=open_h, leaf_t=leaf_t, gap=gap, floor_gap=floor_gap, wall_t=wall_t,
                  coll=coll, leaf_w=leaf_w, with_frame=False, **kw)
    right = make_door(f"{name}_r", hinge="RIGHT", hinge_x=hx, **common)
    left = make_door(f"{name}_l", hinge="LEFT", hinge_x=-hx, mirror_y=True, **common)
    frame = make_frame(f"{name}_frame", open_w, open_h, wall_t, coll=coll)
    return {"left": left, "right": right, "frame": frame, "wall_opening": (open_w + 2 * 0.06, open_h + 0.06, 0.0)}


# --------------------------------------------------------------------------- garage door
def make_garage_door(name="mlo_garage_01", open_w=2.75, open_h=2.3, slab_t=0.045, overlap=0.05,
                     wall_t=0.2, panels=4, style="SECTIONAL", coll=None, meters_per_uv=1.0,
                     collision_material="METAL_GARAGE_DOOR", inside_dir=1, origin="BOTTOM_CENTER"):
    """Rigid slab for Special Attribute 5 (Garage Door). The door system moves the whole object, so panels are
    only visual grooves in ONE mesh. Origin = bottom centre (official Cfx guide), width on X, thickness on Y.
    Mounted on the interior face (inside_dir=+1 -> +Y side), overlapping the opening by `overlap`."""
    coll = coll or get_collection(name)
    w, h = open_w + 2 * overlap, open_h + overlap
    mats = [placeholder_material("normal_spec", "garage_panel", (0.75, 0.75, 0.78, 1))]
    bm = bmesh.new()
    if style == "SECTIONAL":
        ph, groove = h / panels, 0.012
        for i in range(panels):                                  # panels touch via thinner groove strips
            z0 = i * ph + (groove / 2 if i else 0)
            z1 = (i + 1) * ph - (groove / 2 if i < panels - 1 else 0)
            add_box(bm, (-w / 2, -slab_t / 2, z0), (w / 2, slab_t / 2, z1))
            if i < panels - 1:
                add_box(bm, (-w / 2, -slab_t * 0.3, z1), (w / 2, slab_t * 0.3, z1 + groove))
    elif style == "FLAT":
        add_box(bm, (-w / 2, -slab_t / 2, 0.0), (w / 2, slab_t / 2, h))
    else:                                                        # "ROLLER": corrugated slats
        n = max(4, int(h / 0.08))
        sh = h / n
        for i in range(n):
            tt = slab_t if i % 2 == 0 else slab_t * 0.6
            add_box(bm, (-w / 2, -tt / 2, i * sh), (w / 2, tt / 2, (i + 1) * sh))
    x0 = -w / 2
    if origin == "BOTTOM_CORNER":                                # sliding door/gate (attribute 8)
        bmesh.ops.translate(bm, vec=(w / 2, 0.0, 0.0), verts=bm.verts)
        x0 = 0.0
    model = bm_to_object(bm, f"{name}.tmp", coll, mats, meters_per_uv)
    model.location = (-w / 2 - x0, inside_dir * (wall_t / 2 + 0.02 + slab_t / 2), 0.0)
    lod = lod_mesh_from_boxes(f"{name}.model.lod_med", [((x0, -slab_t / 2, 0), (x0 + w, slab_t / 2, h), 0)], mats)
    gd = make_asset(name, model, [((x0, -slab_t / 2, 0.0), (x0 + w, slab_t / 2, h))], coll, [lod],
                    collision_material)
    gd["slab_size"] = (w, slab_t, h)
    gd["wall_opening"] = (open_w, open_h, 0.0)
    return gd


def make_sliding_door(name="mlo_slide_01", open_w=3.0, open_h=2.2, **kw):
    """Sliding door/gate panel: Special Attribute 8 (Sliding Door), origin at the bottom corner (official Cfx).
    The slide direction is engine-defined: test in game and rotate the drawable 180 deg if it slides the wrong way."""
    kw.setdefault("style", "FLAT")
    kw.setdefault("collision_material", "METAL_SOLID_MEDIUM")
    return make_garage_door(name, open_w=open_w, open_h=open_h, origin="BOTTOM_CORNER", **kw)


# --------------------------------------------------------------------------- window
def make_window(name="mlo_win_01", open_w=1.2, open_h=1.4, sill=0.9, wall_t=0.2, frame_w=0.06,
                frame_d=0.08, mullions_v=1, mullions_h=0, mullion_w=0.04, glass_t=0.006, coll=None,
                glass_shader="glass", meters_per_uv=1.0, collision_material="GLASS_BULLETPROOF"):
    """Frame + mullions (one static object) and a separate double-faced glass drawable.
    Origin of both: opening centre (x=0, y=0, z=sill+open_h/2)."""
    coll = coll or get_collection(name)
    cz = sill + open_h / 2
    fmat = placeholder_material("normal_spec", "window_frame", (0.95, 0.95, 0.95, 1))
    gmat = placeholder_material(glass_shader, "window_glass", (0.6, 0.8, 0.9, 0.3))
    iw, ih = open_w - 2 * frame_w, open_h - 2 * frame_w           # glazed area
    bm = bmesh.new()
    hx, hz, fd = open_w / 2, open_h / 2, frame_d / 2
    add_box(bm, (-hx, -fd, -hz), (-hx + frame_w, fd, hz))
    add_box(bm, (hx - frame_w, -fd, -hz), (hx, fd, hz))
    add_box(bm, (-hx + frame_w, -fd, hz - frame_w), (hx - frame_w, fd, hz))
    add_box(bm, (-hx + frame_w, -fd, -hz), (hx - frame_w, fd, -hz + frame_w))
    md = frame_d * 0.75 / 2
    for i in range(1, mullions_v + 1):
        x = -iw / 2 + i * iw / (mullions_v + 1)
        add_box(bm, (x - mullion_w / 2, -md, -ih / 2), (x + mullion_w / 2, md, ih / 2))
    for j in range(1, mullions_h + 1):
        z = -ih / 2 + j * ih / (mullions_h + 1)
        add_box(bm, (-iw / 2, -md, z - mullion_w / 2), (iw / 2, md, z + mullion_w / 2))
    frame = bm_to_object(bm, f"{name}_frame", coll, [fmat], meters_per_uv)
    frame.location = (0, 0, cz)
    # glass: two opposite faces, glass_t apart, 1 cm into the frame (no coplanar faces with the frame)
    gx, gz, gy = iw / 2 + 0.01, ih / 2 + 0.01, glass_t / 2
    bm = bmesh.new()
    add_quad(bm, [(-gx, -gy, -gz), (gx, -gy, -gz), (gx, -gy, gz), (-gx, -gy, gz)])    # faces -Y (exterior)
    add_quad(bm, [(gx, gy, -gz), (-gx, gy, -gz), (-gx, gy, gz), (gx, gy, gz)])        # faces +Y (interior)
    glass = bm_to_object(bm, f"{name}_glass.tmp", coll, [gmat], meters_per_uv)
    glass.location = (0, 0, cz)
    win = make_asset(f"{name}_glass", glass, [((-iw / 2, -0.01, -ih / 2), (iw / 2, 0.01, ih / 2))], coll, [],
                     collision_material)
    win["frame"] = frame
    win["glass_area"] = (iw, ih)
    win["wall_opening"] = (open_w, open_h, sill)
    return win


def portal_corners(x0, x1, z0, z1, y, outside_dir=-1):
    """Portal corners for a room->limbo portal at plane Y=y, ordered like vanilla v_int_66:
    c1 bottom-right, c2 top-right, c3 top-left, c4 bottom-left AS SEEN FROM OUTSIDE.
    Sollumz arrow = -(c3-c1)x(c2-c1) then points to the outside (room -> limbo)."""
    right, left = (x1, x0) if outside_dir < 0 else (x0, x1)
    return [Vector((right, y, z0)), Vector((right, y, z1)), Vector((left, y, z1)), Vector((left, y, z0))]


# --------------------------------------------------------------------------- template armature (official path)
def attach_to_template_bone(model_obj, armature_obj, bone_name):
    """Cfx Part 8: parent the new mesh to the template's armature and add Copy Transforms to its door bone."""
    model_obj.parent = armature_obj
    model_obj.matrix_parent_inverse = Matrix.Identity(4)
    c = model_obj.constraints.new("COPY_TRANSFORMS")
    c.target = armature_obj
    c.subtarget = bone_name
    return c


# --------------------------------------------------------------------------- Sollumz conversion (guarded)
def sollumz_loaded():
    return hasattr(bpy.types.Object, "sollum_type") and hasattr(bpy.ops, "sollumz")


def _select_only(obj):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def sz_apply_shaders(obj):
    """Replace every 'sz_<shader>.<label>' slot with a real Sollumz shader material."""
    wm = bpy.context.window_manager
    if not sollumz_loaded() or not hasattr(wm, "sz_shader_materials"):
        print(f"[skip] Sollumz not loaded: shaders for {obj.name} stay placeholders")
        return False
    index = {item.name: item.index for item in wm.sz_shader_materials}     # e.g. 'GLASS', 'NORMAL_SPEC'
    me = obj.data
    for slot, mat in enumerate(list(me.materials)):
        if not mat or not mat.name.startswith("sz_"):
            continue
        shader, label = mat.name[3:].split(".", 1)
        idx = index.get(shader.upper())
        if idx is None:
            print(f"[warn] unknown Sollumz shader '{shader}'")
            continue
        _select_only(obj)
        bpy.ops.sollumz.createshadermaterial(shader_index=idx)            # appends a new material
        new = me.materials[len(me.materials) - 1]
        new.name = label
        me.materials[slot] = new
        me.materials.pop(index=len(me.materials) - 1)
    return True


def sz_convert(asset):
    """Tag the plain hierarchy with Sollumz types, set LODs, collision material."""
    if not sollumz_loaded():
        print(f"[skip] Sollumz not loaded: {asset['drawable'].name} left as plain objects")
        return False
    asset["drawable"].sollum_type = "sollumz_drawable"
    model = asset["model"]
    model.sollum_type = "sollumz_drawable_model"
    model.sz_lods.high.mesh = model.data
    for lvl, me in zip(("medium", "low", "very_low"), asset["lods"]):
        getattr(model.sz_lods, lvl).mesh = me
    model.sz_lods.active_lod_level = "sollumz_high"
    sz_apply_shaders(model)
    asset["composite"].sollum_type = "sollumz_bound_composite"
    wm = bpy.context.window_manager
    col_index = {item.name: item.index for item in getattr(wm, "sz_collision_materials", [])}
    for b in asset["bounds"]:
        b.sollum_type = "sollumz_bound_box"
        name = asset["drawable"].get("sz_collision_material", "DEFAULT")
        if name in col_index:
            wm.sz_collision_material_index = col_index[name]
            _select_only(b)
            bpy.ops.sollumz.clearandcreatecollisionmaterial()
    print("[todo] copy composite flags from the imported template bound (Sollumz Flags panel) - verify")
    return True


def sz_add_archetype(drawable, special_attribute="IS_NORMAL_DOOR", lod_dist=100.0, dynamic=True,
                     door_physics=True, ytyp_name="mlo_doors"):
    """special_attribute: IS_NORMAL_DOOR (7), IS_GARAGE_DOOR (5), IS_SLIDING_DOOR (8), NOTHING_SPECIAL (glass)."""
    scene = bpy.context.scene
    if not sollumz_loaded() or not hasattr(scene, "ytyps"):
        print("[skip] Sollumz not loaded: create the archetype in the YTYP panel")
        return None
    if len(scene.ytyps) == 0:
        bpy.ops.sollumz.createytyp()
        scene.ytyps[scene.ytyp_index].name = ytyp_name
    ytyp = scene.ytyps[scene.ytyp_index]
    arch = ytyp.new_archetype()
    arch.name = drawable.name
    arch.asset = drawable              # Sollumz fills asset type / physics dictionary
    arch.special_attribute = special_attribute
    arch.lod_dist = lod_dist
    arch.flags.flag18 = dynamic        # Dynamic (131072)
    arch.flags.flag27 = door_physics   # Enable Door Physics (67108864)
    arch.flags.flag6 = False           # never Static (32) on a moving door
    return arch


# --------------------------------------------------------------------------- demo
def build_demo():
    """One wall per element; run with: blender -b -P mlo_openings.py (or exec in the Text Editor)."""
    specs = [
        ("demo_door", lambda c: make_door("vx_demo_door_01", coll=c), 0.0),
        ("demo_ddoor", lambda c: make_double_door("vx_demo_ddoor_01", coll=c), 4.0),
        ("demo_garage", lambda c: make_garage_door("vx_demo_gar_01", coll=c), 8.0),
        ("demo_window", lambda c: make_window("vx_demo_win_01", coll=c), 12.0),
    ]
    for cname, fn, x in specs:
        c = get_collection(cname)
        a = fn(c)
        ow, oh, sill = a["wall_opening"]
        wall = make_wall_with_opening(f"{cname}_wall", max(3.6, ow + 1.0), max(3.0, oh + 0.6), 0.2, ow, oh, sill, coll=c)
        for o in c.objects:
            if o.parent is None:
                o.location.x += x
    bpy.context.view_layer.update()


if __name__ == "__main__":
    build_demo()
```

## Test harness: save as `tests/test_generators.py`

```python
"""Headless tests for mlo_openings.py (run: venv/bin/python tests/test_generators.py)."""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gen"))
import mlo_openings as G  # noqa: E402

TOL = 1e-4
results = []


def check(cond, msg):
    results.append((bool(cond), msg))
    print(("PASS " if cond else "FAIL ") + msg)


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def world_verts(obj):
    bpy.context.view_layer.update()
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def bbox(points):
    xs, ys, zs = zip(*points)
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def signed_volume(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    vol = sum(f.verts[0].co.dot(f.verts[1].co.cross(f.verts[2].co)) for f in bm.faces) / 6.0
    manifold = all(len(e.link_faces) == 2 for e in bm.edges)
    bm.free()
    return vol, manifold


def test_walls():
    fresh()
    w = G.make_wall_with_opening("t_wall_door", 4.0, 3.0, 0.2, 1.0, 2.1, sill=0.0)
    vol, man = signed_volume(w)
    check(man, "door wall is a closed manifold")
    check(abs(vol - (4 * 3 * 0.2 - 1.0 * 2.1 * 0.2)) < TOL, f"door wall volume {vol:.4f} = slab - opening (outward normals)")
    mn, mx = bbox(world_verts(w))
    check((mx - mn - Vector((4, 0.2, 3))).length < TOL, "door wall bbox 4 x 0.2 x 3")
    jambs = [p for p in w.data.polygons if abs(abs(p.normal.x) - 1) < TOL and abs(abs(p.center.x) - 0.5) < TOL]
    check(len(jambs) == 2, "two jamb reveal faces at x = +-0.5")
    heads = [p for p in w.data.polygons if p.normal.z < -0.99 and abs(p.center.z - 2.1) < TOL]
    check(len(heads) == 1, "head reveal face at z = 2.1 facing down")
    check("UVMap 0" in w.data.uv_layers and "Color 1" in w.data.color_attributes, "UVMap 0 + Color 1 present")

    fresh()
    w = G.make_wall_with_opening("t_wall_win", 3.0, 2.8, 0.25, 1.2, 1.4, sill=0.9, open_x=0.3)
    vol, man = signed_volume(w)
    check(man and abs(vol - (3 * 2.8 * 0.25 - 1.2 * 1.4 * 0.25)) < TOL, f"window wall manifold, volume {vol:.4f}")
    sills = [p for p in w.data.polygons if p.normal.z > 0.99 and abs(p.center.z - 0.9) < TOL]
    check(len(sills) == 1 and abs(sills[0].center.x - 0.3) < TOL, "sill reveal face at z = 0.9 under the offset opening")


def swing_check(door, open_w, gap):
    """Rotate the leaf mesh and bound about the local Z axis; nothing may cross the jamb on the hinge side."""
    d = door["drawable"]
    pts = [v.co.copy() for v in door["model"].data.vertices]
    b = door["bounds"][0]
    pts += [b.matrix_basis @ v.co for v in b.data.vertices]          # bound in drawable space (composite at 0)
    hinge_side = 1 if d.matrix_world.translation.x > 0 else -1
    worst = -1e9
    depth = 0.2 / 2 + 0.01                                           # frame jamb spans |y| <= wall_t/2 + 1 cm
    for deg in range(-90, 91, 5):
        r = Matrix.Rotation(math.radians(deg), 4, "Z")
        for p in pts:
            q = d.matrix_world @ (r @ p)
            if abs(q.y) <= depth:                                    # only points that can touch the jamb
                worst = max(worst, hinge_side * q.x)
    return worst, open_w / 2


def test_single_door():
    fresh()
    gap, ow, oh, t = 0.003, 0.9, 2.1, 0.045
    door = G.make_door("t_door", open_w=ow, open_h=oh, leaf_t=t, gap=gap, floor_gap=0.01)
    d = door["drawable"]
    check(d.type == "EMPTY" and door["model"].parent == d and door["composite"].parent == d,
          "hierarchy: drawable empty > model + composite")
    check(door["model"].matrix_basis == Matrix.Identity(4), "model has identity local transform (pivot = drawable origin)")
    exp = Vector((ow / 2 - gap - t / 2, 0.0, 0.01 + (oh - gap - 0.01) / 2))
    check((d.matrix_world.translation - exp).length < TOL, f"pivot on hinge axis, mid-height {tuple(round(c, 4) for c in d.matrix_world.translation)}")
    w, _, h = door["leaf_size"]
    mn, mx = bbox([v.co for v in door["model"].data.vertices])
    check(abs(mn.x + w) < TOL and abs(mx.x - t / 2) < TOL, "leaf spans local -X from hinge (barrel to +t/2)")
    check(abs(mn.z + h / 2) < TOL and abs(mx.z - h / 2) < TOL, "leaf vertically centred on origin")
    wmn, wmx = bbox(world_verts(door["model"]))
    check(abs(wmn.z - 0.01) < TOL and abs(wmx.z - (oh - gap)) < TOL, "floor gap 10 mm, head gap 3 mm")
    check(abs(wmn.x - (-ow / 2 + gap)) < TOL, "free edge keeps 3 mm to the far jamb when closed")
    worst, jamb = swing_check(door, ow, gap)
    check(worst <= jamb - gap + TOL, f"swing -90..90 deg: leaf+bound stay {jamb - worst:.4f} m inside the hinge jamb")
    b = door["bounds"][0]
    bmn, bmx = bbox([b.matrix_basis @ v.co for v in b.data.vertices])
    check(abs(bmx.x) < TOL and abs(bmn.x + w) < TOL, "bound box ends at the hinge axis")
    check(len(door["lods"]) == 1 and len(door["lods"][0].vertices) < len(door["model"].data.vertices), "LOD mesh simpler")
    names = [m.name for m in door["model"].data.materials]
    check(names == ["sz_normal_spec.door_leaf", "sz_normal_spec.door_handle"], f"material slots {names}")
    fr = door["frame"]
    fmn, fmx = bbox(world_verts(fr))
    check(abs(fmx.x - (ow / 2 + 0.06)) < TOL and abs(fmx.z - (oh + 0.06)) < TOL, "frame lines the opening")
    # left-hinged variant
    fresh()
    door = G.make_door("t_door_l", open_w=ow, open_h=oh, hinge="LEFT")
    d = door["drawable"]
    check(abs(d.matrix_world.translation.x + (ow / 2 - gap - t / 2)) < TOL and abs(abs(d.matrix_world.to_euler().z) - math.pi) < 1e-3,
          "LEFT hinge: pivot on -X jamb, rotated 180 deg")
    worst, jamb = swing_check(door, ow, gap)
    check(worst <= jamb - gap + TOL, "LEFT hinge swing clears the jamb")


def test_double_door():
    fresh()
    ow, gap, t = 1.8, 0.003, 0.045
    dd = G.make_double_door("t_dd", open_w=ow, open_h=2.1, leaf_t=t, gap=gap)
    r, l = dd["right"]["drawable"], dd["left"]["drawable"]
    check(abs(r.matrix_world.translation.x + l.matrix_world.translation.x) < TOL, "pivots mirrored about x = 0")
    rmn, _ = bbox(world_verts(dd["right"]["model"]))
    _, lmx = bbox(world_verts(dd["left"]["model"]))
    check(abs((rmn.x - lmx.x) - 2 * gap) < TOL, f"centre gap {rmn.x - lmx.x:.4f} m = 2 x gap")
    for side in ("left", "right"):
        worst, jamb = swing_check(dd[side], ow, gap)
        check(worst <= jamb - gap + TOL, f"{side} leaf swing clears its jamb")
    objs = [o.name for o in bpy.data.collections["t_dd"].objects]
    check(sorted(objs) == sorted(["t_dd_r", "t_dd_r.model", "t_dd_r.col", "t_dd_r.col.box0",
                                  "t_dd_l", "t_dd_l.model", "t_dd_l.col", "t_dd_l.col.box0", "t_dd_frame"]),
          f"double door object names {sorted(objs)}")


def test_garage():
    fresh()
    gd = G.make_garage_door("t_gar", open_w=2.75, open_h=2.3, wall_t=0.2, panels=4)
    d = gd["drawable"]
    w, t, h = gd["slab_size"]
    mn, mx = bbox([v.co for v in gd["model"].data.vertices])
    check(abs(mn.x + w / 2) < TOL and abs(mx.x - w / 2) < TOL and abs(mn.z) < TOL and abs(mx.z - h) < TOL,
          f"slab {w:.2f} x {h:.2f}, origin bottom centre")
    check(abs(d.matrix_world.translation.y - (0.1 + 0.02 + t / 2)) < TOL and abs(d.matrix_world.translation.z) < TOL,
          "mounted on the interior face, origin at floor")
    check(len([o for o in bpy.data.collections["t_gar"].objects if o.type == "MESH" and o.parent == d]) == 1,
          "one rigid mesh (door system moves one object)")
    check(gd["drawable"]["sz_collision_material"] == "METAL_GARAGE_DOOR", "collision material METAL_GARAGE_DOOR")
    fresh()
    sl = G.make_sliding_door("t_slide", open_w=3.0, open_h=2.2)
    smn, smx = bbox([v.co for v in sl["model"].data.vertices])
    w2 = sl["slab_size"][0]
    check(abs(smn.x) < TOL and abs(smx.x - w2) < TOL and abs(smn.z) < TOL, "sliding door: origin at bottom corner")
    wmn, wmx = bbox(world_verts(sl["model"]))
    check(abs(wmn.x + w2 / 2) < TOL and abs(wmx.x - w2 / 2) < TOL, "sliding door still covers the opening")
    fresh()
    rl = G.make_garage_door("t_roll", style="ROLLER")
    mn, mx = bbox([v.co for v in rl["model"].data.vertices])
    check(abs(mn.z) < TOL and mx.z > 2.3, "roller variant builds")


def test_window():
    fresh()
    win = G.make_window("t_win", open_w=1.2, open_h=1.4, sill=0.9, mullions_v=1, mullions_h=1)
    glass = win["model"]
    check(len(glass.data.polygons) == 2, "glass = 2 faces")
    ns = sorted(round(p.normal.y) for p in glass.data.polygons)
    check(ns == [-1, 1], "glass faces point -Y and +Y (visible from both sides)")
    gys = {round(v.co.y, 5) for v in glass.data.vertices}
    fys = {round(v.co.y, 5) for v in win["frame"].data.vertices}
    check(not (gys & fys), f"no glass plane coplanar with frame faces (glass y {sorted(gys)})")
    check(glass.data.materials[0].name == "sz_glass.window_glass", "glass has its own glass material slot")
    gmn, gmx = bbox(world_verts(glass))
    iw, ih = win["glass_area"]
    check(abs((gmx.x - gmn.x) - (iw + 0.02)) < TOL, "glass runs 1 cm into the frame on each side")
    check(abs(win["drawable"].matrix_world.translation.z - (0.9 + 0.7)) < TOL, "glass origin at opening centre")
    check(win["drawable"]["sz_collision_material"] == "GLASS_BULLETPROOF", "glass bound material GLASS_BULLETPROOF")


def test_portal_and_uv():
    for outside in (-1, 1):
        c = G.portal_corners(-0.6, 0.6, 0.9, 2.3, -0.17 * outside * -1, outside_dir=outside)
        n = -(c[2] - c[0]).cross(c[1] - c[0])
        check(n.normalized().y * outside > 0.99, f"portal arrow points to the outside (outside_dir={outside})")
    fresh()
    door = G.make_door("t_uv", open_w=1.0, open_h=2.1, meters_per_uv=0.5)
    me = door["model"].data
    uv = me.uv_layers["UVMap 0"].data
    face = max(me.polygons, key=lambda p: p.area if abs(p.normal.y) > 0.99 else 0)
    us = [uv[i].uv.x for i in face.loop_indices]
    width = max(v.co.x for v in (me.vertices[i] for i in face.vertices)) - min(v.co.x for v in (me.vertices[i] for i in face.vertices))
    check(abs((max(us) - min(us)) - width / 0.5) < TOL, "UV span = size / meters_per_uv (constant texel density)")


def test_template_and_sollumz_guards():
    fresh()
    door = G.make_door("t_tpl")
    arm_data = bpy.data.armatures.new("tpl")
    arm = bpy.data.objects.new("v_template_door", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    c = G.attach_to_template_bone(door["model"], arm, "door_bone")
    check(c.type == "COPY_TRANSFORMS" and door["model"].parent == arm, "template armature + Copy Transforms")
    check(G.sollumz_loaded() is False, "Sollumz not loaded headless -> guarded path")
    check(G.sz_convert(door) is False and G.sz_add_archetype(door["drawable"]) is None, "Sollumz steps skip cleanly")


def test_wall_fit():
    for make, kw in ((G.make_door, {}), (G.make_window, {}), (G.make_garage_door, {})):
        fresh()
        a = make(f"t_fit_{make.__name__}", **kw)
        ow, oh, sill = a["wall_opening"]
        wall = G.make_wall_with_opening("t_fit_wall", ow + 2.0, oh + 1.0, 0.2, ow, oh, sill)
        x0, x1, z0, z1 = wall["opening"]
        part = a.get("frame") or a["model"]
        mn, mx = bbox(world_verts(part))
        if make is G.make_garage_door:
            ok = mn.x < x0 and mx.x > x1 and mn.y > 0.1           # slab overlaps the hole, behind the wall
        else:
            ok = abs(mn.x - x0) < TOL and abs(mx.x - x1) < TOL and abs(mx.z - z1) < TOL
        check(ok, f"{make.__name__}: wall hole {x1 - x0:.3f} x {z1 - z0:.3f} fits the part")
    fresh()
    G.build_demo()
    check(len([o for o in bpy.data.objects if o.name.endswith("_wall")]) == 4, "build_demo creates 4 walls")


if __name__ == "__main__":
    print("bpy", bpy.app.version_string)
    for fn in (test_walls, test_single_door, test_double_door, test_garage, test_window, test_portal_and_uv,
               test_template_and_sollumz_guards, test_wall_fit):
        try:
            fn()
        except Exception as e:  # report and continue
            import traceback
            traceback.print_exc()
            results.append((False, f"{fn.__name__} raised {e!r}"))
    failed = [m for ok, m in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)
```
