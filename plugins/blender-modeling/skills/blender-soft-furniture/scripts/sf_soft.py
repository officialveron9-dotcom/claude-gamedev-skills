"""sf_soft.py - soft furniture helpers: pillows/cushions, mattress, blanket drape, tufting, curtains,
game-ready pass. Pure bpy/bmesh, no add-ons. Runs headless (`blender -b -P`, the `bpy` pip module) or
through a Blender MCP. Tested on Blender 5.2.2 LTS and 4.5.14 LTS (bpy module, headless);
see references/scripts.md.

Usage:
    import sys; sys.path.append("<skill>/scripts"); import sf_soft as SF
    p = SF.make_pillow("Pillow", shape="KNIFE", size=(0.5, 0.5))          # builds, simulates, applies
    m = SF.make_mattress("Mattress", size=(1.6, 2.0, 0.24))
    b = SF.drape_blanket(m, size=(2.2, 2.3), fold_back=0.35)              # drapes, applies, solidifies
    SF.add_tufting(cushion, spacing=(0.12, 0.12)); SF.place_buttons(cushion, spacing=(0.12, 0.12))
    lods, col = SF.game_ready(p, lod_ratios=(1.0, 0.5, 0.25), target_tris=1500)

All sizes are metres, object-local. Every function returns the object(s) it made; nothing is
selected or made active, so the user's selection survives MCP calls.
"""
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

V = bpy.app.version


# ----------------------------------------------------------------------------- basics
def _coll():
    return getattr(bpy.context, "collection", None) or bpy.context.scene.collection


def _obj_from_bm(name, bm, coll=None):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    ob = bpy.data.objects.new(name, me)
    (coll or _coll()).objects.link(ob)
    return ob


def _vgroup(ob, name, weights):
    """weights: dict vertex_index -> weight (0..1). Replaces an existing group of that name."""
    old = ob.vertex_groups.get(name)
    if old:
        ob.vertex_groups.remove(old)
    vg = ob.vertex_groups.new(name=name)
    for i, w in weights.items():
        if w > 0.0:
            vg.add([i], float(min(1.0, w)), 'REPLACE')
    return vg


def _smooth(ob):
    ob.data.shade_smooth()          # Mesh.shade_smooth(): 4.1+


