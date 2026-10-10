# Scripts: `sf_soft.py` and `sf_selftest.py`

Contents: how to run · API · headless baking (what works) · measured results per version · bugs found while
testing · not executed.

Files: [../scripts/sf_soft.py](../scripts/sf_soft.py) (library, pure bpy/bmesh, no add-ons) and
[../scripts/sf_selftest.py](../scripts/sf_selftest.py) (assertions, prints one `SFTEST {json}` line per test).

## 1. Run

```bash
# Blender binary (any OS); exit code != 0 on the first failed assertion
blender -b --factory-startup --python-exit-code 1 -P scripts/sf_selftest.py -- --out /tmp/sf
# bpy pip module (how it was tested here)
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python "bpy==5.2.*"
.venv/bin/python scripts/sf_selftest.py --out /tmp/sf          # 3.11 + bpy==4.5.* works the same
```

MCP (official Blender Lab server or mcp-for-blender): `import sys; sys.path.append(r"<skill>/scripts");
import sf_soft as SF` inside the executed code, then call one function per request (each returns objects,
nothing is selected). Save a copy of the user's file first (`blender-python-pitfalls` §11). `ptcache.bake` prints one
`bake: frame N :: M` line per frame to stdout — redirect long headless runs to a log.

## 2. API (all metres, object-local unless noted)

| Function | Does | Key defaults |
|---|---|---|
| `pillow_base(name, shape, size, thickness, res)` | closed all-quad shell + vertex group `seam` | KNIFE/BOX/ROUND/BOLSTER, res 0.02 |
| `add_pillow_cloth(ob, shape, res, pressure, shrink, bending, quality, frames, self_collision)` | inflation cloth, gravity 0 | `PILLOW_PRESETS` (pressure per metre of edge) |
| `simulate(ob, frames, method)` | bake (`ptcache.bake` + `point_cache` override) or STEP; raises if not baked | BAKE |
| `apply_cloth(ob, frame)` | freeze cloth result into the mesh, remove Cloth; modifiers below Cloth stay live | cache end |
| `make_pillow(...)` | base + cloth + simulate + apply + Subdivision | 45 frames |
| `add_dent(ob, center, radius, depth, direction)` | smoothstep dent/sag | |
| `seam_loops(ob)`, `add_piping(ob, radius)` | ordered seam loops; bevelled poly curve per loop | r 0.004 |
| `make_mattress(name, size, bevel, segments, top_z)` | bevelled box + Collision | 0.04 / 5 seg |
| `mattress_from_frame(frame)` | mattress from `frame["mattress"]` (blender-furniture-modeling) | |
| `fitted_sheet(mattress, wrap, offset)` | shell + bottom band + Displace | 0.05 / 0.002 |
| `set_collider(ob, outer, inner, friction, damping)` | Collision for draping | 0.002 / 0.05 / 40 |
| `register_colliders()` | evaluate depsgraph before creating cloth | call before any cloth object |
| `drape_blanket(bed, size, res, gap, head_offset, fold_back, ...)` | drape + optional turn-down + apply + fold lift + Solidify + Subdivision | 4 cm, 60 frames |
| `lift_group(ob, group, amount, axis=None)` | move a group along −normal (or an axis) | |
| `gap_report(cloth, body)` | inside count, median gap over the top, median gap all | |
| `make_curtain(...)` | sine-pleated, pinned, simulated curtain | fullness 2, tension 60 |
| `tuft_offset(...)`, `tuft_mask(ob)` | lattice formula; vertex group `tuft` | |
| `add_tufting(ob, ...)` | Subdivision + GN `SF_Tufting` (inputs exposed, set per version) | spacing 0.12 |
| `tuft_bmesh(ob, ...)` | destructive fallback, same formula | |
| `place_buttons(ob, ...)` | one button mesh, seated on the funnel rim | r 0.011 |
| `fabric_material(name, kind, color, coords)` | Principled preset + weave/grain bump + variation | `FABRICS` |
| `ensure_uv(ob)` | Smart UV Project if no UV map (edit-mode op under `temp_override`) | 66°, 0.02 |
| `game_ready(ob, lod_ratios, target_tris, collision)` | evaluated copy → LOD0..n (Decimate) + UVs + `UCX_` box | (1, .5, .25) |
| `stats`, `self_intersections`, `intersections`, `max_step` | checks used by the tests | |

## 3. Cloth baking headless — what works [T, 5.2.2 and 4.5.14]

