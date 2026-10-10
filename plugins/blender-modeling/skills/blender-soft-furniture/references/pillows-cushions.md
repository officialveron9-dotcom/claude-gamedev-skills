# Pillows and cushions

Contents: base mesh · cloth settings and measured sweeps · resolution rule · seams and piping · corners ·
sag, dents, settling · sculpt finish · shapes (square, rectangular, round, bolster, box) · balloon fixes.
Tags as in SKILL.md: [T] measured with `sf_selftest.py`/probes (5.2.2 + 4.5.14), [S] source, [W] web snippet.

## 1. Base mesh

| Shape | Build (`SF.pillow_base`) | Seam group | Notes |
|---|---|---|---|
| KNIFE (throw pillow, square/rectangular) | Six welded grids: W × D × 0.02 m, one loop around the middle of the 2 cm band | middle loop | The band becomes the sewn edge after inflation |
| BOX (seat/back cushion) | Same, band = gusset height (0.08–0.15 m), loops every `res` | top + bottom welt loops | Gusset keeps its height only with bending ≥ 2 |
| ROUND | KNIFE grid mapped onto a disc (elliptical grid mapping) | middle loop | All quads, no pole |
| BOLSTER | Cylinder along X with ringed caps | both cap rims | Already round: pressure only holds it |

Wrong vs right:

```python
# WRONG: partial subdivide of a cube -> top/bottom stay n-gons (28-gons measured on 5.2.2)
bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if is_x_or_y(e)], cuts=24, use_grid_fill=True)
# WRONG: UV sphere / revolved disc with a pole -> fans at the centre, barely inflates (ratio 0.11)
# RIGHT: SF.pillow_base(...) = six grids + bmesh.ops.remove_doubles + recalc_face_normals
#        (closed, manifold, 0 boundary edges, all quads; asserted in the self-test)
```

Interactive equivalent: Cube → scale to W × D × 0.02 → Edit Mode → *Loop Cut* (X: W/res cuts, Y: D/res cuts,
one cut around the band) → no Subdivision modifier during the sim (a modifier above Cloth multiplies the cost).
Apply scale first (cloth stiffness and pressure act on the real size).

## 2. Cloth settings

Physics → Cloth (Blender 4.x/5.x names; bpy in brackets):

| Panel | Setting | Pillow | Why |
|---|---|---|---|
| Field Weights | Gravity [`effector_weights.gravity`] | **0** | Inflate in place, no collider needed |
| Shape | Shrinking Factor [`shrink_min`] | 0.02–0.15 (preset) | Pulls the panels → pinched corners, wrinkles; lets a flat panel dome |
| Internal Springs / Pressure | Pressure [`use_pressure`, `uniform_pressure_force`] | 60 × edge length (KNIFE) | Constant pressure when Target Volume = 0 [S] |
| Pressure | Pressure Scale [`pressure_factor`] | 1 (default) | Ambient pressure, kPa [S] |
| Stiffness | Bending | 0.5 throw, 2 seat cushion | Higher = flatter panels, fewer wrinkles |
| Quality | Quality Steps | 8 (4 gave ±10 % result) | |
| Collisions | Self Collision | off (KNIFE/BOX/BOLSTER), on (ROUND, distance 0.003) | |
| Cache | End | 45 | Measured settle < 1–4 mm/frame by 45 |

RNA facts [S, `rna_cloth.cc` 5.2]: Quality = steps per frame (UI 1–80); Shrink range −∞…1 (negative grows);
setting `shrink_min` also raises `shrink_max` to at least that value; Pressure may be negative; Target Volume 0 =
volume change does not affect pressure; Pressure Vertex Group limits pressure to part of the mesh.

### Measured sweeps (0.5 × 0.5 KNIFE, 2 cm edges, quality 8, 30–90 frames) [T]

| Pressure | Shrink | Bending | Thickness/width | Read as |
|---|---|---|---|---|
| 1.0 | 0.0 | 0.5 | 0.18 | flat |
| 1.0 | 0.10 | 0.5 | 0.26 | slim pillow |
| 1.5 | 0.10 | 0.5 | 0.35 | plump |
| 1.2 | 0.10 | 0.5 | **0.29** | preset |
| 2.0 | 0.0–0.15 | 0.5 | 0.48–0.50 | balloon |
| 5.0 | 0.0–0.15 | 0.5 | 0.47–0.58 | balloon |
| 1.0 | 0.10 | 5.0 | 0.14 | stiff board |

