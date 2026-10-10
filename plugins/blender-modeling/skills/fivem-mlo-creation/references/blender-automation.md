# Blender / Sollumz automation (bpy, headless, MCP)

**Tested:** every code block below was executed headless on 2026-10-10 with the `bpy` wheels
**4.5.14 LTS** (Python 3.11) and **5.2.2 LTS** (Python 3.13), Sollumz `main` 07d6a49 (2.9.0-dev, szio 1.4.0.dev1)
loaded as an add-on. Both versions produced byte-identical exports. PyMateria is Windows-only, so the test ran
with **CW XML** output; the `NATIVE` path is the same call with `formats=("NATIVE",)` (not executed here).
Generic bpy rules (temp_override, 5.x API renames): skills `blender-python-pitfalls`, `blender-current-api`;
proving a result with renders/screenshots: `blender-verify` (all in the `blender-modeling` plugin).

## Wrong vs right (all hit during testing or read in the Sollumz source)

| Wrong | Right | Why |
|---|---|---|
| `with temp_override(selected_objects=[...]): bpy.ops.sollumz.export_assets(...)` | `obj.select_set(True)` on the roots, then call | export reads `view_layer.objects.selected`, not the override → only the YTYP is written |
| `export_assets(target_formats={"NATIVE"}, ...)` | add `use_custom_settings=True` | otherwise the user preferences are used and your arguments are silently ignored |
| reading `obj.matrix_world` right after `bpy.data.objects.new` | `bpy.context.view_layer.update()` first | new objects report identity until the depsgraph updates; room bounds came out 1.6 m off in the test |
| `bpy.ops.mesh.separate(type="SELECTED")` in a script/MCP | bmesh split (`separate_selected_faces`) | headless: "Selection not supported in object mode" even after `mode_set` in an override |
| Boolean `solver="FAST"` | `"EXACT"` (both), or `"FLOAT"` (5.x) / `"FAST"` (4.x) | enum items: 4.5 `FAST/EXACT/MANIFOLD`, 5.2 `FLOAT/EXACT/MANIFOLD` |
| `bpy.ops.sollumz.createportalfromselection()` from a script | write `portal.corner1..4` directly | the operator sorts the 4 verts by **screen-space** winding (needs a 3D View region) |
| `setroomboundsfromselection` from a script | `room.bb_min/bb_max` from `bounds_of()` | needs Edit Mode + UI; subtracts only the composite **location** (keep the composite unrotated) |
| room bounds / portal corners in world space | MLO space = relative to the Bound Composite origin | Sollumz stores and exports them relative to `archetype.asset` |
| `light.data.energy = x` | `light.data.light_properties.intensity = x` | `intensity` is a proxy: energy = intensity × 500 (`LIGHT_INTENSITY_SCALE_FACTOR`) |
| hiding a light (`hide_viewport`) to switch it off | intensity 0 | hidden lights still export, at a broken position (muto-atlas, measured) |
| `import sollumz.ybn...` | `szmod("ybn.collision_materials")` | as an extension the package is `bl_ext.<repo>.sollumz` |
| searching objects by the plain name after Convert to Drawable | the mesh is now `<name>.model`; the drawable empty keeps `<name>` | `.001` suffixes break lookups (export drops them) |
| `color_attributes[...].data[i].color = 0.6` | `.color_srgb = 0.6` | on BYTE_COLOR `.color` is gamma-decoded: writing 0.6 stores byte 203, reading returns darker values; Sollumz exports the raw byte (`color_srgb` 0.6 → 153, tested) |
| exporting into a folder that does not exist | `os.makedirs(out, exist_ok=True)` | reported hang on exit (muto-atlas) |

## 1. Generic helpers (no add-on)

Save as `mlo_bpy.py` next to your script.

