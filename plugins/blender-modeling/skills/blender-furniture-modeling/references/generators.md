# Furniture generators (bpy): table, chair, bar stool, shelf, cabinet, drawers, bed frame, billiard table

Read **first** when building furniture by script (MCP or `blender -b`). Code: the block at the end of this file,
saved as `furniture_gen.py`. Tests: [generator-tests.md](generator-tests.md).

**Status.** Ran headless on 2026-10-10 with the `bpy` wheels **5.2.2** (Blender 5.2 LTS, Python 3.13) and
**4.5.14** (Blender 4.5 LTS, Python 3.11): 276/276 checks passed on both (incl. every preset below). Not executed: Blender 4.2 (expected to work:
only 4.1+ APIs are used), the Sollumz conversion (Sollumz cannot load in the bpy wheel), Unreal import, in-game tests.

## Conventions

| Item | Convention | Why |
|---|---|---|
| Units / axes | metres; X = width, Y = depth with the **front facing −Y**, Z = up | Blender front view looks at the front; GTA/Blender Z-up |
| Origin | bottom centre of the footprint (`obj["footprint"]`), z = 0 at floor contact | drop-in placement in MLOs and UE, rotation about the right point |
| Parts | each board/leg/door/handle is its own closed shell in one mesh, face int attribute `part` → `obj["parts"]` names | real construction, per-part grain, tests, merge per part |
| Contacts | parts touch face to face (hidden opposite faces), never share vertices, never coplanar same-facing overlap | no z-fighting, no welding (tested) |
| UVs | `UVMap 0` (Sollumz name), world-scale box projection, U along each part's longest axis | constant texel density, grain direction (tested) |
| Materials | placeholder slots `sz_<GTA shader>.<kind>` with Principled values from `MATERIALS` | `sz_apply_shaders()` (doors skill) converts them; UE gets named slots |
| Collision | `obj["col_boxes"]` (local min/max) → `make_collision(obj, "UE" or "SOLLUMZ")` | UCX boxes or Sollumz box bounds |
| Cleanup | `finalize(obj)` after building (or on any hand-made mesh) | apply transforms, merge per part, normals, origin, Bevel + WN |
| Opening fronts | `make_cabinet(separate_doors=True)`: door objects parented to the carcass, origin on the hinge axis (outer back edge, bottom); `finalize(door, keep_origin=True)` | animation in UE; GTA furniture doors stay static |

## API

| Function | Key parameters (defaults) | Returns / custom props |
|---|---|---|
| `make_table` | width 1.6, depth 0.9, height 0.75, top_t 0.025, leg 0.06, leg_inset 0.05, apron_h 0.09 | `knee_clearance` |
| `make_chair` | seat_h 0.45, seat_w 0.44, seat_d 0.42, back_h 0.86, back_angle 8°, leg 0.035, slats 2, stretcher_z 0.15 | `back_angle` |
| `make_bar_stool` | seat_h 0.75 (0.65 counter), seat_d 0.36, splay 6°, foot_drop 0.45 | `foot_z` |
| `make_shelf` | width 0.8, depth 0.28, height 2.02, t 0.018, back_t 0.003, shelves 5, plinth_h 0.06 | `shelf_clear`, `shelf_span` |
| `make_cabinet` | width, height (incl. worktop), depth (carcass + doors), base PLINTH/KICK/LEGS/NONE, worktop_t, gap 0.003, max_door_w 0.6, handle BAR_V/BAR_H/KNOB/NONE, handle_z, separate_doors | `doors` [x0,x1,z0,z1], `door_objects`, `y_face` |
| `make_drawer_unit` | width 0.8, height 0.8, depth 0.48, drawers 4, graduated, base, handle BAR_H, drawer_boxes | `fronts` [z0,z1] |
| `make_bed_frame` | mattress key (`MATTRESSES`) or (w, l), mattress_t 0.20, mattress_top 0.52, clearance 0.01, headboard_h 1.0 | `mattress` [w, l, t, x, y, z_bottom] for `blender-soft-furniture`, `slat_pitch` |
| `make_billiard_table` | size `9ft`/`8ft_pro`/`8ft`/`7ft`/`snooker_12ft` or (l, w), bed_h 0.762, ball_d 57.15 mm, nose_ratio 0.635, mouths 4.5625/5.0625 in | `play`, `nose_z`, `pockets` |
| `finalize(obj, bevel_width=0.002, bevel_segments=2, bevel_angle=30, weighted_normal=True, meters_per_uv=None, triangulate=False, keep_origin=False)` | | `{"offset", "tris"}` |
| `make_collision(obj, "UE")` / `(obj, "SOLLUMZ")` | | UCX objects / asset dict for `sz_convert` |
| `make_lods(obj)` | | `[LOD1 mesh (no bevel), LOD2 mesh (boxes)]` |
| `build_demo()` | | one of each, finalized, in a row |

## Presets (parameters for common pieces)

| Piece | Call |
|---|---|
| Dining table 6 seats | `make_table("dining_01", 1.8, 0.9, 0.75)` |
| Desk | `make_table("desk_01", 1.4, 0.7, 0.74, top_t=0.025, apron_h=0.06)` (knee clearance ≥ 0.63) |
| Coffee table | `make_table("coffee_01", 1.1, 0.6, 0.42, apron_h=0.06)` |
| Bar table | `make_table("bartable_01", 1.2, 0.6, 1.05, leg=0.07, apron_h=0.08)` |
| Counter / bar stool | `make_bar_stool(seat_h=0.65)` / `make_bar_stool(seat_h=0.75)` |
| EU kitchen base | `make_cabinet("k_base_60", 0.6, 0.9, 0.58, base="KICK", plinth_h=0.15, worktop_t=0.038, handle="BAR_H")` |
| EU wall unit (place at z ≈ 1.45) | `make_cabinet("k_wall_60", 0.6, 0.72, 0.35, base="NONE", handle="BAR_H")` |
| Wardrobe | `make_cabinet("wardrobe_100", 1.0, 2.01, 0.60, base="PLINTH", plinth_h=0.08)` |
| Sideboard / TV unit | `make_cabinet("sideboard_160", 1.6, 0.75, 0.45, base="LEGS", leg_h=0.15, handle="KNOB")` / height 0.50 |
| Dresser | `make_drawer_unit("dresser_01", 0.8, 0.8, 0.48, drawers=4)` |
| Nightstand (mattress top 0.52) | `make_drawer_unit("night_01", 0.45, 0.55, 0.40, drawers=2, graduated=False, base="LEGS", leg_h=0.18, handle="KNOB")` |
| Bed EU 160 / US queen | `make_bed_frame(mattress="EU_160x200")` / `make_bed_frame(mattress="US_queen")` |
| Pool 9 ft / snooker | `make_billiard_table(size="9ft")` / `make_billiard_table(size="snooker_12ft", bed_h=0.819, ball_d=0.0525, diamonds=False)` |