def stats(ob, evaluated=True):
    """Counts and bounds of the (evaluated) mesh in world space; raises on NaN/inf."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    src = ob.evaluated_get(dg) if evaluated else ob
    me = src.to_mesh()
    try:
        co = [ob.matrix_world @ v.co for v in me.vertices]
        if any(not math.isfinite(c) for p in co for c in p):
            raise ValueError(f"{ob.name}: NaN/inf vertex positions (cloth exploded)")
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        mn = Vector((min(p.x for p in co), min(p.y for p in co), min(p.z for p in co)))
        mx = Vector((max(p.x for p in co), max(p.y for p in co), max(p.z for p in co)))
        bm = bmesh.new()
        bm.from_mesh(me)
        nonmanifold = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
        boundary = sum(1 for e in bm.edges if e.is_boundary)
        bm.free()
        return {"verts": len(me.vertices), "tris": tris, "min": tuple(mn), "max": tuple(mx),
                "dims": tuple(mx - mn), "nonmanifold_edges": nonmanifold, "boundary_edges": boundary}
    finally:
        src.to_mesh_clear()


def _bvh(ob, world=True):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    me = oe.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    oe.to_mesh_clear()
    if world:
        bm.transform(ob.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    tri_verts = [tuple(v.index for v in f.verts) for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    coords = [v.co.copy() for v in bm.verts]
    bm.free()
    return tree, tri_verts, coords


def self_intersections(ob):
    """Number of intersecting triangle pairs that share no vertex (0 = clean)."""
    tree, tris, _ = _bvh(ob)
    return sum(1 for a, b in tree.overlap(tree) if a < b and not set(tris[a]) & set(tris[b]))


def intersections(ob_a, ob_b):
    """Number of intersecting triangle pairs between two objects (0 = no clipping)."""
    ta, _, _ = _bvh(ob_a)
    tb, _, _ = _bvh(ob_b)
    return len(ta.overlap(tb))


# ----------------------------------------------------------------------------- base meshes
def _box_grid(W, D, T, res, z_cuts):
    """Closed box W x D x T centred on the origin, quads of ~res on top/bottom, z_cuts loops on the band."""
    # Six grids welded at the borders. (bmesh.ops.subdivide_edges on only the X or Y edges of a cube
    # leaves 28-gons instead of a grid - tested 5.2.2 - and n-gons make cloth fold and twist.)
    n = (max(1, round(W / res)), max(1, round(D / res)), z_cuts + 1)
    size = (W, D, T)
    bm = bmesh.new()
    for axis in range(3):
        a, b = [i for i in range(3) if i != axis]
        for sign in (-1, 1):
            grid = []
            for i in range(n[a] + 1):
                row = []
                for j in range(n[b] + 1):
                    co = [0.0, 0.0, 0.0]
                    co[axis] = sign * size[axis] / 2
                    co[a] = -size[a] / 2 + size[a] * i / n[a]
                    co[b] = -size[b] / 2 + size[b] * j / n[b]
                    row.append(bm.verts.new(co))
                grid.append(row)
            for i in range(n[a]):
                for j in range(n[b]):
                    bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    step = min(s / k for s, k in zip(size, n))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=step * 0.01)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def _revolve(profile, segs, axis="Z"):
    """Closed surface of revolution. profile = [(r, h), ...] from pole to pole (first/last r == 0)."""
    rings = profile[1:-1]
    verts, faces = [], []

    def put(r, h, a):
        c, s = r * math.cos(a), r * math.sin(a)
        return (c, s, h) if axis == "Z" else (h, c, s)

    verts.append(put(0, profile[0][1], 0))
    for r, h in rings:
        for s in range(segs):
            verts.append(put(r, h, 2 * math.pi * s / segs))
    verts.append(put(0, profile[-1][1], 0))
    last = len(verts) - 1

    def idx(i, s):
        return 1 + i * segs + (s % segs)

    for s in range(segs):
        faces.append((0, idx(0, s), idx(0, s + 1)))
        faces.append((last, idx(len(rings) - 1, s + 1), idx(len(rings) - 1, s)))
    for i in range(len(rings) - 1):
        for s in range(segs):
            faces.append((idx(i, s), idx(i + 1, s), idx(i + 1, s + 1), idx(i, s + 1)))
    bm = bmesh.new()
    bvs = [bm.verts.new(v) for v in verts]
    for f in faces:
        bm.faces.new([bvs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def pillow_base(name="Pillow", shape="KNIFE", size=(0.5, 0.5), thickness=None, res=0.02):
    """Closed, manifold pillow shell before inflation. Vertex group 'seam' marks the seam loop(s).

    KNIFE   throw pillow: two panels joined at one edge seam (thin 2 cm band with a centre loop).
    BOX     box/seat cushion: top + bottom panel + gusset band of height `thickness` (two welts).
    ROUND   round pillow: size=(diameter, _), thin band with a centre seam.
    BOLSTER cylinder along X: size=(length, diameter), seams at both cap rims.
    """
    W, D = size
    if shape == "KNIFE":
        T = thickness or 0.02
        bm = _box_grid(W, D, T, res, z_cuts=1)
        seam = lambda co: abs(co.z) < 1e-6
    elif shape == "BOX":
        T = thickness or 0.10
        bm = _box_grid(W, D, T, res, z_cuts=max(1, round(T / res) - 1))
        seam = lambda co: abs(abs(co.z) - T / 2) < 1e-6 and (
            abs(abs(co.x) - W / 2) < 1e-6 or abs(abs(co.y) - D / 2) < 1e-6)
    elif shape == "ROUND":
        # Square KNIFE grid mapped onto a disc (elliptical grid mapping): all quads, no pole.
        # A revolved disc (pole + radial rings) barely inflated at the same pressure (tested 5.2.2).
        R, T = W / 2, thickness or 0.02
        bm = _box_grid(W, W, T, res, z_cuts=1)
        for v in bm.verts:
            x, y = v.co.x / R, v.co.y / R
            v.co.x = R * x * math.sqrt(max(0.0, 1 - y * y / 2))
            v.co.y = R * y * math.sqrt(max(0.0, 1 - x * x / 2))
        seam = lambda co: abs(co.z) < 1e-6
    elif shape == "BOLSTER":
        L, R = W, D / 2
        n, m, segs = max(3, round(R / res)), max(2, round(L / res)), max(16, round(2 * math.pi * R / res))
        prof = [(R * k / n, L / 2) for k in range(n + 1)] + \
               [(R, L / 2 - L * j / m) for j in range(1, m)] + \
               [(R * k / n, -L / 2) for k in range(n, -1, -1)]
        bm = _revolve(prof, segs, "X")
        seam = lambda co: abs(abs(co.x) - L / 2) < 1e-6 and co.yz.length > R * 0.99
    else:
        raise ValueError(f"unknown shape {shape!r}")
    bm.verts.index_update()                      # ops leave .index stale; to_mesh keeps this order
    seam_idx = {v.index: 1.0 for v in bm.verts if seam(v.co)}
    ob = _obj_from_bm(name, bm)
    _vgroup(ob, "seam", seam_idx)
    _smooth(ob)
    return ob


# ----------------------------------------------------------------------------- cloth
def cloth_of(ob):
    return next((m for m in ob.modifiers if m.type == 'CLOTH'), None)


# Presets measured headless (5.2.2, quality 8, 45 frames). Pressure is per area but the mass-spring
# membrane stiffens as edges get shorter, so pressure must scale with edge length `res`:
# KNIFE 0.5 m: P 1.0 @ 2 cm -> thickness/width 0.26; P 1.0 @ 1 cm -> 0.50 (balloon); P 0.5 @ 1 cm -> 0.28.
PILLOW_PRESETS = {
    #           pressure per metre of edge, shrink, bending, self-collision
    "KNIFE":   (60.0, 0.10, 0.5, False),  # throw pillow, thickness/width ~0.29
    "BOX":     (15.0, 0.05, 2.0, False),  # seat cushion 0.6x0.6x0.10 -> 0.15 thick, 2.2 cm crown
    "ROUND":   (30.0, 0.02, 0.5, True),   # without self-collision the seam pinch folds through itself
                                          # (26 tri pairs); with it, shrink drives thickness (0.06 -> 0.53)
    "BOLSTER": (50.0, 0.05, 0.5, False),
}


def add_pillow_cloth(ob, shape="KNIFE", res=0.02, pressure=None, shrink=None, bending=None, quality=8,
                     frames=45, self_collision=None):
    """Inflation setup: gravity 0, Pressure on, slight Shrink so the panels pull and the corners pinch.
    pressure/shrink/bending default to PILLOW_PRESETS[shape] scaled to the mesh edge length `res`."""
    k, sh, bd, sc = PILLOW_PRESETS[shape]
    self_collision = sc if self_collision is None else self_collision
    pressure = k * res if pressure is None else pressure
    shrink = sh if shrink is None else shrink
    bending = bd if bending is None else bending
    m = cloth_of(ob) or ob.modifiers.new("Cloth", 'CLOTH')
    s, c = m.settings, m.collision_settings
    s.quality = quality
    s.mass = 0.3
    s.air_damping = 1.0
    s.tension_stiffness = s.compression_stiffness = 15.0
    s.shear_stiffness = 5.0
    s.bending_stiffness = bending
    s.effector_weights.gravity = 0.0          # inflate in place; no collider needed
    s.use_pressure = True
    s.uniform_pressure_force = pressure
    s.pressure_factor = 1.0
    s.shrink_min = shrink                     # setter also raises shrink_max to >= shrink_min
    c.use_collision = False
    c.use_self_collision = self_collision
    c.self_distance_min = 0.003
    m.point_cache.frame_start = 1
    m.point_cache.frame_end = frames
    return m


def simulate(ob, frames=None, method="BAKE"):
    """Run the cloth sim of `ob` from its cache start to `frames`.
    BAKE: bpy.ops.ptcache.bake (synchronous exec path, works headless). STEP: frame_set every frame.
    Never jump straight to the last frame: an unbaked cloth evaluated at a far frame is wrong."""
    sc = bpy.context.scene
    m = cloth_of(ob)
    pc = m.point_cache
    if frames:
        pc.frame_end = frames
    sc.frame_set(pc.frame_start)
    # Objects created in this script are not in the evaluated depsgraph yet: without this the
    # colliders were never registered and the blanket fell straight through (tested 5.2.2).
    bpy.context.view_layer.update()
    bpy.context.evaluated_depsgraph_get()
    if method == "BAKE":
        with bpy.context.temp_override(scene=sc, object=ob, active_object=ob, point_cache=pc):
            bpy.ops.ptcache.free_bake()
            bpy.ops.ptcache.bake(bake=True)
        if not pc.is_baked:
            raise RuntimeError(f"{ob.name}: ptcache.bake finished but cache is not baked ({pc.info})")
    else:
        for f in range(pc.frame_start, pc.frame_end + 1):
            sc.frame_set(f)
    sc.frame_set(pc.frame_end)
    return pc.frame_end


def apply_cloth(ob, frame=None):
    """Freeze the cloth result at `frame` into the mesh (modifiers above Cloth are baked in too,
    modifiers below stay live). Removes the Cloth modifier and frees its cache."""
    sc = bpy.context.scene
    m = cloth_of(ob)
    sc.frame_set(frame or m.point_cache.frame_end)
    mods = list(ob.modifiers)
    ci = mods.index(m)
    below = mods[ci + 1:]
    states = [(x, x.show_viewport) for x in below]
    for x in below:
        x.show_viewport = False
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    for x, st in states:
        x.show_viewport = st
    old = ob.data
    for x in mods[:ci + 1]:
        ob.modifiers.remove(x)
    ob.data = new
    new.name = old.name
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return ob


def max_step(ob, frame):
    """Largest vertex movement between frame-1 and frame (m). < ~0.001 = settled."""
    sc = bpy.context.scene

    def cos(f):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        oe = ob.evaluated_get(dg)
        me = oe.to_mesh()
        out = [v.co.copy() for v in me.vertices]
        oe.to_mesh_clear()
        return out

    a, b = cos(frame - 1), cos(frame)
    return max((p - q).length for p, q in zip(a, b))


def make_pillow(name="Pillow", shape="KNIFE", size=(0.5, 0.5), thickness=None, res=0.02,
                pressure=None, shrink=None, bending=None, frames=45, apply=True, subsurf=1):
    """Build + inflate + apply. Returns the pillow object (cloth removed, Subdivision on top if subsurf)."""
    ob = pillow_base(name, shape, size, thickness, res)
    add_pillow_cloth(ob, shape, res, pressure, shrink, bending, frames=frames)
    simulate(ob, frames)
    if apply:
        apply_cloth(ob)
        if subsurf:
            sd = ob.modifiers.new("Subdivision", 'SUBSURF')
            sd.levels = sd.render_levels = subsurf
    return ob


def add_dent(ob, center, radius=0.12, depth=0.03, direction=(0, 0, -1)):
    """Sculpt-like dent/sag (someone sat or leaned here). Smoothstep falloff, object-local coords."""
    c, d = Vector(center), Vector(direction).normalized() * depth
    me = ob.data
    for v in me.vertices:
        t = (v.co - c).length / radius
        if t < 1.0:
            w = 1 - (3 * t * t - 2 * t * t * t)
            v.co += d * w
    me.update()
    return ob


# ----------------------------------------------------------------------------- piping (welt)
def seam_loops(ob, group="seam"):
    """Ordered vertex-index loops of the edges whose both verts are in `group`."""
    gi = ob.vertex_groups[group].index
    me = ob.data
    inside = {v.index for v in me.vertices for g in v.groups if g.group == gi and g.weight > 0.5}
    adj = {i: [] for i in inside}
    for e in me.edges:
        a, b = e.vertices
        if a in inside and b in inside:
            adj[a].append(b)
            adj[b].append(a)
    loops, seen = [], set()
    for start in inside:
        if start in seen or len(adj[start]) != 2:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            nxt = [n for n in adj[cur] if n != prev]
            if not nxt or nxt[0] == start:
                break
            prev, cur = cur, nxt[0]
            if cur in seen:
                break
            seen.add(cur)
            loop.append(cur)
        if len(loop) > 2:
            loops.append(loop)
    return loops


def add_piping(ob, group="seam", radius=0.004, resolution=2, name=None):
    """Welt/piping cord along every seam loop: poly curve with bevel depth, parented to `ob`."""
    cu = bpy.data.curves.new(name or ob.name + "_piping", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = resolution
    cu.use_fill_caps = True
    me = ob.data
    for loop in seam_loops(ob, group):
        sp = cu.splines.new('POLY')
        sp.points.add(len(loop) - 1)
        for p, i in zip(sp.points, loop):
            p.co = (*me.vertices[i].co, 1.0)
        sp.use_cyclic_u = True
    po = bpy.data.objects.new(cu.name, cu)
    _coll().objects.link(po)
    po.parent = ob
    return po


# ----------------------------------------------------------------------------- bed
def make_mattress(name="Mattress", size=(1.6, 2.0, 0.24), bevel=0.04, segments=5, top_z=0.5):
    """Rounded mattress (Bevel modifier, smooth shading) whose top sits at world z = top_z.
    Adds a Collision modifier tuned for draping (see set_collider)."""
    W, L, H = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * W, v.co.y * L, v.co.z * H))
    ob = _obj_from_bm(name, bm)
    ob.location.z = top_z - H / 2
    bv = ob.modifiers.new("Bevel", 'BEVEL')
    bv.width, bv.segments, bv.limit_method = bevel, segments, 'ANGLE'
    bv.profile = 0.5
    _smooth(ob)
    set_collider(ob)
    return ob


def fitted_sheet(mattress, wrap=0.05, offset=0.002, name="FittedSheet"):
    """Fitted sheet = shell of the evaluated (bevelled) mattress pushed `offset` out along the normals,
    open at the bottom except a `wrap`-wide band that tucks under the mattress. No sim; add gathers at
    the corners by sculpting. Displace (strength offset, midlevel 0) keeps it editable."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(mattress.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    zmin = min(v.co.z for v in bm.verts)
    bottom = [f for f in bm.faces if f.normal.z < -0.99 and all(abs(v.co.z - zmin) < 1e-5 for v in f.verts)]
    ret = bmesh.ops.inset_region(bm, faces=bottom, thickness=wrap, use_even_offset=True)
    inner = [f for f in bottom if f.is_valid]
    bmesh.ops.delete(bm, geom=inner, context='FACES')
    ob = _obj_from_bm(name, bm)
    ob.matrix_world = mattress.matrix_world.copy()
    d = ob.modifiers.new("Offset", 'DISPLACE')
    d.strength, d.mid_level = offset, 0.0
    _smooth(ob)
    return ob


