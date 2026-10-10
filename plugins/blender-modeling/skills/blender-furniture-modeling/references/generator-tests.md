# Generator test harness and results

Read when changing `furniture_gen.py` or when you need proof that a generator does what [generators.md](generators.md)
claims. Re-run after every change.

## Results (2026-10-10)

`bpy 5.2.2` (Python 3.13) and `bpy 4.5.14` (Python 3.11): **276/276 checks passed** on each.

| Area | What is asserted |
|---|---|
| Every generator and preset (23 objects) | base-mesh bbox = parameters (±0.1 mm); bevelled (evaluated) bbox within 1 mm; origin at floor and centred on the footprint; rotation/scale identity; islands = registered parts; 0 non-manifold edges (base and bevelled); every part's signed volume > 0 (outward normals); no coplanar same-facing overlapping faces between parts; Bevel (weight, Harden Normals) above Weighted Normal; custom normals on the evaluated mesh; `UVMap 0`; `sz_` material slots |
| Table | 4 legs, knee clearance 0.635 m, 25 mm top, top flat face shrunk by exactly 2 × 2 mm (bevel width) |
| Chair | seat top 0.45, back top 0.86, measured post tilt 8.00°, post back edge sunk into the seat (no wedge gap) |
| Bar stool 0.75 / 0.65 | bbox, 4 splayed legs each with 4 vertices on z = 0, footrest at 0.30 / 0.20 |
| Bookcase | 6 equal clear heights (0.306 m), span 0.764 m ≤ 0.80, top keeps a 2.00 mm bevel next to the 3 mm back; the naive angle-limited bevel clamps to 1.50 mm; a global merge-by-distance creates 2 non-manifold edges |
| Wardrobe | 2 doors for 1.0 m, 3 mm gap between doors, 1.5 mm outer reveal, bar handles centred at 1.0 m |
| Kitchen base (KICK, worktop) | worktop top 0.90, worktop depth 0.60, door 1.5 mm under the worktop, door above the 150 mm plinth |
| Sideboard, separate doors | 3 door objects, origins on the hinge axis at door bottom, each door opened 90° stays in front of the carcass |
| Dresser / nightstand | 3 mm gaps, 1.5 mm under the top, graduated fronts (0.215 → 0.149), drawer boxes inside the carcass |
| Bed EU 160 / US queen / UK double / EU 90 | inner opening = mattress + 2 × 10 mm, slats at 0.32, mattress top 0.52, slat gaps ≤ 70 mm, mattress record follows the origin shift |
| Pool 9 ft (+ 8 ft pro, 7 ft) | 2.540 × 1.270 between cushion noses, nose 36.29 mm above the cloth, corner mouth 4.563 in, side mouth 5.062 in, 18 sights 12.5 in apart, bed 0.762 within 29¼–31 in |
| Snooker | floor to top of cushion rail 0.864 |
| finalize | 2× scale + 90° rotation applied to data with world placement unchanged; triangulate keeps custom normals |
| Collision / LOD / export | UCX_table_01_00..04 (8 verts each); LOD tris 972 > 108 > 60; FBX export with the UE settings re-imports as 1.6 × 0.9 × 0.75 m + 5 UCX; Sollumz layout (drawable empty > identity `.model` + `.col` > centred box bounds, 2 LOD meshes) |

Bugs found while testing (now handled in the code or the rules):
- `import bmesh` before `import bpy` fails in the bpy wheel (`ModuleNotFoundError: No module named 'bmesh'`).
- Custom properties come back as `IDPropertyArray`: `sorted(obj["doors"])` raises
  `TypeError: '<' not supported between instances of 'IDPropertyArray' and 'IDPropertyArray'`; convert with `list()`.
- `sum(v.co for v in ...)` raises `Vector addition: (int + Vector) invalid type`; pass `Vector()` as start.
- The first drawer-box version sat 1.5 mm inside the bottom panel; the box bottom is now clamped above it.
- Mirror with merge on closed half-boxes gives doubled inner faces (8 non-manifold edges); open the half first
  (checked with a separate probe, see topology-cleanup.md).

## Re-run