```python
# mlo_bpy.py - generic helpers, no add-on needed
import re, sys, bpy, bmesh
from mathutils import Vector

def faces_by_material(obj, pattern, use_shader=False, select=True):
    """Select polygons whose material name (or Sollumz shader filename) matches regex `pattern`.
    Works in OBJECT mode; returns the list of polygon indices."""
    rx = re.compile(pattern, re.I)
    slots = []
    for i, slot in enumerate(obj.material_slots):
        m = slot.material
        if m is None:
            continue
        key = m.shader_properties.filename if use_shader and hasattr(m, "shader_properties") else m.name
        if rx.search(key):
            slots.append(i)
    hits = [p.index for p in obj.data.polygons if p.material_index in slots]
    if select:
        sel = [False] * len(obj.data.polygons)
        for i in hits:
            sel[i] = True
        obj.data.polygons.foreach_set("select", sel)
        obj.data.update()
    return hits

def separate_selected_faces(obj, new_name):
    """Move the selected polygons of `obj` into a new object (no operators, works headless/MCP).
    UVs, colour attributes and material slots are kept on both parts."""
    src = obj.data
    dst = src.copy()
    dst.name = new_name

    def keep(me, keep_selected):
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.select != keep_selected], context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(me)
        bm.free()

    keep(dst, True)
    keep(src, False)
    new = bpy.data.objects.new(new_name, dst)
    new.matrix_world = obj.matrix_world.copy()
    for c in obj.users_collection:
        c.objects.link(new)
    return new

def make_inner_shell(ext_obj, name, wall=0.25):
    """Inner wall shell from a closed exterior: copy, shrink inward along normals, flip normals.
    The exterior object is not modified (its UVs / vertex colours stay vanilla)."""
    me = ext_obj.data.copy()
    me.name = name
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for v in bm.verts:                                   # shrink/fatten (Alt+S) by -wall
        v.co -= v.normal * wall * v.calc_shell_factor()
    bmesh.ops.reverse_faces(bm, faces=bm.faces)          # normals now point into the rooms
    bm.to_mesh(me)
    bm.free()
    inner = bpy.data.objects.new(name, me)
    inner.matrix_world = ext_obj.matrix_world.copy()
    for c in ext_obj.users_collection:
        c.objects.link(inner)
    return inner

def solidify_apply(obj, thickness=0.25, offset=-1.0):
    """Give a single-sided shell real wall thickness (Solidify), then apply it."""
    mod = obj.modifiers.new("WallThickness", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = offset              # -1 = grow against the normals (inward if normals face out)
    mod.use_even_offset = True       # keep constant thickness at corners
    mod.use_rim = True               # close open edges (door/window cut-outs)
    mod.use_quality_normals = True
    with bpy.context.temp_override(object=obj, active_object=obj):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def floor_slabs(name, min_xy, max_xy, z0, storey_h, n_storeys, slab=0.2, collection=None):
    """One box per storey: floor top at z0 + i*storey_h, `slab` thick. Returns list of objects."""
    col = collection or bpy.context.scene.collection
    out = []
    for i in range(n_storeys):
        top = z0 + i * storey_h
        me = bpy.data.meshes.new(f"{name}_{i}")
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        sx, sy = max_xy[0] - min_xy[0], max_xy[1] - min_xy[1]
        bmesh.ops.scale(bm, vec=(sx, sy, slab), verts=bm.verts)      # bake size into the mesh
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(f"{name}_{i}", me)
        ob.location = ((min_xy[0] + max_xy[0]) / 2, (min_xy[1] + max_xy[1]) / 2, top - slab / 2)
        col.objects.link(ob)
        out.append(ob)
    return out

def room_box(name, bb_min, bb_max, collection=None):
    """Axis-aligned helper box (e.g. to set MLO room bounds or block out a room)."""
    col = collection or bpy.context.scene.collection
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=[b - a for a, b in zip(bb_min, bb_max)], verts=bm.verts)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = [(a + b) / 2 for a, b in zip(bb_min, bb_max)]
    col.objects.link(ob)
    return ob

def paint_vertex_colour(obj, rgba=(0.0, 1.0, 0.0, 1.0), layer="Color 1"):
    """Fill the Sollumz colour layer (FACE CORNER, BYTE COLOR). Raw byte values via color_srgb."""
    me = obj.data
    attr = me.color_attributes.get(layer) or me.color_attributes.new(layer, "BYTE_COLOR", "CORNER")
    flat = list(rgba) * len(attr.data)
    attr.data.foreach_set("color_srgb", flat)
    me.color_attributes.active_color = attr
    return attr

def rename_prefix(objs, old, new):
    """Batch rename: replace prefix `old` with `new` on objects AND their mesh data; strips .001."""
    for o in objs:
        base = re.sub(r"\.\d{3}$", "", o.name)
        if base.startswith(old):
            o.name = new + base[len(old):]
            if o.data is not None and o.type == "MESH":
                o.data.name = o.name
```

