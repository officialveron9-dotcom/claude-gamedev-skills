"""Headless self-test for sf_soft.py. Run:
    blender -b --factory-startup --python-exit-code 1 -P sf_selftest.py -- [--out DIR]
    python sf_selftest.py [--out DIR]          # with the `bpy` pip module (3.13 + bpy 5.2 / 3.11 + bpy 4.2)
Exits non-zero on the first failed assertion. Prints one JSON line per test."""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import sf_soft as SF  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = argv[argv.index("--out") + 1] if "--out" in argv else None
results = {}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def report(name, t0, **kw):
    kw["seconds"] = round(time.time() - t0, 2)
    results[name] = kw
    print("SFTEST", json.dumps({name: kw}, default=lambda o: round(o, 4) if isinstance(o, float) else str(o)))


def test_pillows():
    for shape, size, thick in (("KNIFE", (0.5, 0.5), None), ("BOX", (0.6, 0.6), 0.10),
                               ("ROUND", (0.45, 0.45), None), ("BOLSTER", (0.5, 0.2), None)):
        reset()
        t0 = time.time()
        p = SF.pillow_base("P_" + shape, shape, size, thick)
        before = SF.stats(p, evaluated=False)
        assert before["nonmanifold_edges"] == 0 and before["boundary_edges"] == 0, before
        loops = SF.seam_loops(p)
        assert loops, "no seam loop"
        SF.add_pillow_cloth(p, shape, frames=45)
        SF.simulate(p, 45)
        settle = SF.max_step(p, 45)
        SF.apply_cloth(p)
        assert not any(m.type == 'CLOTH' for m in p.modifiers)
        st = SF.stats(p, evaluated=False)
        d = st["dims"]
        if shape in ("KNIFE", "BOX", "ROUND"):
            ratio = d[2] / max(d[0], d[1])
            grow = 1.2 if shape == "BOX" else 2.0          # BOX starts at full gusset height
            assert d[2] > before["dims"][2] * grow, f"{shape} did not inflate: {d}"
            assert 0.18 < ratio < 0.42, f"{shape}: thickness/width {ratio:.2f} (flat < 0.18 < ok < 0.42 < balloon)"
        else:
            ratio = (d[1] + d[2]) / 2 / d[0]
            # starts as a full cylinder: pressure must hold it round while shrink tightens it
            assert d[1] > before["dims"][1] * 0.9 and abs(d[1] - d[2]) < 0.05 * d[1], f"bolster collapsed: {d}"
        assert p.vertex_groups.get("seam"), "seam group lost on apply"
        pipe = SF.add_piping(p)
        si = SF.self_intersections(p)
        report("pillow_" + shape, t0, verts=st["verts"], dims=[round(x, 3) for x in d], ratio=round(ratio, 3),
               last_frame_step_m=round(settle, 5), self_intersections=si, seam_loops=len(loops),
               piping_splines=len(pipe.data.splines))
        assert si == 0, f"{shape}: {si} self-intersecting triangle pairs"


def test_dent():
    reset()
    t0 = time.time()
    p = SF.make_pillow("Seat", "BOX", (0.6, 0.6), thickness=0.10, subsurf=0)
    top = max(v.co.z for v in p.data.vertices)
    SF.add_dent(p, (0.0, 0.0, top), radius=0.2, depth=0.03)
    centre = min((v for v in p.data.vertices if abs(v.co.x) < 0.03 and abs(v.co.y) < 0.03 and v.co.z > 0),
                 key=lambda v: v.co.z)
    report("dent", t0, top=round(top, 4), centre_after=round(centre.co.z, 4))
    assert top - centre.co.z > 0.02


