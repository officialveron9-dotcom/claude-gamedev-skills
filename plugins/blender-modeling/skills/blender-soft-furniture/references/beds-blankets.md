# Beds: mattress, sheets, duvet/blanket, pillows, headboard

Contents: order of work · mattress · fitted sheet · duvet drape (measured) · turn-down fold · tucked edge ·
pillows on the bed · wrinkles and realism · headboard · throws.
Dimensions (mattress sizes, heights, frame clearance): `blender-furniture-modeling` → `references/dimensions.md`.

## 1. Order of work

1. Frame (sibling skill, `make_bed_frame`) → `SF.mattress_from_frame(frame)` (reads `frame["mattress"]` =
   `[w, l, t, x, y, z_bottom]`, frame-local) or `SF.make_mattress(name, (w, l, t), top_z=...)`.
2. Fitted sheet (`SF.fitted_sheet`) — no sim.
3. Duvet/blanket drape (`SF.drape_blanket`) on the mattress (+ the frame's side rails/footboard as colliders if they
   stand above the mattress bottom).
4. Pillows: inflate (`make_pillow`), place, settle with gravity, dent where the head lies.
5. Wrinkle/compression pass (sculpt), materials, then game-ready.

## 2. Mattress

| Feature | How | Values |
|---|---|---|
| Rounded edges | Bevel modifier, Limit Method Angle, Profile 0.5 | width 0.03–0.05 m, 4–6 segments (`make_mattress` default 0.04/5) |
| Welt/piping on top and bottom edge | Edge loop 1–2 cm in from each border → `add_piping`-style curve (3–4 mm), or crease + Subdivision | |
| Slight crown | Proportional edit / `add_dent(direction=(0,0,1))` at the centre, 5–10 mm | real mattresses are not flat boxes |
| Pillow-top | Second BOX cushion 4–6 cm on top, 1–2 cm smaller per side, pressure preset, welt between | or one loop + crease 1 cm below the top |
| Quilting | Tufting GN with small spacing (0.10–0.15), depth 3–6 mm, no buttons; or stitched channels in the normal map | |
| Collision for draping | `set_collider`: outer 0.002, inner 0.05, cloth friction 40 | see §4 |

## 3. Fitted sheet

`SF.fitted_sheet(mattress, wrap=0.05, offset=0.002)`: shell of the evaluated mattress, bottom face inset by 5 cm and
removed (the band tucks under), pushed out 2 mm with a Displace modifier (strength 0.002, midlevel 0).
Measured: gap 2.0 mm everywhere, 0 overlaps, 0 vertices inside [T]. Then: Subdivide/Remesh the top only if you sculpt;
corner gathers (elastic) with the Cloth brush or Crease brush; tension lines from the corners in the normal map.
A cloth sim for a fitted sheet is not worth it: it slides and never matches the mattress tightly.

## 4. Duvet / blanket drape (`SF.drape_blanket`)

Setup (Blender UI names; bpy in brackets):

| Where | Setting | Value | Measured effect [T] |
|---|---|---|---|
| Blanket mesh | Grid, faces +Z | 3–4 cm edges (2.2 × 2.3 m at 4 cm = 3.2 k verts) | 12 s for 60 frames |
| Cloth | Quality | 8 | |
| Cloth | Mass / Bending | 0.4 / 2 (duvet), 0.3 / 0.5 (sheet, throw) | higher bending = fewer, larger folds |
| Cloth | Air Viscosity [`air_damping`] | **10** (RNA max) | air 1: overhang still swinging 26–110 mm/frame at f60; air 10: 1.2 mm |
| Cloth Collisions | Distance [`distance_min`] | **0.003** | default 0.015 |
| Cloth Collisions | Quality | 4 | |
| Cloth Collisions | Self Collision, distance | on, 0.003 | 0 self-intersections |
| Collider (Physics → Collision) | Thickness Outer | **0.002** | default 0.02 |
| Collider | Cloth Friction [`cloth_friction`] | **40** | 5 (default): duvet with 0.55 m foot overhang slid off; 40 held |
| Cache | End | 60 | settled < 1 mm/frame |

Rest gap ≈ cloth Distance + collider Outer Thickness: defaults 0.015 + 0.02 → **3.1 cm floating** (and 46 s);
0.006 + 0.005 → 1.1 cm; 0.003 + 0.002 → **5 mm**, 0 vertices inside, 0 triangle overlaps [T].