Usage notes:
- `faces_by_material(ext, r"glass|window")` by material name; `faces_by_material(ext, r"^glass|emissive", use_shader=True)`
  by Sollumz shader file name (`material.shader_properties.filename`, e.g. `glass_env.sps`).
- `make_inner_shell` only gives clean results on closed exteriors; run it before cutting openings, then cut the
  same openings in both shells (or bridge them into reveals).
- `solidify_apply`: `offset=-1` with outward normals thickens inward. On imported vanilla meshes Solidify often
  produces spikes at split normals; prefer `make_inner_shell` + manual reveals.
- `paint_vertex_colour(inner, (0, 0.6, 0.2, 1))`: interior R=0, G≈0.6 (artificial ambient); exterior use red-dominant.

## 2. Sollumz helpers

Save as `mlo_sollumz.py`. Sollumz must be enabled.

```python
# mlo_sollumz.py - needs Sollumz 2.9 enabled
import os, sys, bpy
from mathutils import Vector

def szmod(sub):
    """Import a Sollumz submodule whatever the install path (legacy add-on 'sollumz' or extension 'bl_ext.<repo>.sollumz')."""
    name = next(n for n in sys.modules if n.endswith("." + sub) and "sollumz" in n.lower())
    return sys.modules[name]

def add_shader(obj, filename="normal.sps"):
    sm = szmod("ydr.shader_materials")
    idx = next(i for i, s in enumerate(sm.shadermats) if s.value == filename)
    with bpy.context.temp_override(selected_objects=[obj], active_object=obj, object=obj):
        bpy.ops.sollumz.createshadermaterial(shader_index=idx)
    return obj.data.materials[-1]

def to_drawable(mesh_obj):
    """Mesh -> Drawable (empty, keeps the name) + Drawable Model child '<name>.model'."""
    name = mesh_obj.name
    with bpy.context.temp_override(selected_objects=[mesh_obj], active_object=mesh_obj, object=mesh_obj):
        bpy.ops.sollumz.converttodrawable()
    return bpy.data.objects[name]

def to_collision(mesh_obj, material="CONCRETE", room_index=1):
    """Mesh -> Bound Composite (keeps the name = MLO archetype name) -> GeometryBVH -> poly mesh.
    Default flag preset 'General (Default)' is applied by the operator (Sollumz 2.9+)."""
    cm = szmod("ybn.collision_materials")
    names = [m.name for m in cm.collisionmats]
    mat = cm.create_collision_material_from_index(names.index(material))
    mat.collision_properties.room_id = room_index          # index in the MLO room list (limbo = 0)
    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(mat)
    name = mesh_obj.name
    with bpy.context.temp_override(selected_objects=[mesh_obj], active_object=mesh_obj, object=mesh_obj):
        bpy.ops.sollumz.converttocomposite()
    return bpy.data.objects[name]

def world_to_mlo(composite, co):
    """Room bounds / portal corners are stored relative to the MLO asset (composite) origin."""
    return composite.matrix_world.inverted() @ Vector(co)

def bounds_of(obj, composite):
    """Room bounds (bb_min, bb_max) in MLO space from a helper box object."""
    bpy.context.view_layer.update()          # new objects report identity matrix_world until the depsgraph updates
    pts = [world_to_mlo(composite, obj.matrix_world @ Vector(c)) for c in obj.bound_box]
    return tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3))

def build_mlo(ytyp_name, composite, drawables, rooms, portals, entities, mlo_flags=1024):
    """rooms: [(name, bb_min, bb_max, timecycle, flags)]  (limbo is created first automatically)
    portals: [(room_from, room_to, (c1, c2, c3, c4) in MLO space, flags)]
    entities: [(drawable_obj, room_name)]"""
    bpy.ops.sollumz.createytyp()
    sc = bpy.context.scene
    ytyp = sc.ytyps[sc.ytyp_index]
    ytyp.name = ytyp_name
    for d in drawables:                                     # one Base archetype per drawable
        a = ytyp.new_archetype()
        a.name = d.name
        a.asset = d                                          # update callback fills asset type/name/txd
    mlo = ytyp.new_archetype("sollumz_archetype_mlo")
    mlo.name = composite.name                                # MLO name = .ybn name
    mlo.asset = composite
    mlo.mlo_flags.total = str(mlo_flags)
    by_name = {}
    limbo = mlo.new_room(); limbo.name = "limbo"; limbo.timecycle = ""; limbo.flags.total = "96"
    lo, hi = composite_extents(composite)
    limbo.bb_min, limbo.bb_max = lo, hi
    by_name["limbo"] = limbo
    for name, bb_min, bb_max, tc, flags in rooms:
        r = mlo.new_room(); r.name = name; r.bb_min = bb_min; r.bb_max = bb_max
        r.timecycle = tc; r.flags.total = str(flags)
        by_name[name] = r
    for rf, rt, corners, flags in portals:
        p = mlo.new_portal()
        p.room_from_id = str(by_name[rf].id); p.room_to_id = str(by_name[rt].id)
        p.corner1, p.corner2, p.corner3, p.corner4 = corners
        p.flags.total = str(flags)
    for obj, room in entities:
        e = mlo.new_entity()
        e.archetype_name = obj.name
        e.linked_object = obj
        e.attached_room_id = str(by_name[room].id)
    return ytyp, mlo

def composite_extents(composite):
    bpy.context.view_layer.update()
    pts = []
    for ch in composite.children_recursive:
        if ch.type == "MESH":
            pts += [world_to_mlo(composite, ch.matrix_world @ v.co) for v in ch.data.vertices]
    return (tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)))

def export_assets(objs, out_dir, formats=("NATIVE",), versions=("GEN8", "GEN9"), ytyps=True):
    """Export selected Sollumz roots + all YTYPs. Export reads view_layer selection, NOT temp_override."""
    os.makedirs(out_dir, exist_ok=True)                      # missing folder can hang Blender (community report)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.hide_set(False); o.hide_viewport = False; o.hide_select = False
        o.select_set(True)
    assert len(bpy.context.view_layer.objects.selected) == len(objs), "selection silently dropped"
    return bpy.ops.sollumz.export_assets(
        directory=out_dir, direct_export=True, use_custom_settings=True,   # else user prefs win silently
        target_formats=set(formats), target_versions=set(versions), limit_to_selected=True,
        export_ytyps=ytyps, export_ytyps_include="ALL")

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<CPackFileMetaData>
  <MapDataGroups/>
  <HDTxdBindingArray/>
  <imapDependencies/>
  <imapDependencies_2>
    <Item>
      <imapName>{ymap}</imapName>
      <manifestFlags>INTERIOR_DATA</manifestFlags>
      <itypDepArray>
        <Item>{ytyp}</Item>
      </itypDepArray>
    </Item>
  </imapDependencies_2>
  <itypDependencies_2/>
  <Interiors itemType="CInteriorBoundsFiles">
    <Item>
      <Name>{mlo}</Name>
      <Bounds>
        <Item>{mlo}</Item>
      </Bounds>
    </Item>
  </Interiors>
</CPackFileMetaData>
"""

def write_manifest_xml(path, ymap, ytyp, mlo):
    """Same shape as CodeWalker's Manifest Generator for one MLO ymap + ytyp. Prefer CodeWalker's output
    (it also lists vanilla/other ytyps the MLO entities use in itypDependencies_2)."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(MANIFEST.format(ymap=ymap, ytyp=ytyp, mlo=mlo))
```