def test_drape():
    reset()
    t0 = time.time()
    bed = SF.make_mattress("Mattress", (1.6, 2.0, 0.24), top_z=0.6)
    floor = SF._obj_from_bm("Floor", SF._grid("Floor", (4, 4), 1.0, 0.0))
    SF.set_collider(floor)
    b = SF.drape_blanket(bed, size=(2.2, 2.3), res=0.04, head_offset=0.45, fold_back=0.35, frames=60,
                         apply=False)
    settle = SF.max_step(b, 60)
    g = SF.gap_report(b, bed)
    clip = SF.intersections(b, bed)
    si_thin = SF.self_intersections(b)
    SF.apply_cloth(b)
    SF.lift_group(b, "fold", 2 * 0.02)
    so = b.modifiers.new("Solidify", 'SOLIDIFY')
    so.thickness, so.offset, so.use_even_offset = 0.02, 1.0, False
    clip_thick = SF.intersections(b, bed)
    si_thick = SF.self_intersections(b)
    top_blanket = SF.stats(b)["max"][2]
    report("drape_blanket", t0, verts=len(b.data.vertices), last_frame_step_m=round(settle, 5), **g,
           blanket_mattress_tri_overlaps=clip, self_intersections_thin=si_thin,
           solidified_vs_mattress_overlaps=clip_thick, solidified_self_intersections=si_thick,
           top_of_blanket=round(top_blanket, 4))
    assert g["inside"] == 0, f"{g['inside']} blanket verts inside the mattress"
    assert g["median_gap_top"] is not None and g["median_gap_top"] < 0.008, f"floating: {g}"
    assert clip == 0 and clip_thick == 0 and si_thin == 0 and si_thick == 0, (clip, clip_thick, si_thin, si_thick)
    assert top_blanket < g["body_top"] + 0.12, f"spike: blanket top {top_blanket:.3f}"
    assert settle < 0.005, f"not settled: {settle:.4f} m/frame"


def test_step_equals_bake():
    out = []
    for method in ("BAKE", "STEP"):
        reset()
        p = SF.pillow_base("P", "KNIFE", (0.4, 0.4))
        SF.add_pillow_cloth(p, frames=15)
        SF.simulate(p, 15, method=method)
        out.append(SF.stats(p)["dims"])
    reset()
    p = SF.pillow_base("P", "KNIFE", (0.4, 0.4))
    SF.add_pillow_cloth(p, frames=15)
    bpy.context.scene.frame_set(15)                 # the WRONG way: jump without stepping/baking
    jump = SF.stats(p)["dims"]
    diff = max(abs(a - b) for a, b in zip(*out))
    results["bake_vs_step"] = {"bake": out[0], "step": out[1], "jump": jump, "max_diff": diff}
    print("SFTEST", json.dumps({"bake_vs_step": results["bake_vs_step"]}))
    assert diff < 1e-5


def test_curtain():
    reset()
    t0 = time.time()
    c = SF.make_curtain("Curtain", width=1.4, drop=2.4, top_z=2.45, frames=40, apply=False)
    settle = SF.max_step(c, 40)
    SF.apply_cloth(c)
    st = SF.stats(c, evaluated=False)
    stretch = (2.45 - st["min"][2]) - 2.4
    report("curtain", t0, verts=st["verts"], width=round(st["dims"][0], 3), depth=round(st["dims"][1], 3),
           bottom_z=round(st["min"][2], 4), stretch_m=round(stretch, 4), last_frame_step_m=round(settle, 5))
    assert st["max"][2] <= 2.4501, "pinned top moved"
    assert stretch < 0.03, f"drop stretched {stretch:.3f} m"


def test_tufting():
    reset()
    t0 = time.time()
    cu = SF.pillow_base("BackCushion", "BOX", (0.72, 0.54), thickness=0.12, res=0.01)
    mod = SF.add_tufting(cu, spacing=(0.12, 0.12), depth=0.025, subdivide=1)
    st = SF.stats(cu)
    dg = bpy.context.evaluated_depsgraph_get()
    oe = cu.evaluated_get(dg)
    me = oe.to_mesh()
    top = [v.co.copy() for v in me.vertices if v.normal.z > 0.5 or v.co.z > 0.05]
    oe.to_mesh_clear()
    centre = min((c for c in top if abs(c.x) < 0.004 and abs(c.y) < 0.004), key=lambda c: c.z)
    cell = max((c for c in top if abs(c.x - 0.06) < 0.004 and abs(c.y) < 0.004), key=lambda c: c.z)
    dimple = 0.06 - centre.z
    buttons = SF.place_buttons(cu, spacing=(0.12, 0.12))
    n_btn = buttons["sf_button_count"]
    # bmesh fallback must match the GN result
    ref = SF.pillow_base("Ref", "BOX", (0.72, 0.54), thickness=0.12, res=0.01)
    SF.tuft_mask(ref)
    sd = ref.modifiers.new("S", 'SUBSURF')
    sd.levels = 1
    dg = bpy.context.evaluated_depsgraph_get()
    newme = bpy.data.meshes.new_from_object(ref.evaluated_get(dg))
    ref.modifiers.remove(sd)
    ref.data = newme
    SF.tuft_bmesh(ref, spacing=(0.12, 0.12), depth=0.025)
    a = sorted((round(v.co.x, 4), round(v.co.y, 4), v.co.z) for v in ref.data.vertices)
    oe = cu.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = oe.to_mesh()
    b = sorted((round(v.co.x, 4), round(v.co.y, 4), v.co.z) for v in me.vertices)
    oe.to_mesh_clear()
    gn_vs_bmesh = max(abs(p[2] - q[2]) for p, q in zip(a, b)) if len(a) == len(b) else None
    report("tufting", t0, verts=st["verts"], dimple_depth=round(dimple, 4), cell_top=round(cell.z, 4),
           buttons=n_btn, gn_vs_bmesh_max_dz=gn_vs_bmesh, gn_inputs_api="properties.inputs" if bpy.app.version >= (5, 2, 0) else "idprop")
    assert 0.015 < dimple < 0.03, dimple
    assert abs(cell.z - 0.06) < 0.004, cell.z
    assert n_btn >= 12, n_btn
    assert gn_vs_bmesh is not None and gn_vs_bmesh < 2e-3, gn_vs_bmesh