The billiard table is dimension-exact where it matters (playing surface between the noses, bed height, nose height,
pocket mouths, sights) but its pockets are square-cut placeholders: model the jaws (angles in `billiards-game-dev`)
before shipping. The snooker preset sets the rail top to the WPBSA 864 mm; its nose height (0.635 × ball) is not
verified for snooker cushions.

## Workflow

1. `exec(open(".../furniture_gen.py").read())` in an MCP session, or `blender -b --factory-startup
   --python-exit-code 1 -P build.py` with `import furniture_gen as G` (in the bpy wheel `import bpy` must come before
   `import bmesh`).
2. Build: `ob = G.make_cabinet(...)`; move/rotate the object, never edit the mesh scale.
3. `G.finalize(ob)` (also on hand-made meshes: it falls back to islands as parts and the bbox as footprint).
4. Game: `G.make_collision(ob, "UE")` + FBX export, or `asset = G.make_collision(ob, "SOLLUMZ")` then (Sollumz loaded)
   `sz_convert(asset)` from `fivem-mlo-doors-windows`.
5. Look at it: render or MCP screenshot with a 1.75 m box next to it (`blender-verify`).

## Generator: save as `furniture_gen.py`

```python
"""Hard-furniture generators for Blender 4.2+ / 5.x (tested headless: bpy 5.2.2 and 4.5.14).

Pure bpy + bmesh, no add-ons. Every part (top, leg, panel, door, handle ...) is its own closed shell
inside ONE mesh object; parts touch but never share vertices (merge by distance per part only).
Units metres. Axes: X = width, Y = depth (front faces -Y), Z = up. Origin = bottom centre of the
footprint (floor contact). Materials: placeholders 'sz_<GTA shader>.<kind>' with Principled values
(sz_apply_shaders/sz_convert from fivem-mlo-doors-windows swap them for Sollumz shaders).
"""
import math

import bpy  # first: in the bpy wheel, bmesh/mathutils only exist after `import bpy`
import bmesh
from mathutils import Matrix, Vector

EPS = 1e-6
IN = 0.0254                      # inch -> metre

# kind: (GTA shader, base colour, roughness, metallic, coat weight)
MATERIALS = {
    "wood":        ("normal_spec", (0.42, 0.27, 0.15, 1.0), 0.45, 0.0, 0.3),
    "wood_dark":   ("normal_spec", (0.16, 0.10, 0.06, 1.0), 0.40, 0.0, 0.4),
    "lacquer":     ("normal_spec", (0.90, 0.90, 0.88, 1.0), 0.25, 0.0, 0.0),
    "laminate":    ("normal_spec", (0.85, 0.85, 0.83, 1.0), 0.45, 0.0, 0.0),
    "metal":       ("normal_spec_reflect", (0.62, 0.62, 0.64, 1.0), 0.30, 1.0, 0.0),
    "paint_black": ("normal_spec", (0.03, 0.03, 0.03, 1.0), 0.50, 0.0, 0.0),   # powder coat = dielectric
    "stone":       ("normal_spec_reflect", (0.82, 0.82, 0.80, 1.0), 0.15, 0.0, 0.0),
    "glass":       ("glass", (0.85, 0.92, 0.90, 1.0), 0.02, 0.0, 0.0),
    "felt":        ("normal_spec", (0.05, 0.35, 0.15, 1.0), 0.90, 0.0, 0.0),
    "rubber":      ("normal_spec", (0.04, 0.04, 0.04, 1.0), 0.70, 0.0, 0.0),
}

MATTRESSES = {   # (width, length) in metres; EU/UK nominal cm, US nominal inches
    "EU_90x200": (0.90, 2.00), "EU_100x200": (1.00, 2.00), "EU_140x200": (1.40, 2.00),
    "EU_160x200": (1.60, 2.00), "EU_180x200": (1.80, 2.00), "EU_200x200": (2.00, 2.00),
    "UK_single": (0.90, 1.90), "UK_double": (1.35, 1.90), "UK_king": (1.50, 2.00), "UK_superking": (1.80, 2.00),
    "US_twin": (38 * IN, 75 * IN), "US_twin_xl": (38 * IN, 80 * IN), "US_full": (54 * IN, 75 * IN),
    "US_queen": (60 * IN, 80 * IN), "US_king": (76 * IN, 80 * IN), "US_cal_king": (72 * IN, 84 * IN),
}

POOL_TABLES = {  # playing surface between cushion noses (WPA: 9 ft 100x50 in, 8 ft 92x46 in)
    "9ft": (100 * IN, 50 * IN), "8ft_pro": (92 * IN, 46 * IN), "8ft": (88 * IN, 44 * IN),
    "7ft": (78 * IN, 39 * IN), "snooker_12ft": (3.569, 1.778),
}


# ------------------------------------------------------------------ helpers
def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def material(kind):
    shader, rgba, rough, metal, coat = MATERIALS[kind]
    name = f"sz_{shader}.{kind}"
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True                         # 5.0+: always on, setting deprecated
    mat.diffuse_color = rgba
    bsdf = next((n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if bsdf is not None:                             # 4.0+ socket names
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Coat Weight"].default_value = coat
        if kind == "glass":
            bsdf.inputs["Transmission Weight"].default_value = 1.0
            bsdf.inputs["IOR"].default_value = 1.52
    return mat


def islands(bm):
    """Face islands connected through edges (= parts)."""
    left, out = set(bm.faces), []
    while left:
        stack = [left.pop()]
        isl = set(stack)
        while stack:
            f = stack.pop()
            for e in f.edges:
                for g in e.link_faces:
                    if g in left:
                        left.remove(g)
                        isl.add(g)
                        stack.append(g)
        out.append(isl)
    return out


def uv_grain_project(bm, part_layer=None, meters_per_uv=1.0, layer_name="UVMap 0"):
    """Box projection in object space (metres / meters_per_uv = constant texel density on every part).
    Per part, U follows the part's longest dimension wherever that axis lies in the face plane, so wood
    grain runs along legs, rails and tops, vertical on doors, horizontal on drawer fronts."""
    uv = bm.loops.layers.uv.get(layer_name) or bm.loops.layers.uv.new(layer_name)
    bm.normal_update()
    if part_layer is None:
        part_of = {f: i for i, isl in enumerate(islands(bm)) for f in isl}
    else:
        part_of = {f: f[part_layer] for f in bm.faces}
    lo, hi = {}, {}
    for f, p in part_of.items():
        for v in f.verts:
            a = lo.setdefault(p, [1e9] * 3)
            b = hi.setdefault(p, [-1e9] * 3)
            for i in range(3):
                a[i] = min(a[i], v.co[i])
                b[i] = max(b[i], v.co[i])
    long_axis = {p: max(range(3), key=lambda i: hi[p][i] - lo[p][i]) for p in lo}
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        a, b = [i for i in range(3) if i != ax]
        la = long_axis[part_of[f]]
        u_i, v_i = (la, b if la == a else a) if la in (a, b) else ((a, b) if a < b else (b, a))
        for loop in f.loops:
            co = loop.vert.co
            loop[uv].uv = (co[u_i] / meters_per_uv, co[v_i] / meters_per_uv)


class Parts:
    """Collects closed part shells into one bmesh; face int attribute 'part' = index into names."""

    def __init__(self):
        self.bm = bmesh.new()
        self.names, self.mats = [], []
        self.pid = self.bm.faces.layers.int.new("part")

    def _register(self, name, faces, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        idx = len(self.names)
        self.names.append(name)
        for f in faces:
            f[self.pid] = idx
            f.material_index = self.mats.index(mat)
        return idx

    def box(self, name, mn, mx, mat, matrix=None):
        mn, mx = Vector(mn), Vector(mx)
        size = mx - mn
        assert min(size) > EPS, f"{name}: degenerate box {tuple(mn)} {tuple(mx)}"
        m = Matrix.LocRotScale((mn + mx) / 2, None, size)
        if matrix is not None:
            m = matrix @ m
        verts = bmesh.ops.create_cube(self.bm, size=1.0, matrix=m)["verts"]
        return self._register(name, {f for v in verts for f in v.link_faces}, mat)

    def hexa(self, name, corners, mat):
        """8 corners: bottom quad then top quad, same order (sheared legs with level cut ends)."""
        v = [self.bm.verts.new(c) for c in corners]
        quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        return self._register(name, [self.bm.faces.new([v[i] for i in q]) for q in quads], mat)

    def cylinder(self, name, base_center, radius, height, mat, segments=16):
        m = Matrix.Translation(Vector(base_center) + Vector((0.0, 0.0, height / 2)))
        verts = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segments,
                                      radius1=radius, radius2=radius, depth=height, matrix=m)["verts"]
        return self._register(name, {f for v in verts for f in v.link_faces}, mat)

    def extrusion(self, name, profile, axis, a0, a1, mat):
        """Convex profile [(u, z), ...] (u = Y for axis 'X', u = X for axis 'Y'), extruded from a0 to a1."""
        def p(a, u, z):
            return (a, u, z) if axis == "X" else (u, a, z)
        v0 = [self.bm.verts.new(p(a0, u, z)) for u, z in profile]
        v1 = [self.bm.verts.new(p(a1, u, z)) for u, z in profile]
        faces = [self.bm.faces.new(v0[::-1]), self.bm.faces.new(v1)]
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((v0[i], v0[j], v1[j], v1[i])))
        return self._register(name, faces, mat)

    def to_object(self, name, coll, meters_per_uv=1.0):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])     # outward, per closed shell
        uv_grain_project(self.bm, self.pid, meters_per_uv)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        obj = bpy.data.objects.new(name, me)
        coll.objects.link(obj)
        obj["parts"] = self.names
        return obj


def _tag(obj, footprint, col_boxes, **info):
    """footprint (xmin, xmax, ymin, ymax) defines the origin; col_boxes [(mn, mx)] for collision."""
    obj["footprint"] = list(footprint)
    obj["col_boxes"] = [list(mn) + list(mx) for mn, mx in col_boxes]
    for k, v in info.items():
        obj[k] = v
    return obj


# ------------------------------------------------------------------ table
def make_table(name="table_01", width=1.6, depth=0.9, height=0.75, top_t=0.025, leg=0.06, leg_inset=0.05,
               apron_h=0.09, apron_t=0.02, apron_setback=0.01, top_mat="wood", frame_mat="wood",
               coll=None, meters_per_uv=1.0):
    """Top + 4 square legs + 4 aprons. leg_inset = overhang of the top beyond the legs' outer faces."""
    assert apron_setback + apron_t <= leg, "apron must end on the leg face"
    coll = coll or get_collection(name)
    P, mt, mf = Parts(), material(top_mat), material(frame_mat)
    zt = height - top_t
    P.box("top", (-width / 2, -depth / 2, zt), (width / 2, depth / 2, height), mt)
    x1, y1 = width / 2 - leg_inset, depth / 2 - leg_inset          # leg outer faces
    legs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            mn = (min(sx * x1, sx * (x1 - leg)), min(sy * y1, sy * (y1 - leg)), 0.0)
            mx = (max(sx * x1, sx * (x1 - leg)), max(sy * y1, sy * (y1 - leg)), zt)
            P.box("leg", mn, mx, mf)
            legs.append((mn, mx))
    za = zt - apron_h
    for s in (-1, 1):
        yo, yi = s * (y1 - apron_setback), s * (y1 - apron_setback - apron_t)
        P.box("apron_x", (-(x1 - leg), min(yo, yi), za), (x1 - leg, max(yo, yi), zt), mf)
        xo, xi = s * (x1 - apron_setback), s * (x1 - apron_setback - apron_t)
        P.box("apron_y", (min(xo, xi), -(y1 - leg), za), (max(xo, xi), y1 - leg, zt), mf)
    obj = P.to_object(name, coll, meters_per_uv)
    cols = [((-width / 2, -depth / 2, za), (width / 2, depth / 2, height))] + legs
    return _tag(obj, (-width / 2, width / 2, -depth / 2, depth / 2), cols, knee_clearance=za)


# ------------------------------------------------------------------ chair
def make_chair(name="chair_01", seat_h=0.45, seat_w=0.44, seat_d=0.42, seat_t=0.025, back_h=0.86,
               back_angle=8.0, leg=0.035, overhang=0.008, apron_h=0.05, apron_t=0.018, slats=2,
               slat_h=0.06, stretcher_z=0.15, seat_mat="wood", frame_mat="wood", coll=None, meters_per_uv=1.0):
    """Seat (top at seat_h) + 4 legs + seat rails + back posts tilted back_angle deg from vertical about
    their FRONT-bottom edge (back edge sinks into the seat, no wedge gap) + slats + side stretchers.
    Seat overhangs the frame by `overhang` so no frame face is coplanar with a seat face."""
    coll = coll or get_collection(name)
    P, ms, mf = Parts(), material(seat_mat), material(frame_mat)
    zs = seat_h - seat_t
    P.box("seat", (-seat_w / 2, -seat_d / 2, zs), (seat_w / 2, seat_d / 2, seat_h), ms)
    xo, yf, yb = seat_w / 2 - overhang, -seat_d / 2 + overhang, seat_d / 2 - overhang
    for sx in (-1, 1):
        x0, x1 = sorted((sx * xo, sx * (xo - leg)))
        P.box("leg_front", (x0, yf, 0.0), (x1, yf + leg, zs), mf)
        P.box("leg_back", (x0, yb - leg, 0.0), (x1, yb, zs), mf)
        if stretcher_z:                                             # side stretchers, centred in the leg
            c = (x0 + x1) / 2
            P.box("stretcher", (c - leg * 0.3, yf + leg, stretcher_z - 0.0125), (c + leg * 0.3, yb - leg, stretcher_z + 0.0125), mf)
        a0, a1 = sorted((sx * (xo - 0.004), sx * (xo - 0.004 - apron_t)))
        P.box("rail_side", (a0, yf + leg, zs - apron_h), (a1, yb - leg, zs), mf)
    for y0, y1 in ((yf + 0.004, yf + 0.004 + apron_t), (yb - 0.004 - apron_t, yb - 0.004)):
        P.box("rail_x", (-(xo - leg), y0, zs - apron_h), (xo - leg, y1, zs), mf)
    a = math.radians(back_angle)
    L = (back_h - seat_h) / math.cos(a)
    pivot = Vector((0.0, yb - leg, seat_h))
    R = Matrix.Translation(pivot) @ Matrix.Rotation(-a, 4, "X") @ Matrix.Translation(-pivot)
    for sx in (-1, 1):                                               # posts: same footprint as the back legs
        x0, x1 = sorted((sx * xo, sx * (xo - leg)))
        P.box("back_post", (x0, yb - leg, seat_h), (x1, yb, seat_h + L), mf, matrix=R)
    yc = yb - leg / 2
    for i in range(slats):
        top = seat_h + L - i * (slat_h + 0.07)
        P.box("back_slat", (-(xo - leg), yc - 0.009, top - slat_h), (xo - leg, yc + 0.009, top), mf, matrix=R)
    obj = P.to_object(name, coll, meters_per_uv)
    cols = [((-seat_w / 2, -seat_d / 2, 0.0), (seat_w / 2, seat_d / 2, seat_h)),
            ((-xo, yb - leg, seat_h), (xo, yb + L * math.sin(a), back_h))]
    return _tag(obj, (-seat_w / 2, seat_w / 2, -seat_d / 2, seat_d / 2), cols, back_angle=back_angle)


# ------------------------------------------------------------------ bar stool
def make_bar_stool(name="bar_stool_01", seat_h=0.75, seat_d=0.36, seat_t=0.035, leg=0.03, splay=6.0,
                   top_spread=0.22, foot_drop=0.45, ring_t=0.02, seat_segments=24,
                   seat_mat="wood", frame_mat="paint_black", coll=None, meters_per_uv=1.0):
    """Round seat + 4 splayed legs (sheared boxes with level cut ends, so they stand flat) + footrest
    stretchers at seat_h - foot_drop. Crossing stretchers are staggered by ring_t*1.5 (no coplanar overlap)."""
    coll = coll or get_collection(name)
    P, ms, mf = Parts(), material(seat_mat), material(frame_mat)
    zs = seat_h - seat_t
    P.cylinder("seat", (0.0, 0.0, zs), seat_d / 2, seat_t, ms, seat_segments)
    off = zs * math.tan(math.radians(splay))
    dirs = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

    def centre(z, d):                                              # leg centre at height z (diagonal d)
        r = top_spread / 2 + off * (1 - z / zs)
        return Vector((d[0] * r / math.sqrt(2), d[1] * r / math.sqrt(2), z))

    h = leg / 2
    for d in dirs:
        cb, ct = centre(0.0, d), centre(zs, d)
        sq = [(-h, -h), (h, -h), (h, h), (-h, h)]
        P.hexa("leg", [(cb.x + u, cb.y + v, 0.0) for u, v in sq] + [(ct.x + u, ct.y + v, zs) for u, v in sq], mf)
    zf = max(0.18, seat_h - foot_drop)
    for k, (i, j) in enumerate(((2, 3), (1, 0), (2, 1), (3, 0))):  # front, back (along X), sides (along Y)
        z = zf + (0.0 if k < 2 else ring_t * 1.5)
        a, b = centre(z, dirs[i]), centre(z, dirs[j])
        t = ring_t / 2
        if k < 2:
            P.box("footrest_x", (a.x, a.y - t, z - t), (b.x, a.y + t, z + t), mf)
        else:
            P.box("footrest_y", (a.x - t, min(a.y, b.y), z - t), (a.x + t, max(a.y, b.y), z + t), mf)
    obj = P.to_object(name, coll, meters_per_uv)
    r = max(seat_d / 2, (top_spread / 2 + off) / math.sqrt(2) + h)
    return _tag(obj, (-r, r, -r, r), [((-r, -r, 0.0), (r, r, seat_h))], foot_z=zf)


# ------------------------------------------------------------------ shelf / bookcase
def make_shelf(name="bookcase_01", width=0.8, depth=0.28, height=2.02, t=0.018, back_t=0.003, shelves=5,
               plinth_h=0.06, plinth_setback=0.02, shelf_setback=0.003, carcass_mat="wood", coll=None,
               meters_per_uv=1.0):
    """Sides (floor to top), top + bottom between the sides, `shelves` fixed shelves equally spaced,
    recessed plinth rail, back panel nailed on the back (2 mm inside the outline). depth includes the back."""
    coll = coll or get_collection(name)
    P, m = Parts(), material(carcass_mat)
    yf, yb = -depth / 2, depth / 2 - back_t
    xi = width / 2 - t
    for s in (-1, 1):
        x0, x1 = sorted((s * width / 2, s * xi))
        P.box("side", (x0, yf, 0.0), (x1, yb, height), m)
    P.box("top", (-xi, yf, height - t), (xi, yb, height), m)
    P.box("bottom", (-xi, yf, plinth_h), (xi, yb, plinth_h + t), m)
    P.box("plinth", (-xi, yf + plinth_setback, 0.0), (xi, yf + plinth_setback + t, plinth_h), m)
    P.box("back", (-width / 2 + 0.002, yb, 0.002), (width / 2 - 0.002, depth / 2, height - 0.002), m)
    z0, z1 = plinth_h + t, height - t
    clear = (z1 - z0 - shelves * t) / (shelves + 1)
    for i in range(shelves):
        zb = z0 + (i + 1) * clear + i * t
        P.box("shelf", (-xi, yf + shelf_setback, zb), (xi, yb, zb + t), m)
    obj = P.to_object(name, coll, meters_per_uv)
    return _tag(obj, (-width / 2, width / 2, -depth / 2, depth / 2),
                [((-width / 2, -depth / 2, 0.0), (width / 2, depth / 2, height))],
                shelf_clear=clear, shelf_span=2 * xi)


# ------------------------------------------------------------------ shared carcass
def _carcass(P, m, width, depth_c, y0, z_top, t, back_t, base, plinth_h, plinth_setback, leg_h, leg, foot_mat):
    """Box carcass between y0 (front edge) and y0 + depth_c (back face). Returns key heights."""
    xi = width / 2 - t
    yb = y0 + depth_c - back_t
    if base == "PLINTH":       # sides to the floor, recessed kick board (wardrobes, sideboards)
        zs, zb = 0.0, plinth_h
        P.box("plinth", (-xi, y0 + plinth_setback, 0.0), (xi, y0 + plinth_setback + t, plinth_h), m)
    elif base == "KICK":       # EU kitchen: carcass on hidden feet, full-width recessed plinth panel
        zs = zb = plinth_h
        P.box("plinth", (-width / 2, y0 + plinth_setback, 0.0), (width / 2, y0 + plinth_setback + t, plinth_h), m)
    elif base == "LEGS":
        zs = zb = leg_h
        for sx in (-1, 1):
            for sy in (0, 1):
                x0, x1 = sorted((sx * (xi - 0.01), sx * (xi - 0.01 - leg)))
                yy = y0 + 0.03 if sy == 0 else yb - 0.03 - leg
                P.box("leg", (x0, yy, 0.0), (x1, yy + leg, leg_h), foot_mat)
    else:                      # "NONE": wall unit / sits on something
        zs = zb = 0.0
    for s in (-1, 1):
        x0, x1 = sorted((s * width / 2, s * xi))
        P.box("side", (x0, y0, zs), (x1, yb, z_top), m)
    P.box("bottom", (-xi, y0, zb), (xi, yb, zb + t), m)
    P.box("top", (-xi, y0, z_top - t), (xi, yb, z_top), m)
    P.box("back", (-width / 2 + 0.002, yb, zs + 0.002), (width / 2 - 0.002, y0 + depth_c, z_top - 0.002), m)
    return {"xi": xi, "yb": yb, "zs": zs, "zb": zb}


def _handle(P, kind, cx, cz, y_face, mat, length=0.128, vertical=True):
    """Bar handle (2 posts + bar, standing 25 mm proud) or round knob on a front whose face is at y_face."""
    if kind == "KNOB":                                    # square 30 mm knob, 25 mm proud
        P.box("knob", (cx - 0.015, y_face - 0.025, cz - 0.015), (cx + 0.015, y_face, cz + 0.015), mat)
        return
    d, s = 0.012, 0.025
    for k in (-1, 1):
        px, pz = (cx, cz + k * length / 2) if vertical else (cx + k * length / 2, cz)
        P.box("handle_post", (px - 0.004, y_face - s + d, pz - 0.004), (px + 0.004, y_face, pz + 0.004), mat)
    hl = length / 2 + 0.02
    if vertical:
        P.box("handle_bar", (cx - d / 2, y_face - s, cz - hl), (cx + d / 2, y_face - s + d, cz + hl), mat)
    else:
        P.box("handle_bar", (cx - hl, y_face - s, cz - d / 2), (cx + hl, y_face - s + d, cz + d / 2), mat)


# ------------------------------------------------------------------ cabinet / wardrobe / kitchen unit
def make_cabinet(name="cabinet_01", width=0.8, height=0.9, depth=0.58, t=0.018, back_t=0.003, door_t=0.019,
                 gap=0.003, base="PLINTH", plinth_h=0.10, plinth_setback=0.05, leg_h=0.15, leg=0.035,
                 worktop_t=0.0, worktop_overhang=0.02, n_doors=None, max_door_w=0.6, hinge="LEFT",
                 handle="BAR_V", handle_z=None, handle_len=0.128, shelves=0, separate_doors=False,
                 carcass_mat="laminate", front_mat="lacquer", handle_mat="metal", worktop_mat="stone",
                 coll=None, meters_per_uv=1.0):
    """Full-overlay doors with `gap` between doors and gap/2 at the outer edges. height = floor to the
    top surface (incl. worktop); depth = carcass + doors (handles and worktop overhang excluded).
    base: PLINTH | KICK | LEGS | NONE. separate_doors: each door (+ handle) becomes its own object with
    the origin on the hinge axis (outer back edge, bottom) for animation."""
    coll = coll or get_collection(name)
    P, mc, mfr, mh = Parts(), material(carcass_mat), material(front_mat), material(handle_mat)
    z_top = height - worktop_t
    y_face = -depth / 2 + door_t                                   # carcass front plane = door back face
    k = _carcass(P, mc, width, depth - door_t, y_face, z_top, t, back_t, base, plinth_h, plinth_setback,
                 leg_h, leg, mh)
    if worktop_t > 0:
        P.box("worktop", (-width / 2, -depth / 2 - worktop_overhang, z_top), (width / 2, depth / 2, height),
              material(worktop_mat))
    for i in range(shelves):
        z = k["zb"] + t + (i + 1) * (z_top - t - k["zb"] - t) / (shelves + 1)
        P.box("shelf", (-k["xi"], y_face + 0.02, z - t / 2), (k["xi"], k["yb"], z + t / 2), mc)
    n = n_doors or max(1, math.ceil((width - gap) / max_door_w))
    dw = (width - n * gap) / n
    dz0, dz1 = k["zb"] + gap / 2, z_top - gap / 2
    if handle_z is None:
        handle_z = 1.0 if height > 1.5 else (dz0 + 0.07 if base == "NONE" else dz1 - 0.07)
    doors = []
    for i in range(n):
        x0 = -width / 2 + gap / 2 + i * (dw + gap)
        hinge_left = (i < n / 2) if n > 1 else (hinge == "LEFT")
        D = Parts() if separate_doors else P
        D.box("door", (x0, -depth / 2, dz0), (x0 + dw, y_face, dz1), mfr)
        if handle != "NONE":
            free_x = x0 + dw - 0.035 if hinge_left else x0 + 0.035
            if handle == "BAR_H":
                _handle(D, handle, x0 + dw / 2, dz1 - 0.05 if handle_z > dz1 - 0.1 else handle_z,
                        -depth / 2, mh, handle_len, vertical=False)
            else:
                _handle(D, handle, free_x, min(max(handle_z, dz0 + 0.1), dz1 - 0.1), -depth / 2, mh, handle_len)
        doors.append({"x0": x0, "x1": x0 + dw, "z0": dz0, "z1": dz1, "hinge_left": hinge_left, "parts": D})
    obj = P.to_object(name, coll, meters_per_uv)
    door_objs = []
    if separate_doors:
        for i, d in enumerate(doors):
            pivot = Vector((d["x0"] if d["hinge_left"] else d["x1"], y_face, d["z0"]))
            bmesh.ops.translate(d["parts"].bm, vec=-pivot, verts=d["parts"].bm.verts)
            dob = d["parts"].to_object(f"{name}_door_{i:02d}", coll, meters_per_uv)
            dob.parent = obj
            dob.location = pivot
            dob["hinge"] = "LEFT" if d["hinge_left"] else "RIGHT"
            door_objs.append(dob)
    obj["doors"] = [[d["x0"], d["x1"], d["z0"], d["z1"]] for d in doors]
    obj["door_objects"] = [o.name for o in door_objs]
    y_min = -depth / 2 - (worktop_overhang if worktop_t > 0 else 0.0)
    return _tag(obj, (-width / 2, width / 2, -depth / 2, depth / 2),
                [((-width / 2, y_min, 0.0), (width / 2, depth / 2, height))], y_face=y_face)


# ------------------------------------------------------------------ drawer unit / dresser / nightstand
def make_drawer_unit(name="drawers_01", width=0.8, height=0.8, depth=0.48, t=0.018, back_t=0.003,
                     front_t=0.019, gap=0.003, drawers=4, graduated=True, base="PLINTH", plinth_h=0.06,
                     plinth_setback=0.03, leg_h=0.15, leg=0.035, handle="BAR_H", handle_len=0.16,
                     drawer_boxes=False, side_clear=0.0125, carcass_mat="wood", front_mat="wood",
                     handle_mat="metal", coll=None, meters_per_uv=1.0):
    """Carcass + stacked overlay drawer fronts (smallest on top when graduated) with `gap` between them.
    drawer_boxes: 12 mm sides/back + 6 mm bottom behind each front (only worth it if drawers open)."""
    coll = coll or get_collection(name)
    P, mc, mfr, mh = Parts(), material(carcass_mat), material(front_mat), material(handle_mat)
    y_face = -depth / 2 + front_t
    k = _carcass(P, mc, width, depth - front_t, y_face, height, t, back_t, base, plinth_h, plinth_setback,
                 leg_h, leg, mh)
    avail = height - k["zb"] - drawers * gap
    weights = [1.0 + 0.15 * i for i in range(drawers)] if graduated else [1.0] * drawers
    heights = [avail * w / sum(weights) for w in reversed(weights)]          # bottom drawer first (largest)
    fronts, z = [], k["zb"] + gap / 2
    for i, fh in enumerate(heights):
        P.box("drawer_front", (-width / 2 + gap / 2, -depth / 2, z), (width / 2 - gap / 2, y_face, z + fh), mfr)
        if handle != "NONE":
            _handle(P, handle, 0.0, z + fh / 2, -depth / 2, mh, handle_len, vertical=False)
        if drawer_boxes:
            bx0, bx1 = -k["xi"] + side_clear, k["xi"] - side_clear
            by0, by1 = y_face, k["yb"] - 0.02
            bz0, bz1 = max(z + 0.015, k["zb"] + t + 0.003), min(z + fh - 0.03, height - t - 0.003)
            if bz1 - bz0 > 0.04:
                P.box("drawer_side", (bx0, by0, bz0), (bx0 + 0.012, by1, bz1), mc)
                P.box("drawer_side", (bx1 - 0.012, by0, bz0), (bx1, by1, bz1), mc)
                P.box("drawer_back", (bx0 + 0.012, by1 - 0.012, bz0), (bx1 - 0.012, by1, bz1), mc)
                P.box("drawer_bottom", (bx0 + 0.012, by0, bz0), (bx1 - 0.012, by1 - 0.012, bz0 + 0.006), mc)
        fronts.append([z, z + fh])
        z += fh + gap
    obj = P.to_object(name, coll, meters_per_uv)
    obj["fronts"] = fronts
    return _tag(obj, (-width / 2, width / 2, -depth / 2, depth / 2),
                [((-width / 2, -depth / 2, 0.0), (width / 2, depth / 2, height))], y_face=y_face)


# ------------------------------------------------------------------ bed frame
def make_bed_frame(name="bed_01", mattress="EU_160x200", mattress_t=0.20, mattress_top=0.52, clearance=0.01,
                   rail_t=0.03, rail_h=0.20, mattress_above_rail=0.12, leg=0.07, headboard_h=1.0,
                   headboard_t=0.04, footboard_h=0.0, slat_w=0.065, slat_gap=0.05, frame_mat="wood",
                   coll=None, meters_per_uv=1.0):
    """Frame sized from the mattress (inner opening = mattress + 2*clearance), slats on ledgers at
    mattress_top - mattress_t, side/end rails, 4 legs (+ centre legs from 1.4 m width), headboard.
    The mattress itself belongs to blender-soft-furniture: obj['mattress'] = [w, l, t, x, y, z_bottom]."""
    coll = coll or get_collection(name)
    mw, ml = MATTRESSES[mattress] if isinstance(mattress, str) else mattress
    P, m = Parts(), material(frame_mat)
    iw, il = mw + 2 * clearance, ml + 2 * clearance
    ow, ol = iw + 2 * rail_t, il + 2 * rail_t
    y_head, y_foot = ol / 2 + headboard_t, -ol / 2                  # headboard on +Y, foot end faces -Y
    zsl = mattress_top - mattress_t                                   # slat top
    zr1 = zsl + mattress_t - mattress_above_rail                      # rail top
    zr0 = zr1 - rail_h
    assert zr0 > 0.05 and zsl - 0.02 - 0.025 > zr0, "rails too low for this mattress height"
    for s in (-1, 1):
        x0, x1 = sorted((s * ow / 2, s * iw / 2))
        P.box("side_rail", (x0, -il / 2, zr0), (x1, il / 2, zr1), m)
        y0, y1 = sorted((s * ol / 2, s * il / 2))
        P.box("end_rail", (-ow / 2, y0, zr0), (ow / 2, y1, zr1), m)
        lx0, lx1 = sorted((s * iw / 2, s * (iw / 2 - 0.02)))
        P.box("ledger", (lx0, -il / 2, zsl - 0.02 - 0.025), (lx1, il / 2, zsl - 0.02), m)
    xs = [-1, 1] if ow < 1.4 else [-1, 0, 1]
    for sx in xs:
        for sy in (-1, 1):
            cx = sx * (ow / 2 - leg / 2) if sx else 0.0
            cy = sy * (ol / 2 - leg / 2)
            P.box("leg", (cx - leg / 2, cy - leg / 2, 0.0), (cx + leg / 2, cy + leg / 2, zr0), m)
    n = int((il + slat_gap) // (slat_w + slat_gap))
    pitch = (il - n * slat_w) / (n + 1)
    for i in range(n):
        y = -il / 2 + pitch + i * (slat_w + pitch)
        P.box("slat", (-iw / 2 + 0.002, y, zsl - 0.02), (iw / 2 - 0.002, y + slat_w, zsl), m)
    P.box("headboard", (-ow / 2, ol / 2, 0.0), (ow / 2, y_head, headboard_h), m)
    if footboard_h:
        P.box("footboard", (-ow / 2, y_foot - headboard_t, 0.0), (ow / 2, y_foot, footboard_h), m)
        y_foot -= headboard_t
    obj = P.to_object(name, coll, meters_per_uv)
    obj["mattress"] = [mw, ml, mattress_t, 0.0, 0.0, zsl]
    obj["slat_pitch"] = pitch
    return _tag(obj, (-ow / 2, ow / 2, y_foot, y_head),
                [((-ow / 2, y_foot, 0.0), (ow / 2, ol / 2, mattress_top)),
                 ((-ow / 2, ol / 2, 0.0), (ow / 2, y_head, headboard_h))])


# ------------------------------------------------------------------ billiard / pool table
def make_billiard_table(name="pool_table_01", size="9ft", bed_h=0.762, ball_d=2.25 * IN, nose_ratio=0.635,
                        cushion_w=2.0 * IN, rail_wood=0.10, rail_rise=0.045, slate_t=0.025, apron_h=0.20,
                        leg=0.12, corner_mouth=4.5625 * IN, side_mouth=5.0625 * IN, diamonds=True,
                        frame_mat="wood_dark", cloth_mat="felt", coll=None, meters_per_uv=1.0):
    """Pool table with measured placeholders: playing surface `size` between the cushion noses at bed_h,
    cushion nose at nose_ratio * ball_d above the cloth, square-cut cushions that leave the pocket mouths
    (corner mouth across the corner between nose ends, side mouth along the rail), wooden rails open at
    the pockets, slate, apron, legs, pocket cups below the cloth plane, 18 sights 3 11/16 in from the nose.
    Replace pockets/jaws with modelled ones later; keep the measured mouths and nose height."""
    coll = coll or get_collection(name)
    pl, pw = POOL_TABLES[size] if isinstance(size, str) else size
    P = Parts()
    mfr, mcl, mru, mme = material(frame_mat), material(cloth_mat), material("rubber"), material("metal")
    W, L = pw + 2 * (cushion_w + rail_wood), pl + 2 * (cushion_w + rail_wood)
    nose_z, top_z, z_slate = bed_h + nose_ratio * ball_d, bed_h + rail_rise, bed_h - slate_t
    bx, by = pw / 2 + cushion_w, pl / 2 + cushion_w                   # rail inner faces = slate edge
    P.box("bed", (-bx, -by, z_slate), (bx, by, bed_h), mcl)
    za = z_slate - apron_h
    P.box("apron", (-W / 2 + 0.02, -L / 2 + 0.02, za), (W / 2 - 0.02, L / 2 - 0.02, z_slate), mfr)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (W / 2 - 0.06 - leg / 2), sy * (L / 2 - 0.06 - leg / 2)
            P.box("leg", (cx - leg / 2, cy - leg / 2, 0.0), (cx + leg / 2, cy + leg / 2, za), mfr)
    e = corner_mouth / math.sqrt(2)                                     # cushion end -> nose corner distance
    prof = [(0.0, bed_h + 0.004), (cushion_w, nose_z - 0.006), (cushion_w, nose_z), (0.0, top_z - 0.004)]
    long_segs = [(-pl / 2 + e, -side_mouth / 2), (side_mouth / 2, pl / 2 - e)]
    for s in (-1, 1):
        for y0, y1 in long_segs:
            P.extrusion("cushion_long", [(s * (bx - u), z) for u, z in prof], "Y", y0, y1, mcl)
            P.box("rail_long", (min(s * bx, s * W / 2), y0, z_slate), (max(s * bx, s * W / 2), y1, top_z), mfr)
        P.extrusion("cushion_short", [(s * (by - u), z) for u, z in prof], "X", -pw / 2 + e, pw / 2 - e, mcl)
        P.box("rail_short", (-pw / 2 + e, min(s * by, s * L / 2), z_slate), (pw / 2 - e, max(s * by, s * L / 2), top_z), mfr)
    pockets = [(sx * (pw / 2 + 0.03), sy * (pl / 2 + 0.03), 0.06) for sx in (-1, 1) for sy in (-1, 1)]
    pockets += [(sx * (bx + 0.045), 0.0, 0.05) for sx in (-1, 1)]
    for px, py, r in pockets:                                           # top 3 mm under the cloth plane
        P.cylinder("pocket_cup", (px, py, z_slate - 0.10), r, bed_h - 0.003 - (z_slate - 0.10), mru, 16)
    if diamonds:
        sight = 3.6875 * IN
        spots = [(s * (pw / 2 + sight), -pl / 2 + i * pl / 8) for s in (-1, 1) for i in (1, 2, 3, 5, 6, 7)]
        spots += [(-pw / 2 + i * pw / 4, s * (pl / 2 + sight)) for s in (-1, 1) for i in (1, 2, 3)]
        for x, y in spots:
            P.box("sight", (x - 0.006, y - 0.006, top_z), (x + 0.006, y + 0.006, top_z + 0.0015), mme)
    obj = P.to_object(name, coll, meters_per_uv)
    obj["play"] = [pw, pl]
    obj["nose_z"] = nose_z
    obj["pockets"] = [list(p) for p in pockets]
    return _tag(obj, (-W / 2, W / 2, -L / 2, L / 2),
                [((-W / 2, -L / 2, 0.0), (W / 2, L / 2, bed_h)),
                 ((-W / 2, -L / 2, bed_h), (-pw / 2, L / 2, top_z)), ((pw / 2, -L / 2, bed_h), (W / 2, L / 2, top_z)),
                 ((-pw / 2, -L / 2, bed_h), (pw / 2, -pl / 2, top_z)), ((-pw / 2, pl / 2, bed_h), (pw / 2, L / 2, top_z))])


# ------------------------------------------------------------------ realism + cleanup pass
def finalize(obj, bevel_width=0.002, bevel_segments=2, bevel_angle=30.0, weighted_normal=True,
             merge_dist=1e-5, meters_per_uv=None, triangulate=False, keep_origin=False):
    """Apply rotation/scale, merge by distance PER PART, drop loose/degenerate geometry, recalc normals,
    origin -> bottom centre of the footprint, optional UV re-projection, smooth shading + Bevel (weight
    limited, Harden Normals, Miter Outer Arc, Clamp Overlap) + Weighted Normal (+ Triangulate).
    Parts thinner than 2.5 x bevel get a proportionally smaller bevel, so one 3 mm back panel no longer
    clamps the bevel of the whole object (Clamp Overlap is object-wide)."""
    me = obj.data
    loc, rot, scale = obj.matrix_basis.decompose()
    rs = Matrix.LocRotScale(None, rot, scale)
    if rs != Matrix.Identity(4):
        me.transform(rs)
        if rs.determinant() < 0:
            me.flip_normals()
        obj.matrix_basis = Matrix.Translation(loc)
    bm = bmesh.new()
    bm.from_mesh(me)
    for isl in islands(bm):
        bmesh.ops.remove_doubles(bm, verts=list({v for f in isl for v in f.verts}), dist=merge_dist)
    bmesh.ops.dissolve_degenerate(bm, dist=merge_dist, edges=bm.edges[:])
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    fp = obj.get("footprint")
    xs, ys = [v.co.x for v in bm.verts], [v.co.y for v in bm.verts]
    x0, x1, y0, y1 = list(fp) if fp else (min(xs), max(xs), min(ys), max(ys))
    off = Vector(((x0 + x1) / 2, (y0 + y1) / 2, min(v.co.z for v in bm.verts)))
    if keep_origin:                                          # e.g. door leaves: origin = hinge axis
        off = Vector()
    if off.length > EPS:
        bmesh.ops.translate(bm, vec=-off, verts=bm.verts)
        obj.location += off
        if fp:
            obj["footprint"] = [x0 - off.x, x1 - off.x, y0 - off.y, y1 - off.y]
        if obj.get("col_boxes"):
            obj["col_boxes"] = [[b[0] - off.x, b[1] - off.y, b[2] - off.z, b[3] - off.x, b[4] - off.y, b[5] - off.z]
                                for b in obj["col_boxes"]]
        if obj.get("mattress"):
            m = list(obj["mattress"])
            obj["mattress"] = m[:3] + [m[3] - off.x, m[4] - off.y, m[5] - off.z]
    if meters_per_uv:
        layer = bm.faces.layers.int.get("part")
        uv_grain_project(bm, layer, meters_per_uv)
    # bevel weights: dihedral >= bevel_angle, scaled down on thin parts
    thin_w = {}
    for isl in islands(bm):
        vs = {v for f in isl for v in f.verts}
        pts = [v.co for v in vs]
        dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
        w = min(1.0, min(dims) / (2.5 * bevel_width)) if bevel_width > 0 else 0.0
        for f in isl:
            for e in f.edges:
                thin_w[e] = w
    weights = [thin_w.get(e, 0.0) if e.is_manifold and e.calc_face_angle(0.0) >= math.radians(bevel_angle) - 1e-4
               else 0.0 for e in bm.edges]
    bm.to_mesh(me)
    bm.free()
    attr = me.attributes.get("bevel_weight_edge") or me.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    attr.data.foreach_set("value", weights)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    for mod in [m for m in obj.modifiers if m.type in {"BEVEL", "WEIGHTED_NORMAL", "TRIANGULATE"}]:
        obj.modifiers.remove(mod)
    if bevel_width > 0:
        bev = obj.modifiers.new("Bevel", "BEVEL")
        bev.width, bev.segments, bev.profile = bevel_width, bevel_segments, 0.5
        bev.limit_method = "WEIGHT"
        bev.harden_normals = True
        bev.miter_outer = "MITER_ARC"
        bev.use_clamp_overlap = True
    if weighted_normal:
        wn = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        wn.mode, wn.weight, wn.keep_sharp = "FACE_AREA", 50, True
    if triangulate:
        tri = obj.modifiers.new("Triangulate", "TRIANGULATE")
        tri.keep_custom_normals = True
    return {"offset": tuple(off), "tris": tri_count(obj)}


def tri_count(obj, evaluated=True):
    if not evaluated:
        return sum(len(p.vertices) - 2 for p in obj.data.polygons)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    m = ev.to_mesh()
    n = sum(len(p.vertices) - 2 for p in m.polygons)
    ev.to_mesh_clear()
    return n


def _box_mesh(name, boxes):
    bm = bmesh.new()
    for b in boxes:
        mn, mx = Vector(b[:3]), Vector(b[3:])
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.LocRotScale((mn + mx) / 2, None, mx - mn))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def make_collision(obj, style="UE"):
    """UE: one UCX_<name>_NN object per collision box (convex, same transform, export in the same FBX).
    SOLLUMZ: Drawable hierarchy like fivem-mlo-doors-windows make_asset: <name> (empty) > <name>.model +
    <name>.col > <name>.col.box<i>; returns the asset dict sz_convert() expects."""
    coll = obj.users_collection[0]
    boxes = [list(b) for b in obj["col_boxes"]]
    if style == "UE":
        out = []
        for i, b in enumerate(boxes):
            c = bpy.data.objects.new(f"UCX_{obj.name}_{i:02d}", _box_mesh(f"UCX_{obj.name}_{i:02d}", [b]))
            coll.objects.link(c)
            c.matrix_world = obj.matrix_basis.copy()
            c.display_type = "WIRE"
            out.append(c)
        return out
    name = obj.name
    drawable = bpy.data.objects.new(name + ".tmp", None)
    coll.objects.link(drawable)
    drawable.matrix_world = obj.matrix_basis.copy()
    obj.name = f"{name}.model"
    drawable.name = name
    obj.parent = drawable
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Identity(4)
    comp = bpy.data.objects.new(f"{name}.col", None)
    coll.objects.link(comp)
    comp.parent = drawable
    bounds = []
    for i, b in enumerate(boxes):
        mn, mx = Vector(b[:3]), Vector(b[3:])
        h = (mx - mn) / 2
        bo = bpy.data.objects.new(f"{name}.col.box{i}", _box_mesh(f"{name}.col.box{i}", [list(-h) + list(h)]))
        coll.objects.link(bo)
        bo.parent = comp
        bo.location = (mn + mx) / 2                                 # Sollumz box bound: centred on its origin
        bo.display_type = "WIRE"
        bounds.append(bo)
    drawable["sz_collision_material"] = "WOOD_SOLID_MEDIUM"
    return {"drawable": drawable, "model": obj, "composite": comp, "bounds": bounds, "lods": make_lods(obj)}


def make_lods(obj):
    """LOD1 = base mesh without bevel modifiers (same UVs/materials); LOD2 = collision boxes only."""
    lod1 = obj.data.copy()
    lod1.name = f"{obj.name}_LOD1"
    lod2 = _box_mesh(f"{obj.name}_LOD2", obj["col_boxes"])
    for m in obj.data.materials[:1]:
        lod2.materials.append(m)
    for me in (lod1, lod2):
        me.use_fake_user = True
    return [lod1, lod2]


def build_demo():
    """One of each, spaced along X. Run: blender -b -P furniture_gen.py"""
    items = [make_table(), make_chair(), make_bar_stool(), make_shelf(),
             make_cabinet("kitchen_base_01", width=0.6, height=0.9, depth=0.58, base="KICK", plinth_h=0.15,
                          worktop_t=0.038, handle="BAR_H"),
             make_cabinet("wardrobe_01", width=1.0, height=2.01, depth=0.6, base="PLINTH", plinth_h=0.08,
                          back_t=0.003, carcass_mat="laminate"),
             make_drawer_unit(), make_bed_frame(), make_billiard_table()]
    x = 0.0
    for ob in items:
        finalize(ob)
        fp = ob["footprint"]
        ob.location.x = x - fp[0]
        x += fp[1] - fp[0] + 0.5
    bpy.context.view_layer.update()
    return items


if __name__ == "__main__":
    build_demo()
```