## 3. End-to-end: one-room MLO, exported

```python
# run: blender -b --factory-startup --python-exit-code 1 -P build_mlo.py -- C:/out
# (with Sollumz enabled in the user prefs; drop --factory-startup if it disables the add-on)
import sys, os, bpy, bmesh, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mlo_bpy import *
from mlo_sollumz import *
OUT = sys.argv[-1]
print("Blender", bpy.app.version_string)
sc = bpy.context.scene
def box(name, size, loc):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, size[2] / 2), verts=bm.verts)     # origin at floor centre
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); ob.location = loc
    return ob
shell = box("abc_bldg_int", (10, 8, 3.2), (0, 0, 0))
shell.data.uv_layers.new(name="UVMap 0")
paint_vertex_colour(shell, (0.0, 0.6, 0.2, 1.0))
mat = add_shader(shell, "normal.sps"); print("shader", mat.shader_properties.filename)
col = bpy.data.objects.new("abc_bldg_mlo", shell.data.copy()); sc.collection.objects.link(col)
drawable = to_drawable(shell); print("drawable", drawable.name, drawable.sollum_type)
comp = to_collision(col, "CONCRETE", room_index=1)
print("composite", comp.name, [c.sollum_type for c in comp.children_recursive])
helper = room_box("rb_main", (-5, -4, 0), (5, 4, 3.2))
bb = bounds_of(helper, comp); bpy.data.objects.remove(helper)
# exit portal on the +X wall, counter-clockwise seen from outside (arrow points out of the room)
corners = [world_to_mlo(comp, c) for c in ((5, 1, 2.4), (5, -1, 2.4), (5, -1, 0), (5, 1, 0))]
ytyp, mlo = build_mlo("abc_bldg", comp, [drawable],
    rooms=[("main", bb[0], bb[1], "int_gasstation", 96)],
    portals=[("main", "limbo", corners, 0)],
    entities=[(drawable, "main")])
c = [Vector(x) for x in (mlo.portals[0].corner1, mlo.portals[0].corner2, mlo.portals[0].corner3)]
print("portal arrow (Sollumz gizmo formula)", tuple(round(v, 2) for v in (-(c[2] - c[0]).cross(c[1] - c[0])).normalized()))
print("exit portals", mlo.calc_num_exit_portals(), "mlo flags", mlo.mlo_flags.total)
print(export_assets([drawable, comp], OUT, formats=("CWXML",)))
write_manifest_xml(os.path.join(OUT, "_manifest.ymf"), "abc_bldg_milo_", "abc_bldg", "abc_bldg_mlo")
for f in sorted(glob.glob(os.path.join(OUT, "**", "*"), recursive=True)):
    if os.path.isfile(f): print("  ", os.path.relpath(f, OUT), os.path.getsize(f))
```