def test_game_ready():
    reset()
    t0 = time.time()
    p = SF.make_pillow("Pillow", "KNIFE", (0.5, 0.5), subsurf=1)
    src = SF.stats(p)["tris"]
    lods, col = SF.game_ready(p, lod_ratios=(1.0, 0.5, 0.25), target_tris=1500)
    tris = [SF.stats(x, evaluated=False)["tris"] for x in lods]
    cst = SF.stats(col, evaluated=False)
    pmin, pmax = SF.stats(p)["min"], SF.stats(p)["max"]
    inside = all(cst["min"][i] <= pmin[i] + 1e-4 and cst["max"][i] >= pmax[i] - 1e-4 for i in range(3))
    report("game_ready", t0, source_tris=src, lod_tris=tris, collision=col.name, collision_verts=cst["verts"],
           collision_tris=cst["tris"], hull_contains_mesh=inside)
    assert abs(tris[0] - 1500) / 1500 < 0.1, tris
    assert tris[1] < tris[0] * 0.6 and tris[2] < tris[1] * 0.6, tris
    assert cst["verts"] == 8 and cst["tris"] == 12 and inside
    assert all(x.data.uv_layers for x in lods), "LOD without UV map"


def test_mattress_from_frame():
    reset()
    t0 = time.time()
    frame = bpy.data.objects.new("bed_01", None)          # stands in for make_bed_frame's object
    bpy.context.scene.collection.objects.link(frame)
    frame.location = (2.0, 1.0, 0.0)
    frame["mattress"] = [1.6, 2.0, 0.20, 0.0, 0.0, 0.32]
    m = SF.mattress_from_frame(frame)
    st = SF.stats(m)
    report("mattress_from_frame", t0, min=st["min"], max=st["max"])
    assert abs(st["max"][2] - 0.52) < 1e-4 and abs(st["min"][2] - 0.32) < 1e-4
    assert abs((st["min"][0] + st["max"][0]) / 2 - 2.0) < 1e-4 and abs(st["dims"][0] - 1.6) < 1e-4


def test_fitted_sheet():
    reset()
    t0 = time.time()
    bed = SF.make_mattress("Mattress", (1.6, 2.0, 0.24), top_z=0.6)
    sh = SF.fitted_sheet(bed)
    st = SF.stats(sh)
    clip = SF.intersections(sh, bed)
    g = SF.gap_report(sh, bed)
    report("fitted_sheet", t0, verts=st["verts"], boundary_edges=st["boundary_edges"], overlaps=clip,
           median_gap_all=g["median_gap_all"], inside=g["inside"])
    assert clip == 0 and g["inside"] == 0 and st["boundary_edges"] > 0
    assert abs(g["median_gap_all"] - 0.002) < 5e-4


def test_materials():
    reset()
    t0 = time.time()
    names = []
    for kind in SF.FABRICS:
        m = SF.fabric_material("M_" + kind, kind, (0.3, 0.1, 0.1))
        bsdf = next(n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
        assert bsdf.inputs["Base Color"].is_linked, kind
        assert bsdf.inputs["Normal"].is_linked == (SF.FABRICS[kind][5] > 0), kind
        names.append(m.name)
    report("materials", t0, built=names)


if __name__ == "__main__":
    print("Blender", bpy.app.version_string)
    t_all = time.time()
    test_step_equals_bake()
    test_pillows()
    test_dent()
    test_drape()
    test_curtain()
    test_tufting()
    test_game_ready()
    test_materials()
    test_mattress_from_frame()
    test_fitted_sheet()
    print("SFTEST ALL PASSED in", round(time.time() - t_all, 1), "s")
    if OUT:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "sf_selftest.json"), "w") as f:
            json.dump(results, f, indent=1, default=str)