BOX 0.6 × 0.6 × 0.10 (shrink 0.05): P 0.3/b 2 → 0.147 m, crown 2.2 cm (preset); P 0.4/b 2 → 0.158; P 0.2/b 1 →
0.213 (crown 6 cm); P 0.3/b 1 → 0.266 (balloon) [T].
ROUND Ø 0.45: self-coll on, P 0.6: shrink 0 → 0.33, 0.02 → 0.33–0.36, 0.04 → 0.43, 0.06 → 0.53; self-coll off,
P 1.0, shrink 0.06 → 0.28 but 26 intersecting tri pairs at the pinch [T].

### Resolution rule

The mass-spring membrane stiffens as edges get shorter: same P 1.0/shrink 0.1 gave 0.26 at 2 cm and 0.50 at 1 cm;
at 1 cm, P 0.5 gave 0.28 ≈ the 2 cm result [T]. Keep pressure ∝ edge length (presets store pressure per metre of
edge). Pick the edge length first: 2 cm for game props (1.4 k verts, 1.5 s), 1 cm for renders/hero bakes (5.4 k
verts, 9–12 s) [T].

## 3. Seams, piping, welts

- The seam loop is stored as vertex group `seam` by `pillow_base` and survives `apply_cloth` [T].
- **Piping/welt cord** (`SF.add_piping(ob, radius=0.004)`): poly curve through each seam loop, `bevel_depth`
  3–5 mm, parented to the pillow. Convert to mesh for export (or bake it into the normal map for game LODs).
- **Crease-only seam**: select the seam loop → Edge Crease 1 (`crease_edge` attribute, 4.0+) → Subdivision keeps a
  tight ridge. For a pinched seam, scale the loop 0.98 toward the centre before Subdivision.
- **Topstitch**: normal/height texture along the seam (bake from a curve with tiny bevel) — never geometry on props.

## 4. Corners and pinch

- Dog-ears come from shrink + pressure; at shrink 0 corners stay square and the pillow reads as a cushion insert.
- Pinch too sharp (folds through itself) → self-collision on (0.003) or lower shrink; check with
  `SF.self_intersections(ob) == 0` [T].
- "Hollywood"/karate chop: after apply, `add_dent` at the top centre (radius 0.1, depth 0.04) or sculpt a crease.

## 5. Sag, dents, settling

| Need | Method |
|---|---|
| Someone sat here | `SF.add_dent(ob, centre, radius 0.15–0.25, depth 0.02–0.04)` (smoothstep falloff) [T: 3 cm dent] |
| Pillow resting on bed/sofa | Second sim on the applied pillow: gravity 1, pressure ½ of the preset, collider friction 40, 20–30 frames (not executed) |
| Leaning against a backrest | Rotate 10–20°, then the settle sim with both colliders (not executed) |
| Seat cushion sag | `add_dent` centred 10 cm in front of the middle, radius ≈ ⅓ width; never deform the frame |

## 6. Sculpt finish (interactive)

- Cloth brush / Cloth Filter (Sculpt Mode, 2.9+) for local wrinkles without re-simulating; Inflate on a mask for
  overstuffed areas; Smooth to remove sim noise; Crease brush along seams.
- Multires → bake to the game mesh rather than shipping sculpt density.
- Break symmetry: every pillow gets its own dent/rotation/scale (±3–5 %).

## 7. Balloon / flat checklist

| Symptom | Fix in this order |
|---|---|
| Thickness/width > 0.45, round silhouette | Lower pressure (∝ edge length); lower shrink if self-collision is on; BOX: bending 2 |
| No corner pinch | Shrink 0.08–0.12 |
| Too flat (< 0.2) | Raise shrink before pressure; lower bending |
| Wobbles/never settles | 45+ frames; check the base mesh is all quads; quality 8 |
| Different result each run | Jumped frames; always bake or step from frame 1 |