Result in the test: `gen8/` and `gen9/` each with `abc_bldg.ytyp.xml`, `abc_bldg_int.ydr.xml`,
`abc_bldg_mlo.ybn.xml`; MLO flags 1024, room `main` bounds `(-5,-4,0)..(5,4,3.2)`, exit portal arrow `(+1,0,0)`
(outward), `numExitPortals` 1, collision material `CONCRETE` with `RoomID 1`. The CW XML for gen8 and gen9 was
identical for this `normal.sps` model (Gen9 XML only adds Gen9-specific shader parameter defaults for some shaders).

## 4. Sollumz operator ids (present in 2.9.0-dev, 443 operators registered)

| Task | Operator | Context needed |
|---|---|---|
| Import / export | `sollumz.import_assets(directory=, files=[{"name":...}])`, `sollumz.export_assets(directory=, direct_export=True, use_custom_settings=True, ...)` | export: real selection |
| Mesh → drawable | `sollumz.converttodrawable` | `selected_objects` (override OK) |
| Shader material | `sollumz.createshadermaterial(shader_index=i)` (index into `shadermats`) | `selected_objects` |
| Mesh → collision | `sollumz.converttocomposite` (uses `scene.bound_child_type`, `scene.sz_default_flag_preset_name`) | `selected_objects` |
| Bounds / materials | `sollumz.createbound`, `sollumz.createcollisionmaterial` (uses `window_manager.sz_collision_material_index`), `sollumz.load_flag_preset` | selection |
| YTYP / archetypes | `sollumz.createytyp`, `sollumz.createarchetype`, `sollumz.createarchetypefromselected` (MLO needs a Bound Composite) | none / selection |
| Rooms / portals | `sollumz.createroom`, `sollumz.createlimboroom` (bounds from asset extents, name `limbo`), `sollumz.setroomboundsfromselection`, `sollumz.createportal`, `sollumz.createportalfromselection`, `sollumz.flipportal` | selected archetype; last two need Edit Mode/3D View |
| Entities / sets | `sollumz.addobjasentity`, `sollumz.createmloentity`, `sollumz.createentityset`, `sollumz.createtimecyclemodifier` | selected archetype |
| MLO instance (maps) | `sollumz.mlo_create_instance`, `sollumz.mlo_refresh_instances`, `sollumz.import_ymap`, `sollumz.export_ymap` | selected MLO archetype |
| Lights | `sollumz.create_light` (type from `scene.create_light_type`; applies preset "Default": intensity 0.02, time flags 0, flags 0 → set intensity, hours and flags yourself) | active drawable/model = parent |