def mattress_from_frame(frame, name="Mattress", bevel=0.04, segments=5):
    """Mattress for a bed frame built by blender-furniture-modeling (make_bed_frame), which stores
    frame["mattress"] = [w, l, t, x, y, z_bottom] in the frame's local space. Z-rotation is copied."""
    bpy.context.view_layer.update()              # matrix_world is stale after setting location
    w, l, t, x, y, zb = frame["mattress"]
    c = frame.matrix_world @ Vector((x, y, zb))
    ob = make_mattress(name, (w, l, t), bevel=bevel, segments=segments, top_z=c.z + t)
    ob.location.x, ob.location.y = c.x, c.y
    ob.rotation_euler.z = frame.matrix_world.to_euler().z
    return ob


def register_colliders():
    """Evaluate the depsgraph once after the colliders exist and BEFORE the cloth object is created.
    Colliders first evaluated together with a new cloth object were ignored for the whole bake
    (blanket fell through; evaluating right before adding the Cloth modifier was not enough; 5.2.2)."""
    bpy.context.view_layer.update()
    bpy.context.evaluated_depsgraph_get()


def set_collider(ob, outer=0.002, inner=0.05, friction=40.0, damping=0.1):
    """Collision physics for a static collider. Rest gap of cloth on it = cloth distance_min + outer
    (measured: Blender defaults 0.015 + 0.02 -> 3.1 cm floating; 0.003 + 0.002 -> 5 mm, no clipping).
    Friction 5 (default) let a blanket with 0.55 m foot overhang slide off the bed; 40 held it."""
    col = next((m for m in ob.modifiers if m.type == 'COLLISION'), None) or ob.modifiers.new("Collision", 'COLLISION')
    cs = ob.collision
    cs.use = True
    cs.thickness_outer = outer
    cs.thickness_inner = inner
    cs.cloth_friction = friction
    cs.damping = damping
    return col


