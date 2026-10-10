# Sofas, armchairs, tufting

Contents: part breakdown · cushions · seams/welts · sag · tufting (GN maths, parameters, buttons, bmesh fallback) ·
leather vs fabric · throws · what to leave to the sibling skill.
Frames, arms' wooden parts, legs, seat heights/depths: `blender-furniture-modeling`.

## 1. Part breakdown (separate objects)

| Part | Build | Notes |
|---|---|---|
| Frame + arms + back shell (upholstered, rigid) | Sibling skill frame; upholstered shell = BOX-like mesh with bevel 1–2 cm + Subdivision | Rigid: no sim |
| Seat cushions | `make_pillow(shape="BOX", size=(w, d), thickness=0.10–0.15)` | One per seat; 5–15 mm gaps between cushions |
| Back cushions | BOX, thickness 0.12–0.18, leaning 10–15° | Inflate in place, then rotate |
| Scatter pillows | KNIFE 0.45–0.5, ratio 0.25–0.35 | Vary each |
| Tufted panels (back, arms, headboard) | `add_tufting` on the panel object | Panel faces +Z during build |
| Legs / plinth | Sibling skill | |

Separate objects keep seams honest (welts, gaps, shadows) and let GTA/UE LOD each part; merge only at export if the
budget asks for it (see game-ready.md).

## 2. Seat cushion recipe [T]

```python
c = SF.make_pillow("Seat_L", "BOX", (0.62, 0.58), thickness=0.12, subsurf=0)  # P 0.3, shrink 0.05, bending 2
SF.add_piping(c, radius=0.004)                       # both welts (seam group = top + bottom border loops)
top = max(v.co.z for v in c.data.vertices)
SF.add_dent(c, (0.0, -0.08, top), radius=0.22, depth=0.025)   # sag: in front of the centre, not the middle
c.modifiers.new("Subdivision", 'SUBSURF').levels = 1
```

Measured: 0.6 × 0.6 × 0.10 BOX → 0.57 × 0.57 × 0.147 with a 2.2 cm crown; dent 3 cm deep [T].
Settled-sag alternative (not executed): place the applied cushion on the seat deck (Collision, friction 40), second
cloth run with gravity 1, pressure 0.15, 20 frames, plus a sphere collider (r 0.2) pressed 3 cm into it.

## 3. Seams and welts

- BOX cushions: two welts (top/bottom border loops) = `seam` group → `add_piping` radius 3–5 mm.
- Arms/backs of the frame: piping along the front-face border loop, same radius; boxed arms get welts on both edges.
- Gaps: real cushions touch with 5–15 mm gaps and visible compression; never leave cushions intersecting
  (`SF.intersections(a, b) == 0`) and never float them (> 5 mm gap reads as floating at bedroom scale).

## 4. Tufting (Geometry Nodes)

`SF.add_tufting(ob, spacing=(sx, sy), depth, radius, pleat_depth, pleat_width, offset, mask="tuft")` builds
[Subdivision] → GN `SF_Tufting`: Set Position offset = −normal × mask × f(x, y).

Diamond (quincunx) lattice maths: buttons at (i·sx, j·sy) and ((i+½)·sx, (j+½)·sy). With
u = x/sx + y/sy and v = x/sx − y/sy every button sits at integer (u, v) and the diamond edges (pleat lines) are the
lines u = k and v = k. In metres across an edge, 1 lattice unit = h = sx·sy/√(sx² + sy²).

```
du = |fract(u + ½) − ½|,  dv = |fract(v + ½) − ½|
d_button = √(du² + dv²)·h,  d_pleat = min(du, dv)·h
f = depth·exp(−(d_button/radius)²) + pleat_depth·exp(−(d_pleat/pleat_width)²)·(1 − button term)
```

Measured on a 0.72 × 0.54 × 0.12 BOX at 1 cm + Subdivision 1 (43 k verts): dimple exactly 25.0 mm, cell tops
untouched, 39 buttons, GN result = bmesh fallback within 4e-8 m, same on 4.5.14 and 5.2.2 [T].

| Style | Spacing (x, y) | Depth | Radius | Pleat depth/width |
|---|---|---|---|---|
| Chesterfield back | 0.10–0.13 | 0.02–0.03 | 0.012–0.018 | 0.008–0.012 / 0.005–0.008 |
| Headboard | 0.15–0.20 | 0.02–0.03 | 0.015–0.02 | 0.008 / 0.006 |
| Mattress quilting | 0.10–0.15 | 0.004–0.008 | 0.01 | 0 |
| Ottoman top | 0.12–0.15 | 0.015–0.02 | 0.012 | 0.006 / 0.005 |

Rules:
- Resolution: base edges ≤ radius/1.5, then Subdivision 1–2 below the GN modifier (the GN runs on the subdivided
  mesh). Coarser = faceted dimples.
- Mask: vertex group `tuft` (`SF.tuft_mask`: faces with normal.z > 0.7, smoothstep falloff over `margin` 0.06 m from
  the panel border). Vertex groups survive the Subdivision modifier and reach GN as named attributes [T].
- Exposed inputs: Spacing X/Y, Button Depth/Radius, Pleat Depth/Width, Offset X/Y, Mask (string).
  Set them per version: 5.2 `getattr(mod.properties.inputs, sock.identifier).value = v`; ≤ 5.1 `mod[sock.identifier] = v`
  (5.2 raises `TypeError: ... id properties not supported for this type`) [T].
- Buttons: `SF.place_buttons` puts a flattened sphere (r 11 mm, half-height 6 mm) at every lattice point with full
  mask weight, seated at the mean height of 8 rays on a ring of the button radius. Seated at the dimple bottom they
  disappeared inside the 25 mm funnel [T]. Game LODs: bake buttons into normal/AO below LOD0.
- Bmesh fallback (`SF.tuft_bmesh`): same formula, destructive; use when the target exporter cannot evaluate GN or
  when sculpting on top.
- Real tufting pulls fabric: after the GN, a short cloth relax (pressure 0.2, pin the button points) adds sag
  between rows (not executed); usually unnecessary for game props.

## 5. Leather vs fabric

| | Fabric | Leather |
|---|---|---|
| Cloth bending (for sims) | 0.5–2 | 5–15 (fewer, larger wrinkles) |
| Wrinkles | many small, tension lines to corners | few broad creases at seat front/arm top |
| Shading | roughness 0.8–0.95, Sheen 0.3–1.0 | roughness 0.35–0.5, sheen 0, grain bump, optional Coat 0.1–0.2 |
| Wear | pilling, darker arms (dirt), lighter seat front (fade) | glossier/darker wear on arm tops and seat front, cracks in creases |

Values: materials.md (`SF.FABRICS`).

## 6. Throws

Drape on the arm or back with `drape_blanket(bed=arm_object, size=(1.3, 1.7), res=0.03, fold_back=0)` after
`set_collider(arm_object)` (not executed). Fold a throw in thirds by pre-folding (like the turn-down) before the sim.

## 7. Wrong vs right

| Wrong | Right |
|---|---|
| One mesh for frame + cushions | Separate objects; gaps and welts |
| Cloth sim with hundreds of pinned button vertices | GN displacement + button mesh (seconds, exact) |
| Tufting on the low poly | Tuft the high, bake to the low (normal + AO) |
| Identical cushions | Different dents/rotations; one cushion slightly pushed back |
| Leather with Sheen | Sheen 0, grain bump + roughness variation |