```bash
uv venv --python 3.13 venv && uv pip install --python venv/bin/python "bpy==5.2.*"     # or 3.11 + bpy==4.5.*
# gen/furniture_gen.py  = code block in generators.md
# tests/test_furniture.py = code block below
venv/bin/python tests/test_furniture.py        # exit code 1 on any FAIL
```

The bpy wheel needs ~1 GB of disk. The same file runs inside Blender: `blender -b --factory-startup
--python-exit-code 1 -P tests/test_furniture.py`.

## Test harness: save as `tests/test_furniture.py`

```python
"""Headless tests for furniture_gen.py (run: venv/bin/python tests/test_furniture.py)."""
import math
import os
import sys
import tempfile

import bpy  # before bmesh (bpy wheel)
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gen"))
import furniture_gen as G  # noqa: E402

TOL, MM = 1e-4, 1e-3
results = []


def check(cond, msg):
    results.append((bool(cond), msg))
    print(("PASS " if cond else "FAIL ") + msg)


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def bbox(pts):
    xs, ys, zs = zip(*pts)
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def evaluated_mesh(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    return bpy.data.meshes.new_from_object(obj.evaluated_get(dg))


def part_verts(obj, name):
    """Vertices per island of the part(s) called `name` (face attribute 'part')."""
    me = obj.data
    pid = [0] * len(me.polygons)
    me.attributes["part"].data.foreach_get("value", pid)
    idx = {i for i, n in enumerate(obj["parts"]) if n == name}
    out = {}
    for p, k in zip(me.polygons, pid):
        if k in idx:
            out.setdefault(k, set()).update(p.vertices)
    return [[me.vertices[i].co.copy() for i in vs] for vs in out.values()]


def mesh_stats(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    isl = G.islands(bm)
    vols = []
    for faces in isl:
        tris = bmesh.ops.triangulate(bm, faces=list(faces))["faces"]
        vols.append(sum(f.verts[0].co.dot(f.verts[1].co.cross(f.verts[2].co)) for f in tris) / 6.0)
    bm.free()
    return non_manifold, len(isl), vols


def zfight_pairs(obj):
    """Axis-aligned faces of DIFFERENT parts, same plane, same facing, overlapping area -> z-fighting."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    isl_of = {f: i for i, isl in enumerate(G.islands(bm)) for f in isl}
    groups = {}
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        if abs(abs(n[ax]) - 1) > 1e-5:
            continue
        key = (ax, n[ax] > 0, round(f.verts[0].co[ax], 5))
        a, b = [i for i in range(3) if i != ax]
        r = ([min(v.co[a] for v in f.verts), max(v.co[a] for v in f.verts)],
             [min(v.co[b] for v in f.verts), max(v.co[b] for v in f.verts)])
        groups.setdefault(key, []).append((isl_of[f], r))
    bad = 0
    for faces in groups.values():
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                (pi, (ra, rb)), (pj, (sa, sb)) = faces[i], faces[j]
                if pi != pj and min(ra[1], sa[1]) - max(ra[0], sa[0]) > 1e-5 and min(rb[1], sb[1]) - max(rb[0], sb[0]) > 1e-5:
                    bad += 1
    bm.free()
    return bad


def common(obj, dims, label):
    """Shared assertions: size, origin, topology, normals, z-fighting, stack, UVs, materials."""
    me = obj.data
    mn, mx = bbox([v.co for v in me.vertices])
    check((mx - mn - Vector(dims)).length < TOL, f"{label}: bbox {tuple(round(c, 4) for c in mx - mn)} = {dims}")
    fp = obj["footprint"]
    check(abs(mn.z) < 1e-6 and abs(fp[0] + fp[1]) < 1e-6 and abs(fp[2] + fp[3]) < 1e-6,
          f"{label}: origin at floor, centred on the footprint")
    check(obj.matrix_basis.to_3x3() == Matrix.Identity(3), f"{label}: rotation/scale applied")
    nm, n_isl, vols = mesh_stats(me)
    check(nm == 0 and n_isl == len(obj["parts"]), f"{label}: {n_isl} closed parts, 0 non-manifold edges")
    check(min(vols) > 0, f"{label}: every part has outward normals (min signed volume {min(vols):.2e})")
    check(zfight_pairs(obj) == 0, f"{label}: no coplanar overlapping faces between parts")
    ev = evaluated_mesh(obj)
    emn, emx = bbox([v.co for v in ev.vertices])
    nm_e, _, _ = mesh_stats(ev)
    check(nm_e == 0 and (emx - emn - Vector(dims)).length < MM, f"{label}: bevelled mesh manifold, bbox within 1 mm")
    stack = [m.type for m in obj.modifiers]
    bev = obj.modifiers.get("Bevel")
    check(stack[:2] == ["BEVEL", "WEIGHTED_NORMAL"] and bev.harden_normals and bev.limit_method == "WEIGHT",
          f"{label}: Bevel (weight, harden normals) above Weighted Normal")
    check(ev.has_custom_normals, f"{label}: evaluated mesh carries custom normals")
    check("UVMap 0" in me.uv_layers and all(m.name.startswith("sz_") for m in me.materials),
          f"{label}: UVMap 0 + sz_<shader>.<kind> material slots")
    bpy.data.meshes.remove(ev)


def flat_top_extent(obj, z, axis=0):
    """Largest +Z face at height z on the evaluated mesh: its extent along `axis` (bevel shrinks it)."""
    ev = evaluated_mesh(obj)
    f = max((p for p in ev.polygons if p.normal.z > 0.999 and abs(p.center.z - z) < 1e-5), key=lambda p: p.area)
    c = [ev.vertices[i].co[axis] for i in f.vertices]
    bpy.data.meshes.remove(ev)
    return max(c) - min(c)


# ------------------------------------------------------------------ tests
def test_table():
    fresh()
    t = G.make_table(width=1.6, depth=0.9, height=0.75)
    G.finalize(t)
    common(t, (1.6, 0.9, 0.75), "table")
    check(len(part_verts(t, "leg")) == 4 and t["knee_clearance"] >= 0.60,
          f"table: 4 legs, knee clearance {t['knee_clearance']:.3f} m >= 0.60")
    top = part_verts(t, "top")[0]
    check(abs(max(v.z for v in top) - min(v.z for v in top) - 0.025) < TOL, "table: top 25 mm thick")
    check(abs(flat_top_extent(t, 0.75) - (1.6 - 0.004)) < TOL, "table: 2 mm bevel on the top edges")
    fresh()
    c = G.make_table("coffee_01", width=1.1, depth=0.6, height=0.42, apron_h=0.06)
    G.finalize(c)
    common(c, (1.1, 0.6, 0.42), "coffee table")


def test_chair():
    fresh()
    c = G.make_chair(seat_h=0.45, back_h=0.86, back_angle=8.0)
    G.finalize(c)
    me = c.data
    mn, mx = bbox([v.co for v in me.vertices])
    seat = part_verts(c, "seat")[0]
    check(abs(max(v.z for v in seat) - 0.45) < TOL and abs(mx.z - 0.86) < TOL, "chair: seat top 0.45, back top 0.86")
    common(c, tuple(mx - mn), "chair")
    posts = part_verts(c, "back_post")
    p = posts[0]
    edge = [v for v in p if abs(v.x - p[0].x) < TOL]
    lo = min(edge, key=lambda v: v.z + v.y)
    hi = max(edge, key=lambda v: v.z - v.y)
    measured = math.degrees(math.atan2(hi.y - lo.y, hi.z - lo.z))
    check(abs(measured - 8.0) < 0.05, f"chair: back post tilt {measured:.2f} deg = 8")
    check(min(v.z for v in p) < 0.45 - 0.003, "chair: post back edge sinks into the seat (no wedge gap)")
    check(len(part_verts(c, "leg_front")) == 2 and len(part_verts(c, "leg_back")) == 2, "chair: 4 legs")


def test_bar_stool():
    for seat_h in (0.75, 0.65):
        fresh()
        s = G.make_bar_stool(seat_h=seat_h)
        G.finalize(s)
        common(s, (0.36, 0.36, seat_h), f"stool {seat_h}")
        legs = part_verts(s, "leg")
        flat = all(sum(1 for v in leg if abs(v.z) < 1e-6) == 4 for leg in legs)
        check(len(legs) == 4 and flat, f"stool {seat_h}: 4 splayed legs with level feet (4 verts at z=0 each)")
        check(abs(s["foot_z"] - max(0.18, seat_h - 0.45)) < TOL, f"stool {seat_h}: footrest at {s['foot_z']:.2f} m")


def test_shelf_and_clamp():
    fresh()
    b = G.make_shelf(width=0.8, depth=0.28, height=2.02, shelves=5)
    G.finalize(b)
    common(b, (0.8, 0.28, 2.02), "bookcase")
    zs = sorted((min(v.z for v in sh), max(v.z for v in sh)) for sh in part_verts(b, "shelf"))
    bounds = [0.06 + 0.018] + [z for pair in zs for z in pair] + [2.02 - 0.018]
    gaps = [bounds[i + 1] - bounds[i] for i in range(0, len(bounds), 2)]
    check(max(gaps) - min(gaps) < TOL and abs(gaps[0] - b["shelf_clear"]) < TOL,
          f"bookcase: 6 equal clear heights {gaps[0]:.3f} m")
    check(b["shelf_span"] <= 0.80, f"bookcase: shelf span {b['shelf_span']:.3f} m <= 0.80 (18 mm board sag rule)")
    xi = 0.8 / 2 - 0.018
    good = flat_top_extent(b, 2.02)
    check(abs(good - (2 * xi - 0.004)) < TOL, f"bookcase: top keeps its 2 mm bevel with a 3 mm back panel ({(2 * xi - good) / 2 * 1000:.2f} mm)")
    bev = b.modifiers["Bevel"]
    bev.limit_method = "ANGLE"                                     # naive: thin back panel clamps everything
    naive = flat_top_extent(b, 2.02)
    check((2 * xi - naive) / 2 < 0.0019, f"bookcase: naive angle-limited bevel clamps to {(2 * xi - naive) / 2 * 1000:.2f} mm (object-wide Clamp Overlap)")
    bev.limit_method = "WEIGHT"
    # merge by distance: global weld vs per part
    bm = bmesh.new()
    bm.from_mesh(b.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    welded = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    check(welded > 0, f"bookcase: global merge-by-distance welds touching panels -> {welded} non-manifold edges (finalize merges per part: 0)")


def test_cabinets():
    fresh()
    w = G.make_cabinet("wardrobe_01", width=1.0, height=2.01, depth=0.6, base="PLINTH", plinth_h=0.08)
    G.finalize(w)
    common(w, (1.0, 0.625, 2.01), "wardrobe")
    doors = sorted(list(d) for d in w["doors"])
    check(len(doors) == 2, "wardrobe: 1.0 m wide -> 2 doors (max 0.6 m each)")
    check(abs((doors[1][0] - doors[0][1]) - 0.003) < TOL and abs(doors[0][0] + 0.5 - 0.0015) < TOL,
          "wardrobe: 3 mm gap between doors, 1.5 mm at the outer edges")
    bars = part_verts(w, "handle_bar")
    zc = [(min(v.z for v in b) + max(v.z for v in b)) / 2 for b in bars]
    check(len(bars) == 2 and all(abs(z - 1.0) < TOL for z in zc), "wardrobe: vertical bar handles centred at 1.0 m")
    fresh()
    k = G.make_cabinet("kitchen_base_01", width=0.6, height=0.9, depth=0.58, base="KICK", plinth_h=0.15,
                       worktop_t=0.038, worktop_overhang=0.02, handle="BAR_H")
    G.finalize(k)
    me = k.data
    mn, mx = bbox([v.co for v in me.vertices])
    common(k, tuple(mx - mn), "kitchen base")
    wt = part_verts(k, "worktop")[0]
    check(abs(max(v.z for v in wt) - 0.9) < TOL and abs((max(v.y for v in wt) - min(v.y for v in wt)) - 0.60) < TOL,
          "kitchen base: worktop top at 0.90 m, worktop depth 0.60 m")
    door = part_verts(k, "door")[0]
    check(abs(max(v.z for v in door) - (0.9 - 0.038 - 0.0015)) < TOL and abs(min(v.z for v in door) - (0.15 + 0.0015)) < TOL,
          "kitchen base: door 1.5 mm under the worktop gap, starts above the 150 mm plinth")
    fresh()
    s = G.make_cabinet("sideboard_01", width=1.6, height=0.75, depth=0.45, base="LEGS", leg_h=0.15,
                       separate_doors=True, handle="KNOB")
    G.finalize(s)
    for d in s.children:
        G.finalize(d, keep_origin=True)
    common(s, (1.6, 0.45 - 0.019, 0.75), "sideboard carcass (doors are separate objects)")
    check(len(s.children) == 3, "sideboard: 1.6 m -> 3 separate door objects")
    yf = s["y_face"]
    ok = True
    for d in s.children:
        piv = d.matrix_basis.translation
        edges = [x for dd in s["doors"] for x in (dd[0], dd[1])]
        on_edge = any(abs(piv.x - x) < TOL for x in edges) and abs(piv.z - s["doors"][0][2]) < TOL
        ang = math.radians(-90 if d["hinge"] == "LEFT" else 90)
        R = Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, "Z")
        pts = [R @ v.co for v in d.data.vertices]
        ok &= abs(piv.y - yf) < TOL and on_edge and max(p.y for p in pts) <= yf + TOL
    check(ok, "sideboard: door origins on the hinge axis; opened 90 deg every door stays in front of the carcass")


def test_drawers():
    fresh()
    d = G.make_drawer_unit(width=0.8, height=0.8, depth=0.48, drawers=4, graduated=True, drawer_boxes=True)
    G.finalize(d)
    me = d.data
    mn, mx = bbox([v.co for v in me.vertices])
    common(d, (0.8, tuple(mx - mn)[1], 0.8), "dresser")
    fr = d["fronts"]
    gaps = [fr[i + 1][0] - fr[i][1] for i in range(len(fr) - 1)]
    hs = [f[1] - f[0] for f in fr]
    check(all(abs(g - 0.003) < TOL for g in gaps) and abs(fr[-1][1] - (0.8 - 0.0015)) < TOL,
          "dresser: 3 mm gaps between fronts, 1.5 mm under the top")
    check(all(hs[i] > hs[i + 1] for i in range(len(hs) - 1)), f"dresser: graduated fronts {[round(h, 3) for h in hs]}")
    xi, zb = 0.8 / 2 - 0.018, 0.06
    inside = all(-xi < v.x < xi and zb + 0.018 <= v.z <= 0.8 - 0.018
                 for n in ("drawer_side", "drawer_back", "drawer_bottom") for b in part_verts(d, n) for v in b)
    check(inside, "dresser: drawer boxes stay inside the carcass (no intersection with panels)")
    fresh()
    n = G.make_drawer_unit("nightstand_01", width=0.45, height=0.55, depth=0.40, drawers=2, graduated=False,
                           base="LEGS", leg_h=0.18, handle="KNOB")
    G.finalize(n)
    mn, mx = bbox([v.co for v in n.data.vertices])
    common(n, tuple(mx - mn), "nightstand")


def test_beds():
    for key, (mw, ml) in (("EU_160x200", (1.6, 2.0)), ("US_queen", (60 * 0.0254, 80 * 0.0254))):
        fresh()
        b = G.make_bed_frame(mattress=key, mattress_t=0.20, mattress_top=0.52)
        G.finalize(b)
        mn, mx = bbox([v.co for v in b.data.vertices])
        common(b, tuple(mx - mn), f"bed {key}")
        rails = part_verts(b, "side_rail")
        inner = min(min(v.x for v in r) for r in rails if min(v.x for v in r) > 0) * 2
        check(abs(inner - (mw + 0.02)) < TOL, f"bed {key}: inner opening {inner:.4f} = mattress {mw:.4f} + 2 x 10 mm")
        slats = part_verts(b, "slat")
        top = max(v.z for s in slats for v in s)
        m = b["mattress"]
        check(abs(top - 0.32) < TOL and abs(m[5] + m[2] - 0.52) < TOL, f"bed {key}: slats at 0.32, mattress top at 0.52")
        check(b["slat_pitch"] <= 0.07 and abs(abs(m[4]) - 0.02) < TOL,
              f"bed {key}: slat gaps {b['slat_pitch'] * 1000:.0f} mm; mattress record follows the origin shift")


def test_billiard():
    fresh()
    p = G.make_billiard_table(size="9ft", bed_h=0.762)
    G.finalize(p)
    mn, mx = bbox([v.co for v in p.data.vertices])
    common(p, tuple(mx - mn), "pool 9ft")
    noses = [v for n in ("cushion_long", "cushion_short") for c in part_verts(p, n) for v in c
             if abs(v.z - p["nose_z"]) < TOL]
    xs, ys = [abs(v.x) for v in noses], [abs(v.y) for v in noses]
    play_w = 2 * min(x for x, y in zip(xs, ys) if y < 1.2)
    play_l = 2 * min(y for x, y in zip(xs, ys) if x < 0.6)
    check(abs(play_l - 100 * 0.0254) < MM and abs(play_w - 50 * 0.0254) < MM,
          f"pool 9ft: playing surface {play_l:.4f} x {play_w:.4f} m between cushion noses (WPA 100 x 50 in)")
    check(abs(p["nose_z"] - 0.762 - 0.635 * 2.25 * 0.0254) < 1e-5 and 0.743 <= 0.762 <= 0.787,
          f"pool 9ft: nose {1000 * (p['nose_z'] - 0.762):.2f} mm above the cloth (63.5 % of 57.15 mm), bed in 29.25-31 in")
    longs = part_verts(p, "cushion_long")
    shorts = part_verts(p, "cushion_short")
    lend = max(max(v.y for v in c if v.x > 0 and abs(v.z - p["nose_z"]) < TOL) for c in longs if c[0].x > 0)
    send = max(max(v.x for v in c if v.y > 0 and abs(v.z - p["nose_z"]) < TOL) for c in shorts if c[0].y > 0)
    corner = math.hypot(0.635 - send, 1.27 - lend)
    side = 2 * min(min(v.y for v in c if v.y > 0) for c in longs if min(v.y for v in c) > 0)
    check(abs(corner - 4.5625 * 0.0254) < MM and abs(side - 5.0625 * 0.0254) < MM,
          f"pool 9ft: corner mouth {corner / 0.0254:.3f} in, side mouth {side / 0.0254:.3f} in")
    sights = part_verts(p, "sight")
    ys_long = sorted({round((min(v.y for v in s) + max(v.y for v in s)) / 2, 4) for s in sights if abs(min(v.x for v in s)) > 0.7})
    check(len(sights) == 18 and abs(ys_long[1] - ys_long[0] - 12.5 * 0.0254) < TOL, "pool 9ft: 18 sights, 12.5 in apart on the long rails")
    fresh()
    s = G.make_billiard_table("snooker_01", size="snooker_12ft", bed_h=0.864 - 0.045, ball_d=0.0525, diamonds=False)
    G.finalize(s)
    mn, mx = bbox([v.co for v in s.data.vertices])
    check(abs(mx.z - 0.864) < TOL, "snooker: floor to top of cushion rail 864 mm (WPBSA 2022)")


def test_finalize_transforms_and_exports():
    fresh()
    t = G.make_table("scaled_01", width=0.8, depth=0.4, height=0.375)
    t.scale = (2, 2, 2)
    t.rotation_euler = (0, 0, math.radians(90))
    t.location = (3, 1, 0)
    bpy.context.view_layer.update()
    wmn, wmx = bbox([t.matrix_world @ v.co for v in t.data.vertices])
    rep = G.finalize(t)
    bpy.context.view_layer.update()
    amn, amx = bbox([t.matrix_world @ v.co for v in t.data.vertices])
    check(tuple(t.scale) == (1, 1, 1) and t.rotation_euler.z == 0 and (amn - wmn).length < TOL and (amx - wmx).length < TOL,
          "finalize: scale/rotation applied to the data, world placement unchanged")
    mn, mx = bbox([v.co for v in t.data.vertices])
    check(abs(mx.x - mn.x - 0.8) < TOL and abs(mx.y - mn.y - 1.6) < TOL and abs(mn.z) < TOL,
          "finalize: applied 2x scale + 90 deg -> 0.8 x 1.6 x 0.75 in local space, origin on the floor")
    check(rep["tris"] > G.tri_count(t, evaluated=False), f"finalize: LOD0 {rep['tris']} tris (bevelled)")
    fresh()
    t = G.make_table()
    G.finalize(t, triangulate=True)
    ev = evaluated_mesh(t)
    check(all(len(p.vertices) == 3 for p in ev.polygons) and ev.has_custom_normals,
          "finalize(triangulate=True): triangles only, custom normals kept")
    bpy.data.meshes.remove(ev)
    ucx = G.make_collision(t, "UE")
    check([o.name for o in ucx] == [f"UCX_{t.name}_{i:02d}" for i in range(5)] and all(len(o.data.vertices) == 8 for o in ucx),
          "UE collision: UCX_<name>_00..04 boxes (top + 4 legs), 8 verts each")
    lods = G.make_lods(t)
    tris = [G.tri_count(t), sum(len(p.vertices) - 2 for p in lods[0].polygons), sum(len(p.vertices) - 2 for p in lods[1].polygons)]
    check(tris[0] > tris[1] > tris[2], f"LOD tris {tris}")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "table.fbx")
        for o in bpy.context.view_layer.objects:
            o.select_set(o == t or o.name.startswith("UCX_"))
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                                 use_mesh_modifiers=True, mesh_smooth_type="FACE", use_tspace=True)
        fresh()
        bpy.ops.import_scene.fbx(filepath=path)
        bpy.context.view_layer.update()
        imp = bpy.data.objects.get("table_01")
        d = imp.dimensions if imp else Vector()
        check(imp is not None and (Vector(d) - Vector((1.6, 0.9, 0.75))).length < MM and len(bpy.data.objects) == 6,
              f"FBX round trip (UE settings): table {tuple(round(x, 3) for x in d)} m + 5 UCX objects")
    fresh()
    c = G.make_chair()
    G.finalize(c)
    a = G.make_collision(c, "SOLLUMZ")
    ok = (a["drawable"].type == "EMPTY" and a["drawable"].name == "chair_01" and a["model"].name == "chair_01.model"
          and a["model"].parent == a["drawable"] and a["model"].matrix_basis == Matrix.Identity(4)
          and all(abs(sum((v.co for v in b.data.vertices), Vector()).length) < 1e-6 for b in a["bounds"]) and len(a["lods"]) == 2)
    check(ok, "Sollumz layout: drawable empty > .model (identity) + .col > box bounds centred on their origin, 2 LOD meshes")


PRESETS = [
    ("dining", lambda: G.make_table("dining_01", 1.8, 0.9, 0.75), (1.8, 0.9, 0.75)),
    ("desk", lambda: G.make_table("desk_01", 1.4, 0.7, 0.74, top_t=0.025, apron_h=0.06), (1.4, 0.7, 0.74)),
    ("bar table", lambda: G.make_table("bartable_01", 1.2, 0.6, 1.05, leg=0.07, apron_h=0.08), (1.2, 0.6, 1.05)),
    ("wall unit", lambda: G.make_cabinet("k_wall_60", 0.6, 0.72, 0.35, base="NONE", handle="BAR_H"), None),
    ("tv unit", lambda: G.make_cabinet("tv_160", 1.6, 0.50, 0.45, base="LEGS", leg_h=0.15, handle="KNOB"), None),
    ("8ft pro", lambda: G.make_billiard_table("pool_8", size="8ft_pro"), None),
    ("7ft", lambda: G.make_billiard_table("pool_7", size="7ft"), None),
    ("bed UK double", lambda: G.make_bed_frame("bed_uk", mattress="UK_double", footboard_h=0.45), None),
    ("bed EU 90", lambda: G.make_bed_frame("bed_90", mattress="EU_90x200"), None),
]


def test_presets():
    for label, fn, dims in PRESETS:
        fresh()
        ob = fn()
        G.finalize(ob)
        if dims is None:
            mn, mx = bbox([v.co for v in ob.data.vertices])
            dims = tuple(mx - mn)
        common(ob, dims, f"preset {label}")
    fresh()
    d = G.make_table("desk_01", 1.4, 0.7, 0.74, top_t=0.025, apron_h=0.06)
    check(d["knee_clearance"] >= 0.63, f"preset desk: knee clearance {d['knee_clearance']:.3f} m")


if __name__ == "__main__":
    print("bpy", bpy.app.version_string)
    for fn in (test_table, test_chair, test_bar_stool, test_shelf_and_clamp, test_cabinets, test_drawers, test_beds,
               test_billiard, test_finalize_transforms_and_exports, test_presets):
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