def _grid(name, size, res, z):
    W, L = size
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=max(2, round(W / res)), y_segments=max(2, round(L / res)), size=0.5)
    for v in bm.verts:
        v.co = Vector((v.co.x * W, v.co.y * L, z))
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    if bm.faces[0].normal.z < 0:                 # make faces point +Z, or Solidify offset +1
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])   # would then grow INTO the mattress
    return bm


def drape_blanket(bed, size=(2.2, 2.3), res=0.04, gap=0.03, head_offset=0.45, fold_back=0.0,
                  fold_radius=0.02, frames=60, quality=8, bending=2.0, mass=0.4, air_damping=10.0,
                  distance=0.003, self_collision=True, thickness=0.02, apply=True, name="Blanket"):
    """Drop a blanket/duvet onto `bed` (any object with Collision), centred in X, starting `gap` above
    the bed top. head_offset = distance from the bed's head (+Y) end to the blanket's head edge, or to
    the fold line when fold_back > 0 (leave ~0.4-0.5 m for pillows). Foot overhang = L - fold_back -
    (bed length - head_offset). fold_back pre-folds that much of the head end back over itself
    (turn-down): cloth does not fold itself reliably, so the fold is shaped first and self-collision
    keeps it apart; vertex group 'fold' records it. After apply: the fold layer is pushed 2 x thickness
    along its negated normals (they point down/inward after the fold, so both Solidify shells and the
    mattress would otherwise intersect), then
    Solidify(thickness, offset +1 = away from the mattress) + Subdivision 1."""
    register_colliders()                         # must run before the cloth object exists
    bb = [bed.matrix_world @ Vector(c) for c in bed.bound_box]
    top = max(p.z for p in bb)
    cx = (min(p.x for p in bb) + max(p.x for p in bb)) / 2
    head = max(p.y for p in bb)
    W, L = size
    bm = _grid(name, size, res, 0.0)
    y_head = L / 2
    yf = y_head - fold_back                      # fold line (local); = head edge without a fold
    cy = head - head_offset - yf
    fold_w = {}
    if fold_back > 0:
        arc = math.pi * fold_radius
        bm.verts.index_update()
        for v in bm.verts:
            s = v.co.y - yf
            if s <= 0:
                continue
            if s < arc:                          # wrap around a cylinder of radius fold_radius
                a = s / fold_radius
                v.co.y = yf + fold_radius * math.sin(a)
                v.co.z = fold_radius - fold_radius * math.cos(a)
                fold_w[v.index] = a / math.pi
            else:                                # lies back on top, reversed
                v.co.y = yf - (s - arc)
                v.co.z = 2 * fold_radius
                fold_w[v.index] = 1.0
    ob = _obj_from_bm(name, bm)
    if fold_w:
        _vgroup(ob, "fold", fold_w)
    ob.location = (cx, cy, top + gap)
    m = ob.modifiers.new("Cloth", 'CLOTH')
    s, c = m.settings, m.collision_settings
    s.quality, s.mass, s.bending_stiffness = quality, mass, bending
    s.tension_stiffness = s.compression_stiffness = 15.0
    s.air_damping = air_damping                  # 10 = RNA max; at 1 the overhang still swung 26-110 mm/frame at f60
    c.use_collision = True
    c.distance_min = distance
    c.collision_quality = 4
    c.use_self_collision = self_collision
    c.self_distance_min = min(distance, fold_radius * 0.75)
    c.self_friction = 5.0
    m.point_cache.frame_start, m.point_cache.frame_end = 1, frames
    simulate(ob, frames)
    if apply:
        apply_cloth(ob)
        if fold_w:
            lift_group(ob, "fold", 2.0 * thickness)
        so = ob.modifiers.new("Solidify", 'SOLIDIFY')
        # Even Thickness spiked the turn-down fold 0.48 m upward (20 self-intersections); Clamp did not help
        so.thickness, so.offset, so.use_even_offset = thickness, 1.0, False
        sd = ob.modifiers.new("Subdivision", 'SUBSURF')
        sd.levels = sd.render_levels = 1
        _smooth(ob)
    return ob