Property API used above (stable in 2.9): `scene.ytyps[scene.ytyp_index]`, `ytyp.new_archetype(type)`,
`archetype.new_room() / new_portal() / new_entity() / new_entity_set() / new_tcm()`,
`archetype.calc_num_exit_portals()`, `flags.total` (string), `room.timecycle`, `entity.attached_room_id`,
`entity.attached_portal_id`, `material.collision_properties.room_id`.

## 5. Running it: headless, MCP

- Headless batch: `blender -b scene.blend --python-exit-code 1 -P build_mlo.py -- <out_dir>`. Sollumz must be
  enabled in that Blender's preferences (or enable it in the script with `addon_utils.enable(...)`).
- **Official Blender Lab MCP** (`projects.blender.org/lab/blender_mcp`, docs `blender.org/lab/mcp-server`):
  Blender **5.1+**, v1.0.0 2026-04-27 (search snippets; site blocked here). Tool `execute_blender_code`; Sollumz
  operators are callable through it like any bpy code. Setup steps: `blender-modeling` plugin `EXTERNAL.md`.
- **MCP for Blender** (`github.com/ahujasid/mcp-for-blender`, formerly `blender-mcp`, MIT, 2.1.9 on 2026-10-06):
  `claude mcp add blender uvx mcp-for-blender`; add-on bridge on `127.0.0.1:9876`; tool `execute_blender_code`;
  opt-in telemetry; Blender 3.0+.
- Through any MCP the rules in the table above still apply (selection, `use_custom_settings`, depsgraph update).
  Save a copy of the `.blend` first: generated code runs unsandboxed in the open file.