Headless/scripted order (each step was a bug):

```python
SF.register_colliders()              # 1. evaluate the depsgraph with the colliders BEFORE the cloth object exists
blanket = SF._obj_from_bm(...)       # 2. create the cloth object, add Cloth, set cache range
SF.simulate(blanket, 60)             # 3. ptcache.bake with point_cache override (or frame_set every frame)
SF.max_step(blanket, 60) < 0.003     # 4. settled?
SF.apply_cloth(blanket)              # 5. freeze at frame 60, remove Cloth (cache freed)
# 6. Solidify: thickness 0.02 (duvet) / 0.004 (sheet), offset +1, Even Thickness OFF; Subdivision 1
```

## 5. Turn-down (folded-back top edge)

- Do not try to make cloth fold itself (it slides or crumples). Pre-shape it: the head strip (`fold_back` 0.3–0.4 m)
  is wrapped around a 2 cm cylinder and laid back on top, reversed; vertex group `fold` records it (weights ramp
  through the bend) [T].
- Self-collision keeps the layers apart during the sim; gravity flattens the fold to the self distance (~1.2 cm).
- After apply: the fold layer's normals point down/inward. Push it out by 2 × duvet thickness along −normal
  (`SF.lift_group(ob, "fold", 0.04)`), then Solidify offset +1. A +Z lift left the side flaps inside the mattress
  (117 tri pairs) [T]; Even Thickness made a 0.48 m spike at the fold [T].
- `head_offset` = bed head → fold line (0.40–0.50 m leaves room for two rows of pillows).

## 6. Tucked edge (not executed)

- Tuck at the foot/sides: before the sim, bend the rows that should be tucked down the mattress side and under its
  bottom (like the fold: pre-shape), put them in a pin group (`vertex_group_mass`), pin stiffness 1, and simulate;
  the free part drapes onto the pinned part.
- Simpler for props: drape untucked, then delete the hanging rows below the mattress top − 3 cm on the tucked sides
  and close with a Shrinkwrap band into the frame gap (invisible in game).

## 7. Pillows on the bed

- Inflate each pillow separately (`make_pillow`, gravity 0), then place: rows of 2 sleeping pillows (0.5 × 0.7 or
  0.65 × 0.65 EU) leaning 10–20° on the headboard, decorative pillows in front, each rotated/scaled differently.
- Settle (not executed): second sim on the applied pillow with gravity 1, pressure ½, collider = mattress + headboard
  (friction 40), 20–30 frames. Or skip the sim: `add_dent` on the underside and place by hand, then check
  `SF.intersections(pillow, mattress) == 0`.
- Duvet over the pillows: include the pillows as colliders before `register_colliders()`.

## 8. Realism pass

| Fake | Fix |
|---|---|
| Duvet perfectly smooth (uniform tension) | Finer grid (2–3 cm) or bending 0.5–1 for more folds; sculpt compression where pillows/bodies press |
| Hard edge where duvet meets mattress side | Subdivision 1 after Solidify; AO bake; avoid bevel on the duvet |
| Floating | Gap > 1 cm → collision values (§4) |
| Corners hang identical | Rotate the blanket 1–3° before the sim; offset it 2–5 cm sideways |
| Sheets with zero thickness | Solidify 3–5 mm, offset +1 |
| No contact shadow | AO bake (game) or ray-traced AO/contact shadows (UE) |

## 9. Headboard upholstery

- Build the panel as a BOX cushion lying in XY (tufting and `tuft_mask` work on the +Z-facing panel), apply tufting
  (`add_tufting` + `place_buttons`), then rotate the object upright and parent it to the frame's headboard.
- Channel tufting: vertical channels as loops + crease (or sculpt); the diamond GN lattice cannot make straight
  channels.

## 10. Throw blanket on a bed foot or sofa arm (not executed)

`drape_blanket` works with any collider (`bed=` the sofa arm object with `set_collider`), size 1.3 × 1.7 m,
3 cm grid, bending 0.5, `fold_back=0`; rotate the grid 20–40° about Z before the sim for a casual drape. A throw
lying folded in thirds: pre-fold twice like the turn-down, self-collision on.