def lift_group(ob, group, amount, axis=None):
    """Move vertices of `group` by amount * weight. axis=None: along the NEGATED vertex normal, which for
    a turned-down fold (normals flipped by the fold) is up on top and outward on the hanging flaps.
    A +Z lift left the side flaps inside the mattress after Solidify (117 tri pairs, tested 5.2.2)."""
    gi = ob.vertex_groups[group].index
    me = ob.data
    nrm = [v.normal.copy() for v in me.vertices]
    for v in me.vertices:
        w = next((g.weight for g in v.groups if g.group == gi), 0.0)
        if w > 0:
            d = Vector(axis) if axis is not None else -nrm[v.index]
            v.co += d * amount * w
    me.update()
    return ob


def gap_report(cloth_ob, body_ob, region_margin=0.15):
    """Signed distance of every cloth vertex to the body surface (world).
    Returns inside count (< -1 mm), and the median gap of vertices over the body's top area."""
    tree, _, _ = _bvh(body_ob)
    dg = bpy.context.evaluated_depsgraph_get()
    oe = cloth_ob.evaluated_get(dg)
    me = oe.to_mesh()
    pts = [cloth_ob.matrix_world @ v.co for v in me.vertices]
    oe.to_mesh_clear()
    bb = [body_ob.matrix_world @ Vector(c) for c in body_ob.bound_box]
    x0, x1 = min(p.x for p in bb) + region_margin, max(p.x for p in bb) - region_margin
    y0, y1 = min(p.y for p in bb) + region_margin, max(p.y for p in bb) - region_margin
    top = max(p.z for p in bb)
    inside, over, alld = 0, [], []
    for p in pts:
        loc, n, _, dist = tree.find_nearest(p)
        if loc is None:
            continue
        signed = dist if (p - loc).dot(n) >= 0 else -dist
        alld.append(signed)
        if signed < -0.001:
            inside += 1
        if x0 < p.x < x1 and y0 < p.y < y1 and p.z > top - 0.05:
            over.append(signed)
    over.sort()
    med = over[len(over) // 2] if over else None
    alld.sort()
    return {"inside": inside, "over_top_count": len(over), "median_gap_top": med,
            "median_gap_all": alld[len(alld) // 2] if alld else None,
            "min_z": min(p.z for p in pts), "body_top": top}


# ----------------------------------------------------------------------------- curtain
def make_curtain(name="Curtain", width=1.4, drop=None, fullness=2.0, pleat_width=0.12,
                 res=0.02, top_z=2.45, floor_clearance=0.01, frames=40, tension=60.0,
                 bending=1.0, pin_rows=1, apply=True):
    """Pleated curtain panel hanging in the XZ plane, top rows pinned (heading tape/rings).
    fullness = flat fabric width / finished width (2.0-2.5 pinch pleat, 1.5 wave). Pleats are shaped
    as a sine wave first; the sim only relaxes them. Tension 60: a 2.4 m drop stretched 5.5 mm
    (default 15: 12 mm). drop=None -> top_z - floor_clearance - measured stretch (references/curtains.md)."""
    if drop is None:
        drop = top_z - floor_clearance - (0.006 if tension >= 40 else 0.012)
    register_colliders()                         # a floor/sill collider must be evaluated before the cloth exists
    flat = width * fullness
    n_pleats = max(1, round(width / pleat_width))
    nx, nz = max(4, round(flat / res)), max(4, round(drop / res))
    # pleat amplitude so the sine arc length ~= flat width
    k = 2 * math.pi * n_pleats / width
    lo, hi = 0.0, width
    for _ in range(40):                          # bisection on amplitude
        A = (lo + hi) / 2
        L = sum(math.hypot(width / 400, A * k * math.cos(k * (i + 0.5) * width / 400) * width / 400)
                for i in range(400))
        lo, hi = (A, hi) if L < flat else (lo, A)
    A = (lo + hi) / 2
    bm = bmesh.new()
    rows = []
    for j in range(nz + 1):
        z = top_z - drop * j / nz
        row = []
        for i in range(nx + 1):
            x = -width / 2 + width * i / nx
            row.append(bm.verts.new((x, A * math.sin(k * (x + width / 2)), z)))
        rows.append(row)
    for j in range(nz):
        for i in range(nx):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    bm.verts.index_update()
    pin = {v.index: 1.0 for r in rows[:pin_rows] for v in r}
    ob = _obj_from_bm(name, bm)
    _vgroup(ob, "pin", pin)
    m = ob.modifiers.new("Cloth", 'CLOTH')
    s, c = m.settings, m.collision_settings
    s.quality, s.mass, s.bending_stiffness = 8, 0.25, bending
    s.tension_stiffness = s.compression_stiffness = tension
    s.vertex_group_mass = "pin"
    c.use_self_collision = True
    c.self_distance_min = 0.004
    m.point_cache.frame_start, m.point_cache.frame_end = 1, frames
    simulate(ob, frames)
    if apply:
        apply_cloth(ob)
        so = ob.modifiers.new("Solidify", 'SOLIDIFY')
        so.thickness, so.offset = 0.002, 0.0
        _smooth(ob)
    return ob


# ----------------------------------------------------------------------------- tufting
def tuft_offset(x, y, sx, sy, depth, radius, pleat_depth, pleat_width, ox=0.0, oy=0.0):
    """Reference formula shared by the GN tree and the bmesh fallback: inward offset (m, >= 0)
    for a diamond (quincunx) button lattice with pleats along the diamond edges."""
    u = (x - ox) / sx + (y - oy) / sy
    v = (x - ox) / sx - (y - oy) / sy
    du = abs((u + 0.5) % 1.0 - 0.5)
    dv = abs((v + 0.5) % 1.0 - 0.5)
    h = sx * sy / math.hypot(sx, sy)            # metres per lattice unit across a diamond edge
    db = math.hypot(du, dv) * h
    dp = min(du, dv) * h
    b = math.exp(-(db / radius) ** 2)
    p = math.exp(-(dp / pleat_width) ** 2)
    return depth * b + pleat_depth * p * (1 - b)


def tuft_mask(ob, margin=0.06, min_normal_z=0.7, name="tuft"):
    """Vertex group `name`: 1 on the upward-facing panel, smooth falloff over `margin` from its border."""
    me = ob.data
    up = set()
    for p in me.polygons:
        if p.normal.z > min_normal_z:
            up.update(p.vertices)
    if not up:
        raise ValueError(f"{ob.name}: no faces with normal.z > {min_normal_z} (rotate the panel to +Z local)")
    xs = [me.vertices[i].co.x for i in up]
    ys = [me.vertices[i].co.y for i in up]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w = {}
    for i in up:
        co = me.vertices[i].co
        d = min(co.x - x0, x1 - co.x, co.y - y0, y1 - co.y)
        t = max(0.0, min(1.0, d / margin))
        w[i] = t * t * (3 - 2 * t)
    return _vgroup(ob, name, w)


def _gn_set_input(mod, ident, value):
    if V >= (5, 2, 0):
        getattr(mod.properties.inputs, ident).value = value
    else:
        mod[ident] = value


def add_tufting(ob, spacing=(0.12, 0.12), depth=0.025, radius=0.015, pleat_depth=0.010,
                pleat_width=0.006, offset=(0.0, 0.0), mask="tuft", subdivide=2, margin=0.06):
    """Non-destructive Chesterfield/diamond tufting: [Subdivision] -> GN 'SF_Tufting' (displaces along
    the normal by tuft_offset(), weighted by vertex group `mask`). Creates the mask if missing."""
    if not ob.vertex_groups.get(mask):
        tuft_mask(ob, margin=margin, name=mask)
    if subdivide and not any(m.type == 'SUBSURF' for m in ob.modifiers):
        sd = ob.modifiers.new("Subdivision", 'SUBSURF')
        sd.levels = sd.render_levels = subdivide
    ng = bpy.data.node_groups.new("SF_Tufting", 'GeometryNodeTree')
    it = ng.interface
    it.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    params = [("Spacing X", spacing[0]), ("Spacing Y", spacing[1]), ("Button Depth", depth),
              ("Button Radius", radius), ("Pleat Depth", pleat_depth), ("Pleat Width", pleat_width),
              ("Offset X", offset[0]), ("Offset Y", offset[1])]
    socks = {}
    for nm, val in params:
        s = it.new_socket(nm, in_out='INPUT', socket_type='NodeSocketFloat')
        s.default_value = val
        socks[nm] = s
    ms = it.new_socket("Mask", in_out='INPUT', socket_type='NodeSocketString')
    ms.default_value = mask
    it.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput')
    pos, sep = N.new('GeometryNodeInputPosition'), N.new('ShaderNodeSeparateXYZ')
    L.new(pos.outputs[0], sep.inputs[0])

    def math_(op, a, b=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for k, src in enumerate((a, b)):
            if src is None:
                continue
            if isinstance(src, (int, float)):
                n.inputs[k].default_value = src
            else:
                L.new(src, n.inputs[k])
        return n.outputs[0]

    G = lambda nm: gi.outputs[nm]
    x = math_('SUBTRACT', sep.outputs[0], G("Offset X"))
    y = math_('SUBTRACT', sep.outputs[1], G("Offset Y"))
    xs, ys = math_('DIVIDE', x, G("Spacing X")), math_('DIVIDE', y, G("Spacing Y"))
    u, v = math_('ADD', xs, ys), math_('SUBTRACT', xs, ys)
    du = math_('ABSOLUTE', math_('SUBTRACT', math_('FRACT', math_('ADD', u, 0.5)), 0.5))
    dv = math_('ABSOLUTE', math_('SUBTRACT', math_('FRACT', math_('ADD', v, 0.5)), 0.5))
    # h = sx*sy / sqrt(sx^2 + sy^2)
    hyp = math_('SQRT', math_('ADD', math_('MULTIPLY', G("Spacing X"), G("Spacing X")),
                              math_('MULTIPLY', G("Spacing Y"), G("Spacing Y"))))
    h = math_('DIVIDE', math_('MULTIPLY', G("Spacing X"), G("Spacing Y")), hyp)
    db = math_('MULTIPLY', math_('SQRT', math_('ADD', math_('MULTIPLY', du, du), math_('MULTIPLY', dv, dv))), h)
    dp = math_('MULTIPLY', math_('MINIMUM', du, dv), h)

    def gauss(d, r):
        q = math_('DIVIDE', d, r)
        return math_('EXPONENT', math_('MULTIPLY', math_('MULTIPLY', q, q), -1.0))

    b = gauss(db, G("Button Radius"))
    p = gauss(dp, G("Pleat Width"))
    off = math_('ADD', math_('MULTIPLY', G("Button Depth"), b),
                math_('MULTIPLY', math_('MULTIPLY', G("Pleat Depth"), p), math_('SUBTRACT', 1.0, b)))
    na = N.new('GeometryNodeInputNamedAttribute')
    na.data_type = 'FLOAT'
    L.new(G("Mask"), na.inputs["Name"])
    off = math_('MULTIPLY', math_('MULTIPLY', off, na.outputs["Attribute"]), -1.0)
    nrm, sc = N.new('GeometryNodeInputNormal'), N.new('ShaderNodeVectorMath')
    sc.operation = 'SCALE'
    L.new(nrm.outputs[0], sc.inputs[0])
    L.new(off, sc.inputs["Scale"])
    sp = N.new('GeometryNodeSetPosition')
    L.new(gi.outputs["Geometry"], sp.inputs["Geometry"])
    L.new(sc.outputs[0], sp.inputs["Offset"])
    L.new(sp.outputs["Geometry"], go.inputs["Geometry"])
    mod = ob.modifiers.new("Tufting", 'NODES')
    mod.node_group = ng
    for nm, val in params:                       # instance values = defaults; shows how to set them
        _gn_set_input(mod, socks[nm].identifier, val)
    return mod


def tuft_bmesh(ob, spacing=(0.12, 0.12), depth=0.025, radius=0.015, pleat_depth=0.010,
               pleat_width=0.006, offset=(0.0, 0.0), mask="tuft"):
    """Destructive fallback (same formula as add_tufting): displaces ob.data in place.
    Subdivide first (base edge <= radius/3) or the dimples facet."""
    if not ob.vertex_groups.get(mask):
        tuft_mask(ob, name=mask)
    gi = ob.vertex_groups[mask].index
    me = ob.data
    nrm = [v.normal.copy() for v in me.vertices]
    for v in me.vertices:
        w = next((g.weight for g in v.groups if g.group == gi), 0.0)
        if w <= 0:
            continue
        d = tuft_offset(v.co.x, v.co.y, *spacing, depth, radius, pleat_depth, pleat_width, *offset)
        v.co -= nrm[v.index] * d * w
    me.update()
    return ob


def place_buttons(ob, spacing=(0.12, 0.12), offset=(0.0, 0.0), radius=0.011, height=0.006,
                  mask="tuft", min_weight=0.95, name=None):
    """One mesh object with a button at every lattice point whose mask weight >= min_weight, parented
    to `ob`. Each button sits on the funnel wall at its own radius (mean of 8 rays on a ring), so it
    plugs the dimple like a real button; snapped to the centre hit it vanished inside the 25 mm funnel."""
    sx, sy = spacing
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    me = oe.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    oe.to_mesh_clear()
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    gi = ob.vertex_groups[mask].index
    strong = [v.co for v in ob.data.vertices for g in v.groups if g.group == gi and g.weight >= min_weight]
    if not strong:
        return None
    x0, x1 = min(c.x for c in strong), max(c.x for c in strong)
    y0, y1 = min(c.y for c in strong), max(c.y for c in strong)
    ztop = max(c.z for c in strong) + 1.0
    down = Vector((0, 0, -1))
    pts = []
    i0, i1 = math.floor((x0 - offset[0]) / sx) - 1, math.ceil((x1 - offset[0]) / sx) + 1
    j0, j1 = math.floor((y0 - offset[1]) / sy) - 1, math.ceil((y1 - offset[1]) / sy) + 1
    for i in range(i0, i1 + 1):
        for j in range(j0, j1 + 1):
            for fx, fy in ((0.0, 0.0), (0.5, 0.5)):
                x, y = offset[0] + (i + fx) * sx, offset[1] + (j + fy) * sy
                if not (x0 <= x <= x1 and y0 <= y <= y1):
                    continue
                ring = []
                for k in range(8):
                    a = 2 * math.pi * k / 8
                    hit, n, _, _ = tree.ray_cast(Vector((x + radius * math.cos(a), y + radius * math.sin(a), ztop)), down)
                    if hit is not None and n.z > 0.0:
                        ring.append(hit)
                if len(ring) == 8:
                    c = sum(ring, Vector()) / 8
                    pts.append((Vector((x, y, c.z)), Vector((0, 0, 1))))
    out = bmesh.new()
    for c, n in pts:
        ret = bmesh.ops.create_uvsphere(out, u_segments=12, v_segments=6, radius=1.0)
        q = n.to_track_quat('Z', 'Y')
        for vv in ret["verts"]:
            vv.co = c + q @ Vector((vv.co.x * radius, vv.co.y * radius, vv.co.z * height))
    bo = _obj_from_bm(name or ob.name + "_buttons", out)
    bo.parent = ob
    _smooth(bo)
    bo["sf_button_count"] = len(pts)
    return bo


# ----------------------------------------------------------------------------- materials
# Starting values (Principled BSDF v2 names, Blender 4.0+). Grade against reference photos under the
# scene's lights. thread = weave period in metres (bump pattern); grain = bump strength.
FABRICS = {
    #            rough  sheen  sheen_rough spec   thread  bump   variation
    "velvet":   (0.90,  1.00,  0.30,       0.30,  0.0,    0.00,  0.04),
    "cotton":   (0.85,  0.30,  0.50,       0.40,  0.003,  0.15,  0.03),
    "linen":    (0.80,  0.20,  0.50,       0.40,  0.004,  0.25,  0.06),
    "wool":     (0.95,  0.60,  0.60,       0.30,  0.006,  0.20,  0.05),
    "leather":  (0.45,  0.00,  0.50,       0.50,  0.0,    0.15,  0.05),
}


def fabric_material(name, kind="cotton", color=(0.35, 0.30, 0.25), coords="Object"):
    """Principled fabric: roughness/sheen preset, weave (two Wave textures) or leather grain (Voronoi)
    bump, low-frequency value variation. coords 'Object' = metres (thread size is real, needs applied
    scale, bakes fine onto any UV layout); 'UV' only when the UVs have a known texel density.
    For GTA/UE bake it to textures; procedural nodes do not export (materials.md)."""
    rough, sheen, sheen_r, spec, thread, bump, var = FABRICS[kind]
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if V < (5, 0, 0):
        m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = next(n for n in N if n.bl_idname == "ShaderNodeBsdfPrincipled")
    b.inputs["Roughness"].default_value = rough
    b.inputs["Sheen Weight"].default_value = sheen
    b.inputs["Sheen Roughness"].default_value = sheen_r
    tint = [c + (1 - c) * 0.4 for c in color]           # sheen a bit lighter than the dye
    b.inputs["Sheen Tint"].default_value = (*tint, 1.0)
    b.inputs["Specular IOR Level"].default_value = spec
    if "Diffuse Roughness" in b.inputs:                  # 4.3+
        b.inputs["Diffuse Roughness"].default_value = 0.5 if kind != "leather" else 0.0
    tc = N.new("ShaderNodeTexCoord")
    vec = tc.outputs["UV" if coords == "UV" else "Object"]
    # colour variation: Value * (1 +- var)
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0                # ~30 cm blotches in Object space
    L.new(vec, nz.inputs["Vector"])
    ma = N.new("ShaderNodeMath")
    ma.operation = 'MULTIPLY_ADD'
    L.new(nz.outputs["Fac"], ma.inputs[0])
    ma.inputs[1].default_value = 2 * var
    ma.inputs[2].default_value = 1 - var
    hsv = N.new("ShaderNodeHueSaturation")
    hsv.inputs["Color"].default_value = (*color, 1.0)
    L.new(ma.outputs[0], hsv.inputs["Value"])
    L.new(hsv.outputs["Color"], b.inputs["Base Color"])
    if bump > 0:
        if kind == "leather":
            vo = N.new("ShaderNodeTexVoronoi")
            vo.feature = 'DISTANCE_TO_EDGE'
            vo.inputs["Scale"].default_value = 250.0
            L.new(vec, vo.inputs["Vector"])
            height = vo.outputs["Distance"]
        else:
            add = N.new("ShaderNodeMath")
            add.operation = 'ADD'
            for k, axis in enumerate(('X', 'Y')):
                w = N.new("ShaderNodeTexWave")
                w.wave_type, w.bands_direction = 'BANDS', axis
                w.inputs["Scale"].default_value = 2 * math.pi / (20 * thread)   # BANDS period = 2pi/(20*Scale)
                L.new(vec, w.inputs["Vector"])
                L.new(w.outputs["Fac"], add.inputs[k])
            height = add.outputs[0]
        bp = N.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        bp.inputs["Distance"].default_value = 0.001
        L.new(height, bp.inputs["Height"])
        L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def ensure_uv(ob, angle=66.0, margin=0.02):
    """Smart UV Project if the mesh has no UV map. Generated cloth meshes have none, and a UV-less mesh
    exported through Sollumz shares no vertices (about 4x the vertex count; muto-atlas, measured)."""
    if ob.data.uv_layers:
        return False
    vl = bpy.context.view_layer
    prev = vl.objects.active
    vl.objects.active = ob
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                                   selected_editable_objects=[ob]):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
        bpy.ops.object.mode_set(mode='OBJECT')
    vl.objects.active = prev
    return True


# ----------------------------------------------------------------------------- game-ready
def _evaluated_copy(ob, name):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.name = name
    cp = bpy.data.objects.new(name, me)
    _coll().objects.link(cp)
    cp.matrix_world = ob.matrix_world.copy()
    for vg in ob.vertex_groups:                  # keep names so groups survive for Decimate masks
        if not cp.vertex_groups.get(vg.name):
            cp.vertex_groups.new(name=vg.name)
    return cp


def _decimated(src, name, ratio):
    cp = _evaluated_copy(src, name)
    if ratio < 0.999:
        d = cp.modifiers.new("Decimate", 'DECIMATE')
        d.decimate_type, d.ratio, d.use_collapse_triangulate = 'COLLAPSE', ratio, True
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(cp.evaluated_get(dg))
        old = cp.data
        cp.modifiers.remove(d)
        cp.data = me
        me.name = name
        bpy.data.meshes.remove(old)
    else:
        bm = bmesh.new()
        bm.from_mesh(cp.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(cp.data)
        bm.free()
    _smooth(cp)
    return cp


def collision_box(ob, name=None, pad=0.0):
    """Axis-aligned (object-local) box hull of the evaluated mesh: 8 verts, 6 quads, convex.
    Named UCX_<name>_00 for Unreal; for GTA build a Sollumz Bound Box of the same size instead."""
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    me = oe.to_mesh()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    oe.to_mesh_clear()
    lo = Vector((min(xs) - pad, min(ys) - pad, min(zs) - pad))
    hi = Vector((max(xs) + pad, max(ys) + pad, max(zs) + pad))
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((lo.x + hi.x) / 2 + v.co.x * (hi.x - lo.x), (lo.y + hi.y) / 2 + v.co.y * (hi.y - lo.y),
                       (lo.z + hi.z) / 2 + v.co.z * (hi.z - lo.z)))
    cb = _obj_from_bm(name or f"UCX_{ob.name}_00", bm)
    cb.matrix_world = ob.matrix_world.copy()
    cb.display_type = 'WIRE'
    cb.hide_render = True
    return cb


def game_ready(ob, lod_ratios=(1.0, 0.5, 0.25), target_tris=None, collision=True, base_name=None, uv=True):
    """Evaluated copy -> LOD0 (decimated to target_tris if given, Smart UV if it has none) -> LOD1..n
    (ratios of LOD0, UVs carried by Decimate) -> UCX box. Source object is left untouched.
    Returns (lods, collision_obj). Bake the high (source) onto LOD0 with scenario-blender-uv-baking."""
    base = base_name or ob.name
    src_tris = stats(ob)["tris"]
    r0 = min(1.0, target_tris / src_tris) if target_tris else 1.0
    lods = [_decimated(ob, f"{base}_LOD0", r0)]
    if uv:
        ensure_uv(lods[0])
    for i, r in enumerate(lod_ratios[1:], start=1):
        lods.append(_decimated(lods[0], f"{base}_LOD{i}", r))
    col = collision_box(lods[0], f"UCX_{base}_LOD0_00".replace("_LOD0", "")) if collision else None
    return lods, col