```python
sc.frame_set(pc.frame_start)
bpy.context.view_layer.update(); bpy.context.evaluated_depsgraph_get()
with bpy.context.temp_override(scene=sc, object=ob, active_object=ob, point_cache=pc):
    bpy.ops.ptcache.free_bake()
    bpy.ops.ptcache.bake(bake=True)          # EXEC path = synchronous (invoke would start a job)
assert pc.is_baked                           # info e.g. "30 frames in memory (468 KiB)."
```

- `ptcache.bake` poll needs a `point_cache` context member whose owner is the object; with the override it ran
  synchronously in background mode [T; source: `editors/physics/physics_pointcache.cc`, exec → `BKE_ptcache_bake`].
  `ptcache.bake_all(bake=True)` with `temp_override(scene=sc)` also works [T].
- STEP (`frame_set(f)` for every frame) gives bit-identical results (max diff 0.0) but leaves the cache unbaked
  (`is_baked` False, frames still in memory) [T].
- WRONG: `frame_set(N)` directly on an unbaked cloth → wrong shape (0.4 m pillow: 4.3 cm instead of 7.4–7.7 cm) [T].
- Re-baking after changing settings: `free_bake` first (done in `simulate`).

## 4. Measured results (`sf_selftest.py`, 2026-10-10)

| Test | 5.2.2 LTS | 4.5.14 LTS |
|---|---|---|
| bake vs step | identical; jump wrong | identical; jump wrong |
| KNIFE 0.5 | 0.44 × 0.13 m, ratio 0.288, 0 self-int., 1.6 s | 0.288 |
| BOX 0.6 × 0.10 | 0.57 × 0.147, ratio 0.258 | 0.258 |
| ROUND Ø 0.45 | ratio 0.322, settle 4 mm/f | 0.36 |
| BOLSTER | Ø 0.19, ratio 0.394 | same |
| dent | 3.0 cm | 3.0 cm |
| drape (3.2 k verts, 60 f) | gap 5.0 mm, 0 inside, 0 overlaps thin/solidified, 0 self-int., settle 0.8 mm/f, 12 s | same, 12.8 s |
| curtain (17 k verts) | width 1.40, pleat depth 9.8 cm, stretch 5.5 mm, 25 s | same |
| tufting (43 k verts) | dimple 25.0 mm, 39 buttons, GN = bmesh (≤ 4e-8 m), inputs via `properties.inputs` | same via idprops |
| game_ready | 11 600 → 1 500 / 750 / 374 tris, UCX 8 v / 12 t, UVs | same |
| materials | 5 presets build | same |
| mattress_from_frame / fitted sheet | position from frame; sheet gap 2.0 mm, 0 overlaps | same |
| total | ~50 s | ~50 s |

## 5. Bugs found while testing (all fixed in the library)

| Symptom | Cause | Fix |
|---|---|---|
| Pillow twisted, folded through itself | `subdivide_edges` on X/Y cube edges left 28-gons | six welded grids |
| Seam group empty | `bm.verts[i].index` stale after bmesh ops | `bm.verts.index_update()` before reading indices |
| Round pillow stayed flat | revolved disc with a pole | disc-mapped quad grid |
| Blanket fell through the mattress | collider not in the evaluated depsgraph before the cloth object existed | `register_colliders()` first |
| Blanket slid off / kept swinging | friction 5, air damping 1 | friction 40, air damping 10 |
| Blanket 3.1 cm above the mattress | default distances | 0.003 + 0.002 |
| Solidified blanket clipped mattress at the fold | fold flap normals inward; +Z lift | lift along −normal by 2 × thickness |
| 0.48 m spike at the fold | Solidify Even Thickness | Even off |
| Buttons invisible | seated at the dimple bottom | seated on the funnel rim |
| Mattress at the origin instead of on the frame (4.5) | `matrix_world` stale after setting location | `view_layer.update()` before reading matrices |
| `mod["Socket_0"] = v` TypeError on 5.2 | GN inputs moved to `mod.properties.inputs` | version branch |

## 6. Not executed

- Blender 4.2 LTS (4.5.14 and 5.2.2 only); the `blender` binary path (bpy module only; same API).
- Settle-on-collider second sims (pillows on beds, seat sag sim), tucked edges, throw on an arm, sim tufting.
- Sollumz conversion/export of the results, in-game look, UE import — use `fivem-mlo-creation` / `blender-game-export`.
- GN Cloth Dynamics (5.2 experimental XPBD) — see `scenario-blender-geometry-nodes` if installed.
